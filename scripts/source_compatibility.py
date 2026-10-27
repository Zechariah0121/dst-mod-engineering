"""Read-only source comparison. Python 3.10+, stdlib only; never admits evidence.

Candidate schema: CONTROL.json dst-mechanism-research/1. Optional per-entry
compatibility: {dependency_refs: [{ref, role, claim_ids?}], dependency_coverage:
"unknown"|"enumerated_static", unknowns: [...]}. Even enumerated_static does
not certify dynamic/native dependencies. Output contains locators/hashes only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

SCHEMA = "dst-source-compatibility/1"
HASH = re.compile(r"[0-9a-f]{64}\Z")
SYMBOL = re.compile(r"[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*\Z")
STATES = {"byte_identical", "relocation_required", "review_required", "missing", "unknown"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe_zip_name(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a relative ZIP member")
    p = PurePosixPath(value)
    if (":" in value or "\\" in value or p.is_absolute() or p.as_posix() != value
            or any(part in ("", ".", "..") for part in value.split("/"))):
        raise ValueError("Unsafe source member")
    return value


def member_name(value):
    safe_zip_name(value)
    if not value.startswith("scripts/"):
        raise ValueError("Expected exact scripts/... ZIP member")
    return value


class Archive:
    """Never extracts source. Rejects duplicate/unsafe member names."""
    def __init__(self, path, label=None):
        self.path = Path(path).resolve()
        self.sha256 = file_sha(self.path)
        self.label = label  # User label is not an independently verified version.
        self.zip = zipfile.ZipFile(self.path)
        self.files = {}
        self.cache = {}
        try:
            seen = set()
            for info in self.zip.infolist():
                name = info.filename.rstrip("/") if info.is_dir() else info.filename
                safe_zip_name(name)
                if name in seen:
                    raise ValueError("Duplicate ZIP member: " + name)
                seen.add(name)
                if info.is_dir():
                    continue
                if name.startswith("scripts/"):
                    self.files[name] = info
        except Exception:
            self.close()
            raise

    def close(self):
        self.zip.close()

    def raw(self, name):
        member_name(name)
        if name not in self.files:
            return None
        if name not in self.cache:
            self.cache[name] = self.zip.read(self.files[name])
        return self.cache[name]

    def identity(self):
        return {"archive_sha256": self.sha256, "label": self.label,
                "label_verification": "user_supplied_not_version_proof",
                "lua_count": sum(n.endswith(".lua") for n in self.files)}


def range_bytes(lines, start, end):
    if type(start) is not int or type(end) is not int or not 0 < start <= end <= len(lines):
        raise ValueError("Invalid or out-of-bounds source range")
    return "\n".join(lines[start - 1:end]).encode("utf-8")


def masked_lua(text):
    """Navigation lexer only. Blanks strings/comments, preserves character positions.

    Handles quoted escapes, line comments, and Lua [=*[ ... ]=*] strings/comments.
    Does not parse blocks or infer function extent/call graphs.
    """
    out, i, n = list(text), 0, len(text)
    while i < n:
        start = i
        comment = text.startswith("--", i)
        opener = i + 2 if comment else i
        long = re.match(r"\[(=*)\[", text[opener:])
        if long:
            close = "]" + long.group(1) + "]"
            end = text.find(close, opener + len(long.group()))
            i = n if end < 0 else end + len(close)
        elif comment:
            end = text.find("\n", i)
            i = n if end < 0 else end
        elif text[i] in "\"'":
            quote, i = text[i], i + 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            i = min(i, n)
        else:
            i += 1
            continue
        for j in range(start, i):
            if text[j] not in "\r\n":
                out[j] = " "
    return "".join(out)


def locate(archive, symbol, source_file=None, limit=100):
    if not isinstance(symbol, str) or not SYMBOL.fullmatch(symbol):
        raise ValueError("Symbol must be an exact Lua identifier or qualified identifier")
    if source_file:
        member_name(source_file)
    pattern = re.compile(r"(?<![\w.:])" + re.escape(symbol) + r"(?![\w.:])")
    found, total, errors = [], 0, []
    for name in sorted(archive.files):
        if not name.endswith(".lua") or source_file and name != source_file:
            continue
        try:
            text = archive.raw(name).decode("utf-8")
        except UnicodeDecodeError:
            errors.append({"source_file": name, "reason": "non_utf8"})
            continue
        masked = masked_lua(text)
        for match in pattern.finditer(masked):
            total += 1
            if len(found) < limit:
                line = masked.count("\n", 0, match.start()) + 1
                before = masked[max(0, match.start() - 20):match.start()]
                after = masked[match.end():match.end() + 50]
                declaration = bool(re.search(r"\bfunction\s*$", before)
                                   or re.match(r"\s*=\s*function\b", after))
                found.append({"source_file": name, "line": line,
                              "kind": "function_declaration" if declaration else "symbol_occurrence",
                              "file_sha256": sha(archive.raw(name))})
    return {"symbol": symbol, "matches": found, "total_matches": total,
            "truncated": total > limit, "errors": errors,
            "proof_kind": "lexical_navigation_only", "behavior_verified": False}


def compare_reference(ref, old, new, baseline_problem=None):
    result = {"id": ref.get("id"), "original_locator": {k: ref.get(k) for k in
              ("source_file", "file_sha256", "line_start", "line_end", "range_sha256", "symbols")},
              "status": "unknown", "source_identity_reusable": False,
              "runtime_verified": False, "reasons": []}
    try:
        name = member_name(ref["source_file"])
        start, end = ref["line_start"], ref["line_end"]
        for key in ("file_sha256", "range_sha256"):
            if not isinstance(ref[key], str) or not HASH.fullmatch(ref[key]):
                raise ValueError("Invalid " + key)
        if type(start) is not int or type(end) is not int or not 0 < start <= end:
            raise ValueError("Invalid line range")
        symbols = ref.get("symbols", [])
        if not isinstance(symbols, list) or any(not isinstance(s, str) or not s.strip() for s in symbols):
            raise ValueError("Invalid symbols list")
        # Candidate symbols may describe calls or table entries. These hints do
        # not define source identity, and must not veto valid file/range hashes.
        navigation_symbols = [s for s in symbols if SYMBOL.fullmatch(s)]
        skipped_hints = [s for s in symbols if not SYMBOL.fullmatch(s)]
        if skipped_hints:
            result["navigation_hints_not_used"] = skipped_hints
            result["navigation_limitation"] = "non_identifier_hints_preserved_without_guessing_a_symbol"
        if baseline_problem:
            result["reasons"].append(baseline_problem)
            return result
        target = new.raw(name)
        if target is None:
            result.update(status="missing", reasons=["target_member_missing"])
            return result
        result["target_file_sha256"] = sha(target)
        current = target.decode("utf-8").splitlines()
        baseline = old.raw(name) if old else None
        if baseline is not None:
            if sha(baseline) != ref["file_sha256"]:
                result["reasons"].append("provided_baseline_file_does_not_match_reference")
                return result
            original = baseline.decode("utf-8").splitlines()
            old_range = range_bytes(original, start, end)
            if sha(old_range) != ref["range_sha256"]:
                result["reasons"].append("provided_baseline_range_does_not_match_reference")
                return result
        else:
            old_range = None
        if sha(target) == ref["file_sha256"]:
            if sha(range_bytes(current, start, end)) != ref["range_sha256"]:
                result["reasons"].append("reference_range_hash_inconsistent_with_identical_file")
                return result
            result.update(status="byte_identical", source_identity_reusable=True,
                          target_locator={"source_file": name, "line_start": start, "line_end": end},
                          reasons=["exact_original_file_and_range_bytes"])
            return result
        if baseline is None:
            result["reasons"].append("missing_matching_old_source")
            result["symbol_navigation"] = [locate(new, s, name, 20) for s in navigation_symbols]
            return result
        count = end - start + 1
        matches = [i + 1 for i in range(len(current) - count + 1)
                   if sha("\n".join(current[i:i + count]).encode("utf-8")) == ref["range_sha256"]]
        result["matching_range_starts"] = matches
        if len(matches) == 1 and matches[0] != start:
            result.update(status="relocation_required",
                          target_locator={"source_file": name, "line_start": matches[0],
                                          "line_end": matches[0] + count - 1},
                          reasons=["unique_exact_range_moved", "containing_file_changed_semantics_not_certified"])
        elif len(matches) > 1:
            result.update(status="unknown", reasons=["ambiguous_exact_range_matches"])
        elif matches:
            result.update(status="review_required", reasons=["range_unchanged_but_containing_file_changed"])
        else:
            result.update(status="review_required", reasons=["cited_range_changed_or_removed"])
        # Full file whitespace/line-ending changes are changes too; no silent hash rewrite.
        result["changed_line_blocks"] = [
            {"operation": tag, "old_slice_0": [i, j], "new_slice_0": [k, l]}
            for tag, i, j, k, l in difflib.SequenceMatcher(None, original, current, autojunk=False).get_opcodes()
            if tag != "equal"]
        result["symbol_navigation"] = [locate(new, s, name, 20) for s in navigation_symbols]
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
        result["status"] = "unknown"
        result["reasons"].append("invalid_or_unreadable_reference: " + str(exc))
    return result


def worst(statuses):
    for status in ("missing", "review_required", "unknown", "relocation_required", "byte_identical"):
        if status in statuses:
            return status
    return "unknown"


def aggregate_claim(claim, entry, references):
    evidence = claim.get("evidence_refs", [])
    if not isinstance(evidence, list):
        raise ValueError("Candidate evidence_refs must be an array of local reference IDs")
    if any(not isinstance(r, str) for r in evidence):
        raise ValueError("Candidate references must use local string IDs, not legacy artifact references")
    config = entry.get("compatibility", {})
    dependencies = config.get("dependency_refs", [])
    selected = []
    for dep in dependencies:
        if not isinstance(dep, dict) or not isinstance(dep.get("ref"), str) or not dep.get("role"):
            raise ValueError("Each dependency requires ref and role")
        if "claim_ids" not in dep or claim["id"] in dep["claim_ids"]:
            selected.append(dep)
    needed = list(dict.fromkeys(evidence + [d["ref"] for d in selected]))
    rows = [{"ref": r, "status": references[r]["status"] if r in references else "unknown"} for r in needed]
    coverage = config.get("dependency_coverage", "unknown")
    if coverage not in ("unknown", "enumerated_static"):
        raise ValueError("dependency_coverage may only be unknown or enumerated_static")
    reasons = ["dynamic_native_and_unenumerated_consumers_unknown"]
    if not evidence:
        reasons.append("claim_has_no_local_source_reference")
    if any(r not in references for r in needed):
        reasons.append("unresolved_reference_id")
    direct = worst([r["status"] for r in rows])
    return {"id": claim["id"], "kind": claim.get("kind"), "source_status": direct,
            "reference_states": rows, "dependencies": selected,
            "declared_dependency_coverage": coverage,
            "dependency_status": "unknown",
            "compatibility_status": "review_required" if direct in ("missing", "review_required") else "unknown",
            "unknowns": reasons + config.get("unknowns", []),
            "behavior_compatibility_verified": False, "runtime_verified": False}


def validate_compatibility(entry, references):
    """Match CONTROL's optional extension without requiring it on old candidates."""
    if "compatibility" not in entry:
        return
    config = entry["compatibility"]
    if not isinstance(config, dict) or set(config) - {"dependency_refs", "dependency_coverage", "unknowns"}:
        raise ValueError("Invalid optional compatibility object")
    if config.get("dependency_coverage", "unknown") not in ("unknown", "enumerated_static"):
        raise ValueError("Invalid dependency_coverage")
    unknowns = config.get("unknowns", [])
    if not isinstance(unknowns, list) or any(not isinstance(s, str) for s in unknowns):
        raise ValueError("compatibility.unknowns must be a string list")
    deps = config.get("dependency_refs", [])
    if not isinstance(deps, list):
        raise ValueError("dependency_refs must be an array")
    claim_ids = {c["id"] for c in entry.get("claims", [])}
    for dep in deps:
        if (not isinstance(dep, dict) or set(dep) - {"ref", "role", "claim_ids"}
                or dep.get("ref") not in references or not isinstance(dep.get("role"), str)
                or not dep["role"].strip()):
            raise ValueError("Dependency needs a local source ref and nonempty role")
        if "claim_ids" in dep and (not isinstance(dep["claim_ids"], list)
                or any(not isinstance(c, str) or c not in claim_ids for c in dep["claim_ids"])):
            raise ValueError("dependency claim_ids must reference actual claims of this entry")


def assess(documents, old, new):
    results, checklist = [], []
    for path, document in documents:
        if not isinstance(document, dict) or document.get("schema_version") != "dst-mechanism-research/1":
            raise ValueError("Unsupported candidate schema; use legacy-inventory for 187 public records")
        source_refs = document.get("source_references", [])
        if not isinstance(source_refs, list) or any(not isinstance(r, dict) for r in source_refs):
            raise ValueError("source_references must be an array")
        ids = [r.get("id") for r in source_refs]
        if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError("Missing or duplicate reference ID")
        # The supplied baseline must match each document. Multiple baselines are
        # processed as separate invocations, never relabelled as one source epoch.
        problem = None
        expected_archive = document.get("archive_sha256")
        if not isinstance(expected_archive, str) or not HASH.fullmatch(expected_archive):
            problem = "missing_or_invalid_candidate_archive_commitment"
        elif old and old.sha256 != expected_archive:
            problem = "provided_baseline_archive_does_not_match_candidate"
        refs = {ref["id"]: compare_reference(ref, old, new, problem) for ref in source_refs}
        entries = []
        entry_ids = set()
        if not isinstance(document.get("entries", []), list):
            raise ValueError("entries must be an array")
        for entry in document.get("entries", []):
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or entry["id"] in entry_ids:
                raise ValueError("Missing or duplicate entry ID")
            entry_ids.add(entry["id"])
            for field in ("claims", "api_contracts", "mechanism_steps"):
                if not isinstance(entry.get(field, []), list) or any(not isinstance(c, dict) for c in entry.get(field, [])):
                    raise ValueError(field + " must be an object array")
            claim_ids = [c.get("id") for c in entry.get("claims", [])]
            if any(not isinstance(c, str) or not c for c in claim_ids) or len(set(claim_ids)) != len(claim_ids):
                raise ValueError("Missing or duplicate claim ID")
            validate_compatibility(entry, refs)
            claims = [aggregate_claim(c, entry, refs) for c in entry.get("claims", [])]
            contracts = [aggregate_claim({"id": "api:" + str(i) + ":" + api.get("symbol", "unknown"),
                          "kind": "api_contract", "evidence_refs": api.get("evidence_refs", [])}, entry, refs)
                         for i, api in enumerate(entry.get("api_contracts", []))]
            steps = [aggregate_claim({"id": "step:" + str(i), "kind": "mechanism_step",
                     "evidence_refs": step.get("evidence_refs", [])}, entry, refs)
                     for i, step in enumerate(entry.get("mechanism_steps", []))]
            units = claims + contracts + steps
            relevant = {r["ref"] for c in units for r in c["reference_states"]}
            status = worst([refs[r]["status"] if r in refs else "unknown" for r in relevant])
            entries.append({"id": entry["id"], "source_status": status, "claims": claims,
                            "api_contracts": contracts, "mechanism_steps": steps,
                            "original_statuses": {k: entry.get(k) for k in
                             ("knowledge_status", "retrieval_status", "coding_status")},
                            "statuses_changed": False})
            checklist.append({"candidate": str(path), "entry_id": entry["id"], "source_status": status,
                              "affected_units": [c["id"] for c in units if c["source_status"] != "byte_identical"],
                              "affected_refs": sorted(r for r in relevant if r not in refs or refs[r]["status"] != "byte_identical"),
                              "action": "inspect_changed_source_and_dependencies" if status != "byte_identical"
                              else "retain_original_evidence_identity_review_unknown_dependencies",
                              "dependency_followup": "unknown_dynamic_native_and_unenumerated_consumers"})
        results.append({"candidate": str(path), "candidate_sha256": file_sha(path),
                        "evidence_baseline": {"source_epoch": document.get("source_epoch"),
                                              "archive_sha256": expected_archive},
                        "reference_states": list(refs.values()), "entries": entries})
    changes = None
    if old:
        old_names, new_names = set(old.files), set(new.files)
        changes = {"added": sorted(new_names - old_names), "removed": sorted(old_names - new_names),
                   "modified": sorted(n for n in new_names & old_names if sha(old.raw(n)) != sha(new.raw(n)))}
    counts = Counter(r["status"] for d in results for r in d["reference_states"])
    return {"schema": SCHEMA, "baseline": old.identity() if old else None, "target": new.identity(),
            "archive_delta": changes, "reference_status_counts": dict(sorted(counts.items())),
            "candidates": results, "local_review_checklist": checklist,
            "knowledge_reading_available": "independent_public_catalog_or_preserved_baseline_runtime",
            "target_navigation_available": True, "target_admitted_as_evidence_epoch": False,
            "canonical_modified": False, "coding_hold_changed": False, "runtime_verified": False,
            "limitations": ["Exact bytes prove source identity only, not complete behavior compatibility.",
                            "No Lua call graph, native engine model or dynamic consumer closure is inferred.",
                            "Relocation is a proposed locator, never an automatic evidence rewrite."]}


def at(value, pointer):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("Invalid catalog JSON pointer")
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def legacy_inventory(root):
    """Adapter discovery only: preserve family/Scope, never fabricate bindings."""
    root = Path(root).resolve()
    catalog = read_json(root / "CATALOG.json")
    documents, rows = {}, []
    for item in catalog["entries"]:
        relative = item["file"]
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Catalog path escaped knowledge root")
        if relative not in documents:
            documents[relative] = read_json(path)
        entry = at(documents[relative], item["pointer"])
        if entry.get("id") != item["id"]:
            raise ValueError("Catalog ID mismatch")
        rows.append({"id": item["id"], "family": item["family"], "file": relative,
                     "pointer": item["pointer"], "record_sha256": sha(json.dumps(entry, ensure_ascii=False,
                       sort_keys=True, separators=(",", ":")).encode("utf-8")),
                     "original_statuses": {k: entry.get(k) for k in
                         ("knowledge_status", "retrieval_status", "coding_status")},
                     "catalog_statuses": {k: item.get(k) for k in
                         ("knowledge_status", "retrieval_status", "coding_status")},
                     "adapter_status": "unknown_requires_explicit_atom_artifact_scope_binding",
                     "automatic_promotion": False})
    return {"schema": "dst-legacy-compatibility-inventory/1", "record_count": len(rows),
            "family_counts": dict(Counter(r["family"] for r in rows)), "records": rows,
            "canonical_modified": False, "coding_hold_changed": False, "runtime_verified": False}


def main(argv=None):
    supplied = list(sys.argv[1:] if argv is None else argv)
    if supplied and supplied[0] == "legacy-assess":
        if __package__:
            from .legacy_adapter import main as legacy_main
        else:
            from legacy_adapter import main as legacy_main
        # The unified entrypoint always uses the helper shipped beside it.
        return legacy_main(supplied[1:], compatibility_helper=Path(__file__).resolve())
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("legacy-assess", help="Derive per-atom legacy source comparisons; use legacy-assess --help")
    compare = sub.add_parser("assess", help="Single maintenance entry: compare and produce a local review checklist")
    compare.add_argument("--baseline", type=Path)
    compare.add_argument("--target", type=Path, required=True)
    compare.add_argument("--target-label")
    compare.add_argument("--candidate", type=Path, action="append", required=True)
    navigation = sub.add_parser("locate", help="Navigate any explicit target ZIP without an epoch allowlist")
    navigation.add_argument("--target", type=Path, required=True)
    navigation.add_argument("--target-label")
    navigation.add_argument("--symbol", required=True)
    navigation.add_argument("--source-file")
    navigation.add_argument("--limit", type=int, default=100)
    legacy = sub.add_parser("legacy-inventory")
    legacy.add_argument("--knowledge-root", type=Path, required=True)
    for command in (compare, navigation, legacy):
        command.add_argument("--output", type=Path, help="New JSON file; refuses existing paths or source input paths")
    args = parser.parse_args(argv)
    old = new = None
    try:
        if args.command == "legacy-inventory":
            result = legacy_inventory(args.knowledge_root)
        else:
            if args.command == "locate" and not 1 <= args.limit <= 10000:
                raise ValueError("limit must be 1..10000")
            new = Archive(args.target, args.target_label)
            if args.command == "locate":
                result = {"schema": "dst-target-source-navigation/1", "target": new.identity(),
                          **locate(new, args.symbol, args.source_file, args.limit)}
            else:
                old = Archive(args.baseline) if args.baseline else None
                result = assess([(p, read_json(p)) for p in args.candidate], old, new)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            # No output may overwrite candidate, canonical or input archive.
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
        else:
            print(rendered, end="")
        return 0  # Complete assessment, not an assertion of compatibility.
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": {"code": "COMPATIBILITY_INPUT_ERROR", "message": str(exc)},
                          "canonical_modified": False, "runtime_verified": False}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        if old:
            old.close()
        if new:
            new.close()


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())

"""Conservative legacy evidence sidecar. Stdlib only; read-only inputs.

No semantic claim splitting, evidence admission, source restoration or canonical
rewriting. Pass the reviewed current source_compatibility.py explicitly.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
SCHEMA = "dst-legacy-evidence-sidecar/1"
FAMILIES = ("legacy", "native_ai", "native_core")
HASH = re.compile(r"[0-9a-f]{64}\Z")
SCOPE_FIELDS = {"scope", "scope_text", "scope_structured", "source_scope", "original_scope",
                "evidence_scope", "scope_limits", "conditions", "limits", "does_not_prove",
                "does_not_mean", "what_it_does_not_prove", "what_it_proves", "engine_boundary",
                "boundaries", "boundaries_zh", "exclusions", "not_proven", "side", "sides",
                "runtime_environments", "runtime_status", "runtime_tested", "runtime_verified"}
PAYLOAD_FIELDS = {"source_excerpt", "excerpt", "header", "declaration_header"}
ID_LINKS = {"citation_ids", "evidence_ids"}
SKIP_LINKS = {"upstream_citation_ref", "original_payload_metadata", "supporting_locator"}
# Source provenance identities, not a version/ZIP allowlist. A lookalike repo
# name cannot inherit native provenance from generic DST ancestor metadata.
TRUSTED_REPOSITORIES = {"zechariah0121/dst-scripts"}
VANILLA_SOURCE_KINDS = {"vanilla", "vanilla_source_snapshot", "steam_source", "native_source", "klei_source"}


def repository_identity(value):
    if not isinstance(value, str):
        return None
    value = value.strip().rstrip("/")
    if "://" in value:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or parsed.hostname != "github.com" or parsed.username or parsed.password:
            return None
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            return None
        value = "/".join(parts[:2])
    if value.endswith(".git"):
        value = value[:-4]
    return value.lower() if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value) else None


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def escape(part):
    return str(part).replace("~", "~0").replace("/", "~1")


def pointer_tokens(pointer):
    if not isinstance(pointer, str) or pointer and not pointer.startswith("/"):
        raise ValueError("Invalid JSON pointer")
    if re.search(r"~(?![01])", pointer):
        raise ValueError("Invalid JSON pointer escape")
    return [x.replace("~1", "/").replace("~0", "~") for x in pointer.split("/")[1:]] if pointer else []


def at(value, pointer):
    if isinstance(value, str) and isinstance(pointer, str) and pointer.startswith("#L"):
        match = re.fullmatch(r"#L([1-9][0-9]*)(?:-L?([1-9][0-9]*))?", pointer)
        if not match:
            raise ValueError("Unsupported text artifact locator")
        start, end = int(match[1]), int(match[2] or match[1])
        lines = value.splitlines()
        if not 0 < start <= end <= len(lines):
            raise ValueError("Text artifact line anchor outside input")
        return "\n".join(lines[start - 1:end])
    for part in pointer_tokens(pointer):
        if isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                raise ValueError("Invalid JSON array index")
            value = value[int(part)]
        else:
            value = value[part]
    return value


def walk(value, pointer=""):
    yield value, pointer
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, pointer + "/" + escape(key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, pointer + "/" + str(i))


def relative_path(value):
    if (not isinstance(value, str) or not value or ":" in value or "\\" in value
            or PurePosixPath(value).is_absolute() or PurePosixPath(value).as_posix() != value
            or any(x in ("", ".", "..") for x in value.split("/"))):
        raise ValueError("Unsafe knowledge-relative path")
    return value


def load_helper(path):
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("legacy_current_source_compatibility", path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    for name in ("Archive", "compare_reference", "member_name"):
        if not hasattr(helper, name):
            raise ValueError("Compatibility helper lacks " + name)
    return helper, {"path": str(path), "sha256": sha(path.read_bytes())}


def write_sidecar(path, result, exclusive=True):
    """Stable minified JSON, optionally deterministic gzip; no original payload."""
    path = Path(path)
    raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if path.suffix == ".gz":
        raw = gzip.compress(raw, mtime=0)
    with path.open("xb" if exclusive else "wb") as stream:
        stream.write(raw)
    return {"path": str(path.resolve()), "sha256": sha(raw), "bytes": len(raw),
            "serialization": "gzip_utf8_json" if path.suffix == ".gz" else "utf8_json"}


class Store:
    """Exact input bytes and pointers are shared once in normalized tables."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.cache, self.documents, self.nodes, self.scopes = {}, {}, {}, {}
        self.id_indexes = {}
        manifest_path = self.root / "PACKAGE-MANIFEST.json"
        self.manifest = None
        self.manifest_sha256 = None
        if manifest_path.is_file():
            raw = manifest_path.read_bytes()
            self.manifest_sha256 = sha(raw)
            rows = json.loads(raw.decode("utf-8-sig"))["files"]
            self.manifest = {}
            for row in rows:
                name = relative_path(row["path"])
                if name in self.manifest:
                    raise ValueError("Duplicate public manifest file")
                self.manifest[name] = row

    def read(self, name, expected=None):
        name = relative_path(name)
        if name not in self.cache:
            path = self.root / name
            if not path.resolve().is_relative_to(self.root):
                raise ValueError("Knowledge file escaped root")
            raw = path.read_bytes()
            fingerprint = sha(raw)
            if self.manifest is not None:
                row = self.manifest.get(name)
                if not row or row["sha256"] != fingerprint or row["bytes"] != len(raw):
                    raise ValueError("Public manifest mismatch: " + name)
            text = raw.decode("utf-8-sig")
            self.cache[name] = json.loads(text) if name.endswith(".json") else text
            self.documents[name] = {"path": name, "sha256": fingerprint, "bytes": len(raw),
                                    "content_type": "json" if name.endswith(".json") else "utf8_text"}
        if expected is not None and self.documents[name]["sha256"] != expected:
            raise ValueError("Typed artifact hash mismatch: " + name)
        return self.cache[name]

    def node(self, name, pointer):
        value = at(self.read(name), pointer)
        key = "n" + digest([name, pointer, self.documents[name]["sha256"]])[:20]
        self.nodes.setdefault(key, {"document": name, "pointer": pointer, "value_sha256": digest(value)})
        return key

    def ancestors(self, name, pointer):
        """All real target ancestors, even when a typed pointer jumps to a leaf."""
        doc = self.read(name)
        result = [(doc, "")]
        if pointer.startswith("#L"):
            return result
        prefix = ""
        for part in pointer_tokens(pointer):
            prefix += "/" + escape(part)
            result.append((at(doc, prefix), prefix))
        return result

    def typed(self, ref):
        if not isinstance(ref, dict):
            raise ValueError("Typed evidence ref must be an object")
        if {"artifact_path", "sha256", "pointer"} <= ref.keys():
            name, fingerprint, pointer = ref["artifact_path"], ref["sha256"], ref["pointer"]
        elif {"artifact_path", "artifact_sha256", "source_pointer"} <= ref.keys():
            name, fingerprint, pointer = ref["artifact_path"], ref["artifact_sha256"], ref["source_pointer"]
        else:
            raise ValueError("Incomplete typed evidence tuple")
        if not isinstance(fingerprint, str) or not HASH.fullmatch(fingerprint):
            raise ValueError("Invalid typed artifact hash")
        doc = self.read(name, fingerprint)
        at(doc, pointer)
        return name, pointer, {"artifact_path": name, "sha256": fingerprint, "pointer": pointer}

    def scope(self, name, pointer, extra=()):
        doc = self.read(name)
        prefixes = [""]
        for part in pointer_tokens(pointer):
            prefixes.append(prefixes[-1] + "/" + escape(part))
        fragments = []
        for prefix in prefixes:
            parent = at(doc, prefix)
            if isinstance(parent, dict):
                scope_keys = [field for field in parent if field in SCOPE_FIELDS
                              or any(word in field.lower() for word in ("scope", "boundar", "limit", "condition", "runtime", "unknown"))]
                for field in sorted(scope_keys):
                    fragments.append(self.node(name, prefix + "/" + escape(field)))
        fragments = sorted(set(fragments) | set(extra))
        # digest semantic values, with their own paths/pointers; no source text copy.
        signature = [{"document": self.nodes[n]["document"], "pointer": self.nodes[n]["pointer"],
                      "value_sha256": self.nodes[n]["value_sha256"]} for n in fragments]
        key = "s" + digest(signature)[:20]
        self.scopes[key] = {"scope_digest": digest(signature), "fragment_nodes": fragments,
                            "selected_values_available_through_original_nodes": True,
                            "semantic_scope_exhaustiveness_verified": False}
        return key

    def by_id(self, name, value):
        if name not in self.id_indexes:
            index = defaultdict(list)
            for node, pointer in walk(self.read(name)):
                if isinstance(node, dict):
                    for field in ("id", "citation_id", "evidence_id"):
                        if isinstance(node.get(field), str):
                            index[node[field]].append(pointer)
            self.id_indexes[name] = {k: sorted(set(v)) for k, v in index.items()}
        candidates = []
        # Explicit keyed citation/evidence tables are also real named references.
        for table in ("citations", "evidence", "new_evidence", "inherited_evidence"):
            obj = self.read(name).get(table)
            if isinstance(obj, dict) and value in obj:
                candidates.append("/" + table + "/" + escape(value))
            elif isinstance(obj, list):
                candidates += ["/" + table + "/" + str(i) for i, item in enumerate(obj)
                    if isinstance(item, dict) and value in [item.get(k) for k in ("id", "citation_id", "evidence_id")]]
        if not candidates:
            candidates = self.id_indexes[name].get(value, [])
        candidates = sorted(set(candidates))
        if len(candidates) != 1:
            raise ValueError("Unresolved or ambiguous local evidence ID: " + str(value))
        return candidates[0]


class Adapter:
    def __init__(self, root, helper, target=None, baselines=()):
        self.store = Store(root)
        self.helper, self.target, self.baselines = helper, target, list(baselines)
        self.references, self.atoms, self.records, self.edges = {}, {}, [], {}
        self.comparison_cache = {}
        self.active_typed_edges = set()
        self.scope_resolution_cache = {}

    def edge(self, origin):
        key = "e" + digest(origin)[:20]
        self.edges[key] = origin
        return key

    def issue(self, unit, code, detail=None):
        item = {"code": code}
        if detail is not None:
            item["detail"] = str(detail)
        if item not in unit["issues"]:
            unit["issues"].append(item)

    def unit(self, record, name, pointer, kind, scopes=(), relation=None):
        key = "a" + digest([record["id"], name, pointer])[:20]
        unit = {"id": key, "record_id": record["id"], "atom_node": self.store.node(name, pointer),
                "scope_set": self.store.scope(name, pointer, scopes), "kind": kind,
                "reference_ids": [], "evidence_edges": [], "issues": [],
                "dependency_status": "unknown", "runtime_verified": False,
                "behavior_compatibility_verified": False, "coding_status_changed": False}
        if relation:
            unit["relation"] = relation
        if unit["scope_set"] not in self.scope_resolution_cache:
            resolved, errors = set(), []
            for sid in self.store.scopes[unit["scope_set"]]["fragment_nodes"]:
                metadata = self.store.nodes[sid]
                scoped = at(self.store.read(metadata["document"]), metadata["pointer"])
                for child, _ in walk(scoped):
                    if isinstance(child, dict) and "artifact_path" in child and ("pointer" in child or "source_pointer" in child):
                        try:
                            target_name, target_pointer, _ = self.store.typed(child)
                            resolved.add(self.store.node(target_name, target_pointer))
                        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
                            errors.append(str(exc))
            self.scope_resolution_cache[unit["scope_set"]] = (sorted(resolved), errors)
        resolved, errors = self.scope_resolution_cache[unit["scope_set"]]
        if resolved:
            unit["resolved_scope_reference_nodes"] = resolved
        for error in errors:
            self.issue(unit, "invalid_original_scope_reference", error)
        self.atoms[key] = unit
        record["atom_ids"].append(key)
        return unit

    def typed_support(self, unit, ref, historical=False):
        edge = self.edge({"kind": "typed_artifact_reference", "original_evidence_tuple": ref,
                          "historical_context": historical})
        unit["evidence_edges"].append(edge)
        if edge in self.active_typed_edges:
            self.issue(unit, "cyclic_typed_evidence_reference")
            return
        try:
            self.active_typed_edges.add(edge)
            name, pointer, _ = self.store.typed(ref)
            self.edges[edge]["resolved_original_node"] = self.store.node(name, pointer)
            self.extract(unit, name, pointer, edge, historical=historical)
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            self.issue(unit, "invalid_claim_evidence_reference", exc)
        finally:
            self.active_typed_edges.discard(edge)

    def extract(self, unit, name, pointer, edge, seen=None, historical=False):
        historical = historical or self.historical_ancestry(name, pointer)
        seen = set() if seen is None else seen
        identity = (name, pointer, historical)
        if identity in seen:
            return
        seen.add(identity)
        node = at(self.store.read(name), pointer)
        if isinstance(node, dict):
            historical = historical or (node.get("payload_status") == "metadata_only"
                or node.get("evidence_role") == "historical_comparison" or node.get("supports_current_behavior") is False)
            path = next((node[k] for k in ("path", "file", "source_file", "archive_member")
                         if isinstance(node.get(k), str) and node[k].endswith(".lua")), None)
            if path:
                self.citation(unit, name, pointer, node, path, edge, historical)
                return
            if "artifact_path" in node and ("pointer" in node or "source_pointer" in node):
                self.typed_support(unit, node, historical=historical)
                return
            for key, value in node.items():
                if key in PAYLOAD_FIELDS | SKIP_LINKS:
                    continue
                if key in ID_LINKS and isinstance(value, list):
                    for item in value:
                        try:
                            self.extract(unit, name, self.store.by_id(name, item), edge, seen, historical)
                        except (ValueError, KeyError, TypeError) as exc:
                            self.issue(unit, "unresolved_local_evidence_id", exc)
                    continue
                if isinstance(value, (dict, list)):
                    self.extract(unit, name, pointer + "/" + escape(key), edge, seen,
                                 historical or key == "comparison_citations")
        elif isinstance(node, list):
            for i in range(len(node)):
                self.extract(unit, name, pointer + "/" + str(i), edge, seen, historical)

    def historical_ancestry(self, name, pointer):
        if not pointer.startswith("#L") and "comparison_citations" in pointer_tokens(pointer):
            return True
        return any(isinstance(value, dict) and (value.get("payload_status") == "metadata_only"
                   or value.get("evidence_role") == "historical_comparison"
                   or value.get("supports_current_behavior") is False)
                   for value, _ in self.store.ancestors(name, pointer))

    def provenance(self, name, pointer, node, fallback_origin=None):
        if fallback_origin == "non_vanilla":
            return "non_vanilla"
        ancestors = [value for value, _ in self.store.ancestors(name, pointer) if isinstance(value, dict)]
        ancestors.append(node)  # includes Legacy's joined locator metadata
        positive, foreign, ambiguous_repository = False, False, False
        for ancestor in ancestors:
            metadata = [ancestor]
            if isinstance(ancestor.get("source_scope"), dict):
                metadata.append(ancestor["source_scope"])
            for item in metadata:
                for key in ("source_kind", "source_type"):
                    kind = item.get(key)
                    if isinstance(kind, str):
                        lower = kind.strip().lower()
                        if lower == "mod" or any(marker in lower for marker in
                            ("mod_source", "third_party", "case_code", "prior_analysis_report", "sora")):
                            foreign = True
                        positive = positive or lower in VANILLA_SOURCE_KINDS
                for key in ("repository", "source_repository"):
                    repo = item.get(key)
                    if isinstance(repo, str) and repo.strip():
                        identity = repository_identity(repo)
                        if identity in TRUSTED_REPOSITORIES:
                            positive = True
                        elif identity is not None:
                            foreign = True
                        else:
                            ambiguous_repository = True
                url = item.get("url")
                if isinstance(url, str) and url.strip():
                    parsed = urlsplit(url)
                    identity = repository_identity(url)
                    if identity in TRUSTED_REPOSITORIES:
                        positive = True
                    elif parsed.hostname == "github.com":
                        foreign = True
                    else:
                        ambiguous_repository = True
                for key in ("snapshot_id", "native_snapshot_id"):
                    stamp = item.get(key)
                    positive = positive or isinstance(stamp, str) and stamp.upper().startswith("KLEI-")
        if foreign:
            return "non_vanilla"
        if ambiguous_repository:
            return "unknown_origin"
        return "vanilla" if positive or fallback_origin == "vanilla" else "unknown_origin"

    def citation(self, unit, name, pointer, node, path, edge, historical=False, forced_origin=None):
        historical = historical or self.historical_ancestry(name, pointer)
        nid = self.store.node(name, pointer)
        key = "r" + digest([nid, historical, forced_origin])[:20]
        if key not in self.references:
            origin = self.provenance(name, pointer, node, fallback_origin=forced_origin)
            original = {k: node[k] for k in ("path", "file", "source_file", "archive_member", "file_sha256",
                "cited_file_sha256", "range_sha256", "cited_range_sha256", "line_start", "line_end", "start_line", "end_line",
                "symbol", "function", "snapshot_id", "native_snapshot_id", "source_kind", "source_type",
                "range_hash_convention", "hash_convention", "range_hash_scheme", "range_digest_scheme",
                "citation_scheme", "range_hash_verified", "file_hash_verified", "payload_status", "evidence_role",
                "supports_current_behavior", "url", "repository", "commit") if k in node}
            result = {"citation_node": nid, "scope_set": self.store.scope(name, pointer),
                      "original_evidence_tuple": original, "provenance": origin,
                      "binding_class": "unknown", "payload_status": "not_embedded",
                      "source_identity_checked": False,
                      "source_comparison": {"status": "unknown", "reasons": []},
                      "current_evidence_admitted": False, "runtime_verified": False}
            if historical:
                result["binding_class"] = "historical"
                result["source_comparison"]["reasons"].append("historical_metadata_only_never_current_evidence")
            elif origin == "non_vanilla":
                result["binding_class"] = "non_vanilla"
                result["source_comparison"]["reasons"].append("non_vanilla_source_not_compared_to_game_zip")
            elif origin == "unknown_origin":
                result["source_comparison"]["reasons"].append("original_source_provenance_unknown")
            else:
                self.compare_citation(result, node, path)
            self.references[key] = result
        if key not in unit["reference_ids"]:
            unit["reference_ids"].append(key)
        edge_record = self.edges[edge]
        edge_record.setdefault("resolved_citation_ids", [])
        if key not in edge_record["resolved_citation_ids"]:
            edge_record["resolved_citation_ids"].append(key)
        return key

    @staticmethod
    def hash_variants(raw, start, end):
        lines = raw.decode("utf-8").splitlines()
        if type(start) is not int or type(end) is not int or not 0 < start <= end <= len(lines):
            raise ValueError("Invalid committed source range")
        joined = "\n".join(lines[start - 1:end]).encode()
        raw_range = b"".join(raw.splitlines(keepends=True)[start - 1:end])
        return {"LF_join_no_final_LF": joined, "LF_join_with_final_LF": joined + b"\n",
                "raw_original_line_terminators": raw_range}

    def compare_citation(self, result, node, path):
        reasons = result["source_comparison"]["reasons"]
        file_hash = node.get("file_sha256", node.get("cited_file_sha256"))
        range_hash = node.get("range_sha256", node.get("cited_range_sha256"))
        start, end = node.get("line_start", node.get("start_line")), node.get("line_end", node.get("end_line"))
        if path.startswith("logical:vanilla-snapshot/"):
            path = path[len("logical:vanilla-snapshot/"):]
        if not path.startswith("scripts/"):
            path = "scripts/" + path
        try:
            self.helper.member_name(path)
        except ValueError:
            reasons.append("invalid_source_member")
            return
        if not isinstance(file_hash, str) or not HASH.fullmatch(file_hash):
            reasons.append("missing_file_byte_commitment")
            return
        if not isinstance(range_hash, str) or not HASH.fullmatch(range_hash):
            reasons.append("missing_range_byte_commitment_not_synthesized_from_current_lines")
            return
        if type(start) is not int or type(end) is not int or not 0 < start <= end:
            reasons.append("missing_exact_committed_range")
            return
        result["binding_class"] = "exact_commitments"
        has_slot = False
        for field in PAYLOAD_FIELDS & node.keys():
            payload = node[field]
            if isinstance(payload, dict) and "$dst_source_payload_slot" in payload:
                has_slot = True
                result["payload_status"] = "slot_unrestored"
            elif isinstance(payload, str):
                try:
                    modes = self.hash_variants(payload.encode(), 1, len(payload.splitlines()))
                    if range_hash not in {sha(raw) for raw in modes.values()} or len(payload.splitlines()) != end - start + 1:
                        result["binding_class"] = "unknown"
                        reasons.append("embedded_payload_range_hash_mismatch")
                        return
                    result["payload_status"] = "embedded_range_hash_verified"
                except (ValueError, UnicodeError):
                    result["binding_class"] = "unknown"
                    reasons.append("invalid_embedded_payload")
                    return
        if has_slot:
            result["binding_class"] = "unrestored_payload"
        if self.target is None:
            reasons.append("target_not_supplied")
            return
        target_raw = self.target.raw(path)
        if target_raw is None:
            result["source_comparison"] = {"status": "missing", "reasons": ["target_member_missing"]}
            return
        old = next((a for a in self.baselines if a.raw(path) is not None and sha(a.raw(path)) == file_hash), None)
        original_raw = target_raw if sha(target_raw) == file_hash else old.raw(path) if old else None
        if original_raw is None:
            reasons.append("missing_matching_old_source")
            result["source_comparison"]["target_file_sha256"] = sha(target_raw)
            return
        try:
            modes = self.hash_variants(original_raw, start, end)
        except (ValueError, UnicodeError) as exc:
            result["binding_class"] = "unknown"
            reasons.append("invalid_committed_range: " + str(exc))
            return
        matched_modes = [mode for mode, raw in modes.items() if sha(raw) == range_hash]
        if not matched_modes:
            result["binding_class"] = "unknown"
            reasons.append("original_range_hash_mismatch_no_identity_repair")
            return
        ref = {"id": "derived_comparison_only", "source_file": path, "file_sha256": file_hash,
               "range_sha256": sha(modes["LF_join_no_final_LF"]), "line_start": start, "line_end": end,
               "symbols": [node[k] for k in ("symbol", "function") if isinstance(node.get(k), str) and node[k].strip()]}
        cache_key = digest(ref)
        if cache_key not in self.comparison_cache:
            raw_result = self.helper.compare_reference(ref, old, self.target)
            self.comparison_cache[cache_key] = {k: raw_result[k] for k in ("status", "reasons", "target_locator",
                "target_file_sha256", "source_identity_reusable", "navigation_limitation") if k in raw_result}
        compared = dict(self.comparison_cache[cache_key])
        internal = compared.pop("status")
        compared["status"] = {"byte_identical": "same", "relocation_required": "changed",
                              "review_required": "changed", "missing": "missing", "unknown": "unknown"}[internal]
        compared["detail_status"] = internal
        compared["original_range_hash_modes_verified"] = matched_modes
        compared["comparison_normalization"] = {"mode": "LF_join_no_final_LF", "derived_range_sha256": ref["range_sha256"],
                                                  "original_evidence_tuple_unchanged": True}
        result["source_comparison"] = compared
        result["source_identity_checked"] = internal in ("byte_identical", "relocation_required", "review_required")

    def adapt_legacy(self, row, record, value):
        unit = self.unit(record, row["file"], row["pointer"], value.get("entry_type", "legacy_entry_unit"),
                         relation="original_whole_entry_unit_no_invented_semantic_split")
        sources_doc = "data/sources.json"
        try:
            sources = self.store.read(sources_doc)["sources"]
        except (OSError, ValueError, KeyError) as exc:
            self.issue(unit, "legacy_source_registry_unavailable", exc)
            return
        for i, source in enumerate(value.get("sources", [])):
            pointer = row["pointer"] + "/sources/" + str(i)
            edge = self.edge({"kind": "legacy_source_id", "source_node": self.store.node(row["file"], pointer),
                              "source_id": source.get("source_id")})
            unit["evidence_edges"].append(edge)
            matching = [(j, s) for j, s in enumerate(sources) if s.get("id") == source.get("source_id")]
            if len(matching) != 1:
                self.issue(unit, "legacy_source_id_missing_or_ambiguous", source.get("source_id"))
                continue
            j, registry = matching[0]
            self.edges[edge]["registry_node"] = self.store.node(sources_doc, "/sources/" + str(j))
            origin = "vanilla" if registry.get("source_type", registry.get("type")) == "vanilla_source_snapshot" else "non_vanilla"
            locators = source.get("locator_structured", [])
            if origin == "non_vanilla":
                self.citation(unit, row["file"], pointer, source, "unknown.lua", edge, forced_origin="non_vanilla")
                continue
            ranges = [loc for loc in locators if loc.get("type") == "source_lines"]
            if not ranges:
                self.issue(unit, "legacy_no_committed_range", source.get("source_id"))
            fingerprints = registry.get("verification", {}).get("file_fingerprints", [])
            for k, loc in enumerate(locators):
                if loc.get("type") != "source_lines":
                    continue
                # Retain original locator, registry fingerprint separately; never
                # invent its missing range hash from the current source lines.
                leaf = dict(loc)
                matches = [f for f in fingerprints if f.get("path", "").endswith("/scripts/" + loc.get("file", ""))]
                if len(matches) == 1:
                    leaf["file_sha256"] = matches[0]["sha256"]
                leaf["line_start"], leaf["line_end"] = loc.get("start_line"), loc.get("end_line")
                rid = self.citation(unit, row["file"], pointer + "/locator_structured/" + str(k), leaf,
                                   loc.get("file", "unknown.lua"), edge, forced_origin="vanilla")
                if len(matches) == 1:
                    fp_index = fingerprints.index(matches[0])
                    self.references[rid]["file_commitment_joined_from_registry_node"] = self.store.node(sources_doc,
                        "/sources/" + str(j) + "/verification/file_fingerprints/" + str(fp_index))

    def adapt_ai(self, row, record, value):
        main = self.unit(record, row["file"], row["pointer"] + "/native_fact", "NSF")
        map_name = "data/native001/canonical-native001-research-map.json"
        try:
            mapping = self.store.read(map_name)
            choices = [(i, x) for i, x in enumerate(mapping["entries"]) if x.get("canonical_id") == row["id"]]
            if len(choices) != 1 or row["id"] not in value.get("research_evidence_refs", []):
                raise ValueError("AI research mapping missing or ambiguous")
            index, mapping_row = choices[0]
            main["research_map_node"] = self.store.node(map_name, "/entries/" + str(index))
            required = mapping_row.get("direct_native_fact_support", [])
            inference_ids = mapping_row.get("engineering_inference_support", [])
            clarification_ids = [loc.get("candidate_id") for loc in mapping_row.get("clarification_support", []) if isinstance(loc, dict)]
            all_ids = list(dict.fromkeys(mapping_row.get("research_candidate_ids", []) + required + inference_ids + clarification_ids))
            for candidate_id in all_ids:
                selected = [(i, loc) for i, loc in enumerate(mapping_row["source_locators"]) if loc.get("candidate_id") == candidate_id]
                locator_field = "source_locators"
                if not selected and candidate_id in clarification_ids:
                    selected = [(i, loc) for i, loc in enumerate(mapping_row.get("clarification_support", [])) if loc.get("candidate_id") == candidate_id]
                    locator_field = "clarification_support"
                if len(selected) != 1:
                    if candidate_id in required:
                        self.issue(main, "ai_source_candidate_mapping_missing_or_ambiguous", candidate_id)
                    else:
                        field = "research_candidate_ids" if candidate_id in mapping_row.get("research_candidate_ids", []) else "engineering_inference_support"
                        position = mapping_row[field].index(candidate_id)
                        context = self.unit(record, map_name, "/entries/" + str(index) + "/" + field + "/" + str(position),
                            "research_context_reference", self.store.scopes[main["scope_set"]]["fragment_nodes"],
                            relation="AI_related_ID_without_explicit_source_locator")
                        self.issue(context, "context_id_has_no_unique_explicit_artifact_locator", candidate_id)
                    continue
                i, loc = selected[0]
                ref = {"artifact_path": loc.get("artifact_path"), "sha256": loc.get("artifact_sha256"),
                       "pointer": loc.get("source_pointer")}
                try:
                    name, pointer, triple = self.store.typed(ref)
                    original = at(self.store.read(name), pointer)
                    if original.get("candidate_id") != candidate_id:
                        raise ValueError("AI original candidate ID mismatch")
                    scope_fragments = self.store.scopes[main["scope_set"]]["fragment_nodes"]
                    role = ("AI_direct_native_fact_support" if candidate_id in required else
                            "AI_engineering_context_not_per_decision_binding" if candidate_id in inference_ids else
                            "AI_clarification_context" if candidate_id in clarification_ids else "AI_research_context_only")
                    original_unit = self.unit(record, name, pointer, original.get("classification", "unknown"), scope_fragments,
                                              relation=role)
                    original_unit["research_map_locator_node"] = self.store.node(map_name,
                        "/entries/" + str(index) + "/" + locator_field + "/" + str(i))
                    self.typed_support(original_unit, triple)
                    if candidate_id in required:
                        main.setdefault("support_atom_ids", []).append(original_unit["id"])
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    self.issue(main, "invalid_ai_candidate_reference", exc)
            if not required:
                self.issue(main, "ai_no_direct_fact_mapping")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.issue(main, "ai_research_map_invalid", exc)
        # Recommendations do not inherit an entry's NSF citations as proof.
        for field, items_key in (("ai_coding_impact", "decisions"), ("recommended_reasoning", "steps")):
            block = value.get(field, {})
            for i in range(len(block.get(items_key, []))):
                unit = self.unit(record, row["file"], row["pointer"] + "/" + field + "/" + items_key + "/" + str(i),
                                 block.get("claim_type", "REC"))
                self.issue(unit, "recommendation_no_per_atom_source_binding_no_NSF_borrowing")

    def adapt_core(self, row, record, value):
        for i, claim in enumerate(value.get("claims", [])):
            unit = self.unit(record, row["file"], row["pointer"] + "/claims/" + str(i), claim.get("kind", "unknown"))
            refs = claim.get("evidence_refs", [])
            if not refs:
                self.issue(unit, "claim_has_no_own_evidence_refs_entry_refs_not_borrowed")
            for ref in refs:
                self.typed_support(unit, ref)

    def finalize_unit(self, unit, stack=()):
        if unit["id"] in stack:
            self.issue(unit, "cyclic_atom_support")
            return "unknown"
        states = [self.references[r]["source_comparison"]["status"] for r in unit["reference_ids"]]
        classes = [self.references[r]["binding_class"] for r in unit["reference_ids"]]
        for support in unit.get("support_atom_ids", []):
            states.append(self.finalize_unit(self.atoms[support], stack + (unit["id"],)))
            classes += self.atoms[support]["binding_classes"]
        if unit["issues"] or not states or any(c in ("historical", "unknown", "unrestored_payload", "non_vanilla") for c in classes):
            state = "unknown"
        else:
            state = next((s for s in ("missing", "changed", "unknown", "same") if s in states), "unknown")
        unit["source_status"] = state
        unit["binding_classes"] = sorted(set(classes))
        checked = [self.references[r]["source_identity_checked"] for r in unit["reference_ids"]]
        for support in unit.get("support_atom_ids", []):
            checked.append(self.atoms[support]["all_source_identities_checked"])
        unit["all_source_identities_checked"] = bool(checked) and all(checked)
        unit["atom_binding_status"] = ("fully_exact" if states and set(classes) == {"exact_commitments"} and not unit["issues"] and unit["all_source_identities_checked"]
            else "partially_exact" if any(checked) and "exact_commitments" in classes
            else "unknown" if unit["issues"] else "historical_only" if set(classes) == {"historical"}
            else "non_vanilla_only" if classes and set(classes) == {"non_vanilla"} else "unknown")
        return state

    def run(self):
        catalog = self.store.read("CATALOG.json")
        ignored = Counter()
        seen = set()
        for row in catalog["entries"]:
            if row.get("family") not in FAMILIES:
                ignored[row.get("family", "unknown")] += 1
                continue
            if row["id"] in seen:
                raise ValueError("Duplicate selected catalog ID")
            seen.add(row["id"])
            value = at(self.store.read(row["file"]), row["pointer"])
            if value.get("id") != row["id"]:
                raise ValueError("Catalog pointer identity mismatch")
            record = {"id": row["id"], "family": row["family"], "record_node": self.store.node(row["file"], row["pointer"]),
                      "original_record_sha256": digest(value), "scope_set": self.store.scope(row["file"], row["pointer"]),
                      "catalog_node": self.store.node("CATALOG.json", "/entries/" + str(catalog["entries"].index(row))),
                      "original_states": {k: value.get(k, row.get(k)) for k in ("knowledge_status", "retrieval_status", "coding_status", "status")},
                      "atom_ids": []}
            self.records.append(record)
            if row["family"] == "legacy":
                self.adapt_legacy(row, record, value)
            elif row["family"] == "native_ai":
                self.adapt_ai(row, record, value)
            else:
                self.adapt_core(row, record, value)
        for unit in self.atoms.values():
            self.finalize_unit(unit)
        checklist = []
        for record in self.records:
            units = [self.atoms[i] for i in record["atom_ids"]]
            counts = Counter(u["atom_binding_status"] for u in units)
            record["atom_binding_counts"] = dict(counts)
            record["source_status_counts"] = dict(Counter(u["source_status"] for u in units))
            for unit in units:
                if unit["source_status"] != "same":
                    checklist.append({"record_id": record["id"], "atom_id": unit["id"], "status": unit["source_status"],
                                      "action": "review_this_atom_sources_and_unknown_consumers"})
        per_family = {}
        for family in FAMILIES:
            records = [r for r in self.records if r["family"] == family]
            atoms = [self.atoms[a] for r in records for a in r["atom_ids"]]
            refs = {ref for atom in atoms for ref in atom["reference_ids"]}
            per_family[family] = {"records": len(records), "atoms": len(atoms), "unique_citations": len(refs),
                "atom_binding_counts": dict(Counter(a["atom_binding_status"] for a in atoms)),
                "reference_binding_counts": dict(Counter(self.references[r]["binding_class"] for r in refs)),
                "reference_source_status_counts": dict(Counter(self.references[r]["source_comparison"]["status"] for r in refs)),
                "references_with_original_byte_identity_checked": sum(self.references[r]["source_identity_checked"] for r in refs),
                "records_with_any_exact_atom": sum(any(self.atoms[a]["atom_binding_status"] == "fully_exact" for a in r["atom_ids"]) for r in records)}
        return {"schema": SCHEMA, "input_knowledge_root": str(self.store.root),
                "input_manifest_sha256": self.store.manifest_sha256,
                "target": self.target.identity() if self.target else None,
                "baselines": [a.identity() for a in self.baselines],
                "summary": {"records": len(self.records), "atoms": len(self.atoms), "unique_citations": len(self.references),
                            "families": per_family, "ignored_catalog_families": dict(ignored)},
                "documents": self.store.documents, "nodes": self.store.nodes, "scope_sets": self.store.scopes,
                "evidence_edges": self.edges, "source_references": self.references, "atoms": self.atoms,
                "records": self.records, "local_review_checklist": checklist,
                "boundaries": {"canonical_modified": False, "payload_restored": False, "coding_hold_changed": False,
                    "runtime_verified": False, "behavior_compatibility_verified": False, "dynamic_consumer_closure": "unknown",
                    "same_means": "only_original_file_and_range_identity_not_behavior_or_current_admission",
                    "semantic_scope": "Selected labelled scope values are traceable, not proven semantically exhaustive; full original record/atom/citation nodes remain resolvable without truncation."}}


def main(argv=None, compatibility_helper=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", type=Path, required=True)
    if compatibility_helper is None:
        parser.add_argument("--compatibility-helper", type=Path, required=True)
    else:
        parser.set_defaults(compatibility_helper=Path(compatibility_helper))
    parser.add_argument("--target", type=Path)
    parser.add_argument("--target-label")
    parser.add_argument("--baseline", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True, help="New sidecar JSON; never overwrites")
    args = parser.parse_args(argv)
    archives = []
    try:
        helper, identity = load_helper(args.compatibility_helper)
        target = helper.Archive(args.target, args.target_label) if args.target else None
        if target:
            archives.append(target)
        baselines = []
        for path in args.baseline:
            source = helper.Archive(path)
            archives.append(source)
            baselines.append(source)
        result = Adapter(args.knowledge_root, helper, target, baselines).run()
        result["comparison_helper"] = identity
        output = write_sidecar(args.output, result)
        print(json.dumps({**output, "summary": result["summary"]}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, IndexError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": {"code": "LEGACY_ADAPTER_INPUT_ERROR", "message": str(exc)},
                          "canonical_modified": False}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        for archive in archives:
            archive.close()


if __name__ == "__main__":
    raise SystemExit(main())

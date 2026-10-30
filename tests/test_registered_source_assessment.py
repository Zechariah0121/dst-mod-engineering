"""Synthetic committed packages and explicit ZIPs; no game or installed runtime."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import source_compatibility as compat


class RegisteredAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="registered-assessment-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.knowledge = self.root / "knowledge"
        self.knowledge.mkdir()
        self.output = self.root / "report.json"
        self.files = {"scripts/alpha.lua": b"function Alpha()\nreturn 1\nend\n",
                      "scripts/beta.lua": b"function Beta()\nreturn 2\nend\n"}
        self.baseline = self.archive("old.zip", self.files)
        self.target = self.archive("future.zip", {**self.files, "scripts/new.lua": b"return 3\n"})
        self.commitments = {}
        rows, catalog = [], []
        for topic in ("alpha", "beta"):
            entry_id = topic.upper()
            source = "scripts/" + topic + ".lua"
            entry = {"id": entry_id, "title": topic, "aliases": [], "engineering_question": "fixture?",
                     "knowledge_status": "research", "retrieval_status": "restricted", "coding_status": "hold",
                     "scope": {"source_epoch": "old-fixture", "limits": "static only"},
                     "claims": [{"id": entry_id + "-C1", "kind": "NSF", "statement": "Fixture only",
                                 "evidence_refs": ["source"]}],
                     "api_contracts": [{"symbol": topic.title(), "source_file": source,
                        "visibility": "global", "parameters": [], "returns": [], "preconditions": [],
                        "side_effects": [], "lifecycle": [], "evidence_refs": ["source"], "unknowns": []}],
                     "mechanism_steps": [{"step": 1, "description": "Fixture step", "evidence_refs": ["source"]}],
                     "unknowns": ["Native dependencies not tested"]}
            document = {"schema_version": "dst-mechanism-research/1", "topic": topic + " bounded source chain",
                "source_epoch": "old-fixture", "archive_sha256": compat.file_sha(self.baseline),
                "entries": [entry], "source_references": [{"id": "source", "source_file": source,
                    "file_sha256": compat.sha(self.files[source]), "line_start": 1, "line_end": 3,
                    "range_sha256": compat.sha(b"\n".join(self.files[source].splitlines())), "symbols": [topic.title()]}],
                "queries": [{"query": topic, "expected_entry_ids": [entry_id], "purpose": "review"}],
                "limitations": ["No behavior proof"]}
            name = "candidates/" + topic + ".json"
            digest = self.write(name, document)
            review_name = "reviews/" + topic + ".json"
            review_digest = self.write(review_name, {"candidate_sha256": digest, "runtime_verified": False})
            rows.append({"topic": topic, "file": name, "sha256": digest, "entry_ids": [entry_id],
                "record_sha256": {entry_id: compat.sha(json.dumps(entry, ensure_ascii=False, sort_keys=True,
                                                          separators=(",", ":")).encode())},
                "review": {"file": review_name, "sha256": review_digest}})
            catalog.append({"id": entry_id, "title": topic, "family": "native_mechanism", "file": name,
                "pointer": "/entries/0", **{key: entry[key] for key in
                    ("knowledge_status", "retrieval_status", "coding_status")}})
        self.registry = {"schema_version": "dst-family-registry/1", "families": [
            {"name": name, "documents": []} for name in ("legacy", "native_ai", "native_core")] + [
            {"name": "native_mechanism", "documents": rows}]}
        self.catalog = {"entries": catalog, "counts": {"native_mechanism": 2}}
        self.refresh()

    def archive(self, name, files):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            for member, raw in files.items():
                archive.writestr(member, raw)
        return path

    def write(self, name, value):
        path = self.knowledge / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
        path.write_bytes(raw)
        self.commitments[name] = compat.sha(raw)
        return self.commitments[name]

    def refresh(self):
        self.write("FAMILY-REGISTRY.json", self.registry)
        self.write("CATALOG.json", self.catalog)
        self.write("PACKAGE-MANIFEST.json", {"files": [
            {"path": name, "sha256": digest} for name, digest in self.commitments.items()
            if name != "PACKAGE-MANIFEST.json"]})

    def run_assessment(self, baseline=True, output=None):
        args = ["assess-registered", "--knowledge-root", str(self.knowledge), "--target", str(self.target),
                "--target-label", "future-unregistered-version", "--output", str(output or self.output)]
        if baseline:
            args.extend(["--baseline", str(self.baseline)])
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            code = compat.main(args)
        return code, errors.getvalue()

    def test_multi_topic_atoms_and_readonly_inputs(self):
        # Invalid unregistered JSON must not be parsed or assessed.
        self.write("candidates/unregistered.json", {"schema_version": "not-a-candidate"})
        before = {p: compat.file_sha(p) for p in self.knowledge.rglob("*") if p.is_file()}
        self.assertEqual(self.run_assessment()[0], 0)
        after = {p: compat.file_sha(p) for p in self.knowledge.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        report = compat.read_json(self.output)
        self.assertEqual([t["topic"] for t in report["topic_summary"]], ["alpha", "beta"])
        self.assertEqual(report["reference_status_counts"], {"byte_identical": 2})
        self.assertEqual(report["archive_delta"]["added"], ["scripts/new.lua"])
        self.assertFalse(report["registration"]["unregistered_candidates_scanned"])
        for candidate in report["candidates"]:
            entry = candidate["entries"][0]
            self.assertEqual(entry["scope"]["source_epoch"], "old-fixture")
            self.assertEqual(entry["unknowns"], ["Native dependencies not tested"])
            for kind in ("claims", "api_contracts", "mechanism_steps"):
                self.assertEqual(entry[kind][0]["dependency_status"], "unknown")
                self.assertFalse(entry[kind][0]["runtime_verified"])
        self.assertFalse(report["canonical_modified"])

    def test_bad_candidate_hash_fails_without_partial_output(self):
        (self.knowledge / "candidates/beta.json").write_text("{}")
        code, errors = self.run_assessment()
        self.assertEqual(code, 2)
        self.assertIn("hash mismatch", errors)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob(".source-assessment-*")), [])

    def test_bad_registry_commitment(self):
        (self.knowledge / "FAMILY-REGISTRY.json").write_text("{}")
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())

    def test_bad_source_hash_even_in_recommitted_candidate_is_rejected(self):
        row = self.registry["families"][-1]["documents"][0]
        doc = compat.read_json(self.knowledge / row["file"])
        doc["source_references"][0]["file_sha256"] = "not-a-hash"
        row["sha256"] = self.write(row["file"], doc)
        self.refresh()
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())

    def test_missing_committed_review_dependency_is_rejected(self):
        row = self.registry["families"][-1]["documents"][0]
        digest = self.write("reviews/prior.json", {"runtime_verified": False})
        row["review"]["dependencies"] = [{"file": "reviews/prior.json", "sha256": digest}]
        self.refresh()
        (self.knowledge / "reviews/prior.json").unlink()
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())

    def test_unmatched_baseline_remains_unknown(self):
        self.baseline = self.archive("other-old.zip", {"scripts/other.lua": b"return 0\n"})
        self.assertEqual(self.run_assessment()[0], 0)
        report = compat.read_json(self.output)
        self.assertEqual(report["reference_status_counts"], {"unknown": 2})
        self.assertIn("provided_baseline_archive_does_not_match_candidate",
                      report["candidates"][0]["reference_states"][0]["reasons"])

    def test_catalog_omission_and_duplicate_registration(self):
        self.catalog["entries"].pop()
        self.refresh()
        self.assertEqual(self.run_assessment()[0], 2)
        self.registry["families"][-1]["documents"].append(copy.deepcopy(self.registry["families"][-1]["documents"][0]))
        self.refresh()
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())

    def test_unsafe_registered_path_is_rejected(self):
        self.registry["families"][-1]["documents"][0]["file"] = "../escape.json"
        self.refresh()
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())

    def test_missing_old_baseline_and_new_version_change_remain_unknown(self):
        changed = {**self.files, "scripts/alpha.lua": b"function Alpha()\nreturn 99\nend\n"}
        self.target = self.archive("changed.zip", changed)
        self.assertEqual(self.run_assessment(baseline=False)[0], 0)
        report = compat.read_json(self.output)
        refs = report["candidates"][0]["reference_states"]
        self.assertEqual(refs[0]["status"], "unknown")
        self.assertIn("missing_matching_old_source", refs[0]["reasons"])
        self.assertEqual(report["candidates"][1]["reference_states"][0]["status"], "byte_identical")
        self.assertIsNone(report["archive_delta"])

    def test_new_version_change_with_matching_baseline_requires_review(self):
        self.target = self.archive("changed.zip", {**self.files, "scripts/alpha.lua": b"return 99\n"})
        self.assertEqual(self.run_assessment()[0], 0)
        report = compat.read_json(self.output)
        self.assertEqual(report["reference_status_counts"], {"byte_identical": 1, "review_required": 1})
        self.assertEqual(report["difference_summary"]["entries_requiring_source_followup"], 1)

    def test_output_overwrite_and_knowledge_writes_refused(self):
        self.output.write_text("preserve")
        self.assertEqual(self.run_assessment()[0], 2)
        self.assertEqual(self.output.read_text(), "preserve")
        output = self.knowledge / "new-sidecar.json"
        self.assertEqual(self.run_assessment(output=output)[0], 2)
        self.assertFalse(output.exists())

    def test_atomic_publication_failure_removes_staging_file(self):
        with mock.patch.object(compat.os, "link", side_effect=OSError("publication failure")):
            self.assertEqual(self.run_assessment()[0], 2)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob(".source-assessment-*")), [])

    def test_unified_entrypoint_from_other_working_directory(self):
        run = subprocess.run([sys.executable, "-B", "-I", str(REPO / "run_kb.py"), "maintain-sources",
            "assess-registered", "--knowledge-root", str(self.knowledge), "--target", str(self.target),
            "--output", str(self.output)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(compat.read_json(self.output)["registration"]["entry_count"], 2)


if __name__ == "__main__":
    unittest.main()

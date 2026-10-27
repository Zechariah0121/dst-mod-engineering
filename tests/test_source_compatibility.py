"""Synthetic ZIPs only. All writes stay in this compatibility directory."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import warnings
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
import source_compatibility as compat
import catalog_fallback_policy as policy


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".synthetic-", dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.files = {"scripts/producer.lua": b"function Producer(x)\n    return x + 1\nend\n",
                      "scripts/consumer.lua": b"function Consumer(x)\n    return Producer(x)\nend\n"}
        self.old = self.archive("baseline.zip", self.files)
        self.candidate = self.root / "candidate.json"
        refs = []
        for key, name, symbol in (("definition", "scripts/producer.lua", "Producer"),
                                  ("consumer", "scripts/consumer.lua", "Consumer")):
            lines = self.files[name].decode().splitlines()
            refs.append({"id": key, "source_file": name, "file_sha256": compat.sha(self.files[name]),
                         "line_start": 1, "line_end": len(lines),
                         "range_sha256": compat.sha("\n".join(lines).encode()), "symbols": [symbol]})
        self.document = {"schema_version": "dst-mechanism-research/1", "source_epoch": "old-fixture",
                         "archive_sha256": self.old.sha256, "source_references": refs,
                         "entries": [{"id": "FIXTURE", "knowledge_status": "research",
                                      "retrieval_status": "restricted", "coding_status": "hold",
                                      "claims": [{"id": "C1", "kind": "NSF", "statement": "Synthetic only",
                                                  "evidence_refs": ["definition"]}],
                                      "compatibility": {"dependency_coverage": "enumerated_static",
                                                        "dependency_refs": [{"ref": "consumer", "role": "consumer"}]}}]}
        self.save()

    def archive(self, name, files):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            for member, raw in files.items():
                archive.writestr(member, raw)
        value = compat.Archive(path, "arbitrary-unregistered-version")
        self.addCleanup(value.close)
        return value

    def save(self):
        self.candidate.write_text(json.dumps(self.document), encoding="utf-8")

    def assess(self, files, old=True):
        target = self.archive("target.zip", files)
        self.save()
        result = compat.assess([(self.candidate, self.document)], self.old if old else None, target)
        refs = {r["id"]: r for r in result["candidates"][0]["reference_states"]}
        return result, refs, result["candidates"][0]["entries"][0]["claims"][0]

    def test_unrelated_addition_and_arbitrary_version_keep_source_identity(self):
        files = dict(self.files, **{"scripts/new_unrelated.lua": b"return 42\n"})
        result, refs, claim = self.assess(files)
        self.assertNotEqual(result["baseline"]["archive_sha256"], result["target"]["archive_sha256"])
        self.assertEqual(refs["definition"]["status"], "byte_identical")
        self.assertTrue(refs["definition"]["source_identity_reusable"])
        self.assertEqual(claim["dependency_status"], "unknown")
        self.assertFalse(claim["behavior_compatibility_verified"])

    def test_pure_line_movement_requires_locator_review(self):
        files = dict(self.files)
        files["scripts/producer.lua"] = b"-- new comment\n\n" + files["scripts/producer.lua"]
        _, refs, _ = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "relocation_required")
        self.assertEqual(refs["definition"]["target_locator"]["line_start"], 3)
        self.assertFalse(refs["definition"]["source_identity_reusable"])

    def test_descriptive_call_hint_does_not_invalidate_identical_source(self):
        hint = 'AddTaskSet("default")'
        self.document["source_references"][0]["symbols"] = [hint]
        _, refs, _ = self.assess(self.files)
        self.assertEqual(refs["definition"]["status"], "byte_identical")
        self.assertTrue(refs["definition"]["source_identity_reusable"])
        self.assertEqual(refs["definition"]["navigation_hints_not_used"], [hint])

    def test_moved_range_keeps_descriptive_hint_without_guessing_symbol(self):
        self.document["source_references"][0]["symbols"] = ['Producer("label")', 'Producer']
        files = dict(self.files)
        files["scripts/producer.lua"] = b"-- inserted\n" + files["scripts/producer.lua"]
        _, refs, _ = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "relocation_required")
        self.assertEqual([x["symbol"] for x in refs["definition"]["symbol_navigation"]], ['Producer'])
        self.assertFalse(refs["definition"]["source_identity_reusable"])

    def test_function_behavior_change_requires_review(self):
        files = dict(self.files)
        files["scripts/producer.lua"] = files["scripts/producer.lua"].replace(b"x + 1", b"x - 9")
        _, refs, claim = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "review_required")
        self.assertEqual(claim["compatibility_status"], "review_required")

    def test_consumer_change_invalidates_bounded_contract_review(self):
        files = dict(self.files)
        files["scripts/consumer.lua"] = files["scripts/consumer.lua"].replace(b"Producer(x)", b"Producer(x) * 99")
        _, refs, claim = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "byte_identical")
        self.assertEqual(refs["consumer"]["status"], "review_required")
        self.assertEqual(claim["source_status"], "review_required")

    def test_deleted_source(self):
        files = {k: v for k, v in self.files.items() if k != "scripts/producer.lua"}
        _, refs, claim = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "missing")
        self.assertEqual(claim["compatibility_status"], "review_required")

    def test_no_old_source_and_changed_target_is_unknown_but_navigable(self):
        files = dict(self.files)
        files["scripts/producer.lua"] += b"-- new\n"
        result, refs, claim = self.assess(files, old=False)
        self.assertEqual(refs["definition"]["status"], "unknown")
        self.assertIn("missing_matching_old_source", refs["definition"]["reasons"])
        self.assertTrue(refs["definition"]["symbol_navigation"][0]["matches"])
        self.assertTrue(result["target_navigation_available"])
        self.assertFalse(result["coding_hold_changed"])

    def test_no_old_source_but_pinned_identical_bytes_are_self_authenticating(self):
        _, refs, _ = self.assess(self.files, old=False)
        self.assertEqual(refs["definition"]["status"], "byte_identical")

    def test_reference_mismatch_not_silently_rewritten(self):
        self.document["source_references"][0]["file_sha256"] = "a" * 64
        _, refs, _ = self.assess(self.files)
        self.assertEqual(refs["definition"]["status"], "unknown")

    def test_ambiguous_range_and_changed_outside_range(self):
        files = dict(self.files)
        files["scripts/producer.lua"] *= 2
        _, refs, _ = self.assess(files)
        self.assertEqual(refs["definition"]["status"], "unknown")
        files["scripts/producer.lua"] = self.files["scripts/producer.lua"] + b"-- extra\n"
        other = self.archive("other.zip", files)
        ref = compat.compare_reference(self.document["source_references"][0], self.old, other)
        self.assertEqual(ref["status"], "review_required")

    def test_unknown_dependency_and_unresolved_ref(self):
        self.document["entries"][0].pop("compatibility")
        self.document["entries"][0]["claims"][0]["evidence_refs"].append("not-found")
        _, _, claim = self.assess(self.files)
        self.assertEqual(claim["source_status"], "unknown")
        self.assertEqual(claim["dependency_status"], "unknown")

    def test_wrong_archive_baseline_rejected_locally(self):
        self.document["archive_sha256"] = "f" * 64
        _, refs, _ = self.assess(self.files)
        self.assertEqual(refs["definition"]["status"], "unknown")

    def test_optional_compatibility_contract_rejects_nonlocal_dependency(self):
        config = self.document["entries"][0]["compatibility"]
        config["dependency_refs"][0]["claim_ids"] = ["not-a-local-claim"]
        with self.assertRaises(ValueError):
            self.assess(self.files)
        config["dependency_refs"][0]["claim_ids"] = ["C1"]
        config["dependency_refs"][0]["ref"] = "not-a-local-source"
        with self.assertRaises(ValueError):
            self.assess(self.files)

    def test_api_and_mechanism_units_have_individual_review_states(self):
        entry = self.document["entries"][0]
        entry["api_contracts"] = [{"symbol": "Consumer", "evidence_refs": ["consumer"]}]
        entry["mechanism_steps"] = [{"step": 1, "evidence_refs": ["consumer"]}]
        entry.pop("compatibility")
        files = dict(self.files)
        files["scripts/consumer.lua"] += b"-- changed outside range\n"
        result, _, _ = self.assess(files)
        unit = result["candidates"][0]["entries"][0]
        self.assertEqual(unit["claims"][0]["source_status"], "byte_identical")
        self.assertEqual(unit["api_contracts"][0]["source_status"], "review_required")
        self.assertEqual(unit["mechanism_steps"][0]["source_status"], "review_required")

    def test_navigation_ignores_comments_and_strings(self):
        target = self.archive("nav.zip", {"scripts/a.lua": b'-- function Fake()\nlocal x = "Fake"\n--[=[ Fake ]=]\nlocal y = [==[Fake]==]\nfunction Real()\nend\n'})
        self.assertEqual(compat.locate(target, "Fake")["total_matches"], 0)
        self.assertEqual(compat.locate(target, "Real")["matches"][0]["line"], 5)

    def test_cli_refuses_overwrite_and_does_not_change_candidate(self):
        before = self.candidate.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            code = compat.main(["assess", "--target", str(self.old.path), "--candidate", str(self.candidate),
                                "--output", str(self.candidate)])
        self.assertEqual(code, 2)
        self.assertEqual(before, self.candidate.read_bytes())

    def test_zip_duplicate_and_traversal_rejected(self):
        path = self.root / "bad.zip"
        with zipfile.ZipFile(path, "w") as archive:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                archive.writestr("scripts/a.lua", "a")
                archive.writestr("scripts/a.lua", "b")
        with self.assertRaises(ValueError):
            compat.Archive(path)
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("scripts/../a.lua", "bad")
        with self.assertRaises(ValueError):
            compat.Archive(path)

    def test_safe_non_scripts_metadata_is_ignored(self):
        target = self.archive("metadata.zip", dict(self.files, **{"README.md": b"metadata", "metadata/version.txt": b"next"}))
        self.assertEqual(target.identity()["lua_count"], 2)
        self.assertEqual(compat.locate(target, "Producer")["total_matches"], 2)


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".policy-", dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        knowledge = self.root / "knowledge"
        knowledge.mkdir()
        raw = b'{"entries": []}'
        (knowledge / "CATALOG.json").write_bytes(raw)
        (knowledge / "PACKAGE-MANIFEST.json").write_text(json.dumps({
            "schema_version": "dst-public-package-manifest/1", "files": [{"path": "CATALOG.json",
            "bytes": len(raw), "sha256": compat.sha(raw)}]}), encoding="utf-8")

    def test_auto_package_upgrade_reports_degradation(self):
        self.assertEqual(policy.catalog_fallback("auto", "PACKAGE_CHANGED", self.root)["reason_code"], "PACKAGE_CHANGED")

    def test_full_and_corrupt_cache_remain_strict(self):
        self.assertIsNone(policy.catalog_fallback("full", "PACKAGE_CHANGED", self.root))
        self.assertIsNone(policy.catalog_fallback("auto", "RUNTIME_CHANGED", self.root))
        self.assertIsNone(policy.catalog_fallback("auto", "INVALID_PATH", self.root))
        self.assertIsNone(policy.catalog_fallback("auto", "PACKAGE_INCOMPLETE", self.root))

    def test_bad_public_data_never_silently_ignored(self):
        (self.root / "knowledge/CATALOG.json").write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            policy.catalog_fallback("auto", "PACKAGE_CHANGED", self.root)

    def test_invalid_activation_is_not_unprepared(self):
        activation = self.root / "cache/runtime/retrieval-config.json"
        activation.parent.mkdir(parents=True)
        activation.write_text("{}", encoding="utf-8")
        self.assertIsNone(policy.catalog_fallback("auto", "SOURCES_NOT_PREPARED", self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)

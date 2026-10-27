"""Exercise current maintenance helpers, with synthetic source only, read-only imports."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


payload = load("audited_source_payload", REPO / "scripts/source_payload.py")
prepare = load("audited_prepare_sources", REPO / "prepare_sources.py")


class ExistingHydratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".existing-helper-", dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.body = b"function SyntheticOnly()\n    return true\nend\n"
        self.slot = {"content_sha256": payload.sha(self.body), "content_bytes": len(self.body),
                     "original_json_value_sha256": payload.digest(self.body.decode()), "encoding": "utf8",
                     "line_count": 3, "coordinates": [{"source_file": "scripts/a.lua",
                      "expected_file_sha256": payload.sha(self.body), "line_start": 1, "line_end": 3}]}

    def recover(self, raw, extra=False):
        path = self.root / "source.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("scripts/a.lua", raw)
            if extra:
                archive.writestr("scripts/unrelated.lua", b"return false\n")
        sources = payload.Sources([path])
        try:
            return payload.recover(self.slot, sources)
        finally:
            sources.close()

    def test_existing_recovery_does_not_require_whole_archive_hash(self):
        value, proof = self.recover(self.body, extra=True)
        self.assertEqual(value, self.body.decode())
        self.assertTrue(proof["provided_whole_file_equals_original"])

    def test_existing_recovery_already_handles_shifted_exact_range(self):
        value, proof = self.recover(b"-- prefix\n" + self.body)
        self.assertEqual(value, self.body.decode())
        self.assertFalse(proof["provided_whole_file_equals_original"])
        self.assertEqual(proof["matched_line_start"], 2)

    def test_existing_recovery_rejects_changed_required_content(self):
        self.assertEqual(self.recover(self.body.replace(b"true", b"false")), (None, None))

    def test_archive_hash_change_requests_rescan_not_knowledge_invalidation(self):
        path = self.root / "source.zip"
        self.recover(self.body)
        receipt = {"source_inputs": [{"kind": "ZIP", "archive_sha256": prepare.sha(path.read_bytes())}],
                   "hydration": {"missing_optional_identity_cache_count": 0}}
        (self.root / "PREPARATION-RECEIPT.json").write_text(json.dumps(receipt), encoding="utf-8")
        self.assertTrue(prepare.same_source_inputs(self.root, [path]))
        with zipfile.ZipFile(path, "a") as archive:
            archive.writestr("scripts/added.lua", "return 1\n")
        self.assertFalse(prepare.same_source_inputs(self.root, [path]))


if __name__ == "__main__":
    unittest.main(verbosity=2)

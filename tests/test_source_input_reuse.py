"""Missing obsolete optional ranges must not force unchanged ZIP rebuilds."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('input_reuse_prepare', ROOT / 'prepare_sources.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class SourceInputReuseTests(unittest.TestCase):
    def test_unchanged_archive_with_optional_gaps_is_reusable_but_changed_archive_is_not(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'scripts.zip'
            with zipfile.ZipFile(source, 'w') as z:
                z.writestr('scripts/current.lua', 'return true\n')
            prepare.write(root / 'PREPARATION-RECEIPT.json', {
                'source_inputs': [{'kind': 'ZIP', 'archive_sha256': prepare.sha(source.read_bytes())}],
                'hydration': {'missing_optional_identity_cache_count': 76}})
            self.assertTrue(prepare.same_source_inputs(root, [source]))
            with zipfile.ZipFile(source, 'a') as z:
                z.writestr('scripts/added.lua', 'return false\n')
            self.assertFalse(prepare.same_source_inputs(root, [source]))

    def test_directory_with_optional_gaps_is_rescanned_for_new_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'scripts'
            source.mkdir()
            prepare.write(root / 'PREPARATION-RECEIPT.json', {
                'source_inputs': [{'kind': 'DIRECTORY', 'matched_files': []}],
                'hydration': {'missing_optional_identity_cache_count': 1}})
            self.assertFalse(prepare.same_source_inputs(root, [source]))

    def test_directory_with_no_payload_gaps_still_reassesses_locator_only_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'scripts'
            source.mkdir()
            member = source / 'mechanism.lua'
            member.write_text('return "new locator-only behavior"\n', encoding='utf-8')
            prepare.write(root / 'PREPARATION-RECEIPT.json', {
                'source_inputs': [{'kind': 'DIRECTORY', 'matched_files': []}],
                'hydration': {'missing_optional_identity_cache_count': 0}})
            self.assertFalse(prepare.same_source_inputs(root, [source]))


if __name__ == '__main__':
    unittest.main()

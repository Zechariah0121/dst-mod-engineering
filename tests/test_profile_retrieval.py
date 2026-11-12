"""Profiling output reuse must retain its declared runtime input binding."""
import importlib.util
import argparse
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/profile_retrieval.py'
SPEC = importlib.util.spec_from_file_location('profile_retrieval', SCRIPT)
PROFILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROFILE)


class ProfileConfigurationTests(unittest.TestCase):
    def test_labels_cannot_escape_the_evidence_directory(self):
        for label in ('E-R3-01-initial', 'candidate.2', 'baseline_code'):
            self.assertEqual(PROFILE.simple_label(label), label)
        for label in ('', '.', '..', '../outside', 'a/b', 'a\\b', 'C:outside', None):
            with self.subTest(label=label), self.assertRaises(argparse.ArgumentTypeError):
                PROFILE.simple_label(label)

    def test_reuse_accepts_identical_inputs_and_rejects_another_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, output = root / 'first', root / 'second', root / 'output'
            catalog = {'epochs': {'759671': {
                'knowledge_root': 'knowledge', 'index_path': 'cache/index.sqlite3',
                'knowledge_manifest': {'path': 'knowledge/PACKAGE-MANIFEST.json'},
                'contract_map': {'path': 'epoch-assets/contract_map.json'},
                'source_identity_map': {'path': 'epoch-assets/source_identity_map.json'},
                'source_manifests': [{'path': 'epoch-assets/source-manifest.json'}]}}}
            for runtime in (first, second):
                runtime.mkdir()
                (runtime / 'source-epochs.json').write_text(json.dumps(catalog), encoding='utf-8')
            config = PROFILE.prepare_config(first, output)
            before = config.read_bytes(), (output / 'source-epochs.json').read_bytes()
            self.assertEqual(PROFILE.prepare_config(first, output), config)
            with self.assertRaisesRegex(ValueError, 'different runtime inputs'):
                PROFILE.prepare_config(second, output)
            self.assertEqual((config.read_bytes(), (output / 'source-epochs.json').read_bytes()), before)
            config.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'configuration changed'):
                PROFILE.prepare_config(first, output)


if __name__ == '__main__':
    unittest.main()

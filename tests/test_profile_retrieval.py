"""Profiling output reuse must retain its declared runtime input binding."""
import importlib.util
import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


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


class ProfileRunTests(unittest.TestCase):
    def run_main(self, root, labels, extra_args=()):
        runtime = root / 'runtime'
        profiles = runtime / 'dst-kb-service/dst_kb/projection_profiles.json'
        profiles.parent.mkdir(parents=True)
        profiles.write_text('{}', encoding='utf-8')
        (runtime / 'source-epochs.json').write_text('{"epochs": {}}', encoding='utf-8')
        requests = root / 'requests.json'
        requests.write_text(json.dumps([
            {'label': label, 'params': {'name': 'get_entry', 'arguments': {'id': str(index)}}}
            for index, label in enumerate(labels)
        ]), encoding='utf-8')
        service = Mock()
        service.get_entry.side_effect = lambda id: {'entries': [{'id': id}]}
        service_module = types.ModuleType('dst_kb.service')
        service_module.Service = Mock(return_value=service)
        package = types.ModuleType('dst_kb')
        package.service = service_module
        package.projection_v2 = types.ModuleType('dst_kb.projection_v2')
        modules = {'dst_kb': package, 'dst_kb.service': service_module,
                   'dst_kb.projection_v2': package.projection_v2}
        arguments = [str(SCRIPT), '--runtime-root', str(runtime), '--output', str(root / 'output'),
                     '--requests', str(requests), '--label', 'run', *extra_args]
        with patch.object(sys, 'argv', arguments), patch.object(sys, 'path', list(sys.path)), \
                patch.dict(sys.modules, modules), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            PROFILE.main()
        service.close.assert_called_once()
        return root / 'output/run'

    def test_conflicting_labels_fail_before_creating_output(self):
        cases = [(('same', 'same'), []), (('same', 'SAME'), []),
                 (('initialize',), []), (('INITIALIZE',), []),
                 (('same', 'SAME'), ['--repeat', '2'])]
        for labels, arguments in cases:
            with self.subTest(labels=labels, arguments=arguments), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(SystemExit) as caught:
                    self.run_main(root, labels, arguments)
                self.assertEqual(caught.exception.code, 2)
                self.assertFalse((root / 'output').exists())

    def test_counts_must_be_positive_integers(self):
        for option in ('--repeat', '--max-requests'):
            for value in ('0', '-1', '1.5', 'invalid'):
                with self.subTest(option=option, value=value), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    with self.assertRaises(SystemExit) as caught:
                        self.run_main(root, ['first'], [option, value])
                    self.assertEqual(caught.exception.code, 2)
                    self.assertFalse((root / 'output').exists())

    def test_default_run_preserves_request_labels_and_response_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.run_main(Path(directory), ['first', 'second'], ['--no-profile'])
            summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual([row['label'] for row in summary['operations']],
                             ['initialize', 'first', 'second'])
            for label, identifier in (('first', '0'), ('second', '1')):
                self.assertEqual(json.loads((output / (label + '-response.json')).read_bytes()),
                                 {'entries': [{'id': identifier}]})

    def test_multiple_repeated_requests_preserve_all_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.run_main(Path(directory), ['first', 'second', 'unused'],
                                   ['--repeat', '2', '--max-requests', '2'])
            summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual([row['label'] for row in summary['operations']],
                             ['initialize', 'first-1', 'second-1', 'first-2', 'second-2'])
            for row in summary['operations']:
                self.assertTrue(row['profiled'])
                self.assertTrue((output / (row['label'] + '.prof')).is_file())
                self.assertTrue((output / (row['label'] + '-functions.json')).is_file())
            for row, identifier in zip(summary['operations'][1:], ('0', '1', '0', '1')):
                raw = (output / (row['label'] + '-response.json')).read_bytes()
                self.assertEqual(json.loads(raw), {'entries': [{'id': identifier}]})
                self.assertEqual(row['response_sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(row['response_bytes'], len(raw))
                self.assertEqual(row['entries'], [identifier])
            self.assertEqual(len(list(output.glob('*-response.json'))), 4)

    def test_validation_uses_selected_derived_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.run_main(Path(directory), ['initialize', 'INITIALIZE'],
                                   ['--repeat', '2', '--max-requests', '1', '--no-profile'])
            summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual([row['label'] for row in summary['operations']],
                             ['initialize', 'initialize-1', 'initialize-2'])
            self.assertTrue(all(not row['profiled'] for row in summary['operations']))


if __name__ == '__main__':
    unittest.main()

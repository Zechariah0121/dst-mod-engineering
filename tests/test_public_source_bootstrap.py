"""Synthetic bootstrap flow checks; real source/Service acceptance is separate.

The integration flow uses the actual source hydrator. Rebind and original-data
validation are mocked for these deliberately tiny non-KB fixtures.
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_sources as prepare
import run_kb as launcher

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE.parent / 'scripts/source_payload.py'
REBIND = HERE.parent / 'scripts/public_rebind.py'


class BootstrapTests(unittest.TestCase):
    def test_isolated_launcher_locates_packaged_helper_from_other_directory(self):
        with tempfile.TemporaryDirectory(prefix='isolated-client-') as working:
            result = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
                str(HERE.parent / 'run_kb.py'), 'mcp-config'], cwd=working,
                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)['mcpServers']['dst_engineering_kb']
        self.assertIn(str(HERE.parent / 'run_kb.py'), config['args'])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='synthetic-', dir=HERE)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.root = self.folder / 'package with spaces'
        self.root.mkdir()
        for name in prepare.RUNTIME_TREES:
            (self.root / name).mkdir()
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copyfile(PAYLOAD, scripts / 'source_payload.py')
        shutil.copyfile(REBIND, scripts / 'public_rebind.py')
        for name in ('run_kb.py', 'prepare_sources.py'):
            shutil.copyfile(HERE.parent / name, self.root / name)
        payload = prepare.load_helper(PAYLOAD, 'bootstrap_fixture_payload')
        self.body = 'function SyntheticSourceFixture()\n    return true\nend\n'
        slot = {'id': 'synthetic-slot', 'path': 'knowledge/evidence.json',
            'pointer': '/citation/source_excerpt', 'kind': 'strict_knowledge_excerpt',
            'encoding': 'utf8', 'content_sha256': payload.sha(self.body.encode()),
            'content_bytes': len(self.body.encode()), 'original_json_value_sha256': payload.digest(self.body),
            'line_count': 3, 'required_for_knowledge_shape': True, 'missing_policy': 'ERROR',
            'coordinates': [{'source_file': 'scripts/a.lua', 'expected_file_sha256': 'a' * 64,
                             'line_start': 2, 'line_end': 4}]}
        prepare.write(self.root / 'knowledge/evidence.json', {'citation': {
            'source_excerpt': {prepare.MARKER: slot['id']}}})
        prepare.write(self.root / 'source-payload-recipe.json', {'schema': payload.SCHEMA, 'slots': [slot]})
        prepare.write(self.root / 'PUBLICATION-ORIGIN-MAP.json', {'files': [], 'records': {}})
        prepare.write(self.root / 'source-epochs.json', {'epochs': {
            epoch: {'index_path': 'cache/epochs/' + epoch + '/index.sqlite3'} for epoch in prepare.EPOCHS}})
        prepare.write(self.root / 'retrieval-config.json', {'source_epochs_path': 'source-epochs.json'})
        (self.root / 'dst-kb-service/dst_kb_cli.py').write_text('# synthetic, never executed\n', encoding='utf-8')
        self.current = self.folder / 'current.zip'
        with zipfile.ZipFile(self.current, 'w') as archive:
            archive.writestr('scripts/a.lua', 'first\nfunction DifferentSource()\nend\n')
        self.historical = self.folder / 'historical'
        self.historical.mkdir()
        (self.historical / 'a.lua').write_text('first\n' + self.body, encoding='utf-8')

    def build(self, sources):
        original_loader = prepare.load_helper
        def loader(path, name):
            if path.name == 'public_rebind.py':
                return SimpleNamespace(rebind=lambda root, origin: ({'unresolved': [], 'typed_reference_updates': []}, {}))
            return original_loader(path, name)
        with patch.object(prepare, 'load_helper', side_effect=loader), patch.object(
                prepare, 'check_in_subprocess', return_value={'status': 'SYNTHETIC_GUARD_STUB_NOT_REAL_VALIDATION'}):
            return prepare.prepare(self.root, sources)

    def test_two_explicit_sources_hydrate_and_activate_without_touching_templates(self):
        original = (self.root / 'knowledge/evidence.json').read_bytes()
        result = self.build([self.current, self.historical])
        config, build = prepare.prepared_runtime(self.root)
        self.assertEqual(result['status'], 'LOCAL_RUNTIME_PREPARED')
        self.assertEqual(prepare.read(build / 'knowledge/evidence.json')['citation']['source_excerpt'], self.body)
        self.assertEqual((self.root / 'knowledge/evidence.json').read_bytes(), original)
        self.assertEqual(config, self.root / 'cache/runtime/retrieval-config.json')
        receipt = prepare.read(build / 'PREPARATION-RECEIPT.json')
        self.assertFalse(receipt['client_configuration_modified'])
        self.assertEqual(len(receipt['source_payload_input_sha256']), 64)
        with patch.object(prepare, 'check_in_subprocess', side_effect=AssertionError('unchanged runtime must be reused')):
            self.assertEqual(prepare.prepare(self.root, [self.current, self.historical])['status'], 'LOCAL_RUNTIME_ALREADY_PREPARED')

    def test_missing_historical_range_preserves_existing_activation(self):
        self.build([self.current, self.historical])
        active = self.root / 'cache/runtime/retrieval-config.json'
        original = active.read_bytes()
        with self.assertRaises(prepare.PreparationError) as caught:
            self.build([self.current])
        self.assertEqual(caught.exception.code, 'SOURCE_GAP')
        self.assertEqual(caught.exception.details['source_gaps'][0]['source_file'], 'scripts/a.lua')
        self.assertEqual(active.read_bytes(), original)
        self.assertFalse((self.root / 'cache/runtime/.prepare.lock').exists())
        self.assertFalse(list((self.root / 'cache/runtime').glob('.prepare-*')))

    def test_invalid_explicit_source_is_rejected_before_cache_write(self):
        with self.assertRaises(prepare.PreparationError) as caught:
            prepare.prepare(self.root, [self.folder / 'does-not-exist'])
        self.assertEqual(caught.exception.code, 'INVALID_SOURCE')
        self.assertFalse((self.root / 'cache').exists())

    def test_runtime_mutation_and_unsafe_path_are_rejected(self):
        self.build([self.current, self.historical])
        _, build = prepare.prepared_runtime(self.root)
        (build / 'knowledge/evidence.json').write_text('{}\n', encoding='utf-8')
        with self.assertRaises(prepare.PreparationError) as caught:
            prepare.prepared_runtime(self.root)
        self.assertEqual(caught.exception.code, 'RUNTIME_CHANGED')
        with self.assertRaises(prepare.PreparationError):
            prepare.child(self.root, '../outside')

    def test_unprepared_launcher_never_starts_service_and_config_only_prints(self):
        with patch.object(launcher, 'ROOT', self.root), patch.object(launcher.subprocess, 'run') as execute:
            error, output = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(error):
                self.assertEqual(launcher.main(['serve']), 2)
            self.assertIn('prepare_sources.py', error.getvalue())
            with contextlib.redirect_stdout(output):
                self.assertEqual(launcher.main(['mcp-config']), 0)
            self.assertIn(str(self.root / 'run_kb.py'), json.loads(output.getvalue())['mcpServers']['dst_engineering_kb']['args'])
            execute.assert_not_called()
        self.assertFalse((self.root / 'cache').exists())

    def test_bad_call_json_and_inapplicable_epoch_cannot_reach_service(self):
        args = self.folder / 'bad.json'
        args.write_text('[]', encoding='utf-8')
        with patch.object(launcher, 'ROOT', self.root), patch.object(launcher.subprocess, 'run') as execute:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                launcher.main(['call', '--tool', 'get_entry', '--arguments-file', str(args)])
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                launcher.main(['serve', '--source-epoch', '759671'])
            execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()

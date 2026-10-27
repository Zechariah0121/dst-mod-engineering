"""Synthetic bootstrap flow checks; real source/Service acceptance is separate.

The integration flow uses the actual source hydrator. Rebind and original-data
validation are mocked for these deliberately tiny non-KB fixtures.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
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

# These are real competing preparation processes. Only rebind/original-KB
# guards use the same explicit synthetic stubs as build(); locking, hydration,
# manifests, filesystem installation and activation are production code.
PREPARE_WORKER = r'''
import json
from pathlib import Path
import sys
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
import prepare_sources as prepare
original = prepare.load_helper
def loader(path, name):
    if path.name == 'public_rebind.py':
        return SimpleNamespace(rebind=lambda root, origin: ({'unresolved': [], 'typed_reference_updates': []}, {}))
    return original(path, name)
def guard(root):
    Path(sys.argv[5]).write_text('guard entered with lock held', encoding='utf-8')
    sys.stdin.readline()
    return {'status': 'SYNTHETIC_GUARD_STUB_NOT_REAL_VALIDATION'}
prepare.load_helper = loader
prepare.check_in_subprocess = guard
try:
    result = prepare.prepare(Path(sys.argv[2]), [Path(sys.argv[3]), Path(sys.argv[4])])
except prepare.PreparationError as exc:
    print(json.dumps({'error': exc.code}), flush=True)
    sys.exit(2)
print(json.dumps(result), flush=True)
'''


class BootstrapTests(unittest.TestCase):
    def test_isolated_launcher_locates_packaged_helper_from_other_directory(self):
        with tempfile.TemporaryDirectory(prefix='isolated-client-') as working:
            result = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
                str(HERE.parent / 'run_kb.py'), 'mcp-config'], cwd=working,
                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)['mcpServers']['dst_engineering_kb']
        self.assertIn(str(HERE.parent / 'run_kb.py'), config['args'])

    def test_isolated_service_cli_locates_its_packaged_modules(self):
        with tempfile.TemporaryDirectory(prefix='isolated-service-') as working:
            result = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
                str(HERE.parent / 'dst-kb-service/dst_kb_cli.py'), '--help'],
                cwd=working, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Read-only DST KB service', result.stdout)

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
        for name in ('source_compatibility.py', 'catalog_fallback_policy.py', 'legacy_adapter.py'):
            shutil.copyfile(HERE.parent / 'scripts' / name, scripts / name)
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

    def build(self, sources, guard_error=None):
        original_loader = prepare.load_helper
        def loader(path, name):
            if path.name == 'public_rebind.py':
                return SimpleNamespace(rebind=lambda root, origin: ({'unresolved': [], 'typed_reference_updates': []}, {}))
            return original_loader(path, name)
        with patch.object(prepare, 'load_helper', side_effect=loader), patch.object(
                prepare, 'check_in_subprocess', side_effect=guard_error,
                return_value={'status': 'SYNTHETIC_GUARD_STUB_NOT_REAL_VALIDATION'}):
            return prepare.prepare(self.root, sources)

    def start_preparation(self):
        ready = self.folder / 'worker-ready'
        process = subprocess.Popen([sys.executable, '-B', '-X', 'utf8', '-c', PREPARE_WORKER,
            str(HERE.parent), str(self.root), str(self.current), str(self.historical), str(ready)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8')
        def cleanup():
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=10)
        self.addCleanup(cleanup)
        deadline = time.monotonic() + 15
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(ready.exists(), 'preparation worker failed to acquire lock and enter guard')
        return process

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
        # Explicit directories must be reassessed, including locator-only files.
        self.assertEqual(self.build([self.current, self.historical])['status'], 'LOCAL_RUNTIME_PREPARED')

    def test_missing_historical_range_preserves_existing_activation(self):
        self.build([self.current, self.historical])
        active = self.root / 'cache/runtime/retrieval-config.json'
        original = active.read_bytes()
        with self.assertRaises(prepare.PreparationError) as caught:
            self.build([self.current])
        self.assertEqual(caught.exception.code, 'SOURCE_GAP')
        self.assertEqual(caught.exception.details['source_gaps'][0]['source_file'], 'scripts/a.lua')
        self.assertEqual(active.read_bytes(), original)
        self.assertTrue((self.root / 'cache/runtime/.prepare.lock').exists())
        with prepare.preparation_lock(self.root / 'cache/runtime/.prepare.lock'):
            pass
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

    def test_same_sources_repair_corrupt_build_and_preserve_all_previous_data(self):
        self.build([self.current, self.historical])
        active = self.root / 'cache/runtime/retrieval-config.json'
        original_activation = active.read_bytes()
        _, build = prepare.prepared_runtime(self.root)
        damaged = build / 'knowledge/evidence.json'
        damaged.write_text('{broken fixture', encoding='utf-8')
        (build / 'user-notes.txt').write_text('preserve this user file', encoding='utf-8')
        result = self.build([self.current, self.historical])
        self.assertEqual(result['status'], 'LOCAL_RUNTIME_PREPARED')
        _, repaired = prepare.prepared_runtime(self.root)
        self.assertEqual(repaired, build)
        self.assertEqual(active.read_bytes(), original_activation)
        self.assertEqual(prepare.read(repaired / 'knowledge/evidence.json')['citation']['source_excerpt'], self.body)
        preserved = self.root / result['previous_build_preserved_at']
        self.assertEqual((preserved / 'knowledge/evidence.json').read_text(encoding='utf-8'), '{broken fixture')
        self.assertEqual((preserved / 'user-notes.txt').read_text(encoding='utf-8'), 'preserve this user file')

    def test_missing_manifest_can_be_rebuilt_from_identical_sources(self):
        self.build([self.current, self.historical])
        _, build = prepare.prepared_runtime(self.root)
        (build / 'RUNTIME-MANIFEST.json').unlink()
        result = self.build([self.current, self.historical])
        self.assertTrue((self.root / result['previous_build_preserved_at']).is_dir())
        self.assertEqual(prepare.prepared_runtime(self.root)[1], build)

    def test_failed_replacement_install_restores_damaged_build_and_activation(self):
        self.build([self.current, self.historical])
        _, build = prepare.prepared_runtime(self.root)
        (build / 'user-notes.txt').write_text('keep me', encoding='utf-8')
        activation = self.root / 'cache/runtime/retrieval-config.json'
        previous = activation.read_bytes()
        original_rename = Path.rename
        def rename(path, target):
            if path.name == 'assembled' and target == build:
                raise OSError('synthetic installation failure')
            return original_rename(path, target)
        with patch.object(Path, 'rename', new=rename), self.assertRaisesRegex(OSError, 'installation failure'):
            self.build([self.current, self.historical])
        self.assertEqual((build / 'user-notes.txt').read_text(encoding='utf-8'), 'keep me')
        self.assertEqual(activation.read_bytes(), previous)
        self.assertEqual(self.build([self.current, self.historical])['status'], 'LOCAL_RUNTIME_PREPARED')

    def test_guard_failure_never_displaces_damaged_build(self):
        self.build([self.current, self.historical])
        _, build = prepare.prepared_runtime(self.root)
        (build / 'knowledge/evidence.json').write_text('{}', encoding='utf-8')
        with self.assertRaises(prepare.PreparationError) as caught:
            self.build([self.current, self.historical], guard_error=prepare.PreparationError(
                'VALIDATION_FAILED', 'synthetic guard rejection'))
        self.assertEqual(caught.exception.code, 'VALIDATION_FAILED')
        self.assertEqual((build / 'knowledge/evidence.json').read_text(encoding='utf-8'), '{}')
        self.assertFalse((self.root / 'cache/runtime/quarantine').exists())

    def test_failed_installed_build_verification_restores_previous_directory(self):
        self.build([self.current, self.historical])
        _, build = prepare.prepared_runtime(self.root)
        (build / 'user-notes.txt').write_text('previous build data', encoding='utf-8')
        original_rename = Path.rename
        def rename(path, target):
            result = original_rename(path, target)
            if path.name == 'assembled' and target == build:
                (target / 'knowledge/evidence.json').write_text('injected post-install damage', encoding='utf-8')
            return result
        with patch.object(Path, 'rename', new=rename), self.assertRaises(prepare.PreparationError) as caught:
            self.build([self.current, self.historical])
        self.assertEqual(caught.exception.code, 'RUNTIME_CHANGED')
        self.assertEqual((build / 'user-notes.txt').read_text(encoding='utf-8'), 'previous build data')
        self.assertEqual(prepare.read(build / 'knowledge/evidence.json')['citation']['source_excerpt'], self.body)
        failed = list((self.root / 'cache/runtime/quarantine').glob('*-failed-replacement-*'))
        self.assertEqual(len(failed), 1)
        self.assertEqual((failed[0] / 'knowledge/evidence.json').read_text(encoding='utf-8'), 'injected post-install damage')

    def test_concurrent_process_cannot_prepare_until_owner_finishes(self):
        process = self.start_preparation()
        contender = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-c', PREPARE_WORKER,
            str(HERE.parent), str(self.root), str(self.current), str(self.historical),
            str(self.folder / 'contender-ready')], capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(contender.returncode, 2, contender.stderr)
        self.assertEqual(json.loads(contender.stdout)['error'], 'PREPARATION_BUSY')
        self.assertFalse((self.folder / 'contender-ready').exists())
        output, error = process.communicate('\n', timeout=15)
        self.assertEqual(process.returncode, 0, error)
        self.assertEqual(json.loads(output)['status'], 'LOCAL_RUNTIME_PREPARED')
        self.assertEqual(self.build([self.current, self.historical])['status'], 'LOCAL_RUNTIME_PREPARED')

    def test_hard_killed_process_does_not_leave_preparation_busy(self):
        process = self.start_preparation()
        process.kill()
        process.communicate(timeout=10)
        lock = self.root / 'cache/runtime/.prepare.lock'
        self.assertTrue(lock.exists())
        # Legacy PID contents are also ignored: only live OS ownership matters.
        lock.write_text(str(os.getpid()), encoding='utf-8')
        self.assertEqual(self.build([self.current, self.historical])['status'], 'LOCAL_RUNTIME_PREPARED')
        prepare.prepared_runtime(self.root)

    def test_unprepared_launcher_never_starts_service_and_config_only_prints(self):
        with patch.object(launcher, 'ROOT', self.root), patch.object(launcher.subprocess, 'run') as execute:
            error, output = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(error):
                self.assertEqual(launcher.main(['serve', '--mode', 'full']), 2)
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

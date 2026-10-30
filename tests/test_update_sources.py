"""Synthetic ZIP/temporary-package assistant tests; no installed runtime writes.

The existing tiny hydration fixture stubs original-KB semantic guards and rebind,
as documented by that fixture. Snapshot, hydration, lock, manifest, install and
activation logic are real. This suite is not original-source/game validation.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import zipfile

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'tests'))
from scripts import update_sources as update
import test_public_source_bootstrap as bootstrap
import test_registered_source_assessment as registered

class UpdateTests(unittest.TestCase):
    def setUp(self):
        original_temp = tempfile.TemporaryDirectory
        def temporary(*args, **kwargs):
            # Borrowed legacy fixtures default to their source directory; keep
            # this suite portable and independent of repository write access.
            kwargs.pop('dir', None)
            return original_temp(*args, **kwargs)
        self.patch_temp = mock.patch.object(tempfile, 'TemporaryDirectory', side_effect=temporary)
        self.patch_temp.start()
        self.addCleanup(self.patch_temp.stop)
        self.fixture = bootstrap.BootstrapTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.source = self.fixture.folder / 'authorized.zip'
        self.zip(self.source, 'first\n' + self.fixture.body)
        self.public_manifest()
        original_loader = update.preparation.load_helper
        def loader(path, name):
            if path.name == 'public_rebind.py':
                return SimpleNamespace(rebind=lambda root, origin: ({'unresolved': [], 'typed_reference_updates': []}, {}))
            return original_loader(path, name)
        patcher = mock.patch.object(update.preparation, 'load_helper', side_effect=loader)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(update.preparation, 'check_in_subprocess', return_value={'status': 'SYNTHETIC_STUB'})
        patcher.start()
        self.addCleanup(patcher.stop)

    def zip(self, path, text, extra=False):
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('scripts/a.lua', text)
            if extra:
                archive.writestr('scripts/arbitrary_future.lua', 'return true\n')

    def public_manifest(self):
        catalog = self.root / 'knowledge/CATALOG.json'
        catalog.write_text('{"entries": []}', encoding='utf-8')
        rows = [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': update.compatibility.file_sha(p)}
                for p in (catalog, self.root / 'knowledge/evidence.json')]
        update.preparation.write(self.root / 'knowledge/PACKAGE-MANIFEST.json',
                {'schema_version': 'dst-public-package-manifest/1', 'files': rows})

    def test_public_manifest_unknown_schema_is_rejected(self):
        path = self.root / 'knowledge/PACKAGE-MANIFEST.json'
        manifest = update.preparation.read(path)
        manifest['schema_version'] = 'unknown'
        update.preparation.write(path, manifest)
        with self.assertRaises(update.UpdateError) as error:
            self.ensure(status_only=True)
        self.assertEqual(error.exception.code, 'PUBLIC_PACKAGE_INVALID')

    def test_public_manifest_wrong_byte_commitment_is_rejected(self):
        path = self.root / 'knowledge/PACKAGE-MANIFEST.json'
        manifest = update.preparation.read(path)
        manifest['files'][0]['bytes'] += 1
        update.preparation.write(path, manifest)
        with self.assertRaises(update.UpdateError) as error:
            self.ensure(status_only=True)
        self.assertEqual(error.exception.code, 'PUBLIC_PACKAGE_INVALID')

    def ensure(self, source=None, **kwargs):
        return update.ensure(self.root, source=source, **kwargs)

    def bind(self):
        result = self.ensure(self.source)
        self.assertEqual(result['status'], 'PREPARED')
        return result

    def test_uninitialized_requires_explicit_source_and_status_does_not_bind(self):
        self.assertFalse(self.ensure(status_only=True)['bound'])
        with self.assertRaises(update.UpdateError) as error:
            self.ensure()
        self.assertEqual(error.exception.code, 'SOURCE_REQUIRED')

    def test_prepare_then_unchanged_and_reconnect_is_explicit(self):
        self.bind()
        with mock.patch.object(update.preparation, 'prepare', side_effect=AssertionError('must fast return')):
            result = self.ensure()
        self.assertEqual(result['status'], 'UNCHANGED')
        self.assertFalse(result['current_connection_changed'])
        self.assertFalse(result['reconnect_required'])
        self.assertFalse(result['activation_changed'])
        self.assertEqual(result['current_connection_status'], 'unknown')
        self.assertFalse(result['runtime_verified'])

    def test_unknown_future_zip_preserves_old_build_and_scope(self):
        self.bind()
        old_config, old_build = update.preparation.prepared_runtime(self.root)
        old_bytes = (old_build / 'RUNTIME-MANIFEST.json').read_bytes()
        original = (self.root / 'knowledge/evidence.json').read_bytes()
        self.zip(self.source, 'first\n' + self.fixture.body, extra=True)
        self.assertEqual(self.ensure()['status'], 'PREPARED')
        self.assertEqual((old_build / 'RUNTIME-MANIFEST.json').read_bytes(), old_bytes)
        self.assertEqual((self.root / 'knowledge/evidence.json').read_bytes(), original)
        self.assertNotEqual(update.preparation.prepared_runtime(self.root)[1], old_build)

    def test_same_size_same_mtime_replacement_is_detected(self):
        self.bind()
        before = self.source.stat()
        self.zip(self.source, 'other\n' + self.fixture.body)
        self.assertEqual(self.source.stat().st_size, before.st_size)
        os.utime(self.source, ns=(before.st_atime_ns, before.st_mtime_ns))
        result = self.ensure()
        self.assertEqual(result['status'], 'PREPARED')

    def test_gap_preserves_historical_activation_and_generates_sidecar(self):
        self.bind()
        config, build = update.preparation.prepared_runtime(self.root)
        activation = config.read_bytes()
        self.zip(self.source, 'first\nfunction Removed()\nend\n')
        with mock.patch.object(update, 'sidecar', return_value='cache/source-update/synthetic-review.json') as assessment:
            result = self.ensure()
        self.assertEqual(result['status'], 'SOURCE_REVIEW_REQUIRED')
        self.assertEqual(config.read_bytes(), activation)
        self.assertTrue(build.is_dir())
        assessment.assert_called_once()
        self.assertTrue(result['last_attempt']['source_gaps'])
        self.assertIn('task_followup', result['last_attempt'])
        self.assertFalse(result['historical_cache_is_new_evidence'])
        with mock.patch.object(update.preparation, 'prepare', side_effect=AssertionError('no retry')):
            self.assertEqual(self.ensure()['status'], 'RETRY_SUPPRESSED')

    def test_sidecar_failure_is_reported_without_overwriting_activation(self):
        self.bind()
        self.zip(self.source, 'return false\n')
        result = self.ensure()
        self.assertEqual(result['status'], 'SOURCE_REVIEW_REQUIRED')
        self.assertIn('review_error', result['last_attempt'])  # Tiny fixture has no research registry.

    def test_explicit_retry_of_same_failed_fingerprint(self):
        self.zip(self.source, 'return false\n')
        self.assertEqual(self.ensure(self.source)['status'], 'SOURCE_REVIEW_REQUIRED')
        with mock.patch.object(update.preparation, 'prepare', wraps=update.preparation.prepare) as prepare:
            self.ensure(retry=True)
        self.assertEqual(prepare.call_count, 1)

    def test_cache_damage_never_uses_fast_return(self):
        self.bind()
        _, build = update.preparation.prepared_runtime(self.root)
        (build / 'knowledge/evidence.json').write_text('{}')
        with self.assertRaises(update.UpdateError) as error:
            self.ensure()
        self.assertEqual(error.exception.code, 'CACHE_INVALID')

    def test_package_damage_checked_before_suppression(self):
        self.zip(self.source, 'return false\n')
        self.ensure(self.source)
        (self.root / 'knowledge/evidence.json').write_text('{}')
        with self.assertRaises(update.UpdateError) as error:
            self.ensure()
        self.assertEqual(error.exception.code, 'PUBLIC_PACKAGE_INVALID')

    def test_package_upgrade_retries_same_source(self):
        self.bind()
        path = self.root / 'run_kb.py'
        path.write_bytes(path.read_bytes() + b'\n# synthetic package upgrade\n')
        self.assertEqual(self.ensure()['status'], 'PREPARED')

    def test_interruption_persists_attempt_and_explicit_retry_recovers(self):
        with mock.patch.object(update.preparation, 'prepare', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.ensure(self.source)
        self.assertEqual(self.ensure()['status'], 'RETRY_SUPPRESSED')
        self.assertEqual(self.ensure(retry=True)['status'], 'PREPARED')

    def test_source_replaced_during_prepare_is_not_success(self):
        original = update.preparation.prepare
        def prepare(*args):
            result = original(*args)
            self.zip(self.source, 'first\n' + self.fixture.body, extra=True)
            return result
        with mock.patch.object(update.preparation, 'prepare', side_effect=prepare):
            result = self.ensure(self.source)
        self.assertEqual(result['status'], 'INPUT_CHANGED_AFTER_PREPARATION')
        self.assertFalse(result['reconnect_required'])
        _, build = update.preparation.prepared_runtime(self.root)
        receipt = update.preparation.read(build / 'PREPARATION-RECEIPT.json')
        self.assertEqual(receipt['source_inputs'][0]['archive_sha256'], result['source_sha256'])
        self.assertNotEqual(result['source_sha256'], update.compatibility.file_sha(self.source))
        self.assertEqual(self.ensure()['status'], 'PREPARED')

    def test_package_changes_during_prepare_are_not_success(self):
        original = update.preparation.prepare
        def prepare(*args):
            result = original(*args)
            path = self.root / 'run_kb.py'
            path.write_bytes(path.read_bytes() + b'\n# concurrent synthetic package change\n')
            return result
        with mock.patch.object(update.preparation, 'prepare', side_effect=prepare):
            result = self.ensure(self.source)
        self.assertEqual(result['status'], 'INPUT_CHANGED_AFTER_PREPARATION')
        self.assertFalse(result['reconnect_required'])

    def test_source_replaced_during_snapshot_never_prepares(self):
        self.bind()
        config, _ = update.preparation.prepared_runtime(self.root)
        activation = config.read_bytes()
        original = update.compatibility.file_sha
        def hash_file(path):
            result = original(path)
            if Path(path).name == 'scripts.zip':
                self.zip(self.source, 'first\n' + self.fixture.body, extra=True)
            return result
        with mock.patch.object(update.compatibility, 'file_sha', side_effect=hash_file), mock.patch.object(
                update.preparation, 'prepare', side_effect=AssertionError('moving input must not prepare')):
            with self.assertRaises(update.UpdateError) as error:
                self.ensure(retry=True)
        self.assertEqual(error.exception.code, 'SOURCE_CHANGED_DURING_READ')
        self.assertEqual(config.read_bytes(), activation)

    def test_cache_damage_checked_before_failed_fingerprint_suppression(self):
        self.bind()
        _, build = update.preparation.prepared_runtime(self.root)
        self.zip(self.source, 'return false\n')
        self.ensure()
        (build / 'knowledge/evidence.json').write_text('{}')
        with self.assertRaises(update.UpdateError) as error:
            self.ensure()
        self.assertEqual(error.exception.code, 'CACHE_INVALID')

    def test_state_replace_failure_keeps_prior_complete_state(self):
        self.bind()
        path = self.root / 'cache/source-update/state.json'
        before = path.read_bytes()
        with mock.patch.object(update.os, 'replace', side_effect=OSError('synthetic permission failure')):
            with self.assertRaises(OSError):
                self.ensure(retry=True)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(path.parent.glob('.pending-*')), [])

    def test_same_fingerprint_invalid_zip_does_not_loop(self):
        self.source.write_bytes(b'not a ZIP')
        self.assertEqual(self.ensure(self.source)['status'], 'PREPARATION_FAILED')
        self.assertEqual(self.ensure()['status'], 'RETRY_SUPPRESSED')

    def test_lock_contention_is_nonblocking_and_does_not_start_prepare(self):
        directory = self.root / 'cache/source-update'
        directory.mkdir(parents=True)
        with update.preparation.preparation_lock(directory / '.ensure.lock'):
            with self.assertRaises(update.preparation.PreparationError):
                self.ensure(self.source)

    def test_limits_checked_before_prepare(self):
        with mock.patch.object(update, 'MAX_ZIP', 10):
            with self.assertRaises(update.UpdateError) as error:
                self.ensure(self.source)
        self.assertEqual(error.exception.code, 'SOURCE_LIMIT')

    def test_zip_member_limits_and_traversal(self):
        with zipfile.ZipFile(self.source, 'w') as archive:
            archive.writestr('../escape.lua', 'return false')
        self.assertEqual(self.ensure(self.source)['status'], 'PREPARATION_FAILED')

    def test_invalid_state_rejected(self):
        directory = self.root / 'cache/source-update'
        directory.mkdir(parents=True)
        (directory / 'state.json').write_text('{"schema":"bad"}')
        with self.assertRaises(update.UpdateError):
            self.ensure(self.source)

    def test_non_directory_cache_path_fails_without_preparing(self):
        (self.root / 'cache').mkdir()
        (self.root / 'cache/source-update').write_text('preserve user file')
        with mock.patch.object(update.preparation, 'prepare', side_effect=AssertionError('cannot write cache')):
            with self.assertRaises(OSError):
                self.ensure(self.source)
        self.assertEqual((self.root / 'cache/source-update').read_text(), 'preserve user file')

    def test_actual_registered_sidecar_against_synthetic_zip(self):
        fixture = registered.RegisteredAssessmentTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        directory = fixture.root / 'reports'
        directory.mkdir()
        # The mechanism package is a source-free, manifest-committed fixture.
        result = update.sidecar(fixture.root, directory, fixture.target, 'a' * 64)
        report = update.preparation.read(fixture.root / result)
        self.assertEqual(report['registration']['candidate_count'], 2)
        self.assertEqual(report['reference_status_counts'], {'byte_identical': 2})
        self.assertFalse(report['runtime_verified'])

    def test_cli_failure_and_status_codes(self):
        with mock.patch.object(update, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(update.main(['status']), 0)
            self.assertEqual(update.main(['ensure']), 2)
            self.assertEqual(update.main(['ensure', '--source', str(self.source)]), 0)


if __name__ == '__main__':
    unittest.main()

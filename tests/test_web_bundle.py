"""Synthetic complete-release checks; no installed game or private input required."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_release as bundle
import prepare_sources as bootstrap


class CompleteReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / 'source'
        self.source.mkdir()
        for directory in bundle.DIRECTORIES:
            (self.source / directory).mkdir()
        for name in bundle.ROOT_FILES:
            self.put(name, '# fixture\n')
        for name in bundle.SCRIPTS:
            self.put('scripts/' + name, '# fixture\n')
        for name in bundle.SERVICE_FILES:
            self.put('dst-kb-service/' + name, '# fixture\n')
        self.put('dst-kb-service/dst_kb/mcp_server.py', '# MCP\n')
        self.put('dst-kb-service/docs/mcp-tools.md', '# Nine tools\n')
        self.put('dst-kb-service/docs/mcp-tools.json', '{"tools": []}\n')
        self.put('dst-kb-service/tests/test_public_service.py', '# Public regression\n')
        for name in ('contract_map.json', 'projection_profiles.json', 'source_identity_map.json'):
            self.put('dst-kb-service/dst_kb/' + name, '{}\n')
        for name in ('contract_map.json', 'source_identity_map.json', 'source-manifest.json'):
            self.put('epoch-assets/759671/' + name, '{}\n')
        self.put('source-epochs.json', json.dumps({'default_source_epoch': '759671', 'epochs': {'759671': {}}}))
        self.put('references/web-chat.md', '# Web use\n')
        self.put('templates/local-validation.md', '# Validation\n')
        self.put('examples/review.json', '{}\n')
        self.put('knowledge/data/entries.json', '{"entries": []}\n')
        self.catalog = {'entries': [
            {'id': f'{family}-{index}', 'family': family, 'file': 'data/entries.json'}
            for family, count in bundle.EXPECTED_COUNTS.items() for index in range(count)]}
        self.put('knowledge/CATALOG.json', json.dumps(self.catalog))
        self.manifest()
        self.output = self.source / 'dist/release'

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, content):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode('utf-8'))

    def manifest(self):
        files = []
        for name in ('CATALOG.json', 'data/entries.json'):
            data = (self.source / 'knowledge' / name).read_bytes()
            files.append({'path': name, 'sha256': bundle.sha(data), 'bytes': len(data)})
        self.put('knowledge/PACKAGE-MANIFEST.json', json.dumps({'files': files}))

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return bundle.main(['--source', str(self.source), '--out', str(self.output), *args])

    def test_single_archive_has_skill_187_catalog_and_complete_mcp_without_duplicate_knowledge(self):
        for path in ('cache/runtime/private.lua', 'dist/old.zip', '.git/config',
                     'knowledge-history/old/data/entries.json', 'dst-engineering-kb/data/entries.json',
                     'compatibility/v0.1/data/entries.json', 'epoch-assets/756039/old.json',
                     'references/secret.dat', 'dst-kb-service/config.local.json'):
            self.put(path, 'DO NOT PACKAGE')
        outputs = bundle.make_outputs(self.source)
        self.assertEqual(set(outputs), {bundle.ARCHIVE, bundle.CHECKSUMS})
        self.assertEqual(outputs[bundle.CHECKSUMS], (bundle.sha(outputs[bundle.ARCHIVE])
                         + '  ' + bundle.ARCHIVE + '\n').encode('ascii'))
        inputs = bundle.source_files(self.source)
        with zipfile.ZipFile(io.BytesIO(outputs[bundle.ARCHIVE])) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(set(names), {bundle.NAME + '/' + name for name in inputs}
                             | {bundle.NAME + '/' + bundle.MANIFEST})
            self.assertIn(bundle.NAME + '/SKILL.md', names)
            self.assertIn(bundle.NAME + '/prepare_sources.py', names)
            self.assertIn(bundle.NAME + '/run_kb.py', names)
            self.assertIn(bundle.NAME + '/scripts/public_rebind.py', names)
            self.assertIn(bundle.NAME + '/dst-kb-service/dst_kb/mcp_server.py', names)
            self.assertIn(bundle.NAME + '/dst-kb-service/dst_kb/projection_profiles.json', names)
            self.assertIn(bundle.NAME + '/dst-kb-service/docs/mcp-tools.json', names)
            catalog = json.loads(archive.read(bundle.NAME + '/knowledge/CATALOG.json'))
            self.assertEqual(len(catalog['entries']), 187)
            manifest = json.loads(archive.read(bundle.NAME + '/' + bundle.MANIFEST))
            self.assertEqual(manifest['knowledge_records'], 187)
            self.assertEqual(manifest['knowledge_families'], bundle.EXPECTED_COUNTS)
            for name, record in manifest['files'].items():
                data = archive.read(bundle.NAME + '/' + name)
                self.assertEqual(record, {'sha256': bundle.sha(data), 'bytes': len(data)})
                self.assertNotIn(b'DO NOT PACKAGE', data)

    def test_deterministic_bytes_ignore_mtime(self):
        first = bundle.make_outputs(self.source)
        for path in self.source.rglob('*'):
            if path.is_file():
                os.utime(path, (1000000000, 1000000000))
        self.assertEqual(first, bundle.make_outputs(self.source))
        with zipfile.ZipFile(io.BytesIO(first[bundle.ARCHIVE])) as archive:
            for info in archive.infolist():
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)

    def test_source_preparation_input_closure_is_packaged(self):
        inputs = bundle.source_files(self.source)
        required = {row['path'] for row in bootstrap.package_inputs(self.source)}
        self.assertFalse(required - inputs.keys())

    def test_changed_knowledge_missing_manifest_and_invalid_paths_fail(self):
        self.put('knowledge/data/entries.json', 'tampered')
        self.assertEqual(self.cli(), 2)
        self.assertFalse(self.output.exists())
        self.manifest()
        self.assertEqual(self.cli(), 0)
        (self.source / 'knowledge/PACKAGE-MANIFEST.json').unlink()
        self.assertEqual(self.cli(), 2)
        self.put('knowledge/PACKAGE-MANIFEST.json', json.dumps({'files': [
            {'path': '../private.json', 'bytes': 0, 'sha256': '0' * 64}]}))
        self.assertEqual(self.cli(), 2)

    def test_incomplete_duplicate_and_wrong_family_catalogs_fail(self):
        for change in ('missing', 'duplicate', 'family'):
            with self.subTest(change=change):
                altered = json.loads(json.dumps(self.catalog))
                if change == 'missing':
                    altered['entries'].pop()
                elif change == 'duplicate':
                    altered['entries'][1]['id'] = altered['entries'][0]['id']
                else:
                    altered['entries'][0]['family'] = 'native_ai'
                self.put('knowledge/CATALOG.json', json.dumps(altered))
                self.manifest()
                self.assertEqual(self.cli(), 2)

    def test_other_runtime_epoch_is_rejected(self):
        self.put('source-epochs.json', json.dumps({'default_source_epoch': '759671',
                                                 'epochs': {'759671': {}, '756039': {}}}))
        self.assertEqual(self.cli(), 2)

    def test_local_only_input_and_missing_mcp_fail_without_output(self):
        self.put('references/web-chat.md', '\ufeff  <!-- local-only -->\nprivate\n')
        self.assertEqual(self.cli(), 2)
        self.assertFalse(self.output.exists())
        self.put('references/web-chat.md', '# Public\n')
        (self.source / 'dst-kb-service/dst_kb/mcp_server.py').unlink()
        self.assertEqual(self.cli(), 2)

    def test_check_is_read_only_and_owned_release_can_update(self):
        self.assertEqual(self.cli('--check'), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.cli(), 0)
        self.assertEqual(self.cli('--check'), 0)
        original = bundle.existing_files(self.output)
        self.put('README.md', '# Updated\n')
        self.assertEqual(self.cli('--check'), 1)
        self.assertEqual(bundle.existing_files(self.output), original)
        self.assertEqual(self.cli(), 0)
        self.assertEqual(self.cli('--check'), 0)

    def test_modified_or_unowned_outputs_are_preserved(self):
        self.output.mkdir(parents=True)
        self.put('dist/release/user.md', 'keep')
        self.assertEqual(self.cli(), 2)
        self.assertEqual((self.output / 'user.md').read_text(), 'keep')
        (self.output / 'user.md').unlink()
        self.assertEqual(self.cli(), 0)
        (self.output / bundle.ARCHIVE).write_bytes(b'user modification')
        before = bundle.existing_files(self.output)
        self.assertEqual(self.cli(), 2)
        self.assertEqual(bundle.existing_files(self.output), before)

    def test_failed_replace_restores_both_assets(self):
        self.assertEqual(self.cli(), 0)
        before = bundle.existing_files(self.output)
        self.put('README.md', '# Revised\n')
        real_replace = os.replace
        calls = 0
        def fail_once(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return real_replace(source, target)
        with mock.patch.object(bundle.os, 'replace', side_effect=fail_once):
            self.assertEqual(self.cli(), 2)
        self.assertEqual(bundle.existing_files(self.output), before)
        self.assertEqual(list(self.output.parent.glob('.dme-release-*')), [])

    def test_output_locations_and_symlinks_are_rejected(self):
        for path in (self.source, self.base, self.source / 'scripts/output', self.source / 'docs'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                bundle.output_path(self.source, path)
        target = self.base / 'outside.md'
        target.write_bytes(b'outside')
        link = self.source / 'references/linked.md'
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f'Host cannot create symlinks: {exc}')
        with self.assertRaises(ValueError):
            bundle.make_outputs(self.source)


class RepositoryReleaseTests(unittest.TestCase):
    def test_real_repository_preparation_input_closure_and_unique_187_catalog(self):
        root = Path(__file__).resolve().parents[1]
        inputs = bundle.source_files(root)
        required = {row['path'] for row in bootstrap.package_inputs(root)}
        self.assertFalse(required - inputs.keys(), 'Runtime inputs absent from release')
        catalog = json.loads(inputs['knowledge/CATALOG.json'])
        self.assertEqual(len(catalog['entries']), 187)
        self.assertFalse(any(name.startswith(('knowledge-history/', 'dst-engineering-kb/',
                                              'compatibility/', 'knowledge/history/')) for name in inputs))


if __name__ == '__main__':
    unittest.main(verbosity=2)

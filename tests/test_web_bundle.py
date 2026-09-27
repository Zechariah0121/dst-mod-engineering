"""No network, installed skill, game, or real publication output is needed."""
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
import build_web_bundle as bundle


class WebBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / 'source'
        self.source.mkdir()
        for directory in bundle.DIRECTORIES:
            (self.source / directory).mkdir()
        names = set(bundle.ROOT_FILES) | set(bundle.COMMON) | {'templates/local-validation.md'}
        names.update(f'references/{name}.md' for entries in bundle.PROFILE_EXTRA.values() for name in entries)
        names.update({'docs/validation.md', 'scripts/tool.py'})
        for name in names:
            self.put(name, f'# {name}\n\nOriginal body 中文\n')
        self.put('SKILL.md', '---\nname: dst-mod-engineering\ndescription: fixture\n---\n\n'
                 '[Environment](references/environment-tools.md)\n')
        self.put('references/web-chat.md', '# Web\n\n[Template](../templates/local-validation.md#result)\n'
                 '[Source][sample]\n[sample]: ../SKILL.md "Title"\n'
                 '```md\n[Example](keep-relative.md)\n```\n')
        self.output = self.source / 'dist/web'

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, content):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode('utf-8'))

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return bundle.main(['--source', str(self.source), '--out', str(self.output), *args])

    def test_deterministic_bytes_ignore_mtime(self):
        first = bundle.make_outputs(self.source)
        for path in self.source.rglob('*'):
            if path.is_file():
                os.utime(path, (1000000000, 1000000000))
        self.assertEqual(first, bundle.make_outputs(self.source))

    def test_native_zip_layout_raw_content_and_allowlist(self):
        for name in ['private/secret.md', 'tests/test.py', '.git/config', 'dist/old.py',
                     'references/private.dat', 'references/nested/extra.md']:
            self.put(name, 'DO NOT PACKAGE')
        inputs = bundle.source_files(self.source)
        outputs = bundle.make_outputs(self.source)
        with zipfile.ZipFile(io.BytesIO(outputs[f'{bundle.NAME}.skill.zip'])) as archive:
            self.assertEqual(set(archive.namelist()), {bundle.NAME + '/' + name for name in inputs})
            self.assertIn(bundle.NAME + '/SKILL.md', archive.namelist())
            for info in archive.infolist():
                self.assertEqual(archive.read(info), inputs[info.filename.split('/', 1)[1]])
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))

    def test_profiles_source_hashes_complete_text_and_link_destinations(self):
        outputs = bundle.make_outputs(self.source)
        index = json.loads(outputs[bundle.INDEX])
        for profile, sources in index['profiles'].items():
            body = outputs[f'web-{profile}.md'].decode('utf-8')
            self.assertTrue(set(bundle.COMMON).issubset(sources))
            self.assertEqual(sources[-1], 'LICENSE')
            for source in sources:
                raw = (self.source / source).read_bytes()
                self.assertEqual(index['inputs'][source], bundle.sha(raw))
                self.assertIn(f'## 来源：`{source}`', body)
                self.assertIn(f'原始 SHA-256：`{bundle.sha(raw)}`', body)
                self.assertIn(bundle.rewrite_links(raw.decode('utf-8'), source), body)
        starter = outputs['web-starter.md'].decode('utf-8')
        self.assertIn(f'{bundle.REPOSITORY}/blob/main/references/environment-tools.md', starter)
        self.assertIn(f'{bundle.REPOSITORY}/blob/main/templates/local-validation.md#result', starter)
        self.assertIn(f'[sample]: {bundle.REPOSITORY}/blob/main/SKILL.md "Title"', starter)
        self.assertIn('```md\n[Example](keep-relative.md)\n```', starter)

    def test_reading_zip_inner_and_outer_indexes_have_no_self_hash_cycle(self):
        outputs = bundle.make_outputs(self.source)
        outer = json.loads(outputs[bundle.INDEX])
        self.assertNotIn(bundle.INDEX, outer['outputs'])
        for name, record in outer['outputs'].items():
            self.assertEqual(record, bundle.metadata(outputs[name]))
        with zipfile.ZipFile(io.BytesIO(outputs['web-reading.zip'])) as archive:
            inner = json.loads(archive.read('reading-index.json'))
            self.assertNotIn('reading-index.json', inner['outputs'])
            self.assertEqual(inner['source_fingerprint'], outer['source_fingerprint'])
            self.assertEqual(archive.read('local-validation.md'),
                             (self.source / 'templates/local-validation.md').read_bytes())
            self.assertEqual(archive.read('LICENSE'), (self.source / 'LICENSE').read_bytes())
            for name, record in inner['outputs'].items():
                self.assertEqual(record, bundle.metadata(archive.read(name)))

    def test_check_detects_missing_stale_extra_without_writing(self):
        self.assertEqual(self.cli('--check'), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.cli(), 0)
        self.assertEqual(self.cli('--check'), 0)
        original = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.put('README.md', '# Changed source\n')
        self.assertEqual(self.cli('--check'), 1)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, original)
        (self.output / 'stale-user.md').write_bytes(b'keep')
        self.assertEqual(self.cli('--check'), 1)
        self.assertEqual(self.cli(), 2)
        self.assertEqual((self.output / 'stale-user.md').read_bytes(), b'keep')

    def test_missing_profile_source_fails_without_partial_output(self):
        (self.source / 'references/worldgen-spatial.md').unlink()
        self.assertEqual(self.cli(), 2)
        self.assertFalse(self.output.exists())

    def test_rebuild_updates_owned_outputs_and_repairs_missing_owned_file(self):
        self.assertEqual(self.cli(), 0)
        (self.output / 'web-starter.md').unlink()
        self.put('README.md', '# Revised source\n')
        self.assertEqual(self.cli(), 0)
        self.assertEqual(self.cli('--check'), 0)

    def test_unowned_or_user_modified_outputs_are_preserved(self):
        self.output.mkdir(parents=True)
        target = self.output / 'web-starter.md'
        target.write_bytes(b'user note')
        self.assertEqual(self.cli(), 2)
        self.assertEqual(target.read_bytes(), b'user note')
        target.unlink()
        self.assertEqual(self.cli(), 0)
        target.write_bytes(b'edited generated file')
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.assertEqual(self.cli(), 2)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, before)

    def test_dangerous_output_locations_are_rejected(self):
        for path in [self.source, self.base, self.source / 'scripts/output',
                     self.source / 'references/output', self.source / 'docs']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                bundle.output_path(self.source, path)

    def test_modified_index_is_not_silently_overwritten(self):
        self.assertEqual(self.cli(), 0)
        path = self.output / bundle.INDEX
        data = json.loads(path.read_bytes())
        data['user_note'] = 'keep this'
        path.write_bytes(bundle.json_bytes(data))
        before = path.read_bytes()
        self.assertEqual(self.cli(), 2)
        self.assertEqual(path.read_bytes(), before)

    def test_relative_link_resolution_and_escape_rejection(self):
        self.assertEqual(bundle.public_link('<../README.md#intro>', 'references/web-chat.md'),
                         f'<{bundle.REPOSITORY}/blob/main/README.md#intro>')
        self.assertEqual(bundle.public_link('#intro', 'README.md'), f'{bundle.REPOSITORY}/blob/main/README.md#intro')
        self.assertEqual(bundle.public_link('scripts/', 'SKILL.md'), f'{bundle.REPOSITORY}/tree/main/scripts')
        self.assertEqual(bundle.public_link('https://example.com/a', 'SKILL.md'), 'https://example.com/a')
        with self.assertRaises(ValueError):
            bundle.public_link('../../private.md', 'references/web-chat.md')

    def test_linked_badge_rewrites_outer_destination_in_flat_document(self):
        badge = '[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)'
        expected = ('[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)]'
                    f'({bundle.REPOSITORY}/blob/main/LICENSE)')
        self.put('README.md', '# Readme\n\n' + badge + '\n')
        self.assertEqual(bundle.rewrite_links(badge, 'README.md'), expected)
        flattened = bundle.make_outputs(self.source)['web-full.md'].decode('utf-8')
        self.assertIn(expected, flattened)
        self.assertNotIn(badge, flattened)
        self.assertEqual(bundle.rewrite_links('[![Badge](badge.svg)](README.md "Read")', 'SKILL.md'),
                         f'[![Badge]({bundle.REPOSITORY}/blob/main/badge.svg)]'
                         f'({bundle.REPOSITORY}/blob/main/README.md "Read")')

    def test_symlink_input_and_output_are_rejected(self):
        target = self.base / 'outside.md'
        target.write_bytes(b'outside')
        link = self.source / 'references/linked.md'
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f'Host cannot create symlinks: {exc}')
        with self.assertRaises(ValueError):
            bundle.make_outputs(self.source)
        link.unlink()
        external = self.base / 'outside-output'
        external.mkdir()
        self.output.parent.mkdir(parents=True)
        self.output.symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            bundle.output_path(self.source, self.output)

    def test_transaction_restores_owned_output_after_replace_failure(self):
        self.assertEqual(self.cli(), 0)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.put('README.md', '# Changed\n')
        real_replace = os.replace
        calls = 0
        def fail_once(source, destination):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated disk error')
            return real_replace(source, destination)
        with mock.patch.object(bundle.os, 'replace', side_effect=fail_once):
            self.assertEqual(self.cli(), 2)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, before)
        self.assertEqual(list(self.output.parent.glob('.dme-web-*')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

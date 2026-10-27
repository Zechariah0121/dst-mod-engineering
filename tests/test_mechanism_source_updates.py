"""Synthetic source updates preserve evidence identity without a whole-ZIP gate."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import native_mechanism_source as source


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class SourceUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mechanism-update-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_raw = b'-- toy\nfunction AuthoredToy()\nend\n'
        self.old = self.archive('old.zip', {'scripts/toy.lua': self.old_raw})
        self.doc = {'source_epoch': 'old-evidence-epoch', 'archive_sha256': sha(self.old.read_bytes()),
                    'source_references': [{'id': 'R', 'source_file': 'scripts/toy.lua',
                                           'file_sha256': sha(self.old_raw), 'line_start': 2, 'line_end': 3,
                                           'range_sha256': sha(b'function AuthoredToy()\nend'),
                                           'symbols': ['AuthoredToy']}],
                    'entries': [{'id': 'E', 'scope': {'source_epoch': 'old-evidence-epoch',
                                                    'runtime_verified': False}}]}
        self.write_candidate()

    def archive(self, name, members):
        target = self.root / name
        with zipfile.ZipFile(target, 'w') as archive:
            for path, raw in members.items():
                archive.writestr(path, raw)
        return target

    def write_candidate(self):
        path = self.root / 'knowledge/toy.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(self.doc), encoding='utf-8')
        registry = {'families': [{'name': 'native_mechanism', 'documents': [
            {'file': 'toy.json', 'sha256': sha(path.read_bytes())}]}]}
        (path.parent / 'FAMILY-REGISTRY.json').write_text(json.dumps(registry), encoding='utf-8')

    def check(self, *inputs):
        report = source.verify(self.root, inputs)
        self.assertFalse(report['runtime_verified'])
        self.assertFalse(report['coding_admission'])
        self.assertFalse(report['source_text_returned'])
        self.assertEqual(sum(report['reference_counts'].values()), report['total_references'])
        self.assertNotIn('AuthoredToy', json.dumps(report))
        return report, report['documents'][0]['references'][0]

    def test_new_zip_unrelated_file_accepts_exact_ref_and_preserves_scope(self):
        new = self.archive('new.zip', {'scripts/toy.lua': self.old_raw, 'scripts/other.lua': b'-- new'})
        before = (self.root / 'knowledge/toy.json').read_bytes()
        report, ref = self.check(new)
        self.assertEqual(ref['status'], 'EXACT_FILE_RANGE')
        self.assertEqual(report['verified_references'], 1)
        self.assertTrue(report['all_references_verified'])
        self.assertFalse(ref['source_checks'][0]['evidence_archive_identity_matched'])
        self.assertEqual(report['documents'][0]['evidence_epoch'], 'old-evidence-epoch')
        self.assertEqual(report['documents'][0]['archive_sha256'], self.doc['archive_sha256'])
        self.assertEqual(before, (self.root / 'knowledge/toy.json').read_bytes())
        self.assertEqual(report['provided_sources'][0]['archive_sha256'], sha(new.read_bytes()))

    def test_same_range_changed_file_never_grants_file_identity(self):
        new = self.archive('new.zip', {'scripts/toy.lua': self.old_raw.replace(b'-- toy', b'-- changed')})
        report, ref = self.check(new)
        self.assertEqual(ref['status'], 'RANGE_ONLY')
        self.assertEqual(report['verified_references'], 0)
        self.assertFalse(report['all_references_verified'])
        self.assertEqual(report['status'], 'PARTIAL_LOCATOR_MATCHES')
        check = ref['source_checks'][0]
        self.assertFalse(check['source_file_identity_verified'])
        self.assertFalse(check['behavior_verified'])
        self.assertFalse(check['relocated'])

    def test_scripts_directory_itself_has_the_same_explicit_locator_result(self):
        scripts = self.root / 'input/scripts'
        scripts.mkdir(parents=True)
        (scripts / 'toy.lua').write_bytes(self.old_raw)
        _, outer = self.check(scripts.parent)
        _, inner = self.check(scripts)
        self.assertEqual(outer['status'], 'EXACT_FILE_RANGE')
        self.assertEqual(inner['status'], outer['status'])
        self.assertIsNone(inner['source_checks'][0]['provided_archive_sha256'])

    def test_unique_moved_range_has_new_coordinates_only_in_check(self):
        new = self.archive('new.zip', {'scripts/toy.lua': b'-- inserted\n' + self.old_raw})
        _, ref = self.check(new)
        self.assertEqual(ref['status'], 'RANGE_ONLY')
        self.assertEqual(ref['evidence_line_start'], 2)
        self.assertEqual(ref['source_checks'][0]['line_start'], 3)
        self.assertTrue(ref['source_checks'][0]['relocated'])

    def test_multiple_range_matches_are_unknown_even_if_original_position_matches(self):
        new = self.archive('new.zip', {'scripts/toy.lua': self.old_raw + b'function AuthoredToy()\nend\n'})
        _, ref = self.check(new)
        self.assertEqual(ref['status'], 'CHANGED_UNKNOWN')
        self.assertEqual(ref['source_checks'][0]['reason'], 'ambiguous_range_match')
        self.assertNotIn('line_start', ref['source_checks'][0])

    def test_changed_and_missing_refs_are_reported_without_abort(self):
        for members, status in (({'scripts/toy.lua': b'-- completely changed\n'}, 'CHANGED_UNKNOWN'),
                                ({'scripts/other.lua': b'-- new'}, 'MISSING')):
            with self.subTest(status=status):
                new = self.archive('new.zip', members)
                report, ref = self.check(new)
                self.assertEqual(ref['status'], status)
                self.assertEqual(report['status'], 'NO_LOCATOR_MATCHES')
                self.assertEqual(report['verified_references'], 0)

    def test_all_explicit_sources_keep_order_and_target_unknown_visible(self):
        new = self.archive('new.zip', {'scripts/toy.lua': b'-- changed'})
        report, ref = self.check(new, self.old, new)
        self.assertEqual([x['source_input_index'] for x in report['provided_sources']], [0, 1, 2])
        self.assertEqual([x['status'] for x in ref['source_checks']],
                         ['CHANGED_UNKNOWN', 'EXACT_FILE_RANGE', 'CHANGED_UNKNOWN'])
        self.assertEqual(ref['status'], 'EXACT_FILE_RANGE')
        self.assertEqual(report['verified_references'], 1)

    def test_unsafe_duplicate_and_normalized_duplicate_zip_names_fail_closed(self):
        for names in (['scripts/../toy.lua'], ['/scripts/toy.lua'], ['scripts\\toy.lua'],
                      ['scripts/toy.lua', 'scripts/toy.lua'], ['scripts/', 'scripts']):
            with self.subTest(names=names):
                target = self.root / 'unsafe.zip'
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    with zipfile.ZipFile(target, 'w') as archive:
                        for name in names:
                            info = zipfile.ZipInfo(name)
                            info.filename = name
                            archive.writestr(info, b'-- toy')
                with self.assertRaises(ValueError):
                    self.check(target)

    def test_exact_old_archive_bad_commitments_still_error_with_other_source(self):
        new = self.archive('new.zip', {'scripts/toy.lua': self.old_raw, 'scripts/other.lua': b'-- new'})
        for change in ({'file_sha256': '0' * 64}, {'range_sha256': '0' * 64}, {'line_end': 99},
                       {'source_file': 'scripts/missing.lua'}):
            with self.subTest(change=change):
                original = copy.deepcopy(self.doc)
                self.doc['source_references'][0].update(change)
                self.write_candidate()
                with self.assertRaises(ValueError):
                    self.check(new, self.old)
                self.doc = original

    def test_malformed_refs_fail_without_matching_old_zip(self):
        new = self.archive('new.zip', {'scripts/other.lua': b'-- new'})
        for change in ({'file_sha256': 'bad'}, {'line_start': True}, {'line_start': 0},
                       {'line_end': '3'}, {'source_file': 'scripts/../escape.lua'}, {'symbols': 'bad'}):
            with self.subTest(change=change):
                original = copy.deepcopy(self.doc)
                self.doc['source_references'][0].update(change)
                self.write_candidate()
                with self.assertRaises(ValueError):
                    self.check(new)
                self.doc = original

    def test_candidate_commitment_damage_is_fatal(self):
        (self.root / 'knowledge/toy.json').write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'candidate hash'):
            self.check(self.old)

    def test_directory_reads_only_ref_paths_and_has_no_archive_identity(self):
        directory = self.root / 'explicit'
        (directory / 'scripts').mkdir(parents=True)
        (directory / 'scripts/toy.lua').write_bytes(self.old_raw)
        (directory / 'unrelated.zip').write_bytes(b'not scanned')
        report, ref = self.check(directory)
        self.assertEqual(ref['status'], 'EXACT_FILE_RANGE')
        self.assertEqual(report['provided_sources'][0]['kind'], 'DIRECTORY')
        self.assertIsNone(report['provided_sources'][0]['archive_sha256'])
        self.assertFalse(ref['source_checks'][0]['evidence_archive_identity_matched'])
        (directory / 'scripts/toy.lua').unlink()
        _, ref = self.check(directory)
        self.assertEqual(ref['status'], 'MISSING')

    def test_directory_symlink_is_rejected(self):
        directory = self.root / 'linked'
        (directory / 'scripts').mkdir(parents=True)
        target = self.root / 'outside.lua'
        target.write_bytes(self.old_raw)
        try:
            (directory / 'scripts/toy.lua').symlink_to(target)
        except OSError as exc:
            self.skipTest('Symlink creation not permitted: ' + str(exc))
        with self.assertRaisesRegex(ValueError, 'symlink or reparse'):
            self.check(directory)

    def test_bounded_relocation_returns_unknown(self):
        new = self.archive('new.zip', {'scripts/toy.lua': b'-- inserted\n' + self.old_raw})
        with patch.object(source, 'MAX_SCAN_WINDOWS', 1):
            _, ref = self.check(new)
        self.assertEqual(ref['status'], 'CHANGED_UNKNOWN')
        self.assertEqual(ref['source_checks'][0]['reason'], 'range_scan_limit')

    def test_empty_sources_and_missing_explicit_input(self):
        report, ref = self.check()
        self.assertEqual(ref['status'], 'CHANGED_UNKNOWN')
        self.assertEqual(report['provided_sources'], [])
        with self.assertRaises(OSError):
            self.check(self.root / 'missing.zip')


if __name__ == '__main__':
    unittest.main(verbosity=2)

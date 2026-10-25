import base64
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "scripts"))
from pathlib import Path
import tempfile
import unittest
import zipfile

import source_payload as payload


class HydrationTests(unittest.TestCase):
    def slot(self, raw, encoding='utf8', original_file=b'old file\n'):
        value = base64.b64encode(raw).decode() if encoding == 'base64' else raw.decode()
        return {'content_sha256': payload.sha(raw), 'content_bytes': len(raw),
                'original_json_value_sha256': payload.digest(value), 'encoding': encoding,
                'line_count': len(raw.splitlines()), 'coordinates': [{'source_file': 'scripts/a.lua',
                'expected_file_sha256': payload.sha(original_file), 'line_start': 2, 'line_end': 3}]}

    def test_exact_lf_and_shifted_content_is_not_whole_file_proof(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'a.lua').write_bytes(b'added\nfirst\nfunction A()\nend\n')
            sources = payload.Sources([root])
            value, report = payload.recover(self.slot(b'function A()\nend\n'), sources)
            self.assertEqual(value, 'function A()\nend\n')
            self.assertEqual(report['matched_line_start'], 3)
            self.assertFalse(report['provided_whole_file_equals_original'])
            sources.close()

    def test_crlf_raw_base64_recovery_from_lf_source(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'source.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('scripts/a.lua', b'first\nfunction A()\nend\n')
            sources = payload.Sources([path])
            raw = b'function A()\r\nend\r\n'
            value, report = payload.recover(self.slot(raw, 'base64'), sources)
            self.assertEqual(base64.b64decode(value), raw)
            self.assertEqual(report['line_transform'], 'CRLF')
            sources.close()

    def test_wrong_source_never_rewrites_expected_hash(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'a.lua').write_bytes(b'first\nfunction Wrong()\nend\n')
            sources = payload.Sources([root])
            slot = self.slot(b'function A()\nend\n')
            expected = slot['content_sha256']
            self.assertEqual(payload.recover(slot, sources), (None, None))
            self.assertEqual(slot['content_sha256'], expected)
            sources.close()

    def test_same_bytes_base64_utf8_cache_orders_preserve_slot_values(self):
        raw = b'function A()\nend\n'
        for order in (('base64', 'utf8'), ('utf8', 'base64')):
            with self.subTest(order=order):
                with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
                    root = Path(directory)
                    (root / 'a.lua').write_bytes(b'first\n' + raw)
                    sources, cache = payload.Sources([root]), {}
                    try:
                        for encoding in order:
                            slot = self.slot(raw, encoding)
                            value, evidence = payload.recover(slot, sources, cache)
                            expected = base64.b64encode(raw).decode() if encoding == 'base64' else raw.decode()
                            self.assertEqual(value, expected)
                            self.assertEqual(payload.digest(value), slot['original_json_value_sha256'])
                            # Exercise positive cache hits after both encodings exist.
                            again, _ = payload.recover(slot, sources, cache)
                            self.assertEqual(again, expected)
                        self.assertEqual(len(cache), 2)
                    finally:
                        sources.close()

    def test_cache_hit_revalidates_original_json_value(self):
        raw = b'function A()\nend\n'
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'a.lua').write_bytes(b'first\n' + raw)
            sources, cache = payload.Sources([root]), {}
            try:
                slot = self.slot(raw, 'utf8')
                payload.recover(slot, sources, cache)
                key = next(iter(cache))
                cache[key] = (base64.b64encode(raw).decode(), cache[key][1])
                with self.assertRaisesRegex(ValueError, 'Cached source payload differs'):
                    payload.recover(slot, sources, cache)
            finally:
                sources.close()

    def test_recipe_contains_no_payload_and_required_gap_is_explicit(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            private, template, output, source = [root / s for s in ('private', 'template', 'output', 'source')]
            source.mkdir()
            body = 'function UniqueFixture()\nend\n'
            node = {'path': 'scripts/a.lua', 'file_sha256': 'a' * 64,
                'line_start': 2, 'line_end': 3, 'range_sha256': payload.sha(body.encode()),
                'source_excerpt': body, 'snapshot_id': 'fixture'}
            payload.write_json(private / 'knowledge/evidence.json', {'facts': [node]})
            payload.write_json(private / 'knowledge/data/nativecore/native-core.json', {'entries': [
                {'id': 'fixture', 'claims': [{'kind': 'NSF', 'evidence_refs': [
                    {'artifact_path': 'evidence.json', 'pointer': '/facts/0'}]}]}]})
            recipe, templates = payload.generate_recipe(private)
            self.assertNotIn('UniqueFixture', str(recipe))
            self.assertEqual(recipe['summary']['required_slots'], 1)
            for name, document in templates.items():
                payload.write_json(template / name, document)
            report, _ = payload.hydrate(template, recipe, [source], output)
            self.assertEqual(report['status'], 'REQUIRED_SOURCE_GAP')
            self.assertEqual(report['missing_required_count'], 1)
            self.assertFalse(report['runtime_validation_performed'])

    def test_missing_optional_literal_is_deleted_without_marker(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            template, output, source = [root / s for s in ('template', 'output', 'source')]
            source.mkdir()
            slot = self.slot(b'function A()\nend\n')
            slot.update({'id': 'fixture-slot', 'path': 'evidence.json', 'pointer': '/citation/excerpt',
                'kind': 'source_literal', 'required_for_knowledge_shape': False,
                'missing_policy': 'DELETE_OBJECT_FIELD'})
            payload.write_json(template / 'evidence.json', {'citation': {
                'range_sha256': slot['content_sha256'], 'excerpt': {payload.MARKER: slot['id']}}})
            report, documents = payload.hydrate(template, {'schema': payload.SCHEMA, 'slots': [slot]},
                                                [source], output)
            self.assertNotIn('excerpt', documents['evidence.json']['citation'])
            self.assertEqual(report['missing_required_count'], 0)
            self.assertEqual(report['missing_optional_count'], 1)
            self.assertEqual(report['remaining_unresolved_marker_count'], 0)
            self.assertEqual(documents['evidence.json']['citation']['range_sha256'], slot['content_sha256'])
            self.assertFalse(report['runtime_validation_performed'])


if __name__ == '__main__':
    unittest.main()

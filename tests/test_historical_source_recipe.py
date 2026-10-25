"""Historical metadata cannot create required payload slots or hash aliases."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import source_payload as payload


def historical():
    body = 'local historical = true\n'
    return {'path': 'scripts/old.lua', 'file_sha256': 'a' * 64,
            'line_start': 3, 'line_end': 3, 'range_sha256': payload.sha(body.encode()),
            'snapshot_id': 'old', 'evidence_role': 'historical_comparison',
            'supports_current_behavior': False, 'payload_status': 'metadata_only',
            'original_payload_metadata': {'content_sha256': payload.sha(body.encode()),
                'content_bytes': len(body.encode()), 'line_count': 1,
                'original_json_value_sha256': payload.digest(body)}}


class HistoricalRecipeTests(unittest.TestCase):
    def documents(self, old):
        return {'knowledge/evidence.json': {'citations': [old]},
                'knowledge/data/nativecore/native-core.json': {'entries': [{'claims': [
                    {'kind': 'NSF', 'evidence_refs': [
                        {'artifact_path': 'evidence.json', 'pointer': '/citations'}]}]}]}}

    def recipe(self, documents):
        with tempfile.TemporaryDirectory() as directory:
            for name, document in documents.items():
                payload.write_json(Path(directory) / name, document)
            return payload.generate_recipe(directory)

    def test_history_is_not_strict_and_hash_does_not_make_other_copy_required(self):
        documents = self.documents(historical())
        documents['knowledge/optional.json'] = {'source_excerpt': 'local historical = true\n'}
        self.assertEqual(payload.strict_excerpt_locations(documents), set())
        recipe, templates = self.recipe(documents)
        self.assertEqual(recipe['summary']['required_slots'], 0)
        self.assertEqual(len(recipe['slots']), 1)
        self.assertEqual(recipe['slots'][0]['coordinates'], [])
        self.assertFalse(recipe['slots'][0]['required_for_knowledge_shape'])
        self.assertNotIn('knowledge/evidence.json', templates)

    def test_current_plus_history_retains_current_required_slot(self):
        documents = self.documents(historical())
        body = 'local current = true\n'
        documents['knowledge/evidence.json']['citations'].append({
            'path': 'scripts/current.lua', 'file_sha256': 'b' * 64,
            'line_start': 2, 'line_end': 2, 'range_sha256': payload.sha(body.encode()),
            'snapshot_id': 'current', 'source_excerpt': body})
        recipe, _ = self.recipe(documents)
        self.assertEqual(recipe['summary']['required_slots'], 1)
        self.assertEqual(len(recipe['slots']), 1)
        self.assertEqual(recipe['slots'][0]['coordinates'][0]['source_file'], 'scripts/current.lua')

    def test_historical_payload_or_marker_is_rejected(self):
        for field, value in (('source_excerpt', 'local historical = true\n'),
                             ('excerpt', {payload.MARKER: 'slot'}),
                             ('nested', {'source_excerpt': 'hidden'})):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'historical comparison'):
                self.recipe(self.documents(historical() | {field: value}))

    def test_partial_or_damaged_historical_metadata_is_rejected(self):
        for field in ('evidence_role', 'supports_current_behavior', 'payload_status',
                      'file_sha256', 'snapshot_id', 'original_payload_metadata'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'historical comparison'):
                old = historical()
                old.pop(field)
                self.recipe(self.documents(old))


if __name__ == '__main__':
    unittest.main()

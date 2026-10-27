"""Current-input uncertainty stays attached to historical research evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
import prepare_sources
from dst_kb import native_mechanism
from dst_kb.config import KBError
from dst_kb.source_epoch_runtime import EpochContext, bind_epoch, source_preparation_document


class PreparationContextTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'provided.zip'
        source.write_bytes(b'explicit synthetic source identity')
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        prepare_sources.write(root / 'source-epochs.json', {
            'epochs': {'baseline': {}},
            'source_input_targets': [{'archive_sha256': source_hash, 'game_version': 'target'}]})
        ref = {'reference_id': 'R1', 'status': 'CHANGED_UNKNOWN',
               'source_checks': [{'source_input_index': 0, 'status': 'CHANGED_UNKNOWN'}]}
        checks = {'documents': [{'file': 'candidate.json', 'sha256': 'a'*64, 'references': [ref]}],
                  'reference_counts': {'CHANGED_UNKNOWN': 1}}
        summary = prepare_sources.write_source_assessment(root, [source], {
            'recovered_count': 1, 'missing_required_count': 0, 'missing_optional_count': 1}, checks)
        binding = prepare_sources.read(root / 'source-epochs.json')['epochs']['baseline']['source_preparation']
        context = EpochContext('baseline', root/'knowledge', root/'index', root/'config',
                               root/'source-epochs.json', root/'contracts', root/'identities', 'key', (),
                               json.dumps({'source_preparation': binding}))
        record = {'entry': {'id': 'EXAMPLE', 'title': 'Synthetic historical claim',
                            'scope': {'source_epoch': 'baseline'}, 'unknowns': [],
                            'claims': [{'kind': 'NSF', 'statement': 'Historical only', 'evidence_refs': ['R1']}]},
                  'document': {'source_epoch': 'baseline', 'archive_sha256': 'b'*64,
                               'limitations': ['No runtime proof'], 'source_references': [{'id': 'R1'}]},
                  'registration': {'file': 'candidate.json', 'sha256': 'a'*64, 'review': {}}, 'index': 0}
        return context, record, summary

    def test_target_identity_and_unknown_are_separate_from_original_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, record, summary = self.fixture(Path(tmp))
            original = copy.deepcopy(record)
            with bind_epoch(context):
                result = native_mechanism.envelope(record, '/claims/0')
            self.assertEqual(record, original)
            self.assertEqual(result['source_epoch'], 'baseline')
            self.assertEqual(summary['sources'][0]['identified_target']['game_version'], 'target')
            self.assertEqual(result['source_input_assessment']['references'][0]['status'], 'CHANGED_UNKNOWN')
            self.assertEqual(result['evidence_status'], 'LOCATOR_HASH_ONLY')
            self.assertFalse(result['coding_admission_granted'])

    def test_assessment_corruption_fails_before_source_status_can_be_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, _, _ = self.fixture(Path(tmp))
            (Path(tmp)/'SOURCE-PREPARATION.json').write_text('{}', encoding='utf-8')
            with bind_epoch(context), self.assertRaises(KBError):
                source_preparation_document()

    def test_search_summary_keeps_changed_reference_and_input_without_repeating_detail(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, record, _ = self.fixture(Path(tmp))
            with bind_epoch(context):
                result = native_mechanism.envelope(record, '/claims/0', assessment_detail=False)
            compact = result['source_input_assessment']
            self.assertEqual(compact['per_source_reference_states'], {0: {'CHANGED_UNKNOWN': ['R1']}})
            self.assertIn('get_entry', compact['detail_tools'])
            self.assertEqual(result['source_references'], [{'id': 'R1'}])

    def test_candidate_mismatch_does_not_borrow_another_candidates_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, record, _ = self.fixture(Path(tmp))
            record['registration']['sha256'] = 'c'*64
            with bind_epoch(context), self.assertRaises(KBError):
                native_mechanism.envelope(record, '/claims/0')

    def test_unprepared_public_read_never_claims_a_target_was_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _ = self.fixture(Path(tmp))
            with bind_epoch(None):
                self.assertNotIn('source_input_assessment', native_mechanism.envelope(record, '/claims/0'))


if __name__ == '__main__':
    unittest.main()

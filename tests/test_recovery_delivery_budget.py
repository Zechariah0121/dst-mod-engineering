"""Complete research atoms under payload budgets, using independent subjects."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import native_mechanism, projection_v2
from dst_kb.delivery_wire import expand_l1_metadata
from dst_kb.service import Service
from test_mechanism_evidence_budget import assessment_for
from test_research_task_navigation import record


def cost(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


class CompactAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.record = record('SYNTHETIC-API', 'Reference restoration',
                             ['First reference.', 'Second reference.'])
        self.record['entry']['api_contracts'][0]['evidence_refs'] = ['R0', 'R1']
        self.assessment = assessment_for(self.record, inputs=2)
        for row in self.assessment['native_mechanisms']['documents'][0]['references']:
            for check in row['source_checks']:
                check['diagnostic_note'] = 'Detailed observation ' * 500
        checks = self.assessment['native_mechanisms']['documents'][0]['references']
        checks[0]['source_checks'][1]['status'] = 'RANGE_ONLY'
        checks[1]['source_checks'][0]['status'] = 'CHANGED_UNKNOWN'
        self.environment = {
            'source_epoch': '759671',
            'source_input_assessment': {'sources': self.assessment['summary']['sources']},
        }
        self.service = Service.__new__(Service)
        self.service.ready = lambda: None
        self.service._mechanisms = lambda: {self.record['entry']['id']: self.record}
        self.service.epoch_context = SimpleNamespace(
            source_epoch='759671', metadata=lambda: copy.deepcopy(self.environment))
        preparation = patch('dst_kb.source_epoch_runtime.source_preparation_document',
                            return_value=self.assessment)
        preparation.start()
        self.addCleanup(preparation.stop)

    def lookup(self, **options):
        return self.service.lookup_api('Reader:Restore', family='native_mechanism', **options)

    def test_decision_preserves_atom_scope_refs_and_source_identity(self):
        result = self.lookup(max_bytes=24000)
        atom = result['results'][0]
        self.assertEqual(atom['value'], self.record['entry']['api_contracts'][0])
        for key in ('scope', 'unknowns'):
            self.assertEqual(atom[key], self.record['entry'][key])
        self.assertEqual(atom['limitations'], self.record['document']['limitations'])
        self.assertEqual(atom['source_references'], self.record['document']['source_references'])
        self.assertEqual(result['source_environment'], self.environment)
        summary = atom['source_input_assessment']
        self.assertEqual(summary['source_identities'],
                         'source_environment.source_input_assessment.sources')
        self.assertEqual(summary['per_source_reference_states'][0]['CHANGED_UNKNOWN'], ['R1'])
        self.assertEqual(summary['per_source_reference_states'][1]['RANGE_ONLY'], ['R0'])
        self.assertEqual(atom['coding_status'], 'hold')
        self.assertFalse(atom['runtime_validation_performed'])
        self.assertLessEqual(cost(result), 24000)

    def test_explicit_followup_returns_full_observations(self):
        compact = self.lookup()['results'][0]
        followup = compact['source_input_assessment']['detail_followup']
        self.assertEqual(followup['tool'], 'get_entry')
        arguments = dict(followup['arguments'])
        self.assertEqual(arguments.pop('source_epoch'), '759671')
        expanded = self.service.get_entry(**arguments)['entry']
        self.assertTrue(expanded['whole_value_delivered'])
        self.assertEqual(expanded['value'], compact['value'])
        self.assertEqual(expanded['source_references'], compact['source_references'])
        self.assertEqual(expanded['source_input_assessment']['references'],
                         self.assessment['native_mechanisms']['documents'][0]['references'])

    def test_detailed_views_retain_observations_and_tiny_budget_withholds(self):
        for view in ('reviewer', 'evidence'):
            result = self.lookup(view=view, max_bytes=64000)
            self.assertEqual(result['results'][0]['source_input_assessment']['references'],
                             self.assessment['native_mechanisms']['documents'][0]['references'])
        result = self.lookup(max_bytes=1000)
        self.assertEqual(result['results'], [])
        self.assertLessEqual(cost(result), 1000)

    def test_missing_outer_identity_keeps_the_detailed_representation(self):
        self.environment = {'source_epoch': '759671'}
        result = self.lookup(max_bytes=64000)
        assessment = result['results'][0]['source_input_assessment']
        self.assertIn('references', assessment)
        self.assertNotIn('source_identities', assessment)


def admitted_card(owner, first, second):
    """Already admitted typed atoms, before the delivery budget is allocated."""
    entry = {
        'id': 'SYNTHETIC-CLOSED-RECORD', 'title': owner + ' restoration',
        'scope': {'statement': 'Synthetic source fixture only', 'excluded': 'Runtime unknown'},
        'claims': [
            {'kind': 'NSF', 'statement': owner + ':' + first +
             '() paused current phase and remaining work', 'evidence_refs': []},
            {'kind': 'NSF', 'statement': owner + ':' + second +
             '() restores connected references after decoding', 'evidence_refs': []},
            {'kind': 'NSF', 'statement': owner + ':' + first +
             '() current phase explanation ' + 'unrelated ' * 8000, 'evidence_refs': []},
            {'kind': 'UNK', 'statement': 'Native transport remains unknown.', 'evidence_refs': []},
        ],
    }
    atoms = projection_v2._atoms(entry, 'core')
    card = {
        'projection_schema': projection_v2.SCHEMA, 'level': 1,
        'id': entry['id'], 'title': entry['title'], 'family': 'core',
        'record_sha256': projection_v2.record_digest(entry),
        'decision': atoms[:3], 'critical_boundary': [atoms[3]],
        'project_policy_questions': [], 'source_scope': {'original_scope': entry['scope']},
        'record_context_delivery': {'seed_record_pointers': ['/claims/0', '/claims/1', '/claims/2']},
        'context_closure': {'status': 'PARTIAL_CONTEXT', 'needed_context_missing': ['/unknown']},
        'governance': {'knowledge_status': 'canonical', 'retrieval_status': 'reviewer_default',
                       'coding_status': 'hold'},
    }
    query = (owner + ':' + first + ' paused current phase remaining work ' +
             owner + ':' + second + ' decoding connected references')
    service = Service.__new__(Service)
    service._ranker_v2 = lambda: SimpleNamespace(documents=[
        {'id': entry['id'], 'family': 'core', 'entry': entry}])
    return entry, card, query, service


class IncrementalClosedAtomTests(unittest.TestCase):
    def test_complementary_operation_fits_between_single_and_full_group(self):
        for subject in (('Graph', 'Advance', 'LoadEdges'), ('Inventory', 'Rotate', 'ReadItems')):
            with self.subTest(subject=subject):
                entry, card, query, service = admitted_card(*subject)
                before = copy.deepcopy((entry, card))
                pair = projection_v2.atomic_subset(card, entry, ['/claims/0', '/claims/1'], query=query)
                maximum = cost(pair) + 3000
                attempts = []

                def fits(candidate):
                    attempts.append(cost(candidate))
                    return cost(candidate) <= maximum

                result = service._research_seed_view(card, query, fits=fits)
                decoded = expand_l1_metadata(result)
                self.assertEqual({atom['record_pointer'] for atom in decoded['decision']},
                                 {'/claims/0', '/claims/1'})
                self.assertEqual(decoded['critical_boundary'][0]['statement'],
                                 entry['claims'][3]['statement'])
                self.assertEqual(decoded['context_closure']['status'], 'PARTIAL_CONTEXT')
                self.assertFalse(decoded['atomic_delivery']['unknown_dependencies_are_optional'])
                self.assertEqual(projection_v2.delivered_original_atoms(entry, 'core', decoded)[1], [])
                self.assertLessEqual(cost(result), maximum)
                self.assertLessEqual(len(attempts), 4)
                self.assertEqual((entry, card), before)

    def test_small_budget_returns_one_complete_seed_for_the_allocator(self):
        entry, card, query, service = admitted_card('Queue', 'Dispatch', 'LoadBindings')
        single = service._research_seed_view(card, query, grouped=False)
        result = service._research_seed_view(card, query, fits=lambda value: cost(value) <= cost(single))
        self.assertEqual(expand_l1_metadata(result)['atomic_delivery']['delivered_seed_record_pointers'],
                         ['/claims/0'])
        self.assertEqual(projection_v2.delivered_original_atoms(entry, 'core', result)[1], [])

    def test_absent_admission_cannot_be_added_from_canonical_text(self):
        entry, card, query, service = admitted_card('Link', 'Advance', 'ReadNodes')
        card['decision'] = [card['decision'][0], card['decision'][2]]
        card['record_context_delivery']['seed_record_pointers'] = ['/claims/0', '/claims/2']
        result = service._research_seed_view(card, query, fits=lambda value: cost(value) < 16000)
        self.assertNotIn('/claims/1', [atom['record_pointer']
                                     for atom in expand_l1_metadata(result)['decision']])

    def test_original_plan_still_rejects_changed_card_or_record(self):
        entry, card, query, _ = admitted_card('World', 'Advance', 'ReadLinks')
        plan = projection_v2.atomic_delivery_plan(card, entry, query=query)
        changed = copy.deepcopy(card)
        changed['source_scope'] = {'invented': True}
        with self.assertRaises(ValueError):
            projection_v2._atomic_subset_from_plan(changed, entry, ['/claims/0'], plan, query=query)
        changed_record = copy.deepcopy(entry)
        changed_record['claims'][0]['statement'] += ' changed'
        with self.assertRaises(ValueError):
            projection_v2._atomic_subset_from_plan(card, changed_record, ['/claims/0'], plan, query=query)


if __name__ == '__main__':
    unittest.main(verbosity=2)

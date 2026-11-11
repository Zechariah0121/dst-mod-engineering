"""Whole native units and executable followups under fixed research budgets."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import native_mechanism
import test_research_task_navigation as navigation_fixtures
import test_recovery_delivery_budget as assessment_fixtures

record = navigation_fixtures.record


def cost(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


class NativeBundleTests(unittest.TestCase):
    def service(self, records):
        return navigation_fixtures.TaskNavigationTests.service(self, records)

    def test_equal_relevance_preserves_numeric_original_unit_order(self):
        item = record('FIRST', 'Reference restoration', ['Restore saved fields.'] * 12)
        choices = native_mechanism.ranked_units(item['entry'], 'Restore saved fields')
        self.assertEqual([row['pointer'] for row in choices if row['pointer'].startswith('/claims/')],
                         ['/claims/' + str(index) for index in range(12)])

    def test_compact_delivers_whole_units_with_original_context(self):
        for owner, topic in (('Graph', '引用恢复'), ('Inventory', '保存加载')):
            with self.subTest(owner=owner):
                first = record('FIRST', topic, [owner + ':Decode restores saved fields.',
                               'UNREQUESTED ' * 12000], symbol=owner + ':Read')
                second = record('SECOND', '速度modifier来源撤销',
                                ['Equipment modifier contributions use source/key identity.',
                                 'UNREQUESTED ' * 12000])
                before = copy.deepcopy((first, second))
                service = self.service([first, second])
                result = service.get_context_bundle(
                    topic + ' saved fields modifier source/key contributions', mode='research',
                    projection='reviewer', budget='compact')
                self.assertLessEqual(cost(result), 16000)
                self.assertEqual({card['id'] for card in result['entries']}, {'FIRST', 'SECOND'})
                self.assertEqual(len(result['entries']), 2)
                for card in result['entries']:
                    original = {'FIRST': first, 'SECOND': second}[card['id']]
                    self.assertTrue(card['pointer'])
                    field, index = card['pointer'].strip('/').split('/')
                    self.assertEqual(card['value'], original['entry'][field][int(index)])
                    for key in ('scope', 'unknowns'):
                        self.assertEqual(card[key], original['entry'][key])
                    self.assertEqual(card['limitations'], original['document']['limitations'])
                    self.assertEqual(card['coding_status'], 'hold')
                    self.assertFalse(card['runtime_validation_performed'])
                self.assertTrue(result['truncated'])
                self.assertEqual((first, second), before)

    def test_followup_is_an_executable_targeted_read(self):
        item = record('FIRST', '引用恢复', ['Restore saved reference fields.',
                      'Restore remaining state in a separate phase.', 'UNREQUESTED ' * 12000],
                      symbol='Graph:Decode', prose='Restore saved reference fields.')
        service = self.service([item])
        result = service.get_context_bundle('引用恢复 Restore saved reference fields',
                    mode='research', projection='reviewer', budget='compact')
        records = result['deferred_knowledge_navigation']['records']
        self.assertTrue(records)
        followup = records[0]['read_original']
        self.assertEqual(followup['tool'], 'get_entry')
        arguments = dict(followup['arguments'])
        self.assertIsNone(arguments.pop('source_epoch', None))
        self.assertEqual(arguments['max_bytes'], 16000)
        self.assertEqual(arguments['view'], 'decision')
        expanded = service.get_entry(**arguments)['entry']
        self.assertTrue(expanded['whole_value_delivered'])
        self.assertNotEqual(expanded['pointer'], result['entries'][0]['pointer'])
        field, index = expanded['pointer'].strip('/').split('/')
        self.assertEqual(expanded['value'], item['entry'][field][int(index)])

    def test_oversize_exact_api_cannot_be_replaced_with_a_claim(self):
        item = record('FIRST', 'Graph恢复', ['Graph:Decode restores saved fields.'],
                      symbol='Graph:Decode', prose='Complete branch ' * 2000)
        result = self.service([item]).get_context_bundle('Graph:Decode', mode='research',
                    projection='reviewer', budget='compact')
        self.assertEqual(result['entries'], [])
        followup = result['deferred_knowledge_navigation']['records'][0]['read_original']
        self.assertEqual(followup['arguments']['pointer'], '/api_contracts/0')
        self.assertLessEqual(cost(result), 16000)

    def test_oversize_exact_record_id_keeps_an_executable_full_read(self):
        for identifier in ('SYNTHETIC-GRAPH', 'SYNTHETIC-BAG'):
            with self.subTest(identifier=identifier):
                item = record(identifier, 'Reference restoration', ['UNREQUESTED ' * 12000])
                service = self.service([item])
                search = service.search_kb(identifier, mode='research', projection='reviewer')
                self.assertEqual(search['results'], [])
                followup = search['withheld_atoms'][0]['followup']
                self.assertEqual(followup['id'], identifier)
                self.assertEqual(followup['arguments']['id'], identifier)
                self.assertEqual(followup['arguments']['pointer'], '')
                self.assertEqual(followup['arguments']['max_bytes'], 64000)
                self.assertLessEqual(cost(search), 64000)
                bundle = service.get_context_bundle(identifier, mode='research',
                            projection='reviewer', budget='compact')
                self.assertEqual(bundle['entries'], [])
                navigation = bundle['deferred_knowledge_navigation']['records'][0]['read_original']
                self.assertEqual(navigation['arguments']['pointer'], '')
                self.assertEqual(navigation['arguments']['max_bytes'], 16000)
                expanded = service.get_entry(**navigation['arguments'])['entry']
                self.assertFalse(expanded['whole_value_delivered'])
                self.assertIn('/claims', expanded['child_pointers'])
                self.assertLessEqual(cost(bundle), 16000)

    def test_role_and_negative_gates_precede_atomic_delivery(self):
        item = record('FIRST', '引用恢复', ['Restore saved reference fields.'])
        service = self.service([item])
        for options in ({'mode': 'research', 'projection': 'coding'},
                        {'mode': 'architect', 'projection': 'reviewer'}):
            result = service.get_context_bundle('引用恢复', budget='compact', **options)
            self.assertEqual(result['entries'], [])
        result = service.get_context_bundle('引用恢复，不涉及Restore', mode='research',
                    projection='reviewer', budget='compact')
        self.assertEqual(result['entries'], [])

    def test_unknown_and_scope_prose_cannot_supply_topic_coverage(self):
        item = record('FIRST', 'Reference restoration', ['Decode saved fields.'])
        item['entry']['unknowns'] = ['speed modifier buff equipment']
        item['entry']['scope']['excluded'] = 'speed modifier buff equipment'
        service = self.service([item])
        card = native_mechanism.envelope(item, '/claims/0')
        self.assertEqual(service._research_coverage(card, 'speed modifier buff equipment'), set())

    def test_incidental_callee_cannot_claim_a_primary_topic(self):
        item = record('FIRST', 'Bag restoration',
                      ['Bag:Load restores fields then calls Speed:SetModifier for a modifier.'],
                      symbol='Bag:Load')
        service = self.service([item])
        card = native_mechanism.envelope(item, '/claims/0')
        coverage = service._research_coverage(card, 'restore modifier Speed:SetModifier')
        self.assertNotIn('topic:modifier', coverage)
        self.assertIn('symbol:speed:setmodifier', coverage)

    def test_first_record_and_uncovered_followup_precede_repeated_context(self):
        items = [record(name, 'Reference restoration',
                        ['Restore saved reference fields.', 'UNREQUESTED ' * 12000])
                 for name in ('A', 'B', 'C')]
        items.append(record('D', 'Modifier contribution',
                            ['Modifier contributions retain source/key identity.',
                             'UNREQUESTED ' * 12000]))
        for item in items:
            item['entry']['scope']['required_fixture_condition'] = 'condition ' * 650
        service = self.service(items)
        navigate = service._research_navigation_rows
        service._research_navigation_rows = lambda *args: sorted(
            navigate(*args), key=lambda row: row['document']['id'])
        result = service.get_context_bundle('Restore saved fields modifier source/key',
                    mode='research', projection='reviewer', budget='compact')
        self.assertEqual([card['id'] for card in result['entries']], ['A'])
        followups = result['deferred_knowledge_navigation']['records']
        self.assertEqual(followups[0]['id'], 'D')
        self.assertEqual(followups[0]['original_search_rank'], 4)
        self.assertEqual(followups[0]['read_original']['arguments']['pointer'], '/claims/0')
        self.assertLessEqual(cost(result), 16000)

    def test_closed_complementary_facts_precede_incidental_topic_fill(self):
        entry, card, query, _ = assessment_fixtures.admitted_card('Graph', 'Advance', 'LoadEdges')
        entry['scope']['condition'] = 'Required source condition. ' * 500
        card['record_sha256'] = assessment_fixtures.projection_v2.record_digest(entry)
        first = record('FIRST', 'Graph restoration', ['Graph:Advance prepares decoding.'],
                       symbol='Anchor:Read')
        large = record('LARGE', 'Modifier contribution', ['Modifier contributions.'],
                       symbol='Modifier:Apply', prose='Complete original branch. ' * 1900)
        service = self.service([first, large])
        document = {'id': entry['id'], 'family': 'core', 'entry': entry}
        old_row = {'document': document, 'score': 1, 'match_reason': {}}
        diagnosis = {'candidate_matches': 3, 'query_intent': {}, 'excluded': [],
                     'knowledge_gap_meaning': 'Synthetic admitted fixtures.'}
        service._ranker_v2 = lambda: SimpleNamespace(
            documents=[document], search=lambda *a, **k: ([old_row], diagnosis))
        service._view_v2 = lambda *a, **k: copy.deepcopy(card)
        service._research_navigation_rows = lambda rows, mechanisms, query: [
            {'document': {'id': value['entry']['id']}, 'mechanism_record': value,
             'score': 3 - index, 'match_reason': {}}
            for index, value in enumerate((first, large))] + rows
        with patch('dst_kb.service.projection_v2.task_view_admission',
                   return_value={'status': 'TASK_ATOM_DELIVERED'}):
            result = service.search_kb(query + ' Modifier:Apply()', mode='research',
                                       projection='reviewer', top_k=3)
        selected = next(row for row in result['results'] if row['id'] == entry['id'])
        self.assertTrue({'/claims/0', '/claims/1'} <= set(
            selected['atomic_delivery']['delivered_seed_record_pointers']))
        self.assertLessEqual(cost(result), 64000)


class DecisionReadTests(unittest.TestCase):
    setUp = assessment_fixtures.CompactAssessmentTests.setUp
    def test_explicit_decision_read_reuses_compact_source_assessment(self):
        result = self.service.get_entry(self.record['entry']['id'], projection='reviewer',
                    view='decision', pointer='/api_contracts/0', max_bytes=16000)
        atom = result['entry']
        self.assertTrue(atom['whole_value_delivered'])
        self.assertEqual(atom['value'], self.record['entry']['api_contracts'][0])
        self.assertIn('per_source_reference_states', atom['source_input_assessment'])
        self.assertEqual(result['source_environment'], self.environment)
        self.assertLessEqual(cost(result), 16000)
        detailed = self.service.get_entry(self.record['entry']['id'], projection='reviewer',
                    pointer='/api_contracts/0', max_bytes=64000)['entry']
        self.assertIn('references', detailed['source_input_assessment'])

    def test_decision_read_without_outer_identity_retains_source_observations(self):
        self.environment = {'source_epoch': '759671'}
        atom = self.service.get_entry(self.record['entry']['id'], projection='reviewer',
                    view='decision', pointer='/api_contracts/0', max_bytes=64000)['entry']
        self.assertIn('references', atom['source_input_assessment'])
        self.assertNotIn('source_identities', atom['source_input_assessment'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

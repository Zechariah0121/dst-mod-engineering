"""Portable delivery-count and published-schema regressions; no vanilla data."""
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SERVICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE))

from dst_kb.config import KBError
from dst_kb.mcp_server import Server, TOOLS, tool
from dst_kb.service import Service


def candidates(n001=9, legacy=0, oversized=False):
    records = ([{'id': 'oversized', 'family': 'n001', 'body': 'x' * 100000}]
               if oversized else [])
    records += [{'id': 'native-' + str(i), 'family': 'n001'} for i in range(n001)]
    records += [{'id': 'legacy-' + str(i), 'family': 'legacy'} for i in range(legacy)]
    return [{'document': {'entry': record, 'family': record['family']},
             'score': 1, 'match_reason': {}} for record in records]


class DeliveryContractTests(unittest.TestCase):
    def setUp(self):
        self.service = Service.__new__(Service)
        self.service.epoch_context = None
        self.service.ready = lambda: None
        self.service._governance = lambda ids: {}
        self.service._view_v2 = lambda record, family, *args, **kwargs: dict(record)
        self.service._append_companion_contexts = lambda *args: None
        self.service.db = sqlite3.connect(':memory:')
        self.service.db.execute('CREATE TABLE meta(key TEXT, value TEXT)')
        self.service.db.execute("INSERT INTO meta VALUES('kb_version','synthetic')")
        self.admission = patch('dst_kb.service.projection_v2.task_view_admission',
                               return_value={'status': 'TASK_ATOM_DELIVERED'})
        self.admission.start()

    def tearDown(self):
        self.admission.stop()
        self.service.db.close()

    def configure(self, rows):
        diagnosis = {'candidate_matches': len(rows), 'query_intent': {},
                     'excluded': [], 'knowledge_gap_meaning': 'synthetic fixture'}
        self.service._ranker_v2 = lambda: SimpleNamespace(
            documents=[row['document'] for row in rows], search=lambda *a, **kw: (rows, diagnosis))

    def test_public_search_caps_delivered_native_subset_in_all_views_and_modes(self):
        self.configure(candidates())
        for query in ('', 'synthetic task'):
            for mode in (None, 'coding', 'research', 'review'):
                for view in ('decision', 'reviewer', 'evidence'):
                    with self.subTest(query=query, mode=mode, view=view), \
                         patch('dst_kb.service.projection_v2.bundle_decision_card', side_effect=lambda x: x), \
                         patch('dst_kb.service.project_l1_card', side_effect=lambda x, **kw: x):
                        value = self.service.search_kb(query, mode=mode, view=view, top_k=30)
                        self.assertEqual(len(value['results']), 5)
                        self.assertEqual(value['exclusions_summary']['CODING_SUBSET_LIMIT'], 4)
                        self.assertTrue(value['results_truncated'])

    def test_native_cap_does_not_reduce_legacy_or_reviewer_budgets(self):
        self.configure(candidates(9, 4))
        value = self.service.search_kb(view='reviewer', top_k=8)
        self.assertEqual(len(value['results']), 8)
        self.assertEqual(sum(item['family'] == 'n001' for item in value['results']), 5)
        reviewer = self.service.search_kb(view='reviewer', projection='reviewer', top_k=30)
        self.assertEqual(len(reviewer['results']), 13)
        self.assertNotIn('CODING_SUBSET_LIMIT', reviewer['exclusions_summary'])
        self.assertEqual(len(self.service.search_kb(view='reviewer', top_k=3)['results']), 3)

    def test_bundle_enforces_cap_at_actual_accept_and_refills_byte_rejections(self):
        self.configure(candidates(9, 4, oversized=True))
        for budget, maximum in (('compact', 16000), ('normal', 32000), ('deep', 64000)):
            with self.subTest(budget=budget):
                value = self.service.get_context_bundle('', budget=budget, view='reviewer')
                natives = [item for item in value['entries'] if item['family'] == 'n001']
                self.assertEqual(len(natives), 5)
                self.assertNotIn('oversized', [item['id'] for item in value['entries']])
                self.assertEqual(natives[-1]['id'], 'native-4')
                self.assertLessEqual(len(json.dumps(value, ensure_ascii=False).encode('utf-8')), maximum)
                self.assertEqual(value['max_payload_bytes'], maximum)
                self.assertTrue(any(gap['status'] == 'admitted_cards_exceed_card_budget'
                                    for gap in value['knowledge_gaps']))
        reviewer = self.service.get_context_bundle('', budget='deep', projection='reviewer', view='reviewer')
        self.assertEqual(len(reviewer['entries']), 12)
        self.assertEqual(sum(item['family'] == 'n001' for item in reviewer['entries']), 9)


class PublishedSchemaTests(unittest.TestCase):
    def test_published_tools_exactly_match_live_full_service(self):
        published = json.loads((SERVICE / 'docs/mcp-tools.json').read_text(encoding='utf-8'))
        self.assertEqual(published, {'contract_version': '1', 'tools': TOOLS})
        server = Server()
        server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'})
        reply = server.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
        self.assertEqual(reply['result']['tools'], published['tools'])
        self.assertEqual(len(published['tools']), 9)

    def test_transport_reads_subclass_contract_without_opening_full_service(self):
        class NavigationServer(Server):
            tools = [tool('navigation', 'Synthetic navigation fixture', {})]
            instructions = 'Synthetic navigation only'
        server = NavigationServer()
        initialized = server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'})
        self.assertEqual(initialized['result']['instructions'], server.instructions)
        listed = server.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
        self.assertEqual(listed['result']['tools'], server.tools)
        with self.assertRaises(KBError) as error:
            server.call('search_kb', {})
        self.assertEqual(error.exception.code, 'INVALID_TOOL')
        self.assertEqual(server.services, {})


if __name__ == '__main__':
    unittest.main(verbosity=2)

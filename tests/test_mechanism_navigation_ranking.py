"""Synthetic navigation regressions; no frozen evaluation queries or record IDs."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import native_mechanism
from dst_kb.public_catalog import CatalogRanker, declared_identities, tokens


def record(identifier, symbol, *, aliases=(), prose='', symbols=None, dependency=False):
    entry = {'id': identifier, 'title': 'Independent subsystem', 'aliases': list(aliases),
             'engineering_question': 'How is this subsystem coordinated?',
             'api_contracts': [{'symbol': symbol, 'source_file': 'scripts/synthetic.lua',
                                'evidence_refs': ['OWN', 'DEP'] if dependency else ['OWN'], 'side_effects': prose}]}
    return {'entry': entry, 'document': {'source_references': [
        {'id': 'OWN', 'source_file': 'scripts/synthetic.lua', 'symbols': [symbol] + ([] if dependency else symbols or [])},
        {'id': 'DEP', 'source_file': 'scripts/synthetic.lua', 'symbols': symbols or []}]}}


def ordered(records, query):
    return [r['entry']['id'] for r in sorted(records, key=lambda r: (-native_mechanism.score(r, query), r['entry']['id']))
            if native_mechanism.score(r, query) > 0]


class IdentifierSegmentationTests(unittest.TestCase):
    def test_camel_acronym_snake_qualified_and_whole_forms(self):
        parts = tokens('XMLQueueManager:Flush_pending-items')
        self.assertTrue({'xmlqueuemanager:flush_pending-items', 'xml', 'queue', 'manager', 'flush', 'pending', 'items'} <= parts)
        self.assertNotIn('row', tokens('BrowseRegistry'))  # no arbitrary substring stems

    def test_catalog_declared_api_preserves_camel_parts_before_lowercasing(self):
        owner = {'id': 'Z', 'title': 'Task coordination', 'api_contracts': [{'symbol': 'XMLQueueManager:Flush_pending'}]}
        noise = {'id': 'A', 'title': 'Miscellaneous', 'body': 'queue ' * 200}
        rows = [{'id': e['id']} for e in [noise, owner]]
        ranker = CatalogRanker(rows, {e['id']: e for e in [noise, owner]})
        for query in ['Queue', 'pending', 'QueuePending', 'XMLQueueManager:Flush_pending']:
            self.assertEqual(ranker.rank(query)[0]['id'], 'Z', query)
        self.assertIn('xmlqueuemanager:flush_pending', declared_identities(owner))


class MechanismNavigationRankingTests(unittest.TestCase):
    def test_declared_leaf_owners_precede_alias_and_repeated_mentions(self):
        first = record('Z', 'Sender:Flush(ticket)')
        second = record('Y', 'Receiver:Flush(ticket)')
        mention = record('A', 'Observer:Read', aliases=['Flush'], prose='Flush ' * 500)
        self.assertEqual(set(ordered([mention, first, second], 'Flush')[:2]), {'Y', 'Z'})

    def test_qualified_method_never_borrows_another_owner(self):
        owner = record('Z', 'Sender:Flush(ticket)')
        other = record('A', 'Receiver:Flush', aliases=['Flush'], prose='Sender:Flush ' * 500)
        for query in ['Sender:Flush', 'Sender:Flush(ticket)']:
            self.assertEqual(ordered([other, owner], query)[0], 'Z')

    def test_colocated_local_navigation_precedes_dependency_without_promoting_api(self):
        definition = record('Z', 'Dictionary:Lookup', symbols=['LocalKeyTransform'])
        caller = record('A', 'Compiler:Compile', aliases=['LocalKeyTransform'],
                        symbols=['LocalKeyTransform'], dependency=True, prose='LocalKeyTransform ' * 500)
        before = copy.deepcopy([definition, caller])
        self.assertEqual(ordered([caller, definition], 'LocalKeyTransform')[0], 'Z')
        self.assertEqual([definition, caller], before)
        self.assertNotIn('localkeytransform', declared_identities(definition['entry']))
        self.assertEqual(definition['entry']['api_contracts'][0]['symbol'], 'Dictionary:Lookup')

    def test_unused_document_symbol_is_not_this_entrys_definition(self):
        unrelated = record('A', 'Registry:Read', symbols=['UnusedHelper'], dependency=True)
        unrelated['entry']['api_contracts'][0]['evidence_refs'] = ['OWN']
        self.assertEqual(native_mechanism.score(unrelated, 'UnusedHelper'), 0)

    def test_identifier_parts_and_exact_id_work_without_unbounded_substrings(self):
        owner = record('SYNTHETIC-ITEM', 'XMLQueueManager:Flush_pending')
        self.assertGreater(native_mechanism.score(owner, 'pending'), 0)
        self.assertEqual(native_mechanism.score(owner, 'synthetic-item'), 10000)
        self.assertEqual(native_mechanism.score(owner, '    '), 0)
        self.assertEqual(native_mechanism.score(owner, 'TotallyUnrelatedNeedle'), 0)

    def test_equal_scores_use_stable_id_not_registration_order(self):
        a = record('A', 'Sender:Flush')
        z = record('Z', 'Sender:Flush')
        self.assertEqual(ordered([a, z], 'Flush'), ordered([z, a], 'Flush'))

    def test_fragment_overlap_does_not_invent_a_whole_identifier_or_owner(self):
        owner = record('A', 'Table:GetCell')
        self.assertEqual(native_mechanism.score(owner, 'GetUnknownCell'), 0)
        self.assertEqual(native_mechanism.score(owner, 'UnknownOwner:GetCell'), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

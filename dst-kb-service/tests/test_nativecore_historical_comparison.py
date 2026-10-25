"""Explicit history preserves provenance without supplying current NSF proof."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dst_kb import nativecore
from dst_kb.config import KBError


def current():
    body = 'local current = true\n'
    return {'path': 'scripts/a.lua', 'file_sha256': 'a' * 64,
            'line_start': 2, 'line_end': 2, 'range_sha256': sha256(body.encode()).hexdigest(),
            'snapshot_id': 'current-snapshot', 'source_excerpt': body}


def historical():
    node = current()
    body = node.pop('source_excerpt')
    node.update(evidence_role='historical_comparison', supports_current_behavior=False,
                payload_status='metadata_only', snapshot_id='historical-snapshot',
                original_payload_metadata={
                    'content_sha256': node['range_sha256'], 'content_bytes': len(body.encode()),
                    'original_json_value_sha256': sha256(json.dumps(body).encode()).hexdigest(),
                    'line_count': 1})
    return node


class HistoricalComparisonTests(unittest.TestCase):
    def test_current_plus_explicit_history_passes_and_history_is_not_a_locator(self):
        old = historical()
        self.assertEqual(list(nativecore._locator_nodes(old)), [])
        self.assertTrue(nativecore._has_nsf_locator([{'citations': [current(), old]}], {}))

    def test_history_only_never_supplies_current_evidence(self):
        self.assertFalse(nativecore._has_nsf_locator([historical()], {'snapshot_id': 'current'}))

    def test_historical_snapshot_cannot_complete_current_symbol_locator(self):
        node = current()
        node.pop('snapshot_id')
        node.pop('source_excerpt')
        node['symbol'] = 'Current'
        self.assertFalse(nativecore._has_nsf_locator([node, historical()], {}))

    def test_unmarked_missing_payload_and_partial_markers_fail(self):
        for field in ('evidence_role', 'supports_current_behavior', 'payload_status'):
            with self.subTest(field=field):
                old = historical()
                old.pop(field)
                self.assertFalse(nativecore._has_nsf_locator([current(), old], {}))
        old = historical()
        for key in ('evidence_role', 'supports_current_behavior', 'payload_status'):
            old.pop(key)
        self.assertFalse(nativecore._has_nsf_locator([current(), old], {}))

    def test_bad_history_metadata_and_hidden_payload_fail(self):
        cases = [({'file_sha256': 'bad'}), ({'path': 'scripts/../a.lua'}),
                 ({'line_start': True}), ({'snapshot_id': ''}),
                 ({'source_excerpt': ''}),
                 ({'excerpt': {'$dst_source_payload_slot': 'slot'}}),
                 ({'hidden': {'source_excerpt': 'old source'}}),
                 ({'hidden': current()})]
        for change in cases:
            with self.subTest(change=change):
                self.assertFalse(nativecore._has_nsf_locator([current(), historical() | change], {}))
        for field, value in (('content_sha256', 'b' * 64), ('content_bytes', False),
                             ('original_json_value_sha256', 'bad'), ('line_count', 2)):
            with self.subTest(field=field):
                old = historical()
                old['original_payload_metadata'][field] = value
                self.assertFalse(nativecore._has_nsf_locator([current(), old], {}))

    def test_corrupt_current_citation_is_not_hidden_by_valid_history(self):
        for change in ({'source_excerpt': 'wrong\n'}, {'range_sha256': 'f' * 64},
                       {'line_end': 3}, {'file_sha256': 'bad'}):
            with self.subTest(change=change):
                self.assertFalse(nativecore._has_nsf_locator([current() | change, historical()], {}))

    def load_fixture(self, root, claim_node):
        evidence = {'claim': claim_node, 'entry': current()}
        raw = json.dumps(evidence).encode()
        (root / 'evidence.json').write_bytes(raw)
        fingerprint = sha256(raw).hexdigest()
        ref = lambda pointer: {'artifact_path': 'evidence.json', 'sha256': fingerprint, 'pointer': pointer}
        entry = {'id': 'HISTORY-TEST', 'knowledge_status': 'supported',
                 'retrieval_status': 'reviewer_default', 'coding_status': 'hold',
                 'scope': {'snapshot_id': 'current'}, 'evidence_refs': [ref('/entry')],
                 'correction_refs': [], 'claims': [{'kind': 'NSF', 'evidence_refs': [ref('/claim')]}]}
        core = {'version': 'fixture', 'entries': [entry], 'state_registry': [],
                'source_artifacts': [{'artifact_path': 'evidence.json', 'sha256': fingerprint}],
                'historical_product_evidence': []}
        (root / nativecore.FILE).parent.mkdir(parents=True, exist_ok=True)
        (root / nativecore.FILE).write_text(json.dumps(core), encoding='utf-8')
        (root / 'schemas').mkdir(exist_ok=True)
        (root / 'schemas/native-core.schema.json').write_text('{}', encoding='utf-8')
        return nativecore.load(root, lambda *args: [], lambda *args: None)

    def test_loader_blocks_history_only_claim_entry_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(KBError, 'NSF citation lacks'):
                self.load_fixture(root, historical())
            loaded, report = self.load_fixture(root, {'citations': [current(), historical()]})
            self.assertEqual(report['status'], 'PASS')
            self.assertFalse(report['runtime_validation_performed'])
            self.assertEqual(loaded['entries'][0]['coding_status'], 'hold')

    def test_loader_cannot_borrow_entry_evidence_for_corrupt_claim_citations(self):
        malformed = historical()
        malformed.pop('path')
        cases = [malformed, {'citations': [current() | {'source_excerpt': 'wrong\n'}, historical()]}]
        with tempfile.TemporaryDirectory() as directory:
            for claim in cases:
                with self.subTest(claim=claim), self.assertRaisesRegex(KBError, 'NSF citation lacks'):
                    self.load_fixture(Path(directory), claim)


if __name__ == '__main__':
    unittest.main()

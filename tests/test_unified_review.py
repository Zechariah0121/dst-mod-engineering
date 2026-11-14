"""Explicit review adapter against registered public records, no game proof."""
import contextlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import review_reader
from dst_kb.config import KBError
from dst_kb.public_catalog import PublicCatalog
from dst_kb.service import Service
from dst_kb.mcp_server import TOOLS, check_arguments
sys.path.insert(0, str(ROOT))
import run_kb


class UnifiedReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = PublicCatalog(ROOT)

    def setUp(self):
        self.service = Service.__new__(Service)
        self.service.epoch_context = None
        self.service.root = ROOT / 'knowledge'
        self.service.db = sqlite3.connect(':memory:')
        self.addCleanup(self.service.db.close)
        self.service.db.execute('CREATE TABLE entries(id TEXT,type TEXT,json TEXT)')
        self.service.db.execute('CREATE TABLE native_research(id TEXT,json TEXT)')
        self.service.db.execute('CREATE TABLE meta(key TEXT,value TEXT)')
        self.service.db.execute('CREATE TABLE nodes(id TEXT,json TEXT)')
        self.service.db.execute("INSERT INTO meta VALUES('kb_version','fixture')")
        self.service.ready = lambda: None
        self.service._mechanisms = lambda: self.catalog.mechanisms
        families={r['id']:r['family'] for r in self.catalog.rows}
        for record in self.catalog.records.values():
            self.service.db.execute('INSERT INTO entries VALUES(?,?,?)',
                (record['id'], record.get('entry_type', 'native_ai_knowledge' if families[record['id']]=='native_ai' else ''), json.dumps(record)))
        research = json.loads((self.service.root / 'data/native001/canonical-native001-research-map.json').read_text(encoding='utf-8'))
        self.service.db.executemany('INSERT INTO native_research VALUES(?,?)',
            [(r['canonical_id'], json.dumps(r)) for r in research['entries']])
        for name, key in [('sources.json', 'sources'), ('claims.json', 'claims')]:
            data = json.loads((self.service.root / 'data' / name).read_text(encoding='utf-8'))
            self.service.db.executemany('INSERT INTO nodes VALUES(?,?)',
                [(r['id'], json.dumps(r)) for r in data[key]])

    def review(self, identifier, **kwargs):
        return self.service.get_entry(identifier, projection='reviewer', purpose='review', **kwargs)

    def test_every_registered_record_can_be_reviewed_with_complete_context(self):
        for row in self.catalog.rows:
            identifier = row['id']
            with self.subTest(id=identifier):
                result = self.review(identifier, max_bytes=64000)
                self.assertLessEqual(review_reader.size(result), 64000)
                self.assertTrue(result['objects'], result)
                self.assertFalse(result['coding_admission_granted'])
                self.assertFalse(result['runtime_validation_performed'])
                self.assertEqual(result['entry_registration'], row)
                if row['family'] == 'native_mechanism':
                    self.assertEqual(result['scope'], self.catalog.records[identifier]['scope'])
                    self.assertEqual(result['coding_status'], 'hold')
                else:
                    self.assertEqual(result['record_context']['scope'], self.catalog.records[identifier]['scope'])

    def test_owner_subfields_return_whole_original_object(self):
        for identifier, pointer, expected in [
            ('NC-N002-FINAL-01', '/claims/0/statement', '/claims/0'),
            ('AI-N001-01', '/native_fact/statement', '/native_fact'),
            ('EXP-FISH-001', '/api_contracts/2/symbol', '/api_contracts/2')]:
            with self.subTest(id=identifier):
                result = self.review(identifier, pointer=pointer, max_bytes=64000)
                self.assertEqual(result['pointer'], expected)
                self.assertEqual(result['objects'][0]['value'], review_reader.at(self.catalog.records[identifier], expected))

    def test_low_budget_continuation_finishes_without_loss(self):
        record = {'id': 'T', 'scope': {'required': 'yes'}, 'claims': [
            {'kind': 'NSF', 'statement': str(i) + '文' * 900, 'evidence_refs': ['R']} for i in range(10)]}
        context = {'scope': record['scope'], 'coding_status': 'hold', 'unknowns': ['fixture']}
        result = review_reader.read(record, 'core', context, maximum=4800)
        objects = list(result['objects'])
        seen = set()
        while result['continuation']:
            args = result['continuation']['arguments']
            self.assertNotIn(args['cursor'], seen)
            seen.add(args['cursor'])
            result = review_reader.read(record, 'core', context, args['pointer'], args['cursor'], args['max_bytes'])
            self.assertLessEqual(review_reader.size(result), 4800)
            self.assertEqual(result['scope'], context['scope'])
            objects.extend(result['objects'])
        self.assertTrue(result['complete'])
        self.assertEqual([o['value'] for o in objects if o['pointer'].startswith('/claims/')], record['claims'])

    def test_context_and_whole_owner_are_never_split_for_budget(self):
        record = {'id': 'T', 'claims': [{'kind': 'NSF', 'statement': 'x' * 70000}]}
        result = review_reader.read(record, 'core', {'scope': 'required'}, '/claims/0/statement', maximum=1000)
        self.assertEqual(result['objects'], [])
        self.assertFalse(result['complete'])
        result = review_reader.read(record, 'core', {'scope': 'x' * 70000}, maximum=1000)
        self.assertEqual(result['withheld_reason'], 'REQUIRED_CONTEXT_EXCEEDS_BUDGET')
        self.assertLessEqual(review_reader.size(result), 1000)
        result = review_reader.read(record, 'core', {'scope': 'required'}, '/claims/0', maximum=64000)
        self.assertIsNone(result['continuation'])
        self.assertIn('registered file', result['guidance'])

    def test_cursor_binds_record_context_and_requested_selection(self):
        record = {'id': 'T', 'claims': [{'kind': 'NSF', 'statement': 'x' * 800} for _ in range(5)]}
        context = {'scope': 'fixture'}
        first = review_reader.read(record, 'core', context, maximum=1700)
        cursor = first['continuation']['arguments']['cursor']
        for changed, changed_context, pointer in [
            (dict(record, id='OTHER'), context, ''),
            (dict(record, title='Changed'), context, ''),
            (record, {'scope': 'changed'}, ''),
            (record, context, '/claims')]:
            with self.subTest(pointer=pointer, context=changed_context):
                with self.assertRaises(KBError) as caught:
                    review_reader.read(changed, 'core', changed_context, pointer, cursor, 1700)
                self.assertEqual(caught.exception.code, 'INVALID_CURSOR')
        for invalid in ['?', 'W10', 'bnVsbA']:
            with self.assertRaises(KBError):
                review_reader.read(record, 'core', context, cursor=invalid, maximum=1700)

    def test_long_pointer_withheld_response_includes_retry_in_total_budget(self):
        key = 'p' * 1900
        result = review_reader.read({'id': 'T', key: 'small'}, 'legacy', {}, '/' + key, maximum=1000)
        self.assertEqual(result['objects'], [])
        self.assertIsNone(result['continuation'])
        self.assertIn('larger byte budget', result['guidance'])
        self.assertLessEqual(review_reader.size(result), 1000)

    def test_narrow_budget_keeps_retry_when_full_withheld_context_does_not_fit(self):
        record = {'id': 'T', 'title': 'x' * 2000}
        context = {'scope': 'required ' + 'x' * 4300}
        result = review_reader.read(record, 'legacy', context, maximum=4800)
        self.assertEqual(result['objects'], [])
        self.assertFalse(result['complete'])
        self.assertLessEqual(review_reader.size(result), 4800)
        self.assertIsNotNone(result['continuation'])
        arguments = result['continuation']['arguments']
        self.assertEqual(arguments['max_bytes'], 64000)
        resumed = review_reader.read(record, 'legacy', context,
            arguments['pointer'], arguments['cursor'], arguments['max_bytes'])
        self.assertTrue(resumed['complete'])
        self.assertEqual(resumed['scope'], context['scope'])
        self.assertEqual([obj['value'] for obj in resumed['objects']], list(record.values()))

    def test_review_requires_explicit_role_and_does_not_modify_old_shapes(self):
        with self.assertRaises(KBError) as caught:
            self.service.get_entry('AI-N001-01', purpose='review')
        self.assertEqual(caught.exception.code, 'ADMISSION_DENIED')
        old = self.service.get_entry('AI-N001-01')
        self.assertEqual(len(old['entry']), 10)
        with self.assertRaises(KBError):
            self.service.get_entry('AI-N001-01', cursor='any')
        with self.assertRaises(KBError):
            self.service.lookup_api('EntityScript:Remove', family='all', projection='coding')

    def test_tool_contract_keeps_nine_and_accepts_explicit_review(self):
        self.assertEqual(len(TOOLS), 9)
        spec = next(t for t in TOOLS if t['name'] == 'get_entry')
        check_arguments(spec, {'id': 'T', 'purpose': 'review', 'projection': 'reviewer', 'cursor': ''})
        spec = next(t for t in TOOLS if t['name'] == 'lookup_api')
        check_arguments(spec, {'symbol': 'T', 'family': 'all', 'projection': 'reviewer'})

    def test_cross_family_lookup_preserves_ambiguity_and_executable_followups(self):
        research = {'results': [{'id': 'EXP-FISH-001', 'family': 'native_mechanism', 'pointer': '/api_contracts/2'}],
                    'contract_status': 'RESEARCH_CONTRACT_DELIVERED', 'total_matches': 1}
        legacy = {'results': [{'id': 'FACT-DST-001', 'family': 'legacy'}, {'id': 'AI-N001-01', 'family': 'n001'},
                              {'id': 'NC-N002-FINAL-01', 'family': 'core'}],
                  'contract_status': 'TYPED_CONTRACT_PARTIAL', 'total_matches': 3}
        with patch.object(self.service, '_lookup_mechanism_api', return_value=research), \
                patch.object(self.service, 'lookup_api', return_value=legacy):
            result = self.service._lookup_all_api('Demo:Run', 5, 'reviewer', 'decision', None, None, None, 64000)
        self.assertEqual({r['family'] for r in result['results']}, {'legacy', 'n001', 'core', 'native_mechanism'})
        for item in result['results']:
            read = self.service.get_entry(**item['followup']['arguments'])
            self.assertTrue(read['objects'])
        legacy = dict(legacy, results=[], disambiguation_required=True,
                      declaration_candidates=[{'symbol': 'Demo:Run', 'source_file': 'scripts/demo.lua'}])
        with patch.object(self.service, '_lookup_mechanism_api', return_value=research), \
                patch.object(self.service, 'lookup_api', return_value=legacy):
            result = self.service._lookup_all_api('Demo:Run', 5, 'reviewer', 'decision', None, None, None, 1000)
        self.assertTrue(result['disambiguation_required'])
        self.assertEqual(result['results'], [])
        self.assertLessEqual(review_reader.size(result), 1000)

    def test_cross_family_lookup_keeps_withheld_research_navigation(self):
        research = {'results': [], 'results_truncated': True, 'total_matches': 1,
                    'withheld_atoms': [{'id': 'EXP-FISH-001', 'pointer': '/api_contracts/2',
                                        'reason': 'WHOLE_ATOM_AND_REQUIRED_CONTEXT_EXCEED_BUDGET'}]}
        with patch.object(self.service, '_lookup_mechanism_api', return_value=research), \
                patch.object(self.service, 'lookup_api', return_value={'results': []}):
            result = self.service._lookup_all_api('Demo:Run', 5, 'reviewer', 'decision', None, None, None, 64000)
        self.assertEqual(result['results'][0]['id'], 'EXP-FISH-001')
        self.assertEqual(result['results'][0]['followup']['arguments']['purpose'], 'review')
        self.assertTrue(result['results_truncated'])

    def test_legacy_selected_object_keeps_all_conditions_and_execution_status(self):
        for identifier, pointer in [('PATTERN-NET-001', '/details/core_idea'), ('TEST-NET-001', '/details/action')]:
            result = self.review(identifier, pointer=pointer, max_bytes=64000)
            self.assertEqual(result['detail_boundaries'], self.catalog.records[identifier]['details'])


class UnifiedReviewCommandTests(unittest.TestCase):
    def test_unprepared_review_reads_public_material(self):
        failure = run_kb.PreparationError('SOURCES_NOT_PREPARED', 'fixture missing sources')
        for arguments in (['review', 'AI-N001-01'], ['review', '--api', 'Demo:Run']):
            error = io.StringIO()
            with patch.object(run_kb, 'prepared_runtime', side_effect=failure), \
                    patch.object(run_kb, 'public_review', side_effect=AssertionError('no mode downgrade')), \
                    contextlib.redirect_stdout(error):
                self.assertEqual(run_kb.main(arguments), 0)
            self.assertIn('objects' if arguments[1] != '--api' else 'results', json.loads(error.getvalue()))

    def test_id_review_passes_bound_continuation_parameters(self):
        with patch.object(run_kb, 'prepared_runtime', return_value=('fixture-config', ROOT)), \
                patch('dst_kb.public_reader.PublicReader') as factory, contextlib.redirect_stdout(io.StringIO()):
            factory.return_value.call.return_value = {'objects': []}
            code = run_kb.main(['review', 'AI-N001-01', '--pointer', '/native_fact', '--cursor', 'fixture',
                               '--source-epoch', '759671', '--max-bytes', '64000'])
        self.assertEqual(code, 0)
        factory.return_value.call.assert_called_once_with('get_entry', {
            'id': 'AI-N001-01', 'projection': 'reviewer', 'purpose': 'review', 'pointer': '/native_fact',
            'cursor': 'fixture', 'source_epoch': '759671', 'max_bytes': 64000})
        factory.return_value.close.assert_called_once()

    def test_api_review_selects_all_families_without_manual_routing(self):
        with patch.object(run_kb, 'prepared_runtime', return_value=('fixture-config', ROOT)), \
                patch('dst_kb.public_reader.PublicReader') as factory, contextlib.redirect_stdout(io.StringIO()):
            factory.return_value.call.return_value = {'results': []}
            code = run_kb.main(['review', '--api', 'Demo:Run', '--source-file', 'scripts/demo.lua', '--limit', '10'])
        self.assertEqual(code, 0)
        factory.return_value.call.assert_called_once_with('lookup_api', {
            'symbol': 'Demo:Run', 'projection': 'reviewer', 'family': 'all', 'top_k': 10,
            'source_file': 'scripts/demo.lua', 'max_bytes': 24000})


if __name__ == '__main__':
    unittest.main()

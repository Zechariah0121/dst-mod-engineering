"""Single evidence budgets on registered freeze/temperature and hostile edges."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import mechanism_evidence as evidence, native_mechanism as mechanisms
from dst_kb.config import KBError
from dst_kb.service import Service


def cost(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


def assessment_for(record, inputs=3):
    # Real registered locators; synthetic preparation outcomes (no Lua proof).
    refs = []
    for ref in record['document']['source_references']:
        refs.append({'reference_id': ref['id'], 'source_file': ref['source_file'],
                     'evidence_file_sha256': ref['file_sha256'],
                     'evidence_range_sha256': ref['range_sha256'],
                     'status': 'FILE_HASH_MATCH',
                     'source_checks': [{'source_input_index': i,
                                        'provided_archive_sha256': str(i) * 64,
                                        'status': 'FILE_HASH_MATCH',
                                        'observed_file_sha256': ref['file_sha256'],
                                        'observed_range_sha256': ref['range_sha256']}
                                       for i in range(inputs)]})
    return {'summary': {'sources': [{'source_input_index': i, 'archive_sha256': str(i) * 64}
                                    for i in range(inputs)], 'notice': 'Static source checks only.'},
            'native_mechanisms': {'documents': [{'file': record['registration']['file'],
                                                'sha256': record['registration']['sha256'],
                                                'references': refs}]}}


class MechanismEvidenceBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = mechanisms.load(ROOT / 'knowledge')
        cls.freeze = cls.records['EXP-FREEZE-001']
        cls.temperature = cls.records['EXP-TEMP-001']

    def resolve(self, record=None, **kwargs):
        with patch.object(evidence, 'source_preparation_document', return_value=None):
            return evidence.resolve(record or self.freeze, **kwargs)

    def test_registered_freeze_and_temperature_single_ref_fits(self):
        for record in (self.freeze, self.temperature):
            with self.subTest(id=record['entry']['id']):
                assessment = assessment_for(record)
                with patch.object(evidence, 'source_preparation_document', return_value=assessment):
                    result = evidence.resolve(record)
                context = result['evidence']
                identifier = mechanisms.local_refs(record['entry'])[0]
                selected = next(r for r in record['document']['source_references'] if r['id'] == identifier)
                self.assertLessEqual(cost(result), 24000)
                self.assertEqual(context['value'], selected)
                self.assertEqual(context['source_references'], [selected])
                self.assertEqual(context['scope'], record['entry']['scope'])
                self.assertEqual(context['unknowns'], record['entry']['unknowns'])
                self.assertEqual(context['limitations'], record['document']['limitations'])
                self.assertEqual(context['coding_status'], 'hold')
                self.assertFalse(context['coding_admission_granted'])
                self.assertFalse(context['runtime_validation_performed'])
                self.assertEqual(context['source_input_assessment']['references'],
                                 [r for r in assessment['native_mechanisms']['documents'][0]['references']
                                  if r['reference_id'] == identifier])
                self.assertEqual(context['source_input_assessment']['sources'], assessment['summary']['sources'])
                self.assertNotIn('claims', context)

    def test_does_not_construct_or_copy_whole_entry(self):
        record = copy.deepcopy(self.freeze)
        for claim in record['entry']['claims']:
            claim['statement'] = 'UNSELECTED_CLAIM_SENTINEL' * 10000
        with patch.object(mechanisms, 'envelope', side_effect=AssertionError('whole envelope used')):
            result = self.resolve(record)
        self.assertNotIn('UNSELECTED_CLAIM_SENTINEL', json.dumps(result))
        self.assertIn('evidence', result)

    def test_temperature_large_preparation_manifest_is_not_a_single_ref_budget(self):
        record = self.temperature
        assessment = assessment_for(record)
        with patch('dst_kb.source_epoch_runtime.source_preparation_document', return_value=assessment):
            old = mechanisms.envelope(record)
        identifier = mechanisms.local_refs(record['entry'])[0]
        ref = next(r for r in record['document']['source_references'] if r['id'] == identifier)
        old.update(value=ref, source_references=[ref])
        self.assertGreater(cost({'evidence': old, 'projection': 'reviewer'}), 24000)
        with patch.object(evidence, 'source_preparation_document', return_value=assessment):
            current = evidence.resolve(record)
        self.assertLessEqual(cost(current), 24000)
        self.assertEqual(len(current['evidence']['source_input_assessment']['references']), 1)

    def test_subpointer_retains_whole_atom_and_exact_document_coordinate(self):
        index = len(mechanisms.local_refs(self.freeze['entry'])) - 1
        result = self.resolve(index=index, subpointer='/symbols/0')['evidence']
        position = self.freeze['document']['source_references'].index(result['value'])
        pointer = '/source_references/' + str(position)
        self.assertEqual(result['artifact']['pointer'], pointer)
        self.assertEqual(result['pointer'], pointer)
        self.assertEqual(result['requested_pointer'], pointer + '/symbols/0')
        self.assertEqual(result['requested_subpointer'], '/symbols/0')
        self.assertEqual(result['requested_pointer'], result['artifact']['pointer'] + result['requested_subpointer'])
        self.assertIn('file_sha256', result['value'])
        self.assertIn('range_sha256', result['value'])

    def test_strict_subpointers_and_argument_types(self):
        for kwargs in ({'index': -1}, {'index': True}, {'index': 9999},
                       {'maximum': True}, {'maximum': 999}, {'maximum': 24001},
                       {'subpointer': None}, {'subpointer': '#/symbols/0'},
                       {'subpointer': '/symbols/-1'}, {'subpointer': '/symbols/00'},
                       {'subpointer': '/symbols/999'}, {'subpointer': '/bad~2escape'},
                       {'subpointer': '/id/no-scalar-traversal'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(KBError) as caught:
                self.resolve(**kwargs)
            self.assertEqual(caught.exception.code, 'INVALID_ARGUMENT')

    def test_exact_budget_includes_wrapper_source_environment_and_no_partial_atom(self):
        env = {'source_epoch': '759671', 'source_input_assessment': {'sources': ['identity' * 50]}}
        result = self.resolve(source_environment=env)
        size = cost(result)
        self.assertGreater(size, 1000)
        self.assertEqual(self.resolve(source_environment=env, maximum=size), result)
        withheld = self.resolve(source_environment=env, maximum=size - 1)
        self.assertLessEqual(cost(withheld), size - 1)
        self.assertIsNone(withheld['value'])
        self.assertTrue(withheld['bounded'])
        self.assertNotIn('evidence', withheld)
        self.assertNotIn('source_references', withheld)

    def test_oversize_required_scope_and_selected_assessment_are_withheld(self):
        record = copy.deepcopy(self.freeze)
        record['entry']['scope'] = {'required': '范围' * 20000}
        result = self.resolve(record, maximum=1000)
        self.assertIsNone(result['value'])
        self.assertLessEqual(cost(result), 1000)
        assessment = assessment_for(self.freeze)
        identifier = mechanisms.local_refs(self.freeze['entry'])[0]
        selected = next(r for r in assessment['native_mechanisms']['documents'][0]['references']
                        if r['reference_id'] == identifier)
        selected['source_checks'][0]['reason'] = 'REQUIRED_SELECTED_CHECK' * 4000
        with patch.object(evidence, 'source_preparation_document', return_value=assessment):
            result = evidence.resolve(self.freeze)
        self.assertIsNone(result['value'])
        self.assertLessEqual(cost(result), 24000)
        self.assertNotIn('REQUIRED_SELECTED_CHECK', json.dumps(result))

    def test_assessment_identity_missing_and_duplicate_fail_closed(self):
        identifier = mechanisms.local_refs(self.freeze['entry'])[0]
        for change in ('wrong_hash', 'missing', 'duplicate'):
            assessment = assessment_for(self.freeze)
            row = assessment['native_mechanisms']['documents'][0]
            selected = next(r for r in row['references'] if r['reference_id'] == identifier)
            if change == 'wrong_hash':
                row['sha256'] = 'f' * 64
            elif change == 'missing':
                row['references'].remove(selected)
            else:
                row['references'].append(copy.deepcopy(selected))
            with patch.object(evidence, 'source_preparation_document', return_value=assessment):
                with self.assertRaises(KBError) as caught:
                    evidence.resolve(self.freeze)
            self.assertEqual(caught.exception.code, 'SOURCE_EPOCH_STALE')

    def test_unrelated_assessment_not_borrowed_or_required(self):
        assessment = assessment_for(self.freeze)
        identifier = mechanisms.local_refs(self.freeze['entry'])[0]
        row = assessment['native_mechanisms']['documents'][0]
        row['references'] = [r for r in row['references'] if r['reference_id'] == identifier]
        with patch.object(evidence, 'source_preparation_document', return_value=assessment):
            result = evidence.resolve(self.freeze)
        self.assertEqual(len(result['evidence']['source_input_assessment']['references']), 1)

    def test_returned_context_does_not_mutate_committed_inputs(self):
        before = copy.deepcopy(self.freeze)
        result = self.resolve()['evidence']
        result['scope'].clear()
        result['source_references'][0]['symbols'].append('MUTATED')
        result['review_record'].clear()
        self.assertEqual(self.freeze, before)

    def test_proposed_service_adapter_keeps_reviewer_admission(self):
        # Exercise the real router with only the proposed replacement method.
        # No configured/installed service or source environment is touched.
        service = Service.__new__(Service)
        service.root = ROOT / 'knowledge'
        service.loaded_signature = 'single-evidence-budget-fixture'
        service.epoch_context = None
        service.ready = lambda: None
        service.db = sqlite3.connect(':memory:')
        self.addCleanup(service.db.close)
        service.db.execute('CREATE TABLE entries(id TEXT,type TEXT,json TEXT)')
        for identifier, record in self.records.items():
            service.db.execute('INSERT INTO entries VALUES(?,?,?)',
                               (identifier, mechanisms.TYPE, json.dumps(record['entry'])))

        def adapter(self, record, index, subpointer, maximum):
            return evidence.resolve(record, index, subpointer, maximum,
                                    self.epoch_context.metadata() if self.epoch_context is not None else None)

        with patch.object(Service, '_mechanism_evidence', adapter):
            with self.assertRaises(KBError) as caught:
                service.resolve_evidence('EXP-FREEZE-001', projection='coding')
            self.assertEqual(caught.exception.code, 'ADMISSION_DENIED')
            result = service.resolve_evidence('EXP-FREEZE-001', projection='reviewer', subpointer='/line_start')
        self.assertEqual(result['evidence']['requested_subpointer'], '/line_start')
        self.assertEqual(result['evidence']['value'], result['evidence']['source_references'][0])


if __name__ == '__main__':
    unittest.main()

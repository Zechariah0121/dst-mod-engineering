"""Whole-atom progressive research; uses the existing synthetic service fixture."""
import copy
import json
import unittest
from unittest.mock import patch
from test_cross_family_retrieval import fixture, mechanism
from dst_kb import native_mechanism

class ProgressiveResearchTests(unittest.TestCase):
    def setUp(self):
        self.service=fixture();self.addCleanup(self.service.db.close)
        p=patch('dst_kb.service.projection_v2.task_view_admission',return_value={'status':'TASK_ATOM_DELIVERED'})
        p.start();self.addCleanup(p.stop)

    def test_oversized_entry_can_deliver_a_complete_original_atom(self):
        record=mechanism();record['entry']['claims']=[dict(id=f'C{i}',kind='NSF',
            statement='ForceDry source removal '+str(i)+'x'*8000,evidence_refs=['R1']) for i in range(10)]
        self.service._records={record['entry']['id']:record}
        before=copy.deepcopy(record)
        result=self.service.search_kb('ForceDry',projection='reviewer',mode='research',view='decision',top_k=20)
        item=next(r for r in result['results'] if r['family']=='native_mechanism')
        self.assertTrue(item['pointer'].startswith('/claims/'))
        expected=native_mechanism.envelope(record,item['pointer'],assessment_detail=False)
        self.assertEqual({key:item[key] for key in expected},expected)
        self.assertTrue(item['expansion']['reviewer'])
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)
        self.assertEqual(record,before)
        self.assertFalse(item['coding_admission_granted'])

    def test_exact_id_keeps_explicit_full_record_contract(self):
        record=self.service._records['EXP-DEMO-001']
        full=native_mechanism.envelope(record,assessment_detail=False)
        self.assertEqual(self.service._research_seed_view(full,'EXP-DEMO-001'),full)

    def test_navigation_does_not_rank_api_unknowns_as_original_contract(self):
        record=mechanism();record['entry']['api_contracts']=[dict(symbol='Other:Method()',
            parameters=[],returns=[],preconditions=[],side_effects=[],lifecycle='',
            unknowns=['NebulaSentinel'])]
        self.service._records={record['entry']['id']:record}
        rows=self.service._research_navigation_rows([],[record],'NebulaSentinel')
        self.assertEqual(rows,[])

    def test_qualified_contract_identity_outranks_incidental_same_name(self):
        declared=mechanism('EXP-ONE-001');mentioned=mechanism('EXP-TWO-001')
        contract=dict(symbol='Owner:Method()',parameters=[],returns=[],preconditions=[],
            side_effects=[],lifecycle='',unknowns=[])
        declared['entry']['api_contracts']=[contract]
        mentioned['entry']['api_contracts']=[dict(contract,symbol='Other:Method()')]
        for record in [declared,mentioned]:
            record['entry']['title']='Same neutral title'
            record['entry']['claims'][0]['statement']='Owner:Method() and Other:Method() are mentioned here.'
        self.service._records={r['entry']['id']:r for r in [declared,mentioned]}
        rows=self.service._research_navigation_rows([],[mentioned,declared],'Owner:Method')
        self.assertEqual(rows[0]['document']['id'],declared['entry']['id'])
        self.assertGreater(rows[0]['score'],rows[1]['score'])
        self.assertFalse(rows[0]['match_reason']['cross_family_navigation']['coding_admission_granted'])

    def _seed_record(self):
        record=mechanism()
        def api(symbol,content,unknown):
            return dict(symbol=symbol,source_file='scripts/components/demo.lua',
                visibility='component method',parameters=[],returns=['nil'],
                preconditions=[],side_effects=[content],lifecycle='',
                evidence_refs=['R1'],unknowns=[unknown])
        record['entry']['api_contracts']=[
            api('Owner:Run()','', 'Owner:RunExtended timing payload scope cleanup'),
            api('Owner:RunExtended()','', 'not run')]
        record['entry']['claims']=[dict(record['entry']['claims'][0],
            statement='unrelated explanation '*6000)]
        record['entry']['mechanism_steps']=[]
        self.service._records={record['entry']['id']:record}
        return record

    def test_extended_method_does_not_exact_match_shorter_prefix(self):
        record=self._seed_record();before=copy.deepcopy(record)
        card=native_mechanism.envelope(record,assessment_detail=False)
        selected=self.service._research_seed_view(card,'Owner:RunExtended timing payload scope cleanup')
        self.assertEqual(selected['pointer'],'/api_contracts/1')
        self.assertEqual(selected['value'],record['entry']['api_contracts'][1])
        expected=native_mechanism.envelope(record,'/api_contracts/1',assessment_detail=False)
        self.assertEqual(selected,expected)
        self.assertEqual(record,before)

    def test_seed_overlap_excludes_unknowns_visibility_and_evidence_metadata(self):
        record=self._seed_record()
        record['entry']['api_contracts'][0]['side_effects']=['timing payload']
        record['entry']['api_contracts'][0]['unknowns']=[]
        bad=record['entry']['api_contracts'][1]
        bad['unknowns']=['timing payload scope cleanup']
        bad['visibility']='component method timing payload scope cleanup'
        bad['evidence_refs']=['timing','payload','scope','cleanup']
        record['document']['source_references'].extend(
            dict(record['document']['source_references'][0],id=name)
            for name in ['timing','payload','scope','cleanup'])
        card=native_mechanism.envelope(record,assessment_detail=False)
        # Supply valid reference objects for every polluted locator identity.
        # This test selects by authored contract text, not by missing-ref errors.
        selected=self.service._research_seed_view(card,'timing payload scope cleanup')
        self.assertEqual(selected['pointer'],'/api_contracts/0')
        self.assertEqual(selected['value'],record['entry']['api_contracts'][0])

    def test_negative_scope_does_not_supply_positive_seed_identity(self):
        record=self._seed_record();card=native_mechanism.envelope(record,assessment_detail=False)
        for query,pointer in [
            ('Owner:RunExtended timing; 排除 Owner:Run。','/api_contracts/1'),
            ('Owner:Run timing; 排除 Owner:RunExtended。','/api_contracts/0')]:
            with self.subTest(query=query):
                selected=self.service._research_seed_view(card,query)
                self.assertEqual(selected['pointer'],pointer)
        # Public admission is still conservative for a whole entry containing
        # explicitly excluded material; direct helper tests grant no admission.
        self.assertEqual(self.service._mechanism_matches(
            'Owner:RunExtended; 排除 Owner:Run。','reviewer','research',{}),[])

if __name__=='__main__':unittest.main()

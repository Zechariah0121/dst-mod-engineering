"""Cross-family navigation regression; synthetic records, no game/runtime proof."""
import copy
from contextlib import nullcontext
import json
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dst_kb.service import Service
from dst_kb.config import KBError
from dst_kb.retrieval_v2 import Ranker
from dst_kb import native_mechanism


def mechanism(identifier='EXP-DEMO-001', size=0):
    entry={'id':identifier,'title':'Moisture ForceDry source removal',
        'aliases':['moisture','ForceDry'],'engineering_question':'ForceDry source removal',
        **native_mechanism.STATES,'scope':{'source_epoch':'fixture','runtime_verified':False},
        'unknowns':['No runtime test'],
        'claims':[{'id':'C1','kind':'NSF','statement':'Moisture ForceDry source removal '+('x'*size),'evidence_refs':['R1']}],
        'api_contracts':[],'mechanism_steps':[]}
    return {'entry':entry,'index':0,'document':{'source_epoch':'fixture','archive_sha256':'a'*64,
        'limitations':['Synthetic only'],'source_references':[{'id':'R1','source_file':'scripts/demo.lua',
        'file_sha256':'b'*64,'line_start':1,'line_end':2,'range_sha256':'c'*64,'symbols':['ForceDry']}]},
        'registration':{'file':'research/demo.json','sha256':'d'*64,'review':{'file':'review.json','sha256':'e'*64}}}


def fixture():
    legacy={'id':'LEG-DEMO-001','entry_type':'source_fact','title':'Moisture source removal',
        'aliases':['moisture'],'summary':'Moisture:ForceDry() 停止组件更新并清理来源监听。',
        'scope_structured':{},'details':{'statement':'Moisture:ForceDry() 停止组件更新并清理来源监听。'}}
    core={'id':'CORE-DEMO-001','entry_type':'native_core_knowledge','title':'Moisture source removal',
        'aliases':['moisture'],'scope':{'statement':'Moisture source removal'},'gate_a':{'accepted':True},
        'claims':[{'id':'CORE-C1','kind':'NSF','statement':'Moisture:ForceDry() 停止组件更新并清理来源监听。', 'evidence_refs':[]}]}
    governance={core['id']:{'knowledge_status':'verified','retrieval_status':'reviewer_default','coding_status':'hold'}}
    svc=Service.__new__(Service);svc.epoch_context=None;svc.root=Path(__file__).resolve().parents[2]/'knowledge'
    svc.db=sqlite3.connect(':memory:');svc.db.execute('CREATE TABLE meta(key TEXT,value TEXT)')
    svc.db.execute("INSERT INTO meta VALUES('kb_version','synthetic')")
    svc.ready=lambda:None
    distractors=[{'id':f'OTHER-{i}','entry_type':'rule','title':f'Unrelated fixture {i}',
        'summary':'Unrelated graphics placeholder.','scope_structured':{},'details':{}} for i in range(10)]
    svc._ranker=Ranker([legacy,core]+distractors,governance,{})
    svc._ranker_v2=lambda:svc._ranker
    svc._records={'EXP-DEMO-001':mechanism()}
    svc._mechanisms=lambda:svc._records
    svc._governance=lambda ids:{'governance':{k:v for k,v in governance.items() if k in ids}}
    svc._append_companion_contexts=lambda *args,**kwargs:None
    # View rendering is outside this navigation test. Keep original whole
    # records visible, while exercising real ranker admission and service flow.
    svc._view_v2=lambda record,family,*args,**kwargs:{'id':record['id'],'title':record['title'],
        'family':family,'value':copy.deepcopy(record),'source_scope':record.get('scope',{})}
    return svc


class CrossFamilyRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.service=fixture()
        self.addCleanup(self.service.db.close)
        self.admission=patch('dst_kb.service.projection_v2.task_view_admission',return_value={'status':'TASK_ATOM_DELIVERED'})
        self.admission.start();self.addCleanup(self.admission.stop)

    def search(self,**kwargs):
        return self.service.search_kb('ForceDry',projection='reviewer',mode='research',view='reviewer',**kwargs)

    def test_one_global_candidate_stream_includes_all_three_families(self):
        result=self.search(top_k=30)
        self.assertEqual({r['family'] for r in result['results']},{'legacy','core','native_mechanism'})
        self.assertEqual(result['total_matches'],3)
        self.assertTrue(all(r['match_reason']['cross_family_navigation']['corpus_size']==13 for r in result['results']))
        self.assertEqual(self.search(top_k=1)['results'][0]['id'],result['results'][0]['id'])
        self.assertEqual([r['score'] for r in result['results']],sorted((r['score'] for r in result['results']),reverse=True))

    def test_positive_filters_and_or_are_applied_before_global_top_k(self):
        for family in ['legacy','core','native_mechanism']:
            with self.subTest(family=family):
                rows=self.search(families=[family])['results']
                self.assertTrue(rows);self.assertEqual({r['family'] for r in rows},{family})
        self.assertFalse(self.search(families=['native_mechanism'],coding_statuses=['coding_default'])['results'])
        rows=self.search(families=['legacy'],coding_statuses=['hold'],scope_logic='or')['results']
        self.assertEqual({r['family'] for r in rows},{'legacy','core','native_mechanism'})

    def test_negative_only_material_cannot_admit_mechanism(self):
        rows=self.service.search_kb('ForceDry; exclude EXP-DEMO-001',projection='reviewer',mode='research',view='reviewer')['results']
        self.assertNotIn('EXP-DEMO-001',[r['id'] for r in rows])
        records=self.service._mechanism_matches('unrelated; 不要 ForceDry', 'reviewer','research',{})
        self.assertEqual(records,[])

    def test_default_and_coding_admission_stay_closed(self):
        for projection,mode in [('coding','research'),('coding',None),('reviewer',None)]:
            rows=self.service.search_kb('ForceDry',projection=projection,mode=mode,view='reviewer')['results']
            self.assertNotIn('native_mechanism',{r['family'] for r in rows})
            if projection=='coding':self.assertNotIn('core',{r['family'] for r in rows})

    def test_exact_mechanism_id_retains_explicit_review(self):
        result=self.service.search_kb('EXP-DEMO-001',projection='reviewer',view='reviewer')
        self.assertEqual([r['id'] for r in result['results']],['EXP-DEMO-001'])
        item=result['results'][0]
        self.assertEqual(item['value'],self.service._records[item['id']]['entry'])
        self.assertEqual(item['coding_status'],'hold');self.assertFalse(item['runtime_validation_performed'])
        self.assertTrue(item['scope']);self.assertTrue(item['source_references'])

    def test_bundle_uses_entries_and_total_payload_budget_without_slicing(self):
        before=copy.deepcopy(self.service._records['EXP-DEMO-001']['entry'])
        result=self.service.get_context_bundle('ForceDry',mode='research',projection='reviewer',view='reviewer',budget='deep')
        self.assertEqual({r['family'] for r in result['entries']},{'legacy','core','native_mechanism'})
        item=next(r for r in result['entries'] if r['family']=='native_mechanism')
        self.assertEqual(item['value'],before)
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)
        self.service._records['EXP-DEMO-001']=mechanism(size=70000)
        for view in ['reviewer','decision']:
            result=self.service.get_context_bundle('ForceDry',mode='research',projection='reviewer',view=view,budget='compact')
            self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),16000)
            self.assertNotIn('EXP-DEMO-001',[r['id'] for r in result['entries']])
            self.assertTrue(any('EXP-DEMO-001' in g.get('withheld_entry_ids',[]) for g in result['knowledge_gaps']))

    def test_decision_path_preserves_complete_mechanism_envelope(self):
        record=self.service._records['EXP-DEMO-001']
        for use_bundle in [False,True]:
            if use_bundle:
                result=self.service.get_context_bundle('ForceDry',mode='research',projection='reviewer',view='decision',budget='deep')
                rows=result['entries']
            else:
                result=self.service.search_kb('ForceDry',projection='reviewer',mode='research',view='decision')
                rows=result['results']
            item=next(r for r in rows if r['family']=='native_mechanism')
            expected=native_mechanism.envelope(record,assessment_detail=False)
            self.assertEqual({key:item[key] for key in expected},expected)
            self.assertEqual(item['value'],record['entry'])
            self.assertIn('reviewer',item['expansion'])

    def test_budget_rejection_refills_actual_top_k_and_keeps_followup(self):
        # The matching ID puts this huge entry first in shared navigation.
        record=mechanism(size=70000)
        self.service._records['EXP-DEMO-001']=record
        rows,diagnosis=self.service._ranker.search('ForceDry','reviewer',30,mode='research',view='reviewer')
        candidates=self.service._research_navigation_rows(rows,[record],'ForceDry')
        # Explicitly make mechanism the leading admitted view to isolate fit/refill.
        candidates.sort(key=lambda r:'mechanism_record' not in r)
        with patch.object(self.service,'_research_navigation_rows',return_value=candidates):
            result=self.search(top_k=1)
        self.assertEqual(len(result['results']),1)
        self.assertNotEqual(result['results'][0]['id'],'EXP-DEMO-001')
        self.assertEqual(result['withheld_atoms'][0]['followup']['id'],'EXP-DEMO-001')
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)

    def test_oversized_required_environment_rejects_complete_search(self):
        environment={'source_epoch':'fixture','source_input_assessment':{'sources':[
            {'kind':'ZIP','archive_sha256':'a'*64,'identified_target':None} for _ in range(600)]}}
        self.assertGreater(len(json.dumps(environment,ensure_ascii=False).encode()),64000)
        before=copy.deepcopy(self.service._records)
        self.service.epoch_context=SimpleNamespace(source_epoch='fixture',cache_key='fixture',
            metadata=lambda:copy.deepcopy(environment))
        for view in ['decision','reviewer','evidence']:
            with self.subTest(view=view):
                # This metadata-only fixture does not bind a source registry.
                with patch('dst_kb.source_epoch_runtime.bind_epoch',side_effect=lambda context:nullcontext()):
                    with self.assertRaises(KBError) as caught:
                        self.service.search_kb('ForceDry',projection='reviewer',mode='research',view=view)
                self.assertEqual(caught.exception.code,'PAYLOAD_BUDGET_EXCEEDED')
                self.assertEqual(self.service._records,before)
                self.assertEqual(self.service.epoch_context.metadata(),environment)

    def test_many_deferred_rows_are_bounded_after_whole_facts_fit(self):
        self.service._records={f'EXP-DEMO-{i:03d}':mechanism(f'EXP-DEMO-{i:03d}',size=50000)
                               for i in range(60)}
        result=self.search(top_k=20)
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)
        self.assertTrue({'LEG-DEMO-001','CORE-DEMO-001'} <= {r['id'] for r in result['results']})
        self.assertTrue(any(r['family']=='native_mechanism' for r in result['results']))
        self.assertEqual(result['payload_bytes'],len(json.dumps(result,ensure_ascii=False).encode()))
        self.assertGreater(result['withheld_atoms_omitted_count'],0)
        self.assertEqual(result['withheld_atoms_total_count'],
                         len(result['withheld_atoms'])+result['withheld_atoms_omitted_count'])
        self.assertTrue(result['withheld_navigation_followup'])
        for item in result['results']:
            if item['family']=='native_mechanism':
                self.assertEqual(item['value'],self.service._records[item['id']]['entry'])
        self.assertTrue(all(row['followup']['id']==row['id'] for row in result['withheld_atoms']))

    def test_search_withholds_whole_oversized_mechanism(self):
        self.service._records['EXP-DEMO-001']=mechanism(size=70000)
        result=self.search(top_k=30)
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)
        self.assertNotIn('EXP-DEMO-001',[r['id'] for r in result['results']])
        self.assertTrue(result['withheld_atoms'])


if __name__=='__main__':unittest.main()

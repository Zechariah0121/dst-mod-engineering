"""Synthetic task navigation, competing lifecycle subjects and intact delivery."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dst-kb-service'))
from dst_kb import native_mechanism as mechanisms
from dst_kb.service import Service


def record(identifier, title, claims, *, symbol='Reader:Restore', prose='', aliases=()):
    refs=[{'id':'R'+str(i),'source_file':'scripts/sample.lua','file_sha256':'a'*64,
           'line_start':i+1,'line_end':i+1,'range_sha256':'b'*64,'symbols':[]} for i in range(len(claims))]
    entry={'id':identifier,'title':title,'aliases':list(aliases),'engineering_question':title,
           **mechanisms.STATES,'scope':{'evidence':'synthetic static fixture','exclusions':['No engine guarantee']},
           'unknowns':['Actual transport is unknown.'],
           'claims':[{'id':identifier+'-'+str(i),'kind':'NSF','statement':text,'evidence_refs':['R'+str(i)]}
                     for i,text in enumerate(claims)],
           'api_contracts':[{'symbol':symbol,'source_file':'scripts/sample.lua','visibility':'file-local function; not exported',
                             'parameters':['saved input'],'returns':'nil','preconditions':['valid host'],
                             'side_effects':prose,'lifecycle':['scoped owner cleanup'],'unknowns':['not run'],
                             'evidence_refs':['R0']}],
           'mechanism_steps':[]}
    return {'entry':entry,'document':{'source_epoch':'fixture','archive_sha256':'c'*64,
                                    'limitations':['Synthetic fixture, no Lua execution.'],'source_references':refs},
            'registration':{'file':'research/fixture.json','sha256':'d'*64,'review':{'file':'review.json','sha256':'e'*64}},
            'index':0}


class TaskNavigationTests(unittest.TestCase):
    def service(self, records):
        service=Service.__new__(Service)
        service.root=ROOT/'knowledge';service.loaded_signature='fixture';service.epoch_context=None
        service.ready=lambda:None
        service._mechanisms=lambda:{r['entry']['id']:r for r in records}
        diagnosis={'candidate_matches':0,'query_intent':{},'excluded':[],'knowledge_gap_meaning':'No inferred answer.'}
        service._ranker_v2=lambda:SimpleNamespace(documents=[],search=lambda *a,**k:([],copy.deepcopy(diagnosis)))
        service._governance=lambda ids:{}
        service._append_companion_contexts=lambda *a:None
        service.db=sqlite3.connect(':memory:')
        service.db.execute('CREATE TABLE meta(key TEXT,value TEXT)')
        service.db.execute("INSERT INTO meta VALUES('kb_version','fixture')")
        self.addCleanup(service.db.close)
        return service

    def test_mixed_question_is_not_one_unicode_api_identifier(self):
        entry=record('ONE','副本接线', ['replica状态需要按当前实例接线，RestoreSnapshot不会证明控件可读。'],
                     symbol='Mirror:RestoreSnapshot',prose='重新接线并读当前副本。')
        for query in ('replica已建立以后RestoreSnapshot是否能重建控件',
                      'HUD尚未建立时RestoreSnapshot怎样补装'):
            self.assertGreater(mechanisms.score(entry,query),0,query)
        for query in ('UnknownOwner:RestoreSnapshot','RestoreSnapshotSuffix','NeverDeclaredIdentifier'):
            self.assertEqual(mechanisms.score(entry,query),0,query)

    def test_unicode_signature_arguments_preserve_owner_and_complete_method_guards(self):
        entry=record('ONE','恢复回调', ['OnRestore restores saved fields.'],
                     symbol='Owner:OnRestore()',prose='Restore saved fields without a global readiness guarantee.')
        service=self.service([entry])
        for query in ('WrongOwner:OnRestore(中文参数)','OnRestoreExtended(中文参数)'):
            with self.subTest(query=query):
                self.assertEqual(mechanisms.score(entry,query),0)
                self.assertEqual(service.search_kb(query=query,mode='research',projection='reviewer',top_k=5)['results'],[])
        query='Owner:OnRestore(中文参数)'
        self.assertGreater(mechanisms.score(entry,query),0)
        results=service.search_kb(query=query,mode='research',projection='reviewer',top_k=5)['results']
        self.assertEqual([row['id'] for row in results],['ONE'])
        selected=results[0]
        if selected['pointer']=='':
            self.assertEqual(selected['value'],entry['entry'])
        else:
            self.assertEqual(selected['pointer'],'/api_contracts/0')
            self.assertEqual(selected['value'],entry['entry']['api_contracts'][0])

    def test_claim_only_task_enters_navigation_without_metadata_fact_matching(self):
        entry=record('ONE','一项恢复流程',['缺失句柄会阻止跨对象接线，但不补发业务对象。'],symbol='Reader:Read')
        self.assertGreater(mechanisms.score(entry,'跨对象接线缺失句柄'),0)
        # Evidence symbol/unknown prose is not searchable factual content.
        entry['entry']['unknowns'].append('NonexistentBusinessGuarantee')
        self.assertEqual(mechanisms.score(entry,'NonexistentBusinessGuarantee'),0)

    def test_common_callback_mentions_do_not_outvote_the_requested_subject(self):
        target=record('Z','计时器保存与暂停', ['Timer保存paused和剩余值，恢复时重新建任务。'],
                      symbol='Timer:Restore',prose='OnLoad reads paused and restores the timer.')
        noise=record('A','作物外观刷新',['OnLoad和LongUpdate会刷新作物外观。'],
                     symbol='Plant:OnLoad',prose='OnLoad LongUpdate '*500)
        service=self.service([noise,target])
        rows=service._research_navigation_rows([], [noise,target], '计时器 paused OnLoad 剩余值恢复')
        self.assertEqual(rows[0]['document']['id'],'Z')
        self.assertFalse(rows[0]['match_reason']['cross_family_navigation']['coding_admission_granted'])

    def test_english_owner_topic_uses_case_insensitive_word_boundaries(self):
        self.assertEqual(mechanisms.navigation_topics('Timer/Cooldown'),
                         mechanisms.navigation_topics('timer/cooldown'))
        self.assertIn('timer',mechanisms.navigation_topics('Timer:Restore'))
        self.assertNotIn('timer',mechanisms.navigation_topics('NotATimer'))

    def test_resource_owner_routes_survive_a_different_component_load_callback(self):
        owner=record('Z','宿主周期任务的取消', ['Scheduler keeps tasks until explicit cancellation.'],
                     symbol='Scheduler:Schedule',prose='OnLoad can create a new task; cancellation has an owner.')
        incidental=record('A','背包物品的载入', ['OnLoad reads saved contents and creates a task.'],
                          symbol='Bag:OnLoad',prose='OnLoad '*200)
        service=self.service([incidental,owner])
        rows=service._research_navigation_rows([], [incidental,owner], 'OnLoad以后重复任务怎样取消')
        self.assertEqual(rows[0]['document']['id'],'Z')

    def test_legacy_dependency_name_cannot_supply_primary_subject_ownership(self):
        service=self.service([])
        document={'id':'OLD','family':'legacy','entry':{'id':'OLD','title':'背包读取',
                  'entry_type':'source_fact','summary':'读取时可能等待计时器。',
                  'details':{'statement':'读取时可能等待计时器。'}},'contract_navigation':set()}
        service._ranker_v2=lambda:SimpleNamespace(documents=[document])
        query='计时器暂停恢复'
        first=service._research_navigation_rows([{'document':document}],[],query)[0]['score']
        document['contract_navigation']={'Timer:Restore'}
        second=service._research_navigation_rows([{'document':document}],[],query)[0]['score']
        self.assertEqual(first,second)

    def test_complementary_claims_are_the_exact_authored_array_with_full_context(self):
        entry=record('ONE','多阶段恢复',[
            '先按组件载入标量数据，组件遍历不提供固定次序。',
            '后续引用接线只取存在的目标映射，缺失目标保持未知。'],symbol='Reader:Fetch')
        service=self.service([entry]);before=copy.deepcopy(entry)
        card=mechanisms.envelope(entry)
        selected=service._research_seed_view(card,'组件载入标量次序以及引用接线缺失目标映射')
        self.assertEqual(selected['pointer'],'/claims')
        self.assertEqual(selected['value'],entry['entry']['claims'])
        self.assertEqual(selected['scope'],entry['entry']['scope'])
        self.assertEqual(selected['unknowns'],entry['entry']['unknowns'])
        self.assertEqual(selected['limitations'],entry['document']['limitations'])
        self.assertEqual({x['id'] for x in selected['source_references']},{'R0','R1'})
        self.assertEqual(selected['coding_status'],'hold')
        self.assertFalse(selected['runtime_validation_performed'])
        self.assertEqual(entry,before)

    def test_declared_api_query_still_delivers_the_complete_api_not_claim_group(self):
        entry=record('ONE','恢复接口', ['Reader:Restore恢复标量。','Reader:Restore还会接回引用映射。'],
                     prose='Restore scalar and reference state.')
        service=self.service([entry]);card=mechanisms.envelope(entry)
        for query in ('Reader:Restore','Restore'):
            selected=service._research_seed_view(card,query)
            self.assertEqual(selected['pointer'],'/api_contracts/0')
            self.assertEqual(selected['value'],entry['entry']['api_contracts'][0])
            identity=mechanisms.api_identity(selected['value'])
            self.assertEqual(identity['identity_kind'],'file_local')
            self.assertFalse(identity['public_api_inferred'])

    def test_oversize_claim_group_falls_back_whole_with_budget_and_followup(self):
        entry=record('ONE','多阶段恢复',[
            '标量恢复次序必须保留。','目标映射缺失时推迟引用接线。',
            'UNSELECTED_PAYLOAD '*10000],symbol='Reader:Fetch')
        service=self.service([entry])
        result=service.search_kb(query='标量恢复次序与目标映射缺失引用接线',mode='research',projection='reviewer',top_k=1)
        self.assertEqual(len(result['results']),1)
        selected=result['results'][0]
        self.assertRegex(selected['pointer'],r'^/claims/[01]$')
        index=int(selected['pointer'].split('/')[-1])
        self.assertEqual(selected['value'],entry['entry']['claims'][index])
        self.assertEqual(selected['source_references'],[entry['document']['source_references'][index]])
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),64000)
        self.assertNotIn('UNSELECTED_PAYLOAD',json.dumps(result))

    def test_role_mode_filters_and_negative_clauses_still_gate_before_ranking(self):
        entry=record('ONE','引用恢复',['对象接线同时订阅消息推送。'])
        service=self.service([entry])
        self.assertFalse(service.search_kb(query='引用恢复',mode='research',projection='coding')['results'])
        self.assertFalse(service.search_kb(query='引用恢复',projection='reviewer')['results'])
        self.assertFalse(service.search_kb(query='引用恢复',mode='research',projection='reviewer',families=['native_ai'])['results'])
        self.assertFalse(service.search_kb(query='引用恢复，不涉及消息推送',mode='research',projection='reviewer')['results'])
        self.assertTrue(service.search_kb(query='引用恢复',mode='research',projection='reviewer')['results'])


if __name__=='__main__':unittest.main(verbosity=2)

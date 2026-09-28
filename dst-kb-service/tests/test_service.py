import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from dst_kb.service import Service
from dst_kb.config import KBError
from dst_kb.mcp_server import Server,TOOLS

ROOT=Path(__file__).resolve().parents[1]
KB=Path(os.environ.get('DST_KB_TEST_ROOT',ROOT.parent/'dst-engineering-kb'))

def seal(root):
    mf=root/'PACKAGE-MANIFEST.json';m=json.loads(mf.read_text(encoding='utf-8'))
    for row in m['files']:
        p=root/row['path'];row['bytes']=p.stat().st_size;row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    mf.write_text(json.dumps(m),encoding='utf-8')

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='dst-kb-service-tests-')
        cls.work=Path(cls.temp.name);cls.config=cls.work/'config.json'
        cls.config.write_text(json.dumps({'kb_path':str(KB),'index_path':str(cls.work/'index.sqlite3')}),encoding='utf-8')
        cls.s=Service(cls.config)
        cls.before={p.relative_to(KB).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in KB.rglob('*') if p.is_file()}
    @classmethod
    def tearDownClass(cls):
        cls.s.close()
        after={p.relative_to(KB).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in KB.rglob('*') if p.is_file()}
        if cls.before!=after:raise AssertionError('Frozen baseline mutated')
        cls.temp.cleanup()

    def test_exact_id(self):
        id='RULE-NET-001'
        self.assertEqual(self.s.search_kb(id)['results'][0]['id'],id)
        self.assertEqual(self.s.get_entry(id)['entry']['id'],id)
    def test_keyword_bilingual_and_relevance(self):
        for query in ['world manager architecture','世界 管理器']:
            result=self.s.search_kb(query,mode='architect')['results']
            self.assertTrue(result)
            ids=[x['id'] for x in result]
            self.assertIn('PATTERN-WORLD-001',ids)
            self.assertNotEqual(result[0]['id'],'FACT-DST-001')
    def test_domain_filter(self):
        result=self.s.search_kb('',domains=['networking'])['results']
        self.assertTrue(result)
        self.assertTrue(all('networking' in e['scope']['domains'] for e in result))
    def test_evidence_and_confidence_filters(self):
        result=self.s.search_kb('',evidence_levels=['E3'],confidence=['Very High'])['results']
        self.assertTrue(result)
        self.assertTrue(all(e['evidence_level']=='E3' and e['confidence']=='Very High' for e in result))
    def test_runtime_scope_not_fabricated(self):
        self.assertEqual(self.s.search_kb('',runtime_environments=['dedicated'])['results'],[])
    def test_typed_relation_direction(self):
        x=self.s.get_related('CORRECTION-CASE001-001',relation_types=['supersedes'],direction='outgoing')
        self.assertEqual(x['results'][0]['id'],'CLAIM-CASE001-001')
        self.assertEqual(x['results'][0]['status'],'superseded')
        y=self.s.get_related('CLAIM-CASE001-001',relation_types=['supersedes'],direction='incoming')
        self.assertEqual(y['results'][0]['id'],'CORRECTION-CASE001-001')
        both=self.s.get_related('CORRECTION-CASE001-001',relation_types=['corrects','supersedes'],direction='outgoing')
        self.assertEqual({e['relation'] for e in both['edges']},{'corrects','supersedes'})
    def test_klei_only(self):
        x=self.s.get_klei_facts('container')
        self.assertTrue(x['results'])
        self.assertTrue(all(e['entry_type']=='source_fact' for e in x['results']))
        self.assertTrue(any(s['type']=='vanilla_source_snapshot' for s in self.s.get_entry(x['results'][0]['id'])['source_registry']))
    def test_anti_and_decision(self):
        for kind in ['anti_pattern','decision']:
            x=self.s.search_kb('',entry_types=[kind])['results']
            self.assertTrue(x);self.assertTrue(all(e['entry_type']==kind for e in x))
    def test_tests(self):
        x=self.s.get_tests(entry_ids=['PATTERN-NET-001'])['results']
        self.assertTrue(x)
        self.assertTrue(all(e['entry_type']=='test_case' for e in x))
        for e in x:self.assertEqual(self.s.get_entry(e['id'])['entry']['details']['execution_status'],'not_run')
    def test_no_result(self):
        x=self.s.search_kb('unmatchable_zxy987654321')
        self.assertTrue(x['knowledge_gap']);self.assertEqual(x['results'],[])
    def test_invalid_id(self):
        with self.assertRaises(KBError) as ctx:self.s.get_entry('../../config.toml')
        self.assertEqual(ctx.exception.code,'INVALID_ID')
    def test_bundle_budget_and_mode(self):
        for mode in ['architect','implement','review','debug','research']:
            for budget,limit in [('compact',8),('normal',15),('deep',24)]:
                b=self.s.get_context_bundle('world manager networking lifecycle',mode,budget)
                self.assertLessEqual(len(b['entries']),limit)
                self.assertLessEqual(len(json.dumps(b,ensure_ascii=False)),b['max_characters'])
                self.assertEqual(len({e['id'] for e in b['entries']}),len(b['entries']))
                self.assertNotIn('details',b['entries'][0])
                if mode=='architect':self.assertEqual(b['entries'][0]['entry_type'],'playbook')
    def test_empty_bundle_gap(self):
        b=self.s.get_context_bundle('unmatchable_zxy987654321')
        self.assertTrue(b['knowledge_gaps']);self.assertEqual(b['entries'],[])
    def test_hot_search_uses_index(self):
        self.s.db.set_trace_callback(lambda sql:None)
        index_time=self.s.index.stat().st_mtime_ns
        from unittest.mock import patch
        with patch.object(Path,'read_text',side_effect=AssertionError('hot query parsed a KB file')):
            self.assertTrue(self.s.search_kb('world')['results'])
            self.s.get_entry('RULE-NET-001')
        self.assertEqual(self.s.index.stat().st_mtime_ns,index_time)
    def test_reindex(self):
        before=self.s.get_entry('RULE-NET-001')['entry'];self.s.reindex()
        self.assertEqual(before,self.s.get_entry('RULE-NET-001')['entry'])
        self.assertEqual(self.s.status()['entries'],64)

    def fixture(self,name):
        root=self.work/name;shutil.copytree(KB,root)
        cfg=self.work/(name+'.json');cfg.write_text(json.dumps({'kb_path':str(root),'index_path':str(self.work/(name+'.db'))}),encoding='utf-8')
        return root,cfg
    def test_moved_path(self):
        root,cfg=self.fixture('moved');s=Service(cfg)
        try:self.assertEqual(s.search_kb('RULE-NET-001')['results'][0]['id'],'RULE-NET-001')
        finally:s.close()
    def test_corrupted_kb(self):
        root,cfg=self.fixture('corrupt');(root/'data/entries.json').write_text('{bad',encoding='utf-8')
        with self.assertRaises(KBError):Service(cfg)
    def test_unsupported_version(self):
        root,cfg=self.fixture('unsupported');p=root/'data/entries.json';x=json.loads(p.read_text(encoding='utf-8'));x['schema_version']='999';p.write_text(json.dumps(x),encoding='utf-8');seal(root)
        with self.assertRaises(KBError) as ctx:Service(cfg)
        self.assertEqual(ctx.exception.code,'UNSUPPORTED_KB_VERSION')
    def test_unknown_schema_fails_closed(self):
        root,cfg=self.fixture('schema');p=root/'schemas/entries.schema.json';x=json.loads(p.read_text(encoding='utf-8'));x['unevaluatedProperties']=False;p.write_text(json.dumps(x),encoding='utf-8');seal(root)
        with self.assertRaises(KBError) as ctx:Service(cfg)
        self.assertEqual(ctx.exception.code,'UNSUPPORTED_SCHEMA')
    def test_future_knowledge_version_same_contract(self):
        root,cfg=self.fixture('future');p=root/'data/entries.json';x=json.loads(p.read_text(encoding='utf-8'));x['kb_title']='Synthetic fixture v0.2';p.write_text(json.dumps(x),encoding='utf-8');seal(root)
        # 只测试标题不同仍按schema契约读取，不冒充真实KB v0.2已支持。
        s=Service(cfg)
        try:
            self.assertEqual(s.status()['entries'],64)
            self.assertEqual(s.status()['kb_version'],'0.2')
        finally:s.close()
    def test_stale_index_not_served(self):
        root,cfg=self.fixture('stale');s=Service(cfg)
        try:
            p=root/'data/entries.json';p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaises(KBError) as ctx:s.search_kb('world')
            self.assertEqual(ctx.exception.code,'INDEX_STALE')
        finally:s.close()
    def test_offline_mcp_graceful(self):
        cfg=self.work/'offline.json';cfg.write_text(json.dumps({'kb_path':str(self.work/'absent'),'index_path':str(self.work/'offline.db')}))
        server=Server(cfg)
        server.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}})
        x=server.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_kb','arguments':{'query':'world'}}})
        self.assertTrue(x['result']['isError']);self.assertFalse(x['result']['structuredContent']['kb_available']);server.close()
    def test_argument_validation(self):
        s=Server(self.config)
        try:
            for name,args in [('search_kb',{'top_k':True}),('get_entry',{}),('search_kb',{'domains':'networking'}),('search_kb',{'query':'x','unknown':1})]:
                with self.assertRaises(KBError):s.call(name,args)
        finally:s.close()
    def test_real_stdio_handshake_and_tools(self):
        requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},
                  {'jsonrpc':'2.0','method':'notifications/initialized'},
                  {'jsonrpc':'2.0','id':2,'method':'tools/list'},
                  {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_entry','arguments':{'id':'RULE-NET-001'}}}]
        run=subprocess.run([sys.executable,'-B',str(ROOT/'dst_kb_cli.py'),'--config',str(self.config),'serve'],input=''.join(json.dumps(x)+'\n' for x in requests),capture_output=True,encoding='utf-8',timeout=20)
        self.assertEqual(run.returncode,0,run.stderr)
        rows=[json.loads(x) for x in run.stdout.splitlines()]
        self.assertEqual(len(rows),3);self.assertEqual(len(rows[1]['result']['tools']),7)
        self.assertEqual(rows[2]['result']['structuredContent']['entry']['id'],'RULE-NET-001')

if __name__=='__main__':unittest.main(verbosity=2)

"""Registered research: preservation, admission, source guards and atomic budgets."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dst-kb-service'))
sys.path.insert(0,str(ROOT/'scripts'))
from dst_kb import family_registry as families, native_mechanism as mechanisms, mechanism_contract as contract
from dst_kb import native_mechanism_source as sources
from dst_kb.public_catalog import PublicCatalog
from dst_kb.service import Service
from dst_kb.config import KBError
import register_mechanisms as registration
import source_compatibility as compatibility


def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


class ResearchReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=mechanisms.load(ROOT/'knowledge')
        cls.catalog=PublicCatalog(ROOT)

    @classmethod
    def tearDownClass(cls):cls.catalog.close()

    def test_historical_facts_scope_governance_and_ids_are_preserved(self):
        expected={
            'data/entries.json':'d626b4460c5c0bf05190aabc0ac8f51d1e1732762a80b80da97223091d247ce6',
            'data/native001/canonical-native001-ai-knowledge.json':'bcf097f94cc98aeb27a0c00a8d455cb4c70a5beafa40729047480eff839c846a',
        }
        for name,digest in expected.items():self.assertEqual(sha((ROOT/'knowledge'/name).read_bytes()),digest,name)
        registry=families.load(ROOT/'knowledge')
        core=json.loads((ROOT/'knowledge/data/nativecore/native-core.json').read_bytes())
        def semantic(value):
            if isinstance(value,dict):
                return {k:semantic(v) for k,v in value.items() if k not in {'evidence_refs','sha256','bytes','source_artifacts'}}
            if isinstance(value,list):return [semantic(v) for v in value]
            return value
        # Evidence commitments change during reviewed source maintenance; the
        # preserved statements, Scope and governance must not change with them.
        preserved=json.dumps(semantic(core),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        self.assertEqual(sha(preserved),'511815910bbefb6b29ae334c25f1456bea715c087236d6c4a58f5ce12fb6f89a')
        governance={row['id']:row for row in core['state_registry']}
        for row in self.catalog.rows:
            if row['family']=='native_ai':
                for key in ('knowledge_status','retrieval_status','coding_status'):
                    self.assertEqual(row[key],governance[row['id']][key])
        for family in registry['families']:
            if family['name'] in families.HISTORICAL:
                self.assertEqual(sum(len(row['entry_ids']) for row in family['documents']),families.HISTORICAL[family['name']])
        first_batch={'EXP-AI-'+str(i).zfill(3) for i in range(1,8)}|{'EXP-WG-'+str(i).zfill(3) for i in range(1,6)}
        self.assertTrue(first_batch.issubset(self.records))
        registered={identifier for family in registry['families'] if family['name']=='native_mechanism' for document in family['documents'] for identifier in document['entry_ids']}
        self.assertEqual(set(self.records),registered)

    def test_chinese_and_symbol_catalog_search(self):
        for query in ('具名停止','PriorityNode','地皮注册','AddRoomPreInit'):
            results=self.catalog.call('search_catalog',{'query':query,'limit':20})['results']
            self.assertTrue(any(row['family']=='native_mechanism' for row in results),query)

    def test_public_atom_has_scope_epoch_limitations_and_real_local_refs(self):
        result=self.catalog.call('read_public_entry',{'id':'EXP-AI-003','purpose':'review','pointer':'/claims/0/statement','max_bytes':24000})
        self.assertTrue(result['whole_value_delivered'])
        self.assertEqual(result['pointer'],'/claims/0')
        self.assertIn(result['public_value']['kind'],('NSF','EI','REC','UNK'))
        context=result['research_context']
        self.assertEqual(context['scope'],self.records['EXP-AI-003']['entry']['scope'])
        self.assertEqual(context['source_epoch'],'759671')
        self.assertTrue(context['limitations'])
        self.assertEqual(set(result['public_value']['evidence_refs']),{r['id'] for r in context['source_references']})
        self.assertEqual(context['evidence_status'],'LOCATOR_HASH_ONLY')
        self.assertFalse(context['runtime_validation_performed'])

    def service(self):
        service=Service.__new__(Service)
        service.root=ROOT/'knowledge';service.loaded_signature='test-immutable-public-snapshot';service.epoch_context=None
        service.ready=lambda:None
        service.db=sqlite3.connect(':memory:')
        service.db.execute('CREATE TABLE entries(id TEXT,type TEXT,json TEXT)')
        for id,record in self.records.items():service.db.execute('INSERT INTO entries VALUES(?,?,?)',(id,mechanisms.TYPE,json.dumps(record['entry'])))
        self.addCleanup(service.db.close)
        return service

    def test_coding_id_and_evidence_are_denied(self):
        service=self.service()
        self.assertTrue(service.get_entry('EXP-AI-003')['withheld'])
        with self.assertRaises(KBError):service.resolve_evidence('EXP-AI-003',projection='coding')
        self.assertEqual(service._mechanism_matches('PriorityNode','coding','research',{}),[])
        self.assertEqual(service._mechanism_matches('PriorityNode','reviewer',None,{}),[])
        self.assertEqual(service._mechanism_matches('','reviewer','research',{}),[])

    def test_explicit_reviewer_full_entry_and_whole_claim(self):
        service=self.service()
        result=service.get_entry('EXP-AI-003',projection='reviewer',max_bytes=64000)
        self.assertTrue(result['entry']['whole_value_delivered'])
        self.assertEqual(result['entry']['value'],self.records['EXP-AI-003']['entry'])
        atom=service.get_entry('EXP-AI-003',projection='reviewer',pointer='/claims/0/statement')['entry']
        self.assertEqual(atom['value'],self.records['EXP-AI-003']['entry']['claims'][0])

    def test_budget_charges_scope_and_normalizes_deferred_pointer(self):
        record=copy.deepcopy(self.records['EXP-AI-003'])
        record['entry']['claims'][0]['statement']='长'*8000
        withheld=mechanisms.bounded(record,'/claims/0/statement',4000)
        self.assertFalse(withheld['whole_value_delivered'])
        self.assertNotIn('value',withheld)
        self.assertEqual(withheld['scope'],record['entry']['scope'])
        self.assertTrue(all(p.startswith('/claims/0/') and '/statement/' not in p for p in withheld['child_pointers']))
        self.assertLessEqual(len(json.dumps(withheld,ensure_ascii=False).encode()),4000)

    def test_locator_evidence_preserves_required_context_and_boundaries(self):
        result=self.service().resolve_evidence('EXP-AI-003',reference_index=0,projection='reviewer')['evidence']
        self.assertTrue(result['value']['source_file'].startswith('scripts/'))
        self.assertEqual(result['source_references'],[result['value']])
        self.assertTrue(result['scope']);self.assertTrue(result['limitations'])
        self.assertNotIn('source_excerpt',result['value'])

    def test_research_search_bundle_whole_payload_within_budget(self):
        service=self.service()
        records=service._mechanism_matches('PriorityNode','reviewer','research',{})
        self.assertTrue(records)
        for maximum in (16000,32000,64000):
            payload=service._mechanism_results(records,'PriorityNode',5,maximum)
            self.assertLessEqual(len(json.dumps(payload,ensure_ascii=False).encode()),maximum)
            for entry in payload['results']:
                self.assertTrue(entry['scope']);self.assertTrue(entry['limitations']);self.assertIn('source_references',entry)

    def test_contract_rejects_nested_shapes_unknown_kind_ids_and_epoch_hash(self):
        original=self.records['EXP-AI-003']['document']
        changes=[lambda d:d.update(source_epoch=''),lambda d:d.update(archive_sha256='bad'),
                 lambda d:d['entries'][0]['claims'][0].update(kind='RV'),
                 lambda d:d['entries'][0]['claims'][0].update(evidence_refs=[]),
                 lambda d:d['entries'].append(copy.deepcopy(d['entries'][0])),
                 lambda d:d['entries'][0].update(claims='not-an-array'),
                 lambda d:d['source_references'][0].update(source_file='scripts/../escape.lua'),
                 lambda d:d['entries'][0]['scope'].update(runtime_verified=True)]
        for change in changes:
            doc=copy.deepcopy(original);change(doc)
            with self.assertRaises(ValueError):contract.validate(doc)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='registration-fixture-',dir=ROOT/'tests');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'knowledge',self.root/'knowledge',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(ROOT/'source-epochs.json',self.root/'source-epochs.json')
        helpers=self.root/'dst-kb-service/dst_kb';helpers.mkdir(parents=True)
        for name in ('family_registry.py','mechanism_contract.py'):shutil.copyfile(ROOT/'dst-kb-service/dst_kb'/name,helpers/name)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file() and p.name!='batch.json' and not p.name.startswith('input-')}

    def item(self,topic='extra',suffix='X'):
        doc=copy.deepcopy(next(iter(mechanisms.load(ROOT/'knowledge').values()))['document'])
        for entry in doc['entries']:
            previous=entry['id'];entry['id']+='-'+suffix
            for query in doc['queries']:query['expected_entry_ids']=[entry['id'] if x==previous else x for x in query['expected_entry_ids']]
        source=self.root/('input-'+topic+'.json');write(source,doc)
        review=self.root/('input-review-'+topic+'.json');write(review,{'candidate_sha256':sha(source.read_bytes()),'runtime_verified':False,'scope':'Synthetic reviewer fixture; no semantic validation claimed'})
        return {'topic':topic,'candidate':str(source),'sha256':sha(source.read_bytes()),'review':str(review),'review_sha256':sha(review.read_bytes())}

    def batch(self,items):
        path=self.root/'batch.json';write(path,{'documents':items});return path

    def test_default_batch_adds_topic_and_preserves_brain_worldgen(self):
        item=self.item();registration.rebuild(self.root,self.batch([item]))
        registry=families.load(self.root/'knowledge')
        family=next(f for f in registry['families'] if f['name']=='native_mechanism')
        previous=next(f for f in families.load(ROOT/'knowledge')['families'] if f['name']=='native_mechanism')
        self.assertEqual(len(family['documents']),len(previous['documents'])+1)
        self.assertTrue(set(mechanisms.load(ROOT/'knowledge')).issubset(mechanisms.load(self.root/'knowledge')))

    def test_topic_revision_requires_explicit_replace_and_preserves_others(self):
        item=self.item('brain')
        before=self.snapshot()
        with self.assertRaises(ValueError):registration.rebuild(self.root,self.batch([item]))
        self.assertEqual(self.snapshot(),before)
        registration.rebuild(self.root,self.batch([item]),replace_topics=['brain'])
        ids=set(mechanisms.load(self.root/'knowledge'))
        self.assertIn('EXP-WG-001',ids);self.assertIn('EXP-AI-001-X',ids)

    def test_second_bad_hash_leaves_package_unchanged(self):
        first=self.item('first');second=self.item('second','Y');second['sha256']='0'*64
        before=self.snapshot()
        with self.assertRaises(ValueError):registration.rebuild(self.root,self.batch([first,second]))
        self.assertEqual(self.snapshot(),before)

    def test_commit_failure_rolls_back_all_changed_files(self):
        item=self.item();before=self.snapshot();real=registration.os.replace;calls=[]
        def fail_once(source,target):
            calls.append(str(target))
            if len(calls)==3:raise OSError('synthetic write failure')
            return real(source,target)
        with patch.object(registration.os,'replace',side_effect=fail_once):
            with self.assertRaises(OSError):registration.rebuild(self.root,self.batch([item]))
        self.assertEqual(self.snapshot(),before)

    def test_conflicting_ids_and_bad_schema_fail_before_commit(self):
        first=self.item('first');second=self.item('second')
        before=self.snapshot()
        with self.assertRaises(ValueError):registration.rebuild(self.root,self.batch([first,second]))
        self.assertEqual(self.snapshot(),before)


class SourceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='source-fixture-',dir=ROOT/'tests');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.zip=self.root/'new-unknown.zip'
        self.raw=b'-- authored toy\nfunction FutureNavigationOnly()\nend\n'
        with zipfile.ZipFile(self.zip,'w') as archive:archive.writestr('scripts/toy.lua',self.raw)
        self.ref={'id':'R','source_file':'scripts/toy.lua','file_sha256':sha(self.raw),'line_start':2,'line_end':3,'range_sha256':sha(b'function FutureNavigationOnly()\nend'),'symbols':['FutureNavigationOnly']}

    def setup_candidate(self,change=None):
        ref=copy.deepcopy(self.ref)
        if change:change(ref)
        doc={'archive_sha256':sha(self.zip.read_bytes()),'source_epoch':'future-unregistered','source_references':[ref]}
        file=self.root/'knowledge/toy.json';write(file,doc)
        write(self.root/'knowledge/FAMILY-REGISTRY.json',{'families':[{'name':'native_mechanism','documents':[{'file':'toy.json','sha256':sha(file.read_bytes())}]}]})

    def test_static_sources_verified_without_payload(self):
        self.setup_candidate();result=sources.verify(self.root,[self.zip])
        self.assertEqual(result['verified_references'],1);self.assertFalse(result['source_text_returned'])

    def test_hash_line_and_path_corruption_rejected(self):
        for change in (lambda r:r.update(file_sha256='0'*64),lambda r:r.update(line_end=99),lambda r:r.update(source_file='scripts/../toy.lua'),lambda r:r.update(range_sha256='0'*64)):
            self.setup_candidate(change)
            with self.assertRaises(ValueError):sources.verify(self.root,[self.zip])

    def test_unknown_new_archive_navigation_still_available(self):
        archive=compatibility.Archive(self.zip,'future-unregistered')
        try:
            result=compatibility.locate(archive,'FutureNavigationOnly')
            self.assertTrue(result['matches'])
        finally:archive.close()


if __name__=='__main__':unittest.main(verbosity=2)

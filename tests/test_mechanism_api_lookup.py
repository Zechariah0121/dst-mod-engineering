"""Explicit research API identity and whole-atom budgets; no game runtime test."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dst-kb-service'))
from dst_kb import native_mechanism as mechanisms
from dst_kb.service import Service
from dst_kb.config import KBError
from dst_kb.mcp_server import TOOLS


class MechanismAPILookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.records=mechanisms.load(ROOT/'knowledge')

    def service(self,records=None):
        service=Service.__new__(Service)
        service.root=ROOT/'knowledge';service.loaded_signature='immutable-test';service.epoch_context=None
        service.ready=lambda:None
        service._mechanisms=lambda:self.records if records is None else records
        return service

    def lookup(self,symbol,**kwargs):
        return self.service().lookup_api(symbol,family='native_mechanism',**kwargs)

    def test_schema_explicit_opt_in_and_legacy_default(self):
        spec=next(t for t in TOOLS if t['name']=='lookup_api')['inputSchema']['properties']
        self.assertEqual(spec['family']['default'],'legacy')
        service=self.service()
        with patch('dst_kb.source_identity.declaration_candidates',return_value=()), patch.object(service,'_lookup_api_for_source',return_value={'old':True}) as old:
            self.assertEqual(service.lookup_api('PriorityNode'),{'old':True})
            old.assert_called_once_with('PriorityNode',5,'reviewer','decision')
        with self.assertRaises(KBError):self.lookup('PriorityNode',projection='coding')
        with self.assertRaises(KBError):self.service().lookup_api('PriorityNode',owner='PriorityNode')

    def test_whole_atom_identity_version_scope_unknowns_and_refs(self):
        result=self.lookup('Growable:Pause')
        self.assertEqual(result['contract_status'],'RESEARCH_CONTRACT_DELIVERED')
        atom=result['results'][0]
        record=self.records['EXP-GROW-002']
        self.assertEqual(atom['value'],record['entry']['api_contracts'][0])
        self.assertEqual(atom['scope'],record['entry']['scope'])
        self.assertEqual(atom['unknowns'],record['entry']['unknowns'])
        self.assertEqual(atom['archive_sha256'],record['document']['archive_sha256'])
        self.assertEqual(atom['api_identity']['owner'],'Growable')
        self.assertEqual(atom['api_identity']['identity_kind'],'component_method')
        self.assertEqual(atom['coding_status'],'hold')
        self.assertFalse(atom['coding_admission_granted'])
        self.assertFalse(atom['runtime_validation_performed'])
        self.assertEqual(set(atom['value']['evidence_refs']),{r['id'] for r in atom['source_references']})
        self.assertFalse(atom['api_identity']['public_api_inferred'])

    def test_owner_disambiguation_is_not_top_k_selection(self):
        ambiguous=self.lookup('Visit',top_k=1)
        self.assertTrue(ambiguous['disambiguation_required'])
        self.assertGreater(ambiguous['total_identity_matches'],1)
        self.assertTrue(ambiguous['candidate_list_truncated'])
        self.assertEqual(ambiguous['results'],[])
        selected=self.lookup('Visit',owner='SequenceNode')
        self.assertEqual(selected['total_identity_matches'],1)
        self.assertEqual(selected['results'][0]['api_identity']['symbol'],'SequenceNode:Visit')
        self.assertEqual(self.lookup('WrongOwner:Visit')['total_matches'],0)

    def test_module_export_environment_and_global_remain_distinct(self):
        self.assertEqual(self.lookup('cooking.CalculateRecipe')['results'][0]['api_identity']['identity_kind'],'module_export')
        module=self.lookup('require("map/object_layout").Convert')['results'][0]
        self.assertEqual(module['api_identity']['owner'],'require("map/object_layout")')
        self.assertEqual(module['api_identity']['identity_kind'],'module_export')
        self.assertEqual(self.lookup('env.AddCookerRecipe')['results'][0]['api_identity']['owner'],'env')
        ambiguous=self.lookup('AddCookerRecipe')
        self.assertTrue(ambiguous['disambiguation_required'])
        selected=self.lookup('AddCookerRecipe',source_file='scripts/cooking.lua')
        self.assertEqual(selected['results'][0]['api_identity']['identity_kind'],'global')

    def test_module_quotes_require_valid_pairs_in_queries_and_authored_symbols(self):
        expected=self.lookup('require("map/object_layout").Convert')['results'][0]['value']
        for quote in ('"', "'"):
            symbol='require('+quote+'map/object_layout'+quote+').Convert'
            result=self.lookup(symbol)
            self.assertEqual(result['results'][0]['value'],expected)
            authored=copy.deepcopy(expected);authored['symbol']=symbol+'(node_id, item, addEntity)'
            identity=mechanisms.api_identity(authored)
            self.assertEqual(identity['symbol'],'require("map/object_layout").Convert')
            self.assertEqual(identity['owner'],'require("map/object_layout")')
        for opening,closing in (('"', "'"), ("'", '"')):
            symbol='require('+opening+'map/object_layout'+closing+').Convert'
            with self.assertRaises(KBError) as error:self.lookup(symbol)
            self.assertEqual(error.exception.code,'INVALID_ARGUMENT')
            authored=copy.deepcopy(expected);authored['symbol']=symbol+'(node_id, item, addEntity)'
            self.assertIsNone(mechanisms.api_identity(authored))

    def test_require_shape_never_overrides_local_or_unexported_visibility(self):
        record=copy.deepcopy(self.records['EXP-COOK-002'])
        api=copy.deepcopy(record['entry']['api_contracts'][0])
        api['symbol']='require("private/module").Hidden'
        record['entry']['api_contracts']=[api]
        for visibility,expected_kind in (
                ('file-local function; not exported','file_local'),
                ('local function','file_local'),
                ('module export; not exported','unknown'),
                ('not exported','unknown'),
                ('visibility unknown','unknown')):
            api['visibility']=visibility
            service=self.service({'toy':record})
            exported=service.lookup_api(api['symbol'],family='native_mechanism',identity_kind='module_export')
            self.assertEqual(exported['results'],[])
            result=service.lookup_api(api['symbol'],family='native_mechanism',identity_kind=expected_kind)
            atom=result['results'][0]
            self.assertEqual(atom['api_identity']['identity_kind'],expected_kind)
            self.assertEqual(atom['value'],api)
            self.assertEqual(atom['scope'],record['entry']['scope'])
            self.assertFalse(atom['api_identity']['public_api_inferred'])
            self.assertEqual(atom['coding_status'],'hold')

    def test_reference_symbols_never_create_api_contract(self):
        record=copy.deepcopy(self.records['EXP-AI-003'])
        record['document']['source_references'][0]['symbols'].append('NonexistentPublicFunction')
        result=self.service({'toy':record}).lookup_api('NonexistentPublicFunction',family='native_mechanism')
        self.assertEqual(result['results'],[])
        self.assertEqual(result['contract_status'],'RESEARCH_SCOPE_GAP')

    def test_local_export_same_file_and_versions_require_disambiguation(self):
        record=copy.deepcopy(self.records['EXP-COOK-002'])
        export=copy.deepcopy(record['entry']['api_contracts'][1])
        export['symbol']='SameName';export['visibility']='module export backed by local implementation'
        local=copy.deepcopy(export);local['visibility']='file-local function'
        record['entry']['api_contracts']=[export,local]
        service=self.service({'toy':record})
        result=service.lookup_api('SameName',family='native_mechanism',source_file=export['source_file'])
        self.assertTrue(result['disambiguation_required'])
        result=service.lookup_api('SameName',family='native_mechanism',identity_kind='file_local')
        self.assertEqual(result['results'][0]['value'],local)
        other=copy.deepcopy(record);other['document']['source_epoch']='future'
        result=self.service({'one':record,'two':other}).lookup_api('SameName',family='native_mechanism',identity_kind='file_local')
        self.assertTrue(result['disambiguation_required'])

    def test_repeated_same_identity_preserves_multiple_atoms(self):
        record=self.records['EXP-AI-003']
        result=self.service({'one':record,'two':record}).lookup_api('PriorityNode',family='native_mechanism')
        self.assertFalse(result['disambiguation_required'])
        self.assertEqual(result['total_identity_matches'],1)
        self.assertEqual(len(result['results']),2)

    def test_budget_charges_entire_wire_and_withholds_whole_atom(self):
        record=copy.deepcopy(self.records['EXP-AI-003'])
        record['entry']['api_contracts'][0]['preconditions']=['长'*30000]
        service=self.service({'toy':record})
        for maximum in (1000,4000,24000,64000):
            result=service.lookup_api('PriorityNode',family='native_mechanism',max_bytes=maximum)
            self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),maximum)
            self.assertEqual(result['results'],[])
        service.epoch_context=type('Epoch',(),{'metadata':lambda _: {'large':'e'*70000}})()
        result=service._lookup_mechanism_api('PriorityNode',5,'reviewer','decision',None,None,None,1000)
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),1000)
        self.assertTrue(result['withheld'])

    def test_source_environment_and_utf8_are_charged_without_atom_truncation(self):
        service=self.service()
        # Call the inner implementation to isolate serialization from epoch binding.
        service.epoch_context=type('Epoch',(),{'metadata':lambda _: {'source_epoch':'target','scope':'环'*1200}})()
        for maximum in (1000,4000,16000,24000):
            result=service._lookup_mechanism_api('PriorityNode',5,'reviewer','decision',None,None,None,maximum)
            self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),maximum)
            for atom in result['results']:
                self.assertEqual(atom['value'],self.records['EXP-AI-003']['entry']['api_contracts'][0])
                self.assertEqual(result['source_environment']['source_epoch'],'target')
                self.assertEqual(atom['source_epoch'],'759671')

    def test_invalid_paths_signatures_and_kinds_fail_closed(self):
        for kwargs in ({'source_file':'../outside.lua'},{'max_bytes':True},{'identity_kind':'public'}):
            with self.assertRaises(KBError):self.lookup('PriorityNode',**kwargs)
        with self.assertRaises(KBError):self.lookup('Growable:Pause(reason)')
        with self.assertRaises(KBError):self.lookup('countprefabs[prefab]')

if __name__=='__main__':unittest.main()

"""Generic navigation ranking fixtures, independent of evaluation query cases."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dst-kb-service'))
from dst_kb.public_catalog import CatalogRanker, PublicCatalog, at


def ranked(records,query,reverse=False):
    rows=[{'id':record['id'],'title':record['title'],'family':record.get('family','legacy')} for record in records]
    if reverse:rows.reverse()
    return [row['id'] for row in CatalogRanker(rows,{record['id']:record for record in records}).rank(query)]


class CatalogRankingTests(unittest.TestCase):
    def test_explicit_alias_beats_many_prose_mentions_across_families(self):
        for family in ('legacy','native_ai','native_core','native_mechanism'):
            with self.subTest(family=family):
                noise={'id':'A','title':'General notes','family':'legacy','body':'LoadWorkshop '*300}
                owner={'id':'Z','title':'Module loading','family':family,'aliases':['LoadWorkshop']}
                self.assertEqual(ranked([noise,owner],'LoadWorkshop')[0],'Z')

    def test_title_and_chinese_alias_outrank_incidental_body(self):
        noise={'id':'A','title':'杂项','body':'取消订阅 '*200}
        title={'id':'B','title':'取消订阅'}
        alias={'id':'C','title':'资源清理','aliases':['取消订阅']}
        self.assertEqual(set(ranked([noise,title,alias],'取消订阅')[:2]),{'B','C'})

    def test_exact_owner_qualified_api_beats_other_owner_and_bare_mentions(self):
        wrong={'id':'A','title':'Cancel','aliases':['Cancel'],'api_contracts':[{'symbol':'Receiver:Cancel'}]}
        prose={'id':'B','title':'Notes','body':'Sender:Cancel '*300}
        owner={'id':'Z','title':'Sender lifecycle','api_contracts':[{'symbol':'Sender:Cancel(ticket)'}]}
        for query in ('Sender:Cancel','Sender:Cancel(ticket)'):
            self.assertEqual(ranked([wrong,prose,owner],query)[0],'Z')

    def test_bare_method_keeps_multiple_declared_owners_ahead_of_body(self):
        records=[{'id':'A','title':'Discussion','body':'Abort '*500},
                 {'id':'B','title':'Sender','api_contracts':[{'symbol':'Sender:Abort'}]},
                 {'id':'C','title':'Receiver','api_contracts':[{'symbol':'Receiver:Abort'}]}]
        self.assertEqual(set(ranked(records,'Abort')[:2]),{'B','C'})

    def test_qualified_historical_keyword_is_explicit_navigation_identity(self):
        records=[{'id':'A','title':'Notes','body':'Controller:Detach '*200},
                 {'id':'Z','title':'Ownership','task_keywords':['Controller:Detach(handle)']}]
        self.assertEqual(ranked(records,'Controller:Detach')[0],'Z')

    def test_prose_is_not_promoted_to_an_owned_api(self):
        records=[{'id':'A','title':'Description','task_keywords':['Use Controller:Detach only after cleanup']},
                 {'id':'Z','title':'Other','api_contracts':[{'symbol':'Controller:Detach'}]}]
        self.assertEqual(ranked(records,'Controller:Detach')[0],'Z')

    def test_rare_content_and_length_normalization_reduce_generic_noise(self):
        records=[{'id':'A','title':'General','body':'cleanup '*300},
                 {'id':'B','title':'Specific','body':'cleanup redelivery'},
                 {'id':'C','title':'Other','body':'cleanup bookkeeping'}]
        self.assertEqual(ranked(records,'cleanup redelivery')[0],'B')

    def test_unknown_and_empty_queries_and_exact_historical_id(self):
        records=[{'id':'HIST-002','title':'Second','body':'common'},
                 {'id':'HIST-001','title':'First','body':'HIST-002 '*30}]
        self.assertEqual(ranked(records,''),['HIST-002','HIST-001'])
        self.assertEqual(ranked(records,'   '),['HIST-002','HIST-001'])
        self.assertEqual(ranked(records,'unrelated_unique_identifier'),[])
        self.assertEqual(ranked(records,'hist-002')[0],'HIST-002')

    def test_nonempty_ties_do_not_depend_on_catalog_history_order(self):
        records=[{'id':'Z','title':'Same','body':'common'},{'id':'A','title':'Same','body':'common'}]
        self.assertEqual(ranked(records,'common'),ranked(records,'common',reverse=True))


class CatalogOwnerPointerTests(unittest.TestCase):
    def test_small_budget_returns_only_valid_normalized_owner_pointer(self):
        server=PublicCatalog.__new__(PublicCatalog)
        entry={'id':'TOY','title':'Toy owner','scope':{'boundary':'authored fixture'},'unknowns':[],
               'claims':[{'id':'TOY-C','kind':'NSF','statement':'长'*2500,'evidence_refs':['TOY-R']}],
               'knowledge_status':'research','retrieval_status':'restricted','coding_status':'hold'}
        server.records={'TOY':entry}
        server.rows=[{'id':'TOY','title':'Toy owner','family':'native_mechanism'}]
        server.corrections=[]
        server.mechanisms={'TOY':{'entry':entry,'document':{'source_epoch':'toy','archive_sha256':'a'*64,'limitations':['未运行'],
            'source_references':[{'id':'TOY-R','source_file':'scripts/toy.lua','file_sha256':'b'*64,'range_sha256':'c'*64,'line_start':1,'line_end':1,'symbols':['Toy']}]},
            'registration':{'file':'research/toy.json','sha256':'d'*64,'review':{'file':'research/review.json','sha256':'e'*64}},'index':0}}
        result=server.call('read_public_entry',{'id':'TOY','purpose':'review','pointer':'/claims/0/statement','max_bytes':4000})
        self.assertFalse(result['whole_value_delivered'])
        self.assertEqual(result['pointer'],'/claims/0')
        self.assertEqual(result['child_pointers'],['/claims/0'])
        self.assertLessEqual(len(json.dumps(result,ensure_ascii=False).encode()),4000)
        for pointer in result['child_pointers']:
            self.assertEqual(at(entry,pointer),entry['claims'][0])
            expanded=server.call('read_public_entry',{'id':'TOY','purpose':'review','pointer':pointer,'max_bytes':24000})
            self.assertTrue(expanded['whole_value_delivered'])
            self.assertEqual(expanded['public_value'],entry['claims'][0])
            self.assertTrue(expanded['research_context']['source_references'])


if __name__=='__main__':unittest.main(verbosity=2)

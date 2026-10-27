"""Reviewed cooking/growth intake: identities, immutable evidence and HOLD."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dst-kb-service'))
from dst_kb import family_registry, native_mechanism
from dst_kb.public_catalog import PublicCatalog

EXPECTED={
    'cooking':('39f19e255b6daa103177ef8d3bea5cf4d556beee4efe1509ee95dfdd408c323b',
               {'EXP-COOK-'+str(i).zfill(3) for i in range(1,8)}),
    'growth':('06fcb280862dc556bd35f7d7317111c7b633a2c72c290ef1e0725a80299ec1b6',
              {'EXP-GROW-'+str(i).zfill(3) for i in range(1,5)}),
}


class ReviewedBatchExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=family_registry.load(ROOT/'knowledge')
        cls.records=native_mechanism.load(ROOT/'knowledge',cls.registry)
        cls.catalog=PublicCatalog(ROOT)

    @classmethod
    def tearDownClass(cls):cls.catalog.close()

    def test_new_topics_match_independently_reviewed_document_hashes(self):
        family=next(row for row in self.registry['families'] if row['name']=='native_mechanism')
        for topic,(digest,ids) in EXPECTED.items():
            row=next(item for item in family['documents'] if item['topic']==topic)
            self.assertEqual(row['sha256'],digest)
            self.assertEqual(set(row['entry_ids']),ids)
            review=family_registry.read_committed(ROOT/'knowledge',row['review']['file'],row['review']['sha256'])
            self.assertEqual(review['candidate_sha256'],digest)
            self.assertIs(review['runtime_verified'],False)
            self.assertTrue(row['review']['dependencies'])

    def test_previous_first_batch_and_new_batch_ids_remain_registered(self):
        first={'EXP-AI-'+str(i).zfill(3) for i in range(1,8)}|{'EXP-WG-'+str(i).zfill(3) for i in range(1,6)}
        expanded=first|set().union(*(item[1] for item in EXPECTED.values()))
        self.assertTrue(expanded.issubset(self.records))
        counts=family_registry.counts(self.registry)
        self.assertEqual({key:counts[key] for key in ('legacy','native_ai','native_core')},{'legacy':64,'native_ai':13,'native_core':110})
        self.assertEqual(counts['total'],sum(counts[key] for key in counts if key!='total'))

    def test_every_new_entry_preserves_hold_and_atom_context_closure(self):
        for _,ids in EXPECTED.values():
            for id in ids:
                record=self.records[id]
                entry=record['entry']
                self.assertEqual({k:entry[k] for k in native_mechanism.STATES},native_mechanism.STATES)
                result=self.catalog.call('read_public_entry',{'id':id,'purpose':'review','pointer':'/claims/0/statement','max_bytes':24000})
                self.assertTrue(result['whole_value_delivered'],id)
                self.assertEqual(result['public_value'],entry['claims'][0])
                context=result['research_context']
                self.assertEqual(context['scope'],entry['scope'])
                self.assertEqual(context['limitations'],record['document']['limitations'])
                self.assertEqual({ref['id'] for ref in context['source_references']},set(entry['claims'][0]['evidence_refs']))
                self.assertIs(context['runtime_validation_performed'],False)


if __name__=='__main__':unittest.main(verbosity=2)

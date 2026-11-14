"""Public default discovery, identity boundaries and real source-free entrypoints."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
sys.path.insert(0, str(ROOT))
from dst_kb.public_reader import PublicReader
from dst_kb.mcp_server import Server
from dst_kb.config import KBError
from dst_kb import review_reader

QUESTIONS = [
    ('做一顶装备后有夜视、会耗燃料、可以补充燃料的帽子', 'EXP-CHAIN-GEAR-001'),
    ('自定义法术按鼠标地面施放', 'EXP-CHAIN-SPELL-001'),
    ('角色死亡复活后定时效果如何清理', 'guide:references/characters-brains-stategraphs.md'),
    ('建筑部署收起保存耐久', 'EXP-CHAIN-DEPLOY-001'),
    ('生物两种形态变身恢复', 'EXP-CHAIN-STAGE-001'),
    ('海钓鱼群生成', 'EXP-FISH-001'),
    ('物品容器保存和恢复', 'FACT-DST-002'),
    ('RPC 客户端服务端同步', 'guide:references/networking-rpc.md'),
    ('角色动画bank build symbol', 'guide:references/assets-animation.md'),
    ('锅料理添加配方', 'guide:references/cooker-dishes.md'),
    ('农作物水肥压力', 'EXP-FARM-002'),
    ('组件移除取消定时任务', 'EXP-LIFE-006'),
]


class PublicReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = PublicReader(ROOT)

    def test_all_four_families_read_without_preparing_sources(self):
        catalog = json.loads((ROOT / 'knowledge/CATALOG.json').read_bytes())
        self.assertCountEqual([r['id'] for r in self.reader.rows],
                              [r['id'] for r in catalog['entries']])
        self.assertEqual(len({r['family'] for r in self.reader.rows}), 4)
        with patch('prepare_sources.prepared_runtime', side_effect=AssertionError('must not prepare')):
            for row in self.reader.rows:
                result = self.reader.read(row['id'], maximum=64000)
                self.assertTrue(result['objects'], row['id'])
                self.assertLessEqual(review_reader.size(result), 64000)
                self.assertFalse(result['coding_admission_granted'])

    def test_natural_queries_deliver_body_with_scope(self):
        for question, identifier in QUESTIONS:
            with self.subTest(query=question):
                result = self.reader.call('search_kb', {'query': question, 'top_k': 3})
                selected = next(r for r in result['results'] if r['entry']['id'] == identifier)
                body = selected['reading']
                self.assertTrue(body['objects'])
                self.assertTrue(body['scope'])
                self.assertTrue(any(len(json.dumps(o['value'], ensure_ascii=False)) > 20 for o in body['objects']))
                self.assertLessEqual(review_reader.size(result), 64000)

    def test_server_schema_and_dispatch_default_to_public_reader(self):
        server = Server()
        self.addCleanup(server.close)
        for name in ('search_kb', 'get_entry', 'lookup_api'):
            spec = next(t for t in server.tools if t['name'] == name)
            self.assertEqual(spec['inputSchema']['properties']['projection']['default'], 'reviewer')
        with patch('prepare_sources.prepared_runtime', side_effect=AssertionError('must not prepare')):
            self.assertTrue(server.call('search_kb', {'query': QUESTIONS[0][0]})['results'][0]['reading']['objects'])

    def test_legacy_coding_still_passes_only_explicit_arguments(self):
        with patch.object(self.reader, '_pass_legacy', return_value={'old': True}) as legacy:
            args = {'query': 'hat', 'projection': 'coding'}
            self.assertEqual(self.reader.call('search_kb', args), {'old': True})
            legacy.assert_called_once_with('search_kb', args)

    def test_server_explicit_epoch_and_coding_keep_original_config(self):
        with patch('dst_kb.mcp_server.resolve_epoch', return_value=None) as resolve, \
                patch('dst_kb.mcp_server.Service') as factory:
            factory.return_value.search_kb.return_value = {'legacy': True}
            server = Server('explicit-config')
            try:
                self.assertEqual(server.call('search_kb', {'query': 'x', 'mode': 'coding'}), {'legacy': True})
                resolve.assert_called_with('explicit-config', None)
                server.call('search_kb', {'query': 'x', 'source_epoch': '759671'})
                resolve.assert_called_with('explicit-config', '759671')
            finally:
                server.close()

    def test_filters_and_guide_continuation_preserve_scope(self):
        result = self.reader.call('search_kb', {'query': '保存', 'families': ['native_mechanism'], 'coding_statuses': ['hold']})
        self.assertTrue(result['results'])
        self.assertTrue(all(r['entry']['family'] == 'native_mechanism' for r in result['results']))
        with self.assertRaises(KBError) as caught:
            self.reader.call('search_kb', {'query': '保存', 'sides': ['server']})
        self.assertEqual(caught.exception.code, 'UNSUPPORTED_PUBLIC_FILTER')
        identifier = 'guide:references/complex-mod-architecture.md'
        result = self.reader.read(identifier, maximum=5000)
        objects = list(result['objects'])
        seen = set()
        while result['continuation']:
            args = result['continuation']['arguments']
            self.assertNotIn(args['cursor'], seen)
            seen.add(args['cursor'])
            result = self.reader.call(result['continuation']['tool'], args)
            self.assertLessEqual(review_reader.size(result), 64000)
            objects.extend(result['objects'])
        paragraphs = [o['value'] for o in objects if o['pointer'].startswith('/sections/')]
        self.assertEqual(paragraphs, self.reader.records[identifier]['sections'])

    def test_selected_owner_retains_legacy_boundaries_and_core_corrections(self):
        for identifier in ('PATTERN-NET-001', 'TEST-NET-001'):
            record = self.reader.records[identifier]
            result = self.reader.read(identifier, '/details')
            self.assertEqual(result['detail_boundaries'], record['details'])
        result = self.reader.read('NC-N004-FINAL-01', '/claims/0/statement', maximum=64000)
        self.assertEqual(result['pointer'], '/claims/0')
        self.assertEqual(result['correction_refs'], self.reader.records['NC-N004-FINAL-01']['correction_refs'])

    def test_module_export_and_bare_identity_groups(self):
        exact = self.reader.lookup({'symbol': 'require("map/object_layout").LayoutForDefinition'})
        self.assertTrue(exact['results'])
        self.assertTrue(all(r['symbol'] == exact['symbol'] for r in exact['results']))
        bare = self.reader.lookup({'symbol': 'Get', 'top_k': 30, 'max_bytes': 64000})
        self.assertGreater(bare['total_groups'], 1)
        for group in bare['groups']:
            self.assertIn('owner', group)
            self.assertIn('source_file', group)
            self.assertIn('visibility', group)
        wrong = self.reader.lookup({'symbol': 'Fueled:TakeFuelItem', 'owner': 'Other'})
        self.assertFalse(wrong['results'])
        for path in ('../scripts/components/fueled.lua', 'scripts/../secrets.lua', 'C:/secret.lua', 'scripts\\a.lua'):
            with self.assertRaises(KBError):
                self.reader.lookup({'symbol': 'Get', 'source_file': path})

    def test_total_payload_budget_and_cursor_guard(self):
        result = self.reader.call('search_kb', {'query': '装备 保存 恢复 状态', 'top_k': 30})
        self.assertLessEqual(review_reader.size(result), 64000)
        self.assertLessEqual(review_reader.size(self.reader.lookup({'symbol': 'OnSave', 'top_k': 30, 'max_bytes': 1000})), 1000)
        first = self.reader.read('NC-N004-FINAL-01', maximum=8000)
        self.assertIsNotNone(first['continuation'])
        args = first['continuation']['arguments']
        with self.assertRaises(KBError) as caught:
            self.reader.read('NC-N004-FINAL-02', args['pointer'], args['cursor'], args['max_bytes'])
        self.assertEqual(caught.exception.code, 'INVALID_CURSOR')
        for identifier in ('guide:../LICENSE', 'guide:references/../SKILL.md', 'guide:run_kb.py'):
            with self.assertRaises(KBError): self.reader.read(identifier)

    def test_invalid_independent_evidence_does_not_hide_public_body(self):
        with patch('dst_kb.evidence_snapshot.active_assessment', side_effect=KBError('SNAPSHOT_INVALID', 'hash mismatch')):
            result = self.reader.read('EXP-CHAIN-GEAR-001', '/claims/0')
        self.assertTrue(result['objects'])
        self.assertEqual(result['source_input_assessment']['status'], 'UNAVAILABLE')
        self.assertFalse(result['source_input_assessment']['evidence_expansion_allowed'])

    def test_snapshot_verified_once_per_request_then_revalidated(self):
        with patch('dst_kb.evidence_snapshot.active_assessment', return_value=None) as assess:
            self.reader.call('search_kb', {'query': QUESTIONS[0][0], 'top_k': 3})
            self.assertEqual(assess.call_count, 1)
            self.reader.call('search_kb', {'query': QUESTIONS[0][0], 'top_k': 3})
            self.assertEqual(assess.call_count, 2)

    def test_large_partial_source_inventory_cannot_displace_body(self):
        observed = {f'scripts/prefabs/example_{i}.lua': 'f' * 64 for i in range(2000)}
        state = {'status': 'PARTIAL', 'snapshot_id': 'a' * 64,
            'sources': [{'archive_sha256': 'b' * 64, 'kind': 'ZIP', 'source_input_index': 0,
                         'observed_files': observed}],
            'references': [{'reference_id': 'MISSING-REF', 'status': 'MISSING',
                            'affected_entry_ids': ['EXP-GEAR-001']}]}
        with patch('dst_kb.evidence_snapshot.active_assessment', return_value=state):
            result = self.reader.call('search_kb', {'query': QUESTIONS[0][0], 'top_k': 3})
        self.assertTrue(all(r['reading'] and r['reading']['objects'] for r in result['results']))
        self.assertLessEqual(review_reader.size(result), 64000)
        assessment = result['results'][0]['reading']['source_input_assessment']
        self.assertEqual(assessment['status'], 'PARTIAL')
        self.assertEqual(assessment['snapshot_status'], 'PARTIAL')
        self.assertEqual(assessment['references'][0]['status'], 'MISSING')
        self.assertEqual(assessment['sources'][0]['observed_file_count'], 2000)
        self.assertEqual(assessment['sources'][0]['observed_files_sha256'], review_reader.digest(observed))
        self.assertNotIn('observed_files', assessment['sources'][0])
        self.assertEqual(assessment['sources'][0]['archive_sha256'], 'b' * 64)
        self.assertEqual(assessment['source_details']['snapshot_id'], 'a' * 64)

    def test_real_source_free_stdio_and_cli(self):
        requests = [{'jsonrpc': '2.0', 'id': 0, 'method': 'initialize', 'params': {}}]
        requests += [{'jsonrpc': '2.0', 'id': i + 1, 'method': 'tools/call', 'params': {
            'name': 'search_kb', 'arguments': {'query': question, 'top_k': 3}}} for i, (question, _) in enumerate(QUESTIONS)]
        proc = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'run_kb.py'), 'serve'],
            input='\n'.join(json.dumps(r) for r in requests) + '\n', capture_output=True, text=True, encoding='utf-8', timeout=90)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        responses = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual(len(responses), 13)
        for response in responses[1:]:
            self.assertFalse(response['result']['isError'])
            self.assertTrue(any(r['reading'] and r['reading']['objects'] for r in response['result']['structuredContent']['results']))
        cli = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'run_kb.py'), 'review', 'EXP-CHAIN-GEAR-001', '--pointer', '/claims/0'], capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertTrue(json.loads(cli.stdout)['objects'])

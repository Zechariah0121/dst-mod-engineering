"""Small 0.3 public-protocol development regression, using a public64 fixture.

This is not a new knowledge evaluation, a full-187 preparation qualification,
an autonomous-agent acceptance, or a DST game/runtime test.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SERVICE = Path(os.environ.get('DST_KB_PROTOCOL_SERVICE_ROOT', Path(__file__).resolve().parents[1])).resolve()
PACKAGE = SERVICE.parent
sys.path.insert(0, str(SERVICE))

from dst_kb.mcp_server import Server
from dst_kb.delivery_wire import expand_l1_metadata

TOOLS = {'search_kb', 'get_entry', 'get_related', 'get_klei_facts', 'get_tests',
         'get_context_bundle', 'lookup_api', 'resolve_evidence', 'validate_kb'}
EPOCH = 'public64-protocol-fixture'
FACT = 'FACT-DST-001'
TASK = '核对 EntityScript 的 GetPersistData / SetPersistData 如何遍历 components 并调用 OnSave / OnLoad。'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {path.relative_to(root).as_posix(): checksum(path)
            for path in root.rglob('*') if path.is_file()}


def pointer(value, path):
    if not path:
        return value
    for part in path[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def fixture_source():
    explicit = os.environ.get('DST_KB_PROTOCOL_FIXTURE')
    candidates = [Path(explicit)] if explicit else [PACKAGE / 'knowledge']
    for path in candidates:
        if (path / 'data/entries.json').is_file():
            records = read(path / 'data/entries.json')['entries']
            if len(records) != 64:
                raise AssertionError('Protocol fixture requires the unchanged 64 legacy records')
            return path.resolve()
    raise AssertionError('Protocol fixture requires the package knowledge root or DST_KB_PROTOCOL_FIXTURE')


def derive_legacy_fixture(source, destination):
    # Derive a protocol-only fixture in test scratch from the single canonical
    # root. Native source templates are deliberately absent from this fixture.
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        'native001', 'nativecore', 'research', 'history', '__pycache__'))
    catalog = read(destination / 'CATALOG.json')
    catalog['entries'] = [row for row in catalog['entries'] if row['family'] == 'legacy']
    catalog['counts'] = {'total': len(catalog['entries']), 'legacy': len(catalog['entries']),
                         'native_ai': 0, 'native_core': 0}
    write(destination / 'CATALOG.json', catalog)
    manifest = read(destination / 'PACKAGE-MANIFEST.json')
    manifest['files'] = [{'path': path.relative_to(destination).as_posix(),
                          'bytes': path.stat().st_size, 'sha256': checksum(path)}
                         for path in sorted(destination.rglob('*'))
                         if path.is_file() and path.name != 'PACKAGE-MANIFEST.json']
    write(destination / 'PACKAGE-MANIFEST.json', manifest)


def initialized(server):
    return server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                          'params': {'protocolVersion': '2025-06-18', 'capabilities': {},
                                     'clientInfo': {'name': 'public-protocol-development', 'version': '1'}}})


def call(server, name, arguments):
    return server.handle({'jsonrpc': '2.0', 'id': 10, 'method': 'tools/call',
                          'params': {'name': name, 'arguments': arguments}})


class PublicProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = fixture_source()
        cls.source_before = inventory(cls.source)
        # Keep all writes in the caller-selected test work area, never the
        # package knowledge, service cache, global configuration, or game tree.
        parent = os.environ.get('DST_KB_PROTOCOL_TEMP_PARENT')
        cls.temporary = tempfile.TemporaryDirectory(prefix='public-protocol-', dir=parent)
        cls.work = Path(cls.temporary.name)
        cls.kb = cls.work / 'public64'
        derive_legacy_fixture(cls.source, cls.kb)
        cls.records = {record['id']: record for record in read(cls.kb / 'data/entries.json')['entries']}
        assets = cls.work / 'assets'
        write(assets / 'contract.json', {'records': {}})
        write(assets / 'identity.json', {'schema': 'derived-source-identity-index/1',
              'behavior_or_scope_modified': False, 'runtime_source_dependency': False, 'records': {}})
        write(assets / 'source-manifest.json', {'schema': 'synthetic-public64-test-source-manifest/1', 'files': {}})
        def committed(path):
            return {'path': str(path), 'sha256': checksum(path)}
        catalog = {'schema_version': 'dst-source-epochs/1', 'default_source_epoch': EPOCH,
            'epochs': {EPOCH: {'aliases': [], 'knowledge_root': str(cls.kb),
                'index_path': str(cls.work / 'cache/index.sqlite3'),
                'knowledge_manifest': committed(cls.kb / 'PACKAGE-MANIFEST.json'),
                'contract_map': committed(assets / 'contract.json'),
                'source_identity_map': committed(assets / 'identity.json'),
                'source_manifests': [committed(assets / 'source-manifest.json')],
                'source_environment_identity': {'synthetic_fixture': True,
                    'game_version': 'UNKNOWN', 'runtime_verified': False}}}}
        write(cls.work / 'source-epochs.json', catalog)
        cls.config = cls.work / 'config.json'
        write(cls.config, {'source_epochs_path': 'source-epochs.json', 'default_source_epoch': EPOCH})
        cls.server = Server(cls.config)
        initialized(cls.server)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.server.close()
            if inventory(cls.source) != cls.source_before:
                raise AssertionError('The public reference fixture was modified')
        finally:
            cls.temporary.cleanup()

    def payload(self, name, arguments):
        response = call(self.server, name, arguments)
        self.assertFalse(response['result']['isError'], response)
        value = response['result']['structuredContent']
        self.assertEqual(json.loads(response['result']['content'][0]['text']), value)
        return value

    def test_stdio_initialize_and_nine_tool_inventory(self):
        messages = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'initialize', 'params': {
                'protocolVersion': '2025-06-18', 'capabilities': {},
                'clientInfo': {'name': 'public-protocol-development', 'version': '1'}}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/list', 'params': {}},
            {'jsonrpc': '2.0', 'id': 4, 'method': 'ping', 'params': {}},
        ]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for key in ('DST_KB_PATH', 'DST_KB_INDEX', 'DST_KB_CONFIG'):
            env.pop(key, None)
        run = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SERVICE / 'dst_kb_cli.py'),
                              '--config', str(self.config), 'serve'],
            input=''.join(json.dumps(message) + '\n' for message in messages),
            capture_output=True, text=True, encoding='utf-8', env=env, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        replies = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([reply['id'] for reply in replies], [1, 2, 3, 4])
        self.assertEqual(replies[0]['error']['code'], -32000)
        self.assertEqual(replies[1]['result']['protocolVersion'], '2025-06-18')
        self.assertEqual(replies[1]['result']['serverInfo']['version'], '0.3.1')
        specs = {item['name']: item for item in replies[2]['result']['tools']}
        self.assertEqual(set(specs), TOOLS)
        for name, spec in specs.items():
            with self.subTest(tool=name):
                self.assertIn('source_epoch', spec['inputSchema']['properties'])
                self.assertFalse(spec['inputSchema']['additionalProperties'])
                self.assertTrue(spec['annotations']['readOnlyHint'])
                self.assertFalse(spec['annotations']['destructiveHint'])
        self.assertEqual(specs['get_entry']['inputSchema']['properties']['projection']['default'], 'coding')
        self.assertEqual(specs['lookup_api']['inputSchema']['properties']['projection']['default'], 'reviewer')
        self.assertEqual(replies[3]['result'], {})

    def test_explicit_decision_view_preserves_exact_fact_and_original_scope(self):
        value = self.payload('get_entry', {'id': FACT, 'projection': 'reviewer',
                             'view': 'decision', 'source_epoch': EPOCH})
        self.assertEqual(value['source_environment']['source_epoch'], EPOCH)
        self.assertEqual(value['view'], 'decision')
        card = expand_l1_metadata(value['entry'])
        self.assertEqual(card['id'], FACT)
        atoms = {atom['record_pointer']: atom['statement'] for atom in card['decision']}
        self.assertEqual(atoms['/details/observed_behaviour'], self.records[FACT]['details']['observed_behaviour'])
        self.assertIn('OnSave', atoms['/details/observed_behaviour'])
        self.assertIn('OnLoad', atoms['/details/observed_behaviour'])
        self.assertIn(self.records[FACT]['scope_text'], json.dumps(card['source_scope'], ensure_ascii=False))
        self.assertTrue(all(atom['kind'].startswith('LEGACY_') or atom['kind'] in ('REC', 'EI')
                            for atom in card['decision']))

    def test_omitted_view_retains_legacy_exact_record_shape(self):
        value = self.payload('get_entry', {'id': FACT, 'source_epoch': EPOCH})
        self.assertEqual(value['entry'], self.records[FACT])
        self.assertIn('source_registry', value)
        self.assertIn('correction_warnings', value)
        self.assertNotIn('source_environment', value)

    def test_invalid_schema_arguments_fail_before_any_service_is_opened(self):
        absent = self.work / 'absent-config.json'
        isolated = Server(absent)
        try:
            initialized(isolated)
            for name, arguments in [
                ('get_entry', {}), ('search_kb', {'top_k': True}),
                ('search_kb', {'query': 'x', 'unknown': 1}),
                ('get_entry', {'id': FACT, 'source_file': 'scripts/a.lua'}),
                ('get_context_bundle', {'task_description': TASK, 'budget': 'unbounded'}),
                ('resolve_evidence', {'id': FACT, 'reference_index': -1}),
            ]:
                with self.subTest(tool=name, arguments=arguments):
                    response = call(isolated, name, arguments)['result']
                    self.assertTrue(response['isError'])
                    self.assertEqual(response['structuredContent']['error']['code'], 'INVALID_ARGUMENT')
                    self.assertEqual(isolated.services, {})
        finally:
            isolated.close()

    def test_unknown_epoch_id_and_escaping_lookup_path_fail_closed(self):
        cases = [
            ('get_entry', {'id': FACT, 'source_epoch': 'unknown-epoch'}, 'INVALID_SOURCE_EPOCH'),
            ('get_entry', {'id': '../../private-config', 'source_epoch': EPOCH}, 'INVALID_ID'),
            ('lookup_api', {'symbol': 'Combat:GetAttacked', 'source_file': '../outside.lua',
                            'source_epoch': EPOCH}, 'INVALID_ARGUMENT'),
        ]
        for name, arguments, expected in cases:
            with self.subTest(tool=name, expected=expected):
                result = call(self.server, name, arguments)['result']
                self.assertTrue(result['isError'])
                self.assertEqual(result['structuredContent']['error']['code'], expected)

    def test_complete_utf8_bundle_budget_and_literal_atoms(self):
        # Isolate packing from old-public64 retrieval admission/ranking. The
        # candidate is the exact real get_entry result, not invented knowledge.
        # Only the search seam is mocked; public dispatch, budget packing,
        # source-environment accounting and serialized literal values are real.
        card = self.payload('get_entry', {'id': FACT, 'projection': 'reviewer',
                            'view': 'decision', 'source_epoch': EPOCH})['entry']
        candidate = {'results': [card], 'kb_version': self.records[FACT]['version'],
                     'results_truncated': False}
        service = self.server.service
        nonempty = False
        for budget, count, maximum in [('compact', 5, 16000), ('normal', 8, 32000), ('deep', 12, 64000)]:
            with self.subTest(budget=budget), patch.object(service, 'search_kb', return_value=candidate):
                value = self.payload('get_context_bundle', {'task_description': TASK, 'mode': 'review',
                    'budget': budget, 'projection': 'reviewer', 'view': 'decision', 'source_epoch': EPOCH})
                self.assertEqual(value['max_payload_bytes'], maximum)
                self.assertEqual(value['budget_applies_to'], 'complete_structured_payload_utf8')
                self.assertLessEqual(len(json.dumps(value, ensure_ascii=False).encode('utf-8')), maximum)
                self.assertLessEqual(len(value['entries']), count)
                self.assertEqual(len({entry['id'] for entry in value['entries']}), len(value['entries']))
                self.assertEqual(value['source_environment']['source_epoch'], EPOCH)
                self.assertIsInstance(value['knowledge_gaps'], list)
                for wire in value['entries']:
                    card = expand_l1_metadata(wire)
                    for atom in card.get('decision', []):
                        nonempty = True
                        self.assertEqual(atom['statement'], pointer(self.records[card['id']], atom['record_pointer']))
        self.assertTrue(nonempty, 'Budget checks must actually exercise at least one delivered literal atom')

    def test_unprepared_templates_do_not_start_or_read_a_service(self):
        package = self.work / 'unprepared-package'
        package.mkdir()
        for name in ('run_kb.py', 'prepare_sources.py'):
            source = PACKAGE / name
            self.assertTrue(source.is_file(), 'Public launcher missing: ' + name)
            shutil.copyfile(source, package / name)
        write(package / 'knowledge/evidence.json', {'source_excerpt': {'$dst_source_payload_slot': 'synthetic-slot'}})
        before = (package / 'knowledge/evidence.json').read_bytes()
        sentinel = package / 'service-was-started'
        service = package / 'dst-kb-service/dst_kb_cli.py'
        service.parent.mkdir()
        service.write_text('from pathlib import Path\nPath(__file__).parents[1].joinpath("service-was-started").write_text("bad")\n', encoding='utf-8')
        run = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(package / 'run_kb.py'), '--mode', 'full', 'serve'],
                             capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertEqual(run.stdout, '')
        result = json.loads(run.stderr)
        self.assertEqual(result['error']['code'], 'SOURCES_NOT_PREPARED')
        self.assertFalse(result['service_started'])
        self.assertIn('prepare_sources.py', result['error']['message'])
        self.assertFalse(sentinel.exists())
        self.assertFalse((package / 'cache').exists())
        self.assertEqual((package / 'knowledge/evidence.json').read_bytes(), before)

    def test_utf8_environment_pressure_is_budgeted_without_silent_trimming(self):
        # Synthetic environment metadata supplies byte pressure without changing
        # any fact, role, source evidence or product threshold. 6000 Chinese
        # characters fit a 16000-character limit, but exceed 16000 UTF-8 bytes.
        folder = self.work / 'utf8-pressure'
        catalog = read(self.work / 'source-epochs.json')
        epoch = catalog['epochs'][EPOCH]
        epoch['index_path'] = str(folder / 'index.sqlite3')
        pressure = '汉' * 6000
        epoch['source_environment_identity']['synthetic_utf8_pressure'] = pressure
        write(folder / 'catalog.json', catalog)
        config = folder / 'config.json'
        write(config, {'source_epochs_path': 'catalog.json', 'default_source_epoch': EPOCH})
        server = Server(config)
        try:
            initialized(server)
            reply = call(server, 'get_entry', {'id': FACT, 'projection': 'reviewer',
                         'view': 'decision', 'source_epoch': EPOCH})['result']
            self.assertFalse(reply['isError'], reply)
            candidate = {'results': [reply['structuredContent']['entry']],
                         'kb_version': self.records[FACT]['version'], 'results_truncated': False}
            arguments = {'task_description': TASK, 'mode': 'review', 'projection': 'reviewer',
                         'view': 'decision', 'source_epoch': EPOCH}
            with patch.object(server.service, 'search_kb', return_value=candidate):
                compact = call(server, 'get_context_bundle', dict(arguments, budget='compact'))['result']
                self.assertTrue(compact['isError'])
                self.assertEqual(compact['structuredContent']['error']['code'], 'PAYLOAD_BUDGET_EXCEEDED')
                normal = call(server, 'get_context_bundle', dict(arguments, budget='normal'))['result']
                self.assertFalse(normal['isError'], normal)
            value = normal['structuredContent']
            self.assertTrue(value['entries'])
            self.assertEqual(value['source_environment']['source_environment_identity']['synthetic_utf8_pressure'], pressure)
            self.assertLessEqual(len(json.dumps(value, ensure_ascii=False).encode('utf-8')), 32000)
        finally:
            server.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)

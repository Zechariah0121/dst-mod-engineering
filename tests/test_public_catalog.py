"""Exercise source-free navigation without weakening full-source admission."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
sys.path.insert(0, str(ROOT))
from dst_kb.public_catalog import PublicCatalog
from dst_kb.config import KBError
from prepare_sources import PreparationError

spec = importlib.util.spec_from_file_location('catalog_launcher_test', ROOT / 'run_kb.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class PublicCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = PublicCatalog(ROOT)

    @classmethod
    def tearDownClass(cls):
        cls.server.close()

    def test_search_is_metadata_only_and_keeps_hold(self):
        result = self.server.call('search_catalog', {'query': 'Perishable:Perish'})
        self.assertTrue(result['results'])
        self.assertEqual(result['service_mode'], 'public_catalog')
        self.assertFalse(result['coding_context_delivered'])
        self.assertNotIn('decision', result['results'][0])
        core = next(row for row in self.server.rows if row['family'] == 'native_core')
        exact = self.server.call('search_catalog', {'query': core['id']})['results'][0]
        self.assertEqual(exact['id'], core['id'])
        self.assertEqual(exact['coding_status'], 'hold')

    def test_review_requires_explicit_purpose_and_preserves_correction(self):
        with self.assertRaises(KBError):
            self.server.call('read_public_entry', {'id': 'CORRECTION-CASE001-001'})
        result = self.server.call('read_public_entry', {'id': 'CORRECTION-CASE001-001', 'purpose': 'review'})
        self.assertTrue(result['whole_value_delivered'])
        self.assertEqual(result['public_value']['id'], 'CORRECTION-CASE001-001')
        self.assertEqual(result['historical_claim_corrections'][0]['status'], 'superseded')
        self.assertFalse(result['runtime_validation_performed'])

    def test_large_review_withholds_whole_value_and_pointer_selects_exact_text(self):
        row = next(row for row in self.server.rows if row['family'] == 'native_core')
        result = self.server.call('read_public_entry', {'id': row['id'], 'purpose': 'review', 'max_bytes': 4000})
        self.assertFalse(result['whole_value_delivered'])
        self.assertNotIn('public_value', result)
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False).encode('utf-8')), 4000)
        selected = self.server.call('read_public_entry', {'id': row['id'], 'purpose': 'review', 'pointer': '/title'})
        self.assertEqual(selected['public_value'], self.server.records[row['id']]['title'])
        self.assertEqual(selected['entry']['coding_status'], 'hold')

    def test_invalid_pointer_and_full_tool_cannot_bypass_catalog(self):
        for pointer in ['../other', '/claims/-1', '/invalid~2key']:
            with self.assertRaises(KBError):
                self.server.call('read_public_entry', {'id': 'FACT-DST-001', 'purpose': 'review', 'pointer': pointer})
        for name in ('get_context_bundle', 'resolve_evidence', 'validate_kb'):
            with self.assertRaises(KBError) as caught:
                self.server.call(name, {})
            self.assertEqual(caught.exception.code, 'FULL_SERVICE_REQUIRED')

    def test_subpointer_keeps_its_record_corrections_and_negative_boundaries(self):
        identifier = 'NC-N002-FINAL-07'
        result = self.server.call('read_public_entry', {'id': identifier, 'purpose': 'review', 'pointer': '/claims/0'})
        self.assertTrue(result['whole_value_delivered'])
        self.assertEqual(result['correction_refs'], self.server.records[identifier]['correction_refs'])
        self.assertEqual(len(result['correction_refs']), 2)
        self.assertEqual(result['record_boundaries']['does_not_prove'], self.server.records[identifier]['does_not_prove'])
        native = self.server.call('read_public_entry', {'id': 'AI-N001-01', 'purpose': 'review', 'pointer': '/native_fact'})
        self.assertTrue(native['whole_value_delivered'])
        self.assertEqual(native['record_boundaries']['does_not_mean'], self.server.records['AI-N001-01']['does_not_mean'])

    def test_manifest_rejects_changed_catalog_before_navigation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            kb = root / 'knowledge'
            kb.mkdir()
            raw = b'{"entries": []}'
            (kb / 'CATALOG.json').write_bytes(raw + b' ')
            (kb / 'PACKAGE-MANIFEST.json').write_text(json.dumps({'files': [{'path': 'CATALOG.json',
                'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}]}), encoding='utf-8')
            with self.assertRaises(KBError) as caught:
                PublicCatalog(root)
            self.assertEqual(caught.exception.code, 'PUBLIC_PACKAGE_CHANGED')

    def test_real_stdio_unprepared_package_exposes_only_catalog_tools(self):
        requests = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'search_catalog', 'arguments': {'query': 'World Manager'}}},
        ]
        process = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'run_kb.py'), 'serve', '--mode', 'catalog'],
            input='\n'.join(json.dumps(row) for row in requests) + '\n', capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertIn('PUBLIC CATALOG MODE', responses[0]['result']['instructions'])
        self.assertEqual({tool['name'] for tool in responses[1]['result']['tools']}, {'search_catalog', 'read_public_entry'})
        self.assertTrue(responses[2]['result']['structuredContent']['results'])

    def test_auto_fallback_only_when_no_activation_and_full_stays_strict(self):
        from dst_kb import public_catalog
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            knowledge = root / 'knowledge'
            knowledge.mkdir()
            raw = b'{"entries": []}'
            (knowledge / 'CATALOG.json').write_bytes(raw)
            (knowledge / 'PACKAGE-MANIFEST.json').write_text(json.dumps({
                'schema_version': 'dst-public-package-manifest/1', 'files': [{
                'path': 'CATALOG.json', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}]}), encoding='utf-8')
            error = PreparationError('SOURCES_NOT_PREPARED', 'missing')
            with patch.object(launcher, 'ROOT', root), patch.object(launcher, 'prepared_runtime', side_effect=error), \
                    patch.object(public_catalog, 'main', return_value=0) as catalog, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(launcher.main(['status']), 0)
                catalog.assert_called_once()
                catalog.reset_mock()
                self.assertEqual(launcher.main(['status', '--mode', 'full']), 2)
                catalog.assert_not_called()
                activation = root / 'cache/runtime/retrieval-config.json'
                activation.parent.mkdir(parents=True)
                activation.write_text('{}', encoding='utf-8')
                self.assertEqual(launcher.main(['status']), 2)
                catalog.assert_not_called()

    def test_cache_corruption_never_silently_downgrades(self):
        from dst_kb import public_catalog
        for code in ('RUNTIME_CHANGED', 'INVALID_PATH', 'PACKAGE_INCOMPLETE'):
            with patch.object(launcher, 'prepared_runtime', side_effect=PreparationError(code, 'changed')), \
                    patch.object(public_catalog, 'main') as catalog, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(launcher.main(['status']), 2)
                catalog.assert_not_called()


if __name__ == '__main__':
    unittest.main()

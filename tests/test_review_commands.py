"""User-facing review commands preserve the existing public catalog boundary."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import run_kb


class ReviewCommandTests(unittest.TestCase):
    def invoke(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                patch.object(run_kb, 'prepared_runtime', side_effect=AssertionError('Review must not prepare sources')):
            code = run_kb.main(arguments)
        return code, json.loads(out.getvalue() or err.getvalue())

    def test_find_and_review_every_family_without_source_preparation(self):
        catalog = json.loads((ROOT / 'knowledge/CATALOG.json').read_text(encoding='utf-8'))
        representatives = {row['family']: row['id'] for row in catalog['entries']}
        self.assertEqual(len(representatives), 4)
        for identifier in representatives.values():
            with self.subTest(id=identifier):
                code, found = self.invoke(['find', identifier, '--limit', '1'])
                self.assertEqual(code, 0)
                self.assertEqual(found['results'][0]['id'], identifier)
                code, read = self.invoke(['read', identifier, '--pointer', '/title', '--max-bytes', '24000'])
                self.assertEqual(code, 0)
                if not read['objects']:
                    self.assertEqual(read['withheld_reason'], 'REQUIRED_CONTEXT_EXCEEDS_BUDGET')
                    followup = read['continuation']['arguments']
                    code, read = self.invoke(['review', followup['id'], '--pointer', followup['pointer'],
                                              '--cursor', followup['cursor'],
                                              '--max-bytes', str(followup['max_bytes'])])
                    self.assertEqual(code, 0)
                self.assertEqual(read['entry_registration']['id'], identifier)
                self.assertTrue(read['complete'])
                self.assertEqual(read['objects'], [{'pointer': '/title', 'value': found['results'][0]['title']}])
                self.assertFalse(read['coding_admission_granted'])
                self.assertFalse(read['runtime_validation_performed'])
                self.assertIn('source_input_assessment', read)

    def test_mechanism_owner_is_whole_and_hold_is_preserved(self):
        code, read = self.invoke(['read', 'EXP-FISH-001', '--pointer', '/api_contracts/2', '--max-bytes', '24000'])
        self.assertEqual(code, 0)
        self.assertTrue(read['whole_value_delivered'])
        self.assertEqual(read['entry_registration']['coding_status'], 'hold')
        self.assertIn('source_references', read)

    def test_unknown_id_and_bad_pointer_fail(self):
        for arguments in (['read', 'NOT-A-RECORD'], ['read', 'EXP-FISH-001', '--pointer', '/../bad'],
                          ['read', 'EXP-FISH-001', '--max-bytes', '999999'], ['find', 'fish', '--limit', '31']):
            with self.subTest(arguments=arguments):
                code, result = self.invoke(arguments)
                self.assertEqual(code, 2)
                self.assertIn('error', result)

    def test_isolated_cli_from_another_working_directory(self):
        result = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'run_kb.py'),
                                 'read', 'EXP-FISH-001', '--pointer', '/title'],
                                cwd=ROOT.parent, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['entry_registration']['id'], 'EXP-FISH-001')


if __name__ == '__main__':
    unittest.main()

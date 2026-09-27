"""Portable tool regressions using original synthetic fixtures, not game files."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
FIXTURES = Path(__file__).resolve().parent / 'fixtures'
sys.path.insert(0, str(SCRIPTS))
import check_api as api
import dst_modtest as runner
import dst_zip_tool as ziptool


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / 'scripts.zip'
        vanilla = FIXTURES / 'vanilla_stub'
        with zipfile.ZipFile(self.archive, 'w') as z:
            for path in sorted(vanilla.rglob('*.lua')):
                z.write(path, path.relative_to(vanilla).as_posix())
        self.mod = self.root / 'mod'
        shutil.copytree(FIXTURES / 'mod', self.mod)

    def tearDown(self):
        self.temp.cleanup()

    def modmain(self, content):
        (self.mod / 'modmain.lua').write_text(content, encoding='utf-8')

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True, encoding='utf-8', timeout=15)

    def test_direct_read_no_cache(self):
        expected = (FIXTURES / 'vanilla_stub/scripts/components/health.lua').read_bytes()
        self.assertEqual(ziptool.read_member(self.archive, 'components/health.lua'), expected)
        self.assertFalse((self.root / '.zip_cache').exists())
        self.assertFalse((SCRIPTS / '.zip_cache').exists())

    def test_reject_bad_member_paths(self):
        for value in ['../escape', '/absolute', 'C:\\escape', 'scripts/../../escape']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                ziptool.read_member(self.archive, value)

    def test_extract_no_overwrite(self):
        target = self.root / 'export.lua'
        ziptool.extract_one(self.archive, 'components/health.lua', target)
        self.assertEqual(target.read_bytes(), ziptool.read_member(self.archive, 'components/health.lua'))
        target.write_text('owned by someone else', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            ziptool.extract_one(self.archive, 'components/health.lua', target)
        self.assertEqual(target.read_text(encoding='utf-8'), 'owned by someone else')

    def test_explicit_invalid_archive_fails(self):
        with self.assertRaises(ValueError):
            ziptool.scripts_zip(archive=self.root / 'missing.zip')
        invalid = self.root / 'invalid.zip'
        invalid.write_text('not a zip', encoding='utf-8')
        with self.assertRaises(ValueError):
            ziptool.scripts_zip(archive=invalid)

    def test_zip_cli_reads_and_missing_search_has_distinct_exit(self):
        result = self.cli('dst_zip_tool.py', '--zip', self.archive, 'info')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['lua_files'], 2)
        result = self.cli('dst_zip_tool.py', '--zip', self.archive, 'grep', 'DoDelta')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('scripts/components/health.lua:', result.stdout)
        result = self.cli('dst_zip_tool.py', '--zip', self.archive, 'grep', 'NeverDefinedHere')
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_server_and_replica_never_merged(self):
        self.modmain('inst.components.health:DoDelta(1)\ninst.components.health:GetValue()\ninst.replica.health:GetValue()')
        data = api.review(self.mod, archive=self.archive)
        self.assertEqual([c['status'] for c in data['calls']], ['DECLARED', 'NEEDS_REVIEW', 'DECLARED'])

    def test_strings_and_long_comments_are_not_calls(self):
        self.modmain('local s="inst.components.health:Fake()"\n--[=[ inst.components.health:Nope() ]=]\ninst.components.health:DoDelta(1)')
        data = api.review(self.mod, archive=self.archive)
        self.assertEqual(data['direct_calls'], 1)
        self.assertEqual(data['needs_review'], 0)

    def test_custom_component(self):
        path = self.mod / 'scripts/components/custom.lua'
        path.parent.mkdir(parents=True)
        path.write_text('local C=Class(function(self) end)\nfunction C:Reset() end\nreturn C', encoding='utf-8')
        self.modmain('inst.components.custom:Reset()')
        data = api.review(self.mod, archive=self.archive)
        self.assertEqual(data['needs_review'], 0)
        self.assertEqual(Path(data['calls'][0]['source']).resolve(), path.resolve())

    def test_other_objects_self_is_not_component_declaration(self):
        tree = api.parse_lua('local C=Class(function(self) end)\nlocal Helper={}\nfunction Helper:Init() self.OnlyHelper=function() end end\nreturn C')
        self.assertNotIn('OnlyHelper', api.declarations(tree))

    def test_invalid_lua_is_failure(self):
        self.modmain('name="bad",\nversion="1",')
        self.assertEqual(len(api.review(self.mod, archive=self.archive)['syntax_errors']), 1)

    def test_empty_input_and_wrong_source_are_errors(self):
        empty = self.root / 'empty'
        empty.mkdir()
        with self.assertRaises(ValueError):
            api.review(empty, archive=self.archive)
        with self.assertRaises(ValueError):
            api.review(self.mod, vanilla=self.root)

    def test_no_calls_is_not_declaration_evidence(self):
        self.assertEqual(api.review(self.mod, archive=self.archive)['direct_calls'], 0)
        result = self.cli('check_api.py', self.mod, '--zip', self.archive)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['direct_calls'], 0)

    def test_api_cli_exit_codes_distinguish_review_and_syntax(self):
        for source, status in [('inst.components.health:DoDelta(1)', 0),
                               ('inst.components.health:Unknown()', 2),
                               ('local = broken', 1)]:
            with self.subTest(status=status):
                self.modmain(source)
                report = self.root / 'report.json'
                result = self.cli('check_api.py', self.mod, '--zip', self.archive, '--out', report)
                self.assertEqual(result.returncode, status, result.stderr)
                data = json.loads(report.read_text(encoding='utf-8'))
                self.assertEqual(bool(data['syntax_errors']), status == 1)
                self.assertEqual(bool(data['needs_review']), status == 2)

    def test_missing_parser_dependency_is_not_reported_as_lua_syntax(self):
        self.modmain('inst.components.health:DoDelta(1)')
        report = self.root / 'report.json'
        for output_args in [[], ['--out', str(report)]]:
            with self.subTest(output_args=output_args):
                result = subprocess.run(
                    [sys.executable, '-S', str(SCRIPTS / 'check_api.py'),
                     str(self.mod), '--zip', str(self.archive), *output_args],
                    capture_output=True, text=True, encoding='utf-8', timeout=15)
                self.assertEqual(result.returncode, 2)
                self.assertIn('luaparser is required', result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertFalse(report.exists())

    def test_stale_same_name_not_used(self):
        mods = self.root / 'game_mods'
        stale = mods / 'mod'
        stale.mkdir(parents=True)
        (stale / 'modinfo.lua').write_text('name="stale"', encoding='utf-8')
        before = (self.mod / 'modinfo.lua').read_bytes()
        record = runner.stage_mod(self.mod, mods, 'unique', 0)
        self.assertEqual((Path(record['staged']) / 'modinfo.lua').read_bytes(), before)
        self.assertEqual(record['sha256'], runner.file_manifest(self.mod))
        self.assertEqual((stale / 'modinfo.lua').read_text(encoding='utf-8'), 'name="stale"')
        with self.assertRaises(ValueError):
            runner.stage_mod(self.mod, mods, 'unique', 0)

    def test_current_token_required(self):
        state = runner.Outcome('new')
        for line in ['LOADING LUA SUCCESS', '[DME:new:READY]', '[DME:old:DONE]', '[MODTEST] SCRIPT_OK', 'status:ok']:
            state.consume(line)
        self.assertFalse(state.passed())
        state.consume('[DME:new:DONE]')
        self.assertTrue(state.passed())

    def test_late_failure_overrides_done(self):
        state = runner.Outcome('x')
        for line in ['LOADING LUA SUCCESS', '[DME:x:READY]', '[DME:x:DONE]', '[DME:x:FAIL] later assertion']:
            state.consume(line)
        self.assertFalse(state.passed())

    def test_script_return_is_not_done(self):
        state = runner.Outcome('x')
        state.consume('LOADING LUA SUCCESS')
        state.consume('[DME:x:READY]')
        self.assertFalse(state.passed())

    def test_every_requested_mod_must_be_loaded(self):
        state = runner.Outcome('x', ['a', 'b'])
        for line in ['LOADING LUA SUCCESS', '[DME:x:READY]', '[DME:x:DONE]', '[DME:x:LOADED:a]']:
            state.consume(line)
        self.assertFalse(state.passed())
        state.consume('[DME:old:LOADED:b]')
        self.assertFalse(state.passed())
        state.consume('[DME:x:LOADED:b]')
        self.assertTrue(state.passed())

    def test_config_and_runner_are_valid_lua(self):
        _, cluster = runner.write_cluster(self.root / 'storage', ['mod'], 11018,
                                          {'0': {'s': '\n\r\t"\\012中文', 'flag': False}})
        api.parse_lua((cluster / 'Master/modoverrides.lua').read_text(encoding='utf-8'))
        key = runner.stage_runner(self.root, 'id', script=None)
        api.parse_lua((Path(key['staged']) / 'modmain.lua').read_text(encoding='utf-8'))
        behavior = FIXTURES / 'behavior.lua'
        key = runner.stage_runner(self.root, 'id2', script=behavior)
        target = Path(key['staged'])
        api.parse_lua((target / 'modmain.lua').read_text(encoding='utf-8'))
        self.assertEqual((target / 'test_script.lua').read_bytes(), behavior.read_bytes())

    def test_nonfinite_cli_inputs_are_rejected_before_environment_checks(self):
        for flag, value in [('--timeout', 'nan'), ('--grace', 'inf'), ('--delay', 'nan')]:
            with self.subTest(flag=flag):
                result = self.cli('dst_modtest.py', self.mod, '--dst', self.root,
                                  '--out', self.root / 'out', flag, value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr.strip(), 'ERROR: Invalid timeout/grace/delay')
                self.assertFalse((self.root / 'out').exists())

    def test_nonfinite_config_numbers_are_rejected(self):
        for value in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                runner.lua_value({'value': value})

    def run_fake_server(self, body, timeout=5, grace=0.25):
        command = [sys.executable, '-u', '-c', 'import time\n' + body]
        log = self.root / 'console.log'
        result = runner.run_server(command, self.root, log, 'current', timeout, grace,
                                   quiet=True, expected=['fixture'])
        return result, log.read_text(encoding='utf-8')

    def ready_lines(self):
        return 'print("LOADING LUA SUCCESS\\n[DME:current:LOADED:fixture]\\n[DME:current:READY]", flush=True)\n'

    def test_subprocess_matching_completion_passes_after_observation(self):
        result, log = self.run_fake_server(self.ready_lines() +
            'print("[DME:current:DONE]", flush=True)\ntime.sleep(10)')
        self.assertTrue(result['passed'], result)
        self.assertIsNone(result['failure'])
        self.assertIn('[DME:current:DONE]', log)
        self.assertGreaterEqual(result['elapsed_seconds'], result['observation_after_done_seconds'])

    def test_subprocess_late_failure_is_not_lost(self):
        result, log = self.run_fake_server(self.ready_lines() +
            'print("[DME:current:DONE]", flush=True)\n'
            'time.sleep(0.05)\nprint("[DME:current:FAIL] delayed assertion", flush=True)\ntime.sleep(10)')
        self.assertFalse(result['passed'])
        self.assertIn('delayed assertion', result['failure'])
        self.assertIn('delayed assertion', log)

    def test_subprocess_missing_done_times_out(self):
        result, log = self.run_fake_server(self.ready_lines() + 'time.sleep(10)', timeout=1)
        self.assertFalse(result['passed'])
        self.assertFalse(result['done'])
        self.assertIsNotNone(result['failure'])
        self.assertIn('[DME:current:READY]', log)

    def test_subprocess_early_exit_is_not_success(self):
        result, _ = self.run_fake_server(self.ready_lines() + 'print("[DME:current:DONE]", flush=True)', grace=5)
        self.assertEqual(result['returncode'], 0)
        self.assertFalse(result['passed'])
        self.assertIsNotNone(result['failure'])

    def test_all_repository_lua_fixtures_parse(self):
        for path in FIXTURES.rglob('*.lua'):
            with self.subTest(path=path.relative_to(FIXTURES)):
                api.parse_lua(path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)

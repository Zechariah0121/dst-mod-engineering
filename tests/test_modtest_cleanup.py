"""Owned staging cleanup with synthetic mods and Python child processes."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import dst_modtest as runner


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.dst = self.root / 'game'
        self.mods = self.dst / 'mods'
        self.mods.mkdir(parents=True)
        self.binary = self.dst / 'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe'
        self.binary.parent.mkdir()
        self.binary.write_bytes(b'synthetic fixture, never executed')
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'modinfo.lua').write_text('name="fixture"', encoding='utf-8')
        (self.source / 'modmain.lua').write_text('-- source fixture', encoding='utf-8')
        self.out = self.root / 'evidence'
        self.behavior = self.root / 'behavior.lua'
        self.behavior.write_text('TEST.Done("fixture")', encoding='utf-8')
        self.stderr = io.StringIO()

    def tearDown(self):
        self.temp.cleanup()

    def record(self, run_id='one'):
        return {'ownership_version': 1, 'mods_root': str(self.mods), 'run_id': run_id,
                'owned_stages': [], 'process': None, 'result': {'passed': True}}

    def stage(self, record):
        return runner.stage_mod(self.source, self.mods, record['run_id'], 0, record['owned_stages'])

    def read_run(self):
        paths = list(self.out.glob('*/manifest.json'))
        self.assertEqual(len(paths), 1)
        return json.loads(paths[0].read_text(encoding='utf-8')), paths[0]

    def assert_cleaned(self, record):
        self.assertEqual(record['cleanup']['status'], 'complete', record['cleanup'])
        for entry in record['owned_stages']:
            self.assertFalse(Path(entry['staged']).exists())
            snapshot = Path(entry['snapshot'])
            self.assertTrue(snapshot.is_dir())
            self.assertEqual(entry['snapshot_sha256'], runner.file_manifest(snapshot))

    def invoke(self, server_mode='pass', extra=()):
        original = runner.run_server

        def fake_command(command, cwd, log_path, run_id, timeout, grace, quiet, expected, record, checkpoint):
            lines = ['LOADING LUA SUCCESS', *[f'[DME:{run_id}:LOADED:{key}]' for key in expected],
                     f'[DME:{run_id}:READY]']
            if server_mode == 'pass':
                lines.append(f'[DME:{run_id}:DONE]')
            elif server_mode == 'fail':
                lines.append(f'[DME:{run_id}:FAIL] fixture failure')
            body = 'import time\nprint(' + repr('\n'.join(lines)) + ', flush=True)\ntime.sleep(20)'
            return original([sys.executable, '-u', '-c', body], cwd, log_path, run_id,
                            timeout, grace, quiet, expected, record, checkpoint)

        args = [str(self.source), '--dst', str(self.dst), '--out', str(self.out),
                '--script', str(self.behavior), '--timeout', '0.6', '--grace', '0.05', '--quiet', *extra]
        with patch.object(runner, 'run_server', side_effect=fake_command), redirect_stdout(io.StringIO()), redirect_stderr(self.stderr):
            return runner.main(args)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_success_stops_process_then_cleans_and_retains_evidence(self):
        self.assertEqual(self.invoke(), 0)
        record, path = self.read_run()
        self.assertTrue(record['result']['passed'])
        self.assertFalse(record['process']['running'])
        self.assertFalse(runner.pid_is_running(record['process']['pid']))
        self.assert_cleaned(record)
        self.assertIn('DONE', (path.parent / 'console.log').read_text(encoding='utf-8'))
        self.assertTrue((Path(record['cluster_snapshot']) / 'Master/modoverrides.lua').is_file())
        runner_copy = Path(record['runner']['snapshot'])
        self.assertEqual((runner_copy / 'test_script.lua').read_bytes(), self.behavior.read_bytes())

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_failure_and_timeout_keep_original_result_and_clean(self):
        for mode in ['fail', 'timeout']:
            with self.subTest(mode=mode):
                self.assertEqual(self.invoke(mode), 1)
                record, _ = self.read_run()
                self.assertFalse(record['result']['passed'])
                self.assertIn('fixture failure' if mode == 'fail' else 'timeout', record['result']['failure'])
                self.assertFalse(record['process']['running'])
                self.assert_cleaned(record)
                shutil.rmtree(self.out)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_keyboard_interrupt_stops_child_and_cleans(self):
        get = runner.queue.Queue.get
        interrupted = []

        def interrupt_once(queue, *args, **kwargs):
            if not interrupted:
                interrupted.append(True)
                raise KeyboardInterrupt
            return get(queue, *args, **kwargs)

        with patch.object(runner.queue.Queue, 'get', interrupt_once):
            self.assertEqual(self.invoke('timeout'), 130)
        record, _ = self.read_run()
        self.assertEqual(record['result']['kind'], 'interrupted')
        self.assertFalse(record['process']['running'])
        self.assertFalse(runner.pid_is_running(record['process']['pid']))
        self.assert_cleaned(record)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_launch_failure_cleans_stages(self):
        with patch.object(runner.subprocess, 'Popen', side_effect=OSError('launch fixture')):
            self.assertEqual(self.invoke(), 2)
        record, _ = self.read_run()
        self.assertIn('launch fixture', record['error'])
        self.assertIsNone(record['process'])
        self.assert_cleaned(record)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_half_copy_is_registered_snapshotted_and_cleaned(self):
        copytree = shutil.copytree

        def half_copy(source, target, *args, **kwargs):
            if Path(target).parent == self.mods:
                shutil.copyfile(Path(source) / 'modinfo.lua', Path(target) / 'modinfo.lua')
                raise OSError('half copy fixture')
            return copytree(source, target, *args, **kwargs)

        with patch.object(runner.shutil, 'copytree', side_effect=half_copy):
            self.assertEqual(self.invoke(), 2)
        record, _ = self.read_run()
        self.assertEqual(len(record['owned_stages']), 1)
        self.assertFalse(record['owned_stages'][0]['stage_complete'])
        self.assertIn('half copy fixture', record['error'])
        self.assert_cleaned(record)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_partial_runner_write_is_registered_and_cleaned(self):
        copyfile = shutil.copyfile

        def fail_script(source, target, *args, **kwargs):
            if Path(target).name == 'test_script.lua':
                raise OSError('runner script copy fixture')
            return copyfile(source, target, *args, **kwargs)

        with patch.object(runner.shutil, 'copyfile', side_effect=fail_script):
            self.assertEqual(self.invoke(), 2)
        record, _ = self.read_run()
        self.assertEqual(len(record['owned_stages']), 2)
        self.assertFalse(record['owned_stages'][-1]['stage_complete'])
        self.assert_cleaned(record)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_keep_staged_and_explicit_manifest_cleanup(self):
        self.assertEqual(self.invoke(extra=['--keep-staged']), 0)
        record, path = self.read_run()
        self.assertEqual(record['cleanup']['status'], 'kept')
        self.assertTrue(all(Path(e['staged']).exists() for e in record['owned_stages']))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['--dst', str(self.dst), '--cleanup-manifest', str(path)]), 0)
        record = json.loads(path.read_text(encoding='utf-8'))
        self.assert_cleaned(record)
        self.assertTrue(record['result']['passed'])

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_busy_file_reports_cleanup_error_without_changing_pass(self):
        with patch.object(runner.shutil, 'rmtree', side_effect=PermissionError('occupied fixture')):
            self.assertEqual(self.invoke(), 3)
        record, _ = self.read_run()
        self.assertTrue(record['result']['passed'])
        self.assertEqual(record['test_exit_code'], 0)
        self.assertEqual(record['exit_code'], 3)
        self.assertEqual(record['cleanup']['status'], 'incomplete')
        self.assertEqual(len(record['cleanup']['errors']), 2)
        self.assertIn('CLEANUP ERROR', self.stderr.getvalue())
        self.assertTrue(all(Path(e['staged']).exists() for e in record['owned_stages']))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_snapshot_failure_preserves_unique_run_copy_and_manual_retry_recovers(self):
        original_server = runner.run_server
        copytree = shutil.copytree
        after_run = []

        def lose_evidence_after_run(*args, **kwargs):
            result = original_server(*args, **kwargs)
            record = args[8]
            shutil.rmtree(record['owned_stages'][0]['snapshot'])
            after_run.append(True)
            return result

        def fail_evidence_copy(source, target, *args, **kwargs):
            if after_run and Path(target).parent.name == 'snapshots':
                raise OSError('evidence disk fixture')
            return copytree(source, target, *args, **kwargs)

        with patch.object(runner, 'run_server', side_effect=lose_evidence_after_run), patch.object(runner.shutil, 'copytree', side_effect=fail_evidence_copy):
            # invoke wraps the saved run_server callable to substitute a Python child.
            self.assertEqual(self.invoke(), 3)
        record, path = self.read_run()
        self.assertTrue(record['result']['passed'])
        self.assertEqual(record['cleanup']['status'], 'incomplete')
        self.assertTrue(Path(record['owned_stages'][0]['staged']).is_dir())
        self.assertIn('evidence disk fixture', self.stderr.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['--dst', str(self.dst), '--cleanup-manifest', str(path)]), 0)
        record = json.loads(path.read_text(encoding='utf-8'))
        self.assert_cleaned(record)
        self.assertTrue(record['result']['passed'])

    def test_manual_cleanup_preserves_checkpoint_only_partial_copy(self):
        record = self.record()
        run_dir = self.out / 'one'
        run_dir.mkdir(parents=True)
        record['evidence_dir'] = str(run_dir)
        target, entry = runner.create_stage(self.mods, 'one', 0, record['owned_stages'])
        (target / 'partial.lua').write_text('-- partial copy', encoding='utf-8')
        runner.write_manifest(record, run_dir)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['--dst', str(self.dst), '--cleanup-manifest', str(run_dir / 'manifest.json')]), 0)
        saved = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
        self.assertFalse(target.exists())
        self.assertEqual((Path(saved['owned_stages'][0]['snapshot']) / 'partial.lua').read_text(encoding='utf-8'), '-- partial copy')
        self.assertFalse(saved['owned_stages'][0]['stage_complete'])

    @unittest.skipUnless(sys.platform == 'win32', 'Windows runner integration')
    def test_process_start_checkpoint_failure_still_stops_and_cleans(self):
        write = runner.write_manifest

        def fail_process_checkpoint(record, run_dir):
            if (record.get('process') or {}).get('running'):
                raise OSError('process checkpoint fixture')
            return write(record, run_dir)

        with patch.object(runner, 'write_manifest', side_effect=fail_process_checkpoint):
            self.assertEqual(self.invoke(), 2)
        record, _ = self.read_run()
        self.assertIn('process checkpoint fixture', record['error'])
        self.assertFalse(record['process']['running'])
        self.assertFalse(runner.pid_is_running(record['process']['pid']))
        self.assert_cleaned(record)

    def test_other_run_and_user_folder_survive(self):
        one, two = self.record('one'), self.record('two')
        first, second = self.stage(one), self.stage(two)
        user = self.mods / 'user_mod'
        user.mkdir()
        self.assertEqual(runner.cleanup_staged(one, self.mods)['status'], 'complete')
        self.assertFalse(Path(first['staged']).exists())
        self.assertTrue(Path(second['staged']).is_dir())
        self.assertTrue(user.is_dir())

    def test_parallel_runs_clean_only_their_own_directories(self):
        barrier = threading.Barrier(2)
        errors = []

        def run(run_id):
            try:
                record = self.record(run_id)
                entry = self.stage(record)
                barrier.wait(timeout=5)
                self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'complete')
                self.assertFalse(Path(entry['staged']).exists())
            except BaseException as error:
                errors.append(error)

        threads = [threading.Thread(target=run, args=(name,)) for name in ['parallel1', 'parallel2']]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
            self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])

    @unittest.skipUnless(sys.platform == 'win32', 'Windows open-file deletion semantics')
    def test_open_file_blocks_cleanup_and_retry_succeeds_after_close(self):
        record = self.record()
        entry = self.stage(record)
        target = Path(entry['staged'])
        with (target / 'modinfo.lua').open('rb'):
            report = runner.cleanup_staged(record, self.mods)
            self.assertEqual(report['status'], 'incomplete')
            self.assertTrue(report['errors'])
            self.assertTrue(target.exists())
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'complete')
        self.assertFalse(target.exists())

    def test_process_must_be_stopped_before_cleanup(self):
        record = self.record()
        entry = self.stage(record)
        record['process'] = {'pid': os.getpid(), 'running': True}
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'blocked')
        self.assertTrue(Path(entry['staged']).exists())
        record['process']['running'] = False
        self.assertEqual(runner.cleanup_staged(record, self.mods, inspect_process=True)['status'], 'blocked')

    def test_forged_path_wrong_root_and_identity_are_rejected(self):
        record = self.record()
        entry = self.stage(record)
        original = entry['staged']
        entry['staged'] = str(self.source)
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'incomplete')
        self.assertTrue(self.source.is_dir())
        entry['staged'] = original
        entry['directory_id'] = [-1, -1]
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'incomplete')
        self.assertTrue(Path(original).is_dir())
        self.assertEqual(runner.cleanup_staged(record, self.root)['status'], 'blocked')

    @unittest.skipUnless(sys.platform == 'win32', 'Windows junction check')
    def test_junction_at_root_child_and_source_is_refused(self):
        victim = self.root / 'victim'
        victim.mkdir()
        sentinel = victim / 'keep.txt'
        sentinel.write_text('keep', encoding='utf-8')

        def junction(link):
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(victim)],
                                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode, 0, result.stderr)

        record = self.record()
        entry = self.stage(record)
        junction(Path(entry['staged']) / 'linked-child')
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'incomplete')
        self.assertTrue(sentinel.exists())
        linked_source = self.root / 'linked-source'
        junction(linked_source)
        with self.assertRaises(ValueError):
            runner.stage_mod(linked_source, self.mods, 'bad', 0)
        fake_root = self.root / 'linked-mods'
        junction(fake_root)
        self.assertEqual(runner.cleanup_staged(record, fake_root)['status'], 'blocked')
        root_entry = self.stage(self.record('replace'))
        target = Path(root_entry['staged'])
        shutil.rmtree(target)
        junction(target)
        replaced = self.record('replace')
        replaced['owned_stages'] = [root_entry]
        self.assertEqual(runner.cleanup_staged(replaced, self.mods)['status'], 'incomplete')
        self.assertTrue(sentinel.exists())

    def test_symlink_inside_stage_is_refused(self):
        record = self.record()
        entry = self.stage(record)
        try:
            (Path(entry['staged']) / 'linked-file').symlink_to(self.source / 'modinfo.lua')
        except OSError as error:
            self.skipTest(f'Symlink privilege unavailable: {error}')
        self.assertEqual(runner.cleanup_staged(record, self.mods)['status'], 'incomplete')
        self.assertTrue((self.source / 'modinfo.lua').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)

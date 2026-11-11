"""Isolated Windows DST headless smoke/behavior runner. Standard library only.

Snapshots requested sources into unique mod folders. Evidence and reproducible
copies stay under --out. Owned game folders are removed after the process stops,
unless --keep-staged is selected. Interrupted runs can use --cleanup-manifest.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid


FAIL_PATTERNS = ('Error loading mod!', 'Error loading modinfo.lua', 'LUA ERROR',
                 '[Error]', '[CRITICAL]', 'Invalid port selection', 'Error loading file', 'terminated prematurely',
                 "Couldn't find mod", 'Could not find mod', '[MODTEST] script error:')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_manifest(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def regular_directory(path):
    path = Path(os.path.abspath(path))
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        reparse = getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or reparse:
            raise ValueError(f'Requires a real directory without links: {part}')
    return path.resolve()


def check_tree(root):
    regular_directory(root)
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            info = path.lstat()
            reparse = getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
            if reparse or stat.S_ISLNK(info.st_mode) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError(f'Requires a regular tree without links: {path}')


def create_stage(mods_root, run_id, suffix, owned=None, checkpoint=None):
    mods_root = regular_directory(mods_root)
    if not re.fullmatch(r'[A-Za-z0-9]+', run_id) or not re.fullmatch(r'(?:[0-9]+|runner)', str(suffix)):
        raise ValueError('Invalid staging run ID or suffix')
    key = f'_dme_test_{run_id}_{suffix}'
    target = mods_root / key
    try:
        target.mkdir()
    except FileExistsError:
        raise ValueError(f'Staging collision: {target}') from None
    info = target.lstat()
    entry = {'key': key, 'staged': str(target), 'owned': True,
             'directory_id': [info.st_dev, info.st_ino], 'stage_complete': False, 'sha256': {}}
    if owned is not None:
        owned.append(entry)
    if checkpoint:
        checkpoint()
    return target, entry


def stage_mod(source, mods_root, run_id, index, owned=None, checkpoint=None):
    source = regular_directory(source)
    if not (source / 'modinfo.lua').is_file():
        raise ValueError(f'Not a mod folder: {source}')
    check_tree(source)
    before = file_manifest(source)
    target, entry = create_stage(mods_root, run_id, index, owned, checkpoint)
    entry['source'] = str(source)
    shutil.copytree(source, target, dirs_exist_ok=True, symlinks=True)
    check_tree(target)
    after = file_manifest(target)
    if before != after or before != file_manifest(source):
        raise ValueError(f'Source changed while staging: {source}; snapshot retained at {target}')
    entry.update(sha256=after, stage_complete=True)
    if checkpoint:
        checkpoint()
    return entry


RUNNER_INFO = '''name = "DST engineering test runner"
description = "Isolated local headless validation"
author = "local"
version = "1"
api_version = 10
dst_compatible = true
all_clients_require_mod = false
client_only_mod = false
server_only_mod = true
'''

RUNNER_TEMPLATE = '''local G = GLOBAL
local token = "__RUN_ID__"
local function mark(kind, detail)
    G.print("[DME:" .. token .. ":" .. kind .. "] " .. G.tostring(detail or ""))
end
AddSimPostInit(function()
    if not G.TheWorld.ismastersim then return end
    G.TheWorld:DoTaskInTime(__DELAY__, function()
        for _, key in G.ipairs(__EXPECTED__) do
            local mod = G.ModManager:GetMod(key)
            if mod == nil or mod.modinfo.failed or not G.KnownModIndex:IsModCompatibleWithMode(key) then
                mark("FAIL", "requested mod not loaded/compatible: " .. key)
                return
            end
            if mod.modinfo.client_only_mod then
                mark("FAIL", "client-only mod requires a real client; unsupported by this harness: " .. key)
                return
            end
            mark("LOADED:" .. key)
        end
        mark("READY")
        local failed = false
        local finished = false
        local test = {}
        function test.Fail(reason)
            failed = true
            mark("FAIL", reason)
        end
        function test.Done(detail)
            if not failed and not finished then
                finished = true
                mark("DONE", detail)
            end
        end
        function test.After(seconds, fn)
            return G.TheWorld:DoTaskInTime(seconds, function()
                local ok, err = G.xpcall(fn, G.tostring)
                if not ok then test.Fail(err) end
            end)
        end
        __BODY__
    end)
end)
'''

SCRIPT_BODY = '''local fn = G.kleiloadlua(MODROOT .. "test_script.lua")
        if G.type(fn) ~= "function" then test.Fail(fn) return end
        local environment = G.setmetatable({GLOBAL=G, TEST=test}, {__index=G})
        G.setfenv(fn, environment)
        local ok, err = G.xpcall(fn, G.tostring)
        if not ok then test.Fail(err) end'''


def stage_runner(mods_root, run_id, script=None, delay=2, expected=(), owned=None, checkpoint=None):
    target, entry = create_stage(mods_root, run_id, 'runner', owned, checkpoint)
    (target / 'modinfo.lua').write_text(RUNNER_INFO, encoding='utf-8')
    body = SCRIPT_BODY if script else 'test.Done("world smoke only")'
    content = (RUNNER_TEMPLATE.replace('__RUN_ID__', run_id).replace('__DELAY__', str(delay))
               .replace('__BODY__', body).replace('__EXPECTED__', lua_value(list(expected))))
    (target / 'modmain.lua').write_text(content, encoding='utf-8')
    if script:
        shutil.copyfile(script, target / 'test_script.lua')
    entry.update(sha256=file_manifest(target), stage_complete=True)
    if checkpoint:
        checkpoint()
    return entry


def write_manifest(record, run_dir):
    path = Path(run_dir) / 'manifest.json'
    pending = path.with_suffix('.json.tmp')
    pending.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    pending.replace(path)


def snapshot_stages(record, run_dir):
    errors = []
    for entry in record['owned_stages']:
        snapshot = Path(run_dir) / 'snapshots' / entry['key']
        try:
            if entry.get('snapshot_complete') and snapshot.is_dir():
                check_tree(snapshot)
                if file_manifest(snapshot) == entry['snapshot_sha256']:
                    continue
            entry['snapshot_complete'] = False
            target = owned_stage_path(record, entry, regular_directory(record['mods_root']))
            info = target.lstat()
            if [info.st_dev, info.st_ino] != entry['directory_id']:
                raise ValueError(f'Staged directory identity changed: {target}')
            check_tree(target)
            snapshot.parent.mkdir(exist_ok=True)
            shutil.copytree(target, snapshot, dirs_exist_ok=True, symlinks=True)
            check_tree(snapshot)
            files = file_manifest(snapshot)
            if files != file_manifest(target):
                raise ValueError(f'Evidence copy differs from staged tree: {target}')
            entry.update(snapshot=str(snapshot), snapshot_sha256=files, snapshot_complete=True)
        except (OSError, ValueError) as error:
            entry['snapshot_complete'] = False
            errors.append(f'{entry["key"]}: evidence snapshot: {error}')
    return errors


def owned_stage_path(record, entry, mods_root):
    key = entry['key']
    target = Path(entry['staged'])
    if (entry.get('owned') is not True or
            not re.fullmatch(r'_dme_test_' + re.escape(record['run_id']) + r'_(?:[0-9]+|runner)', key) or
            target != mods_root / key):
        raise ValueError(f'Invalid owned stage: {target}')
    return target


def pid_is_running(pid):
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: PID absent
                return False
            raise OSError(ctypes.get_last_error(), f'Cannot inspect PID {pid}')
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise OSError(ctypes.get_last_error(), f'Cannot inspect PID {pid}')
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def validate_cleanup(record, mods_root, inspect_process=False):
    mods_root = regular_directory(mods_root)
    if record.get('ownership_version') != 1 or Path(record['mods_root']) != mods_root:
        raise ValueError('Manifest does not own stages in the specified mods root')
    if not isinstance(record.get('owned_stages'), list):
        raise ValueError('Manifest has no owned stage list')
    if not re.fullmatch(r'[A-Za-z0-9]+', record['run_id']):
        raise ValueError('Invalid manifest run ID')
    process = record.get('process') or {}
    if process.get('pid') is not None and (type(process['pid']) is not int or process['pid'] <= 0):
        raise ValueError('Invalid manifest process ID')
    if inspect_process and process.get('pid'):
        running = pid_is_running(process['pid'])
    else:
        running = process.get('running', False)
    if running:
        raise ValueError('Run process is still running; stop it before cleaning its stages')
    return mods_root


def cleanup_staged(record, mods_root, keep=False, inspect_process=False):
    report = {'status': 'kept' if keep else 'complete', 'removed': [], 'missing': [], 'retained': [], 'errors': []}
    record['cleanup'] = report
    if keep:
        return report
    try:
        mods_root = validate_cleanup(record, mods_root, inspect_process)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report.update(status='blocked', errors=[str(error)])
        return report
    for entry in record['owned_stages']:
        try:
            target = owned_stage_path(record, entry, mods_root)
            try:
                info = target.lstat()
            except FileNotFoundError:
                report['missing'].append(str(target))
                continue
            if [info.st_dev, info.st_ino] != entry['directory_id']:
                raise ValueError(f'Staged directory identity changed: {target}')
            if record.get('evidence_dir'):
                snapshot = Path(record['evidence_dir']) / 'snapshots' / entry['key']
                if not entry.get('snapshot_complete') or Path(entry.get('snapshot', '')) != snapshot:
                    report['retained'].append(str(target))
                    raise ValueError(f'Evidence snapshot unavailable; preserved {target}; retry --cleanup-manifest')
                check_tree(snapshot)
                if file_manifest(snapshot) != entry['snapshot_sha256']:
                    report['retained'].append(str(target))
                    raise ValueError(f'Evidence snapshot changed; preserved {target}; retry --cleanup-manifest')
            check_tree(target)
            shutil.rmtree(target)
            report['removed'].append(str(target))
        except (OSError, ValueError, KeyError, TypeError) as error:
            report['errors'].append(str(error))
    if report['errors']:
        report['status'] = 'incomplete'
    return report


def free_udp_port():
    # Current offline engine limits LAN ports to this range; arbitrary ephemeral
    # ports silently fall back to 10999. Availability can still race with launch.
    for port in range(11018, 10997, -1):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise ValueError('No free LAN UDP port in engine range 10998..11018')


def write_cluster(storage, keys, port, options=None):
    storage = Path(storage)
    cluster = storage / 'DME/Cluster'
    master = cluster / 'Master'
    master.mkdir(parents=True)
    (cluster / 'cluster.ini').write_text(
        '[GAMEPLAY]\nmax_players = 1\ngame_mode = survival\npause_when_empty = false\n'
        '[NETWORK]\nlan_only_cluster = true\noffline_cluster = true\ncluster_name = DME local test\n'
        '[SHARD]\nshard_enabled = false\n', encoding='utf-8')
    (master / 'server.ini').write_text(
        f'[NETWORK]\nserver_port = {port}\n[SHARD]\nis_master = true\n'
        '[ACCOUNT]\ndedicated_lan_server = true\n', encoding='utf-8')
    config = options or {}
    lines = ['return {']
    for index, key in enumerate(keys):
        settings = config.get(str(index), {})
        lines.append(f'[{lua_value(key)}] = {{enabled=true, configuration_options={lua_value(settings)}}},')
    lines.append('}')
    (master / 'modoverrides.lua').write_text('\n'.join(lines), encoding='utf-8')
    return storage, cluster


def lua_value(value):
    if isinstance(value, str):
        # Lua 5.1 does not support JSON unicode escapes. Encode control bytes as
        # three-digit decimal escapes to keep adjacent digits unambiguous.
        return '"' + ''.join('\\' + c if c in '\\"' else f'\\{ord(c):03}' if ord(c) < 32 else c for c in value) + '"'
    if value is None:
        return 'nil'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        import math
        if not math.isfinite(value):
            raise ValueError('Non-finite config number')
        return str(value)
    if isinstance(value, dict):
        return '{' + ','.join(f'[{lua_value(k)}]={lua_value(v)}' for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '{' + ','.join(lua_value(v) for v in value) + '}'
    raise ValueError(f'Unsupported config value: {type(value)}')


class Outcome:
    def __init__(self, run_id, expected=()):
        self.run_id = run_id
        self.expected = list(expected)
        self.loaded = []
        self.lua_loaded = False
        self.ready = False
        self.done = False
        self.failure = None

    def consume(self, line):
        for key in self.expected:
            if key not in self.loaded and f'[DME:{self.run_id}:LOADED:{key}]' in line:
                self.loaded.append(key)
        self.lua_loaded |= 'LOADING LUA SUCCESS' in line
        self.ready |= f'[DME:{self.run_id}:READY]' in line
        self.done |= f'[DME:{self.run_id}:DONE]' in line
        if f'[DME:{self.run_id}:FAIL]' in line or any(p in line for p in FAIL_PATTERNS):
            self.failure = self.failure or line.strip()

    def passed(self):
        return (self.lua_loaded and self.ready and self.done and self.failure is None
                and set(self.loaded) == set(self.expected))


def run_server(command, cwd, log_path, run_id, timeout, grace, quiet, expected=(), record=None, checkpoint=None):
    result = Outcome(run_id, expected)
    output = queue.Queue()
    start = time.monotonic()
    done_at = None
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    proc = None
    thread = None
    stop_errors = []

    def pump():
        with Path(log_path).open('w', encoding='utf-8') as log:
            for line in proc.stdout:
                log.write(line)
                log.flush()
                output.put(line)

    try:
        proc = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding='utf-8', errors='replace', text=True, creationflags=flags)
        if record is not None:
            record['process'] = {'pid': proc.pid, 'running': True}
        if checkpoint:
            checkpoint()
        thread = threading.Thread(target=pump, daemon=True)
        thread.start()
        while True:
            try:
                line = output.get(timeout=0.1)
                result.consume(line)
                if not quiet:
                    print(line, end='')
            except queue.Empty:
                pass
            now = time.monotonic()
            if result.failure:
                break
            if result.passed():
                done_at = done_at or now
                if now - done_at >= grace:
                    break
            if now - start >= timeout:
                result.failure = 'timeout: no complete matching result (including post-DONE observation)'
                break
            if proc.poll() is not None and output.empty():
                result.failure = result.failure or 'server exited before the observation window completed'
                break
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=15)
            except (OSError, subprocess.SubprocessError) as error:
                try:
                    proc.kill()
                    proc.wait(timeout=10)
                except (OSError, subprocess.SubprocessError) as kill_error:
                    stop_errors.extend([str(error), str(kill_error)])
        if proc is not None and record is not None:
            record['process'].update(running=proc.poll() is None, returncode=proc.returncode, stop_errors=stop_errors)
        if thread is not None and thread.ident is not None:
            thread.join(timeout=5)
            if thread.is_alive():
                result.failure = result.failure or 'log reader did not finish; result incomplete'
        while not output.empty():
            result.consume(output.get_nowait())
        if proc is not None and proc.poll() is not None:
            proc.stdout.close()
    return {**vars(result), 'passed': result.passed(), 'returncode': proc.returncode,
            'elapsed_seconds': round(time.monotonic() - start, 2), 'pid': proc.pid,
            'observation_after_done_seconds': grace, 'log': str(log_path), 'process_stop_errors': stop_errors}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mods', nargs='*', help='Exact source directories; copies always get unique names')
    p.add_argument('--dst', required=True, help='Installed game root')
    p.add_argument('--out', help='Evidence parent; a unique run directory is created')
    p.add_argument('--keep-staged', action='store_true', help='Keep owned game mod folders after this run')
    p.add_argument('--cleanup-manifest', help='Clean only owned folders recorded by this runner after its process stops')
    p.add_argument('--storage-root', help='ASCII parent for engine saves (default: OS temp/dst_mod_engineering)')
    p.add_argument('--script', help='Lua script; must explicitly call TEST.Done() after ALL assertions')
    p.add_argument('--config', help='JSON object keyed by zero-based source index, e.g. {"0":{"option":true}}')
    p.add_argument('--timeout', type=float, default=240)
    p.add_argument('--grace', type=float, default=3, help='Post-Done log observation window')
    p.add_argument('--delay', type=float, default=2, help='Seconds after AddSimPostInit before test')
    p.add_argument('--quiet', action='store_true')
    a = p.parse_args(argv)
    record = None
    run_dir = None
    test_exit_code = None
    try:
        if a.cleanup_manifest:
            manifest = Path(a.cleanup_manifest)
            loaded = json.loads(manifest.read_text(encoding='utf-8-sig'))
            if not isinstance(loaded, dict):
                raise ValueError('Cleanup manifest must be an object')
            record = loaded
            run_dir = regular_directory(manifest.parent)
            validate_cleanup(record, Path(a.dst) / 'mods', inspect_process=True)
            evidence_errors = snapshot_stages(record, run_dir)
            report = cleanup_staged(record, Path(a.dst) / 'mods', inspect_process=True)
            report['evidence_errors'] = evidence_errors
            write_manifest(record, run_dir)
            print(json.dumps(report, ensure_ascii=False))
            return 0 if report['status'] == 'complete' and not evidence_errors else 3
        if not a.mods or not a.out:
            raise ValueError('Test runs require mod sources and --out')
        if not all(math.isfinite(v) for v in (a.timeout, a.grace, a.delay)) or a.timeout <= 0 or a.grace < 0 or a.delay < 0:
            raise ValueError('Invalid timeout/grace/delay')
        if sys.platform != 'win32':
            raise ValueError('This runner is validated for Windows only; port explicitly for other hosts.')
        dst = regular_directory(a.dst)
        choices = [dst / 'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe',
                   dst / 'bin/dontstarve_dedicated_server_nullrenderer.exe']
        exe = next((path for path in choices if path.is_file()), None)
        if exe is None or not (dst / 'mods').is_dir():
            raise ValueError('Invalid game installation or missing dedicated binary')
        if a.script and not Path(a.script).is_file():
            raise ValueError(f'Missing behavior script: {a.script}')
        options = json.loads(Path(a.config).read_text(encoding='utf-8-sig')) if a.config else {}
        if not isinstance(options, dict) or any(k not in {str(i) for i in range(len(a.mods))} or not isinstance(v, dict) for k, v in options.items()):
            raise ValueError('--config must map valid zero-based mod indexes to option objects')
        lua_value(options)
        run_id = uuid.uuid4().hex
        storage = (Path(a.storage_root) if a.storage_root else Path(tempfile.gettempdir()) / 'dst_mod_engineering').resolve() / run_id
        if not str(storage).isascii():
            raise ValueError('Use an ASCII --storage-root; this Windows engine failed to read/write a tested Chinese save path.')
        run_dir = Path(a.out).resolve() / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        record = {'run_id': run_id, 'utc': datetime.now(timezone.utc).isoformat(), 'dst': str(dst),
                  'binary': str(exe), 'scope': 'Offline single shard, no real clients',
                  'staged_mods': [], 'options': options, 'result': None,
                  'ownership_version': 1, 'mods_root': str(regular_directory(dst / 'mods')),
                  'owned_stages': [], 'process': None, 'keep_staged': a.keep_staged, 'evidence_dir': str(run_dir)}
        checkpoint = lambda: write_manifest(record, run_dir)
        checkpoint()
        archive = dst / 'data/databundles/scripts.zip'
        if archive.is_file():
            record['scripts_zip_sha256'] = sha(archive)
        for i, source in enumerate(a.mods):
            record['staged_mods'].append(stage_mod(source, dst / 'mods', run_id, i,
                                                 record['owned_stages'], checkpoint))
        expected = [m['key'] for m in record['staged_mods']]
        runner = stage_runner(dst / 'mods', run_id, a.script, a.delay, expected,
                              record['owned_stages'], checkpoint)
        record['runner'] = runner
        snapshot_errors = snapshot_stages(record, run_dir)
        if snapshot_errors:
            raise OSError('; '.join(snapshot_errors))
        port = free_udp_port()
        keys = [m['key'] for m in record['staged_mods']] + [runner['key']]
        storage, cluster = write_cluster(storage, keys, port, options)
        command = [str(exe), '-offline', '-console', '-persistent_storage_root', str(storage),
                   '-conf_dir', 'DME', '-cluster', 'Cluster', '-shard', 'Master', '-port', str(port)]
        record.update(command=command, cluster=str(cluster), port=port)
        checkpoint()
        print(f'Run: {run_id}\nEvidence: {run_dir}', flush=True)
        record['result'] = run_server(command, exe.parent, run_dir / 'console.log', run_id,
                                      a.timeout, a.grace, a.quiet, expected, record, checkpoint)
        print('RESULT: ' + ('PASS' if record['result']['passed'] else 'FAIL'))
        if record['result']['failure']:
            print(record['result']['failure'])
        test_exit_code = 0 if record['result']['passed'] else 1
        return test_exit_code
    except KeyboardInterrupt:
        if record is not None:
            record['result'] = {'passed': False, 'failure': 'interrupted', 'kind': 'interrupted'}
        print('INTERRUPTED', file=sys.stderr)
        test_exit_code = 130
        return test_exit_code
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        if record is not None:
            record['cleanup_command_error' if a.cleanup_manifest else 'error'] = str(e)
        print(f'ERROR: {e}', file=sys.stderr)
        test_exit_code = 2
        return test_exit_code
    finally:
        if record is not None and run_dir is not None and not a.cleanup_manifest:
            evidence_errors = []
            try:
                write_manifest(record, run_dir)
            except OSError as error:
                evidence_errors.append(f'Cannot save result before cleanup: {error}')
            evidence_errors.extend(snapshot_stages(record, run_dir))
            if record.get('cluster') and not (record.get('process') or {}).get('running', False):
                try:
                    cluster = Path(record['cluster'])
                    check_tree(cluster)
                    cluster_snapshot = run_dir / 'cluster'
                    shutil.copytree(cluster, cluster_snapshot, dirs_exist_ok=True, symlinks=True)
                    record['cluster_snapshot'] = str(cluster_snapshot)
                except (OSError, ValueError) as error:
                    evidence_errors.append(f'Cluster snapshot: {error}')
            report = cleanup_staged(record, dst / 'mods', a.keep_staged)
            if (record.get('process') or {}).get('running'):
                evidence_errors.append('Run process could not be stopped; stages retained')
            report['evidence_errors'] = evidence_errors
            incomplete = report['status'] not in ('complete', 'kept') or bool(evidence_errors)
            record['test_exit_code'] = test_exit_code
            record['exit_code'] = 3 if test_exit_code == 0 and incomplete else test_exit_code
            for error in evidence_errors + report['errors']:
                print(f'CLEANUP ERROR: {error}', file=sys.stderr)
            try:
                write_manifest(record, run_dir)
            except OSError as error:
                print(f'MANIFEST ERROR: {error}', file=sys.stderr)
                incomplete = True
            if test_exit_code == 0 and incomplete:
                return 3


if __name__ == '__main__':
    raise SystemExit(main())

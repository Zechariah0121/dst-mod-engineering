"""Isolated Windows DST headless smoke/behavior runner. Standard library only.

Always snapshots the requested source into unique mod folders. Evidence is kept
under --out. Staged game folders are kept too: inspect their manifest before
manual cleanup. No shared response files and no implicit async success.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import queue
import shutil
import socket
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


def stage_mod(source, mods_root, run_id, index):
    source, mods_root = Path(source).resolve(), Path(mods_root).resolve()
    if not (source / 'modinfo.lua').is_file():
        raise ValueError(f'Not a mod folder: {source}')
    key = f'_dme_test_{run_id}_{index}'
    target = mods_root / key
    if target.exists():
        raise ValueError(f'Staging collision: {target}')
    # Do not silently follow a symlink/junction into unrelated data.
    for path in [source, *source.rglob('*')]:
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError(f'Staging requires a regular source tree: {path}')
    before = file_manifest(source)
    shutil.copytree(source, target)
    after = file_manifest(target)
    if before != after or before != file_manifest(source):
        raise ValueError(f'Source changed while staging: {source}; snapshot retained at {target}')
    return {'source': str(source), 'key': key, 'staged': str(target), 'sha256': after}


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


def stage_runner(mods_root, run_id, script=None, delay=2, expected=()):
    key = f'_dme_test_{run_id}_runner'
    target = Path(mods_root) / key
    target.mkdir()
    (target / 'modinfo.lua').write_text(RUNNER_INFO, encoding='utf-8')
    body = SCRIPT_BODY if script else 'test.Done("world smoke only")'
    content = (RUNNER_TEMPLATE.replace('__RUN_ID__', run_id).replace('__DELAY__', str(delay))
               .replace('__BODY__', body).replace('__EXPECTED__', lua_value(list(expected))))
    (target / 'modmain.lua').write_text(content, encoding='utf-8')
    if script:
        shutil.copyfile(script, target / 'test_script.lua')
    return {'key': key, 'staged': str(target), 'sha256': file_manifest(target)}


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


def run_server(command, cwd, log_path, run_id, timeout, grace, quiet, expected=()):
    result = Outcome(run_id, expected)
    output = queue.Queue()
    start = time.monotonic()
    done_at = None
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    proc = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding='utf-8', errors='replace', text=True, creationflags=flags)

    def pump():
        with Path(log_path).open('w', encoding='utf-8') as log:
            for line in proc.stdout:
                log.write(line)
                log.flush()
                output.put(line)

    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    try:
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
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        thread.join(timeout=5)
        if thread.is_alive():
            result.failure = result.failure or 'log reader did not finish; result incomplete'
        while not output.empty():
            result.consume(output.get_nowait())
        proc.stdout.close()
    return {**vars(result), 'passed': result.passed(), 'returncode': proc.returncode,
            'elapsed_seconds': round(time.monotonic() - start, 2), 'pid': proc.pid,
            'observation_after_done_seconds': grace, 'log': str(log_path)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mods', nargs='+', help='Exact source directories; copies always get unique names')
    p.add_argument('--dst', required=True, help='Installed game root')
    p.add_argument('--out', required=True, help='Evidence parent; a unique run directory is created')
    p.add_argument('--storage-root', help='ASCII parent for engine saves (default: OS temp/dst_mod_engineering)')
    p.add_argument('--script', help='Lua script; must explicitly call TEST.Done() after ALL assertions')
    p.add_argument('--config', help='JSON object keyed by zero-based source index, e.g. {"0":{"option":true}}')
    p.add_argument('--timeout', type=float, default=240)
    p.add_argument('--grace', type=float, default=3, help='Post-Done log observation window')
    p.add_argument('--delay', type=float, default=2, help='Seconds after AddSimPostInit before test')
    p.add_argument('--quiet', action='store_true')
    a = p.parse_args()
    record = None
    run_dir = None
    try:
        if not all(math.isfinite(v) for v in (a.timeout, a.grace, a.delay)) or a.timeout <= 0 or a.grace < 0 or a.delay < 0:
            raise ValueError('Invalid timeout/grace/delay')
        if sys.platform != 'win32':
            raise ValueError('This runner is validated for Windows only; port explicitly for other hosts.')
        dst = Path(a.dst).resolve()
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
                  'staged_mods': [], 'options': options, 'result': None}
        archive = dst / 'data/databundles/scripts.zip'
        if archive.is_file():
            record['scripts_zip_sha256'] = sha(archive)
        for i, source in enumerate(a.mods):
            record['staged_mods'].append(stage_mod(source, dst / 'mods', run_id, i))
        expected = [m['key'] for m in record['staged_mods']]
        runner = stage_runner(dst / 'mods', run_id, a.script, a.delay, expected)
        record['runner'] = runner
        port = free_udp_port()
        keys = [m['key'] for m in record['staged_mods']] + [runner['key']]
        storage, cluster = write_cluster(storage, keys, port, options)
        command = [str(exe), '-offline', '-console', '-persistent_storage_root', str(storage),
                   '-conf_dir', 'DME', '-cluster', 'Cluster', '-shard', 'Master', '-port', str(port)]
        record.update(command=command, cluster=str(cluster), port=port)
        (run_dir / 'manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Run: {run_id}\nEvidence: {run_dir}', flush=True)
        record['result'] = run_server(command, exe.parent, run_dir / 'console.log', run_id,
                                      a.timeout, a.grace, a.quiet, expected)
        print('RESULT: ' + ('PASS' if record['result']['passed'] else 'FAIL'))
        if record['result']['failure']:
            print(record['result']['failure'])
        print('Staged folders retained; exact owned paths are in manifest.json.')
        return 0 if record['result']['passed'] else 1
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        if record is not None:
            record['error'] = str(e)
        print(f'ERROR: {e}', file=sys.stderr)
        return 2
    finally:
        if record is not None and run_dir is not None:
            (run_dir / 'manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())

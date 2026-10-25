"""Portable KB entrypoint. Prepare authorized local sources before starting MCP."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess

ROOT = Path(__file__).resolve().parent
# Locate our packaged helper even when the caller uses Python isolated mode.
# Never depend on the client's working directory or inherited PYTHONPATH.
sys.path.insert(0, str(ROOT))
from prepare_sources import PreparationError, prepared_runtime


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['serve', 'status', 'validate', 'reindex', 'call', 'mcp-config'])
    parser.add_argument('--tool')
    parser.add_argument('--arguments-file', type=Path)
    parser.add_argument('--source-epoch', choices=['759671', '756039', 'original48-w1-f35a16fad3f4e44a'])
    args = parser.parse_args(argv)
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ is required')
    try:
        with sqlite3.connect(':memory:') as database:
            database.execute('CREATE VIRTUAL TABLE runtime_fts5_check USING fts5(value)')
    except sqlite3.Error as exc:
        parser.error('This Python must include SQLite FTS5: ' + str(exc))
    if args.command != 'call' and (args.tool or args.arguments_file or args.source_epoch):
        parser.error('--tool, --arguments-file and --source-epoch apply only to call')
    if args.command == 'mcp-config':
        print(json.dumps({'mcpServers': {'dst_engineering_kb': {
            'command': sys.executable,
            'args': ['-B', '-X', 'utf8', str(ROOT / 'run_kb.py'), 'serve']
        }}}, ensure_ascii=False, indent=2))
        return 0
    try:
        values = None
        if args.command == 'call':
            if not args.tool:
                parser.error('call requires --tool')
            values = json.loads(args.arguments_file.read_text(encoding='utf-8-sig')) if args.arguments_file else {}
            if not isinstance(values, dict):
                parser.error('Arguments must be a JSON object')
            if args.source_epoch:
                if values.get('source_epoch', args.source_epoch) != args.source_epoch:
                    parser.error('Conflicting source_epoch values')
                values['source_epoch'] = args.source_epoch
        config, build = prepared_runtime(ROOT)
        command = [sys.executable, '-B', '-X', 'utf8', str(build / 'dst-kb-service' / 'dst_kb_cli.py'),
                   '--config', str(config), args.command]
        if values is not None:
            command += ['--tool', args.tool, '--arguments', json.dumps(values, ensure_ascii=False)]
        env = dict(os.environ)
        for name in ('DST_KB_PATH', 'DST_KB_INDEX', 'DST_KB_CONFIG'):
            env.pop(name, None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        return subprocess.run(command, env=env).returncode
    except (PreparationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': {'code': getattr(exc, 'code', 'CONFIG_ERROR'), 'message': str(exc)},
                          'service_started': False, 'client_configuration_modified': False},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

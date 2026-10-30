"""Portable KB entrypoint: public catalog or fully source-verified MCP."""
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
    supplied = list(sys.argv[1:] if argv is None else argv)
    if supplied and supplied[0] == 'maintain-sources':
        from scripts.source_compatibility import main as compatibility_main
        return compatibility_main(supplied[1:])
    parser = argparse.ArgumentParser(description=__doc__, epilog='maintain-sources assess|assess-registered|locate|legacy-inventory|legacy-assess: read-only maintenance of any explicit target ZIP; run maintain-sources --help for options.')
    parser.add_argument('command', choices=['serve', 'status', 'validate', 'reindex', 'call', 'mcp-config', 'maintain-sources'])
    parser.add_argument('--tool')
    parser.add_argument('--arguments-file', type=Path)
    parser.add_argument('--source-epoch', choices=['759671'])
    parser.add_argument('--mode', choices=['auto', 'full', 'catalog'], default='auto',
                        help='auto uses verified public review for unprepared sources or package drift with a visible reason; cache damage stays an error; full requires verified sources')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ is required')
    if args.command != 'call' and (args.tool or args.arguments_file or args.source_epoch):
        parser.error('--tool, --arguments-file and --source-epoch apply only to call')
    if args.command == 'mcp-config':
        print(json.dumps({'mcpServers': {'dst_engineering_kb': {
            'command': sys.executable,
            'args': ['-B', '-X', 'utf8', str(ROOT / 'run_kb.py'), 'serve', '--mode', args.mode]
        }}}, ensure_ascii=False, indent=2))
        return 0
    try:
        fallback_notice = None
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
        config = build = None
        if args.mode != 'catalog':
            try:
                config, build = prepared_runtime(ROOT)
            except PreparationError as exc:
                if args.mode != 'auto':
                    raise
                from scripts.catalog_fallback_policy import catalog_fallback
                fallback_notice = catalog_fallback(args.mode, exc.code, ROOT)
                if fallback_notice is None:
                    raise
        if build is None:
            sys.path.insert(0, str(ROOT / 'dst-kb-service'))
            from dst_kb.public_catalog import main as catalog_main
            from dst_kb.config import KBError
            try:
                return catalog_main(ROOT, args.command, args.tool, values, fallback_notice=fallback_notice)
            except KBError as exc:
                raise PreparationError(exc.code, str(exc)) from exc
        try:
            with sqlite3.connect(':memory:') as database:
                database.execute('CREATE VIRTUAL TABLE runtime_fts5_check USING fts5(value)')
        except sqlite3.Error as exc:
            raise PreparationError('FTS5_REQUIRED', 'Full MCP requires SQLite FTS5: ' + str(exc)) from exc
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

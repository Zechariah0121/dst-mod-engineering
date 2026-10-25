"""Regenerate or check the published full-service MCP tools contract."""
import argparse
import json
from pathlib import Path

from dst_kb.mcp_server import TOOLS


def document():
    return {'contract_version': '1', 'tools': TOOLS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = Path(__file__).resolve().parent / 'docs/mcp-tools.json'
    expected = document()
    if args.check:
        actual = json.loads(target.read_text(encoding='utf-8'))
        if actual != expected:
            parser.exit(1, 'MCP schema differs from mcp_server.TOOLS; run export_mcp_tools.py\n')
    else:
        target.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

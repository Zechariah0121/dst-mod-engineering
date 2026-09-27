"""Lua syntax + conservative direct component/replica declaration review.

Requires luaparser. A declaration match is not a runtime/API-signature check.
Does not resolve aliases, inheritance, dynamic patches or engine C++ methods.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
from dst_zip_tool import scripts_zip, read_member


def parser():
    try:
        from luaparser import ast, astnodes
    except ImportError as e:
        raise ValueError('luaparser is required; select an existing Python environment with it installed.') from e
    return ast, astnodes


def parse_lua(text):
    ast, _ = parser()
    with contextlib.redirect_stderr(io.StringIO()):
        return ast.parse(text)


def name(node):
    _, n = parser()
    if isinstance(node, n.Name):
        return node.id
    if isinstance(node, n.String):
        return node.s.decode() if isinstance(node.s, bytes) else node.s
    return None


def direct_calls(tree):
    ast, n = parser()
    for node in ast.walk(tree):
        if not isinstance(node, n.Invoke) or not isinstance(node.source, n.Index):
            continue
        component = node.source
        side = component.value
        if isinstance(side, n.Index) and name(side.idx) in ('components', 'replica'):
            comp, method = name(component.idx), name(node.func)
            if comp and method:
                yield {'side': name(side.idx), 'component': comp, 'method': method,
                       'line': getattr(getattr(node, '_first_token', None), 'line', None)}


def declarations(tree):
    ast, n = parser()
    classes = set()
    for node in tree.body.body:
        if isinstance(node, n.Return):
            classes.update(name(v) for v in node.values if name(v))
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, n.Method) and name(node.source) in classes:
            methods.add(name(node.name))
        elif isinstance(node, n.Function) and isinstance(node.name, n.Index) and name(node.name.value) in classes:
            methods.add(name(node.name.idx))
        elif isinstance(node, n.Assign):
            for target, value in zip(node.targets, node.values):
                if (isinstance(target, n.Index) and name(target.value) in classes
                        and isinstance(value, n.AnonymousFunction)):
                    methods.add(name(target.idx))
    return methods


def review(target, archive=None, vanilla=None):
    root = Path(target).resolve()
    if not root.is_dir():
        raise ValueError(f'Mod directory does not exist: {root}')
    paths = sorted(root.rglob('*.lua'))
    if not paths:
        raise ValueError('No Lua files found; nothing was checked.')
    if vanilla:
        vanilla = Path(vanilla).resolve()
        if not (vanilla / 'components').is_dir():
            raise ValueError('--scripts-dir must directly contain components/, prefabs/, etc.')
    elif archive is None:
        raise ValueError('Current vanilla --scripts-dir or archive is required.')
    parser()
    errors, results, cache = [], [], {}
    for path in paths:
        try:
            tree = parse_lua(path.read_text(encoding='utf-8-sig'))
        except Exception as e:
            errors.append({'file': str(path.relative_to(root)), 'error': str(e)})
            continue
        for call in direct_calls(tree):
            call['file'] = str(path.relative_to(root))
            key = (call['side'], call['component'])
            if key not in cache:
                suffix = '_replica' if key[0] == 'replica' else ''
                relative = f'components/{key[1]}{suffix}.lua'
                custom = root / 'scripts' / relative
                try:
                    if custom.is_file():
                        content, origin = custom.read_text(encoding='utf-8-sig'), str(custom)
                    elif vanilla:
                        content, origin = (vanilla / relative).read_text(encoding='utf-8-sig'), str(vanilla / relative)
                    else:
                        content, origin = read_member(archive, relative).decode('utf-8-sig'), f'{archive}!scripts/{relative}'
                    cache[key] = (declarations(parse_lua(content)), origin, None)
                except Exception as e:
                    cache[key] = (set(), relative, str(e))
            methods, origin, error = cache[key]
            call.update(status='DECLARED' if call['method'] in methods else 'NEEDS_REVIEW', source=origin)
            if error:
                call['source_error'] = error
            results.append(call)
    unresolved = sum(c['status'] != 'DECLARED' for c in results)
    return {'scope': 'Syntax and direct colon-call declaration lookup only; no runtime/signature proof.',
            'mod': str(root), 'lua_files': len(paths), 'syntax_errors': errors,
            'direct_calls': len(results), 'needs_review': unresolved, 'calls': results,
            'limitations': ['Aliases/dynamic calls not enumerated', 'No argument/authority/lifetime check',
                            'Engine/inherited/injected methods require manual source or runtime verification']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mod_root')
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument('--dst')
    src.add_argument('--zip')
    src.add_argument('--scripts-dir', help='Extracted scripts directory itself')
    p.add_argument('--out', help='Write JSON report, otherwise print JSON')
    a = p.parse_args()
    try:
        archive = scripts_zip(a.dst, a.zip) if not a.scripts_dir else None
        data = review(a.mod_root, archive, a.scripts_dir)
        output = json.dumps(data, ensure_ascii=False, indent=2)
        if a.out:
            Path(a.out).write_text(output, encoding='utf-8')
            print(f"Lua={data['lua_files']} syntax_errors={len(data['syntax_errors'])} direct_calls={data['direct_calls']} needs_review={data['needs_review']} -> {a.out}")
        else:
            print(output)
        return 1 if data['syntax_errors'] else (2 if data['needs_review'] or not data['direct_calls'] else 0)
    except (OSError, ValueError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

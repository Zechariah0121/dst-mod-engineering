"""Read current DST scripts.zip directly; no extraction cache or game writes."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile


def scripts_zip(dst=None, archive=None):
    if archive:
        path = Path(archive).resolve()
    elif dst:
        path = Path(dst).resolve() / 'data/databundles/scripts.zip'
    else:
        raise ValueError('Provide --dst INSTALL_ROOT or --zip SCRIPTS_ZIP explicitly.')
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise ValueError(f'Not a ZIP archive: {path}')
    return path


def member_name(value):
    value = value.replace('\\', '/')
    p = PurePosixPath(value)
    if p.is_absolute() or ':' in value or '..' in p.parts or not p.parts:
        raise ValueError(f'Unsafe archive member: {value!r}')
    result = str(p)
    return result if result.startswith('scripts/') else 'scripts/' + result


def lua_members(archive):
    with zipfile.ZipFile(archive) as z:
        return sorted(n for n in z.namelist() if n.startswith('scripts/') and n.endswith('.lua'))


def read_member(archive, member):
    name = member_name(member)
    with zipfile.ZipFile(archive) as z:
        return z.read(name)


def extract_one(archive, member, output):
    data = read_member(archive, member)
    target = Path(output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as f:
        f.write(data)
    return target


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--dst')
    source.add_argument('--zip')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('info')
    ls = sub.add_parser('list')
    ls.add_argument('contains', nargs='?', default='')
    show = sub.add_parser('show')
    show.add_argument('member')
    show.add_argument('--start', type=int, default=1)
    show.add_argument('--count', type=int, default=120)
    grep = sub.add_parser('grep')
    grep.add_argument('pattern', help='Literal text by default')
    grep.add_argument('--regex', action='store_true')
    grep.add_argument('--path', default='')
    grep.add_argument('--limit', type=int, default=100)
    extract = sub.add_parser('extract')
    extract.add_argument('member')
    extract.add_argument('--out', required=True, help='Exact new file path; never overwrite')
    a = p.parse_args()
    try:
        archive = scripts_zip(a.dst, a.zip)
        if a.command == 'info':
            print(json.dumps({'archive': str(archive), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                              'lua_files': len(lua_members(archive))}, indent=2))
        elif a.command == 'list':
            print('\n'.join(n for n in lua_members(archive) if a.contains in n))
        elif a.command == 'show':
            if a.start < 1 or a.count < 1:
                raise ValueError('start/count must be positive')
            lines = read_member(archive, a.member).decode('utf-8-sig').splitlines()
            for i in range(a.start - 1, min(len(lines), a.start - 1 + a.count)):
                print(f'{i+1}: {lines[i]}')
        elif a.command == 'grep':
            if a.limit < 1:
                raise ValueError('limit must be positive')
            rx = re.compile(a.pattern if a.regex else re.escape(a.pattern))
            found = 0
            with zipfile.ZipFile(archive) as z:
                for name in lua_members(archive):
                    if a.path not in name:
                        continue
                    for i, line in enumerate(z.read(name).decode('utf-8-sig').splitlines(), 1):
                        if rx.search(line):
                            print(f'{name}:{i}: {line}')
                            found += 1
                            if found >= a.limit:
                                print(f'[stopped at limit={a.limit}; refine query]', file=sys.stderr)
                                return 0
            return 0 if found else 1
        else:
            print(extract_one(archive, a.member, a.out))
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, re.error) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

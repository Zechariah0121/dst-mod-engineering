"""Build reproducible upload bundles from authoritative repository files (stdlib only)."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import posixpath
import re
import stat
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import zipfile

NAME = 'dst-mod-engineering'
REPOSITORY = 'https://github.com/Zechariah0121/dst-mod-engineering'
GENERATOR = 'dst-mod-engineering/web-bundle-v1'
INDEX = 'bundle-index.json'
LOCAL_ONLY_MARKER = '<!-- local-only -->'
ROOT_FILES = ('SKILL.md', 'README.md', 'LICENSE', 'requirements.txt')
DIRECTORIES = {'references': '.md', 'docs': '.md', 'templates': '.md', 'scripts': '.py'}
MAINTAINER_ONLY = frozenset({
    'docs/maintainers.md', 'docs/consolidation.md', 'docs/validation.md',
    'scripts/build_web_bundle.py', 'scripts/build_public_kb.py',
})
COMMON = ('SKILL.md', 'references/web-chat.md', 'references/environment-tools.md',
          'references/testing-release.md')
PROFILE_EXTRA = {
    'starter': ('agent-setup', 'tool-bootstrap'),
    'code-review': ('core-lua-hooks', 'entities-components', 'lifecycle-save', 'items-food-plants',
                    'spells-and-custom-stats', 'cooker-dishes'),
    'networking': ('core-lua-hooks', 'networking-rpc', 'lifecycle-save', 'ui-actions-controls',
                   'spells-and-custom-stats'),
    'assets': ('tool-bootstrap', 'assets-animation', 'dst-mod-tool', 'audio-particles',
               'animation-recipes', 'character-and-equipment-art'),
    'worldgen': ('core-lua-hooks', 'entities-components', 'worldgen-spatial'),
    'full': (),
}
OUTPUT_NAMES = {f'web-{p}.md' for p in PROFILE_EXTRA} | {f'{NAME}.skill.zip', 'web-reading.zip'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def metadata(data):
    return {'sha256': sha(data), 'size': len(data)}


def regular_path(path):
    """Check lexical ancestors before resolve() can hide a symlink/junction."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            entry = part.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(entry.st_mode)
                or getattr(entry, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)):
            raise ValueError(f'Symlink/junction not allowed: {part}')
    return path.resolve()


def source_files(root):
    root = regular_path(root)
    if not root.is_dir():
        raise ValueError(f'Missing source directory: {root}')
    paths = [root / name for name in ROOT_FILES]
    for directory, suffix in DIRECTORIES.items():
        folder = regular_path(root / directory)
        if not folder.is_dir():
            raise ValueError(f'Missing source directory: {folder}')
        paths.extend(sorted(folder.glob('*' + suffix)))
    inputs = {}
    for path in paths:
        path = regular_path(path)
        if not path.is_file():
            raise ValueError(f'Missing source file: {path}')
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if path.suffix == '.md' and any(
                line.strip() == LOCAL_ONLY_MARKER for line in data.decode('utf-8-sig').splitlines()):
            raise ValueError(f'Local-only source cannot be published: {name}')
        if name in MAINTAINER_ONLY:
            continue
        inputs[name] = data
    required = set(COMMON) | {'templates/local-validation.md'}
    required.update(f'references/{name}.md' for names in PROFILE_EXTRA.values() for name in names)
    missing = required - inputs.keys()
    if missing:
        raise ValueError('Missing profile sources: ' + ', '.join(sorted(missing)))
    return dict(sorted(inputs.items()))


def public_link(target, source):
    wrapped = target.startswith('<') and target.endswith('>')
    raw = target[1:-1] if wrapped else target
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return target
    path = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path))) if parsed.path else source
    if path == '..' or path.startswith('../') or path.startswith('/'):
        raise ValueError(f'Link escapes repository in {source}: {target}')
    kind = 'tree' if path in DIRECTORIES or raw.split('#')[0].split('?')[0].endswith('/') else 'blob'
    encoded = quote(path, safe='/.-_')
    rewritten = urlunsplit(('https', 'github.com', f'/Zechariah0121/{NAME}/{kind}/main/{encoded}',
                            parsed.query, parsed.fragment))
    return '<' + rewritten + '>' if wrapped else rewritten


def rewrite_links(text, source):
    """Rewrite Markdown destinations outside fenced code; preserve examples verbatim."""
    inline = re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^\s)]+)')
    linked_image = re.compile(r'(\[!\[[^\]\n]*\]\((?:<[^>\n]+>|[^)\n]+)\)\]\()(<[^>\n]+>|[^\s)]+)')
    definition = re.compile(r'^(\s{0,3}\[[^\]\n]+\]:\s*)(<[^>\n]+>|\S+)')
    fence = None
    lines = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            lines.append(line)
            continue
        if fence is None:
            replace = lambda match: match.group(1) + public_link(match.group(2), source)
            line = inline.sub(replace, line)
            line = linked_image.sub(replace, line)
            line = definition.sub(replace, line)
        lines.append(line)
    return ''.join(lines)


def zip_bytes(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return output.getvalue()


def make_outputs(root):
    inputs = source_files(root)
    hashes = {name: sha(data) for name, data in inputs.items()}
    fingerprint = sha(json_bytes(hashes))
    profiles, outputs = {}, {}
    for profile, names in PROFILE_EXTRA.items():
        selected = list(COMMON) + [f'references/{name}.md' for name in names]
        if profile == 'full':
            selected += [name for name in inputs if name.endswith('.md')]
        selected.append('LICENSE')
        selected = list(dict.fromkeys(selected))
        profiles[profile] = selected
        sections = [f'# {NAME} / web-{profile}\n\n',
                    f'生成器：`{GENERATOR}`；源码指纹：`{fingerprint}`。\n\n',
                    '这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，'
                    '不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；'
                    '上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。\n\n',
                    '本包包含：\n' + ''.join(f'- `{name}`\n' for name in selected) + '\n']
        for name in selected:
            text = inputs[name].decode('utf-8')
            sections.extend([f'\n---\n\n## 来源：`{name}`\n\n原始 SHA-256：`{hashes[name]}`\n\n',
                             rewrite_links(text, name), '\n'])
        outputs[f'web-{profile}.md'] = (''.join(sections).rstrip('\n') + '\n').encode('utf-8')
    reading = {name: data for name, data in outputs.items()}
    reading['local-validation.md'] = inputs['templates/local-validation.md']
    reading['LICENSE'] = inputs['LICENSE']
    reading['reading-index.json'] = json_bytes({
        'generator': GENERATOR, 'source_fingerprint': fingerprint, 'inputs': hashes,
        'profiles': profiles, 'outputs': {name: metadata(data) for name, data in reading.items()}})
    outputs['web-reading.zip'] = zip_bytes(reading)
    outputs[f'{NAME}.skill.zip'] = zip_bytes({f'{NAME}/{name}': data for name, data in inputs.items()})
    outputs[INDEX] = json_bytes({'generator': GENERATOR, 'source_fingerprint': fingerprint,
                                'inputs': hashes, 'profiles': profiles,
                                'outputs': {name: metadata(data) for name, data in outputs.items()}})
    return dict(sorted(outputs.items()))


def output_path(source, output):
    source, output = regular_path(source), regular_path(output)
    if output == source or source.is_relative_to(output):
        raise ValueError('Output must not contain or equal the source root')
    if output.is_relative_to(source) and output.relative_to(source).parts[0] != 'dist':
        raise ValueError('Output inside source is only allowed below dist/')
    if output.exists() and not output.is_dir():
        raise ValueError('Output is not a directory')
    return output


def existing_files(output):
    if not output.exists():
        return {}
    found = {}
    for path in output.iterdir():
        regular_path(path)
        if not path.is_file():
            raise ValueError(f'Unexpected output directory or special file: {path}')
        found[path.name] = path.read_bytes()
    return found


def check_outputs(output, expected):
    actual = existing_files(output)
    return ([f'Missing: {name}' for name in sorted(expected.keys() - actual.keys())]
            + [f'Extra: {name}' for name in sorted(actual.keys() - expected.keys())]
            + [f'Changed: {name}' for name in sorted(actual.keys() & expected.keys()) if actual[name] != expected[name]])


def verify_ownership(actual):
    if not actual:
        return
    if INDEX not in actual:
        raise ValueError('Nonempty output has no ownership index; choose a new directory')
    try:
        index = json.loads(actual[INDEX])
        owned = index['outputs']
        if (set(index) != {'generator', 'source_fingerprint', 'inputs', 'profiles', 'outputs'}
                or actual[INDEX] != json_bytes(index)
                or index['source_fingerprint'] != sha(json_bytes(index['inputs']))):
            raise ValueError('Ownership index was modified or is invalid')
        if index['generator'] != GENERATOR or not isinstance(owned, dict) or set(owned) != OUTPUT_NAMES:
            raise ValueError('Unrecognized ownership index')
        if set(actual) - set(owned) - {INDEX}:
            raise ValueError('Extra output files are not owned by this builder')
        for name in set(actual) & set(owned):
            if metadata(actual[name]) != owned[name]:
                raise ValueError(f'Generated file was modified; refusing overwrite: {name}')
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid ownership index; refusing overwrite') from exc


def write_outputs(output, expected):
    before = existing_files(output)
    verify_ownership(before)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.dme-web-', dir=output.parent)).resolve()
    if stage.parent != output.parent.resolve():
        raise ValueError('Unexpected staging directory')
    replaced = []
    created_output = not output.exists()
    try:
        for name, data in expected.items():
            (stage / name).write_bytes(data)
        if existing_files(output) != before:
            raise ValueError('Output changed during build; retry after inspecting it')
        output.mkdir(exist_ok=True)
        for name in sorted(expected, key=lambda name: (name == INDEX, name)):
            os.replace(stage / name, output / name)
            replaced.append(name)
    except Exception:
        for name in reversed(replaced):
            if name in before:
                (stage / name).write_bytes(before[name])
                os.replace(stage / name, output / name)
            else:
                (output / name).unlink()
        if created_output and output.exists() and not any(output.iterdir()):
            output.rmdir()
        raise
    finally:
        for path in stage.iterdir():
            path.unlink()
        stage.rmdir()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', action='store_true', help='Compare only; do not create or update files')
    args = parser.parse_args(argv)
    try:
        output = output_path(args.source, args.out or args.source / 'dist/web')
        expected = make_outputs(args.source)
        if args.check:
            differences = check_outputs(output, expected)
            print('\n'.join(differences) if differences else 'Web bundles are current.')
            return 1 if differences else 0
        write_outputs(output, expected)
        print(f'Built {len(expected)} files in {output}')
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

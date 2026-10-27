"""Build one reproducible, payload-free Skill + knowledge + MCP release (stdlib)."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
import zipfile

NAME = 'dst-mod-engineering'
VERSION = 'v2026.10.27.1'
ARCHIVE = NAME + '.zip'
CHECKSUMS = 'SHA256SUMS.txt'
MANIFEST = 'RELEASE-MANIFEST.json'
ROOT_FILES = ('SKILL.md', 'README.md', 'README.en.md', 'LICENSE', 'requirements.txt',
              'prepare_sources.py', 'run_kb.py', 'retrieval-config.json',
              'source-epochs.json', 'source-payload-recipe.json', 'PUBLICATION-ORIGIN-MAP.json')
DIRECTORIES = {'references': '.md', 'docs': '.md', 'templates': '.md', 'examples': '.json'}
SCRIPTS = ('dst_zip_tool.py', 'check_api.py', 'dst_modtest.py', 'source_payload.py', 'public_rebind.py', 'source_compatibility.py', 'catalog_fallback_policy.py', 'register_mechanisms.py', 'legacy_adapter.py')
SERVICE_FILES = ('LICENSE', 'README.md', 'config.example.json', 'dst_kb_cli.py', 'export_mcp_tools.py')
SERVICE_DATA = ('dst-kb-service/dst_kb/contract_map.json',
                'dst-kb-service/dst_kb/source_identity_map.json',
                'dst-kb-service/dst_kb/projection_profiles.json',
                'dst-kb-service/docs/mcp-tools.json')
MAINTAINER_DOCS = {'docs/maintainers.md', 'docs/validation.md'}
EXPECTED_COUNTS = {'legacy': 64, 'native_ai': 13, 'native_core': 110}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def regular_path(path):
    """Reject links and Windows reparse points before resolving their targets."""
    path = Path(os.path.abspath(path))
    for ancestor in (path, *path.parents):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0)
                & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)):
            raise ValueError(f'Symlink/junction not allowed: {ancestor}')
    return path.resolve()


def source_files(root):
    root = regular_path(root)
    inputs = {}

    def add(name):
        parts = PurePosixPath(name)
        if (parts.is_absolute() or '..' in parts.parts or '\\' in name or ':' in name
                or parts.as_posix() != name):
            raise ValueError('Invalid package path: ' + name)
        path = regular_path(root / name)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or invalid source file: ' + name)
        data = path.read_bytes()
        if path.suffix == '.md' and any(line.strip() == '<!-- local-only -->'
                for line in data.decode('utf-8-sig').splitlines()):
            raise ValueError('Local-only source cannot be published: ' + name)
        inputs[name] = data

    for name in ROOT_FILES:
        add(name)
    for directory, suffix in DIRECTORIES.items():
        folder = regular_path(root / directory)
        if not folder.is_dir():
            raise ValueError('Missing source directory: ' + directory)
        for path in sorted(folder.glob('*' + suffix)):
            name = path.relative_to(root).as_posix()
            if name not in MAINTAINER_DOCS:
                add(name)
    for name in SCRIPTS:
        add('scripts/' + name)
    for name in SERVICE_FILES:
        add('dst-kb-service/' + name)
    for directory, suffix in [('dst-kb-service/dst_kb', '.py'), ('dst-kb-service/dst_kb', '.json'),
                               ('dst-kb-service/docs', '.md'), ('dst-kb-service/docs', '.json'),
                               ('dst-kb-service/tests', '.py'),
                               ('epoch-assets/759671', '.json')]:
        folder = regular_path(root / directory)
        if not folder.is_dir():
            raise ValueError('Missing source directory: ' + directory)
        for path in sorted(folder.glob('*' + suffix)):
            add(path.relative_to(root).as_posix())
    if 'dst-kb-service/dst_kb/mcp_server.py' not in inputs:
        raise ValueError('Missing MCP implementation')
    for name in SERVICE_DATA:
        add(name)
    for name in ('contract_map.json', 'source_identity_map.json', 'source-manifest.json'):
        add('epoch-assets/759671/' + name)
    epochs = json.loads(inputs['source-epochs.json'])
    if epochs.get('default_source_epoch') != '759671' or set(epochs.get('epochs', {})) != {'759671'}:
        raise ValueError('Release must contain only the current 759671 runtime environment')

    add('knowledge/PACKAGE-MANIFEST.json')
    package = json.loads(inputs['knowledge/PACKAGE-MANIFEST.json'])
    seen = set()
    for row in package['files']:
        name = row['path']
        if name in seen or name == 'PACKAGE-MANIFEST.json':
            raise ValueError('Duplicate knowledge publication input: ' + name)
        seen.add(name)
        add('knowledge/' + name)
        data = inputs['knowledge/' + name]
        if row['sha256'] != sha(data) or row['bytes'] != len(data):
            raise ValueError('Knowledge publication commitment changed: ' + name)
    catalog = json.loads(inputs['knowledge/CATALOG.json'])
    entries = catalog['entries']
    counts = {family: sum(row['family'] == family for row in entries) for family in EXPECTED_COUNTS}
    registry_file = root / 'knowledge/FAMILY-REGISTRY.json'
    if registry_file.is_file():
        import importlib.util
        spec = importlib.util.spec_from_file_location('release_families', root / 'dst-kb-service/dst_kb/family_registry.py')
        families = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(families)
        families.validate_catalog(root / 'knowledge', catalog, families.load(root / 'knowledge'))
    elif counts != EXPECTED_COUNTS or len(entries) != 187 or len({row['id'] for row in entries}) != 187:
        raise ValueError('Knowledge catalog must contain exactly 64 + 13 + 110 unique records')
    for row in entries:
        if 'knowledge/' + row['file'] not in inputs:
            raise ValueError('Catalog points outside packaged knowledge: ' + row['file'])
    return dict(sorted(inputs.items()))


def zip_bytes(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def make_outputs(root):
    inputs = source_files(root)
    manifest = {'schema': 'dst-complete-release/1', 'version': VERSION,
                'knowledge_records': len(json.loads(inputs['knowledge/CATALOG.json'])['entries']),
                'knowledge_families': {family: sum(row['family'] == family for row in json.loads(inputs['knowledge/CATALOG.json'])['entries']) for family in sorted({row['family'] for row in json.loads(inputs['knowledge/CATALOG.json'])['entries']})},
                'source_epoch': '759671',
                'files': {name: {'sha256': sha(data), 'bytes': len(data)} for name, data in inputs.items()}}
    files = {NAME + '/' + name: data for name, data in inputs.items()}
    files[NAME + '/' + MANIFEST] = json_bytes(manifest)
    archive = zip_bytes(files)
    return {ARCHIVE: archive, CHECKSUMS: (sha(archive) + '  ' + ARCHIVE + '\n').encode('ascii')}


def output_path(source, output):
    source, output = regular_path(source), regular_path(output)
    if output == source or source.is_relative_to(output):
        raise ValueError('Output must not contain or equal source root')
    if output.is_relative_to(source) and output.relative_to(source).parts[0] != 'dist':
        raise ValueError('Output inside source is only allowed below dist/')
    if output.exists() and not output.is_dir():
        raise ValueError('Output is not a directory')
    return output


def existing_files(output):
    if not output.exists():
        return {}
    result = {}
    for path in output.iterdir():
        regular_path(path)
        if not path.is_file():
            raise ValueError('Unexpected output directory or special file: ' + str(path))
        result[path.name] = path.read_bytes()
    return result


def check_outputs(output, expected):
    actual = existing_files(output)
    return ([f'Missing: {name}' for name in sorted(expected.keys() - actual.keys())]
            + [f'Extra: {name}' for name in sorted(actual.keys() - expected.keys())]
            + [f'Changed: {name}' for name in sorted(actual.keys() & expected.keys()) if actual[name] != expected[name]])


def verify_ownership(actual):
    if not actual:
        return
    if set(actual) != {ARCHIVE, CHECKSUMS}:
        raise ValueError('Output is not an owned complete release; choose a new directory')
    if actual[CHECKSUMS] != (sha(actual[ARCHIVE]) + '  ' + ARCHIVE + '\n').encode('ascii'):
        raise ValueError('Release was modified; refusing overwrite')
    try:
        with zipfile.ZipFile(io.BytesIO(actual[ARCHIVE])) as archive:
            manifest = json.loads(archive.read(NAME + '/' + MANIFEST))
            expected = {NAME + '/' + name for name in manifest['files']} | {NAME + '/' + MANIFEST}
            if set(archive.namelist()) != expected or manifest['schema'] != 'dst-complete-release/1':
                raise ValueError('Unrecognized release layout')
            for name, row in manifest['files'].items():
                data = archive.read(NAME + '/' + name)
                if row != {'sha256': sha(data), 'bytes': len(data)}:
                    raise ValueError('Release contents differ from manifest')
    except (KeyError, TypeError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise ValueError('Invalid release; refusing overwrite') from exc


def write_outputs(output, expected):
    before = existing_files(output)
    verify_ownership(before)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.dme-release-', dir=output.parent)).resolve()
    replaced = []
    created = not output.exists()
    try:
        for name, data in expected.items():
            (stage / name).write_bytes(data)
        if existing_files(output) != before:
            raise ValueError('Output changed during build')
        output.mkdir(exist_ok=True)
        for name in (ARCHIVE, CHECKSUMS):
            os.replace(stage / name, output / name)
            replaced.append(name)
    except Exception:
        for name in reversed(replaced):
            if name in before:
                (stage / name).write_bytes(before[name])
                os.replace(stage / name, output / name)
            else:
                (output / name).unlink()
        if created and output.exists() and not any(output.iterdir()):
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
    parser.add_argument('--check', action='store_true', help='Compare only; do not write')
    args = parser.parse_args(argv)
    try:
        output = output_path(args.source, args.out or args.source / 'dist/release')
        expected = make_outputs(args.source)
        if args.check:
            differences = check_outputs(output, expected)
            print('\n'.join(differences) if differences else 'Complete release is current.')
            return 1 if differences else 0
        write_outputs(output, expected)
        print(f'Built {ARCHIVE} and {CHECKSUMS} in {output}')
        return 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

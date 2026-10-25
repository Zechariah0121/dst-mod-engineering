"""Assemble explicitly supplied local source into a verified, private runtime cache."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
EPOCHS = ('759671',)
MARKER = '$dst_source_payload_slot'
SCHEMA = 'dst-prepared-local-runtime/1'
RUNTIME_FILES = ('source-epochs.json', 'retrieval-config.json',
                 'source-payload-recipe.json', 'PUBLICATION-ORIGIN-MAP.json')
RUNTIME_TREES = ('knowledge', 'epoch-assets', 'dst-kb-service')


class PreparationError(Exception):
    def __init__(self, code, message, details=None):
        self.code, self.details = code, details or {}
        super().__init__(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8', newline='\n')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def child(root, relative):
    name = PurePosixPath(relative)
    if (not relative or ':' in relative or '\\' in relative or name.is_absolute()
            or '..' in name.parts or name.as_posix() != relative):
        raise PreparationError('INVALID_PATH', 'Expected a package-relative path: ' + str(relative))
    target = root / relative
    for path in (target, *target.parents):
        if path.exists() or path.is_symlink():
            info = path.lstat()
            if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0)
                    & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)):
                raise PreparationError('INVALID_PATH', 'Links/junctions are not runtime inputs: ' + str(path))
        if path == root:
            break
    if not target.resolve().is_relative_to(root.resolve()):
        raise PreparationError('INVALID_PATH', 'Path escaped the package')
    return target


def helper_path(root, name):
    for relative in ('scripts/' + name, name, 'tools/' + name):
        path = child(root, relative)
        if path.is_file():
            return path
    raise PreparationError('PACKAGE_INCOMPLETE', 'Missing helper: ' + name)


def load_helper(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package_inputs(root):
    paths = [child(root, name) for name in RUNTIME_FILES]
    paths += [helper_path(root, name) for name in ('source_payload.py', 'public_rebind.py')]
    paths += [child(root, name) for name in ('prepare_sources.py', 'run_kb.py')]
    for name in RUNTIME_TREES:
        folder = child(root, name)
        if not folder.is_dir():
            raise PreparationError('PACKAGE_INCOMPLETE', 'Missing runtime tree: ' + name)
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(root).as_posix()
            child(root, relative)
            if path.is_file() and not any(p in ('cache', '__pycache__') for p in path.relative_to(folder).parts):
                if path.suffix not in ('.pyc', '.sqlite', '.sqlite3', '.db'):
                    paths.append(path)
    rows = []
    for path in sorted(set(paths)):
        if not path.is_file():
            raise PreparationError('PACKAGE_INCOMPLETE', 'Missing runtime input: ' + path.relative_to(root).as_posix())
        raw = path.read_bytes()
        rows.append({'path': path.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
    return rows


def source_inputs(values):
    if not values:
        raise PreparationError('SOURCE_REQUIRED', 'Supply one or more explicit --source ZIP or directories.')
    result = []
    for value in values:
        path = Path(value).expanduser().resolve()
        if not (path.is_dir() or (path.is_file() and zipfile.is_zipfile(path))):
            raise PreparationError('INVALID_SOURCE', 'Source must be an existing directory or ZIP: ' + str(path))
        if path not in result:
            result.append(path)
    return result


def unique_gaps(report):
    unique = {}
    for gap in report.get('required_gaps', []) + report.get('optional_gaps', []):
        for coordinate in gap.get('coordinates', []):
            key = (coordinate['source_file'], gap['content_sha256'])
            row = unique.setdefault(key, {'source_file': key[0], 'content_sha256': key[1],
                                         'required': False, 'coordinates': []})
            row['required'] |= gap.get('required_for_knowledge_shape', False)
            if coordinate not in row['coordinates']:
                row['coordinates'].append(coordinate)
        if not gap.get('coordinates'):
            unique.setdefault(('', gap['content_sha256']), {'source_file': None,
                'content_sha256': gap['content_sha256'], 'required': gap.get('required_for_knowledge_shape', False),
                'coordinates': [], 'artifact_path': gap['path'], 'pointer': gap['pointer']})
    return list(unique.values())


def remaining_slots(root):
    found = []
    for folder in RUNTIME_TREES:
        for path in (root / folder).rglob('*.json'):
            if MARKER in path.read_text(encoding='utf-8-sig'):
                found.append(path.relative_to(root).as_posix())
    return found


def validate_runtime(root):
    """Run existing data/identity/profile/contract guards, without importing Service."""
    sys.path.insert(0, str(root / 'dst-kb-service'))
    from dst_kb.validation import validate
    from dst_kb.source_epoch_runtime import resolve_epoch, bind_epoch
    from dst_kb import source_identity, facet_contracts, projection_v2
    config = root / 'retrieval-config.json'
    results = []
    for epoch in EPOCHS:
        context = resolve_epoch(config, epoch)
        context.assert_current()
        with bind_epoch(context):
            _, report = validate(context.root)
            if report.get('status') != 'PASS' or report.get('entries') != 187:
                raise PreparationError('VALIDATION_FAILED', 'The original validator did not accept 187 records: ' + epoch)
            core = read(context.root / 'data/nativecore/native-core.json')['entries']
            registry = source_identity._registry()
            accepted = 0
            for record in core:
                accepted += len(registry.rows(record, 'core'))
                facet_contracts._record_map(record)
                projection_v2._profile(record, None)
            declared = sum(len(rows) for rows in registry._rows.values())
            results.append({'source_epoch': epoch, 'validator': report,
                'identity_guard_accepted_rows': accepted,
                'identity_guard_excluded_rows': declared - accepted,
                'contract_record_and_projection_profile_guards': 'PASS',
                'guard_exclusions_preserved': True})
    return {'status': 'PASS_ORIGINAL_DATA_AND_GUARD_CHECKS', 'epochs': results,
            'service_started': False, 'dst_runtime_tested': False}


def check_in_subprocess(root):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for name in ('DST_KB_PATH', 'DST_KB_INDEX', 'DST_KB_CONFIG'):
        env.pop(name, None)
    result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                             '--check-runtime', str(root)], capture_output=True,
                            text=True, encoding='utf-8', env=env)
    if result.returncode:
        raise PreparationError('VALIDATION_FAILED', 'Local source was assembled, but unchanged original guards rejected it.',
                               {'guard_output': result.stderr.strip() or result.stdout.strip()})
    return json.loads(result.stdout)


def build_manifest(root):
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.name != 'RUNTIME-MANIFEST.json':
            raw = path.read_bytes()
            rows.append({'path': path.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
    return {'schema': 'dst-local-runtime-files/1', 'files': rows}


def verify_build(root, expected_manifest):
    manifest_path = child(root, 'RUNTIME-MANIFEST.json')
    if sha(manifest_path.read_bytes()) != expected_manifest:
        raise PreparationError('RUNTIME_CHANGED', 'Prepared runtime manifest changed; prepare sources again.')
    manifest = read(manifest_path)
    declared = set()
    for row in manifest['files']:
        path = child(root, row['path'])
        declared.add(row['path'])
        raw = path.read_bytes()
        if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
            raise PreparationError('RUNTIME_CHANGED', 'Prepared runtime file changed: ' + row['path'])
    actual = {path.relative_to(root).as_posix() for path in root.rglob('*')
              if path.is_file() and path.relative_to(root).parts[0] not in ('cache', 'reports')}
    if actual != declared | {'RUNTIME-MANIFEST.json'}:
        raise PreparationError('RUNTIME_CHANGED', 'Prepared runtime file set changed; prepare sources again.')


def prepared_runtime(root=ROOT):
    """Fail closed before starting a service; template slots are never runtime source."""
    config = child(root, 'cache/runtime/retrieval-config.json')
    if not config.is_file():
        raise PreparationError('SOURCES_NOT_PREPARED',
            'Prepare local sources first: python -B -X utf8 prepare_sources.py --source "<current scripts.zip>" '
            '--source "<authorized historical scripts.zip or directory>". '
            'Public JSON slots are reading templates, not source evidence; a 759671 ZIP alone lacks historical ranges.')
    value = read(config)
    state = value.get('prepared_runtime', {})
    if state.get('schema') != SCHEMA:
        raise PreparationError('SOURCES_NOT_PREPARED', 'Prepared runtime activation is missing or unsupported.')
    if state.get('package_input_sha256') != digest(package_inputs(root)):
        raise PreparationError('PACKAGE_CHANGED', 'Public package inputs changed; prepare sources again.')
    name = state.get('runtime_build', '')
    build_id = name.removeprefix('builds/')
    if not name.startswith('builds/') or len(build_id) != 64 or any(c not in '0123456789abcdef' for c in build_id):
        raise PreparationError('INVALID_PATH', 'Invalid prepared runtime build')
    build = child(root, 'cache/runtime/' + name)
    if value.get('source_epochs_path') != name + '/source-epochs.json':
        raise PreparationError('INVALID_PATH', 'Prepared source catalog does not match activated build')
    verify_build(build, state['runtime_manifest_sha256'])
    catalog = read(build / 'source-epochs.json')
    for epoch in catalog['epochs'].values():
        child(build, epoch['index_path'])
    return config, build


def same_source_inputs(build, sources):
    receipt = read(build / 'PREPARATION-RECEIPT.json')
    previous = receipt.get('source_inputs', [])
    if len(previous) != len(sources) or receipt['hydration']['missing_optional_identity_cache_count']:
        return False
    for row, source in zip(previous, sources):
        if source.is_file():
            if row.get('kind') != 'ZIP' or row.get('archive_sha256') != sha(source.read_bytes()):
                return False
        else:
            if row.get('kind') != 'DIRECTORY':
                return False
            for name, expected in row.get('matched_files', []):
                path = next((child(source, candidate) for candidate in
                    (name, name.removeprefix('scripts/')) if child(source, candidate).is_file()), None)
                if path is None or sha(path.read_bytes()) != expected:
                    return False
    return True


def prepare(root, values):
    root = Path(root).resolve()
    sources = source_inputs(values)
    rows = package_inputs(root)
    package_hash = digest(rows)
    if child(root, 'cache/runtime/retrieval-config.json').is_file():
        try:
            _, previous = prepared_runtime(root)
            if same_source_inputs(previous, sources):
                return {'status': 'LOCAL_RUNTIME_ALREADY_PREPARED',
                    'runtime_build': previous.relative_to(root).as_posix(), 'source_epochs': list(EPOCHS),
                    'client_configuration_modified': False, 'service_started': False,
                    'local_source_payload_do_not_publish': True}
        except (PreparationError, OSError, ValueError, KeyError, TypeError):
            # Rebuild from explicit sources; an existing activation stays intact
            # until the new build independently passes all original checks.
            pass
    runtime = child(root, 'cache/runtime')
    runtime.mkdir(parents=True, exist_ok=True)
    lock = child(root, 'cache/runtime/.prepare.lock')
    try:
        lockfile = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise PreparationError('PREPARATION_BUSY', 'Another preparation holds cache/runtime/.prepare.lock; keep the current runtime.') from exc
    try:
        with lockfile:
            lockfile.write(str(os.getpid()))
        payload = load_helper(helper_path(root, 'source_payload.py'), 'dst_public_source_payload')
        rebind = load_helper(helper_path(root, 'public_rebind.py'), 'dst_public_rebind')
        recipe = read(root / 'source-payload-recipe.json')
        with tempfile.TemporaryDirectory(prefix='.prepare-', dir=runtime) as directory:
            temporary = Path(directory)
            assembled, templates = temporary / 'assembled', temporary / 'templates'
            assembled.mkdir()
            for row in rows:
                name = row['path']
                if name in RUNTIME_FILES or name.split('/')[0] in RUNTIME_TREES:
                    destination = child(assembled, name)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(child(root, name), destination)
            for name in {slot['path'] for slot in recipe['slots']}:
                destination = child(templates, name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(child(root, name), destination)
            hydrated, _ = payload.hydrate(templates, recipe, sources, output_root=assembled)
            if (hydrated.get('missing_required_count') or hydrated.get('missing_noncache_source_literal_count')):
                raise PreparationError('SOURCE_GAP',
                    'Required historical source ranges are missing. Add authorized older sources with another --source; no partial runtime was activated.',
                    {'hydration_status': hydrated['status'], 'missing_required_count': hydrated['missing_required_count'],
                     'missing_noncache_source_literal_count': hydrated['missing_noncache_source_literal_count'],
                     'source_gaps': unique_gaps(hydrated)})
            remaining = remaining_slots(assembled)
            if remaining:
                raise PreparationError('SOURCE_GAP', 'Unresolved source slots remain; no runtime activated.', {'files': remaining})
            rebound, origins = rebind.rebind(assembled, assembled / 'PUBLICATION-ORIGIN-MAP.json')
            if rebound.get('unresolved'):
                raise PreparationError('REBIND_FAILED', 'Typed source commitments could not be rebound.', {'unresolved': rebound['unresolved']})
            write(assembled / 'PUBLICATION-ORIGIN-MAP.json', origins)
            write(assembled / 'retrieval-config.json', {'source_epochs_path': 'source-epochs.json', 'default_source_epoch': '759671'})
            guards = check_in_subprocess(assembled)
            receipt = {'schema': SCHEMA, 'package_input_sha256': package_hash,
                'source_payload_input_sha256': digest(hydrated['matches']),
                'source_inputs': [{'input_index': index, 'kind': 'DIRECTORY' if path.is_dir() else 'ZIP',
                    'archive_sha256': sha(path.read_bytes()) if path.is_file() else None,
                    'matched_files': sorted({match['source_file']: match['provided_file_sha256']
                        for match in hydrated['matches'] if match['source_input_index'] == index}.items())}
                    for index, path in enumerate(sources)],
                'hydration': {'source_slots': hydrated['source_slots'], 'recovered_count': hydrated['recovered_count'],
                    'missing_required_count': 0, 'missing_noncache_source_literal_count': 0,
                    'missing_optional_identity_cache_count': hydrated['missing_optional_count'],
                    'whole_historical_snapshot_identity_inferred': False},
                'rebind': {'typed_reference_updates': len(rebound.get('typed_reference_updates', [])),
                           'historical_source_hashes_globally_replaced': False},
                'guards': guards, 'client_configuration_modified': False, 'local_source_payload_do_not_publish': True}
            write(assembled / 'PREPARATION-RECEIPT.json', receipt)
            manifest = build_manifest(assembled)
            build_id = digest(manifest)
            write(assembled / 'RUNTIME-MANIFEST.json', manifest)
            manifest_hash = sha((assembled / 'RUNTIME-MANIFEST.json').read_bytes())
            builds = child(root, 'cache/runtime/builds')
            builds.mkdir(exist_ok=True)
            final = child(root, 'cache/runtime/builds/' + build_id)
            if final.exists():
                verify_build(final, manifest_hash)
            else:
                assembled.rename(final)
            activation = {'source_epochs_path': 'builds/' + build_id + '/source-epochs.json',
                'default_source_epoch': '759671', 'prepared_runtime': {'schema': SCHEMA,
                    'runtime_build': 'builds/' + build_id, 'package_input_sha256': package_hash,
                    'runtime_manifest_sha256': manifest_hash}}
            pending = temporary / 'activation.json'
            write(pending, activation)
            os.replace(pending, runtime / 'retrieval-config.json')
            return {'status': 'LOCAL_RUNTIME_PREPARED', 'runtime_build': 'cache/runtime/builds/' + build_id,
                    'source_epochs': list(EPOCHS), 'client_configuration_modified': False,
                    'service_started': False, 'local_source_payload_do_not_publish': True}
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', type=Path,
                        help='Explicit authorized scripts ZIP or directory; repeat to supply historical ranges.')
    parser.add_argument('--check-runtime', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10):
            raise PreparationError('PYTHON_VERSION', 'Python 3.10+ is required.')
        if args.check_runtime is not None:
            if args.source:
                parser.error('--source and internal --check-runtime cannot be combined')
            result = validate_runtime(args.check_runtime.resolve())
        else:
            result = prepare(ROOT, args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PreparationError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        result = {'error': {'code': getattr(exc, 'code', 'PREPARATION_FAILED'), 'message': str(exc)},
                  **getattr(exc, 'details', {}), 'activated': False, 'service_started': False}
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

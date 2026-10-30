"""Explicit, local-only Skill update assistant. Never called by serve.

ensure --source <scripts.zip> authorizes one path; later ensure reuses it.
State contains a private local path: do not publish cache/. A successful prepare
changes activation for NEW connections only. No client or running service edits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import prepare_sources as preparation
from scripts import source_compatibility as compatibility
from scripts.catalog_fallback_policy import verify_public_files

SCHEMA = 'dst-skill-source-update/1'
MAX_ZIP = 1024 * 1024 * 1024
MAX_EXPANDED = 2 * MAX_ZIP
MAX_MEMBERS = 20000


class UpdateError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def read(path):
    if path.stat().st_size > 1024 * 1024:
        raise UpdateError('STATE_TOO_LARGE', 'Assistant metadata exceeds 1 MiB.')
    return json.loads(path.read_text(encoding='utf-8'))


def atomic(path, value):
    raw = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if len(raw.encode('utf-8')) > 1024 * 1024:
        raise UpdateError('STATE_TOO_LARGE', 'Assistant metadata exceeds 1 MiB; prior state preserved.')
    fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def fingerprint(path):
    if path.is_symlink() or path.resolve() != path or not path.is_file():
        raise UpdateError('SOURCE_PATH_CHANGED', 'Authorized source must remain the same regular path.')
    before = path.stat()
    if not 0 < before.st_size <= MAX_ZIP:
        raise UpdateError('SOURCE_LIMIT', 'Source ZIP must be nonempty and at most 1 GiB.')
    result = compatibility.file_sha(path)
    after = path.stat()
    if any(getattr(before, field) != getattr(after, field) for field in
           ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')):
        raise UpdateError('SOURCE_CHANGED_DURING_READ', 'Source changed while fingerprinting; try a later ensure.')
    return result


def verify_zip(path):
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS or sum(m.file_size for m in members) > MAX_EXPANDED:
            raise UpdateError('SOURCE_LIMIT', 'ZIP exceeds member or expanded-size limit.')
        names = set()
        for member in members:
            name = member.filename.rstrip('/') if member.is_dir() else member.filename
            compatibility.safe_zip_name(name)
            if name in names or member.flag_bits & 1 or member.file_size > 64 * 1024 * 1024:
                raise UpdateError('UNSAFE_ZIP', 'Duplicate, encrypted or oversized ZIP member.')
            names.add(name)
        if not any(n.startswith('scripts/') and n.endswith('.lua') for n in names):
            raise UpdateError('INVALID_SOURCE', 'Expected an explicit scripts ZIP with scripts/*.lua members.')


def verify_public(root):
    """Verify every public manifest member, even on a suppressed retry.

    This is local integrity, not a signature or semantic catalog admission.
    PublicCatalog still validates its own schema when opened for review.
    """
    knowledge = preparation.child(root, 'knowledge')
    manifest = preparation.read(knowledge / 'PACKAGE-MANIFEST.json')
    rows = manifest['files']
    if not isinstance(rows, list) or not 0 < len(rows) <= 10000:
        raise UpdateError('PUBLIC_PACKAGE_INVALID', 'Invalid public manifest size.')
    seen = set()
    for row in rows:
        name, digest = row['path'], row['sha256']
        if name in seen or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise UpdateError('PUBLIC_PACKAGE_INVALID', 'Duplicate or invalid public commitment.')
        seen.add(name)
        preparation.child(knowledge, name)
    if 'CATALOG.json' not in seen:
        raise UpdateError('PUBLIC_PACKAGE_INVALID', 'Public catalog is not committed.')
    try:
        verify_public_files(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise UpdateError('PUBLIC_PACKAGE_INVALID', 'Public manifest schema, bytes, paths or hashes failed verification.') from exc


def runtime_state(root):
    config = preparation.child(root, 'cache/runtime/retrieval-config.json')
    if not config.exists():
        # Leftover builds are preserved; never guessed or activated.
        return {'status': 'uninitialized', 'historical_build': None}
    try:
        _, build = preparation.prepared_runtime(root)
        return {'status': 'verified', 'historical_build': build.relative_to(root).as_posix()}
    except preparation.PreparationError as exc:
        if exc.code == 'PACKAGE_CHANGED':
            # prepared_runtime verifies the old manifest BEFORE package drift.
            value = preparation.read(config)
            return {'status': 'package_changed', 'historical_build': 'cache/runtime/' + value['prepared_runtime']['runtime_build']}
        raise UpdateError('CACHE_INVALID', 'Cache activation/integrity check failed: ' + exc.code) from exc
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise UpdateError('CACHE_INVALID', 'Cache activation or payload is damaged.') from exc


def sidecar(root, directory, snapshot, key):
    output = preparation.child(directory, 'review-' + key + '-' + uuid.uuid4().hex + '.json')
    with_archive = compatibility.Archive(snapshot)
    try:
        result = compatibility.assess_registered(root / 'knowledge', None, with_archive)
        # Local sidecar: paths refer to public package candidates, never source text.
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        compatibility.publish_new_json(output, rendered)
    finally:
        with_archive.close()
    return output.relative_to(root).as_posix()


def ensure(root=ROOT, source=None, retry=False, status_only=False):
    root = Path(root).resolve()
    directory = preparation.child(root, 'cache/source-update')
    directory.mkdir(parents=True, exist_ok=True)
    state_path = preparation.child(root, 'cache/source-update/state.json')
    lock_path = preparation.child(root, 'cache/source-update/.ensure.lock')
    with preparation.preparation_lock(lock_path):
        state = read(state_path) if state_path.exists() else {'schema': SCHEMA}
        if not isinstance(state, dict) or state.get('schema') != SCHEMA:
            raise UpdateError('STATE_INVALID', 'Assistant state has an unsupported schema.')
        if not isinstance(state.get('attempt', {}), dict) or ('source' in state and not isinstance(state['source'], str)):
            raise UpdateError('STATE_INVALID', 'Assistant state fields are invalid.')
        verify_public(root)
        runtime = runtime_state(root)
        common = {'schema': SCHEMA, 'runtime': runtime, 'runtime_verified': False,
                  'client_configuration_modified': False, 'current_connection_changed': False,
                  'activation_changed': False, 'current_connection_status': 'unknown',
                  'source_identity_is_not_behavior_proof': True}
        if status_only:
            return {**common, 'status': 'STATUS', 'bound': bool(state.get('source')),
                    'authorized_source': state.get('source'), 'last_attempt': state.get('attempt')}
        explicit = source is not None
        if explicit:
            source = Path(source).expanduser().resolve()
        elif state.get('source'):
            source = Path(state['source'])
            if not source.is_absolute():
                raise UpdateError('STATE_INVALID', 'Remembered source must be absolute.')
        else:
            raise UpdateError('SOURCE_REQUIRED', 'First use requires ensure --source <authorized scripts.zip>.')
        source_hash = fingerprint(source)
        common.update(authorized_source=str(source), source_sha256=source_hash)
        package_hash = preparation.digest(preparation.package_inputs(root))
        key = preparation.digest({'source': str(source), 'source_sha256': source_hash,
                                  'package_sha256': package_hash, 'assistant_sha256': compatibility.file_sha(Path(__file__))})
        attempt = state.get('attempt', {})
        if not retry and attempt.get('key') == key:
            if attempt.get('status') == 'prepared' and runtime['status'] == 'verified':
                # Activation may have been replaced by a separate explicit prepare.
                _, build = preparation.prepared_runtime(root)
                if preparation.same_source_inputs(build, [source]):
                    return {**common, 'status': 'UNCHANGED', 'source_sha256': source_hash,
                            'reconnect_required': False, 'message': 'Activation unchanged. Compare the current connection source assessment if needed; no automatic reconnection is requested.'}
            elif attempt.get('status') != 'prepared':
                return {**common, 'status': 'RETRY_SUPPRESSED', 'source_sha256': source_hash,
                        'last_attempt': attempt, 'message': 'Same source/package already attempted; inspect result or use explicit --retry.'}
        # Freeze one authorized input for ALL consumers; prepare never reads a moving game ZIP.
        with tempfile.TemporaryDirectory(prefix='.input-', dir=directory) as temporary:
            snapshot = Path(temporary) / 'scripts.zip'
            with source.open('rb') as incoming, snapshot.open('xb') as outgoing:
                total = 0
                for block in iter(lambda: incoming.read(1024 * 1024), b''):
                    total += len(block)
                    if total > MAX_ZIP:
                        raise UpdateError('SOURCE_LIMIT', 'Source grew beyond ZIP limit.')
                    outgoing.write(block)
            if compatibility.file_sha(snapshot) != source_hash or fingerprint(source) != source_hash:
                raise UpdateError('SOURCE_CHANGED_DURING_READ', 'Source replaced during snapshot; no preparation attempted.')
            state = {'schema': SCHEMA, 'source': str(source), 'attempt': {'key': key, 'status': 'interrupted_or_running',
                     'source_sha256': source_hash, 'package_sha256': package_hash}}
            atomic(state_path, state)  # Survives cancellation; same fingerprint needs explicit retry.
            try:
                verify_zip(snapshot)
                prepared = preparation.prepare(root, [snapshot])
            except (preparation.PreparationError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
                code = getattr(exc, 'code', 'PREPARATION_FAILED')
                attempt = state['attempt']
                attempt.update(status='failed', error_code=code)
                # Busy preparations can still be changing activation: do not call them complete.
                if code == 'SOURCE_GAP':
                    gaps = getattr(exc, 'details', {}).get('source_gaps', [])
                    # Keep actionable locators bounded, never source excerpts.
                    attempt['source_gaps'] = [{k: gap[k] for k in
                        ('source_file', 'content_sha256', 'required', 'artifact_path', 'pointer') if k in gap}
                        for gap in gaps[:1000]]
                    attempt['source_gaps_truncated'] = len(gaps) > 1000
                    attempt['task_followup'] = [
                        'Use the authorized source path and source_sha256 above as the explicit current target; verify its hash before task lookup.',
                        'Use source_gaps to choose task-relevant files; run maintain-sources locate --target <authorized source> --symbol <task symbol>. Do not invent a missing symbol.',
                        'If the original file is missing or has zero matches, repeat locate without --source-file to find relocation.',
                        'Read matched current source with scripts/dst_zip_tool.py; check definition, consumers, authority and lifecycle for the current task.',
                        'Record current-source findings separately from historical KB evidence; never rewrite canonical Scope or HOLD.'
                    ]
                    try:
                        attempt['review_sidecar'] = sidecar(root, directory, snapshot, key)
                    except (OSError, ValueError, KeyError, TypeError, AttributeError, zipfile.BadZipFile) as review_error:
                        attempt['review_error'] = type(review_error).__name__
                atomic(state_path, state)
                verify_public(root)
                historical = runtime_state(root)
                return {**common, 'runtime': historical, 'status': 'SOURCE_REVIEW_REQUIRED' if code == 'SOURCE_GAP' else 'PREPARATION_FAILED',
                        'last_attempt': attempt, 'historical_cache_is_new_evidence': False,
                        'public_manifest_verified': True, 'current_source_check_available': True,
                        'message': 'Historical verified build preserved if listed; it is not evidence for the new input. Review public catalog and current source explicitly.'}
            attempt = state['attempt']
            attempt.update(status='prepared', preparation=prepared)
            # Replacement during prepare cannot contaminate the frozen build, but it is stale.
            current = fingerprint(source)
            after_package = preparation.digest(preparation.package_inputs(root))
            stale = current != source_hash or after_package != package_hash
            atomic(state_path, state)
            verified = runtime_state(root)
            stale = stale or verified['status'] != 'verified'
            activation_changed = verified['historical_build'] != runtime['historical_build']
            return {**common, 'runtime': verified, 'status': 'INPUT_CHANGED_AFTER_PREPARATION' if stale else 'PREPARED',
                    'source_sha256': source_hash, 'activation_changed': activation_changed,
                    'reconnect_required': activation_changed and not stale,
                    'message': 'Frozen snapshot prepared; run ensure again for changed inputs.' if stale else
                    'Strict preparation complete. Reconnect if activation_changed to use the new activation; this connection has not changed.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('ensure', 'status'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--retry', action='store_true', help='Explicitly retry a failed/interrupted fingerprint once')
    args = parser.parse_args(argv)
    if args.command == 'status' and (args.source or args.retry):
        parser.error('status does not bind or retry; use ensure')
    try:
        result = ensure(ROOT, args.source, args.retry, args.command == 'status')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] in ('STATUS', 'PREPARED', 'UNCHANGED') else 2
    except (UpdateError, preparation.PreparationError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': {'code': getattr(exc, 'code', 'UPDATE_FAILED'), 'message': str(exc)},
                          'current_connection_changed': False, 'runtime_verified': False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

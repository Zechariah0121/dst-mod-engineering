"""Independent source assessments; never a source-complete Service runtime.

Only metadata is persisted here. Historical knowledge identity and admission
remain unchanged, even when a supplied source recovers an original range.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .config import KBError

SCHEMA = 'dst-evidence-snapshot/1'


def _raw(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _child(root, name):
    if not isinstance(name, str) or not re.fullmatch(r'[a-f0-9]{64}', name):
        raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Invalid evidence snapshot identity.')
    path = root / 'cache/evidence/snapshots' / (name + '.json')
    for parent in (path, *path.parents):
        if parent.is_symlink() or (parent.exists() and getattr(parent.lstat(), 'st_file_attributes', 0) & 0x400):
            raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Linked evidence snapshot path.')
        if parent == root:
            break
    return path


def active_assessment(package_root):
    """Return None only when no snapshot was activated. Corruption fails closed."""
    return _load(package_root, verify_package=True)


def _load(package_root, verify_package):
    root = Path(package_root).resolve()
    activation = root / 'cache/evidence/active.json'
    # Validate the directory chain even when the activation itself is missing.
    _child(root, '0' * 64)
    if activation.is_symlink():
        raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Linked evidence activation.')
    if not activation.exists():
        return None
    try:
        pointer = json.loads(activation.read_bytes())
        identity = pointer['snapshot_id']
        raw = _child(root, identity).read_bytes()
        document = json.loads(raw)
        if (_sha(raw) != identity or document.get('schema') != SCHEMA
                or pointer.get('schema') != SCHEMA):
            raise ValueError('Snapshot commitment mismatch')
        if verify_package:
            import importlib.util
            spec = importlib.util.spec_from_file_location('_evidence_package_inputs', root / 'prepare_sources.py')
            preparation = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(preparation)
            if preparation.digest(preparation.package_inputs(root)) != document['package_input_sha256']:
                raise KBError('EVIDENCE_PACKAGE_CHANGED', 'Evidence snapshot belongs to different package inputs; prepare again.')
        return dict(document, snapshot_id=identity)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Active evidence snapshot failed integrity checks.') from exc


def activate(package_root, assessment):
    """Install immutable metadata before replacing the sole activation pointer.

    Caller owns prepare's interprocess lock. A failed replace preserves the old
    pointer; unreferenced completed snapshots are safe and deliberately retained.
    """
    root = Path(package_root).resolve()
    raw = _raw(assessment)
    identity = _sha(raw)
    target = _child(root, identity)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != raw:
            raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Existing snapshot bytes changed.')
    else:
        _atomic(target, raw)
    # Read back before changing activation.
    if _sha(target.read_bytes()) != identity:
        raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Snapshot changed before activation.')
    pointer = root / 'cache/evidence/active.json'
    if pointer.is_symlink():
        raise KBError('EVIDENCE_SNAPSHOT_INVALID', 'Linked evidence activation.')
    _atomic(pointer, _raw({'schema': SCHEMA, 'snapshot_id': identity}))
    return identity


def _atomic(path, raw):
    fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _dependencies(root, catalog, issues=None):
    """Follow authored artifact/pointer edges, including evidence-of-evidence."""
    documents, reverse = {}, {}
    def load(name):
        if name not in documents:
            path = root / name
            if (not isinstance(name, str) or '\\' in name or ':' in name
                    or '..' in Path(name).parts or not path.resolve().is_relative_to(root.resolve())):
                raise ValueError('Unsafe evidence dependency artifact')
            documents[name] = json.loads(path.read_bytes()) if path.exists() and path.suffix == '.json' else None
        return documents[name]
    def links(node):
        if isinstance(node, dict):
            if isinstance(node.get('artifact_path'), str) and isinstance(node.get('pointer'), str):
                yield ('knowledge/' + node['artifact_path'], node['pointer'])
            if isinstance(node.get('artifact_path'), str) and isinstance(node.get('source_pointer'), str):
                yield ('knowledge/' + node['artifact_path'], node['source_pointer'])
            if isinstance(node.get('source_file'), str) and node['source_file'].startswith('research/') and isinstance(node.get('source_pointer'), str):
                name = node['source_file']
                # Historical N001 logical paths have an explicit installed prefix.
                if name.split('/')[1] in ('NATIVE-001', 'NATIVE-001.1', 'NATIVE-001.2'):
                    name = 'research/native001/' + name.removeprefix('research/')
                yield ('knowledge/' + name, node['source_pointer'])
            for value in node.values():
                yield from links(value)
        elif isinstance(node, list):
            for value in node:
                yield from links(value)
    for row in catalog:
        todo, seen = [('knowledge/' + row['file'], row['pointer'])], set()
        if row.get('family') == 'native_ai':
            name = 'knowledge/data/native001/canonical-native001-research-map.json'
            for index, item in enumerate(load(name)['entries']):
                if item['canonical_id'] == row['id']:
                    todo.append((name, '/entries/' + str(index)))
        while todo:
            name, pointer = todo.pop()
            if (name, pointer) in seen:
                continue
            seen.add((name, pointer))
            reverse.setdefault(name, []).append((pointer, row['id']))
            node = load(name)
            if node is None:
                continue
            if pointer:
                if not pointer.startswith('/'):
                    raise ValueError('Malformed evidence dependency pointer')
                try:
                    for token in pointer[1:].split('/'):
                        token = token.replace('~1', '/').replace('~0', '~')
                        node = node[int(token)] if isinstance(node, list) else node[token]
                except (KeyError, IndexError, TypeError, ValueError):
                    if issues is not None:
                        issues.append({'artifact_path': name, 'pointer': pointer, 'affected_entry_ids': [row['id']],
                                       'status': 'UNKNOWN', 'reason': 'historical_dependency_pointer_unavailable'})
                    continue
            todo.extend(links(node))
    return reverse


def verify_native_ai(root, paths):
    """N001 has locator-only evidence: check exact files, never invent ranges."""
    from contextlib import ExitStack
    from .native_mechanism_source import Source
    name = Path(root) / 'knowledge/data/native001/canonical-native001-research-map.json'
    if not name.exists():
        return []
    refs = []
    with ExitStack() as stack:
        inputs = []
        for index, path in enumerate(paths):
            source = Source(path, index)
            stack.callback(source.close)
            inputs.append(source)
        for item in json.loads(name.read_bytes())['entries']:
            found = set()
            def walk(node):
                if isinstance(node, dict):
                    file, expected = node.get('file'), node.get('file_sha256')
                    if isinstance(file, str) and file.endswith('.lua') and isinstance(expected, str):
                        if not re.fullmatch('[a-f0-9]{64}', expected):
                            raise ValueError('Invalid N001 source hash')
                        found.add((file if file.startswith('scripts/') else 'scripts/' + file, expected))
                    for value in node.values():
                        walk(value)
                elif isinstance(node, list):
                    for value in node:
                        walk(value)
            walk(item.get('source_locators', []))
            for file, expected in sorted(found):
                checks = []
                for source in inputs:
                    member = source.member(file)
                    checks.append(dict(source.identity(), provided_file_sha256=member.get('file_sha256') if member else None,
                        status='MISSING' if member is None else 'EXACT_FILE' if member.get('file_sha256') == expected else 'CHANGED_UNKNOWN'))
                status = min((c['status'] for c in checks), key=('EXACT_FILE', 'CHANGED_UNKNOWN', 'MISSING').index) if checks else 'UNKNOWN'
                refs.append({'reference_id': item['canonical_id'] + '#' + file + '#' + expected,
                    'kind': 'native_ai_file_locator', 'artifact_path': 'knowledge/data/native001/canonical-native001-research-map.json',
                    'status': status, 'source_file': file, 'evidence_file_sha256': expected,
                    'source_checks': checks, 'affected_entry_ids': [item['canonical_id']], 'range_verified': False})
    return refs


def build(package_root, recipe, hydration, mechanisms, sources, package_hash, native_ai=None):
    """Map exact artifact/pointer dependencies; never infer semantic equivalence."""
    root = Path(package_root)
    catalog_path = root / 'knowledge/CATALOG.json'
    catalog = json.loads(catalog_path.read_bytes()).get('entries', []) if catalog_path.exists() else []
    dependency_issues = []
    dependencies = _dependencies(root, catalog, dependency_issues)
    matches = {row['id']: row for row in hydration['matches']}
    refs = []
    for slot in recipe['slots']:
        match = matches.get(slot['id'])
        status = ('EXACT_FILE_RANGE' if match['provided_whole_file_equals_original'] else 'RANGE_ONLY') if match else hydration.get('gap_statuses', {}).get(slot['id'], 'UNKNOWN')
        impacted = set()
        for pointer, entry_id in dependencies.get(slot['path'], []):
            if (not pointer or slot['pointer'] == pointer or slot['pointer'].startswith(pointer + '/')
                    or pointer.startswith(slot['pointer'] + '/')):
                impacted.add(entry_id)
        for row in catalog:
            if (slot['path'] == 'knowledge/' + row['file'] and
                    (slot['pointer'] == row['pointer'] or slot['pointer'].startswith(row['pointer'] + '/'))):
                impacted.add(row['id'])
            # Contract-map slots explicitly name the owning stable record ID.
            if slot['pointer'].startswith('/records/' + row['id'].replace('~', '~0').replace('/', '~1') + '/'):
                impacted.add(row['id'])
        refs.append({'reference_id': slot['id'], 'kind': slot['kind'], 'artifact_path': slot['path'],
                     'pointer': slot['pointer'], 'status': status, 'affected_entry_ids': sorted(impacted),
                     'expected_content_sha256': slot['content_sha256'], 'coordinates': slot['coordinates'],
                     'source_match': match, 'required_for_full_runtime': slot['required_for_knowledge_shape']})
    for doc in mechanisms.get('documents', []):
        source_doc = json.loads((root / 'knowledge' / doc['file']).read_bytes())
        for ref in doc['references']:
            impacted = []
            for entry in source_doc.get('entries', []):
                # Only explicit evidence_refs create dependencies.
                def uses(node):
                    if isinstance(node, dict):
                        return ref['reference_id'] in node.get('evidence_refs', []) or any(uses(v) for v in node.values())
                    return isinstance(node, list) and any(uses(v) for v in node)
                if uses(entry):
                    impacted.append(entry['id'])
            refs.append(dict(ref, reference_id=doc['file'] + '#' + ref['reference_id'],
                             kind='mechanism_locator', artifact_path='knowledge/' + doc['file'],
                             affected_entry_ids=sorted(impacted)))
    refs.extend(native_ai or [])
    for issue in dependency_issues:
        refs.append(dict(issue, reference_id='dependency:' + issue['affected_entry_ids'][0] + ':' + issue['artifact_path'] + '#' + issue['pointer'],
                         kind='unresolved_dependency_pointer'))
    covered = {entry_id for ref in refs for entry_id in ref['affected_entry_ids']}
    for row in catalog:
        if row['id'] not in covered:
            refs.append({'reference_id': 'unassessed:' + row['id'], 'kind': 'unassessed_registered_entry',
                'artifact_path': 'knowledge/' + row['file'], 'pointer': row['pointer'],
                'status': 'UNKNOWN', 'affected_entry_ids': [row['id']],
                'reason': 'No checked source-payload or locator reference covers this registered entry.'})
    old = _load(root, verify_package=False)
    old_refs = {r['reference_id']: r for r in old['references']} if old else {}
    changes = [{'reference_id': r['reference_id'], 'previous_status': old_refs.get(r['reference_id'], {}).get('status'),
                'status': r['status'], 'affected_entry_ids': r['affected_entry_ids']} for r in refs
               if old_refs.get(r['reference_id'], {}).get('status') != r['status']]
    unresolved = [r for r in refs if r['status'] not in ('EXACT_FILE_RANGE', 'RANGE_ONLY', 'EXACT_FILE')]
    return {'schema': SCHEMA, 'status': 'PARTIAL' if unresolved else 'COMPLETE',
            'package_input_sha256': package_hash, 'sources': sources, 'references': refs,
            'reference_count': len(refs), 'unresolved_reference_count': len(unresolved),
            'affected_entry_ids': sorted({i for r in unresolved for i in r['affected_entry_ids']}),
            'unmapped_reference_ids': [r['reference_id'] for r in refs if not r['affected_entry_ids']],
            'unavailable_dependency_artifacts': sorted(name for name in dependencies if not (root / name).exists()),
            'previous_comparison': {'snapshot_id': old.get('snapshot_id') if old else None,
                                    'sources': old.get('sources') if old else None, 'changes': changes},
            'full_runtime_activated': False, 'runtime_game_verified': False,
            'historical_evidence_identity_rewritten': False}

"""Rebind a public derivative's exact references and commitments.

Only typed reference tuples and named digest fields are updated. Historical
source-file, range, archive and provenance hashes are never globally replaced.
The caller supplies the origin map produced before redaction/hydration.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath


CORE = 'data/nativecore/native-core.json'
N001 = 'data/native001/canonical-native001-ai-knowledge.json'
ROOTS = ('knowledge', 'knowledge-history/e42')
_HASHES = {}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def checksum(path):
    path = Path(path).resolve()
    key = str(path)
    if key not in _HASHES:
        _HASHES[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _HASHES[key]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8', newline='\n')
    _HASHES.pop(str(path.resolve()), None)


def child(root, relative):
    name = PurePosixPath(relative)
    if not relative or ':' in relative or '\\' in relative or '..' in name.parts or name.is_absolute():
        raise ValueError('Unsafe relative artifact path: ' + str(relative))
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Artifact escaped package')
    return result


def at(document, pointer):
    pointer = pointer.removeprefix('#')
    if pointer == '':
        return document
    if not pointer.startswith('/'):
        raise ValueError('Expected JSON pointer')
    for key in pointer[1:].split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


def walk(value, pointer=''):
    if isinstance(value, dict):
        yield value, pointer
        for key, item in value.items():
            yield from walk(item, pointer + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, pointer + '/' + str(index))


def ref_parts(node):
    if {'artifact_path', 'sha256', 'pointer'} <= node.keys():
        return 'artifact_path', 'sha256', 'pointer'
    if {'artifact_path', 'artifact_sha256', 'source_pointer'} <= node.keys():
        return 'artifact_path', 'artifact_sha256', 'source_pointer'
    return None


def _manifest(root):
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_file() and path != root / 'PACKAGE-MANIFEST.json' and '__pycache__' not in path.parts:
            rows.append({'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                         'sha256': checksum(path)})
    write(root / 'PACKAGE-MANIFEST.json', {'schema_version': 'dst-public-package-manifest/1',
          'public_derivative': True, 'files': rows})


def rebind(target, originmapping, report_path=None):
    """Rebuild exact refs, record/node digests, manifests and epoch catalog.

    originmapping may be a dictionary or JSON file. This is safe to distribute:
    it needs relative paths, old hashes and record IDs, never private originals.
    It can run repeatedly after local source payload assembly.
    """
    root = Path(target).resolve()
    _HASHES.clear()
    origins = read(originmapping) if isinstance(originmapping, (str, Path)) else copy.deepcopy(originmapping)
    file_origins = {row['path']: row for row in origins['files']}
    changes, errors = [], []
    for kbname in ROOTS:
        kb = child(root, kbname)
        if not kb.exists():
            continue
        old_rows = {row['id']: row for row in origins['records'][kbname]}
        # Evidence files form a DAG; changing a child updates only references to
        # that exact old path/hash, never unrelated historical hash fields.
        documents = {}
        core = read(kb / CORE)
        research_path = 'data/native001/canonical-native001-research-map.json'
        research = read(kb / research_path)
        evidence_paths = {row['artifact_path'] for row in core['source_artifacts'] + research['source_artifacts']}
        for relative in evidence_paths:
            path = child(kb, relative)
            if path.suffix == '.json':
                documents[relative] = read(path)
        done, active = set(), set()

        def current_ref(node):
            parts = ref_parts(node)
            if not parts:
                return None
            pk, hk, tk = parts
            name = node[pk]
            path = child(kb, name)
            if not path.is_file():
                raise ValueError('Missing typed reference artifact: ' + kbname + '/' + name)
            origin = file_origins.get(kbname + '/' + name)
            # Accept original, previous public, or current exact commitment.
            allowed = {checksum(path)}
            if origin:
                allowed |= {origin['sha256'], origin.get('public_sha256')}
            if node[hk] not in allowed and node[hk] not in origins.get('previous_public_hashes', {}).get(kbname + '/' + name, []):
                # A later hydrate pass changes an artifact before its dependants;
                # hashes written by earlier passes are tracked in the origin map.
                raise ValueError('Unrecognized typed reference hash: ' + kbname + '/' + name + ' ' + str(node[tk]))
            value = None
            if path.suffix == '.json':
                doc = documents.get(name)
                if doc is None:
                    doc = read(path)
                try:
                    value = at(doc, node[tk])
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError('Unresolved public pointer: ' + kbname + '/' + name + ' ' + str(node[tk])) from exc
                if value is None:
                    raise ValueError('Typed reference points to withheld sparse slot: ' + name + str(node[tk]))
            elif str(node[tk]).startswith('#L'):
                line = int(node[tk][2:])
                if not 0 < line <= len(path.read_text(encoding='utf-8').splitlines()):
                    raise ValueError('Invalid public text line pointer')
            return parts, path, value

        def bind_refs(value):
            for node, pointer in walk(value):
                parts = ref_parts(node)
                if not parts:
                    continue
                pk, hk, tk = parts
                name = node[pk]
                if name in documents and name not in done:
                    finish(name)
                _, path, selected = current_ref(node)
                old = node[hk]
                node[hk] = checksum(path)
                if 'bytes' in node:
                    node['bytes'] = path.stat().st_size
                if old != node[hk]:
                    changes.append({'path': kbname + '/' + name, 'pointer': node[tk],
                                    'old_sha256': old, 'new_sha256': node[hk], 'reason': 'EXACT_TYPED_REFERENCE_REBOUND'})
                if selected is not None:
                    for field in ('original_source_value_sha256', 'artifact_value_sha256'):
                        if field in node:
                            node[field] = digest(selected)

        def finish(name):
            if name in done:
                return
            if name in active:
                raise ValueError('Cyclic evidence commitment: ' + name)
            active.add(name)
            bind_refs(documents[name])
            write(kb / name, documents[name])
            active.remove(name)
            done.add(name)

        for name in sorted(documents):
            finish(name)
        for doc, relative in ((core, CORE), (research, research_path)):
            bind_refs(doc)
            for row in doc['source_artifacts']:
                path = child(kb, row['artifact_path'])
                row['sha256'], row['bytes'] = checksum(path), path.stat().st_size
            write(kb / relative, doc)
        for path in (kb / 'data').rglob('*.json'):
            if path in (kb / CORE, kb / research_path):
                continue
            doc = read(path)
            bind_refs(doc)
            write(path, doc)
        # Legacy preservation is a real public byte identity, not the original
        # private archive identity. Only validator-required baseline is mirrored.
        for relative in origins.get('legacy_mirror_files', []):
            path = child(kb, relative)
            dest = child(kb, 'history/v0.1.1/' + relative)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(path.read_bytes())
        records = {}
        for relative in ('data/entries.json', N001, CORE):
            for record in read(kb / relative)['entries']:
                records[record['id']] = record
        record_digests = {row['sha256']: digest(records[identifier]) for identifier, row in old_rows.items()}
        # Include every already rebound digest so a second hydration/rebind works.
        for identifier, record in records.items():
            for old in origins.setdefault('record_digest_history', {}).setdefault(kbname, {}).setdefault(identifier, []):
                record_digests[old] = digest(record)
            history = origins['record_digest_history'][kbname][identifier]
            if digest(record) not in history:
                history.append(digest(record))
        catalog = read(root / 'source-epochs.json')
        assets = []
        for epoch in catalog['epochs'].values():
            if epoch['knowledge_root'] == kbname:
                assets += [epoch['contract_map']['path'], epoch['source_identity_map']['path']]
        if kbname == 'knowledge':
            assets += ['dst-kb-service/dst_kb/contract_map.json', 'dst-kb-service/dst_kb/source_identity_map.json']
        lexical_keys = {}
        for asset in sorted(dict.fromkeys(assets), key=lambda name: ('source_identity_map' not in name, name)):
            doc = read(root / asset)
            bind_refs(doc)
            for node, _ in walk(doc):
                if node.get('record_sha256') in record_digests:
                    node['record_sha256'] = record_digests[node['record_sha256']]
                reference = node.get('reference')
                if isinstance(reference, dict) and ref_parts(reference):
                    selected = current_ref(reference)[2]
                    if 'artifact_value_sha256' in node:
                        node['artifact_value_sha256'] = digest(selected)
                    if 'artifact_scope_sha256' in node:
                        source_doc = read(child(kb, reference['artifact_path']))
                        node['artifact_scope_sha256'] = digest(source_doc['scope'])
                for refkey, hashkey in (('whole_fact_reference', 'whole_fact_value_sha256'), ('source_scope_reference', 'source_scope_sha256')):
                    if refkey in node and hashkey in node:
                        node[hashkey] = digest(current_ref(node[refkey])[2])
            if 'records' in doc:
                for identifier, mapped in doc['records'].items():
                    mapped['record_sha256'] = digest(records[identifier])
                    # Equality-bound whole scope is copied without inferring roles.
                    if 'original_scope' in mapped:
                        mapped['original_scope'] = copy.deepcopy(records[identifier].get('scope', records[identifier].get('scope_text', '')))
                    for pointer in mapped.get('claim_reference_bindings', {}):
                        selected = at(records[identifier], pointer)
                        mapped['claim_reference_bindings'][pointer] = copy.deepcopy(selected.get('evidence_refs', []))
                doc['knowledge_commitments'] = {relative: checksum(kb / relative) for relative in ('data/entries.json', N001, CORE)}
                if 'applicability_ledger_sha256' in doc:
                    doc['applicability_ledger_sha256'] = checksum(kb / 'data/source-epoch-coverage.json')
            if 'canonical_sha256' in doc:
                doc['canonical_sha256'] = checksum(kb / CORE)
            # Lexical certificates are keyed by their own exact JSON digest.
            if isinstance(doc.get('lexical_witnesses'), dict):
                keymap = {old: digest(value) for old, value in doc['lexical_witnesses'].items()}
                lexical_keys.update(keymap)
                doc['lexical_witnesses'] = {keymap[old]: value for old, value in doc['lexical_witnesses'].items()}
            for node, _ in walk(doc):
                if node.get('lexical_witness_ref') in lexical_keys:
                    node['lexical_witness_ref'] = lexical_keys[node['lexical_witness_ref']]
            write(root / asset, doc)
        _manifest(kb)
    # Projection profiles use preserved selection indexes, with exact new record
    # hashes. Variant hash keys are remapped using their original record identity.
    profilepath = root / 'dst-kb-service/dst_kb/projection_profiles.json'
    if profilepath.is_file():
        profiles = read(profilepath)
        all_records = {}
        for kbname in ROOTS:
            for relative in ('data/entries.json', N001, CORE):
                for record in read(root / kbname / relative)['entries']:
                    all_records.setdefault(record['id'], []).append(record)
        for identifier, row in profiles.get('profiles', {}).items():
            old = row['record_sha256']
            for kbname, records in origins['records'].items():
                previous = origins.get('record_digest_history', {}).get(kbname, {}).get(identifier, [])
                if any(x['id'] == identifier and x['sha256'] == old for x in records) or old in previous:
                    row['record_sha256'] = digest(next(x for x in read(root / kbname / CORE)['entries'] if x['id'] == identifier))
                    break
        for identifier, variants in profiles.get('record_variants', {}).items():
            updated = {}
            for old, row in variants.items():
                match = next((kbname for kbname, rows in origins['records'].items() if any(x['id'] == identifier and x['sha256'] == old for x in rows) or old in origins.get('record_digest_history', {}).get(kbname, {}).get(identifier, [])), None)
                if match:
                    row['record_sha256'] = digest(next(x for x in read(root / match / CORE)['entries'] if x['id'] == identifier))
                updated[row['record_sha256']] = row
            profiles['record_variants'][identifier] = updated
        write(profilepath, profiles)
    catalog = read(root / 'source-epochs.json')
    for epoch in catalog['epochs'].values():
        for field in ('knowledge_manifest', 'contract_map', 'source_identity_map', 'applicability_ledger'):
            if field in epoch:
                epoch[field]['sha256'] = checksum(child(root, epoch[field]['path']))
        for source in epoch['source_manifests']:
            source['sha256'] = checksum(child(root, source['path']))
    write(root / 'source-epochs.json', catalog)
    for row in origins['files']:
        path = child(root, row['path'])
        if path.is_file():
            now = checksum(path)
            histories = origins.setdefault('previous_public_hashes', {}).setdefault(row['path'], [])
            if now not in histories:
                histories.append(now)
            row['public_sha256'] = now
    unique = {json.dumps(row, sort_keys=True): row for row in changes}
    result = {'schema': 'dst-public-rebind-report/1', 'typed_reference_updates': list(unique.values()),
              'unresolved': errors, 'historical_source_hashes_globally_replaced': False}
    publication_path = root / 'PUBLICATION-REPORT.json'
    if publication_path.is_file():
        publication = read(publication_path)
        for row in publication.get('files', []):
            path = child(root, row['path'])
            if path.is_file():
                row['new_sha256'] = checksum(path)
        publication['commitments_rebound'] = True
        write(publication_path, publication)
    if report_path:
        write(report_path, result)
    return result, origins


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('originmapping')
    parser.add_argument('--report')
    args = parser.parse_args()
    report, origins = rebind(args.target, args.originmapping, args.report)
    write(args.originmapping, origins)
    print(json.dumps({'updates': len(report['typed_reference_updates']), 'unresolved': report['unresolved']}))

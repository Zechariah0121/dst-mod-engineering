"""Manifest-protected family identities, shared by catalog, service and builders.

No dependencies on Service or source payload. Old packages retain their frozen
three-family contract; an extended package requires this explicit registry.
"""
import hashlib
import json
from pathlib import Path

FILE = 'FAMILY-REGISTRY.json'
SCHEMA = 'dst-family-registry/1'
HISTORICAL = {'legacy': 64, 'native_ai': 13, 'native_core': 110}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def decode(raw):
    def pairs(values):
        result={}
        for key,value in values:
            if key in result:raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    def constant(value):
        raise ValueError('Invalid JSON constant: '+value)
    return json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs,parse_constant=constant)


def inside(root, name):
    if not isinstance(name, str) or not name or any(c in name for c in ('\\', ':', '\x00')) or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError('Unsafe registered artifact path')
    path = (Path(root) / name).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Registered artifact escaped knowledge root')
    return path


def read_committed(root, name, expected):
    raw = inside(root, name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Registered artifact hash mismatch: ' + name)
    return decode(raw)


def load(root, reader=None):
    root = Path(root)
    if not (root / FILE).is_file():
        return None
    # Catalog supplies its manifest-verified reader. Other callers validate the
    # complete manifest independently; always verify this registry commitment.
    if reader is None:
        manifest = json.loads((root / 'PACKAGE-MANIFEST.json').read_bytes())
        rows = [r for r in manifest['files'] if r['path'] == FILE]
        if len(rows) != 1:
            raise ValueError('Family registry must be committed exactly once')
        registry = read_committed(root, FILE, rows[0]['sha256'])
    else:
        reader(FILE)
        registry = decode((root / FILE).read_bytes())
    if registry.get('schema_version') != SCHEMA:
        raise ValueError('Unsupported family registry')
    names, ids = set(), set()
    for family in registry['families']:
        name = family['name']
        if name in names or name not in (*HISTORICAL, 'native_mechanism'):
            raise ValueError('Duplicate or unsupported family')
        names.add(name)
        family_ids = []
        for row in family['documents']:
            doc = read_committed(root, row['file'], row['sha256'])
            entries = doc['entries']
            if [e['id'] for e in entries] != row['entry_ids']:
                raise ValueError('Registered entry identity/order differs')
            if {e['id']: digest(e) for e in entries} != row['record_sha256']:
                raise ValueError('Registered record body differs')
            family_ids.extend(row['entry_ids'])
            if name == 'native_mechanism':
                review = read_committed(root, row['review']['file'], row['review']['sha256'])
                for dependency in row['review'].get('dependencies',[]):
                    read_committed(root,dependency['file'],dependency['sha256'])
                prior=review.get('previous_review',{}).get('sha256')
                if prior and not any(dep['sha256']==prior for dep in row['review'].get('dependencies',[])):
                    raise ValueError('Missing exact prior review artifact')
                if review.get('candidate_sha256') != row['sha256'] or review.get('runtime_verified') is not False:
                    raise ValueError('Research review does not bind candidate/no-runtime boundary')
        if name in HISTORICAL and len(family_ids) != HISTORICAL[name]:
            raise ValueError('Historical family identity count changed')
        if len(family_ids) != len(set(family_ids)) or ids.intersection(family_ids):
            raise ValueError('Duplicate family IDs')
        ids.update(family_ids)
    if not set(HISTORICAL).issubset(names):
        raise ValueError('Missing historical family')
    return registry


def catalog_rows(root, registry):
    rows = []
    governance = {}
    for family in registry['families']:
        if family['name'] == 'native_core':
            for document in family['documents']:
                core = read_committed(root, document['file'], document['sha256'])
                governance.update({row['id']: row for row in core.get('state_registry', [])})
    for family in registry['families']:
        for document in family['documents']:
            data = read_committed(root, document['file'], document['sha256'])
            for i, entry in enumerate(data['entries']):
                row = {'id': entry['id'], 'title': entry['title'], 'family': family['name'],
                       'file': document['file'], 'pointer': '/entries/' + str(i)}
                for key in ('status', 'knowledge_status', 'retrieval_status', 'coding_status'):
                    if key in entry:
                        row[key] = entry[key]
                    elif key in governance.get(entry['id'], {}):
                        row[key] = governance[entry['id']][key]
                rows.append(row)
    return rows


def counts(registry):
    result = {f['name']: sum(len(d['entry_ids']) for d in f['documents']) for f in registry['families']}
    return {'total': sum(result.values()), **result}


def validate_catalog(root, catalog, registry):
    if registry is None:
        return
    if catalog['entries'] != catalog_rows(root, registry) or catalog['counts'] != counts(registry):
        raise ValueError('Catalog differs from registered family identities/bodies/states')


def refresh_derived_baseline(root):
    """Called ONLY by source hydration/rebind, never silently at read time.

    Exact original public identities remain in published_record_sha256. Existing
    baseline hydration changes typed evidence refs, so derived hashes are rebound;
    new candidate/review artifacts remain immutable and must still match.
    """
    path = Path(root) / FILE
    if not path.is_file():
        return
    registry = json.loads(path.read_bytes())
    for family in registry['families']:
        if family['name'] not in HISTORICAL:
            continue
        for row in family['documents']:
            raw = inside(root, row['file']).read_bytes()
            entries = json.loads(raw)['entries']
            if [e['id'] for e in entries] != row['entry_ids']:
                raise ValueError('Rebind changed historical identities')
            row['sha256'] = hashlib.sha256(raw).hexdigest()
            row['record_sha256'] = {e['id']: digest(e) for e in entries}
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

"""Explicit Reviewer research only. Locators are not restored Lua/runtime proof."""
import copy
import json
import re
from collections import Counter
from .config import KBError
from . import family_registry as families
from . import mechanism_contract
from .nativecore import pointer as at

TYPE = 'native_mechanism_research'
STATES = {'knowledge_status': 'research', 'retrieval_status': 'restricted', 'coding_status': 'hold'}
NOTICE = 'Static research; source_references are locators/hashes, not restored Lua. No runtime verification or Coding admission.'


def local_refs(value):
    found = []
    def walk(node):
        if isinstance(node, dict):
            found.extend(node.get('evidence_refs', []))
            if 'ref' in node and 'role' in node:
                found.append(node['ref'])
            for key, item in node.items():
                if key not in ('evidence_refs', 'ref'):
                    walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(value)
    return list(dict.fromkeys(found))


def load(root, registry=None):
    registry = families.load(root) if registry is None else registry
    records = {}
    if registry is None:
        return records
    for family in registry['families']:
        if family['name'] != 'native_mechanism':
            continue
        for row in family['documents']:
            doc = families.read_committed(root, row['file'], row['sha256'])
            mechanism_contract.validate(doc)
            if doc.get('schema_version') != 'dst-mechanism-research/1':
                raise ValueError('Unknown mechanism candidate schema')
            refs = {r['id']: r for r in doc['source_references']}
            if len(refs) != len(doc['source_references']):
                raise ValueError('Duplicate local source reference')
            for ref in refs.values():
                name = ref['source_file']
                families.inside(root, name)  # same exact path guard; no file read
                if not name.startswith('scripts/'):
                    raise ValueError('Mechanism source locator must use scripts/')
                if any(not isinstance(ref.get(k), str) or not re.fullmatch('[0-9a-f]{64}', ref[k]) for k in ('file_sha256', 'range_sha256')):
                    raise ValueError('Invalid mechanism source hash')
                if type(ref['line_start']) is not int or type(ref['line_end']) is not int or not 1 <= ref['line_start'] <= ref['line_end']:
                    raise ValueError('Invalid mechanism source range')
            for i, entry in enumerate(doc['entries']):
                if any(entry.get(k) != value for k, value in STATES.items()) or not entry.get('scope'):
                    raise ValueError('Mechanism admission state/Scope changed')
                for claim in entry['claims']:
                    if claim.get('kind') not in ('NSF', 'EI', 'REC', 'UNK') or (claim['kind'] == 'NSF' and not claim['evidence_refs']):
                        raise ValueError('Unknown mechanism claim kind or NSF without evidence')
                if any(r not in refs for r in local_refs(entry)):
                    raise ValueError('Dangling local mechanism evidence')
                records[entry['id']] = {'entry': entry, 'document': doc, 'registration': row, 'index': i}
    return records


def envelope(record, pointer='', assessment_detail=True):
    if not isinstance(pointer,str) or len(pointer)>2000 or (pointer and not pointer.startswith('/')):
        raise KBError('INVALID_ARGUMENT','Expected a bounded absolute entry pointer')
    entry, doc, registration = record['entry'], record['document'], record['registration']
    # A subfield request cannot detach statement prose from its typed whole atom.
    requested = pointer
    match = re.match(r'^/(claims|api_contracts|mechanism_steps)/(0|[1-9][0-9]*)(?:/|$)', pointer)
    if match:
        # Validate the actual requested subpointer before expanding its owner.
        try:
            at(entry, pointer)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise KBError('INVALID_ARGUMENT', 'Invalid mechanism atom subpointer') from exc
        pointer = '/' + match[1] + '/' + match[2]
    try:
        value = entry if not pointer else at(entry, pointer)
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise KBError('INVALID_ARGUMENT', 'Invalid mechanism entry pointer') from exc
    ids = local_refs(value)
    refs = {r['id']: r for r in doc['source_references']}
    result = {'id': entry['id'], 'title': entry['title'], 'family': 'native_mechanism', 'entry_type': TYPE,
            **STATES, 'scope': copy.deepcopy(entry['scope']), 'unknowns': copy.deepcopy(entry['unknowns']),
            'source_epoch': doc['source_epoch'], 'archive_sha256': doc['archive_sha256'],
            'limitations': copy.deepcopy(doc['limitations']), 'pointer': pointer, 'requested_pointer': requested,
            'value': copy.deepcopy(value), 'source_references': [copy.deepcopy(refs[r]) for r in ids],
            'artifact': {'file': registration['file'], 'sha256': registration['sha256'], 'pointer': '/entries/' + str(record['index']) + pointer},
            'review_record': copy.deepcopy(registration['review']),
            'evidence_status': 'LOCATOR_HASH_ONLY', 'runtime_validation_performed': False,
            'coding_admission_granted': False, 'notice': NOTICE}
    from .source_epoch_runtime import source_preparation_document
    assessment = source_preparation_document()
    if assessment is not None:
        matched = [row for row in assessment['native_mechanisms'].get('documents', [])
                   if row['file'] == registration['file'] and row['sha256'] == registration['sha256']]
        if len(matched) != 1:
            raise KBError('SOURCE_EPOCH_STALE', 'Mechanism assessment does not bind this candidate.')
        checks = {row['reference_id']: row for row in matched[0]['references']}
        if any(identifier not in checks for identifier in ids):
            raise KBError('SOURCE_EPOCH_STALE', 'Mechanism source assessment is incomplete.')
        result['source_input_assessment'] = {
            'sources': copy.deepcopy(assessment['summary']['sources']),
            'references': [copy.deepcopy(checks[identifier]) for identifier in ids],
            'notice': assessment['summary']['notice'], 'runtime_game_verified': False}
        if not assessment_detail:
            # Search already carries the committed source identities in its
            # outer environment. Group every selected ref by input/status;
            # coordinate/hash details remain available through explicit reads.
            per_source = {}
            for identifier in ids:
                for check in checks[identifier]['source_checks']:
                    states = per_source.setdefault(check['source_input_index'], {})
                    states.setdefault(check['status'], []).append(identifier)
            result['source_input_assessment'] = {
                'per_source_reference_states': per_source,
                'source_identities': 'source_environment.source_input_assessment.sources',
                'detail_tools': ['get_entry', 'resolve_evidence'], 'runtime_game_verified': False}
    return result


def bounded(record, pointer='', max_bytes=24000):
    if type(max_bytes) is not int or not 1000 <= max_bytes <= 64000:
        raise KBError('INVALID_ARGUMENT', 'Mechanism max_bytes must be 1000..64000')
    value = envelope(record, pointer)
    # Charge every mandatory field, not just claim prose.
    delivered = value | {'whole_value_delivered': True}
    if len(json.dumps(delivered, ensure_ascii=False).encode()) <= max_bytes:
        return delivered
    withheld = {k: value[k] for k in ('id', 'family', 'knowledge_status', 'retrieval_status', 'coding_status', 'scope', 'unknowns', 'source_epoch', 'archive_sha256', 'limitations', 'artifact', 'notice')}
    selected = value['value']
    keys = list(selected) if isinstance(selected, dict) else list(range(len(selected))) if isinstance(selected, list) else []
    withheld.update(whole_value_delivered=False, withheld_reason='WHOLE_ATOM_AND_REQUIRED_CONTEXT_EXCEED_BUDGET',
                    child_pointers=[value['pointer'] + '/' + str(k).replace('~', '~0').replace('/', '~1') for k in keys[:30]])
    if len(json.dumps(withheld, ensure_ascii=False).encode()) > max_bytes:
        return {'id': value['id'], 'whole_value_delivered': False, 'withheld_reason': 'REQUIRED_SCOPE_EXCEEDS_BUDGET', 'guidance': 'Read the registered file with complete Scope; no facts delivered.'}
    return withheld


def score(record, query):
    # Share navigation token/identity syntax with the source-free catalog. This
    # import is deliberately local: public_catalog imports this module for reads.
    from .public_catalog import IDENTITY, declared_identities, token_sequence, tokens
    entry = record['entry']
    query = query.strip()
    if not query:
        return 0
    lowered = query.lower()
    if lowered == entry['id'].lower():
        return 10000
    terms = tokens(query)
    if not terms:
        return 0
    identities = declared_identities(entry)
    identity = IDENTITY.fullmatch(query)
    requested = identity[1].lower() if identity else None
    qualified = requested is not None and ('.' in requested or ':' in requested)
    leaves = {re.split(r'[.:]', name)[-1] for name in identities}

    def canonical(value):
        match = IDENTITY.fullmatch(value.strip()) if isinstance(value, str) else None
        return match[1].lower() if match else None

    def source_matches(value):
        name = canonical(value)
        return name is not None and (name == requested if qualified else re.split(r'[.:]', name)[-1] == requested)

    # Source symbols are navigation metadata, not API declarations. Prefer a
    # bounded range containing a declared method's own symbol over a range cited
    # only as its dependency. A co-located local helper stays local: no identity,
    # visibility, payload, evidence or Coding admission is changed here.
    used = set(local_refs(entry))
    references = [ref for ref in record.get('document', {}).get('source_references', []) if ref['id'] in used]
    source_hit = anchored_hit = False
    for ref in references:
        if requested is None or not any(source_matches(symbol) for symbol in ref.get('symbols', [])):
            continue
        source_hit = True
        for api in entry.get('api_contracts', []):
            declaration = canonical(api.get('symbol'))
            if declaration is None or api.get('source_file') != ref['source_file'] or ref['id'] not in api.get('evidence_refs', []):
                continue
            if any(canonical(symbol) == declaration or
                   (canonical(symbol) is not None and '.' not in canonical(symbol) and ':' not in canonical(symbol) and
                    canonical(symbol) == re.split(r'[.:]', declaration)[-1]) for symbol in ref.get('symbols', [])):
                anchored_hit = True

    aliases = {value.strip().lower() for value in entry.get('aliases', []) if isinstance(value, str)}
    priority = (80 if qualified and requested in identities else
                70 if not qualified and requested in leaves else
                60 if anchored_hit else
                50 if lowered == entry.get('title', '').strip().lower() or lowered in aliases else
                30 if source_hit else 0)
    fields = [(6, entry.get('title', '')), (5, ' '.join(entry.get('aliases', []))),
              (8, ' '.join(sorted(declared_identities(entry, lowercase=False)))),
              (3, entry.get('engineering_question', '')),
              (1, json.dumps(entry.get('api_contracts', []), ensure_ascii=False))]
    relevance = 0
    whole_identifier_hit = bool(priority)
    for weight, text in fields:
        counts = Counter(token_sequence(text))
        whole_identifier_hit |= requested is not None and requested in counts
        # Bounded frequency: a large contract mentioning another owner's method
        # repeatedly cannot displace its declaration just by growing in length.
        relevance += weight * sum(min(counts[term], 3) / (min(counts[term], 3) + 1) for term in terms if counts[term])
    # Fragment tokens aid navigation for a component query (e.g. "Queue"), but
    # coincidental pieces such as Get/Value cannot fabricate a whole requested
    # identifier or a different qualified owner in the full research route.
    if requested is not None and not whole_identifier_hit:
        return 0
    return priority * 100 + min(relevance, 99)


# Navigation syntax only. It never establishes a physical/public declaration.
NAME = r'[A-Za-z_][A-Za-z0-9_]*(?:[.:][A-Za-z_][A-Za-z0-9_]*)*'
MODULE = r'require\((?P<quote>["\'])(?P<module>[A-Za-z0-9_/-]+)(?P=quote)\)\.(?P<member>[A-Za-z_][A-Za-z0-9_]*)'
IDENTITY_KINDS = ('component_method', 'method', 'module_export', 'file_local',
                  'environment_member', 'global', 'qualified_member', 'unknown')


def api_identity(api):
    """Conservative authored identity, distinct from accepted legacy declarations.

    A module export may have a local implementation; its export identity must
    not collapse into a same-name file-local helper. Preserve visibility prose.
    """
    text = api['symbol'].strip()
    visibility = api['visibility'].strip().lower()
    explicit_local = visibility.startswith(('file-local', 'local function', '文件局部', '文件 local'))
    not_exported = any(marker in visibility for marker in ('not exported', '未导出', '不导出'))
    explicit_export = visibility.startswith(('module export', '模块导出', '模块返回表'))
    module = re.fullmatch(MODULE + r'(?:\([^()]*\))?', text)
    if module:
        name = 'require("' + module['module'] + '").' + module['member']
        owner, leaf = 'require("' + module['module'] + '")', module['member']
        # A require-shaped name cannot override explicit local/negative metadata.
        # Without an authored export statement its visibility remains unknown.
        kind = 'file_local' if explicit_local else 'module_export' if explicit_export and not not_exported else 'unknown'
    else:
        match = re.fullmatch('(' + NAME + r')(?:\([^()]*\))?', text)
        if match is None:
            return None  # e.g. dynamic table indexing: no fabricated bare name
        name = match[1]
        parts = re.split('[.:]', name)
        owner, leaf = (re.split(r'[.:][^.:]+$', name)[0], parts[-1]) if len(parts)>1 else (None, name)
        if explicit_local:
            kind = 'file_local'
        elif not_exported:
            kind = 'unknown'
        elif explicit_export:
            kind = 'module_export'
        elif ':' in name:
            kind = 'component_method' if api['source_file'].startswith('scripts/components/') else 'method'
        elif name.startswith('env.'):
            kind = 'environment_member'
        elif visibility.startswith(('global ', 'raw global ', '原版全局', '全局原版')):
            kind = 'global'
        else:
            kind = 'qualified_member' if owner else 'unknown'
    return {'symbol': name, 'owner': owner, 'leaf': leaf, 'identity_kind': kind,
            'source_file': api['source_file'], 'visibility': api['visibility'],
            'identity_basis': 'AUTHORED_RESEARCH_CONTRACT_NOT_PHYSICAL_DECLARATION',
            'public_api_inferred': False}


def api_matches(records, symbol, source_file=None, owner=None, identity_kind=None):
    # Only api_contracts participate; aliases and source_references.symbols do not.
    matches = []
    qualified = '.' in symbol or ':' in symbol or symbol.startswith('require(')
    for identifier, record in sorted(records.items()):
        for index, api in enumerate(record['entry']['api_contracts']):
            identity = api_identity(api)
            if identity is None or (identity['symbol'] if qualified else identity['leaf']) != symbol:
                continue
            if source_file is not None and identity['source_file'] != source_file:continue
            if owner is not None and identity['owner'] != owner:continue
            if identity_kind is not None and identity['identity_kind'] != identity_kind:continue
            identity = dict(identity, source_epoch=record['document']['source_epoch'],
                            archive_sha256=record['document']['archive_sha256'])
            # Visibility and evidence version are not interchangeable identities.
            key = tuple(identity[k] for k in ('symbol','source_file','visibility','source_epoch','archive_sha256'))
            matches.append((key, record, '/api_contracts/' + str(index), identity))
    return matches

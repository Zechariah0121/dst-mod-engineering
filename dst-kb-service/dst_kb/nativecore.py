"""Native Core governance: independent states and explicit referenced evidence only."""
import copy
import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path, PureWindowsPath

from . import native
from .config import KBError

FILE = 'data/nativecore/native-core.json'
SCHEMA = 'native-core-governance/1'
TYPE = 'native_core_knowledge'
STATES = ('knowledge_status', 'retrieval_status', 'coding_status')
KNOWLEDGE = ('research', 'supported', 'canonical', 'corrected', 'superseded')
RETRIEVAL = ('reviewer_default', 'task_conditional', 'deep_only', 'restricted')
CODING = ('coding_default', 'coding_conditional', 'hold', 'prohibited')
HEX = re.compile(r'[a-f0-9]{64}')


def paths(root):
    return [FILE] if (root / FILE).is_file() else []


def pointer(document, reference):
    """Strict RFC 6901 tokens; no negative array indexing or malformed escapes."""
    if not isinstance(reference, str):
        raise ValueError('JSON pointer must be a string')
    reference = reference.removeprefix('#')
    if not reference.startswith('/'):
        raise ValueError('JSON pointer must start with /')
    result = document
    for token in reference[1:].split('/'):
        if re.search(r'~(?![01])', token):
            raise ValueError('Invalid JSON pointer escape')
        key = token.replace('~1', '/').replace('~0', '~')
        if isinstance(result, list):
            if not re.fullmatch(r'0|[1-9][0-9]*', key):
                raise ValueError('Invalid JSON pointer array index')
            result = result[int(key)]
        elif isinstance(result, dict):
            result = result[key]
        else:
            raise ValueError('JSON pointer traverses a scalar')
    return result


def accepted(entry):
    return entry.get('gate_a', {}).get('accepted') is True


def metadata(entry):
    return {key: copy.deepcopy(entry[key]) for key in ('id',) + STATES}


def reviewer_allowed(entry, explicit=False):
    if not accepted(entry):
        return False
    return explicit or (entry['knowledge_status'] != 'superseded' and entry['retrieval_status'] != 'restricted')


def coding_allowed(entry):
    return accepted(entry) and entry['coding_status'] in ('coding_default', 'coding_conditional') and entry['knowledge_status'] not in ('research', 'superseded') and entry['retrieval_status'] != 'restricted'


def matches(entry, query):
    value = native.normalized(query)
    return value == entry['id'].lower() or any(native.contains(value, term)
        for term in entry['aliases'] + entry['task_keywords'])


def references(entry):
    refs = list(entry['evidence_refs']) + list(entry['correction_refs'])
    for claim in entry['claims']:
        refs.extend(claim['evidence_refs'])
    refs.extend(node for node in native.walk(entry) if {'artifact_path','sha256','pointer'}.issubset(node))
    unique = {}
    for ref in refs:
        key = (ref['artifact_path'], ref['sha256'], ref['pointer'].removeprefix('#'))
        unique.setdefault(key, ref)
    return list(unique.values())


def expanded(entry, artifacts):
    return copy.deepcopy(entry) | {'reviewer_expansion': [
        {'reference': copy.deepcopy(ref), 'evidence': copy.deepcopy(pointer(artifacts[ref['artifact_path']], ref['pointer']))}
        for ref in references(entry)]}


def _historical_marker(node):
    return (node.get('evidence_role') == 'historical_comparison' or
            node.get('supports_current_behavior') is False or
            node.get('payload_status') == 'metadata_only')


def _historical_comparison(node):
    """An explicit, bounded history record is never current NSF evidence."""
    if not (node.get('evidence_role') == 'historical_comparison' and
            node.get('supports_current_behavior') is False and
            node.get('payload_status') == 'metadata_only'):
        return False
    path = node.get('path') or node.get('file') or node.get('source_file') or node.get('source_path')
    first, last = node.get('line_start'), node.get('line_end')
    metadata = node.get('original_payload_metadata')
    if (not isinstance(path, str) or not path.startswith('scripts/') or
            not path.endswith('.lua') or '\\' in path or ':' in path or
            any(part in ('', '.', '..') for part in path.split('/')) or
            any(not isinstance(node.get(key), str) or not HEX.fullmatch(node[key])
                for key in ('file_sha256', 'range_sha256')) or
            not isinstance(node.get('snapshot_id'), str) or not node['snapshot_id'].strip() or
            type(first) is not int or first <= 0 or type(last) is not int or last < first or
            not isinstance(metadata, dict) or
            metadata.get('content_sha256') != node['range_sha256'] or
            type(metadata.get('content_bytes')) is not int or metadata['content_bytes'] <= 0 or
            type(metadata.get('line_count')) is not int or metadata['line_count'] != last - first + 1 or
            not isinstance(metadata.get('original_json_value_sha256'), str) or
            not HEX.fullmatch(metadata['original_json_value_sha256'])):
        return False
    # A metadata-only marker cannot conceal source payload or nested locators.
    payload_keys = {'source_excerpt', 'excerpt', 'declaration_header', 'header', '$dst_source_payload_slot'}
    locator_keys = {'path', 'file', 'source_file', 'source_path', 'symbol', 'function',
                    'line_start', 'line_end', 'file_sha256', 'range_sha256'}
    return all(not (payload_keys & child.keys()) and
               (child is node or not (locator_keys & child.keys()))
               for child in native.walk(node))


def _locator_nodes(value, inherited_path=None, inherited_hash=None):
    if isinstance(value,dict):
        if _historical_comparison(value):
            return
        own_path=value.get('path') or value.get('file') or value.get('source_file') or value.get('source_path')
        path=own_path or inherited_path
        fingerprint=value.get('file_sha256',value.get('sha256')) or inherited_hash
        yield value,path,fingerprint,own_path
        for child in value.values():
            yield from _locator_nodes(child,path,fingerprint)
    elif isinstance(value,list):
        for child in value:yield from _locator_nodes(child,inherited_path,inherited_hash)


def _exact_excerpt_locator(node, path, fingerprint):
    """Validate a bounded original Lua range, without inventing an API symbol.

    This is package evidence-shape validation, not a declaration identity or
    behavior proof. API binding still requires the separate source registry.
    Source archive/file identities are independently audited and committed by
    the selected source environment.
    """
    excerpt = node.get('source_excerpt', node.get('excerpt'))
    first, last = node.get('line_start'), node.get('line_end')
    snapshot = node.get('snapshot_id')
    if (not isinstance(path, str) or not path.startswith('scripts/') or
            not path.endswith('.lua') or '\\' in path or ':' in path or
            any(part in ('', '.', '..') for part in path.split('/')) or
            not isinstance(fingerprint, str) or not HEX.fullmatch(fingerprint) or
            not isinstance(node.get('range_sha256'), str) or not HEX.fullmatch(node['range_sha256']) or
            not isinstance(snapshot, str) or not snapshot.strip() or
            type(first) is not int or first <= 0 or type(last) is not int or last < first or
            not isinstance(excerpt, str) or not excerpt):
        return False
    raw = excerpt.encode('utf-8')
    return (len(raw.splitlines(keepends=True)) == last - first + 1 and
            sha256(raw).hexdigest() == node['range_sha256'])


def _has_nsf_locator(values, scope):
    if any(_historical_marker(node) and not _historical_comparison(node)
           for value in values for node in native.walk(value)):
        return False
    snapshots = [scope.get('snapshot_id'), scope.get('source_snapshot_id')]
    snapshots.extend(item for value in values+[scope] for node,_,_,_ in _locator_nodes(value) for key,item in node.items()
                     if key=='snapshot_id' or key.endswith('_snapshot_id'))
    snapshots.extend(item for value in values+[scope] for node,_,_,_ in _locator_nodes(value) for key,item in node.items()
                     if (key=='source_commit' or key.endswith('_source_commit')) and isinstance(item,str) and re.fullmatch('[a-f0-9]{40}',item))
    if not any(isinstance(item, str) and item.strip() for item in snapshots):
        return False
    locators=[]
    for value in values:
        for node,path,fingerprint,own_path in _locator_nodes(value):
            symbol = node.get('symbol') or node.get('function')
            anchor = node.get('anchor') or node.get('supporting_locator', {}).get('anchor')
            first = node.get('line_start', node.get('start_line'))
            last = node.get('line_end', node.get('end_line', first))
            lines = type(first) is int and first > 0 and type(last) is int and last >= first
            if (symbol and (path or fingerprint or first is not None or anchor)) or (own_path and (first is not None or anchor)):
                valid=bool(path and symbol and isinstance(fingerprint,str) and HEX.fullmatch(fingerprint) and (anchor or lines))
                # Whole source ranges may cover constants, several declarations
                # or call sites; a fabricated function label adds no evidence.
                # Accept their exact original bytes, never just a line/hash label.
                if not symbol:
                    valid = _exact_excerpt_locator(node, path, fingerprint)
                locators.append(valid)
    return bool(locators) and all(locators)


def _has_runtime_record(values):
    for value in values:
        for node in native.walk(value):
            if node.get('evaluation_kind') or node.get('claim_type')=='HISTORICAL_PRODUCT_EVIDENCE':
                continue
            kind=node.get('claim_type',node.get('source_kind'))
            if kind in ('RV_OBSERVATION','RV_OBSERVATION_SYNTHESIS') and node.get('scope') and node.get('runtime_status') in ('CONFIRMED','HISTORICAL_CONFIRMED_NARROW') and node.get('new_runtime_execution') is not True:
                return True
    return False


def load(root, schema_errors, check_supported_schema, legacy_native_present=False, known_ids=()):
    if not paths(root):
        return None, {'present': False, 'entries': 0, 'state_registry_entries': 0}
    try:
        document = json.loads((root / FILE).read_text(encoding='utf-8'))
        schema = json.loads((root / 'schemas/native-core.schema.json').read_text(encoding='utf-8'))
        check_supported_schema(schema)
        errors = schema_errors(document, schema, schema, 'nativecore')
        if errors:
            raise KBError('CORRUPTED_KB', '; '.join(errors[:12]))
        entries = document['entries']
        states = document['state_registry']
        ids = [entry['id'] for entry in entries]
        state_ids = [row['id'] for row in states]
        byid = {entry['id']: entry for entry in entries}
        registry = {row['id']: row for row in states}
        if len(set(ids)) != len(ids) or set(ids) & (set(known_ids) | set(native.IDS)):
            errors.append('NativeCore duplicate or legacy ID namespace collision')
        if len(set(state_ids)) != len(state_ids):
            errors.append('NativeCore duplicate state registry ID')
        if legacy_native_present and not set(native.IDS).issubset(registry):
            errors.append('NativeCore requires complete N001 state registry')
        if set(state_ids) - (set(native.IDS) | set(ids)):
            errors.append('NativeCore unknown state registry ID')
        for row in states:
            if row['id'] in byid and any(row[key] != byid[row['id']][key] for key in STATES):
                errors.append('NativeCore registry/entry state contradiction: ' + row['id'])
        for entry in entries + states:
            if entry['retrieval_status'] == 'restricted' and entry['coding_status'] != 'prohibited':
                errors.append('NativeCore restricted entry must prohibit Coding: ' + entry['id'])
            if entry['knowledge_status'] == 'superseded' and entry['coding_status'] != 'prohibited':
                errors.append('NativeCore superseded entry must prohibit Coding: ' + entry['id'])
            if entry['knowledge_status'] == 'research' and entry['coding_status'] in CODING[:2]:
                errors.append('NativeCore unapproved research Coding admission: ' + entry['id'])
        for entry in entries:
            # 本轮知识接受与 Coding 准入分开；新研究不得因 Gate A 通过而进入 Coding。
            if entry['coding_status'] in CODING[:2]:
                errors.append('NativeCore sprint permits zero new Coding admissions: ' + entry['id'])
        artifacts = {}
        hashes = {}
        for row in document['source_artifacts']:
            relative = row['artifact_path']
            path = (root / relative).resolve()
            if Path(relative).is_absolute() or PureWindowsPath(relative).is_absolute() or '\\' in relative or not path.is_relative_to(root.resolve()):
                errors.append('NativeCore artifact outside KB: ' + relative)
                continue
            if relative in artifacts:
                errors.append('NativeCore duplicate artifact: ' + relative)
                continue
            if not path.is_file() or sha256(path.read_bytes()).hexdigest() != row['sha256']:
                errors.append('NativeCore artifact hash: ' + relative)
                continue
            if 'bytes' in row and (type(row['bytes']) is not int or row['bytes'] != path.stat().st_size):
                errors.append('NativeCore artifact bytes: ' + relative)
            artifacts[relative] = json.loads(path.read_text(encoding='utf-8')) if path.suffix.lower()=='.json' else path.read_text(encoding='utf-8')
            hashes[relative] = row['sha256']

        def resolve(ref, entry_id):
            relative = ref['artifact_path']
            if relative not in artifacts or hashes.get(relative) != ref['sha256']:
                errors.append('NativeCore reference artifact/hash: ' + entry_id)
                return None
            try:
                return pointer(artifacts[relative], ref['pointer'])
            except (ValueError, TypeError, KeyError, IndexError):
                errors.append('NativeCore unresolved JSON pointer: ' + entry_id)
                return None

        for artifact in document['source_artifacts']:
            if 'pointer' in artifact:resolve(artifact,'source_artifacts')
        for entry in entries:
            for ref in references(entry):
                resolve(ref, entry['id'])
            for claim in entry['claims']:
                if claim['kind'] == 'NSF':
                    values = [resolve(ref, entry['id']) for ref in claim['evidence_refs']]
                    entry_values = [resolve(ref, entry['id']) for ref in entry['evidence_refs']]
                    context = entry['scope'] | {'entry_reference_context':entry_values}
                    valid = _has_nsf_locator(values,context)
                    # Claim 的直接定位优先；entry 引用可补 snapshot 或无定位的 fact，不能掩盖损坏 citation。
                    has_claim_locator=any(((node.get('symbol') or node.get('function')) and (path or fingerprint or node.get('line_start',node.get('start_line')) is not None)) or (own_path and node.get('line_start',node.get('start_line')) is not None)
                                          for value in values for node,path,fingerprint,own_path in _locator_nodes(value))
                    # Explicit comparison-only refs cannot borrow entry evidence
                    # to become current-behavior claims, even when well formed.
                    has_claim_locator = has_claim_locator or any(_historical_marker(node)
                        for value in values for node in native.walk(value))
                    if not valid and not has_claim_locator:valid=_has_nsf_locator(values+entry_values,context)
                    if not valid:
                        errors.append('NativeCore NSF citation lacks snapshot/path/symbol/hash/anchor: ' + entry['id'])
                if claim['kind'] == 'RV':
                    values = [resolve(ref, entry['id']) for ref in claim['evidence_refs']]
                    if not _has_runtime_record(values):
                        errors.append('NativeCore RV requires claim-specific historical runtime, never product evaluation: ' + entry['id'])
        # 历史产品证据也只通过明确引用校验，禁止把旧 Eval Gate 作为 Research Canonical 门槛。
        for node in native.walk(document['historical_product_evidence']):
            if {'artifact_path', 'sha256', 'pointer'}.issubset(node):
                resolve(node, 'historical_product_evidence')
        if errors:
            raise KBError('CORRUPTED_KB', '; '.join(dict.fromkeys(errors))[:4000])
        return {'document': document, 'entries': entries, 'registry': registry, 'artifacts': artifacts}, {
            'present': True, 'status': 'PASS', 'schema_version': SCHEMA, 'version': document['version'],
            'entries': len(entries), 'state_registry_entries': len(states),
            'source_artifacts_checked': len(artifacts), 'reference_count': sum(len(references(entry)) for entry in entries),
            'knowledge_status_counts': dict(Counter(entry['knowledge_status'] for entry in entries)),
            'retrieval_status_counts': dict(Counter(entry['retrieval_status'] for entry in entries)),
            'coding_status_counts': dict(Counter(entry['coding_status'] for entry in entries)),
            'gate_a_accepted': sum(accepted(entry) for entry in entries),
            'new_coding_admissions': sum(coding_allowed(entry) for entry in entries),
            'runtime_validation_performed': False}
    except KBError:
        raise
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        raise KBError('CORRUPTED_KB', 'NativeCore: ' + str(exc)) from exc

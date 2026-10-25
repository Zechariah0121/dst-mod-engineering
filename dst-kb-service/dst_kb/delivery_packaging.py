"""Lossless card-local sharing for repeated delivery metadata, never fact text."""
import copy
import json
from collections import Counter


SCHEMA = 'dst-decision-metadata-sharing/2'
CHANNELS = ('facet_admission', 'task_admission', 'delivery_admission', 'context_closure',
            'contract_mapping', 'contract_delivery', 'companion_context_status', 'copy_bridge',
            'atomic_delivery')
ATOM_GROUPS = ('decision', 'critical_boundary', 'project_policy_questions')
VISIBLE = ('record_pointer', 'kind', 'role', 'symbol', 'receiver', 'binding_kind',
           'relation_polarity', 'admitted', 'supported', 'query_assertion_verified',
           'context_is_method_contract', 'callee_semantics_supported',
           'full_method_contract_verified', 'not_a_universal_method_subject',
           'necessary_dependency_verified', 'single_operation_verified')
INLINE = frozenset(('statement', 'source_scope', 'original_scope', 'scope', 'governance'))
LOCAL_IDENTITY = frozenset(('record_pointer', 'kind', 'symbol', 'receiver', 'relation_polarity',
                            'polarity', 'source_field', 'delivery_scope', 'contract_bindings'))
REF_IDENTITY = frozenset(('record_pointer', 'kind', 'role', 'symbol', 'receiver', 'relation_polarity'))


def _key(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _bytes(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


def _has_inline(value):
    if isinstance(value, dict):
        return bool(set(value) & INLINE) or any(_has_inline(child) for child in value.values())
    return isinstance(value, list) and any(_has_inline(child) for child in value)


def _channels(card):
    for name in CHANNELS:
        if name in card:
            yield card, name
    for name in ATOM_GROUPS:
        if name in card:
            yield card, name


def _share_scalar_metadata(card):
    """Use the existing exact metadata_ref inverse for repeated long scalars.

    This runs after compound factoring, so only repetitions still present on
    the serialized wire count. Statements, Scope, governance and visible atom
    identity remain inline. No new reference namespace or schema is introduced.
    """
    result = copy.deepcopy(card)
    protected = INLINE | (set(LOCAL_IDENTITY) - {'contract_bindings'}) | set(REF_IDENTITY)
    counts, originals = Counter(), {}

    def visit(value, replace=None):
        if isinstance(value, list):
            return [visit(child, replace) for child in value]
        if isinstance(value, dict):
            return {key: copy.deepcopy(child) if key in protected else visit(child, replace)
                    for key, child in value.items()}
        if isinstance(value, str) and len(value.encode('utf-8')) >= 32:
            marker = _key(value)
            if replace is None:
                counts[marker] += 1
                originals[marker] = value
            elif marker in replace:
                return {'metadata_ref': replace[marker]}
        return copy.deepcopy(value)

    table = result.get('shared_metadata')
    for owner, name in _channels(result):
        visit(owner[name])
    if isinstance(table, dict):
        for value in table['values'] + table['templates']:
            visit(value)
    existing = len(table['values']) if isinstance(table, dict) else 0
    chosen = [marker for marker, count in counts.items() if count > 1 and
              (count - 1) * _bytes(originals[marker]) > count * _bytes({'metadata_ref': existing}) + 16]
    if not chosen:
        return result
    if table is None:
        table = {'schema': SCHEMA, 'reference_space': 'THIS_CARD_SHARED_METADATA_VALUES_ZERO_BASED_INDEX',
            'interpretation': 'metadata_ref is one exact value; metadata_template contributes exactly its shared fields. Local fields cannot override different template values. Indices belong to this card only. Fact statements, Scope and governance stay inline.',
            'values': [], 'templates': []}
        result['shared_metadata'] = table
    mapping = {marker: len(table['values']) + index for index, marker in enumerate(chosen)}
    for owner, name in _channels(result):
        owner[name] = visit(owner[name], mapping)
    table['values'] = [visit(value, mapping) for value in table['values']]
    table['templates'] = [visit(value, mapping) for value in table['templates']]
    # Literal scalar entries are appended last and never rewritten as self refs.
    table['values'].extend(originals[marker] for marker in chosen)
    return result if _bytes(result) < _bytes(card) else copy.deepcopy(card)


def share_metadata(card, *, preserve_contracts=False):
    if 'shared_metadata' in card:
        return copy.deepcopy(card)
    result = copy.deepcopy(card)
    if 'companion_context' in result:
        result['companion_context'] = [share_metadata(child, preserve_contracts=preserve_contracts)
                                       for child in result['companion_context']]
    counts, lengths, shapes = Counter(), {}, {}

    def collect(value):
        if not isinstance(value, (dict, list)):
            return
        marker = _key(value)
        counts[marker] += 1
        lengths[marker] = len(marker.encode('utf-8'))
        children = value.values() if isinstance(value, dict) else value
        if isinstance(value, dict):
            shapes.setdefault(tuple(sorted(value)), []).append(value)
            for key, child in value.items():
                if key not in INLINE and not (preserve_contracts and key == 'contract_bindings'):
                    collect(child)
        else:
            for child in children:
                collect(child)

    for owner, name in _channels(result):
        collect(owner[name])
    candidates = {}
    for shape, rows in shapes.items():
        if len(rows) < 2:
            continue
        groups = [rows]
        # 同一源文件的不同原 pointer 共享精确路径/hash；各 pointer 与关系仍逐行保留。
        if {'artifact_path', 'sha256'}.issubset(shape):
            artifacts = {}
            for row in rows:
                artifacts.setdefault(_key([row['artifact_path'], row['sha256']]), []).append(row)
            groups.extend(artifacts.values())
        for group in groups:
            if len(group) < 2:
                continue
            common = {key: copy.deepcopy(group[0][key]) for key in shape
                      if key not in INLINE and (key not in LOCAL_IDENTITY or
                         (not preserve_contracts and key in ('polarity', 'source_field', 'delivery_scope')))
                      and not _has_inline(group[0][key])
                      and all(_key(row[key]) == _key(group[0][key]) for row in group[1:])}
            if common and (len(group) - 1) * _bytes(common) > len(group) * 40 + 80:
                for row in group:
                    marker = _key(row)
                    if _bytes(common) > _bytes(candidates.get(marker, {})):
                        candidates[marker] = common
    # 同卡合同只共享逐值相等的公共字段；各行身份与不同的来源/guard仍独立保留。
    mapping_rows = result.get('contract_mapping')
    if (isinstance(mapping_rows, list) and len(mapping_rows) >= 2
            and all(isinstance(row, dict) for row in mapping_rows)):
        common_keys = set.intersection(*(set(row) for row in mapping_rows))
        common = {key: copy.deepcopy(mapping_rows[0][key]) for key in sorted(common_keys)
                  if key not in INLINE and key not in LOCAL_IDENTITY
                  and key not in ('owner', 'role', 'guard', 'original_governance')
                  and not _has_inline(mapping_rows[0][key])
                  and all(_key(row[key]) == _key(mapping_rows[0][key]) for row in mapping_rows[1:])}
        if (common and (len(mapping_rows) - 1) * _bytes(common)
                > len(mapping_rows) * 40 + 80):
            for row in mapping_rows:
                marker = _key(row)
                if _bytes(common) > _bytes(candidates.get(marker, {})):
                    candidates[marker] = common
    values, identities, templates, template_identities = [], {}, [], {}

    def pack_template(value):
        common = candidates.get(_key(value))
        if common is None:
            return None
        marker = _key(common)
        if marker not in template_identities:
            # Templates contain their complete original common fields. A local
            # row never overrides a different owner, polarity or guard value.
            template_identities[marker] = len(templates)
            index = len(templates)
            templates.append(None)
            templates[index] = {key: pack(child) for key, child in common.items()}
        index = template_identities[marker]
        return {'metadata_template': index, **{key: (copy.deepcopy(child) if key in INLINE or
                (preserve_contracts and key == 'contract_bindings') else pack(child))
                for key, child in value.items() if key not in common}}

    def pack(value):
        if not isinstance(value, (dict, list)):
            return copy.deepcopy(value)
        marker = _key(value)
        shared = counts[marker] > 1 and lengths[marker] >= 160 and not _has_inline(value)
        visible = {key: copy.deepcopy(child) for key, child in value.items()
                   if key in REF_IDENTITY or 'owner' in key} if isinstance(value, dict) else {}
        if shared and marker in identities:
            return {'metadata_ref': identities[marker], **visible}
        packed = ({key: (copy.deepcopy(child) if key in INLINE or
                       (preserve_contracts and key == 'contract_bindings') else pack(child)) for key, child in value.items()} if isinstance(value, dict)
                  else [pack(child) for child in value])
        if isinstance(value, dict):
            templated = pack_template(value)
            if templated is not None and _bytes(templated) < _bytes(packed):
                packed = templated
        if not shared or _bytes(packed) <= _bytes({'metadata_ref': len(values), **visible}) + 24:
            return packed
        index = len(values)
        identities[marker] = index
        values.append(packed)
        return {'metadata_ref': index, **visible}

    for owner, name in _channels(result):
        if not (preserve_contracts and name == 'delivery_admission'):
            owner[name] = pack(owner[name])
    if values or templates:
        result['shared_metadata'] = {'schema': SCHEMA,
            'reference_space': 'THIS_CARD_SHARED_METADATA_VALUES_ZERO_BASED_INDEX',
            'interpretation': 'metadata_ref is one exact value; metadata_template contributes exactly its shared fields. Local fields cannot override different template values. Indices belong to this card only. Fact statements, Scope and governance stay inline.',
            'values': values, 'templates': templates}
    if not preserve_contracts:
        result = _share_scalar_metadata(result)
    return result if _bytes(result) < _bytes(card) else copy.deepcopy(card)


def expand_metadata(card):
    """Strict inverse for validation and consumers that need the full audit tree."""
    result = copy.deepcopy(card)
    table = result.pop('shared_metadata', None)
    if table is not None:
        if (not isinstance(table, dict) or table.get('schema') != SCHEMA
                or table.get('reference_space') != 'THIS_CARD_SHARED_METADATA_VALUES_ZERO_BASED_INDEX'
                or not isinstance(table.get('values'), list) or not isinstance(table.get('templates'), list)):
            raise ValueError('Invalid shared metadata schema')
        values = table['values']
        templates = table['templates']

        def expand(value, active=()):
            if isinstance(value, list):
                return [expand(child, active) for child in value]
            if not isinstance(value, dict):
                return copy.deepcopy(value)
            if 'metadata_ref' in value:
                index = value['metadata_ref']
                token = ('value', index)
                if (type(index) is not int or not 0 <= index < len(values) or token in active
                        or 'metadata_template' in value):
                    raise ValueError('Invalid card-local metadata reference')
                original = expand(values[index], active + (token,))
                for key, child in value.items():
                    if key != 'metadata_ref' and (not isinstance(original, dict) or key not in original
                                                  or _key(original[key]) != _key(child)):
                        raise ValueError('Shared metadata visible field mismatch')
                return original
            if 'metadata_template' in value:
                index = value['metadata_template']
                token = ('template', index)
                if type(index) is not int or not 0 <= index < len(templates) or token in active:
                    raise ValueError('Invalid card-local metadata template')
                original = expand(templates[index], active + (token,))
                if not isinstance(original, dict) or any(key in original for key in INLINE):
                    raise ValueError('Invalid shared metadata template value')
                for key, child in value.items():
                    if key == 'metadata_template':
                        continue
                    expanded = copy.deepcopy(child) if key in INLINE else expand(child, active)
                    if key in original and _key(original[key]) != _key(expanded):
                        raise ValueError('Shared metadata template field mismatch')
                    original[key] = expanded
                return original
            return {key: (copy.deepcopy(child) if key in INLINE else expand(child, active))
                    for key, child in value.items()}

        for owner, name in _channels(result):
            owner[name] = expand(owner[name])
    if 'companion_context' in result:
        result['companion_context'] = [expand_metadata(child) for child in result['companion_context']]
    return result

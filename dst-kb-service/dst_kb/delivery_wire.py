"""Semantic L1 transport projection after rich-card admission and validation.

This module does not select atoms, infer facts, read evidence, or replay queries.
Only named diagnostic details and redundant, well-shaped source proof locators
are deferred. Unknown values and all semantic restrictions remain deliverable.
"""
import copy
import json
import re
from collections import Counter
from hashlib import sha256

from .delivery_packaging import expand_metadata, share_metadata
from .source_epoch_runtime import epoch_arguments


SCHEMA = 'dst-agent-l1-wire/1'
PROFILE = 'semantic-values-and-explicit-gaps/6'
PUBLIC_PROFILE = 'semantic-values-public-contracts/1'
BUNDLE_PROFILE = 'semantic-values-and-explicit-gaps/7'
STATEMENT_REFERENCE_SCHEMA = 'dst-original-atom-statement-reference/1'
BINDING_SCHEMA = 'dst-agent-l1-binding-groups/1'
ATOM_GROUPS = ('decision', 'critical_boundary', 'project_policy_questions')
_OPAQUE = frozenset(('statement', 'source_scope', 'original_scope', 'scope',
                     'governance', 'original_governance', 'source_context',
                     'source_context_reference_proofs'))
_SUPPORT_DIAGNOSTICS = frozenset((
    'mechanism_hits', 'subject_hits', 'source_subjects', 'local_source_subjects',
    'inherited_source_subjects', 'inherited_source_symbols', 'requested_subjects',
    'matched_symbols', 'operation_hits', 'requested_operations', 'lexical_hits',
    'anchors', 'bounded_source_paths', 'bounded_query_paths',
    'verified_method_head_symbols', 'supported_task_units', 'source_unit',
    'task_unit', 'source_unit_sha256', 'task_unit_sha256',
    'source_unit_utf8_bytes', 'task_unit_utf8_bytes',
    'original_units_sha256', 'original_units_delivered_by_diagnostics',
    'effective_task_unit', 'request_context_units',
    'relevance_source_unit', 'relevance_content_anchors', 'relevance_shared_concerns',
    'relevance_original_pointer',
))
_MATCH_DIAGNOSTICS = frozenset((
    'matched_focus_terms', 'matched_atom_terms', 'matched_task_concepts',
    'source_supported_task_units', 'matched_semantic_unit_sha256',
    'matched_semantic_unit_utf8_bytes', 'absolute_relevance_floor',
    'task_phrases', 'topic_hits', 'primary_subject_hits', 'direct_topic_anchor',
    'score_components', 'query_relative_relevance_floor',
))
_PUBLIC_MATCH_POINTERS = frozenset(('source_supported_atom_pointers',
    'source_supported_policy_pointers', 'source_supported_nonpolicy_pointers'))
_PROOF_KEYS = frozenset(('schema', 'artifact_path', 'sha256', 'pointer',
    'record_sha256', 'record_pointer', 'claim_kind', 'symbol',
    'original_reference_integrity_verified', 'identity_is_native_declaration_proof'))
_REF_KEYS = frozenset(('artifact_path', 'sha256', 'pointer'))
_SHA = re.compile(r'[0-9a-fA-F]{64}')
_CHANNELS = frozenset(('facet_admission', 'task_admission', 'delivery_admission',
    'context_closure', 'contract_mapping', 'contract_delivery', 'match_reason',
    'companion_context_status', 'copy_bridge', 'record_context_delivery'))
_RELATION_LISTS = frozenset(('contract_bindings', 'bindings', 'context_pointer_bindings',
                           'source_adjacency_navigation', 'typed_context_reference_proofs'))
_ADMISSION_ROWS = {
    'task_admission': ('decisions', frozenset(('method', 'exact_symbol_contract_path',
        'entire_task_completion_proven', 'diagnostic_details_deferred',
        'diagnostic_details_sha256', 'decisions', 'decisions_deferred_count'))),
    'facet_admission': ('decisions', frozenset(('method', 'excluded_atom_count',
        'diagnostic_details_deferred', 'diagnostic_details_sha256',
        'decisions', 'decisions_deferred_count'))),
    'record_context_delivery': ('admission', frozenset(('relation', 'seed_record_pointers',
        'method_contract_verified', 'necessary_dependency_proven',
        'entire_task_completion_proven', 'admission', 'admission_deferred_count'))),
}
_DEBUG_ROW_KEYS = frozenset(('record_pointer', 'kind', 'admitted', 'reason',
    'consumption_hint', 'sample_identity', 'delivery_scope', 'support',
    'explicit_scope_excluded', 'different_proved_method_owner',
    'different_original_subject',
    'basis_admission', 'policy_decisions', 'other_distinct_results'))
_DEBUG_SUPPORT_KEYS = _SUPPORT_DIAGNOSTICS | frozenset((
    'supported', 'support_meaning', 'query_assertion_verified',
    'whole_atom_delivery_allowed', 'whole_atom_excluded_relation_owners',
    'subject_mismatch', 'excluded_source_scope', 'scoped_cleanup',
    'support_type', 'concrete_behavior', 'relation_evidence_roles',
    'relation_role_subjects', 'displayed_data_subjects', 'requested_operation_subjects',
    'display_consumer_relation', 'displayed_data_contract_verified', 'unit_lane',
    'relevance_lane', 'method_contract_verified',
))
_NODE_KEYS = frozenset(('original_record_pointer', 'record_sha256', 'scope_value_sha256',
    'role', 'basis_record_pointers', 'value', 'value_ref', 'facet_admission'))
_BUNDLE_DEFERRED_FIELDS = frozenset(('admission.support_details', 'admission.repeated_results',
    'query_selection', 'match_reason.details', 'facet_admission.decisions.support_details',
    'task_admission.decisions.support_details', 'unrequested_navigation_symbols',
    'noncanonical_consumption_hints', 'repeated_evidence_tool_argument_templates'))
_WIRE_KEYS = frozenset(('schema', 'profile', 'stage', 'omitted_diagnostic_or_provenance_fields',
    'whole_original_atoms_preserved', 'source_scope_and_governance_preserved',
    'query_diagnostics_recoverable_from_record_expansion', 'query_diagnostics_omitted',
    'record_expansion', 'source_provenance_omitted_is_not_new_evidence',
    'statement_reference_schema', 'original_atoms_and_scope_values_preserved'))


def _key(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _digest(value):
    return sha256(_key(value).encode('utf-8')).hexdigest()


def json_bytes(value):
    """UTF-8 size with the service's ordinary json.dumps representation."""
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


def _ref(value):
    return (isinstance(value, dict) and set(value) == _REF_KEYS
            and isinstance(value['artifact_path'], str) and bool(value['artifact_path'])
            and isinstance(value['pointer'], str) and value['pointer'].startswith('/')
            and isinstance(value['sha256'], str) and _SHA.fullmatch(value['sha256']))


def _proof(value, card):
    return (isinstance(value, dict) and set(value) <= _PROOF_KEYS
            and _REF_KEYS <= set(value)
            and _ref({key: value[key] for key in _REF_KEYS})
            and value.get('schema') == 'original-qualified-typed-atom-reference/1'
            and value.get('record_sha256') == card.get('record_sha256')
            and isinstance(value.get('record_pointer'), str)
            and value['record_pointer'].startswith('/')
            and isinstance(value.get('claim_kind'), str)
            and isinstance(value.get('symbol'), str)
            and type(value.get('original_reference_integrity_verified')) is bool
            and type(value.get('identity_is_native_declaration_proof')) is bool)


def _unique(values):
    seen, result = set(), []
    for value in values:
        marker = _key(value)
        if marker not in seen:
            result.append(value)
            seen.add(marker)
    return result


def _known_debug_row(row, *, compact_support=False):
    if (not isinstance(row, dict) or set(row) - _DEBUG_ROW_KEYS
            or type(row.get('admitted')) is not bool
            or not (isinstance(row.get('record_pointer'), str) or (
                compact_support and 'record_pointer' in row and row['record_pointer'] is None
                and row.get('kind') == 'REC' and row.get('consumption_hint') is True
                and row.get('admitted') is False))):
        return False
    # 无原文 pointer 的已拒绝合成提示仍须经过下方全部未知字段/关系守卫。
    for key in ('basis_admission', 'policy_decisions', 'other_distinct_results'):
        if key in row and (not isinstance(row[key], list)
                           or not all(_known_debug_row(child, compact_support=compact_support) for child in row[key])):
            return False
    support = row.get('support')
    if support is not None:
        extra_keys = {'bounded_knowledge_consultation', 'relevance_relation_frames'} if compact_support else set()
        if not isinstance(support, dict) or set(support) - (_DEBUG_SUPPORT_KEYS | extra_keys):
            return False
        # 只省略明确未启用的新诊断；有内容的关系帧仍可能承载主体/边界。
        if ('bounded_knowledge_consultation' in support
                and support['bounded_knowledge_consultation'] is not False):
            return False
        if ('relevance_relation_frames' in support and
                (type(support['relevance_relation_frames']) is not list or support['relevance_relation_frames'])):
            return False
        # 未知嵌套对象可能承载 owner/guard/依赖；不把它当作简单诊断吞掉。
        if any(isinstance(child, dict) or (isinstance(child, list)
               and any(isinstance(item, (dict, list)) for item in child))
               for child in support.values()):
            return False
        if support.get('query_assertion_verified', False) is not False:
            return False
        if support.get('method_contract_verified', False) is not False:
            return False
        if 'relevance_lane' in support and support['relevance_lane'] != 'ORIGINAL_CONTENT':
            return False
    return not any(isinstance(child, (dict, list)) for key, child in row.items()
                   if key not in ('support', 'basis_admission', 'policy_decisions', 'other_distinct_results'))


def _defer_admission_rows(card, defer, *, compact_empty=False):
    for channel, (key, allowed) in _ADMISSION_ROWS.items():
        block = card.get(channel)
        if not isinstance(block, dict) or set(block) - allowed or not isinstance(block.get(key), list):
            continue
        if (compact_empty and key == 'decisions' and not block[key]
                and key + '_deferred_count' not in block
                and block.get('diagnostic_details_deferred') is True
                and block.get('diagnostic_details_sha256') == _digest({'decisions': []})):
            # 只合并已证明为空的诊断；方法、排除数及合同限制仍原样送达。
            for name in (key, 'diagnostic_details_deferred', 'diagnostic_details_sha256'):
                block.pop(name)
            defer('empty_admission_diagnostics', 3)
            continue
        retained = [row for row in block[key] if not _known_debug_row(row, compact_support=compact_empty)]
        count = len(block[key]) - len(retained)
        if not count:
            continue
        if retained:
            block[key] = retained
        else:
            block.pop(key)
        block[key + '_deferred_count'] = block.get(key + '_deferred_count', 0) + count
        # 这些是本次 query 的执行证明，L2 原记录展开不能重现。
        block.pop('diagnostic_details_sha256', None)
        defer(channel + '.' + key, count)


def _defer_scope_node_hashes(card, defer):
    scope = card.get('source_scope')
    digest = card.get('record_sha256')
    if (not isinstance(scope, dict) or scope.get('scope_schema') != 'dst-semantic-scope/2.13'
            or not isinstance(digest, str) or not _SHA.fullmatch(digest)
            or scope.get('record_sha256') != digest or not isinstance(scope.get('nodes'), dict)):
        return
    count = 0
    for node in scope['nodes'].values():
        if (not isinstance(node, dict) or set(node) - _NODE_KEYS
                or node.get('record_sha256') != digest
                or not isinstance(node.get('original_record_pointer'), str)
                or not node['original_record_pointer'].startswith('/scope/')
                or ('value' in node) == ('value_ref' in node)):
            continue
        if 'value' in node:
            value = node['value']
        else:
            ref = node['value_ref']
            if (not isinstance(ref, dict) or set(ref) != {'card_pointer', 'reference_space'}
                    or ref.get('reference_space') != 'SINGLE_DECISION_CARD_JSON_POINTER'
                    or not isinstance(ref.get('card_pointer'), str)):
                continue
            match = re.fullmatch(r'/(decision|critical_boundary|project_policy_questions)/(0|[1-9][0-9]*)/statement',
                                 ref['card_pointer'])
            if match is None:
                continue
            atoms = card.get(match.group(1))
            index = int(match.group(2))
            if (not isinstance(atoms, list) or index >= len(atoms)
                    or not isinstance(atoms[index], dict) or 'statement' not in atoms[index]):
                continue
            value = atoms[index]['statement']
        if node.get('scope_value_sha256') != _digest(value):
            continue
        node.pop('record_sha256')
        node.pop('scope_value_sha256')
        count += 2
    if count:
        scope['node_provenance_hash_fields_deferred_count'] = count
        defer('source_scope.nodes.repeated_verified_hashes', count)


def _merge_bundle_notice(card, defer):
    block = card.get('bundle_packaging')
    if (not isinstance(block, dict) or set(block) != {'schema', 'deferred_diagnostic_fields',
            'diagnostic_expansion', 'whole_original_atoms_and_required_context_preserved'}
            or block.get('schema') != 'dst-bundle-decision/2'
            or block.get('whole_original_atoms_and_required_context_preserved') is not True
            or not isinstance(block.get('deferred_diagnostic_fields'), list)
            or any(not isinstance(name, str) or name not in _BUNDLE_DEFERRED_FIELDS
                   for name in block['deferred_diagnostic_fields'])
            or block.get('diagnostic_expansion') not in (
                'Original search_kb/lookup_api decision view and opt-in developer trace',
                'Opt-in developer trace; original record expansion does not reconstruct query diagnostics')):
        return
    card.pop('bundle_packaging')
    defer('bundle_packaging.repeated_wire_notice')


def _group_bindings(rows):
    if not (isinstance(rows, list) and rows and all(isinstance(row, dict)
            and 'symbol' in row and 'receiver' in row for row in rows)):
        return rows
    groups, indexes, order = [], {}, []
    for row in rows:
        metadata = copy.deepcopy({key: child for key, child in row.items()
                                  if key not in ('symbol', 'receiver')})
        dependencies = {}
        if isinstance(metadata.get('pointer_role'), dict):
            for key in ('basis_record_pointers', 'required_basis_record_pointers'):
                if key in metadata['pointer_role']:
                    dependencies[key] = metadata['pointer_role'].pop(key)
        marker = _key(metadata)
        if marker not in indexes:
            indexes[marker] = len(groups)
            groups.append({'binding': metadata, 'subjects': []})
        index = indexes[marker]
        subjects = groups[index]['subjects']
        order.append([index, len(subjects)])
        subject = {key: row[key] for key in ('symbol', 'receiver')}
        if dependencies:
            subject['pointer_role_dependencies'] = dependencies
        subjects.append(subject)
    grouped = {'binding_group_schema': BINDING_SCHEMA, 'groups': groups,
               'binding_order': order}
    return grouped if json_bytes(grouped) < json_bytes(rows) else rows


def expand_l1_metadata(card):
    """Resolve actual card-local metadata and exact grouped semantic bindings.

    This cannot restore omitted query diagnostics or source proof locators.
    The shared_metadata namespace is never borrowed from a parent or donor.
    """
    result = expand_metadata(card)
    referenced_atoms = {(name, index) for name in ATOM_GROUPS
        for index, atom in enumerate(result.get(name, []))
        if isinstance(atom, dict) and 'statement_ref' in atom}
    for name in ATOM_GROUPS:
        for atom in result.get(name, []):
            if not isinstance(atom, dict) or 'statement_ref' not in atom:
                continue
            wire = result.get('wire_projection', {})
            reference = atom['statement_ref']
            if (wire.get('profile') != BUNDLE_PROFILE
                    or wire.get('statement_reference_schema') != STATEMENT_REFERENCE_SCHEMA
                    or 'statement' in atom or not isinstance(reference, dict)
                    or set(reference) != {'card_pointer', 'reference_space'}
                    or reference.get('reference_space') != 'SINGLE_DECISION_CARD_JSON_POINTER'
                    or not isinstance(reference.get('card_pointer'), str)):
                raise ValueError('Invalid original atom statement reference')
            location = re.fullmatch(r'/(decision|critical_boundary|project_policy_questions)/(0|[1-9][0-9]*)/statement',
                                    reference['card_pointer'])
            if location is None:
                raise ValueError('Invalid original atom statement location')
            targets = result.get(location.group(1))
            index = int(location.group(2))
            if not isinstance(targets, list) or index >= len(targets):
                raise ValueError('Dangling original atom statement reference')
            target = targets[index]
            # Only a complete literal original in this card may be shared.
            # No chain, cycle, cross-card/epoch reference or kind coercion.
            if ((location.group(1), index) in referenced_atoms
                    or not isinstance(target, dict) or 'statement_ref' in target
                    or not isinstance(target.get('statement'), str)
                    or target.get('kind') != atom.get('kind')
                    or atom.get('kind') not in ('REC', 'EI', 'REC / EI', 'EI / REC')):
                raise ValueError('Invalid original atom statement target')
            atom['statement'] = target['statement']
            atom.pop('statement_ref')
    for name in ATOM_GROUPS:
        for atom in result.get(name, []):
            packed = atom.get('contract_bindings') if isinstance(atom, dict) else None
            if not isinstance(packed, dict) or 'binding_group_schema' not in packed:
                continue
            if (packed.get('binding_group_schema') != BINDING_SCHEMA
                    or set(packed) != {'binding_group_schema', 'groups', 'binding_order'}
                    or not isinstance(packed['groups'], list)
                    or not isinstance(packed['binding_order'], list)):
                raise ValueError('Invalid L1 binding groups')
            groups, rows, used = packed['groups'], [], set()
            for item in packed['binding_order']:
                if (not isinstance(item, list) or len(item) != 2
                        or any(type(index) is not int for index in item)):
                    raise ValueError('Invalid L1 binding order')
                index, subject_index = item
                if not 0 <= index < len(groups):
                    raise ValueError('Dangling L1 binding group')
                group = groups[index]
                if (not isinstance(group, dict) or set(group) != {'binding', 'subjects'}
                        or not isinstance(group['binding'], dict)
                        or set(group['binding']) & {'symbol', 'receiver'}
                        or not isinstance(group['subjects'], list)
                        or not 0 <= subject_index < len(group['subjects'])):
                    raise ValueError('Invalid L1 binding subject')
                subject = group['subjects'][subject_index]
                if (not isinstance(subject, dict) or not {'symbol', 'receiver'} <= set(subject)
                        or set(subject) - {'symbol', 'receiver', 'pointer_role_dependencies'}):
                    raise ValueError('Invalid L1 binding identity')
                token = (index, subject_index)
                if token in used:
                    raise ValueError('Repeated L1 binding order')
                used.add(token)
                row = {**{key: copy.deepcopy(subject[key]) for key in ('symbol', 'receiver')},
                       **copy.deepcopy(group['binding'])}
                if 'pointer_role_dependencies' in subject:
                    dependencies = subject['pointer_role_dependencies']
                    if (not isinstance(dependencies, dict) or set(dependencies) - {
                            'basis_record_pointers', 'required_basis_record_pointers'}
                            or not isinstance(row.get('pointer_role'), dict)
                            or set(dependencies) & set(row['pointer_role'])):
                        raise ValueError('Invalid L1 binding dependencies')
                    row['pointer_role'].update(copy.deepcopy(dependencies))
                rows.append(row)
            if len(used) != sum(len(group.get('subjects', [])) for group in groups
                                if isinstance(group, dict)):
                raise ValueError('Unreachable L1 binding subject')
            atom['contract_bindings'] = rows
    if 'companion_context' in result:
        result['companion_context'] = [expand_l1_metadata(child) for child in result['companion_context']]
    return result


def _share_repeated_statements(card):
    """Share exact repeated recommendation prose, preserving every identity.

    This does not infer that evidence, Scope or restrictions are equivalent:
    all of each original atom's other fields remain on that original atom.
    Selection and Scope rebuilding happen before this local presentation step.
    """
    first, references, existing_targets = {}, 0, set()

    def collect_targets(value):
        if isinstance(value, list):
            for child in value:
                collect_targets(child)
        elif isinstance(value, dict):
            if isinstance(value.get('card_pointer'), str):
                existing_targets.add(value['card_pointer'])
            for child in value.values():
                collect_targets(child)
    collect_targets(card)
    for name in ATOM_GROUPS:
        for index, atom in enumerate(card.get(name, [])):
            if (not isinstance(atom, dict) or atom.get('kind') not in
                    ('REC', 'EI', 'REC / EI', 'EI / REC')
                    or not isinstance(atom.get('statement'), str) or not atom['statement']
                    or not isinstance(atom.get('record_pointer'), str)):
                continue
            marker = (atom['kind'], atom['statement'])
            if marker not in first:
                first[marker] = f'/{name}/{index}/statement'
                continue
            if f'/{name}/{index}/statement' in existing_targets:
                # Scope/unknown semantic references already name this literal.
                # Keep it in place instead of rewriting any original binding.
                continue
            reference = {'card_pointer': first[marker],
                         'reference_space': 'SINGLE_DECISION_CARD_JSON_POINTER'}
            if json_bytes({'statement_ref': reference}) >= json_bytes({'statement': atom['statement']}):
                continue
            atom.pop('statement')
            atom['statement_ref'] = reference
            references += 1
    if references:
        wire = card.setdefault('wire_projection', {'schema': SCHEMA})
        wire['profile'] = BUNDLE_PROFILE
        wire['statement_reference_schema'] = STATEMENT_REFERENCE_SCHEMA
    return card


def _defer_query_navigation(match, card):
    """Defer only named query navigation, independently of other match guards.

    A positive task can carry diagnostic support alongside semantic exclusions.
    An unrecognized sibling must not force repeated source locators into every
    atom trial, nor authorize discarding that sibling or its restrictions.
    """
    if not isinstance(match, dict):
        return 0
    symbols = match.get('matched_contract_navigation')
    if isinstance(symbols, list) and symbols and all(isinstance(symbol, str) for symbol in symbols):
        match.pop('matched_contract_navigation')
    recall = match.get('independent_task_recall')
    if (isinstance(recall, dict) and set(recall) == {'method', 'supported_task_units',
            'cross_record_dependency_proven', 'absolute_floor_unchanged', 'relative_fraction_unchanged'}
            and recall['method'] == 'ORIGINAL_SUPPORTED_SUBQUESTION_POOLS'
            and recall['cross_record_dependency_proven'] is False
            and isinstance(recall['supported_task_units'], list)
            and all(isinstance(unit, str) for unit in recall['supported_task_units'])
            and all(type(recall[key]) in (int, float) for key in
                    ('absolute_floor_unchanged', 'relative_fraction_unchanged'))):
        match.pop('independent_task_recall')
    navigation = match.get('exact_source_symbol_navigation')
    if not isinstance(navigation, list) or not navigation:
        return 0

    def diagnostic(row):
        keys = {'symbol', 'artifact_path', 'sha256', 'pointer', 'record_pointer',
                'source_file', 'role', 'context_only', 'claim_kind', 'record_sha256',
                'original_scope_ref', 'original_reference_integrity_verified'}
        if not isinstance(row, dict):
            return False
        adjacent = (set(row) == keys
            and row.get('role') == 'explicit_original_typed_context_reference_not_method_proof'
            and row.get('context_only') is True)
        cited_navigation = (set(row) == keys - {'context_only'}
            and row.get('role') == 'exact_cited_source_symbol_navigation_not_new_fact')
        if (not (adjacent or cited_navigation)
                or not _ref({key: row[key] for key in _REF_KEYS})
                or not isinstance(row['symbol'], str)
                or not isinstance(row['record_pointer'], str)
                or not row['record_pointer'].startswith('/')
                or row['record_sha256'] != card.get('record_sha256')
                or row['original_reference_integrity_verified'] is not True
                or not isinstance(row['claim_kind'], str)
                or row['source_file'] is not None and not isinstance(row['source_file'], str)):
            return False
        scope = row['original_scope_ref']
        expected = {'tool': 'get_entry', 'arguments': epoch_arguments({
            'id': card.get('id'), 'projection': 'reviewer', 'view': 'reviewer'})}
        return (isinstance(scope, dict) and set(scope) == {'original_record_pointer',
                'record_sha256', 'scope_value_sha256', 'record_scope_expansion',
                'full_original_scope_at_card_pointer'}
            and scope['original_record_pointer'] == '/scope'
            and scope['record_sha256'] == card.get('record_sha256')
            and isinstance(scope['scope_value_sha256'], str)
            and _SHA.fullmatch(scope['scope_value_sha256'])
            and scope['record_scope_expansion'] == expected
            and scope['full_original_scope_at_card_pointer'] is False)

    retained = [row for row in navigation if not diagnostic(row)]
    if retained:
        match['exact_source_symbol_navigation'] = retained
    else:
        match.pop('exact_source_symbol_navigation')
    return len(navigation) - len(retained)


def _defer_scope_navigation_proofs(scope, card):
    """Defer only closed, already-verified projection-header navigation proofs."""
    if not isinstance(scope, dict) or not isinstance(scope.get('source_metadata_navigation_proofs'), list):
        return
    prior = scope.get('deferred_navigation_proofs')
    status = {'proof_role': 'SOURCE_METADATA_NAVIGATION_ONLY', 'new_fact': False,
              'method_dependency': False, 'necessary_scope_enumeration_proven': False}
    if prior is not None and (not isinstance(prior, dict) or set(prior) != set(status) | {'count'}
            or type(prior.get('count')) is not int or prior['count'] < 0
            or any(type(prior.get(key)) is not type(value) or prior[key] != value for key, value in status.items())):
        return
    keys = {'schema', 'proof_role', 'record_sha256', 'scope_pointer', 'scope_value_sha256',
        'original_reference_owner', 'original_reference', 'source_scope_reference', 'source_node_role',
        'source_field_pointer', 'source_field_role', 'source_field_value_sha256', 'source_node_sha256',
        'new_fact', 'method_dependency', 'necessary_scope_enumeration_proven'}
    def known(proof):
        if (not isinstance(proof, dict) or set(proof) != keys
                or proof.get('schema') != 'source-backed-scope-navigation-proof/1'
                or proof.get('record_sha256') != card.get('record_sha256')
                or any(type(proof.get(key)) is not type(value) or proof[key] != value for key, value in status.items())
                or proof.get('source_node_role') != 'CODING_PROJECTION_HEADER'
                or not isinstance(proof.get('source_field_role'), str)
                or not all(isinstance(proof.get(key), str) and _SHA.fullmatch(proof[key]) for key in
                    ('record_sha256', 'scope_value_sha256', 'source_field_value_sha256', 'source_node_sha256'))
                or proof['scope_value_sha256'] != proof['source_field_value_sha256']
                or not isinstance(proof.get('original_reference_owner'), str)
                or not re.fullmatch(r'/evidence_refs/[0-9]+', proof['original_reference_owner'])
                or not _ref(proof.get('original_reference')) or not _ref(proof.get('source_scope_reference'))):
            return False
        source, reference = proof['original_reference'], proof['source_scope_reference']
        field = {'PROJECTION_LOAD_WHEN': ('load_when', 'load_when_zh'),
                 'PROJECTION_TITLE': ('original_question', 'title_zh')}.get(proof['source_field_role'])
        return bool(field and reference['pointer'] == '/scope'
            and source['artifact_path'] == reference['artifact_path'] and source['sha256'] == reference['sha256']
            and re.fullmatch(r'/coding_projection/[0-9]+', source['pointer'])
            and isinstance(proof['scope_pointer'], str)
            and re.fullmatch(r'/scope/source_scopes/[0-9]+/' + field[0], proof['scope_pointer'])
            and proof['source_field_pointer'] == source['pointer'] + '/' + field[1])
    proofs = scope['source_metadata_navigation_proofs']
    retained = [proof for proof in proofs if not known(proof)]
    deferred = len(proofs) - len(retained)
    if deferred:
        if retained:
            scope['source_metadata_navigation_proofs'] = retained
        else:
            scope.pop('source_metadata_navigation_proofs')
        scope['deferred_navigation_proofs'] = {'count': deferred + (prior['count'] if prior else 0), **status}


def _defer_identity_query_group(group, card):
    keys = {'symbol', 'receiver', 'mapping_status', 'mapping_basis', 'binding_kind', 'record_pointers',
        'claim_kinds', 'availability_record_pointers', 'availability_claim_kinds', 'pointer_roles',
        'record_sha256', 'original_governance', 'method_semantics_not_synthesized', 'context_record_pointers',
        'context_claim_kinds', 'context_pointer_bindings', 'context_is_method_contract', 'context_closure_gaps',
        'context_admission', 'needed_context_excluded', 'context_dependency_edges', 'source_references_expanded',
        'original_scope_ref'}
    empty = ('record_pointers', 'claim_kinds', 'availability_record_pointers', 'availability_claim_kinds',
        'context_record_pointers', 'context_claim_kinds', 'context_pointer_bindings', 'context_closure_gaps',
        'context_admission', 'needed_context_excluded', 'context_dependency_edges')
    if (not isinstance(card.get('source_scope'), dict)
            or not isinstance(group, dict) or set(group) - keys or group.get('mapping_status') != 'IDENTITY_ONLY'
            or group.get('binding_kind') != 'identity_only'
            or group.get('mapping_basis') != 'NAVIGATION_ONLY_NO_MAPPED_TYPED_CONTRACT'
            or not isinstance(group.get('symbol'), str)
            or group.get('receiver') is not None and not isinstance(group['receiver'], str)
            or group.get('record_sha256') != card.get('record_sha256')
            or group.get('record_pointers') != [] or group.get('pointer_roles') != {}
            or any(key in group and group[key] != [] for key in empty)
            or group.get('context_is_method_contract') is not False
            or group.get('source_references_expanded') is not False
            or group.get('method_semantics_not_synthesized') is not True):
        return
    ref, governance = group.get('original_scope_ref'), group.get('original_governance')
    if (not isinstance(ref, dict) or set(ref) != {'original_record_pointer', 'record_sha256', 'scope_value_sha256',
            'record_scope_expansion', 'canonical_scope_identity_verified', 'card_pointer', 'reference_space',
            'full_original_scope_at_card_pointer', 'shared_scope_is_selected_semantic_nodes'}
            or ref.get('record_sha256') != card.get('record_sha256')
            or ref.get('scope_value_sha256') != card.get('source_scope', {}).get('scope_value_sha256')
            or ref.get('original_record_pointer') != '/scope' or ref.get('card_pointer') != '/source_scope'
            or ref.get('reference_space') != 'SINGLE_DECISION_CARD_JSON_POINTER'
            or ref.get('record_scope_expansion') != 'get_entry(view=reviewer|evidence)'
            or ref.get('canonical_scope_identity_verified') is not True
            or ref.get('shared_scope_is_selected_semantic_nodes') is not True
            or ref.get('full_original_scope_at_card_pointer') is not False
            or not isinstance(governance, dict) or set(governance) - {'id', 'knowledge_status', 'retrieval_status', 'coding_status'}
            or 'id' in governance and governance['id'] != card.get('id')
            or any(governance.get(key) != card.get('governance', {}).get(key)
                   for key in ('knowledge_status', 'retrieval_status', 'coding_status'))):
        return
    preserved = {key: value for key, value in group.items() if key in {'symbol', 'receiver', 'mapping_status',
        'binding_kind', 'record_pointers', 'pointer_roles', 'context_is_method_contract', 'context_closure_gaps',
        'context_dependency_edges', 'needed_context_excluded'}}
    group.clear()
    group.update(preserved, details_deferred=True, full_method_contract_verified=False)


def _defer_contract_group_provenance(group, card):
    """Defer known L2/L3 provenance and empty navigation display fields.

    Method roles, polarity, restrictions, dependency edges and unknown children
    retain their values. Atoms and selected semantic Scope stay in the body.
    """
    if not isinstance(group, dict):
        return
    scope = card.get('source_scope')
    reference = group.get('original_scope_ref')
    reference_keys = {'original_record_pointer', 'record_sha256', 'scope_value_sha256',
        'record_scope_expansion', 'canonical_scope_identity_verified', 'card_pointer',
        'reference_space', 'full_original_scope_at_card_pointer', 'shared_scope_is_selected_semantic_nodes'}
    if (isinstance(scope, dict) and scope.get('scope_schema') == 'dst-semantic-scope/2.13'
            and isinstance(reference, dict) and not set(reference) - reference_keys
            and reference.get('record_sha256') == card.get('record_sha256') == scope.get('record_sha256')
            and reference.get('scope_value_sha256') == scope.get('scope_value_sha256')
            and isinstance(reference.get('scope_value_sha256'), str)
            and _SHA.fullmatch(reference['scope_value_sha256'])
            and reference.get('original_record_pointer') == '/scope'
            and reference.get('card_pointer') == '/source_scope'
            and reference.get('reference_space') == 'SINGLE_DECISION_CARD_JSON_POINTER'
            and reference.get('canonical_scope_identity_verified') is True
            and reference.get('full_original_scope_at_card_pointer') is False
            and reference.get('shared_scope_is_selected_semantic_nodes') is True
            and reference.get('record_scope_expansion') == 'get_entry(view=reviewer|evidence)'):
        group.pop('original_scope_ref')
    digest = card.get('record_sha256')
    if isinstance(digest, str) and _SHA.fullmatch(digest) and group.get('record_sha256') == digest:
        group.pop('record_sha256')
    governance = card.get('governance')
    original_governance = group.get('original_governance')
    if (isinstance(governance, dict) and isinstance(original_governance, dict)
            and not set(original_governance) - {'id', 'knowledge_status', 'retrieval_status', 'coding_status'}
            and ('id' not in original_governance or original_governance['id'] == card.get('id'))
            and all(key in governance and governance[key] == value
                    for key, value in original_governance.items() if key != 'id')):
        group.pop('original_governance')
    if group.get('mapping_basis') == 'WHOLE_ORIGINAL_NSF_WITH_EXPLICIT_ROLE_AND_SEPARATE_AVAILABILITY':
        group.pop('mapping_basis')
    if group.get('source_references_expanded') is False:
        group.pop('source_references_expanded')
    for key in ('availability_record_pointers', 'availability_claim_kinds', 'context_admission',
                'context_claim_kinds', 'context_pointer_bindings', 'context_record_pointers'):
        if group.get(key) == []:
            group.pop(key)


def compact_bundle_diagnostics(card):
    """Defer navigation and redundant diagnostics, after atomic selection.

    This is a presentation projection, not an inverse for query diagnostics.
    Original atoms, semantic Scope values, negative/unknown proof boundaries
    and source-condition bindings are untouched. Unknown diagnostic children
    prevent pruning their containing block. Ordinary search/get_entry retain
    their established presentation.
    """
    if not isinstance(card, dict) or card.get('level') != 1:
        return copy.deepcopy(card)
    result = expand_l1_metadata(card)
    prior_wire = result.pop('wire_projection', None)
    prior_navigation_count = (prior_wire.get('omitted_diagnostic_or_provenance_fields', {}).get(
        'query_source_symbol_navigation', 0) if isinstance(prior_wire, dict)
        and isinstance(prior_wire.get('omitted_diagnostic_or_provenance_fields', {}), dict) else 0)
    prior_positive_rows = (prior_wire.get('omitted_diagnostic_or_provenance_fields', {}).get(
        'positive_query_admission_rows', 0) if isinstance(prior_wire, dict)
        and isinstance(prior_wire.get('omitted_diagnostic_or_provenance_fields', {}), dict) else 0)
    deferred_positive_rows = 0
    unknown_wire = ({key: copy.deepcopy(value) for key, value in prior_wire.items() if key not in _WIRE_KEYS}
                    if isinstance(prior_wire, dict) else {})
    match = result.get('match_reason')
    deferred_query_navigation = _defer_query_navigation(match, result)
    known_match = {'pipeline', 'family', 'exact_id', 'matched_symbols',
        'single_symbol_contract_identity', 'source_atom_pointer', 'matched_unit_lane',
        'admission', 'project_policy_requested', 'policy_resolved', 'generated_metadata_ranked'}
    known_match |= _PUBLIC_MATCH_POINTERS
    # These are exact empty-query diagnostics already emitted by retrieval.
    # Any different value or unknown child remains an unrecognized structure.
    empty_defaults = {'matched_contract_navigation': [], 'task_semantic_anchor': False,
        'source_task_support': {'supported': False, 'reason': 'EMPTY_QUERY_DEFAULT_ADMISSION'},
        'source_support_universe': 'ORIGINAL_DELIVERABLE_ATOMS_AND_BOUNDARIES',
        'negative_intent_applied': [], 'review_guards_applied': [],
        'exact_source_symbol_navigation': [], 'diagnostic_source_prose_deferred': True}
    empty_support_schema = (isinstance(match, dict) and match.get('pipeline') == 'native-retrieval/2.13'
        and json.dumps(match.get('source_task_support'), ensure_ascii=False, sort_keys=True) ==
        json.dumps(empty_defaults['source_task_support'], ensure_ascii=False, sort_keys=True))
    support = match.get('source_task_support') if isinstance(match, dict) else None
    positive_support_diagnostic = (isinstance(support, dict)
        and match.get('pipeline') == 'native-retrieval/2.13'
        and support.get('supported') is True
        and support.get('support_meaning') == 'TASK_RELEVANCE_ONLY'
        and support.get('query_assertion_verified') is False
        and support.get('whole_atom_delivery_allowed', True) is True
        and _known_debug_row({'record_pointer': '/query', 'admitted': True, 'support': support},
                             compact_support=True)
        and all(support.get(key, False) is False for key in (
            'subject_mismatch', 'excluded_source_scope', 'scoped_cleanup',
            'display_consumer_relation', 'displayed_data_contract_verified'))
        and all(support.get(key, []) == [] for key in ('relation_evidence_roles',
            'relation_role_subjects', 'whole_atom_excluded_relation_owners', 'displayed_data_subjects')))
    recognized_defaults = {key for key, value in match.items() if key in empty_defaults and
        json.dumps(value, ensure_ascii=False, sort_keys=True) ==
        json.dumps(empty_defaults[key], ensure_ascii=False, sort_keys=True)} if (
            empty_support_schema or positive_support_diagnostic) else set()
    if positive_support_diagnostic:
        recognized_defaults.add('source_task_support')
        known_match.add('task_semantic_anchor')
    known_match |= recognized_defaults
    admission_shape = match.get('admission') if isinstance(match, dict) else None
    known_admission = (admission_shape is None or isinstance(admission_shape, dict)
        and not set(admission_shape) - {'projection', 'knowledge_status', 'retrieval_status',
                                      'coding_status', 'strong_task_trigger'}
        and all(not isinstance(value, (dict, list)) for value in admission_shape.values()))
    known_match_values = isinstance(match, dict) and all(key in recognized_defaults or key == 'admission' or
        (key in _PUBLIC_MATCH_POINTERS | {'matched_symbols'} and isinstance(value, list)
         and all(isinstance(symbol, str) for symbol in value)) or
        not isinstance(value, (dict, list)) for key, value in match.items())
    if isinstance(match, dict) and not set(match) - known_match and known_admission and known_match_values:
        result.pop('match_reason')
    elif (isinstance(match, dict) and match.get('pipeline') == 'native-retrieval/2.13'
            and isinstance(support, dict) and support.get('supported') is True
            and support.get('support_meaning') == 'TASK_RELEVANCE_ONLY'
            and support.get('query_assertion_verified') is False):
        # An active role/frame keeps its own support block. It does not make
        # unrelated query ranking scalars into conditions of the original fact.
        neutral = {
            'pipeline': 'native-retrieval/2.13', 'family': result.get('family'),
            'exact_id': False, 'single_symbol_contract_identity': False,
            'generated_metadata_ranked': False, 'diagnostic_source_prose_deferred': True,
            'source_support_universe': 'ORIGINAL_DELIVERABLE_ATOMS_AND_BOUNDARIES'}
        for key, expected in neutral.items():
            if key in match and type(match[key]) is type(expected) and match[key] == expected:
                match.pop(key)
        for key in ('matched_symbols', 'matched_contract_navigation'):
            if isinstance(match.get(key), list) and all(isinstance(value, str) for value in match[key]):
                match.pop(key)
        for key in ('negative_intent_applied', 'review_guards_applied', 'exact_source_symbol_navigation'):
            if match.get(key) == []:
                match.pop(key)
        if type(match.get('task_semantic_anchor')) is bool:
            match.pop('task_semantic_anchor')
        if (isinstance(match.get('source_atom_pointer'), str)
                and match['source_atom_pointer'].startswith('/')):
            match.pop('source_atom_pointer')
        if match.get('matched_unit_lane') in ('ORIGINAL_NONPOLICY_ATOM', 'ORIGINAL_POLICY_ATOM'):
            match.pop('matched_unit_lane')
        for key in ('project_policy_requested', 'policy_resolved'):
            if key in match and type(match[key]) is bool and match[key] is result.get(key):
                match.pop(key)
        admission = match.get('admission')
        governance = result.get('governance')
        if isinstance(admission, dict) and isinstance(governance, dict):
            for key in ('knowledge_status', 'retrieval_status', 'coding_status'):
                if (isinstance(admission.get(key), str) and key in governance
                        and admission[key] == governance[key]):
                    admission.pop(key)
    represented = {atom.get('record_pointer') for group in ATOM_GROUPS
                   for atom in result.get(group, []) if isinstance(atom, dict)}
    for group in result.get('contract_mapping', []):
        _defer_identity_query_group(group, result)
        _defer_contract_group_provenance(group, result)
        pointers = group.get('record_pointers') if isinstance(group, dict) else None
        if (not isinstance(pointers, list) or not pointers
                or any(not isinstance(pointer, str) for pointer in pointers)
                or set(pointers) & represented):
            continue
        deferred = []
        scope_ref = group.get('original_scope_ref')
        if (isinstance(scope_ref, dict) and set(scope_ref) <= {
                'original_record_pointer', 'record_sha256', 'scope_value_sha256',
                'record_scope_expansion', 'canonical_scope_identity_verified', 'card_pointer',
                'reference_space', 'full_original_scope_at_card_pointer', 'shared_scope_is_selected_semantic_nodes'}
                and scope_ref.get('record_sha256') == result.get('record_sha256')
                and scope_ref.get('original_record_pointer') == '/scope'
                and scope_ref.get('canonical_scope_identity_verified') is True
                and scope_ref.get('full_original_scope_at_card_pointer') is False):
            group.pop('original_scope_ref')
            deferred.append('original_scope_ref')
        navigation = group.get('source_adjacency_navigation')
        if (isinstance(navigation, list) and navigation and all(isinstance(row, dict)
                and set(row) <= {'record_pointer', 'kind', 'relation', 'dependency_verified',
                                'basis_evidence_references_deferred'}
                and row.get('relation') == 'SHARED_GROUPED_SOURCE_CITATION_NAVIGATION_ONLY'
                and row.get('dependency_verified') is False for row in navigation)):
            group.pop('source_adjacency_navigation')
            deferred.append('source_adjacency_navigation')
        roles = group.get('pointer_roles')
        role_keys = {'role', 'basis', 'callee_semantics_supported', 'claim_kind',
            'positive_callsite_evidence', 'relation_polarity', 'binding_kind',
            'reference_context_only', 'context_is_method_contract', 'full_method_contract_verified'}
        if (isinstance(roles, dict) and roles and set(roles) <= set(pointers)
                and all(isinstance(role, dict) and not set(role) - role_keys
                    and role.get('claim_kind') == 'NSF' and role.get('role') in {
                        'METHOD_SUBJECT', 'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL',
                        'BOUNDED_CALLEE_RELATION_UNDETERMINED'}
                    and not any(isinstance(value, (dict, list)) for value in role.values())
                    and ('basis' not in role or role['basis'] == 'RECLASSIFIED_LOCAL_RELATION_IN_ORIGINAL_TYPED_STATEMENT')
                    for role in roles.values())):
            group.pop('pointer_roles')
            group['deferred_pointer_role_count'] = len(roles)
            deferred.append('pointer_roles')
        if group.get('mapping_basis') == 'WHOLE_ORIGINAL_NSF_WITH_EXPLICIT_ROLE_AND_SEPARATE_AVAILABILITY':
            group.pop('mapping_basis')
            deferred.append('mapping_basis')
        if group.get('original_governance') == result.get('governance') and isinstance(result.get('governance'), dict):
            group.pop('original_governance')
            deferred.append('original_governance')
        for key in ('availability_record_pointers', 'availability_claim_kinds', 'context_admission'):
            if group.get(key) == []:
                group.pop(key)
                deferred.append(key)
        if deferred:
            group['undelivered_group_diagnostics_deferred'] = deferred
            group['original_group_content_delivered'] = False
            group['full_method_contract_verified'] = False
    task = result.get('task_admission')
    if (isinstance(task, dict) and not set(task) - _ADMISSION_ROWS['task_admission'][1]
            and isinstance(task.get('decisions'), list) and type(prior_positive_rows) is int
            and prior_positive_rows >= 0):
        originals = {atom.get('record_pointer'): atom for atom in result.get('decision', [])
                     if isinstance(atom, dict) and atom.get('kind') == 'NSF' and isinstance(atom.get('statement'), str)}
        retained = []
        for row in task['decisions']:
            support = row.get('support') if isinstance(row, dict) else None
            checked = copy.deepcopy(row)
            if isinstance(support, dict):
                checked['support']['relevance_relation_frames'] = []
            if (isinstance(support, dict) and row.get('admitted') is True and row.get('kind') == 'NSF'
                    and row.get('record_pointer') in originals
                    and support.get('relevance_relation_frames') == ['local_method_comparison']
                    and support.get('query_assertion_verified') is False
                    and support.get('whole_atom_delivery_allowed') is True
                    and all(support.get(key, False) is False for key in ('method_contract_verified',
                        'subject_mismatch', 'excluded_source_scope', 'scoped_cleanup'))
                    and support.get('whole_atom_excluded_relation_owners', []) == []
                    and support.get('relation_evidence_roles', []) == []
                    and _known_debug_row(checked, compact_support=True)):
                deferred_positive_rows += 1
            else:
                retained.append(row)
        task['decisions'] = retained
    def compact_positive_support(value):
        if isinstance(value, list):
            for child in value:
                compact_positive_support(child)
        elif isinstance(value, dict):
            for key, child in list(value.items()):
                if key in ('support', 'source_task_support') and isinstance(child, dict):
                    if (child.get('support_meaning') == 'TASK_RELEVANCE_ONLY'
                            and child.get('supported') is True
                            and child.get('query_assertion_verified') is False):
                        neutral = {'supported': True, 'support_meaning': 'TASK_RELEVANCE_ONLY',
                            'support_type': 'behavior', 'concrete_behavior': True,
                            'bounded_knowledge_consultation': False, 'display_consumer_relation': False,
                            'displayed_data_contract_verified': False, 'displayed_data_subjects': [],
                            'relevance_lane': 'ORIGINAL_CONTENT'}
                        for name, expected in neutral.items():
                            if name in child and type(child[name]) is type(expected) and child[name] == expected:
                                child.pop(name)
                        if (isinstance(child.get('requested_operation_subjects'), list)
                                and all(isinstance(name, str) for name in child['requested_operation_subjects'])):
                            child.pop('requested_operation_subjects')
                if key not in _OPAQUE:
                    compact_positive_support(child)
    # Active relationship names, query truth/contract limits, exclusion flags,
    # owner constraints and every unknown child remain on their original row.
    for channel in ('match_reason', 'task_admission', 'delivery_admission'):
        if channel in result:
            compact_positive_support(result[channel])
    # Original expansion remains available by this record's ID. Do not imply
    # that get_entry reconstructs the omitted query-dependent diagnostics.
    expansion = result.get('expansion')
    navigation = expansion.get('reviewer') if isinstance(expansion, dict) else None
    if (isinstance(expansion, dict) and not set(expansion) - {
            'reviewer', 'evidence_view', 'default_evidence_expanded'}
            and isinstance(navigation, dict) and set(navigation) == {'tool', 'arguments'}
            and navigation['tool'] == 'get_entry' and isinstance(navigation['arguments'], dict)
            and navigation['arguments'] == epoch_arguments({'id': result.get('id'), 'projection': 'reviewer', 'view': 'reviewer'})):
        result.pop('expansion')
    task = result.get('task_admission')
    if isinstance(task, dict) and not set(task) - _ADMISSION_ROWS['task_admission'][1]:
        if isinstance(task.get('method'), str):
            task.pop('method')
        if task.get('diagnostic_details_deferred') is True:
            task.pop('diagnostic_details_deferred')
        if type(task.get('decisions_deferred_count')) is int:
            task.pop('decisions_deferred_count')
    admission = result.get('delivery_admission', {})
    if isinstance(admission, dict):
        # Counts are removable only when their complete pointer lists agree.
        pairs = (('supported_original_atom_count', 'supported_record_pointers'),
                 ('supported_nonpolicy_atom_count', 'supported_nonpolicy_record_pointers'),
                 ('supported_policy_atom_count', 'supported_policy_record_pointers'))
        for count, pointers in pairs:
            if (isinstance(admission.get(pointers), list) and type(admission.get(count)) is int
                    and admission[count] == len(admission[pointers])):
                admission.pop(count, None)
        if (type(admission.get('total_supported_original_atom_count')) is int
                and admission['total_supported_original_atom_count'] == len(admission.get('supported_record_pointers', []))):
            admission.pop('total_supported_original_atom_count', None)
        if isinstance(admission.get('method'), str):
            admission.pop('method')
        if admission.get('supported_policy_record_pointers') == [] and admission.get('project_policy_requested') is False:
            if admission.get('policy_decisions') == []:
                admission.pop('policy_decisions')
            if admission.get('policy_support_meaning') == 'POLICY_RELEVANCE_ONLY':
                admission.pop('policy_support_meaning')
            admission.pop('supported_policy_record_pointers')
            if admission.get('supported_nonpolicy_record_pointers') == admission.get('supported_record_pointers'):
                admission.pop('supported_nonpolicy_record_pointers')
    context = result.get('record_context_delivery', {})
    if isinstance(context, dict):
        if type(context.get('admission_deferred_count')) is int:
            context.pop('admission_deferred_count')
        atomic = result.get('atomic_delivery', {})
        if atomic.get('delivered_seed_record_pointers') == context.get('seed_record_pointers'):
            context.pop('seed_record_pointers', None)
        if context.get('relation') == 'SAME_CANONICAL_RECORD':
            context.pop('relation')
    scope = result.get('source_scope', {})
    if isinstance(scope, dict):
        _defer_scope_navigation_proofs(scope, result)
        navigation = scope.get('full_record_scope_expansion')
        if (isinstance(navigation, dict) and not set(navigation) - {'tool', 'arguments',
                'alternative_view', 'returned_pointer', 'scope',
                'resolve_evidence_supports_arbitrary_scope_pointer'}
                and navigation.get('tool') == 'get_entry'
                and isinstance(navigation.get('arguments'), dict)
                and navigation['arguments'] == epoch_arguments({'id': result.get('id'), 'projection': 'reviewer', 'view': 'reviewer'})
                and navigation.get('scope') == 'FULL_ORIGINAL_RECORD_SCOPE_NOT_QUERY_FILTERED'
                and navigation.get('returned_pointer') == '/source_scope'
                and navigation.get('alternative_view') == 'evidence'
                and navigation.get('resolve_evidence_supports_arbitrary_scope_pointer') is False):
            scope.pop('full_record_scope_expansion')
        counts = scope.get('deferred_node_counts')
        if isinstance(counts, dict) and all(isinstance(key, str) and type(value) is int for key, value in counts.items()):
            scope.pop('deferred_node_counts')
        if type(scope.get('node_provenance_hash_fields_deferred_count')) is int:
            scope.pop('node_provenance_hash_fields_deferred_count')
        for key in ('identified_necessary_scope_dependencies_complete', 'delivered_node_values_complete'):
            if scope.get(key) is True:
                scope.pop(key)
        if type(scope.get('identified_selected_atom_scope_missing_count')) is int and scope['identified_selected_atom_scope_missing_count'] == 0:
            scope.pop('identified_selected_atom_scope_missing_count')
    atomic = result.get('atomic_delivery', {})
    if isinstance(atomic, dict) and isinstance(atomic.get('withheld_atoms'), list):
        # These are navigation rows for boundaries belonging solely to atoms
        # already deferred. No boundary statement or delivered owner's source
        # binding is removed, and unknown-context pointer rows remain explicit.
        rows = atomic['withheld_atoms']
        boundary = [row for row in rows if isinstance(row, dict)
            and set(row) == {'record_pointer', 'kind', 'relation'}
            and row['kind'] == 'BOUNDARY'
            and isinstance(row['record_pointer'], str)
            and re.fullmatch(r'/does_not_prove/[0-9]+', row['record_pointer'])
            and row['relation'] == 'ORIGINAL_SOURCE_BOUNDARY_OF_DEFERRED_ATOM']
        if boundary:
            atomic['withheld_atoms'] = [row for row in rows if row not in boundary]
            atomic['deferred_boundary_navigation_count'] = len(boundary)
    if result.get('consumption_hints') == []:
        hint = result.get('consumption_hint_metadata')
        if hint == {'source': 'PROJECTION_PROFILE', 'evidence_class': 'NON_CANONICAL_METADATA', 'task_or_method_proof': False}:
            result.pop('consumption_hint_metadata', None)
        result.pop('consumption_hints')
    companion = result.get('companion_context_budget')
    if (isinstance(companion, dict) and set(companion) == {'status', 'withheld_donors', 'reason',
            'withheld_context_delivered', 'entire_task_completion_proven', 'necessary_dependency_proven', 'followup'}
            and companion.get('status') == 'PARTIAL_BOUNDED_CONTEXT'
            and companion.get('reason') == 'COMPLETE_PRIMARY_CARD_AND_DONOR_EXCEED_PAYLOAD_BUDGET'
            and all(companion.get(key) is False for key in ('withheld_context_delivered',
                'entire_task_completion_proven', 'necessary_dependency_proven'))
            and isinstance(companion.get('withheld_donors'), list) and companion['withheld_donors']
            and companion.get('followup') == 'Expand the listed donor IDs before relying on unserved context; primary facts and their original Scope remain whole.'):
        companion.pop('followup')
    if result.get('project_policy_questions') == []:
        result.pop('project_policy_questions')
    # These are navigation aids derived from already delivered original text.
    symbols = result.get('exact_symbols')
    if isinstance(symbols, list) and all(isinstance(row, str) or
            (isinstance(row, dict) and not set(row) - {'symbol', 'receiver', 'role',
             'basis_record_pointers', 'context_record_pointers', 'basis_record_pointer', 'receiver_spelling'}
             and ('receiver_spelling' not in row or isinstance(row.get('symbol'), str)
                 and isinstance(row['receiver_spelling'], str)
                 and re.split(r'[.:]', row['symbol'])[0] == row['receiver_spelling'])) for row in symbols):
        result.pop('exact_symbols')
    relevant = result.get('when_relevant')
    if isinstance(relevant, list) and all(isinstance(row, str) for row in relevant):
        result.pop('when_relevant')
    omission = result.get('omission', {})
    if isinstance(omission, dict):
        omission.pop('exact_symbols', None)
        omission.pop('bundle_navigation_symbols_deferred', None)
        kinds = omission.get('typed_atoms_by_kind')
        if (isinstance(kinds, dict) and kinds and all(isinstance(key, str)
                and type(count) is int and count >= 0 for key, count in kinds.items())
                and type(omission.get('typed_atoms')) is int
                and omission['typed_atoms'] == sum(kinds.values())):
            # Preserve the total omitted-original count and the explicit
            # atomic withheld ledger; this is only its diagnostic breakdown.
            omission.pop('typed_atoms_by_kind')
    # The wire notice already describes omitted query diagnostics. Carry the
    # original-value invariant there once, rather than a second notice block.
    prior_bundle = result.get('bundle_diagnostic_projection')
    if (prior_bundle is None or prior_bundle == {'schema': 'dst-bundle-diagnostic-projection/1',
            'original_atoms_and_scope_values_preserved': True, 'query_diagnostics_recoverable': False}):
        result.pop('bundle_diagnostic_projection', None)
    strength = result.get('evidence_strength')
    if (isinstance(strength, dict) and isinstance(strength.get('claim_kinds'), dict)
            and all(isinstance(kind, str) and type(count) is int and count >= 0
                    for kind, count in strength['claim_kinds'].items())):
        # Original-record type totals are query diagnostics, not delivered
        # atom counts, evidence strength, runtime status or a knowledge gap.
        strength.pop('claim_kinds')
    facet = result.get('facet_admission')
    if (isinstance(facet, dict) and set(facet) == {'method', 'excluded_atom_count'}
            and type(facet['excluded_atom_count']) is int and facet['excluded_atom_count'] == 0):
        result.pop('facet_admission')
    if isinstance(result.get('title'), str):
        result.pop('title')
    if type(result.get('score')) in (int, float):
        result.pop('score')
    packed = project_l1_card(result)
    table = packed.get('shared_metadata')
    if (isinstance(table, dict) and table.get('schema') == 'dst-decision-metadata-sharing/2'
            and table.get('interpretation') == 'metadata_ref is one exact value; metadata_template contributes exactly its shared fields. Local fields cannot override different template values. Indices belong to this card only. Fact statements, Scope and governance stay inline.'):
        # The schema/reference-space and strict decoder define this invariant;
        # the repeated human-readable explanation is optional display metadata.
        table.pop('interpretation')
    # The encoder may create fresh omission counters while rebuilding local
    # references. They describe deferred diagnostics, never a source condition.
    # Remove only those named counters after the last encoding pass as well.
    facet = packed.get('facet_admission')
    if (isinstance(facet, dict) and set(facet) == {'method', 'excluded_atom_count'}
            and type(facet['excluded_atom_count']) is int and facet['excluded_atom_count'] == 0):
        packed.pop('facet_admission')
    task = packed.get('task_admission')
    if (isinstance(task, dict) and not set(task) - _ADMISSION_ROWS['task_admission'][1]
            and type(task.get('decisions_deferred_count')) is int):
        task.pop('decisions_deferred_count')
    scope = packed.get('source_scope')
    if isinstance(scope, dict) and type(scope.get('node_provenance_hash_fields_deferred_count')) is int:
        scope.pop('node_provenance_hash_fields_deferred_count')
    wire = packed.setdefault('wire_projection', {'schema': SCHEMA, 'profile': PROFILE})
    wire.update(unknown_wire)
    if deferred_query_navigation or prior_navigation_count:
        counters = wire.setdefault('omitted_diagnostic_or_provenance_fields', {})
        if type(prior_navigation_count) is int and prior_navigation_count >= 0:
            counters['query_source_symbol_navigation'] = prior_navigation_count + deferred_query_navigation
        else:
            counters['query_source_symbol_navigation'] = copy.deepcopy(prior_navigation_count)
    if deferred_positive_rows or prior_positive_rows:
        counters = wire.setdefault('omitted_diagnostic_or_provenance_fields', {})
        counters['positive_query_admission_rows'] = (deferred_positive_rows + prior_positive_rows
            if type(prior_positive_rows) is int and prior_positive_rows >= 0 else copy.deepcopy(prior_positive_rows))
    wire['original_atoms_and_scope_values_preserved'] = True
    wire['query_diagnostics_recoverable_from_record_expansion'] = False
    counts = wire.get('omitted_diagnostic_or_provenance_fields')
    if isinstance(counts, dict):
        named_counts = {'empty_admission_diagnostics', 'query_matching_detail',
            'source_scope.nodes.repeated_verified_hashes', 'task_admission.decisions',
            'facet_admission.decisions', 'record_context_delivery.admission',
            'query_selection', 'bundle_packaging.repeated_wire_notice',
            'query_parser_units', 'relation_parser_spans',
            'repeated_source_provenance_locators', 'repeated_typed_source_provenance_locators',
            'repeated_full_record_scope_provenance'}
        counts = {key: count for key, count in counts.items()
                  if key not in named_counts or type(count) is not int or count < 0}
        if counts:
            wire['omitted_diagnostic_or_provenance_fields'] = counts
        else:
            wire.pop('omitted_diagnostic_or_provenance_fields')
    return _share_repeated_statements(packed)


def project_l1_card(card, *, public_contract=False):
    """Return an Agent L1 card; call only after validation on the rich card.

    Non-L1 values are copied without alteration. Each companion owns an
    independent projection and metadata table. This is deliberately not an
    inverse serialization: query diagnostics are explicitly omitted, while
    original record/evidence expansion remains a separate, existing workflow.
    """
    if not isinstance(card, dict):
        return copy.deepcopy(card)
    if card.get('level') != 1 or not isinstance(card.get('projection_schema'), str):
        return copy.deepcopy(card)
    prior = card.get('wire_projection')
    if prior is not None and (not isinstance(prior, dict) or prior.get('schema') != SCHEMA):
        return copy.deepcopy(card)
    profile = PUBLIC_PROFILE if public_contract else PROFILE
    if isinstance(prior, dict) and (prior.get('profile') == profile
            or not public_contract and prior.get('profile') == BUNDLE_PROFILE):
        return copy.deepcopy(card)
    if public_contract and isinstance(prior, dict):
        raise ValueError('Public L1 contracts require the original rich card, not a compact wire projection')
    result = expand_l1_metadata(card)
    omitted = Counter()
    if isinstance(prior, dict):
        counts = prior.get('omitted_diagnostic_or_provenance_fields')
        if isinstance(counts, dict) and all(isinstance(key, str) and type(count) is int
                                            and count >= 0 for key, count in counts.items()):
            omitted.update(counts)

    def defer(name, count=1):
        omitted[name] += count

    def compact(value, channel='', in_support=False):
        if isinstance(value, list):
            return [compact(child, channel, in_support) for child in value]
        if not isinstance(value, dict):
            return copy.deepcopy(value)
        row = {}
        for key, child in value.items():
            if key == 'original_scope' and isinstance(child, dict) and (
                    isinstance(result.get('source_scope'), dict)
                    and result['source_scope'].get('scope_value_sha256') == _digest(child)
                    and value.get('record_sha256') == result.get('record_sha256')
                    and isinstance(result.get('expansion', {}).get('reviewer'), dict)):
                # 完整原 Scope 有真实 L2 入口；它不是当前 selected-nodes 的伪副本。
                row['original_scope_ref'] = {
                    'original_record_pointer': '/scope',
                    'record_sha256': result['record_sha256'],
                    'scope_value_sha256': _digest(child),
                    'record_scope_expansion': copy.deepcopy(result['expansion']['reviewer']),
                    'full_original_scope_at_card_pointer': False,
                }
                defer('repeated_full_record_scope_provenance')
            elif key in _OPAQUE:
                row[key] = copy.deepcopy(child)
            elif (in_support and key in _SUPPORT_DIAGNOSTICS) or (
                    channel == 'match_reason' and (key in _MATCH_DIAGNOSTICS or
                    not public_contract and key in _PUBLIC_MATCH_POINTERS)):
                if not (not public_contract and channel == 'match_reason'
                        and key in _PUBLIC_MATCH_POINTERS and isinstance(child, list) and not child):
                    defer('query_matching_detail')
            elif key in ('source_unit', 'task_unit', 'original_units_sha256',
                         'original_units_delivered_by_diagnostics'):
                defer('query_parser_units')
            elif (key == 'call_relations' and isinstance(child, list) and child
                  and all(isinstance(item, dict) and set(item) <= {
                      'relation_polarity', 'symbol_span', 'predicate_span'}
                      and 'relation_polarity' in item for item in child)):
                row[key] = _unique([{name: copy.deepcopy(item[name]) for name in item
                                    if name not in ('symbol_span', 'predicate_span')}
                                   for item in child])
                defer('relation_parser_spans', sum('symbol_span' in item for item in child)
                      + sum('predicate_span' in item for item in child))
            elif (key == 'basis_evidence_references' and isinstance(child, list)
                  and child and all(_ref(item) for item in child)):
                # 原 evidence 的 hash/pointer 可从当前记录的 L3 manifest 选择；
                # 这里省略证明定位，不替换成不能 resolve 的伪 reference。
                defer('repeated_source_provenance_locators', len(child))
                row['basis_evidence_references_deferred'] = True
            elif (key == 'typed_context_reference_proofs' and isinstance(child, list)
                  and child and all(_proof(item, result) for item in child)):
                covered = all(item['record_pointer'] == value.get('record_pointer')
                              and item['claim_kind'] == value.get('kind')
                              and item['symbol'] in value.get('relation_symbols', [])
                              for item in child)
                if covered:
                    row['typed_context_reference_proof_limits'] = _unique([
                        {name: copy.deepcopy(item[name]) for name in
                         ('schema', 'original_reference_integrity_verified',
                          'identity_is_native_declaration_proof')}
                        for item in child])
                else:
                    # 未由外层关系完整覆盖的身份仍逐个保留。
                    row[key] = _unique([{name: copy.deepcopy(item[name]) for name in item
                                        if name not in _REF_KEYS} for item in child])
                row['typed_context_source_locators_deferred'] = True
                defer('repeated_typed_source_provenance_locators', len(child))
            else:
                row[key] = compact(child, channel, in_support or key in ('support', 'source_task_support'))
                if key in _RELATION_LISTS and isinstance(row[key], list):
                    row[key] = _unique(row[key])
        return row

    for name in _CHANNELS:
        if name in result:
            result[name] = compact(result[name], name)
    for name in ATOM_GROUPS:
        # 事实本体和附加未知字段不被重新解释；仅准入之后的合同元数据可投影。
        for atom in result.get(name, []):
            if isinstance(atom, dict) and 'contract_bindings' in atom:
                bindings = compact(atom['contract_bindings'], 'contract_bindings')
                atom['contract_bindings'] = bindings if public_contract else _group_bindings(bindings)
    if 'query_selection' in result:
        result.pop('query_selection')
        defer('query_selection')
    if 'companion_context' in result:
        result['companion_context'] = [project_l1_card(child, public_contract=public_contract)
                                       for child in result['companion_context']]
    _defer_admission_rows(result, defer, compact_empty=not public_contract)
    if not public_contract:
        _defer_scope_node_hashes(result, defer)
    _merge_bundle_notice(result, defer)
    if omitted:
        result['wire_projection'] = {
            **({key: copy.deepcopy(child) for key, child in prior.items()
                if key not in _WIRE_KEYS} if isinstance(prior, dict) else {}),
            'schema': SCHEMA,
            'profile': profile,
            'omitted_diagnostic_or_provenance_fields': dict(sorted(omitted.items())),
            'query_diagnostics_recoverable_from_record_expansion': False,
        }
    packed = share_metadata(result, preserve_contracts=public_contract)

    def reduce_refs(value):
        if isinstance(value, list):
            return [reduce_refs(child) for child in value]
        if not isinstance(value, dict):
            return value
        if 'metadata_ref' in value:
            # 原 share_metadata 表已保存全部字段；这个引用只使用本卡的实际表。
            return {'metadata_ref': value['metadata_ref']}
        return {key: (child if key in _OPAQUE else reduce_refs(child))
                for key, child in value.items()}

    for name in _CHANNELS:
        if name in packed:
            packed[name] = reduce_refs(packed[name])
    for name in ATOM_GROUPS:
        for atom in packed.get(name, []):
            if not public_contract and isinstance(atom, dict) and 'contract_bindings' in atom:
                atom['contract_bindings'] = reduce_refs(atom['contract_bindings'])
    return packed


def project_l1_payload(payload):
    """Project L1 cards in an output payload, leaving envelopes/L2/L3 intact."""
    if isinstance(payload, list):
        return [project_l1_payload(child) for child in payload]
    if not isinstance(payload, dict):
        return copy.deepcopy(payload)
    if payload.get('level') == 1 and isinstance(payload.get('projection_schema'), str):
        return project_l1_card(payload)
    return {key: project_l1_payload(child) for key, child in payload.items()}

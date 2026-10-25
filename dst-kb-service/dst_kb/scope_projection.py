"""Whole original semantic Scope nodes, with record navigation deferred to L2/L3.

This module opens no files and does not infer a method contract from a locator.
"""
import copy
import json
import re
from hashlib import sha256

from .facet_contracts import facet_admission, query_scope
from .intent_scope import task_support
from .scope_navigation import proved_navigation
from .original_supplement_context import verified_scope_supplements
from .source_epoch_runtime import epoch_arguments

SCHEMA = 'dst-semantic-scope/2.13'
_REF_KEYS = frozenset(('artifact_path', 'sha256', 'pointer'))
_LOCATOR_KEYS = frozenset(('snapshot_id', 'repository', 'commit', 'source_path',
    'symbol', 'line_start', 'line_end', 'file_sha256', 'range_sha256', 'url',
    'citation_ref', 'source_bytes_shipped', 'source_validation'))
_DISPOSITION_KEYS = frozenset(('batch', 'fact_id', 'kinds', 'disposition', 'fact_ref'))
_FACET_KEYS = frozenset(('id', 'facet_ref', 'overlay_ref'))
_IDENTITY_KEYS = frozenset(('source_commit', 'snapshot_id', 'source_repository',
    'dot_source_commit', 'dot_snapshot_id', 'dot_game_build', 'main_targeted_snapshot_id',
    'batch', 'fact_id', 'kinds', 'disposition', 'candidate_id', 'chain_id', 'role',
    'selected_questions', 'original_fact_ids', 'related_entry_ids', 'reviewer_profiles',
    'reclassified_from_track', 'supporting_fact_ids', 'reviewer_fact_ids', 'reuse_ids',
    'question_ids', 'latest_complete_input_hash_verified',
    'projection_preserved_exact_as_json_value', 'reclassification_is_governance_only',
    'new_canonical_record_count', 'baseline_modified', 'native_cloud_filesystem_only',
    'user_computer_used', 'cloud_task_created', 'remote_used', 'harness_used',
    'raw_Lua_in_deliverable', 'private_source_cache_is_not_deliverable'))
_CONTEXT_CONTAINERS = frozenset(('original_projection', 'original_predecessor_projections',
    'original_fact_statements', 'selected_interaction_chain', 'complementary_state_consumer_chain',
    'original_source_contract', 'source_scopes', 'facet_bindings', 'typed_fact_dispositions',
    'sample_support', 'source_locators'))
_POINTER_KEYS = frozenset(('record_pointer', 'record_pointers', 'basis_record_pointer',
    'basis_record_pointers', 'availability_record_pointers', 'context_record_pointers'))
_ID_KEYS = frozenset(('fact_id', 'basis_atom_ids', 'basis_fact_ids', 'supporting_fact_ids'))


def value_digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                            separators=(',', ':')).encode('utf-8')).hexdigest()


def _token(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def _ref_key(value):
    if isinstance(value, dict) and _REF_KEYS <= value.keys():
        return tuple(value[key] for key in ('artifact_path', 'sha256', 'pointer'))
    return None


def _identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:#/-]+', value) is not None


def _pure_identity(key, value):
    if key not in _IDENTITY_KEYS:
        return False
    if isinstance(value, list):
        return all(_identifier(item) for item in value)
    return _identifier(value) or type(value) in (bool, int) or value is None


def _question_navigation(key, value):
    return (key in ('load_when', 'original_question', 'engineering_question', 'selected_engineering_question')
            and isinstance(value, str) and bool(re.search(r'[?？]\s*$|^(?:如何|怎样|怎么|是否|为何|何时|'
                r'how\b|what\b|which\b|why\b)', value.strip(), re.I)))


def _pure_navigation(value):
    if isinstance(value, list):
        return bool(value) and all(_pure_navigation(child) for child in value)
    if not isinstance(value, dict):
        return False
    keys = set(value)
    # A closed research-question inventory describes what the source author
    # investigated. Its impact/rationale is not an object condition or an atom.
    # Unknown children invalidate this classification and stay semantic Scope.
    if keys == {'questions_count', 'questions', 'stop_rule', 'genuine_static_gap_remaining'}:
        questions = value.get('questions')
        required = {'id', 'engineering_question', 'implementation_impact',
                    'reviewer_fact_ids', 'status', 'stopping_condition_met'}
        if (type(value.get('questions_count')) is int and isinstance(questions, list)
                and value['questions_count'] == len(questions) and bool(questions)
                and all(isinstance(value.get(key), str) and value[key]
                        for key in ('stop_rule', 'genuine_static_gap_remaining'))
                and all(isinstance(question, dict) and set(question) == required
                    and _identifier(question.get('id'))
                    and all(isinstance(question.get(key), str) and question[key]
                        for key in ('engineering_question', 'implementation_impact', 'status', 'stopping_condition_met'))
                    and _question_navigation('engineering_question', question['engineering_question'])
                    and isinstance(question.get('reviewer_fact_ids'), list)
                    and all(_identifier(identity) for identity in question['reviewer_fact_ids'])
                    for question in questions)):
            return True
    if _ref_key(value) and keys <= _REF_KEYS:
        return (isinstance(value['artifact_path'], str) and isinstance(value['pointer'], str)
                and value['pointer'].startswith('/') and isinstance(value['sha256'], str)
                and re.fullmatch(r'[a-fA-F0-9]{64}', value['sha256']) is not None)
    if {'source_path', 'symbol'} <= keys and keys <= _LOCATOR_KEYS:
        return all(_pure_navigation(child) for key, child in value.items() if key == 'citation_ref')
    if {'fact_id', 'fact_ref'} <= keys and keys <= _DISPOSITION_KEYS:
        return (_pure_navigation(value['fact_ref']) and _identifier(value['fact_id'])
                and all(_identifier(item) for item in value.get('kinds', []))
                and _identifier(value.get('disposition', 'canonical_typed_claim')))
    if 'id' in keys and keys <= _FACET_KEYS and keys & {'facet_ref', 'overlay_ref'}:
        return all(_pure_navigation(child) for key, child in value.items() if key != 'id')
    return False


def _original_atoms(record):
    result = {f'/claims/{index}': claim for index, claim in enumerate(record.get('claims', []))}
    boundaries = record.get('does_not_prove', [])
    if isinstance(boundaries, list):
        result.update({f'/does_not_prove/{index}': {'kind': 'BOUNDARY', 'statement': value}
                       for index, value in enumerate(boundaries)})
    elif boundaries:
        result['/does_not_prove'] = {'kind': 'BOUNDARY', 'statement': boundaries}
    return result


def _dependency_indexes(record, originals):
    references, statements, ids = {}, {}, {}
    for pointer, atom in originals.items():
        statements.setdefault(value_digest(atom.get('statement')), set()).add(pointer)
        if atom.get('id'):
            ids.setdefault(atom['id'], set()).add(pointer)
        for ref in atom.get('evidence_refs', []):
            key = _ref_key(ref)
            if key:
                references.setdefault(key, set()).add(pointer)
    scope = record.get('scope', {})
    for disposition in scope.get('typed_fact_dispositions', []) if isinstance(scope, dict) else []:
        if isinstance(disposition, dict):
            pointers = references.get(_ref_key(disposition.get('fact_ref')), set())
            if pointers and disposition.get('fact_id'):
                ids.setdefault(disposition['fact_id'], set()).update(pointers)
    return references, statements, ids


def _explicit_dependencies(value, references, ids):
    pointers, unknown = set(), set()
    if not isinstance(value, dict):
        return pointers, unknown
    for key, child in value.items():
        values = child if isinstance(child, list) else [child]
        if key in _POINTER_KEYS:
            pointers.update(pointer for pointer in values if isinstance(pointer, str))
        elif key in _ID_KEYS:
            for identity in values:
                if isinstance(identity, str):
                    pointers.update(ids.get(identity, set()))
                    if identity not in ids:
                        unknown.add(identity)
        elif key in ('fact_ref', 'evidence_refs'):
            for ref in values:
                pointers.update(references.get(_ref_key(ref), set()))
    return pointers, unknown


def _negative_conflict(query, value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    scope = query_scope(query)
    if not scope['negative_clauses']:
        return False
    support = task_support(query, text, {'scope': text, 'receivers': []})
    if support.get('excluded_source_scope'):
        return True
    # An explicitly excluded named API also gates a Scope-only condition.
    for clause in scope['negative_clauses']:
        for symbol in re.findall(r'[A-Za-z_][A-Za-z0-9_]*(?:[:.][A-Za-z_][A-Za-z0-9_]*)+', clause):
            if re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', text, re.I):
                return True
    return False


def semantic_scope(record, family, delivered_groups, query='', excluded_pointers=(), navigation_context=None, supplement_context=None):
    """Select Scope context using original pointer dependencies, never a byte cap.

    Independent historical projections and unattributed sample structures require
    reviewer expansion. Unknown dependencies are reported rather than guessed.
    """
    original_scope = record.get('scope', {})
    if family != 'core' or not isinstance(original_scope, dict):
        return copy.deepcopy(original_scope)
    digest = value_digest(record)
    originals = _original_atoms(record)
    references, statements, ids = _dependency_indexes(record, originals)
    delivered, text_refs = set(), {}
    for field, atoms in delivered_groups.items():
        for index, atom in enumerate(atoms):
            if atom.get('record_pointer') in originals:
                delivered.add(atom['record_pointer'])
                text_refs.setdefault(value_digest(atom['statement']), f'/{field}/{index}/statement')
    excluded = set(excluded_pointers)
    scoped_supplements = verified_scope_supplements(record, family, delivered_groups, query, supplement_context)
    excluded -= scoped_supplements
    supplement_values = {value_digest(originals[pointer]['statement']) for pointer in scoped_supplements}
    nodes, missing, deferred, navigation_proofs = {}, [], [], []

    def defer(pointer, reason, needed=False, basis=()):
        deferred.append((pointer, reason))
        if needed:
            item = {'original_record_pointer': pointer, 'reason': reason}
            if basis:
                item['basis_record_pointers'] = sorted(basis)
            associated = bool(set(basis) & delivered)
            item['scope_relation_status'] = ('DECLARED_SELECTED_ATOM_SCOPE_DEPENDENCY' if associated else
                                             'UNATTRIBUTED_POTENTIAL_RECORD_SCOPE_DEPENDENCY')
            item['current_atom_scope_association_identified'] = associated
            item['current_atom_necessity_verified'] = False
            missing.append(item)

    def basis_admitted(pointers):
        atoms = [{**originals[p], 'record_pointer': p} for p in pointers if p in originals]
        admitted, _ = facet_admission(record, family, atoms, query)
        return {atom['record_pointer'] for atom in atoms} <= {atom['record_pointer'] for atom in admitted} | scoped_supplements

    def groupable(value, inherited_basis):
        # A complete original semantic subtree needs one provenance envelope.
        # Every leaf is still checked; grouping cannot hide another sample or
        # an excluded dependency behind an admitted parent dictionary.
        if _pure_navigation(value):
            return False
        local, unknown = _explicit_dependencies(value, references, ids)
        required = set(inherited_basis) | local | statements.get(value_digest(value), set())
        if unknown or required & excluded or not required <= delivered or not basis_admitted(required):
            return False
        if isinstance(value, dict):
            if any(key in _CONTEXT_CONTAINERS for key in value):
                return False
            return all(groupable(child, required) for child in value.values())
        if isinstance(value, list):
            return all(groupable(child, required) for child in value)
        atom = {'kind': 'SCOPE_CONTEXT', 'statement': value}
        admitted, _ = facet_admission(record, family, [atom], query)
        return (bool(admitted) or value_digest(value) in supplement_values) and not _negative_conflict(query, value)

    def subtree_basis(value):
        local, _ = _explicit_dependencies(value, references, ids)
        result = local | statements.get(value_digest(value), set())
        if isinstance(value, dict):
            for child in value.values():
                result |= subtree_basis(child)
        elif isinstance(value, list):
            for child in value:
                result |= subtree_basis(child)
        return result

    def visit(value, pointer, key='', contextual=False, basis=frozenset(), unknown=frozenset()):
        proof = proved_navigation(navigation_context, record, pointer, value)
        if proof is not None:
            navigation_proofs.append(proof)
            defer(pointer, 'SOURCE_METADATA_NAVIGATION_DEFERRED')
            return
        if (_pure_navigation(value) or _pure_identity(key, value) or _question_navigation(key, value)
                or key in _POINTER_KEYS):
            defer(pointer, 'RECORD_NAVIGATION_DEFERRED')
            return
        local, unresolved = _explicit_dependencies(value, references, ids)
        basis = set(basis) | local
        unknown = set(unknown) | unresolved
        exact = statements.get(value_digest(value), set())
        if exact:
            basis |= exact
        contextual = contextual or key in _CONTEXT_CONTAINERS
        if basis and (basis & excluded or not basis <= delivered):
            defer(pointer, 'SCOPE_BASIS_EXCLUDED' if basis & excluded else 'SCOPE_BASIS_NOT_DELIVERED',
                  bool(basis & delivered), basis)
            return
        if basis:
            if not basis_admitted(basis):
                defer(pointer, 'SCOPE_BASIS_SAMPLE_EXCLUDED', True, basis)
                return
        if unknown:
            defer(pointer, 'UNRESOLVED_ORIGINAL_SCOPE_DEPENDENCY', True, basis)
            return
        if isinstance(value, (dict, list)) and value and (contextual or not groupable(value, basis)):
            if isinstance(value, dict):
                for child_key, child in value.items():
                    visit(child, pointer + '/' + _token(child_key), child_key, contextual, basis, unknown)
            else:
                for index, child in enumerate(value):
                    visit(child, pointer + '/' + str(index), '', contextual, basis, unknown)
            return
        if contextual and not basis:
            defer(pointer, 'UNRESOLVED_ORIGINAL_SCOPE_DEPENDENCY', True)
            return
        if isinstance(value, (dict, list)):
            basis |= subtree_basis(value)
        atom = {'kind': 'SCOPE_CONTEXT', 'statement': value, 'record_pointer': pointer}
        admitted, admission = facet_admission(record, family, [atom], query)
        if not admitted and value_digest(value) in supplement_values:
            admitted = [atom]
            admission.append({'record_pointer': pointer, 'admitted': True,
                              'reason': 'EXACT_DELIVERED_ORIGINAL_SUPPLEMENT_SCOPE_VALUE',
                              'not_a_generic_contract': True})
        if not admitted or _negative_conflict(query, value):
            defer(pointer, 'SCOPE_SAMPLE_OR_EXPLICIT_INTENT_EXCLUDED', bool(basis), basis)
            return
        node = {'original_record_pointer': pointer, 'record_sha256': digest,
                'scope_value_sha256': value_digest(value),
                'role': 'ORIGINAL_ATOM_SCOPE_CONTEXT' if basis else 'RECORD_SCOPE_CONSTRAINT'}
        if basis:
            node['basis_record_pointers'] = sorted(basis)
        if admission:
            node['facet_admission'] = admission
        if value_digest(value) in text_refs:
            node['value_ref'] = {'card_pointer': text_refs[value_digest(value)],
                                 'reference_space': 'SINGLE_DECISION_CARD_JSON_POINTER'}
        else:
            node['value'] = copy.deepcopy(value)
        nodes['scope-' + str(len(nodes)).zfill(4)] = node

    for key, value in original_scope.items():
        visit(value, '/scope/' + _token(key), key)
    # Missing nodes are grouped by their original containing subtree, with all
    # original values still available through reviewer/evidence get_entry.
    grouped_missing = {}
    for item in missing:
        tokens = item['original_record_pointer'].split('/')
        parent = '/'.join(tokens[:3])
        group = grouped_missing.setdefault(parent, {'original_record_pointer': parent,
            'reasons': set(), 'basis_record_pointers': set(), 'scope_relation_statuses': set(),
            'current_atom_necessity_verified': False, 'deferred_node_count': 0})
        group['reasons'].add(item['reason'])
        group['scope_relation_statuses'].add(item['scope_relation_status'])
        group['basis_record_pointers'].update(item.get('basis_record_pointers', []))
        group['deferred_node_count'] += 1
    unresolved = [{**group, 'reasons': sorted(group['reasons']),
                   'basis_record_pointers': sorted(group['basis_record_pointers']),
                   'scope_relation_statuses': sorted(group['scope_relation_statuses']),
                   'current_atom_scope_association_identified': 'DECLARED_SELECTED_ATOM_SCOPE_DEPENDENCY' in group['scope_relation_statuses']}
                  for group in grouped_missing.values()]
    identified_count = sum('DECLARED_SELECTED_ATOM_SCOPE_DEPENDENCY' in item['scope_relation_statuses'] for item in unresolved)
    unattributed_count = sum('UNATTRIBUTED_POTENTIAL_RECORD_SCOPE_DEPENDENCY' in item['scope_relation_statuses'] for item in unresolved)
    counts = {}
    for _, reason in deferred:
        counts[reason] = counts.get(reason, 0) + 1
    result = {'scope_schema': SCHEMA, 'delivery': 'SELECTED_ORIGINAL_SEMANTIC_NODES',
            'original_record_pointer': '/scope', 'record_sha256': digest,
            'scope_value_sha256': value_digest(original_scope), 'nodes': nodes,
            'closure': 'SELECTED_ATOM_SCOPE_DEPENDENCY_REQUIRES_EXPANSION' if identified_count else
                       'UNATTRIBUTED_RECORD_SCOPE_REQUIRES_EXPANSION' if unattributed_count else 'DELIVERED_NODES_ONLY',
            'delivered_node_values_complete': True,
            'identified_necessary_scope_dependencies_complete': not bool(identified_count),
            'scope_dependency_resolution_complete': not unresolved,
            'identified_selected_atom_scope_missing_count': identified_count,
            'unattributed_potential_record_scope_missing_count': unattributed_count,
            'necessary_scope_complete': False,
            'necessary_scope_completeness_basis': 'RECORD_SCOPE_DEPENDENCY_ENUMERATION_NOT_PROVEN',
            'unidentified_scope_dependencies': 'UNKNOWN', 'needed_scope_missing': unresolved,
            'deferred_node_counts': counts, 'full_record_scope_delivered': False,
            'full_record_scope_expansion': {'tool': 'get_entry',
                'arguments': epoch_arguments({'id': record['id'], 'projection': 'reviewer', 'view': 'reviewer'}),
                'alternative_view': 'evidence', 'returned_pointer': '/source_scope',
                'scope': 'FULL_ORIGINAL_RECORD_SCOPE_NOT_QUERY_FILTERED',
                'resolve_evidence_supports_arbitrary_scope_pointer': False}}
    if navigation_proofs:
        result['source_metadata_navigation_proofs'] = navigation_proofs
    return result


def scope_dependency_plan(record, family, delivered_groups, query='', excluded_pointers=(),
                          navigation_context=None, supplement_context=None):
    """Return original Scope associations for whole-atom budget closure.

    A shared semantic node cannot survive with only part of its original basis.
    Unattributed or unresolved constraints remain unknown, never optional. This
    API does not establish that the record enumerates every necessary condition.
    """
    scope = semantic_scope(record, family, delivered_groups, query, excluded_pointers,
                           navigation_context=navigation_context,
                           supplement_context=supplement_context)
    edges = []
    if isinstance(scope, dict) and scope.get('scope_schema') == SCHEMA:
        for node in scope.get('nodes', {}).values():
            basis = node.get('basis_record_pointers', [])
            for dependent in basis:
                for required in basis:
                    if dependent != required:
                        edges.append({'dependent_record_pointer': dependent,
                                      'required_record_pointer': required,
                                      'scope_record_pointer': node['original_record_pointer'],
                                      'basis': 'SHARED_ORIGINAL_SEMANTIC_SCOPE_NODE'})
        unresolved = copy.deepcopy(scope.get('needed_scope_missing', []))
    else:
        unresolved = []
    return {'schema': 'dst-atomic-scope-dependencies/1', 'scope': scope,
            'edges': edges, 'unresolved': unresolved,
            'unattributed_constraints_are_optional': False,
            'record_dependency_enumeration_proven': False}


def scope_reference(original_scope, record_sha256, delivered_scope=None):
    result = {'original_record_pointer': '/scope', 'record_sha256': record_sha256,
              'scope_value_sha256': value_digest(original_scope),
              'record_scope_expansion': 'get_entry(view=reviewer|evidence)'}
    is_projection = isinstance(delivered_scope, dict) and delivered_scope.get('scope_schema') == SCHEMA
    delivered_digest = (delivered_scope.get('scope_value_sha256') if is_projection
                        else value_digest(delivered_scope)) if delivered_scope is not None else None
    matches = delivered_digest == result['scope_value_sha256']
    result['canonical_scope_identity_verified'] = matches
    if delivered_scope is not None and matches:
        result['card_pointer'] = '/source_scope'
        result['reference_space'] = 'SINGLE_DECISION_CARD_JSON_POINTER'
        result['full_original_scope_at_card_pointer'] = not is_projection
        if not result['full_original_scope_at_card_pointer']:
            result['shared_scope_is_selected_semantic_nodes'] = True
    elif delivered_scope is not None:
        result.pop('original_record_pointer')
        result['canonical_scope_identity_verified'] = False
        result['record_scope_expansion'] = 'MAPPING_SCOPE_DIFFERS_FROM_CANONICAL_SCOPE'
    return result


def shared_scope_references(value, delivered_scope=None, record_sha256=None):
    """Replace every duplicated mapping/context Scope with explicit provenance."""
    if isinstance(value, list):
        return [shared_scope_references(child, delivered_scope, record_sha256) for child in value]
    if not isinstance(value, dict):
        return copy.deepcopy(value)
    digest = value.get('record_sha256', record_sha256) or (delivered_scope.get('record_sha256')
             if isinstance(delivered_scope, dict) else None)
    result = {key: shared_scope_references(child, delivered_scope, digest)
              for key, child in value.items() if key != 'original_scope'}
    if 'original_scope' in value:
        result['original_scope_ref'] = scope_reference(value['original_scope'],
            digest, delivered_scope)
    return result


def compact_diagnostics(value):
    """L1 keeps decisions and anchors; original units are not a fact side channel."""
    if isinstance(value, list):
        return [compact_diagnostics(child) for child in value]
    if not isinstance(value, dict):
        return copy.deepcopy(value)
    result = {key: compact_diagnostics(child) for key, child in value.items()
              if key not in ('source_unit', 'task_unit')}
    if 'source_unit' in value or 'task_unit' in value:
        result['original_units_delivered_by_diagnostics'] = False
        result['original_units_sha256'] = {key: value_digest(value[key])
            for key in ('source_unit', 'task_unit') if key in value}
    return result


_TASK_SUPPORT_DETAIL_KEYS = frozenset((
    'mechanism_hits', 'subject_hits', 'source_subjects', 'local_source_subjects',
    'inherited_source_subjects', 'inherited_source_symbols', 'requested_subjects',
    'matched_symbols', 'operation_hits', 'requested_operations', 'lexical_hits',
    'anchors', 'bounded_source_paths', 'bounded_query_paths',
    'verified_method_head_symbols', 'supported_task_units',
    'original_units_sha256', 'original_units_delivered_by_diagnostics',
))


def compact_task_diagnostics(values):
    """Keep pointer outcomes and constraints, merging only complementary rows.

    Ranking hits and original text units are diagnostic detail. Unknown fields,
    relation owners, polarity, query uncertainty and exclusions are retained.
    Different values are never resolved by taking the last observed outcome.
    """
    def prepare(value, in_support=False):
        if isinstance(value, list):
            return [prepare(child, in_support) for child in value]
        if not isinstance(value, dict):
            return copy.deepcopy(value)
        result = {}
        for key, child in value.items():
            if key in ('source_unit', 'task_unit') or (in_support and key in _TASK_SUPPORT_DETAIL_KEYS):
                continue
            if key in ('basis_admission', 'policy_decisions') and isinstance(child, list):
                result[key] = compact_task_diagnostics(child)
            else:
                result[key] = prepare(child, in_support or key == 'support')
        return result

    conflict = object()

    def merge(first, second):
        if value_digest(first) == value_digest(second):
            return copy.deepcopy(first)
        if not isinstance(first, dict) or not isinstance(second, dict):
            return conflict
        combined = copy.deepcopy(first)
        for key, child in second.items():
            if key not in combined:
                combined[key] = copy.deepcopy(child)
            else:
                child_result = merge(combined[key], child)
                if child_result is conflict:
                    return conflict
                combined[key] = child_result
        return combined

    rows = []
    for value in values:
        if isinstance(value, dict) and isinstance(value.get('other_distinct_results'), list):
            rows.extend(value['other_distinct_results'])
            value = {key: child for key, child in value.items() if key != 'other_distinct_results'}
        rows.append(value)
    grouped, order = {}, []
    for value in rows:
        item = prepare(value)
        pointer = item.get('record_pointer') if isinstance(item, dict) else None
        key = ('pointer', pointer) if pointer is not None else ('value', value_digest(item))
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        alternatives = grouped[key]
        for index, previous in enumerate(alternatives):
            combined = merge(previous, item)
            if combined is not conflict:
                alternatives[index] = combined
                break
        else:
            alternatives.append(item)
    result = []
    for key in order:
        alternatives = grouped[key]
        item = copy.deepcopy(alternatives[-1])
        if len(alternatives) > 1 and isinstance(item, dict):
            item['other_distinct_results'] = copy.deepcopy(alternatives[:-1])
        result.append(item)
    return result


def scope_navigation(values, record, family, query):
    """Keep whole navigation values while applying sample/explicit exclusions."""
    if not query.strip():
        return copy.deepcopy(values)
    result = []
    for value in values:
        atom = {'kind': 'NAVIGATION', 'statement': value}
        admitted, _ = facet_admission(record, family, [atom], query)
        if admitted and not _negative_conflict(query, value):
            result.append(copy.deepcopy(value))
    return result

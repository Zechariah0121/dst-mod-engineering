"""Fixed-Source input route stages, independent of method and result contracts."""
import copy
import re

from .relevance_frames import input_route_stage_request, input_route_stage_witness
from .scope_navigation import ExactSourceReader, ProofError, digest, ref_key, triple

SCHEMA = 'bounded-input-route-reference/1'
_VIEWS = frozenset(('decision', 'reviewer', 'evidence'))
_URL = re.compile(r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/([a-f0-9]{40})/([^\s#]+)#L([0-9]+)(?:-L([0-9]+))?')


def _version_metadata_matches(node, version):
    """Explicit aliases in already readable nodes may not contradict proof."""
    aliases = {'snapshot_id': ('snapshot_id', 'source_snapshot_id', 'dot_snapshot_id'),
        'source_commit': ('source_commit', 'commit', 'dot_source_commit'),
        'source_repository': ('source_repository', 'repository')}
    return isinstance(node, dict) and all(node[key] == version.get(field)
        for field, keys in aliases.items() for key in keys if key in node)


def _own_citations(original, version, reader):
    """Only exact citations nested in the matched whole Source fact count."""
    ref = version['original_fact_ref']
    fact = reader.read(ref)
    citations = fact.get('citations') if isinstance(fact, dict) else None
    if not isinstance(citations, list) or not citations:
        return None
    own = {ref_key(row) for row in original.get('evidence_refs', [])}
    prefix = ref['pointer'] + '/citations/'
    for key in own:
        if key[2].startswith(prefix):
            index = key[2][len(prefix):]
            if (key[:2] != ref_key(ref)[:2] or not re.fullmatch(r'0|[1-9][0-9]*', index)
                    or int(index) >= len(citations)):
                return None
    result = []
    repositories = set()
    for index, citation in enumerate(citations):
        citation_ref = {**triple(ref), 'pointer': ref['pointer'] + '/citations/' + str(index)}
        if (ref_key(citation_ref) not in own or not isinstance(citation, dict)
                or reader.read(citation_ref) != citation):
            return None
        url = _URL.fullmatch(citation.get('url', ''))
        path = citation.get('path', citation.get('file'))
        start, end = citation.get('line_start'), citation.get('line_end')
        if (url is None or url[2] != version.get('source_commit') or url[3] != path
                or (version.get('source_repository') and url[1] != version['source_repository'])
                or type(start) is not int or type(end) is not int or not 0 < start <= end
                or int(url[4]) != start or int(url[5] or url[4]) != end):
            return None
        if (any(citation[key] != path for key in ('path', 'file') if key in citation)
                or not _version_metadata_matches(citation, {**version, 'source_repository': url[1]})):
            return None
        repositories.add(url[1])
        result.append({'reference': citation_ref, 'path': path, 'value_sha256': digest(citation)})
    if (len(repositories) != 1 or not _version_metadata_matches(fact,
            {**version, 'source_repository': next(iter(repositories))})
            or any(fact[key] != 'NSF' for key in ('kind', 'claim_type') if key in fact)
            or fact.get('classification') in ('RV', 'EI', 'REC', 'UNK', 'PROJECT_POLICY')):
        return None
    return result


def _classified_stage_version(record, original, reader):
    """N003's original classification NSF shape, without method-role inference.

    This adapter is local to route references. It does not alter the sample,
    SourceIdentity, SourceContext or method classifier's accepted shapes.
    """
    scope = record.get('scope')
    commit = scope.get('source_commit') if isinstance(scope, dict) else None
    if not isinstance(commit, str) or not re.fullmatch(r'[a-f0-9]{40}', commit):
        return None
    versions = {}
    for ref in original.get('evidence_refs', []):
        if not re.fullmatch(r'/entries/(0|[1-9][0-9]*)/native_atoms/(0|[1-9][0-9]*)/original_atom', ref.get('pointer', '')):
            continue
        if reader.root_schema(ref) != {'schema_version': 'native003-consolidation-draft-1.0'}:
            continue
        fact = reader.read(ref)
        if (not isinstance(fact, dict) or fact.get('classification') != 'NSF'
                or any(fact[key] != 'NSF' for key in ('kind', 'claim_type') if key in fact)
                or fact.get('statement') != original['statement']):
            return None
        commit_ref = {**triple(ref), 'pointer': '/source_commit'}
        if (not any(ref_key(row) == ref_key(commit_ref) for row in original.get('evidence_refs', []))
                or reader.read(commit_ref) != commit):
            return None
        version = {'source_commit': commit, 'snapshot_id': scope.get('snapshot_id'),
            'source_repository': scope.get('source_repository'),
            'original_fact_ref': triple(ref), 'source_type': 'ORIGINAL_CLASSIFICATION_NSF',
            'original_fact_sha256': digest(fact)}
        citations = _own_citations(original, version, reader)
        if citations is None:
            return None
        repositories = {_URL.fullmatch(reader.read(row['reference'])['url'])[1] for row in citations}
        if len(repositories) != 1:
            return None
        repository = next(iter(repositories))
        if version['source_repository'] and version['source_repository'] != repository:
            return None
        version['source_repository'] = repository
        version['repository_status'] = 'DISCLOSED'
        versions[(commit, repository, digest(fact))] = version
    return next(iter(versions.values())) if len(versions) == 1 else None


def bounded_input_route_reference(record, atom, query, *, context=None,
        projection='coding', view=None, role='reviewer', existing_admitted=False,
        existing_deep_admitted=False, source_reader=None):
    """Disclose only an already admitted original stage and its independent gaps."""
    from .sample_reference import (_original_atom, _reader, _fixed_version,
                                   sample_reference_excluded)
    from .intent_scope import query_scope
    from .task_relevance import record_content_context, task_support
    if (projection != 'reviewer' or role != 'reviewer' or view not in _VIEWS
            or existing_admitted is not True or not isinstance(query, str)
            or not query.strip() or not isinstance(record, dict) or not isinstance(atom, dict)):
        return None
    original = _original_atom(record, atom)
    if (original is None or atom.get('kind') != 'NSF'
            or any(original[key] != 'NSF' for key in ('kind', 'claim_type') if key in original)):
        return None
    if (record.get('knowledge_status') == 'superseded' or record.get('retrieval_status') == 'restricted'
            or record.get('retrieval_status') == 'deep_only' and
               (existing_deep_admitted is not True or query_scope(query)['deep_forbidden'])
            or sample_reference_excluded(query, {}, atom['statement'])):
        return None
    if context is not None and (not isinstance(context, dict)
            or context.get('record_pointer', atom['record_pointer']) != atom['record_pointer']
            or context.get('atom_kind', atom['kind']) != atom['kind']):
        return None
    own_context = {'scope': '', 'receivers': [], 'role_bindings': [], 'atom_kind': atom['kind'],
        'record_pointer': atom['record_pointer'], 'original_content_index': record_content_context([atom])}
    support = task_support(query, atom['statement'], own_context)
    witness = support.get('bounded_route_stage')
    if (not support.get('whole_atom_delivery_allowed') or not isinstance(witness, dict)
            or not input_route_stage_request(query_scope(query)['positive_query'])):
        return None
    try:
        reader = _reader(record, original) if source_reader is None else source_reader
        if not isinstance(reader, ExactSourceReader):
            return None
        classified_shape = any(re.fullmatch(
            r'/entries/(0|[1-9][0-9]*)/native_atoms/(0|[1-9][0-9]*)/original_atom', ref.get('pointer', ''))
            for ref in original.get('evidence_refs', []))
        # This route-local supported shape keeps all its own root/type checks
        # even when the whole Source fact also supplies a literal kind field.
        version = (_classified_stage_version(record, original, reader) if classified_shape else
                   _fixed_version(record, original, atom['kind'], reader))
        if version is None:
            return None
        citations = _own_citations(original, version, reader)
        if citations is None or not _version_metadata_matches(record.get('scope'), version):
            return None
        # A unique own component file is a component actor only. Its cited
        # symbol is not promoted to the caller/function of a demonstrative.
        owners = {re.fullmatch(r'scripts/components/([A-Za-z_]\w*)\.lua', row['path'])[1]
            for row in citations if re.fullmatch(r'scripts/components/([A-Za-z_]\w*)\.lua', row['path'])}
        actor = witness.get('actual_subject')
        if len(owners) == 1 and all(row['path'] == 'scripts/components/' + next(iter(owners)) + '.lua' for row in citations):
            owner = next(iter(owners))
            if actor and re.search(r'[.:]', actor) and re.split(r'[.:]', actor)[0].casefold() != owner.casefold():
                return None
            subject, binding = owner, 'OWN_EXACT_SOURCE_COMPONENT_ONLY'
        elif actor and re.search(r'[.:]', actor):
            owner = re.split(r'[.:]', actor)[0]
            if any(re.split(r'[.:]', str(reader.read(row['reference']).get('symbol', '')))[0].casefold() != owner.casefold()
                   for row in citations):
                return None
            subject, binding = actor, 'ORIGINAL_LITERAL_HEAD_IN_OWN_EXACT_SOURCE'
        else:
            return None
    except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError, UnicodeError):
        return None
    relation = copy.deepcopy(witness)
    relation.update(actual_subject=subject, subject_binding=binding,
        local_behavior_subject=witness.get('actual_subject'),
        function_subject_identity_verified=False, callee_semantics_supported=False)
    return {'schema': SCHEMA, 'record_id': record['id'], 'record_pointer': atom['record_pointer'],
        'kind': atom['kind'], 'statement_sha256': digest(atom['statement']),
        'actual_subject': subject, 'subject_binding': binding,
        'fixed_source_version': version, 'exact_source_citations': citations,
        'current_task_relation': relation, 'stage_kinds': relation['stage_kinds'],
        'named_paths': relation['named_paths'], 'proof_limit': relation['proof_limit'], 'gaps': relation['gaps'],
        'reference_only': True, 'generic_contract_complete': False,
        'full_method_contract_verified': False, 'final_outcome_proven': False,
        'function_subject_identity_verified': False, 'callee_semantics_supported': False,
        'request_transport_proven': False, 'execution_acceptance_proven': False,
        'original_scope_ref': {'record_pointer': '/scope', 'value_sha256': digest(record.get('scope'))},
        'proves': {'record_pointer': atom['record_pointer'], 'kind': atom['kind'], 'statement_sha256': digest(atom['statement'])},
        'notice': '只在本 atom 的固定 Source 与完整原 Scope 内提供中间输入路由阶段参考；'
            '组件来源主体不等于函数主体或 callee METHOD_SUBJECT。此阶段不证明请求传输、执行接受、'
            '最终业务结果、通用闭环或 API 合同完整；原未知、排除和范围缺口仍须独立保留。'}

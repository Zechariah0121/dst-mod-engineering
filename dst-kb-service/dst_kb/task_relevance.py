"""Original-content retrieval, separate from method-role or truth verification."""
import copy
import re

from .request_analysis import analyzed_request, memoized_analysis, memoized_support

from .intent_scope import (
    BROAD_CONCEPTS, DOMAIN_SUBJECTS, SOURCE_METADATA_LABEL, SUBJECT_CONCEPTS, SEMANTIC_REGEX,
    _business_component_names, _explicit_task_owners, _lexical_tokens, _narrow_context, _operations, _precise_symbols,
    _relations, _source_units, _structured_source_units, _structured_competing_head, _source_relation_witness,
    _source_unknown_owner_frames, _verified_method_head, CONCRETE_BEHAVIOR, COMPARISON_REQUEST,
    _comparison_navigation_text, _visible_comparison_request,
    effective_task_query, expand_semantic_query, focused_task_query, query_scope, semantic_concepts, positive_focus_support, structured_record_ids,
    task_requests, task_subjects, task_support as strict_task_support,
)
from .relevance_frames import (request_relations, resource_topics, source_relations,
    literal_data_prose, read_selection_contexts, result_input_scenario,
    result_action_reference, result_action_subject, result_source_relations,
    result_request_dispatch, result_dispatch_senders, literal_result_return,
    input_route_stage_request, input_route_stage_witness, engineering_relations)
from .predicate_grammar import literal_relations


_PROSE_KINDS = frozenset(('NSF', 'REC', 'EI'))
_QUALIFIED_CALLER_HEAD = re.compile(r'^\s*([A-Za-z_]\w*[.:][A-Za-z_]\w*)(?![A-Za-z0-9_])', re.ASCII)
_POSITIVE_QUALIFIED_CALL = re.compile(
    r'(?:调用|\b(?:calls?|invokes?)\b)\s*([A-Za-z_]\w*[.:][A-Za-z_]\w*)(?![A-Za-z0-9_])', re.I | re.ASCII)
_UNCERTAIN_CALL_PREFIX = re.compile(
    r'不|未|没|是否|未知|可能|也许|如果|除非|若|仅当'
    r'|\b(?:not|never|cannot|whether|unknown|unverified|may|might|could|if|unless|when)\b', re.I)
_QUANTITY_SHORTAGE = re.compile(r'不足|短缺|\b(?:shortages?|insufficient|not\s+enough)\b', re.I)


def _original_prose_kind(kind):
    kinds = set(kind.replace(' ', '').split('/'))
    return bool(kinds) and all(value in _PROSE_KINDS or value.startswith('LEGACY_') for value in kinds)
_OPERATION_RELATION_BRIDGES = frozenset(('operation_order',
    'observer_registration_identity', 'registration_state',
    'event_data_bridge', 'declared_initial_value', 'initial_state_arrangement', 'initial_observation'))


_SPECIFIC_RELATIONS = frozenset(('argument_binding', 'callback_binding',
    'field_mutation', 'result_behavior', 'progress_suspension', 'data_handoff',
    'coordinate_binding', 'numeric_value'))
_LABEL_ONLY = re.compile(
    r'^\s*(?:(?:only|just)\s+)?(?:labels?|keywords?|API names)\s*:(?=\s|$)'
    r'|^\s*(?:only|just)\s+(?:metadata|labels?|topic|navigation|keywords?|API names)\s*(?:[:：]|[.!]?\s*$)'
    r'|^\s*(?:仅有标签|仅有标题|导航词)\s*[:：]', re.I)
_DIRECTIVE = re.compile(
    r'应|需|必须|优先|仅|只|先|再|避免|不要|不得|不能|不把|不假定|按|明确|区分|将|保留|列明|核验|核对|决定'
    r'|\b(?:should|must|keep|preserve|separate|choose|use|avoid|never|only|first|then|check|do not)\b', re.I)
_TASK_NOUNS = frozenset(('identity', 'configuration', 'module_loading',
    'world_observation', 'replicated_view'))
_CONTENT_STOP = frozenset(('一个', '这个', '那个', '这些', '那些', '哪些', '一种',
    '这种', '那种', '一些', '所有', '任何', '已经', '还是', '到底', '进行', '能否',
    '的值', '现在', '新建', '重建', '获得', '取得', '获取'))
_DATA_ANCHOR_STOP = frozenset(('data', 'table', 'tables', 'field', 'fields', 'record', 'records',
    'read', 'reads', 'reading', 'load', 'loads', 'select', 'which', 'what', 'source',
    'consumes', 'consume', 'consumption', '数据', '读取', '哪种', '何种', '读哪', '取哪', '消费', '消耗'))
_LIFECYCLE_CONTEXTS = frozenset(('death', 'reroll', 'shard', 'snapshot'))
_RESOURCE_OBJECTS = re.compile(
    r'\b(?:removes?|cancels?|unbinds?|releases?|unsubscribes?)\s+'
    r'(?:(?:the|its|their|these|those|saved|previous|existing)\s+)*'
    r'(?P<objects>[A-Za-z_][A-Za-z0-9_]*(?:\s*(?:[/,]|\band\b|\bor\b)\s*'
    r'[A-Za-z_][A-Za-z0-9_]*)*)\s+'
    r'(?:subscriptions?|listeners?|callbacks?|tasks?|handles?)\b'
    r'(?!\s+(?:names?|labels?|counts?|results?|arguments?|parameters?|status)\b)', re.I)


@memoized_analysis
def content_tokens(text):
    return _lexical_tokens(text) - _CONTENT_STOP


@memoized_analysis
def _request_operations(text):
    operations = _operations(text)
    # Installing a persistence callback wrapper is a construction relation;
    # the callback name alone does not ask to serialize component data.
    if ('save_state' in operations and re.search(
            r'保存包装|保存回调.{0,12}包装|\bonsave\b.{0,30}\bwrapp?\w*\b'
            r'|\bwrapp?\w*\b.{0,30}\b(?:onsave|save callback)\b', text, re.I)
            and re.search(r'\b(?:postinit|common_postinit|master_postinit|prefab|onsave|callbacks?)\b|回调', text, re.I | re.ASCII)
            and not re.search(r'\b(?:serializ\w*|writes?\s+(?:save|persist)\w*\s+data)\b|序列化|写入存档|保存数据', text, re.I)):
        operations.discard('save_state')
    return operations


@memoized_analysis
def _qualified_symbols(text):
    return {value.lower().replace('.', ':') for value in re.findall(
        r'\b[A-Za-z_]\w*[.:][A-Za-z_]\w*\b', text, re.ASCII)
        if value.split(':')[0].split('.')[0].lower() not in
        {'self', 'inst', 'target', 'act', 'data'} and not value.endswith('.lua')}


def _prose(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ' '.join(_prose(child) for child in value)
    if isinstance(value, dict):
        # Dictionary keys and metadata are never source statements.
        return ' '.join(_prose(child) for key, child in value.items()
                        if key not in ('id', 'owner', 'title', 'scope', 'tags',
                            'record_pointer', 'source_refs', 'evidence_refs', 'source', 'sources',
                            'knowledge_kind', 'evidence_level', 'confidence', 'locator', 'locator_structured'))
    return ''


def original_engineering_relations(statement, kind):
    """Literal predicates from an original typed body, never topic metadata."""
    text = _prose(statement)
    if (not _original_prose_kind(kind) or not text.strip()
            or SOURCE_METADATA_LABEL.search(text) or _LABEL_ONLY.search(text)):
        return frozenset()
    return engineering_relations(text, source=True)


def record_content_context(atoms):
    """A disposable lexical index over original prose, excluding all navigation."""
    texts = [_prose(atom['statement']) for atom in atoms
             if _original_prose_kind(atom.get('kind', ''))
             and atom.get('kind') and atom.get('record_pointer')]
    subjects, previous, call_relations = {}, [], []
    for atom in atoms:
        text = _prose(atom['statement'])
        if atom.get('kind') == 'NSF' and isinstance(atom['statement'], str):
            # Only a literal positive call in the caller's own first sentence
            # provides a one-hop relevance edge. Names elsewhere do not.
            sentence = re.split(r'[。；;\n]|(?<=[.!?])\s+', _callsite_prose(text), maxsplit=1)[0]
            caller_head = _QUALIFIED_CALLER_HEAD.match(sentence)
            if caller_head and not SOURCE_METADATA_LABEL.search(sentence):
                for call in _POSITIVE_QUALIFIED_CALL.finditer(sentence):
                    if _UNCERTAIN_CALL_PREFIX.search(sentence[:call.start()]):
                        continue
                    caller = caller_head.group(1).lower().replace('.', ':')
                    callee = call.group(1).lower().replace('.', ':')
                    if caller != callee:
                        call_relations.append({'caller': caller, 'callee': callee,
                            'record_pointer': atom['record_pointer'],
                            'original_statement': atom['statement'],
                            'relation': 'ORIGINAL_NSF_POSITIVE_DIRECT_CALL'})
        head = re.match(r'\s*([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)(?![A-Za-z0-9_])', text, re.ASCII)
        name = head.group(1) if head else ''
        method = bool(name and (re.search(r'[.:_]|[a-z][A-Z]', name) or
                       re.fullmatch(r'[A-Z][a-z]+', name)) and name.lower() not in {
                       'the', 'a', 'an', 'this', 'that', 'if', 'when', 'otherwise', 'source', 'scope'})
        if method:
            previous = [name]
            subjects[atom['record_pointer']] = previous
        elif re.match(r'\s*(?:通过.{0,12}后|本方法|该方法|组件本体|函数本体|此方法|'
                      r'(?:the|this)\s+(?:method|function|component)\s+(?:body\s+)?|after\s+(?:the\s+)?(?:gate|check))', text, re.I):
            subjects[atom['record_pointer']] = list(previous)
        else:
            previous = []
    return {'original_content_tokens': sorted(set().union(*(content_tokens(text) for text in texts))),
            'original_content_concepts': sorted(set().union(*(semantic_concepts(text) for text in texts))),
            'original_method_subjects': subjects, 'original_direct_call_relations': call_relations}


def relevance_query(query):
    """Idempotent focus navigation; task_requests owns all problem continuity."""
    return focused_task_query(query)


def _valid_frames(request, unit, context, source_owners=None):
    frames = request_relations(request)
    # Route stages use their own whole-atom/Source-bounded path below. Generic
    # frame fallback must not revive an excluded or unverified stage.
    matched = (frames & source_relations(unit)) - {'input_route_stage'}
    if _visible_comparison_request(request) and _comparison_method_context(request, unit, context):
        matched = matched | {'mechanism_distinction'}
    if _local_method_comparison(request, unit, context):
        matched = matched | {'local_method_comparison'}
    initial_or_bridge = {'declared_initial_value', 'initial_state_arrangement', 'initial_observation', 'event_data_bridge'}
    if matched & initial_or_bridge:
        requested_data = task_subjects(request) & {'display', 'replicated_view'}
        actual_data = task_subjects(unit) & {'display', 'replicated_view'}
        if requested_data and not actual_data:
            matched -= {'declared_initial_value', 'initial_observation', 'event_data_bridge'}
            if context.get('atom_kind') not in ('REC', 'EI') or _explicit_task_owners(unit):
                matched -= {'initial_state_arrangement'}
    if ('reference_binding_phase' in matched
            and not _reference_phase_method(request, unit, context)):
        matched -= {'reference_binding_phase'}
    if 'operation_order' in matched and not _ordered_step_anchors(request, unit, context):
        matched -= {'operation_order'}
    if ('mechanism_distinction' in matched
            and not _comparison_method_context(request, unit, context)):
        matched -= {'mechanism_distinction'}
    if 'result_contract' in frames and literal_result_return(unit):
        same_method = _primary_method(request, request=True) & _primary_method(unit)
        requested_owners = _explicit_task_owners(request) - {'input', 'action', 'rpc'}
        source_owners_literal = _explicit_task_owners(unit)
        if same_method or requested_owners and requested_owners == source_owners_literal:
            matched = matched | {'result_contract'}
    if 'current_observation' in frames:
        subjects = task_subjects(unit)
        named = _explicit_task_owners(unit) or _qualified_symbols(unit)
        inherited = ((_narrow_context(context) if source_owners is None else source_owners)
                     if not named and not _structured_competing_head(unit) else set())
        if ('display' in task_subjects(request) and
                not (subjects | inherited) & {'display', 'replicated_view'}):
            matched -= {'current_observation'}
    if 'resource_lifetime' in matched:
        requested_resources, source_resources = resource_topics(request), resource_topics(unit)
        # A literally described scheduling operation identifies its task even
        # when an anaphoric request calls that object a job or another noun.
        if 'schedule_task' in _operations(request):
            requested_resources = requested_resources | {'task'}
        if requested_resources and source_resources and not requested_resources & source_resources:
            matched -= {'resource_lifetime'}
    if matched & {'data_source', 'data_flow'}:
        anchors = (content_tokens(request) & content_tokens(
            literal_data_prose(unit, _precise_symbols(request)))) - _DATA_ANCHOR_STOP
        requested_contexts = read_selection_contexts(request) if 'data_source' in frames else frozenset()
        shared_contexts = requested_contexts & read_selection_contexts(unit)
        if requested_contexts and not shared_contexts:
            matched -= {'data_source'}
        if not anchors and not shared_contexts:
            matched -= {'data_source', 'data_flow'}
    return matched


def _frame_compatible(request, unit, context, source_owners=None):
    requested = request_relations(request)
    valid = _valid_frames(request, unit, context, source_owners)
    initial_frames = {'declared_initial_value', 'initial_state_arrangement', 'initial_observation'}
    if (requested & initial_frames and not valid & initial_frames
            and not valid & requested & {'event_data_bridge'}):
        return False
    if (requested & {'reference_binding_phase', 'operation_order', 'mechanism_distinction',
                     'observer_registration_identity'}) - valid:
        return False
    if 'result_contract' in requested:
        return bool(valid)
    return bool(not requested or _qualified_symbols(request) or valid)


def _frame_credit(concerns, operations, requested, valid):
    concerns, operations = set(concerns), set(operations)
    if 'current_observation' in requested and 'current_observation' not in valid:
        concerns.difference_update(('initial_read', 'initial_value'))
        operations.difference_update(('initial_read', 'initial_value'))
    return concerns, operations


@memoized_analysis
def _predicate_owners(unit):
    passive = re.search(r'\b(?:is|are|was|were)\s+\w+ed\s+by\s+([A-Za-z_]\w*(?:[.:]\w+)?)', unit, re.I)
    if passive:
        return task_subjects(passive.group(1)) & (DOMAIN_SUBJECTS | {'display'})
    masked = re.sub(r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b',
                    lambda m: ' ' * len(m.group()), unit)
    predicate = re.search(CONCRETE_BEHAVIOR.pattern + r'|进入|取用|取值|\benters?\b', masked, re.I)
    if predicate:
        return task_subjects(unit[:predicate.start()]) & (DOMAIN_SUBJECTS | {'display'})
    return set()


def _transport_domain_bridge(request, unit, frames):
    if 'input_request_dispatch' not in frames or not result_input_scenario(request):
        return False
    requested = task_subjects(request) & DOMAIN_SUBJECTS
    if requested - {'input', 'action', 'rpc'}:
        return False
    for prefix in result_dispatch_senders(unit):
        # 保留发送者 receiver；RPC 宾语和裸函数的拆词主题不能冒充 owner。
        receivers = [task_subjects(head.group(1)) & DOMAIN_SUBJECTS for head in
            re.finditer(r'\b([A-Za-z_]\w*)[.:][A-Za-z_]\w*', prefix, re.ASCII)]
        if any(not receiver or receiver - {'input', 'rpc'} for receiver in receivers):
            continue
        prose = literal_data_prose(prefix, literal_names=False)
        owners = _explicit_task_owners(prose)
        if owners - {'input', 'action', 'rpc'} or _business_component_names(prose):
            continue
        if not prefix.strip():
            continue
        return True
    return False


def _domain_compatible(request, query_subjects, unit, source_subjects, frames):
    requested = query_subjects & DOMAIN_SUBJECTS
    actual = source_subjects & DOMAIN_SUBJECTS
    # Explicit SG requests keep their owner during prose fallback. Generic
    # construction/load navigation must not substitute player spawn wrappers.
    if ('stategraph' in query_subjects and re.search(
            r'\bstategraph(?:instance)?\b|状态图', request, re.I | re.ASCII)):
        requested = requested | {'stategraph'}
        actual = actual | (source_subjects & {'stategraph'})
    if _transport_domain_bridge(request, unit, frames):
        return True
    # 坐标是属性，不能让界面布局借用另一个世界查询的具体行为。
    if ('display' in query_subjects and 'spatial' in requested and
            not _predicate_owners(unit) & {'display', 'skilltree'} and
            not _precise_symbols(request) & _precise_symbols(unit)):
        return False
    if ('result_contract' in frames and result_action_subject(unit)
            and (result_input_scenario(request) or result_action_reference(request))
            and not requested - {'input', 'action'}):
        # 输入只是这条明确结果问题的场景；不让其它业务组件借 action 的返回值。
        return True
    if not requested or requested & actual:
        return True
    # 生命周期场景不是清理资源的 owner；input 也可能只是并列资源之一。
    if 'resource_lifetime' in frames:
        requested -= _LIFECYCLE_CONTEXTS
    if 'resource_lifetime' in frames and (
            resource_topics(request) & resource_topics(unit) - {'input'}):
        requested -= {'input'}
    if 'resource_lifetime' in frames and _requested_local_head(request, unit, {}):
        spans = list(_RESOURCE_OBJECTS.finditer(request))
        objects = set().union(*(task_subjects(match.group('objects')) for match in spans))
        remainder = _RESOURCE_OBJECTS.sub('', request)
        # 只去掉本句清理动作的资源宾语；其它位置的业务要求仍保留。
        requested -= objects - task_subjects(remainder) - _explicit_task_owners(request)
    if requested:
        return False
    # 通用资源/通道可以跨生命周期复用，另一个具体业务组件仍不能借题准入。
    return not (actual - {'input', 'world'} - _LIFECYCLE_CONTEXTS)


def _result_callee_contract_blocked(request, context):
    if 'result_contract' not in request_relations(request):
        return False
    primary = _primary_method(request, request=True)
    bindings = [row for row in context.get('role_bindings', [])
                if row.get('symbol', '').lower().replace('.', ':') in primary]
    return bool(bindings and all(row.get('role') in (
        'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL',
        'BOUNDED_CALLEE_RELATION_UNDETERMINED') and not row.get('callee_semantics_supported')
        for row in bindings))


def _primary_method(text, context=None, request=False):
    if context is not None:
        verified, _ = _verified_method_head(text, context)
        names = {name.lower().replace('.', ':') for name in verified if ':' in name or '.' in name}
        if names:
            return names
    if request:
        for name in re.finditer(_CALLABLE_SPELLING, text, re.ASCII):
            value = name.group()
            if ':' in value:
                return {value.lower()}
            if '.' in value:
                owner, member = value.split('.', 1)
                if owner[0].isupper() and not (owner.isupper() and member.isupper()):
                    return {value.lower().replace('.', ':')}
            elif '_' not in value:
                return {value.lower()}
        return set()
    prefix = re.sub(r'^\s*(?:(?:review|check|explain|describe|whether|how|does|the|an?)\s+)*', '', text, flags=re.I)
    head = re.match(r'([A-Za-z_]\w*[.:][A-Za-z_]\w*)\b', prefix, re.ASCII)
    return {head.group(1).lower().replace('.', ':')} if head else ({_literal_callable_head(prefix)} if _literal_callable_head(prefix) else set())


# The CamelCase tail already admits every letter/digit; repeating that tail
# adds no spellings, but creates ambiguous partitions during a failed match.
_CALLABLE_SPELLING = r'(?:[A-Za-z_]\w*[.:][A-Za-z_]\w*|[a-z]+_[a-z_]+|[A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*)'


@memoized_analysis
def _literal_callable_head(unit):
    head = re.match(r'\s*(' + _CALLABLE_SPELLING + r')(?![A-Za-z0-9_])', unit, re.ASCII)
    return head.group(1).lower().replace('.', ':') if head else ''


def _requested_local_head(request, unit, context):
    """A literal named subject can navigate prose without promoting its role."""
    heads = _primary_method(unit, context)
    literal = _literal_callable_head(unit)
    if literal:
        heads.add(literal)
    # Several literal methods can be grammatical co-subjects of one original
    # predicate. Only their existing METHOD_SUBJECT bindings may navigate here;
    # a later mentioned callee or another sentence cannot acquire that role.
    identifier = r'[A-Za-z_][A-Za-z0-9_]*(?:[.:][A-Za-z_][A-Za-z0-9_]*)?'
    separator = r'\s*(?:与|和|、|(?i:\band\b)|,)\s*'
    co_subject = re.match(r'\s*(' + identifier +
        r'(?:' + separator + identifier + r')+)'
        r'\s*(?:都|均|各自|(?i:\b(?:both|each|all)\b))', unit, re.ASCII)
    # Preserve the original case-insensitive detection language (including an
    # ordinary first head), without embedding its ambiguous classes in a list.
    if co_subject:
        for name in re.split(separator, co_subject.group(1)):
            if ':' in name or '.' in name:
                continue  # The identifier scan already checked both segments.
            word = name.lower()
            split = word.find('_')
            snake = (split > 0 and word[:split].isalpha() and split + 1 < len(word)
                     and all(char.isalpha() or char == '_' for char in word[split + 1:]))
            camel = (len(word) >= 3 and word[0].isalpha() and word.isalnum()
                     and any(char.isalpha() for char in word[2:]))
            if not (snake or camel):
                co_subject = None
                break
    if co_subject:
        names = {value.lower().replace('.', ':')
                 for value in re.findall(_CALLABLE_SPELLING, co_subject.group(1), re.ASCII)}
        for binding in context.get('role_bindings', []):
            if binding.get('role') != 'METHOD_SUBJECT':
                continue
            symbol = binding.get('symbol', '').lower().replace('.', ':')
            if symbol in names or symbol.rsplit(':', 1)[-1] in names:
                heads.add(symbol)
    requested = {name.replace('.', ':') for name in _precise_symbols(request)}
    return bool(heads & requested or any(
        ':' in head and head.rsplit(':', 1)[0] in requested for head in heads) or any(
        head.rsplit(':', 1)[-1] in requested and
        re.search(r'(?<![A-Za-z0-9_.:])' + re.escape(head.rsplit(':', 1)[-1]) +
                  r'(?![A-Za-z0-9_])', request, re.I | re.ASCII)
        for head in heads))


def _local_method_comparison(request, unit, context):
    """A local comparison selects a preserved relation, never callee contracts."""
    if (not isinstance(context, dict) or context.get('atom_kind') != 'NSF'
            or not context.get('record_pointer') or _LABEL_ONLY.search(unit)
            or SOURCE_METADATA_LABEL.search(unit)):
        return False
    visible_request, visible_unit = _callsite_prose(request), _callsite_prose(unit)
    comparison = bool(COMPARISON_REQUEST.search(visible_request) or re.search(
        r'(?:当作|视为|认定|认为)[^。；;\n]{0,30}(?:同一|相同|等价)'
        r'|\b(?:same|equivalent)\s+(?:contract|behavior|semantics)\b', visible_request, re.I))
    if not comparison or not _source_relation_witness(unit, context)['concrete_behavior']:
        return False
    selected = set()
    for binding in context.get('role_bindings', []):
        symbol = binding.get('symbol', '')
        if not isinstance(symbol, str) or not symbol:
            continue
        leaf = re.split(r'[.:]', symbol)[-1]
        spelling = re.escape(symbol).replace(r'\:', '[.:]')
        qualified = bool(re.search(r'(?<![A-Za-z0-9_])' + spelling + r'(?![A-Za-z0-9_])', visible_request, re.I))
        bare = bool(re.search(r'(?<![A-Za-z0-9_.:])' + re.escape(leaf) + r'(?![A-Za-z0-9_])', visible_request, re.I))
        if not (qualified or bare):
            continue
        if re.search(r'(?<![A-Za-z0-9_])' + re.escape(leaf) + r'(?![A-Za-z0-9_])', visible_unit, re.I):
            selected.add(symbol.lower().replace('.', ':'))
    heads, owners = _verified_method_head(unit, context)
    requested_owners = _explicit_task_owners(visible_request)
    if (requested_owners and not requested_owners & owners
            and not heads & _qualified_symbols(visible_request)):
        return False
    return bool(len({name.rsplit(':', 1)[-1] for name in selected}) >= 2 and heads & selected)


def _same_sentence_comparison_head(query, frame, request, unit, context):
    navigation = frame.get('comparison_navigation') if isinstance(frame, dict) else None
    if not isinstance(navigation, dict) or navigation.get('schema') != 'same-sentence-comparison-navigation/1':
        return False
    original = navigation.get('original_sentence')
    offset = navigation.get('comparison_marker_offset')
    if (not isinstance(original, str) or query.count(original) != 1 or type(offset) is not int or
            navigation.get('request_text') != frame.get('text', '').strip() or
            not original.startswith(navigation['request_text']) or
            not original.endswith(navigation.get('comparison_text', '')) or
            not _visible_comparison_request(query, at=query.find(original) + offset) or
            not _visible_comparison_request(original, at=offset)):
        return False
    method = _unique_original_method(context)
    if not method:
        return False
    symbol, receiver = method
    leaf = symbol.rsplit(':', 1)[-1]
    for clause in query_scope(query)['negative_clauses']:
        if (symbol in _qualified_symbols(clause) or re.search(
                r'(?<![A-Za-z0-9_.:])' + re.escape(leaf) + r'(?![A-Za-z0-9_])', clause, re.I | re.ASCII)):
            return False
    verified, _ = _verified_method_head(unit, context)
    if symbol not in verified or _literal_callable_head(unit) != leaf:
        return False
    visible = _comparison_navigation_text(request)
    if visible is None:
        return False
    bare = {match.group().lower() for match in re.finditer(_CALLABLE_SPELLING, visible, re.ASCII)
            if ':' not in match.group() and '.' not in match.group()}
    if bare != {leaf}:
        return False
    owners = {name.rsplit(':', 1)[0] for name in _qualified_symbols(visible)}
    if owners != {receiver.lower()}:
        return False
    for match in re.finditer(r'(?<![A-Za-z0-9_.:])' + re.escape(leaf) + r'(?![A-Za-z0-9_])',
                             visible, re.I | re.ASCII):
        nearby = visible[max(0, match.start() - 50):match.start()]
        if re.search(r'\b(?:parameters?|arguments?|labels?|metadata|strings?|fields?|titles?)\b|参数|标签|元数据|字符串|字段', nearby, re.I):
            return False
    return True


_ORDER_ANCHOR_STOP = frozenset(('review', 'check', 'please', 'the', 'of', 'order', 'ordering',
    'sequence', 'call', 'calls', 'operation', 'execution', 'cleanup', 'clean', 'clear',
    'consumption', 'consume', 'guard', '先后', '顺序', '审查', '清理', '消耗'))


@memoized_analysis
def _order_anchor_tokens(text):
    tokens = content_tokens(text) - _ORDER_ANCHOR_STOP
    latin = {token for token in tokens if re.fullmatch(r'[a-z_][a-z0-9_]*', token)}
    return {token[:-3] if token.endswith('ing') and len(token) > 5 else token
            for token in (latin or tokens)}


def _nominal_method_order(request, unit, context):
    """Bind a nominal cleanup/callback order to its proved original method head.

    This only supplies navigation for an existing literal order. It cannot
    supply missing steps, a different receiver, or a callback's own contract.
    """
    requested = _qualified_symbols(request)
    verified, _ = _verified_method_head(unit, context)
    verified = {name.lower().replace('.', ':') for name in verified if ':' in name or '.' in name}
    if len(requested) != 1 or not requested <= verified:
        return False
    for continuation in re.split(r'[;；。!?！？\n]', unit)[1:]:
        competing = _primary_method(continuation, context)
        if _structured_competing_head(continuation) or competing and not competing <= requested:
            return False
    if 'operation_order' not in source_relations(unit):
        return False
    residual = _callsite_prose(request)
    if re.search(r'→|->|\b(?:before|after|first|then|followed\s+by)\b|之前|之后|然后|先.{0,40}再', residual, re.I):
        return False
    # effective_text can prepend the already-resolved object referent. Keep
    # its qualified method check above, then inspect the actual review noun.
    review = re.search(r'请?(?:审查|核对|说明)|\b(?:review|check|explain|describe)\b', residual, re.I)
    if review:
        residual = residual[review.start():]
    residual = re.sub(r'\b[A-Za-z_]\w*[.:][A-Za-z_]\w*\b', ' ', residual, flags=re.ASCII)
    residual = re.sub(r'(?:限定|仅限|只看|仅看)(?:这个|该|此|本)?(?:方法|函数)(?:的)?(?:实际)?(?:路径|实现)',
                      ' ', residual)
    residual = re.sub(r'(?:这个|该|此|本)(?:组件|方法|函数)', ' ', residual)
    # Every named aspect must be present in this same original sentence.
    # Unknown nouns remain in the residual and cannot borrow its method name.
    relations = literal_relations(unit)
    if 'callback_binding' in relations:
        residual = re.sub(r'\bcallbacks?\b|回调', ' ', residual, flags=re.I)
    if 'cancel_task' in _operations(unit, source=True):
        residual = re.sub(r'\b(?:cleanup|cancellation|retirement|tasks?|handles?)\b|清理|取消|收尾|任务|句柄',
                          ' ', residual, flags=re.I)
    for concept in semantic_concepts(unit) & semantic_concepts(request):
        residual = SEMANTIC_REGEX[concept].sub(' ', residual)
    residual = re.sub(r'\b(?:review|check|explain|describe|please|the|of|and|order|ordering|sequence)\b'
                      r'|请|审查|核对|说明|先后|顺序|的|与|和|及', ' ', residual, flags=re.I)
    return not re.search(r'[A-Za-z0-9_\u3400-\u9fff]', residual)


def _ordered_step_anchors(request, unit, context=None):
    # Internal ordering belongs to the requested implementation, not to a
    # caller that happens to invoke it as one step in a different sequence.
    visible = _callsite_prose(request)
    internal = re.search(
        r'\b(?:inside|within)\s+(?:the\s+)?(?:(?:body|implementation)\s+of\s+)?'
        r'(' + _CALLABLE_SPELLING + r')(?![A-Za-z0-9_])'
        r'|\b(?:internal|implementation)\s+(?:operation\s+|call\s+)?(?:order|sequence)\s+of\s+'
        r'(' + _CALLABLE_SPELLING + r')(?![A-Za-z0-9_])'
        r'|(' + _CALLABLE_SPELLING + r')\s*(?:内部|函数体|方法体|实现内)',
        visible, re.I | re.ASCII)
    if internal:
        owner = next(value for value in internal.groups() if value).lower().replace('.', ':')
        if owner not in _primary_method(unit, context):
            return False
    if context and _nominal_method_order(request, unit, context):
        return True
    # A single named received/invoked callback can be a caller dispatch step.
    # Additional requested steps still go through the complete anchor check.
    requested = {match.group().lower().replace('.', ':') for match in
                 re.finditer(_CALLABLE_SPELLING, visible, re.ASCII)}
    source = _callsite_prose(unit)
    available = {match.group().lower().replace('.', ':') for match in
                 re.finditer(_CALLABLE_SPELLING, source, re.ASCII)}
    extra_steps = re.search(r'\b(?:and|before|after|then|followed\s+by)\b|、|和|与|及|之后|之前|然后', visible, re.I | re.ASCII)
    if (len(requested) == 1 and requested <= available and not internal and not extra_steps
            and 'operation_order' in source_relations(unit)):
        name = re.escape(next(iter(requested))).replace(':', '[.:]')
        invoked = (r'(?:\b(?:receiv\w*|invok\w*|calls?|calling|dispatch\w*)\s+'
                   r'(?:(?!(?:order|sequence|inside|within)\b)[A-Za-z_]+\s+){0,4}'
                   r'|(?:收到|接收|调用|派发|分派)(?!顺序|次序)[^。；;!?！？\n]{0,24})')
        source_call = r'\b(?:calls?|invokes?|dispatch\w*)\b|调用|派发|分派'
        if (re.search(invoked + name, visible, re.I | re.ASCII)
                and re.search(r'(?:' + source_call + r')[^。；;!?！？\n]{0,70}' + name, source, re.I | re.ASCII)):
            return True
    # 顺序只绑定一个原句内的并列步骤，不跨独立句子或另名主体拼接。
    parts = re.split(r'、|和|与|及|\band\b', request, flags=re.I)
    groups = [_order_anchor_tokens(part) for part in parts]
    if len(groups) == 1 and not requested:
        # A nominal question can name one ordering object without proposing
        # its steps. Require an original content anchor, never just a domain.
        anchors = groups[0] & (content_tokens(unit) - _ORDER_ANCHOR_STOP)
        anchors = {anchor for anchor in anchors if not task_subjects(anchor) & DOMAIN_SUBJECTS}
        if anchors and 'operation_order' in source_relations(unit):
            return True
    if len(groups) < 2 or any(not group for group in groups):
        return False
    available = _order_anchor_tokens(unit)
    if not all(group <= available for group in groups):
        return False
    clauses = re.split(r'[;；]', unit)
    if any(_structured_competing_head(part) for part in clauses[1:]):
        return False
    heads = [re.match(r'\s*(?:the\s+)?([A-Za-z_]\w*)(?![A-Za-z0-9_])',
                      part, re.I | re.ASCII) for part in clauses]
    # 接收者参数和后续callee不是分号后另起的行为主体。
    owners = [_explicit_task_owners(head.group(1)) for head in heads if head]
    owners = [owner for owner in owners if owner]
    return not owners or all(owner == owners[0] for owner in owners)


def _ordered_source_units(statement):
    if not isinstance(statement, str):
        return []
    sentences = [unit.strip() for unit in re.split(r'[。!?！？\n]+|(?<=[.!?])\s+', statement) if unit.strip()]
    result = [(unit, frozenset(), ('ordered_sentence', index))
              for index, unit in enumerate(sentences) if 'operation_order' in source_relations(unit)]
    if (len(sentences) > 1 and result and
            all(re.match(r'\s*(?:该|此|本|其|this\b|that\b|the same\b)', unit, re.I)
                for unit in sentences[1:])):
        result.append((statement, frozenset(), ('ordered_original_atom', 0)))
    return result


def _unique_original_method(context):
    if (not isinstance(context, dict) or context.get('atom_kind') != 'NSF'
            or not context.get('record_pointer')):
        return None
    methods = set()
    for binding in context.get('role_bindings', []):
        if not isinstance(binding, dict) or binding.get('role') != 'METHOD_SUBJECT':
            continue
        symbol, receiver = binding.get('symbol'), binding.get('receiver')
        if (not isinstance(symbol, str) or not isinstance(receiver, str)
                or not re.fullmatch(r'[A-Za-z_]\w*[.:][A-Za-z_]\w*', symbol, re.ASCII)):
            continue
        owner, leaf = re.split(r'[.:]', symbol)
        if owner.lower() == receiver.lower() and owner.lower() not in {
                'self', 'inst', 'target', 'doer', 'item', 'act', 'data'}:
            methods.add((owner.lower() + ':' + leaf.lower(), receiver))
    return next(iter(methods)) if len(methods) == 1 else None


def _comparison_method_context(request, unit, context):
    method = _unique_original_method(context)
    noncall = bool(re.search(
        r'(?:没有|不会|不|未)(?:自动|直接)?调用|\b(?:does\s+not|never)\s+(?:automatically\s+|directly\s+)?(?:call|invoke)\b',
        _callsite_prose(unit), re.I) and any(
            binding.get('role') == 'BOUNDED_CALLEE_NONCALL'
            and binding.get('relation_polarity') == 'NEGATIVE'
            and re.search(r'(?<![A-Za-z0-9_])' + re.escape(binding.get('symbol', '').rsplit(':', 1)[-1])
                          + r'(?![A-Za-z0-9_])', unit, re.I)
            for binding in context.get('role_bindings', [])))
    if not method or not ('mechanism_distinction' in source_relations(unit) or noncall):
        return False
    symbol, _ = method
    leaf = symbol.rsplit(':', 1)[-1]
    original_head = re.match(r'\s*(?:' + re.escape(symbol).replace(':', '[.:]') +
        '|' + re.escape(leaf) + r')(?![A-Za-z0-9_])', unit, re.I | re.ASCII)
    deictic = re.match(r'\s*(?:此|该)(?:函数|方法)|\s*(?:this|that)\s+(?:function|method)\b', unit, re.I)
    nonequivalence_head = re.match(r'\s*(?:不是|不等同|不等价|not\s+(?:simply\s+)?equivalent)', unit, re.I)
    nonequivalence = re.search(r'不是.{0,25}(?:等同|等价)|不(?:等同|等价)'
        r'|\bnot\s+(?:simply\s+)?equivalent\b', unit, re.I)
    if not (original_head or deictic or nonequivalence_head):
        return False
    requested = _primary_method(request, request=True)
    receiver = method[1]
    if re.search(r'(?<![A-Za-z0-9_])' + re.escape(receiver) + r'\s+' + re.escape(leaf)
                 + r'(?![A-Za-z0-9_])', request, re.I):
        requested.add(symbol)
    if not requested:
        return False
    # 对比上下文保留明确非等价关系；它不证明被调用方法的函数体。
    return bool((requested & {symbol, leaf}) or nonequivalence and any(
        re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(name.rsplit(':', 1)[-1]) +
            r'(?![A-Za-z0-9_])', unit, re.I | re.ASCII) for name in requested))


def _reference_phase_method(request, unit, context):
    if (not isinstance(context, dict) or context.get('atom_kind') != 'NSF'
            or not context.get('record_pointer')):
        return False
    methods = set()
    for binding in context.get('role_bindings', []):
        if not isinstance(binding, dict) or binding.get('role') != 'METHOD_SUBJECT':
            continue
        symbol, receiver = binding.get('symbol'), binding.get('receiver')
        if (not isinstance(symbol, str) or not isinstance(receiver, str)
                or not re.fullmatch(r'[A-Za-z_]\w*[.:][A-Za-z_]\w*', symbol, re.ASCII)):
            continue
        owner, leaf = re.split(r'[.:]', symbol)
        if owner.lower() in {'self', 'inst', 'target', 'doer', 'item', 'act', 'data'}:
            continue
        if owner.lower() == receiver.lower():
            methods.add((owner.lower() + ':' + leaf.lower(), leaf.lower()))
    # 短leaf只导航当前原子唯一的声明，不从参数、callee或多个owner中猜主体。
    if len(methods) != 1:
        return False
    symbol, leaf = next(iter(methods))
    qualified = re.findall(r'\b[A-Za-z_]\w*[.:][A-Za-z_]\w*\b', request, re.ASCII)
    prose = literal_data_prose(request, [*qualified, symbol, symbol.replace(':', '.'), leaf], literal_names=False)
    requested = _qualified_symbols(prose)
    if requested and requested != {symbol}:
        return False
    directive = (r'(?:\b(?:review|check|explain|describe)\s+'
                 r'(?:(?:how|whether|the|method|function)\s+)*|(?:审查|检查|解释|说明)\s*)')
    spellings = (re.escape(symbol).replace(':', '[.:]'), re.escape(leaf))
    if not any(re.search(directive + spelling + r'(?![A-Za-z0-9_])', prose, re.I | re.ASCII)
               for spelling in spellings):
        return False
    source_heads = {name for name in _primary_method(unit, context)
                    if name.split(':', 1)[0] not in {'self', 'inst', 'target', 'doer', 'item', 'act', 'data'}}
    if source_heads and source_heads - {symbol, leaf}:
        return False
    subject = re.match(r'^\s*(?:the\s+)?([A-Za-z_]\w*)\s+'
        r'(?:(?:later|then|subsequently)\s+)?(?:captures?|captured|rereads?|reread)\b', unit, re.I | re.ASCII)
    if subject and subject.group(1).lower() not in {leaf, 'self'}:
        return False
    subject = re.match(r'^\s*([A-Za-z_]\w*)(?:后续|随后|先前|先|再|已经)?'
        r'(?:捕获|重读|重新(?:读取|读|取)|再次(?:读取|读))', unit, re.ASCII)
    if subject and subject.group(1).lower() not in {leaf, 'self'}:
        return False
    if re.match(r'^\s*(?:回调(?:函数)?|callback)\s*(?:后续|随后|重新|重读)', unit, re.I):
        return False
    return True


def _helper_reference_compatible(frame, statement, context):
    if frame is None:
        return True
    question = frame['text']
    typed = re.search(r'\b(?:that|this|the same)\s+(?:helper|function|method)\b'
                      r'|(?:该|此|这个|那个)(?:辅助)?(?:函数|方法)', question, re.I)
    premises = frame.get('context_units', [])
    if typed:
        targets = set()
        for premise in premises:
            targets.update(match.group(1).lower().replace('.', ':') for match in re.finditer(
                r'\b(?i:uses?|calls?|invokes?)\s+(' + _CALLABLE_SPELLING + r')(?![A-Za-z0-9_])',
                premise, re.ASCII))
            for match in re.finditer(r'(?:使用|调用)\s*(' + _CALLABLE_SPELLING + r')(?![A-Za-z0-9_])', premise, re.ASCII):
                targets.add(match.group(1).lower().replace('.', ':'))
            if not targets:
                head = _literal_callable_head(premise)
                if head:
                    targets.add(head)
        # 无前提或多个候选都不能给单数回指补造对象。
        if len(targets) != 1:
            return False
        heads = set()
        for unit in _source_units(statement):
            heads |= _primary_method(unit, context)
            head = _literal_callable_head(unit)
            if head:
                heads.add(head)
        if not targets & heads:
            return False
    described = re.search(r'\bthe\s+(?:inspected|named|available)\s+'
                          r'([A-Za-z][A-Za-z /-]{0,70}?)\s+helpers?\b', question, re.I)
    if described:
        descriptors = content_tokens(described.group(1)) - {'and', 'or', 'same', 'other'}
        subject_tokens = set()
        for unit in _source_units(statement):
            head = _literal_callable_head(unit)
            if head:
                original_head = re.match(r'\s*(' + _CALLABLE_SPELLING + r')', unit, re.ASCII).group(1)
                subject_tokens |= content_tokens(original_head)
            else:
                predicate = CONCRETE_BEHAVIOR.search(unit)
                prefix = unit[:predicate.start()] if predicate else ''
                if re.search(r'\b(?:helper|function|method)s?\b', prefix, re.I):
                    subject_tokens |= content_tokens(prefix)
        if descriptors and not descriptors & subject_tokens:
            return False
    return True


@memoized_analysis
def _callsite_prose(unit):
    """Hide string contents, retaining inline formatting of a callable expression."""
    result, index = list(unit), 0
    quotes = {'"': '"', "'": "'", '`': '`', '“': '”', '‘': '’'}
    while index < len(unit):
        long_string = re.match(r'\[(=*)\[', unit[index:]) if unit[index] == '[' else None
        if long_string:
            closing = ']' + long_string.group(1) + ']'
            end = unit.find(closing, index + long_string.end())
            stop = len(unit) if end == -1 else end + len(closing)
            result[index:stop] = ' ' * (stop - index)
            index = stop
            continue
        quote = unit[index]
        if quote not in quotes or quote in ("'", '‘') and index and unit[index - 1].isalnum():
            index += 1
            continue
        end = index + 1
        while end < len(unit):
            if unit[end] == '\\':
                end += 2
            elif unit[end] == quotes[quote]:
                break
            else:
                end += 1
        content = unit[index + 1:end]
        formatted_call = quote == '`' and end < len(unit) and re.fullmatch(
            _CALLABLE_SPELLING + r'(?:\([^`\n]*\))?', content.strip(), re.ASCII)
        if formatted_call:
            result[index + 1:end] = _callsite_prose(content)
        else:
            stop = min(end + 1, len(unit))
            result[index:stop] = ' ' * (stop - index)
        index = end + 1
    return ''.join(result)


@memoized_analysis
def _callsite_text_operand(prefix):
    return bool(re.search(
        r'\b(?:stores?|writes?|prints?|logs?|records?|displays?)\b'
        r'(?:(?!\b(?:and|then|before|after)\b).){0,60}'
        r'\b(?:text|strings?|labels?|messages?)\b'
        r'(?:\s+(?:containing|saying|reading))?\s*[:=]?\s*$'
        r'|(?:存储|保存|写入|打印|记录|显示)'
        r'(?:(?!然后|再|并且|并)[^，,。；;\n]){0,24}'
        r'(?:文本|字符串|标签|日志)(?:内容|文字)?\s*[:：=]?\s*$', prefix, re.I))


def _primary_bounded_callsite(request, unit, context, primary):
    """Navigate an already typed call to the primary target, never its contract."""
    if (not isinstance(context, dict) or context.get('atom_kind') != 'NSF'
            or not context.get('record_pointer') or not context.get('original_content_index')
            or len(primary) != 1):
        return False
    request_prose = re.sub(r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b', ' ', request)
    if (_relations(request, query=True) & {'argument_binding', 'result_behavior'}
            or re.search(r'\b(?:outputs?|outcomes?|yield(?:s|ed)?(?:\s+values?)?)\b'
                         r'|\binputs?\s+(?:values?|data|arguments?|parameters?)\b'
                         r'|输入(?:值|数据|参数)|入参|输出|产出', request_prose, re.I)
            or semantic_concepts(request) & {'return_nil', 'return_false', 'return_contract'}):
        return False
    target = next(iter(primary))
    bindings = [binding for binding in context.get('role_bindings', [])
                if isinstance(binding, dict) and isinstance(binding.get('symbol'), str)]
    normalize = lambda value: value.lower().replace('.', ':')
    leaf = target.rsplit(':', 1)[-1]
    candidates = [binding for binding in bindings
                  if normalize(binding['symbol']) == target or
                  ':' not in target and normalize(binding['symbol']).rsplit(':', 1)[-1] == leaf]
    if not candidates:
        return False
    peers = [binding for binding in bindings
             if normalize(binding['symbol']).rsplit(':', 1)[-1] == leaf]
    owners = {normalize(binding['symbol']).rsplit(':', 1)[0]
              for binding in peers if ':' in normalize(binding['symbol'])}
    owners |= {normalize(binding['receiver']) for binding in peers
               if isinstance(binding.get('receiver'), str) and binding['receiver']}
    if ':' not in target and len(owners) > 1:
        return False
    if any(binding.get('role') in ('BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')
           for binding in candidates):
        return False
    from .facet_contracts import statement_binding
    callsite_unit = _callsite_prose(unit)
    for binding in candidates:
        if (binding.get('record_pointer', context['record_pointer']) != context['record_pointer']
                or binding.get('role') != 'BOUNDED_CALLEE_CALLSITE'
                or binding.get('relation_polarity') != 'POSITIVE'
                or binding.get('positive_callsite_evidence') is not True
                or binding.get('callee_semantics_supported') is not False):
            continue
        if (':' in normalize(binding['symbol']) and len(owners) > 1 and
                not re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(binding['symbol']) +
                              r'(?![A-Za-z0-9_])', callsite_unit, re.ASCII)):
            continue
        witness = statement_binding(callsite_unit, binding['symbol'], allow_bare=True, source_callable=True)
        if (witness and witness.get('role') == 'BOUNDED_CALLEE_CALLSITE'
                and witness.get('relation_polarity') == 'POSITIVE'
                and witness.get('positive_callsite_evidence') is True
                and witness.get('callee_semantics_supported') is False
                and any(not _callsite_text_operand(callsite_unit[:relation['predicate_span'][0]])
                        for relation in witness.get('call_relations', []))):
            return True
    return False


def _local_predicate_compatible(request, query_subjects, unit, source_subjects, frames, context=None,
                                comparison_navigation=False, requested_operations=None):
    if _LABEL_ONLY.search(unit) or SOURCE_METADATA_LABEL.search(unit):
        return False
    requested_operations = (_request_operations(request) if requested_operations is None
                            else requested_operations)
    source_operations = _operations(unit, source=True)
    if (requested_operations and not requested_operations & source_operations
            and not frames & _OPERATION_RELATION_BRIDGES):
        return False
    if 'schedule_task' in requested_operations and 'schedule_task' not in source_operations:
        return False
    requested_names, source_names = _qualified_symbols(request), _qualified_symbols(unit)
    requested_head, source_head = _primary_method(request, request=True), _primary_method(unit, context)
    named_head = _requested_local_head(request, unit, context)
    compared_head = bool(comparison_navigation or 'local_method_comparison' in frames
                         or _visible_comparison_request(request) and
                         (named_head or 'mechanism_distinction' in frames))
    bare_head_match = named_head and any(':' not in name for name in requested_head)
    ordered_step = bool('operation_order' in frames and _ordered_step_anchors(request, unit, context))
    primary_callsite = False
    if requested_head and source_head and not requested_head & source_head and not (compared_head or bare_head_match or ordered_step):
        primary_callsite = _primary_bounded_callsite(request, unit, context, requested_head)
        if not primary_callsite:
            return False
    source_names |= {name for name in source_head if ':' in name}
    if requested_names and source_names and not requested_names & source_names and not (compared_head or primary_callsite or ordered_step):
        return False
    if (re.search(r'\b(?:dispatch\w*|emits?|send\w*|push\w*|event delivery)\b|推送|发送|分派|派发', request, re.I)
            and 'event_delivery' in _relations(request, query=True) and
            'event_delivery' not in literal_relations(unit)):
        return False
    if (re.search(r'\bcallbacks?\s+(?:invocations?|calls?)\b|\b(?:calls?|invokes?)\s+(?:the\s+)?callback\b'
                  r'|调用.{0,8}回调|回调.{0,8}调用', request, re.I)
            and 'callback_binding' not in literal_relations(unit)):
        return False
    if 'value_evaluation_phase' in frames:
        owners = _predicate_owners(unit) or source_subjects
        requested = query_subjects & DOMAIN_SUBJECTS - {'combat', 'spatial', 'world'}
        if requested and not requested & owners:
            return False
    return named_head or _domain_compatible(request, query_subjects, unit, source_subjects, frames)


def _excluded_original_owners(query, statement, context):
    scope = query_scope(query)
    if not scope['negative_clauses']:
        return set()
    excluded = set().union(*(task_subjects(clause) for clause in scope['negative_clauses']))
    excluded -= _explicit_task_owners(effective_task_query(query))
    result = set()
    for unit in _source_units(statement):
        if (_source_relation_witness(unit, context)['concrete_behavior'] or _DIRECTIVE.search(unit)):
            result |= _explicit_task_owners(unit) & excluded
    return result


def _bounded_route_excluded(query, statement, witness):
    from .relevance_frames import _route_quote_view
    visible_query, visible_statement = _route_quote_view(query), _route_quote_view(statement)
    # The shared task parser treats 实现 as a possible new positive request.
    # Preserve this route's explicit local implementation exclusion before
    # that parser can shorten “不要具体实现” to the word “具体”. An owner
    # before or after “implementation” still scopes only that owner's facts.
    implementation = re.compile(r'实现(?:细节)?|\bimplementations?(?:\s+details?)?\b', re.I)
    markers = re.compile(r'(?:不要|不需要|无需|排除|不涉及|不讨论|不展开|不看|禁止|别|'
        r'\b(?:without|excluding|exclude|no|not\s+interested\s+in|do\s+not\s+need|'
        r'must\s+not|do\s+not|don[\x27’]t|cannot|can[\x27’]t|never|not)\b)\s*'
        r'(?P<body>(?:(?!\.\s)[^，,。；;!?！？\n])+)', re.I)
    for match in markers.finditer(visible_query):
        body = re.split(r'\b(?:but|however|instead|now|please)\b|但是|但|而是', match['body'], maxsplit=1, flags=re.I)[0]
        if not implementation.search(body):
            continue
        selector = implementation.sub(' ', body)
        selector = re.sub(r'\b(?:include|show|give|provide|return|any|all|the|a|an|concrete|specific|'
            r'detailed|actual|details?|code|of|for|and|or|components?|methods?|functions?)\b'
            r'|任何|所有|具体|实际|相关|详细|展开|介绍|说明|提供|返回|包括|这类|代码|细节|组件|函数|方法|的',
            ' ', selector, flags=re.I).strip(' \t\r\n.:：')
        if not selector:
            # A masked quoted owner/payload must not turn a scoped exclusion
            # into an ownerless global exclusion.
            original_body = query[match.start('body'):match.start('body') + len(body)]
            if not any(not char.isspace() and visible.isspace()
                       for char, visible in zip(original_body, body)):
                return True
            continue
        qualified = {name.casefold().replace('.', ':') for name in re.findall(
            r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b', selector, re.ASCII)}
        if qualified:
            source_paths = {name.casefold().replace('.', ':') for name in re.findall(
                r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b', visible_statement, re.ASCII)}
            if any(source == name or source.endswith(':' + name)
                   for name in qualified for source in source_paths):
                return True
            continue
        identifiers = {name.casefold() for name in re.findall(r'\b[A-Za-z_]\w*\b', selector, re.ASCII)}
        source_identifiers = {name.casefold() for name in re.findall(r'\b[A-Za-z_]\w*\b', visible_statement, re.ASCII)}
        precise = _precise_symbols(selector)
        owners = _explicit_task_owners(selector) or task_subjects(selector) & DOMAIN_SUBJECTS
        matches = (precise & source_identifiers if precise else
                   owners & task_subjects(visible_statement) if owners else identifiers & source_identifiers)
        if matches:
            return True
    for negative in query_scope(visible_query)['negative_clauses']:
        if implementation.search(negative):
            # Its complete owner scope was already checked above; words such
            # as candidate/dispatch inside it cannot become global filters.
            if re.fullmatch(r'\s*(?:(?:any|all|include|give|show|return|provide)\s+)*'
                    r'(?:implementations?|implementation\s+details?|实现(?:细节)?)\s*[。.!！?？]?\s*', negative, re.I):
                return True
            continue
        if (re.search(r'中间(?:阶段|过程)|路由(?:阶段|过程)|\bintermediate\s+(?:(?:route|routing)\s+)?(?:stages?|steps?|process)\b', negative, re.I)
                or _qualified_symbols(negative) & _qualified_symbols(statement)
                or re.search(r'候选|重选|\b(?:candidates?|reselection)\b', negative, re.I)
                   and any(kind.startswith('CANDIDATE_') for kind in witness['stage_kinds'])
                or re.search(r'locomotor|分流|分发|\bdispatch\b', negative, re.I)
                   and 'ACTION_LOCOMOTOR_DISPATCH' in witness['stage_kinds']):
            return True
    return False


def _bounded_route_support(query, positive, statement, context, original, requests):
    """A route stage is an independent bounded relation, not a result witness."""
    if (not input_route_stage_request(positive) or not isinstance(statement, str)
            or context.get('atom_kind') != 'NSF' or not context.get('record_pointer')
            or original.get('excluded_source_scope') or original.get('whole_atom_excluded_relation_owners')
            or any(row.get('ambiguous_owner_reference') for row in requests)):
        return None
    witness = input_route_stage_witness(statement)
    if witness is None or _bounded_route_excluded(query, statement, witness):
        return None
    requested = task_subjects(positive) & DOMAIN_SUBJECTS
    # This bridge is only the input/action question. Other business owners and
    # recipient requests keep the existing independent relation/owner gates.
    if requested - {'input', 'action', 'rpc'} or 'recipient_routing' in request_relations(positive):
        return None
    requested_names = _qualified_symbols(positive)
    source_names = _qualified_symbols(statement)
    if requested_names and not requested_names & source_names:
        return None
    if _business_component_names(positive) - _business_component_names(statement):
        return None
    source_actor = witness['actual_subject']
    if source_actor:
        actor_owners = task_subjects(source_actor) & DOMAIN_SUBJECTS
        # Qualified unrelated receivers cannot borrow a named input operand.
        if actor_owners - {'input', 'action', 'rpc'}:
            return None
        if ':' in source_actor or '.' in source_actor:
            actor = re.split(r'[.:]', source_actor)[0]
            if _business_component_names(actor) and not actor_owners:
                return None
    result = copy.deepcopy(original)
    result.update(supported=True, whole_atom_delivery_allowed=True,
        support_meaning='TASK_RELEVANCE_ONLY', query_assertion_verified=False,
        relevance_lane='ORIGINAL_CONTENT', method_contract_verified=False,
        relevance_original_pointer=context['record_pointer'], relevance_source_unit=statement,
        relevance_relation_frames=['input_route_stage'], bounded_route_stage=witness,
        supported_task_units=[row['text'] for row in requests],
        mechanism_hits=['input_route_stage'], lexical_hits=[])
    return result


def _direct_callee_shortage_reference(request, statement, context, original,
                                     predicate_request, requested_operations):
    """Select a helper's own bounded result through one original positive call.

    The edge establishes task relevance only. It never supplies the caller's
    return contract, changes either source role, or proves cross-version use.
    """
    visible_request = _callsite_prose(request)
    if (not isinstance(context, dict) or context.get('atom_kind') != 'NSF'
            or not context.get('record_pointer') or not isinstance(statement, str)
            or not _QUANTITY_SHORTAGE.search(visible_request)
            or requested_operations
            or not re.search(r'返回|结果|边界|\b(?:returns?|results?|outputs?|boundar\w*)\b',
                             _callsite_prose(predicate_request), re.I)
            or _relations(predicate_request, query=True) & {'argument_binding', 'callback_binding', 'event_delivery'}
            or original.get('excluded_source_scope')
            or original.get('whole_atom_excluded_relation_owners')):
        return None
    if any(not task_subjects(name) & DOMAIN_SUBJECTS
           for name in _business_component_names(visible_request)):
        return None
    index = context.get('original_content_index')
    if not isinstance(index, dict):
        return None
    candidates = []
    for edge in index.get('original_direct_call_relations', []):
        if edge.get('relation') != 'ORIGINAL_NSF_POSITIVE_DIRECT_CALL':
            continue
        caller = edge['caller']
        owner, leaf = caller.split(':', 1)
        # Bare names, unknown receivers and similarly named owners cannot select
        # this edge. A space-separated owner/method is ordinary API navigation.
        if not task_subjects(owner) & DOMAIN_SUBJECTS:
            continue
        if not {caller, leaf} & _primary_method(visible_request, request=True):
            continue
        literal_caller = bool(re.search(r'(?<![A-Za-z0-9_])' + re.escape(owner)
            + r'(?:[.:]|\s+)' + re.escape(leaf) + r'(?![A-Za-z0-9_])', visible_request, re.I))
        if not literal_caller:
            continue
        for unit in _source_units(statement):
            heads, _ = _verified_method_head(unit, context)
            if (edge['callee'] not in heads or SOURCE_METADATA_LABEL.search(unit)
                    or not _source_relation_witness(unit, context)['concrete_behavior']):
                continue
            if not (re.search(r'\breturns?\b|返回', _callsite_prose(unit), re.I)
                    and re.search(r'\btables?\b|表', _callsite_prose(unit), re.I)
                    and _QUANTITY_SHORTAGE.search(_callsite_prose(statement))):
                continue
            candidates.append((edge, unit))
    unique = {(edge['caller'], edge['callee'], edge['record_pointer'], unit): (edge, unit)
              for edge, unit in candidates}
    if len(unique) != 1:
        return None
    edge, unit = next(iter(unique.values()))
    result = copy.deepcopy(original)
    result.update(supported=True, whole_atom_delivery_allowed=True,
        support_meaning='TASK_RELEVANCE_ONLY', query_assertion_verified=False,
        method_contract_verified=False, relevance_lane='ORIGINAL_CONTENT',
        relevance_original_pointer=context['record_pointer'], relevance_source_unit=unit,
        relevance_relation_frames=['bounded_direct_callee_shortage_result'],
        mechanism_hits=['bounded_direct_callee_shortage_result'], supported_task_units=[request],
        bounded_callee_reference={'caller': edge['caller'], 'callee': edge['callee'],
            'original_call_record_pointer': edge['record_pointer'],
            'source_result_record_pointer': context['record_pointer'],
            'caller_contract_verified': False, 'source_role_promoted': False})
    return result


def _single_request_support(query, statement, context='', request_frame=None):
    """Relevance can select original advice without asserting a callee contract."""
    bounded_frames = [request_frame] if request_frame is not None else None
    original = (strict_task_support(query, statement, context) if bounded_frames is None else
                strict_task_support(query, statement, context, _request_frames=bounded_frames))
    if not isinstance(context, dict) or not context.get('original_content_index'):
        return original
    if not query.strip() or re.fullmatch(r'[A-Za-z_]\w*(?:[.:]\w+)?', query.strip()):
        return original
    resolved = relevance_query(query) if request_frame is None else query
    result = strict_task_support(resolved, statement, context) if resolved != query else original
    requests = task_requests(resolved) if bounded_frames is None else bounded_frames
    positive = '; '.join(row['effective_text'] for row in requests)
    # A definite object reference contributes its original owner and conditions;
    # it does not request replay of every background operation on that object.
    operation_request = '; '.join(row.get('predicate_text',
        row['text'] if row.get('context_role') == 'REFERENT_ONLY' else row['effective_text'])
        for row in requests)
    requested_operations = _request_operations(operation_request)
    if _result_callee_contract_blocked(positive, context):
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'result_callee_contract_blocked': True}
    inherited_subjects = set().union(*(set(row['inherited_subjects']) for row in requests))
    inherited_unknown_owners = {owner.split(':', 1)[1] for row in requests
        for owner in row.get('inherited_owner_context', []) if owner.startswith('component:')}
    text = _prose(statement)
    if not all(_helper_reference_compatible(row, text, context) for row in requests):
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'unresolved_helper_reference': True}
    excluded_symbols = set().union(*(_qualified_symbols(clause)
                                    for clause in query_scope(query)['negative_clauses']))
    source_symbols = _qualified_symbols(text) | set().union(*(
        _verified_method_head(unit, context)[0] for unit in _source_units(text)))
    if excluded_symbols & source_symbols:
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'excluded_source_scope': True}
    helper_reference = _direct_callee_shortage_reference(positive, statement, context, original,
                                                        operation_request, requested_operations)
    if helper_reference is not None:
        return helper_reference
    route = _bounded_route_support(query, positive, statement, context, result, requests)
    if route is not None:
        return route
    if (result.get('whole_atom_delivery_allowed') and
            not request_relations(positive) & {'operation_order', 'mechanism_distinction'} and
            not _LABEL_ONLY.search(text) and
            _frame_compatible(positive, result.get('source_unit', ''), context) and
            _local_predicate_compatible(positive, task_subjects(positive) | inherited_subjects,
                result.get('source_unit', ''), set(result.get('source_subjects', [])),
                _valid_frames(positive, result.get('source_unit', ''), context), context,
                _same_sentence_comparison_head(query, request_frame, positive,
                                               result.get('source_unit', ''), context),
                requested_operations=requested_operations)):
        request = positive
        if request_relations(request) and not _qualified_symbols(request):
            result = copy.deepcopy(result)
            valid = _valid_frames(request, result.get('source_unit', ''), context)
            hits, _ = _frame_credit(result.get('mechanism_hits', []), set(), request_relations(request), valid)
            result['mechanism_hits'] = sorted(hits | valid)
            result['relevance_relation_frames'] = sorted(valid)
        return result
    # 关系问题不能退化成碰巧出现的名词；不把拒绝的 strict 结果误作兜底成功。
    if result.get('whole_atom_delivery_allowed'):
        result = copy.deepcopy(result)
        result.update(supported=False, whole_atom_delivery_allowed=False, supported_task_units=[])
        original = result
    kinds = set(context.get('atom_kind', '').replace(' ', '').split('/'))
    if not kinds or not kinds <= _PROSE_KINDS or not context.get('record_pointer'):
        return original
    if not text.strip() or SOURCE_METADATA_LABEL.search(text) or _LABEL_ONLY.search(text):
        return original
    if (result.get('excluded_source_scope') or result.get('whole_atom_excluded_relation_owners')
            or any(row.get('ambiguous_owner_reference') for row in task_requests(query))):
        return original
    # 检索相关性不得把一个明确的另名组件或 callee 参数/返回变成当前方法证明。
    requested_owners = _explicit_task_owners(positive) | (inherited_subjects & DOMAIN_SUBJECTS)
    bounded_owners = set(result.get('source_subjects', [])) & DOMAIN_SUBJECTS
    if (requested_owners and bounded_owners and not requested_owners & bounded_owners
            and result.get('subject_mismatch') and not result.get('matched_symbols')
            and not any(_transport_domain_bridge(positive, unit, _valid_frames(positive, unit, context))
                        for unit in _source_units(text))):
        return original
    unknown_owners = {name for name in _business_component_names(positive)
                      if not task_subjects(name) & DOMAIN_SUBJECTS} | inherited_unknown_owners
    if unknown_owners and _explicit_task_owners(text):
        return original
    original_operations = _operations(text, source=True)
    if (requested_operations and not requested_operations & original_operations
            and not any(_valid_frames(positive, unit, context) & _OPERATION_RELATION_BRIDGES
                        for unit in _source_units(text))):
        return original
    if 'schedule_task' in requested_operations and 'schedule_task' not in original_operations:
        return original
    requested_relations = _relations(positive, query=True)
    if ('argument_binding' in requested_relations and
            'argument_binding' not in _relations(text, context=context) and
            'recipient_routing' not in request_relations(positive)):
        return original
    bindings = context.get('role_bindings', [])
    requested_symbols = _precise_symbols(positive)
    qualified_requested = _qualified_symbols(positive)
    qualified_context = {binding.get('symbol', '').lower().replace('.', ':') for binding in bindings}
    matching_roles = [binding for binding in bindings
                      if binding.get('symbol', '').lower() in requested_symbols]
    if (matching_roles and all(binding.get('role') in
            ('BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')
            for binding in matching_roles)
            and (requested_relations & {'argument_binding', 'result_behavior'} or
                 semantic_concepts(positive) & {'return_nil', 'return_false', 'return_contract'} or
                 re.search(r'\breturns?\b|返回|返回值', positive, re.I))):
        return original
    query_tokens = content_tokens(expand_semantic_query(positive))
    query_concepts = semantic_concepts(positive)
    query_subjects = task_subjects(positive) | inherited_subjects
    query_frames = request_relations(positive)
    context_owners = _narrow_context(context)
    matches = []
    previous_owners, previous_qualified = set(), set()
    previous_owner_seen = False
    path_owners = set()
    structured_owner_blocked = False
    previous_lane = object()
    source_units = _structured_source_units(statement)
    unknown_source_frames = (_source_unknown_owner_frames(statement) if unknown_owners else
                             [frozenset() for _ in source_units])
    if len(unknown_source_frames) != len(source_units):
        return original
    framed_source_units = list(zip(source_units, unknown_source_frames))
    if 'operation_order' in query_frames:
        for ordered_unit in _ordered_source_units(statement):
            owners = frozenset()
            if unknown_owners:
                local_frames = _source_unknown_owner_frames(ordered_unit[0])
                if local_frames and all(frame == local_frames[0] for frame in local_frames):
                    owners = local_frames[0]
            framed_source_units.append((ordered_unit, owners))
    for (unit, structured_owner, lane), unknown_source_owners in framed_source_units:
        if lane != previous_lane:
            previous_owners, previous_qualified = set(), set()
            previous_owner_seen = False
            path_owners = set()
            structured_owner_blocked = False
            previous_lane = lane
        named_owners = _explicit_task_owners(unit)
        qualified = _qualified_symbols(unit)
        verified_symbols, verified_owners = _verified_method_head(unit, context)
        if verified_symbols:
            # A proved current grammatical method head owns this predicate;
            # a named positive/negative callee later in it is still an operand.
            named_owners = verified_owners or named_owners
            qualified = qualified | verified_symbols
        competing_head = _structured_competing_head(unit)
        if competing_head:
            previous_owners, previous_qualified = set(), set()
            previous_owner_seen = True
            structured_owner_blocked = True
        if named_owners or qualified:
            previous_owners, previous_qualified = named_owners, qualified
            previous_owner_seen = True
        local_subjects = task_subjects(unit) - {'return_contract', 'allocation'}
        if not named_owners and not qualified and len(local_subjects) == 1:
            previous_owners = local_subjects
            previous_owner_seen = True
        inherited = ((set(structured_owner or ()) or context_owners)
                     if not structured_owner_blocked and not previous_owner_seen else set())
        source_owners = named_owners or previous_owners or inherited
        if ('mechanism_distinction' in _valid_frames(positive, unit, context)
                and _unique_original_method(context)):
            source_owners = task_subjects(_unique_original_method(context)[1]) & DOMAIN_SUBJECTS
        path_continuation = bool(re.match(r'\s*(?:therefore\s+)?(?:this|that|its)\s+(?:\w+\s+){0,2}(?:chain|path|branch)\b'
            r'|\s*(?:因此)?(?:此|该|其)(?:默认|普通|武器|当前){0,3}(?:链|路径|分支)', unit, re.I))
        if path_continuation and path_owners:
            source_owners |= path_owners
        elif (re.search(r'\b(?:chain|path)\b|链|路径', unit, re.I) or
              qualified and re.search(r'\b(?:calls?|invokes?)\b|调用', unit, re.I)):
            path_owners = _predicate_owners(unit)
        else:
            path_owners = set()
        qualified = qualified or previous_qualified
        if unknown_owners and not unknown_owners & unknown_source_owners:
            continue
        transport = _transport_domain_bridge(positive, unit, _valid_frames(positive, unit, context))
        if requested_owners and source_owners and not requested_owners & source_owners and not transport:
            continue
        comparison_navigation = _same_sentence_comparison_head(query, request_frame, positive, unit, context)
        compared_head = bool(comparison_navigation or _visible_comparison_request(positive) and
                             _requested_local_head(positive, unit, context))
        if qualified_requested and not qualified_requested & (qualified or qualified_context) and not compared_head:
            continue
        unit_operations = _operations(unit, source=True)
        if (requested_operations and not requested_operations & unit_operations
                and not _valid_frames(positive, unit, context, source_owners) & _OPERATION_RELATION_BRIDGES):
            continue
        source_tokens = content_tokens(unit)
        owner_tokens = {token for token in source_tokens | query_tokens
                        if task_subjects(token) & DOMAIN_SUBJECTS and not _operations(token)}
        literal = (query_tokens & source_tokens) - owner_tokens
        source_concepts = semantic_concepts(unit)
        source_subjects = task_subjects(unit) | source_owners
        shared_frames = _valid_frames(positive, unit, context, source_owners)
        if query_frames and not _frame_compatible(positive, unit, context, source_owners):
            continue
        if not _local_predicate_compatible(positive, query_subjects, unit, source_subjects, shared_frames, context,
                                          comparison_navigation, requested_operations=requested_operations):
            continue
        # 一个具体领域不能借同句“返回/状态”等词回答另一个领域的自然任务。
        if (not _domain_compatible(positive, query_subjects, unit, source_subjects, shared_frames) and
                not requested_symbols & _precise_symbols(unit)):
            continue
        # 初读展示依赖同句的初值消费者或复制数据提供方；普通监听不能补足这条关系。
        if ('display' in query_subjects and 'initial_read' in query_concepts
                and not shared_frames - {'current_observation'}):
            inherited_view = source_owners if not named_owners else set()
            if ('initial_read' not in source_concepts or
                    not (task_subjects(unit) | inherited_view) & {'display', 'replicated_view'}):
                continue
        concerns = query_concepts & source_concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS
        operations = requested_operations & unit_operations
        concerns, operations = _frame_credit(concerns, operations, query_frames, shared_frames)
        named = requested_symbols & _precise_symbols(unit)
        directive = bool(kinds & {'REC', 'EI'} and _DIRECTIVE.search(unit))
        topic_advice = directive and bool(query_concepts & source_concepts & _TASK_NOUNS)
        unit_support = strict_task_support(positive, unit, context)
        locally_supported = bool(unit_support.get('whole_atom_delivery_allowed'))
        if locally_supported:
            concerns |= set(unit_support.get('mechanism_hits', []))
        # 相关内容与 owner 必须在同一原句，不能借另一句的无关主体补票。
        content_anchor = bool(locally_supported or shared_frames or len(literal) >= 2
                              or concerns and (literal or operations)
                              or named and directive or topic_advice and literal)
        if not content_anchor:
            continue
        factual = bool(kinds == {'NSF'} and (unit_support.get('concrete_behavior') or
            shared_frames & {'operation_order', 'mechanism_distinction',
                             'observer_registration_identity', 'registration_state',
                             'declared_initial_value'} or
            'result_contract' in shared_frames and result_source_relations(unit) or
            'input_request_dispatch' in shared_frames and result_request_dispatch(unit)))
        if directive or factual:
            matches.append((literal, named, concerns, operations, unit, shared_frames))
    if not matches:
        return original
    literal, named, concerns, operations, unit, frames = max(matches, key=lambda row: len(row[0]) + len(row[2]) + len(row[5]))
    result = copy.deepcopy(result)
    result.update({'supported': True, 'whole_atom_delivery_allowed': True,
        'support_meaning': 'TASK_RELEVANCE_ONLY', 'query_assertion_verified': False,
        'relevance_lane': 'ORIGINAL_CONTENT', 'method_contract_verified': False,
        'relevance_original_pointer': context['record_pointer'],
        'relevance_source_unit': unit,
        'relevance_content_anchors': sorted(literal | named),
        'relevance_shared_concerns': sorted(concerns | operations | frames),
        'relevance_relation_frames': sorted(frames),
        'supported_task_units': [row['text'] for row in requests],
        'mechanism_hits': sorted(concerns | operations | frames),
        'lexical_hits': sorted(literal)})
    return result


def _legacy_content_support(query, statement, context, requests, original):
    """Select existing engineering prose without promoting its Legacy evidence."""
    kind = context.get('atom_kind', '')
    if not kind.startswith('LEGACY_') or not context.get('record_pointer'):
        return None
    if kind in ('LEGACY_PLAYBOOK', 'LEGACY_DECISION'):
        # Questions, navigation steps and decision prompts describe a process;
        # their vocabulary is not an assertion about the system being reviewed.
        if (engineering_relations(query, source=False) and not re.search(
                r'\b(?:playbook|protocol|process|workflow|steps?|decision\s+tree)\b|流程|决策树|步骤', query, re.I)):
            return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                    'supported_task_units': [], 'legacy_navigation_not_mechanism': True}
        return None
    if (original.get('excluded_source_scope') or original.get('whole_atom_excluded_relation_owners')
            or any(row.get('ambiguous_owner_reference') for row in requests)):
        return None
    text = _prose(statement)
    if not text.strip() or SOURCE_METADATA_LABEL.search(text) or _LABEL_ONLY.search(text):
        return None
    scope = query_scope(query)
    identity = context.get('original_record_identity', {})
    scoped_ids = structured_record_ids(_prose(context.get('scope', '')))
    original_ids = {value for value in scoped_ids if not any(
        other.startswith(value + '-') for other in scoped_ids)}
    original_ids |= {value.upper() for value in [identity.get('id'), *identity.get('case_ids', []),
                                                *identity.get('corrected_claim_ids', [])]
                     if isinstance(value, str)}
    references = set(scope.get('record_references', []))
    if any(re.search(r'\d', value) for value in references) and not references & original_ids:
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'legacy_record_identity_mismatch': True}
    source_frames = engineering_relations(text, source=True)
    if kind not in ('LEGACY_CASE', 'LEGACY_CORRECTION'):
        source_frames = source_frames - {'record_evidence_limit'}
    if not source_frames:
        return None
    matches = []
    for request in requests:
        positive = request['effective_text']
        shared = engineering_relations(positive, source=False) & source_frames
        if not shared:
            continue
        requested_owners = _explicit_task_owners(positive)
        source_owners = _explicit_task_owners(text)
        if requested_owners and source_owners and not requested_owners & source_owners:
            continue
        # A generic allocation/registry concern is independent of a crafting
        # scenario. An explicitly named foreign component remains a boundary.
        if (requested_owners and not source_owners and requested_owners - {'world', 'container', 'builder'}
                and shared & {'resource_budget_identity', 'query_commitment_boundary',
                              'registry_state_ownership', 'registry_index_boundary'}):
            continue
        matches.append((request, shared))
    if not matches:
        return None
    frames = set().union(*(shared for _, shared in matches))
    result = copy.deepcopy(original)
    result.update(supported=True, whole_atom_delivery_allowed=True,
                  support_meaning='TASK_RELEVANCE_ONLY', query_assertion_verified=False,
                  relevance_lane='ORIGINAL_CONTENT', method_contract_verified=False,
                  legacy_evidence_not_promoted=True, relevance_original_pointer=context['record_pointer'],
                  relevance_source_unit=text, relevance_relation_frames=sorted(frames),
                  mechanism_hits=sorted(frames), lexical_hits=sorted(content_tokens(text) & content_tokens(query)),
                  subject_hits=sorted(task_subjects(text) & task_subjects(query)),
                  subject_mismatch=False,
                  supported_task_units=[row['text'] for row, _ in matches])
    return result


@analyzed_request
def task_support(query, statement, context='', request_frames=None):
    """Each independently requested relation earns only its own coverage credit."""
    requests = task_requests(query) if request_frames is None else request_frames
    return _support_for_frames(query, statement, context, requests)


@memoized_support
def _support_for_frames(query, statement, context, requests):
    """Pure original-atom relevance; record/source/projection guards are outside.

    Resolve omitted request frames before building the key, so ranking and
    projection share the same actual complete frame content. The full context,
    original statement and all role/source/Scope fields remain key inputs.
    """
    focus = positive_focus_support(query, statement, context)
    if not focus['allowed']:
        original = strict_task_support(query, statement, context, _request_frames=requests)
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'positive_focus_allowed': False,
                'positive_focus_reason': focus['reason']}
    if isinstance(context, dict) and context.get('atom_kind', '').startswith('LEGACY_'):
        original = strict_task_support(query, statement, context, _request_frames=requests)
        legacy = _legacy_content_support(query, statement, context, requests, original)
        if legacy is not None:
            return legacy
    if not isinstance(context, dict) or not context.get('original_content_index'):
        return strict_task_support(query, statement, context, _request_frames=requests)
    route = input_route_stage_witness(statement)
    if route is not None and _bounded_route_excluded(query, statement, route):
        original = strict_task_support(query, statement, context, _request_frames=requests)
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'supported_task_units': [], 'bounded_route_stage_excluded': True}
    excluded = _excluded_original_owners(query, statement, context)
    if excluded:
        original = strict_task_support(query, statement, context, _request_frames=requests)
        return {**original, 'supported': False, 'whole_atom_delivery_allowed': False,
                'whole_atom_excluded_relation_owners': sorted(excluded | set(original.get('whole_atom_excluded_relation_owners', []))),
                'supported_task_units': []}
    if len(requests) <= 1:
        return _single_request_support(query, statement, context,
            request_frame=requests[0] if requests else None)
    original = strict_task_support(query, statement, context, _request_frames=requests)
    if (original.get('excluded_source_scope') or original.get('whole_atom_excluded_relation_owners')
            or any(row.get('ambiguous_owner_reference') for row in requests)):
        return original
    matches = []
    for row in requests:
        # 保留原排除和主体框架；背景机制不随主体绑定进入这个子问。
        support = _single_request_support(query, statement, context, request_frame=row)
        if support.get('whole_atom_delivery_allowed'):
            matches.append((row['text'], support))
    if not matches:
        return _single_request_support(query, statement, context) if not requests else {
            **original, 'supported': False, 'whole_atom_delivery_allowed': False, 'supported_task_units': []}
    result = copy.deepcopy(max(matches, key=lambda pair: (len(pair[1].get('mechanism_hits', [])),
                               len(pair[1].get('subject_hits', []))))[1])
    result['supported_task_units'] = list(dict.fromkeys(row for row, _ in matches))
    return result

"""Conservative outcome-aware ordering of already-admitted whole L1 cards.

Witnesses describe ordering evidence in delivered original statements. They do
not verify an answer, expand admission, or establish runtime completion.
"""
import re

from .delivery_wire import (PROFILE as WIRE_PROFILE, PUBLIC_PROFILE as WIRE_PUBLIC_PROFILE,
                            SCHEMA as WIRE_SCHEMA, expand_l1_metadata)
from .intent_scope import (_precise_symbols, _explicit_task_owners, _business_component_names,
                           focused_task_query, query_scope)
from .relevance_frames import _data_quote_view


_PROJECTION_SCHEMA = 'dst-coding-projection/2.13'
_KINDS = frozenset(('NSF', 'REC', 'EI'))
_BUSINESS_BASES = frozenset(('authoritative_business_basis',
                           'feature_completion_criterion'))


def _pattern(value):
    return re.compile(value, re.I | re.ASCII)


_REQUEST_HEAD = _pattern(r'^\s*(?:(?:please|only|help\s+me)\s+)*'
    r'(?:how|what|can|could|identify|recognize|recognise|determine|confirm|verify|judge|tell|explain)\b'
    r'|^\s*(?:请|帮我|只|仅)*(?:如何|怎么|怎样|识别|确认|判断|判定|核验|核对|验证)')
_ASSERTION_PREFIX = _pattern(r'^\s*(?:(?:therefore|thus|consequently|must|should|the)\b\s*'
    r'|(?:因此|所以|必须|应该|应当|需要|应|需|建议|推荐)\s*)*')
_REQUEST = _pattern(r'\b(?:identify|recognize|recognise|determine|confirm|verify|judge|'
                    r'(?:how\s+(?:can|do|does|to)[^.;!?]{0,24})?(?:tell|know))\b'
                    r'|识别|确认|判断|判定|核验|核对|验证|(?:如何|怎么|怎样)知道')
_OUTCOME = _pattern(r'\b(?:actual|real|final|business|authoritative)\s+'
                    r'(?:(?:business|action)\s+)?(?:outcome|result|success|completion)\b'
                    r'|\bbusiness\s+(?:(?:has|is|was)\s+)?(?:really\s+)?completed\b'
                    r'|(?:实际|真正|最终|业务|权威)(?:业务)?(?:结果|成功|完成)'
                    r'|业务(?:是否)?(?:真正|实际|已经|已)?(?:成功|完成)')
_QUERY_NEGATIVE = _pattern(r'\b(?:not|never|no|without|exclude\w*|ignore\w*|neither)\b'
                           r'|不要|不问|不用|不需要|无需|排除|别(?:问|判断|确认|识别)')
_PREVIEW_ONLY = _pattern(r'\bonly\b[^.;!?]{0,45}\b(?:preview|dispatch|request\s+dispatch)\b'
                         r'|(?:只|仅)(?:问|解释|审查|分析)[^。；;！？]{0,30}(?:preview|预演|分发)')
_EXACT_CALL = re.compile(r'\b[A-Za-z_]\w*\s*\(')
_BACKGROUND = _pattern(r'^\s*(?:background\s*:|背景\s*[:：])')
_REPORTED = _pattern(r'\b(?:(?:the|an?)\s+)?(?:author|reviewer|review|note|comment|proposal|hypothesis)\s+'
                     r'(?:says?|claims?|assumes?|expects?|asks?)\b|作者(?:说|声称|认为|假定)|声称|假定')
_REQUEST_HYPOTHETICAL = _pattern(r'\b(?:if|unless|when|assuming|suppose)\b|如果|假如|假设|若')
_SENTENCE_END = re.compile(r'[。！？!?\n]+|\.(?=\s|$)')
_CLAUSE_END = re.compile(r'[；;,，]')
_CONDITIONAL = _pattern(r'\b(?:if|unless|when|would|could|might|may|suppose|assuming|hypothetical|whether)\b'
                        r'|如果|假如|假设|若|可能|也许|是否|能否')
_NEGATIVE = _pattern(r'\b(?:not|never|no|cannot|without|neither|false|incorrect)\b|不|未|禁止|不得')
_META = _pattern(r'^\s*(?:(?:the|a|an)\s+)?(?:label|title|name|identifier|string|literal|'
                 r'example\s+sentence|quoted\s+(?:text|sentence)|wording|metadata)\b'
                 r'|^\s*(?:标题|标签|名称|名字|字面量|字符串|元数据|示例句)\s*[:：]?')

_AUTH_EN = (r'(?:(?:the|a|an|its)\s+)?(?:readable|observable)\s+'
            r'(?:authoritative|server[- ]owned)\s+(?:business\s+)?(?:state|result|outcome)\b')
_AUTH_ZH = (r'(?:(?:该|本|此|具体|对应|实际|选定|所选)?\s*(?:业务|功能)(?:的)?\s*)?'
            r'(?:可读|可观察)(?:的)?\s*(?:权威|服务器权威|服务端权威)(?:的)?\s*(?:业务)?(?:结果|状态)')
_BUSINESS_EN = r'(?:UI\s+success|business\s+(?:success|completion|outcome)|(?:actual|final)\s+business\s+(?:result|outcome))'
_BUSINESS_ZH = r'(?:UI\s*(?:成功|完成)|(?:实际|最终)?业务(?:成功|完成|结果)|实际结果)'
_AUTH_BASIS = tuple(_pattern(p) for p in (
    _BUSINESS_EN + r'\s+(?:depends?\s+on|is\s+based\s+on|is\s+(?:determined|judged|confirmed)\s+(?:by|from))\s+' + _AUTH_EN,
    r'\b(?:determine|judge|confirm|identify|(?:the\s+)?UI\s+(?:determines|judges|confirms))\s+(?:the\s+)?' + _BUSINESS_EN + r'\s+(?:from|using|based\s+on)\s+' + _AUTH_EN,
    _BUSINESS_ZH + r'\s*(?:依(?:据|赖)?|取决于|根据|基于|由)\s*' + _AUTH_ZH,
    r'(?:根据|依据|基于)\s*' + _AUTH_ZH + r'\s*(?:来)?(?:判断|判定|确认|识别)\s*' + _BUSINESS_ZH,
))
_CRITERION_EN = (r'(?:(?:the\s+)?(?:selected|chosen|specific|this)\s+feature\s*\'?s?\s+'
                 r'explicit\s+completion\s+(?:criteria|criterion|conditions?)'
                 r'|explicit\s+feature\s+completion\s+(?:criteria|criterion|conditions?))\b')
_FEATURE_CRITERION = tuple(_pattern(p) for p in (
    r'\b(?:interpret|explain|judge|determine)\s+(?:the\s+)?(?:UI|business\s+(?:success|completion))\s+'
    r'(?:according\s+to|using|based\s+on)\s+' + _CRITERION_EN,
    r'\b(?:judge|determine|confirm)\s+feature\s+completion\s+(?:according\s+to|using|based\s+on)\s+'
    r'its\s+explicit\s+completion\s+(?:criteria|criterion|conditions?)\b',
    r'(?:根据|按照|依据|基于)\s*(?:选定|所选|具体|该|对应)?\s*(?:feature|功能|特性)\s*的?\s*'
    r'(?:明确|显式|具体)(?:的)?\s*(?:完成|成功)(?:条件|标准)\s*(?:来)?\s*'
    r'(?:判断|解释|判定|确认)\s*(?:UI|界面|业务(?:成功|完成)|该功能(?:的)?(?:完成|结果))',
))
_RETURN_CONSUMPTION = tuple(_pattern(p) for p in (
    r'\b(?:the\s+)?(?:action|action\.fn|action\s+function)\s+returns?\s+success'
    r'(?:\s*(?:,|and)\s*reason)?\s*[;；,，]\s*(?:the\s+)?(?:caller|calling\s+code)\s+'
    r'(?:consumes?|uses?)\s+(?:the\s+)?(?:returned\s+)?success\s+to\s+(?:choose|select|invoke|dispatch)\s+'
    r'(?:Succeed\s+or\s+Fail|(?:the\s+)?success\s+or\s+failure\s+callbacks?)\b',
    r'(?:动作|动作执行函数)\s*返回\s*success\s*(?:(?:和|与|、)\s*reason)?\s*[;；,，]\s*'
    r'(?:调用方|调用者)\s*(?:根据|消费|使用)\s*success\s*(?:来)?\s*(?:选择|调用|分发)\s*'
    r'(?:成功或失败回调|Succeed\s*(?:或|/)\s*Fail)',
))

_ROUTE_INPUT = _pattern(r'\b(?:input|click|controller)\b[^.;!?]{0,70}\brequests?\b'
    r'|\brequests?\b[^.;!?]{0,40}\b(?:input|click|controller)\b'
    r'|(?:输入|点击|控制器)[^。！？]{0,25}请求')
_ROUTE_MOVE = _pattern(r'\b(?:reach(?:es)?|send\w*|deliver\w*|rout\w*)\b|到达|送到|发送|送达|路由')
_ROUTE_DESTINATION = _pattern(r'\b(?:authoritative|server[- ]owned|server)\b[^.;!?]{0,35}'
    r'\b(?:effects?|execution|gameplay|mutation)\b|(?:权威|服务器|服务端)[^。！？]{0,15}(?:效果|执行|业务|状态)')
_RPC_SEND = _pattern(r'^\s*(?:[A-Za-z_]\w*(?:[.:]\w+)?|the\s+client|client)\s+'
    r'(?:sends?\s+|发送\s*)RPC\.(?P<route>[A-Za-z_]\w*)\b')
_AUTHORITY_HANDLER = _pattern(r'^\s*OnRemote(?P<route>[A-Za-z_]\w*)\s+'
    r'(?:requires?\s+|要求\s*)mastersim\b')
_HANDLER_FORWARD = _pattern(r'\b(?:and|then)\s+(?:it\s+)?(?:push(?:es)?|calls?|invokes?)\b'
    r'|[,;]\s*(?:then\s+)?(?:push(?:es)?|calls?|invokes?)\b'
    r'|(?:后|再|并|才|，|；)\s*(?:调用|推入|推送)')
_CALL_ACTION = _pattern(r'^\s*(?:(?:the\s+)?(?:method|caller)|[A-Za-z_]\w*(?::\w+)?)\s+'
    r'(?:calls?|invokes?)\s+action\.fn\b'
    r'|^\s*(?:(?:只有)?通过[^。！？；;，,]{1,45}后才|[A-Za-z_]\w*(?::\w+)?\s*)?调用\s*action\.fn\b')
_CONSUME_ACTION = _pattern(r'(?:^|[;,]\s*|\band\s+)(?:(?:the\s+)?(?:caller|method)|it)\s+'
    r'(?:consumes?|uses?)\s+(?:the\s+)?(?:returned\s+)?success\s+to\s+'
    r'(?:choose|select|invoke|dispatch)\s+(?:Succeed\s+or\s+Fail|success\s+or\s+failure\s+callbacks?)\b'
    r'|(?:^|[,，;；]\s*)(?:按|根据|使用|消费)\s*(?:返回的\s*)?success\s*(?:来)?\s*'
    r'(?:调用|选择|分发)\s*Succeed\s*(?:或|/)\s*Fail\b')


def _unquoted(value):
    return _data_quote_view(value)


def _requests_outcome(query):
    if not isinstance(query, str):
        return False
    focused = focused_task_query(query)
    scope = query_scope(focused)
    if scope['negative_clauses'] or scope['guard_clauses']:
        return False
    value = _unquoted(scope['positive_user_query'])
    if (_QUERY_NEGATIVE.search(value) or _PREVIEW_ONLY.search(value)
            or _precise_symbols(value) or _EXACT_CALL.search(value)
            or _explicit_task_owners(value) or _business_component_names(value)):
        return False
    # 请求动作与结果对象必须位于同一原文句子，不能从背景拼出新请求。
    return any(_REQUEST_HEAD.search(unit) and _REQUEST.search(unit) and _OUTCOME.search(unit)
               and not any(pattern.search(unit) for pattern in
                           (_META, _BACKGROUND, _REPORTED, _REQUEST_HYPOTHETICAL))
               for unit in _SENTENCE_END.split(value))


def _validate_schemas(card):
    if (not isinstance(card, dict) or card.get('projection_schema') != _PROJECTION_SCHEMA
            or type(card.get('level')) is not int or card['level'] != 1):
        raise ValueError('Unsupported whole-card projection')
    wire = card.get('wire_projection')
    if wire is not None and (not isinstance(wire, dict) or wire.get('schema') != WIRE_SCHEMA
            or wire.get('profile') not in (WIRE_PROFILE, WIRE_PUBLIC_PROFILE)):
        raise ValueError('Unsupported whole-card wire')
    scope = card.get('source_scope')
    if (isinstance(scope, dict) and 'scope_schema' in scope
            and scope['scope_schema'] != 'dst-semantic-scope/2.13'):
        raise ValueError('Unsupported whole-card scope')
    children = card.get('companion_context', [])
    if not isinstance(children, list):
        raise ValueError('Invalid whole-card companions')
    for child in children:
        _validate_schemas(child)


def _decoded(card):
    _validate_schemas(card)
    result = expand_l1_metadata(card)
    if (not isinstance(result.get('decision'), list)
            or any(not isinstance(atom, dict) for atom in result['decision'])):
        raise ValueError('Invalid whole-card decisions')
    return result


def _scope_permits(decoded):
    scope = decoded.get('source_scope', {})
    if not isinstance(scope, dict):
        return False
    if (scope.get('identified_selected_atom_scope_missing_count', 0) != 0
            or scope.get('identified_necessary_scope_dependencies_complete') is False
            or scope.get('delivered_node_values_complete') is False):
        return False
    # 潜在但尚未归属的缺口仍是未知；不会在排序时改写为 Scope 完整。
    missing = scope.get('needed_scope_missing', [])
    if not isinstance(missing, list):
        return False
    return not any(not isinstance(item, dict)
                   or item.get('current_atom_necessity_verified') is True for item in missing)


def _sentences(value):
    start = 0
    for match in _SENTENCE_END.finditer(value):
        yield start, value[start:match.start()], match.group()
        start = match.end()
    if start < len(value):
        yield start, value[start:], ''


def _witnesses(query, decoded):
    if not _requests_outcome(query) or not _scope_permits(decoded):
        return []
    result = []
    for atom in decoded['decision']:
        kind, pointer, statement = (atom.get(name) for name in ('kind', 'record_pointer', 'statement'))
        if (kind not in _KINDS or not isinstance(pointer, str) or not pointer.startswith('/')
                or not isinstance(statement, str) or not statement.strip()):
            continue
        visible = _unquoted(statement)
        for offset, sentence, ending in _sentences(visible):
            if (_CONDITIONAL.search(sentence) or _META.search(sentence)
                    or '?' in ending or '？' in ending):
                continue
            for match in _RETURN_CONSUMPTION:
                found = match.match(sentence, len(sentence) - len(sentence.lstrip()))
                if found and not _NEGATIVE.search(sentence):
                    result.append(_witness(atom, 'action_return_consumption',
                                           offset + found.start(), offset + found.end()))
                    break
            start = 0
            for end in [m.start() for m in _CLAUSE_END.finditer(sentence)] + [len(sentence)]:
                clause = sentence[start:end]
                if not (_NEGATIVE.search(clause) or _META.search(clause)):
                    for relation, patterns in (('authoritative_business_basis', _AUTH_BASIS),
                                               ('feature_completion_criterion', _FEATURE_CRITERION)):
                        asserted = clause[_ASSERTION_PREFIX.match(clause).end():]
                        if any(pattern.match(asserted) for pattern in patterns):
                            left = len(clause) - len(clause.lstrip())
                            right = len(clause.rstrip())
                            result.append(_witness(atom, relation, offset + start + left,
                                                   offset + start + right))
                start = end + 1
    return result


def _witness(atom, relation, start, end):
    statement = atom['statement']
    return {'relation': relation, 'kind': atom['kind'],
            'record_pointer': atom['record_pointer'], 'statement': statement,
            'clause': statement[start:end], 'statement_span': [start, end],
            'answer_truth_verified': False,
            'meaning': 'WHOLE_CARD_ORDER_ONLY_NOT_RUNTIME_OR_COMPLETION_PROOF'}


def outcome_priority_witnesses(query, card):
    """Return card-local original decision evidence, conservatively on failure."""
    try:
        return _witnesses(query, _decoded(card))
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        return []


def _requests_authoritative_route(query):
    if not _requests_outcome(query):
        return False
    value = _unquoted(query_scope(focused_task_query(query))['positive_user_query'])
    return any(_REQUEST_HEAD.search(unit) and _ROUTE_INPUT.search(unit)
               and _ROUTE_MOVE.search(unit) and _ROUTE_DESTINATION.search(unit)
               and not any(pattern.search(unit) for pattern in
                           (_META, _BACKGROUND, _REPORTED, _REQUEST_HYPOTHETICAL))
               for unit in _SENTENCE_END.split(value))


def _coverage_scope_known(decoded):
    scope = decoded.get('source_scope')
    if not isinstance(scope, dict) or not _scope_permits(decoded):
        return False
    nodes = scope.get('nodes')
    if 'scope_schema' in scope:
        if (scope['scope_schema'] != 'dst-semantic-scope/2.13' or not isinstance(nodes, dict)
                or type(scope.get('identified_selected_atom_scope_missing_count')) is not int
                or scope.get('identified_necessary_scope_dependencies_complete') is not True
                or scope.get('delivered_node_values_complete') is not True):
            return False
        nodes = list(nodes.values())
    if isinstance(nodes, list):
        return all(isinstance(node, dict) and isinstance(node.get('role'), str)
                   and ('value' in node or 'value_ref' in node) for node in nodes)
    # Older bounded native cards carry their full, explicitly named Scope map.
    return (all(isinstance(scope.get(name), str) for name in
                ('snapshot_id', 'version', 'sides', 'runtime_environments'))
            and isinstance(scope.get('exclusions'), list))


def _obligation_witness(atom, decoded, relation, start, end):
    return {**_witness(atom, relation, start, end), 'obligation': relation,
            'record_sha256': decoded.get('record_sha256')}


def _whole_task_witnesses(query, decoded):
    result = []
    for witness in _witnesses(query, decoded):
        if witness['relation'] in _BUSINESS_BASES:
            result.append({**witness, 'obligation': 'business_result_basis',
                           'record_sha256': decoded.get('record_sha256')})
    for atom in decoded['decision']:
        pointer, statement = atom.get('record_pointer'), atom.get('statement')
        if (atom.get('kind') != 'NSF' or not isinstance(pointer, str) or not pointer.startswith('/')
                or not isinstance(statement, str) or not statement.strip()):
            continue
        visible = _unquoted(statement)
        sent, handlers = {}, {}
        for offset, sentence, ending in _sentences(visible):
            if (any(pattern.search(sentence) for pattern in (_META, _REPORTED, _CONDITIONAL))
                    or '?' in ending or '？' in ending):
                continue
            sender = _RPC_SEND.match(sentence)
            if sender:
                sent.setdefault(sender['route'].casefold(), (offset, offset + len(sentence)))
            handler = _AUTHORITY_HANDLER.match(sentence)
            if handler and _HANDLER_FORWARD.search(sentence[handler.end():]):
                handlers.setdefault(handler['route'].casefold(), (offset, offset + len(sentence)))
            if _NEGATIVE.search(sentence):
                continue
            consumed = any(pattern.match(sentence, len(sentence) - len(sentence.lstrip()))
                           for pattern in _RETURN_CONSUMPTION)
            if consumed or (_CALL_ACTION.match(sentence) and _CONSUME_ACTION.search(sentence)):
                result.append(_obligation_witness(atom, decoded, 'native_action_result_consumption',
                                                 offset, offset + len(sentence)))
        for route in sent.keys() & handlers.keys():
            left = min(sent[route][0], handlers[route][0])
            right = max(sent[route][1], handlers[route][1])
            result.append(_obligation_witness(atom, decoded, 'authoritative_request_handoff', left, right))
    return result


def whole_task_priority_witnesses(query, card):
    """Trace bounded original evidence for ordering, never task completion."""
    if not _requests_authoritative_route(query):
        return []
    try:
        decoded = _decoded(card)
        return _whole_task_witnesses(query, decoded) if _coverage_scope_known(decoded) else []
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        return []


def _stable_superset_order(cards, witnesses):
    obligations = [frozenset(row['obligation'] for row in rows) for rows in witnesses]
    remaining, ordered = list(range(len(cards))), []
    while remaining:
        selected = next(index for index in remaining
                        if not any(obligations[other] > obligations[index] for other in remaining))
        ordered.append(cards[selected])
        remaining.remove(selected)
    return ordered


def prioritize_whole_cards(query, cards):
    """Return the same card objects, stably prioritizing explicit business bases.

    Action-return consumption remains traceable but cannot alone promote a card
    as the basis of actual business completion. A decode failure preserves the
    original order of the entire list.
    """
    original = list(cards)
    if not _requests_outcome(query):
        return original
    if _requests_authoritative_route(query):
        try:
            decoded = [_decoded(card) for card in original]
            if not all(_coverage_scope_known(card) for card in decoded):
                return original
            return _stable_superset_order(original, [_whole_task_witnesses(query, card) for card in decoded])
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
            return original
    try:
        witnesses = [_witnesses(query, _decoded(card)) for card in original]
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        return original
    preferred = [any(w['relation'] in _BUSINESS_BASES for w in rows) for rows in witnesses]
    return ([card for card, priority in zip(original, preferred) if priority]
            + [card for card, priority in zip(original, preferred) if not priority])


def requested_method_identity_match(query, context):
    """An explicit requested name may order its original method-subject unit.

    A caller's callee occurrence and a constant namespace cannot supply this
    witness. It only orders an atom that has already passed task admission.
    """
    if not isinstance(context, dict):
        return False
    visible = _data_quote_view(query_scope(focused_task_query(query))['positive_user_query'])
    bound = {row.get('symbol') for row in context.get('role_bindings', [])
             if row.get('role') == 'METHOD_SUBJECT' and isinstance(row.get('symbol'), str)}
    original = set(context.get('original_content_index', {}).get('original_method_subjects', {}).get(
        context.get('record_pointer'), []))
    qualified = {name for name in bound | original if ':' in name or '.' in name}
    leaves = {re.split(r'[.:]', name)[-1] for name in qualified}
    owners = {re.split(r'[.:]', name)[0] for name in qualified}
    # A receiver/namespace token emitted beside its methods is not itself a
    # requested method. Bare method subjects retain their original-head or
    # qualified method witness; a caller/callee mention cannot supply one.
    names = qualified | {name for name in bound | original if
                         name not in owners and (name in original or name in leaves)}
    for name in names:
        parts = re.split(r'[.:]', name)
        if len(parts)==1 and len(context.get('receivers',[]))>1:
            continue
        if len(parts)>1 and parts[0].isupper() and parts[-1].isupper():
            continue
        choices = [name]
        method_owners={re.split(r'[.:]',other)[0] for other in qualified
                       if re.split(r'[.:]',other)[-1]==parts[-1]}
        if len(method_owners)<=1:
            choices.append(parts[-1])
        if any(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(value) + r'(?![A-Za-z0-9_:]|\.[A-Za-z_])',
                         visible, re.I | re.ASCII) for value in choices):
            return True
    return False


def admitted_atom_unit_key(kind, payload_bytes, record_rank, atom_rank, requested_method=False):
    """Order already-admitted whole task units; cost is never relevance proof.

    Direct typed facts and original Legacy content precede inferred/advisory
    units. Within a layer prefer a smaller complete unit, with original stable
    order as tie-breaker. This cannot add an atom or relax admission or Scope.
    """
    kinds = {value.strip() for value in kind.split('/')} if isinstance(kind, str) else set()
    direct = bool(kinds & {'NSF', 'RV', 'PROJECT_POLICY'} or any(value.startswith('LEGACY_') for value in kinds))
    return (0 if direct else 1, 0 if requested_method else 1, payload_bytes, record_rank, atom_rank)

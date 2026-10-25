"""Explicit Reviewer relevance for original, unresolved project-policy atoms.

This lane proves a bounded consultation is relevant; it never chooses a policy
or establishes a native fact. All statements are retained as whole originals.
"""
import copy
import json
import re
from .intent_scope import query_scope, task_subjects

LANE = 'PROJECT_POLICY'
CONSULT = re.compile(r'列出|列举|审查|审计|比较|对比|澄清|梳理|说明|讨论|'
                     r'\b(?:list|review|audit|compare|clarify|discuss|explain|enumerate)\b', re.I)
POLICY_OBJECT = re.compile(r'项目.{0,18}(?:政策|选择|取舍|决策|解释)|设计(?:取舍|选择)|'
                          r'(?:尚未|未)(?:裁定|决定|选定|确定).{0,16}(?:选择|政策|解释|方案)|'
                          r'\b(?:project\s+(?:policy|policies|choices?|decisions?)|design\s+(?:choices?|tradeoffs?)|'
                          r'(?:undecided|unresolved|unselected)\s+(?:policy|policies|choices?|alternatives?|interpretations?))\b', re.I)
FACT_ONLY = re.compile(r'只(?:查|看|要|列出).{0,10}(?:原版|事实)|'
                       r'\bonly\s+(?:native\s+)?(?:facts?|source\s+facts?)\b', re.I)
CLAUSES = re.compile(r'[。；;!?！？\n，,]+')
SG = re.compile(r'\b(?:sg|stategraph|statemem|onexit)\b|状态图|入态', re.I)
BUFFER = re.compile(r'\b(?:buffer|bufferedaction|buffered\s+action)\b|动作缓存|缓冲', re.I)
ATTEMPT = re.compile(r'\b(?:attempts?|captured\s+(?:actions?|work))\b|本次(?:动作|尝试)|捕获.{0,12}动作', re.I)
CAPTURE = re.compile(r'\b(?:captur\w*|grab\w*|held|hold\w*|owns?|ownership)\b|捕获|抓住|持有|所属|归属', re.I)
REPLACE = re.compile(r'\breplac\w*\b|替换|更换', re.I)
INVALIDATE = re.compile(r'\b(?:invalidat\w*|cancel\w*|revok\w*)\b|失效|撤销|取消', re.I)
LIFETIME = re.compile(r'\b(?:exit|timeout|until|active|ownership|owns?)\b|退出|超时|直到|仍活动|持有|所属|归属', re.I)
RELATIONS = {
    'initial_read': re.compile(r'\b(?:initial\s+read|first\s+read|read\w*.{0,14}initial)\b|初读|初值|首次读取', re.I),
    'subscription_binding': re.compile(r'\b(?:bind|register|subscribe|detach)\w*.{0,24}(?:listener|event)|监听.{0,10}(?:绑定|登记|解绑)', re.I),
    'field_replacement': re.compile(r'\b(?:replace\w*|assign\w*|write\w*)\s+(?:the\s+)?(?:field|property)|(?:替换|赋值|写入).{0,8}(?:字段|属性)', re.I),
    'task_cancellation': re.compile(r'\bcancel\w*.{0,18}(?:task|handle)|(?:取消|清理).{0,8}(?:任务|句柄)', re.I),
}
PRECISE = re.compile(r'(?<![A-Za-z0-9_])[A-Za-z_]\w*[.:][A-Za-z_]\w*(?![A-Za-z0-9_])')
ALTERNATIVE = re.compile(r'\b[A-Z][A-Z0-9_]{2,}\b')


def _text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


def _subjects(value):
    text = _text(value)
    result = task_subjects(text) - {'return_contract', 'allocation', 'subscription', 'task'}
    if SG.search(text):
        result.add('stategraph')
    if BUFFER.search(text):
        result.add('action_buffer')
    if ATTEMPT.search(text):
        result.add('captured_attempt')
    result.update('symbol:' + symbol.lower() for symbol in PRECISE.findall(text))
    return result


def _relations(value):
    text = _text(value)
    result = {name for name, pattern in RELATIONS.items() if pattern.search(text)}
    # 关系必须由原主体与谓词共同建立，咨询“政策/选择”本身不是机制。
    if BUFFER.search(text) and REPLACE.search(text):
        result.add('buffer_replacement')
    if ATTEMPT.search(text) and INVALIDATE.search(text):
        result.add('captured_attempt_invalidation')
    if ATTEMPT.search(text) and CAPTURE.search(text) and LIFETIME.search(text):
        result.add('captured_attempt_ownership')
    return result


def project_policy_intent(query):
    scope = query_scope(query)
    positive = scope['positive_query']
    clauses = [value.strip() for value in CLAUSES.split(positive) if value.strip()]
    requests, concrete = [], []
    for index, value in enumerate(clauses):
        if not (CONSULT.search(value) and POLICY_OBJECT.search(value)):
            continue
        requests.append(value)
        if _subjects(value):
            # 明确咨询主体只能由本句建立关系；不能借前面的另一任务补齐。
            anchor = value if _unique_relation_owner(value) else None
        else:
            anchor = None
            for preceding in reversed(clauses[:index]):
                if not (_subjects(preceding) or _relations(preceding)):
                    continue
                # 最近候选本身不唯一时就停止，不越过它向更早的任务借主体。
                anchor = preceding if _unique_relation_owner(preceding) else None
                break
        if anchor and anchor not in concrete:
            concrete.append(anchor)
    excluded = scope['negative_clauses']
    policy_excluded = any(POLICY_OBJECT.search(value) or re.search(r'政策|\bpolic(?:y|ies)\b', value, re.I)
                          for value in excluded) or bool(FACT_ONLY.search(positive))
    return {'requested': bool(requests and concrete and not policy_excluded),
            'request_clause': requests[0] if requests else '',
            'concrete_task_clauses': concrete, 'exclusion_clauses': copy.deepcopy(excluded),
            'policy_excluded': policy_excluded, 'review_only': True,
            'query_assertion_verified': False}


def _unique_relation_owner(clause):
    subjects = _subjects(clause)
    precise = {value for value in subjects if value.startswith('symbol:')}
    owners = subjects - precise - {'action', 'action_buffer', 'captured_attempt'}
    if len(precise) > 1 or len(owners) > 1:
        return False
    if not owners:
        owners = precise or ({'captured_attempt'} if 'captured_attempt' in subjects else
                             {'action_buffer'} if 'action_buffer' in subjects else set())
    return bool(len(owners) == 1 and _relations(clause))


def project_policy_eligible(projection, query_intent, ordinary_admission, facet_admission=True):
    return bool(projection == 'reviewer' and query_intent.get('requested')
                and ordinary_admission is True and facet_admission is True)


def record_policy_admitted(record, family, governance, projection, query):
    """Additional pure-view guard; search has already run ordinary record gates."""
    if projection != 'reviewer' or (family == 'core' and not record.get('gate_a', {}).get('accepted')):
        return False
    exact = query.strip().lower() == record['id'].lower()
    if governance.get('retrieval_status') == 'restricted' and not exact:
        return False
    if governance.get('knowledge_status') == 'superseded' and not exact:
        return False
    if family == 'legacy' and record.get('status') in ('superseded', 'deprecated', 'retracted') and not exact:
        return False
    return True


def policy_units(record, family):
    from .projection_v2 import _atoms, _claim_contexts, record_digest
    atoms = [atom for atom in _atoms(record, family) if atom['kind'] == LANE]
    if not atoms:
        return []
    contexts = _claim_contexts(record, family, atoms)
    return [{'unit_lane': LANE, 'kind': LANE, 'original_kind': LANE,
             'original_text': copy.deepcopy(atom['statement']), 'record_pointer': atom['record_pointer'],
             'original_scope': copy.deepcopy(record.get('scope', record.get('scope_text', ''))),
             'context': contexts[atom['record_pointer']], 'record_sha256': record_digest(record)}
            for atom in atoms]


def policy_task_support(query, whole_policy, original_context, query_intent=None):
    intent = query_intent or project_policy_intent(query)
    text = _text(whole_policy)
    units = [value.strip() for value in CLAUSES.split(text) if value.strip()]
    excluded_subjects = set().union(*(_subjects(value) for value in intent['exclusion_clauses'])) if intent['exclusion_clauses'] else set()
    conflicts = set().union(*(_subjects(value) & excluded_subjects for value in units if _relations(value))) if units else set()
    context_kind = original_context.get('atom_kind') if isinstance(original_context, dict) else None
    original_policy = context_kind == LANE
    scope = original_context.get('scope', '') if isinstance(original_context, dict) else ''
    inherited = _subjects(scope)
    inherited = inherited if len(inherited) == 1 else set()
    matches = []
    for source in units:
        explicit = _subjects(source)
        subjects = explicit or inherited
        relations = _relations(source)
        for request in intent['concrete_task_clauses']:
            requested_subjects = _subjects(request)
            subject_hits = requested_subjects & subjects
            relation_hits = _relations(request) & relations
            precise = {value for value in requested_subjects if value.startswith('symbol:')}
            query_owners = requested_subjects - {'action', 'captured_attempt', 'action_buffer'}
            source_owners = subjects - {'action', 'captured_attempt', 'action_buffer'}
            mismatch = bool(not subject_hits or (query_owners and not query_owners & source_owners))
            mismatch |= bool(precise and not precise & subjects)
            # Buffer/attempt choices bind both ends; one shared domain word is insufficient.
            bounded_pair = requested_subjects & {'action_buffer', 'captured_attempt'}
            mismatch |= bool(bounded_pair and not bounded_pair <= subjects)
            alternatives = set(ALTERNATIVE.findall(request)) & set(ALTERNATIVE.findall(source))
            supported = bool(original_policy and intent['requested'] and not mismatch and relation_hits and not conflicts)
            matches.append({'supported': supported, 'subject_hits': sorted(subject_hits),
                            'relation_hits': sorted(relation_hits), 'mechanism_hits': sorted(relation_hits),
                            'matched_alternatives': sorted(alternatives), 'subject_mismatch': mismatch,
                            'source_subjects': sorted(subjects), 'requested_subjects': sorted(requested_subjects),
                            'source_policy_clause': source, 'task_unit': request})
    result = max(matches, key=lambda item: (item['supported'], not item['subject_mismatch'],
                                          bool(item['relation_hits']), len(item['subject_hits']))) if matches else {
        'supported': False, 'subject_hits': [], 'relation_hits': [], 'mechanism_hits': [],
        'matched_alternatives': [], 'subject_mismatch': bool(intent['concrete_task_clauses']),
        'source_subjects': [], 'requested_subjects': [], 'source_policy_clause': '', 'task_unit': ''}
    result.update({'support_meaning': 'POLICY_RELEVANCE_ONLY', 'unit_lane': LANE,
                   'whole_atom_delivery_allowed': result['supported'],
                   'explicit_policy_intent': intent['requested'], 'original_kind_verified': original_policy,
                   'excluded_source_scope': bool(conflicts), 'whole_atom_excluded_relation_owners': sorted(conflicts),
                   'policy_request_clause': intent['request_clause'], 'assertion_verified': False,
                   'query_assertion_verified': False, 'policy_resolved': False,
                   'matched_symbols': [], 'anchors': result['subject_hits'] + result['relation_hits']})
    return result


def select_project_policy_atoms(record, family, query, projection, admitted_atoms, governance=None):
    from .projection_v2 import _atoms, _claim_contexts
    intent = project_policy_intent(query)
    ordinary = record_policy_admitted(record, family, governance or {}, projection, query)
    if not project_policy_eligible(projection, intent, ordinary):
        return [], []
    originals = {atom['record_pointer']: atom for atom in _atoms(record, family) if atom['kind'] == LANE}
    values = [atom for atom in admitted_atoms if atom.get('record_pointer') in originals
              and atom.get('kind') == LANE and not atom.get('consumption_hint')
              and atom.get('statement') == originals[atom['record_pointer']]['statement']]
    contexts = _claim_contexts(record, family, values)
    selected, decisions = [], []
    for atom in values:
        support = policy_task_support(query, atom['statement'], contexts[atom['record_pointer']], intent)
        decisions.append({'record_pointer': atom['record_pointer'], 'kind': LANE,
                          'admitted': support['whole_atom_delivery_allowed'], 'support': support})
        if support['whole_atom_delivery_allowed']:
            selected.append(copy.deepcopy(atom))
    return selected, decisions


def policy_delivery_admission(record, family, item, query, projection, verified=None):
    from .projection_v2 import delivered_original_atoms
    from .facet_contracts import facet_admission
    if verified is None:
        verified, _ = delivered_original_atoms(record, family, item)
    values = [atom for atom in verified.values() if atom['kind'] == LANE]
    admitted, _ = facet_admission(record, family, values, query)
    selected, decisions = select_project_policy_atoms(record, family, query, projection, admitted, item.get('governance', {}))
    return {'supported_policy_record_pointers': [atom['record_pointer'] for atom in selected],
            'supported_policy_atom_count': len(selected), 'policy_support_meaning': 'POLICY_RELEVANCE_ONLY',
            'policy_resolved': False, 'policy_decisions': decisions,
            'project_policy_requested': project_policy_intent(query)['requested']}

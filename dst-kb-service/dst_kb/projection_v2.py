"""Pure, typed projections; admission and evidence resolution belong to the service."""
import copy
from . import developer_trace as dt
import json
import re
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from .facet_contracts import (facet_admission, requested_contracts, query_scope,
                              contract_symbols, contract_matches, normalize_symbol,
                              context_admission, bounded_source_context)
from .intent_scope import expand_semantic_query, task_subjects, DOMAIN_SUBJECTS
from .task_relevance import task_support, record_content_context
from .scope_projection import (semantic_scope as compact_semantic_scope, shared_scope_references,
                               compact_diagnostics, compact_task_diagnostics, scope_navigation,
                               scope_dependency_plan, SCHEMA as SCOPE_SCHEMA)
from .delivery_budget import atom_closure_units, ATOMIC_BUDGET_UNIT
from .source_context import context_payload
from .policy_context import select_project_policy_atoms, policy_delivery_admission, project_policy_intent
from .delivery_packaging import share_metadata
from .provider_context import provider_context_atoms
from .original_supplement_context import supplement_atoms
from .bounded_route_reference import bounded_input_route_reference
from .source_epoch_runtime import epoch_arguments

SCHEMA = 'dst-coding-projection/2.13'
FAMILIES = ('core', 'n001', 'legacy')
GOVERNANCE_FIELDS = ('knowledge_status', 'retrieval_status', 'coding_status')
HISTORY = 'HISTORICAL_PRODUCT_EVIDENCE'
PROFILE_PATH = Path(__file__).with_name('projection_profiles.json')
QUALIFIED = re.compile(r'(?<![A-Za-z0-9_])(?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Za-z_][A-Za-z0-9_]*[:.][A-Za-z_][A-Za-z0-9_]*(?:\([^\n()]{0,160}\))?')
BARE_API = re.compile(r'(?<![A-Za-z0-9_])([A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*)\s*(?=\()')
SYMBOL_TERM = re.compile(r'(?:[A-Za-z_][A-Za-z0-9_]*[:.])*[A-Za-z_][A-Za-z0-9_]*(?:\([^\n()]*\))?')
WRAPPER_BOUNDARY_PREFIXES = ('本轮只做', 'canonical 是', '建议、原创', 'NSF 仅指',
                             '固定公开 GitHub', 'source cache', '第三方静态审阅',
                             'Dot source commit', 'Coding Eval is historical',
                             'Recommendations apply only')
QUERY_WORD = re.compile(r'[A-Za-z_][A-Za-z0-9_]*(?:[:.][A-Za-z_][A-Za-z0-9_]*)*')
QUERY_HAN = re.compile(r'[\u3400-\u9fff]{2,}')
EN_STOP = frozenset('a an and are as at be can could does for from how if in is it of on or should that the this to use what when which with would'.split())
ZH_STOP = frozenset(('什么', '怎样', '如何', '可以', '是否', '调用', '处理', '默认', '这个',
                     '使用', '需要', '哪些', '何时', '怎么', '应该', '为了', '相关', '本次', '函数', '组件', '目标'))


def record_digest(record):
    """Fingerprint the unexpanded JSON value, independent of serialization whitespace."""
    value = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return sha256(value.encode('utf-8')).hexdigest()


def append_source_context(card, record, verified):
    """Append an independently verified lane; old method delivery is unchanged."""
    if card.get('id') != record.get('id') or card.get('record_sha256') != record_digest(record):
        raise ValueError('Source context does not match the projected record')
    return {**card, **context_payload(record, verified)}


@lru_cache(maxsize=1)
def _profiles():
    return json.loads(PROFILE_PATH.read_text(encoding='utf-8'))['profiles']


@lru_cache(maxsize=1)
def _profile_variants():
    return json.loads(PROFILE_PATH.read_text(encoding='utf-8')).get('record_variants', {})


def _profile(record, supplied):
    result = copy.deepcopy(_profiles().get(record['id'], {}) if supplied is None else supplied)
    if not isinstance(result, dict):
        raise ValueError('profile must be a dict or None')
    expected = result.get('record_sha256')
    if expected and record_digest(record) != expected:
        digest = record_digest(record)
        variant = (_profile_variants().get(record['id'], {}).get(digest)
                   if supplied is None else None)
        if not isinstance(variant, dict) or variant.get('record_sha256') != digest:
            raise ValueError('Projection profile does not match canonical record: ' + record['id'])
        result = copy.deepcopy(variant)
    return result


def _validate(record, family, governance):
    if family not in FAMILIES:
        raise ValueError('family must be core, n001 or legacy')
    if not isinstance(record, dict) or not isinstance(record.get('id'), str):
        raise ValueError('record must be an unexpanded canonical entry')
    if 'reviewer_expansion' in record:
        raise ValueError('Expanded evidence is not an input to projection')
    if not isinstance(governance, dict):
        raise ValueError('governance must be independent metadata')
    if governance.get('id', record['id']) != record['id']:
        raise ValueError('governance ID does not match record')


def _governance(record, governance):
    # 投影不从历史 wrapper 推导准入，更不能用 profile 覆盖 HOLD。
    return {'id': record['id'], **{key: copy.deepcopy(governance[key])
                                 for key in GOVERNANCE_FIELDS if key in governance}}


def _atom(kind, statement, pointer):
    return {'kind': kind, 'statement': copy.deepcopy(statement), 'record_pointer': pointer}


def _atoms(record, family):
    if family == 'core':
        return [_atom(claim['kind'], claim['statement'], f'/claims/{index}')
                for index, claim in enumerate(record.get('claims', []))]
    if family == 'n001':
        result = []
        fact = record.get('native_fact', {})
        if 'statement' in fact:
            result.append(_atom(fact.get('claim_type', 'UNK'), fact['statement'], '/native_fact'))
        for field, subfield in (('ai_coding_impact', 'decisions'), ('recommended_reasoning', 'steps')):
            data = record.get(field, {})
            for index, statement in enumerate(data.get(subfield, [])):
                result.append(_atom(data.get('claim_type', 'REC'), statement, f'/{field}/{subfield}/{index}'))
        return result
    # 旧条目没有 Native claim typing，保留 LEGACY 类型，不擅自升级为 NSF/RV。
    details = record.get('details', {})
    legacy_kind = 'LEGACY_' + record.get('entry_type', 'knowledge').upper()
    # When the original statement is also used as its summary, retain the
    # semantic field's exact pointer instead of substituting a navigation copy.
    result = ([] if 'statement' in details and details['statement'] == record.get('summary') else
              [_atom(legacy_kind, record.get('summary', ''), '/summary')])
    semantic_fields = ('api_mechanism', 'observed_behaviour', 'statement', 'why',
                       'applies_when', 'failure_if_violated', 'symptoms',
                       'why_it_happens', 'why_it_is_dangerous', 'detection',
                       'safer_alternatives', 'steps', 'question', 'branches',
                       'recommended_direction', 'exceptions', 'problem', 'context',
                       'core_idea', 'structure', 'state_ownership', 'authority',
                       'lifecycle', 'networking', 'persistence', 'performance',
                       'costs', 'use_when', 'avoid_when', 'implementation_notes',
                       'preconditions', 'expected_correctness', 'limits', 'purpose',
                       'setup', 'action', 'expected_invariant', 'failure_signal',
                       'applicability', 'replacement', 'correction_scope',
                       'retrieval_policy', 'stop_conditions', 'architecture_summary', 'observations',
                       'runtime_tested', 'dedicated_tested', 'counter_evidence', 'subsequent_evidence',
                       'result', 'history_policy', 'previous_claim')
    for key in semantic_fields:
        if key in details:
            # These original fields enumerate independent original objects.
            # Preserve each complete element (including its own metadata), not
            # a selected sentence or an unrelated mixed-topic parent array.
            value = details[key]
            enumerated = key in ('architecture_summary', 'observations',
                                 'counter_evidence', 'subsequent_evidence') and isinstance(value, list)
            values = list(enumerate(value)) if enumerated else [(None, value)]
            for index, original in values:
                pointer = '/details/' + key + ('/' + str(index) if index is not None else '')
                atom = _atom(legacy_kind, original, pointer)
                if key in ('runtime_tested', 'dedicated_tested'):
                    atom['legacy_evidence_status'] = True
                result.append(atom)
    if 'status' in record:
        result.append({**_atom(legacy_kind, record['status'], '/status'), 'legacy_evidence_status': True})
    for key in ('implication', 'recommendation', 'recommended_approach', 'failure', 'risk'):
        if key in details:
            result.append(_atom('REC' if key in ('implication', 'recommendation', 'recommended_approach') else 'EI',
                                details[key], '/details/' + key))
    return result


def _unique(values):
    result, seen = [], set()
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(copy.deepcopy(value))
    return result


def _unique_whole_atoms(values):
    """Collapse only complete dictionary subsets of one identical original atom."""
    same = lambda left, right: record_digest({'value': left}) == record_digest({'value': right})
    result = []
    for atom in _unique(values):
        if not isinstance(atom, dict) or not atom.get('record_pointer'):
            result.append(atom)
            continue
        for index, prior in enumerate(result):
            if not isinstance(prior, dict) or any(not same(prior.get(key), atom.get(key))
                    for key in ('record_pointer', 'kind', 'statement')):
                continue
            if all(key in prior and same(prior[key], value) for key, value in atom.items()):
                break
            if all(key in atom and same(atom[key], value) for key, value in prior.items()):
                result[index] = atom
                break
        else:
            result.append(atom)
    return result


def _split_kind(atom):
    # REC / EI 是原记录的混合标签；不改成 NSF，也不伪造更精确分类。
    return [value.strip() for value in atom['kind'].split('/')]


def _query_terms(query):
    query = expand_semantic_query(query)
    terms = {}
    for token in QUERY_WORD.findall(query):
        term = token.lower()
        if term in EN_STOP or len(term) < 2:
            continue
        symbol = (':' in token or '.' in token or '_' in token or
                  re.search(r'[a-z][A-Z]', token) is not None or token.startswith(('onhit', 'onattack')))
        terms[term] = {'weight': 8.0 if symbol else 2.0, 'symbol': symbol, 'han': False}
    for phrase in QUERY_HAN.findall(query):
        for size in (2, 3, 4):
            for index in range(len(phrase) - size + 1):
                term = phrase[index:index + size]
                if term not in ZH_STOP:
                    terms[term] = {'weight': 1.5 if size == 2 else 2.5 if size == 3 else 3.0,
                                   'symbol': False, 'han': True}
        if 2 <= len(phrase) <= 12 and phrase not in ZH_STOP:
            terms[phrase] = {'weight': min(4.0, float(len(phrase))), 'symbol': False, 'han': True}
    return terms


def _term_match(statement, term, is_han):
    return term in statement if is_han else re.search(r'(?<![a-z0-9_])' + re.escape(term) + r'(?![a-z0-9_])', statement) is not None


def _decision_bucket(atom):
    types = _split_kind(atom)
    if any(kind in ('UNK', 'PROJECT_POLICY', HISTORY) for kind in types):
        return None
    return next((kind for kind in ('NSF', 'RV', 'REC', 'EI') if kind in types), 'LEGACY')


def _query_scores(atoms, query):
    terms = _query_terms(query)
    eligible = [(index, atom) for index, atom in enumerate(atoms) if _decision_bucket(atom)]
    texts = {index: (atom['statement'] if isinstance(atom['statement'], str) else
                    json.dumps(atom['statement'], ensure_ascii=False)).lower()
             for index, atom in eligible}
    frequency = {term: sum(_term_match(text, term, spec['han']) for text in texts.values())
                 for term, spec in terms.items()}
    scores = {}
    for index, text in texts.items():
        matched = [term for term, spec in terms.items() if _term_match(text, term, spec['han'])]
        # 同一中文短语的重叠 bigram/trigram 只按最长匹配计一次，避免长度代替相关性。
        matched = [term for term in matched if not terms[term]['han'] or
                   not any(term != other and terms[other]['han'] and term in other for other in matched)]
        score = sum(terms[term]['weight'] * (1.0 + (len(eligible) - frequency[term]) / max(1, len(eligible)))
                    for term in matched)
        strong = any(terms[term]['symbol'] for term in matched) or (score >= 5.0 and
                 (len(matched) >= 2 or any(terms[term]['han'] and len(term) >= 4 for term in matched)))
        scores[index] = {'score': round(score, 3), 'strong': strong,
                         'matched_terms': sorted(matched, key=lambda term: (-terms[term]['weight'], term))}
    return scores


def _select_atoms(atoms, profile, query='', context='', reviewer_task=False):
    scores = _query_scores(atoms, query_scope(query)['positive_query']) if query.strip() else {}
    supports = {index: task_support(query, atom['statement'],
                 context.get(atom['record_pointer'], {}) if isinstance(context, dict) and
                 any(str(k).startswith('/') for k in context) else context)
                 for index, atom in enumerate(atoms)} if query.strip() else {}
    supported = {index: support.get('supported') is True for index, support in supports.items()}
    whole_allowed = {index: supported[index] and support.get('whole_atom_delivery_allowed') is True
                     for index, support in supports.items()}
    if reviewer_task and query.strip():
        # 原事实直送名额保持；实际支持pointer和必要context仍独立闭合。
        indexes = profile.get('claim_indexes', [])
        if any(type(index) is not int or index < 0 or index >= len(atoms) for index in indexes):
            raise ValueError('profile claim index out of bounds')
        order = list(dict.fromkeys(list(indexes) + sorted(range(len(atoms)),
                     key=lambda index: (-scores.get(index, {}).get('score', 0), index))))
        selected, counts = [], Counter()
        direct_limits = {'NSF': 3, 'RV': 1}
        for index in order:
            atom = atoms[index]
            bucket = _decision_bucket(atom)
            admitted = bool(bucket and whole_allowed.get(index, False) and
                            (bucket not in direct_limits or counts[bucket] < direct_limits[bucket]))
            dt.atom(None, atom['record_pointer'], 'REVIEWER_TASK_SELECTION', kind=atom['kind'],
                    profile_member=index in indexes, supported=supported.get(index),
                    whole_atom_delivery_allowed=whole_allowed.get(index), selected=admitted,
                    reason='ORIGINAL_TASK_ATOM_SELECTED' if admitted else 'ORIGINAL_TASK_ATOM_NOT_ADMITTED')
            if admitted:
                selected.append(atom)
                counts[bucket] += 1
        return _unique(selected)
    if 'claim_indexes' in profile:
        indexes = profile['claim_indexes']
        if any(type(index) is not int or index < 0 or index >= len(atoms) for index in indexes):
            raise ValueError('profile claim index out of bounds')
        selected = [atoms[index] for index in indexes
                    if not query.strip() or whole_allowed.get(index, False)]
        for index in indexes:
            dt.atom(None,atoms[index]['record_pointer'],'PROFILE_SELECTION',kind=atoms[index]['kind'],
                index=index,profile_member=True,supported=supported.get(index),
                whole_atom_delivery_allowed=whole_allowed.get(index),
                selected=not query.strip() or whole_allowed.get(index,False),
                reason='PROFILE_SELECTED' if not query.strip() or whole_allowed.get(index,False) else
                       'PROFILE_TASK_UNSUPPORTED' if not supported.get(index,False) else 'PROFILE_WHOLE_ATOM_DISALLOWED')
        if any(_decision_bucket(atom) is None for atom in selected):
            raise ValueError('profile cannot place unknown, policy or history into decision')
        if scores:
            extras = []
            for index, atom in enumerate(atoms):
                if index in indexes:
                    continue
                bucket = _decision_bucket(atom)
                if bucket != 'NSF':
                    dt.atom(None,atom['record_pointer'],'PROFILE_EXTRA',kind=atom['kind'],bucket=bucket,
                        profile_member=False,reason='EXTRA_NOT_NSF',selected=False)
                    continue
                strong = scores.get(index, {}).get('strong')
                if not strong:
                    dt.atom(None,atom['record_pointer'],'PROFILE_EXTRA',kind=atom['kind'],bucket=bucket,
                        strong=strong,score=scores.get(index,{}).get('score'),reason='EXTRA_NOT_STRONG',selected=False)
                    continue
                if not whole_allowed.get(index, False):
                    dt.atom(None,atom['record_pointer'],'PROFILE_EXTRA',kind=atom['kind'],bucket=bucket,
                        strong=strong,supported=supported.get(index),whole_atom_delivery_allowed=whole_allowed.get(index),
                        reason='PROFILE_TASK_UNSUPPORTED' if not supported.get(index,False) else 'PROFILE_WHOLE_ATOM_DISALLOWED',selected=False)
                    continue
                extras.append(index)
            extras.sort(key=lambda index: (-scores[index]['score'], index))
            for position,index in enumerate(extras,1):
                dt.atom(None,atoms[index]['record_pointer'],'PROFILE_EXTRA_CAP',kind=atoms[index]['kind'],
                    score=scores[index]['score'],strong=scores[index]['strong'],supported=supported.get(index),
                    whole_atom_delivery_allowed=whole_allowed.get(index),
                    extras_position=position,selected=position<=2,reason='EXTRA_SELECTED' if position<=2 else 'EXTRA_CAP')
            selected.extend(atoms[index] for index in extras[:2])
        result = _unique(selected)
        for position,atom in enumerate(result,1):
            dt.atom(None,atom['record_pointer'],'SELECTION_UNIQUE',kind=atom['kind'],selected=True,selection_position=position)
        return result
    selected, counts = [], Counter()
    limits = {'NSF': 3, 'RV': 1, 'EI': 1, 'REC': 2, 'LEGACY': 4}
    order = sorted(range(len(atoms)), key=lambda index: (-scores.get(index, {}).get('score', 0), index)) if scores else range(len(atoms))
    for index in order:
        atom = atoms[index]
        bucket = _decision_bucket(atom)
        if bucket is None or (query.strip() and not whole_allowed.get(index, False)):
            dt.atom(None,atom['record_pointer'],'BUCKET_SELECTION',kind=atom['kind'],bucket=bucket,
                score=scores.get(index,{}).get('score'),supported=supported.get(index),
                whole_atom_delivery_allowed=whole_allowed.get(index),selected=False,
                reason='ATOM_BUCKET_NOT_DECISION_ELIGIBLE' if bucket is None else
                       'ATOM_TASK_UNSUPPORTED' if not supported.get(index,False) else 'ATOM_WHOLE_ATOM_DISALLOWED')
            continue
        dt.atom(None,atom['record_pointer'],'BUCKET_CAP',kind=atom['kind'],bucket=bucket,
            score=scores.get(index,{}).get('score'),supported=supported.get(index),
            whole_atom_delivery_allowed=whole_allowed.get(index),
            bucket_count_before=counts[bucket],bucket_limit=limits.get(bucket,1),
            selected=counts[bucket]<limits.get(bucket,1),
            reason='BUCKET_SELECTED' if counts[bucket]<limits.get(bucket,1) else 'ATOM_BUCKET_CAP')
        if counts[bucket] < limits.get(bucket, 1):
            selected.append(atom)
            counts[bucket] += 1
    result = _unique(selected)
    for position,atom in enumerate(result,1):
        dt.atom(None,atom['record_pointer'],'SELECTION_UNIQUE',kind=atom['kind'],selected=True,selection_position=position)
    return result


def _hints(profile, field):
    result = []
    for item in profile.get(field, []):
        # 提示是消费建议，不新增 Native claim；完整依据在 L3 manifest 后置。
        if item.get('kind') != 'REC' or item.get('consumption_hint') is not True:
            raise ValueError('Additional projection advice must be REC / consumption_hint')
        result.append({key: copy.deepcopy(item[key]) for key in
                       ('kind', 'consumption_hint', 'statement', 'basis_record_pointers') if key in item})
    return result


def _boundaries(record, family):
    key = 'does_not_prove' if family == 'core' else 'does_not_mean'
    values = record.get(key, [])
    indexed = isinstance(values, list)
    if not indexed:
        values = [values]
    result = [{**_atom('BOUNDARY', value, f'/{key}/{index}' if indexed else f'/{key}'),
               'polarity': 'ORIGINAL_BOUNDARY_TEXT', 'source_field': key, 'delivery_scope': 'BOUNDARY_NOT_ASSERTION',
               'display_instruction': '保留原句及其边界字段语境，不额外翻转极性；既有否定、未知和 scope 原样保留，不当作事实断言或默认建议。'}
              for index, value in enumerate(values)]
    if family == 'legacy':
        for name in ('does_not_mean', 'do_not_infer', 'unknowns', 'unverified'):
            value = record.get('details', {}).get(name)
            pointer = '/details/' + name
            if value and not any(item['record_pointer'] == pointer for item in result):
                boundary = name in ('does_not_mean', 'do_not_infer')
                result.append({**_atom('BOUNDARY' if boundary else 'UNK', value, pointer),
                               'polarity': 'ORIGINAL_BOUNDARY_TEXT' if boundary else 'UNRESOLVED',
                               'source_field': name,
                               'delivery_scope': 'BOUNDARY_NOT_ASSERTION' if boundary else 'UNKNOWN_OR_UNVERIFIED',
                               'display_instruction': '按原句保留已有否定，不额外反转原句极性。' if boundary else '原文是未验证项或未知状态，不作为已证明的肯定事实。'})
    return result


def _when(record, family, profile):
    if 'when_relevant' in profile:
        return copy.deepcopy(profile['when_relevant'])
    if family == 'n001':
        return [record.get('engineering_question', '')] + record.get('typical_mod_tasks', [])[:2]
    if family == 'legacy':
        return [record.get('scope_text', record.get('scope', ''))]
    scope = record.get('scope', {})
    statement = scope.get('statement') if isinstance(scope, dict) else scope
    tasks = record.get('task_keywords', [])
    natural = [term for term in tasks if any('\u3400' <= char <= '\u9fff' for char in term)]
    return _unique(([statement] if statement else []) + (natural or tasks)[:2])


def _symbols(record, family, profile, atoms):
    result = []
    for atom in atoms:
        if 'NSF' not in _split_kind(atom) and not atom['kind'].startswith('LEGACY_SOURCE_FACT'):
            continue
        statement = atom['statement']
        if not isinstance(statement, str):
            continue
        for symbol in list(QUALIFIED.findall(statement)) + BARE_API.findall(statement):
            item = {'symbol': symbol, 'basis_record_pointer': atom['record_pointer']}
            if ':' in symbol:
                item['receiver_spelling'] = symbol.split(':', 1)[0]
            result.append(item)
    fields = ('task_keywords',) if family == 'core' else ('retrieval_triggers',)
    for field in fields:
        for index, symbol in enumerate(record.get(field, [])):
            if SYMBOL_TERM.fullmatch(symbol) and not re.match(r'(?:AI-|NC-|N\d{3}-|NSF-|STUI-|SLOT-|[A-Z]{2,}-[A-Z])', symbol):
                result.append({'symbol': symbol, 'basis_record_pointer': f'/{field}/{index}',
                               'role': 'navigation_token_receiver_not_inferred'})
    if family == 'legacy':
        for i, source in enumerate(record.get('sources', [])):
            for j, locator in enumerate(source.get('locator_structured', [])):
                if locator.get('type') == 'source_symbol' and locator.get('symbol'):
                    result.append({'symbol': locator['symbol'], 'file': locator.get('file'),
                                   'basis_record_pointer': f'/sources/{i}/locator_structured/{j}'})
    result.extend(copy.deepcopy(profile.get('receiver_bindings', [])))
    represented = {atom['record_pointer'] for atom in atoms}
    for symbol in contract_symbols(record, family):
        for match in contract_matches(record, family, symbol):
            if match.get('receiver') and represented.intersection(match['record_pointers']):
                result.append({'symbol': symbol, 'receiver': match['receiver'],
                               'role': (match.get('binding_kind', match['mapping_status'])
                                        if match.get('binding_kind') != 'typed_behavioral_contract' else match['mapping_status']),
                               'basis_record_pointers': match['record_pointers']})
    # 同一拼写可有多条依据；保留第一条和显式 receiver hint，限制条数时不截断签名。
    seen, unique = set(), []
    for item in result:
        key = (item['symbol'], item.get('receiver'), item.get('role'))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def _strength(record, family, atoms):
    if family == 'n001':
        return copy.deepcopy(record.get('evidence_strength', {}))
    if family == 'legacy':
        return {'legacy_evidence_level': record.get('evidence_level'),
                'legacy_confidence': record.get('confidence'),
                'native_claim_classification': 'NOT_PROMOTED',
                'runtime_verification_by_projection': False}
    return {'claim_kinds': dict(Counter(atom['kind'] for atom in atoms)),
            'native_fact_basis': 'BOUNDED_SOURCE_FACTS_IN_FROZEN_RECORD',
            'runtime_verified': record.get('gate_a', {}).get('runtime_verified', False),
            'effect_on_AI_quality': 'NOT_ESTABLISHED_BY_SOURCE_OR_GATE_A'}


def _expansion(entry_id):
    return {'reviewer': {'tool': 'get_entry', 'arguments': epoch_arguments({'id': entry_id, 'projection': 'reviewer', 'view': 'reviewer'})},
            'manifest': {'tool': 'get_entry', 'arguments': epoch_arguments({'id': entry_id, 'projection': 'reviewer', 'view': 'evidence'})},
            'resolve': {'tool': 'resolve_evidence', 'arguments': epoch_arguments({'id': entry_id,
                        'projection': 'reviewer', 'reference_index': 0, 'subpointer': '', 'max_bytes': 24000}),
                        'selection': 'Choose the exact reference_index from the evidence manifest'},
            'default_evidence_expanded': False}


def delivery_contract_mappings(matches, source_scope=None):
    """L1 carries exact provenance identity; source nodes remain behind L3."""
    fields = ('symbol', 'receiver', 'mapping_status', 'mapping_basis', 'binding_kind',
              'record_pointers', 'claim_kinds', 'availability_record_pointers',
              'availability_claim_kinds', 'pointer_roles', 'record_sha256',
              'original_scope', 'original_governance', 'method_semantics_not_synthesized',
              'context_record_pointers', 'context_claim_kinds', 'context_pointer_bindings',
              'context_is_method_contract', 'source_adjacency_navigation', 'context_closure_gaps',
              'context_admission', 'needed_context_excluded',
              'reference_context_only', 'reference_context_record_pointers',
              'query_name_resolution', 'context_dependency_edges')
    return [compact_diagnostics(shared_scope_references({**{key: copy.deepcopy(match[key]) for key in fields if key in match},
             'source_references_expanded': False}, source_scope)) for match in matches]


def delivered_original_atoms(record, family, item):
    """Validate actual view identity, pointer, original kind and whole value."""
    expected = {atom['record_pointer']: atom for atom in _atoms(record, family) + _boundaries(record, family)}
    verified, errors, invalid = {}, [], set()
    digest = record_digest(record)
    identity = item.get('id') == record['id'] and item.get('record_sha256') == digest
    for field in ('decision', 'typed_atoms', 'critical_boundary', 'does_not_mean', 'project_policy_questions'):
        for atom in item.get(field, []):
            if not isinstance(atom, dict) or atom.get('consumption_hint'):
                continue
            pointer = atom.get('record_pointer')
            original = expected.get(pointer)
            if original is None:
                if pointer is not None:
                    errors.append({'record_pointer': pointer, 'reason': 'POINTER_NOT_IN_ORIGINAL_RECORD'})
                continue
            node = record
            try:
                for token in pointer.split('/')[1:]:
                    token = token.replace('~1', '/').replace('~0', '~')
                    node = node[int(token)] if isinstance(node, list) else node[token]
                typed_claim_node = (family == 'core' and re.fullmatch(r'/claims/\d+', pointer)) or (family == 'n001' and pointer == '/native_fact')
                original_text = node['statement'] if typed_claim_node and isinstance(node, dict) and 'statement' in node else node
                pointer_valid = original_text == original['statement']
            except (KeyError, IndexError, ValueError, TypeError):
                pointer_valid = False
            if not identity or not pointer_valid or atom.get('kind') != original['kind'] or atom.get('statement') != original['statement']:
                errors.append({'record_pointer': pointer, 'reason': 'ORIGINAL_HASH_KIND_OR_TEXT_MISMATCH'})
                invalid.add(pointer)
                verified.pop(pointer, None)
                continue
            if pointer not in invalid:
                verified[pointer] = original
    return verified, errors


def atom_value_key(atom):
    return atom['kind'], record_digest({'statement': atom['statement']})


def original_fact_copy_keys(record, verified_references):
    """Same original fact, whole typed value and original Scope; never citation similarity."""
    scope = record.get('scope', {})
    if not isinstance(scope, dict):
        return {}
    ref_key = lambda ref: tuple(ref.get(key) for key in ('artifact_path', 'sha256', 'pointer'))
    facts = {ref_key(row['fact_ref']): row for row in scope.get('typed_fact_dispositions', [])
             if isinstance(row.get('fact_ref'), dict) and row.get('disposition') == 'canonical_typed_claim'
             and ref_key(row['fact_ref']) in verified_references}
    scopes = [row for row in scope.get('source_scopes', [])
              if isinstance(row.get('scope_ref'), dict) and ref_key(row['scope_ref']) in verified_references
              and row.get('snapshot_id') and row.get('source_commit')]
    result = {}
    from .facet_contracts import _sample_scope
    for index, atom in enumerate(record.get('claims', [])):
        if atom['kind'] not in ('NSF', 'EI', 'REC', 'UNK'):
            continue
        pointer = f'/claims/{index}'
        for ref in atom.get('evidence_refs', []):
            key = ref_key(ref)
            if key not in facts or atom['kind'] not in facts[key].get('kinds', []):
                continue
            matching = sorted(({'scope_ref': row['scope_ref'], 'snapshot_id': row['snapshot_id'],
                                'source_commit': row['source_commit']} for row in scopes
                               if row['scope_ref']['artifact_path'] == ref['artifact_path']),
                              key=lambda row: json.dumps(row, sort_keys=True))
            if not matching:
                continue
            digest = record_digest({'fact_ref': ref, 'kind': atom['kind'], 'whole_statement': atom['statement'],
                'original_source_scopes': matching, 'sample_scope': _sample_scope(record, {**atom, 'record_pointer': pointer})})
            result.setdefault(pointer, []).append((digest, copy.deepcopy(ref)))
    return result


def companion_context_card(card, seed_pointers, copy_bindings, represented, record=None, query='', navigation_context=None):
    """A donor owns its pointers. Its verified copy is a bridge, not another task seed."""
    closure = card.get('context_closure', {})
    bindings = [binding for binding in closure.get('bindings', [])
                if set(binding.get('basis_record_pointers', [])) & set(seed_pointers)]
    required = {binding['record_pointer'] for binding in bindings} - set(seed_pointers)
    groups = {}
    selected = set()
    for field in ('decision', 'critical_boundary', 'project_policy_questions'):
        groups[field] = [copy.deepcopy(atom) for atom in card.get(field, [])
                         if atom.get('record_pointer') in required and atom_value_key(atom) not in represented]
        selected.update(atom['record_pointer'] for atom in groups[field])
    donor_gaps = bool(closure.get('needed_context_missing') or closure.get('needed_context_excluded')
                      or closure.get('needed_semantic_scope_node_count')
                      or closure.get('scope_dependency_resolution_complete') is False
                      or closure.get('identified_necessary_scope_dependencies_complete') is False)
    if not selected and not donor_gaps:
        return None
    # donor 的原记录限制随其上下文交付；没有绑定的缺口不能被误删或冒称已证明必要。
    limits = [copy.deepcopy(atom) for atom in card.get('critical_boundary', [])
              if atom.get('source_field') in ('does_not_prove', 'does_not_mean')]
    groups['critical_boundary'] = _unique(groups['critical_boundary'] + limits)
    selected.update(atom['record_pointer'] for atom in limits)
    focus_decisions, focus_excluded = [], set()
    if record is not None and query.strip():
        contexts = _claim_contexts(record, card['family'],
                                   _atoms(record, card['family']) + _boundaries(record, card['family']))
        groups, focus_decisions, focus_excluded = _final_positive_focus(
            record, card['family'], groups, query, contexts)
        # Original record limits accompany the surviving donor facts. A limit
        # often omits the method name and cannot be discarded for that reason.
        limit_pointers = {atom['record_pointer'] for atom in limits}
        groups['critical_boundary'] = _unique(groups['critical_boundary'] + limits)
        focus_excluded -= limit_pointers
        focus_decisions = [row for row in focus_decisions if row.get('record_pointer') not in limit_pointers]
        selected = {atom['record_pointer'] for values in groups.values() for atom in values}
        donor_gaps |= bool(focus_excluded)
    result = {key: copy.deepcopy(card[key]) for key in
              ('projection_schema', 'level', 'family', 'id', 'title', 'record_sha256',
               'source_scope', 'governance', 'evidence_strength', 'expansion', 'entry_type') if key in card}
    result.update(groups)
    if record is not None:
        result['source_scope'] = compact_semantic_scope(record, card['family'], groups, query,
            sorted(set(closure.get('needed_context_excluded', [])) | focus_excluded),
            navigation_context=navigation_context)
    result['context_closure'] = {**copy.deepcopy(closure),
        'status': 'PARTIAL_CONTEXT' if donor_gaps else 'BOUNDED_DONOR_ORIGINAL_CONTEXT',
        'bindings': [copy.deepcopy(binding) for binding in bindings if binding['record_pointer'] in selected],
        'universal_method_contract_verified': False,
        'donor_gap_scope': 'DONOR_VIEW_GAPS_PRESERVED_NOT_PROVED_NECESSARY_TO_PARENT',
        'original_record_limits_preserved': True}
    if focus_excluded:
        result['context_closure']['needed_context_excluded'] = sorted(
            set(closure.get('needed_context_excluded', [])) | focus_excluded)
        result['context_closure']['admission'] = copy.deepcopy(closure.get('admission', [])) + focus_decisions
    result['copy_bridge'] = {'relation': 'ONE_HOP_SAME_ORIGINAL_FACT_COPY',
        'bindings': [copy.deepcopy(binding) for binding in copy_bindings
                     if binding['donor_record_pointer'] in seed_pointers],
        'duplicate_seed_delivered_in_parent': True, 'donor_seed_verified_in_actual_view': True,
        'context_is_method_contract': False, 'recursive_donor_expansion': False}
    result['omission'] = {'whole_atoms_preserved': True, 'full_record_delivered': False}
    return sample_reference_assessment(result)


def _delivery_status(groups, fallback='IDENTITY_ONLY'):
    if not groups:
        return fallback
    statuses = [group['status'] for group in groups]
    if all(status == 'TYPED_CONTRACT_DELIVERED' for status in statuses):
        return 'TYPED_CONTRACT_DELIVERED'
    if any(status in ('TYPED_CONTRACT_DELIVERED', 'TYPED_CONTRACT_PARTIAL') for status in statuses):
        return 'TYPED_CONTRACT_PARTIAL'
    if any(status == 'CONTRACT_SCOPE_EXCLUDED' for status in statuses):
        return 'CONTRACT_SCOPE_EXCLUDED'
    if all(status == 'BOUNDED_CONTEXT_DELIVERED' for status in statuses):
        return 'BOUNDED_CONTEXT_DELIVERED'
    if any(status in ('BOUNDED_CONTEXT_DELIVERED', 'BOUNDED_CONTEXT_PARTIAL') for status in statuses):
        return 'BOUNDED_CONTEXT_PARTIAL'
    if all(status == 'AVAILABILITY_EXISTENCE_DELIVERED' for status in statuses):
        return 'AVAILABILITY_EXISTENCE_DELIVERED'
    if any(status in ('AVAILABILITY_EXISTENCE_DELIVERED', 'AVAILABILITY_EXISTENCE_PARTIAL') for status in statuses):
        return 'AVAILABILITY_EXISTENCE_PARTIAL'
    return fallback


def contract_delivery(record, family, item, matches, symbol='', identity_match=False):
    """Exact original delivery preserves each group's verified semantic role."""
    delivered, integrity_errors = delivered_original_atoms(record, family, item)
    verified = set(delivered)
    digest = record_digest(record)
    projected_scope = item.get('source_scope', {})
    has_scope_projection = isinstance(projected_scope, dict) and projected_scope.get('scope_schema') == SCOPE_SCHEMA
    scope_missing = copy.deepcopy(projected_scope.get('needed_scope_missing', [])) if has_scope_projection else []
    selected_scope_missing = sum('DECLARED_SELECTED_ATOM_SCOPE_DEPENDENCY' in node.get('scope_relation_statuses', [])
                                 for node in scope_missing)
    unattributed_scope_missing = sum('UNATTRIBUTED_POTENTIAL_RECORD_SCOPE_DEPENDENCY' in node.get('scope_relation_statuses', [])
                                    for node in scope_missing)
    scope_closure_status = ('PARTIAL_SELECTED_ATOM_SCOPE_DEPENDENCY' if selected_scope_missing else
                            'PARTIAL_UNATTRIBUTED_RECORD_SCOPE' if scope_missing else
                            'IDENTIFIED_SCOPE_DEPENDENCIES_DELIVERED' if has_scope_projection else
                            'NO_PROJECTED_SCOPE_DEPENDENCY_GAPS_DECLARED')
    excluded = {decision.get('record_pointer') for decision in
                item.get('facet_admission', {}).get('decisions', []) if not decision.get('admitted')}
    groups = []
    for index, match in enumerate(matches):
        direct = set(match.get('record_pointers', []))
        context = set(match.get('context_record_pointers', []))
        availability = set(match.get('availability_record_pointers', []))
        required_basis = {pointer for binding in match.get('context_pointer_bindings', [])
                          for pointer in binding.get('required_basis_record_pointers', [])}
        required_basis |= {edge['required_record_pointer'] for edge in match.get('context_dependency_edges', [])}
        required = direct | context | required_basis
        mapping_valid = match.get('record_sha256') == digest
        actual = verified if mapping_valid else set()
        missing = required - actual
        missing_availability = availability - actual
        closure_gaps = match.get('context_closure_gaps', [])
        reference_only = match.get('reference_context_only') is True
        complete_status = 'BOUNDED_CONTEXT_DELIVERED' if reference_only else 'TYPED_CONTRACT_DELIVERED'
        partial_status = 'BOUNDED_CONTEXT_PARTIAL' if reference_only else 'TYPED_CONTRACT_PARTIAL'
        if direct and not missing and not closure_gaps:
            status = complete_status
        elif direct and required & actual:
            status = partial_status
        elif direct and missing & excluded:
            status = 'CONTRACT_SCOPE_EXCLUDED'
        elif direct:
            status = partial_status
        elif context and match.get('mapping_status') == 'BOUNDED_CONTEXT' and reference_only:
            status = 'BOUNDED_CONTEXT_DELIVERED' if not missing and not closure_gaps else 'BOUNDED_CONTEXT_PARTIAL'
        elif availability and not missing_availability:
            status = 'AVAILABILITY_EXISTENCE_DELIVERED'
        elif availability & actual:
            status = 'AVAILABILITY_EXISTENCE_PARTIAL'
        else:
            status = 'IDENTITY_ONLY'
        # 原 atom 完整不等于必要语义 Scope 已交付；导航后置和未证明
        # 全 record 依赖枚举本身不会降低已识别合同的交付状态。
        if scope_missing and status == 'TYPED_CONTRACT_DELIVERED':
            status = 'TYPED_CONTRACT_PARTIAL'
        elif scope_missing and status == 'BOUNDED_CONTEXT_DELIVERED':
            status = 'BOUNDED_CONTEXT_PARTIAL'
        elif scope_missing and status == 'AVAILABILITY_EXISTENCE_DELIVERED':
            status = 'AVAILABILITY_EXISTENCE_PARTIAL'
        groups.append({'mapping_index': index, 'symbol': match.get('symbol'), 'status': status,
                       'reference_context_only': reference_only,
                       'required_record_pointers': sorted(required),
                       'direct_record_pointers': sorted(direct), 'context_record_pointers': sorted(context),
                       'delivered_record_pointers': sorted(required & actual),
                       'missing_record_pointers': sorted(missing),
                       'scope_excluded_record_pointers': sorted(missing & excluded),
                       'availability_record_pointers': sorted(availability & actual),
                       'missing_availability_record_pointers': sorted(missing_availability),
                       'record_sha256': digest, 'mapping_identity_verified': mapping_valid,
                       'direct_claims_complete': bool(direct) and direct <= actual,
                       'required_context_complete': (context | required_basis) <= actual and not closure_gaps,
                       'identified_necessary_scope_dependencies_complete': not bool(selected_scope_missing),
                       'scope_dependency_resolution_complete': not bool(scope_missing),
                       'needed_semantic_scope_node_count': len(scope_missing),
                       'unresolved_context_record_pointers': closure_gaps,
                       'context_is_method_contract': False})
    all_atoms = {atom['record_pointer'] for atom in _atoms(record, family)}
    return {'status': _delivery_status(groups, 'IDENTITY_ONLY' if matches or identity_match else 'CATALOG_SCOPE_GAP'),
            'symbol': symbol, 'record_sha256': digest,
            'mappings': delivery_contract_mappings(matches, item.get('source_scope')), 'groups': groups,
            'all_mapping_groups_complete': bool(groups) and all(group['status'] == 'TYPED_CONTRACT_DELIVERED' for group in groups),
            'all_original_groups_complete': bool(groups) and all(group['status'] in (
                'TYPED_CONTRACT_DELIVERED', 'BOUNDED_CONTEXT_DELIVERED', 'AVAILABILITY_EXISTENCE_DELIVERED') for group in groups),
            'delivered_record_pointers': sorted(verified & {p for match in matches for p in match.get('record_pointers', [])}),
            'context_record_pointers': sorted(verified & {p for match in matches for p in match.get('context_record_pointers', [])}),
            'availability_record_pointers': sorted(verified & {p for match in matches for p in match.get('availability_record_pointers', [])}),
            'original_delivery_integrity_errors': integrity_errors,
            'availability_is_behavior_contract': False,
            'method_semantics_inferred_from_grouped_citation': False,
            'semantic_scope_closure': {'status': scope_closure_status,
                                      'identified_necessary_scope_dependencies_complete': not bool(selected_scope_missing),
                                      'scope_dependency_resolution_complete': not bool(scope_missing),
                                      'identified_selected_atom_scope_missing_count': selected_scope_missing,
                                      'unattributed_potential_record_scope_missing_count': unattributed_scope_missing,
                                      'record_scope_dependency_enumeration_proven': False,
                                      'needed_scope_missing': scope_missing,
                                      'pure_navigation_deferral_does_not_downgrade': True},
            'scope': 'All returned mapped original groups and exact citation context; method universal closure is not established',
            'full_method_contract_verified': False, 'canonical_claims_complete': bool(all_atoms) and all_atoms <= verified,
            'source_contract_closure': scope_closure_status if scope_missing else
                                       'BOUNDED_ORIGINAL_POINTER_CONTEXT_ONLY', 'full_record_delivered': False}


def _sample_reference_atoms(item):
    """Opaque legacy fields are not typed atoms or sample proof."""
    if not isinstance(item, dict):
        return
    for field in ('decision', 'critical_boundary', 'typed_atoms', 'does_not_mean'):
        atoms = item.get(field)
        if not isinstance(atoms, (list, tuple)):
            continue
        for atom in atoms:
            if not isinstance(atom, dict):
                continue
            reference = atom.get('sample_reference')
            pointer = atom.get('record_pointer')
            if (isinstance(reference, dict) and isinstance(pointer, str) and pointer.startswith('/')
                    and reference.get('record_pointer') == pointer
                    and reference.get('schema') == 'bounded-named-sample-reference/2'):
                yield atom, reference


def sample_reference_assessment(item):
    """Report bounded examples independently of generic contract proof."""
    if not isinstance(item, dict):
        return item
    pointers = [atom['record_pointer'] for atom, _ in _sample_reference_atoms(item)]
    if pointers:
        item['sample_reference_assessment'] = {
            'policy': 'bounded-named-sample-reference/2',
            'delivered_reference_record_pointers': list(dict.fromkeys(pointers)),
            'sample_references_prove_generic_contract': False,
            'generic_contract_completion_claimed': False,
            'generic_contract_gap_retained': True,
            'independent_generic_evidence_assessment': 'REQUIRED_SEPARATELY',
            'notice': '具名例证只证明固定来源及原 Scope 内的有界事实。通用合同须独立判断；例证的相关性或完整交付均不能消除通用证据缺口。'}
    else:
        item.pop('sample_reference_assessment', None)
    return item


def sample_reference_entry_ids(items):
    ids = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if any(True for _ in _sample_reference_atoms(item)):
            ids.append(item['id'])
        ids.extend(sample_reference_entry_ids(item.get('companion_context', [])))
    return list(dict.fromkeys(ids))


def annotate_sample_reference_view(record, family, item, query, reference_context):
    """Keep L2 whole-body/L3 manifest semantics and explicit exclusions."""
    if not query.strip() or reference_context is None:
        return item
    verified, errors = delivered_original_atoms(record, family, item)
    if errors:
        return item
    from .facet_contracts import _sample_scope
    from .sample_reference import sample_reference_excluded
    excluded = [pointer for pointer, atom in verified.items()
                if _sample_scope(record, atom) is not None and
                sample_reference_excluded(query, _sample_scope(record, atom), atom['statement'])]
    if excluded:
        # L2 约定交付整个原记录；明确排除时拒绝该记录，不能悄悄删句改成另一种 view。
        item['sample_reference_exclusion'] = {'status': 'WHOLE_VIEW_WITHHELD_FOR_EXPLICIT_SAMPLE_EXCLUSION',
                                              'record_pointers': excluded}
        return item
    if item.get('level') == 1:
        return sample_reference_assessment(item)
    wrapped, _ = facet_admission(record, family, list(verified.values()), query,
                                reference_context=reference_context)
    references = {atom['record_pointer']: atom['sample_reference'] for atom in wrapped
                  if atom.get('sample_reference')}
    for field in ('typed_atoms', 'does_not_mean'):
        for atom in item.get(field, []):
            if atom.get('record_pointer') in references:
                atom['sample_reference'] = copy.deepcopy(references[atom['record_pointer']])
    return sample_reference_assessment(item)


def annotate_bounded_route_view(record, family, item, query, reference_context):
    """Attach route limits to delivered whole atoms in every existing view."""
    if not query.strip() or reference_context is None:
        return item
    from .relevance_frames import input_route_stage_request, input_route_stage_witness
    from .sample_reference import sample_reference_excluded
    from .task_relevance import _bounded_route_excluded
    route_requested = input_route_stage_request(query_scope(query)['positive_query'])
    verified, errors = delivered_original_atoms(record, family, item)
    if errors:
        return item
    excluded = []
    unverified = []
    references = {}
    for pointer, atom in verified.items():
        witness = input_route_stage_witness(atom['statement'])
        if witness is None or atom['kind'] != 'NSF':
            continue
        if (sample_reference_excluded(query, {}, atom['statement'])
                or _bounded_route_excluded(query, atom['statement'], witness)):
            excluded.append(pointer)
            continue
        if not route_requested:
            continue
        reference = bounded_input_route_reference(record, atom, query, **reference_context)
        if reference is not None:
            references[pointer] = reference
        else:
            unverified.append(pointer)
    if excluded and item.get('level') != 1:
        # L2 remains the original whole record. Excluding a stage withholds the
        # whole view instead of quietly cutting a sentence out of its body.
        item['bounded_route_exclusion'] = {'status': 'WHOLE_VIEW_WITHHELD_FOR_EXPLICIT_ROUTE_EXCLUSION',
                                          'record_pointers': excluded}
    elif unverified and item.get('level') == 2:
        # L2 cannot retain a bare intermediate stage if its own Source/actor
        # proof or current task relation failed. Keep the original body whole
        # and let the existing view-admission gate withhold it explicitly.
        item['bounded_route_exclusion'] = {'status': 'WHOLE_VIEW_WITHHELD_FOR_UNVERIFIED_ROUTE_STAGE',
                                          'record_pointers': unverified}
    for field in ('decision', 'critical_boundary', 'typed_atoms', 'does_not_mean'):
        for atom in item.get(field, []):
            if atom.get('record_pointer') in references:
                atom['bounded_route_reference'] = copy.deepcopy(references[atom['record_pointer']])
    return item


def task_view_admission(record, family, item, query, projection='coding'):
    """Natural-query admission is established by actual preserved view atoms."""
    verified, errors = delivered_original_atoms(record, family, item)
    exact = normalize_symbol(query) in contract_symbols(record, family) if query.strip() else False
    contexts = _claim_contexts(record, family, _atoms(record, family))
    pointers = []
    for pointer, atom in verified.items():
        if set(_split_kind(atom)) & {'PROJECT_POLICY', HISTORY}:
            continue
        support = task_support(query, atom['statement'], contexts.get(pointer, {'scope': _scope(record), 'receivers': []}))
        dt.atom(record['id'],pointer,'ACTUAL_VIEW_TASK',kind=atom['kind'],supported=support.get('supported'),
            whole_atom_delivery_allowed=support.get('whole_atom_delivery_allowed',False),
            subject_mismatch=support.get('subject_mismatch'),excluded_source_scope=support.get('excluded_source_scope'))
        route = support.get('bounded_route_stage')
        route_delivered = any(candidate.get('record_pointer') == pointer and candidate.get('bounded_route_reference')
            for field in ('decision', 'critical_boundary', 'typed_atoms', 'does_not_mean')
            for candidate in item.get(field, []) if isinstance(candidate, dict))
        if support.get('whole_atom_delivery_allowed', False) and (not route or route_delivered):
            pointers.append(pointer)
    dt.record(record['id'],'ACTUAL_VIEW_INTEGRITY',integrity_error_count=len(errors))
    policy = policy_delivery_admission(record, family, item, query, projection, verified)
    policy_pointers = policy['supported_policy_record_pointers']
    if item.get('bounded_route_exclusion'):
        pointers, policy_pointers = [], []
    return {'method': 'actual_view_original_atom_task_relation/2.13',
            'status': 'EXACT_SYMBOL_NAVIGATION' if exact else 'TASK_AND_POLICY_ATOMS_DELIVERED' if pointers and policy_pointers else
                      'POLICY_ATOM_DELIVERED' if policy_pointers else 'TASK_ATOM_DELIVERED' if pointers else
                      'MANIFEST_NAVIGATION_ONLY' if item.get('level') == 3 else 'NO_TASK_ATOM_DELIVERED',
            'supported_record_pointers': pointers,
            'supported_original_atom_count': len(pointers), 'original_delivery_integrity_errors': errors,
            'supported_nonpolicy_record_pointers': pointers, 'supported_nonpolicy_atom_count': len(pointers),
            'total_supported_original_atom_count': len(pointers) + len(policy_pointers),
            'nonpolicy_support_meaning': 'TASK_RELEVANCE_ONLY_NOT_NATIVE_FACT_ASSERTION',
            'metadata_or_hint_admits_result': False, **policy}


def _claim_contexts(record, family, atoms):
    """One original-pointer context for candidate support and actual delivery."""
    scope = record.get('scope', record.get('scope_text', ''))
    if isinstance(scope, dict):
        scope = scope.get('statement', '')
    receivers = {a['record_pointer']: set() for a in atoms}
    roles = {a['record_pointer']: [] for a in atoms}
    for symbol in contract_symbols(record, family):
        for match in contract_matches(record, family, symbol):
            owner = match.get('receiver')
            for pointer in match.get('record_pointers', []) + match.get('availability_record_pointers', []):
                role = match.get('pointer_roles', {}).get(pointer, {})
                role_detail = role if isinstance(role, dict) else {'role': role}
                role = role_detail.get('role')
                # Caller/callee observation never supplies another fact's subject.
                if pointer in roles:
                    binding = {'symbol': match.get('symbol', symbol), 'receiver': owner, **copy.deepcopy(role_detail)}
                    if binding not in roles[pointer]:
                        roles[pointer].append(binding)
                if owner and pointer in receivers and role in ('METHOD_SUBJECT', 'AVAILABILITY_EXISTENCE'):
                    receivers[pointer].add(owner)
    original_kinds = {atom['record_pointer']: atom['kind']
                      for atom in _atoms(record, family) + _boundaries(record, family)}
    kinds = {atom['record_pointer']: original_kinds.get(atom['record_pointer']) for atom in atoms}
    content_index = record_content_context(_atoms(record, family))
    identity = {}
    if family == 'legacy':
        cases = []
        for values in (record.get('created_from_case', []), record.get('scope_structured', {}).get('cases', [])):
            values = [values] if isinstance(values, str) else values
            if isinstance(values, list):
                cases.extend(value for value in values if isinstance(value, str))
        corrected = record.get('details', {}).get('target_claim_ids', [])
        corrected = [corrected] if isinstance(corrected, str) else list(corrected) if isinstance(corrected, list) else []
        for relations in (record.get('typed_relations', []), record.get('relations', [])):
            if not isinstance(relations, list):
                continue
            for relation in relations:
                if (isinstance(relation, dict) and relation.get('type', relation.get('relation_type')) in ('corrects', 'supersedes')
                        and isinstance(relation.get('target', relation.get('target_id')), str)):
                    corrected.append(relation.get('target', relation.get('target_id')))
        identity = {'original_record_identity': {'id': record['id'],
            'entry_type': record.get('entry_type'), 'case_ids': list(dict.fromkeys(cases)),
            'corrected_claim_ids': list(dict.fromkeys(value for value in corrected if isinstance(value, str)))}}
    return {pointer: {'scope': scope, 'receivers': sorted(owners), 'role_bindings': roles[pointer],
                      'atom_kind': kinds[pointer], 'record_pointer': pointer,
                      'original_content_index': content_index, **copy.deepcopy(identity)}
            for pointer, owners in receivers.items()}


def direct_contract_seed_pointers(contracts):
    """Behavioral subjects and bounded calls/noncalls, never identity references."""
    result = set()
    for match in contracts:
        if match.get('reference_context_only'):
            continue
        reference_only = set(match.get('reference_context_record_pointers', []))
        for pointer in match.get('record_pointers', []):
            role = match.get('pointer_roles', {}).get(pointer, {})
            if (pointer not in reference_only and isinstance(role, dict) and
                    not role.get('reference_context_only') and role.get('role') in
                    ('METHOD_SUBJECT', 'SOURCE_OBSERVATION_SUBJECT',
                     'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL')):
                result.add(pointer)
    return result


def _explicit_context_head(atom):
    text = atom.get('statement')
    if not isinstance(text, str):
        return set()
    head = re.match(r'\s*(?:The\s+)?([A-Za-z_]\w*)(?=[\s:.]|组件|$)', text, re.I)
    return ((task_subjects(head.group(1)) & DOMAIN_SUBJECTS) - {'shard', 'death', 'reroll', 'snapshot'}
            if head else set())


def _record_context_atoms(record, family, candidates, seeds, query, contexts, contracts=()):
    """Original recommendations/limits accompany a real seed, not a new API claim."""
    if not seeds or not query.strip():
        return [], []
    seed_pointers = {atom['record_pointer'] for atom in seeds}
    owners = {pointer: set(context.get('receivers', [])) for pointer, context in contexts.items()}
    for match in contracts:
        for pointer, role in match.get('pointer_roles', {}).items():
            if isinstance(role, dict) and role.get('role') == 'METHOD_SUBJECT' and match.get('receiver'):
                owners.setdefault(pointer, set()).add(match['receiver'])
    seed_owners = set().union(*(owners.get(pointer, set()) for pointer in seed_pointers))
    seed_heads = set().union(*(_explicit_context_head(atom) for atom in seeds))
    eligible = [atom for atom in candidates if
                (set(_split_kind(atom)) <= {'REC', 'EI'} or
                 atom.get('source_field') in ('does_not_prove', 'does_not_mean', 'do_not_infer'))]
    admitted, decisions = facet_admission(record, family, eligible, query)
    result = []
    for original in admitted:
        pointer = original['record_pointer']
        context = contexts.get(pointer, {'scope': _scope(record), 'receivers': []})
        support = task_support(query, original['statement'], context)
        other_owner = bool(seed_owners and owners.get(pointer) and not seed_owners & owners[pointer])
        head = _explicit_context_head(original)
        other_owner |= bool(seed_heads and head and not seed_heads & head and support.get('subject_mismatch'))
        excluded = bool(support.get('excluded_source_scope') or
                        support.get('whole_atom_excluded_relation_owners') or other_owner)
        decisions.append({'record_pointer': pointer, 'kind': original['kind'], 'admitted': not excluded,
                          'reason': 'RECORD_CONTEXT_EXCLUDED' if excluded else 'ORIGINAL_RECORD_CONTEXT',
                          'explicit_scope_excluded': bool(support.get('excluded_source_scope') or
                                                        support.get('whole_atom_excluded_relation_owners')),
                          'different_proved_method_owner': other_owner})
        if not excluded:
            atom = copy.deepcopy(original)
            atom['record_context'] = {'relation': 'SAME_CANONICAL_RECORD',
                                      'seed_record_pointers': sorted(seed_pointers),
                                      'method_contract_verified': False,
                                      'necessary_dependency_proven': False,
                                      'entire_task_completion_proven': False}
            result.append(atom)
    return result, decisions


def _n001_context_head(atom):
    text = atom.get('statement')
    if not isinstance(text, str):
        return set()
    head = re.match(r'\s*(?:The\s+)?([A-Za-z_]\w*)(?=[\s:.]|组件|$)', text, re.I)
    return task_subjects(head.group(1)) if head else set()


def _final_positive_focus(record, family, groups, query, contexts):
    """Apply the shared explicit-only scope after every context addition path."""
    from . import intent_scope
    check = getattr(intent_scope, 'positive_focus_support', None)
    if check is None or not query.strip():
        return groups, [], set()
    selected, decisions, excluded = {}, [], set()
    for field, values in groups.items():
        selected[field] = []
        for atom in values:
            pointer = atom.get('record_pointer')
            if pointer is None or atom.get('consumption_hint'):
                selected[field].append(atom)
                continue
            support = check(query, atom['statement'], contexts.get(pointer,
                {'scope': _scope(record), 'receivers': []}))
            if support.get('allowed') is False:
                excluded.add(pointer)
                decisions.append({'record_pointer': pointer, 'kind': atom['kind'],
                    'admitted': False, 'reason': 'FINAL_POSITIVE_FOCUS_EXCLUDED',
                    'positive_focus_support': copy.deepcopy(support),
                    'whole_statement_withheld': True})
            else:
                selected[field].append(atom)
    return selected, decisions, excluded


def _n001_coding_record_context(record, governance, candidates, seeds, query, contexts, contracts=()):
    """One admitted N001 record may carry its original context around a real seed."""
    if (not query.strip() or governance.get('coding_status') not in ('coding_default', 'coding_conditional')
            or governance.get('knowledge_status') not in ('supported', 'canonical', 'corrected')
            or governance.get('retrieval_status') not in ('reviewer_default', 'task_conditional', 'deep_only')):
        return [], [], None
    originals = {atom['record_pointer']: atom for atom in candidates}
    actual_seeds = []
    for seed in seeds:
        pointer = seed.get('record_pointer')
        original = originals.get(pointer)
        if (original is None or seed.get('consumption_hint') or seed.get('record_context')
                or seed.get('provider_context') or not set(_split_kind(original))
                or set(_split_kind(original)) - {'NSF', 'REC', 'EI'}
                or not _decision_bucket(original)):
            continue
        context = contexts.get(pointer, {'scope': _scope(record), 'receivers': []})
        roles = context.get('role_bindings', [])
        if roles and all(role.get('reference_context_only') or role.get('role') == 'AVAILABILITY_EXISTENCE'
                         or role.get('role') in ('BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')
                         for role in roles):
            continue
        support = task_support(query, original['statement'], context)
        # REC 的标题/名词相关性不能带出原事实；必须有原文行为关系支持。
        if (support.get('whole_atom_delivery_allowed') is True and
                (support.get('concrete_behavior') is True or
                 support.get('relevance_lane') == 'ORIGINAL_CONTENT')):
            actual_seeds.append(original)
    actual_seeds, _ = facet_admission(record, 'n001', actual_seeds, query)
    if not actual_seeds:
        return [], [], None
    seed_pointers = {atom['record_pointer'] for atom in actual_seeds}
    owners = {pointer: set(context.get('receivers', [])) for pointer, context in contexts.items()}
    for match in contracts:
        for pointer, role in match.get('pointer_roles', {}).items():
            if isinstance(role, dict) and role.get('role') == 'METHOD_SUBJECT' and match.get('receiver'):
                owners.setdefault(pointer, set()).add(match['receiver'])
    seed_owners = set().union(*(owners.get(pointer, set()) for pointer in seed_pointers))
    seed_heads = set().union(*(_n001_context_head(atom) for atom in actual_seeds))
    eligible = [atom for atom in candidates if atom['record_pointer'] not in seed_pointers and
                ((atom['record_pointer'] == '/native_fact' and set(_split_kind(atom)) == {'NSF'})
                 or (bool(_split_kind(atom)) and set(_split_kind(atom)) <= {'REC', 'EI'})
                 or atom.get('source_field') == 'does_not_mean')]
    admitted, decisions = facet_admission(record, 'n001', eligible, query)
    negative_clauses = query_scope(query)['negative_clauses']
    result = []
    for original in admitted:
        pointer = original['record_pointer']
        context = contexts.get(pointer, {'scope': _scope(record), 'receivers': []})
        support = task_support(query, original['statement'], context)
        other_owner = bool(seed_owners and owners.get(pointer) and not seed_owners & owners[pointer])
        head = _n001_context_head(original)
        other_subject = bool(seed_heads and head and not seed_heads & head and support.get('subject_mismatch'))
        explicit_negative = any(task_support(clause, original['statement'], context).get('whole_atom_delivery_allowed')
                                for clause in negative_clauses)
        excluded = bool(support.get('excluded_source_scope') or
                        support.get('whole_atom_excluded_relation_owners') or other_owner or other_subject or explicit_negative)
        decisions.append({'record_pointer': pointer, 'kind': original['kind'], 'admitted': not excluded,
                          'reason': 'N001_RECORD_CONTEXT_EXCLUDED' if excluded else 'N001_ORIGINAL_RECORD_CONTEXT',
                          'explicit_scope_excluded': bool(support.get('excluded_source_scope') or
                                                        support.get('whole_atom_excluded_relation_owners') or explicit_negative),
                          'different_proved_method_owner': other_owner,
                          'different_original_subject': other_subject})
        if not excluded:
            atom = copy.deepcopy(original)
            atom['record_context'] = {'relation': 'SAME_CANONICAL_RECORD',
                                      'seed_record_pointers': sorted(seed_pointers),
                                      'claim_type_unchanged': True,
                                      'method_contract_verified': False,
                                      'necessary_dependency_proven': False,
                                      'entire_task_completion_proven': False}
            result.append(atom)
    delivered = {atom['record_pointer'] for atom in result}
    withheld = [atom['record_pointer'] for atom in eligible if atom['record_pointer'] not in delivered]
    status = {'schema': 'n001-coding-single-record-context/1',
              'status': 'PARTIAL_RECORD_CONTEXT' if withheld else 'COMPLETE_ADMITTED_RECORD_CONTEXT',
              'seed_record_pointers': sorted(seed_pointers),
              'context_record_pointers': sorted(delivered), 'withheld_record_pointers': withheld,
              'budget_unit': ATOMIC_BUDGET_UNIT,
              'context_may_seed_expansion': False, 'adds_records': False,
              'method_contract_verified': False, 'necessary_dependency_proven': False,
              'entire_task_completion_proven': False}
    return result, decisions, status


def decision_card(record, family, governance, profile=None, query='', preferred_record_pointers=(), navigation_context=None, projection='coding', supported_record_pointers=(), supplement_context=None, sample_reference_context=None):
    """L1: bounded complete atoms. No authority/admission or evidence expansion."""
    _validate(record, family, governance)
    if not isinstance(query, str):
        raise ValueError('query must be a string')
    if (not isinstance(preferred_record_pointers, (list, tuple)) or len(preferred_record_pointers) > 1
            or any(not isinstance(pointer, str) for pointer in preferred_record_pointers)):
        raise ValueError('preferred_record_pointers must contain at most one original pointer')
    profile = _profile(record, profile)
    atoms = _atoms(record, family)
    all_boundaries = _boundaries(record, family)
    original_by_pointer = {atom['record_pointer']: atom for atom in atoms + all_boundaries}
    if (not isinstance(supported_record_pointers, (list, tuple))
            or len(supported_record_pointers) > len(original_by_pointer)
            or any(not isinstance(pointer, str) or pointer not in original_by_pointer
                   for pointer in supported_record_pointers)
            or len(set(supported_record_pointers)) != len(supported_record_pointers)):
        raise ValueError('supported_record_pointers must be a bounded set of unique original pointers')
    positive_query = query_scope(query)['positive_query']
    contracts = _unique(requested_contracts(record, family, query)) if query.strip() else []
    mapped_pointers = list(dict.fromkeys(pointer for match in contracts
                                       for pointer in (match['record_pointers'] if match['mapping_status'] == 'TYPED_CONTRACT' else [])
                                       + match.get('availability_record_pointers', []) + match.get('context_record_pointers', [])))
    context_pointers = {pointer for match in contracts for pointer in match.get('context_record_pointers', [])}
    excluded_context_pointers = {pointer for match in contracts for pointer in match.get('needed_context_excluded', [])}
    required_context_pointers = context_pointers | excluded_context_pointers
    required_context_pointers |= {edge['required_record_pointer'] for match in contracts
                                 for edge in match.get('context_dependency_edges', [])}
    context_admission_decisions = [decision for match in contracts for decision in match.get('context_admission', [])]
    alias_subject = any(normalize_symbol(query) == match.get('query_name_resolution', {}).get('query_name') and
                        match.get('query_name_resolution', {}).get('basis') ==
                        'UNIQUE_ACCEPTED_ORIGINAL_SOURCE_METHOD_SUBJECT' and
                        match['query_name_resolution'].get('verified_subject_record_pointers')
                        for match in contracts)
    symbol_lookup = bool(query.strip() and
                         (normalize_symbol(query) in contract_symbols(record, family) or alias_subject))
    semantic_scope = _claim_contexts(record, family, atoms + all_boundaries) if query.strip() and not symbol_lookup else {}
    reference_context = None
    if sample_reference_context is not None and not symbol_lookup:
        reference_context = {**sample_reference_context, 'atom_contexts': semantic_scope}
    facet_options = {'reference_context': reference_context, 'atom_contexts': semantic_scope}
    admitted_atoms, facet_decisions = facet_admission(record, family, atoms, query, **facet_options)
    allowed_pointers = {atom['record_pointer'] for atom in admitted_atoms}
    admitted_by_pointer = {atom['record_pointer']: atom for atom in admitted_atoms}
    dt.record(record['id'],'SELECTION_MODE',selection_mode='SYMBOL_MAPPING' if symbol_lookup else 'ATOM_SELECTION')
    if symbol_lookup and not mapped_pointers:
        dt.terminal(record['id'],'SYMBOL_MAPPING','IDENTITY_NO_MAPPED_DECISION_ATOM')
    for pointer in mapped_pointers:
        dt.atom(record['id'],pointer,'MAPPED_POINTER',admitted=pointer in allowed_pointers)
    task_decisions = []

    def task_filter(values):
        if not query.strip() or symbol_lookup:
            return values
        selected = []
        for atom in values:
            if atom.get('kind') == 'PROJECT_POLICY':
                policies, policy_decisions = select_project_policy_atoms(record, family, query, projection, [atom], governance)
                task_decisions.extend(policy_decisions)
                selected.extend(policies)
                continue
            pointer = atom.get('record_pointer')
            context = semantic_scope.get(pointer, {'scope': _scope(record), 'receivers': []})
            support = task_support(query, atom['statement'], context)
            if pointer is not None:
                dt.atom(record['id'],pointer,'WHOLE_ATOM_TASK_FILTER',kind=atom.get('kind'),
                    supported=support.get('supported'),whole_atom_delivery_allowed=support.get('whole_atom_delivery_allowed',False),
                    subject_mismatch=support.get('subject_mismatch'),excluded_source_scope=support.get('excluded_source_scope'))
            task_decisions.append({'record_pointer': pointer, 'kind': atom.get('kind'),
                                   'admitted': bool(support.get('whole_atom_delivery_allowed', False)), 'support': support,
                                   'consumption_hint': bool(atom.get('consumption_hint'))})
            if support.get('whole_atom_delivery_allowed', False):
                if support.get('bounded_route_stage'):
                    reference = bounded_input_route_reference(record, atom, query, context=context,
                        **(sample_reference_context or {}))
                    if reference is None:
                        task_decisions[-1]['admitted'] = False
                        task_decisions[-1]['reason'] = 'BOUNDED_ROUTE_SOURCE_SUBJECT_NOT_VERIFIED'
                        continue
                    atom = {**atom, 'bounded_route_reference': reference}
                selected.append(atom)
        return selected

    preferred_atoms, preferred_facets = [], []
    if query.strip() and not symbol_lookup:
        supported = [pointer for pointer in supported_record_pointers
                     if set(_split_kind(original_by_pointer[pointer])) &
                     {'NSF', 'RV', 'EI', 'REC', 'UNK', 'BOUNDARY', 'PROJECT_POLICY'}]
        if projection == 'reviewer' and family == 'core':
            supported = list(dict.fromkeys(supported + [atom['record_pointer'] for atom in atoms + all_boundaries
                                                        if atom['kind'] in ('UNK', 'BOUNDARY')]))
        candidates = [original_by_pointer[pointer] for pointer in
                      dict.fromkeys((*preferred_record_pointers, *supported))
                      if pointer in original_by_pointer]
        preferred_atoms, preferred_facets = facet_admission(record, family, candidates, query, **facet_options)
        preferred_atoms = task_filter(preferred_atoms)
    preferred_decisions = [atom for atom in preferred_atoms if atom['kind'] != 'BOUNDARY' and _decision_bucket(atom)]
    preferred_boundaries = [atom for atom in preferred_atoms if atom['kind'] in ('UNK', 'BOUNDARY')]
    preferred_policies = [atom for atom in preferred_atoms if atom['kind'] == 'PROJECT_POLICY']

    if contracts and symbol_lookup:
        # API identity is not a method answer. Only explicit existing whole atoms
        # can bypass lexical selection; a catalog gap is left visibly empty.
        decisions = [admitted_by_pointer[pointer] for pointer in mapped_pointers
                     if pointer in admitted_by_pointer and _decision_bucket(admitted_by_pointer[pointer])]
    else:
        decisions = [admitted_by_pointer[atom['record_pointer']]
                     for atom in _select_atoms(atoms, profile, query, semantic_scope,
                                              reviewer_task=projection == 'reviewer' and family == 'core')
                     if atom['record_pointer'] in allowed_pointers]
        decisions = _unique([admitted_by_pointer[pointer] for pointer in mapped_pointers
                             if pointer in admitted_by_pointer and _decision_bucket(admitted_by_pointer[pointer])] + decisions)
    decisions = _unique(task_filter(decisions) + preferred_decisions)
    # 只有直接交付的原语义 atom 可以带出同记录建议；导航/存在性/上下文不能继续扩张。
    typed_subjects = direct_contract_seed_pointers(contracts)
    record_seeds = [atom for atom in decisions if not atom.get('consumption_hint') and
                    not atom.get('legacy_evidence_status') and
                    (not symbol_lookup or atom['record_pointer'] in typed_subjects)]
    if not symbol_lookup:
        record_seeds = [atom for atom in record_seeds if not (
            semantic_scope.get(atom['record_pointer'], {}).get('role_bindings') and
            all(role.get('reference_context_only') or role.get('role') == 'AVAILABILITY_EXISTENCE'
                for role in semantic_scope[atom['record_pointer']]['role_bindings']))]
    accepted_context_seed = symbol_lookup and any(
        match.get('mapping_status') == 'BOUNDED_CONTEXT' and match.get('reference_context_only') is True and
        any(pointer in allowed_pointers for pointer in match.get('context_record_pointers', []))
        for match in contracts)
    has_task_seed = bool(query.strip() and (decisions or preferred_boundaries or accepted_context_seed))
    dependency_contracts = []
    if query.strip() and not symbol_lookup:
        main_pointers = {atom['record_pointer'] for atom in decisions}
        for candidate in contract_symbols(record, family):
            for match in contract_matches(record, family, candidate):
                if (main_pointers.intersection(match.get('record_pointers', [])) or
                        any(main_pointers.intersection(context.get('basis_record_pointers', []))
                            for context in match.get('context_pointer_bindings', []))):
                    dependency_contracts.append(match)
        dependency_contracts = _unique(dependency_contracts)
        dependency_contexts = _unique([context for match in dependency_contracts
                                      for context in match.get('context_pointer_bindings', [])
                                      if main_pointers.intersection(context['basis_record_pointers'])])
        required_context_pointers |= {context['record_pointer'] for context in dependency_contexts}
        required_context_pointers |= {edge['required_record_pointer'] for match in dependency_contracts
                                     for edge in match.get('context_dependency_edges', [])
                                     if edge['dependent_record_pointer'] in main_pointers or
                                     any(edge in context.get('dependency_edges', [])
                                         for context in dependency_contexts)}
        admitted_contexts, dependency_admission = context_admission(record, family, dependency_contexts, query)
        context_admission_decisions += dependency_admission
        excluded_context_pointers |= {decision['record_pointer'] for decision in dependency_admission if not decision['admitted']}
        dependency_pointers = {context['record_pointer'] for context in admitted_contexts}
        context_pointers |= dependency_pointers
        decisions = _unique(decisions + [admitted_by_pointer[pointer] for pointer in sorted(dependency_pointers)
                                         if pointer in admitted_by_pointer and
                                         _decision_bucket(admitted_by_pointer[pointer])])
    source_contexts = []
    if query.strip() and decisions:
        # 精确同源范围只交付有界上下文，不提升为方法或必要因果证明。
        local_contexts = bounded_source_context(record, family, [atom['record_pointer'] for atom in decisions])
        source_contexts, local_admission = context_admission(record, family, local_contexts, query)
        context_admission_decisions += local_admission
        required_context_pointers |= {context['record_pointer'] for context in local_contexts}
        excluded_context_pointers |= {decision['record_pointer'] for decision in local_admission if not decision['admitted']}
        local_pointers = {context['record_pointer'] for context in source_contexts}
        context_pointers |= local_pointers
        decisions = _unique(decisions + [admitted_by_pointer[pointer] for pointer in sorted(local_pointers)
                                         if pointer in admitted_by_pointer and _decision_bucket(admitted_by_pointer[pointer])])
    if projection == 'reviewer' and not symbol_lookup:
        # 只用原任务直接 seed 取回同记录 provider 原事实；新上下文不递归扩张。
        provider_atoms, _ = provider_context_atoms(record, family, query, record_seeds)
        represented_provider = {atom['record_pointer'] for atom in decisions}
        decisions += [atom for atom in provider_atoms if atom['record_pointer'] not in represented_provider]
    n001_context_status, n001_context_boundaries = None, []
    if projection == 'reviewer':
        record_context, record_context_admission = _record_context_atoms(
            record, family, atoms, record_seeds, query, semantic_scope, contracts)
    elif projection == 'coding' and family == 'n001':
        n001_context, record_context_admission, n001_context_status = _n001_coding_record_context(
            record, governance, atoms + all_boundaries, record_seeds, query, semantic_scope, contracts)
        record_context = [atom for atom in n001_context if atom['kind'] != 'BOUNDARY']
        n001_context_boundaries = [atom for atom in n001_context if atom['kind'] == 'BOUNDARY']
    else:
        record_context, record_context_admission = [], []
    represented_decisions = {atom['record_pointer'] for atom in decisions}
    decisions += [atom for atom in record_context if atom['record_pointer'] not in represented_decisions]
    if family == 'legacy' and record_seeds:
        represented_legacy = {atom['record_pointer'] for atom in decisions}
        for atom in atoms:
            if (atom['record_pointer'] in ('/status', '/details/runtime_tested', '/details/dedicated_tested')
                    and atom['record_pointer'] not in represented_legacy):
                status_atom = copy.deepcopy(atom)
                status_atom['legacy_evidence_status'] = True
                status_atom['record_context'] = {'relation': 'ORIGINAL_RECORD_EVIDENCE_STATUS',
                    'seed_record_pointers': [seed['record_pointer'] for seed in record_seeds],
                    'native_fact_promotion': False, 'runtime_verification_claimed': False}
                decisions.append(status_atom)
            elif (record.get('entry_type', '').lower() == 'correction'
                  and atom['record_pointer'].split('/')[2:3] in
                      (['subsequent_evidence'], ['replacement'], ['correction_scope'])
                  and atom['record_pointer'] not in represented_legacy):
                evidence_atom = copy.deepcopy(atom)
                evidence_atom['legacy_correction_evidence_context'] = True
                evidence_atom['record_context'] = {'relation': 'ORIGINAL_CORRECTION_EVIDENCE_CHAIN',
                    'seed_record_pointers': [seed['record_pointer'] for seed in record_seeds],
                    'native_fact_promotion': False, 'necessity_enumeration_proven': False}
                decisions.append(evidence_atom)
    original_supplement_status = None
    supplemental = []
    if projection == 'reviewer' and family == 'core' and supplement_context is not None:
        supplemental, original_supplement_status = supplement_atoms(
            record, family, query, record_seeds, supplement_context, semantic_scope)
    binding_contracts = _unique(contracts + dependency_contracts)
    for atom in decisions:
        if atom.get('record_context') or atom.get('provider_context') or atom.get('supplement_context'):
            continue
        bindings = [match for match in binding_contracts if atom['record_pointer'] in
                    match['record_pointers'] + match.get('availability_record_pointers', []) + match.get('context_record_pointers', [])]
        if bindings:
            atom['contract_bindings'] = _unique([{'symbol': match['symbol'], 'receiver': match['receiver'],
                                          'mapping_basis': match['mapping_basis'],
                                          'binding_kind': 'availability_existence' if atom['record_pointer'] in match.get('availability_record_pointers', []) else 'original_pointer_dependency_context' if atom['record_pointer'] in match.get('context_record_pointers', []) else match.get('pointer_roles', {}).get(atom['record_pointer'], {}).get('binding_kind', match.get('binding_kind', 'typed_behavioral_contract')),
                                          'pointer_role': role,
                                          'full_method_contract_verified': False}
                                         for match in bindings
                                         for role in (_unique(
                                             ([match['pointer_roles'][atom['record_pointer']]]
                                              if match.get('pointer_roles', {}).get(atom['record_pointer']) is not None else []) +
                                             [context for context in match.get('context_pointer_bindings', [])
                                              if context['record_pointer'] == atom['record_pointer']]) or [None])])
    selection = {}
    if query.strip():
        scores = _query_scores(atoms, positive_query)
        original_indexes = {atom['record_pointer']: index for index, atom in enumerate(atoms)}
        mandatory = {atoms[index]['record_pointer'] for index in profile.get('claim_indexes', [])}
        reviewer_task = projection == 'reviewer' and family == 'core'
        selection = {'query_selection': {'method': ('reviewer_whole_original_task_atoms_with_profile_order/2.13' if reviewer_task else
                     'symbol_contract_then_whole_atom_task_support_with_lexical_order/2.13'),
                     'nonmatching_nonmandatory_atoms_not_filled': True,
                     **({'profile_is_order_only': True} if reviewer_task else {}),
                     'selected': [{'record_pointer': atom['record_pointer'],
                                   'mandatory_profile_atom': atom['record_pointer'] in mandatory and not reviewer_task,
                                   **scores.get(original_indexes[atom['record_pointer']], {'score': 0, 'strong': False, 'matched_terms': []})}
                                  for atom in decisions]}}
    defaults = [index for index, atom in enumerate(all_boundaries)
                if not isinstance(atom['statement'], str) or not atom['statement'].startswith(WRAPPER_BOUNDARY_PREFIXES)]
    indexes = list(range(len(all_boundaries))) if has_task_seed else defaults if symbol_lookup else profile.get(
        'boundary_indexes', defaults if query.strip() else defaults[:3])
    if any(type(index) is not int or index < 0 or index >= len(all_boundaries) for index in indexes):
        raise ValueError('profile boundary index out of bounds')
    boundaries, boundary_facets = facet_admission(record, family, [all_boundaries[index] for index in indexes], query)
    if projection == 'reviewer' and record_seeds:
        boundaries, record_limits_admission = _record_context_atoms(
            record, family, boundaries, record_seeds, query, semantic_scope, contracts)
        record_context_admission += record_limits_admission
    elif projection == 'coding' and family == 'legacy' and record_seeds and query.strip():
        # 原限制随合法行为陪送；未知项仍须独立准入，不借限制补出新事实。
        original_limits = [atom for atom in boundaries if atom['kind'] == 'BOUNDARY']
        limits, record_limits_admission = _record_context_atoms(
            record, family, original_limits, record_seeds, query, semantic_scope, contracts)
        record_context_admission += record_limits_admission
        boundaries = limits + task_filter([atom for atom in boundaries if atom['kind'] != 'BOUNDARY'])
    elif has_task_seed:
        boundaries = task_filter(boundaries)
    boundaries = _unique_whole_atoms(boundaries + n001_context_boundaries)
    unknowns = [atom for atom in atoms if atom['kind'] == 'UNK']
    hints = _hints(profile, 'critical_boundary')
    rejected = {item['record_pointer'] for item in facet_decisions if not item['admitted']}
    # A compound hint depending on an excluded sample cannot reintroduce it.
    hints = [hint for hint in hints if not rejected.intersection(hint.get('basis_record_pointers', []))]
    hints, hint_facets = facet_admission(record, family, hints, query)
    hints = task_filter(hints)
    unknowns = [admitted_by_pointer[a['record_pointer']] for a in unknowns if a['record_pointer'] in allowed_pointers]
    required_unknowns = [atom for atom in unknowns if atom['record_pointer'] in context_pointers]
    # 未知项保留真实直接任务支持与已证明 context；默认浏览保留原展示约定。
    boundaries = _unique_whole_atoms(required_unknowns + preferred_boundaries + boundaries if has_task_seed else
                         required_unknowns + preferred_boundaries + task_filter(
                             _unique(boundaries + ([] if query.strip() else unknowns[:2]))))
    policies = [admitted_by_pointer[atom['record_pointer']] for atom in atoms
                if atom['kind'] == 'PROJECT_POLICY' and atom['record_pointer'] in allowed_pointers]
    policies, policy_decisions = select_project_policy_atoms(record, family, query, projection, policies, governance)
    task_decisions.extend(policy_decisions)
    policies = _unique(policies + preferred_policies)
    if original_supplement_status is not None:
        independent = {atom['record_pointer'] for atom in decisions + boundaries + policies
                       if 'record_pointer' in atom}
        additions = [atom for atom in supplemental if atom['record_pointer'] not in independent]
        original_supplement_status['supplement_only_record_pointers'] = [atom['record_pointer'] for atom in additions]
        # 已有未知边界不能变成可延期补充；新增 UNK 仍放在边界组。
        boundaries += [atom for atom in additions if atom['kind'] == 'UNK']
        decision_additions = [atom for atom in additions if atom['kind'] != 'UNK']
        decisions += decision_additions
        if selection:
            selection['query_selection']['selected'] += [
                {'record_pointer': atom['record_pointer'], 'mandatory_profile_atom': False,
                 **scores.get(original_indexes[atom['record_pointer']], {'score': 0, 'strong': False, 'matched_terms': []})}
                for atom in decision_additions]
    focused, focus_decisions, focus_excluded = _final_positive_focus(record, family,
        {'decision': decisions, 'critical_boundary': boundaries, 'project_policy_questions': policies},
        query, semantic_scope)
    decisions, boundaries, policies = (focused[field] for field in
        ('decision', 'critical_boundary', 'project_policy_questions'))
    task_decisions.extend(focus_decisions)
    excluded_context_pointers |= focus_excluded
    record_seeds = [atom for atom in record_seeds if atom['record_pointer'] not in focus_excluded]
    if focus_excluded and selection:
        selection['query_selection']['selected'] = [row for row in selection['query_selection']['selected']
                                                    if row['record_pointer'] not in focus_excluded]
    if focus_excluded and original_supplement_status is not None:
        kept_relations = []
        for relation in original_supplement_status.get('relations', []):
            if relation.get('record_pointer') in focus_excluded:
                original_supplement_status.setdefault('gaps', []).append({**copy.deepcopy(relation),
                    'delivered': False, 'reason': 'EXPLICIT_POSITIVE_FOCUS_EXCLUDED'})
            else:
                kept_relations.append(relation)
        original_supplement_status['relations'] = kept_relations
        original_supplement_status['supplement_only_record_pointers'] = [pointer for pointer in
            original_supplement_status.get('supplement_only_record_pointers', []) if pointer not in focus_excluded]
    if n001_context_status is not None and focus_excluded:
        n001_context_status['status'] = 'PARTIAL_RECORD_CONTEXT'
        for field in ('seed_record_pointers', 'context_record_pointers'):
            n001_context_status[field] = [pointer for pointer in n001_context_status[field]
                                         if pointer not in focus_excluded]
        n001_context_status['withheld_record_pointers'] = sorted(
            set(n001_context_status['withheld_record_pointers']) | focus_excluded)
    symbols = _symbols(record, family, profile, decisions)
    for match in contracts:
        symbols.insert(0, {'symbol': match['symbol'], 'receiver': match['receiver'],
                           'role': match.get('binding_kind', match['mapping_status']),
                           'basis_record_pointers': match['record_pointers'] + match.get('availability_record_pointers', []),
                           'context_record_pointers': match.get('context_record_pointers', [])})
    # 显式 receiver binding 必须即使有较多 API token 也留在 L1。
    bound = [item for item in symbols if item.get('receiver')]
    selected_symbols = _unique(bound + [item for item in symbols if not item.get('receiver')][:12])
    represented = {atom['record_pointer'] for atom in decisions + boundaries + policies
                   if 'record_pointer' in atom}
    omitted = [atom for atom in atoms if atom['record_pointer'] not in represented]
    boundary_pointers = {atom['record_pointer'] for atom in all_boundaries}
    policy_hints, policy_facets = facet_admission(record, family, _hints(profile, 'project_policy_questions'), query)
    policy_hints = [hint for hint in policy_hints if not rejected.intersection(hint.get('basis_record_pointers', []))]
    # 派生 hint 不形成政策支持；本通道只交付经过同一谓词的原 whole atom。
    policy_hints = []
    unresolved_context = sorted({pointer for match in binding_contracts for pointer in match.get('context_closure_gaps', [])}
                                | (required_context_pointers - represented) | excluded_context_pointers)
    context_bindings = _unique([binding for match in binding_contracts for binding in match.get('context_pointer_bindings', [])
                                if binding['record_pointer'] in represented] +
                               [binding for binding in source_contexts if binding['record_pointer'] in represented])
    source_scope = compact_semantic_scope(record, family,
        {'decision': decisions, 'critical_boundary': boundaries,
         'project_policy_questions': policies + policy_hints}, query,
        (rejected | excluded_context_pointers) - set(original_supplement_status.get('supplement_only_record_pointers', []) if original_supplement_status else []),
        navigation_context=navigation_context, supplement_context=supplement_context)
    needed_semantic_scope = (source_scope.get('needed_scope_missing', []) if isinstance(source_scope, dict)
                             and source_scope.get('scope_schema') == SCOPE_SCHEMA else [])
    for atom in decisions:
        for binding in atom.get('contract_bindings', []):
            if isinstance(binding.get('pointer_role'), dict):
                binding['pointer_role'] = shared_scope_references(binding['pointer_role'], source_scope)
    card = {'projection_schema': SCHEMA, 'level': 1, 'family': family,
            'id': record['id'], 'title': record.get('title', ''), 'record_sha256': record_digest(record),
            'when_relevant': scope_navigation(_when(record, family, profile), record, family, query), 'decision': decisions,
            'exact_symbols': selected_symbols, 'critical_boundary': boundaries,
            'consumption_hints': hints,
            'consumption_hint_metadata': {'source': 'PROJECTION_PROFILE', 'evidence_class': 'NON_CANONICAL_METADATA',
                                          'task_or_method_proof': False},
            'project_policy_questions': policies + policy_hints,
            'project_policy_requested': project_policy_intent(query)['requested'], 'policy_resolved': False,
            'evidence_strength': _strength(record, family, atoms),
            'source_scope': source_scope,
            'governance': _governance(record, governance),
            'omission': {'typed_atoms': len(omitted), 'typed_atoms_by_kind': dict(Counter(a['kind'] for a in omitted)),
                         'boundaries': len(all_boundaries) - sum(atom.get('record_pointer') in boundary_pointers for atom in boundaries),
                         'exact_symbols': len(symbols) - len(selected_symbols),
                         'whole_atoms_preserved': True, 'full_record_delivered': False},
            'expansion': _expansion(record['id']),
            'facet_admission': {'method': 'whole_atom_sample_identity/2.13',
                                'decisions': compact_diagnostics(facet_decisions + boundary_facets + hint_facets + policy_facets + context_admission_decisions + preferred_facets),
                                'excluded_atom_count': len(rejected)},
            'task_admission': {'method': 'actual_original_atom_task_relation/2.13',
                               'exact_symbol_contract_path': bool(symbol_lookup), 'decisions': compact_task_diagnostics(task_decisions),
                               **({'entire_task_completion_proven': False} if query.strip() and not symbol_lookup else {})},
            'record_context_delivery': {'relation': 'SAME_CANONICAL_RECORD',
                                        'seed_record_pointers': [atom['record_pointer'] for atom in record_seeds],
                                        'admission': record_context_admission,
                                        'method_contract_verified': False,
                                        'necessary_dependency_proven': False,
                                        'entire_task_completion_proven': False},
            'context_closure': {'status': 'PARTIAL_CONTEXT' if unresolved_context or needed_semantic_scope else 'BOUNDED_ORIGINAL_POINTER_CONTEXT',
                                'bindings': shared_scope_references(context_bindings, source_scope), 'needed_context_missing': unresolved_context,
                                 'needed_context_excluded': sorted(excluded_context_pointers),
                                 'admission': compact_diagnostics(context_admission_decisions),
                                 'identified_necessary_scope_dependencies_complete': (source_scope.get('identified_necessary_scope_dependencies_complete', True)
                                     if isinstance(source_scope, dict) else True),
                                 'scope_dependency_resolution_complete': not bool(needed_semantic_scope),
                                 'needed_semantic_scope_node_count': len(needed_semantic_scope),
                                'universal_method_contract_verified': False},
            'contract_mapping': delivery_contract_mappings(contracts, source_scope), **selection}
    sample_reference_assessment(card)
    if n001_context_status is not None:
        card['n001_coding_context'] = n001_context_status
    if original_supplement_status is not None and (original_supplement_status['relations'] or original_supplement_status['gaps']):
        card['original_supplement_context'] = original_supplement_status
        card['context_closure']['original_supplement_context_complete'] = not bool(original_supplement_status['gaps'])
        if original_supplement_status['gaps']:
            card['context_closure']['status'] = 'PARTIAL_CONTEXT'
    if not query.strip():
        # 空任务只是默认浏览，无任务推断和依赖图，避免每张卡重复携带空证明。
        card.pop('task_admission')
        if not context_bindings and not unresolved_context:
            card.pop('context_closure')
    for slot,values in (('decision',decisions),('critical_boundary',boundaries),('project_policy_questions',policies+policy_hints)):
        for atom in values:
            if atom.get('record_pointer') is not None:
                dt.atom(record['id'],atom['record_pointer'],'VIEW_SELECTED',kind=atom['kind'],selected=True,delivered_slot=slot)
    return card


def supplement_subset(card, record, included_pointers, query='', navigation_context=None, supplement_context=None):
    """Budget only optional whole supplements, then rebuild card-local Scope refs.

    This is a projection of already selected atoms, never a second retrieval or
    another task selection. Independently selected atoms cannot be removed here.
    """
    from .delivery_wire import expand_l1_metadata, project_l1_card, PUBLIC_PROFILE
    original_wire = card.get('wire_projection', {})
    result = expand_l1_metadata(card)
    if result.get('id') != record.get('id') or result.get('record_sha256') != record_digest(record):
        raise ValueError('Supplement budget record identity mismatch')
    status = result.get('original_supplement_context', {})
    optional = set(status.get('supplement_only_record_pointers', []))
    included = set(included_pointers)
    if any(not isinstance(pointer, str) for pointer in included) or not included <= optional:
        raise ValueError('Only original supplement-only pointers may be budgeted')
    removed = optional - included
    if not removed:
        return copy.deepcopy(card)
    verified, errors = delivered_original_atoms(record, result.get('family'), result)
    if errors or not optional <= set(verified):
        raise ValueError('Supplement budget requires actual whole original atoms')
    seeds = set(result.get('record_context_delivery', {}).get('seed_record_pointers', []))
    if removed & seeds:
        raise ValueError('An independently selected seed cannot be budgeted as a supplement')
    if any(atom.get('record_pointer') in removed and not atom.get('supplement_context')
           for field in ('decision', 'critical_boundary', 'project_policy_questions')
           for atom in result.get(field, [])):
        raise ValueError('An independently delivered atom cannot be budgeted as a supplement')
    for field in ('decision', 'critical_boundary', 'project_policy_questions'):
        result[field] = [atom for atom in result.get(field, []) if atom.get('record_pointer') not in removed]
    relations = []
    for relation in status.get('relations', []):
        if relation.get('record_pointer') in removed:
            status.setdefault('gaps', []).append({**copy.deepcopy(relation), 'delivered': False,
                'reason': 'WHOLE_ORIGINAL_SUPPLEMENT_EXCEEDS_PAYLOAD_BUDGET'})
        else:
            relations.append(relation)
    status['relations'] = relations
    status['supplement_only_record_pointers'] = sorted(included)
    status['withheld_context_delivered'] = False
    closure = result.setdefault('context_closure', {})
    closure['status'] = 'PARTIAL_CONTEXT'
    closure['original_supplement_context_complete'] = False
    excluded = set(closure.get('needed_context_excluded', []))
    result['source_scope'] = compact_semantic_scope(record, result['family'],
        {field: result.get(field, []) for field in ('decision', 'critical_boundary', 'project_policy_questions')},
        query, excluded, navigation_context=navigation_context, supplement_context=supplement_context)
    scope = result['source_scope']
    if isinstance(scope, dict) and scope.get('scope_schema') == SCOPE_SCHEMA:
        closure['identified_necessary_scope_dependencies_complete'] = scope['identified_necessary_scope_dependencies_complete']
        closure['scope_dependency_resolution_complete'] = scope['scope_dependency_resolution_complete']
        closure['needed_semantic_scope_node_count'] = len(scope['needed_scope_missing'])
    for atom in result.get('decision', []):
        for binding in atom.get('contract_bindings', []):
            if isinstance(binding.get('pointer_role'), dict):
                binding['pointer_role'] = shared_scope_references(binding['pointer_role'], scope)
    if isinstance(result.get('query_selection', {}).get('selected'), list):
        result['query_selection']['selected'] = [row for row in result['query_selection']['selected'] if row.get('record_pointer') not in removed]
    omission = result.setdefault('omission', {})
    omission['typed_atoms'] = omission.get('typed_atoms', 0) + len(removed)
    counts = omission.setdefault('typed_atoms_by_kind', {})
    for pointer in removed:
        kind = verified[pointer]['kind']
        counts[kind] = counts.get(kind, 0) + 1
    # 原 wire 的共享表已经展开；重打包会重建局部引用和绑定组，不能沿用旧下标。
    sample_reference_assessment(result)
    result.pop('wire_projection', None)
    return project_l1_card(result, public_contract=original_wire.get('profile') == PUBLIC_PROFILE) if original_wire else result


def original_condition_associations(record, source_reader):
    """Bind complete original source limits to their exact NSF owner only.

    JSON flags, matching words, shared files and recommendations cannot create
    this relation. A source limit with multiple exact owners keeps all owners;
    unassigned canonical boundaries remain global and conservative.
    """
    from .scope_navigation import ExactSourceReader, ProofError, triple
    if not isinstance(source_reader, ExactSourceReader):
        return {'boundary_owners': {}, 'bindings': []}
    boundaries = _boundaries(record, 'core')
    owners, bindings = {}, []
    source_kinds = {'NSF': 'NSF', 'DirectSourceFact': 'NSF', 'DirectLuaSourceFact': 'NSF',
                    'EI': 'EI', 'REC': 'REC', 'UNK': 'UNK', 'PROJECT_POLICY': 'PROJECT_POLICY'}
    for index, claim in enumerate(record.get('claims', [])):
        if claim.get('kind') != 'NSF':
            continue
        for ref in claim.get('evidence_refs', []):
            try:
                node = source_reader.read(ref)
            except (ProofError, KeyError, IndexError, TypeError, ValueError):
                continue
            if not isinstance(node, dict) or node.get('statement') != claim.get('statement'):
                continue
            kinds = [source_kinds[node[key]] for key in ('kind', 'claim_type', 'claim_kind', 'classification')
                     if node.get(key) in source_kinds]
            if not kinds or set(kinds) != {'NSF'}:
                continue
            conditions = {}
            for field in ('limits', 'does_not_prove'):
                values = node.get(field)
                if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                    continue
                for limit_index, value in enumerate(values):
                    for boundary in boundaries:
                        if boundary['statement'] == value:
                            pointer = boundary['record_pointer']
                            owner = f'/claims/{index}'
                            owners.setdefault(pointer, set()).add(owner)
                            conditions.setdefault(pointer, []).append(ref['pointer'] + '/' + field + '/' + str(limit_index))
            if conditions:
                bindings.append({'owner_record_pointer': f'/claims/{index}', 'claim_kind': 'NSF',
                    'whole_statement_sha256': record_digest({'statement': claim['statement']}),
                    'source_reference': triple(ref), 'source_condition_pointers': conditions,
                    'relation': 'EXACT_ORIGINAL_SOURCE_FACT_DECLARED_LIMIT',
                    'dependency_enumeration_exhaustive': False})
    return {'boundary_owners': {pointer: sorted(values) for pointer, values in owners.items()},
            'bindings': _unique(bindings)}


def atomic_delivery_plan(card, record, query='', navigation_context=None, supplement_context=None,
                         source_reader=None):
    """Partition already admitted task seeds, retaining conservative context.

    No new task selection, retrieval or evidence admission happens here. Source
    adjacency is not a necessary edge. Unresolved adjacent context may only be
    deferred with a visible unknown closure gap, never labelled unnecessary.
    """
    from .delivery_wire import expand_l1_metadata
    decoded = expand_l1_metadata(card)
    family = decoded.get('family')
    if (not query.strip() or decoded.get('projection_schema') != SCHEMA
            or decoded.get('level') != 1 or family not in FAMILIES):
        raise ValueError('Atomic budgeting requires an original task decision card')
    verified, errors = delivered_original_atoms(record, family, decoded)
    if errors or not verified:
        raise ValueError('Atomic budgeting requires verified whole original atoms')
    groups = {field: decoded.get(field, []) for field in
              ('decision', 'critical_boundary', 'project_policy_questions')}
    seeds = set(decoded.get('record_context_delivery', {}).get('seed_record_pointers', []))
    if not seeds:
        seeds = set(decoded.get('delivery_admission', {}).get('supported_record_pointers', []))
    seeds |= set(decoded.get('delivery_admission', {}).get('supported_policy_record_pointers', []))
    ordered = []
    for field in ('decision', 'project_policy_questions'):
        for atom in groups[field]:
            pointer = atom.get('record_pointer')
            if (pointer in seeds and pointer in verified and pointer not in ordered
                    and not any(atom.get(key) for key in
                                ('record_context', 'provider_context', 'supplement_context', 'consumption_hint'))
                    and not set(_split_kind(atom)) & {'UNK', 'BOUNDARY', HISTORY}):
                ordered.append(pointer)
    if not ordered:
        raise ValueError('No independent admitted task seed for atomic budgeting')
    edges = []

    def dependencies(value):
        if isinstance(value, list):
            for child in value:
                dependencies(child)
        elif isinstance(value, dict):
            if {'dependent_record_pointer', 'required_record_pointer'} <= value.keys():
                edges.append({key: value[key] for key in
                              ('dependent_record_pointer', 'required_record_pointer')})
            for key, child in value.items():
                if key not in ('statement', 'source_scope', 'original_scope', 'shared_metadata'):
                    dependencies(child)
    dependencies(decoded)
    bindings = list(decoded.get('context_closure', {}).get('bindings', []))
    for match in decoded.get('contract_mapping', []):
        bindings.extend(match.get('context_pointer_bindings', []))
    for atom in groups['decision']:
        if isinstance(atom.get('provider_context'), dict):
            bindings.append({'record_pointer': atom.get('record_pointer'), **atom['provider_context']})
    for binding in bindings:
        pointer = binding.get('record_pointer')
        if not isinstance(pointer, str):
            continue
        # Exact citations, shared files and METHOD_SOURCE_LEAF association prove
        # provenance, not semantic necessity. Explicit back-reference edges are
        # already collected above; only independently verified necessity adds
        # an additional requirement here.
        if binding.get('necessary_dependency_verified') is True:
            for parent in binding.get('basis_record_pointers', []):
                edges.append({'dependent_record_pointer': parent, 'required_record_pointer': pointer})
            for parent in binding.get('required_basis_record_pointers', []):
                edges.append({'dependent_record_pointer': pointer, 'required_record_pointer': parent})
    closure = decoded.get('context_closure', {})
    scope_plan = scope_dependency_plan(record, family, groups, query,
        closure.get('needed_context_excluded', []), navigation_context=navigation_context,
        supplement_context=supplement_context)
    edges.extend(scope_plan['edges'])
    conditions = original_condition_associations(record, source_reader) if family == 'core' else {
        'boundary_owners': {}, 'bindings': []}
    for pointer, condition_owners in conditions['boundary_owners'].items():
        for owner in condition_owners:
            edges.append({'dependent_record_pointer': owner, 'required_record_pointer': pointer})
    adjacent = {binding.get('record_pointer') for binding in bindings}
    context_order = []
    for atom in groups['decision']:
        pointer = atom.get('record_pointer')
        if (pointer in verified and pointer not in ordered and pointer not in context_order
                and not set(_split_kind(atom)) & {'UNK', 'BOUNDARY', HISTORY}
                and not atom.get('legacy_evidence_status')
                and not atom.get('legacy_correction_evidence_context')
                and (pointer in adjacent or any(atom.get(key) for key in
                     ('record_context', 'provider_context', 'supplement_context')))):
            context_order.append(pointer)
    # Unknown facts and every original selected boundary are conservative parts
    # of every seed. Unattributed context is not silently discarded: it remains
    # an explicit deferred unit with unknown necessity and a partial closure.
    protected = set(verified) - set(ordered) - set(context_order) - set(conditions['boundary_owners'])
    units = atom_closure_units(verified, ordered, protected, edges)
    context_units = atom_closure_units(verified, context_order, protected, edges)
    return {'schema': 'dst-atomic-delivery-plan/1', 'id': record['id'],
            'record_sha256': record_digest(record), 'input_card_sha256': record_digest(card),
            'seed_record_pointers': ordered, 'protected_record_pointers': sorted(protected),
            'units': units, 'context_units': context_units, 'context_record_pointers': context_order,
            'dependency_edges': _unique(edges),
            'original_condition_associations': conditions,
            'unresolved_scope_dependencies': scope_plan['unresolved'],
            'unknown_dependencies_are_optional': False,
            'record_dependency_enumeration_proven': False}


def atomic_subset(card, record, included_seed_pointers, query='', navigation_context=None,
                  supplement_context=None, included_context_pointers=(), source_reader=None):
    """Rebuild one original card from unions of complete admitted atom closures."""
    plan = atomic_delivery_plan(card, record, query, navigation_context, supplement_context, source_reader)
    return _atomic_subset_from_plan(card, record, included_seed_pointers, plan, query,
                                    navigation_context, supplement_context, included_context_pointers, source_reader)


def _atomic_subset_from_plan(card, record, included_seed_pointers, plan, query='',
                             navigation_context=None, supplement_context=None, included_context_pointers=(),
                             source_reader=None):
    """Internal reuse of a plan from the same immutable card in one request."""
    from .delivery_wire import expand_l1_metadata, project_l1_card, PUBLIC_PROFILE
    if (plan.get('input_card_sha256') != record_digest(card)
            or plan.get('record_sha256') != record_digest(record)):
        raise ValueError('Atomic plan does not match the original card and record')
    included = set(included_seed_pointers)
    if (not included or any(not isinstance(pointer, str) for pointer in included)
            or not included <= set(plan['seed_record_pointers'])):
        raise ValueError('Atomic subset must select original independent seed pointers')
    included_context = set(included_context_pointers)
    if (any(not isinstance(pointer, str) for pointer in included_context)
            or not included_context <= set(plan['context_record_pointers']) | set(plan['protected_record_pointers'])):
        raise ValueError('Atomic context must be an already admitted original context pointer')
    represented = {pointer for unit in plan['units'] if unit['seed_record_pointer'] in included
                   for pointer in unit['record_pointers']}
    represented |= {pointer for unit in plan['context_units'] if unit['seed_record_pointer'] in included_context
                    for pointer in unit['record_pointers']}
    decoded = expand_l1_metadata(card)
    verified, errors = delivered_original_atoms(record, decoded['family'], decoded)
    if errors:
        raise ValueError('Invalid original atom in atomic subset')
    removed = set(verified) - represented
    if not removed:
        return copy.deepcopy(card)
    boundary_owners = plan['original_condition_associations']['boundary_owners']
    if not removed <= set(plan['seed_record_pointers']) | set(plan['context_record_pointers']) | set(boundary_owners):
        raise ValueError('Cannot defer unverified context or an original atom dependency')
    if any(set(boundary_owners[pointer]) & represented for pointer in removed & set(boundary_owners)):
        raise ValueError('Cannot defer a delivered fact original declared condition')
    for field in ('decision', 'critical_boundary', 'project_policy_questions'):
        decoded[field] = [atom for atom in decoded.get(field, [])
                          if atom.get('record_pointer') not in removed]
    groups = {field: decoded.get(field, []) for field in
              ('decision', 'critical_boundary', 'project_policy_questions')}
    closure = decoded.setdefault('context_closure', {})
    # Binding prose/proofs belong to the actual delivered context pointer.
    # Deferred source text must not leak back through an admission/metadata lane.
    if isinstance(closure.get('bindings'), list):
        closure['bindings'] = [binding for binding in closure['bindings']
                               if binding.get('record_pointer') in represented]
    for match in decoded.get('contract_mapping', []):
        if isinstance(match.get('context_pointer_bindings'), list):
            match['context_pointer_bindings'] = [binding for binding in match['context_pointer_bindings']
                                                if binding.get('record_pointer') in represented]
    old_scope = decoded.get('source_scope', {})
    decoded['source_scope'] = compact_semantic_scope(record, decoded['family'], groups, query,
        closure.get('needed_context_excluded', []), navigation_context=navigation_context,
        supplement_context=supplement_context)
    scope = decoded['source_scope']
    if isinstance(scope, dict) and scope.get('scope_schema') == SCOPE_SCHEMA:
        # No previously unknown constraint becomes complete because a seed was
        # deferred. Keep its original uncertainty if it has no atom attribution.
        prior_unknown = [node for node in old_scope.get('needed_scope_missing', [])
                         if not node.get('basis_record_pointers')]
        scope['needed_scope_missing'] = _unique(scope.get('needed_scope_missing', []) + prior_unknown)
        scope['unattributed_potential_record_scope_missing_count'] = sum(
            'UNATTRIBUTED_POTENTIAL_RECORD_SCOPE_DEPENDENCY' in node.get('scope_relation_statuses', [])
            for node in scope['needed_scope_missing'])
        scope['scope_dependency_resolution_complete'] = not bool(scope['needed_scope_missing'])
        closure['identified_necessary_scope_dependencies_complete'] = scope['identified_necessary_scope_dependencies_complete']
        closure['scope_dependency_resolution_complete'] = scope['scope_dependency_resolution_complete']
        closure['needed_semantic_scope_node_count'] = len(scope['needed_scope_missing'])
    missing = {pointer for unit in plan['units'] if unit['seed_record_pointer'] in included
               for pointer in unit['needed_context_missing']}
    unresolved_context = removed & set(plan['context_record_pointers'])
    closure['needed_context_missing'] = sorted(set(closure.get('needed_context_missing', [])) | missing)
    closure['status'] = 'PARTIAL_CONTEXT' if (closure.get('status') == 'PARTIAL_CONTEXT'
        or closure['needed_context_missing'] or unresolved_context or closure.get('needed_semantic_scope_node_count')
        or closure.get('original_supplement_context_complete') is False) else 'BOUNDED_ORIGINAL_POINTER_CONTEXT'
    closure['universal_method_contract_verified'] = False
    if unresolved_context:
        closure['deferred_context_necessity_unknown'] = sorted(unresolved_context)
        closure['context_dependency_resolution_complete'] = False
    context_status = decoded.get('record_context_delivery')
    if isinstance(context_status, dict):
        context_status['seed_record_pointers'] = [pointer for pointer in
            context_status.get('seed_record_pointers', []) if pointer in represented]
        context_status['entire_task_completion_proven'] = False
    n001_status = decoded.get('n001_coding_context')
    if isinstance(n001_status, dict):
        for field in ('seed_record_pointers', 'context_record_pointers'):
            n001_status[field] = [pointer for pointer in n001_status.get(field, []) if pointer in represented]
        n001_status['withheld_record_pointers'] = sorted(set(n001_status.get('withheld_record_pointers', [])) | removed)
        n001_status['status'] = 'PARTIAL_RECORD_CONTEXT'
        n001_status['budget_unit'] = ATOMIC_BUDGET_UNIT
    selection = decoded.get('query_selection', {})
    if isinstance(selection.get('selected'), list):
        selection['selected'] = [row for row in selection['selected'] if row.get('record_pointer') in represented]
    admission = decoded.get('delivery_admission')
    if isinstance(admission, dict):
        for field in ('supported_record_pointers', 'supported_nonpolicy_record_pointers',
                      'supported_policy_record_pointers'):
            if isinstance(admission.get(field), list):
                admission[field] = [pointer for pointer in admission[field] if pointer in represented]
        nonpolicy = len(admission.get('supported_nonpolicy_record_pointers', admission.get('supported_record_pointers', [])))
        policy = len(admission.get('supported_policy_record_pointers', []))
        for key, value in (('supported_original_atom_count', nonpolicy),
                           ('supported_nonpolicy_atom_count', nonpolicy),
                           ('supported_policy_atom_count', policy),
                           ('total_supported_original_atom_count', nonpolicy + policy)):
            if key in admission:
                admission[key] = value
        if admission.get('status') != 'EXACT_SYMBOL_NAVIGATION':
            admission['status'] = ('TASK_AND_POLICY_ATOMS_DELIVERED' if nonpolicy and policy else
                'TASK_ATOM_DELIVERED' if nonpolicy else 'POLICY_ATOM_DELIVERED' if policy else 'NO_TASK_ATOM_DELIVERED')
    if 'contract_delivery' in decoded:
        previous = decoded['contract_delivery']
        decoded['contract_delivery'] = contract_delivery(record, decoded['family'], decoded,
            decoded.get('contract_mapping', []), previous.get('symbol', ''))
    omission = decoded.setdefault('omission', {})
    omission['typed_atoms'] = omission.get('typed_atoms', 0) + len(removed)
    counts = omission.setdefault('typed_atoms_by_kind', {})
    for pointer in removed:
        kind = verified[pointer]['kind']
        counts[kind] = counts.get(kind, 0) + 1
    decoded['atomic_delivery'] = {'schema': 'dst-atomic-delivery/1', 'budget_unit': ATOMIC_BUDGET_UNIT,
        'status': 'PARTIAL_ADMITTED_TASK_ATOMS',
        'delivered_seed_record_pointers': [pointer for pointer in plan['seed_record_pointers'] if pointer in represented],
        'withheld_atoms': [{'record_pointer': pointer, 'kind': verified[pointer]['kind'],
            **({'relation': 'ADJACENT_CONTEXT_NECESSITY_UNKNOWN'} if pointer in unresolved_context else
               {'relation': 'ORIGINAL_SOURCE_BOUNDARY_OF_DEFERRED_ATOM'} if pointer in boundary_owners else {})}
            for pointer in sorted(removed)],
        'withheld_content_delivered': False, 'entire_task_completion_proven': False,
        'unknown_dependencies_are_optional': False, 'record_dependency_enumeration_proven': False}
    if boundary_owners:
        decoded['atomic_delivery']['original_condition_bindings'] = [binding for binding in
            plan['original_condition_associations']['bindings'] if binding['owner_record_pointer'] in represented]
    # Old wire namespaces and array offsets cannot survive a subset. Expand,
    # rebuild Scope values, then let the existing strict local encoder repack.
    original_wire = card.get('wire_projection', {})
    decoded.pop('wire_projection', None)
    sample_reference_assessment(decoded)
    return project_l1_card(decoded, public_contract=original_wire.get('profile') == PUBLIC_PROFILE) if original_wire else decoded


def _bundle_admission_decisions(values):
    """Keep final pointer outcomes; distinct constraints are never overwritten."""
    grouped, order = {}, []
    for value in values:
        item = copy.deepcopy(value)
        if not isinstance(item, dict):
            key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        else:
            item.pop('original_units_sha256', None)
            item.pop('original_units_delivered_by_diagnostics', None)
            # 只按通用诊断排除规则压缩；未知 support 字段可能是限制，不能用白名单删掉。
            for field in ('basis_admission', 'policy_decisions'):
                if isinstance(item.get(field), list):
                    item[field] = _bundle_admission_decisions(item[field])
            pointer = item.get('record_pointer')
            key = ('pointer', pointer) if pointer is not None else (
                'unpointed', json.dumps(item, ensure_ascii=False, sort_keys=True))
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(item)
    result = []
    for key in order:
        distinct = _unique(grouped[key])
        final = copy.deepcopy(grouped[key][-1])
        if len(distinct) > 1 and isinstance(final, dict):
            # 同一原 pointer 可能有不同关系或准入结果，不能用最后一次覆盖前面的限制。
            final_marker = json.dumps(final, ensure_ascii=False, sort_keys=True)
            final['other_distinct_results'] = [item for item in distinct
                if json.dumps(item, ensure_ascii=False, sort_keys=True) != final_marker]
        result.append(final)
    return compact_task_diagnostics(result)


def bundle_decision_card(card):
    """Internal bundle packaging; original atoms and necessary context are intact."""
    if card.get('wire_projection', {}).get('schema') == 'dst-agent-l1-wire/1':
        return copy.deepcopy(card)
    result = copy.deepcopy(card)
    if (result.get('projection_schema') != SCHEMA or result.get('level') != 1
            or result.get('family') not in FAMILIES):
        return result
    if 'companion_context' in result:
        result['companion_context'] = [bundle_decision_card(donor) for donor in result['companion_context']]
    represented = {atom['record_pointer']
                   for field in ('decision', 'critical_boundary', 'project_policy_questions')
                   for atom in result.get(field, []) if atom.get('record_pointer') is not None}
    requested_symbols = {match.get('symbol') for match in result.get('contract_mapping', [])}
    requested_pointers = {pointer for match in result.get('contract_mapping', [])
                          for field in ('record_pointers', 'availability_record_pointers',
                                        'context_record_pointers') for pointer in match.get(field, [])}
    symbols, deferred_symbols = [], 0
    for item in result.get('exact_symbols', []):
        basis = set(item.get('basis_record_pointers', [])) | set(item.get('context_record_pointers', []))
        if item.get('basis_record_pointer') is not None:
            basis.add(item['basis_record_pointer'])
        if item.get('receiver') or item.get('symbol') in requested_symbols or basis & (represented | requested_pointers):
            symbols.append(item)
        else:
            deferred_symbols += 1
    result['exact_symbols'] = _unique(symbols)
    if deferred_symbols:
        omission = result.setdefault('omission', {})
        omission['exact_symbols'] = omission.get('exact_symbols', 0) + deferred_symbols
        omission['bundle_navigation_symbols_deferred'] = deferred_symbols
    for field in ('decision', 'critical_boundary', 'project_policy_questions'):
        for atom in result.get(field, []):
            if isinstance(atom.get('contract_bindings'), list):
                atom['contract_bindings'] = _unique(atom['contract_bindings'])
    for field in ('facet_admission', 'task_admission'):
        if isinstance(result.get(field), dict) and isinstance(result[field].get('decisions'), list):
            result[field]['decisions'] = _bundle_admission_decisions(result[field]['decisions'])
    closure = result.get('context_closure')
    if isinstance(closure, dict):
        if isinstance(closure.get('bindings'), list):
            closure['bindings'] = _unique(closure['bindings'])
        if isinstance(closure.get('admission'), list):
            closure['admission'] = _bundle_admission_decisions(closure['admission'])
    for match in result.get('contract_mapping', []):
        if isinstance(match.get('context_pointer_bindings'), list):
            match['context_pointer_bindings'] = _unique(match['context_pointer_bindings'])
        if isinstance(match.get('context_admission'), list):
            match['context_admission'] = _bundle_admission_decisions(match['context_admission'])
    admission = result.get('delivery_admission')
    if isinstance(admission, dict) and isinstance(admission.get('policy_decisions'), list):
        admission['policy_decisions'] = _bundle_admission_decisions(admission['policy_decisions'])
    deferred = ['admission.support_details', 'admission.repeated_results']
    if 'query_selection' in result:
        result.pop('query_selection')
        deferred.append('query_selection')
    # Match diagnostics remain original here. The existing caller's public or
    # budget wire boundary owns their projection and supported-pointer shape.
    # L1 保留事实、限制和上下文；逐句检索诊断仅在 opt-in developer trace 可观察。
    for field in ('facet_admission', 'task_admission'):
        admission = result.get(field)
        if not isinstance(admission, dict) or 'decisions' not in admission:
            continue
        details = admission['decisions']
        outcomes = []
        for row in details:
            alternatives = row.get('other_distinct_results', []) if isinstance(row, dict) else []
            for item in [*alternatives, row]:
                if isinstance(item, dict):
                    # 上游已移除具名诊断；保留语义 guard，由 wire 判断已知诊断行是否可延后。
                    outcomes.append(copy.deepcopy(item))
        admission['decisions'] = _unique(outcomes)
        admission['diagnostic_details_deferred'] = True
        admission['diagnostic_details_sha256'] = record_digest({'decisions': details})
        deferred.append(field + '.decisions.support_details')
    navigation = result.get('exact_symbols', [])
    kept_symbols = [row for row in navigation if row.get('symbol') in requested_symbols]
    if len(kept_symbols) != len(navigation):
        omitted_count = len(navigation) - len(kept_symbols)
        result['exact_symbols'] = kept_symbols
        omission = result.setdefault('omission', {})
        omission['exact_symbols'] = omission.get('exact_symbols', 0) + omitted_count
        omission['bundle_navigation_symbols_deferred'] = omission.get('bundle_navigation_symbols_deferred', 0) + omitted_count
        deferred.append('unrequested_navigation_symbols')
    hints = result.get('consumption_hints', [])
    if hints and all(row.get('consumption_hint') is True for row in hints):
        result['consumption_hints'] = []
        result.setdefault('omission', {})['noncanonical_consumption_hints_deferred'] = len(hints)
        deferred.append('noncanonical_consumption_hints')
    expansion = result.get('expansion')
    if isinstance(expansion, dict) and 'reviewer' in expansion:
        result['expansion'] = {'reviewer': expansion['reviewer'],
            'evidence_view': 'get_entry(view=evidence); then resolve_evidence(selected reference)',
            'default_evidence_expanded': False}
        deferred.append('repeated_evidence_tool_argument_templates')
    result['bundle_packaging'] = {'schema': 'dst-bundle-decision/2',
                                  'deferred_diagnostic_fields': deferred,
                                  'diagnostic_expansion': 'Opt-in developer trace; original record expansion does not reconstruct query diagnostics',
                                  'whole_original_atoms_and_required_context_preserved': True}
    return share_metadata(result)


def reviewer_view(record, family, governance, profile=None):
    """L2: all typed fact atoms and boundaries, still without referenced evidence."""
    _validate(record, family, governance)
    profile = _profile(record, profile)
    atoms = _atoms(record, family)
    return {'projection_schema': SCHEMA, 'level': 2, 'family': family,
            'id': record['id'], 'title': record.get('title', ''), 'record_sha256': record_digest(record),
            'when_relevant': _when(record, family, profile),
            'typed_atoms': atoms, 'does_not_mean': _boundaries(record, family),
            'failure_modes': copy.deepcopy(record.get('common_ai_failure', [])),
            **({'legacy_details': {key: copy.deepcopy(value) for key, value in record.get('details', {}).items()
                                   if key not in ('evidence', 'case_evidence', 'klei_basis', 'dst_klei_basis',
                                                  'evidence_source', 'counter_evidence', 'project_hash',
                                                  'hash_algorithm', 'source_file', 'source_locator')}}
               if family == 'legacy' else {}),
            'source_symbols': _symbols(record, family, profile, atoms),
            'consumption_hints': _hints(profile, 'critical_boundary') + _hints(profile, 'project_policy_questions'),
            'project_policy_questions': [a for a in atoms if a['kind'] == 'PROJECT_POLICY'],
            'source_scope': _scope(record), 'evidence_strength': _strength(record, family, atoms),
            'governance': _governance(record, governance),
            'omission': {'typed_atoms': 0, 'boundaries': 0, 'default_evidence_expanded': False},
            'expansion': _expansion(record['id'])}


def _scope(record):
    # 原作用域也承载调用者、条件、分支和建议前提；字段白名单会丢失限制。
    return copy.deepcopy(record.get('scope', {}))


def _walk(value, path=''):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            token = str(key).replace('~', '~0').replace('/', '~1')
            yield from _walk(child, path + '/' + token)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + '/' + str(index))


def evidence_manifest(record, family, governance, profile=None):
    """L3: exact locators only; the service separately resolves selected reference IDs."""
    _validate(record, family, governance)
    profile = _profile(record, profile)
    refs = {}
    for path, value in _walk(record):
        if {'artifact_path', 'sha256', 'pointer'}.issubset(value):
            key = (value['artifact_path'], value['sha256'], value['pointer'])
            refs.setdefault(key, []).append(path)
    references = [{'reference_id': f'ref-{index:04d}', 'reference_index': index, 'artifact_path': key[0],
                   'sha256': key[1], 'pointer': key[2], 'used_by_record_pointers': paths}
                  for index, (key, paths) in enumerate(sorted(refs.items()))]
    missing = []
    locators = []
    if family == 'n001':
        missing = [{'role': 'research_map_entry', 'canonical_id': value,
                    'resolution_required': 'native_research.source_locators',
                    'artifact_hash_pointer_available_in_record': False}
                   for value in record.get('research_evidence_refs', [])]
    elif family == 'legacy':
        for index, source in enumerate(record.get('sources', [])):
            locators.append({key: copy.deepcopy(source[key]) for key in
                             ('source_id', 'role', 'locator', 'locator_structured') if key in source}
                            | {'record_pointer': f'/sources/{index}',
                               'hash_available_in_record': bool(source.get('sha256'))})
    hints = profile.get('critical_boundary', []) + profile.get('project_policy_questions', [])
    hint_sources = _unique([source for hint in hints for source in hint.get('verified_source_locators', [])])
    return {'projection_schema': SCHEMA, 'level': 3, 'family': family,
            'id': record['id'], 'title': record.get('title', ''), 'record_sha256': record_digest(record),
            'governance': _governance(record, governance), 'source_scope': _scope(record),
            'references': references, 'reference_count': len(references),
            'legacy_source_locators': locators, 'unresolved_research_links': missing,
            'consumption_hint_verification_locators': hint_sources,
            'resolution': epoch_arguments({'evidence_expanded': False, 'selected_only': True,
                           'tool': 'resolve_evidence', 'id': record['id'],
                           'projection': 'reviewer', 'reference_index': 0,
                           'subpointer': '', 'max_bytes': 24000})}

"""One-hop original provider facts; never synthesize a callee contract."""
import copy
import re
from pathlib import PurePosixPath
from . import facet_contracts as facets, source_identity
from .intent_scope import task_requests

ROLE = 'BOUNDED_ORIGINAL_PROVIDER_CONTEXT'
PROVIDER_REQUEST = re.compile(r'\b(?:providers?|suppliers?|upstream providers?)\b|提供方|供应方|供给方|(?:依赖|依存).{0,12}(?:提供|供应|来源|返回)', re.I)
COMPONENT = re.compile(r'\b(?:[A-Za-z_]\w*\.)*components\.([A-Za-z_]\w*)\b', re.ASCII)
PRONOUN_CALL = re.compile(r'(?:其|它的|\bits\s+)([A-Za-z_]\w*)\s*\(', re.ASCII | re.I)
QUALIFIED_CALL = re.compile(r'(?<![A-Za-z0-9_:.])([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+)\s*\(', re.ASCII)
RESULT_USE = re.compile(r'读取|取值|获取|使用|采用|计算|乘|除|\b(?:reads?|uses?|takes?|gets?|calculat\w*|multipl\w*|divid\w*)\b', re.I)
UNSAFE_LOCAL = re.compile(r'不(?:会|曾|能|确定|使用|调用|读取|计算|存在)|没有|未(?:曾|知|确认|验证|调用|使用)|从不|可能|是否|或许|\b(?:not|never|no|may|might|could|possibly|unknown|uncertain|whether|unverified)\b', re.I)
RESULT_SUFFIX = re.compile(r'^\s*(?:的\s*)?(?:返回|returns?\b)', re.I)
INTERVENING_RECEIVER = re.compile(
    r'(?<![A-Za-z0-9_:.])(?:[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+|[A-Z][A-Za-z0-9_]*)(?![A-Za-z0-9_])'
    r'|\b(?i:entit(?:y|ies)|objects?|receivers?|replicas?|components?|another|other|different)\b'
    r'|实体|对象|接收者|组件|另一|其他', re.ASCII)

def _method(symbol):
    return symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]

def _quoted(text, index):
    quote, escaped = None, False
    closers = {'"': '"', "'": "'", '“': '”', '‘': '’'}
    for ch in text[:index]:
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
        elif ch in closers:
            quote = closers[ch]
    return quote is not None

def _close_call(text, opening):
    depth, quote, escaped = 0, None, False
    for index in range(opening, len(text)):
        ch = text[index]
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return index
    return None

def _clauses(text):
    start = 0
    for stop in re.finditer(r'[。；;\n]+|(?<=[.!?])\s+', text):
        yield start, text[start:stop.start()]
        start = stop.end()
    yield start, text[start:]

def _qualified_relation(text, declared):
    for base, clause in _clauses(text):
        names = [match.group(1) for match in QUALIFIED_CALL.finditer(clause)
                 if not _quoted(clause, match.start()) and _method(match.group(1)) == _method(declared)]
        if declared not in names or len(set(names)) != 1:
            continue
        binding = facets.statement_binding(clause, declared)
        if (binding and binding.get('role') == 'BOUNDED_CALLEE_CALLSITE' and
                binding.get('relation_polarity') == 'POSITIVE' and binding.get('positive_callsite_evidence') is True):
            return {'relation': 'EXPLICIT_QUALIFIED_PROVIDER_INVOCATION',
                    'source_clause_span': [base, base + len(clause)],
                    'original_call_binding': copy.deepcopy(binding)}
    return None

def _component_result_relation(text, declared, proofs):
    owner = proofs[0].get('owner')
    if not owner or any(proof.get('owner') != owner for proof in proofs):
        return None
    for base, clause in _clauses(text):
        for call in PRONOUN_CALL.finditer(clause):
            if call.group(1) != _method(declared) or _quoted(clause, call.start()):
                continue
            paths = [match for match in COMPONENT.finditer(clause[:call.start()])
                     if not _quoted(clause, match.start())]
            owners = {match.group(1).casefold() for match in COMPONENT.finditer(clause)
                      if not _quoted(clause, match.start())}
            if not paths or len(owners) != 1:
                continue
            path = paths[-1]
            component = path.group(1)
            if component.casefold() != owner.casefold() or call.start() - path.end() > 80:
                continue
            # 组件字段与声明所在原组件模块须同时对齐，不能按裸方法名猜 owner。
            if not all(proof.get('source_file', '').startswith('scripts/components/') and
                       PurePosixPath(proof['source_file']).stem.casefold() == component.casefold()
                       for proof in proofs):
                continue
            uses = list(RESULT_USE.finditer(clause[:path.start()]))
            # 结果用途与极性检查共用同一 clause 前缀，长句不能漏掉 may/可能。
            if UNSAFE_LOCAL.search(clause[:call.start()]) or not uses:
                continue
            bridge = clause[path.end():call.start()]
            if any(not _quoted(clause, path.end() + match.start())
                   for match in INTERVENING_RECEIVER.finditer(bridge)):
                continue
            competitors = [match.group(1) for match in QUALIFIED_CALL.finditer(clause)
                           if not _quoted(clause, match.start()) and
                           _method(match.group(1)) == _method(declared) and match.group(1) != declared]
            if competitors:
                continue
            closing = _close_call(clause, call.end() - 1)
            if closing is None or not RESULT_SUFFIX.match(clause[closing + 1:]):
                continue
            if UNSAFE_LOCAL.search(clause[closing + 1:closing + 33]):
                continue
            return {'relation': 'EXPLICIT_COMPONENT_PRONOUN_PROVIDER_RESULT_USE',
                    'source_component_expression': path.group(0), 'provider_component': component,
                    'source_result_use_span': [base + uses[-1].start(), base + uses[-1].end()],
                    'source_component_span': [base + path.start(), base + path.end()],
                    'source_call_span': [base + call.start(), base + closing + 1],
                    'relation_polarity': 'POSITIVE_CONDITIONAL_RESULT_USE'}
    return None

def provider_context_atoms(record, family, query, seeds):
    """Return original NSF copies and one-hop relation metadata.

    The caller must already admit this exact record for its projection, task and
    deep governance. This function never grants record or Coding admission.
    """
    requests = task_requests(query)
    if family != 'core' or not any(PROVIDER_REQUEST.search(request['text']) for request in requests):
        return [], []
    original = {atom['record_pointer']: atom for atom in facets._typed_atoms(record, family)}
    valid_seeds = []
    for seed in seeds:
        own = original.get(seed.get('record_pointer')) if isinstance(seed, dict) else None
        if (own and own['kind'] == 'NSF' and seed.get('kind') == own['kind'] and
                seed.get('statement') == own['statement'] and not seed.get('provider_context')):
            valid_seeds.append(own)
    if not valid_seeds:
        return [], []
    seed_pointers = {seed['record_pointer'] for seed in valid_seeds}
    candidates, relations, seen = [], [], set()
    for declared in source_identity.identity_symbols(record, family):
        proofs = source_identity.identity_bindings(record, family, declared)
        if not proofs or proofs[0]['declared_symbol'] != declared or not proofs[0].get('owner'):
            continue
        for match in facets.contract_matches(record, family, declared):
            if match.get('reference_context_only'):
                continue
            for pointer in match.get('record_pointers', []):
                own = original.get(pointer)
                role = match.get('pointer_roles', {}).get(pointer, {})
                target_proofs = [proof for proof in proofs if proof['record_pointer'] == pointer]
                if (not own or own['kind'] != 'NSF' or pointer in seed_pointers or not target_proofs or
                        role.get('role') != 'METHOD_SUBJECT' or role.get('callee_semantics_supported') is not True or
                        pointer in match.get('reference_context_record_pointers', [])):
                    continue
                for seed in valid_seeds:
                    relation = (_qualified_relation(seed['statement'], declared) or
                                _component_result_relation(seed['statement'], declared, target_proofs))
                    key = seed['record_pointer'], pointer, declared
                    if relation is None or key in seen:
                        continue
                    seen.add(key)
                    relation.update({'role': ROLE, 'record_pointer': pointer, 'kind': 'NSF',
                                     'basis_record_pointers': [seed['record_pointer']],
                                     'required_basis_record_pointers': [seed['record_pointer']],
                                     'declaration_identity': declared, 'provider_owner': target_proofs[0]['owner'],
                                     'relation_symbols': [declared, target_proofs[0]['owner']],
                                     'identity_binding_sha256': [facets._digest(proof) for proof in target_proofs],
                                     'original_scope': copy.deepcopy(record.get('scope', record.get('scope_text', ''))),
                                     'caller_method_contract_verified': False, 'necessary_dependency_proven': False,
                                     'entire_task_completion_proven': False, 'record_admission_granted': False,
                                     'provider_expansion_depth': 1})
                    candidates.append(relation)
    admitted, _ = facets.context_admission(record, family, candidates, query)
    by_pointer = {}
    for relation in admitted:
        # 完整原 Scope 用于准入；送达只保留同记录定位，reviewer 可取原值。
        relation.pop('original_scope', None)
        relation.update({'record_sha256': facets._digest(record),
                         'original_scope_record_pointer': '/scope' if 'scope' in record else '/scope_text',
                         'original_scope_access': 'get_entry reviewer'})
        pointer = relation['record_pointer']
        atom = by_pointer.setdefault(pointer, copy.deepcopy(original[pointer]))
        atom.setdefault('provider_context', []).append(copy.deepcopy(relation))
        relations.append(relation)
    return list(by_pointer.values()), relations

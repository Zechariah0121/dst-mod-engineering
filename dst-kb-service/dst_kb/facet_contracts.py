"""Frozen-record contract navigation and whole-atom scope admission.

Only explicit comparison context reads its accepted original schema. Names never create facts.
"""
import copy
import base64
from . import developer_trace as dt
import json
import re
from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from .intent_scope import query_scope as _shared_query_scope
from .intent_scope import task_support
from .intent_scope import positive_focus_support
from .task_relevance import record_content_context
from .relevance_frames import _data_quote_view
from .contract_cache import BoundedContractCache
from . import source_identity
from .source_epoch_runtime import active_epoch, epoch_key

MAP_PATH = Path(__file__).with_name('contract_map.json')
QUALIFIED = re.compile(r'(?<![A-Za-z0-9_])(?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Za-z_][A-Za-z0-9_]*[:.][A-Za-z_][A-Za-z0-9_]*')
BARE = re.compile(r'(?<![A-Za-z0-9_])([A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*)\s*(?=\()')
NEGATIVE = re.compile(r'^(?:不(?:讨论|考虑|涉及|需要|做|要|包含|使用|讲|覆盖)|不要|排除|无需|忽略|非此|without\b|exclude\b|excluding\b|no\b|not\b)', re.I)
CLAUSES = re.compile(r'[，,；;。\n]|\bbut\b|\band\b(?=\s*(?:not|no|without|exclude))|但(?:是)?', re.I)
_SOURCE_NAVIGATION = OrderedDict()
_NAVIGATION_CACHE_LIMIT = 512
_CONTRACT_CACHE = BoundedContractCache()
_RECORD_DERIVATION = ContextVar('dst_record_contract_derivation', default=None)
BEHAVIOR = re.compile(r'返回|调用|调(?=\s*[A-Za-z_])|(?<![A-Za-z0-9_])local\s+[A-Za-z_]\w*\s*=(?!=)|要求|检查|确认|交给|注册|赋|写|保存|存|登记|删除|清|取消|安排|重设|设|读|执行|复制|捕获|限制|增加|移除|添加|恢复|拒绝|更新|转发|浅拷贝|匹配|安全|计算|结算|遍历|重算|乘|生成|改变|连接|替换|'
                      r'消耗|推送|启动|重建|保留|置|终止|委派|求值|接收|接受|安装|处理|累计|遍历|遍|转回|转换|构造|取|建|统计|刷新|监听|验证|断言|播放|做|收集|将|稀释|比较|排序|传|搜索|消费|折算|支持|为真|有|guard|assert|'
                      r'\b(?:returns?|calls?|requires?|checks?|sets?|stores?|saves?|reads?|clears?|cancels?|starts?|stops?|updates?|copies|removes?|adds?|rejects?|maps?|forwards?|writes?|takes?|receives?|selects?|registers?|captures?|restores?|clamps?|acts?|constructs?|constructed|calculates?|deletes?|skips?|passes?|delegates?|chooses?|schedules?|retries|accepts?|replaces?|declares?|installs?|means?|process(?:es)?|searches?|sorts?)\b', re.I)
CALL_CONTEXT = re.compile(r'调用|调(?=\s*[A-Za-z_])|转交|传入|执行|运行|使用|采用|构造|读取|通过|以|\b(?:calls?|calling|invokes?|invoking|uses?|using|passes?|passing|runs?|running|reads?|reading|via|with)\b', re.I)
CALLABLE_RESULT = re.compile(r'^\s*(?:\([^\n]*\))?\s*(?:仅|只|会|总是|直接|都|本身|\s)*(?:返回|接受|接收|要求|检查|遍历|安装|guard|assert|\b(?:returns?|requires?|receives?|accepts?|checks?)\b)', re.I)


def _digest(record):
    current = _RECORD_DERIVATION.get()
    if current is not None and 'record_snapshot' in current and record is current['record_snapshot']:
        # Only the private copy owned by this synchronous derivation may reuse
        # its complete input hash. Caller-owned records are always rehashed.
        return current['key'][0][2]
    return sha256(json.dumps(record, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode('utf-8')).hexdigest()


def _catalog():
    context=active_epoch()
    return _catalog_for(context.contract_map if context is not None else MAP_PATH, epoch_key())

@lru_cache(maxsize=8)
def _catalog_for(path, context_key):
    return json.loads(Path(path).read_text(encoding='utf-8'))

_catalog.cache_clear = _catalog_for.cache_clear


def _record_map(record):
    mapped = _catalog()['records'].get(record['id'], {})
    if mapped.get('record_sha256') and mapped['record_sha256'] != _digest(record):
        raise ValueError('Contract map does not match canonical record: ' + record['id'])
    return mapped


def normalize_symbol(symbol):
    return re.sub(r'\([^\n]*\)$', '', symbol.strip()).strip()


def _navigation_key(record, family):
    return epoch_key(), family, _digest(record)


def _bounded_source_label(label):
    """An opaque single locator label is not a callable declaration."""
    return (isinstance(label, str) and bool(label.strip()) and
            not re.search(r'[/,;\n]|、|；', label) and
            not re.fullmatch(r'\s*[A-Za-z_]\w*\s+(?:and|or)\s+[A-Za-z_]\w*\s*', label, re.I) and
            len(set(QUALIFIED.findall(label))) <= 1 and
            len(set(re.findall(r'(?<![A-Za-z0-9_])([A-Za-z_]\w*(?:[:.][A-Za-z_]\w*)*)\s*\(', label))) <= 1)


def _steam_context_version(record, atom, item, proof):
    if not isinstance(proof, dict) or proof.get('source_commit', object()) is not None:
        return None
    try:
        own = record['claims'][int(atom['record_pointer'].rsplit('/', 1)[1])]
        scope_ref = proof.get('original_source_scope_ref', {})
        if scope_ref not in own.get('evidence_refs', []):
            return None
        registry = source_identity._registry()
        scope, citation = registry._node(scope_ref), registry._node(item)
        version = source_identity.steam_source_version(scope, [citation])
        if version is None or version['snapshot_id'] != proof.get('snapshot_id'):
            return None
        if any(citation.get(left) != proof.get(right) for left, right in (
                ('path', 'source_file'), ('line_start', 'line_start'), ('line_end', 'line_end'),
                ('file_sha256', 'file_sha256'), ('range_sha256', 'range_sha256'))):
            return None
        return version
    except (KeyError, TypeError, ValueError, OSError, IndexError):
        return None


def _bounded_context_item(record, family, item, atom, scope_binding):
    proof = item.get('source_context_proof')
    scope = record.get('scope', record.get('scope_text', ''))
    own = (record['claims'][int(atom['record_pointer'].rsplit('/', 1)[1])]
           if family == 'core' else record.get('native_fact', {}))
    source_scope = proof.get('original_source_scope_ref') if isinstance(proof, dict) else None
    if (not isinstance(proof, dict) or item.get('context_only') is not True or
            atom['kind'] not in ('NSF', 'EI', 'REC', 'UNK') or
            proof.get('schema') != 'original-bounded-source-leaf/1' or
            proof.get('precision') != 'EXACT_SOURCE_RANGE_CONTEXT_ONLY' or
            proof.get('single_locator_node') is not True or
            proof.get('artifact_integrity_verified') is not True or
            proof.get('record_sha256') != _digest(record) or
            proof.get('record_pointer') != atom['record_pointer'] or
            proof.get('claim_kind') != atom['kind'] or
            proof.get('whole_statement_sha256') != _digest(atom['statement']) or
            proof.get('original_scope') != scope or
            not _bounded_source_label(proof.get('source_label')) or
            proof.get('source_label') != item.get('source_label') or
            not isinstance(proof.get('source_file'), str) or not proof['source_file'] or
            proof.get('source_file') != item.get('source_file') or
            type(proof.get('line_start')) is not int or proof['line_start'] <= 0 or
            type(proof.get('line_end')) is not int or proof['line_end'] < proof['line_start'] or
            not all(isinstance(proof.get(field), str) and re.fullmatch(r'[0-9a-fA-F]{64}', proof[field])
                    for field in ('sha256', 'file_sha256', 'range_sha256', 'original_source_value_sha256')) or
            not isinstance(proof.get('snapshot_id'), str) or not proof['snapshot_id'] or
            not (isinstance(proof.get('source_commit'), str) and proof['source_commit'] or
                 _steam_context_version(record, atom, item, proof)) or
            not isinstance(source_scope, dict) or
            not all(source_scope.get(field) == item.get(field) for field in ('artifact_path', 'sha256')) or
            not all(proof.get(field) == item.get(field) for field in ('artifact_path', 'sha256', 'pointer')) or
            not any(_reference_key(ref) == _reference_key(item) for ref in own.get('evidence_refs', [])) or
            not isinstance(scope, dict) or not any(
                row.get('scope_ref') == source_scope and row.get('snapshot_id') == proof['snapshot_id'] and
                row.get('source_commit') == proof['source_commit']
                for row in scope.get('source_scopes', []) if isinstance(row, dict)) or
            not any(row.get('citation_ref') == {field: item[field] for field in ('artifact_path', 'sha256', 'pointer')} and
                    row.get('source_path') == proof['source_file'] and
                    row.get('symbol') == proof['source_label'] and
                    row.get('snapshot_id') == proof['snapshot_id'] and
                    row.get('commit') == proof['source_commit'] and
                    all(row.get(field) == proof[field] for field in
                        ('line_start', 'line_end', 'file_sha256', 'range_sha256'))
                    for row in scope.get('source_locators', []) if isinstance(row, dict))):
        return None
    return {'symbol': '', 'source_label': proof['source_label'],
            'record_pointer': atom['record_pointer'], 'source_file': proof['source_file'],
            'context_only': True,
            'source_context_proof': {**{field: copy.deepcopy(value) for field, value in proof.items()
                                       if field != 'original_scope'}, **scope_binding},
            **{field: item[field] for field in ('artifact_path', 'sha256', 'pointer')}}


def register_source_navigation(record, family, navigation):
    """Accept original-ref navigation and separately verified typed-context leaves.

    This function never reads evidence or source files. Registration is replacement,
    keyed by family and complete canonical-record digest rather than entry ID.
    """
    atoms = {a['record_pointer']: a for a in _typed_atoms(record, family)}
    record_digest = _digest(record)
    scope_pointer = '/scope' if 'scope' in record else '/scope_text' if 'scope_text' in record else None
    scope_binding = ({'original_scope_ref': {'record_sha256': record_digest, 'record_pointer': scope_pointer}}
                     if scope_pointer else {'original_scope': copy.deepcopy(record.get('scope', record.get('scope_text', '')))})
    accepted, rejected, seen = [], 0, set()
    for item in navigation:
        pointer = item.get('record_pointer') if isinstance(item, dict) else None
        atom = atoms.get(pointer)
        if atom is not None and item.get('source_context_proof') is not None:
            bounded = _bounded_context_item(record, family, item, atom, scope_binding)
            if bounded is None:
                rejected += 1
                continue
            key = ('bounded_context', pointer, item['artifact_path'], item['sha256'], item['pointer'])
            if key not in seen:
                seen.add(key)
                accepted.append(bounded)
            continue
        spelling = item.get('symbol', '') if isinstance(item, dict) else ''
        symbol = normalize_symbol(spelling) if isinstance(spelling, str) else ''
        if atom is None or not QUALIFIED.fullmatch(symbol):
            rejected += 1
            continue
        original = record['claims'][int(pointer.rsplit('/', 1)[1])] if family == 'core' else record.get('native_fact', {})
        matching_ref = any(all(ref.get(key) == item.get(key) and item.get(key) is not None
                               for key in ('artifact_path', 'sha256', 'pointer'))
                           for ref in original.get('evidence_refs', []))
        if not matching_ref:
            rejected += 1
            continue
        proof = item.get('typed_context_proof')
        verified_named_context = (item.get('original_reference_integrity_verified') is True and
            item.get('record_sha256') == record_digest and item.get('claim_kind') == atom['kind'] and
            item.get('original_scope') == record.get('scope', record.get('scope_text', '')) and
            isinstance(atom['statement'], str) and bool(re.search(
                r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_:.])', atom['statement'])))
        verified_context = (isinstance(proof, dict) and
            proof.get('schema') == 'original-single-method-leaf/1' and
            proof.get('record_sha256') == record_digest and
            proof.get('record_pointer') == pointer and proof.get('claim_kind') == atom['kind'] and
            proof.get('symbol') == symbol and proof.get('precision') == 'EXACT_SINGLE_METHOD_LEAF' and
            proof.get('artifact_integrity_verified') is True and
            proof.get('original_scope') == record.get('scope', record.get('scope_text', '')) and
            all(proof.get(field) == item.get(field) for field in ('artifact_path', 'sha256', 'pointer')) and
            isinstance(proof.get('source_file'), str) and bool(proof['source_file']) and
            proof.get('source_file') == item.get('source_file') and
            type(proof.get('line_start')) is int and proof['line_start'] > 0 and
            type(proof.get('line_end')) is int and proof['line_end'] >= proof['line_start'] and
            all(isinstance(proof.get(field), str) and re.fullmatch(r'[0-9a-fA-F]{64}', proof[field])
                for field in ('file_sha256', 'range_sha256', 'sha256')) and
            isinstance(proof.get('snapshot_id'), str) and bool(proof['snapshot_id']))
        if (proof is not None and not verified_context or
            atom['kind'] != 'NSF' and not (verified_context or verified_named_context) or
            not set(atom['kind'].replace(' ', '').split('/')) <= {'NSF', 'EI', 'REC', 'UNK', 'PROJECT_POLICY'}):
            rejected += 1
            continue
        context_only = item.get('context_only') is True or atom['kind'] != 'NSF'
        key = symbol, pointer, item['artifact_path'], item['sha256'], item['pointer'], context_only
        if key not in seen:
            seen.add(key)
            accepted.append({'symbol': symbol, 'record_pointer': pointer,
                             'source_file': item.get('source_file'),
                             'context_only': context_only,
                             **({'named_typed_context': True, 'original_reference_integrity_verified': True,
                                 'record_sha256': item['record_sha256'], 'claim_kind': item['claim_kind'],
                                 **scope_binding}
                                if verified_named_context else {}),
                             **({'typed_context_proof': {**{field: copy.deepcopy(value) for field, value in proof.items()
                                                         if field != 'original_scope'}, **scope_binding}}
                                if verified_context else {}),
                             **{field: item[field] for field in ('artifact_path', 'sha256', 'pointer')}})
    key = _navigation_key(record, family)
    _SOURCE_NAVIGATION[key] = accepted
    current=_RECORD_DERIVATION.get()
    if current is not None and current['key']==(key,source_identity.selected_source_file()):
        current.pop('navigation',None)
    _SOURCE_NAVIGATION.move_to_end(key)
    while len(_SOURCE_NAVIGATION) > _NAVIGATION_CACHE_LIMIT:
        _SOURCE_NAVIGATION.popitem(last=False)
    return {'accepted_navigation_bindings': len(accepted), 'rejected_navigation_bindings': rejected,
            'record_digest': record_digest, 'new_evidence_or_source_reads': False}


@contextmanager
def record_contract_context(record, family):
    """Reuse verified inputs only within one synchronous record derivation.

    The scope never survives a projection or semantic-unit computation; the next
    call resolves the live source registry again. Nested use shares only this
    exact record content, family, epoch and selected source.
    """
    key=(_navigation_key(record, family),source_identity.selected_source_file())
    current=_RECORD_DERIVATION.get()
    if current is not None and current['key']==key:
        yield
        return
    token=_RECORD_DERIVATION.set({'key':key})
    try:
        yield
    finally:
        _RECORD_DERIVATION.reset(token)


def _record_identity_bindings(record, family):
    current=_RECORD_DERIVATION.get()
    key=(_navigation_key(record, family),source_identity.selected_source_file())
    if current is None or current['key']!=key:
        return source_identity.record_identity_bindings(record, family)
    if 'identity_bindings' not in current:
        current['identity_bindings']=source_identity.record_identity_bindings(record, family)
    return current['identity_bindings']


def _registered_navigation(record, family):
    current=_RECORD_DERIVATION.get()
    key=(_navigation_key(record, family),source_identity.selected_source_file())
    scoped=current is not None and current['key']==key
    if scoped and 'navigation' in current:return current['navigation']
    navigation = list(_SOURCE_NAVIGATION.get(_navigation_key(record, family), []))
    for proof in _record_identity_bindings(record, family):
        symbol = proof['declared_symbol']
        if not (QUALIFIED.fullmatch(symbol) or
                proof.get('declaration_kind') in ('file_local_function', 'global_function') and
                re.fullmatch(r'[A-Za-z_]\w*', symbol)):
            continue
        navigation.append({'symbol': symbol, 'record_pointer': proof['record_pointer'],
                           'source_file': proof['source_file'], 'context_only': proof['claim_kind'] != 'NSF',
                           'declaration_identity_proof': proof,
                           **proof['reference']})
    if scoped:current['navigation']=navigation
    return navigation


def _typed_atoms(record, family):
    if family == 'core':
        return [{'kind': a['kind'], 'statement': a['statement'], 'record_pointer': f'/claims/{i}'}
                for i, a in enumerate(record.get('claims', []))]
    if family == 'n001':
        fact = record.get('native_fact', {})
        return ([{'kind': fact.get('claim_type', 'UNK'), 'statement': fact['statement'],
                  'record_pointer': '/native_fact'}] if 'statement' in fact else [])
    return []


def _navigation(record, family):
    result = []
    field = 'task_keywords' if family == 'core' else 'retrieval_triggers'
    for value in record.get(field, []):
        if isinstance(value, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:[:.][A-Za-z_][A-Za-z0-9_]*)*(?:\([^\n]*\))?', value):
            result.append(normalize_symbol(value))
    for locator in record.get('scope', {}).get('source_locators', []) if isinstance(record.get('scope'), dict) else []:
        # grouped citation names are navigation only; no method semantics are inferred.
        result.extend(QUALIFIED.findall(locator.get('symbol', '')))
    for atom in _typed_atoms(record, family):
        if isinstance(atom['statement'], str):
            result.extend(QUALIFIED.findall(atom['statement']))
            result.extend(BARE.findall(atom['statement']))
    return list(dict.fromkeys(result))


def contract_symbols(record, family):
    mapped = _record_map(record)
    return list(dict.fromkeys(list(mapped.get('contracts', {})) +
                              mapped.get('navigation_symbols', []) +
                              [n['symbol'] for n in _registered_navigation(record, family) if n['symbol']] +
                              _navigation(record, family) + list(source_identity.identity_symbols(record, family))))


def _sentence_start(statement, end):
    start = max(statement.rfind(x, 0, end) for x in ('。', '；', ';', '\n')) + 1
    stops = list(re.finditer(r'\.\s+', statement[:end]))
    return max(start, stops[-1].end()) if stops else start


def _availability_only(statement, symbol):
    occurrences = list(re.finditer(r'(?<![A-Za-z0-9_])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', statement))
    if not occurrences:
        return False
    for match in occurrences:
        start = _sentence_start(statement, match.start())
        end_match = re.search(r'[。；;\n]|\.\s+', statement[match.end():])
        end = match.end() + end_match.start() if end_match else len(statement)
        prefix, suffix = statement[start:match.start()], statement[match.end():end]
        # Absence applies to a name/list following the marker, not to an earlier
        # negative gameplay condition in the same original sentence.
        absent = bool(re.search(r'(?:没有|未定义|不存在|未提供|未实现|不是|错写为|虚构成?|捏造|\bno\b|\bnot defined\b)\s*[A-Za-z0-9_:./(),、\s]*$', prefix, re.I) or
                      re.match(r'\s*(?:\(\))?\s*(?:未定义|不存在|没有定义|并不存在|is not defined|does not exist)', suffix, re.I) or
                      re.search(r'^\s*(?:\([^\n]*?\))?\s*(?:,?\s*(?:or|and)\s+[A-Za-z_]\w*\s*)*(?:override\s+)?is defined', suffix, re.I) and
                      re.search(r'\bno\s+[A-Za-z_,\s]+$', prefix, re.I))
        listed = bool(re.search(r'公开接口是|公开方法只有|接口列表|方法声明|全文方法|\bpublic interfaces?\b', prefix, re.I))
        available = bool(re.match(r'\s*(?:\([^\n]*?\))?\s*(?:存在|已定义|已提供)(?:\s*$|[。；;])|\s*(?:\([^\n]*?\))?\s*(?:exists?|is defined|is available)(?:\s*$|\s+(?:in|on|as)\b)', suffix, re.I))
        if not absent and not listed and not available:
            return False
    return True


def _subject_predicate_owner(statement, occurrence, start, end):
    """Identify outer relations before a suffix can lend its verb to a name."""
    prefix = statement[start:occurrence.start()].strip()
    tail = statement[occurrence.end():end]
    reference_tail = tail.lstrip()
    if reference_tail.startswith('('):
        depth, quote, escaped = 0, None, False
        for index, char in enumerate(reference_tail):
            if quote:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in ('"', "'"):
                quote = char
            elif char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    reference_tail = reference_tail[index + 1:]
                    break
    if ((re.search(r'(?:在|于)\s*$', prefix) and re.match(
            r'\s*(?:(?:返回|执行|完成|结束|退出|调用)\s*)*(?:之前|之后|以前|以后|前|后)', reference_tail)) or
            re.search(r'\b(?:before|after|once|when)\s*$', prefix, re.I)):
        return 'TEMPORAL_REFERENCE'
    if re.match(r'\s*=(?!=)', tail):
        return 'RESULT_ALIAS'
    if (re.match(r'\s*\(', tail) and re.search(
            r'(?:实例化|构造|新建|创建)\s*$|\b(?:constructs?|instantiates?)\s*$', prefix, re.I)):
        return 'CALLER_CONSTRUCTION'
    sentence_start = _sentence_start(statement, occurrence.start())
    if start <= sentence_start or not re.fullmatch(
            r'(?:最后|最终|然后|随后|接着|再|并|\b(?:finally|then|next|subsequently)\b)\s*', prefix, re.I):
        return None
    upstream = statement[sentence_start:start]
    subjects = []
    for segment in re.split(r'[，,]', upstream):
        head = re.match(r'\s*([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)', segment)
        if head and (BEHAVIOR.search(segment[head.end():]) or
                     re.match(r'\s+[a-z][a-z_]*(?:s|ed)\b', segment[head.end():])):
            subjects.append(head[1])
    if subjects:
        owner, spelling = subjects[-1], occurrence[0]
        if owner != spelling and owner.rsplit(':', 1)[-1].rsplit('.', 1)[-1] != spelling:
            return 'CALLER_CONTINUATION'
    return None


def _subject_reference_occurrence(statement, occurrence, start, end):
    """A local reference object cannot borrow its suffix as method behavior."""
    prefix = statement[start:occurrence.start()].strip()
    tail = re.split(r'[。；;\n]|\.\s+', statement[occurrence.end():end], maxsplit=1)[0]
    if _subject_predicate_owner(statement, occurrence, start, end) in ('TEMPORAL_REFERENCE', 'RESULT_ALIAS'):
        return True
    if re.match(r'\s*(?:的)?调用(?:点|处|位置)|\s+(?:call\s*site|invocation\s+site)\b', tail, re.I):
        return True
    if re.search(r'(?:替代|代替|取代|不同于|区别于|相对于|关于|提及|提到|引用|名为|命名为|称为)\s*$|'
                 r'\b(?:unlike|versus|about|mentions?|references?|named|called)\s*$', prefix, re.I):
        return True
    if (re.search(r'(?:在|于)\s*$', prefix) and
            re.match(r'\s*(?:之前|之后|以前|以后|前|后)', tail)):
        return True
    if (re.search(r'(?:与|和|同|比|相比(?:于)?|相较(?:于)?)\s*(?:普通|常规|默认|原版)?\s*$', prefix) and
            re.match(r"\s*(?:的|之|['’]s\b)", tail) and
            re.search(r'不同|不相同|相同|不一致|一致|有别|不等价', tail)):
        return True
    if (re.search(r'(?:所用|所述|引用的|提及的)\s*$', prefix) and
            re.match(r'\s*(?:不等于|不意味着|并不等于|并不意味着)', tail)):
        return True
    # 引号内的方法名字是引用文本；反引号仍可包裹真实代码主体。
    quote, escaped = None, False
    closers = {'"': '"', "'": "'", '“': '”', '‘': '’'}
    for index, char in enumerate(statement[:occurrence.start()]):
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in closers and not (char == "'" and index > 0 and
                statement[index - 1].isalnum() and index + 1 < len(statement) and
                statement[index + 1].isalnum()):
            quote = closers[char]
    return quote is not None


def _subject_caller_occurrence(statement, occurrence, start, end):
    """Explicit caller grammar cannot supply a callee's own predicate."""
    prefix = statement[start:occurrence.start()].strip()
    tail = statement[occurrence.end():end]
    if _subject_predicate_owner(statement, occurrence, start, end) in ('CALLER_CONTINUATION', 'CALLER_CONSTRUCTION'):
        return True
    if (re.match(r'\s*\(', tail) and
            re.search(r'(?:且|若|如果|除非|\b(?:if|unless))\s*$', prefix, re.I)):
        return True
    local_tail = re.split(r'[。；;\n，,]|\.\s+', tail, maxsplit=1)[0]
    # 返回值的消费动作属于 caller，不能借“返回”二字变成 callee 的谓语。
    result_noun = re.match(r"\s*(?:(?:的)?返回(?:值|结果)|(?:['’]s\s+)?(?:return(?:ed)?\s+(?:value|result)|results?)\b)",
                           local_tail, re.I)
    passive_return = re.match(r'\s*(?:返回\s*(?:完全|直接|全部|均|都)?\s*(?:丢弃|忽略|舍弃)|'
                              r'returns?\s+(?:is|are|was|were)\s+(?:(?:completely|entirely|directly)\s+)*'
                              r'(?:discarded|ignored|consumed)\b)', local_tail, re.I)
    consumer = re.compile(r'丢弃|忽略|舍弃|被(?:调用者|caller|其他方法)|'
                          r'\b(?:discard(?:s|ed)?|ignor(?:e[sd]?|ing)|consum(?:e[sd]?|ing))\b', re.I)
    if passive_return or (result_noun and
            (consumer.search(local_tail[result_noun.end():]) or consumer.search(prefix))):
        return True
    usage = re.compile(r'捕获|读取|检查|使用|保存|传递|比较|结算|'
                       r'\b(?:captur(?:e[sd]?|ing)|reads?|checks?|checked|uses?|used|'
                       r'stor(?:e[sd]?|ing)|passes?|passed|compar(?:e[sd]?|ing))\b', re.I)
    if result_noun and (usage.search(local_tail[result_noun.end():]) or usage.search(prefix)):
        return True
    if (re.match(r'\s*\(', tail) and re.search(
            r'(?:尝试|试图|成功后|失败后|否则|随后|然后|再)\s*$|'
            r'\b(?:try|tries|tried|attempt|attempts|attempted)\s+to\s*$', prefix, re.I)):
        return True
    # 返回值被用作另一个主体的分支条件，不是 callee 自身的返回流程。
    return bool(re.match(r'\s*(?:仅|只|会|本身|直接)*返回', tail) and re.search(
        r'(?:时|则|\bthen\b)\s*(?:该|此)?(?:fn|action|caller|function|调用者|动作)'
        r'(?![A-Za-z0-9_])', tail, re.I))


def _subject_reference_only(statement, symbol, allow_bare=False):
    """Pure-reference delivery requires positive evidence at every occurrence."""
    if not isinstance(statement, str):
        return False
    exact = list(re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) +
                            r'(?![A-Za-z0-9_])', statement))
    spelling = symbol if exact else symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    occurrences = exact if exact else (list(re.finditer(
        r'(?<![A-Za-z0-9_:.])' + re.escape(spelling) + r'(?![A-Za-z0-9_])', statement))
        if allow_bare else [])
    return bool(occurrences) and all(_subject_reference_occurrence(
        statement, occurrence, _sentence_start(statement, occurrence.start()), len(statement))
        for occurrence in occurrences)


def _subject_behavior(statement, symbol, exact=False):
    """Require a real named subject; all delivered text remains the original atom."""
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    spelling = symbol if exact else method
    if _availability_only(statement, spelling):
        return False
    for match in re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(spelling) + r'(?![A-Za-z0-9_])', statement):
        # 实参里的名称不是主体；顶层逗号后的独立谓语不能借给前一方法。
        start, end = 0, len(statement)
        depth, quote, escaped, nested = 0, None, False, False
        for index, char in enumerate(statement):
            if index == match.start() and (depth or quote):
                nested = True
                break
            if quote:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
            elif depth and char in ('"', "'"):
                quote = char
            elif char == '(':
                depth += 1
            elif char == ')' and depth:
                depth -= 1
            elif not depth and (char in '。；;\n，,' or
                               (char == '.' and index + 1 < len(statement) and statement[index + 1].isspace())):
                if index < match.start():
                    start = index + 1
                else:
                    end = index
                    break
        if (nested or _subject_reference_occurrence(statement, match, start, end) or
                _subject_caller_occurrence(statement, match, start, end)):
            continue
        prefix = statement[start:match.start()].strip()
        # A preceding call/behavior belongs to the caller. Conditions and prose
        # qualifiers can precede a new subject, but another API cannot lend it
        # behavior. Shared slash subjects are accepted as one explicit list.
        qualifier = re.sub(r'(?:[A-Za-z_]\w*(?:[:.][A-Za-z_]\w*)*(?:\([^()]*\))?\s*(?:/|及|与|和|、|\band\b)\s*)+$', '', prefix).strip()
        if qualifier and (BEHAVIOR.search(qualifier) or QUALIFIED.search(qualifier) or
                          re.search(r'[A-Za-z_]\w*\s*\(|\b[A-Z][a-z]+[A-Z]\w*\b', qualifier)):
            continue
        tail = statement[match.end():end]
        if re.match(r'\s+has\s+(?:the\s+)?(?:Lua\s+)?signature\b', tail, re.I):
            return True
        # Skip balanced formal arguments, including nested defaults. This only
        # identifies the subject; the delivered atom is never cut or rewritten.
        stripped = tail.lstrip()
        if stripped.startswith('('):
            depth, quote, escaped = 0, None, False
            for index, char in enumerate(stripped):
                if quote:
                    if escaped:
                        escaped = False
                    elif char == '\\':
                        escaped = True
                    elif char == quote:
                        quote = None
                elif char in ('"', "'"):
                    quote = char
                elif char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        tail = stripped[index + 1:]
                        break
        segment = re.split(r'[。；;\n]', tail, maxsplit=1)[0]
        if BEHAVIOR.search(_data_quote_view(segment, literal_names=False)):
            return True
    return False


def _bare_method_behavior(statement, symbol):
    """Compatibility entry point for exact source navigation plus a bare subject."""
    return _subject_behavior(statement, symbol)


def _source_declared_subject(statement, symbol, source_symbols):
    """A cited declaration plus an original local relation can bind a subject.

    This path is used only for registered navigation on this exact NSF/ref.
    Formal arguments, field comparisons and named source relations are grammar,
    not extra natural-task vocabulary or facts inferred from source metadata.
    """
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    explicit = bool(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) +
                              r'(?![A-Za-z0-9_])', statement))
    spelling = symbol if explicit else method
    if _availability_only(statement, spelling):
        return False
    for match in re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(spelling) +
                             r'(?![A-Za-z0-9_])', statement):
        start = _sentence_start(statement, match.start())
        if (_subject_reference_occurrence(statement, match, start, len(statement)) or
                _subject_caller_occurrence(statement, match, start, len(statement))):
            continue
        # A bare name after a caller, condition or another owner is not a new
        # declaration. Commas inside argument/call syntax cannot create one.
        if statement[start:match.start()].strip().strip('`'):
            continue
        tail = statement[match.end():].lstrip()
        formal = tail.startswith('(')
        if not (formal or ':' in symbol or re.fullmatch(
                r'[A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*|Do|Max|Hit|Get|Put|Eat', method)):
            continue
        if formal:
            depth, quote, escaped, closed = 0, None, False, False
            for index, char in enumerate(tail):
                if quote:
                    if escaped:
                        escaped = False
                    elif char == '\\':
                        escaped = True
                    elif char == quote:
                        quote = None
                elif char in ('"', "'"):
                    quote = char
                elif char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        tail, closed = tail[index + 1:], True
                        break
            if not closed:
                continue
        clause = re.split(r'[。；;\n]|\.\s+', tail, maxsplit=1)[0]
        comparison = r'(?<![A-Za-z0-9_])(?:self\.)?[A-Za-z_]\w*\s*(?:==|~=|<=|>=|<|>)\s*\S'
        if not formal and re.search(comparison, clause):
            return True
        # 仅同原 NSF/ref 的声明证据可绑定 uses 的直接宾语；不借后句行为。
        if re.match(r'^[ \t]*uses?[ \t]+(?![。；;,.\r\n])\S', tail, re.I):
            return True
        if formal:
            # A declaration's first sentence may define parameters before a
            # semicolon, then give its own guards/branches. It cannot borrow a
            # later independent sentence's method behavior.
            sentence = re.split(r'[。\n]|\.\s+', tail, maxsplit=1)[0]
            # 顶层逗号也能换主体；实参/引号内逗号仍属于原表达式。
            segments, segment_start = [], 0
            depth, quote, escaped = 0, None, False
            for index, char in enumerate(sentence):
                if quote:
                    if escaped:
                        escaped = False
                    elif char == '\\':
                        escaped = True
                    elif char == quote:
                        quote = None
                elif depth and char in ('"', "'"):
                    quote = char
                elif char == '(':
                    depth += 1
                elif char == ')' and depth:
                    depth -= 1
                elif not depth and char in '，,；;':
                    segments.append(sentence[segment_start:index])
                    segment_start = index + 1
            segments.append(sentence[segment_start:])
            own_segments = segments[:1]
            declared = {name.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
                        for name in source_symbols}
            for segment in segments[1:]:
                if re.match(r'^\s*(?:该|此)?(?:fn|action|caller|function|调用者|动作)'
                            r'(?![A-Za-z0-9_])', segment, re.I):
                    break
                head = re.match(r'^\s*([A-Za-z_]\w*(?:[:.][A-Za-z_]\w*)*)', segment)
                if (head and not re.match(comparison, segment.strip()) and
                        (QUALIFIED.fullmatch(head[1]) or head[1] in declared) and head[1] not in (symbol, method)):
                    break
                own_segments.append(segment)
            sentence = ';'.join(own_segments)
            if re.search(comparison, sentence) or BEHAVIOR.search(sentence):
                return True
        else:
            # A source-declared method can be the grammatical subject of a
            # local relation to another source-declared method without spelling
            # a call, e.g. a getter asking its owner's slot lookup. Mere names,
            # field paths or metadata that contains names cannot establish it.
            dependencies = {name.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
                            for name in source_symbols if name != symbol}
            active_predicate = bool(re.match(r'^\s*[a-z][a-z_]*(?:s|ed)\s+\S', tail))
            if active_predicate and any(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(name) +
                                                  r'(?![A-Za-z0-9_])', clause)
                                        for name in dependencies):
                return True
    return False


def _call_list_prefix(value):
    """Only direct or coordinated call objects can share a call predicate."""
    depth, quote, escaped, plain = 0, None, False, []
    for char in value:
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif depth and char in ('"', "'"):
            quote = char
        elif char == '(':
            depth += 1
        elif char == ')' and depth:
            depth -= 1
        elif not depth:
            plain.append(char)
    if depth or quote:
        return False
    plain = ''.join(plain)
    plain = QUALIFIED.sub('', plain)
    plain = re.sub(r'(?<![A-Za-z0-9_])(?:[A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*|Do|Max|Hit|Get|Put|Eat)(?![A-Za-z0-9_])', '', plain)
    return not re.sub(r'\b(?:and|or|forced)\b|[\s`,，、/]|及|与|和', '', plain, flags=re.I)


def _callsite_relations(statement, symbol):
    """Classify a local invocation predicate, never an atom-wide negation."""
    if not isinstance(statement, str):
        return []
    # 字符串和实参中的名字不向外借调用谓词；嵌套函数留在本函数代码指纹中。
    def visible_text(value):
        plain, depth, quote, escaped = [], 0, None, False
        closers = {'"': '"', "'": "'", '“': '”', '‘': '’'}
        for index, char in enumerate(value):
            if quote:
                plain.append(' ')
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in closers and not (char == "'" and index and value[index - 1].isalnum()
                                            and index + 1 < len(value) and value[index + 1].isalnum()):
                quote = closers[char]
                plain.append(' ')
            elif char in '([{':
                depth += 1
                plain.append(' ')
            elif char in ')]}' and depth:
                depth -= 1
                plain.append(' ')
            else:
                plain.append(char if not depth else ' ')
        return ''.join(plain)

    flags = re.I | re.ASCII
    modifiers = re.compile(r'(?:(?:\b(?:directly|explicitly|automatically)\b|直接|自动|显式(?:地)?)\s*)+$', flags)
    boundaries = re.compile(r'[，,。；;!?！？\n]|\b(?:but|and|then|however|else|otherwise|while)\b|但是|但|随后|然后|接着|之后|否则|反之', flags)
    uncertain = re.compile(r'\b(?:may|might|could|possibly|perhaps)\s*(?:(?:not|never)\s*)?$|'
        r'\bwhether\b[^.;。；]*$|(?:是否|可能|未确认|尚未确认|未证实|尚未证实)'
        r'(?:会|将|并不|不会|没有|未曾|从不|不|未)?\s*$', flags)
    negative = re.compile(r"\b(?:(?:does|do|did|will|would|can|should|must)\s+not|cannot|[a-z]+n['’]t|not|never|neither)\s*$|"
                          r'(?:并不|不会|没有|未曾|从不|不|未)\s*$', flags)
    action = re.compile(r'\b(?:calls?|invokes?|executes?|runs?|uses?|cancels?|removes?|stops?)\b|调用|执行|取消|移除|停止|清理', flags)

    def local_polarity(value):
        value = modifiers.sub('', value.strip()).strip()
        if uncertain.search(value):
            return 'UNDETERMINED'
        if negative.search(value):
            return 'NEGATIVE'
        return None

    def predicate_polarity(value):
        value = boundaries.split(value)[-1]
        direct = local_polarity(value)
        if direct is not None:
            return direct
        tail = modifiers.sub('', value.strip()).strip()
        connector = re.search(r'\b(?:or|nor)\s*$|或\s*$', tail, flags)
        if connector is not None:
            head = tail[:connector.start()]
            # 只识别一个明确协调层；更复杂嵌套不能硬造肯定调用。
            nested = bool(re.search(r'\b(?:or|nor)\b|或', head, flags))
            for prior in action.finditer(head):
                polarity = local_polarity(head[:prior.start()])
                if polarity is not None:
                    return 'UNDETERMINED' if nested else polarity
            if re.search(r'\b(?:not|never|neither|cannot|may|might|could|whether)\b|是否|可能|没有|不会|不', head, flags):
                return 'UNDETERMINED'
        return 'POSITIVE'

    visible = visible_text(statement)
    result = []
    for occurrence in re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', statement):
        if visible[occurrence.start():occurrence.end()] != occurrence[0]:
            continue
        start = _sentence_start(visible, occurrence.start())
        prefix = visible[start:occurrence.start()]
        # Keep the call object visible to lookahead while accepting only
        # predicates that finish before that object.
        context = visible[start:occurrence.end()]
        markers = [marker for marker in CALL_CONTEXT.finditer(context)
                   if marker.end() <= len(prefix)]
        if not markers:
            continue
        marker = markers[-1]
        between = statement[start + marker.end():occurrence.start()]
        captured_invocation = (marker[0] in ('调用', '执行') and QUALIFIED.fullmatch(symbol)
                               and re.fullmatch(r'\s*(?:原)?捕获\s*', between)
                               and re.match(r'\s*\(', statement[occurrence.end():]))
        coordinated = re.sub(r'\bnor\b|或', ' or ', between, flags=flags)
        if not (_call_list_prefix(coordinated) or captured_invocation):
            continue
        predicate = prefix[:marker.start()]
        polarity = predicate_polarity(predicate)
        result.append({'relation_polarity': polarity, 'symbol_span': [occurrence.start(), occurrence.end()],
                       'predicate_span': [start + marker.start(), start + marker.end()]})
    return result


def _callsite_context(statement, symbol):
    """An explicit affirmative invocation is bounded caller evidence only."""
    return any(r['relation_polarity'] == 'POSITIVE' for r in _callsite_relations(statement, symbol))


def statement_binding(statement, symbol, allow_bare=False, source_callable=False):
    """Derived role and invocation polarity from one unchanged original atom."""
    if not isinstance(statement, str):
        return None
    explicit = bool(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', statement))
    spelling = symbol if explicit else symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    if not explicit and not allow_bare:
        return None
    if _availability_only(statement, spelling):
        return {'role': 'AVAILABILITY_EXISTENCE', 'relation_polarity': 'UNDETERMINED',
                'positive_callsite_evidence': False, 'callee_semantics_supported': False}
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    callable_shape = (source_callable or ':' in symbol or bool(re.fullmatch(r'[A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*|Do|Max|Hit|Get|Put|Eat', method)) or
                      bool(re.search(re.escape(spelling) + r'\s*\(', statement)) or
                      any(CALLABLE_RESULT.search(statement[m.end():]) for m in re.finditer(re.escape(spelling), statement)))
    relations = _callsite_relations(statement, spelling) if callable_shape else []
    if relations:
        polarities = {r['relation_polarity'] for r in relations}
        polarity = next(iter(polarities)) if len(polarities) == 1 else 'UNDETERMINED'
        role, kind = {'POSITIVE': ('BOUNDED_CALLEE_CALLSITE', 'bounded_caller_callsite'),
                      'NEGATIVE': ('BOUNDED_CALLEE_NONCALL', 'bounded_caller_noncall'),
                      'UNDETERMINED': ('BOUNDED_CALLEE_RELATION_UNDETERMINED', 'bounded_caller_relation_unresolved')}[polarity]
        return {'role': role, 'relation_polarity': polarity, 'binding_kind': kind,
                'positive_callsite_evidence': polarity == 'POSITIVE',
                'callee_semantics_supported': False, 'call_relations': relations}
    if callable_shape and _subject_behavior(statement, symbol, exact=explicit):
        return {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                'positive_callsite_evidence': False, 'callee_semantics_supported': True}
    return None


def statement_binding_role(statement, symbol, allow_bare=False, source_callable=False):
    """Public grammar classifier shared by runtime matching and catalog auditing."""
    binding = statement_binding(statement, symbol, allow_bare, source_callable)
    return binding['role'] if binding else None


def _source_bound_independent_subject(record, family, pointer, symbol, statement):
    """A prior call occurrence cannot erase a separately stated method subject.

    Bare prose heads require a unique, already validated declaration in this
    exact NSF. Identity supplies only the receiver; the predicate must be stated
    by the independent original clause, never by a call argument or label.
    """
    if family != 'core' or not QUALIFIED.fullmatch(symbol) or not isinstance(statement, str):
        return False
    method = re.split(r'[.:]', symbol)[-1]
    proofs = [proof for proof in source_identity.record_identity_bindings(record, family)
              if proof.get('record_pointer') == pointer and proof.get('claim_kind') == 'NSF'
              and proof.get('statement_sha256') == _digest(statement)
              and proof.get('identity_is_behavior_proof') is False
              and proof.get('runtime_verified') is False
              and re.split(r'[.:]', proof.get('declared_symbol', ''))[-1] == method]
    selected = [proof for proof in proofs if proof.get('declared_symbol') == symbol]
    if not selected:
        return False
    physical = {(proof.get('declared_symbol'), proof.get('source_file'),
                 proof.get('declaration_line'), proof.get('declaration_header')) for proof in proofs}
    visible = _data_quote_view(statement, literal_names=False)
    for clause in re.split(r'[。；;\n]|\.\s+', visible):
        head = re.match(r'\s*(' + re.escape(symbol) + '|' + re.escape(method) +
                        r')(?![A-Za-z0-9_:.])', clause)
        if not head or (head[1] == method and len(physical) != 1):
            continue
        tail = re.sub(r'^\s*(?:(?:仅|只|会|总是|直接|都|本身)\s*|'
                      r'\b(?:only|just|always|directly)\b\s*)*', '', clause[head.end():], flags=re.I)
        if (BEHAVIOR.match(tail) and _subject_behavior(clause, symbol, exact=head[1] == symbol)):
            return True
    return False


def _mapped_owner_subject(statement, symbol, source_bindings):
    """Recheck an accepted subject using its declared source owner and prose."""
    if not isinstance(statement, str) or not QUALIFIED.fullmatch(symbol) or re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', statement):
        return False
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    occurrences = list(re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(method) + r'(?![A-Za-z0-9_])', statement))
    if not occurrences and any(name.rsplit(':', 1)[-1].rsplit('.', 1)[-1] == method
                               for name in QUALIFIED.findall(statement)):
        return False
    local = statement_binding(statement, symbol, allow_bare=True, source_callable=True)
    callee_only = (local is not None and local['role'] in ('BOUNDED_CALLEE_CALLSITE',
                  'BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED') and
                  not _subject_behavior(statement, symbol, exact=False))
    reference_only = _subject_reference_only(statement, symbol, allow_bare=True)
    caller_only = occurrences and all(_subject_caller_occurrence(
        statement, occurrence, _sentence_start(statement, occurrence.start()), len(statement)) or
        _subject_reference_occurrence(statement, occurrence,
            _sentence_start(statement, occurrence.start()), len(statement))
        for occurrence in occurrences)
    if callee_only or reference_only or caller_only:
        return False
    receiver = symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0]
    declared = False
    for binding in source_bindings:
        if normalize_symbol(binding.get('symbol', '')) != symbol:
            continue
        if _steam_binding_proof(binding, symbol) is not None:
            declared = True
        locator = binding.get('source_locator', {})
        for field in ('symbol', 'function', 'signature', 'signatures'):
            value = locator.get(field, [])
            values = [value] if isinstance(value, str) else value if isinstance(value, list) else []
            if any(isinstance(name, str) and symbol in QUALIFIED.findall(name) for name in values):
                declared = True
    return declared and _subject_behavior(statement, receiver, exact=True)


def _steam_binding_proof(binding, symbol):
    """Match an unmended citation to its accepted literal declaration proof."""
    if (binding.get('original_reference_precision') != 'EXACT_STEAM_CITATION_DECLARATION' or
            binding.get('name_kind') != 'exact_frozen_declaration' or binding.get('symbol') != symbol):
        return None
    try:
        for proof in source_identity._registry().public_alias_rows(symbol):
            if (proof.get('schema') != source_identity.STEAM_SCHEMA or proof['declared_symbol'] != symbol or
                    binding.get('declaration_identity_proof') != proof or
                    binding.get('record_pointer') != proof['record_pointer'] or
                    any(binding.get(key) != proof['reference'].get(key) for key in ('artifact_path', 'sha256', 'pointer')) or
                    binding.get('source_file') != proof['source_file']):
                continue
            locator = binding.get('source_locator', {})
            if all(locator.get(left) == proof.get(right) for left, right in (
                    ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                    ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'), ('line_end', 'line_end'))):
                return proof
    except (KeyError, ValueError, TypeError, OSError):
        return None
    return None


def _unique_accepted_declaration_leaf(proof, all_proofs):
    peers = [row for row in all_proofs if row['record_pointer'] == proof['record_pointer'] and
             row['reference'] == proof['reference'] and
             row['artifact_value_sha256'] == proof['artifact_value_sha256']]
    physical = {(row['source_lf_sha256'], row['source_file'], row['declaration_line'],
                 row['declared_symbol'], row['declaration_kind']) for row in peers}
    if len(physical) != 1:
        return False
    # 身份索引按原引用中的名字筛声明，不能把请求过滤后的一条证明误当整个区间只有一个声明。
    try:
        registry = source_identity._registry()
        if proof['range_hash_mode'] == 'RAW_EXACT_LINE_BYTES':
            raw = base64.b64decode(registry.raw_ranges[proof['range_bytes_ref']], validate=True)
        else:
            raw = registry.ranges[proof['range_text_ref']].encode('utf-8')
        if sha256(raw).hexdigest() != proof['cited_range_sha256']:
            return False
        lines = raw.decode('utf-8').splitlines()
    except (KeyError, TypeError, ValueError, UnicodeError, OSError):
        return False
    headers = [(proof['line_start'] + offset, line)
               for offset, line in enumerate(lines) if source_identity.HEADER.match(line)]
    return headers == [(proof['declaration_line'], proof['declaration_header'])]


def _declared_original_subject(record, family, pointer, symbol):
    """An original subject witness proves prose grammar, never method behavior."""
    if (family != 'core' or not QUALIFIED.fullmatch(symbol) or
            source_identity.resolve_identity(record, family, symbol) != symbol):
        return None
    atom = next((atom for atom in _typed_atoms(record, family) if atom['record_pointer'] == pointer), None)
    if (not atom or atom['kind'] != 'NSF' or not isinstance(atom['statement'], str) or _sample_scope(record, atom)):
        return None
    owner = symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0]
    try:
        source_identity._lexical_fingerprint()
        witness = source_identity.lexical.subject_witness(atom['statement'], symbol)
    except (TypeError, ValueError, OSError):
        return None
    if not witness or witness.get('declared_owner') != owner:
        return None
    proofs = [proof for proof in source_identity.identity_bindings(record, family, symbol)
              if proof.get('schema') == 'accepted-original-subject-declaration-identity/1' and
              proof.get('proof_kind') == 'ORIGINAL_NSF_SUBJECT_IN_PINNED_CITATION_RANGE' and
              proof.get('record_sha256') == _digest(record) and proof.get('record_pointer') == pointer and
              proof.get('claim_kind') == 'NSF' and proof.get('statement_sha256') == _digest(atom['statement']) and
              proof.get('declared_symbol') == symbol and proof.get('aliases') == [symbol] and
              proof.get('owner') == owner and proof.get('subject_witness') == witness and
              proof.get('identity_is_behavior_proof') is False and proof.get('runtime_verified') is False]
    if not proofs:
        return None
    return {'schema': 'original-pinned-nsf-subject-relation/1', 'record_pointer': pointer,
            'qualified_identity': symbol, 'owner': owner, 'claim_kind': 'NSF',
            'whole_statement_sha256': _digest(atom['statement']), 'subject_witness': copy.deepcopy(witness),
            'accepted_declaration_sha256': [_digest(proof) for proof in proofs],
            'same_original_atom_and_reference': True, 'identity_is_behavior_proof': False,
            'subject_syntax_is_method_body_proof': False}


def _qualified_getter_context(record, family, symbol):
    """Prove a qualified getter's local branch mention, never method behavior."""
    if (family != 'core' or not QUALIFIED.fullmatch(symbol) or
            source_identity.resolve_identity(record, family, symbol) != symbol):
        return []
    owner = symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0]
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    bare = r'(?<![A-Za-z0-9_:.])' + re.escape(method) + r'(?![A-Za-z0-9_])'
    branch = re.compile(bare + r'(?:\s*\([^()\n]*\))?'
        r'(?:\s*/\s*[A-Za-z_]\w*(?:\([^()\n]*\))?)*\s*的(?:实际)?分支条件(?:是|为)'
        r'[^。；;\n]*(?:委托|返回|读取|读)', re.ASCII)
    proofs = source_identity.identity_bindings(record, family, symbol)
    atoms = {atom['record_pointer']: atom for atom in _typed_atoms(record, family)}
    result = []
    for proof in proofs:
        pointer = proof['record_pointer']
        atom = atoms.get(pointer)
        if (not atom or atom['kind'] != 'NSF' or not isinstance(atom['statement'], str) or
                not branch.search(atom['statement']) or _sample_scope(record, atom) or
                proof['owner'] != owner or proof['declared_symbol'] != symbol or
                proof['declaration_kind'] not in ('colon_method', 'qualified_dot_function')):
            continue
        try:
            registry = source_identity._registry()
            raw = (base64.b64decode(registry.raw_ranges[proof['range_bytes_ref']], validate=True)
                   if proof['range_hash_mode'] == 'RAW_EXACT_LINE_BYTES' else
                   registry.ranges[proof['range_text_ref']].encode('utf-8'))
            if sha256(raw).hexdigest() != proof['cited_range_sha256']:
                continue
            headers = [(proof['line_start'] + offset, line)
                       for offset, line in enumerate(raw.decode('utf-8').splitlines())
                       if (header := source_identity.HEADER.match(line)) and header[2] == symbol]
        except (KeyError, TypeError, ValueError, UnicodeError, OSError):
            continue
        # 多声明段只核对目标头的身份；旧“单方法整段”行为门禁完全保留。
        if headers != [(proof['declaration_line'], proof['declaration_header'])]:
            continue
        result.append({'schema': 'qualified-getter-branch-context/1', 'record_sha256': _digest(record),
                       'record_pointer': pointer, 'claim_kind': 'NSF', 'qualified_identity': symbol,
                       'owner': owner, 'whole_statement_sha256': _digest(atom['statement']),
                       'role': 'TYPED_EVIDENCE_CONTEXT', 'declaration_identity_proof': copy.deepcopy(proof),
                       'context_is_method_contract': False, 'callee_semantics_supported': False,
                       'full_method_contract_verified': False, 'single_method_range_verified': False})
    return result


def _mapped_single_leaf_proofs(spec, proofs, symbol, all_proofs):
    """Join existing typed pointers to accepted declarations, never owner aliases."""
    pointers = spec.get('record_pointers', [])
    if (not pointers or spec.get('mapping_status') != 'TYPED_CONTRACT' or
            spec.get('context_only') is True or
            spec.get('binding_kind') in ('identity_only', 'availability_existence', 'typed_evidence_context') or
            set(pointers).intersection(spec.get('excluded_record_pointers', []))):
        return []
    accepted = []
    for pointer in pointers:
        own = []
        for binding in spec.get('source_bindings', {}).get(pointer, []):
            steam_proof = _steam_binding_proof(binding, symbol)
            if binding.get('original_reference_precision') != 'SINGLE_SOURCE_LOCATOR_NODE' and steam_proof is None:
                continue
            locator = binding.get('source_locator', {})
            for proof in proofs:
                if (proof['record_pointer'] != pointer or proof['claim_kind'] != 'NSF' or
                        normalize_symbol(symbol).rsplit(':', 1)[-1].rsplit('.', 1)[-1] !=
                        proof['declared_symbol'].rsplit(':', 1)[-1].rsplit('.', 1)[-1] or
                        binding.get('source_file') != proof['source_file'] or
                        (steam_proof != proof and locator.get('symbol') not in (proof['declared_symbol'],
                            proof['declared_symbol'].rsplit(':', 1)[-1].rsplit('.', 1)[-1])) or
                        binding.get('original_source_value_sha256') != proof['artifact_value_sha256'] or
                        any(binding.get(key) != proof['reference'].get(key)
                            for key in ('artifact_path', 'sha256', 'pointer')) or
                        any(locator.get(left) != proof.get(right) for left, right in (
                            ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                            ('line_start', 'line_start'), ('line_end', 'line_end'),
                            ('range_sha256', 'cited_range_sha256')))):
                    continue
                # 声明索引已校验 raw/LF 与区间表示；这里只比较同一原引用的承诺，禁止自行归一化 hash。
                if _unique_accepted_declaration_leaf(proof, all_proofs) and proof not in own:
                    own.append(proof)
        if not own:
            return []
        for proof in own:
            if proof not in accepted:
                accepted.append(proof)
    return accepted


def _identity_mapped_spec(record, family, symbol, mapped):
    """Select an existing map only through the same physical declaration."""
    identities = source_identity.resolve_identities(record, family,
        [symbol, *mapped.get('contracts', {})])
    declared = identities[symbol]
    if declared is None:
        return None
    proofs = source_identity.identity_bindings(record, family, symbol)
    all_proofs = None
    pointers = {proof['record_pointer'] for proof in proofs}
    candidates = []
    contracts = mapped.get('contracts', {})
    # 精确映射保持优先；只有缺少精确项时才比较其他映射，且不能在歧义中任选。
    choices = [(symbol, contracts[symbol])] if symbol in contracts else contracts.items()
    for name, spec in choices:
        if identities[name] is not None and identities[name] != declared:
            continue
        existing = (identities[name] == declared and pointers.intersection(
            spec.get('record_pointers', []) + spec.get('availability_record_pointers', [])))
        leaf_proofs = []
        if not existing:
            if all_proofs is None:
                all_proofs = _record_identity_bindings(record, family)
            leaf_proofs = _mapped_single_leaf_proofs(spec, proofs, name, all_proofs)
        if existing or leaf_proofs:
            candidates.append((name, spec, leaf_proofs or list(proofs)))
    # 多个不同映射即使共用一处声明也不任意选第一个；同一映射的多条原引用可合并。
    if len(candidates) != 1:
        return None
    original_symbol, original, selected_proofs = candidates[0]
    spec = copy.deepcopy(original)
    # 声明证明只补身份，不把 caller、REC 或存在性改成方法主体。
    spec['receiver'] = selected_proofs[0]['owner']
    spec['original_contract_symbol'] = original_symbol
    spec['identity_declaration_proofs'] = copy.deepcopy(selected_proofs)
    return spec


def _declared_local_subject(record, family, pointer, symbol):
    """Bind adjacent original prose only after the exact declaration/ref is proved."""
    if family != 'core' or not QUALIFIED.fullmatch(symbol):
        return None
    atom = next((atom for atom in _typed_atoms(record, family)
                 if atom['record_pointer'] == pointer), None)
    if not atom or atom['kind'] != 'NSF' or not isinstance(atom['statement'], str):
        return None
    proofs = [proof for proof in source_identity.identity_bindings(record, family, symbol)
              if proof['record_pointer'] == pointer and proof['claim_kind'] == 'NSF']
    if not proofs:
        return None
    owner = symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0]
    if any(proof['owner'] != owner for proof in proofs):
        return None
    statement = atom['statement']
    clauses = re.split(r'[。；;\n]|\.\s+', statement)
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    bare = r'(?<![A-Za-z0-9_:.])' + re.escape(method) + r'(?![A-Za-z0-9_])'
    uncertain = re.compile(r"没有|不会|可能|也许|未曾|尚未|未|不|\b(?:no|not|never|cannot|[a-z]+n['’]t|without|may|might|could|possibly|whether)\b", re.I)
    for index, clause in enumerate(clauses):
        if not index:
            continue
        previous = clauses[index - 1].strip()
        nominal = re.fullmatch(r'\s*(?:它的|其|its\b)\s*' + bare +
            r'\s*(?:\([^()\n]*\))?\s*(?:是|is\b)\s*([^，,]*)[，,]?.*', clause, re.I)
        installed = re.search(r'(?:添加|安装|\badds?|\binstalls?)\s+(?:an?\s+)?' +
                              re.escape(owner) + r'\s*$', previous, re.I)
        if (nominal and installed and not uncertain.search(previous) and
                not uncertain.search(nominal[1]) and
                re.search(r'\b(?:getter|accessor)\s*\.?$', nominal[1], re.I)):
            relation = 'ADJACENT_INSTALLED_OWNER_AND_ITS_NOMINAL_GETTER'
        else:
            latter = re.match(r'\s*(?:后者|the latter\b)\s*', clause, re.I)
            if not latter or not BEHAVIOR.match(clause[latter.end():]):
                continue
            occurrences = list(re.finditer(bare, previous))
            if len(occurrences) != 1:
                continue
            occurrence = occurrences[0]
            if not re.fullmatch(r'\s*(?:\([^()\n]*\))?\s*', previous[occurrence.end():]):
                continue
            callers = QUALIFIED.findall(previous[:occurrence.start()])
            if len(callers) != 1:
                continue
            caller_owner = callers[0].rsplit(':', 1)[0] if ':' in callers[0] else callers[0].rsplit('.', 1)[0]
            relations = _callsite_relations(previous, method)
            if (caller_owner != owner or not relations or
                    any(row['relation_polarity'] != 'POSITIVE' for row in relations) or
                    _subject_reference_occurrence(previous, occurrence, 0, len(previous))):
                continue
            relation = 'ADJACENT_SAME_OWNER_CALLEE_AND_LATTER_BEHAVIOR'
        return {'schema': 'original-declared-local-subject/1', 'relation': relation,
                'qualified_identity': symbol, 'owner': owner,
                'antecedent_clause_index': index - 1, 'subject_clause_index': index,
                'same_original_atom_and_reference': True,
                'declaration_is_behavior_proof': False}
    return None


def _declared_property_subject(record, family, pointer, symbol):
    """Join original property behavior to its exact cited Class callback map.

    The on<field> spelling supplies no relation. Both the callback declaration
    and literal Class property table must occur in the same accepted source
    range, while the behavior still comes exclusively from the whole NSF.
    """
    if family != 'core' or not re.fullmatch(r'[A-Za-z_]\w*', symbol):
        return None
    atom = next((a for a in _typed_atoms(record, family) if a['record_pointer'] == pointer), None)
    if not atom or atom['kind'] != 'NSF' or not isinstance(atom['statement'], str):
        return None
    for proof in source_identity.identity_bindings(record, family, symbol):
        if (proof['record_pointer'] != pointer or proof['claim_kind'] != 'NSF' or
                proof['declaration_kind'] != 'file_local_function'):
            continue
        try:
            registry = source_identity._registry()
            raw = (base64.b64decode(registry.raw_ranges[proof['range_bytes_ref']], validate=True)
                   if proof['range_hash_mode'] == 'RAW_EXACT_LINE_BYTES' else
                   registry.ranges[proof['range_text_ref']].encode('utf-8'))
            if sha256(raw).hexdigest() != proof['cited_range_sha256']:
                continue
            text = raw.decode('utf-8').replace('\r\n', '\n')
            source_identity._lexical_fingerprint()
            masked = source_identity.lexical.scan(text)['masked']
            classes = list(re.finditer(r'\blocal\s+([A-Za-z_]\w*)\s*=\s*Class\s*\(\s*function\s*\(', masked))
            tails = list(re.finditer(r'\bend\s*,\s*nil\s*,\s*\{([^{}]*)\}\s*\)', masked))
            if len(classes) != 1 or len(tails) != 1 or classes[0].end() >= tails[0].start():
                continue
            properties = re.findall(r'(?:^|,)\s*([A-Za-z_]\w*)\s*=\s*' +
                                    re.escape(symbol) + r'\s*(?=,|$)', tails[0][1], re.ASCII)
            if len(properties) != 1:
                continue
            prop = properties[0]
            statement = atom['statement']
            # Require original prose to assert the mapped property's behavior.
            # An occurrence in another method's arguments is insufficient.
            property_behavior = _subject_behavior(statement, prop, exact=True)
            assignment_behavior = bool(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(prop) +
                r'\s*=\s*[^，,。；;\n()（）]+[（(]\s*(?:property|属性)\s*'
                r'(?:令|使|回调|updates?\b|sets?\b)[^）)]+[）)]', statement, re.I))
            if not property_behavior and not assignment_behavior:
                continue
            return {'schema': 'original-class-property-callback-subject/1',
                    'record_pointer': pointer, 'qualified_identity': symbol,
                    'source_file': proof['source_file'], 'declaration_kind': 'file_local_function',
                    'class_name': classes[0][1], 'property': prop,
                    'same_original_atom_and_reference': True,
                    'declaration_is_behavior_proof': False,
                    'class_mapping_source_reference': copy.deepcopy(proof['reference'])}
        except (KeyError, TypeError, ValueError, UnicodeError, OSError):
            continue
    return None


def _contract_matches(record, family, symbol):
    """Return existing typed pointers, receiver and explicit absence of a contract."""
    symbol = normalize_symbol(symbol)
    mapped = _record_map(record)
    spec = mapped.get('contracts', {}).get(symbol)
    if spec is None:
        spec = _identity_mapped_spec(record, family, symbol, mapped)
    atoms = _typed_atoms(record, family)
    by_pointer = {a['record_pointer']: a for a in atoms}
    # 显式冻结映射（包括空身份映射）保持权威；仅无 spec 时派生声明主体。
    frozen_identity = None
    if spec is not None:
        pointers = spec.get('record_pointers', [])
        availability = spec.get('availability_record_pointers', [])
        if any(pointer not in by_pointer for pointer in pointers + availability):
            raise ValueError('Contract pointer not found in canonical record')
        frozen_identity = [{'symbol': symbol, 'record_pointers': list(pointers),
                 'claim_kinds': [by_pointer[p]['kind'] for p in pointers],
                 'receiver': spec.get('receiver'),
                 'mapping_status': spec.get('mapping_status', 'TYPED_CONTRACT'),
                 'mapping_basis': spec.get('mapping_basis', 'EXPLICIT_FROZEN_TYPED_CLAIM'),
                 'pointer_roles': copy.deepcopy(spec.get('pointer_roles', {})),
                 'owner_basis': copy.deepcopy(spec.get('owner_basis', [])),
                 'binding_kind': 'typed_behavioral_contract' if pointers else 'availability_existence' if availability else 'identity_only',
                 'availability_record_pointers': list(availability),
                 'availability_claim_kinds': [by_pointer[p]['kind'] for p in availability],
                 'record_sha256': _digest(record),
                 'claim_reference_bindings': {p: copy.deepcopy(mapped.get('claim_reference_bindings', {}).get(p, [])) for p in pointers + availability},
                 'source_bindings': {p: copy.deepcopy(spec.get('source_bindings', {}).get(p, [])) for p in pointers + availability},
                 **({key: copy.deepcopy(spec[key]) for key in ('original_contract_symbol', 'identity_declaration_proofs') if key in spec}),
                 'original_scope': copy.deepcopy(mapped.get('original_scope', record.get('scope'))),
                 'original_governance': copy.deepcopy(mapped.get('original_governance', {})),
                 'method_semantics_not_synthesized': True}]
        if pointers or availability:
            return frozen_identity
    navigation = _registered_navigation(record, family)
    registered = [n for n in navigation if n['symbol'] == symbol]
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    # Same bare name with two cited receiver owners is ambiguous. Exact qualified
    # text can still use the existing exact-text path below; bare text cannot.
    registered = [n for n in registered if QUALIFIED.fullmatch(symbol) and re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) +
                                                   r'(?![A-Za-z0-9_])', by_pointer[n['record_pointer']]['statement']) or
                  (len({name.rsplit(':', 1)[0] if ':' in name else name.rsplit('.', 1)[0]
                        for name in [other['symbol'] for other in navigation
                                     if other['record_pointer'] == n['record_pointer'] and not other.get('context_only')]
                        + QUALIFIED.findall(by_pointer[n['record_pointer']]['statement'])
                        if name.rsplit(':', 1)[-1].rsplit('.', 1)[-1] == method}) == 1 and
                   (QUALIFIED.fullmatch(symbol) or
                    source_identity.resolve_identity(record, family, symbol) == symbol))]
    local_subjects = {n['record_pointer']: relation for n in registered
                      if (relation := _declared_local_subject(record, family, n['record_pointer'], symbol))}
    local_subjects.update({n['record_pointer']: relation for n in registered
                           if (relation := _declared_property_subject(record, family, n['record_pointer'], symbol))})
    derived = [by_pointer[n['record_pointer']] for n in registered
               if not n.get('context_only') and by_pointer[n['record_pointer']]['kind'] == 'NSF' and
               isinstance(by_pointer[n['record_pointer']]['statement'], str) and
                (n['record_pointer'] in local_subjects or
                 _bare_method_behavior(by_pointer[n['record_pointer']]['statement'], symbol) or
                _source_declared_subject(by_pointer[n['record_pointer']]['statement'], symbol,
                    [other['symbol'] for other in navigation
                     if other['record_pointer'] == n['record_pointer'] and not other.get('context_only')]))]
    derived = list({a['record_pointer']: a for a in derived}.values())
    if derived:
        return [{'symbol': symbol, 'record_pointers': [a['record_pointer'] for a in derived],
                 'claim_kinds': [a['kind'] for a in derived],
                 'receiver': symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0] if '.' in symbol else None,
                 'mapping_status': 'TYPED_CONTRACT',
                 'mapping_basis': 'ACCEPTED_NAVIGATION_PLUS_BARE_METHOD_BEHAVIOR_IN_ORIGINAL_NSF',
                 'binding_kind': 'typed_behavioral_contract',
                  'pointer_roles': {a['record_pointer']: {
                      'role': 'SOURCE_OBSERVATION_SUBJECT' if _sample_scope(record, a) else 'METHOD_SUBJECT',
                      'basis': 'ORIGINAL_DECLARED_LOCAL_SUBJECT' if a['record_pointer'] in local_subjects else 'ORIGINAL_BARE_NAMED_SUBJECT',
                      **({'local_subject_relation': local_subjects[a['record_pointer']]}
                         if a['record_pointer'] in local_subjects else {})} for a in derived},
                 'availability_record_pointers': [],
                 'source_bindings': {a['record_pointer']: [
                     {**{key: n[key] for key in ('artifact_path', 'sha256', 'pointer')},
                      'source_file': n.get('source_file'), 'source_locator': {'symbol': symbol},
                      **({'declaration_identity_proof': copy.deepcopy(n['declaration_identity_proof'])}
                         if n.get('declaration_identity_proof') else {}),
                      'original_reference_precision': 'REGISTERED_DECLARATION_NAVIGATION_ONLY'}
                     for n in registered if n['record_pointer'] == a['record_pointer']]
                     for a in derived},
                 'method_semantics_not_synthesized': True}]
    if symbol in contract_symbols(record, family):
        if frozen_identity is not None:
            return frozen_identity
        # Exact spelling in a typed statement maps only that whole statement.
        # Name lists / negative API availability lists cannot supply per-method behavior.
        qualified = ':' in symbol or '.' in symbol
        roles = {a['record_pointer']: statement_binding_role(a['statement'], symbol)
                 for a in atoms if a['kind'] == 'NSF' and isinstance(a['statement'], str)}
        eligible = [a for a in atoms if roles.get(a['record_pointer']) in ('METHOD_SUBJECT', 'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')]
        availability = [a['record_pointer'] for a in atoms if roles.get(a['record_pointer']) == 'AVAILABILITY_EXISTENCE']
        availability.extend(n['record_pointer'] for n in registered
                            if not n.get('context_only') and by_pointer[n['record_pointer']]['kind'] == 'NSF' and
                            _availability_only(by_pointer[n['record_pointer']]['statement'], method))
        availability = list(dict.fromkeys(availability))
        if qualified and eligible:
            return [{'symbol': symbol, 'record_pointers': [a['record_pointer'] for a in eligible],
                     'claim_kinds': [a['kind'] for a in eligible],
                     'receiver': symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0],
                     'mapping_status': 'TYPED_CONTRACT',
                     'mapping_basis': 'EXACT_SYMBOL_IN_WHOLE_TYPED_CLAIM',
                     'binding_kind': 'typed_behavioral_contract',
                     'availability_record_pointers': availability,
                     'pointer_roles': {a['record_pointer']: {'role': 'SOURCE_OBSERVATION_SUBJECT' if roles[a['record_pointer']] == 'METHOD_SUBJECT' and _sample_scope(record, a) else roles[a['record_pointer']], 'basis': 'EXACT_SYMBOL_ROLE_IN_ORIGINAL_WHOLE_NSF'} for a in eligible},
                     'method_semantics_not_synthesized': True}]
        return [{'symbol': symbol, 'record_pointers': [], 'claim_kinds': [], 'receiver': None,
                 'mapping_status': 'IDENTITY_ONLY',
                 'mapping_basis': 'NAVIGATION_ONLY_NO_MAPPED_TYPED_CONTRACT',
                 'binding_kind': 'availability_existence' if availability else 'identity_only',
                 'availability_record_pointers': availability,
                 'availability_claim_kinds': [by_pointer[p]['kind'] for p in availability],
                 'pointer_roles': {p: {'role': 'AVAILABILITY_EXISTENCE', 'basis': 'ORIGINAL_NSF_AVAILABILITY_ONLY'} for p in availability},
                 'method_semantics_not_synthesized': True}]
    return []


def _reference_key(ref):
    return tuple(ref.get(key) for key in ('artifact_path', 'sha256', 'pointer'))


def _single_method_locator(binding, symbol):
    """A grouped source label supplies navigation, not a dependency relation."""
    steam = _steam_binding_proof(binding, symbol)
    if steam is not None:
        return _unique_accepted_declaration_leaf(steam, [steam])
    if binding.get('original_reference_precision') != 'SINGLE_SOURCE_LOCATOR_NODE':
        return False
    locator = binding.get('source_locator', {})
    method = normalize_symbol(symbol).rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    names = []
    for field in ('symbol', 'function', 'signature', 'signatures'):
        value = locator.get(field, [])
        names.extend([value] if isinstance(value, str) else value if isinstance(value, list) else [])
    if not names:
        return False
    identified = []
    for name in names:
        if not isinstance(name, str):
            return False
        name = normalize_symbol(name.strip().strip('`'))
        qualified = QUALIFIED.findall(name)
        bare = re.findall(r'(?<![A-Za-z0-9_])(?:[A-Z][A-Za-z0-9_]*[a-z][A-Za-z0-9_]*|Do|Max|Hit|Get|Put|Eat)(?![A-Za-z0-9_])', name)
        declared = qualified or bare or ([name] if re.fullmatch(r'[A-Za-z_]\w*', name) else [])
        if len(set(declared)) != 1:
            return False
        identified.extend(declared)
    return bool(identified) and all(name.rsplit(':', 1)[-1].rsplit('.', 1)[-1] == method
                                    for name in identified)


def _named_subjects(statement):
    if not isinstance(statement, str):
        return []
    names = QUALIFIED.findall(statement) + BARE.findall(statement)
    # Constructor/consumer prose can name a subject without writing call syntax.
    names += re.findall(r'(?:^|[。；;\n])\s*([A-Za-z_][A-Za-z0-9_]*(?:[:.][A-Za-z_][A-Za-z0-9_]*)*)', statement)
    return [name for name in dict.fromkeys(names)
            if _subject_behavior(statement, name, exact=True)]


def _explicit_adjacent_relation(source, adjacent, symbol):
    """Original prose supplies a bounded relation; a shared ref only navigates."""
    if not isinstance(source, str) or not isinstance(adjacent, str):
        return None
    for name in _named_subjects(adjacent):
        if _callsite_context(source, name):
            return {'relation': 'EXPLICIT_ORIGINAL_CALLER_TO_NAMED_CALLEE',
                    'relation_symbols': [name]}
    source_subjects, adjacent_subjects = set(_named_subjects(source)), set(_named_subjects(adjacent))
    consumer_names = lambda text: set(re.findall(r'(?:^|[。；;\n])\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?=拼|读|取|保存|建立|创建|\b(?:reads?|stores?|creates?|builds?)\b)', text, re.I))
    common = (source_subjects | consumer_names(source)) & (adjacent_subjects | consumer_names(adjacent))
    contains_symbol = lambda text: bool(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_])', text))
    if (common and contains_symbol(source) and contains_symbol(adjacent) and
            re.search(r'后续|后面|再次|分支|\b(?:later|subsequent|branch)\b', source, re.I) and
            re.search(r'条件|分支|truthy|false|nil|\b(?:if|when|otherwise|branch)\b', adjacent, re.I)):
        return {'relation': 'EXPLICIT_ORIGINAL_NAMED_CONSUMER_BRANCH',
                'relation_symbols': sorted(common | {symbol})}
    # A backward reference is local only when its immediately preceding atom is
    # the actual basis. Group membership alone cannot identify its antecedent.
    if re.match(r'^\s*(?:上述|前述|以上|该(?:返回|条件|门禁|检查|分支)|这(?:一|两)?步|The (?:above|preceding) (?:condition|branch))', adjacent, re.I):
        return {'relation': 'EXPLICIT_ORIGINAL_LOCAL_BACK_REFERENCE',
                'relation_symbols': [symbol], 'requires_immediate_predecessor': True}
    return None


def context_admission(record, family, contexts, query):
    """Every expansion inherits the original atom's positive and negative scope."""
    atoms = {a['record_pointer']: a for a in _typed_atoms(record, family)}
    allowed, decisions = facet_admission(record, family,
                                        [atoms[c['record_pointer']] for c in contexts], query)
    admitted = {a['record_pointer'] for a in allowed}
    scope_intent = query_scope(query)
    negatives = scope_intent['negative_clauses']
    exclusive = scope_intent['positive_focus']['exclusive']
    result = []
    for context in contexts:
        pointer = context['record_pointer']
        required_basis = context.get('required_basis_record_pointers')
        basis_atoms = [atoms[p] for p in (required_basis if required_basis is not None else
                                        context.get('basis_record_pointers', []))]
        basis_allowed, basis_decisions = facet_admission(record, family, basis_atoms, query)
        basis_excluded = (len(basis_allowed) != len(basis_atoms) if required_basis is not None else
                          bool(basis_atoms) and not basis_allowed)
        if required_basis is not None:
            for basis_atom in basis_atoms:
                own_context = _atom_scope_context(record, basis_atom, atoms.values())
                basis_support = task_support(query, basis_atom['statement'], own_context)
                basis_focus = positive_focus_support(query, basis_atom['statement'], own_context)
                if (basis_support.get('excluded_source_scope') or
                        basis_support.get('whole_atom_excluded_relation_owners') or
                        not basis_focus['allowed'] or exclusive and
                        basis_support.get('whole_atom_delivery_allowed') is False):
                    basis_excluded = True
                    basis_decisions.append({'record_pointer': basis_atom['record_pointer'], 'admitted': False,
                                            'reason': ('CONTEXT_REQUIRED_BASIS_POSITIVE_SCOPE_GAP' if not basis_focus['allowed'] or
                                                       exclusive and basis_support.get('whole_atom_delivery_allowed') is False
                                                       else 'CONTEXT_REQUIRED_BASIS_EXPLICITLY_EXCLUDED'),
                                            'support': basis_support, 'positive_focus_support': basis_focus})
        symbols = context.get('relation_symbols', [])
        excluded = any(re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(name) + r'(?![A-Za-z0-9_])', clause, re.I)
                       for clause in negatives for name in symbols)
        own_context = _atom_scope_context(record, atoms[pointer], atoms.values())
        support = task_support(query, atoms[pointer]['statement'], own_context)
        focus = positive_focus_support(query, atoms[pointer]['statement'], own_context)
        positive_task_gap = exclusive and support.get('whole_atom_delivery_allowed') is False
        excluded = excluded or bool(support.get('excluded_source_scope') or
                                    support.get('whole_atom_excluded_relation_owners')) or not focus['allowed'] or positive_task_gap
        if excluded:
            decisions.append({'record_pointer': pointer, 'admitted': False,
                              'reason': ('CONTEXT_POSITIVE_TASK_ADMISSION_GAP' if positive_task_gap else
                                         'CONTEXT_POSITIVE_OBJECT_SCOPE_GAP' if not focus['allowed']
                                         else 'CONTEXT_EXPLICITLY_EXCLUDED'), 'delivery_scope': 'SOURCE_ADJACENT_CONTEXT',
                              'support': support, 'positive_focus_support': focus})
        if basis_excluded:
            decisions.append({'record_pointer': pointer, 'admitted': False,
                              'reason': 'CONTEXT_BASIS_SCOPE_EXCLUDED',
                              'basis_record_pointers': context.get('basis_record_pointers', []),
                              **({'required_basis_record_pointers': required_basis} if required_basis is not None else {}),
                              'basis_admission': basis_decisions,
                              'delivery_scope': 'SOURCE_ADJACENT_CONTEXT'})
        dt.atom(record['id'],pointer,'CONTEXT_ADMISSION',kind=atoms[pointer]['kind'],
            admitted=pointer in admitted and not excluded and not basis_excluded,
            reason=('CONTEXT_POSITIVE_TASK_ADMISSION_GAP' if positive_task_gap else
                    'CONTEXT_POSITIVE_OBJECT_SCOPE_GAP' if not focus['allowed'] else 'CONTEXT_EXPLICITLY_EXCLUDED')
                   if excluded else 'CONTEXT_BASIS_SCOPE_EXCLUDED' if basis_excluded else
                   'CONTEXT_ADMITTED' if pointer in admitted else 'CONTEXT_FACET_EXCLUDED')
        if pointer in admitted and not excluded and not basis_excluded:
            result.append(copy.deepcopy(context))
    return result, decisions


def _append_bounded_context_relation(proofs, basis_proof, context_proof):
    """Share identical accepted leaf values; preserve participant relations."""
    atom_fields = ('record_sha256', 'record_pointer', 'claim_kind', 'whole_statement_sha256')
    if not proofs:
        proofs.append({'schema': 'original-bounded-source-relations/2',
                       'leaf_pointer_space': 'ACCEPTED_ARTIFACT_PATH_SHA256_JSON_POINTER',
                       'participant_pointer_space': 'CANONICAL_RECORD_SHA256_JSON_POINTER',
                       'index_space': 'ZERO_BASED_ENVELOPE_LOCAL_LIST_INDEX',
                       'source_leaves': [], 'participants': [], 'relations': []})
    envelope = proofs[0]

    def participant(proof, role):
        leaf = {field: value for field, value in proof.items() if field not in atom_fields}
        source_leaves = envelope['source_leaves']
        leaf_index = next((index for index, value in enumerate(source_leaves) if value == leaf), None)
        if leaf_index is None:
            leaf_index = len(source_leaves)
            source_leaves.append(copy.deepcopy(leaf))
        atom = {field: proof[field] for field in atom_fields}
        atom['source_leaf_index'] = leaf_index
        participants = envelope['participants']
        participant_index = next((index for index, value in enumerate(participants)
                                  if all(value.get(field) == item for field, item in atom.items())), None)
        if participant_index is None:
            participant_index = len(participants)
            participants.append({**atom, 'roles': []})
        if role not in participants[participant_index]['roles']:
            participants[participant_index]['roles'].append(role)
        return participant_index

    relation = {'basis_participant_index': participant(basis_proof, 'BASIS'),
                'context_participant_index': participant(context_proof, 'CONTEXT')}
    if relation not in envelope['relations']:
        envelope['relations'].append(relation)


def expand_bounded_context_reference_proofs(proofs):
    """Losslessly render old per-basis proof values; this is not verification."""
    atom_fields = ('record_sha256', 'record_pointer', 'claim_kind', 'whole_statement_sha256')
    result = []
    for envelope in proofs:
        if (envelope.get('schema') != 'original-bounded-source-relations/2' or
                envelope.get('leaf_pointer_space') != 'ACCEPTED_ARTIFACT_PATH_SHA256_JSON_POINTER' or
                envelope.get('participant_pointer_space') != 'CANONICAL_RECORD_SHA256_JSON_POINTER' or
                envelope.get('index_space') != 'ZERO_BASED_ENVELOPE_LOCAL_LIST_INDEX'):
            raise ValueError('Unsupported bounded context presentation schema')

        def source_leaf(index, role):
            if type(index) is not int or not 0 <= index < len(envelope['participants']):
                raise ValueError('Invalid envelope-local participant index')
            atom = envelope['participants'][index]
            leaf_index = atom['source_leaf_index']
            if (role not in atom['roles'] or type(leaf_index) is not int or
                    not 0 <= leaf_index < len(envelope['source_leaves'])):
                raise ValueError('Invalid envelope-local source leaf index or role')
            return {**copy.deepcopy(envelope['source_leaves'][leaf_index]),
                    **{field: atom[field] for field in atom_fields}}

        for relation in envelope['relations']:
            basis = source_leaf(relation['basis_participant_index'], 'BASIS')
            context = source_leaf(relation['context_participant_index'], 'CONTEXT')
            result.append({'basis_record_pointer': basis['record_pointer'],
                           'basis_source_leaf': basis, 'context_source_leaf': context})
    return result


def bounded_source_context(record, family, seed_record_pointers):
    """Return exact source-range context for real seeds, without method proof."""
    if family != 'core':
        return []
    atoms = {atom['record_pointer']: atom for atom in _typed_atoms(record, family)}
    if (not isinstance(seed_record_pointers, (list, tuple, set, frozenset)) or
            any(pointer not in atoms for pointer in seed_record_pointers)):
        raise ValueError('context seeds must be original typed record pointers')
    seeds = set(seed_record_pointers)
    leaves = [item for item in _registered_navigation(record, family)
              if item.get('source_context_proof')]
    fields = ('source_file', 'line_start', 'line_end', 'file_sha256', 'range_sha256',
              'snapshot_id', 'source_commit', 'original_source_scope_ref', 'original_scope_ref', 'original_scope')
    result = {}
    for target in leaves:
        pointer = target['record_pointer']
        if pointer in seeds:
            continue
        atom, proof = atoms[pointer], target['source_context_proof']
        bases = [basis for basis in leaves
                 if basis['record_pointer'] in seeds and
                 all(basis['source_context_proof'].get(field) == proof.get(field) for field in fields) and
                 _sample_scope(record, atoms[basis['record_pointer']]) == _sample_scope(record, atom)]
        if not bases:
            continue
        context = result.setdefault(pointer, {
            **copy.deepcopy(atom), 'record_sha256': _digest(record),
            'role': 'BOUNDED_SOURCE_CONTEXT', 'binding_kind': 'typed_evidence_context',
            'relation': 'SHARED_VERIFIED_EXACT_SOURCE_RANGE_BOUNDED_CONTEXT',
            'reference_precision': 'EXACT_SOURCE_RANGE_CONTEXT_ONLY',
            'basis_record_pointers': [], 'basis_evidence_references': [],
            'source_context_reference_proofs': [],
            'original_scope': copy.deepcopy(record.get('scope', record.get('scope_text', ''))),
            'context_is_method_contract': False, 'callee_semantics_supported': False,
            'full_method_contract_verified': False, 'not_a_universal_method_subject': True,
            'necessary_dependency_verified': False, 'single_operation_verified': False})
        for basis in bases:
            if basis['record_pointer'] not in context['basis_record_pointers']:
                context['basis_record_pointers'].append(basis['record_pointer'])
            ref = {field: basis[field] for field in ('artifact_path', 'sha256', 'pointer')}
            if ref not in context['basis_evidence_references']:
                context['basis_evidence_references'].append(ref)
            _append_bounded_context_relation(context['source_context_reference_proofs'],
                                             basis['source_context_proof'], proof)
    return list(result.values())


def _explicit_comparison_context(record, family, match):
    """Join an explicit comparison to an independent original NSF, context only."""
    from .scope_navigation import ExactSourceReader, ProofError, at, ref_key, triple
    symbol = match.get('symbol', '')
    scope = record.get('scope', {})
    if (family != 'core' or not QUALIFIED.fullmatch(symbol) or
            match.get('record_sha256') != _digest(record) or match.get('original_scope') != scope or
            not isinstance(scope, dict) or source_identity.resolve_identity(record, family, symbol) != symbol):
        return []
    owner = symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0]
    if match.get('receiver') != owner:
        return []
    declarations = _record_identity_bindings(record, family)
    registry = source_identity._registry()
    allowed = [ref for claim in record.get('claims', []) for ref in claim.get('evidence_refs', [])]
    reader = ExactSourceReader(registry.root,
        [{'artifact_path': name, 'sha256': checksum} for name, checksum in registry.manifest.items()], allowed)
    cache = {}

    def original(proof):
        """Only the N004 editorial original fact and its own citation child."""
        key = _digest(proof)
        if key in cache:
            return cache[key]
        cache[key] = None
        try:
            pointer, reference = proof['record_pointer'], proof['reference']
            claim = at(record, pointer)
            own = {ref_key(ref): ref for ref in claim.get('evidence_refs', [])}
            child = re.fullmatch(r'(/facts/(?:0|[1-9][0-9]*)/original)/citations/(0|[1-9][0-9]*)', reference['pointer'])
            if (proof.get('schema') != 'accepted-source-declaration-identity/1' or not child or
                    proof.get('record_sha256') != _digest(record) or claim.get('kind') != 'NSF' or
                    not isinstance(claim.get('statement'), str) or not claim['statement'] or
                    proof.get('claim_kind') != 'NSF' or proof.get('statement_sha256') != _digest(claim['statement']) or
                    ref_key(reference) not in own or reader.root_schema(reference) !=
                    {'schema_version': 'native004-evidence-editorial-map-1.0'}):
                return None
            fact_ref, scope_ref = ({**triple(reference), 'pointer': value}
                                   for value in (child[1], '/source_scope'))
            if ref_key(fact_ref) not in own or ref_key(scope_ref) not in own:
                return None
            leaf, fact, source_scope = reader.read(reference), reader.read(fact_ref), reader.read(scope_ref)
            if (not isinstance(leaf, dict) or not isinstance(fact, dict) or not isinstance(source_scope, dict) or
                    _digest(leaf) != proof.get('artifact_value_sha256') or
                    fact.get('claim_type') != 'NSF' or fact.get('origin_lane') != 'DOT_V04_EXISTING_EVIDENCE' or
                    fact.get('statement') != claim['statement'] or not isinstance(fact.get('citations'), list) or
                    int(child[2]) >= len(fact['citations']) or fact['citations'][int(child[2])] != leaf or
                    source_scope != scope.get('source_scope') or
                    fact.get('snapshot_id') != source_scope.get('dot_snapshot_id') or
                    not isinstance(fact.get('snapshot_id'), str) or not fact['snapshot_id'] or
                    not isinstance(source_scope.get('dot_source_commit'), str) or
                    not re.fullmatch(r'[0-9a-f]{40}', source_scope['dot_source_commit']) or
                    any(leaf.get(a) != proof.get(b) for a, b in (
                        ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                        ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'), ('line_end', 'line_end')))):
                return None
            commit = source_scope['dot_source_commit']
            url = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/' +
                re.escape(commit) + '/' + re.escape(leaf['path']) + '#L' + str(leaf['line_start']) +
                '-L' + str(leaf['line_end']), leaf.get('url', ''))
            if not url:
                return None
            result = {'fact_ref': triple(fact_ref), 'fact_sha256': _digest(fact),
                      'source_scope_ref': triple(scope_ref), 'source_scope_sha256': _digest(source_scope),
                      'snapshot_id': fact['snapshot_id'], 'source_commit': commit, 'source_repository': url[1],
                      'references': [{'reference': triple(ref), 'value_sha256': _digest(node)}
                                     for ref, node in ((fact_ref, fact), (reference, leaf), (scope_ref, source_scope))]}
            cache[key] = result
            return result
        except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError):
            return None

    def exact_owner(proof, name):
        expected = name.rsplit(':', 1)[0] if ':' in name else name.rsplit('.', 1)[0]
        return (proof.get('declared_symbol') == name and proof.get('owner') == expected and
                proof.get('declaration_kind') in ('colon_method', 'qualified_dot_function'))

    def comparison_clauses(statement):
        # 必须先保留整条原文的引号/括号状态，不能分句后把引述误当事实。
        quotes = {'"': '"', "'": "'", '`': '`', '“': '”', '‘': '’', '「': '」', '『': '』'}
        pairs = {'(': ')', '[': ']', '{': '}', '（': '）', '【': '】'}
        visible, quote, escaped, stack, comment = [], None, False, [], False
        for index, char in enumerate(statement):
            if comment:
                visible.append(False)
                if char == '\n':
                    comment = False
            elif quote:
                visible.append(False)
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in quotes:
                visible.append(False)
                quote = quotes[char]
            elif statement.startswith('--', index):
                visible.append(False)
                comment = True
            elif char in pairs:
                visible.append(False)
                stack.append(pairs[char])
            elif char in pairs.values():
                visible.append(False)
                if not stack or stack.pop() != char:
                    return []
            else:
                visible.append(not stack)
        if quote or stack:
            return []
        literal = ''.join(char if visible[index] else ' ' for index, char in enumerate(statement))
        # 显式假设/引述标记的范围无法从标点推断结束；整条比较保持未证明。
        if re.search(r'假设|假定|假如|假想|以下[^。；;\n]*(?:示例|引述|引文)|仅[作为]*(?:示例|演示)|'
                     r'\b(?:hypothes(?:is|es)|hypothetical|assuming|suppose|supposing)\b', literal, re.I):
            return []
        return [item.group() for item in re.finditer(r'[^。；;\n]+', statement)
                if all(visible[index] or statement[index].isspace()
                       for index in range(item.start(), item.end()))]

    physical = ('declared_symbol', 'owner', 'declaration_kind', 'source_file', 'source_raw_sha256',
                'source_lf_sha256', 'cited_file_sha256', 'line_start', 'line_end', 'cited_range_sha256',
                'range_hash_mode', 'declaration_line', 'declaration_header', 'declaration_header_sha256',
                'artifact_value_sha256')
    result = {}
    for pointer in match.get('record_pointers', []):
        role = match.get('pointer_roles', {}).get(pointer, {})
        claim = at(record, pointer)
        if (claim.get('kind') != 'NSF' or role.get('role') != 'METHOD_SUBJECT' or
                role.get('claim_kind') != 'NSF' or role.get('callee_semantics_supported') is not True):
            continue
        seed_proofs = [proof for proof in declarations if proof.get('record_pointer') == pointer and
                       exact_owner(proof, symbol) and original(proof) is not None]
        if not seed_proofs:
            continue
        # 有限原文语法；可能、是否、引述与无明确比较方向的文本不补事实。
        pattern = (r'\s*(?:它|该方法|该函数|该组件|' + re.escape(symbol) + r')\s*(?:和|与)\s*'
                   r'(?:普通\s*)?(' + QUALIFIED.pattern + r')\s*'
                   r'(?:的(?:暂停处理|处理|行为|语义|分支))?(?:并)?(?:不相同|不同|有区别)\s*')
        for clause in comparison_clauses(claim['statement']):
            comparison = re.fullmatch(pattern, clause)
            if not comparison:
                continue
            target_symbol = comparison[1]
            if target_symbol == symbol or source_identity.resolve_identity(record, family, target_symbol) != target_symbol:
                continue
            anchors = [proof for proof in declarations if proof.get('record_pointer') == pointer and
                       exact_owner(proof, target_symbol) and original(proof) is not None]
            targets = [proof for proof in declarations if proof.get('record_pointer') != pointer and
                       exact_owner(proof, target_symbol) and original(proof) is not None and
                       _subject_behavior(at(record, proof['record_pointer'])['statement'], target_symbol, exact=True)]
            for anchor in anchors:
                basis = original(anchor)
                seeds = [proof for proof in seed_proofs if original(proof)['fact_ref'] == basis['fact_ref'] and
                         original(proof)['fact_sha256'] == basis['fact_sha256']]
                if not seeds:
                    continue
                for target in targets:
                    context_source = original(target)
                    if (any(anchor.get(field) != target.get(field) for field in physical) or
                            any(anchor['reference'][field] != target['reference'][field]
                                for field in ('artifact_path', 'sha256')) or
                            any(basis[field] != context_source[field] for field in
                                ('snapshot_id', 'source_commit', 'source_repository', 'source_scope_sha256'))):
                        continue
                    target_pointer = target['record_pointer']
                    seed = seeds[0]
                    references = []
                    for source in (original(seed), basis, context_source):
                        for ref in source['references']:
                            if ref not in references:
                                references.append(copy.deepcopy(ref))
                    proof = {'schema': 'original-explicit-qualified-comparison/1',
                        'basis_record_pointer': pointer, 'context_record_pointer': target_pointer,
                        'query_identity': symbol, 'query_owner': owner,
                        'comparison_target_identity': target_symbol, 'comparison_target_owner': target['owner'],
                        'original_comparison_clause': clause, 'comparison_polarity': 'DIFFERENT',
                        'basis_whole_statement_sha256': _digest(claim['statement']),
                        'context_whole_statement_sha256': _digest(at(record, target_pointer)['statement']),
                        'accepted_root': str(registry.root),
                        'accepted_declaration_sha256': {'basis_subject': _digest(seed),
                            'basis_comparison_anchor': _digest(anchor), 'context_subject': _digest(target)},
                        'same_physical_comparison_declaration': {field: copy.deepcopy(anchor[field]) for field in physical},
                        **{field: copy.deepcopy(basis[field]) for field in
                            ('snapshot_id', 'source_commit', 'source_repository', 'source_scope_ref', 'source_scope_sha256')},
                        'references': references}
                    context = result.setdefault(target_pointer, {'record_pointer': target_pointer, 'kind': 'NSF',
                        'record_sha256': _digest(record), 'role': 'TYPED_EVIDENCE_CONTEXT',
                        'binding_kind': 'typed_evidence_context', 'relation': 'EXPLICIT_QUALIFIED_ORIGINAL_COMPARISON',
                        'relation_symbols': [symbol, target_symbol], 'basis_record_pointers': [],
                        'required_basis_record_pointers': [], 'comparison_reference_proofs': [],
                        'original_scope': copy.deepcopy(scope), 'context_is_method_contract': False,
                        'callee_semantics_supported': False, 'full_method_contract_verified': False,
                        'not_a_universal_method_subject': True})
                    for field in ('basis_record_pointers', 'required_basis_record_pointers'):
                        if pointer not in context[field]:
                            context[field].append(pointer)
                    if proof not in context['comparison_reference_proofs']:
                        context['comparison_reference_proofs'].append(proof)
    return list(result.values())


def _dependency_context(record, family, match):
    """Shared exact cited source nodes are context, never new method subjects."""
    if family != 'core' or not match.get('record_pointers'):
        return []
    source_bindings = match.get('source_bindings', {})
    anchors, broad = {}, {}
    for pointer in match['record_pointers']:
        for binding in source_bindings.get(pointer, []):
            key = _reference_key(binding)
            if all(key) and binding.get('source_file') and binding.get('source_locator'):
                target = anchors if _single_method_locator(binding, match['symbol']) else broad
                target.setdefault(key, []).append(pointer)
    result = []
    for index, claim in enumerate(record.get('claims', [])):
        pointer = f'/claims/{index}'
        if claim.get('kind') not in ('NSF', 'EI', 'REC', 'UNK', 'PROJECT_POLICY'):
            continue
        # 同操作原 atom 即使已是主体候选，也仍可成为已选 seed 的必要上下文。
        shared = [ref for ref in claim.get('evidence_refs', [])
                  if any(basis != pointer for basis in anchors.get(_reference_key(ref), []))]
        navigation = [ref for ref in claim.get('evidence_refs', []) if _reference_key(ref) in broad]
        if navigation and not shared:
            relations = []
            for ref in navigation:
                for basis in broad[_reference_key(ref)]:
                    if basis == pointer:
                        continue
                    relation = _explicit_adjacent_relation(
                        record['claims'][int(basis.rsplit('/', 1)[1])]['statement'], claim.get('statement'), match['symbol'])
                    if relation and (not relation.pop('requires_immediate_predecessor', False) or
                                     int(basis.rsplit('/', 1)[1]) == index - 1):
                        relations.append((basis, ref, relation))
            if relations:
                result.append({'record_pointer': pointer, 'kind': claim['kind'],
                               'role': 'SOURCE_ADJACENT_CONTEXT',
                               'relation': 'EXPLICIT_ORIGINAL_STATEMENT_RELATION_WITH_SHARED_SOURCE',
                               'statement_relations': [relation for _, _, relation in relations],
                               'relation_symbols': sorted({name for _, _, relation in relations for name in relation['relation_symbols']}),
                               'reference_precision': 'GROUPED_NAVIGATION_PLUS_EXPLICIT_ORIGINAL_RELATION',
                               'basis_record_pointers': list(dict.fromkeys(basis for basis, _, _ in relations)),
                               'basis_evidence_references': [{key: ref[key] for key in ('artifact_path', 'sha256', 'pointer')}
                                                            for _, ref, _ in relations],
                               'original_scope': copy.deepcopy(record.get('scope', record.get('scope_text', ''))),
                               'context_is_method_contract': False,
                               'not_a_universal_method_subject': True})
            match.setdefault('source_adjacency_navigation', []).append({
                'record_pointer': pointer, 'kind': claim['kind'],
                'relation': 'SHARED_GROUPED_SOURCE_CITATION_NAVIGATION_ONLY',
                'dependency_verified': False,
                'basis_evidence_references': [{key: ref[key] for key in ('artifact_path', 'sha256', 'pointer')}
                                             for ref in navigation]})
        if shared:
            result.append({'record_pointer': pointer, 'kind': claim['kind'],
                           'role': 'ORIGINAL_SOURCE_ADJACENT_CONTEXT',
                           'relation': 'SHARED_EXACT_ORIGINAL_SOURCE_CITATION',
                           'reference_precision': 'SINGLE_SOURCE_LOCATOR_NODE_AND_EXACT_NAMED_METHOD',
                           'basis_record_pointers': list(dict.fromkeys(p for ref in shared
                                                                      for p in anchors[_reference_key(ref)] if p != pointer)),
                           'basis_evidence_references': [{key: ref[key] for key in
                                                          ('artifact_path', 'sha256', 'pointer')}
                                                         for ref in shared],
                           'context_is_method_contract': False, 'callee_semantics_supported': False,
                           'full_method_contract_verified': False,
                           'not_a_universal_method_subject': True})
    # 指代只沿同一原引用的立即前驱收束；后继 context 不能代替前驱。
    claims = record.get('claims', [])
    scope = record.get('scope', record.get('scope_text', ''))
    edges, by_pointer = [], {context['record_pointer']: context for context in result}
    pending = []
    if match.get('original_scope', scope) == scope:
        for pointer in match['record_pointers']:
            owned = {_reference_key(ref) for ref in claims[int(pointer.rsplit('/', 1)[1])].get('evidence_refs', [])}
            refs = {_reference_key(binding) for binding in source_bindings.get(pointer, [])
                    if all(_reference_key(binding)) and _reference_key(binding) in owned and
                    binding.get('source_file') and binding.get('source_locator')}
            if refs:
                pending.append((pointer, (pointer,), (), refs))
        for context in result:
            if context.get('relation') != 'EXPLICIT_ORIGINAL_STATEMENT_RELATION_WITH_SHARED_SOURCE':
                continue
            refs = {_reference_key(ref) for ref in context.get('basis_evidence_references', [])}
            pending.append((context['record_pointer'], tuple(context['basis_record_pointers']), (), refs))
    visited = set()
    while pending:
        dependent, roots, path, inherited_refs = pending.pop(0)
        key = dependent, roots, path, tuple(sorted(inherited_refs))
        if key in visited:
            continue
        visited.add(key)
        index = int(dependent.rsplit('/', 1)[1])
        statement = claims[index].get('statement')
        if (not isinstance(statement, str) or index == 0 or not re.match(
                r'^\s*(?:上述|前述|以上|该(?:返回|条件|门禁|检查|分支)|这(?:一|两)?步|The (?:above|preceding) (?:condition|branch))', statement, re.I)):
            continue
        predecessor = f'/claims/{index - 1}'
        claim = claims[index - 1]
        if claim.get('kind') not in ('NSF', 'EI', 'REC', 'UNK', 'PROJECT_POLICY'):
            continue
        original_refs = {_reference_key(ref) for ref in claims[index].get('evidence_refs', [])}
        shared_refs = [ref for ref in claim.get('evidence_refs', [])
                       if all(_reference_key(ref)) and _reference_key(ref) in original_refs & inherited_refs]
        relation = _explicit_adjacent_relation('', statement, match['symbol'])
        if not shared_refs or not relation or not relation.get('requires_immediate_predecessor'):
            continue
        edge = {'dependent_record_pointer': dependent, 'required_record_pointer': predecessor,
                'relation': relation['relation'], 'relation_direction': 'DEPENDENT_TO_IMMEDIATE_ANTECEDENT'}
        if edge not in edges:
            edges.append(edge)
        required_basis = list(dict.fromkeys((*roots, *path, dependent)))
        if predecessor not in roots and predecessor not in path:
            context = by_pointer.get(predecessor)
            if context is None:
                context = {'record_pointer': predecessor, 'kind': claim['kind'],
                           'role': 'SOURCE_ADJACENT_CONTEXT',
                           'relation': 'EXPLICIT_ORIGINAL_LOCAL_BACK_REFERENCE',
                           'relation_direction': 'DEPENDENT_TO_IMMEDIATE_ANTECEDENT',
                           'relation_symbols': [match['symbol']],
                           'reference_precision': 'SHARED_ORIGINAL_REFERENCE_PLUS_IMMEDIATE_ANTECEDENT',
                           'basis_record_pointers': [], 'required_basis_record_pointers': [],
                           'basis_evidence_references': [], 'dependency_edges': [],
                           'original_scope': copy.deepcopy(scope), 'context_is_method_contract': False,
                           'not_a_universal_method_subject': True}
                result.append(context)
                by_pointer[predecessor] = context
            context['basis_record_pointers'] = list(dict.fromkeys(context['basis_record_pointers'] + list(roots)))
            context['required_basis_record_pointers'] = list(dict.fromkeys(
                context.get('required_basis_record_pointers', []) + required_basis))
            context.setdefault('dependency_edges', [])
            if edge not in context['dependency_edges']:
                context['dependency_edges'].append(edge)
            for ref in shared_refs:
                original_ref = {field: ref[field] for field in ('artifact_path', 'sha256', 'pointer')}
                if original_ref not in context['basis_evidence_references']:
                    context['basis_evidence_references'].append(original_ref)
        pending.append((predecessor, roots, tuple(required_basis), {_reference_key(ref) for ref in shared_refs}))
    match['context_dependency_edges'] = edges
    existing = {context['record_pointer'] for context in result}
    result.extend(context for context in _explicit_comparison_context(record, family, match)
                  if context['record_pointer'] not in existing)
    return result


def _constructor_source_range(registry, node):
    """Read an already frozen citation range; never read installed Lua Source."""
    checksum = node.get('range_sha256')
    if not isinstance(checksum, str) or not re.fullmatch(r'[0-9a-f]{64}', checksum):
        return None
    text = registry.ranges.get(checksum)
    if text is None and checksum in registry.raw_ranges:
        text = base64.b64decode(registry.raw_ranges[checksum], validate=True).decode('utf-8')
    start, end = node.get('line_start'), node.get('line_end')
    if (not isinstance(text, str) or sha256(text.encode()).hexdigest() != checksum or
            type(start) is not int or type(end) is not int or not 0 < start <= end or
            len(text.splitlines()) != end - start + 1):
        return None
    return text


def _returned_constructor_signature(record, family, pointer, symbol):
    """Preserve an original narrow signature, independently of caller prose."""
    if family != 'core' or not re.fullmatch(r'[A-Za-z_]\w*', symbol, re.ASCII):
        return None
    if not re.fullmatch(r'/claims/(0|[1-9][0-9]*)', pointer):
        return None
    try:
        claim = record['claims'][int(pointer.rsplit('/', 1)[1])]
        statement, scope = claim['statement'], record['scope']
        if (claim.get('kind') != 'NSF' or not isinstance(statement, str) or
                not re.search(r'构造器签名|\bconstructor\s+signature\b', statement, re.I) or
                not isinstance(scope, dict)):
            return None
        registry = source_identity._registry()
        refs = claim.get('evidence_refs', [])
        accepted = []
        for fact_ref in refs:
            if not re.fullmatch(r'/direct_facts/(0|[1-9][0-9]*)', fact_ref.get('pointer', '')):
                continue
            fact = registry._node(fact_ref)
            document = registry._documents[fact_ref['artifact_path']]
            if (document.get('schema_version') != 'native-campaign-research/1' or
                    not isinstance(fact, dict) or fact.get('claim_kind') != 'DirectSourceFact' or
                    fact.get('statement_zh') != statement or fact.get('runtime_tested') is not False or
                    fact.get('canonical') is not False or not isinstance(fact.get('citation_ids'), list) or
                    not isinstance(document.get('scope'), dict) or
                    scope.get('original_source_scope') != document['scope']):
                continue
            metadata = {}
            for name, scope_name in (('baseline_snapshot_id', 'snapshot_id'),
                                     ('source_commit', 'source_commit'), ('source_repository', 'source_repository')):
                reference = {**fact_ref, 'pointer': '/' + name}
                if reference not in refs:
                    break
                metadata[scope_name] = registry._node(reference)
                if metadata[scope_name] != scope.get(scope_name):
                    break
            else:
                if (not isinstance(metadata['source_commit'], str) or
                        not re.fullmatch(r'[0-9a-f]{40}', metadata['source_commit']) or
                        not isinstance(metadata['snapshot_id'], str) or not metadata['snapshot_id'] or
                        not isinstance(metadata['source_repository'], str) or not metadata['source_repository']):
                    continue
                signatures = []
                for value in fact.get('signatures', []):
                    if not isinstance(value, str):
                        continue
                    parsed = re.fullmatch(re.escape(symbol) + r'\(\s*([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)?\s*\)', value, re.ASCII)
                    if parsed:
                        signatures.append([name.strip() for name in parsed[1].split(',')] if parsed[1] else [])
                if len(signatures) != 1:
                    continue
                arguments = signatures[0]
                leaves = []
                for reference in refs:
                    if (any(reference.get(key) != fact_ref.get(key) for key in ('artifact_path', 'sha256')) or
                            not re.fullmatch(r'/citations/(0|[1-9][0-9]*)', reference.get('pointer', ''))):
                        continue
                    node = registry._node(reference)
                    if (not isinstance(node, dict) or node.get('id') not in fact['citation_ids'] or
                            node.get('commit') != metadata['source_commit'] or
                            node.get('repository') != metadata['source_repository'] or
                            node.get('snapshot_id') != metadata['snapshot_id'] or
                            node.get('snapshot_identity_verified') is not True or
                            not isinstance(node.get('path'), str) or not node['path'].startswith('scripts/') or
                            not isinstance(node.get('file_sha256'), str) or
                            not re.fullmatch(r'[0-9a-f]{64}', node['file_sha256'])):
                        continue
                    text = _constructor_source_range(registry, node)
                    if text is not None:
                        leaves.append((reference, node, text))
                for alias_ref, alias_node, alias_text in leaves:
                    aliases = []
                    pattern = (r'^\s*local\s+' + re.escape(symbol) + r'\s*=\s*require\s*'
                               r'(?:\(\s*[\"\']([A-Za-z0-9_/]+)[\"\']\s*\)|[\"\']([A-Za-z0-9_/]+)[\"\'])\s*;?\s*$')
                    for line in alias_text.splitlines():
                        match = re.fullmatch(pattern, line, re.ASCII)
                        if match:
                            aliases.append(match[1] or match[2])
                    if len(aliases) != 1:
                        continue
                    module = aliases[0]
                    target_file = 'scripts/' + module + '.lua'
                    for export_ref, export_node, export_text in leaves:
                        exported = re.fullmatch(r'\s*return\s+([A-Za-z_]\w*)\s*;?\s*', export_text, re.ASCII)
                        if not exported or export_node['path'] != target_file:
                            continue
                        class_name = exported[1]
                        formal = ['self'] + arguments
                        formal_pattern = r'\(\s*' + r'\s*,\s*'.join(map(re.escape, formal)) + r'\s*\)'
                        prose = (r'(?:return|返回)\s+' + re.escape(class_name) + r'\s*[；;]\s*后者Class构造器签名为\s*' + formal_pattern)
                        named_prose = re.escape(class_name) + r'(?:\s*Class)?\s*(?:的)?构造器签名(?:为|是)\s*' + formal_pattern
                        if not (re.search(prose, statement) or re.search(named_prose, statement)):
                            continue
                        for header_ref, header_node, header_text in leaves:
                            if (header_node['path'] != target_file or
                                    header_node['file_sha256'] != export_node['file_sha256']):
                                continue
                            head = re.fullmatch(r'\s*(?:local\s+)?' + re.escape(class_name) +
                                r'\s*=\s*Class\(\s*(?:[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*\s*,\s*)?function\s*' + formal_pattern + r'\s*', header_text, re.ASCII)
                            if not head:
                                continue
                            witnesses = [(alias_ref, alias_node), (export_ref, export_node), (header_ref, header_node)]
                            accepted.append({'schema': 'original-returned-constructor-signature/1',
                                'record_pointer': pointer, 'record_sha256': _digest(record),
                                'whole_statement_sha256': _digest(statement),
                                'whole_fact_reference': copy.deepcopy(fact_ref), 'whole_fact_sha256': _digest(fact),
                                'signature': symbol + '(' + ','.join(arguments) + ')', 'symbol': symbol,
                                'module': module, 'returned_class': class_name, **metadata,
                                'original_scope_sha256': _digest(scope),
                                'source_references': [{'reference': copy.deepcopy(reference), 'value_sha256': _digest(node),
                                    'source_file': node['path'], 'file_sha256': node['file_sha256'],
                                    'range_sha256': node['range_sha256']} for reference, node in witnesses],
                                'same_original_fact_and_refs': True, 'callee_signature_supported': True,
                                'constructor_body_semantics_supported': False, 'full_method_contract_verified': False,
                                'full_source_lexical_identity_reproved': False,
                                'proof_scope': 'ORIGINAL_EXPLICIT_SIGNATURE_ONLY_WITH_FROZEN_ALIAS_EXPORT_HEADER_CORROBORATION'})
        unique = {_digest(proof): proof for proof in accepted}
        return next(iter(unique.values())) if len(unique) == 1 else None
    except (KeyError, IndexError, TypeError, ValueError, OSError, UnicodeError):
        return None


def _uncached_contract_matches(record, family, symbol):
    """Bind every returned mapping to the original record and typed context."""
    matches = _contract_matches(record, family, symbol)
    record_digest = _digest(record)
    atoms = {atom['record_pointer']: atom for atom in _typed_atoms(record, family)}
    for match in matches:
        role_symbol = match.get('original_contract_symbol', match['symbol'])
        navigation = [item for item in _registered_navigation(record, family) if item['symbol'] == match['symbol']]
        # 静态 map 只给原候选；补充主体仍须原 NSF、当前主体语义和同记录原引用证明。
        for item in navigation:
            pointer = item['record_pointer']
            atom = atoms[pointer]
            if (item.get('context_only') or atom['kind'] != 'NSF' or
                    not (item.get('named_typed_context') or item.get('typed_context_proof')) or
                    pointer in match.get('record_pointers', [])):
                continue
            binding = statement_binding(atom['statement'], match['symbol'])
            if not binding or binding.get('role') != 'METHOD_SUBJECT':
                continue
            match['record_pointers'].append(pointer)
            if pointer in match.get('availability_record_pointers', []):
                match['availability_record_pointers'].remove(pointer)
            match.setdefault('pointer_roles', {})[pointer] = {**binding,
                'basis': 'CURRENT_EXACT_QUALIFIED_ORIGINAL_NSF_WITH_VERIFIED_OWN_REFERENCE'}
            proof = item.get('typed_context_proof')
            source_binding = {field: item[field] for field in ('artifact_path', 'sha256', 'pointer')}
            source_binding.update({'symbol': match['symbol'], 'record_pointer': pointer,
                                   'source_file': item.get('source_file'),
                                   'original_reference_precision': 'CANONICAL_NAMED_TYPED_ATOM_ONLY'})
            if proof:
                source_binding.update({'source_locator': {'path': proof['source_file'], 'symbol': proof['symbol'],
                    **{field: proof[field] for field in ('line_start', 'line_end', 'file_sha256', 'range_sha256')}},
                    'original_reference_precision': 'SINGLE_SOURCE_LOCATOR_NODE',
                    'typed_context_proof': copy.deepcopy(proof)})
            match.setdefault('source_bindings', {}).setdefault(pointer, []).append(source_binding)
            match.setdefault('claim_reference_bindings', {})[pointer] = copy.deepcopy(
                record['claims'][int(pointer.rsplit('/', 1)[1])].get('evidence_refs', [])
                if family == 'core' else record.get('native_fact', {}).get('evidence_refs', []))
            match['mapping_basis'] = 'FROZEN_CANDIDATES_PLUS_VERIFIED_ORIGINAL_TYPED_POINTERS'
        # Repair availability grammar against original text, including English
        # sentence boundaries; a preceding absence never negates a new subject.
        availability = list(match.get('availability_record_pointers', []))
        pointers = list(match.get('record_pointers', []))
        for pointer in availability[:]:
            atom = atoms[pointer]
            bindings = match.get('source_bindings', {}).get(pointer, [])
            role = statement_binding_role(atom['statement'], role_symbol,
                                          allow_bare=bool(bindings), source_callable=bool(bindings))
            if role in ('METHOD_SUBJECT', 'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED') and atom['kind'] == 'NSF':
                availability.remove(pointer)
                pointers.append(pointer)
                match.setdefault('pointer_roles', {})[pointer] = {
                    'role': 'SOURCE_OBSERVATION_SUBJECT' if role == 'METHOD_SUBJECT' and _sample_scope(record, atom) else role,
                    'basis': 'ORIGINAL_TYPED_STATEMENT_WITH_SENTENCE_BOUNDED_SUBJECT'}
        match['record_pointers'] = list(dict.fromkeys(pointers))
        match['claim_kinds'] = [atoms[p]['kind'] for p in match['record_pointers']]
        match['availability_record_pointers'] = availability
        match['availability_claim_kinds'] = [atoms[p]['kind'] for p in availability]
        # 原 map 只保存定位；调用角色每次按原 statement 复核，避免旧肯定
        # callsite 标签把“没有调用”变成参数、返回或完整 callee 合同。
        for pointer in match['record_pointers'] + availability:
            atom = atoms[pointer]
            original_role = match.get('pointer_roles', {}).get(pointer, {})
            original_role = original_role if isinstance(original_role, dict) else {'role': original_role}
            source_bindings = match.get('source_bindings', {}).get(pointer, [])
            binding = statement_binding(atom['statement'], role_symbol,
                                        allow_bare=bool(source_bindings), source_callable=bool(source_bindings))
            if (atom['kind'] == 'NSF' and binding and binding.get('role') in
                    ('BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL',
                     'BOUNDED_CALLEE_RELATION_UNDETERMINED')
                    and _subject_behavior(atom['statement'], role_symbol)
                    and _source_bound_independent_subject(record, family, pointer, role_symbol, atom['statement'])):
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True}
            local_subject = (_declared_local_subject(record, family, pointer, role_symbol)
                             if original_role.get('local_subject_relation') else None)
            if local_subject is None and original_role.get('local_subject_relation'):
                local_subject = _declared_property_subject(record, family, pointer, role_symbol)
            if local_subject:
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True,
                           'local_subject_relation': local_subject}
            # 同名 bare callsite 属于另一 receiver 时，不能覆盖已接受的
            # method subject；保留仍须同 owner Source 声明与原句行为复核。
            if (atom['kind'] == 'NSF' and original_role.get('role') in ('METHOD_SUBJECT', 'SOURCE_OBSERVATION_SUBJECT')
                    and _mapped_owner_subject(atom['statement'], role_symbol, source_bindings)):
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True}
            if atom['kind'] != 'NSF':
                binding = {'role': 'TYPED_EVIDENCE_CONTEXT', 'relation_polarity': 'UNDETERMINED',
                           'binding_kind': 'typed_evidence_context',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': False}
            elif binding is None and original_role.get('role') in ('METHOD_SUBJECT', 'SOURCE_OBSERVATION_SUBJECT') and source_bindings and _source_declared_subject(
                    atom['statement'], role_symbol,
                    [n['symbol'] for n in _registered_navigation(record, family)
                     if n['record_pointer'] == pointer and not n.get('context_only')]):
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True}
            elif binding is None:
                reference_only = _subject_reference_only(atom['statement'], role_symbol,
                                                         allow_bare=bool(source_bindings))
                binding = {'role': 'BOUNDED_CALLEE_RELATION_UNDETERMINED', 'relation_polarity': 'UNDETERMINED',
                           'binding_kind': ('typed_evidence_context' if reference_only else
                                            'bounded_caller_relation_unresolved'),
                           'reference_context_only': reference_only,
                           'positive_callsite_evidence': False, 'callee_semantics_supported': False}
            original_subject = (_declared_original_subject(record, family, pointer, role_symbol)
                                if pointer in match['record_pointers'] else None)
            if original_subject:
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True,
                           'original_subject_relation': original_subject}
            constructor = (_returned_constructor_signature(record, family, pointer, role_symbol)
                           if binding.get('callee_semantics_supported') is not True else None)
            if constructor:
                binding = {'role': 'METHOD_SUBJECT', 'relation_polarity': 'UNDETERMINED',
                           'positive_callsite_evidence': False, 'callee_semantics_supported': True,
                           'support_kind': 'ORIGINAL_CONSTRUCTOR_SIGNATURE_ONLY',
                           'constructor_body_semantics_supported': False,
                           'constructor_signature_relation': constructor}
            if binding['role'] == 'METHOD_SUBJECT' and _sample_scope(record, atom):
                binding['role'] = 'SOURCE_OBSERVATION_SUBJECT'
                binding['callee_semantics_supported'] = False
            match.setdefault('pointer_roles', {})[pointer] = {**original_role, **binding,
                'basis': 'RECLASSIFIED_LOCAL_RELATION_IN_ORIGINAL_TYPED_STATEMENT', 'claim_kind': atom['kind']}
        if pointers:
            # mapping_status 保留 typed-pointer 选择；行为标签只按复核后的角色汇总。
            match['mapping_status'] = 'TYPED_CONTRACT'
            match['binding_kind'] = 'typed_behavioral_contract'
            direct_roles = [match['pointer_roles'][pointer] for pointer in match['record_pointers']]
            callee_roles = ('BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL',
                            'BOUNDED_CALLEE_RELATION_UNDETERMINED')
            if direct_roles and all(role.get('role') in callee_roles for role in direct_roles):
                kinds = {role.get('binding_kind', 'bounded_caller_relation_unresolved') for role in direct_roles}
                match['binding_kind'] = (next(iter(kinds)) if len(kinds) == 1 else
                                         'bounded_caller_relation_unresolved')
            reference_pointers = [pointer for pointer in match['record_pointers']
                                  if match['pointer_roles'][pointer].get('reference_context_only') is True]
            if reference_pointers:
                match['reference_context_record_pointers'] = reference_pointers
                match['reference_context_only'] = len(reference_pointers) == len(match['record_pointers'])
        match['record_sha256'] = record_digest
        match.setdefault('original_scope', copy.deepcopy(record.get('scope', record.get('scope_text', ''))))
        match.setdefault('original_governance', {key: record[key] for key in
                                                ('knowledge_status', 'retrieval_status', 'coding_status') if key in record})
        contexts = _dependency_context(record, family, match)
        context_by_pointer = {context['record_pointer']: context for context in contexts}
        for item in navigation:
            pointer = item['record_pointer']
            atom = atoms[pointer]
            proof = item.get('typed_context_proof')
            named = item.get('named_typed_context') is True
            if (pointer in match['record_pointers'] + match.get('availability_record_pointers', [])
                    and not proof):
                continue
            roots = []
            basis_refs = []
            if proof:
                fields = ('symbol', 'source_file', 'line_start', 'line_end', 'file_sha256',
                          'range_sha256', 'snapshot_id', 'original_scope_ref', 'original_scope')
                for basis in navigation:
                    basis_pointer = basis['record_pointer']
                    basis_proof = basis.get('typed_context_proof')
                    if (basis_pointer != pointer and basis_proof and
                        all(basis_proof.get(field) == proof.get(field) for field in fields) and
                        _sample_scope(record, atoms[basis_pointer]) == _sample_scope(record, atom)):
                        roots.append(basis_pointer)
                        basis_refs.append({field: basis[field] for field in ('artifact_path', 'sha256', 'pointer')})
            if not named and not roots:
                continue
            if pointer in match['record_pointers'] + match.get('availability_record_pointers', []) and not roots:
                continue
            context = context_by_pointer.get(pointer)
            if context is None:
                context = {'record_pointer': pointer, 'kind': atom['kind'], 'role': 'TYPED_EVIDENCE_CONTEXT',
                    'binding_kind': 'typed_evidence_context', 'relation_symbols': [match['symbol']],
                    'basis_record_pointers': [], 'required_basis_record_pointers': [],
                    'basis_evidence_references': [], 'original_scope': copy.deepcopy(
                        record.get('scope', record.get('scope_text', ''))),
                    'context_is_method_contract': False, 'callee_semantics_supported': False,
                    'full_method_contract_verified': False, 'not_a_universal_method_subject': True}
                contexts.append(context)
                context_by_pointer[pointer] = context
            context.setdefault('typed_context_relations', [])
            relation = 'EXPLICIT_ORIGINAL_QUALIFIED_TYPED_ATOM' if named else 'SAME_VERIFIED_SINGLE_METHOD_SOURCE_LEAF'
            if relation not in context['typed_context_relations']:
                context['typed_context_relations'].append(relation)
            context.setdefault('relation', relation)
            context['basis_record_pointers'] = list(dict.fromkeys(context['basis_record_pointers'] + roots))
            context['required_basis_record_pointers'] = list(dict.fromkeys(
                context.get('required_basis_record_pointers', context['basis_record_pointers']) + roots))
            own_ref = {field: item[field] for field in ('artifact_path', 'sha256', 'pointer')}
            for ref in basis_refs or [own_ref]:
                if ref not in context['basis_evidence_references']:
                    context['basis_evidence_references'].append(ref)
            context.setdefault('typed_context_reference_proofs', [])
            reference_proof = {'record_sha256': record_digest, 'record_pointer': pointer,
                               'claim_kind': atom['kind'], 'symbol': match['symbol'], **own_ref}
            if named:
                reference_proof.update({'schema': 'original-qualified-typed-atom-reference/1',
                    'original_reference_integrity_verified': True,
                    'identity_is_native_declaration_proof': False})
            if proof:
                reference_proof['single_method_leaf'] = {field: copy.deepcopy(value)
                    for field, value in proof.items() if field != 'original_scope'}
            if reference_proof not in context['typed_context_reference_proofs']:
                context['typed_context_reference_proofs'].append(reference_proof)
            original_binding = statement_binding(atom['statement'], role_symbol)
            if original_binding and original_binding.get('role') != 'METHOD_SUBJECT':
                context.setdefault('original_relation_binding', original_binding)
        if contexts and not match['record_pointers']:
            match['mapping_status'] = 'BOUNDED_CONTEXT'
            match['binding_kind'] = 'typed_evidence_context'
            match['reference_context_only'] = True
            match['mapping_basis'] = 'VERIFIED_ORIGINAL_TYPED_CONTEXT_WITHOUT_NATIVE_METHOD_SUBJECT'
        match['context_record_pointers'] = [context['record_pointer'] for context in contexts]
        match['context_claim_kinds'] = [context['kind'] for context in contexts]
        match['context_pointer_bindings'] = contexts
        match['context_is_method_contract'] = False
        match['context_closure_gaps'] = [pointer for pointer in
                                       dict.fromkeys(match['record_pointers'] + match['context_record_pointers'])
                                       if isinstance(atoms[pointer]['statement'], str) and
                                       re.match(r'^\s*(?:上述|前述|以上|该(?:返回|条件|门禁|检查|分支)|这(?:一|两)?步|The (?:above|preceding) (?:condition|branch))',
                                                atoms[pointer]['statement'], re.I) and
                                       not any(edge['dependent_record_pointer'] == pointer and
                                               edge['required_record_pointer'] ==
                                               f'/claims/{int(pointer.rsplit("/", 1)[1]) - 1}'
                                               for edge in match.get('context_dependency_edges', []))]
    return matches


def contract_matches(record, family, symbol):
    """Cache only query-independent mappings by complete current input content."""
    with record_contract_context(record, family):
        return _cached_contract_matches(record, family, symbol)


def _cached_contract_matches(record, family, symbol):
    symbol = normalize_symbol(symbol)
    navigation = _registered_navigation(record, family)
    catalog = _catalog()
    mapped = {'record_map': catalog['records'].get(record['id'], {}),
              'sample_rules': catalog.get('sample_rules', [])}
    def compute():
        current = _RECORD_DERIVATION.get()
        key = (_navigation_key(record, family), source_identity.selected_source_file())
        if current is None or current['key'] != key:
            return _uncached_contract_matches(record, family, symbol)
        # Contract helpers never mutate their record input. An unexposed copy
        # permits repeated pure derivations to share its already verified hash;
        # the caller's current full content still participates in every cache key.
        if 'record_snapshot' not in current:
            current['record_snapshot'] = copy.deepcopy(record)
        return _uncached_contract_matches(current['record_snapshot'], family, symbol)
    return _CONTRACT_CACHE.get_or_compute(record, family, symbol, {'epoch':epoch_key(),
                                         'source_file': source_identity.selected_source_file(), 'map':mapped}, navigation,
                                         compute)


def query_scope(query):
    """Use the same positive/excluded clauses as ranking and role routing."""
    return _shared_query_scope(query)


def _identity_match(text, aliases):
    return any((alias.lower() in text.lower() if not alias.isascii() else
                re.search(r'(?<![A-Za-z0-9_])' + re.escape(alias) + r'(?![A-Za-z0-9_])', text, re.I))
               for alias in aliases)


def _sample_scope(record, atom):
    mapped = _record_map(record)
    direct = mapped.get('facet_scopes', {}).get(atom.get('record_pointer'))
    if direct:
        return direct
    statement = atom.get('statement', '')
    if not isinstance(statement, str):
        return None
    for scope in _catalog().get('sample_rules', []):
        if any(pattern in statement for pattern in scope['statement_markers']):
            return {key: value for key, value in scope.items() if key != 'statement_markers'}
    return None


def _atom_scope_context(record, atom, atoms):
    return {'scope': record.get('scope', record.get('scope_text', '')),
            'atom_kind': atom.get('kind'), 'record_pointer': atom.get('record_pointer'),
            'role_bindings': [], 'original_content_index': record_content_context(list(atoms))}


def _sample_declaration_request(record, family, atom, query):
    """A unique declaration can select only its existing original sample atom."""
    positive = query_scope(query)['positive_user_query']
    for symbol in source_identity.identity_symbols(record, family):
        if not re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_:.])', positive):
            continue
        proofs = [proof for proof in source_identity.identity_bindings(record, family, symbol)
                  if proof['record_pointer'] == atom['record_pointer'] and proof['claim_kind'] == atom['kind']]
        if not proofs:
            continue
        for match in _contract_matches(record, family, symbol):
            pointer = atom['record_pointer']
            role = match.get('pointer_roles', {}).get(pointer, {})
            if (pointer in match.get('record_pointers', []) and atom['kind'] == 'NSF' and
                    role.get('role') in ('METHOD_SUBJECT', 'SOURCE_OBSERVATION_SUBJECT') and
                    _subject_behavior(atom['statement'], symbol, exact=':' in symbol or '.' in symbol)):
                return {'schema': 'unique-declaration-original-sample-alignment/1',
                        'declared_symbol': proofs[0]['declared_symbol'], 'source_file': proofs[0]['source_file'],
                        'declaration_kind': proofs[0]['declaration_kind'],
                        'record_pointer': pointer, 'same_original_atom_and_reference': True,
                        'identity_is_behavior_proof': False, 'public_api_inferred': False}
    return None


def facet_admission(record, family, atoms, query, *, reference_context=None, atom_contexts=None):
    """Filter only scoped atoms. Preserve statement/kind/pointer byte-for-byte."""
    scope_query = query_scope(query)
    allowed, decisions = [], []
    original_atoms = _typed_atoms(record, family)
    for atom in atoms:
        own_context = (atom_contexts or {}).get(atom.get('record_pointer'))
        own_context = own_context or (reference_context or {}).get('atom_contexts', {}).get(atom.get('record_pointer'))
        own_context = own_context or _atom_scope_context(record, atom, original_atoms)
        focus = positive_focus_support(query, atom.get('statement', ''), own_context)
        if not focus['allowed']:
            decisions.append({'record_pointer': atom.get('record_pointer'), 'admitted': False,
                              'reason': 'POSITIVE_EXCLUSIVE_OBJECT_SCOPE_GAP',
                              'positive_focus_support': focus, 'whole_original_atom_preserved': True})
            dt.atom(record['id'], atom.get('record_pointer'), 'FACET_ADMISSION', kind=atom.get('kind'),
                    admitted=False, reason='POSITIVE_EXCLUSIVE_OBJECT_SCOPE_GAP')
            continue
        scope = _sample_scope(record, atom)
        if scope is None:
            if atom.get('record_pointer') is not None:
                dt.atom(record['id'],atom['record_pointer'],'FACET_ADMISSION',kind=atom.get('kind'),admitted=True,reason='UNSCOPED_FACET_ALLOWED')
            allowed.append(copy.deepcopy(atom))
            continue
        aliases = scope['aliases']
        excluded = any(_identity_match(clause, aliases) for clause in scope_query['negative_clauses'])
        explicit = _identity_match(scope_query['positive_query'], aliases)
        declaration_alignment = _sample_declaration_request(record, family, atom, query) if not explicit else None
        reference = None
        from .sample_reference import bounded_sample_reference, sample_reference_excluded
        excluded = excluded or sample_reference_excluded(query, scope, atom.get('statement', ''))
        admitted = not excluded and (not query.strip() or ((explicit or declaration_alignment) and not scope_query['generic']))
        if not admitted and not excluded and reference_context is not None:
            reference = bounded_sample_reference(record, atom, scope, query,
                context=reference_context.get('atom_contexts', {}).get(atom.get('record_pointer')),
                **{key: reference_context[key] for key in
                   ('projection', 'view', 'role', 'existing_admitted', 'existing_deep_admitted', 'request_frames')
                   if key in reference_context})
            admitted = reference is not None
        decision = {'record_pointer': atom.get('record_pointer'),
                    'sample_identity': scope['identity'],
                    'admitted': admitted,
                    'reason': ('SAMPLE_EXPLICITLY_EXCLUDED' if excluded else
                               'TASK_RELEVANT_SAMPLE_REFERENCE' if reference is not None else
                               'GENERIC_SCOPE_EXCLUDES_SAMPLE' if scope_query['generic'] else
                               'UNIQUE_DECLARATION_SELECTS_ORIGINAL_SAMPLE' if declaration_alignment else
                               'SAMPLE_IDENTITY_REQUESTED' if explicit else
                               'EXACT_RECORD_BROWSE' if not query.strip() else
                               'SAMPLE_IDENTITY_NOT_REQUESTED'),
                    'delivery_scope': 'SAMPLE_SPECIFIC'}
        decisions.append(decision)
        if atom.get('record_pointer') is not None:
            dt.atom(record['id'],atom['record_pointer'],'FACET_ADMISSION',kind=atom.get('kind'),
                admitted=admitted,reason=decision['reason'])
        if admitted:
            wrapped = copy.deepcopy(atom)
            wrapped['delivery_scope'] = {'kind': 'SAMPLE_SPECIFIC',
                                         'sample_identity': scope['identity'],
                                         'not_a_generic_contract': True}
            if reference is not None:
                wrapped['sample_reference'] = reference
            if declaration_alignment is not None:
                wrapped['sample_declaration_alignment'] = declaration_alignment
            allowed.append(wrapped)
    return allowed, decisions


def _exact_subject_locator(binding, symbol, original_refs):
    """An accepted original source declaration can resolve a method alias only."""
    steam = _steam_binding_proof(binding, symbol)
    if steam is not None:
        return _reference_key(binding) in original_refs
    if (normalize_symbol(binding.get('symbol', '')) != symbol or
            binding.get('original_reference_precision') != 'SINGLE_SOURCE_LOCATOR_NODE' or
            not binding.get('source_file') or
            _reference_key(binding) not in original_refs or not all(_reference_key(binding))):
        return False
    locator = binding.get('source_locator', {})
    names = []
    for field in ('symbol', 'function', 'signature', 'signatures'):
        value = locator.get(field, [])
        names.extend([value] if isinstance(value, str) else value if isinstance(value, list) else [])
    method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
    for name in names:
        if not isinstance(name, str):
            continue
        name = name.strip().strip('`')
        head = re.match(r'^(?:function\s+)?(' + QUALIFIED.pattern + r')', name)
        if not head or head.group(1) != symbol:
            continue
        declarations = QUALIFIED.findall(name)
        # 描述中的字段不提供方法 owner；并列方法或同名异 owner 则拒绝别名。
        if any(other != symbol and (':' in other or
                   other.rsplit('.', 1)[-1] == method) for other in declarations):
            continue
        return True
    return False


def _bare_alias_requested(positive, method):
    for occurrence in re.finditer(r'(?<![A-Za-z0-9_:.])' + re.escape(method) +
                                  r'(?![A-Za-z0-9_:.])', positive):
        start = max(positive.rfind(separator, 0, occurrence.start())
                    for separator in ('。', '；', ';', '\n', '，', ',')) + 1
        prefix = positive[start:occurrence.start()]
        suffix = positive[occurrence.end():]
        if re.search(r'(?:字段|变量|参数|\b(?:field|variable|parameter|argument)\b)\s*(?:名(?:称)?(?:为|叫)?|named|name|called)?\s*$', prefix, re.I):
            continue
        if re.match(r'\s*(?:字段|变量|参数|=|\b(?:field|variable|parameter|argument)\b)', suffix, re.I):
            continue
        if prefix.count('(') > prefix.count(')') and not re.match(r'\s*\(', suffix):
            continue
        return True
    return False


def _subject_aliases(record, family, positive, symbols):
    """Resolve an unqualified name to one already accepted source method subject.

    This does not add caller/callee edges or claim a complete method contract.
    """
    explicit_methods = {name.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
                        for name in QUALIFIED.findall(positive)}
    atoms = {atom['record_pointer']: atom for atom in _typed_atoms(record, family)}
    candidates = {}
    for symbol in symbols:
        if not QUALIFIED.fullmatch(symbol):
            continue
        method = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
        if method in explicit_methods or not _bare_alias_requested(positive, method):
            continue
        for match in contract_matches(record, family, symbol):
            accepted = []
            for pointer in match.get('record_pointers', []):
                atom = atoms[pointer]
                role = match.get('pointer_roles', {}).get(pointer, {})
                role = role.get('role') if isinstance(role, dict) else role
                if atom['kind'] != 'NSF' or role != 'METHOD_SUBJECT':
                    continue
                original = (record['claims'][int(pointer.rsplit('/', 1)[1])]
                            if family == 'core' else record.get('native_fact', {}))
                refs = {_reference_key(ref) for ref in original.get('evidence_refs', [])}
                declaration_proofs = source_identity.identity_bindings(record, family, symbol)
                declared_subject = any(proof['record_pointer'] == pointer and
                    _reference_key(proof['reference']) in refs for proof in declaration_proofs)
                current_subject = match.get('pointer_roles', {}).get(pointer, {}).get('callee_semantics_supported') is True
                if (declared_subject and current_subject) or (any(_exact_subject_locator(binding, symbol, refs)
                        for binding in match.get('source_bindings', {}).get(pointer, [])) and
                        (_subject_behavior(atom['statement'], symbol, exact=False) or
                         _mapped_owner_subject(atom['statement'], symbol,
                                               match.get('source_bindings', {}).get(pointer, [])))):
                    accepted.append(pointer)
            if accepted:
                canonical_symbol = source_identity.resolve_identity(record, family, symbol) or symbol
                owners = candidates.setdefault(method, {})
                owners[canonical_symbol] = list(dict.fromkeys(owners.get(canonical_symbol, []) + accepted))
    return {next(iter(owners)): {'query_name': method,
                                'basis': 'UNIQUE_ACCEPTED_ORIGINAL_SOURCE_METHOD_SUBJECT',
                                'verified_subject_record_pointers': next(iter(owners.values())),
                                'new_dependency_relation': False}
            for method, owners in candidates.items() if len(owners) == 1}


def requested_contracts(record, family, query):
    positive = query_scope(query)['positive_query']
    qualified_methods = {symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
                         for symbol in QUALIFIED.findall(positive)}
    result = []
    symbols = contract_symbols(record, family)
    aliases = _subject_aliases(record, family, positive, symbols)
    for symbol in symbols:
        if ':' not in symbol and '.' not in symbol and symbol in qualified_methods:
            continue
        if symbol in aliases or re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(symbol) + r'(?![A-Za-z0-9_:.])', positive):
            matches = contract_matches(record, family, symbol)
            for match in matches:
                if symbol in aliases:
                    match['query_name_resolution'] = copy.deepcopy(aliases[symbol])
                contexts, decisions = context_admission(record, family, match.get('context_pointer_bindings', []), query)
                match['context_admission'] = decisions
                match['excluded_context_record_pointers'] = sorted({decision['record_pointer'] for decision in decisions if not decision['admitted']})
                match['needed_context_excluded'] = match['excluded_context_record_pointers']
                match['context_closure_gaps'] = sorted(set(match.get('context_closure_gaps', [])) |
                                                      set(match['excluded_context_record_pointers']))
                match['context_pointer_bindings'] = contexts
                match['context_record_pointers'] = [context['record_pointer'] for context in contexts]
                match['context_claim_kinds'] = [context['kind'] for context in contexts]
            result.extend(matches)
    return result

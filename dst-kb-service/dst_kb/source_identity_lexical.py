"""Pure Lua declaration lexing and conservative original-subject syntax."""
import json
import re
from hashlib import sha256
from pathlib import Path
from types import CodeType, FunctionType

HEADER_PATTERN = r'^\s*(local\s+)?function\s+([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)\s*\('
HEADER = re.compile(HEADER_PATTERN, re.ASCII)
IDENTITY_PATTERN = r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*'
SUBJECT_VERSION = 'original-nsf-named-subject-syntax/1'
PREDICATE_PATTERN = (r'^(?:\s*\([^()]*\))?\s*(?:(?:会|直接|仅)\s*)?(?:用(?!作|于名称|于列表)|遍历|调用|返回|保存|读取|检查|创建|新建|删除|移除|登记|'
                     r'执行|拒绝|跳过|设置|清除|清空|不检查|不读取|为每次|'
                     r'(?:returns?|uses?|iterates?|calls?|stores?|reads?|checks?|creates?|removes?|'
                     r'registers?|rejects?|skips?|sets?|clears?)\b)')
FINGERPRINT_FUNCTIONS = ('_digest', '_code_value', 'scan', 'headers', 'subject_witness', 'accepted_fingerprint')


def _digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _code_value(value):
    if isinstance(value, CodeType):
        fields = ('co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount', 'co_nlocals',
                  'co_stacksize', 'co_flags', 'co_code', 'co_names', 'co_varnames',
                  'co_name', 'co_freevars', 'co_cellvars', 'co_consts')
        return {'code': {name: _code_value(getattr(value, name, None)) for name in fields}}
    if isinstance(value, bytes):
        return {'bytes': value.hex()}
    if isinstance(value, tuple):
        return {'tuple': [_code_value(x) for x in value]}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise ValueError('UNSUPPORTED_IDENTITY_HELPER_CONSTANT')


def scan(text, initial_state='CODE', require_closed=True):
    """Preserve positions while masking strings/comments; never guess a state."""
    if not isinstance(text, str) or '\r' in text or '\x00' in text or initial_state != 'CODE':
        raise ValueError('UNVERIFIED_LUA_LEXICAL_START')
    masked, line_states, i, quoted, long_end, valid = [], ['CODE'], 0, None, None, True

    def state():
        return 'LONG:' + long_end if long_end else 'SHORT:' + quoted if quoted else 'CODE'

    def consume(segment, opaque=True):
        for char in segment:
            masked.append('\n' if char == '\n' else ' ' if opaque else char)
            if char == '\n':
                line_states.append(state())

    while i < len(text):
        char = text[i]
        if long_end:
            if text.startswith(long_end, i):
                size = len(long_end)
                consume(text[i:i + size]); i += size; long_end = None
            else:
                consume(char); i += 1
        elif quoted:
            if char == '\\' and i + 1 < len(text):
                consume(text[i:i + 2]); i += 2
            else:
                if char == '\n':
                    valid = False
                consume(char); i += 1
                if char == quoted:
                    quoted = None
        elif char in ('"', "'"):
            quoted = char; consume(char); i += 1
        else:
            comment = text.startswith('--', i)
            long = re.match(r'\[(=*)\[', text[i + (2 if comment else 0):])
            if long:
                size = len(long.group()) + (2 if comment else 0)
                long_end = ']' + long.group(1) + ']'
                consume(text[i:i + size]); i += size
            elif comment:
                end = text.find('\n', i)
                if end < 0:
                    end = len(text)
                consume(text[i:end]); i = end
            else:
                consume(char, False); i += 1
    terminal = state()
    if not valid or (require_closed and terminal != 'CODE'):
        raise ValueError('INVALID_OR_UNCLOSED_LUA_LEXICAL_STATE')
    return {'masked': ''.join(masked), 'line_states': line_states, 'terminal_state': terminal}


def headers(text, masked, start=1):
    raw_lines, code_lines = text.splitlines(), masked.splitlines()
    if len(raw_lines) != len(code_lines):
        raise ValueError('LUA_MASK_LINE_MISMATCH')
    found = []
    for offset, (raw, code) in enumerate(zip(raw_lines, code_lines)):
        original, actual = HEADER.match(raw), HEADER.match(code)
        if original and actual and original.groups() == actual.groups():
            local, symbol = original.groups()
            found.append({'line': start + offset, 'symbol': symbol, 'local': bool(local), 'header': raw})
    return found


def subject_witness(statement, symbol):
    """Recognize a clause-initial named subject, without identity/role recursion."""
    if (not isinstance(statement, str) or not isinstance(symbol, str) or
            re.fullmatch(IDENTITY_PATTERN, symbol, re.ASCII) is None or
            not (':' in symbol or '.' in symbol)):
        return None
    owner, method = re.split(r'[:.]', symbol)[-2:]
    owner = symbol[:-(len(method) + 1)]
    qualified = re.findall(r'(?<![A-Za-z0-9_:.])([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+)(?![A-Za-z0-9_:.])', statement, re.ASCII)
    if not any(name[:-(len(re.split(r'[:.]', name)[-1]) + 1)] == owner for name in qualified):
        return None
    foreign = [name for name in qualified if re.split(r'[:.]', name)[-1] == method and name != symbol]
    if foreign:
        return None
    for spelling in (symbol, method):
        pattern = r'(?<![A-Za-z0-9_:.])' + re.escape(spelling) + r'(?![A-Za-z0-9_:.])'
        for occurrence in re.finditer(pattern, statement, re.ASCII):
            before = statement[:occurrence.start()]
            depth, quote, escaped = 0, None, False
            for char in before:
                if quote:
                    if escaped:
                        escaped = False
                    elif char == '\\':
                        escaped = True
                    elif char == quote:
                        quote = None
                elif char in ('"', "'", '`'):
                    quote = char
                elif char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth -= 1
            if depth or quote:
                continue
            boundary = list(re.finditer(r'[。；;\n]|\.\s+', before))
            start = boundary[-1].end() if boundary else 0
            if statement[start:occurrence.start()].strip():
                continue
            stop = re.search(r'[。；;\n]|\.\s+', statement[occurrence.end():])
            end = occurrence.end() + stop.start() if stop else len(statement)
            tail = statement[occurrence.end():end]
            if not re.match(PREDICATE_PATTERN, tail, re.I):
                continue
            return {'schema': SUBJECT_VERSION, 'spelling': spelling,
                    'span_start': occurrence.start(), 'span_end': occurrence.end(),
                    'clause_start': start, 'clause_end': end,
                    'clause_sha256': _digest(statement[start:end]), 'declared_owner': owner}
    return None


def accepted_fingerprint():
    """Bind both current source bytes and loaded helper code, including globals."""
    path = Path(__file__).resolve()
    raw = path.read_bytes()
    compiled = compile(raw, str(path), 'exec', dont_inherit=True)
    source = {value.co_name: _digest(_code_value(value)) for value in compiled.co_consts if isinstance(value, CodeType)}
    loaded = {}
    for name in FINGERPRINT_FUNCTIONS:
        function = globals().get(name)
        if not isinstance(function, FunctionType) or function.__module__ != __name__:
            raise ValueError('UNVERIFIED_LOADED_IDENTITY_HELPER')
        loaded[name] = _digest(_code_value(function.__code__))
        if source.get(name) != loaded[name] or Path(function.__code__.co_filename).resolve() != path:
            raise ValueError('IDENTITY_HELPER_CODE_ARTIFACT_MISMATCH')
    return {'schema': 'source-identity-pure-helper-fingerprint/1', 'artifact_name': path.name,
            'artifact_sha256': sha256(raw).hexdigest(), 'loaded_function_code_sha256': loaded,
            'header_pattern': HEADER.pattern, 'header_flags': HEADER.flags,
            'identity_pattern': IDENTITY_PATTERN, 'predicate_pattern': PREDICATE_PATTERN,
            'subject_version': SUBJECT_VERSION, 'loaded_code_matches_artifact': True}

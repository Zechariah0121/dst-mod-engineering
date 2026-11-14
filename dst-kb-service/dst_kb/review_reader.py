"""Explicit whole-object review with content-bound, stateless continuation."""
import base64
import copy
import json
import re
from hashlib import sha256

from .config import KBError
from .source_epoch_runtime import epoch_arguments


def size(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def token(binding, offset):
    raw = json.dumps([binding, offset], separators=(',', ':')).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def offset(cursor, binding, count):
    if not cursor:
        return 0
    try:
        if not isinstance(cursor, str) or len(cursor) > 2000 or not re.fullmatch(r'[A-Za-z0-9_-]+', cursor):
            raise ValueError()
        expected, index = json.loads(base64.b64decode(cursor + '=' * (-len(cursor) % 4), altchars=b'-_', validate=True))
        if expected != binding or type(index) is not int or not 0 <= index < count:
            raise ValueError()
        return index
    except (ValueError, TypeError, UnicodeError) as exc:
        raise KBError('INVALID_CURSOR', 'Continuation does not match this request, record or source environment') from exc


def at(value, pointer):
    # Share the strict public JSON Pointer implementation, including escapes.
    from .public_catalog import at as select
    return select(value, pointer)


def owner_pointer(record, family, pointer):
    at(record, pointer)  # Validate the requested subfield before widening.
    if family in ('core', 'native_mechanism'):
        match = re.match(r'^/(claims|api_contracts|mechanism_steps)/(0|[1-9][0-9]*)(?:/|$)', pointer)
        if match:
            return '/' + match[1] + '/' + match[2]
    if family == 'n001':
        match = re.match(r'^/(native_fact|ai_coding_impact|common_ai_failure|recommended_reasoning)(?:/|$)', pointer)
        if match:
            return '/' + match[1]
    if family == 'legacy':
        match = re.match(r'^/details/([^/]+)(?:/|$)', pointer)
        if match:
            return '/details/' + match[1]
    return pointer


def children(record, family, pointer):
    """Split only containers, retaining typed owners and their original fields."""
    value = at(record, pointer)
    if owner_pointer(record, family, pointer) != pointer:
        return []
    if re.fullmatch(r'/(claims|api_contracts|mechanism_steps)/[0-9]+', pointer):
        return []
    if family == 'n001' and pointer in ('/native_fact', '/ai_coding_impact', '/common_ai_failure', '/recommended_reasoning'):
        return []
    if family == 'legacy' and pointer.startswith('/details/'):
        return []
    keys = list(value) if isinstance(value, dict) else range(len(value)) if isinstance(value, list) else []
    return [pointer + '/' + str(key).replace('~', '~0').replace('/', '~1') for key in keys]


def units(record, family, pointer):
    """One level of automatic container expansion, with stable record order."""
    selected = children(record, family, pointer)
    if not selected:
        return [pointer]
    result = []
    for child in selected:
        value = at(record, child)
        if (child in ('/claims', '/api_contracts', '/mechanism_steps', '/details', '/reviewer_expansion')
                or family == 'guide' and child == '/sections') and isinstance(value, (dict, list)):
            result.extend(children(record, family, child) or [child])
        else:
            result.append(child)
    return result


def read(record, family, context, pointer='', cursor='', maximum=24000):
    if type(maximum) is not int or not 1000 <= maximum <= 64000:
        raise KBError('INVALID_ARGUMENT', 'max_bytes must be 1000..64000')
    if not isinstance(pointer, str) or len(pointer) > 2000 or (pointer and not pointer.startswith('/')):
        raise KBError('INVALID_ARGUMENT', 'Expected a bounded record-relative JSON Pointer')
    canonical = owner_pointer(record, family, pointer)
    base = copy.deepcopy(context) | {
        'id': record['id'], 'family': family, 'purpose': 'review', 'projection': 'reviewer',
        'pointer': canonical, 'requested_pointer': pointer, 'objects': [],
        'coding_admission_granted': False, 'runtime_validation_performed': False,
        'whole_value_delivered': False, 'complete': False, 'continuation': None,
    }
    binding = digest({'record': record, 'context': context, 'pointer': pointer})
    whole = base | {'objects': [{'pointer': canonical, 'value': at(record, canonical)}],
                    'whole_value_delivered': True, 'complete': True}
    if not cursor and size(whole) <= maximum:
        return whole
    pointers = units(record, family, canonical)
    index = offset(cursor, binding, len(pointers))
    if size(base) > maximum:
        retry = None if maximum == 64000 or size(base) > 64000 else {
            'tool': 'get_entry', 'arguments': epoch_arguments({
                'id': record['id'], 'purpose': 'review', 'projection': 'reviewer',
                'pointer': pointer, 'cursor': token(binding, index), 'max_bytes': 64000})}
        withheld = {'id': record['id'], 'purpose': 'review', 'objects': [], 'complete': False,
                'whole_value_delivered': False, 'withheld_reason': 'REQUIRED_CONTEXT_EXCEEDS_BUDGET',
                'minimum_context_bytes': size(base), 'coding_admission_granted': False,
                'continuation': retry,
                'guidance': 'Use the supplied larger-budget call.' if retry else 'Read the registered file with complete Scope and evidence.'}
        if size(withheld) > maximum:
            withheld['continuation'] = None
            withheld['guidance'] = 'Retry with a larger byte budget or read the registered file with complete Scope and evidence.'
        return withheld
    result = base
    while index < len(pointers):
        selected = pointers[index]
        followup = None if index + 1 == len(pointers) else {
            'tool': 'get_entry', 'arguments': epoch_arguments({
                'id': record['id'], 'purpose': 'review', 'projection': 'reviewer',
                'pointer': pointer, 'cursor': token(binding, index + 1), 'max_bytes': maximum})}
        proposed = result | {
            'objects': result['objects'] + [{'pointer': selected, 'value': at(record, selected)}],
            'continuation': followup, 'complete': followup is None,
        }
        if size(proposed) > maximum:
            if result['objects']:
                break
            retry = None if maximum == 64000 else {'tool': 'get_entry', 'arguments': epoch_arguments({
                'id': record['id'], 'purpose': 'review', 'projection': 'reviewer',
                'pointer': pointer, 'cursor': token(binding, index), 'max_bytes': 64000})}
            withheld = base | {'withheld_reason': 'WHOLE_OBJECT_AND_REQUIRED_CONTEXT_EXCEED_BUDGET',
                              'withheld_pointer': selected, 'continuation': retry,
                              'required_payload_bytes': size(proposed)}
            if retry is None:
                withheld['guidance'] = 'This complete object exceeds the service byte ceiling. Read the registered file with its complete Scope and evidence.'
            if size(withheld) <= maximum:
                return withheld
            compact = {
                'id': record['id'], 'purpose': 'review', 'objects': [], 'complete': False,
                'whole_value_delivered': False,
                'withheld_reason': 'REQUIRED_CONTEXT_EXCEEDS_BUDGET',
                'coding_admission_granted': False, 'continuation': retry,
                'guidance': 'Use the supplied larger-budget call.' if retry else
                    'Read the registered file with its complete Scope and evidence.',
            }
            if size(compact) > maximum:
                compact['continuation'] = None
                compact['guidance'] = 'Retry with a larger byte budget or read the registered file with complete Scope and evidence.'
            return compact
        result = proposed
        index += 1
    return result

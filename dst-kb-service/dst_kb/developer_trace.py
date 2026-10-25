"""Opt-in, request-local observations. These diagnostics are never source facts."""
import copy
import json
import math
import re
from contextvars import ContextVar
from .config import KBError

_CURRENT = ContextVar('dst_developer_trace', default=None)
_RECORD = ContextVar('dst_developer_trace_record', default=None)
_NUMBERS = frozenset(('rank_score', 'unanchored_score', 'absolute_floor', 'relative_floor'))
_RECORD_FIELDS = frozenset(('family', 'admission', 'filters', 'rank_position',
    'ranker_limit_status', 'service_top_k_status', 'delivery_admission_status',
    'result_position', 'strong_task_trigger', 'role_factor', 'role_preference',
    'correction_priority', 'absolute_pass', 'relative_pass', 'score_components',
    'source_context_status', 'source_context_attempted', 'integrity_error_count',
    'selection_mode', 'semantic_inventory_status')) | _NUMBERS
_ATOM_FIELDS = frozenset(('kind', 'evaluated', 'reason', 'supported',
    'whole_atom_delivery_allowed', 'subject_mismatch', 'excluded_source_scope',
    'bucket', 'score', 'lexical_score', 'semantic_score', 'strong', 'profile_member',
    'bucket_count_before', 'bucket_limit', 'extras_position', 'selection_position',
    'selected', 'delivered_slot', 'index', 'admitted', 'unit_lane'))


def _enum(value):
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(r'[A-Za-z0-9_ /.-]+', value):
        raise ValueError('invalid diagnostic enum')
    return value


def _scalar(value):
    if value is None or type(value) is bool or type(value) is int:
        return value
    if type(value) is float and math.isfinite(value):
        return value
    return _enum(value)


def _number(value=None):
    return {'value': value, 'evaluated': value is not None,
            'status': 'EVALUATED' if value is not None else 'NOT_EVALUATED'}


class Collector:
    MAX_RECORDS = 32
    MAX_ATOMS = 256
    MAX_EVENTS = 8192
    MAX_BYTES = 1048576

    def __init__(self, record_ids):
        self.complete = True
        self.truncated = False
        self.dropped_count = 0
        self.affected = set()
        self.events = 0
        self.stopped = False
        self.records = {}
        for kid in record_ids:
            if len(self.records) >= self.MAX_RECORDS:
                self.fail('RECORD_CAP')
                continue
            self.records[kid] = {'id': kid, 'family': None,
                'terminal_stage': 'NOT_OBSERVED_RECORD', 'terminal_reason': 'UNKNOWN',
                'admission': 'NOT_EVALUATED', 'filters': [],
                **{field: _number() for field in _NUMBERS}, 'rank_position': None,
                'ranker_limit_status': 'NOT_EVALUATED', 'service_top_k_status': 'NOT_EVALUATED',
                'delivery_admission_status': 'NOT_EVALUATED', 'result_position': None,
                'source_context_status': 'NOT_EVALUATED', 'source_context_attempted': False,
                'semantic_inventory_status': 'NOT_OBSERVED_PREBUILT', 'atoms': []}

    def fail(self, stage, truncated=True):
        self.complete = False
        self.truncated |= truncated
        self.dropped_count += 1
        self.affected.add(stage)

    def observe(self, kid, stage, fields, pointer=None, terminal=False):
        if kid not in self.records:
            return
        if self.stopped or self.events >= self.MAX_EVENTS:
            self.fail(stage)
            self.stopped = True
            return
        self.events += 1
        record = self.records[kid]
        stage = _enum(stage)
        if pointer is not None:
            if not isinstance(pointer, str) or not pointer.startswith('/') or len(pointer) > 512:
                raise ValueError('invalid original atom pointer')
            if len(record['atoms']) >= self.MAX_ATOMS:
                self.fail(stage)
                return
            atom = {'record_pointer': pointer, 'stage': stage, 'evaluated': True,
                    **{key: None for key in _ATOM_FIELDS if key != 'evaluated'}}
            for key, value in fields.items():
                if key not in _ATOM_FIELDS:
                    raise ValueError('unknown diagnostic atom field')
                atom[key] = _scalar(value)
            record['atoms'].append(atom)
        elif terminal:
            record['terminal_stage'] = stage
            record['terminal_reason'] = _enum(fields['reason'])
        else:
            for key, value in fields.items():
                if key not in _RECORD_FIELDS:
                    raise ValueError('unknown diagnostic record field')
                if key in _NUMBERS:
                    record[key] = _number(_scalar(value))
                elif key == 'filters':
                    record[key].append({'passed': _scalar(value)})
                elif key == 'score_components':
                    record[key] = {_enum(k): _scalar(v) for k, v in value.items()}
                else:
                    record[key] = _scalar(value)

    def finish(self):
        result = {'schema_version': 'dst-developer-trace/1',
            'kind': 'DEVELOPER_DIAGNOSTIC', 'evidence_class': 'NOT_SOURCE_FACT',
            'normal_method_contract': False, 'task_answer_proof': False,
            'complete': self.complete, 'truncated': self.truncated,
            'dropped_count': self.dropped_count, 'records': list(self.records.values()),
            'not_observed_stages': sorted(self.affected)}
        if len(json.dumps(result, ensure_ascii=False).encode('utf-8')) > self.MAX_BYTES:
            self.fail('TRACE_BYTE_CAP')
            result.update(complete=False, truncated=True, dropped_count=self.dropped_count,
                          records=[], not_observed_stages=sorted(self.affected))
        return copy.deepcopy(result)


def _observe(kid, stage, fields, pointer=None, terminal=False):
    collector = _CURRENT.get()
    if collector is None:
        return
    try:
        collector.observe(kid or _RECORD.get(), stage, fields, pointer, terminal)
    except Exception:
        # 只关闭诊断；不接管正常业务异常，也不把异常原文写进 trace。
        collector.complete = False
        collector.stopped = True
        collector.dropped_count += 1
        collector.affected.add('COLLECTOR_FAILURE')


def record(kid, stage, **fields):
    _observe(kid, stage, fields)


def atom(kid, pointer, stage, **fields):
    _observe(kid, stage, fields, pointer=pointer)


def terminal(kid, stage, reason):
    _observe(kid, stage, {'reason': reason}, terminal=True)


def top_k_break(kid):
    collector = _CURRENT.get()
    if collector is None:
        return
    record(kid, 'SERVICE_TOP_K', service_top_k_status='BREAK_TRIGGER')
    for target, value in collector.records.items():
        if value['terminal_stage'] == 'RANKER_RETURNED':
            record(target, 'SERVICE_TOP_K', service_top_k_status='NOT_EVALUATED_AFTER_SERVICE_TOP_K_BREAK')
            terminal(target, 'SERVICE_TOP_K', 'NOT_EVALUATED_AFTER_SERVICE_TOP_K_BREAK')


def bind_record(kid):
    return _RECORD.set(kid)


def reset_record(token):
    _RECORD.reset(token)


def _incomplete(stage):
    return {'schema_version': 'dst-developer-trace/1',
        'kind': 'DEVELOPER_DIAGNOSTIC', 'evidence_class': 'NOT_SOURCE_FACT',
        'normal_method_contract': False, 'task_answer_proof': False,
        'complete': False, 'truncated': False, 'dropped_count': 1,
        'records': [], 'not_observed_stages': [stage]}


def call(instance, tool, arguments, record_ids, developer_opt_in=True):
    if developer_opt_in is not True:
        raise KBError('INVALID_ARGUMENT', 'developer trace requires explicit opt-in')
    if tool not in ('search_kb', 'lookup_api') or not isinstance(arguments, dict):
        raise KBError('INVALID_ARGUMENT', 'unsupported developer diagnostic call')
    if (not isinstance(record_ids, (list, tuple)) or not 1 <= len(record_ids) <= 32 or
            any(not isinstance(kid, str) or not kid or len(kid) > 128 for kid in record_ids)):
        raise KBError('INVALID_ARGUMENT', 'record_ids must contain 1..32 bounded IDs')
    try:
        collector = Collector(list(dict.fromkeys(record_ids)))
    except Exception:
        collector = None
    token = _CURRENT.set(collector)
    record_token = _RECORD.set(None)
    try:
        normal_response = getattr(instance, tool)(**arguments)
        if collector is None:
            trace = _incomplete('COLLECTOR_INIT_FAILURE')
        else:
            try:
                trace = collector.finish()
            except Exception:
                trace = _incomplete('COLLECTOR_FINALIZE_FAILURE')
        return {'normal_response': normal_response, 'developer_trace': trace}
    finally:
        _RECORD.reset(record_token)
        _CURRENT.reset(token)

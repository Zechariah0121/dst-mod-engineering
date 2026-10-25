"""Whole original atom closures and separately bounded deferred companions."""
import copy
import json
from contextlib import contextmanager
from contextvars import ContextVar
from hashlib import sha256


ATOMIC_BUDGET_UNIT = 'WHOLE_ORIGINAL_ATOM_WITH_CONDITIONS_SCOPE_BOUNDARIES_AND_DEPENDENCIES'
_COST_OBSERVER = ContextVar('dst_atomic_budget_cost_observer', default=None)


@contextmanager
def observe_budget_trials(*, include_payload=True):
    """Offline, request-local receipt of actual serialized fit attempts.

    Nothing is added to the public response or retained between requests. The
    optional payload is the complete proposed packet, never a summed estimate
    of atoms. Nested/concurrent observers own independent ledgers.
    """
    rows = []
    token = _COST_OBSERVER.set((rows, include_payload))
    try:
        yield rows
    finally:
        _COST_OBSERVER.reset(token)


def serialized_payload_cost(payload, maximum=None, *, trial=None, phase='trial'):
    """Measure the ordinary service JSON that is actually used for fitting."""
    encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    observer = _COST_OBSERVER.get()
    if observer is not None:
        rows, include_payload = observer
        row = {'phase': phase, 'complete_payload_utf8_bytes': len(encoded),
               'complete_payload_sha256': sha256(encoded).hexdigest(),
               'max_payload_bytes': maximum,
               'fits': len(encoded) <= maximum if maximum is not None else None,
               'selected_entry_ids': [card.get('id') for card in payload.get('entries', [])]}
        if isinstance(trial, dict):
            row.update(trial_entry_id=trial.get('id'),
                seed_record_pointers=list(trial.get('atomic_delivery', {}).get(
                    'delivered_seed_record_pointers', trial.get('record_context_delivery', {}).get('seed_record_pointers', []))),
                whole_original_record_pointers=list(dict.fromkeys(atom['record_pointer']
                    for field in ('decision', 'critical_boundary', 'project_policy_questions')
                    for atom in trial.get(field, [])
                    if isinstance(atom, dict) and isinstance(atom.get('record_pointer'), str))))
        if include_payload:
            row['complete_payload'] = copy.deepcopy(payload)
        rows.append(row)
    return len(encoded)


def atom_closure_units(pointers, seeds, protected, edges):
    """Keep directed required-pointer closure; never infer absent dependencies.

    Protected context/unknowns accompany every unit. An already missing required
    pointer stays a gap and cannot be invented or admitted by budget selection.
    """
    universe = set(pointers)
    protected = set(protected)
    if not protected <= universe or len(set(seeds)) != len(seeds) or not set(seeds) <= universe:
        raise ValueError('Invalid original atom closure universe')
    graph = {pointer: set() for pointer in universe}
    for edge in edges:
        dependent, required = edge.get('dependent_record_pointer'), edge.get('required_record_pointer')
        if not isinstance(dependent, str) or not isinstance(required, str):
            raise ValueError('Invalid original atom dependency')
        if dependent in graph:
            graph[dependent].add(required)
    units = []
    for seed in seeds:
        included, missing = protected | {seed}, set()
        pending = list(included)
        while pending:
            for required in graph[pending.pop()]:
                if required not in universe:
                    missing.add(required)
                elif required not in included:
                    included.add(required)
                    pending.append(required)
        units.append({'seed_record_pointer': seed, 'record_pointers': sorted(included),
                      'needed_context_missing': sorted(missing)})
    return units


def companion_subset(card, included):
    """Never split an atom/Scope or treat an unserved donor as delivered."""
    companions = card.get('companion_context', [])
    included = set(included)
    if any(type(index) is not int or not 0 <= index < len(companions) for index in included):
        raise ValueError('Invalid companion index')
    result = copy.deepcopy(card)
    result['companion_context'] = [copy.deepcopy(value) for index, value in enumerate(companions)
                                   if index in included]
    deferred = []
    for index, donor in enumerate(companions):
        if index in included:
            continue
        deferred.append({'id': donor['id'], 'record_sha256': donor['record_sha256'],
                         'record_pointers': [atom['record_pointer']
                             for field in ('decision', 'critical_boundary', 'project_policy_questions')
                             for atom in donor.get(field, []) if atom.get('record_pointer')],
                         'expansion': copy.deepcopy(donor.get('expansion', {}).get('reviewer'))})
    if deferred:
        result['companion_context_budget'] = {
            'status': 'PARTIAL_BOUNDED_CONTEXT', 'withheld_donors': deferred,
            'reason': 'COMPLETE_PRIMARY_CARD_AND_DONOR_EXCEED_PAYLOAD_BUDGET',
            'withheld_context_delivered': False, 'entire_task_completion_proven': False,
            'necessary_dependency_proven': False,
            'followup': 'Expand the listed donor IDs before relying on unserved context; primary facts and their original Scope remain whole.'}
    return result

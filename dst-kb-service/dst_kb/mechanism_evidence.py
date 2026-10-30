"""Whole single-locator evidence, with only its own source assessment.

The caller owns Reviewer admission. This module never restores Lua, expands
claims, or promotes research/HOLD. A locator's file/hash/range is one atom.
"""
import copy
import json

from .config import KBError
from . import native_mechanism, nativecore
from .source_epoch_runtime import source_preparation_document


def _cost(value):
    return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))


def resolve(record, index=0, subpointer='', maximum=24000, source_environment=None):
    """Resolve one entry-manifest reference; narrower pointers retain its atom."""
    if type(index) is not int or not 0 <= index <= 9999:
        raise KBError('INVALID_ARGUMENT', 'reference_index must be 0..9999')
    if type(maximum) is not int or not 1000 <= maximum <= 24000:
        raise KBError('INVALID_ARGUMENT', 'max_bytes must be 1000..24000')
    if (not isinstance(subpointer, str) or len(subpointer) > 2000
            or (subpointer and not subpointer.startswith('/'))):
        raise KBError('INVALID_ARGUMENT', 'subpointer must be empty or an absolute JSON pointer')
    entry, doc, registration = record['entry'], record['document'], record['registration']
    identifiers = native_mechanism.local_refs(entry)
    if index >= len(identifiers):
        raise KBError('INVALID_ARGUMENT', 'Mechanism reference index outside entry manifest')
    identifier = identifiers[index]
    position, ref = next((i, r) for i, r in enumerate(doc['source_references']) if r['id'] == identifier)
    if subpointer:
        try:
            nativecore.pointer(ref, subpointer)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise KBError('INVALID_ARGUMENT', 'Invalid source locator subpointer') from exc
    pointer = '/source_references/' + str(position)
    context = {
        'id': entry['id'], 'title': entry['title'], 'family': 'native_mechanism',
        'entry_type': native_mechanism.TYPE, **native_mechanism.STATES,
        'scope': copy.deepcopy(entry['scope']), 'unknowns': copy.deepcopy(entry['unknowns']),
        'source_epoch': doc['source_epoch'], 'archive_sha256': doc['archive_sha256'],
        'limitations': copy.deepcopy(doc['limitations']),
        'pointer': pointer, 'requested_pointer': pointer + subpointer,
        'requested_subpointer': subpointer, 'reference_index': index,
        'value': copy.deepcopy(ref), 'source_references': [copy.deepcopy(ref)],
        'artifact': {'file': registration['file'], 'sha256': registration['sha256'], 'pointer': pointer},
        'review_record': copy.deepcopy(registration['review']),
        'evidence_status': 'LOCATOR_HASH_ONLY', 'runtime_validation_performed': False,
        'coding_admission_granted': False, 'notice': native_mechanism.NOTICE,
    }
    assessment = source_preparation_document()
    if assessment is not None:
        matches = [row for row in assessment['native_mechanisms'].get('documents', [])
                   if row['file'] == registration['file'] and row['sha256'] == registration['sha256']]
        if len(matches) != 1:
            raise KBError('SOURCE_EPOCH_STALE', 'Mechanism assessment does not bind this candidate.')
        selected = [row for row in matches[0]['references'] if row['reference_id'] == identifier]
        if len(selected) != 1:
            raise KBError('SOURCE_EPOCH_STALE', 'Mechanism source assessment is incomplete or ambiguous.')
        context['source_input_assessment'] = {
            'sources': copy.deepcopy(assessment['summary']['sources']),
            'references': copy.deepcopy(selected), 'notice': assessment['summary']['notice'],
            'runtime_game_verified': False,
        }
    payload = {'evidence': context, 'projection': 'reviewer'}
    if source_environment is not None:
        payload['source_environment'] = copy.deepcopy(source_environment)
    if _cost(payload) <= maximum:
        return payload
    # Withhold the entire locator and assessment together. Context is retained
    # only if it also fits; never shorten Scope/unknowns or a selected locator.
    withheld = {key: copy.deepcopy(context[key]) for key in (
        'id', 'family', 'knowledge_status', 'retrieval_status', 'coding_status',
        'scope', 'unknowns', 'source_epoch', 'archive_sha256', 'limitations',
        'artifact', 'pointer', 'requested_pointer', 'requested_subpointer', 'reference_index',
        'notice', 'runtime_validation_performed', 'coding_admission_granted')}
    withheld.update(bounded=True, withheld_reason='LOCATOR_AND_REQUIRED_SCOPE_EXCEED_BUDGET', value=None)
    if _cost(withheld) <= maximum:
        return withheld
    return {'id': entry['id'], 'bounded': True, 'value': None,
            'withheld_reason': 'LOCATOR_AND_REQUIRED_SCOPE_EXCEED_BUDGET',
            'guidance': 'No facts delivered. Retry with a larger budget; required context is never truncated.'}

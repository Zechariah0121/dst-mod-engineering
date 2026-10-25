"""Native knowledge sidecar: bounded projections and deterministic task routing."""
import copy
import json
import re
from hashlib import sha256
from pathlib import Path
from .config import KBError

FIELDS = ('id', 'title', 'engineering_question', 'native_fact', 'scope',
          'ai_coding_impact', 'common_ai_failure', 'recommended_reasoning',
          'does_not_mean', 'evidence_strength')
IDS = tuple(f'AI-N001-{n:02d}' for n in range(1, 14))
SCHEMA = 'native-ai-1.0'
TYPE = 'native_ai_knowledge'
DIRECTORY = 'data/native001/'
FILES = ('canonical-native001-ai-knowledge.json', 'canonical-native001-research-map.json',
         'canonical-native001-evaluation-metadata.json', 'canonical-native001-retrieval-map.json',
         'native001-track-status.json', 'T-P0-02-final-status.json')
EVIDENCE = {'native_fact': 'DIRECT_STATIC_SOURCE_IN_EXISTING_SNAPSHOT',
            'engineering_recommendation': 'BOUNDED_REASONING_FROM_SOURCE_AND_TASK_REQUIREMENTS',
            'effect_on_AI_quality': 'PER_ENTRY_CAUSAL_EFFECT_NOT_ESTABLISHED'}
SPECIAL = ('migration', 'shard', 'death', 'ghost', 'reroll', 'seamless', 'snapshot',
           '迁移', '分片', '跨洞穴', '死亡', '幽灵', '换角', '回档', '快照')


def paths(root):
    return [DIRECTORY + name for name in FILES if (root / DIRECTORY / name).is_file()]


def projection(value):
    if value not in ('coding', 'reviewer'):
        raise KBError('INVALID_ARGUMENT', 'projection must be coding or reviewer')
    return value


def coding(entry):
    return {key: copy.deepcopy(entry[key]) for key in FIELDS}


def reviewer(entry, research):
    return copy.deepcopy(entry) | {'reviewer_expansion': copy.deepcopy(research)}


def normalized(text):
    return re.sub(r'\s+', ' ', re.sub(r'([a-z])([A-Z])', r'\1 \2', text).lower()).strip()


def contains(text, term):
    term = normalized(term)
    if not term:
        return False
    if any('\u3400' <= c <= '\u9fff' for c in term):
        return term in text
    return re.search(r'(?<![a-z0-9_])' + re.escape(term) + r'(?![a-z0-9_])', text) is not None


def special_topic(text, routing):
    rules = routing.get('routing_rules', {})
    return any(contains(normalized(text), term) for term in rules.get('special_topic_triggers', SPECIAL))


def route(text, routing):
    """Stable task order and explicit topic gate; never expand supporting research."""
    value = normalized(text)
    rules = routing.get('routing_rules', {})
    aliases = rules.get('task_aliases', {})
    matched = []
    for order, task in enumerate(routing.get('tasks', [])):
        name = task['task']
        hits = [term for term in [name] + aliases.get(name, []) if contains(value, term)]
        if hits:
            matched.append(task)
    selected = []
    special = special_topic(text, routing)
    if special:
        selected.append(IDS[-1])
    for task in matched:
        for entry_id in task['core_entries']:
            if entry_id == IDS[-1] and not special:
                continue
            if entry_id not in selected:
                selected.append(entry_id)
    cap = min(5, rules.get('default_cap', routing.get('default_core_per_task_max', 5)))
    return selected[:cap], [task['task'] for task in matched]


def pointer(document, reference):
    if not isinstance(reference, str) or not reference.startswith('/'):
        raise ValueError('source pointer must be an absolute JSON pointer')
    result = document
    for part in reference[1:].split('/'):
        key = part.replace('~1', '/').replace('~0', '~')
        result = result[int(key)] if isinstance(result, list) else result[key]
    return result


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def load(root, schema_errors, check_supported_schema):
    present = paths(root)
    if not present:
        return None, {'present': False, 'entries': 0}
    if len(present) != len(FILES):
        raise KBError('CORRUPTED_KB', 'Incomplete Native sidecar file set')
    try:
        documents = {name: json.loads((root / DIRECTORY / name).read_text(encoding='utf-8')) for name in FILES}
        primary = documents[FILES[0]]
        schema = json.loads((root / 'schemas/native-ai.schema.json').read_text(encoding='utf-8'))
        check_supported_schema(schema)
        errors = schema_errors(primary, schema, schema, 'native')
        if errors:
            raise KBError('CORRUPTED_KB', '; '.join(errors[:10]))
        entries = primary['entries']
        byid = {entry['id']: entry for entry in entries}
        if [entry['id'] for entry in entries] != list(IDS):
            errors.append('Native canonical IDs/order must be exactly AI-N001-01..13')
        if primary.get('default_projection_fields') != list(FIELDS):
            errors.append('Native public projection contract')
        if set(primary.get('evidence_class_contract', {})) != {'NSF', 'RV', 'EI', 'REC', 'UNK', 'KNOWLEDGE_PRODUCT_EVALUATION'}:
            errors.append('Native evidence class registry')
        research_doc = documents[FILES[1]]
        rows = research_doc.get('entries', [])
        research = {row.get('canonical_id'): row for row in rows}
        if len(rows) != 13 or set(research) != set(IDS):
            errors.append('Native research mapping must cover all 13 IDs once')
        routing = documents[FILES[3]]
        rules = routing.get('routing_rules', {})
        cap = rules.get('default_cap', routing.get('default_core_per_task_max'))
        if type(cap) is not int or not 1 <= cap <= 5:
            errors.append('Native Coding cap must be 1..5')
        if routing.get('default_projection_fields') != list(FIELDS):
            errors.append('Native route projection contract')
        tasks = routing.get('tasks', [])
        names = [task.get('task') for task in tasks]
        task_count=routing.get('task_count')
        if type(task_count) is not int or task_count<1 or len(tasks)!=task_count or len(set(names))!=len(tasks) or any(not isinstance(name, str) or not name for name in names):
            errors.append('Native routing requires task_count unique nonempty named tasks')
        aliases = rules.get('task_aliases', {})
        if not isinstance(aliases, dict) or set(aliases) - set(names):
            errors.append('Native task alias registry')
        else:
            for values in aliases.values():
                if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                    errors.append('Native task aliases must be nonempty strings')
        triggers = rules.get('special_topic_triggers', SPECIAL)
        if not isinstance(triggers, (list, tuple)) or not triggers or any(not isinstance(term, str) or not term.strip() for term in triggers):
            errors.append('Native special topic gate')
        for task in tasks:
            values = task.get('core_entries', [])
            if not values or len(values) > 5 or len(values) != len(set(values)) or set(values) - set(IDS):
                errors.append('Native task references/cap: ' + str(task.get('task')))
        for override in routing.get('topic_overrides', []):
            if set(override.get('core_entries', [])) - set(IDS):
                errors.append('Native override reference')
        for case in routing.get('case_route_corrections', routing.get('proposed_eval_case_routes', [])):
            if set(case.get('core_subset', [])) - set(IDS) or len(case.get('core_subset', [])) > 5:
                errors.append('Native case route correction')
        source_artifacts = research_doc.get('source_artifacts', [])
        if not source_artifacts:
            errors.append('Native research artifact registry missing')
        artifacts = {}
        fingerprints = {}
        candidates = {}
        for ref in source_artifacts:
            relative = ref.get('artifact_path')
            if not isinstance(relative, str) or not relative:
                errors.append('Native artifact path missing')
                continue
            artifact = (root / relative).resolve()
            if Path(relative).is_absolute() or not artifact.is_relative_to(root.resolve()):
                errors.append('Native artifact outside KB: ' + relative)
                continue
            fingerprint = ref.get('sha256')
            if not isinstance(fingerprint, str) or not re.fullmatch('[a-f0-9]{64}', fingerprint):
                errors.append('Native artifact fingerprint missing: ' + relative)
                continue
            if not artifact.is_file() or sha256(artifact.read_bytes()).hexdigest() != fingerprint:
                errors.append('Native artifact hash: ' + relative)
                continue
            if relative in artifacts:
                errors.append('Native duplicate artifact: ' + relative)
            if 'bytes' in ref and (type(ref['bytes']) is not int or ref['bytes'] != artifact.stat().st_size):
                errors.append('Native artifact bytes: ' + relative)
            payload = json.loads(artifact.read_text(encoding='utf-8')) if artifact.suffix == '.json' else artifact.read_text(encoding='utf-8')
            artifacts[relative] = payload
            fingerprints[relative] = fingerprint
            if isinstance(payload, (dict, list)):
                for value in walk(payload):
                    candidate_id = value.get('candidate_id')
                    if candidate_id and str(candidate_id).startswith('NC-') and ('statement' in value or 'classification' in value):
                        candidates.setdefault(candidate_id, value)
        for entry in entries:
            entry_id = entry['id']
            if entry.get('evidence_strength') != EVIDENCE:
                errors.append('Native mixed evidence promotion: ' + entry_id)
            if entry['native_fact'].get('claim_type') != 'NSF' or entry['recommended_reasoning'].get('claim_type') != 'REC':
                errors.append('Native fact/recommendation boundary: ' + entry_id)
            row = research.get(entry_id, {})
            candidate_ids = row.get('research_candidate_ids', [])
            if not candidate_ids or len(candidate_ids) != len(set(candidate_ids)) or any(candidate_id not in candidates for candidate_id in candidate_ids):
                errors.append('Native research candidate coverage: ' + entry_id)
            direct_support = row.get('direct_native_fact_support', [])
            if not direct_support or any(candidate_id not in candidate_ids or candidates.get(candidate_id, {}).get('classification') != 'NSF' for candidate_id in direct_support):
                errors.append('Native direct fact support must remain NSF: ' + entry_id)
            for candidate_id in row.get('engineering_inference_support', []):
                if candidate_id not in candidate_ids or candidates.get(candidate_id, {}).get('classification') != 'EI':
                    errors.append('Native inference support must remain EI: ' + entry_id)
            if entry.get('research_evidence_refs') != [entry_id]:
                errors.append('Native research evidence reference: ' + entry_id)
            if set(entry.get('related_native_facts', [])) != {edge['target'] for edge in entry.get('typed_relations', [])}:
                errors.append('Native typed relations mismatch: ' + entry_id)
            runtime = row.get('runtime_status', {})
            if runtime.get('new_runtime_runs') != 0 or runtime.get('whole_entry_runtime_verified') is not False:
                errors.append('Native whole-entry runtime promotion: ' + entry_id)
            locators = row.get('source_locators', [])
            if not isinstance(locators, list) or not locators:
                errors.append('Native source locators missing: ' + entry_id)
                continue
            for locator in locators + row.get('clarification_support', []):
                relative = locator.get('artifact_path', locator.get('source_file'))
                if relative not in artifacts or not isinstance(artifacts[relative], (dict, list)):
                    errors.append('Native locator artifact missing: ' + entry_id)
                    continue
                if locator.get('artifact_sha256') != fingerprints[relative]:
                    errors.append('Native locator fingerprint mismatch: ' + entry_id)
                try:
                    located = pointer(artifacts[relative], locator.get('source_pointer'))
                except (ValueError, KeyError, TypeError, IndexError):
                    errors.append('Native unresolved pointer: ' + entry_id)
                    continue
                candidate_id = locator.get('candidate_id')
                if candidate_id and (candidate_id not in candidates or not isinstance(located, dict) or located.get('candidate_id') != candidate_id):
                    errors.append('Native locator candidate mismatch: ' + entry_id)
                for evidence in locator.get('evidence_locators', locator.get('native_locators', [])):
                    fingerprint = evidence.get('file_sha256', evidence.get('sha256'))
                    anchor = evidence.get('anchor') or evidence.get('supporting_locator', {}).get('anchor')
                    if not all(evidence.get(key) for key in ('snapshot_id', 'file', 'symbol')) or not anchor or not isinstance(fingerprint, str) or not re.fullmatch('[a-f0-9]{64}', fingerprint):
                        errors.append('Native historical locator incomplete: ' + entry_id)
            for record in row.get('runtime_evidence_records', []):
                relative = record.get('artifact_path', record.get('source_file'))
                reference = record.get('source_pointer')
                if relative not in artifacts or record.get('artifact_sha256') != fingerprints.get(relative):
                    errors.append('Native scoped runtime artifact mismatch: ' + entry_id)
                    continue
                try:
                    if isinstance(artifacts[relative], str):
                        match = re.fullmatch(r'#L([1-9][0-9]*)', reference or '')
                        if not match or int(match.group(1)) > len(artifacts[relative].splitlines()):
                            raise ValueError('text line reference')
                    else:
                        pointer(artifacts[relative], reference)
                except (ValueError, KeyError, TypeError, IndexError):
                    errors.append('Native scoped runtime pointer: ' + entry_id)
                if record.get('new_runtime_execution') is True:
                    errors.append('Native scoped runtime must be historical: ' + entry_id)
                if record.get('claim_type') not in ('RV_OBSERVATION', 'RV_OBSERVATION_SYNTHESIS') or record.get('source_kind') != record.get('claim_type') or not record.get('scope') or record.get('runtime_status') not in ('CONFIRMED', 'HISTORICAL_CONFIRMED_NARROW'):
                    errors.append('Native scoped runtime classification: ' + entry_id)
                if '/linked-history/' not in relative:
                    errors.append('Native Pilot/candidate artifact cannot become RV: ' + entry_id)
            for key in ('pilot_promoted_to_rv', 'pilot_is_runtime_evidence', 'evaluation_is_runtime_evidence'):
                if any(value.get(key) is True for value in walk(documents[FILES[2]])):
                    errors.append('Native Pilot -> RV promotion')
        core13 = byid.get(IDS[-1], {})
        if core13.get('knowledge_role') != 'BOUNDARY_GUARDRAIL' or core13.get('coverage_status') != 'PARTIAL / BRIDGE_ONLY':
            errors.append('Native CORE13 boundary role/coverage')
        evaluation = documents[FILES[2]]
        for key, expected in {'evaluation_kind': 'MICRO_EVAL_PILOT', 'per_entry_causal_effect': 'NOT_ESTABLISHED',
                              'evaluation_is_runtime_evidence': False, 'runtime_runs_in_pilot': 0,
                              'autonomous_retrieval_validated': False}.items():
            if evaluation.get(key) != expected:
                errors.append('Native evaluation boundary: ' + key)
        track = documents[FILES[4]]
        for key, expected in {'track_id': 'NATIVE-001', 'research_status': 'CLOSED', 'ai_knowledge_status': 'CANONICAL',
                              'autonomous_retrieval_status': 'NOT_VALIDATED', 'canonical_entry_count': 13,
                              'special_lifecycle_coverage': 'PARTIAL / BRIDGE_ONLY'}.items():
            if track.get(key) != expected:
                errors.append('Native track status: ' + key)
        test_status = documents[FILES[5]]
        for key, expected in {'test_id': 'T-P0-02', 'execution_history': 'BLOCKED / PRE-FLIGHT FAILED',
                              'campaign_decision': 'CLOSED_BY_ROI', 'history_rewritten_to_PASS': False,
                              'pass03_started': False}.items():
            if test_status.get(key) != expected:
                errors.append('Native historical test status: ' + key)
        for document, key in [(evaluation, 'evidence_refs'), (test_status, 'source_refs')]:
            if any(relative not in artifacts for relative in document.get(key, [])):
                errors.append('Native metadata artifact reference: ' + key)
        if errors:
            raise KBError('CORRUPTED_KB', '; '.join(dict.fromkeys(errors))[:3000])
        return {'primary': primary, 'entries': entries, 'research': research, 'routing': routing,
                'documents': documents, 'artifacts': source_artifacts}, {
            'present': True, 'status': 'PASS', 'schema_version': SCHEMA, 'version': primary['version'],
            'entries': 13, 'source_artifacts_checked': len(artifacts), 'new_runtime_runs': 0,
            'effect_on_AI_quality': EVIDENCE['effect_on_AI_quality'], 'runtime_validation_performed': False}
    except KBError:
        raise
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        raise KBError('CORRUPTED_KB', 'Native sidecar: ' + str(exc)) from exc

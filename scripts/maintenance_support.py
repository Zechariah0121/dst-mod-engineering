"""Author maintenance and independent candidates bound to explicit review."""
import copy
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import sys
import os
import tempfile
import uuid
import zipfile

CORE = 'data/nativecore/native-core.json'
ORIGINS = 'PUBLICATION-ORIGIN-MAP.json'
GATE_A_ORIGINAL = '/gate_a/original_fact_statement_preserved'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def child(root, relative):
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Author document escaped knowledge root')
    return target


def verify_source_slots(recipe, original, updated, paths):
    documents = {name: (json.loads(original[name]), json.loads(updated[name])) for name in paths}
    count = 0
    for slot in recipe['slots']:
        if slot['path'] not in documents:
            continue
        old_value, new_value = documents[slot['path']]
        for part in slot['pointer'].split('/')[1:]:
            part = part.replace('~1', '/').replace('~0', '~')
            old_value = old_value[int(part)] if isinstance(old_value, list) else old_value[part]
            new_value = new_value[int(part)] if isinstance(new_value, list) else new_value[part]
        if old_value != new_value:
            raise ValueError('Maintenance would change a source payload slot')
        count += 1
    return count


def records(knowledge, registry):
    result = {}
    for family in registry['families']:
        for document in family['documents']:
            entries = read(child(knowledge, document['file']))['entries']
            if [r['id'] for r in entries] != document['entry_ids']:
                raise ValueError('Author ID membership/order changed; use explicit registration: ' + document['file'])
            for i, record in enumerate(entries):
                if record['id'] in result:
                    raise ValueError('Duplicate author ID: ' + record['id'])
                result[record['id']] = {'record': record, 'family': family['name'],
                                        'file': document['file'], 'pointer': '/entries/' + str(i)}
    return result


def differences(old, new, pointer=''):
    if type(old) is not type(new):
        return [pointer or '/']
    if isinstance(old, dict) and isinstance(new, dict):
        result = []
        for key in sorted(set(old) | set(new)):
            path = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
            result.extend(differences(old[key], new[key], path) if key in old and key in new else [path])
        return result
    if isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        return [p for i, (before, after) in enumerate(zip(old, new))
                for p in differences(before, after, pointer + '/' + str(i))]
    return [] if old == new else [pointer or '/']


def intersects(left, right):
    return left == right or left.startswith(right + '/') or right.startswith(left + '/') or '/' in (left, right)


def pending_review(before, after, contract, identity):
    result = []
    old_digest = {digest(row['record']): key for key, row in before.items()}
    for identifier in sorted(set(before) | set(after)):
        old = before.get(identifier, {}).get('record')
        new = after.get(identifier, {}).get('record')
        changed = differences(old, new)
        if not changed:
            continue
        # Only title changes are known to be outside technical assertions. Other
        # edits stay pending even if an author describes them as a typo fix.
        technical = any(path != '/title' for path in changed)
        dependencies = []
        entry = contract.get('records', {}).get(identifier, {})
        for symbol, spec in entry.get('contracts', {}).items():
            for field in ('record_pointers', 'availability_record_pointers'):
                for pointer in spec.get(field, []):
                    if not technical or any(intersects(pointer, path) for path in changed) or any(
                            path.startswith(('/scope', '/knowledge_status', '/retrieval_status', '/coding_status')) for path in changed):
                        dependencies.append({'artifact': 'contract_map.json', 'record_id': identifier,
                            'symbol': symbol, 'atom': pointer, 'field': field,
                            'dependent_fields': ['pointer_roles', 'source_bindings', 'facet_scopes', 'claim_reference_bindings'],
                            'role': spec.get('pointer_roles', {}).get(pointer)})
        for i, row in enumerate(identity.get('bindings', [])):
            if old_digest.get(row.get('record_sha256')) == identifier and (
                    not technical or any(intersects(row['record_pointer'], p) for p in changed) or
                    any(p.startswith('/scope') for p in changed)):
                dependencies.append({'artifact': 'source_identity_map.json', 'pointer': '/bindings/' + str(i),
                                     'atom': row['record_pointer'], 'declared_symbol': row.get('declared_symbol'),
                                     'reference': row.get('reference')})
        for source_file, group in contract.get('owner_registry', {}).items():
            for basis in group.get('basis', []):
                if basis.get('id') == identifier:
                    dependencies.append({'artifact': 'contract_map.json', 'field': 'owner_registry',
                                         'source_file': source_file, 'basis': basis})
        result.append({'id': identifier, 'changed_pointers': changed,
            'change_class': 'TECHNICAL_REVIEW_REQUIRED' if technical else 'TITLE_ONLY',
            'old_record_sha256': digest(old), 'new_record_sha256': digest(new),
            'technical_semantics_approved': False,
            'dependencies': dependencies if technical else [],
            'record_fingerprint_dependents': ['FAMILY-REGISTRY.json', 'contract_map.json', 'source_identity_map.json'],
            'registration_review': 'Exact candidate/review binding must be renewed' if after.get(identifier, {}).get('family') == 'native_mechanism' else None})
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def select(document, pointer):
    """Resolve a canonical JSON Pointer from review or committed package data."""
    if pointer == '':
        return document
    require(isinstance(pointer, str) and pointer.startswith('/') and not re.search(r'~(?![01])', pointer),
            'Invalid review JSON pointer')
    for token in pointer[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(document, list):
            require(re.fullmatch(r'0|[1-9][0-9]*', token), 'Invalid review array index')
            document = document[int(token)]
        else:
            document = document[token]
    return document


def referenced_node(reference, inputs):
    name = 'knowledge/' + reference['artifact_path']
    raw = inputs[name]
    require(hashlib.sha256(raw).hexdigest() == reference['sha256'],
            'Reviewed evidence artifact no longer matches its commitment')
    return select(json.loads(raw), reference['pointer'].removeprefix('#'))


def validate_technical_change(before, after, pending, decision):
    """Match one manually reviewed, statement-only Core NSF correction."""
    fields = {'schema', 'decision', 'reviewer', 'rationale', 'record_id', 'claim_pointer',
              'old_record_sha256', 'new_record_sha256', 'gate_a_original_fact_statement_preserved',
              'source', 'maps'}
    require(isinstance(decision, dict) and set(decision) == fields and
            decision['schema'] == 'dst-author-technical-stage-review/1' and
            decision['decision'] == 'APPROVE_ISOLATED_CANDIDATE' and
            all(isinstance(decision[key], str) and decision[key].strip() for key in ('reviewer', 'rationale')),
            'An explicit human technical review with reviewer and rationale is required')
    identifier = decision['record_id']
    atom = decision['claim_pointer']
    require(isinstance(atom, str) and re.fullmatch(r'/claims/(0|[1-9][0-9]*)', atom) and
            len(pending) == 1 and pending[0]['id'] == identifier and
            pending[0]['change_class'] == 'TECHNICAL_REVIEW_REQUIRED' and
            before[identifier]['family'] == after[identifier]['family'] == 'native_core' and
            before[identifier]['file'] == after[identifier]['file'] == CORE,
            'Reviewed technical staging requires exactly one existing Core NSF claim')
    old, new = before[identifier]['record'], after[identifier]['record']
    require(digest(old) == decision['old_record_sha256'] and digest(new) == decision['new_record_sha256'],
            'Reviewed old/new record fingerprints do not match')
    old_claim, new_claim = select(old, atom), select(new, atom)
    gate = decision['gate_a_original_fact_statement_preserved']
    expected = {atom + '/statement'}
    if gate is not None:
        require(gate == {'before': True, 'after': False} and gate['before'] is True and gate['after'] is False and
                select(old, GATE_A_ORIGINAL) is True and select(new, GATE_A_ORIGINAL) is False,
                'Gate A permits only an explicitly reviewed true-to-false change')
        expected.add(GATE_A_ORIGINAL)
    require(old.get('gate_a', {}).get('accepted') is True and
            new['gate_a'].get('original_fact_statement_preserved') is False and
            old_claim['kind'] == new_claim['kind'] == 'NSF' and
            isinstance(new_claim['statement'], str) and new_claim['statement'].strip() and
            set(differences(old, new)) == expected,
            'Only the reviewed NSF statement and explicit Gate A correction may change')
    return identifier, atom


def locator_details(value):
    return {key: value.get(key) for key in ('path', 'file_sha256', 'range_sha256', 'line_start', 'line_end')}


def cited_locators(value):
    if isinstance(value, dict):
        locator = locator_details(value)
        if all(item is not None for item in locator.values()):
            yield locator
        for item in value.values():
            yield from cited_locators(item)
    elif isinstance(value, list):
        for item in value:
            yield from cited_locators(item)


def verify_review_source(inputs, source, archive, claim):
    require(isinstance(source, dict) and set(source) == {'archive_sha256', 'reference', 'range'} and
            source['reference'] in claim['evidence_refs'], 'Reviewed source must be an existing claim-owned reference')
    locator = source['range']
    original = referenced_node(source['reference'], inputs)
    require(isinstance(locator, dict) and isinstance(original, dict) and locator == locator_details(original),
            'Reviewed source range does not equal its committed historical locator')
    require(all(cited == locator for ref in claim['evidence_refs']
                for cited in cited_locators(referenced_node(ref, inputs))),
            'Additional claim source range requires separate review')
    name, start, end = locator['path'], locator['line_start'], locator['line_end']
    require(isinstance(name, str) and re.fullmatch(r'scripts/(?:[A-Za-z0-9_]+[A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\.lua', name) and
            type(start) is int and type(end) is int and 1 <= start <= end and
            original.get('hash_convention', 'LF_JOIN_WITHOUT_TRAILING_NEWLINE') == 'LF_JOIN_WITHOUT_TRAILING_NEWLINE',
            'Reviewed source range must be one exact historical LF Lua citation')
    epochs = json.loads(inputs['source-epochs.json'])
    known = [row.get('archive_sha256') for row in epochs.get('source_input_targets', [])]
    known.extend(epoch.get('source_environment_identity', {}).get('archive_sha256') for epoch in epochs['epochs'].values())
    require(source['archive_sha256'] in known, 'Reviewed source archive is absent from package source commitments')
    raw_zip = Path(archive).read_bytes()
    archive_sha = hashlib.sha256(raw_zip).hexdigest()
    require(archive_sha == source['archive_sha256'], 'Reviewed source ZIP SHA-256 does not match actual ZIP')
    # Use the same immutable bytes for the outer fingerprint and member read.
    with zipfile.ZipFile(BytesIO(raw_zip)) as source_zip:
        members = [info for info in source_zip.infolist() if info.filename == name and not info.is_dir()]
        require(len(members) == 1, 'Reviewed source ZIP member is absent or ambiguous')
        raw = source_zip.read(members[0])
    lines = raw.decode('utf-8').splitlines()
    require(end <= len(lines), 'Reviewed source coordinates fall outside the actual Lua member')
    text = '\n'.join(lines[start - 1:end])
    require(hashlib.sha256(text.encode()).hexdigest() == locator['range_sha256'],
            'Reviewed Lua range differs at its exact coordinates')
    return text, {'archive_sha256': archive_sha, 'member_sha256': hashlib.sha256(raw).hexdigest(),
                  'reference': source['reference'], 'range': locator}


def contains_exact(value, needle):
    if isinstance(value, dict):
        return needle in value or any(contains_exact(item, needle) for item in value.values())
    if isinstance(value, list):
        return any(contains_exact(item, needle) for item in value)
    return value == needle


def review_technical_maps(root, inputs, decision, old, new, atom, source_text):
    """Check both maps independently and prepare explicit, narrow metadata updates."""
    identifier = old['id']
    old_hash = decision['old_record_sha256']
    claim, updated = select(old, atom), select(new, atom)
    locator = decision['source']['range']
    profiles = json.loads(inputs['dst-kb-service/dst_kb/projection_profiles.json'])
    ledger = json.loads(inputs['knowledge/data/source-epoch-coverage.json'])
    require(not any(contains_exact(document, identifier) or contains_exact(document, old_hash)
                    for document in (profiles, ledger)),
            'Projection profile or source-epoch coverage dependency requires separate review')
    epochs = json.loads(inputs['source-epochs.json'])
    map_pairs = {(e['contract_map']['path'], e['source_identity_map']['path']) for e in epochs['epochs'].values()}
    map_pairs.add(('dst-kb-service/dst_kb/contract_map.json', 'dst-kb-service/dst_kb/source_identity_map.json'))
    require(len(map_pairs) == 2 and {p for pair in map_pairs for p in pair} ==
            {name for name in inputs if name.endswith(('/contract_map.json', '/source_identity_map.json'))},
            'Review requires the complete service and epoch map namespaces')
    reviews = decision['maps']
    require(isinstance(reviews, dict) and set(reviews) == {contract for contract, _ in map_pairs},
            'Technical review must explicitly cover both map namespaces')
    service = str(root / 'dst-kb-service')
    sys.path.insert(0, service)
    try:
        from dst_kb.facet_contracts import statement_binding
    finally:
        sys.path.remove(service)

    changes, proofs = {}, []
    for contract_name, identity_name in sorted(map_pairs):
        review = reviews[contract_name]
        require(isinstance(review, dict) and set(review) == {'contract_sha256', 'contract_symbol', 'contract_spec_sha256',
                'identity_path', 'identity_sha256', 'identity_rows'} and review['identity_path'] == identity_name and
                review['contract_sha256'] == hashlib.sha256(inputs[contract_name]).hexdigest() and
                review['identity_sha256'] == hashlib.sha256(inputs[identity_name]).hexdigest(),
                'Reviewed map paths or file fingerprints differ: ' + contract_name)
        contract = json.loads(inputs[contract_name])
        entry = contract['records'][identifier]
        related = {symbol: spec for symbol, spec in entry['contracts'].items()
                   if atom in spec.get('record_pointers', []) + spec.get('availability_record_pointers', [])}
        symbol = review['contract_symbol']
        require(set(related) == {symbol}, 'Technical review supports one existing direct method contract per changed atom')
        spec = related[symbol]
        require(digest(spec) == review['contract_spec_sha256'] and entry['record_sha256'] == old_hash and
                entry['original_scope'] == old['scope'] and entry['claim_reference_bindings'][atom] == claim['evidence_refs'] and
                spec['record_pointers'] == [atom] and not spec['availability_record_pointers'] and
                spec['pointer_roles'][atom]['role'] == 'METHOD_SUBJECT' and atom not in entry['facet_scopes'],
                'Reviewed method contract, role, references or scope differs')
        require(not any(contains_exact(contract[key], identifier) or contains_exact(contract[key], old_hash)
                        for key in ('owner_registry', 'sample_rules')) and
                not any(contains_exact(value, old_hash) for key, value in contract['records'].items() if key != identifier) and
                not contains_exact({key: value for key, value in entry.items() if key != 'record_sha256'}, old_hash),
                'Additional owner, sample or cross-record contract dependency requires separate review')
        bindings = spec['source_bindings'][atom]
        require(bindings, 'Reviewed method has no committed source bindings')
        seen_refs = []
        for binding in bindings:
            ref = {key: binding[key] for key in ('artifact_path', 'sha256', 'pointer')}
            require(ref in claim['evidence_refs'] and binding['original_reference_precision'] == 'SINGLE_SOURCE_LOCATOR_NODE' and
                    binding['original_reference_locator_count'] == 1 and locator_details(binding['source_locator']) == locator and
                    binding['original_source_value_sha256'] == digest(referenced_node(ref, inputs)),
                    'Method contract must retain one exact cited range and its committed evidence nodes')
            seen_refs.append(ref)
        require(decision['source']['reference'] in seen_refs,
                'Reviewed source reference is not directly bound to the method contract')
        old_role = statement_binding(claim['statement'], symbol, allow_bare=True, source_callable=True)
        new_role = statement_binding(updated['statement'], symbol, allow_bare=True, source_callable=True)
        require(old_role == new_role and old_role is not None and old_role['role'] == 'METHOD_SUBJECT',
                'Revised statement does not preserve the existing method subject')
        spec['mapping_basis'] = 'EXPLICIT_FROZEN_TYPED_CLAIM'
        changes[contract_name] = contract

        identity = json.loads(inputs[identity_name])
        require(not contains_exact({k: v for k, v in identity.items() if k != 'bindings'}, old_hash),
                'Additional identity dependency requires separate review')
        reviewed_rows = {}
        for index, row in enumerate(identity['bindings']):
            if row['record_sha256'] != old_hash or row['record_pointer'] != atom:
                continue
            node = referenced_node(row['reference'], inputs)
            line = row['declaration_line']
            require(type(line) is int and locator['line_start'] <= line <= locator['line_end'],
                    'Reviewed declaration lies outside the cited Lua range')
            header = source_text.split('\n')[line - locator['line_start']]
            require(row['schema'] == 'accepted-source-declaration-identity/1' and row.get('proof_kind') is None and
                    row['declared_symbol'] == symbol and row['reference'] in seen_refs and
                    locator_details(node) == locator and digest(node) == row['artifact_value_sha256'] and
                    row['range_hash_mode'] == 'LF_JOIN_NO_FINAL_NEWLINE' and row['cited_range_sha256'] == locator['range_sha256'] and
                    header == row['declaration_header'] and hashlib.sha256(header.encode()).hexdigest() == row['declaration_header_sha256'] and
                    row['identity_is_behavior_proof'] is False and row['runtime_verified'] is False,
                    'Technical review supports only exact existing declaration bindings in the cited Lua range')
            reviewed_rows['/bindings/' + str(index)] = digest(row)
        require(reviewed_rows and reviewed_rows == review['identity_rows'],
                'Reviewed identity rows differ from the complete affected set: ' + identity_name)
        changes[identity_name] = identity
        proofs.append({'contract_map': contract_name, 'identity_map': identity_name,
                       'symbol': symbol, 'claim_pointer': atom, 'role': 'METHOD_SUBJECT',
                       'contract_source_bindings': len(bindings), 'reviewed_identity_rows': reviewed_rows})
    return changes, proofs


def historical(root, baseline, knowledge, generators, output, contract_path, identity_path):
    # Import current runtime modules before loading history, whose old scripts
    # prepend their candidate service path. The generator code itself is intact.
    sys.path.insert(0, str(root / 'dst-kb-service'))
    from dst_kb import facet_contracts, nativecore  # noqa: F401
    mapper = load_module('_author_historical_map', generators / 'build_map_v24.py')
    mapper.KB = knowledge
    seed, rebase = mapper.rebase_contract_map(read(contract_path), baseline)
    catalog = mapper.contracts._catalog
    mapper.contracts._catalog = lambda: seed
    try:
        candidate, audit = mapper.build(copy.deepcopy(seed))
        candidate = mapper.preserve_verified_old_atoms(candidate, seed)
    finally:
        mapper.contracts._catalog = catalog
    candidate['knowledge_commitments'] = {relative: hashlib.sha256((knowledge / relative).read_bytes()).hexdigest()
        for relative in ('data/entries.json', 'data/native001/canonical-native001-ai-knowledge.json', 'data/nativecore/native-core.json')}
    write(output / 'candidates/contract_map.json', candidate)
    identity_builder = load_module('_author_historical_identity', generators / 'build_source_identity.py')
    identity, identity_report = identity_builder.rebase_identity(knowledge, baseline, identity_path)
    original_core = read(baseline / 'data/nativecore/native-core.json')['entries']
    original_by_digest = {digest(record): record for record in original_core}
    new_by_id = {record['id']: record for record in read(knowledge / 'data/nativecore/native-core.json')['entries']}
    rejected_keys = {(row['record_id'], row['record_pointer']) for row in identity_report['dropped_changed_rows']}
    exact_rejections = []
    for index, row in enumerate(read(identity_path)['bindings']):
        original = original_by_digest.get(row['record_sha256'])
        if original is None or (original['id'], row['record_pointer']) not in rejected_keys:
            continue
        try:
            old_claim = identity_builder.at(original, row['record_pointer'])
            new_claim = identity_builder.at(new_by_id[original['id']], row['record_pointer'])
        except (KeyError, IndexError, TypeError):
            old_claim, new_claim = None, None
        checks = {'whole_claim_equal': old_claim is not None and old_claim == new_claim,
                  'statement_sha256_matches': old_claim is not None and row['statement_sha256'] == digest(old_claim.get('statement')),
                  'reference_is_claim_owned': old_claim is not None and row['reference'] in old_claim.get('evidence_refs', [])}
        if not all(checks.values()):
            exact_rejections.append({'record_id': original['id'], 'record_pointer': row['record_pointer'],
                'binding_pointer': '/bindings/' + str(index), 'declared_symbol': row.get('declared_symbol'),
                'reference': row.get('reference'), 'checks': checks,
                'reason': 'ORIGINAL_CLAIM_KIND_STATEMENT_OR_REFERENCES_CHANGED'})
    identity_report['dropped_changed_rows'] = exact_rejections
    write(output / 'candidates/source_identity_map.json', identity)
    report = {'generator_sha256': {name: hashlib.sha256((generators / name).read_bytes()).hexdigest()
                                  for name in ('build_map_v24.py', 'build_source_identity.py')},
        'contract_map': {'original_catalog_records': audit['original_catalog_records'],
                         'before': audit['before']['nsf_pointer_status_counts'],
                         'after_grammar_audit': audit['after']['nsf_pointer_status_counts'], **rebase},
        'identity': identity_report,
        'published_comparison': {'contract_structurally_equal': candidate == read(contract_path),
                                 'identity_structurally_equal': identity == read(identity_path)},
        'candidate_is_release_ready': False, 'behavior_verified': False,
        'scope': 'Historical three-family map grammar plus unchanged-atom preservation; identity preserves only unchanged cited claims. No declaration extraction without explicit original source bytes.'}
    write(output / 'historical-receipt.json', report)
    return report


def stage_title_candidate(root, knowledge, output, destination, before, after, pending):
    """Stage proven Core title edits through the shared candidate builder."""
    if not pending or any(row['change_class'] != 'TITLE_ONLY' or after[row['id']]['family'] != 'native_core' for row in pending):
        raise ValueError('Candidate staging supports only Core TITLE_ONLY edits; technical/other-family changes require review')
    for row in pending:
        identifier = row['id']
        old, new = before[identifier]['record'], after[identifier]['record']
        if {k: v for k, v in old.items() if k != 'title'} != {k: v for k, v in new.items() if k != 'title'}:
            raise ValueError('Whole non-title record proof failed: ' + identifier)
    return stage_candidate_package(root, knowledge, output, destination, before, after, pending)


def stage_candidate_package(root, knowledge, output, destination, before, after, pending, decision=None, archive=None):
    destination = Path(destination).resolve()
    if destination.exists() or any(destination.is_relative_to(p) for p in (root, knowledge, output)):
        raise ValueError('Candidate must be a new external directory')
    builder = load_module('_author_release_builder', root / 'scripts/build_release.py')
    inputs = builder.source_files(root)
    decode = load_module('_author_stage_families', root / 'dst-kb-service/dst_kb/family_registry.py').decode
    original_core = decode(inputs['knowledge/' + CORE])
    edited_core_raw = (knowledge / CORE).read_bytes()
    edited_core = decode(edited_core_raw)
    require(not differences({k: v for k, v in original_core.items() if k != 'entries'},
                            {k: v for k, v in edited_core.items() if k != 'entries'}) and
            not differences(original_core['entries'], [row['record'] for row in before.values() if row['file'] == CORE]) and
            not differences(edited_core['entries'], [row['record'] for row in after.values() if row['file'] == CORE]),
            'Candidate package or edited Core differs from the explicit maintenance inputs')
    technical = None
    prepared_maps = {}
    if decision is not None:
        identifier, atom = validate_technical_change(before, after, pending, decision)
        old, new = before[identifier]['record'], after[identifier]['record']
        text, source_proof = verify_review_source(inputs, decision['source'], archive, select(old, atom))
        prepared_maps, dependencies = review_technical_maps(root, inputs, decision, old, new, atom, text)
        epochs = json.loads(inputs['source-epochs.json'])
        active_map = epochs['epochs'][epochs['default_source_epoch']]['source_identity_map']['path']
        approved_gaps = next(row['reviewed_identity_rows'] for row in dependencies if row['identity_map'] == active_map)
        require(all(gap.get('record_id') == identifier and gap.get('record_pointer') == atom and
                    gap.get('binding_pointer') in approved_gaps
                    for gap in read(output / 'pending-review.json')['generator_gaps']),
                'Historical generation found unreviewed dependencies')
        technical = {'decision': decision, 'canonical_decision_sha256': digest(decision),
                     'source': source_proof, 'reviewed_dependencies': dependencies}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='author-stage-', dir=destination.parent) as staging:
        stage = Path(staging) / 'package'
        receipt = write_candidate_package(builder, inputs, edited_core_raw, output, stage, before, after, pending,
                                          technical, prepared_maps)
        require(not destination.exists(), 'Candidate destination appeared during staging')
        os.rename(stage, destination)
    receipt['candidate_root'] = str(destination)
    write(output / 'staged-candidate.json', receipt)
    return receipt


def write_candidate_package(builder, inputs, edited_core_raw, output, destination, before, after, pending,
                            technical, prepared_maps):
    """Write and validate an isolated package using only builder-owned files."""
    changes = {row['id']: row for row in pending}
    for name, raw in inputs.items():
        target = child(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (destination / 'knowledge' / CORE).write_bytes(edited_core_raw)
    catalog = (output / 'derived/CATALOG.json').read_bytes()
    if technical:
        require(not differences(json.loads(catalog), json.loads(inputs['knowledge/CATALOG.json'])),
                'Technical statement correction may not change catalog entries')
    else:
        (destination / 'knowledge/CATALOG.json').write_bytes(catalog)
    registry = read(destination / 'knowledge/FAMILY-REGISTRY.json')
    new_core_hash = hashlib.sha256(edited_core_raw).hexdigest()
    for group in registry['families']:
        if group['name'] == 'native_core':
            for document in group['documents']:
                require(document['file'] == CORE, 'Unexpected Core registration document')
                document['sha256'] = new_core_hash
                for identifier in changes:
                    document['record_sha256'][identifier] = changes[identifier]['new_record_sha256']
                # published_record_sha256 remains exact original provenance.
    write(destination / 'knowledge/FAMILY-REGISTRY.json', registry)
    map_proofs = []
    for name in inputs:
        if not name.endswith(('/contract_map.json', '/source_identity_map.json')):
            continue
        document = prepared_maps[name] if technical else read(destination / name)
        if name.endswith('/contract_map.json'):
            for identifier, change in changes.items():
                entry = document['records'][identifier]
                if entry['record_sha256'] != change['old_record_sha256']:
                    raise ValueError('Contract baseline identity mismatch: ' + name)
                entry['record_sha256'] = change['new_record_sha256']
            document['knowledge_commitments'][CORE] = new_core_hash
        else:
            rebound = 0
            for row in document['bindings']:
                for identifier, change in changes.items():
                    if row['record_sha256'] != change['old_record_sha256']:
                        continue
                    claim = select(before[identifier]['record'], row['record_pointer'])
                    require(row['statement_sha256'] == digest(claim.get('statement')) and
                            row['claim_kind'] == claim.get('kind') and row['reference'] in claim.get('evidence_refs', []),
                            'Changed record has an unproven identity row: ' + identifier)
                    if technical:
                        require(row['artifact_value_sha256'] == digest(referenced_node(row['reference'], inputs)),
                                'Rebased identity row evidence no longer matches its commitment')
                        decision = technical['decision']
                        if row['record_pointer'] == decision['claim_pointer']:
                            row['statement_sha256'] = digest(select(after[identifier]['record'],
                                                                    decision['claim_pointer'] + '/statement'))
                        else:
                            rebound += 1
                    row['record_sha256'] = change['new_record_sha256']
            document['canonical_sha256'] = new_core_hash
            if technical:
                proof = next(row for row in technical['reviewed_dependencies'] if row['identity_map'] == name)
                proof.update(unchanged_atom_identity_rows_rebound=rebound,
                             total_identity_rows=len(document['bindings']))
        write(destination / name, document)
        map_proofs.append({'path': name, 'technical_fields_preserved': technical is None})
    if technical:
        origins = read(destination / ORIGINS)
        for identifier, change in changes.items():
            history = origins['record_digest_history']['knowledge'][identifier]
            require(change['old_record_sha256'] in history and change['new_record_sha256'] not in history,
                    'Publication origin history differs from the reviewed baseline')
            history.append(change['new_record_sha256'])
        core_name = 'knowledge/' + CORE
        origin = next(row for row in origins['files'] if row['path'] == core_name)
        require(origin['public_sha256'] == hashlib.sha256(inputs[core_name]).hexdigest(),
                'Publication origin document differs from the reviewed baseline')
        origin['public_sha256'] = new_core_hash
        file_history = origins['previous_public_hashes'][core_name]
        if new_core_hash not in file_history:
            file_history.append(new_core_hash)
        write(destination / ORIGINS, origins)
    manifest = read(destination / 'knowledge/PACKAGE-MANIFEST.json')
    for row in manifest['files']:
        raw = (destination / 'knowledge' / row['path']).read_bytes()
        row.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    write(destination / 'knowledge/PACKAGE-MANIFEST.json', manifest)
    epochs = read(destination / 'source-epochs.json')
    for epoch in epochs['epochs'].values():
        for field in ('knowledge_manifest', 'contract_map', 'source_identity_map'):
            epoch[field]['sha256'] = hashlib.sha256(child(destination, epoch[field]['path']).read_bytes()).hexdigest()
    write(destination / 'source-epochs.json', epochs)
    candidate_inputs = builder.source_files(destination)
    changed_files = [name for name in inputs if candidate_inputs[name] != inputs[name]]
    # Source bytes, public payload-slot recipe, strict source manifests and
    # coverage evidence must remain exactly the existing package's bytes.
    allowed = {'knowledge/' + CORE, ORIGINS if technical else 'knowledge/CATALOG.json', 'knowledge/FAMILY-REGISTRY.json',
               'knowledge/PACKAGE-MANIFEST.json', 'source-epochs.json', *[row['path'] for row in map_proofs]}
    require(inputs.keys() == candidate_inputs.keys() and set(changed_files) <= allowed,
            'Candidate modified unreviewed package dependencies')
    recipe = json.loads(inputs['source-payload-recipe.json'])
    slot_paths = set(changed_files) & {slot['path'] for slot in recipe['slots']}
    slot_count = verify_source_slots(recipe, inputs, candidate_inputs, sorted(slot_paths))
    receipt = {'changed_files': changed_files, 'proofs': map_proofs,
        'all_non_title_record_fields_equal': technical is None,
        'source_slots_recipe_and_evidence_unchanged': True,
        'source_payload_slots_checked': slot_count, 'total_source_payload_slots': len(recipe['slots']),
        'inherited_identity_gaps_approved': False, 'ready_for_read_and_build_review': True,
        'release_approved': False}
    if technical:
        receipt['technical_review'] = technical
    return receipt


def repair_retired_private_identities(root, audit):
    """Explicit reviewed removal; never infer a replacement claim or source."""
    core = read(root / 'knowledge/data/nativecore/native-core.json')
    record = next(row for row in core['entries'] if row['id'] == 'NC-N003-INT-05')
    claim = record['claims'][16]
    if claim['kind'] != 'UNK' or not all(ref['artifact_path'] == 'research/publication/public-evidence-boundaries.json'
                                        and ref['pointer'] == '/private_context' for ref in claim['evidence_refs']):
        raise ValueError('Reviewed withheld claim no longer matches repair scope')
    names = ['dst-kb-service/dst_kb/source_identity_map.json', 'epoch-assets/759671/source_identity_map.json']
    original = {name: (root / name).read_bytes() for name in names + ['source-epochs.json']}
    updates, proofs = {}, []
    for name in names:
        document = json.loads(original[name])
        removed = [(i, row) for i, row in enumerate(document['bindings'])
                   if row['record_sha256'] == digest(record) and row['record_pointer'] == '/claims/16']
        if len(removed) not in (0, 5) or any(row['claim_kind'] != 'EI' or row['declared_symbol'] != 'StateGraphInstance:GoToState'
                or row['statement_sha256'] == digest(claim['statement']) or row['reference'] in claim['evidence_refs'] for _, row in removed):
            raise ValueError('Identity removal differs from reviewed five-row scope: ' + name)
        rejected = {i for i, _ in removed}
        kept = [row for i, row in enumerate(document['bindings']) if i not in rejected]
        document['bindings'] = kept
        updates[name] = (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        # Every remaining binding and every declaration/range value stays exact.
        if len(kept) != 5317:
            raise ValueError('Remaining identity count differs from reviewed baseline')
        proofs.append({'path': name, 'before_sha256': hashlib.sha256(original[name]).hexdigest(),
            'after_sha256': hashlib.sha256(updates[name]).hexdigest(), 'kept_rows': len(kept),
            'removed': [{'pointer': '/bindings/' + str(i), 'row_sha256': digest(row), 'row': row} for i, row in removed],
            'all_other_rows_and_ranges_unchanged': True})
    epochs = json.loads(original['source-epochs.json'])
    for epoch in epochs['epochs'].values():
        path = epoch['source_identity_map']['path']
        if path in updates:
            epoch['source_identity_map']['sha256'] = hashlib.sha256(updates[path]).hexdigest()
    updates['source-epochs.json'] = (json.dumps(epochs, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    slot_count = verify_source_slots(read(root / 'source-payload-recipe.json'), original, updates, names)
    for name, raw in original.items():
        target = audit / 'backups' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    applied = []
    try:
        for name, raw in updates.items():
            if (root / name).read_bytes() != original[name]:
                raise ValueError('Package changed during reviewed identity repair')
            temporary = (root / name).with_name('.' + Path(name).name + '.repair-' + uuid.uuid4().hex)
            temporary.write_bytes(raw)
            os.replace(temporary, root / name)
            applied.append(name)
    except BaseException:
        for name in reversed(applied):
            (root / name).write_bytes(original[name])
        raise
    report = {'review_decision': 'MAINT-IDENTITY-CLAIM16-01: explicitly authorized removal of retired private EI bindings',
        'private_claim_restored': False, 'replacement_binding_inferred': False, 'proofs': proofs,
        'source_payload_slots_unchanged': slot_count,
        'changed_paths': [name for name in updates if updates[name] != original[name]]}
    write(audit / 'repair-audit.json', report)
    return report


def rebuild(root, baseline, knowledge, output, generators=None, stage_candidate=None, repair_private=False,
            reviewed_technical_decision=None, source=None):
    root, baseline, knowledge, output = [Path(p).resolve() for p in (root, baseline, knowledge, output)]
    if reviewed_technical_decision or source:
        require(stage_candidate and reviewed_technical_decision and source and not repair_private,
                'Technical staging requires a decision, source ZIP and candidate path, separately from identity repair')
    if output.exists() or any(output.is_relative_to(p) for p in (root, baseline, knowledge)):
        raise ValueError('Output must be absent and outside all input roots')
    family = load_module('_author_families', root / 'dst-kb-service/dst_kb/family_registry.py')
    registry = family.load(baseline)
    before, after = records(baseline, registry), records(knowledge, registry)
    if set(before) != set(after):
        raise ValueError('Adding/removing IDs requires explicit registration; maintenance cannot infer membership')
    # This entry point handles bodies, not a hidden mutation of reviewed source
    # artifacts, source manifests, state registries or registration decisions.
    documents = {d['file'] for f in registry['families'] for d in f['documents']}
    for relative in documents:
        old_doc, new_doc = read(child(baseline, relative)), read(child(knowledge, relative))
        if differences({k: v for k, v in old_doc.items() if k != 'entries'},
                       {k: v for k, v in new_doc.items() if k != 'entries'}):
            raise ValueError('Non-entry metadata changed; explicit source/governance review required: ' + relative)
    for row in read(baseline / 'PACKAGE-MANIFEST.json')['files']:
        if row['path'] not in documents and hashlib.sha256(child(knowledge, row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Non-author artifact changed; explicit evidence/registration review required: ' + row['path'])
    epochs = read(root / 'source-epochs.json')
    epoch = epochs['epochs'][epochs['default_source_epoch']]
    contract_path = child(root, epoch['contract_map']['path'])
    identity_path = child(root, epoch['source_identity_map']['path'])
    contract, identity = read(contract_path), read(identity_path)
    pending = pending_review(before, after, contract, identity)
    output.mkdir(parents=True)
    if repair_private:
        repair_retired_private_identities(root, output / 'approved-identity-repair')
        identity = read(identity_path)
        pending = pending_review(before, after, contract, identity)
    for path in (contract_path, identity_path):
        (output / 'preserved').mkdir(exist_ok=True)
        shutil.copyfile(path, output / 'preserved' / path.name)
    # The registry's ID/document membership is authored input. Make transient
    # body commitments solely to call the established pure catalog generator.
    transient = copy.deepcopy(registry)
    for group in transient['families']:
        for doc in group['documents']:
            doc['sha256'] = hashlib.sha256(child(knowledge, doc['file']).read_bytes()).hexdigest()
    catalog = read(baseline / 'CATALOG.json')
    catalog['entries'] = family.catalog_rows(knowledge, transient)
    catalog['counts'] = family.counts(transient)
    write(output / 'derived/CATALOG.json', catalog)
    write(output / 'derived/author-record-index.json', {'schema': 'dst-author-body-index/1',
        'records': [{'id': key, **row, 'record_sha256': digest(row['record'])} for key, row in after.items()]})
    review = {'schema': 'dst-author-pending-review/1', 'changes': pending,
              'generator_gaps': [], 'release_blocked': bool(pending), 'runtime_verified': False}
    status = {'changed_records': len(pending), 'technical_review_records': sum(
        row['change_class'] == 'TECHNICAL_REVIEW_REQUIRED' for row in pending),
        'catalog_records': len(after), 'active_package_modified': bool(repair_private),
        'manual_artifacts_preserved': True, 'historical_generator_status': 'NOT_REQUESTED'}
    if generators:
        try:
            historical_report = historical(root, baseline, knowledge, Path(generators).resolve(), output, contract_path, identity_path)
            review['generator_gaps'] = [{'artifact': 'source_identity_map.json', **gap}
                for gap in historical_report['identity']['dropped_changed_rows']]
            review['release_blocked'] = bool(pending or review['generator_gaps'])
            status['historical_generator_status'] = 'CANDIDATE_BUILT'
        except Exception as exc:
            status['historical_generator_status'] = 'BLOCKED_REVIEW_REQUIRED'
            write(output / 'historical-error.json', {'type': type(exc).__name__, 'message': str(exc),
                                                      'old_maps_preserved': True})
            review['generator_gaps'] = [{'reason': str(exc), 'generator_failed': True}]
            review['release_blocked'] = True
    write(output / 'pending-review.json', review)
    if stage_candidate:
        try:
            if Path(stage_candidate).resolve().is_relative_to(baseline):
                raise ValueError('Candidate cannot be inside baseline')
            if reviewed_technical_decision:
                decision = family.decode(Path(reviewed_technical_decision).read_bytes())
                require(isinstance(decision, dict), 'Expected a technical review decision object')
                stage_candidate_package(root, knowledge, output, stage_candidate, before, after, pending, decision, source)
            else:
                stage_title_candidate(root, knowledge, output, stage_candidate, before, after, pending)
            status['candidate_stage_status'] = 'STAGED_FOR_REVIEW'
        except Exception as exc:
            status['candidate_stage_status'] = 'BLOCKED'
            write(output / 'candidate-stage-error.json', {'type': type(exc).__name__, 'message': str(exc)})
    write(output / 'maintenance-receipt.json', status)
    return status

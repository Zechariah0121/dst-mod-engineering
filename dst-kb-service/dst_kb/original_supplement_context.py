"""One-hop, same-record context from explicit, hash-checked original fact edges."""
import copy
import json
import re
from collections import OrderedDict
from hashlib import sha256
from pathlib import Path
from threading import RLock

from .facet_contracts import context_admission
from . import facet_contracts as facets
from .scope_navigation import ProofError, at, digest, ref_key, triple
from .task_relevance import task_support

SCHEMA = 'original-explicit-supplement-context/1'
ROLE = 'BOUNDED_ORIGINAL_SUPPLEMENT_CONTEXT'
_SEAL = object()
_KINDS = frozenset(('NSF', 'EI', 'REC', 'UNK'))
_ID = re.compile(r'[A-Za-z0-9_.:#/-]+')


def _fact_id(node):
    values = [node[key] for key in ('fact_id', 'evidence_id', 'atom_id') if key in node]
    if (not values or any(not isinstance(value, str) or not _ID.fullmatch(value) for value in values)
            or len(set(values)) != 1):
        raise ProofError('ORIGINAL_FACT_IDENTITY_AMBIGUOUS')
    return values[0]


def _kind(node):
    values = [node[key] for key in ('kind', 'claim_type') if node.get(key) in _KINDS]
    if node.get('classification') == 'DirectLuaSourceFact':
        values.append('NSF')
    if not values or len(set(values)) != 1:
        raise ProofError('ORIGINAL_FACT_KIND_UNPROVEN_OR_CONFLICTING')
    return values[0]


def _version(node, identity):
    for fields, expected in ((('snapshot_id', 'source_snapshot_id'), identity['snapshot_id']),
                             (('source_commit', 'commit'), identity['source_commit']),
                             (('source_repository', 'repository'), identity['source_repository'])):
        if any(node[key] != expected for key in fields if key in node):
            raise ProofError('ORIGINAL_SOURCE_VERSION_CONFLICT')


def _identity(record):
    scope = record.get('scope')
    fields = ('snapshot_id', 'source_commit', 'source_repository')
    if not isinstance(scope, dict) or not all(isinstance(scope.get(k), str) and scope[k] for k in fields):
        raise ProofError('ORIGINAL_RECORD_SCOPE_IDENTITY_UNPROVEN')
    return {key: scope[key] for key in fields}


class VerifiedSupplementContext:
    """A process capability; neither JSON proof flags nor an entry ID can create it."""
    __slots__ = ('_record_sha256', '_payload', '_seal', '_current')

    def __init__(self, record_sha256, payload, seal, current):
        if seal is not _SEAL:
            raise ProofError('UNVERIFIED_SUPPLEMENT_CONTEXT')
        self._record_sha256, self._payload, self._seal = record_sha256, copy.deepcopy(payload), seal
        self._current = current

    def render(self, record):
        if self._seal is not _SEAL or not self._current() or digest(record) != self._record_sha256:
            raise ProofError('SUPPLEMENT_RECORD_IDENTITY_CHANGED')
        return copy.deepcopy(self._payload)


class OriginalSupplementRegistry:
    """Content-keyed bounded memoization; current bytes are checked on every use.

    The manifest and epoch are immutable per registry. Replacing an accepted
    manifest requires a new registry. File times never authorize cached facts.
    """
    def __init__(self, root, registered_artifacts, epoch, snapshot_check=None,
                 max_entries=128, max_bytes=2 * 1024 * 1024):
        if type(max_entries) is not int or max_entries < 1 or type(max_bytes) is not int or max_bytes < 1:
            raise ValueError('Invalid supplement cache bounds')
        self._root = Path(root).resolve()
        self._manifest = copy.deepcopy(registered_artifacts)
        self._registered = {}
        for row in self._manifest:
            name, expected, _ = ref_key({**row, 'pointer': '/'})
            if name in self._registered:
                raise ProofError('DUPLICATE_SOURCE_ARTIFACT')
            self._registered[name] = expected
        self._identity = digest([str(self._root), self._manifest, str(epoch)])
        self._snapshot_check = snapshot_check
        self._max_entries, self._max_bytes = max_entries, max_bytes
        self._cache, self._documents = OrderedDict(), OrderedDict()
        self._bytes, self._document_bytes, self._lock = 0, 0, RLock()
        self._revision, self._accepted_content = 0, {}

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._documents.clear()
            self._bytes = self._document_bytes = 0
            self._revision += 1
            self._accepted_content.clear()

    def info(self):
        with self._lock:
            return {'entries': len(self._cache), 'charged_json_bytes': self._bytes,
                    'parsed_artifacts': len(self._documents), 'charged_artifact_bytes': self._document_bytes,
                    'max_entries': self._max_entries, 'max_bytes': self._max_bytes,
                    'content_revalidated_each_use': True}

    def context_for(self, record):
        with self._lock:
            if self._snapshot_check is not None and not self._snapshot_check():
                self.clear()
                return self._sealed(record, {'edges': [], 'rejected': [], 'status': 'ACCEPTED_SNAPSHOT_CHANGED'})
            refs = [ref for claim in record.get('claims', []) for ref in claim.get('evidence_refs', [])]
            snapshot_ref = record.get('scope', {}).get('snapshot_source') if isinstance(record.get('scope'), dict) else None
            if isinstance(snapshot_ref, dict):
                refs.append(snapshot_ref)
            documents, failures, content = {}, {}, {}
            for ref in refs:
                try:
                    name, expected, _ = ref_key(ref)
                    if self._registered.get(name) != expected:
                        raise ProofError('SOURCE_REFERENCE_NOT_REGISTERED')
                    if name in content or name in failures:
                        continue
                    path = (self._root / name).resolve()
                    if not path.is_relative_to(self._root):
                        raise ProofError('SOURCE_PATH_ESCAPED_ROOT')
                    raw = path.read_bytes()
                    actual = sha256(raw).hexdigest()
                    if name in self._accepted_content and self._accepted_content[name] != actual:
                        self._revision += 1
                    self._accepted_content[name] = actual
                    content[name] = actual
                    if actual != expected:
                        raise ProofError('SOURCE_ARTIFACT_SHA256_MISMATCH')
                    cached = self._documents.get((name, actual))
                    if cached is None:
                        document = json.loads(raw)
                        if len(raw) <= self._max_bytes:
                            self._documents[(name, actual)] = (document, len(raw))
                            self._document_bytes += len(raw)
                            while len(self._documents) > self._max_entries or self._document_bytes > self._max_bytes:
                                _, (_, removed) = self._documents.popitem(last=False)
                                self._document_bytes -= removed
                    else:
                        document = cached[0]
                        self._documents.move_to_end((name, actual))
                    documents[name] = document
                except (ProofError, OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
                    failed_name = ref.get('artifact_path', '<invalid>') if isinstance(ref, dict) else '<invalid>'
                    if failed_name in self._accepted_content and failed_name not in content:
                        self._revision += 1
                        self._accepted_content.pop(failed_name)
                    failures[failed_name] = str(exc)
            key = digest([self._identity, record, content, failures])
            if key in self._cache:
                payload, _ = self._cache[key]
                self._cache.move_to_end(key)
            else:
                payload = _compile(record, documents, failures)
                payload['accepted_source_identity'] = {'root': str(self._root), 'manifest_epoch_sha256': self._identity,
                                                      'artifact_content_sha256': content}
                size = len(json.dumps(payload, ensure_ascii=False).encode('utf-8')) + len(key)
                if size <= self._max_bytes:
                    self._cache[key] = (copy.deepcopy(payload), size)
                    self._bytes += size
                    while len(self._cache) > self._max_entries or self._bytes > self._max_bytes:
                        _, (_, removed) = self._cache.popitem(last=False)
                        self._bytes -= removed
            if self._snapshot_check is not None and not self._snapshot_check():
                self.clear()
                return self._sealed(record, {'edges': [], 'rejected': [], 'status': 'ACCEPTED_SNAPSHOT_CHANGED'})
            return self._sealed(record, payload)

    def _sealed(self, record, payload):
        revision = self._revision
        accepted = copy.deepcopy(payload.get('accepted_source_identity', {}).get('artifact_content_sha256', {}))
        def current():
            with self._lock:
                if revision != self._revision or (self._snapshot_check is not None and not self._snapshot_check()):
                    return False
                try:
                    for name, expected in accepted.items():
                        path = (self._root / name).resolve()
                        if (not path.is_relative_to(self._root) or self._registered.get(name) != expected or
                                sha256(path.read_bytes()).hexdigest() != expected):
                            self.clear()
                            return False
                except OSError:
                    self.clear()
                    return False
                return True
        return VerifiedSupplementContext(digest(record), {'schema': SCHEMA, **payload}, _SEAL, current)


def _compile(record, documents, failures):
    rejected, candidates = [], []
    try:
        identity = _identity(record)
    except ProofError as exc:
        return {'edges': [], 'rejected': [], 'status': str(exc)}
    scope = record['scope']
    snapshot_ref = scope.get('snapshot_source')
    snapshot_verified = False
    if isinstance(snapshot_ref, dict):
        try:
            name, _, pointer = ref_key(snapshot_ref)
            if name in failures or name not in documents:
                raise ProofError('ORIGINAL_SNAPSHOT_REFERENCE_UNAVAILABLE')
            snapshot_verified = at(documents[name], pointer) == identity['snapshot_id']
        except (ProofError, KeyError, IndexError, TypeError, ValueError):
            pass
    for index, claim in enumerate(record.get('claims', [])):
        pointer = '/claims/' + str(index)
        for ref in claim.get('evidence_refs', []):
            try:
                name, _, source_pointer = ref_key(ref)
                if name in failures or name not in documents:
                    raise ProofError(failures.get(name, 'SOURCE_ARTIFACT_UNAVAILABLE'))
                artifact = documents[name]
                if not isinstance(artifact, dict):
                    raise ProofError('ORIGINAL_ARTIFACT_ROOT_NOT_OBJECT')
                node = at(artifact, source_pointer)
                if not isinstance(node, dict) or not isinstance(node.get('statement'), str):
                    continue
                fact_id = _fact_id(node)
                candidate = {'record_pointer': pointer, 'fact_id': fact_id, 'reference': triple(ref),
                             'supplements': node.get('supplements_existing_ids', []), 'valid': False}
                candidates.append(candidate)
                if node['statement'] != claim.get('statement'):
                    raise ProofError('ORIGINAL_WHOLE_STATEMENT_MISMATCH')
                if _kind(node) != claim.get('kind'):
                    raise ProofError('ORIGINAL_CLAIM_KIND_MISMATCH')
                _version(artifact, identity)
                _version(node, identity)
                if (artifact.get('repository', artifact.get('source_repository')) != identity['source_repository'] or
                        artifact.get('source_commit', artifact.get('commit')) != identity['source_commit']):
                    raise ProofError('ORIGINAL_ARTIFACT_VERSION_UNPROVEN')
                if not snapshot_verified and artifact.get('snapshot_id', artifact.get('source_snapshot_id')) != identity['snapshot_id']:
                    raise ProofError('ORIGINAL_SNAPSHOT_IDENTITY_UNPROVEN')
                if ('original_source_scope' in scope and 'scope' in artifact and
                        scope['original_source_scope'] != artifact['scope']):
                    raise ProofError('ORIGINAL_SOURCE_SCOPE_MISMATCH')
                for citation in node.get('citations', []):
                    if isinstance(citation, dict):
                        _version(citation, identity)
                limits = []
                for field in ('scope', 'evidence_scope'):
                    if field in node:
                        if isinstance(node[field], dict):
                            _version(node[field], identity)
                        limits.append({'reference': {**triple(ref), 'pointer': source_pointer + '/' + field},
                                       'value': copy.deepcopy(node[field])})
                if 'scope' in artifact:
                    limits.append({'reference': {**triple(ref), 'pointer': '/scope'},
                                   'value': copy.deepcopy(artifact['scope'])})
                candidate.update(valid=True, kind=claim['kind'], statement_sha256=digest(claim['statement']),
                                 original_source_scopes=limits)
            except (ProofError, KeyError, IndexError, TypeError, ValueError) as exc:
                reason = str(exc)
                if candidates and candidates[-1].get('record_pointer') == pointer and candidates[-1].get('reference') == ref:
                    candidates[-1]['reason'] = reason
                rejected.append({'record_pointer': pointer, 'reference': copy.deepcopy(ref), 'reason': reason})
    by_id, by_pointer = {}, {}
    for candidate in candidates:
        by_id.setdefault(candidate['fact_id'], []).append(candidate)
        by_pointer.setdefault(candidate['record_pointer'], []).append(candidate)
    edges = []
    for target in candidates:
        names = target['supplements']
        if not isinstance(names, list) or any(not isinstance(name, str) or not _ID.fullmatch(name) for name in names):
            rejected.append({'record_pointer': target['record_pointer'], 'reason': 'INVALID_ORIGINAL_SUPPLEMENT_IDS'})
            continue
        for name in dict.fromkeys(names):
            bases = by_id.get(name, [])
            for basis in bases:
                if basis['record_pointer'] == target['record_pointer']:
                    continue
                edge = {'schema': SCHEMA, 'relation': 'EXPLICIT_ORIGINAL_SUPPLEMENTS_EXISTING_FACT',
                        'basis_record_pointer': basis['record_pointer'], 'record_pointer': target['record_pointer'],
                        'basis_fact_id': name, 'supplement_fact_id': target['fact_id'],
                        'basis_reference': basis['reference'], 'supplement_reference': target['reference'],
                        'relation_reference': {**target['reference'], 'pointer': target['reference']['pointer'] + '/supplements_existing_ids'},
                        'record_sha256': digest(record), 'original_scope_record_pointer': '/scope',
                        'original_scope_sha256': digest(scope), 'original_source_identity': identity,
                        'context_is_method_contract': False, 'necessary_dependency_proven': False,
                        'recursive_expansion': False, 'expansion_hops': 1}
                ambiguous = (len(bases) != 1 or len(by_id[target['fact_id']]) != 1 or
                             len(by_pointer[basis['record_pointer']]) != 1 or len(by_pointer[target['record_pointer']]) != 1)
                if ambiguous or not basis['valid'] or not target['valid']:
                    edge['reason'] = 'ORIGINAL_FACT_IDENTITY_AMBIGUOUS' if ambiguous else target.get('reason', basis.get('reason', 'ORIGINAL_FACT_UNVERIFIED'))
                    rejected.append(edge)
                else:
                    edge['original_source_scopes'] = target['original_source_scopes']
                    edges.append(edge)
    return {'edges': edges, 'rejected': rejected, 'status': 'EXPLICIT_ORIGINAL_RELATIONS_COMPILED'}


def supplement_atoms(record, family, query, seeds, verified, contexts=None):
    """Return whole context atoms; input seeds are fixed before this lane runs."""
    status = {'schema': SCHEMA, 'relation': 'EXPLICIT_ORIGINAL_SUPPLEMENTS_EXISTING_FACT',
              'relations': [], 'gaps': [], 'supplement_only_record_pointers': [],
              'context_is_method_contract': False, 'necessary_dependency_proven': False,
              'recursive_expansion': False, 'expansion_hops': 1}
    if family != 'core' or not seeds or not query.strip() or type(verified) is not VerifiedSupplementContext:
        return [], status
    try:
        payload = verified.render(record)
    except ProofError as exc:
        status['proof_status'] = str(exc)
        return [], status
    status['proof_status'] = payload['status']
    originals = {f'/claims/{i}': claim for i, claim in enumerate(record.get('claims', []))}
    seed_pointers = {seed['record_pointer'] for seed in seeds
                     if seed.get('record_pointer') in originals and
                     seed.get('kind') == originals[seed['record_pointer']].get('kind') and
                     seed.get('statement') == originals[seed['record_pointer']].get('statement') and
                     not any(seed.get(key) for key in ('record_context', 'provider_context', 'supplement_context', 'consumption_hint'))}
    status['proof_rejections'] = [row for row in payload['rejected'] if row.get('basis_record_pointer') in seed_pointers]
    status['gaps'].extend(copy.deepcopy(status['proof_rejections']))
    contexts = contexts or {}
    owners = _proved_owners(record, family)
    result = {}
    for edge in payload['edges']:
        basis, pointer = edge['basis_record_pointer'], edge['record_pointer']
        if basis not in seed_pointers:
            continue
        names = [name for name in facets.QUALIFIED.findall(originals[pointer]['statement'])
                 if ':' in name or '.' in name]
        names += [re.split(r'[:.]', name)[0] for name in names]
        context = {'record_pointer': pointer, 'basis_record_pointers': [basis], 'required_basis_record_pointers': [basis],
                   'relation_symbols': list(dict.fromkeys(names)), 'original_scope': record['scope']}
        admitted, decisions = context_admission(record, family, [context], query)
        basis_owners = set(contexts.get(basis, {}).get('receivers', []))
        target_owners = set(contexts.get(pointer, {}).get('receivers', []))
        original_basis_owners, original_target_owners = owners.get(basis, set()), owners.get(pointer, set())
        owner_mismatch = bool((basis_owners and target_owners and not basis_owners & target_owners) or
            (original_basis_owners and original_target_owners and not original_basis_owners & original_target_owners))
        sample_proof = (_seed_sample_proof(record, family, query, basis, pointer, decisions)
                        if not admitted and not owner_mismatch else None)
        if sample_proof is not None:
            admitted = [context]
        if not admitted or owner_mismatch:
            status['gaps'].append({**copy.deepcopy(edge), 'reason': 'SUPPLEMENT_DISTINCT_PROVED_OWNER' if owner_mismatch else 'SUPPLEMENT_CONTEXT_EXCLUDED',
                                   'admission': decisions, 'delivered': False})
            continue
        original = originals[pointer]
        atom = result.setdefault(pointer, {'record_pointer': pointer, 'kind': original['kind'],
                                          'statement': copy.deepcopy(original['statement']), 'supplement_context': []})
        relation = {'role': ROLE, **copy.deepcopy(edge)}
        if sample_proof is not None:
            relation['sample_admission'] = sample_proof
            relation['original_admission'] = copy.deepcopy(decisions)
            atom['delivery_scope'] = {'kind': 'SAMPLE_SPECIFIC', 'sample_identity': sample_proof['sample_identity'],
                                      'not_a_generic_contract': True}
        atom['supplement_context'].append(relation)
        status['relations'].append({**copy.deepcopy(relation), 'delivered': True})
    return list(result.values()), status


def _proved_owners(record, family):
    owners = {}
    for symbol in facets.contract_symbols(record, family):
        for match in facets.contract_matches(record, family, symbol):
            for pointer, role in match.get('pointer_roles', {}).items():
                if (isinstance(role, dict) and role.get('role') == 'METHOD_SUBJECT' and
                        role.get('callee_semantics_supported') is True and
                        not role.get('reference_context_only') and not match.get('reference_context_only') and
                        pointer in match.get('record_pointers', []) and match.get('receiver')):
                    owners.setdefault(pointer, set()).add(match['receiver'])
    return owners


def _seed_sample_proof(record, family, query, basis, pointer, decisions):
    """Only a proved selected method subject may identify its own sample context."""
    rejected = [row for row in decisions if row.get('admitted') is False]
    if (len(rejected) != 1 or rejected[0].get('record_pointer') != pointer or
            rejected[0].get('reason') != 'SAMPLE_IDENTITY_NOT_REQUESTED' or facets.query_scope(query)['generic']):
        return None
    sample = rejected[0].get('sample_identity')
    if not isinstance(sample, str):
        return None
    normalized = facets.normalize_symbol(sample).replace(':', '.')
    proofs = []
    for symbol in facets.contract_symbols(record, family):
        for match in facets.contract_matches(record, family, symbol):
            role = match.get('pointer_roles', {}).get(basis, {})
            if (basis not in match.get('record_pointers', []) or not isinstance(role, dict) or
                    role.get('role') != 'METHOD_SUBJECT' or role.get('callee_semantics_supported') is not True or
                    role.get('reference_context_only') or match.get('reference_context_only') or
                    basis in match.get('reference_context_record_pointers', []) or
                    facets.normalize_symbol(match.get('symbol', '')).replace(':', '.') != normalized):
                continue
            owner = match.get('receiver')
            if not owner or normalized.rsplit('.', 1)[0] != owner:
                continue
            proof = {'sample_identity': sample, 'basis_record_pointer': basis, 'record_pointer': pointer,
                     'method_subject_identity': match['symbol'], 'receiver': owner,
                     'record_sha256': digest(record), 'role': 'METHOD_SUBJECT',
                     'basis': 'EXPLICIT_SUPPLEMENT_OF_ACTUAL_ADMITTED_SAME_METHOD_SUBJECT',
                     'not_a_generic_contract': True, 'query_rewritten': False}
            if proof not in proofs:
                proofs.append(proof)
    return proofs[0] if len(proofs) == 1 else None


def verified_scope_supplements(record, family, delivered_groups, query, verified):
    """Recheck the capability and actual whole seed/target atoms for Scope gating."""
    if family != 'core' or type(verified) is not VerifiedSupplementContext:
        return set()
    actual = {}
    originals = {f'/claims/{i}': claim for i, claim in enumerate(record.get('claims', []))}
    for atoms in delivered_groups.values():
        for atom in atoms:
            pointer = atom.get('record_pointer')
            original = originals.get(pointer)
            if original and atom.get('kind') == original['kind'] and atom.get('statement') == original['statement']:
                actual[pointer] = atom
    contexts = {pointer: {'record_pointer': pointer, 'scope': '', 'receivers': [], 'role_bindings': [],
                          'atom_kind': atom['kind']} for pointer, atom in actual.items()}
    for symbol in facets.contract_symbols(record, family):
        for match in facets.contract_matches(record, family, symbol):
            for pointer, role in match.get('pointer_roles', {}).items():
                if pointer not in contexts or not isinstance(role, dict):
                    continue
                contexts[pointer]['role_bindings'].append({'symbol': match.get('symbol'), 'receiver': match.get('receiver'), **role})
                if role.get('role') == 'METHOD_SUBJECT' and match.get('receiver'):
                    contexts[pointer]['receivers'].append(match['receiver'])
    # 此处只核验已经实际交付的原子，不以缺少原检索上下文的第二次相关性判定改写 seed。
    # 原样例、否定和 basis 门禁仍由 supplement_atoms 逐条执行。
    seeds = [atom for pointer, atom in actual.items()
             if not any(atom.get(k) for k in ('record_context', 'provider_context', 'supplement_context', 'consumption_hint'))]
    supplements, _ = supplement_atoms(record, family, query, seeds, verified, contexts)
    return {atom['record_pointer'] for atom in supplements if atom['record_pointer'] in actual and
            atom['statement'] == actual[atom['record_pointer']]['statement'] and
            any(row.get('sample_admission') for row in atom['supplement_context'])}

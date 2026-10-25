"""Exact Source-backed metadata navigation; no facts or method dependencies."""
import copy
import json
import re
import time
from collections import OrderedDict
from hashlib import sha256
from pathlib import Path
from threading import RLock

SCHEMA = 'source-backed-scope-navigation-proof/1'
REF_FIELDS = ('artifact_path', 'sha256', 'pointer')
FIELDS = {'original_question': {'title': 'PROJECTION_TITLE', 'title_zh': 'PROJECTION_TITLE'},
          'load_when': {'load_when': 'PROJECTION_LOAD_WHEN', 'load_when_zh': 'PROJECTION_LOAD_WHEN'}}
SCOPE_LEAF = re.compile(r'^/scope/source_scopes/(0|[1-9][0-9]*)/(original_question|load_when)$')
PROJECTION_NODE = re.compile(r'^/coding_projection/(0|[1-9][0-9]*)$')
COPIED_SCOPE_LEAF = re.compile(r'^/scope/original_projection/(title|title_zh|load_when|load_when_zh)$')
COPIED_HEADER_NODE = re.compile(r'^/(coding_projection|coding_facets)/(0|[1-9][0-9]*)$')
COPIED_FIELDS = {field: role for fields in FIELDS.values() for field, role in fields.items()}
COPIED_HEADER_SCHEMAS = {
    'coding_projection': ('native-campaign-research/1', 'ORIGINAL_CODING_PROJECTION_HEADER'),
    'coding_facets': ('native-campaign/batch006/world-ready/1', 'ORIGINAL_CODING_FACET_HEADER'),
}
CLAIM_OWNER = re.compile(r'^/claims/(0|[1-9][0-9]*)/evidence_refs/(0|[1-9][0-9]*)$')
RECORD_OWNER = re.compile(r'^/evidence_refs/(0|[1-9][0-9]*)$')
_SEAL = object()


class ProofError(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':')).encode('utf-8')).hexdigest()


def at(value, pointer):
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise ProofError('INVALID_JSON_POINTER')
    for token in pointer.split('/')[1:]:
        if re.search(r'~(?![01])', token):
            raise ProofError('INVALID_JSON_POINTER')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            if not re.fullmatch(r'0|[1-9][0-9]*', token):
                raise ProofError('INVALID_JSON_POINTER')
            value = value[int(token)]
        elif isinstance(value, dict):
            value = value[token]
        else:
            raise ProofError('INVALID_JSON_POINTER')
    return value


def ref_key(ref):
    if not isinstance(ref, dict) or not all(isinstance(ref.get(k), str) for k in REF_FIELDS):
        raise ProofError('INVALID_REFERENCE_TRIPLE')
    if not re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) or not ref['pointer'].startswith('/'):
        raise ProofError('INVALID_REFERENCE_TRIPLE')
    artifact = ref['artifact_path']
    if (not artifact or artifact.startswith(('/', '\\')) or ':' in artifact or '\\' in artifact
            or any(part in ('', '.', '..') for part in artifact.split('/'))):
        raise ProofError('INVALID_ARTIFACT_IDENTITY')
    return tuple(ref[k] for k in REF_FIELDS)


def triple(ref):
    ref_key(ref)
    return {k: ref[k] for k in REF_FIELDS}


def evidence_references(record, allow_record_refs=False):
    values = []
    for i, claim in enumerate(record.get('claims', [])):
        for j, ref in enumerate(claim.get('evidence_refs', [])):
            values.append((f'/claims/{i}/evidence_refs/{j}', ref))
    if allow_record_refs:
        values.extend((f'/evidence_refs/{i}', ref) for i, ref in enumerate(record.get('evidence_refs', [])))
    return values


class ExactSourceReader:
    """Checks full artifact bytes, exposes only original registered exact nodes."""
    def __init__(self, root, registered_artifacts, allowed_refs):
        self._root = Path(root).resolve()
        self._registered = {}
        for row in registered_artifacts:
            artifact, expected = row.get('artifact_path'), row.get('sha256')
            ref_key({'artifact_path': artifact, 'sha256': expected, 'pointer': '/'})
            if artifact in self._registered:
                raise ProofError('DUPLICATE_SOURCE_ARTIFACT')
            self._registered[artifact] = expected
        self._allowed = {ref_key(ref) for ref in allowed_refs}
        self._documents = {}
        self.requested = []

    def read(self, ref):
        key = ref_key(ref)
        if key not in self._allowed:
            raise ProofError('UNREGISTERED_EXACT_REFERENCE')
        artifact, expected, pointer = key
        if self._registered.get(artifact) != expected:
            raise ProofError('SOURCE_REFERENCE_NOT_REGISTERED')
        if artifact not in self._documents:
            target = (self._root / artifact).resolve()
            if not target.is_relative_to(self._root):
                raise ProofError('SOURCE_PATH_ESCAPED_ROOT')
            try:
                raw = target.read_bytes()
            except OSError as exc:
                raise ProofError('SOURCE_ARTIFACT_UNAVAILABLE') from exc
            if sha256(raw).hexdigest() != expected:
                raise ProofError('SOURCE_ARTIFACT_SHA256_MISMATCH')
            try:
                self._documents[artifact] = json.loads(raw)
            except (ValueError, UnicodeError) as exc:
                raise ProofError('SOURCE_ARTIFACT_NOT_JSON') from exc
        try:
            node = at(self._documents[artifact], pointer)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProofError('SOURCE_EXACT_NODE_MISSING') from exc
        self.requested.append(triple(ref))
        return copy.deepcopy(node)

    def root_schema(self, ref):
        # Reauthorize the exact ref; root identity comes only from SHA-checked bytes.
        self.read(ref)
        document = self._documents[ref['artifact_path']]
        if not isinstance(document, dict):
            raise ProofError('SOURCE_ROOT_NOT_OBJECT')
        return {key: copy.deepcopy(document[key]) for key in ('schema_version', 'schema') if key in document}


def _projection_header(ref, node):
    if not PROJECTION_NODE.fullmatch(ref['pointer']):
        raise ProofError('NOT_EXACT_PROJECTION_HEADER_REFERENCE')
    if not (isinstance(node, dict) and isinstance(node.get('id'), str)
            and isinstance(node.get('source_contract'), list)
            and isinstance(node.get('evidence_ids'), list)
            and all(isinstance(x, str) for x in node['source_contract'] + node['evidence_ids'])):
        raise ProofError('NOT_SUPPORTED_SOURCE_METADATA_NODE')


def _copied_header_role(ref, node, root_schema):
    match = COPIED_HEADER_NODE.fullmatch(ref['pointer'])
    if not match:
        raise ProofError('NOT_EXACT_COPIED_HEADER_REFERENCE')
    schema, role = COPIED_HEADER_SCHEMAS[match[1]]
    if root_schema != {'schema_version': schema}:
        raise ProofError('NOT_SUPPORTED_SOURCE_ROOT_SCHEMA')

    def strings(field):
        values = node.get(field)
        return isinstance(values, list) and bool(values) and all(isinstance(x, str) and x for x in values)

    if not (isinstance(node, dict) and isinstance(node.get('id'), str) and node['id']
            and strings('source_contract') and strings('evidence_ids') and strings('reuse_ids')):
        raise ProofError('NOT_SUPPORTED_COPIED_HEADER_ROLE')
    if match[1] == 'coding_projection':
        supported = (strings('signatures')
                     and node.get('recommendation_kind') == 'EngineeringRecommendation_NotRuntimeValidated'
                     and isinstance(node.get('recommendation_zh'), str) and bool(node['recommendation_zh'])
                     and node.get('canonical') is False and node.get('runtimeReady') is False)
    else:
        supported = (strings('questions') and strings('branches')
                     and isinstance(node.get('positive_result'), str) and bool(node['positive_result'])
                     and node.get('recommendation_kind') == 'EngineeringRecommendation_NotEngineFact'
                     and isinstance(node.get('recommendation'), str) and bool(node['recommendation']))
    if not supported:
        raise ProofError('NOT_SUPPORTED_COPIED_HEADER_ROLE')
    return role


def _build_copied_header(record, scope_pointer, owner, ref, reader, allow_record_refs):
    match = COPIED_SCOPE_LEAF.fullmatch(scope_pointer)
    if not match:
        raise ProofError('NOT_SUPPORTED_SCOPE_NAVIGATION_LEAF')
    authorized = dict(evidence_references(record, allow_record_refs))
    if owner not in authorized or ref_key(authorized[owner]) != ref_key(ref):
        raise ProofError('REFERENCE_OWNER_OR_TRIPLE_MISMATCH')
    value = at(record, scope_pointer)
    if not isinstance(value, str) or not value:
        raise ProofError('NOT_LITERAL_NAVIGATION_STRING')
    node = reader.read(ref)
    root_schema = reader.root_schema(ref)
    node_role = _copied_header_role(ref, node, root_schema)
    wrapper = at(record, '/scope/original_projection')
    if wrapper != node or digest(wrapper) != digest(node):
        raise ProofError('COPIED_WRAPPER_NOT_EXACT_SOURCE_HEADER')
    candidates = [(field, role) for field, role in COPIED_FIELDS.items()
                  if isinstance(node.get(field), str) and node[field] == value]
    if len(candidates) != 1 or candidates[0][0] != match[1]:
        raise ProofError('SOURCE_METADATA_LITERAL_MATCH_NOT_UNIQUE')
    field, role = candidates[0]
    return {'schema': SCHEMA, 'proof_role': 'SOURCE_METADATA_NAVIGATION_ONLY',
            'record_sha256': digest(record), 'scope_pointer': scope_pointer,
            'scope_value_sha256': digest(value), 'original_reference_owner': owner,
            'original_reference': triple(ref), 'source_root_schema': root_schema,
            'source_node_role': node_role, 'source_field_pointer': ref['pointer'] + '/' + field,
            'source_field_role': role, 'source_field_value_sha256': digest(node[field]),
            'source_node_sha256': digest(node), 'scope_wrapper_pointer': '/scope/original_projection',
            'scope_wrapper_sha256': digest(wrapper), 'new_fact': False, 'method_dependency': False,
            'necessary_scope_enumeration_proven': False}


def _build(record, scope_pointer, owner, ref, reader, allow_record_refs):
    if COPIED_SCOPE_LEAF.fullmatch(scope_pointer):
        return _build_copied_header(record, scope_pointer, owner, ref, reader, allow_record_refs)
    match = SCOPE_LEAF.fullmatch(scope_pointer)
    if not match:
        raise ProofError('NOT_SUPPORTED_SCOPE_NAVIGATION_LEAF')
    authorized = dict(evidence_references(record, allow_record_refs))
    if owner not in authorized or ref_key(authorized[owner]) != ref_key(ref):
        raise ProofError('REFERENCE_OWNER_OR_TRIPLE_MISMATCH')
    value = at(record, scope_pointer)
    if not isinstance(value, str) or not value:
        raise ProofError('NOT_LITERAL_NAVIGATION_STRING')
    entry = at(record, f'/scope/source_scopes/{match[1]}')
    scope_ref = entry.get('scope_ref') if isinstance(entry, dict) else None
    if ref_key(scope_ref)[:2] != ref_key(ref)[:2] or scope_ref['pointer'] != '/scope':
        raise ProofError('SAME_ARTIFACT_SCOPE_REFERENCE_NOT_PROVEN')
    node = reader.read(ref)
    _projection_header(ref, node)
    if not isinstance(reader.read(scope_ref), dict):
        raise ProofError('SOURCE_SCOPE_NODE_NOT_OBJECT')
    candidates = [(field, role) for field, role in FIELDS[match[2]].items()
                  if isinstance(node.get(field), str) and node[field] == value]
    if len(candidates) != 1:
        raise ProofError('SOURCE_METADATA_LITERAL_MATCH_NOT_UNIQUE')
    field, role = candidates[0]
    return {'schema': SCHEMA, 'proof_role': 'SOURCE_METADATA_NAVIGATION_ONLY',
            'record_sha256': digest(record), 'scope_pointer': scope_pointer,
            'scope_value_sha256': digest(value), 'original_reference_owner': owner,
            'original_reference': triple(ref), 'source_scope_reference': triple(scope_ref),
            'source_node_role': 'CODING_PROJECTION_HEADER',
            'source_field_pointer': ref['pointer'] + '/' + field, 'source_field_role': role,
            'source_field_value_sha256': digest(node[field]), 'source_node_sha256': digest(node),
            'new_fact': False, 'method_dependency': False, 'necessary_scope_enumeration_proven': False}


def compile_navigation_proofs(record, reader, allow_record_refs=False):
    proofs, rejected = [], []
    refs = evidence_references(record, allow_record_refs)
    scopes = record.get('scope', {}).get('source_scopes', [])
    for i, entry in enumerate(scopes if isinstance(scopes, list) else []):
        if not isinstance(entry, dict):
            continue
        for key in FIELDS:
            if key not in entry:
                continue
            pointer = f'/scope/source_scopes/{i}/{key}'
            for owner, ref in refs:
                try:
                    if not isinstance(ref, dict) or not PROJECTION_NODE.fullmatch(str(ref.get('pointer', ''))):
                        continue
                    proofs.append(_build(record, pointer, owner, ref, reader, allow_record_refs))
                    break
                except (ProofError, KeyError, IndexError, TypeError) as exc:
                    rejected.append({'scope_pointer': pointer, 'reference_owner': owner, 'reason': str(exc)})
            else:
                rejected.append({'scope_pointer': pointer, 'reason': 'NO_EXACT_SOURCE_METADATA_PROOF'})
    wrapper = record.get('scope', {}).get('original_projection')
    if isinstance(wrapper, dict):
        copied_refs = sorted(refs, key=lambda item: not bool(RECORD_OWNER.fullmatch(item[0])))
        for field in COPIED_FIELDS:
            if field not in wrapper:
                continue
            pointer = '/scope/original_projection/' + field
            for owner, ref in copied_refs:
                try:
                    if not isinstance(ref, dict) or not COPIED_HEADER_NODE.fullmatch(str(ref.get('pointer', ''))):
                        continue
                    proofs.append(_build_copied_header(record, pointer, owner, ref, reader, allow_record_refs))
                    break
                except (ProofError, KeyError, IndexError, TypeError) as exc:
                    rejected.append({'scope_pointer': pointer, 'reference_owner': owner, 'reason': str(exc)})
            else:
                rejected.append({'scope_pointer': pointer, 'reason': 'NO_EXACT_SOURCE_METADATA_PROOF'})
    return {'proofs': proofs, 'rejected': rejected, 'facts_added': 0, 'dependencies_added': 0}


def validate_navigation_proof(record, proof, reader, allow_record_refs=False):
    try:
        owner = proof['original_reference_owner']
        if not (CLAIM_OWNER.fullmatch(owner) or (allow_record_refs and RECORD_OWNER.fullmatch(owner))):
            raise ProofError('REFERENCE_OWNER_NOT_AUTHORIZED')
        expected = _build(record, proof['scope_pointer'], owner, proof['original_reference'], reader, allow_record_refs)
        if proof != expected or digest(proof) != digest(expected):
            raise ProofError('PROOF_CONTENT_OR_RECORD_IDENTITY_MISMATCH')
        return {'valid': True, 'proof': copy.deepcopy(expected)}
    except (ProofError, KeyError, IndexError, TypeError, ValueError) as exc:
        return {'valid': False, 'reason': str(exc)}


class VerifiedNavigationContext:
    """An internal capability, never a caller-supplied proof flag or dict."""
    def __init__(self, record_sha256, proofs, seal):
        if seal is not _SEAL:
            raise ProofError('UNVERIFIED_NAVIGATION_CONTEXT')
        self._record_sha256 = record_sha256
        self._proofs = {proof['scope_pointer']: copy.deepcopy(proof) for proof in proofs}

    def proof_for(self, record, pointer, value):
        proof = self._proofs.get(pointer)
        if (proof and digest(record) == self._record_sha256
                and proof['record_sha256'] == self._record_sha256
                and proof['scope_value_sha256'] == digest(value)):
            return copy.deepcopy(proof)
        return None


def proved_navigation(context, record, pointer, value):
    return context.proof_for(record, pointer, value) if type(context) is VerifiedNavigationContext else None


class NavigationProofRegistry:
    """Per-Service bounded cache; root, accepted epoch and full record isolate it."""
    def __init__(self, root, registered_artifacts, epoch, snapshot_check=None,
                 max_entries=256, max_bytes=2 * 1024 * 1024, ttl_seconds=300, clock=time.monotonic):
        if (type(max_entries) is not int or max_entries < 1 or type(max_bytes) is not int or max_bytes < 1
                or not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0):
            raise ValueError('Invalid navigation cache bounds')
        self._root = Path(root).resolve()
        self._registered = copy.deepcopy(registered_artifacts)
        self._epoch = sha256(str(epoch).encode('utf-8')).hexdigest()
        self._snapshot_check = snapshot_check
        self._max_entries, self._max_bytes, self._ttl = max_entries, max_bytes, ttl_seconds
        self._clock, self._cache, self._bytes, self._lock = clock, OrderedDict(), 0, RLock()

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._bytes = 0

    def info(self):
        with self._lock:
            return {'entries': len(self._cache), 'charged_json_bytes': self._bytes,
                    'max_entries': self._max_entries, 'max_bytes': self._max_bytes,
                    'ttl_seconds': self._ttl}

    def context_for(self, record):
        record_sha = digest(record)
        with self._lock:
            if self._snapshot_check is not None and not self._snapshot_check():
                self.clear()
                return VerifiedNavigationContext(record_sha, [], _SEAL)
            key = (str(self._root), self._epoch, record_sha)
            now = self._clock()
            for old_key, (_, expiry, size) in list(self._cache.items()):
                if expiry <= now:
                    self._bytes -= size
                    del self._cache[old_key]
            if key in self._cache:
                proofs, _, _ = self._cache[key]
                self._cache.move_to_end(key)
                return VerifiedNavigationContext(record_sha, proofs, _SEAL)
            proofs = []
            try:
                refs = [ref for _, ref in evidence_references(record, True)]
                refs.extend(entry['scope_ref'] for entry in record.get('scope', {}).get('source_scopes', [])
                            if isinstance(entry, dict) and 'scope_ref' in entry)
                reader = ExactSourceReader(self._root, self._registered, refs)
                compiled = compile_navigation_proofs(record, reader, True)
                proofs = [proof for proof in compiled['proofs']
                          if validate_navigation_proof(record, proof, reader, True)['valid']]
            except (ProofError, KeyError, IndexError, TypeError, ValueError):
                pass
            size = len(json.dumps(proofs, ensure_ascii=False).encode('utf-8')) + sum(map(len, key))
            if size <= self._max_bytes:
                self._cache[key] = (copy.deepcopy(proofs), now + self._ttl, size)
                self._bytes += size
                while len(self._cache) > self._max_entries or self._bytes > self._max_bytes:
                    _, (_, _, removed) = self._cache.popitem(last=False)
                    self._bytes -= removed
            return VerifiedNavigationContext(record_sha, proofs, _SEAL)

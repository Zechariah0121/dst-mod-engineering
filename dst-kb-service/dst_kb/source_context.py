"""Exact original source context, independent of method-contract delivery."""
import copy
import ast
import json
import re
import contextlib
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import CodeType, FunctionType
from . import facet_contracts
from . import source_identity
from . import relevance_frames
from .source_epoch_runtime import active_epoch
from .scope_navigation import ExactSourceReader, ProofError, at, digest, ref_key, triple

SCHEMA = 'bounded-original-source-context/1'
NOTICE = ('此绑定仅呈现原知识记录中有界的源码上下文；它不证明被查询方法自身行为、'
          'callee 签名、参数/返回语义或完整闭包。')
IDENTITY = re.compile(r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*', re.ASCII)
DIRECT_EDGE = re.compile(r'DIRECT:\s*([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+)\.?', re.ASCII)
_SEAL = object()
METHOD_ROLES = frozenset(('METHOD_SUBJECT', 'BOUNDED_CALLEE_CALLSITE',
                         'BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED'))
ROLE_FUNCTIONS = ('contract_matches', '_uncached_contract_matches', '_contract_matches',
                  'normalize_symbol', 'statement_binding', '_callsite_relations',
                  '_subject_behavior', '_subject_reference_occurrence', '_subject_caller_occurrence',
                  '_subject_reference_only', '_mapped_owner_subject', '_source_declared_subject', '_sample_scope',
                  '_identity_mapped_spec', '_declared_local_subject', '_qualified_getter_context',
                  '_explicit_comparison_context', 'context_admission', '_declared_original_subject')
ROLE_FUNCTIONS += ('_subject_predicate_owner', '_constructor_source_range', '_returned_constructor_signature')
ROLE_FUNCTIONS += ('_steam_binding_proof', '_declared_property_subject',
                   '_source_bound_independent_subject', '_digest',
                   'record_contract_context', '_cached_contract_matches',
                   '_navigation_key', '_record_map', '_record_identity_bindings',
                   '_registered_navigation')
IDENTITY_ROLE_FUNCTIONS = ('digest', '_at', '_owner', '_method', '_physical',
    'SourceIdentityRegistry.__init__', 'SourceIdentityRegistry._node', 'SourceIdentityRegistry._valid',
    'SourceIdentityRegistry._valid_row', 'SourceIdentityRegistry._valid_original_subject',
    'SourceIdentityRegistry.rows', 'SourceIdentityRegistry._unambiguous_rows',
    'SourceIdentityRegistry._matching_rows', 'SourceIdentityRegistry.bindings',
    'SourceIdentityRegistry.resolve', 'SourceIdentityRegistry.resolve_many', 'SourceIdentityRegistry.symbols')
IDENTITY_ROLE_FUNCTIONS += ('steam_source_version', '_steam_manifest_files',
                            'SourceIdentityRegistry._valid_steam_excerpt', '_current_source_files',
                            'SourceIdentityRegistry.public_alias_rows')
IDENTITY_ROLE_FUNCTIONS += ('_lexical_fingerprint', '_source_manifest_inputs',
                            'SourceIdentityRegistry._public_alias_table',
                            'SourceIdentityRegistry._filtered_public_alias_rows')
_LRU_WRAPPER = type(lru_cache()(lambda: None))
_CONTEXTMANAGER_CODE = contextlib.contextmanager(lambda: None).__code__
STEAM_WHOLE_SCHEMA = {'schema': 'w27-versioned-whole-claim-source-evidence/1'}


def _present_epoch(epoch):
    try:
        ledger = json.loads(epoch)
    except (TypeError, ValueError, RecursionError):
        return epoch
    if (type(ledger) is not list or not ledger or
        any(type(row) is not list or len(row) != 4 or
            type(row[0]) is not str or type(row[1]) is not int or
            type(row[2]) is not int or type(row[3]) is not str or
            re.fullmatch(r'[0-9a-fA-F]{64}', row[3]) is None for row in ledger)):
        return epoch
    # 只压缩对外账本表示；原 epoch 与内部失效检查保留，形状和摘要不新增真实性证明。
    return 'sha256:' + sha256(epoch.encode('utf-8')).hexdigest()


def _code_value(value):
    if isinstance(value, CodeType):
        fields = ('co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount', 'co_nlocals',
                  'co_stacksize', 'co_flags', 'co_code', 'co_names', 'co_varnames',
                  'co_filename', 'co_name', 'co_qualname', 'co_firstlineno', 'co_linetable',
                  'co_exceptiontable', 'co_freevars', 'co_cellvars', 'co_consts')
        return {'code': {field: _code_value(getattr(value, field, None)) for field in fields}}
    if isinstance(value, bytes):
        return {'bytes': value.hex()}
    if isinstance(value, tuple):
        return {'tuple': [_code_value(x) for x in value]}
    if isinstance(value, frozenset):
        return {'frozenset': sorted((_code_value(x) for x in value), key=digest)}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise ProofError('UNSUPPORTED_CLASSIFIER_CODE_CONSTANT')


def _code_sha(value):
    return digest(_code_value(value))


def _loaded_role_codes():
    result = {}
    for name in ROLE_FUNCTIONS:
        function = getattr(facet_contracts, name, None)
        if name == 'record_contract_context':
            wrapped = getattr(function, '__wrapped__', None)
            closure = getattr(function, '__closure__', None)
            if (not isinstance(function, FunctionType) or
                    function.__code__ is not _CONTEXTMANAGER_CODE or
                    function.__globals__ is not vars(contextlib) or
                    not closure or len(closure) != 1 or
                    closure[0].cell_contents is not wrapped):
                raise ProofError('UNVERIFIED_LOADED_ROLE_CLASSIFIER')
            function = wrapped
        if (not isinstance(function, FunctionType) or function.__module__ != facet_contracts.__name__
                or not isinstance(function.__code__, CodeType)):
            raise ProofError('UNVERIFIED_LOADED_ROLE_CLASSIFIER')
        result[name] = _code_sha(function.__code__)
    return result


def _accepted_identity_classifier():
    path = Path(source_identity.__file__).resolve()
    if path != Path(__file__).resolve().with_name('source_identity.py'):
        raise ProofError('UNSUPPORTED_IDENTITY_CLASSIFIER_ARTIFACT')
    raw = path.read_bytes()
    compiled = compile(raw, str(path), 'exec', dont_inherit=True)
    source_codes = {}
    for code in compiled.co_consts:
        if not isinstance(code, CodeType):
            continue
        source_codes[code.co_name] = _code_sha(code)
        if code.co_name == 'SourceIdentityRegistry':
            for method in code.co_consts:
                if isinstance(method, CodeType):
                    source_codes[code.co_name + '.' + method.co_name] = _code_sha(method)
    loaded = {}
    for name in IDENTITY_ROLE_FUNCTIONS:
        function = source_identity
        for part in name.split('.'):
            function = getattr(function, part, None)
        if name in ('_steam_manifest_files', '_source_manifest_inputs'):
            if type(function) is not _LRU_WRAPPER:
                raise ProofError('UNVERIFIED_LOADED_IDENTITY_CLASSIFIER')
            function = getattr(function, '__wrapped__', None)
        if (not isinstance(function, FunctionType) or function.__module__ != source_identity.__name__ or
                Path(function.__code__.co_filename).resolve() != path):
            raise ProofError('UNVERIFIED_LOADED_IDENTITY_CLASSIFIER')
        loaded[name] = _code_sha(function.__code__)
        if source_codes.get(name) != loaded[name]:
            raise ProofError('IDENTITY_CLASSIFIER_CODE_ARTIFACT_MISMATCH')
    return {'artifact_path': str(path), 'artifact_sha256': sha256(raw).hexdigest(),
            'fingerprint_schema': 'python-code-canonical-json/1',
            'loaded_function_code_sha256': loaded, 'loaded_code_matches_artifact': True}


def _accepted_behavior_regex(raw):
    """Verify the one source-declared regex without executing classifier code."""
    assignments = [node for node in ast.parse(raw).body if isinstance(node, ast.Assign) and
                   any(isinstance(target, ast.Name) and target.id == 'BEHAVIOR' for target in node.targets)]
    if len(assignments) != 1:
        raise ProofError('UNSUPPORTED_BEHAVIOR_REGEX_DECLARATION')
    assignment, = assignments
    call = assignment.value
    if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute) or
            not isinstance(call.func.value, ast.Name) or call.func.value.id != 're' or call.func.attr != 'compile' or
            len(call.args) != 2 or call.keywords or not isinstance(call.args[1], ast.Attribute) or
            not isinstance(call.args[1].value, ast.Name) or call.args[1].value.id != 're' or call.args[1].attr != 'I'):
        raise ProofError('UNSUPPORTED_BEHAVIOR_REGEX_DECLARATION')
    try:
        pattern = ast.literal_eval(call.args[0])
    except (ValueError, TypeError):
        raise ProofError('UNSUPPORTED_BEHAVIOR_REGEX_DECLARATION')
    loaded = getattr(facet_contracts, 'BEHAVIOR', None)
    flags = int(re.I | re.UNICODE)
    if (not isinstance(pattern, str) or not isinstance(loaded, re.Pattern) or
            loaded.pattern != pattern or loaded.flags != flags):
        raise ProofError('ROLE_CLASSIFIER_REGEX_ARTIFACT_MISMATCH')
    return {'pattern_sha256': sha256(pattern.encode('utf-8')).hexdigest(), 'flags': flags,
            'source_assignment_line': assignment.lineno, 'loaded_matches_source': True}


def _accepted_quote_view_helper():
    """Bind the actual facet alias to its one accepted cross-module source."""
    path = Path(relevance_frames.__file__).resolve()
    if path != Path(__file__).resolve().with_name('relevance_frames.py'):
        raise ProofError('UNSUPPORTED_QUOTE_VIEW_HELPER_ARTIFACT')
    raw = path.read_bytes()
    alias = getattr(facet_contracts, '_data_quote_view', None)
    original = getattr(relevance_frames, '_data_quote_view', None)
    if (alias is not original or not isinstance(alias, FunctionType) or
            alias.__name__ != '_data_quote_view' or
            relevance_frames.__name__ != 'dst_kb.relevance_frames' or
            alias.__module__ != relevance_frames.__name__ or
            not isinstance(alias.__code__, CodeType) or
            Path(alias.__code__.co_filename).resolve() != path or
            alias.__globals__.get('re') is not re):
        raise ProofError('UNVERIFIED_LOADED_QUOTE_VIEW_HELPER')
    compiled = compile(raw, str(path), 'exec', dont_inherit=True)
    codes = [code for code in compiled.co_consts
             if isinstance(code, CodeType) and code.co_name == '_data_quote_view']
    loaded_sha = _code_sha(alias.__code__)
    if len(codes) != 1 or _code_sha(codes[0]) != loaded_sha:
        raise ProofError('QUOTE_VIEW_HELPER_CODE_ARTIFACT_MISMATCH')
    return {'artifact_path': str(path), 'artifact_sha256': sha256(raw).hexdigest(),
            'function_name': '_data_quote_view', 'module': relevance_frames.__name__,
            'loaded_function_code_sha256': loaded_sha,
            'loaded_alias_matches_module': True, 'loaded_code_matches_artifact': True}


def _accepted_role_classifier():
    path = Path(facet_contracts.__file__).resolve()
    if path != Path(__file__).resolve().with_name('facet_contracts.py'):
        raise ProofError('UNSUPPORTED_ROLE_CLASSIFIER_ARTIFACT')
    raw = path.read_bytes()
    loaded = _loaded_role_codes()
    function = getattr(facet_contracts, 'contract_matches', None)
    if not isinstance(function, FunctionType):
        raise ProofError('UNVERIFIED_LOADED_ROLE_CLASSIFIER')
    code = function.__code__
    if not isinstance(code, CodeType):
        raise ProofError('UNVERIFIED_LOADED_ROLE_CLASSIFIER')
    filename = code.co_filename
    if Path(filename).resolve() != path:
        raise ProofError('UNVERIFIED_LOADED_ROLE_CLASSIFIER')
    # 编译只用于核对本进程已加载的角色函数与当前接受的源码字节，不执行另一个分类器。
    compiled = compile(raw, filename, 'exec', dont_inherit=True)
    source_codes = {code.co_name: _code_sha(code)
                    for code in compiled.co_consts if isinstance(code, CodeType)}
    if any(source_codes.get(name) != checksum for name, checksum in loaded.items()):
        raise ProofError('ROLE_CLASSIFIER_CODE_ARTIFACT_MISMATCH')
    lexical_path = Path(source_identity.lexical.__file__).resolve()
    if lexical_path != Path(__file__).resolve().with_name('source_identity_lexical.py'):
        raise ProofError('UNSUPPORTED_IDENTITY_LEXICAL_ARTIFACT')
    return {'artifact_path': str(path), 'artifact_sha256': sha256(raw).hexdigest(),
            'fingerprint_schema': 'python-code-canonical-json/1',
            'loaded_function_code_sha256': loaded, 'loaded_code_matches_artifact': True,
            'loaded_regex_constants': {'BEHAVIOR': _accepted_behavior_regex(raw)},
            'quote_view_helper': _accepted_quote_view_helper(),
            'identity_validator': _accepted_identity_classifier(),
            'identity_lexical_helper': source_identity.lexical.accepted_fingerprint(),
            'identity_lexical_artifact_path': str(lexical_path)}


def exact_identity(value):
    return value.strip() if isinstance(value, str) and IDENTITY.fullmatch(value.strip()) else None


def _same_identity(request, declared):
    # Bare requests enumerate a source-local identity; qualified owners never merge.
    return request == declared or ('.' not in request and ':' not in request and
                                  request == declared.rsplit('.', 1)[-1].rsplit(':', 1)[-1])


def _read_document(path, schema):
    raw = path.read_bytes()
    value = json.loads(raw)
    if value.get('schema_version') != schema:
        raise ProofError('UNSUPPORTED_CONTEXT_CATALOG_SCHEMA')
    return value, sha256(raw).hexdigest()


def bounded_context_navigation(record, claim_index, ref, original_node, original_artifact):
    """Build context-only navigation from an already hash-accepted exact node.

    The service calls this only after canonical artifact-byte validation. The
    original locator and original source-scope metadata must independently agree.
    """
    try:
        if type(claim_index) is not int or claim_index < 0:
            return []
        claim = record['claims'][claim_index]
        own = {ref_key(value) for value in claim.get('evidence_refs', [])}
        if ref_key(ref) not in own or claim.get('kind') not in ('NSF', 'EI', 'REC', 'UNK'):
            return []
        node = original_node
        if (not isinstance(node, dict) or at(original_artifact, ref['pointer']) != node or
                any(isinstance(value, (dict, list)) for value in node.values()) or
                not facet_contracts._bounded_source_label(node.get('symbol')) or
                not isinstance(node.get('path'), str) or not node['path'] or
                type(node.get('line_start')) is not int or node['line_start'] <= 0 or
                type(node.get('line_end')) is not int or node['line_end'] < node['line_start'] or
                not all(isinstance(node.get(field), str) and re.fullmatch(r'[0-9a-fA-F]{64}', node[field])
                        for field in ('file_sha256', 'range_sha256'))):
            return []
        scope = record.get('scope', {})
        if not isinstance(scope, dict):
            return []
        source_scopes = [row for row in scope.get('source_scopes', []) if isinstance(row, dict) and
                         isinstance(row.get('scope_ref'), dict) and
                         all(row['scope_ref'].get(field) == ref[field] for field in ('artifact_path', 'sha256'))]
        source_locators = [row for row in scope.get('source_locators', []) if isinstance(row, dict) and
                           row.get('citation_ref') == triple(ref)]
        compatible = []
        for source_scope in source_scopes:
            if (not isinstance(at(original_artifact, source_scope['scope_ref']['pointer']), dict) or
                    not isinstance(source_scope.get('snapshot_id'), str) or not source_scope['snapshot_id'] or
                    not isinstance(source_scope.get('source_commit'), str) or not source_scope['source_commit']):
                continue
            original_snapshots = [original_artifact[field] for field in
                                  ('snapshot_id', 'source_snapshot_id', 'baseline_snapshot_id')
                                  if field in original_artifact]
            if (any(value != source_scope['snapshot_id'] for value in original_snapshots) or
                    original_artifact.get('source_commit', source_scope['source_commit']) != source_scope['source_commit']):
                continue
            for locator in source_locators:
                if (locator.get('source_path') == node['path'] and locator.get('symbol') == node['symbol'] and
                        all(locator.get(field) == node[field]
                            for field in ('line_start', 'line_end', 'file_sha256', 'range_sha256')) and
                        locator.get('snapshot_id') == source_scope['snapshot_id'] and
                        locator.get('commit') == source_scope['source_commit'] and
                        node.get('commit') == source_scope['source_commit']):
                    compatible.append(source_scope)
        if len({digest(row['scope_ref']) for row in compatible}) != 1:
            return []
        source_scope = compatible[0]
        pointer = '/claims/' + str(claim_index)
        proof = {'schema': 'original-bounded-source-leaf/1',
                 'precision': 'EXACT_SOURCE_RANGE_CONTEXT_ONLY', 'source_label': node['symbol'],
                 'source_file': node['path'],
                 **{field: node[field] for field in ('line_start', 'line_end', 'file_sha256', 'range_sha256')},
                 'snapshot_id': source_scope['snapshot_id'], 'source_commit': source_scope['source_commit'],
                 'original_source_scope_ref': triple(source_scope['scope_ref']),
                 'original_scope': copy.deepcopy(scope), **triple(ref),
                 'record_sha256': digest(record), 'record_pointer': pointer,
                 'claim_kind': claim['kind'], 'whole_statement_sha256': digest(claim['statement']),
                 'single_locator_node': True, 'single_operation_verified': False,
                 'artifact_integrity_verified': True, 'original_source_value_sha256': digest(node)}
        return [{'symbol': '', 'source_label': node['symbol'], 'record_pointer': pointer,
                 'source_file': node['path'], 'context_only': True,
                 **triple(ref), 'source_context_proof': proof}]
    except (ProofError, KeyError, IndexError, TypeError, ValueError):
        return []


class VerifiedSourceContext:
    __slots__ = ('_record_digest', '_payload', '_seal')

    def __init__(self, record_sha, payload, seal):
        if seal is not _SEAL:
            raise ProofError('UNVERIFIED_SOURCE_CONTEXT')
        self._record_digest, self._payload, self._seal = record_sha, copy.deepcopy(payload), seal

    def render(self, record):
        if self._seal is not _SEAL or digest(record) != self._record_digest:
            raise ProofError('CONTEXT_RECORD_MISMATCH')
        return copy.deepcopy(self._payload)


def context_payload(record, verified):
    if not isinstance(verified, VerifiedSourceContext):
        raise ProofError('UNVERIFIED_SOURCE_CONTEXT')
    return verified.render(record)


class SourceContextRegistry:
    """Service-owned accepted root/epoch and exact-ref whitelist; no rank changes."""
    def __init__(self, root, epoch, snapshot_check=None):
        self.root = Path(root).resolve()
        self.source_environment = active_epoch()
        if self.source_environment is not None and self.source_environment.root != self.root:
            raise ProofError('SOURCE_EPOCH_ROOT_MISMATCH')
        self.epoch = str(epoch)
        self.snapshot_check = snapshot_check
        self._active = True
        self._catalogs, self._files = {}, {}
        if self.source_environment is not None:
            self._files.update({Path(path).resolve(): checksum
                                for path, checksum in self.source_environment.commitments})
        for family, relative, schema in (
            ('core', 'data/nativecore/native-core.json', 'native-core-governance/1'),
            ('n001', 'data/native001/canonical-native001-ai-knowledge.json', 'native-ai-1.0'),
            ('research', 'data/native001/canonical-native001-research-map.json', 'native-research-map-1.0')):
            path = self.root / relative
            document, checksum = _read_document(path, schema)
            self._catalogs[family] = document
            self._files[path] = checksum
        self._records = {family: {r['id']: r for r in self._catalogs[family]['entries']}
                         for family in ('core', 'n001')}
        self._research = {r['canonical_id']: r for r in self._catalogs['research']['entries']}
        self._research_pointers = {r['canonical_id']: '/entries/' + str(i)
                                   for i, r in enumerate(self._catalogs['research']['entries'])}
        self._map_path = (self.source_environment.contract_map if self.source_environment is not None
                          else Path(__file__).with_name('contract_map.json'))
        raw = self._map_path.read_bytes()
        self._maps = json.loads(raw)['records']
        self._files[self._map_path] = sha256(raw).hexdigest()
        identity_map_path = (self.source_environment.source_identity_map if self.source_environment is not None
                             else source_identity.MAP_PATH)
        for path in (Path(source_identity.__file__).resolve(), identity_map_path):
            self._files[path] = sha256(path.read_bytes()).hexdigest()
        self._role_classifier = _accepted_role_classifier()
        self._files[Path(self._role_classifier['artifact_path'])] = self._role_classifier['artifact_sha256']
        self._files[Path(self._role_classifier['identity_lexical_artifact_path'])] = (
            self._role_classifier['identity_lexical_helper']['artifact_sha256'])

    def clear(self):
        self._active = False

    def _envelope(self, record, status, atoms=(), reasons=()):
        return VerifiedSourceContext(digest(record), {
            'source_context_schema': SCHEMA, 'source_context': list(atoms),
            'source_context_status': status, 'source_context_rejections': list(reasons),
            'source_context_notice': NOTICE, 'source_context_is_method_contract': False,
            'source_context_verifies_task_answer': False,
        }, _SEAL)

    def _current(self):
        current_environment = active_epoch()
        source_environment = getattr(self, 'source_environment', None)
        same_environment = ((current_environment is None and source_environment is None) or
                            (current_environment is not None and source_environment is not None and
                             current_environment.cache_key == source_environment.cache_key))
        return (same_environment and self._active and (self.snapshot_check is None or self.snapshot_check()) and
                _loaded_role_codes() == self._role_classifier['loaded_function_code_sha256'] and
                _accepted_behavior_regex(Path(self._role_classifier['artifact_path']).read_bytes()) ==
                    self._role_classifier['loaded_regex_constants']['BEHAVIOR'] and
                _accepted_quote_view_helper() == self._role_classifier['quote_view_helper'] and
                _accepted_identity_classifier() == self._role_classifier['identity_validator'] and
                source_identity.lexical.accepted_fingerprint() == self._role_classifier['identity_lexical_helper'] and
                all(sha256(p.read_bytes()).hexdigest() == h for p, h in self._files.items()))

    def _current_role_matches(self, record, identity):
        return facet_contracts.contract_matches(record, 'core', identity)

    def _core_derived_fact(self, record, pointer, declaration, reader):
        claim = at(record, pointer)
        scope = record.get('scope', {})
        reference = declaration['reference']
        own = {ref_key(ref): ref for ref in claim.get('evidence_refs', [])}
        if (not isinstance(scope, dict) or ref_key(reference) not in own or
                not isinstance(scope.get('snapshot_id'), str) or not scope['snapshot_id']):
            return None
        leaf = reader.read(reference)
        if (not isinstance(leaf, dict) or digest(leaf) != declaration['artifact_value_sha256'] or
                any(leaf.get(left) != declaration.get(right) for left, right in (
                    ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                    ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'),
                    ('line_end', 'line_end')))):
            return None
        # 新格式只按已知原 schema 接纳；声明和相同文字都不能独自构成整条原事实。
        if reader.root_schema(reference) != {'schema_version': 'native005.scoped-ui-complete.v1'}:
            return None
        metadata = {}
        for name in ('source_commit', 'repository'):
            ref = {**triple(reference), 'pointer': '/' + name}
            if ref_key(ref) not in own:
                return None
            metadata[name] = reader.read(ref)
        if (not isinstance(metadata['source_commit'], str) or
                not re.fullmatch(r'[0-9a-f]{40}', metadata['source_commit']) or
                not isinstance(metadata['repository'], str) or not metadata['repository'].strip() or
                metadata['source_commit'] != scope.get('source_commit') or
                leaf.get('commit') != metadata['source_commit'] or
                metadata['repository'] != scope.get('source_repository') or
                leaf.get('repository') != metadata['repository']):
            return None
        facts = []
        for ref in claim.get('evidence_refs', []):
            if (ref['artifact_path'] != reference['artifact_path'] or ref['sha256'] != reference['sha256'] or
                    not re.fullmatch(r'/reviewer_facts/(0|[1-9][0-9]*)', ref['pointer'])):
                continue
            child = re.fullmatch(re.escape(ref['pointer']) + r'/citations/(0|[1-9][0-9]*)', reference['pointer'])
            if child is None:
                continue
            fact = reader.read(ref)
            if (not isinstance(fact, dict) or fact.get('classification') != 'DirectLuaSourceFact' or
                    not isinstance(fact.get('fact_id'), str) or not fact['fact_id'] or
                    claim.get('kind') != 'NSF' or fact.get('statement') != claim.get('statement') or
                    not isinstance(fact.get('scope'), str) or not fact['scope'] or
                    not isinstance(fact.get('citations'), list) or
                    not isinstance(scope.get('original_fact_ids'), list) or
                    fact['fact_id'] not in scope['original_fact_ids'] or
                    not isinstance(scope.get('original_fact_statements'), dict) or
                    scope['original_fact_statements'].get(fact['fact_id']) != fact['statement']):
                continue
            index = int(child[1])
            if index >= len(fact['citations']) or fact['citations'][index] != leaf:
                continue
            facts.append((ref, fact))
        if len(facts) != 1:
            return None
        whole_ref, fact = facts[0]
        return {'references': [{'reference': triple(whole_ref), 'value_sha256': digest(fact)},
                               {'reference': triple(reference), 'value_sha256': digest(leaf)}],
                'scope': {'schema': 'original-reviewer-fact-context/1',
                          'original_fact_ref': triple(whole_ref), 'fact_id': fact['fact_id'],
                          'source_schema': 'native005.scoped-ui-complete.v1',
                          'scope': copy.deepcopy(fact['scope']), **metadata,
                          'snapshot_id': scope['snapshot_id']},
                'lineage': {'original_fact_ref': triple(whole_ref), 'original_fact_sha256': digest(fact),
                            'original_fact_id': fact['fact_id'], 'classification': fact['classification'],
                            'exact_citation_ref': triple(reference)}}

    def _core_steam_fact(self, record, pointer, declaration, reader):
        """One whole NSF, not a translation, summary, or arbitrary null-commit fact."""
        claim = at(record, pointer)
        reference = declaration['reference']
        whole_ref = declaration.get('whole_fact_reference', {})
        scope_ref = declaration.get('source_scope_reference', {})
        own = {ref_key(ref) for ref in claim.get('evidence_refs', [])}
        child = re.fullmatch(r'(/facts/(?:0|[1-9][0-9]*))/citations/(0|[1-9][0-9]*)',
                             reference.get('pointer', ''))
        if (not child or whole_ref.get('pointer') != child[1] or scope_ref.get('pointer') != '/source_scope' or
                any(ref_key(ref) not in own for ref in (reference, whole_ref, scope_ref)) or
                any(any(ref.get(key) != reference.get(key) for key in ('artifact_path', 'sha256'))
                    for ref in (whole_ref, scope_ref)) or reader.root_schema(reference) != STEAM_WHOLE_SCHEMA):
            return None
        leaf, fact, scope = (reader.read(ref) for ref in (reference, whole_ref, scope_ref))
        if (not isinstance(fact, dict) or not isinstance(scope, dict) or not isinstance(leaf, dict) or
                claim.get('kind') != 'NSF' or fact.get('kind') != 'NSF' or
                fact.get('classification') != 'DirectLuaSourceFact' or
                fact.get('statement') != claim.get('statement') or fact.get('source_scope') != scope or
                digest(leaf) != declaration.get('artifact_value_sha256') or
                digest(fact) != declaration.get('whole_fact_value_sha256') or
                digest(scope) != declaration.get('source_scope_sha256') or
                not isinstance(fact.get('citations'), list) or not fact['citations'] or
                int(child[2]) >= len(fact['citations']) or fact['citations'][int(child[2])] != leaf or
                any(value.get(flag) is True for value in (fact, scope) for flag in
                    ('runtime_verified', 'runtime_game_verified', 'runtime_tested'))):
            return None
        citations = fact['citations']
        version = source_identity.steam_source_version(scope, citations)
        if version is None:
            return None
        bindings = [row for row in record.get('scope', {}).get('source_scopes', [])
                    if isinstance(row, dict) and row.get('scope_ref') == scope_ref]
        if (not bindings or len({digest(row) for row in bindings}) != 1 or
                any(row.get('source_commit', object()) is not None or
                    row.get('game_version_txt', row.get('game_version')) != version['game_version'] or
                    any(row.get(key) != version[key] for key in
                        ('snapshot_id', 'source_epoch_id', 'archive_sha256', 'steam_buildid'))
                    for row in bindings)):
            return None
        refs = [{'reference': triple(whole_ref), 'value_sha256': digest(fact)},
                {'reference': triple(scope_ref), 'value_sha256': digest(scope)}]
        for index, citation in enumerate(citations):
            ref = {**triple(whole_ref), 'pointer': whole_ref['pointer'] + '/citations/' + str(index)}
            if ref_key(ref) not in own or reader.read(ref) != citation:
                return None
            refs.append({'reference': ref, 'value_sha256': digest(citation)})
        return {'references': refs,
                'scope': {'schema': 'original-steam-whole-nsf-context/1',
                    'original_fact_ref': triple(whole_ref), 'original_source_scope_ref': triple(scope_ref),
                    'source_schema': STEAM_WHOLE_SCHEMA['schema'], 'scope': copy.deepcopy(scope),
                    'original_fact_limits': {key: copy.deepcopy(fact[key]) for key in
                        ('conditions', 'limits', 'limitations', 'not_proven', 'does_not_prove',
                         'runtime_verified', 'runtime_game_verified', 'runtime_tested') if key in fact},
                    **version},
                'lineage': {'original_fact_ref': triple(whole_ref), 'original_fact_sha256': digest(fact),
                    'classification': fact['classification'], 'claim_kind': 'NSF',
                    'exact_citation_ref': triple(reference), 'source_scope_ref': triple(scope_ref)}}

    def _core_steam_context(self, record, identity, reader):
        declared = source_identity.resolve_identity(record, 'core', identity)
        if not declared or not _same_identity(identity, declared) or ('.' not in declared and ':' not in declared):
            return []
        owner = declared.rsplit(':', 1)[0] if ':' in declared else declared.rsplit('.', 1)[0]
        matches = [match for match in self._current_role_matches(record, declared)
                   if match.get('symbol') == declared and match.get('receiver') == owner and
                   match.get('record_sha256') == digest(record) and
                   match.get('original_scope') == record.get('scope', {})]
        if len(matches) != 1:
            return []
        match, = matches
        declarations = source_identity.identity_bindings(record, 'core', declared)
        atoms = []
        for pointer in match.get('record_pointers', []):
            if not re.fullmatch(r'/claims/(0|[1-9][0-9]*)', pointer):
                continue
            claim, role = at(record, pointer), match.get('pointer_roles', {}).get(pointer, {})
            if (claim.get('kind') != 'NSF' or role.get('claim_kind') != 'NSF' or
                    role.get('role') != 'METHOD_SUBJECT' or role.get('callee_semantics_supported') is not True):
                continue
            current_refs = {ref_key(ref) for ref in match.get('source_bindings', {}).get(pointer, [])}
            accepted, contexts = [], {}
            for proof in declarations:
                if (proof.get('schema') != source_identity.STEAM_SCHEMA or
                        proof.get('proof_kind') != source_identity.STEAM_KIND or
                        proof.get('record_sha256') != digest(record) or proof.get('record_pointer') != pointer or
                        proof.get('declared_symbol') != declared or proof.get('owner') != owner or
                        proof.get('claim_kind') != 'NSF' or proof.get('statement_sha256') != digest(claim['statement']) or
                        ref_key(proof['reference']) not in current_refs):
                    continue
                context = self._core_steam_fact(record, pointer, proof, reader)
                if context is not None:
                    accepted.append(copy.deepcopy(proof))
                    contexts[ref_key(context['lineage']['original_fact_ref'])] = context
            if len(contexts) != 1:
                continue
            context, = contexts.values()
            binding = {'verification_basis': 'CURRENT_ROLE_AND_EXACT_COMMITTED_STEAM_WHOLE_NSF',
                'identity': declared, 'owner': owner,
                'verified_source_role': {'role': role['role'], 'claim_kind': 'NSF',
                    'record_pointer': pointer, 'qualified_identity': declared, 'owner': owner,
                    'whole_statement_sha256': digest(claim['statement']), 'role_value_sha256': digest(role)},
                'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                    'current_match_sha256': digest(match), 'record_sha256': digest(record),
                    'declaration_identity_proofs': accepted},
                'context_is_method_contract': False, 'callee_semantics_supported': False,
                'full_method_contract_verified': False}
            atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT',
                context['references'], [context['scope']], binding, [context['lineage']]))
        return atoms

    def _core_derived_context(self, record, identity, reader):
        declared = source_identity.resolve_identity(record, 'core', identity)
        if not declared or ('.' not in declared and ':' not in declared):
            return []
        owner = declared.rsplit(':', 1)[0] if ':' in declared else declared.rsplit('.', 1)[0]
        matches = [match for match in self._current_role_matches(record, declared)
                   if match.get('symbol') == declared and match.get('receiver') == owner and
                   match.get('record_sha256') == digest(record) and
                   match.get('original_scope') == record.get('scope', {})]
        if len(matches) != 1:
            return []
        match = matches[0]
        declarations = source_identity.identity_bindings(record, 'core', declared)
        atoms = []
        for pointer in match.get('record_pointers', []):
            if not re.fullmatch(r'/claims/(0|[1-9][0-9]*)', pointer):
                continue
            claim = at(record, pointer)
            role = match.get('pointer_roles', {}).get(pointer, {})
            local = role.get('local_subject_relation', {})
            if (claim.get('kind') != 'NSF' or role.get('claim_kind') != 'NSF' or
                    role.get('role') != 'METHOD_SUBJECT' or role.get('callee_semantics_supported') is not True or
                    local.get('schema') != 'original-declared-local-subject/1' or
                    local.get('same_original_atom_and_reference') is not True or
                    local.get('qualified_identity') != declared or local.get('owner') != owner):
                continue
            current_refs = {ref_key(binding) for binding in match.get('source_bindings', {}).get(pointer, [])}
            accepted, fact_contexts = [], []
            for proof in declarations:
                if (proof.get('record_sha256') != digest(record) or proof.get('record_pointer') != pointer or
                        proof.get('declared_symbol') != declared or proof.get('owner') != owner or
                        proof.get('claim_kind') != 'NSF' or proof.get('statement_sha256') != digest(claim['statement']) or
                        ref_key(proof['reference']) not in current_refs):
                    continue
                context = self._core_derived_fact(record, pointer, proof, reader)
                if context is not None:
                    accepted.append(proof)
                    fact_contexts.append(context)
            if not fact_contexts:
                continue
            refs, scopes, lineage = [], [], []
            for context in fact_contexts:
                for ref in context['references']:
                    if ref not in refs:
                        refs.append(ref)
                if context['scope'] not in scopes:
                    scopes.append(context['scope'])
                if context['lineage'] not in lineage:
                    lineage.append(context['lineage'])
            # 当前派生证明独立于历史 map；不生成一个并不存在的历史角色。
            binding = {'verification_basis': 'CURRENT_DERIVED_ROLE_AND_EXACT_ORIGINAL_FACT',
                       'identity': declared, 'owner': owner,
                       'verified_source_role': {'role': role['role'], 'claim_kind': 'NSF',
                           'record_pointer': pointer, 'qualified_identity': declared, 'owner': owner,
                           'whole_statement_sha256': digest(claim['statement']), 'role_value_sha256': digest(role),
                           'local_subject_relation': copy.deepcopy(local)},
                       'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                           'current_match_sha256': digest(match), 'record_sha256': digest(record),
                           'declaration_identity_proofs': copy.deepcopy(accepted)},
                       'context_is_method_contract': False, 'callee_semantics_supported': False,
                       'full_method_contract_verified': False}
            atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT',
                                    refs, scopes, binding, lineage))
        return atoms

    def _core_original_subject_fact(self, record, pointer, declaration, reader):
        claim, scope = at(record, pointer), record.get('scope', {})
        reference, whole_ref = declaration['reference'], declaration.get('whole_fact_reference', {})
        own = {ref_key(ref): ref for ref in claim.get('evidence_refs', [])}
        child = re.fullmatch(r'(/reused_direct_facts/(?:0|[1-9][0-9]*))/citations/(0|[1-9][0-9]*)', reference['pointer'])
        if (not child or child[1] != whole_ref.get('pointer') or ref_key(whole_ref) not in own or
                ref_key(reference) not in own or any(whole_ref.get(k) != reference[k] for k in ('artifact_path', 'sha256')) or
                reader.root_schema(reference) != {'schema_version': 'native005.scoped-ui-complete.v1'}):
            return None
        leaf, fact = reader.read(reference), reader.read(whole_ref)
        root = reader._documents[reference['artifact_path']]
        original_scope = root.get('scope')
        if (not isinstance(leaf, dict) or not isinstance(fact, dict) or not isinstance(original_scope, dict) or
                digest(leaf) != declaration['artifact_value_sha256'] or digest(fact) != declaration['whole_fact_value_sha256'] or
                digest(original_scope) != declaration['artifact_scope_sha256'] or
                original_scope != scope.get('original_source_scope') or claim.get('kind') != 'NSF' or
                fact.get('classification') != 'DirectLuaSourceFact' or fact.get('kind') != 'reused_direct_source_fact' or
                fact.get('new_fact') is not False or fact.get('runtime_tested') is not False or
                fact.get('statement') != claim.get('statement') or not isinstance(fact.get('fact_id'), str) or
                not fact['fact_id'] or fact['fact_id'] not in scope.get('original_fact_ids', []) or
                scope.get('original_fact_statements', {}).get(fact['fact_id']) != claim['statement'] or
                not isinstance(fact.get('citations'), list) or not fact['citations'] or
                int(child[2]) >= len(fact['citations']) or fact['citations'][int(child[2])] != leaf or
                any(leaf.get(a) != declaration.get(b) for a, b in (
                    ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                    ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'), ('line_end', 'line_end')))):
            return None
        refs = [{'reference': triple(whole_ref), 'value_sha256': digest(fact)}]
        metadata = {}
        for name in ('source_commit', 'repository'):
            ref = {**triple(reference), 'pointer': '/' + name}
            if ref_key(ref) not in own:
                return None
            metadata[name] = reader.read(ref)
            refs.append({'reference': triple(ref), 'value_sha256': digest(metadata[name])})
        if (not isinstance(metadata['repository'], str) or not re.fullmatch(r'[^\s/]+/[^\s/]+', metadata['repository']) or
                not isinstance(metadata['source_commit'], str) or not re.fullmatch(r'[0-9a-f]{40}', metadata['source_commit']) or
                metadata['repository'] != scope.get('source_repository') or
                metadata['repository'] != declaration.get('source_repository') or
                metadata['source_commit'] != scope.get('source_commit') or
                metadata['source_commit'] != declaration.get('source_commit')):
            return None
        for index, citation in enumerate(fact['citations']):
            ref = {**triple(whole_ref), 'pointer': whole_ref['pointer'] + '/citations/' + str(index)}
            if (ref_key(ref) not in own or not isinstance(citation, dict) or reader.read(ref) != citation or
                    citation.get('repository') != metadata['repository'] or citation.get('commit') != metadata['source_commit'] or
                    not isinstance(citation.get('path'), str) or not citation['path'] or
                    type(citation.get('line_start')) is not int or citation['line_start'] <= 0 or
                    type(citation.get('line_end')) is not int or citation['line_end'] < citation['line_start'] or
                    not all(isinstance(citation.get(field), str) and re.fullmatch(r'[0-9a-f]{64}', citation[field])
                            for field in ('file_sha256', 'range_sha256'))):
                return None
            refs.append({'reference': triple(ref), 'value_sha256': digest(citation)})
        snapshot_ref = scope.get('snapshot_source', {})
        if (not isinstance(snapshot_ref, dict) or snapshot_ref.get('pointer') != '/snapshot_id' or
                ref_key(snapshot_ref) not in own or reader.root_schema(snapshot_ref) != {'schema_version': '1.0'} or
                not isinstance(scope.get('snapshot_id'), str) or not scope['snapshot_id'] or
                reader.read(snapshot_ref) != scope['snapshot_id']):
            return None
        if isinstance(fact.get('origin'), dict) and fact['origin'].get('artifact_sha256') != snapshot_ref['sha256']:
            return None
        refs.append({'reference': triple(snapshot_ref), 'value_sha256': digest(scope['snapshot_id'])})
        source_scope_ref = {**triple(reference), 'pointer': '/scope'}
        refs.append({'reference': source_scope_ref, 'value_sha256': digest(original_scope)})
        return {'references': refs,
                'scope': {'schema': 'original-reused-fact-context/1', 'original_fact_ref': triple(whole_ref),
                    'original_source_scope_ref': source_scope_ref, 'scope': copy.deepcopy(original_scope),
                    'source_schema': 'native005.scoped-ui-complete.v1', 'snapshot_id': scope['snapshot_id'], **metadata},
                'lineage': {'original_fact_ref': triple(whole_ref), 'original_fact_id': fact['fact_id'],
                    'original_fact_sha256': digest(fact), 'classification': fact['classification'],
                    'source_fact_kind': fact['kind'], 'exact_citation_ref': triple(reference),
                    'snapshot_source_ref': triple(snapshot_ref)}}

    def _core_original_subject_context(self, record, identity, reader):
        if (not (':' in identity or '.' in identity) or
                source_identity.resolve_identity(record, 'core', identity) != identity):
            return []
        owner = identity.rsplit(':', 1)[0] if ':' in identity else identity.rsplit('.', 1)[0]
        matches = [match for match in self._current_role_matches(record, identity)
                   if match.get('symbol') == identity and match.get('receiver') == owner and
                   match.get('record_sha256') == digest(record) and match.get('original_scope') == record.get('scope', {})]
        if len(matches) != 1:
            return []
        match, = matches
        atoms = []
        for pointer in match.get('record_pointers', []):
            claim = at(record, pointer)
            role = match.get('pointer_roles', {}).get(pointer, {})
            relation = role.get('original_subject_relation', {})
            if (claim.get('kind') != 'NSF' or role.get('role') != 'METHOD_SUBJECT' or
                    role.get('callee_semantics_supported') is not True or
                    relation.get('schema') != 'original-pinned-nsf-subject-relation/1' or
                    relation.get('record_pointer') != pointer or relation.get('qualified_identity') != identity or
                    relation.get('owner') != owner or relation.get('whole_statement_sha256') != digest(claim['statement'])):
                continue
            current_refs = {ref_key(binding) for binding in match.get('source_bindings', {}).get(pointer, [])}
            accepted, contexts = [], []
            for proof in source_identity.identity_bindings(record, 'core', identity):
                if (proof.get('schema') != 'accepted-original-subject-declaration-identity/1' or
                        proof.get('proof_kind') != 'ORIGINAL_NSF_SUBJECT_IN_PINNED_CITATION_RANGE' or
                        proof.get('record_pointer') != pointer or proof.get('owner') != owner or
                        proof.get('declared_symbol') != identity or proof.get('aliases') != [identity] or
                        proof.get('subject_witness') != relation.get('subject_witness') or
                        digest(proof) not in relation.get('accepted_declaration_sha256', []) or
                        ref_key(proof['reference']) not in current_refs):
                    continue
                context = self._core_original_subject_fact(record, pointer, proof, reader)
                if context is not None:
                    accepted.append(copy.deepcopy(proof))
                    contexts.append(context)
            if not contexts:
                continue
            refs, scopes, lineage = [], [], []
            for context in contexts:
                for ref in context['references']:
                    if ref not in refs:
                        refs.append(ref)
                if context['scope'] not in scopes:
                    scopes.append(context['scope'])
                if context['lineage'] not in lineage:
                    lineage.append(context['lineage'])
            binding = {'verification_basis': 'CURRENT_ORIGINAL_SUBJECT_AND_EXACT_REUSED_FACT',
                       'identity': identity, 'owner': owner,
                       'verified_source_role': {'role': 'METHOD_SUBJECT', 'claim_kind': 'NSF',
                           'record_pointer': pointer, 'qualified_identity': identity, 'owner': owner,
                           'whole_statement_sha256': digest(claim['statement']),
                           'original_subject_relation': copy.deepcopy(relation)},
                       'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                           'current_match_sha256': digest(match), 'record_sha256': digest(record),
                           'declaration_identity_proofs': accepted},
                       'context_is_method_contract': False, 'callee_semantics_supported': False,
                       'full_method_contract_verified': False}
            atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT', refs, scopes, binding, lineage))
        return atoms

    def _core_qualified_getter_context(self, record, identity):
        candidates = facet_contracts._qualified_getter_context(record, 'core', identity)
        if not candidates:
            return []
        scope = record.get('scope', {})
        scope_rows = [row for row in scope.get('source_scopes', []) if isinstance(row, dict)
                      and isinstance(row.get('scope_ref'), dict)]
        atoms, seen = [], set()
        for candidate in candidates:
            pointer = candidate['record_pointer']
            claim = at(record, pointer)
            declaration = candidate['declaration_identity_proof']
            own = {ref_key(ref): ref for ref in claim.get('evidence_refs', [])}
            reference = declaration['reference']
            if (candidate.get('record_sha256') != digest(record) or claim.get('kind') != 'NSF' or
                    candidate.get('whole_statement_sha256') != digest(claim['statement']) or
                    ref_key(reference) not in own or pointer in seen):
                continue
            reader = ExactSourceReader(self.root, self._catalogs['core'].get('source_artifacts', []),
                                       list(own.values()) + [row['scope_ref'] for row in scope_rows])
            leaf = reader.read(reference)
            if (reader.root_schema(reference) != {'schema_version': '1.0'} or not isinstance(leaf, dict) or
                    digest(leaf) != declaration['artifact_value_sha256'] or
                    any(leaf.get(left) != declaration.get(right) for left, right in (
                        ('path', 'source_file'), ('file_sha256', 'cited_file_sha256'),
                        ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'), ('line_end', 'line_end')))):
                continue
            # root 来自同一 ExactSourceReader 已逐字节验 SHA 的原文档快照。
            root = reader._documents[reference['artifact_path']]
            repository, commit, snapshot = (root.get(key) for key in
                ('source_repository', 'source_commit', 'baseline_snapshot_id'))
            if (not isinstance(repository, str) or not repository.strip() or
                    not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit) or
                    not isinstance(snapshot, str) or not snapshot or not isinstance(root.get('scope'), dict) or
                    not isinstance(root.get('direct_facts'), list) or not isinstance(root.get('citations'), list)):
                continue
            same_artifact = lambda ref: isinstance(ref, dict) and all(
                ref.get(field) == reference[field] for field in ('artifact_path', 'sha256'))
            compatible = [row for row in scope_rows if same_artifact(row['scope_ref']) and
                          row['scope_ref']['pointer'] == '/scope' and row.get('source_commit') == commit
                          and row.get('snapshot_id') == snapshot]
            if len({digest(row['scope_ref']) for row in compatible}) != 1:
                continue
            source_scope_ref = compatible[0]['scope_ref']
            source_scope = reader.read(source_scope_ref)

            def valid_citation(ref, node):
                if (not isinstance(node, dict) or not isinstance(node.get('id'), str) or not node['id'] or
                        node.get('repository') != repository or node.get('commit') != commit or
                        not isinstance(node.get('path'), str) or not node['path'] or
                        not isinstance(node.get('symbol'), str) or not node['symbol'] or
                        type(node.get('line_start')) is not int or node['line_start'] <= 0 or
                        type(node.get('line_end')) is not int or node['line_end'] < node['line_start'] or
                        not all(isinstance(node.get(field), str) and re.fullmatch(r'[0-9a-f]{64}', node[field])
                                for field in ('file_sha256', 'range_sha256'))):
                    return False
                locators = [row for row in scope.get('source_locators', []) if isinstance(row, dict)
                            and row.get('citation_ref') == triple(ref) and row.get('snapshot_id') == snapshot
                            and row.get('commit') == commit and row.get('source_path') == node.get('path')
                            and row.get('symbol') == node.get('symbol') and all(row.get(field) == node.get(field)
                                for field in ('line_start', 'line_end', 'file_sha256', 'range_sha256'))]
                return len({digest(row) for row in locators}) == 1

            if not valid_citation(reference, leaf):
                continue
            contexts = []
            for disposition in scope.get('typed_fact_dispositions', []):
                if (not isinstance(disposition, dict) or disposition.get('disposition') != 'canonical_typed_claim'
                        or 'NSF' not in disposition.get('kinds', [])):
                    continue
                ref = disposition.get('fact_ref', {})
                if (not same_artifact(ref) or ref_key(ref) not in own or
                        not re.fullmatch(r'/direct_facts/(0|[1-9][0-9]*)', ref['pointer'])):
                    continue
                fact = reader.read(ref)
                if (not isinstance(fact, dict) or fact.get('classification') != 'DirectSourceFact_NarrowGetterBoundary'
                        or not isinstance(fact.get('id'), str) or not fact['id'] or
                        fact['id'] != disposition.get('fact_id') or fact.get('statement_zh') != claim['statement'] or
                        not isinstance(fact.get('citation_ids'), list) or not fact['citation_ids'] or
                        not all(isinstance(value, str) and value for value in fact['citation_ids']) or
                        len(set(fact['citation_ids'])) != len(fact['citation_ids']) or leaf['id'] not in fact['citation_ids']):
                    continue
                citations = []
                for citation_id in fact['citation_ids']:
                    matching = []
                    for own_ref in own.values():
                        if same_artifact(own_ref) and re.fullmatch(r'/citations/(0|[1-9][0-9]*)', own_ref['pointer']):
                            node = reader.read(own_ref)
                            if isinstance(node, dict) and node.get('id') == citation_id and valid_citation(own_ref, node):
                                matching.append({'reference': triple(own_ref), 'value_sha256': digest(node)})
                    if len(matching) != 1:
                        break
                    citations.extend(matching)
                else:
                    contexts.append((ref, fact, citations))
            if len(contexts) != 1:
                continue
            ref, fact, citations = contexts[0]
            verified = {'role': 'TYPED_EVIDENCE_CONTEXT', 'record_pointer': pointer, 'claim_kind': 'NSF',
                        'qualified_identity': identity, 'owner': candidate['owner'],
                        'whole_statement_sha256': digest(claim['statement']),
                        'single_method_range_verified': False}
            binding = {'verification_basis': 'QUALIFIED_GETTER_CONTEXT_WITH_EXACT_ORIGINAL_FACT',
                       'identity': identity, 'owner': candidate['owner'], 'verified_source_role': verified,
                       'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                           'current_context_candidate_sha256': digest(candidate),
                           'declaration_identity_proofs': [copy.deepcopy(declaration)]},
                       'context_is_method_contract': False, 'callee_semantics_supported': False,
                       'full_method_contract_verified': False}
            refs = [{'reference': triple(ref), 'value_sha256': digest(fact)}, *citations,
                    {'reference': triple(source_scope_ref), 'value_sha256': digest(source_scope)}]
            lineage = {'source_schema': {'schema_version': '1.0', 'fact_classification': fact['classification']},
                       'original_fact_ref': triple(ref), 'original_fact_id': fact['id'],
                       'original_fact_sha256': digest(fact), 'original_citation_ids': copy.deepcopy(fact['citation_ids'])}
            scopes = [{'original_source_scope_ref': triple(source_scope_ref), 'scope': source_scope,
                       'snapshot_id': snapshot, 'source_commit': commit, 'source_repository': repository}]
            atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT',
                                    refs, scopes, binding, lineage))
            seen.add(pointer)
        return atoms

    def _core_comparison_context(self, record, identity):
        atoms = []
        for match in self._current_role_matches(record, identity):
            contexts = [context for context in match.get('context_pointer_bindings', [])
                        if context.get('relation') == 'EXPLICIT_QUALIFIED_ORIGINAL_COMPARISON']
            contexts, _ = facet_contracts.context_admission(record, 'core', contexts, identity)
            for context in contexts:
                pointer = context['record_pointer']
                claim = at(record, pointer)
                if (context.get('record_sha256') != digest(record) or claim.get('kind') != 'NSF' or
                        context.get('original_scope') != record.get('scope', {})):
                    continue
                references, scopes, proofs = [], [], []
                for proof in context.get('comparison_reference_proofs', []):
                    if (proof.get('schema') != 'original-explicit-qualified-comparison/1' or
                            proof.get('accepted_root') != str(self.root) or
                            proof.get('query_identity') != identity or proof.get('context_record_pointer') != pointer or
                            proof.get('context_whole_statement_sha256') != digest(claim['statement'])):
                        continue
                    owned = [ref for p in [pointer, proof['basis_record_pointer']]
                             for ref in at(record, p).get('evidence_refs', [])]
                    reader = ExactSourceReader(self.root, self._catalogs['core'].get('source_artifacts', []), owned)
                    checked = []
                    for ref in proof['references']:
                        if digest(reader.read(ref['reference'])) != ref['value_sha256']:
                            break
                        checked.append(copy.deepcopy(ref))
                    else:
                        source_scope = reader.read(proof['source_scope_ref'])
                        if digest(source_scope) != proof['source_scope_sha256']:
                            continue
                        for ref in checked:
                            if ref not in references:
                                references.append(ref)
                        scope = {'original_source_scope_ref': copy.deepcopy(proof['source_scope_ref']),
                                 'scope': source_scope, **{field: proof[field] for field in
                                     ('snapshot_id', 'source_commit', 'source_repository')}}
                        if scope not in scopes:
                            scopes.append(scope)
                        proofs.append(copy.deepcopy(proof))
                if not proofs:
                    continue
                target_identities = {proof['comparison_target_identity'] for proof in proofs}
                if len(target_identities) != 1:
                    continue
                binding = {'verification_basis': 'EXPLICIT_QUALIFIED_COMPARISON_WITH_OWN_ORIGINAL_FACTS',
                           'identity': identity, 'comparison_target_identity': next(iter(target_identities)),
                           'verified_source_role': {'role': 'TYPED_EVIDENCE_CONTEXT', 'claim_kind': 'NSF',
                               'record_pointer': pointer, 'whole_statement_sha256': digest(claim['statement'])},
                           'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                               'current_match_sha256': digest(match), 'comparison_reference_proofs': proofs},
                           'context_is_method_contract': False, 'callee_semantics_supported': False,
                           'full_method_contract_verified': False}
                lineage = {'relation': 'EXPLICIT_QUALIFIED_ORIGINAL_COMPARISON',
                           'basis_record_pointers': copy.deepcopy(context['basis_record_pointers']),
                           'source_schema': 'native004-evidence-editorial-map-1.0'}
                atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT',
                                        references, scopes, binding, lineage))
        return atoms

    def _core_current_role(self, record, pointer, declared, spec, historical, leaves):
        if '.' not in declared and ':' not in declared:
            return None, 'QUALIFIED_SOURCE_ROLE_OWNER_MISSING'
        owner = declared.rsplit(':', 1)[0] if ':' in declared else declared.rsplit('.', 1)[0]
        matches = [match for match in self._current_role_matches(record, declared)
                   if match.get('symbol') == declared and match.get('receiver') == owner
                   and match.get('record_sha256') == digest(record)
                   and pointer in match.get('record_pointers', [])]
        declared_proofs = [proof for proof in source_identity.identity_bindings(record, 'core', declared)
                           if proof['record_pointer'] == pointer and proof['owner'] == owner]
        if len(matches) != 1 or (spec.get('receiver') != owner and not declared_proofs):
            return None, 'CURRENT_SOURCE_ROLE_OWNER_OR_POINTER_UNVERIFIED'
        match = matches[0]
        role = match.get('pointer_roles', {}).get(pointer)
        if not isinstance(role, dict) or role.get('claim_kind') != 'NSF':
            return None, 'CURRENT_SOURCE_ROLE_UNVERIFIED'
        if role.get('role') != historical.get('role'):
            return None, 'CURRENT_SOURCE_ROLE_DIFFERS_FROM_STATIC_MAP'
        if role.get('role') == 'METHOD_SUBJECT':
            verified = role.get('callee_semantics_supported') is True
        elif role.get('role') == 'BOUNDED_CALLEE_CALLSITE':
            verified = (role.get('relation_polarity') == 'POSITIVE' and
                        role.get('positive_callsite_evidence') is True and
                        role.get('callee_semantics_supported') is False)
        else:
            verified = False
        if not verified or match.get('original_scope') != record.get('scope', {}):
            return None, 'CURRENT_SOURCE_ROLE_NOT_VERIFIED_FOR_CONTEXT'
        current_refs = {ref_key(binding) for binding in match.get('source_bindings', {}).get(pointer, [])
                        if binding.get('record_pointer') == pointer}
        if not all(ref_key(leaf['reference']) in current_refs for leaf in leaves):
            return None, 'CURRENT_SOURCE_ROLE_EXACT_REF_UNVERIFIED'
        escaped = lambda value: str(value).replace('~', '~0').replace('/', '~1')
        return {'identity': declared, 'owner': owner,
                'historical_static_role': {'value': copy.deepcopy(historical), 'value_sha256': digest(historical),
                    'map_pointer': '/records/' + escaped(record['id']) + '/contracts/' + escaped(spec.get('original_contract_symbol', declared)) +
                                   '/pointer_roles/' + escaped(pointer),
                    'map_sha256': self._files[self._map_path],
                    'provenance_status': 'HISTORICAL_STATIC_MAP_VALUE_NOT_CURRENT_ROLE_PROOF',
                    'current_role_verified': False},
                'verified_source_role': {'role': role['role'], 'relation_polarity': role.get('relation_polarity'),
                    'claim_kind': 'NSF', 'record_pointer': pointer, 'qualified_identity': declared, 'owner': owner,
                    'whole_statement_sha256': digest(record['claims'][int(pointer.rsplit('/', 1)[-1])]['statement']),
                    'role_value_sha256': digest(role),
                    'verification_basis': 'CURRENT_CONTRACT_MATCHES_SAME_ORIGINAL_NSF_POINTER_AND_OWNER'},
                'current_role_proof': {'classifier': copy.deepcopy(self._role_classifier),
                    'current_match_sha256': digest(match), 'record_sha256': digest(record),
                    'declaration_identity_proofs': declared_proofs},
                'context_is_method_contract': False, 'callee_semantics_supported': False,
                'full_method_contract_verified': False}, None

    def _atom(self, record, pointer, node, identity, role, refs, scopes, role_basis, lineage=None):
        return {'record_pointer': pointer, 'record_sha256': digest(record),
                'kind': node.get('kind', node.get('claim_type')), 'statement': copy.deepcopy(node['statement']),
                'original_atom_sha256': digest(node), 'source_context_role': role,
                'query_identity': identity, 'original_scope': copy.deepcopy(record.get('scope', {})),
                'provenance_scopes': copy.deepcopy(scopes), 'source_role_binding': copy.deepcopy(role_basis),
                'proof': {'schema': SCHEMA, 'root': str(self.root), 'accepted_epoch': _present_epoch(self.epoch),
                          'record_sha256': digest(record), 'atom_sha256': digest(node),
                          'references': copy.deepcopy(refs),
                          'accepted_catalogs': [{'path': str(path.relative_to(self.root)), 'sha256': checksum}
                              for path, checksum in self._files.items() if path.is_relative_to(self.root)],
                          'whole_atom_lineage': copy.deepcopy(lineage)},
                'context_is_method_contract': False, 'callee_semantics_supported': False,
                'full_method_contract_verified': False, 'runtime_verified_by_context': False,
                'unidentified_scope_dependencies': 'UNKNOWN', 'notice': NOTICE}

    def context_for(self, record, family, identity, projection, admitted=False):
        request = exact_identity(identity)
        if not request:
            return self._envelope(record, 'NOT_EXACT_IDENTITY')
        if not admitted or projection not in ('coding', 'reviewer'):
            return self._envelope(record, 'ROLE_ADMISSION_WITHHELD')
        if projection == 'coding' and family == 'core' and record.get('coding_status') not in ('coding_default', 'coding_task_conditional'):
            return self._envelope(record, 'ROLE_ADMISSION_WITHHELD')
        try:
            if not self._current():
                return self._envelope(record, 'CONTEXT_EPOCH_STALE')
            original = self._records.get(family, {}).get(record.get('id'))
            if original is None or digest(original) != digest(record):
                return self._envelope(record, 'CONTEXT_RECORD_MISMATCH')
            atoms, reasons = (self._core(record, request) if family == 'core' else
                              self._n001(record, request) if family == 'n001' else ([], ['UNSUPPORTED_FAMILY']))
            return self._envelope(record, 'BOUND_CONTEXT_PRESENT' if atoms else 'CONTEXT_PROOF_MISSING', atoms, reasons)
        except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError):
            return self._envelope(record, 'CONTEXT_PROOF_MISSING', reasons=['EXACT_SOURCE_PROOF_REJECTED'])

    def _core(self, record, identity):
        mapped = self._maps.get(record['id'], {})
        if mapped.get('record_sha256') != digest(record):
            return [], ['ORIGINAL_ROLE_MAP_MISMATCH']
        requested = source_identity.resolve_identity(record, 'core', identity)
        specs = []
        for name, original_spec in mapped.get('contracts', {}).items():
            declared = source_identity.resolve_identity(record, 'core', name)
            if not (_same_identity(identity, name) or requested and declared == requested):
                continue
            spec = copy.deepcopy(original_spec)
            spec['original_contract_symbol'] = name
            specs.append((declared or name, spec))
        allowed = [ref for claim in record.get('claims', []) for ref in claim.get('evidence_refs', [])]
        reader = ExactSourceReader(self.root, self._catalogs['core'].get('source_artifacts', []), allowed)
        atoms, seen, rejected = [], set(), []
        for declared, spec in specs:
            for pointer in spec.get('record_pointers', []):
                role = spec.get('pointer_roles', {}).get(pointer, {})
                if not isinstance(role, dict) or role.get('role') not in METHOD_ROLES:
                    continue
                if not re.fullmatch(r'/claims/(0|[1-9][0-9]*)', pointer):
                    continue
                claim = record['claims'][int(pointer.rsplit('/', 1)[-1])]
                if claim.get('kind') != 'NSF':
                    continue
                owned = {ref_key(ref) for ref in claim.get('evidence_refs', [])}
                whole_refs = []
                for ref in claim.get('evidence_refs', []):
                    source = reader.read(ref)
                    if (isinstance(source, dict) and isinstance(source.get('atom_id'), str) and
                        source.get('claim_type') == claim['kind'] and source.get('statement') == claim['statement']
                        and isinstance(source.get('source_refs'), list)):
                        whole_refs.append({'reference': triple(ref), 'value_sha256': digest(source)})
                leaves = []
                for binding in spec.get('source_bindings', {}).get(pointer, []):
                    if (ref_key(binding) not in owned or binding.get('record_pointer') != pointer or
                        binding.get('original_reference_precision') != 'SINGLE_SOURCE_LOCATOR_NODE'):
                        continue
                    leaf = reader.read(binding)
                    if not isinstance(leaf, dict):
                        continue
                    leaf_symbol = leaf.get('symbol')
                    local = (exact_identity(facet_contracts.normalize_symbol(leaf_symbol))
                             if isinstance(leaf_symbol, str) else None)
                    declared_identity = exact_identity(facet_contracts.normalize_symbol(declared))
                    qualified_leaf = bool(local and (':' in local or '.' in local))
                    declaration_proofs = [proof for proof in source_identity.identity_bindings(record, 'core', declared)
                                          if proof['record_pointer'] == pointer and
                                          ref_key(proof['reference']) == ref_key(binding)]
                    if (not local or not declared_identity or
                        ((local != declared_identity and not declaration_proofs) if qualified_leaf else
                         local != declared_identity.rsplit('.', 1)[-1].rsplit(':', 1)[-1])):
                        continue
                    if (leaf.get('path') != binding.get('source_file') or
                        leaf.get('file_sha256') != binding.get('source_sha256') or
                        leaf.get('path') != binding.get('source_locator', {}).get('path') or
                        leaf.get('range_sha256') != binding.get('source_locator', {}).get('range_sha256')):
                        continue
                    if binding.get('original_source_value_sha256') != digest(leaf):
                        continue
                    if ':' in declared or '.' in declared:
                        owner = declared.rsplit(':', 1)[0] if ':' in declared else declared.rsplit('.', 1)[0]
                        if spec.get('receiver') != owner and not any(proof['owner'] == owner for proof in declaration_proofs):
                            continue
                    leaves.append({'reference': triple(binding), 'value_sha256': digest(leaf)})
                if whole_refs and leaves and pointer not in seen:
                    verified_role, reason = self._core_current_role(record, pointer, declared, spec, role, leaves)
                    if verified_role is None:
                        rejected.append(reason)
                        continue
                    seen.add(pointer)
                    atoms.append(self._atom(record, pointer, claim, identity, 'BOUNDED_SOURCE_CONTEXT',
                        whole_refs + leaves, [], verified_role))
        for atom in self._core_derived_context(record, identity, reader):
            if atom['record_pointer'] not in seen:
                seen.add(atom['record_pointer'])
                atoms.append(atom)
        for atom in self._core_original_subject_context(record, identity, reader):
            if atom['record_pointer'] not in seen:
                seen.add(atom['record_pointer'])
                atoms.append(atom)
        for atom in self._core_steam_context(record, identity, reader):
            if atom['record_pointer'] not in seen:
                seen.add(atom['record_pointer'])
                atoms.append(atom)
        for atom in self._core_qualified_getter_context(record, identity):
            if atom['record_pointer'] not in seen:
                seen.add(atom['record_pointer'])
                atoms.append(atom)
        for atom in self._core_comparison_context(record, identity):
            if atom['record_pointer'] not in seen:
                seen.add(atom['record_pointer'])
                atoms.append(atom)
        return atoms, list(dict.fromkeys(rejected)) if rejected else [] if atoms else ['EXACT_ATOM_OR_ORIGINAL_ROLE_BINDING_MISSING']

    def _n001(self, record, identity):
        research = self._research.get(record['id'], {})
        original = research.get('detailed_evidence', {}).get('original_rebaseline_entry', {})
        current, old = record.get('native_fact', {}), original.get('native_fact', {})
        if (current.get('claim_type') != 'NSF' or old.get('claim_type') != 'NSF' or
            current.get('statement') != old.get('statement')):
            return [], ['CURRENT_ATOM_PROVENANCE_NOT_BOUND']
        support = old.get('source_candidate_ids')
        if (not isinstance(support, list) or not support or len(set(support)) != len(support) or
            set(support) != set(research.get('direct_native_fact_support', []))):
            return [], ['EXPLICIT_WHOLE_ATOM_LINEAGE_MISSING']
        selected = [x for x in research.get('source_locators', []) if x.get('candidate_id') in support]
        if {x.get('candidate_id') for x in selected} != set(support):
            return [], ['EXPLICIT_WHOLE_ATOM_LINEAGE_MISSING']
        refs = [{'artifact_path': x['artifact_path'], 'sha256': x['artifact_sha256'], 'pointer': x['source_pointer']} for x in selected]
        reader = ExactSourceReader(self.root, self._catalogs['research'].get('source_artifacts', []), refs)
        verified, scopes, roles = [], [copy.deepcopy(original.get('scope', {}))], []
        for locator, ref in zip(selected, refs):
            if not re.fullmatch(r'/candidates/(0|[1-9][0-9]*)', ref['pointer']):
                raise ProofError('UNKNOWN_SOURCE_CANDIDATE_SHAPE')
            node = reader.read(ref)
            if (not isinstance(node, dict) or node.get('candidate_id') != locator['candidate_id'] or
                node.get('classification') != 'NSF' or not isinstance(node.get('statement'), str) or 'scope' not in node):
                raise ProofError('UNKNOWN_SOURCE_CANDIDATE_SHAPE')
            verified.append({'reference': triple(ref), 'value_sha256': digest(node)})
            scopes.append(copy.deepcopy(node['scope']))
            # Only complete DIRECT edge clauses in the original relation field.
            # Grouped source-symbol labels and prose mentions never create a role.
            for field in ('callers', 'callees'):
                values = node.get(field, [])
                if not isinstance(values, list):
                    continue
                for index, value in enumerate(values):
                    if not isinstance(value, str):
                        continue
                    for clause in value.split(';'):
                        match = DIRECT_EDGE.fullmatch(clause.strip())
                        if not match or not _same_identity(identity, match[1]):
                            continue
                        local = match[1].rsplit('.', 1)[-1].rsplit(':', 1)[-1]
                        exact_leaf = [x for x in locator.get('evidence_locators', [])
                                      if x.get('symbol') == local and isinstance(x.get('file'), str) and x.get('file_sha256')]
                        # The same leaf must be original source metadata, not a research title.
                        evidence = node.get('evidence', [])
                        if isinstance(evidence, dict):
                            evidence = evidence.get('evidence_locators', [])
                        if not isinstance(evidence, list):
                            continue
                        exact_leaf = [x for x in exact_leaf if any(
                            e.get('file') == x['file'] and e.get('symbol') == local and
                            e.get('file_sha256') == x['file_sha256'] for e in evidence if isinstance(e, dict))]
                        if exact_leaf:
                            roles.append({'identity': match[1], 'source_field': field,
                                'original_relation_schema': 'n001-original-qualified-DIRECT-clause/1',
                                'role_assertion_pointer': ref['pointer'] + '/' + field + '/' + str(index),
                                'original_role_assertion': value, 'value_sha256': digest(value),
                                'exact_leaf': copy.deepcopy(exact_leaf[0]), 'original_reference': triple(ref),
                                'role': 'DIRECT_EDGE_SOURCE_CONTEXT'})
        if not roles:
            return [], ['EXACT_ORIGINAL_ROLE_BINDING_MISSING']
        # Existing canonical whole atom and every supporting ref travel together.
        lineage = {'research_pointer': self._research_pointers[record['id']],
                   'research_record_sha256': digest(research), 'original_atom_pointer':
                   self._research_pointers[record['id']] + '/detailed_evidence/original_rebaseline_entry/native_fact',
                   'original_atom_sha256': digest(old), 'explicit_support_ids': copy.deepcopy(support)}
        return [self._atom(record, '/native_fact', current, identity, 'DIRECT_EDGE_SOURCE_CONTEXT',
                           verified, scopes, roles, lineage)], []

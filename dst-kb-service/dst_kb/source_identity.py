"""Declaration identity only; original claims and method roles remain separate."""
import copy
import base64
import json
import re
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from contextlib import contextmanager
from contextvars import ContextVar
from types import FunctionType
from . import source_identity_lexical as lexical
from .source_epoch_runtime import active_epoch

SCHEMA = 'derived-source-identity-index/1'
MAP_PATH = Path(__file__).with_name('source_identity_map.json')
KNOWLEDGE_ROOT = Path(__file__).resolve().parents[2] / 'knowledge'
IDENTITY = re.compile(r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*', re.ASCII)
HEADER = re.compile(r'^\s*(local\s+)?function\s+([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)\s*\(', re.ASCII)
HASH = re.compile(r'[0-9a-f]{64}')
SUBJECT_SCHEMA = 'accepted-original-subject-declaration-identity/1'
SUBJECT_KIND = 'ORIGINAL_NSF_SUBJECT_IN_PINNED_CITATION_RANGE'
STEAM_SCHEMA = 'accepted-steam-source-excerpt-declaration-identity/1'
STEAM_KIND = 'LITERAL_DECLARATION_IN_PINNED_STEAM_CITATION'
_SELECTED_SOURCE = ContextVar('selected_declaration_source', default=None)
_LEXICAL_FINGERPRINT_CACHE = None


def _lexical_fingerprint():
    """Reuse pure validation only while source bytes and live bindings agree."""
    global _LEXICAL_FINGERPRINT_CACHE
    path = Path(lexical.__file__).resolve()
    raw = path.read_bytes()
    functions = []
    for name in lexical.FINGERPRINT_FUNCTIONS:
        function = vars(lexical).get(name)
        if not isinstance(function, FunctionType) or function.__module__ != lexical.__name__:
            raise ValueError('UNVERIFIED_LOADED_IDENTITY_HELPER')
        code = function.__code__
        # Keep the CodeType alive and compare identity rather than structural
        # equality, so a replacement cannot reuse an old validation.
        functions.append((name, function, id(code), code, function.__module__, code.co_filename))
    filenames = {function[-1] for function in functions}
    if (any(Path(filename).resolve() != path for filename in filenames) or
            not isinstance(lexical.HEADER, re.Pattern)):
        raise ValueError('IDENTITY_HELPER_CODE_ARTIFACT_MISMATCH')
    key = (path, raw, tuple(lexical.FINGERPRINT_FUNCTIONS), tuple(functions),
           lexical.HEADER, lexical.HEADER.pattern, lexical.HEADER.flags,
           lexical.HEADER_PATTERN, lexical.IDENTITY_PATTERN, lexical.PREDICATE_PATTERN,
           lexical.SUBJECT_VERSION, lexical.json, lexical.re, lexical.sha256,
           lexical.Path, lexical.CodeType, lexical.FunctionType)
    if _LEXICAL_FINGERPRINT_CACHE is None or _LEXICAL_FINGERPRINT_CACHE[0] != key:
        value = lexical.accepted_fingerprint()
        _LEXICAL_FINGERPRINT_CACHE = key, value
    return copy.deepcopy(_LEXICAL_FINGERPRINT_CACHE[1])


def validate_source_file(source_file=None):
    if source_file is not None and (not isinstance(source_file, str) or
            len(source_file) > 512 or
            not re.fullmatch(r'scripts/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.lua', source_file) or
            any(part in ('.', '..') for part in source_file.split('/'))):
        raise ValueError('Use an exact relative scripts/...lua source_file')


@contextmanager
def source_file_bound(source_file=None):
    """Narrow an identity lookup to an explicit relative original source path."""
    validate_source_file(source_file)
    token = _SELECTED_SOURCE.set(source_file)
    try:
        yield
    finally:
        _SELECTED_SOURCE.reset(token)


def selected_source_file():
    return _SELECTED_SOURCE.get()


def _manifest_source_file(value):
    """Historical file and archive member names share one exact archive key."""
    if not isinstance(value, str):
        raise ValueError('Invalid committed source file path')
    source_file = value if value.startswith('scripts/') else 'scripts/' + value
    # The historical tree also commits translations/controller.vdf. Preserve
    # those authority entries without widening the public Lua selector.
    if (len(source_file) > 512 or
            not re.fullmatch(r'scripts/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+', source_file) or
            any(part in ('.', '..') for part in source_file.split('/'))):
        raise ValueError('Invalid committed source file path')
    return source_file


@lru_cache(maxsize=8)
def _steam_manifest_files(epoch_key, commitments, expected_json):
    expected = json.loads(expected_json)
    files = {}
    for name, checksum in commitments:
        path = Path(name)
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != checksum:
            raise ValueError('Committed Steam source manifest changed')
        document = json.loads(raw)
        if document.get('schema_version') != 'dst-source-environment-manifest/1':
            continue
        if document.get('source_environment_identity') != expected:
            continue
        rows = document.get('file_hashes', [])
        if not isinstance(rows, list):
            raise ValueError('Invalid committed source file table')
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('sha256'), str) or not HASH.fullmatch(row['sha256']):
                raise ValueError('Invalid committed source file hash')
            names = [_manifest_source_file(row[field]) for field in ('member', 'file') if field in row]
            if not names or len(set(names)) != 1:
                raise ValueError('Inconsistent committed source file path')
            member, fingerprint = names[0], row['sha256']
            if member in files and files[member] != fingerprint:
                raise ValueError('Conflicting committed source file')
            files[member] = fingerprint
    return files


@lru_cache(maxsize=8)
def _source_manifest_inputs(epoch_key, catalog, commitments, metadata_json):
    """Pure path/metadata parsing, keyed by the complete frozen epoch inputs."""
    metadata = json.loads(metadata_json)
    expected = metadata.get('source_environment_identity', {})
    committed = {Path(path).resolve(): checksum for path, checksum in commitments}
    paths = tuple((str((Path(catalog).parent / ref['path']).resolve()), ref['sha256'])
                  for ref in metadata.get('source_manifests', []))
    if not paths or any(committed.get(Path(path)) != checksum for path, checksum in paths):
        raise ValueError('Source epoch has no committed file authority')
    return paths, json.dumps(expected, sort_keys=True, separators=(',', ':'))


def _current_source_files():
    """The selected epoch's committed file authority, never the installed game."""
    context = active_epoch()
    if context is None:
        return None
    metadata_json = getattr(context, 'metadata_json', None)
    if metadata_json is None:
        metadata_json = json.dumps(context.metadata(), sort_keys=True, separators=(',', ':'))
    paths, expected_json = _source_manifest_inputs(context.cache_key, context.catalog,
        tuple(context.commitments), metadata_json)
    return _steam_manifest_files(context.cache_key, paths, expected_json)


def steam_source_version(scope, citations):
    """Validate a no-Git source scope against the bound archive/file authority.

    A null commit alone is never a version proof. This adapter needs an exact
    frozen archive, build/version and original citation byte commitments.
    """
    context = active_epoch()
    if context is None or not isinstance(scope, dict) or scope.get('source_commit', object()) is not None:
        return None
    expected = context.metadata().get('source_environment_identity', {})
    version = scope.get('game_version_txt', scope.get('game_version'))
    if (not HASH.fullmatch(str(scope.get('archive_sha256', ''))) or
            scope.get('archive_sha256') != expected.get('archive_sha256') or
            not isinstance(version, str) or not version or version != expected.get('game_version') or
            not isinstance(scope.get('steam_buildid'), str) or not scope['steam_buildid'] or
            scope['steam_buildid'] != expected.get('steam_buildid') or
            not isinstance(scope.get('snapshot_id'), str) or not scope['snapshot_id'] or
            not isinstance(scope.get('source_epoch_id'), str) or not scope['source_epoch_id'] or
            not isinstance(citations, list) or not citations):
        return None
    try:
        manifests = context.metadata().get('source_manifests', [])
        committed = {Path(path).resolve(): checksum for path, checksum in context.commitments}
        paths = tuple((str((context.catalog.parent / ref['path']).resolve()), ref['sha256'])
                      for ref in manifests)
        if any(committed.get(Path(path)) != checksum for path, checksum in paths):
            return None
        files = _steam_manifest_files(context.cache_key, paths,
            json.dumps(expected, sort_keys=True, separators=(',', ':')))
        for citation in citations:
            if (not isinstance(citation, dict) or files.get(citation.get('path')) != citation.get('file_sha256') or
                    not HASH.fullmatch(str(citation.get('file_sha256', ''))) or
                    not HASH.fullmatch(str(citation.get('range_sha256', ''))) or
                    type(citation.get('line_start')) is not int or type(citation.get('line_end')) is not int or
                    not 0 < citation['line_start'] <= citation['line_end'] or
                    citation.get('snapshot_id') != scope['snapshot_id'] or
                    isinstance(citation.get('source_scope'), dict) and citation['source_scope'] != scope):
                return None
            excerpt = citation.get('source_excerpt', citation.get('excerpt'))
            if (not isinstance(excerpt, str) or sha256(excerpt.encode('utf-8')).hexdigest() != citation['range_sha256'] or
                    len(excerpt.splitlines()) != citation['line_end'] - citation['line_start'] + 1):
                return None
    except (KeyError, TypeError, ValueError, OSError):
        return None
    return {'snapshot_id': scope['snapshot_id'], 'source_epoch_id': scope['source_epoch_id'],
            'source_commit': None, 'source_repository': None, 'archive_sha256': scope['archive_sha256'],
            'game_version': version, 'steam_buildid': scope['steam_buildid'],
            'source_identity_kind': 'COMMITTED_STEAM_ARCHIVE_AND_FILE_MANIFEST',
            'runtime_verified': False}

def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def _at(document, pointer):
    value = document
    for part in pointer.strip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def _owner(symbol):
    return symbol.rsplit(':', 1)[0] if ':' in symbol else symbol.rsplit('.', 1)[0] if '.' in symbol else None

def _method(symbol):
    return symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]

def _physical(row):
    return row['source_lf_sha256'], row['source_file'], row['declaration_line'], row['declared_symbol'], row['declaration_kind']

class SourceIdentityRegistry:
    """Validate derived header proofs against exact original canonical refs.

    Runtime reads accepted artifact bytes, never the current game Source. The
    range excerpt is checked against the original citation commitment; source
    raw-byte and LF commitments remain explicitly different.
    """
    def __init__(self, document, root, artifact_manifest, accepted_records=None):
        if document.get('schema') != SCHEMA or document.get('behavior_or_scope_modified') is not False or document.get('runtime_source_dependency') is not False:
            raise ValueError('Unsupported identity index')
        self.root = Path(root).resolve()
        self.manifest = dict(artifact_manifest)
        self.ranges = copy.deepcopy(document.get('ranges', {}))
        self.raw_ranges = copy.deepcopy(document.get('raw_ranges', {}))
        self.lexical_witnesses = copy.deepcopy(document.get('lexical_witnesses', {}))
        self.augmentation = copy.deepcopy(document.get('original_subject_augmentation', {}))
        self._documents = {}
        self._rows = {}
        self._validated = {}
        self._validated_helper_epochs = {}
        self._public_alias_epoch = None
        self._public_aliases = None
        self._accepted_records = None if accepted_records is None else tuple(
            record for record in accepted_records if record.get('gate_a', {}).get('accepted') is True and
            record.get('knowledge_status') in ('supported', 'canonical', 'corrected') and
            record.get('retrieval_status') != 'restricted')
        for row in document.get('bindings', []):
            if isinstance(row, dict) and HASH.fullmatch(str(row.get('record_sha256', ''))):
                self._rows.setdefault(row['record_sha256'], []).append(copy.deepcopy(row))

    def _node(self, reference):
        name, checksum = reference['artifact_path'], reference['sha256']
        if self.manifest.get(name) != checksum:
            raise ValueError('Identity artifact not accepted')
        if name not in self._documents:
            path = (self.root / name).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError('Identity artifact escaped root')
            raw = path.read_bytes()
            if sha256(raw).hexdigest() != checksum:
                raise ValueError('Identity artifact changed')
            self._documents[name] = json.loads(raw)
        return _at(self._documents[name], reference['pointer'])

    def _valid(self, record, row):
        try:
            return self._valid_row(record, row)
        except (KeyError, IndexError, TypeError, ValueError, OSError):
            return False

    def _valid_row(self, record, row):
        schema = row.get('schema')
        if schema not in ('accepted-source-declaration-identity/1', SUBJECT_SCHEMA, STEAM_SCHEMA):
            return False
        if schema == SUBJECT_SCHEMA and row.get('proof_kind') != SUBJECT_KIND:
            return False
        if schema == STEAM_SCHEMA and row.get('proof_kind') != STEAM_KIND:
            return False
        if schema == 'accepted-source-declaration-identity/1' and row.get('proof_kind') is not None:
            return False
        pointer = row.get('record_pointer', '')
        if not re.fullmatch(r'/claims/(0|[1-9][0-9]*)', pointer):
            return False
        claim = _at(record, pointer)
        if row.get('claim_kind') != claim.get('kind') or row.get('statement_sha256') != digest(claim.get('statement')):
            return False
        ref = row.get('reference', {})
        if not any(all(own.get(k) == ref.get(k) for k in ('artifact_path', 'sha256', 'pointer')) for own in claim.get('evidence_refs', [])):
            return False
        node = self._node(ref)
        if not isinstance(node, dict) or digest(node) != row.get('artifact_value_sha256'):
            return False
        for original, derived in (('path', 'source_file'), ('file_sha256', 'cited_file_sha256'), ('range_sha256', 'cited_range_sha256'), ('line_start', 'line_start'), ('line_end', 'line_end')):
            if node.get(original) != row.get(derived):
                return False
        for name in ('source_raw_sha256', 'source_lf_sha256', 'cited_file_sha256', 'cited_range_sha256', 'declaration_header_sha256'):
            if not HASH.fullmatch(str(row.get(name, ''))):
                return False
        relation = row.get('source_hash_relation')
        if relation == 'RAW_BYTES_EQUAL':
            if row['source_raw_sha256'] != row['cited_file_sha256']:
                return False
        elif relation == 'CRLF_TO_LF_ONLY_EQUAL':
            if row['source_raw_sha256'] == row['cited_file_sha256'] or row['source_lf_sha256'] != row['cited_file_sha256']:
                return False
        else:
            return False
        mode = row.get('range_hash_mode')
        if mode == 'RAW_EXACT_LINE_BYTES':
            if (relation != 'RAW_BYTES_EQUAL' or row['source_raw_sha256'] != row['cited_file_sha256'] or
                    row.get('range_bytes_encoding') != 'base64' or row.get('range_line_endings') != 'PRESERVED_ORIGINAL_BYTES'):
                return False
            raw_range = base64.b64decode(self.raw_ranges.get(row.get('range_bytes_ref'), ''), validate=True)
            if sha256(raw_range).hexdigest() != row['cited_range_sha256']:
                return False
            text = raw_range.decode('utf-8')
        elif mode in ('LF_EXACT_LINE_SLICE', 'LF_JOIN_NO_FINAL_NEWLINE'):
            text = self.ranges.get(row.get('range_text_ref'))
            if not isinstance(text, str) or '\r' in text:
                return False
        else:
            return False
        start, end, line = row.get('line_start'), row.get('line_end'), row.get('declaration_line')
        if not isinstance(text, str) or type(start) is not int or type(end) is not int or type(line) is not int or not 0 < start <= line <= end:
            return False
        if sha256(text.encode()).hexdigest() != row['cited_range_sha256']:
            return False
        lines = text.splitlines()
        if len(lines) != end - start + 1 or lines[line - start] != row.get('declaration_header'):
            return False
        header = row['declaration_header']
        if sha256(header.encode()).hexdigest() != row['declaration_header_sha256']:
            return False
        match = HEADER.match(header)
        if not match or match.group(2) != row.get('declared_symbol'):
            return False
        local, symbol = match.groups()
        kind = 'file_local_function' if local else 'colon_method' if ':' in symbol else 'qualified_dot_function' if '.' in symbol else 'global_function'
        if (local and _owner(symbol)) or row.get('declaration_kind') != kind or row.get('owner') != _owner(symbol):
            return False
        if schema == SUBJECT_SCHEMA:
            if not self._valid_original_subject(record, row, claim, node, text):
                return False
        elif schema == STEAM_SCHEMA:
            if not self._valid_steam_excerpt(record, row, claim, node, text):
                return False
        else:
            cited_names = set(re.findall(r'(?<![A-Za-z0-9_])([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)(?![A-Za-z0-9_])', str(node.get('symbol', '')), re.ASCII))
            if symbol not in cited_names and _method(symbol) not in cited_names:
                return False
        for alias in row.get('aliases', []):
            if not isinstance(alias, str) or not IDENTITY.fullmatch(alias):
                return False
            if alias not in (symbol, _method(symbol)) and not (_owner(symbol) and _owner(alias) == _owner(symbol) and _method(alias) == _method(symbol) and re.search(r'(?<![A-Za-z0-9_:.])' + re.escape(alias) + r'(?![A-Za-z0-9_:.])', claim['statement'])):
                return False
        return row.get('identity_is_behavior_proof') is False and row.get('runtime_verified') is False

    def _valid_steam_excerpt(self, record, row, claim, node, text):
        """Literal no-symbol citations need the frozen full-file lexical proof."""
        ref, whole_ref, scope_ref = row['reference'], row.get('whole_fact_reference', {}), row.get('source_scope_reference', {})
        citation = re.fullmatch(r'(/facts/(?:0|[1-9][0-9]*))/citations/(?:0|[1-9][0-9]*)', ref.get('pointer', ''))
        own = claim.get('evidence_refs', [])
        if (not citation or whole_ref.get('pointer') != citation[1] or scope_ref.get('pointer') != '/source_scope' or
                any(any(other.get(key) != ref.get(key) for key in ('artifact_path', 'sha256'))
                    for other in (whole_ref, scope_ref)) or whole_ref not in own or scope_ref not in own or
                row.get('record_sha256') != digest(record)):
            return False
        fact, scope = self._node(whole_ref), self._node(scope_ref)
        if (not isinstance(fact, dict) or fact.get('kind') != claim.get('kind') or
                fact.get('statement') != claim.get('statement') or fact.get('source_scope') != scope or
                digest(fact) != row.get('whole_fact_value_sha256') or digest(scope) != row.get('source_scope_sha256') or
                not any(binding.get('scope_ref') == scope_ref and binding.get('snapshot_id') == scope.get('snapshot_id') and
                        binding.get('archive_sha256') == scope.get('archive_sha256')
                        for binding in record.get('scope', {}).get('source_scopes', []) if isinstance(binding, dict)) or
                steam_source_version(scope, [node]) is None or
                node.get('source_excerpt', node.get('excerpt')) != text):
            return False
        certificate = self.lexical_witnesses.get(row.get('lexical_witness_ref'))
        if (not isinstance(certificate, dict) or digest(certificate) != row.get('lexical_witness_ref') or
                certificate.get('schema') != 'offline-full-file-lexical-witness/1' or
                certificate.get('full_file_verified') is not True or certificate.get('runtime_source_dependency') is not False or
                certificate.get('provenance') != 'MATCHED_FROZEN_FULL_FILE' or certificate.get('start_state') != 'CODE' or
                certificate.get('reference') != ref or certificate.get('artifact_value_sha256') != row['artifact_value_sha256'] or
                not HASH.fullmatch(str(certificate.get('prefix_lf_sha256', ''))) or
                certificate.get('helper_fingerprint') != _lexical_fingerprint()):
            return False
        for field in ('source_file', 'source_raw_sha256', 'source_lf_sha256', 'cited_file_sha256',
                      'cited_range_sha256', 'range_hash_mode', 'line_start', 'line_end'):
            if certificate.get(field) != row.get(field):
                return False
        checked = lexical.scan(text.replace('\r\n', '\n'), certificate['start_state'], require_closed=False)
        if (sha256(checked['masked'].encode()).hexdigest() != certificate.get('masked_range_sha256') or
                checked['terminal_state'] != certificate.get('range_terminal_state')):
            return False
        declarations = lexical.headers(text.replace('\r\n', '\n'), checked['masked'], row['line_start'])
        target = {'line': row['declaration_line'], 'symbol': row['declared_symbol'],
                  'local': row['declaration_kind'] == 'file_local_function', 'header': row['declaration_header']}
        return (declarations == certificate.get('declarations') and target in declarations and
                sum(head['symbol'] == row['declared_symbol'] for head in declarations) == 1)

    def _valid_original_subject(self, record, row, claim, node, text):
        """A separate context-only proof; old cited-label proofs stay strict."""
        if (claim.get('kind') != 'NSF' or row.get('record_sha256') != digest(record) or
                row.get('aliases') != [row.get('declared_symbol')] or
                row.get('declaration_kind') not in ('colon_method', 'qualified_dot_function')):
            return False
        ref, whole_ref = row['reference'], row.get('whole_fact_reference', {})
        match = re.fullmatch(r'(/reused_direct_facts/(?:0|[1-9][0-9]*))/citations/(?:0|[1-9][0-9]*)', ref.get('pointer', ''))
        if (not match or whole_ref.get('pointer') != match[1] or
                any(whole_ref.get(key) != ref.get(key) for key in ('artifact_path', 'sha256')) or
                not any(own == whole_ref for own in claim.get('evidence_refs', []))):
            return False
        fact = self._node(whole_ref)
        document = self._documents[ref['artifact_path']]
        if (document.get('schema_version') != 'native005.scoped-ui-complete.v1' or
                not isinstance(document.get('scope'), dict) or
                digest(document['scope']) != row.get('artifact_scope_sha256') or
                not isinstance(fact, dict) or fact.get('classification') != 'DirectLuaSourceFact' or
                fact.get('kind') != 'reused_direct_source_fact' or fact.get('new_fact') is not False or
                fact.get('runtime_tested') is not False or fact.get('statement') != claim['statement'] or
                digest(fact) != row.get('whole_fact_value_sha256')):
            return False
        if not isinstance(fact.get('fact_id'), str) or not fact['fact_id']:
            return False
        repository, commit = document.get('repository'), document.get('source_commit')
        if (not isinstance(repository, str) or not re.fullmatch(r'[^\s/]+/[^\s/]+', repository) or
                not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit) or
                repository != node.get('repository') or commit != node.get('commit') or
                row.get('source_repository') != repository or row.get('source_commit') != commit):
            return False
        for pointer in ('/repository', '/source_commit'):
            own_ref = {**ref, 'pointer': pointer}
            if not any(own == own_ref for own in claim.get('evidence_refs', [])):
                return False
        witness = lexical.subject_witness(claim['statement'], row['declared_symbol'])
        if not witness or witness != row.get('subject_witness'):
            return False
        certificate = self.lexical_witnesses.get(row.get('lexical_witness_ref'))
        if not isinstance(certificate, dict) or digest(certificate) != row.get('lexical_witness_ref'):
            return False
        if (certificate.get('schema') != 'offline-full-file-lexical-witness/1' or
                certificate.get('full_file_verified') is not True or
                certificate.get('runtime_source_dependency') is not False or
                certificate.get('provenance') != 'MATCHED_FROZEN_FULL_FILE' or
                certificate.get('start_state') != 'CODE' or
                certificate.get('reference') != ref or
                certificate.get('artifact_value_sha256') != row['artifact_value_sha256'] or
                certificate.get('base_map_sha256') != self.augmentation.get('base_map_sha256') or
                not HASH.fullmatch(str(certificate.get('prefix_lf_sha256', ''))) or
                certificate.get('helper_fingerprint') != _lexical_fingerprint()):
            return False
        for field in ('source_file', 'source_raw_sha256', 'source_lf_sha256', 'cited_file_sha256',
                      'cited_range_sha256', 'range_hash_mode', 'line_start', 'line_end'):
            if certificate.get(field) != row.get(field):
                return False
        # checkpoint 来自被接纳的离线全文生成记录；不能把孤立 range 的起点猜成 CODE。
        normalized = text.replace('\r\n', '\n')
        checked = lexical.scan(normalized, certificate['start_state'], require_closed=False)
        if (sha256(checked['masked'].encode()).hexdigest() != certificate.get('masked_range_sha256') or
                checked['terminal_state'] != certificate.get('range_terminal_state')):
            return False
        declarations = lexical.headers(normalized, checked['masked'], row['line_start'])
        if declarations != certificate.get('declarations'):
            return False
        same_tail = [head for head in declarations if _method(head['symbol']) == _method(row['declared_symbol'])]
        return same_tail == [{'line': row['declaration_line'], 'symbol': row['declared_symbol'],
                              'local': False, 'header': row['declaration_header']}]

    def rows(self, record, family):
        if family != 'core':
            return ()
        checksum = digest(record)
        if any(row.get('schema') in (SUBJECT_SCHEMA, STEAM_SCHEMA) for row in self._rows.get(checksum, [])):
            try:
                epoch = digest(_lexical_fingerprint())
            except (ValueError, TypeError, OSError):
                epoch = None
            if checksum not in self._validated_helper_epochs or self._validated_helper_epochs[checksum] != epoch:
                self._validated.pop(checksum, None)
                self._validated_helper_epochs[checksum] = epoch
        if checksum not in self._validated:
            rows = []
            for row in self._rows.get(checksum, []):
                try:
                    if self._valid(record, row):
                        rows.append(row)
                except (KeyError, IndexError, TypeError, ValueError, OSError):
                    continue
            self._validated[checksum] = tuple(rows)
        return self._validated[checksum]

    @staticmethod
    def _unambiguous_rows(rows):
        return rows if len({_physical(row) for row in rows}) == 1 else ()

    def _public_alias_table(self):
        """Validate the live helper once for one synchronous alias operation.

        symbols/resolve_many examine several aliases of the same validated
        records. Their internal alias loop shares this table; another public
        operation still rechecks the actual helper bytes and live bindings.
        """
        if self._accepted_records is None:
            return {}
        helper_epoch = digest(_lexical_fingerprint())
        if self._public_aliases is None or self._public_alias_epoch != helper_epoch:
            aliases = {}
            for record in self._accepted_records:
                for row in self.rows(record, 'core'):
                    for alias in row['aliases']:
                        aliases.setdefault(alias, []).append(row)
            self._public_aliases, self._public_alias_epoch = aliases, helper_epoch
        return self._public_aliases

    def _filtered_public_alias_rows(self, request, aliases):
        selected = selected_source_file()
        files = _current_source_files()
        return tuple(row for row in aliases.get(request, ())
                     if (selected is None or row['source_file'] == selected) and
                     (files is None or files.get(row['source_file']) in
                      (row['source_raw_sha256'], row['source_lf_sha256'])))

    def public_alias_rows(self, request):
        if self._accepted_records is None:
            return ()
        return self._filtered_public_alias_rows(request, self._public_alias_table())

    def _matching_rows(self, record, family, request, validated_rows=None, alias_operation=None):
        if not isinstance(request, str) or not IDENTITY.fullmatch(request):
            return ()
        selected = selected_source_file()
        own_rows = self.rows(record, family) if validated_rows is None else validated_rows
        rows = tuple(row for row in own_rows if request in row['aliases'] and
                     (selected is None or row['source_file'] == selected))
        if not rows:
            return ()
        # Ambiguity is physical and epoch-wide. Repeated records/citations of
        # one declaration do not create extra owners, while another source does.
        if self._accepted_records is None:
            peers = rows
        elif alias_operation is None:
            peers = self.public_alias_rows(request)
        else:
            # Laziness preserves the original no-own-row/selected-source
            # short circuits, which do not require a lexical helper proof.
            if 'table' not in alias_operation:
                alias_operation['table'] = self._public_alias_table()
            peers = self._filtered_public_alias_rows(request, alias_operation['table'])
        physical = {_physical(row) for row in peers}
        return tuple(row for row in rows if _physical(row) in physical) if len(physical) == 1 else ()

    def bindings(self, record, family, request):
        return tuple(copy.deepcopy(row) for row in self._matching_rows(record, family, request))

    def resolve(self, record, family, request):
        rows = self._matching_rows(record, family, request)
        return rows[0]['declared_symbol'] if rows else None

    def resolve_many(self, record, family, requests):
        resolved = dict.fromkeys(requests)
        valid = {request for request in resolved
                 if isinstance(request, str) and IDENTITY.fullmatch(request)}
        if not valid:
            return resolved
        validated_rows = self.rows(record, family)
        alias_operation = {}
        for request in resolved:
            rows = self._matching_rows(record, family, request, validated_rows,
                                       alias_operation) if request in valid else ()
            if rows:
                resolved[request] = rows[0]['declared_symbol']
        return resolved

    def symbols(self, record, family):
        by_alias = {}
        validated_rows = self.rows(record, family)
        for row in validated_rows:
            for symbol in row['aliases']:
                by_alias.setdefault(symbol, []).append(row)
        alias_operation = {}
        return tuple(sorted(symbol for symbol in by_alias if self._matching_rows(
            record, family, symbol, validated_rows, alias_operation)))

def _registry():
    context = active_epoch()
    if context is not None:
        return _registry_for(context.root, context.source_identity_map, context.cache_key)
    return _registry_for(KNOWLEDGE_ROOT, MAP_PATH, 'legacy-unbound')


@lru_cache(maxsize=8)
def _registry_for(root, map_path, epoch_key):
    root, map_path = Path(root).resolve(), Path(map_path).resolve()
    core_path = root / 'data/nativecore/native-core.json'
    raw = core_path.read_bytes()
    document = json.loads(map_path.read_text(encoding='utf-8'))
    if document.get('canonical_sha256') != sha256(raw).hexdigest():
        raise ValueError('Identity index canonical commitment mismatch')
    core = json.loads(raw)
    return SourceIdentityRegistry(document, root, {row['artifact_path']: row['sha256'] for row in core['source_artifacts']}, core['entries'])

def clear_identity_cache():
    global _LEXICAL_FINGERPRINT_CACHE
    _registry_for.cache_clear()
    _steam_manifest_files.cache_clear()
    _source_manifest_inputs.cache_clear()
    _LEXICAL_FINGERPRINT_CACHE = None

def identity_symbols(record, family):
    try:
        return _registry().symbols(record, family)
    except (ValueError, KeyError, TypeError, OSError):
        return ()

def resolve_identity(record, family, request):
    try:
        return _registry().resolve(record, family, request)
    except (ValueError, KeyError, TypeError, OSError):
        return None

def resolve_identities(record, family, requests):
    requests = tuple(requests)
    try:
        return _registry().resolve_many(record, family, requests)
    except (ValueError, KeyError, TypeError, OSError):
        return dict.fromkeys(requests)

def identity_bindings(record, family, request):
    try:
        return _registry().bindings(record, family, request)
    except (ValueError, KeyError, TypeError, OSError):
        return ()

def record_identity_bindings(record, family):
    try:
        return tuple(copy.deepcopy(row) for row in _registry().rows(record, family))
    except (ValueError, KeyError, TypeError, OSError):
        return ()


def declaration_candidates(request):
    """Distinct accepted physical declarations, for an explicit disambiguation UI."""
    try:
        registry = _registry()
        unique = {}
        for row in registry.public_alias_rows(request):
            key = _physical(row)
            unique.setdefault(key, {field: row[field] for field in (
                'declared_symbol', 'source_file', 'declaration_line', 'declaration_kind', 'owner', 'source_lf_sha256')})
        return tuple(copy.deepcopy(row) for row in unique.values())
    except (ValueError, KeyError, TypeError, OSError):
        return ()

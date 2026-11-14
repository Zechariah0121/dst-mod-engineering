"""Current-package knowledge reading; source validation is a separate channel.

PublicCatalog remains the manifest-checked canonical registry. Guides are
navigation companions, never additions to that canonical registry.
"""
import copy
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from .config import KBError
from .public_catalog import PublicCatalog, at, tokens
from . import review_reader, native_mechanism
from .mcp_server import TOOLS as LEGACY_TOOLS, tool, STR, check_arguments

INSTRUCTIONS = ('Read-only current-package DST knowledge. Default search_kb, get_entry and '
    'lookup_api read public knowledge without source preparation. Search returns complete '
    'relevant original objects with their Scope, corrections and evidence state; follow '
    'get_entry continuations unchanged. Guides are navigation companions, not canonical '
    'records. Research/HOLD and source-version boundaries remain binding. Reading grants '
    'no Coding admission or runtime verification. Explicit projection=coding uses the '
    'legacy source-verified admission path. Source evidence expansion requires separately '
    'verified sources; unavailable or invalid evidence is never delivered as verified.')

TOOLS = copy.deepcopy(LEGACY_TOOLS)
PUBLIC_DESCRIPTIONS = {
    'search_kb': 'Discover current public knowledge across four families and registered task guides. Default reviewer reading returns relevant complete original body objects with Scope, corrections and independent source state. Explicit projection=coding or mode=coding retains legacy admission. scope_logic combines supported explicit filters.',
    'get_entry': 'Read a current public knowledge or guide ID without source preparation. Default reviewer preserves complete Scope, corrections and typed owner objects. Follow content-bound continuation unchanged, or select a relative JSON pointer. Explicit coding or source_epoch retains the legacy source-verified contract.',
    'lookup_api': 'Navigate authored API identities across all families by default. Qualified identities match their complete owner; bare names group symbol/owner/file/visibility without merging file-local and exported identities. Supports require("module").field. Use each executable followup to read its complete contract; navigation does not establish a public API or current behavior.',
    'get_context_bundle': 'Select public knowledge and guide body objects for a task, preserving Scope and evidence limits. compact/normal/deep bound the whole response at 16000/32000/64000 bytes. Default reviewer uses current public package; explicit coding uses legacy admission.',
}
for spec in TOOLS:
    if spec['name'] in PUBLIC_DESCRIPTIONS:
        spec['description'] = PUBLIC_DESCRIPTIONS[spec['name']]
    props = spec['inputSchema']['properties']
    if 'source_epoch' in props:
        props['source_epoch']['description'] = 'Explicit legacy source-verified environment. Omit to read current public package independently of source preparation.'
    if 'projection' in props:
        props['projection']['default'] = 'reviewer'
    if 'top_k' in props:
        props['top_k']['maximum'] = 30
    if spec['name'] == 'lookup_api':
        props['family']['enum'] += ['native_ai', 'native_core']
        props['family']['default'] = 'all'
TOOLS += [
    tool('search_catalog', 'Navigate current public knowledge and registered companion guides.',
         {'query': STR, 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 30}}),
    tool('read_public_entry', 'Read a public object with complete Scope and content-bound continuation.',
         {'id': STR, 'purpose': {'type': 'string', 'enum': ['review']},
          'pointer': STR, 'cursor': STR,
          'max_bytes': {'type': 'integer', 'minimum': 1000, 'maximum': 64000}}, ['id']),
]


def family_name(name):
    return {'native_core': 'core', 'native_ai': 'n001'}.get(name, name)


class PublicReader(PublicCatalog):
    tools = TOOLS
    instructions = INSTRUCTIONS

    def __init__(self, root):
        super().__init__(root)
        self.package_root = Path(root).resolve()
        self.registrations = {r['id']: r for r in self.rows}
        self.guides = {}
        # Only actual local references registered by the public skill entrypoint.
        skill = (self.package_root / 'SKILL.md').read_text(encoding='utf-8-sig')
        for name in sorted(set(re.findall(r'\]\(((?:references|docs)/[^)#\s]+\.md)(?:#[^)]*)?\)', skill))):
            path = (self.package_root / name).resolve()
            if ('..' in PurePosixPath(name).parts or '\\' in name or ':' in name
                    or not path.is_relative_to(self.package_root) or not path.is_file()
                    or any((self.package_root / Path(*PurePosixPath(name).parts[:i])).is_symlink()
                           for i in range(1, len(PurePosixPath(name).parts) + 1))):
                continue
            identifier = 'guide:' + name
            text = path.read_text(encoding='utf-8-sig')
            record = {'id': identifier, 'title': next((line.lstrip('# ').strip() for line in text.splitlines() if line.startswith('#')), name),
                      'scope': 'Public task guide; follow its linked records and their individual source/version boundaries.',
                      'sections': [p for p in re.split(r'\n\s*\n', text) if p.strip()]}
            self.guides[identifier] = {'path': path, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            self.records[identifier] = record
            self.registrations[identifier] = {'id': identifier, 'title': record['title'], 'family': 'guide', 'file': name, 'pointer': '', 'canonical': False}
        self._ranking_rows = list(self.registrations.values())
        self.legacy = None
        self.api_rows = []
        for row in self.rows:
            self._index_apis(self.records[row['id']], row, '')

    def _index_apis(self, node, row, pointer):
        if isinstance(node, dict):
            if all(isinstance(node.get(k), str) for k in ('symbol', 'source_file', 'visibility')):
                identity = native_mechanism.api_identity(node)
                if identity:
                    self.api_rows.append(identity | {'id': row['id'], 'family': row['family'], 'pointer': pointer})
            for key in ('symbol', 'function', 'signature'):
                if key == 'symbol' and all(isinstance(node.get(k), str) for k in ('source_file', 'visibility')):
                    continue
                value = node.get(key)
                if not isinstance(value, str):
                    continue
                from .public_catalog import IDENTITY
                match = IDENTITY.fullmatch(value.strip())
                if match:
                    symbol = match[1]
                    self.api_rows.append({'id': row['id'], 'family': row['family'], 'symbol': symbol,
                        'owner': node.get('owner', re.split(r'[.:][^.:]+$', symbol)[0] if re.search(r'[.:]', symbol) else None),
                        'source_file': node.get('source_file', node.get('file')),
                        'visibility': node.get('visibility', 'NOT_RECORDED'),
                        'identity_kind': node.get('identity_kind'), 'pointer': pointer})
            for key, value in node.items():
                self._index_apis(value, row, pointer + '/' + str(key).replace('~', '~0').replace('/', '~1'))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                self._index_apis(value, row, pointer + '/' + str(i))

    def boundary(self):
        return {'service_mode': 'public_reader', 'coding_context_delivered': False,
                'runtime_validation_performed': False}

    def assessment(self, identifier):
        try:
            cache = getattr(self, '_request_assessment_cache', None)
            if cache is not None and cache:
                state, failure = cache[0]
                if failure is not None:
                    raise failure
            else:
                try:
                    from .evidence_snapshot import active_assessment
                    state = active_assessment(self.package_root)
                except ImportError:
                    state = None
                except Exception as exc:
                    if cache is not None:
                        cache.append((None, exc))
                    raise
                if cache is not None:
                    cache.append((state, None))
        except ImportError:
            state = None
        except Exception as exc:
            return {'status': 'UNAVAILABLE', 'error': {'code': getattr(exc, 'code', 'EVIDENCE_STATE_INVALID'), 'message': str(exc)},
                    'evidence_expansion_allowed': False}
        if state is None:
            return {'status': 'NOT_ASSESSED', 'evidence_expansion_allowed': False}
        references = [{k: r[k] for k in ('reference_id', 'status') if k in r}
            for r in state.get('references', []) if identifier in r.get('affected_entry_ids', [])]
        sources = []
        for index, source in enumerate(state.get('sources', [])):
            observed = source.get('observed_files', {})
            sources.append({k: source[k] for k in ('archive_sha256', 'kind', 'source_input_index') if k in source} | {
                'observed_file_count': len(observed),
                'observed_files_sha256': review_reader.digest(observed),
                'source_record_sha256': review_reader.digest(source),
                'snapshot_pointer': '/sources/' + str(index)})
        return {key: state[key] for key in ('snapshot_id',) if key in state} | {
            'sources': sources,
            'source_details': {'snapshot_id': state.get('snapshot_id'), 'pointer': '/sources',
                'fingerprint_encoding': 'json.dumps(ensure_ascii=False, sort_keys=True) UTF-8 SHA256'},
            'snapshot_status': state.get('status'),
            'status': ('NOT_ASSESSED' if not references else 'PARTIAL' if any(r.get('status') in
                ('CHANGED_UNKNOWN', 'MISSING', 'UNKNOWN') for r in references) else 'COMPLETE'),
            'references': references,
            'runtime_game_verified': False}

    def read(self, identifier, pointer='', cursor='', maximum=24000):
        if identifier not in self.records:
            raise KBError('INVALID_ID', 'Unknown registered knowledge or guide ID')
        record = self.records[identifier]
        row = self.registrations[identifier]
        if identifier in self.guides:
            guide = self.guides[identifier]
            if hashlib.sha256(guide['path'].read_bytes()).hexdigest() != guide['sha256']:
                raise KBError('PUBLIC_PACKAGE_CHANGED', 'Guide changed during this reader session')
        else:
            # Reject a changed canonical file even if it was cached at startup.
            raw = (self.root / row['file']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != self.files[row['file']]['sha256']:
                raise KBError('PUBLIC_PACKAGE_CHANGED', 'Registered public file changed')
        family = family_name(row['family'])
        context = {'entry_registration': row, 'scope': record.get('scope', record.get('scope_text')),
            'source_input_assessment': self.assessment(identifier),
            'record_boundaries': {k: record[k] for k in ('does_not_prove', 'does_not_mean', 'knowledge_kind',
                'knowledge_status', 'retrieval_status', 'coding_status', 'historical_status', 'unknowns',
                'evidence_strength', 'evidence_level', 'confidence') if k in record},
            'correction_refs': record.get('correction_refs', []),
            'correction_warnings': self._corrections(record),
            'evidence_status': 'PUBLIC_LOCATORS_NOT_SOURCE_VERIFICATION'}
        if family == 'legacy':
            context['detail_boundaries'] = record.get('details', {})
            context['source_locators'] = record.get('sources', [])
        if identifier in self.guides:
            context['guide_sha256'] = self.guides[identifier]['sha256']
        # All stored local reference metadata is available in the whole record;
        # attach selected mechanism references rather than every global source.
        if identifier in self.mechanisms:
            document = self.mechanisms[identifier]['document']
            context.update({key: document[key] for key in ('limitations', 'source_epoch', 'archive_sha256') if key in document})
            refs = native_mechanism.local_refs(at(record, review_reader.owner_pointer(record, family, pointer)))
            context['source_references'] = [r for r in self.mechanisms[identifier]['document']['source_references'] if r['id'] in refs]
        return review_reader.read(record, family, context, pointer, cursor, maximum)

    def _corrections(self, record):
        ids = set()
        for ref in record.get('correction_refs', []) + record.get('claim_refs', []) + record.get('sources', []):
            if isinstance(ref, str): ids.add(ref)
            elif isinstance(ref, dict):
                for key in ('claim_id', 'id'):
                    if isinstance(ref.get(key), str): ids.add(ref[key])
        result = [r for r in self.read_file('data/claims.json')['claims'] if r['id'] in ids and r.get('status') == 'superseded']
        for ref in record.get('correction_refs', []):
            if not isinstance(ref, dict) or not ref.get('artifact_path'):
                continue
            name = ref['artifact_path']
            if name not in self.files or self.files[name]['sha256'] != ref.get('sha256'):
                raise KBError('PUBLIC_PACKAGE_CHANGED', 'Correction artifact commitment mismatch')
            result.append({'reference': ref, 'value': at(self.read_file(name), ref.get('pointer', ''))})
        return result

    def _pass_legacy(self, name, args):
        if self.legacy is None:
            try:
                import sys
                sys.path.insert(0, str(self.package_root))
                from prepare_sources import prepared_runtime
                config, _ = prepared_runtime(self.package_root)
                from .mcp_server import Server
                self.legacy = Server(config, public_default=False)
            except Exception as exc:
                raise KBError('SOURCE_VERIFIED_SERVICE_UNAVAILABLE', str(exc)) from exc
        result = self.legacy.call(name, args)
        return result

    def call(self, name, args):
        # A response binds one fully verified snapshot. Revalidate on the next
        # request, never trust mtimes or carry source verification across calls.
        self._request_assessment_cache = []
        try:
            return self._call(name, args)
        finally:
            del self._request_assessment_cache

    def _call(self, name, args):
        spec = next((s for s in self.tools if s['name'] == name), None)
        if spec is None:
            raise KBError('INVALID_TOOL', 'Unknown tool')
        check_arguments(spec, args)
        if args.get('projection') == 'coding' or args.get('mode') == 'coding' or name in ('resolve_evidence', 'validate_kb', 'get_klei_facts', 'get_tests', 'get_related'):
            return self._pass_legacy(name, args)
        if args.get('source_epoch'):
            # An explicit historical environment remains an evidence-bound
            # legacy request; never apply its cursor to current public data.
            return self._pass_legacy(name, args)
        if name in ('get_entry', 'read_public_entry'):
            return self.read(args['id'], args.get('pointer', ''), args.get('cursor', ''), args.get('max_bytes', 24000))
        if name == 'lookup_api':
            return self.lookup(args)
        if name in ('search_kb', 'search_catalog', 'get_context_bundle'):
            supported_filters = {'families', 'entry_types', 'statuses', 'knowledge_statuses', 'retrieval_statuses', 'coding_statuses', 'tags'}
            declared_filters = set(next(s for s in self.tools if s['name'] == 'search_kb')['inputSchema']['properties']) - {
                'query', 'top_k', 'mode', 'projection', 'view', 'scope_logic', 'source_epoch'}
            if any(args.get(key) for key in declared_filters - supported_filters):
                raise KBError('UNSUPPORTED_PUBLIC_FILTER', 'This filter requires an explicit source_epoch verified-service request')
            query = args.get('query', args.get('task_description', ''))
            limit = args.get('top_k', args.get('limit', 5))
            maximum = 64000
            if name == 'get_context_bundle':
                limit, maximum = {'compact': (5, 16000), 'normal': (8, 32000), 'deep': (12, 64000)}[args.get('budget', 'normal')]
            if not 1 <= limit <= 30:
                raise KBError('INVALID_ARGUMENT', 'top_k must be 1..30')
            rows = self.ranker.rank(query)
            selected_filters = {k: v for k, v in args.items() if k in supported_filters and v}
            def matches(row):
                record = self.records[row['id']]
                fields = {'families': [row['family'], family_name(row['family'])],
                    'entry_types': [record.get('entry_type')], 'statuses': [record.get('status', row.get('status'))],
                    'tags': record.get('tags', [])}
                for key in ('knowledge_statuses', 'retrieval_statuses', 'coding_statuses'):
                    fields[key] = [record.get(key[:-2], row.get(key[:-2]))]
                checks = [bool(set(values) & set(fields[key])) for key, values in selected_filters.items()]
                return not checks or (any(checks) if args.get('scope_logic') == 'or' else all(checks))
            rows = [r for r in rows if matches(r)]
            if name == 'search_catalog':
                return self.boundary() | {'query': query, 'results': rows[:limit], 'total_matches': len(rows)}
            results = []
            for row in rows[:limit]:
                identifier = row['id']
                record = self.records[identifier]
                family = family_name(row['family'])
                candidates = review_reader.units(record, family, '')
                # Exclude identity/metadata-only objects from factual search delivery.
                candidates = [p for p in candidates if p.startswith(('/claims/', '/api_contracts/', '/mechanism_steps/', '/details/', '/sections/')) or p in ('/summary', '/native_fact', '/ai_coding_impact', '/common_ai_failure', '/recommended_reasoning')]
                if row['family'] == 'guide':
                    candidates = ['/sections/' + str(i) for i in range(len(record['sections']))]
                terms = tokens(query)
                candidates.sort(key=lambda p: -len(terms & tokens(json.dumps(at(record, p), ensure_ascii=False))))
                delivered = None
                for pointer in candidates:
                    value = self.read(identifier, pointer, maximum=16000)
                    if value.get('objects'):
                        delivered = value
                        break
                results.append({'entry': row, 'reading': delivered,
                    'gap': None if delivered else 'NO_COMPLETE_RELEVANT_OBJECT_WITHIN_SEARCH_BUDGET',
                    'followup': {'tool': 'get_entry', 'arguments': {'id': identifier, 'projection': 'reviewer', 'max_bytes': 64000}}})
            payload = self.boundary() | {'query': query, 'results': results, 'total_matches': len(rows),
                'ranking': 'shared_field_weighted_bm25', 'projection': 'reviewer', 'max_bytes': maximum}
            for selected in reversed(results):
                if review_reader.size(payload) <= maximum:
                    break
                selected['reading'] = None
                selected['gap'] = 'TOTAL_SEARCH_BUDGET_USE_FOLLOWUP'
            return payload
        raise KBError('INVALID_TOOL', 'Unsupported public operation')

    def lookup(self, args):
        symbol = args['symbol'].strip()
        from .public_catalog import IDENTITY
        module = re.fullmatch(native_mechanism.MODULE, symbol)
        if module:
            symbol = 'require("' + module['module'] + '").' + module['member']
        if not IDENTITY.fullmatch(symbol) and not module:
            raise KBError('INVALID_ARGUMENT', 'Expected a declared bare or owner-qualified API identity')
        if args.get('source_file') is not None:
            name = args['source_file']
            parts = PurePosixPath(name)
            if (not name.startswith('scripts/') or not name.endswith('.lua') or '..' in parts.parts
                    or parts.is_absolute() or '\\' in name or ':' in name or '//' in name):
                raise KBError('INVALID_ARGUMENT', 'source_file must be an exact scripts/...lua relative identity')
        qualified = '.' in symbol or ':' in symbol
        hits = [r for r in self.api_rows if (r['symbol'] == symbol if qualified else re.split(r'[.:]', r['symbol'])[-1] == symbol)]
        for field in ('owner', 'source_file', 'identity_kind'):
            if args.get(field) is not None:
                hits = [r for r in hits if r[field] == args[field]]
        if args.get('family', 'all') != 'all':
            hits = [r for r in hits if r['family'] == args['family']]
        groups = {}
        for hit in hits:
            key = tuple(hit[k] for k in ('symbol', 'owner', 'source_file', 'visibility', 'identity_kind'))
            group = groups.setdefault(key, {k: hit[k] for k in ('symbol', 'owner', 'source_file', 'visibility', 'identity_kind')} | {'records': []})
            group['records'].append(hit | {'followup': {'tool': 'get_entry', 'arguments': {'id': hit['id'], 'pointer': hit['pointer'], 'projection': 'reviewer', 'max_bytes': args.get('max_bytes', 24000)}}})
        limit = args.get('top_k', 5)
        payload = self.boundary() | {'symbol': symbol, 'qualified': qualified, 'total_groups': len(groups),
            'groups': list(groups.values())[:limit], 'total_matches': len(hits),
            'results': [r for group in list(groups.values())[:limit] for r in group['records']],
            'contract_status': 'NAVIGATION_ONLY_USE_FOLLOWUP'}
        maximum = args.get('max_bytes', 24000)
        # Groups stay whole; never split same-identity records or visibility.
        while review_reader.size(payload) > maximum and payload['groups']:
            payload['groups'].pop()
            payload['results'] = [r for group in payload['groups'] for r in group['records']]
            payload['withheld_reason'] = 'WHOLE_IDENTITY_GROUP_EXCEEDS_BUDGET'
        if review_reader.size(payload) > maximum:
            payload.pop('symbol')
            payload['symbol_sha256'] = hashlib.sha256(symbol.encode('utf-8')).hexdigest()
            payload['withheld_reason'] = 'REQUEST_IDENTITY_EXCEEDS_BUDGET'
        return payload

    def close(self):
        if getattr(self, 'legacy', None) is not None:
            self.legacy.close()
        super().close()

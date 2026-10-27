"""Source-free public-material navigation, separate from verified Coding retrieval."""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path, PurePosixPath
import re
import sys

from .config import KBError
from . import family_registry, native_mechanism
from .mcp_server import Server, check_arguments, tool, STR

INSTRUCTIONS = (
    'PUBLIC CATALOG MODE: source evidence has not been restored or verified. '
    'Use search_catalog to navigate the registered public records, then read_public_entry '
    'only for explicit review of selected public material. This is not the full '
    'nine-tool service, a Coding context provider, or a source-contract verifier. '
    'Core Coding HOLD and every record Scope/correction remain binding. '
    'Source payload slots are unavailable evidence, never source text. '
    'For implementation inspect authorized current source independently. '
    'Prepare complete authorized sources and restart the MCP session for full service.'
)
TOOLS = [
    tool('search_catalog', 'Find public record locations and governance metadata; delivers no facts or Coding context.',
         {'query': STR, 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 20, 'default': 5}}),
    tool('read_public_entry', 'Review one public record or exact JSON subpointer. Does not resolve source evidence or grant Coding admission. Oversized values are withheld whole; select a narrower pointer.',
         {'id': STR, 'purpose': {'type': 'string', 'enum': ['review']},
          'pointer': {'type': 'string', 'maxLength': 1000, 'default': ''},
          'max_bytes': {'type': 'integer', 'minimum': 4000, 'maximum': 24000, 'default': 12000}},
         ['id', 'purpose']),
]


def at(value, pointer):
    if not isinstance(pointer, str) or (pointer and not pointer.startswith('/')):
        raise KBError('INVALID_ARGUMENT', 'pointer must be empty or an absolute JSON pointer within the selected record')
    try:
        for token in pointer.split('/')[1:]:
            if re.search(r'~(?![01])', token):
                raise ValueError('Invalid pointer escape')
            token = token.replace('~1', '/').replace('~0', '~')
            if isinstance(value, list):
                if not re.fullmatch(r'0|[1-9][0-9]*', token):
                    raise ValueError('Invalid array index')
                value = value[int(token)]
            else:
                value = value[token]
        return value
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise KBError('INVALID_ARGUMENT', 'JSON pointer does not select a value in this record') from exc


def encoded(value):
    return json.dumps(value, ensure_ascii=False).encode('utf-8')


def token_sequence(value):
    # Keep case until identifier boundaries have been recovered. Lowercasing
    # first erases distinctions such as QueueManager -> queue + manager.
    raw = re.findall(r'[A-Za-z0-9_][A-Za-z0-9_.:-]*|[\u3400-\u9fff]+', value)
    terms = []
    for term in raw:
        variants = [term.lower()]
        for part in re.split(r'[_.:-]+', term):
            if not part:
                continue
            variants.append(part.lower())
            split = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', part)
            split = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', split)
            variants.extend(split.lower().split())
        terms.extend(dict.fromkeys(variants))
    return [t for term in terms for t in
               ([term[i:i + 2] for i in range(len(term) - 1)] if re.match(r'[\u3400-\u9fff]', term) and len(term) > 2 else [term])]


def tokens(value):
    return set(token_sequence(value))


IDENTITY = re.compile(r'([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)(?:\s*\([^\n]*\))?\Z')


def declared_identities(record, *, lowercase=True):
    """Read explicit identity fields, never infer ownership from prose mentions.

    A qualified task keyword is a declared navigation identity in older families;
    a bare keyword remains a keyword, not an owned API declaration.
    """
    found = set()
    def add(value, qualified_only=False):
        if not isinstance(value, str):
            return
        match = IDENTITY.fullmatch(value.strip())
        if match and (not qualified_only or '.' in match[1] or ':' in match[1]):
            found.add(match[1].lower() if lowercase else match[1])
    for key in ('api_contracts', 'apis', 'methods', 'functions'):
        values = record.get(key, [])
        if isinstance(values, dict):
            values = list(values.values())
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str):
                add(value)
            elif isinstance(value, dict):
                for field in ('symbol', 'function', 'signature'):
                    add(value.get(field))
    for value in record.get('task_keywords', []):
        add(value, qualified_only=True)
    return found


class CatalogRanker:
    """Cross-family navigation ranking; field relevance never promotes evidence."""
    WEIGHTS = {'title': 6, 'aliases': 5, 'api': 7, 'keywords': 3, 'question': 3, 'body': 1}

    def __init__(self, rows, records):
        self.rows = rows
        self.documents = {}
        self.frequencies = Counter()
        lengths = Counter()
        for row in rows:
            record = records[row['id']]
            aliases = [value for value in record.get('aliases', []) if isinstance(value, str)]
            keywords = [value for value in record.get('task_keywords', []) if isinstance(value, str)]
            identities = declared_identities(record)
            fields = {'title': record.get('title', ''), 'aliases': ' '.join(aliases),
                      'api': ' '.join(sorted(declared_identities(record, lowercase=False))), 'keywords': ' '.join(keywords),
                      'question': record.get('engineering_question', ''),
                      'body': json.dumps(record, ensure_ascii=False)}
            counts = {key: Counter(token_sequence(value)) for key, value in fields.items()}
            self.documents[row['id']] = {'counts': counts, 'title': fields['title'].strip().lower(),
                'aliases': {value.strip().lower() for value in aliases},
                'keywords': {value.strip().lower() for value in keywords}, 'identities': identities,
                'leaves': {re.split(r'[.:]', value)[-1] for value in identities}}
            self.frequencies.update(set().union(*(value.keys() for value in counts.values())))
            for key, value in counts.items():
                lengths[key] += sum(value.values())
        self.average_lengths = {key: max(1, lengths[key] / max(1, len(rows))) for key in self.WEIGHTS}

    def rank(self, query):
        original_query = query.strip()
        query = original_query.lower()
        if not query:
            return list(self.rows)
        terms = tokens(original_query)
        if not terms:
            return []
        identity_match = IDENTITY.fullmatch(query)
        query_identity = identity_match[1] if identity_match else None
        qualified = query_identity is not None and ('.' in query_identity or ':' in query_identity)
        ranked = []
        size = len(self.rows)
        for row in self.rows:
            identifier = row['id']
            doc = self.documents[identifier]
            # Exact owner-qualified APIs never borrow a different owner's leaf.
            priority = (6 if query == identifier.lower() else
                        5 if qualified and query_identity in doc['identities'] else
                        4 if query == doc['title'] or query in doc['aliases'] else
                        3 if not qualified and query_identity in doc['leaves'] else
                        2 if query in doc['keywords'] else 0)
            relevance = 0
            for field, counts in doc['counts'].items():
                length = sum(counts.values())
                norm = 1.2 * (0.25 + 0.75 * length / self.average_lengths[field])
                for term in terms:
                    frequency = counts.get(term, 0)
                    if frequency:
                        rarity = math.log1p((size - self.frequencies[term] + 0.5) / (self.frequencies[term] + 0.5))
                        relevance += self.WEIGHTS[field] * rarity * frequency * 2.2 / (frequency + norm)
            if priority or relevance:
                ranked.append((-priority, -relevance, identifier, row))
        ranked.sort(key=lambda value: value[:3])
        return [value[3] for value in ranked]


class PublicCatalog(Server):
    tools = TOOLS
    instructions = INSTRUCTIONS

    def __init__(self, root):
        super().__init__()
        self.root = Path(root).resolve() / 'knowledge'
        try:
            manifest = json.loads((self.root / 'PACKAGE-MANIFEST.json').read_text(encoding='utf-8-sig'))
            self.files = {row['path']: row for row in manifest['files']}
            self.documents = {}
            self.rows = self.read_file('CATALOG.json')['entries']
            self.family_registry = family_registry.load(self.root, self.read_file)
            if self.family_registry is not None:
                family_registry.validate_catalog(self.root, self.read_file('CATALOG.json'), self.family_registry)
            self.mechanisms = native_mechanism.load(self.root, self.family_registry)
            if self.family_registry is None and (len(self.rows) != 187 or len({row['id'] for row in self.rows}) != 187):
                raise KBError('PUBLIC_PACKAGE_CHANGED', 'Expected 187 unique catalog IDs')
            self.records = {}
            self.search_text = {}
            for row in self.rows:
                record = at(self.read_file(row['file']), row['pointer'])
                if record['id'] != row['id']:
                    raise KBError('PUBLIC_PACKAGE_CHANGED', 'Catalog pointer identity mismatch')
                self.records[row['id']] = record
                self.search_text[row['id']] = json.dumps(record, ensure_ascii=False).lower()
            self.ranker = CatalogRanker(self.rows, self.records)
            self.corrections = [{key: claim.get(key) for key in ('id', 'status', 'superseded_by')}
                                for claim in self.read_file('data/claims.json')['claims']
                                if claim.get('status') == 'superseded']
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise KBError('PUBLIC_PACKAGE_CHANGED', 'Public package is missing or invalid: ' + str(exc)) from exc

    def read_file(self, name):
        if name in self.documents:
            return self.documents[name]
        parts = PurePosixPath(name)
        path = (self.root / name).resolve()
        if (parts.is_absolute() or '..' in parts.parts or '\\' in name or ':' in name
                or not path.is_relative_to(self.root) or name not in self.files):
            raise KBError('PUBLIC_PACKAGE_CHANGED', 'Invalid public file reference')
        data = path.read_bytes()
        row = self.files[name]
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise KBError('PUBLIC_PACKAGE_CHANGED', 'Public file differs from manifest: ' + name)
        self.documents[name] = json.loads(data.decode('utf-8-sig'))
        return self.documents[name]

    def boundary(self):
        return {'service_mode': 'public_catalog', 'full_service_available': False,
                'source_evidence_status': 'NOT_RESTORED_OR_VERIFIED',
                'coding_context_delivered': False, 'runtime_validation_performed': False,
                'guidance': self.instructions,
                'availability_fallback': getattr(self, 'availability_fallback', None)}

    def call(self, name, args):
        spec = next((value for value in self.tools if value['name'] == name), None)
        if spec is None:
            raise KBError('FULL_SERVICE_REQUIRED', 'This session offers public catalog tools only; prepare sources and restart for full MCP')
        check_arguments(spec, args)
        if name == 'search_catalog':
            query, limit = args.get('query', '').strip(), args.get('limit', 5)
            ranked = self.ranker.rank(query)
            return self.boundary() | {'query': query, 'total_matches': len(ranked),
                                      'results': ranked[:limit],
                                      'ranking': 'field_weighted_bm25_navigation_only',
                                      'catalog_is_navigation_not_delivered_facts': True}
        identifier = args['id']
        if identifier not in self.records:
            raise KBError('INVALID_ID', 'Unknown public record ID')
        pointer = args.get('pointer', '')
        record = self.records[identifier]
        value = at(record, pointer)
        row = next(row for row in self.rows if row['id'] == identifier)
        result = self.boundary() | {'purpose': 'review', 'entry': row, 'pointer': pointer,
                    'scope': record.get('scope', record.get('scope_text')),
                    'evidence_strength': record.get('evidence_strength', record.get('evidence_level')),
                    'record_boundaries': {key: record[key] for key in
                        ('does_not_prove', 'does_not_mean', 'knowledge_kind', 'confidence',
                         'knowledge_status', 'retrieval_status', 'coding_status', 'historical_status') if key in record},
                    'correction_refs': record.get('correction_refs', []),
                    'historical_claim_corrections': self.corrections,
                    'unresolved_source_slot_in_selection': '$dst_source_payload_slot' in json.dumps(value),
                    'public_value': value, 'whole_value_delivered': True}
        if identifier in self.mechanisms:
            context = native_mechanism.envelope(self.mechanisms[identifier], pointer)
            value=context.pop('value')
            result['public_value']=value
            result['pointer']=context['pointer']
            result['research_context'] = context
        if len(encoded(result)) > args.get('max_bytes', 12000):
            result.pop('public_value')
            result['whole_value_delivered'] = False
            result['withheld_reason'] = 'WHOLE_VALUE_EXCEEDS_BYTE_BUDGET'
            keys = list(value) if isinstance(value, dict) else list(range(len(value))) if isinstance(value, list) else []
            owner_pointer = result['pointer']
            if identifier in self.mechanisms and re.fullmatch(r'/(claims|api_contracts|mechanism_steps)/(0|[1-9][0-9]*)', owner_pointer):
                # These are whole owner atoms: another subfield would expand to
                # the same owner again. Offer only its valid canonical pointer.
                result['child_pointers'] = [owner_pointer]
                result['child_pointers_truncated'] = False
                result['guidance'] = 'Read this whole owner atom with a larger byte budget; subfields do not split its evidence/Scope.'
            else:
                result['child_pointers'] = [owner_pointer + '/' + str(key).replace('~', '~0').replace('/', '~1') for key in keys[:30]]
                result['child_pointers_truncated'] = len(keys) > 30
            # Never truncate Scope or source text to make a response fit.
            if len(encoded(result)) > args.get('max_bytes', 12000):
                result = self.boundary() | {'entry': row, 'pointer': result['pointer'], 'whole_value_delivered': False,
                    'withheld_reason': 'REQUIRED_SCOPE_EXCEEDS_BYTE_BUDGET',
                    'guidance': 'Review this record and its complete Scope by file; no facts were delivered.'}
        return result


def main(root, command, tool_name=None, arguments=None, fallback_notice=None):
    server = PublicCatalog(root)
    server.availability_fallback = fallback_notice
    if fallback_notice:
        server.instructions += ' Availability fallback: ' + json.dumps(fallback_notice, ensure_ascii=False)
    try:
        if command == 'status':
            print(json.dumps(server.boundary() | {'records': len(server.rows), 'tools': [t['name'] for t in TOOLS]}, ensure_ascii=False))
        elif command == 'call':
            print(json.dumps(server.call(tool_name, arguments or {}), ensure_ascii=False))
        elif command == 'serve':
            while True:
                line = sys.stdin.buffer.readline(1024 * 1024 + 1)
                if not line or len(line) > 1024 * 1024:
                    break
                try:
                    result = server.handle(json.loads(line))
                except (ValueError, UnicodeError):
                    result = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Invalid JSON'}}
                if result is not None:
                    sys.stdout.buffer.write(encoded(result) + b'\n')
                    sys.stdout.buffer.flush()
        else:
            raise KBError('FULL_SERVICE_REQUIRED', 'Catalog mode has no full validation/index; prepare sources for this command')
        return 0
    finally:
        server.close()

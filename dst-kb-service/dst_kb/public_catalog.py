"""Source-free public-material navigation, separate from verified Coding retrieval."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

from .config import KBError
from .mcp_server import Server, check_arguments, tool, STR

INSTRUCTIONS = (
    'PUBLIC CATALOG MODE: source evidence has not been restored or verified. '
    'Use search_catalog to navigate the 187 public records, then read_public_entry '
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


def tokens(value):
    terms = re.findall(r'[a-z0-9_][a-z0-9_.:-]*|[\u3400-\u9fff]+', value.lower())
    terms += [part for term in list(terms) for part in re.split(r'[.:]+', term) if part and part != term]
    return set(t for term in terms for t in
               ([term[i:i + 2] for i in range(len(term) - 1)] if re.match(r'[\u3400-\u9fff]', term) and len(term) > 2 else [term]))


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
            if len(self.rows) != 187 or len({row['id'] for row in self.rows}) != 187:
                raise KBError('PUBLIC_PACKAGE_CHANGED', 'Expected 187 unique catalog IDs')
            self.records = {}
            self.search_text = {}
            for row in self.rows:
                record = at(self.read_file(row['file']), row['pointer'])
                if record['id'] != row['id']:
                    raise KBError('PUBLIC_PACKAGE_CHANGED', 'Catalog pointer identity mismatch')
                self.records[row['id']] = record
                self.search_text[row['id']] = json.dumps(record, ensure_ascii=False).lower()
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
                'guidance': INSTRUCTIONS}

    def call(self, name, args):
        spec = next((value for value in self.tools if value['name'] == name), None)
        if spec is None:
            raise KBError('FULL_SERVICE_REQUIRED', 'This session offers public catalog tools only; prepare sources and restart for full MCP')
        check_arguments(spec, args)
        if name == 'search_catalog':
            query, limit = args.get('query', '').strip(), args.get('limit', 5)
            terms = tokens(query)
            ranked = []
            for position, row in enumerate(self.rows):
                text = self.search_text[row['id']]
                score = sum(1 for term in terms if term in text)
                if query.lower() == row['id'].lower():
                    score += 1000
                if not terms or score:
                    ranked.append((-score, position, row))
            ranked.sort(key=lambda item: item[:2])
            return self.boundary() | {'query': query, 'total_matches': len(ranked),
                                      'results': [row for _, _, row in ranked[:limit]],
                                      'ranking': 'keyword_navigation_only',
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
        if len(encoded(result)) > args.get('max_bytes', 12000):
            result.pop('public_value')
            result['whole_value_delivered'] = False
            result['withheld_reason'] = 'WHOLE_VALUE_EXCEEDS_BYTE_BUDGET'
            keys = list(value) if isinstance(value, dict) else list(range(len(value))) if isinstance(value, list) else []
            result['child_pointers'] = [pointer + '/' + str(key).replace('~', '~0').replace('/', '~1') for key in keys[:30]]
            result['child_pointers_truncated'] = len(keys) > 30
            # Never truncate Scope or source text to make a response fit.
            if len(encoded(result)) > args.get('max_bytes', 12000):
                result = self.boundary() | {'entry': row, 'pointer': pointer, 'whole_value_delivered': False,
                    'withheld_reason': 'REQUIRED_SCOPE_EXCEEDS_BYTE_BUDGET',
                    'guidance': 'Review this record and its complete Scope by file; no facts were delivered.'}
        return result


def main(root, command, tool_name=None, arguments=None):
    server = PublicCatalog(root)
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

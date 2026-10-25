"""Build payload-free JSON templates and recover exact source bytes locally.

This is a data-build helper, not a retrieval validator or proof admission path.
Only explicitly supplied source archives/directories are read. A matching range
never asserts that its containing supplied file is an original historical file.
"""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

SCHEMA = 'dst-local-source-payload-recipe/1'
MARKER = '$dst_source_payload_slot'
HASH = re.compile(r'[0-9a-f]{64}')
HEADER_ONLY = re.compile(r'^\s*(?:local\s+)?function\s+[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*\s*\([^\n]*?\)\s*(?:--[^\n]*)?$')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8', newline='\n')


def tokens(pointer):
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise ValueError('Invalid JSON pointer')
    return [p.replace('~1', '/').replace('~0', '~') for p in pointer[1:].split('/')]


def at(value, pointer):
    for part in tokens(pointer):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def set_at(value, pointer, replacement, remove=False):
    parts = tokens(pointer)
    parent = value
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    last = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    if remove:
        if isinstance(parent, list):
            raise ValueError('Payload slots cannot delete array elements')
        parent.pop(last, None)
    else:
        parent[last] = replacement


def safe_child(root, relative):
    p = PurePosixPath(relative)
    if (not relative or '\\' in relative or ':' in relative or p.is_absolute()
            or '..' in p.parts or p.as_posix() != relative):
        raise ValueError('Unsafe relative path')
    root = Path(root).resolve()
    result = (root / relative).resolve()
    if not result.is_relative_to(root):
        raise ValueError('Path escaped root')
    return result


def walk(value, pointer='', ancestors=()):
    if isinstance(value, dict):
        yield value, pointer, ancestors
        for key, item in value.items():
            escaped = key.replace('~', '~0').replace('/', '~1')
            yield from walk(item, pointer + '/' + escaped, ancestors + (value,))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from walk(item, pointer + '/' + str(i), ancestors)


def source_name(node):
    for key in ('path', 'file', 'source_file', 'source_path'):
        name = node.get(key)
        if isinstance(name, str):
            name = name.replace('\\', '/')
            if name.endswith('.lua') and ':' not in name and '..' not in PurePosixPath(name).parts:
                return name if name.startswith('scripts/') else 'scripts/' + name
    return None


def coordinate(node):
    name = source_name(node)
    start, end = node.get('line_start'), node.get('line_end')
    fingerprint = node.get('file_sha256', node.get('cited_file_sha256'))
    if (name and type(start) is int and type(end) is int and 0 < start <= end
            and isinstance(fingerprint, str) and HASH.fullmatch(fingerprint)):
        return {'source_file': name, 'expected_file_sha256': fingerprint,
                'line_start': start, 'line_end': end}
    return None


def historical_comparison(node):
    """Recognize only complete metadata-only history, never a payload waiver."""
    marked = (node.get('evidence_role') == 'historical_comparison' or
              node.get('supports_current_behavior') is False or
              node.get('payload_status') == 'metadata_only')
    if not marked:
        return False
    ref = coordinate(node)
    metadata = node.get('original_payload_metadata')
    path = node.get('path') or node.get('file') or node.get('source_file') or node.get('source_path')
    valid = (node.get('evidence_role') == 'historical_comparison' and
             node.get('supports_current_behavior') is False and
             node.get('payload_status') == 'metadata_only' and ref and
             isinstance(path, str) and path.startswith('scripts/') and
             '\\' not in path and ':' not in path and
             all(part not in ('', '.', '..') for part in path.split('/')) and
             isinstance(node.get('file_sha256'), str) and HASH.fullmatch(node['file_sha256']) and
             isinstance(node.get('range_sha256'), str) and HASH.fullmatch(node['range_sha256']) and
             isinstance(node.get('snapshot_id'), str) and node['snapshot_id'].strip() and
             isinstance(metadata, dict) and
             metadata.get('content_sha256') == node['range_sha256'] and
             type(metadata.get('content_bytes')) is int and metadata['content_bytes'] > 0 and
             type(metadata.get('line_count')) is int and
             metadata['line_count'] == ref['line_end'] - ref['line_start'] + 1 and
             isinstance(metadata.get('original_json_value_sha256'), str) and
             HASH.fullmatch(metadata['original_json_value_sha256']))
    payload_keys = {'source_excerpt', 'excerpt', 'declaration_header', 'header', MARKER}
    locator_keys = {'path', 'file', 'source_file', 'source_path', 'symbol', 'function',
                    'line_start', 'line_end', 'file_sha256', 'range_sha256'}
    if (not valid or any(payload_keys & child.keys() or
                         (child is not node and locator_keys & child.keys())
                         for child, _, _ in walk(node))):
        raise ValueError('Malformed historical comparison metadata or source payload')
    return True


def source_walk(value, pointer='', ancestors=()):
    """Walk current source evidence without propagating historical hashes."""
    if isinstance(value, dict):
        if historical_comparison(value):
            return
        yield value, pointer, ancestors
        for key, item in value.items():
            escaped = key.replace('~', '~0').replace('/', '~1')
            yield from source_walk(item, pointer + '/' + escaped, ancestors + (value,))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from source_walk(item, pointer + '/' + str(i), ancestors)


def json_documents(root):
    root = Path(root).resolve()
    for path in sorted(root.rglob('*.json')):
        if any(p in ('__pycache__', '.git', 'cache') for p in path.relative_to(root).parts):
            continue
        yield path.relative_to(root).as_posix(), read_json(path)


def strict_excerpt_locations(documents):
    """Identify no-symbol range nodes consumed by existing NativeCore NSF refs.

    This only labels recipe completeness. The original runtime validator remains
    the sole admission check after data assembly and commitment rebinding.
    """
    strict = set()
    for name, core in documents.items():
        if not name.endswith('/data/nativecore/native-core.json'):
            continue
        prefix = name[:-len('data/nativecore/native-core.json')]
        for record in core.get('entries', []):
            for claim in record.get('claims', []):
                if claim.get('kind') != 'NSF':
                    continue
                for ref in claim.get('evidence_refs', []):
                    target = prefix + ref['artifact_path']
                    doc = documents.get(target)
                    if doc is None:
                        continue
                    for node, pointer, ancestors in source_walk(at(doc, ref['pointer']), ref['pointer']):
                        if (not (node.get('symbol') or node.get('function'))
                                and source_name(node) and node.get('line_start', node.get('start_line')) is not None):
                            strict.add((target, pointer))
    return strict


def generate_recipe(private_root, public_root=None):
    """Return (recipe, templates); write nothing and never mutate either root.

    public_root may be an already redacted copy with unchanged artifact paths
    and JSON pointers. Identity/path rebinding is performed by the parent export
    workflow AFTER this stage; map recipe target paths alongside artifact paths
    if the exporter renames an artifact. No private path is emitted in recipe.
    """
    private = dict(json_documents(private_root))
    public = private if public_root is None else dict(json_documents(public_root))
    coordinates = {}
    for document in private.values():
        for node, pointer, ancestors in source_walk(document):
            ref = coordinate(node)
            fingerprint = node.get('range_sha256', node.get('cited_range_sha256'))
            if ref and isinstance(fingerprint, str) and HASH.fullmatch(fingerprint):
                coordinates.setdefault(fingerprint, {})[digest(ref)] = ref
    strict = strict_excerpt_locations(private)
    templates, slots, non_lua_excerpts = {}, [], []
    strict_hashes = set()
    for name, pointer in strict:
        node = at(private[name], pointer)
        if isinstance(node.get('range_sha256'), str):
            strict_hashes.add(node['range_sha256'])
    for name, document in private.items():
        if name not in public:
            continue
        target = copy.deepcopy(public[name])
        file_slots = []
        for node, pointer, ancestors in source_walk(document):
            for field in ('ranges', 'raw_ranges'):
                table = node.get(field)
                if (not isinstance(table, dict) or node.get('schema') != 'derived-source-identity-index/1'):
                    continue
                for fingerprint, value in table.items():
                    if not isinstance(value, str):
                        continue
                    raw = base64.b64decode(value, validate=True) if field == 'raw_ranges' else value.encode('utf-8')
                    if sha(raw) != fingerprint:
                        raise ValueError('Original range key/content mismatch')
                    location = pointer + '/' + field + '/' + fingerprint
                    file_slots.append((location, value, raw, 'base64' if field == 'raw_ranges' else 'utf8',
                                       list(coordinates.get(fingerprint, {}).values()), False, 'identity_range_cache'))
            for field in ('source_excerpt', 'excerpt', 'declaration_header', 'header'):
                value = node.get(field)
                if not isinstance(value, str) or not value:
                    continue
                if field in ('declaration_header', 'header'):
                    if HEADER_ONLY.fullmatch(value) or not re.search(r'\b(?:function|return|local)\b', value):
                        continue
                raw = value.encode('utf-8')
                choices = list(coordinates.get(sha(raw), {}).values())
                own = coordinate(node)
                if own and own not in choices:
                    choices.insert(0, own)
                if not choices:
                    for ancestor in reversed(ancestors):
                        own = coordinate(ancestor)
                        if own:
                            choices.append(own)
                            break
                original_locator = node.get('source_file', node.get('artifact_path', ''))
                if (field in ('source_excerpt', 'excerpt') and not choices
                        and isinstance(original_locator, str)
                        and original_locator.lower().endswith(('.md', '.txt', '.json'))):
                    # Historical report quotations are not installed Lua source.
                    # They belong to the separate privacy/evidence export review.
                    non_lua_excerpts.append({'path': name, 'pointer': pointer + '/' + field})
                    continue
                if field in ('declaration_header', 'header'):
                    line = node.get('declaration_line', node.get('line'))
                    if type(line) is int:
                        choices = [{**choice, 'line_start': line, 'line_end': line} for choice in choices]
                required = (name, pointer) in strict or sha(raw) in strict_hashes
                file_slots.append((pointer + '/' + field, value, raw, 'utf8', choices, required,
                                   'strict_knowledge_excerpt' if required else 'source_literal'))
        for location, original, raw, encoding, choices, required, kind in file_slots:
            try:
                current = at(target, location)
            except (KeyError, IndexError, TypeError):
                continue
            # A redactor must not quietly change the source body before slotting.
            if current != original:
                raise ValueError('Public source body differs before slotting: ' + name + location)
            slot_id = digest({'path': name, 'pointer': location, 'content_sha256': sha(raw)})
            slot = {'id': slot_id, 'path': name, 'pointer': location, 'kind': kind,
                    'encoding': encoding, 'content_sha256': sha(raw), 'content_bytes': len(raw),
                    'original_json_value_sha256': digest(original),
                    'line_count': len(raw.splitlines()), 'coordinates': choices,
                    'required_for_knowledge_shape': required,
                    'missing_policy': 'ERROR' if required else 'DELETE_OBJECT_FIELD'}
            slots.append(slot)
            set_at(target, location, {MARKER: slot_id})
        if file_slots:
            templates[name] = target
    recipe = {'schema': SCHEMA, 'slots': slots,
              'contains_source_payload': False, 'source_paths_are_logical': True,
              'original_facts_and_source_identities_are_not_revised': True,
              'range_match_is_not_whole_file_identity': True,
              'requires_identity_commitment_rebind_after_assembly': True,
              'excluded_non_lua_report_excerpts': non_lua_excerpts,
              'summary': {'slots': len(slots), 'template_files': len(templates),
                          'required_slots': sum(s['required_for_knowledge_shape'] for s in slots),
                          'without_coordinates': sum(not s['coordinates'] for s in slots)}}
    return recipe, templates


class Sources:
    def __init__(self, inputs):
        self.inputs = [Path(p).resolve() for p in inputs]
        self.archives = {}
        self.cache = {}

    def candidates(self, source_file):
        if source_file in self.cache:
            return self.cache[source_file]
        results = []
        for i, root in enumerate(self.inputs):
            names = tuple(dict.fromkeys((source_file, source_file.removeprefix('scripts/'))))
            if root.is_dir():
                for name in names:
                    path = safe_child(root, name)
                    if path.is_file():
                        results.append((i, path.read_bytes()))
                        break
            elif root.is_file() and zipfile.is_zipfile(root):
                if root not in self.archives:
                    self.archives[root] = zipfile.ZipFile(root)
                archive = self.archives[root]
                members = archive.namelist()
                for name in names:
                    if members.count(name) > 1:
                        raise ValueError('Ambiguous duplicate ZIP source member')
                    if name in members:
                        results.append((i, archive.read(name)))
                        break
            else:
                raise ValueError('Source must be an existing directory or ZIP archive')
        self.cache[source_file] = results
        return results

    def close(self):
        for archive in self.archives.values():
            archive.close()


def variants(raw):
    lf = raw.replace(b'\r\n', b'\n')
    candidates = [('RAW', raw), ('LF', lf), ('CRLF', lf.replace(b'\n', b'\r\n'))]
    seen = set()
    for mode, value in candidates:
        for trim, candidate in (('', value), ('_NO_FINAL_NEWLINE', value.rstrip(b'\r\n'))):
            if candidate not in seen:
                seen.add(candidate)
                yield mode + trim, candidate


def recover(slot, sources, cache=None):
    """Recover only bytes whose SHA and length equal the original payload slot."""
    cache = {} if cache is None else cache
    key = (slot['content_sha256'], slot['content_bytes'], digest(slot['coordinates']),
           slot['encoding'], slot['original_json_value_sha256'])
    if key in cache:
        value, evidence = cache[key]
        if value is not None:
            raw = (base64.b64decode(value, validate=True) if slot['encoding'] == 'base64'
                   else value.encode('utf-8'))
            if (len(raw) != slot['content_bytes'] or sha(raw) != slot['content_sha256']
                    or digest(value) != slot['original_json_value_sha256']):
                raise ValueError('Cached source payload differs from requested slot value')
        return value, evidence
    expected = slot['content_sha256']
    for coordinate_row in slot['coordinates']:
        for source_index, full in sources.candidates(coordinate_row['source_file']):
            lines = full.splitlines(keepends=True)
            count = coordinate_row['line_end'] - coordinate_row['line_start'] + 1
            counts = tuple(dict.fromkeys((count, slot['line_count'])))
            for line_count in counts:
                if line_count <= 0 or line_count > len(lines):
                    continue
                first = coordinate_row['line_start'] - 1
                starts = [first] if 0 <= first <= len(lines) - line_count else []
                starts.extend(p for p in range(len(lines) - line_count + 1) if p != first)
                for start in starts:
                    block = b''.join(lines[start:start + line_count])
                    for mode, raw in variants(block):
                        if len(raw) != slot['content_bytes'] or sha(raw) != expected:
                            continue
                        value = base64.b64encode(raw).decode('ascii') if slot['encoding'] == 'base64' else raw.decode('utf-8')
                        if digest(value) != slot['original_json_value_sha256']:
                            raise ValueError('Recovered source bytes have different original JSON value')
                        evidence = {'source_input_index': source_index,
                            'source_file': coordinate_row['source_file'],
                            'provided_file_sha256': sha(full),
                            'expected_original_file_sha256': coordinate_row['expected_file_sha256'],
                            'provided_whole_file_equals_original': sha(full) == coordinate_row['expected_file_sha256'],
                            'match_basis': 'EXACT_ORIGINAL_RANGE_CONTENT_HASH',
                            'matched_line_start': start + 1, 'matched_line_end': start + line_count,
                            'line_transform': mode, 'content_sha256': expected}
                        cache[key] = (value, evidence)
                        return value, evidence
    cache[key] = (None, None)
    return None, None


def hydrate(root, recipe, source_inputs, output_root=None, write=True):
    """Hydrate templates into a separate root; unresolved optional slots vanish.

    Completeness is a build report, not validation PASS. The exporter must next
    rebind authoritative hashes, manifests and epoch descriptors and run the
    original validators. No service is started and no cache is created here.
    """
    if recipe.get('schema') != SCHEMA:
        raise ValueError('Unsupported source recipe')
    root = Path(root).resolve()
    output = Path(output_root).resolve() if output_root is not None else None
    if write and (output is None or output == root or output.is_relative_to(root) or root.is_relative_to(output)):
        raise ValueError('Choose a separate output root')
    sources = Sources(source_inputs)
    documents, cache, recovered, gaps, removed_optional = {}, {}, [], [], []
    try:
        for slot in recipe['slots']:
            name = slot['path']
            if name not in documents:
                documents[name] = read_json(safe_child(root, name))
            current = at(documents[name], slot['pointer'])
            if current != {MARKER: slot['id']}:
                raise ValueError('Source slot marker mismatch: ' + name + slot['pointer'])
            value, evidence = recover(slot, sources, cache)
            if value is None:
                gaps.append({k: slot[k] for k in ('id', 'path', 'pointer', 'content_sha256',
                    'coordinates', 'required_for_knowledge_shape')})
                if (not slot['required_for_knowledge_shape']
                        and slot.get('missing_policy') == 'DELETE_OBJECT_FIELD'):
                    set_at(documents[name], slot['pointer'], None, remove=True)
                    removed_optional.append({'id': slot['id'], 'path': name,
                        'pointer': slot['pointer'], 'kind': slot['kind'],
                        'proof_policy': 'MISSING_ORIGINAL_PAYLOAD_REJECTED_BY_UNCHANGED_GUARD'})
            else:
                set_at(documents[name], slot['pointer'], value)
                recovered.append({'id': slot['id'], 'path': name, 'pointer': slot['pointer'], **evidence})
        if write:
            for name, document in documents.items():
                write_json(safe_child(output, name), document)
    finally:
        sources.close()
    required = [g for g in gaps if g['required_for_knowledge_shape']]
    kinds = {slot['id']: slot['kind'] for slot in recipe['slots']}
    noncache_gaps = [g for g in gaps if kinds[g['id']] != 'identity_range_cache']
    report = {'schema': 'dst-local-source-hydration-result/1',
        'status': ('REQUIRED_SOURCE_GAP' if required else
                   'REQUIRED_SLOTS_ASSEMBLED_WITH_OPTIONAL_SOURCE_GAPS_REBIND_REQUIRED' if gaps
                   else 'SOURCE_SLOTS_ASSEMBLED_REBIND_REQUIRED'),
        'source_slots': len(recipe['slots']), 'recovered_count': len(recovered),
        'missing_required_count': len(required), 'missing_optional_count': len(gaps) - len(required),
        'missing_noncache_source_literal_count': len(noncache_gaps),
        'removed_optional_fields': removed_optional,
        'remaining_unresolved_marker_count': sum(
            MARKER in node for document in documents.values()
            for node, _, _ in walk(document)),
        'required_gaps': required, 'optional_gaps': [g for g in gaps if not g['required_for_knowledge_shape']],
        'matches': recovered, 'runtime_validation_performed': False,
        'whole_historical_snapshot_identity_inferred': False,
        'next_step': 'Rebind transformed data identities/manifests/catalog; run unchanged original validators before runtime.'}
    return report, documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    generate = sub.add_parser('generate')
    generate.add_argument('--private-root', type=Path, required=True)
    generate.add_argument('--public-root', type=Path)
    generate.add_argument('--recipe', type=Path, required=True)
    generate.add_argument('--templates-out', type=Path)
    restore = sub.add_parser('hydrate')
    restore.add_argument('--root', type=Path, required=True)
    restore.add_argument('--recipe', type=Path, required=True)
    restore.add_argument('--source', type=Path, action='append', required=True)
    restore.add_argument('--output-root', type=Path, required=True)
    restore.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'generate':
        recipe, templates = generate_recipe(args.private_root, args.public_root)
        write_json(args.recipe, recipe)
        if args.templates_out:
            for name, document in templates.items():
                write_json(safe_child(args.templates_out, name), document)
        print(json.dumps(recipe['summary']))
        return 0
    report, _ = hydrate(args.root, read_json(args.recipe), args.source, args.output_root)
    write_json(args.report, report)
    print(json.dumps({k: report[k] for k in ('status', 'source_slots', 'recovered_count',
        'missing_required_count', 'missing_optional_count')}))
    return int(bool(report['missing_required_count']))


if __name__ == '__main__':
    raise SystemExit(main())

"""Bounded, explicit research-locator checks; never returns game source text.

An archive match, an exact file/range and a range-only match are distinct.
Authored Scope and admission states are never rewritten by this helper.
"""
from collections import Counter, OrderedDict
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import stat
import zipfile


MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_CACHE_BYTES = 64 * 1024 * 1024
MAX_SCAN_WINDOWS = 200000
MAX_SCAN_BYTES = 128 * 1024 * 1024
STATUSES = ('EXACT_FILE_RANGE', 'RANGE_ONLY', 'CHANGED_UNKNOWN', 'MISSING')
HASH = re.compile(r'[0-9a-f]{64}\Z')
BOUNDARY = {'source_text_returned': False, 'runtime_verified': False, 'coding_admission': False}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(name):
    return (isinstance(name, str) and bool(name) and not any(c in name for c in ('\\', ':', '\x00'))
            and not any(ord(c) < 32 for c in name) and all(p not in ('', '.', '..') for p in name.split('/')))


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def validate_ref(ref):
    if not isinstance(ref, dict) or not isinstance(ref.get('id'), str) or not ref['id'].strip():
        raise ValueError('Malformed mechanism source reference')
    if not safe(ref.get('source_file')) or not ref['source_file'].startswith('scripts/'):
        raise ValueError('Unsafe source locator')
    if any(not isinstance(ref.get(k), str) or not HASH.fullmatch(ref[k]) for k in ('file_sha256', 'range_sha256')):
        raise ValueError('Malformed mechanism source hash')
    first, last = ref.get('line_start'), ref.get('line_end')
    if type(first) is not int or type(last) is not int or not 1 <= first <= last:
        raise ValueError('Malformed mechanism source range')
    symbols = ref.get('symbols')
    if not isinstance(symbols, list) or any(not isinstance(s, str) or not s.strip() for s in symbols):
        raise ValueError('Malformed mechanism source symbols')


def reject_link(path):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
        raise ValueError('Unsafe symlink or reparse source path')


class Source:
    """Read only explicit referenced paths; archive metadata is checked once."""
    def __init__(self, path, index):
        self.path = Path(path).absolute()
        self.index = index
        self.zip = None
        self.files, self.cache, self.cache_bytes, self.matches = {}, OrderedDict(), 0, {}
        for parent in reversed((self.path, *self.path.parents)):
            reject_link(parent)
        if self.path.is_dir():
            self.kind, self.sha256 = 'DIRECTORY', None
            return
        if not self.path.is_file():
            raise ValueError('Explicit mechanism source input is not a file or directory')
        self.kind, self.sha256 = 'ZIP', file_sha(self.path)
        self.zip = zipfile.ZipFile(self.path)
        try:
            seen = set()
            for info in self.zip.infolist():
                original = info.orig_filename[:-1] if info.orig_filename.endswith('/') else info.orig_filename
                if info.orig_filename != info.filename or not safe(original):
                    raise ValueError('Unsafe normalized source ZIP member')
                name = info.filename[:-1] if info.is_dir() else info.filename
                if not safe(name) or name in seen:
                    raise ValueError('Unsafe or duplicate source ZIP member')
                seen.add(name)
                if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                    raise ValueError('Unsafe symlink or encrypted source ZIP member')
                if not info.is_dir():
                    self.files[name] = info
        except Exception:
            self.close()
            raise

    def close(self):
        if self.zip is not None:
            self.zip.close()

    def identity(self):
        return {'source_input_index': self.index, 'kind': self.kind, 'archive_sha256': self.sha256}

    def member(self, name):
        if name in self.cache:
            self.cache.move_to_end(name)
            return self.cache[name][0]
        if self.zip is not None:
            info = self.files.get(name)
            if info is None:
                return None
            if info.file_size > MAX_MEMBER_BYTES:
                return {'error': 'member_size_limit'}
            stream = self.zip.open(info)
        else:
            target = None
            for relative in dict.fromkeys((name, name.removeprefix('scripts/'))):
                candidate = self.path
                for part in relative.split('/'):
                    candidate = candidate / part
                    try:
                        reject_link(candidate)
                    except FileNotFoundError:
                        break
                else:
                    target = candidate
                    break
            if target is None:
                return None
            if not target.resolve().is_relative_to(self.path.resolve()) or not target.is_file():
                raise ValueError('Unsafe or non-file source member')
            if target.stat().st_size > MAX_MEMBER_BYTES:
                return {'error': 'member_size_limit'}
            stream = target.open('rb')
        with stream:
            raw = stream.read(MAX_MEMBER_BYTES + 1)
        if len(raw) > MAX_MEMBER_BYTES:
            return {'error': 'member_size_limit'}
        result = {'file_sha256': sha(raw)}
        try:
            result['lines'] = raw.decode('utf-8').splitlines()
        except UnicodeDecodeError:
            result['error'] = 'source_not_utf8'
        cost = len(raw)
        while self.cache and self.cache_bytes + cost > MAX_CACHE_BYTES:
            _, (_, old_cost) = self.cache.popitem(last=False)
            self.cache_bytes -= old_cost
        self.cache[name] = (result, cost)
        self.cache_bytes += cost
        return result

    def locate_range(self, ref, lines):
        key = (ref['source_file'], ref['line_end'] - ref['line_start'] + 1, ref['range_sha256'])
        if key in self.matches:
            return self.matches[key]
        _, width, wanted = key
        count, scanned, hits = max(0, len(lines) - width + 1), 0, []
        if count > MAX_SCAN_WINDOWS:
            return {'reason': 'range_scan_limit'}
        for offset in range(count):
            raw = '\n'.join(lines[offset:offset + width]).encode('utf-8')
            scanned += len(raw)
            if scanned > MAX_SCAN_BYTES:
                result = {'reason': 'range_scan_limit'}
                break
            if sha(raw) == wanted:
                hits.append(offset + 1)
                if len(hits) > 1:
                    result = {'reason': 'ambiguous_range_match', 'match_count_at_least': 2}
                    break
        else:
            result = ({'line_start': hits[0], 'line_end': hits[0] + width - 1}
                      if hits else {'reason': 'range_content_not_found'})
        self.matches[key] = result
        return result

    def check(self, doc, ref):
        result = {'source_input_index': self.index, 'provided_archive_sha256': self.sha256,
                  'evidence_archive_identity_matched': self.sha256 == doc['archive_sha256']}
        member = self.member(ref['source_file'])
        strict = result['evidence_archive_identity_matched']
        if member is None:
            if strict:
                raise ValueError('Mechanism evidence archive member is missing: ' + ref['source_file'])
            return dict(result, status='MISSING', reason='source_member_missing')
        if 'file_sha256' in member:
            result['provided_file_sha256'] = member['file_sha256']
        if member.get('error'):
            if strict:
                raise ValueError('Mechanism evidence archive member cannot be verified: ' + member['error'])
            return dict(result, status='CHANGED_UNKNOWN', reason=member['error'])
        same_file = member['file_sha256'] == ref['file_sha256']
        lines, first, last = member['lines'], ref['line_start'], ref['line_end']
        same_range = last <= len(lines) and sha('\n'.join(lines[first-1:last]).encode('utf-8')) == ref['range_sha256']
        if same_file:
            if not same_range:
                raise ValueError('Mechanism source range commitment mismatch: ' + ref['source_file'])
            return dict(result, status='EXACT_FILE_RANGE', line_start=first, line_end=last,
                        source_file_identity_verified=True, range_verified=True)
        if strict:
            raise ValueError('Mechanism source member hash mismatch in evidence archive: ' + ref['source_file'])
        match = self.locate_range(ref, lines)
        if 'line_start' in match:
            return dict(result, status='RANGE_ONLY', **match,
                        relocated=match['line_start'] != first, source_file_identity_verified=False,
                        range_verified=True, behavior_verified=False)
        return dict(result, status='CHANGED_UNKNOWN', **match,
                    source_file_identity_verified=False, range_verified=False)


def summarize(references):
    counts = Counter(r['status'] for r in references)
    exact = counts['EXACT_FILE_RANGE']
    status = ('NO_SOURCE_REFERENCES' if not references else 'STATIC_LOCATOR_HASHES_VERIFIED'
              if exact == len(references) else 'PARTIAL_LOCATOR_MATCHES'
              if exact or counts['RANGE_ONLY'] else 'NO_LOCATOR_MATCHES')
    return {'status': status, 'total_references': len(references), 'verified_references': exact,
            'reference_counts': {key: counts[key] for key in STATUSES},
            'all_references_verified': bool(references) and exact == len(references)}


def verify(root, sources):
    root = Path(root)
    registry_path = root / 'knowledge/FAMILY-REGISTRY.json'
    if not registry_path.is_file():
        return dict(BOUNDARY, status='NO_REGISTERED_MECHANISM_FAMILY', verified_references=0)
    registry = json.loads(registry_path.read_bytes())
    documents, all_refs = [], []
    with ExitStack() as stack:
        inputs = []
        for index, source in enumerate(sources):
            item = Source(source, index)
            stack.callback(item.close)
            inputs.append(item)
        for family in registry['families']:
            if family['name'] != 'native_mechanism':
                continue
            for row in family['documents']:
                if not safe(row['file']) or not isinstance(row.get('sha256'), str) or not HASH.fullmatch(row['sha256']):
                    raise ValueError('Unsafe or malformed mechanism candidate artifact')
                candidate_path = (root / 'knowledge' / row['file']).resolve()
                if not candidate_path.is_relative_to((root / 'knowledge').resolve()):
                    raise ValueError('Mechanism candidate artifact escaped root')
                raw = candidate_path.read_bytes()
                if sha(raw) != row['sha256']:
                    raise ValueError('Mechanism candidate hash differs before source preparation')
                doc = json.loads(raw)
                if (not isinstance(doc.get('archive_sha256'), str) or not HASH.fullmatch(doc['archive_sha256'])
                        or not isinstance(doc.get('source_epoch'), str) or not doc['source_epoch'].strip()
                        or not isinstance(doc.get('source_references'), list)):
                    raise ValueError('Malformed mechanism source document')
                ids, refs = set(), []
                for ref in doc['source_references']:
                    validate_ref(ref)
                    if ref['id'] in ids:
                        raise ValueError('Duplicate mechanism source reference ID')
                    ids.add(ref['id'])
                    checks = [item.check(doc, ref) for item in inputs]
                    # Keep every input's result, even when another input matches.
                    best = min(checks, key=lambda c: STATUSES.index(c['status'])) if checks else None
                    result = {'reference_id': ref['id'], 'source_file': ref['source_file'],
                              'evidence_file_sha256': ref['file_sha256'], 'evidence_range_sha256': ref['range_sha256'],
                              'evidence_line_start': ref['line_start'], 'evidence_line_end': ref['line_end'],
                              'status': best['status'] if best else 'CHANGED_UNKNOWN', 'source_checks': checks}
                    if best is None:
                        result['reason'] = 'no_explicit_source_input'
                    refs.append(result)
                documents.append({'file': row['file'], 'sha256': row['sha256'],
                                  'evidence_epoch': doc['source_epoch'], 'archive_sha256': doc['archive_sha256'],
                                  'references': refs, **summarize(refs), **BOUNDARY})
                all_refs.extend(refs)
        provided = [item.identity() for item in inputs]
    return {**summarize(all_refs), 'documents': documents, 'provided_sources': provided, **BOUNDARY}

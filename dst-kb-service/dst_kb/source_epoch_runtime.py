"""Frozen source environments, never a promotion of individual record evidence."""
import copy
import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from hashlib import sha256
from pathlib import Path

from .config import KBError, configuration

SCHEMA = 'dst-source-epochs/1'
_ACTIVE = ContextVar('dst_kb_source_epoch', default=None)
_HASH = re.compile(r'[a-f0-9]{64}')


def _hash(path):
    try:
        return sha256(Path(path).read_bytes()).hexdigest()
    except OSError as exc:
        raise KBError('SOURCE_EPOCH_UNAVAILABLE', 'Cannot read committed source environment input: ' + str(path)) from exc


def _path(base, value):
    if not isinstance(value, str) or not value.strip():
        raise KBError('INVALID_CONFIG', 'Source environment paths must be nonempty strings.')
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def _commitment(base, value, name):
    if not isinstance(value, dict) or not _HASH.fullmatch(str(value.get('sha256', ''))):
        raise KBError('INVALID_CONFIG', 'Missing exact SHA256 commitment for ' + name)
    return _path(base, value.get('path')), value['sha256']


@dataclass(frozen=True)
class EpochContext:
    source_epoch: str
    root: Path
    index: Path
    config: Path
    catalog: Path
    contract_map: Path
    source_identity_map: Path
    cache_key: str
    commitments: tuple
    metadata_json: str

    @property
    def map_path(self):
        return self.contract_map

    def assert_current(self):
        for path, expected in self.commitments:
            if _hash(path) != expected:
                raise KBError('SOURCE_EPOCH_STALE', 'Committed source environment input changed; rebuild assets and reconnect: ' + str(path))

    def metadata(self):
        return json.loads(self.metadata_json)

    def index_metadata(self):
        return {'source_epoch': self.source_epoch, 'source_epoch_context': self.cache_key,
                'contract_map_sha256': dict(self.commitments)[self.contract_map],
                'source_identity_map_sha256': dict(self.commitments)[self.source_identity_map]}


def active_epoch():
    return _ACTIVE.get()


def source_preparation_document():
    context = active_epoch()
    if context is None:
        return None
    binding = context.metadata().get('source_preparation')
    if binding is None:
        return None
    path, expected = _commitment(context.catalog.parent, binding, 'source_preparation')
    if _hash(path) != expected:
        raise KBError('SOURCE_EPOCH_STALE', 'Source preparation assessment changed; reconnect after preparing sources.')
    return json.loads(path.read_bytes())


def epoch_arguments(arguments):
    """Keep generated expansion/navigation calls in their originating epoch."""
    result = dict(arguments)
    context = active_epoch()
    if context is not None:
        try:
            selected = context.source_epoch
        except AttributeError:
            selected = context.metadata()['source_epoch']
        if not isinstance(selected, str) or not selected:
            raise ValueError('Navigation requires the bound canonical source epoch')
        result['source_epoch'] = selected
    return result


def epoch_key():
    context = active_epoch()
    return context.cache_key if context is not None else 'legacy-unbound'


@contextmanager
def bind_epoch(context):
    token = _ACTIVE.set(context)
    try:
        yield context
    finally:
        _ACTIVE.reset(token)


def epoch_bound(function):
    """Bind each direct Service call, including nested calls and exceptional exits."""
    @wraps(function)
    def call(self, *args, **kwargs):
        context = getattr(self, 'epoch_context', None)
        selected = kwargs.pop('source_epoch', None)
        if selected is not None and (context is None or selected != context.source_epoch):
            raise KBError('SOURCE_EPOCH_MISMATCH', 'Select another source environment through the public tool router or a new Service instance.')
        with bind_epoch(context):
            return function(self, *args, **kwargs)
    return call


def resolve_epoch(config=None, source_epoch=None):
    """Return None only for an explicitly legacy single-root configuration."""
    config_path, options = configuration(config)
    catalog_name = options.get('source_epochs_path')
    if not catalog_name:
        if source_epoch is not None:
            raise KBError('SOURCE_EPOCH_UNAVAILABLE', 'This configuration has no source epoch catalog.')
        return None
    catalog_path = _path(config_path.parent, catalog_name)
    try:
        catalog_raw = catalog_path.read_bytes()
        catalog = json.loads(catalog_raw)
    except (OSError, ValueError) as exc:
        raise KBError('SOURCE_EPOCH_UNAVAILABLE', 'Cannot read source epoch catalog.') from exc
    if catalog.get('schema_version') != SCHEMA or not isinstance(catalog.get('epochs'), dict):
        raise KBError('INVALID_CONFIG', 'Unsupported source epoch catalog schema.')
    epochs = catalog['epochs']
    selected = source_epoch if source_epoch is not None else options.get('default_source_epoch', catalog.get('default_source_epoch'))
    if not isinstance(selected, str) or not selected:
        raise KBError('INVALID_CONFIG', 'A default_source_epoch is required.')
    choices = [key for key, row in epochs.items() if selected == key or selected in row.get('aliases', [])]
    if len(choices) != 1:
        raise KBError('INVALID_SOURCE_EPOCH', 'Unknown or ambiguous source_epoch: ' + selected)
    selected = choices[0]
    entry = epochs[selected]
    base = catalog_path.parent
    root, index = (_path(base, entry.get(name)) for name in ('knowledge_root', 'index_path'))
    if index.is_relative_to(root):
        raise KBError('INVALID_CONFIG', 'Derived epoch index must be outside canonical knowledge.')
    indexes = [_path(base, row.get('index_path')) for row in epochs.values()]
    if len(indexes) != len(set(indexes)):
        raise KBError('INVALID_CONFIG', 'Every source environment requires an independent index path.')
    commitments = [(catalog_path, sha256(catalog_raw).hexdigest())]
    if config_path.is_file():
        commitments.append((config_path, _hash(config_path)))
    assets = {}
    for field in ('knowledge_manifest', 'contract_map', 'source_identity_map'):
        path, checksum = _commitment(base, entry.get(field), field)
        if field == 'knowledge_manifest' and path != root / 'PACKAGE-MANIFEST.json':
            raise KBError('INVALID_CONFIG', 'knowledge_manifest must commit the selected knowledge root.')
        commitments.append((path, checksum))
        assets[field] = path
    ledger = entry.get('applicability_ledger')
    if ledger is not None:
        commitments.append(_commitment(base, ledger, 'applicability_ledger'))
    sources = entry.get('source_manifests')
    if not isinstance(sources, list) or not sources:
        raise KBError('INVALID_CONFIG', 'Source environments require committed source manifests.')
    for source in sources:
        commitments.append(_commitment(base, source, 'source_manifests'))
    preparation = entry.get('source_preparation')
    preparation_summary = None
    if preparation is not None:
        path, expected = _commitment(base, preparation, 'source_preparation')
        commitments.append((path, expected))
        if _hash(path) != expected:
            raise KBError('SOURCE_EPOCH_STALE', 'Source preparation assessment commitment changed.')
        assessment = json.loads(path.read_bytes())
        if assessment.get('schema') != 'dst-source-preparation-assessment/1':
            raise KBError('INVALID_CONFIG', 'Unsupported source preparation assessment.')
        preparation_summary = assessment['summary']
    key_data = {'source_epoch': selected, 'root': str(root), 'index': str(index),
                'commitments': [(str(p), h) for p, h in commitments]}
    key = sha256(json.dumps(key_data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    metadata = {'source_epoch': selected, 'source_environment_identity': copy.deepcopy(entry.get('source_environment_identity', {})),
                'source_manifests': copy.deepcopy(sources), 'source_epoch_context_sha256': key,
                'record_evidence_scope': 'Each record retains its original source Scope; environment selection does not verify all records for this build.',
                'review_coverage': copy.deepcopy(entry.get('review_coverage', {}))}
    if preparation is not None:
        metadata['source_preparation'] = copy.deepcopy(preparation)
        metadata['source_input_assessment'] = copy.deepcopy(preparation_summary)
    result = EpochContext(selected, root, index, config_path, catalog_path, assets['contract_map'],
                          assets['source_identity_map'], key, tuple(commitments),
                          json.dumps(metadata, ensure_ascii=False, separators=(',', ':')))
    result.assert_current()
    return result

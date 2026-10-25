"""Disposable, bounded reuse of pure analysis inside one retrieval request.

Only explicitly decorated pure derivations participate. Record/source/projection
guards and final answers are never cached here. Support derivations use every
actual typed input, including their complete original context and request frames.
New requests start empty; stored snapshots never escape their request.
"""
import marshal
import sys
from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from hashlib import sha256


_ACTIVE = ContextVar('dst_kb_request_analysis', default=None)


def _frozen(value):
    kind = type(value)
    if kind in (str, bool, int, float, bytes, type(None)):
        return kind, value
    if kind in (tuple, list):
        return kind, tuple(_frozen(item) for item in value)
    if kind is dict:
        # Keep original order and container types; do not normalize source input.
        return kind, tuple((_frozen(key), _frozen(item)) for key, item in value.items())
    if kind in (set, frozenset):
        return kind, frozenset(_frozen(item) for item in value)
    raise TypeError('unsupported analysis input')


def _size(value):
    amount = sys.getsizeof(value)
    if type(value) in (tuple, list, set, frozenset):
        amount += sum(_size(item) for item in value)
    elif type(value) is dict:
        amount += sum(_size(key) + _size(item) for key, item in value.items())
    return amount


def _supported(value):
    """Accept only exact builtin value trees, never code or owned objects."""
    kind = type(value)
    if kind in (str, bool, int, float, bytes, type(None)):
        return
    if kind in (tuple, list, set, frozenset):
        for item in value:
            _supported(item)
        return
    if kind is dict:
        for key, item in value.items():
            _supported(key)
            _supported(item)
        return
    raise TypeError('unsupported analysis value')


def _encoded(value, version=4):
    _supported(value)
    # These bytes are created and consumed only in this process, never loaded
    # from disk or a caller. Builtin container types and order survive decoding.
    return marshal.dumps(value, version)


class RequestAnalysis:
    def __init__(self, max_entries=8192, max_bytes=24 * 1024 * 1024):
        if type(max_entries) is not int or max_entries < 1:
            raise ValueError('max_entries must be a positive integer')
        if type(max_bytes) is not int or max_bytes < 1:
            raise ValueError('max_bytes must be a positive integer')
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.entries = OrderedDict()
        self.charged_bytes = self.hits = self.misses = 0
        self.support_cache = None

    def compute(self, function, args, kwargs, *, compact=False):
        try:
            # Version 2 omits marshal's identity/reference encoding: equal
            # complete inputs do not miss merely because one tree shares nodes.
            # No context field, source marker, role or container type is dropped.
            key = ((function, sha256(_encoded((args, kwargs), 2)).digest()) if compact else
                   (function, _frozen(args), _frozen(kwargs)))
        except (TypeError, ValueError, RecursionError):
            return function(*args, **kwargs)
        found = self.entries.get(key)
        if found is not None:
            self.hits += 1
            snapshot, _ = found
            self.entries.move_to_end(key)
            return marshal.loads(snapshot)
        self.misses += 1
        result = function(*args, **kwargs)
        # Generators and context-owned objects are intentionally unsupported.
        try:
            snapshot = _encoded(result)
        except (TypeError, ValueError, RecursionError):
            return result
        size = _size(key) + sys.getsizeof(snapshot)
        if size <= self.max_bytes:
            self.entries[key] = (snapshot, size)
            self.charged_bytes += size
            while len(self.entries) > self.max_entries or self.charged_bytes > self.max_bytes:
                _, (_, removed) = self.entries.popitem(last=False)
                self.charged_bytes -= removed
        return result

    def compute_support(self, function, args, kwargs):
        # Whole support results must survive the many small feature derivations
        # between ranking and projection. A separate bounded LRU avoids those
        # features evicting already analyzed original atoms in the same request.
        if self.support_cache is None:
            self.support_cache = RequestAnalysis(min(self.max_entries, 4096),
                                                 min(self.max_bytes, 8 * 1024 * 1024))
        return self.support_cache.compute(function, args, kwargs, compact=True)

    def clear(self):
        self.entries.clear()
        self.charged_bytes = 0
        if self.support_cache is not None:
            self.support_cache.clear()

    def info(self):
        result = {'entries': len(self.entries), 'charged_bytes': self.charged_bytes,
                'max_entries': self.max_entries, 'max_bytes': self.max_bytes,
                'hits': self.hits, 'misses': self.misses}
        if self.support_cache is not None:
            result['support_cache'] = self.support_cache.info()
        return result


@contextmanager
def analysis_scope():
    active = _ACTIVE.get()
    if active is not None:
        yield active
        return
    active = RequestAnalysis()
    token = _ACTIVE.set(active)
    try:
        yield active
    finally:
        _ACTIVE.reset(token)
        active.clear()


def analyzed_request(function):
    """Establish a lifecycle only; never memoize a request/support result."""
    @wraps(function)
    def invoke(*args, **kwargs):
        with analysis_scope():
            return function(*args, **kwargs)
    return invoke


def memoized_analysis(function):
    """Reuse an explicitly pure derivation by all of its actual typed inputs."""
    @wraps(function)
    def invoke(*args, **kwargs):
        active = _ACTIVE.get()
        return (function(*args, **kwargs) if active is None else
                active.compute(function, args, kwargs))
    return invoke


def memoized_support(function):
    """Reuse pure support by complete typed content; external guards stay live."""
    @wraps(function)
    def invoke(*args, **kwargs):
        active = _ACTIVE.get()
        return (function(*args, **kwargs) if active is None else
                active.compute_support(function, args, kwargs))
    return invoke

"""Bounded process-local memoization of query-independent contract derivations."""
import copy
import json
from collections import OrderedDict
from hashlib import sha256
from threading import RLock


def _json_bytes(value):
    # 顺序也是输出契约的一部分；不排序字典，也不截断原输入。
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


class BoundedContractCache:
    """No filesystem, admission or evidence resolution is performed here.

    The caller supplies the actual full per-record map, related catalog rules
    and accepted navigation used by compute. Keys include their complete ordered
    JSON content, alongside
    the complete record, family and normalized symbol. IDs and file stat values
    never substitute for these inputs.
    """

    def __init__(self, max_entries=1024, max_bytes=32 * 1024 * 1024):
        if type(max_entries) is not int or max_entries < 1:
            raise ValueError('max_entries must be a positive integer')
        if type(max_bytes) is not int or max_bytes < 1:
            raise ValueError('max_bytes must be a positive integer')
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self._entries = OrderedDict()
        self._bytes = 0
        self._lock = RLock()

    def get_or_compute(self, record, family, symbol, record_map, navigation, compute):
        inputs = tuple(_json_bytes(value) for value in
                       (record, family, symbol, record_map, navigation))
        key = tuple(sha256(value).digest() for value in inputs)
        with self._lock:
            if key in self._entries:
                result, _, encoded = self._entries[key]
                self._entries.move_to_end(key)
                return json.loads(result) if encoded else copy.deepcopy(result)
            result = compute()
            payload = _json_bytes(result)
            decoded = json.loads(payload)
            # Contract derivations are JSON values. Immutable serialized storage
            # avoids copying their repeated proof dictionaries twice per miss,
            # while every caller still receives its own recursively isolated tree.
            # Preserve the historical deepcopy behavior for non-JSON containers.
            encoded = decoded == result
            stored = payload if encoded else copy.deepcopy(result)
            # 输入只留下固定长度内容哈希；按保留的键和输出JSON计容量。
            # 不重复计入已释放的完整输入，否则同一条目的多方法会抖动淘汰。
            size = sum(map(len, key)) + len(payload)
            if size <= self.max_bytes:
                self._entries[key] = (stored, size, encoded)
                self._bytes += size
                while len(self._entries) > self.max_entries or self._bytes > self.max_bytes:
                    _, (_, removed_size, _) = self._entries.popitem(last=False)
                    self._bytes -= removed_size
            return decoded if encoded else copy.deepcopy(result)

    def clear(self):
        with self._lock:
            self._entries.clear()
            self._bytes = 0

    def info(self):
        with self._lock:
            return {'entries': len(self._entries), 'charged_json_bytes': self._bytes,
                    'max_entries': self.max_entries, 'max_bytes': self.max_bytes}

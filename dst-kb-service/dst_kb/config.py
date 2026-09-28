import json
import os
from pathlib import Path

class KBError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)

def settings(path=None):
    config_path = Path(path or os.environ.get('DST_KB_CONFIG', Path.home()/'.codex/dst-kb.json'))
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.is_file() else {}
    root = os.environ.get('DST_KB_PATH') or config.get('kb_path')
    if not root:
        raise KBError('KB_UNAVAILABLE', 'Configure DST_KB_PATH or kb_path in DST_KB_CONFIG.')
    def resolve(value):
        p = Path(value).expanduser()
        return (p if p.is_absolute() else config_path.parent/p).resolve()
    root = resolve(root)
    cache = resolve(os.environ.get('DST_KB_INDEX') or config.get('index_path', str(Path.home()/'.cache/dst-kb/index.sqlite3')))
    if cache.is_relative_to(root):
        raise KBError('INVALID_CONFIG', 'Derived index must be outside canonical KB.')
    return root, cache, config_path.resolve()

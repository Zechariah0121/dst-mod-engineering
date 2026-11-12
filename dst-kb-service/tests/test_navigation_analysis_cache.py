"""Request-local lexical reuse keeps value isolation and live integrity guards."""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dst_kb import native_mechanism, retrieval_v2, validation
from dst_kb.config import KBError
from dst_kb.request_analysis import analysis_scope
from dst_kb.service import Service
from dst_kb.source_epoch_runtime import EpochContext


class NavigationAnalysisCacheTests(unittest.TestCase):
    def test_cached_values_equal_uncached_and_caller_mutation_is_isolated(self):
        functions = (retrieval_v2.topics, native_mechanism.navigation_topics,
                     native_mechanism.navigation_terms)
        for function in functions:
            for text in ('Timer:Restore', 'NotATimer', '监听解绑与库存恢复',
                         'OceanFishingRod:CatchFish rain lure', ''):
                with self.subTest(function=function.__name__, text=text):
                    expected = function.__wrapped__(text)
                    with analysis_scope():
                        first = function(text)
                        first.add('caller mutation')
                        self.assertEqual(function(text), expected)
                        self.assertEqual(function(text=text), expected)

    def test_lexical_work_is_reused_only_inside_one_request(self):
        with patch.object(retrieval_v2, 'contains', wraps=retrieval_v2.contains) as contains:
            with analysis_scope():
                expected = retrieval_v2.topics('Timer:Restore')
                first_calls = contains.call_count
                self.assertGreater(first_calls, 0)
                self.assertEqual(retrieval_v2.topics('Timer:Restore'), expected)
                self.assertEqual(contains.call_count, first_calls)
            with analysis_scope():
                self.assertEqual(retrieval_v2.topics('Timer:Restore'), expected)
                self.assertGreater(contains.call_count, first_calls)
            before = contains.call_count
            retrieval_v2.topics('Timer:Restore')
            self.assertGreater(contains.call_count, before)

    def test_exception_exit_clears_the_navigation_request_cache(self):
        with self.assertRaisesRegex(RuntimeError, 'request failed'):
            with analysis_scope() as failed:
                native_mechanism.navigation_terms('Timer:Restore')
                self.assertGreater(failed.info()['entries'], 0)
                raise RuntimeError('request failed')
        self.assertEqual(failed.info()['entries'], 0)
        with analysis_scope() as fresh:
            self.assertIsNot(fresh, failed)
            self.assertEqual(fresh.info()['entries'], 0)
            self.assertIn('timer', native_mechanism.navigation_terms('Timer:Restore'))

    def test_same_size_same_mtime_knowledge_drift_still_fails_in_request(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in validation.INPUTS + ['PACKAGE-MANIFEST.json']:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'{}')
            service = Service.__new__(Service)
            service.root = root
            service.epoch_context = None
            service.loaded_signature = validation.signature(root)
            changed = root / validation.INPUTS[0]
            stat = changed.stat()
            with analysis_scope():
                retrieval_v2.topics('Timer:Restore')
                service.ready()
                changed.write_bytes(b'[]')
                os.utime(changed, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                with self.assertRaises(KBError) as caught:
                    service.ready()
                self.assertEqual(caught.exception.code, 'INDEX_STALE')

    def test_same_size_same_mtime_environment_drift_still_fails_in_request(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'committed.json'
            path.write_bytes(b'{}')
            stat = path.stat()
            context = EpochContext('test', path.parent, path, path, path, path, path,
                                   'test', ((path, hashlib.sha256(b'{}').hexdigest()),), '{}')
            with analysis_scope():
                native_mechanism.navigation_topics('Timer:Restore')
                context.assert_current()
                path.write_bytes(b'[]')
                os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                with self.assertRaises(KBError) as caught:
                    context.assert_current()
                self.assertEqual(caught.exception.code, 'SOURCE_EPOCH_STALE')


if __name__ == '__main__':
    unittest.main()

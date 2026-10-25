"""Regression guards for the unified catalog; mutate documents only in memory."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import validate_v011 as validator


class UnifiedKnowledgeIntegrityTests(unittest.TestCase):
    def errors_for(self, relative, change, full=False):
        target = ROOT / relative
        original_read = validator.read
        document = copy.deepcopy(original_read(target))
        change(document)

        def substituted_read(path):
            return document if path == target else original_read(path)

        with patch.object(validator, 'read', substituted_read):
            if full:
                return validator.validate_root(ROOT)['errors']
            errors = []
            validator.validate_catalog_native(ROOT, errors)
            return errors

    def assert_detected(self, errors, message):
        self.assertTrue(any(message in error for error in errors), errors)

    def test_legacy_body_must_match_hash_baseline(self):
        errors = self.errors_for('data/entries.json',
            lambda doc: doc['entries'][0].update(summary='Synthetic altered summary.'), full=True)
        self.assert_detected(errors, 'legacy baseline record mismatch')

    def test_catalog_pointer_must_resolve_to_its_own_entry(self):
        errors = self.errors_for('CATALOG.json',
            lambda doc: doc['entries'][0].update(pointer='/entries/1'))
        self.assert_detected(errors, 'catalog pointer identity')

    def test_nativecore_hold_cannot_be_silently_promoted(self):
        errors = self.errors_for('data/nativecore/native-core.json',
            lambda doc: doc['entries'][0].update(coding_status='coding_default'))
        self.assert_detected(errors, 'NativeCore Coding HOLD changed')

    def test_native_evidence_pointer_must_resolve(self):
        errors = self.errors_for('data/nativecore/native-core.json',
            lambda doc: doc['entries'][0]['evidence_refs'][0].update(pointer='/missing-evidence-regression'))
        self.assert_detected(errors, 'native artifact ')


if __name__ == '__main__':
    unittest.main()

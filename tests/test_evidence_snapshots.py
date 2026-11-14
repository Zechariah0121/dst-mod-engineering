"""Independent evidence activation, using real hydrator and synthetic guards."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_public_source_bootstrap as bootstrap
prepare = bootstrap.prepare
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'dst-kb-service'))
from dst_kb import evidence_snapshot as snapshots
from dst_kb.config import KBError


class EvidenceSnapshotTests(unittest.TestCase):
    setUp = bootstrap.BootstrapTests.setUp
    build = bootstrap.BootstrapTests.build

    def setUp(self):
        bootstrap.BootstrapTests.setUp(self)
        prepare.write(self.root / 'knowledge/CATALOG.json', {'entries': [
            {'id': 'FIXTURE', 'file': 'evidence.json', 'pointer': '/citation'}]})

    def test_new_install_partial_has_dependency_and_no_runtime(self):
        result = self.build([self.current])
        self.assertEqual(result['status'], 'PARTIAL_EVIDENCE_PREPARED')
        assessment = snapshots.active_assessment(self.root)
        self.assertEqual(assessment['status'], 'PARTIAL')
        self.assertEqual(assessment['references'][0]['status'], 'CHANGED_UNKNOWN')
        self.assertEqual(assessment['affected_entry_ids'], ['FIXTURE'])
        self.assertFalse((self.root / 'cache/runtime/retrieval-config.json').exists())

    def test_partial_preserves_old_complete_runtime_and_comparison(self):
        self.build([self.current, self.historical])
        old = snapshots.active_assessment(self.root)
        config = self.root / 'cache/runtime/retrieval-config.json'
        before = config.read_bytes()
        self.build([self.current])
        new = snapshots.active_assessment(self.root)
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual(new['previous_comparison']['snapshot_id'], old['snapshot_id'])
        self.assertEqual(new['previous_comparison']['sources'], old['sources'])
        self.assertFalse(new['full_runtime_activated'])
        self.assertEqual(old['status'], 'COMPLETE')

    def test_failed_activation_preserves_old_snapshot_and_runtime(self):
        self.build([self.current, self.historical])
        active = self.root / 'cache/evidence/active.json'
        runtime = self.root / 'cache/runtime/retrieval-config.json'
        before, old_runtime = active.read_bytes(), runtime.read_bytes()
        replace = snapshots.os.replace
        def fail(source, target):
            if Path(target) == active:
                raise OSError('injected atomic replace failure')
            return replace(source, target)
        with patch.object(snapshots.os, 'replace', side_effect=fail):
            with self.assertRaises(OSError):
                self.build([self.current])
        self.assertEqual(active.read_bytes(), before)
        self.assertEqual(runtime.read_bytes(), old_runtime)
        self.assertEqual(snapshots.active_assessment(self.root)['status'], 'COMPLETE')

    def test_guard_failure_does_not_switch_evidence(self):
        self.build([self.current])
        active = self.root / 'cache/evidence/active.json'
        before = active.read_bytes()
        with self.assertRaises(prepare.PreparationError):
            self.build([self.current, self.historical], prepare.PreparationError('VALIDATION_FAILED', 'injected'))
        self.assertEqual(active.read_bytes(), before)

    def test_snapshot_and_package_tampering_fail_closed(self):
        self.build([self.current])
        active = self.root / 'cache/evidence/active.json'
        pointer = json.loads(active.read_bytes())
        file = self.root / 'cache/evidence/snapshots' / (pointer['snapshot_id'] + '.json')
        raw = file.read_bytes()
        file.write_bytes(raw + b' ')
        with self.assertRaises(KBError):
            snapshots.active_assessment(self.root)
        file.write_bytes(raw)
        (self.root / 'knowledge/evidence.json').write_text('{}')
        with self.assertRaises(KBError) as error:
            snapshots.active_assessment(self.root)
        self.assertEqual(error.exception.code, 'EVIDENCE_PACKAGE_CHANGED')
        active.write_text('{"snapshot_id":"../../bad"}')
        with self.assertRaises(KBError):
            snapshots.active_assessment(self.root)

    def test_missing_file_and_no_coordinates_are_distinct(self):
        self.current.unlink()
        self.current.mkdir()
        self.build([self.current])
        self.assertEqual(snapshots.active_assessment(self.root)['references'][0]['status'], 'MISSING')

    def test_native_ai_locator_only_evidence_is_checked(self):
        raw = (self.historical / 'a.lua').read_bytes()
        prepare.write(self.root / 'knowledge/data/native001/canonical-native001-research-map.json',
            {'entries': [{'canonical_id': 'AI-FIXTURE', 'source_locators': [
                {'evidence_locators': [{'file': 'a.lua', 'file_sha256': prepare.sha(raw)}]}]}]})
        self.build([self.historical])
        refs = snapshots.active_assessment(self.root)['references']
        ai = next(r for r in refs if r['kind'] == 'native_ai_file_locator')
        self.assertEqual(ai['status'], 'EXACT_FILE')
        self.assertFalse(ai['range_verified'])
        self.build([self.current])
        self.assertIn('AI-FIXTURE', snapshots.active_assessment(self.root)['affected_entry_ids'])

    def test_failed_full_runtime_replace_rolls_back_evidence_pointer(self):
        self.build([self.current])
        active = self.root / 'cache/evidence/active.json'
        before = active.read_bytes()
        runtime = self.root / 'cache/runtime/retrieval-config.json'
        replace = prepare.os.replace
        def fail(source, target):
            if Path(target) == runtime:
                raise OSError('injected runtime replace failure')
            return replace(source, target)
        with patch.object(prepare.os, 'replace', side_effect=fail):
            with self.assertRaises(OSError):
                self.build([self.current, self.historical])
        self.assertEqual(active.read_bytes(), before)
        self.assertFalse(runtime.exists())

    def test_real_catalog_core_without_payload_slot_is_explicitly_unassessed(self):
        root = Path(__file__).resolve().parents[1]
        recipe = prepare.read(root / 'source-payload-recipe.json')
        assessment = snapshots.build(root, recipe, {'matches': []}, {}, [], '0' * 64)
        references = assessment['references']
        core = [r for r in references if 'NC-N002-FINAL-01' in r['affected_entry_ids']]
        self.assertTrue(core)
        self.assertTrue(any(r['kind'] == 'unassessed_registered_entry' and r['status'] == 'UNKNOWN' for r in core))
        catalog = prepare.read(root / 'knowledge/CATALOG.json')['entries']
        self.assertEqual({row['id'] for row in catalog},
                         {entry_id for ref in references for entry_id in ref['affected_entry_ids']})


if __name__ == '__main__':
    unittest.main()

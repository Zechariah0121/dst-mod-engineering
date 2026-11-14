"""Offline author maintenance boundaries; no source hydration or game runtime."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('maintenance_support', Path(__file__).resolve().parents[1] / 'scripts/maintenance_support.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AuthorMaintenanceTests(unittest.TestCase):
    def rows(self, statement='old', title='title'):
        return {'X': {'record': {'id': 'X', 'title': title,
                'claims': [{'statement': statement}, {'statement': 'unchanged'}]}, 'family': 'native_core'}}

    def contract(self):
        return {'records': {'X': {'contracts': {'Owner:Fn': {
            'record_pointers': ['/claims/0', '/claims/1'],
            'pointer_roles': {'/claims/0': {'role': 'METHOD_SUBJECT'}}}}}}}

    def test_title_does_not_invalidate_technical_atoms(self):
        row = m.pending_review(self.rows(), self.rows(title='corrected'), self.contract(), {})[0]
        self.assertEqual(row['change_class'], 'TITLE_ONLY')
        self.assertEqual(row['dependencies'], [])
        self.assertNotEqual(row['old_record_sha256'], row['new_record_sha256'])

    def test_statement_requires_specific_atom_and_mapping_review(self):
        row = m.pending_review(self.rows(), self.rows(statement='new meaning'), self.contract(), {})[0]
        self.assertEqual(row['changed_pointers'], ['/claims/0/statement'])
        self.assertEqual([d['atom'] for d in row['dependencies']], ['/claims/0'])
        self.assertEqual(row['dependencies'][0]['symbol'], 'Owner:Fn')
        self.assertFalse(row['technical_semantics_approved'])

    def test_scope_change_invalidates_all_method_bindings(self):
        old, new = self.rows(), self.rows()
        old['X']['record']['scope'] = {'version': 'old'}
        new['X']['record']['scope'] = {'version': 'new'}
        row = m.pending_review(old, new, self.contract(), {})[0]
        self.assertEqual(len(row['dependencies']), 2)

    def test_identity_dependency_names_exact_existing_row(self):
        before = self.rows()
        identity = {'bindings': [{'record_sha256': m.digest(before['X']['record']),
                     'record_pointer': '/claims/0', 'declared_symbol': 'Owner:Fn'}]}
        row = m.pending_review(before, self.rows(statement='new'), {}, identity)[0]
        self.assertEqual(row['dependencies'][0]['pointer'], '/bindings/0')

    def test_json_pointer_escaping(self):
        self.assertEqual(m.differences({'a/b': {'~': 1}}, {'a/b': {'~': 2}}), ['/a~1b/~0'])

    def test_output_cannot_overwrite_author_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaisesRegex(ValueError, 'Output must be absent'):
                m.rebuild(path, path, path, path / 'derived')

    def test_author_path_cannot_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'escaped'):
                m.child(Path(directory), '../external.json')

    def test_registered_membership_and_order_cannot_silently_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            m.write(root / 'records.json', {'entries': [{'id': 'B'}, {'id': 'A'}]})
            registry = {'families': [{'name': 'native_ai', 'documents': [
                {'file': 'records.json', 'entry_ids': ['A', 'B']}]}]}
            with self.assertRaisesRegex(ValueError, 'membership/order changed'):
                m.records(root, registry)

    def test_technical_change_cannot_create_readable_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / 'candidate'
            with self.assertRaisesRegex(ValueError, 'only Core TITLE_ONLY'):
                m.stage_title_candidate(root / 'package', root / 'knowledge', root / 'output',
                    destination, self.rows(), self.rows(statement='new'),
                    [{'id': 'X', 'change_class': 'TECHNICAL_REVIEW_REQUIRED'}])
            self.assertFalse(destination.exists())

    def test_reviewed_technical_change_allows_only_one_nsf_statement_and_gate_a(self):
        before = self.rows()
        before['X'].update(family='native_core', file=m.CORE)
        record = before['X']['record']
        record.update(scope={'runtime_verified': False}, gate_a={'accepted': True, 'original_fact_statement_preserved': True})
        record['claims'][0].update(kind='NSF', evidence_refs=[])
        after = m.copy.deepcopy(before)
        revised = after['X']['record']
        revised['claims'][0]['statement'] = 'new meaning'
        revised['gate_a']['original_fact_statement_preserved'] = False
        decision = {'schema': 'dst-author-technical-stage-review/1', 'decision': 'APPROVE_ISOLATED_CANDIDATE',
            'reviewer': 'reviewer', 'rationale': 'source range read', 'record_id': 'X',
            'claim_pointer': '/claims/0', 'old_record_sha256': m.digest(record),
            'new_record_sha256': m.digest(revised),
            'gate_a_original_fact_statement_preserved': {'before': True, 'after': False},
            'source': {}, 'maps': {}}
        pending = m.pending_review(before, after, {}, {})
        self.assertEqual(m.validate_technical_change(before, after, pending, decision), ('X', '/claims/0'))
        revised['scope']['runtime_verified'] = 0
        with self.assertRaisesRegex(ValueError, 'fingerprints'):
            m.validate_technical_change(before, after, m.pending_review(before, after, {}, {}), decision)
        decision['new_record_sha256'] = m.digest(revised)
        with self.assertRaisesRegex(ValueError, 'Only the reviewed NSF statement'):
            m.validate_technical_change(before, after, m.pending_review(before, after, {}, {}), decision)

    def test_reviewed_technical_source_binds_existing_citation_and_actual_archive(self):
        import hashlib
        import zipfile
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'scripts.zip'
            member = 'scripts/example.lua'
            text = 'function owner:Example() end'
            with zipfile.ZipFile(archive, 'w') as source_zip:
                source_zip.writestr(member, text + '\n')
            locator = {'path': member, 'line_start': 1, 'line_end': 1, 'file_sha256': 'old',
                       'range_sha256': hashlib.sha256(text.encode()).hexdigest()}
            evidence = m.json.dumps({'source': locator}).encode()
            reference = {'artifact_path': 'evidence.json', 'pointer': '/source',
                         'sha256': hashlib.sha256(evidence).hexdigest()}
            archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
            inputs = {'knowledge/evidence.json': evidence, 'source-epochs.json':
                m.json.dumps({'source_input_targets': [{'archive_sha256': archive_sha}], 'epochs': {}}).encode()}
            source = {'reference': reference, 'range': locator, 'archive_sha256': archive_sha}
            self.assertEqual(m.verify_review_source(inputs, source, archive, {'evidence_refs': [reference]})[0], text)
            with self.assertRaisesRegex(ValueError, 'claim-owned'):
                m.verify_review_source(inputs, source, archive, {'evidence_refs': []})
            archive.write_bytes(b'different archive')
            with self.assertRaisesRegex(ValueError, 'actual ZIP'):
                m.verify_review_source(inputs, source, archive, {'evidence_refs': [reference]})

    def test_reviewed_identity_repair_refuses_an_expanded_row_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            claim = {'kind': 'UNK', 'statement': 'withheld', 'evidence_refs': [
                {'artifact_path': 'research/publication/public-evidence-boundaries.json', 'pointer': '/private_context'}]}
            record = {'id': 'NC-N003-INT-05', 'claims': [{}] * 16 + [claim]}
            m.write(root / 'knowledge/data/nativecore/native-core.json', {'entries': [record]})
            row = {'record_sha256': m.digest(record), 'record_pointer': '/claims/16',
                   'claim_kind': 'EI', 'declared_symbol': 'StateGraphInstance:GoToState',
                   'statement_sha256': 'old', 'reference': {'artifact_path': 'old'}}
            for name in ('dst-kb-service/dst_kb/source_identity_map.json', 'epoch-assets/759671/source_identity_map.json'):
                m.write(root / name, {'bindings': [row] * 6})
            m.write(root / 'source-epochs.json', {'epochs': {}})
            before = (root / 'dst-kb-service/dst_kb/source_identity_map.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'reviewed five-row scope'):
                m.repair_retired_private_identities(root, root / 'audit')
            self.assertEqual(before, (root / 'dst-kb-service/dst_kb/source_identity_map.json').read_bytes())

    def test_source_slot_pointer_must_still_select_identical_value(self):
        recipe = {'slots': [{'path': 'identity.json', 'pointer': '/bindings/0/header'}]}
        original = {'identity.json': '{"bindings":[{"header":{"slot":"A"}}]}'}
        updated = {'identity.json': '{"bindings":[{"header":{"slot":"B"}}]}'}
        self.assertEqual(m.verify_source_slots(recipe, original, original, ['identity.json']), 1)
        with self.assertRaisesRegex(ValueError, 'change a source payload slot'):
            m.verify_source_slots(recipe, original, updated, ['identity.json'])


if __name__ == '__main__':
    unittest.main()

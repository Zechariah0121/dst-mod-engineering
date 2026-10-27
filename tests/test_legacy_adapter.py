"""Real family shapes, authored synthetic source bytes, all writes lane-local."""
import contextlib
import copy
import io
import json
import gzip
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("DST_LEGACY_TEST_REPOSITORY", HERE.parent))
sys.path.insert(0, str(REPO / "scripts"))
import legacy_adapter as adapter
HELPER_PATH = REPO / "scripts/source_compatibility.py"
helper, _ = adapter.load_helper(HELPER_PATH)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


class LegacyAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".test-", dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.knowledge = self.root / "knowledge"
        self.knowledge.mkdir()
        self.files = {"scripts/producer.lua": b"function Producer(x)\n    return x + 1\nend\n",
                      "scripts/consumer.lua": b"function Consumer(x)\n    return Producer(x)\nend\n"}
        self.old = self.archive("old.zip", self.files)
        self.target = self.old
        self.artifact_name = "research/fact.json"
        self.fact = {"source_scope": {"snapshot_id": "KLEI-SYNTHETIC", "runtime_verified": False},
                     "facts": [{"statement": "Authored synthetic fixture only", "citations": [self.citation()]}]}
        self.artifact_hash = self.put(self.artifact_name, self.fact)
        raw = read(REPO / "knowledge/data/nativecore/native-core.json")["entries"][0]
        self.record = copy.deepcopy(raw)
        self.record["scope"] = {"statement": "Synthetic scoped unit", "exclusions": ["No game behavior"]}
        self.record["claims"] = [{"kind": "NSF", "statement": "Authored fixture",
                                  "evidence_refs": [self.ref()]}]
        self.record["evidence_refs"] = [self.ref()]
        self.family = "native_core"
        self.record_file = "data/nativecore/native-core.json"

    def put(self, name, value):
        path = self.knowledge / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return adapter.sha(path.read_bytes())

    def archive(self, name, files):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            for member, raw in files.items():
                archive.writestr(member, raw)
        value = helper.Archive(path, "unregistered-future-target")
        self.addCleanup(value.close)
        return value

    def citation(self, name="scripts/producer.lua"):
        raw = self.files[name]
        return {"path": name, "file_sha256": adapter.sha(raw), "range_sha256": adapter.sha(raw.rstrip(b"\n")),
                "line_start": 1, "line_end": 3, "symbol": 'Producer("descriptive hint")',
                "source_kind": "vanilla_source_snapshot"}

    def ref(self, pointer="/facts/0", name=None, fingerprint=None):
        return {"artifact_path": name or self.artifact_name, "sha256": fingerprint or self.artifact_hash, "pointer": pointer}

    def refresh_fact(self):
        self.artifact_hash = self.put(self.artifact_name, self.fact)
        self.record["claims"][0]["evidence_refs"] = [self.ref()]
        self.record["evidence_refs"] = [self.ref()]

    def run_adapter(self, baselines=()):
        self.put(self.record_file, {"entries": [self.record]})
        self.put("CATALOG.json", {"entries": [{"id": self.record["id"], "family": self.family,
                    "file": self.record_file, "pointer": "/entries/0", "coding_status": self.record.get("coding_status", "hold")} ]})
        result = adapter.Adapter(self.knowledge, helper, self.target, baselines).run()
        return result, list(result["atoms"].values())[0], list(result["source_references"].values())

    def test_core_real_claim_shape_exact_pins_and_original_scope(self):
        result, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertEqual(atom["atom_binding_status"], "fully_exact")
        record = result["records"][0]
        self.assertEqual(record["original_record_sha256"], adapter.digest(self.record))
        self.assertEqual(record["original_states"]["coding_status"], "hold")
        self.assertTrue(result["scope_sets"][atom["scope_set"]]["fragment_nodes"])
        self.assertFalse(result["scope_sets"][atom["scope_set"]]["semantic_scope_exhaustiveness_verified"])
        self.assertIn(record["record_node"], result["nodes"])
        self.assertIn(atom["atom_node"], result["nodes"])
        self.assertFalse(refs[0]["current_evidence_admitted"])

    def test_bad_claim_citation_cannot_borrow_good_entry_evidence(self):
        self.record["claims"][0]["evidence_refs"] = [self.ref(fingerprint="f" * 64)]
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertEqual(refs, [])
        self.assertIn("invalid_claim_evidence_reference", [i["code"] for i in atom["issues"]])

    def test_good_atom_ref_does_not_mask_bad_explicit_claim_leaf(self):
        self.record["claims"][0]["evidence_refs"].append(self.ref("/facts/0/citations/0", fingerprint="a" * 64))
        _, atom, refs = self.run_adapter()
        self.assertTrue(refs)
        self.assertEqual(atom["source_status"], "unknown")

    def test_wrong_range_hash_never_repaired_from_target(self):
        self.fact["facts"][0]["citations"][0]["range_sha256"] = "f" * 64
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertFalse(refs[0]["source_identity_checked"])
        self.assertIn("original_range_hash_mismatch_no_identity_repair", refs[0]["source_comparison"]["reasons"])

    def test_public_slot_is_not_restored_by_equal_target(self):
        self.fact["facts"][0]["citations"][0]["source_excerpt"] = {"$dst_source_payload_slot": "fixture"}
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(refs[0]["source_comparison"]["status"], "same")
        self.assertEqual(refs[0]["binding_class"], "unrestored_payload")
        self.assertEqual(atom["source_status"], "unknown")

    def test_embedded_synthetic_restored_payload_integrity_checked(self):
        self.fact["facts"][0]["citations"][0]["source_excerpt"] = self.files["scripts/producer.lua"].decode().rstrip("\n")
        self.refresh_fact()
        result, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertEqual(refs[0]["payload_status"], "embedded_range_hash_verified")
        self.assertNotIn("return x + 1", json.dumps(result))

    def test_payload_hash_mismatch_never_admitted(self):
        self.fact["facts"][0]["citations"][0]["source_excerpt"] = "unrelated source"
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertEqual(refs[0]["binding_class"], "unknown")

    def test_consumer_change_marks_own_atom_for_local_review(self):
        self.fact["facts"][0]["citations"].append(self.citation("scripts/consumer.lua"))
        self.refresh_fact()
        changed = dict(self.files)
        changed["scripts/consumer.lua"] = changed["scripts/consumer.lua"].replace(b"Producer(x)", b"Producer(x) * 3")
        self.target = self.archive("consumer-new.zip", changed)
        result, atom, _ = self.run_adapter([self.old])
        self.assertEqual(atom["source_status"], "changed")
        self.assertEqual(result["local_review_checklist"][0]["atom_id"], atom["id"])
        self.assertEqual(atom["dependency_status"], "unknown")

    def test_range_shift_preserves_original_tuple(self):
        changed = dict(self.files)
        changed["scripts/producer.lua"] = b"-- move\n" + changed["scripts/producer.lua"]
        self.target = self.archive("shift.zip", changed)
        _, atom, refs = self.run_adapter([self.old])
        self.assertEqual(atom["source_status"], "changed")
        self.assertEqual(refs[0]["source_comparison"]["detail_status"], "relocation_required")
        self.assertEqual(refs[0]["original_evidence_tuple"]["line_start"], 1)
        self.assertEqual(refs[0]["source_comparison"]["target_locator"]["line_start"], 2)

    def test_no_old_baseline_changed_file_is_unknown(self):
        changed = dict(self.files)
        changed["scripts/producer.lua"] += b"-- change\n"
        self.target = self.archive("no-old.zip", changed)
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertEqual(refs[0]["source_comparison"]["reasons"], ["missing_matching_old_source"])

    def test_deleted_path_reports_missing(self):
        self.target = self.archive("deleted.zip", {"scripts/consumer.lua": self.files["scripts/consumer.lua"]})
        _, atom, refs = self.run_adapter([self.old])
        self.assertEqual(refs[0]["source_comparison"]["status"], "missing")
        self.assertEqual(atom["source_status"], "missing")

    def test_historical_parent_context_propagates_across_typed_artifact(self):
        other = "research/other.json"
        checksum = self.put(other, self.fact)
        self.fact = {"source_scope": {"snapshot_id": "KLEI-SYNTHETIC"}, "facts": [{"payload_status": "metadata_only",
                "linked_evidence": [self.ref(name=other, fingerprint=checksum)]}]}
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(refs[0]["binding_class"], "historical")
        self.assertEqual(atom["source_status"], "unknown")

    def test_direct_typed_leaf_cannot_bypass_historical_ancestors(self):
        parent = self.fact["facts"][0]
        for flag, value in (("payload_status", "metadata_only"), ("evidence_role", "historical_comparison"),
                            ("supports_current_behavior", False)):
            with self.subTest(flag=flag):
                for key in ("payload_status", "evidence_role", "supports_current_behavior"):
                    parent.pop(key, None)
                parent[flag] = value
                self.refresh_fact()
                self.record["claims"][0]["evidence_refs"] = [self.ref("/facts/0/citations/0")]
                _, atom, refs = self.run_adapter()
                self.assertEqual(refs[0]["binding_class"], "historical")
                self.assertEqual(refs[0]["source_comparison"]["status"], "unknown")
                self.assertEqual(atom["source_status"], "unknown")

    def test_nearer_mod_provenance_overrides_generic_vanilla_ancestor(self):
        self.fact["facts"][0]["repository"] = "someone/third-party-mod"
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(refs[0]["binding_class"], "non_vanilla")
        self.assertEqual(atom["source_status"], "unknown")

    def test_lookalike_repository_names_never_grant_native_provenance(self):
        for repo in ("someone/dst-scripts-mod", "someone/klei-mirror", "someone/dst-scripts",
                     "https://github.com/someone/dst-scripts-mod"):
            with self.subTest(repository=repo):
                self.fact["facts"][0]["repository"] = repo
                self.refresh_fact()
                self.record["claims"][0]["evidence_refs"] = [self.ref("/facts/0/citations/0")]
                _, atom, refs = self.run_adapter()
                self.assertEqual(refs[0]["provenance"], "non_vanilla")
                self.assertEqual(refs[0]["binding_class"], "non_vanilla")
                self.assertEqual(atom["source_status"], "unknown")

    def test_legacy_registry_cannot_override_local_mod_locator(self):
        self.record = {"id": "LEGACY-SYNTHETIC", "entry_type": "legacy_entry_unit", "coding_status": "hold",
            "scope": {"statement": "Synthetic only"}, "sources": [{"source_id": "KLEI-FIXTURE", "role": "direct_evidence",
            "locator_structured": [{"type": "source_lines", "file": "producer.lua", "start_line": 1, "end_line": 3,
                "source_kind": "mod_source", "range_sha256": adapter.sha(self.files["scripts/producer.lua"].rstrip(b"\n"))}]}]}
        self.family, self.record_file = "legacy", "data/entries.json"
        self.put("data/sources.json", {"sources": [{"id": "KLEI-FIXTURE", "source_type": "vanilla_source_snapshot",
            "verification": {"file_fingerprints": [{"path": "logical:vanilla-snapshot/scripts/producer.lua",
                "sha256": adapter.sha(self.files["scripts/producer.lua"])}]}}]})
        _, atom, refs = self.run_adapter()
        self.assertEqual(refs[0]["provenance"], "non_vanilla")
        self.assertEqual(refs[0]["binding_class"], "non_vanilla")
        self.assertEqual(refs[0]["source_comparison"]["status"], "unknown")
        self.assertEqual(atom["source_status"], "unknown")

    def test_invalid_scope_reference_blocks_same_claim(self):
        self.record["scope"]["scope_refs"] = [self.ref("/source_scope", fingerprint="f" * 64)]
        _, atom, _ = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertIn("invalid_original_scope_reference", [i["code"] for i in atom["issues"]])

    def test_real_runtime_history_text_anchor_is_context_not_source_promotion(self):
        name = "history/narrow-runtime.md"
        path = self.knowledge / name
        path.parent.mkdir(parents=True)
        path.write_text("# Historical only\nNarrow observation, no new runtime\n", encoding="utf-8")
        self.record["scope"]["runtime_evidence_records"] = [{"artifact_path": name,
            "artifact_sha256": adapter.sha(path.read_bytes()), "source_pointer": "#L2",
            "scope": "only one past observed run", "new_runtime_execution": False}]
        result, atom, _ = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertTrue(atom["resolved_scope_reference_nodes"])
        self.assertEqual(result["documents"][name]["content_type"], "utf8_text")
        self.assertFalse(result["boundaries"]["runtime_verified"])

    def test_deterministic_gzip_keeps_full_normalized_tables(self):
        result, _, _ = self.run_adapter()
        one, two = self.root / "one.gz", self.root / "two.gz"
        adapter.write_sidecar(one, result)
        adapter.write_sidecar(two, result)
        self.assertEqual(one.read_bytes(), two.read_bytes())
        self.assertEqual(json.loads(gzip.decompress(one.read_bytes())), result)

    def test_local_id_resolves_only_explicit_citation_registry(self):
        self.fact["citations"] = {"C1": self.citation()}
        self.fact["facts"][0] = {"statement_zh": "Synthetic", "citation_ids": ["C1"]}
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertEqual(len(refs), 1)

    def test_original_final_newline_hash_is_preserved(self):
        original_hash = adapter.sha(self.files["scripts/producer.lua"])
        self.fact["facts"][0]["citations"][0]["range_sha256"] = original_hash
        self.refresh_fact()
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertEqual(refs[0]["original_evidence_tuple"]["range_sha256"], original_hash)
        self.assertIn("LF_join_with_final_LF", refs[0]["source_comparison"]["original_range_hash_modes_verified"])

    def test_legacy_real_shape_missing_range_commitment_stays_unknown(self):
        self.record = copy.deepcopy(read(REPO / "knowledge/data/entries.json")["entries"][0])
        self.family, self.record_file = "legacy", "data/entries.json"
        self.record["sources"] = [{"source_id": "KLEI-FIXTURE", "role": "direct_evidence",
            "locator_structured": [{"type": "source_lines", "file": "producer.lua", "start_line": 1, "end_line": 3}]}]
        self.put("data/sources.json", {"sources": [{"id": "KLEI-FIXTURE", "source_type": "vanilla_source_snapshot",
            "verification": {"file_fingerprints": [{"path": "logical:vanilla-snapshot/scripts/producer.lua",
                                                   "sha256": adapter.sha(self.files["scripts/producer.lua"])}]}}]})
        _, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "unknown")
        self.assertIn("missing_range_byte_commitment_not_synthesized_from_current_lines", refs[0]["source_comparison"]["reasons"])
        self.assertIn("file_commitment_joined_from_registry_node", refs[0])

    def test_native_ai_real_research_map_shape_resolves_original_candidate(self):
        self.record = copy.deepcopy(read(REPO / "knowledge/data/native001/canonical-native001-ai-knowledge.json")["entries"][0])
        self.family, self.record_file = "native_ai", "data/native001/canonical-native001-ai-knowledge.json"
        self.record["scope"] = {"snapshot_id": "KLEI-SYNTHETIC", "exclusions": ["Synthetic only"]}
        candidate_name = "research/candidate.json"
        candidate = {"candidate_id": "NC-FIXTURE", "classification": "NSF", "statement": "Synthetic candidate",
                     "scope": {"snapshot_id": "KLEI-SYNTHETIC"}, "evidence": [self.citation()]}
        checksum = self.put(candidate_name, {"candidates": [candidate]})
        mapping = {"entries": [{"canonical_id": self.record["id"], "direct_native_fact_support": ["NC-FIXTURE"],
             "source_locators": [{"candidate_id": "NC-FIXTURE", "artifact_path": candidate_name,
                                  "artifact_sha256": checksum, "source_pointer": "/candidates/0"}]}]}
        self.put("data/native001/canonical-native001-research-map.json", mapping)
        result, atom, refs = self.run_adapter()
        self.assertEqual(atom["source_status"], "same")
        self.assertTrue(atom["support_atom_ids"])
        self.assertEqual(result["atoms"][atom["support_atom_ids"][0]]["relation"], "AI_direct_native_fact_support")
        rec_atoms = [u for u in result["atoms"].values() if u["kind"] in ("REC", "REC / EI")]
        self.assertTrue(rec_atoms)
        self.assertTrue(all(u["source_status"] == "unknown" for u in rec_atoms))

    def test_cli_refuses_existing_output_without_modifying_record(self):
        self.run_adapter()
        output = self.root / "report.json"
        output.write_text("preserve", encoding="utf-8")
        record_path = self.knowledge / self.record_file
        old = record_path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            code = adapter.main(["--knowledge-root", str(self.knowledge), "--compatibility-helper", str(HELPER_PATH),
                                 "--target", str(self.old.path), "--output", str(output)])
        self.assertEqual(code, 2)
        self.assertEqual(output.read_text(), "preserve")
        self.assertEqual(record_path.read_bytes(), old)

    def test_unified_entry_uses_packaged_helper_without_runtime_or_cwd_dependency(self):
        self.run_adapter()
        output = self.root / 'unified.json.gz'
        command = [sys.executable, '-B', '-X', 'utf8', str(REPO / 'run_kb.py'),
                   'maintain-sources', 'legacy-assess', '--knowledge-root', str(self.knowledge),
                   '--target', str(self.old.path), '--target-label', 'unregistered-future-target',
                   '--output', str(output)]
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True,
                                encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        sidecar = json.loads(gzip.decompress(output.read_bytes()))
        self.assertEqual(sidecar['summary']['records'], 1)
        self.assertEqual(sidecar['comparison_helper']['sha256'], adapter.sha(HELPER_PATH.read_bytes()))
        self.assertTrue(all(atom['source_status'] == 'same' for atom in sidecar['atoms'].values()))
        before = output.read_bytes()
        again = subprocess.run(command, cwd=self.root, capture_output=True, text=True,
                               encoding='utf-8', timeout=30)
        self.assertEqual(again.returncode, 2)
        self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)

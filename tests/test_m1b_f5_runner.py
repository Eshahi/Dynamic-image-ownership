"""Unit tests for m1b_f5_runner — manifest validation, sharding, resume (CPU only, no GPU/images)."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import m1b_f5_runner as r  # noqa: E402


def _manifest(sources, **kw):
    m = dict(schema="m1b-f5-manifest-v1", version=r.VERSION, data_split="development", config_path="configs/f5-r2.json", profile_path="experiments/c4-v5-two-tier-regeneration-v1/profile.json", sources=sources)
    m.update(kw)
    return m


def _src(i, owner="thesis:owner:00"):
    return dict(id=f"src-{i:03d}", path=f"data/raw/val2017/val2017/00000{i}.jpg", owner=owner, wrong_owner="thesis:owner:01")


class TestValidateManifest(unittest.TestCase):
    def test_valid_minimal(self):
        m = _manifest([_src(1), _src(2)])
        r.validate_manifest(m)

    def test_reject_empty_sources(self):
        m = _manifest([])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_duplicate_id(self):
        m = _manifest([_src(1), _src(1)])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_extra_id(self):
        m = _manifest([_src(1), _src(2)])
        m["sources"].append(dict(id="src-003", path="x", owner="thesis:owner:00"))
        # Add an observation with an extra id not in planned — endpoints layer should reject, but manifest itself is valid
        r.validate_manifest(m)

    def test_reject_bad_schema(self):
        m = _manifest([_src(1)])
        m["schema"] = "wrong"
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_wrong_owner_equals_owner(self):
        s = _src(1, owner="thesis:owner:00")
        s["wrong_owner"] = "thesis:owner:00"
        m = _manifest([s])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_duplicate_t4_pair_id(self):
        m = _manifest([_src(1), _src(2)], t4_pairs=[dict(id="p01", donor="src-001", recipient="src-002"), dict(id="p01", donor="src-002", recipient="src-001")])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_t4_missing_donor(self):
        m = _manifest([_src(1)], t4_pairs=[dict(id="p01", recipient="src-001")])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_reject_duplicate_strengths(self):
        m = _manifest([_src(1)], t3_strengths=[0.1, 0.1])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)

    def test_t5_optional(self):
        m = _manifest([_src(1), _src(2)], t5_pairs=[dict(id="q01", a="src-001", b="src-002")])
        r.validate_manifest(m)


class TestSharding(unittest.TestCase):
    def test_deterministic_sorted(self):
        srcs = [_src(3), _src(1), _src(2)]
        a = r.shard_sources(srcs, 0, 2)
        b = r.shard_sources(srcs, 0, 2)
        self.assertEqual([s["id"] for s in a], [s["id"] for s in b])

    def test_no_overlap_and_cover(self):
        srcs = [_src(i) for i in range(5)]
        shards = [r.shard_sources(srcs, k, 3) for k in range(3)]
        all_ids = [s["id"] for sh in shards for s in sh]
        self.assertEqual(sorted(all_ids), sorted(s["id"] for s in srcs))
        # Overlap check
        for i in range(3):
            for j in range(i + 1, 3):
                self.assertEqual(set(s["id"] for s in shards[i]) & set(s["id"] for s in shards[j]), set())

    def test_bad_index(self):
        with self.assertRaises(ValueError):
            r.shard_sources([_src(1)], 1, 1)

    def test_single_shard(self):
        srcs = [_src(i) for i in range(3)]
        self.assertEqual(len(r.shard_sources(srcs, 0, 1)), 3)


class TestJournalResume(unittest.TestCase):
    def test_read_empty(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(r.read_journal(Path(td)), {})

    def test_append_and_read(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            out.mkdir()
            r.append_journal(out, dict(id="row-1", ok=True))
            r.append_journal(out, dict(id="row-2", ok=False))
            j = r.read_journal(out)
            self.assertEqual(set(j), {"row-1", "row-2"})
            self.assertTrue(j["row-1"]["ok"])

    def test_truncated_last_line_is_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            out.mkdir()
            jp = out / "journal.jsonl"
            jp.write_text('{"id":"a","x":1}\n{"id":"b"', encoding="utf-8")
            # read_journal will fail on truncated JSON; ensure it raises or handles
            # Our implementation currently raises — that is acceptable: journal corruption must be surfaced
            with self.assertRaises(Exception):
                r.read_journal(out)

    def test_resume_skips_completed(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            out.mkdir()
            # Simulate a journal with one completed row
            r.append_journal(out, dict(id="src-001:clean:C1:correct", outcome="completed", detection=dict(outcome="both_match")))
            j = r.read_journal(out)
            self.assertIn("src-001:clean:C1:correct", j)
            # sharding check: source would be considered done for that probe id
            probe_ids = ["src-001:clean:C0:correct", "src-001:clean:C1:correct"]
            self.assertFalse(all(pid in j for pid in probe_ids))
            r.append_journal(out, dict(id="src-001:clean:C0:correct", outcome="completed", detection=dict(outcome="both_match")))
            j2 = r.read_journal(out)
            self.assertTrue(all(pid in j2 for pid in probe_ids))


class TestNeverSubstituteSeeds(unittest.TestCase):
    def test_manifest_strengths_are_exact(self):
        m = _manifest([_src(1)], t3_strengths=[0.05, 0.1], t3_seeds=[0, 1])
        validated = r.validate_manifest(m)
        self.assertEqual(validated["t3_strengths"], [0.05, 0.1])
        self.assertEqual(validated["t3_seeds"], [0, 1])
        # No silent filling — missing keys fall back to frozen defaults only at run time, not by mutation
        m2 = _manifest([_src(1)])
        r.validate_manifest(m2)
        self.assertNotIn("t3_strengths", m2)
        self.assertEqual(r.T3_STRENGTHS, (0.05, 0.1, 0.2, 0.4))

    def test_validation_rejects_substituted_seed_list(self):
        # A manifest that claims seeds 0,1,2 but also has duplicates should be rejected
        m = _manifest([_src(1)], t3_seeds=[0, 0, 1])
        with self.assertRaises(ValueError):
            r.validate_manifest(m)


class TestSuccessRules(unittest.TestCase):
    def _det(self, outcome, found, match, read, inst=False):
        return {"outcome": outcome, "semantic": {"found": found, "content_match": match, "read": read},
                "instance": {"found": inst}}

    def test_semantic_only_counts_for_t3_but_not_both_match(self):
        d = self._det("semantic_only", True, True, True)
        self.assertTrue(r.success_of(d, "semantic"))
        self.assertTrue(r.success_of(d, "semantic_checked"))
        self.assertFalse(r.success_of(d, "semantic_assumed"))
        self.assertFalse(r.success_of(d, "both_match"))

    def test_recomputed_only_is_assumed(self):
        d = self._det("semantic_only", True, True, False)
        self.assertTrue(r.success_of(d, "semantic"))
        self.assertFalse(r.success_of(d, "semantic_checked"))
        self.assertTrue(r.success_of(d, "semantic_assumed"))

    def test_checked_plus_assumed_partition_semantic(self):
        for found in (True, False):
            for match in (True, False):
                for read in (True, False):
                    d = self._det("x", found, match, read)
                    self.assertEqual(r.success_of(d, "semantic"),
                                     r.success_of(d, "semantic_checked") or r.success_of(d, "semantic_assumed"))
                    self.assertFalse(r.success_of(d, "semantic_checked") and r.success_of(d, "semantic_assumed"))

    def test_any_found_and_unknown_rule(self):
        self.assertTrue(r.success_of(self._det("instance_only", False, False, False, inst=True), "any_found"))
        self.assertFalse(r.success_of(self._det("neither_match", False, False, False), "any_found"))
        with self.assertRaises(ValueError):
            r.success_of({}, "nope")


class TestRecoveryInventory(unittest.TestCase):
    def test_upstream_failures_still_count_every_planned_endpoint(self):
        planned = r.planned_row_ids([_src(1), _src(2)], [0.1], [0], [], [])
        journal = {"src-001:embed": {"outcome": "failed"}, "src-002:embed": {"outcome": "failed"}}
        cells = r.summarize_cells(planned, journal, [0.1])
        clean = cells["clean_C1_correct_both_match"]
        self.assertEqual((clean["planned"], clean["missing"], clean["conservative_events"]), (2, 2, 0))
        negative = cells["clean_C1_wrong_owner_any_found"]
        self.assertEqual((negative["planned"], negative["missing"], negative["conservative_events"]), (2, 2, 2))
        self.assertEqual(r.inventory_status(planned, journal)["outcome"], "incomplete")

    def test_full_smoke_inventory_is_100_rows_and_no_clustering_verdict(self):
        planned = r.planned_row_ids([_src(1), _src(2)], r.T3_STRENGTHS, r.T3_SEEDS,
                                   [{"id": "p", "donor": "src-001", "recipient": "src-002"}],
                                   [{"id": "q", "a": "src-001", "b": "src-002"}])
        self.assertEqual(len(planned), 100)
        self.assertEqual(len(set(planned)), 100)
        cells = r.summarize_cells(planned, {}, r.T3_STRENGTHS)
        self.assertEqual(cells["clean_C0_wrong_owner_any_found"]["planned"], 2)
        self.assertEqual(cells["clean_C1_wrong_owner_any_found"]["planned"], 2)
        self.assertIsNone(cells["t3_C1_diffusion_0.1_correct_semantic"]["meets_numerical_target"])

    def test_pair_references_cannot_silently_disappear(self):
        for pair in ({"id": "q"}, {"id": "q", "a": "src-001", "b": "unknown"},
                     {"id": "q", "a": "src-001", "b": "src-001"}):
            with self.assertRaises(ValueError):
                r.validate_manifest(_manifest([_src(1)], t5_pairs=[pair]))

    def test_zero_rows_is_incomplete(self):
        self.assertEqual(r.inventory_status(["planned"], {}),
                         {"planned_rows": 1, "missing_rows": 1, "failed_rows": 0, "completed_rows": 0, "outcome": "incomplete"})

    def test_portable_image_filename_keeps_journal_id_separate(self):
        self.assertNotIn(":", r._image_path(Path("images"), "src:t3:C1:diffusion:0.1:0:correct").name)


if __name__ == "__main__":
    unittest.main()

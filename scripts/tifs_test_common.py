"""Pure-logic Stage S tests; no scientific modules, images or GPU access."""
import copy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tifs_common import (Budget, Journal, ResourceStop, atomic_json, clean_ids,
                         load_json, majority_bounds, planned_output_ids, predicates,
                         quality_eligible, runtime_identity, secondary_ids, sha256_file,
                         stable_seed, strict_quality, validate_output, validate_sources)

ROOT = Path(__file__).resolve().parents[1]
TD = ROOT / "research/tifs-20261028/stage-s"


class CommonTests(unittest.TestCase):
    def test_json_strict_and_atomic(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "a.json"
            atomic_json(p, {"a": 1})
            self.assertEqual(load_json(p), {"a": 1})
            with self.assertRaises(ValueError):
                atomic_json(p, {"a": float("nan")})
            self.assertEqual(load_json(p), {"a": 1})
            for raw in ('{"a":NaN}', '{"a":1e999}', '{"a":1,"a":2}'):
                p.write_text(raw)
                with self.assertRaises(ValueError):
                    load_json(p)

    def test_journal_last_wins_terminal_and_torn(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "events.jsonl"
            j = Journal(p)
            j.append({"id": "x", "status": "retry"})
            self.assertFalse(j.done("x"))
            for status in ("ok", "safety_blocked", "error_terminal"):
                j.append({"id": "x", "status": status})
                self.assertTrue(j.done("x"))
            with p.open("ab") as stream:
                stream.write(b'{"id":"torn')
            j = Journal(p)
            self.assertEqual(j.latest["x"]["status"], "error_terminal")
            self.assertEqual(len(list(Path(t).glob("*.torn-*"))), 1)
            j.append({"id": "y", "status": "ok"})
            self.assertTrue(Journal(p).done("y"))

    def test_journal_corruption_not_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "j"
            for raw in (b'broken\n{"id":"y","status":"ok"}\n', b'broken\n',
                        b'{"id":"x"}', b'{"id":"x","status":"ok","a":NaN}'):
                p.write_bytes(raw)
                with self.assertRaises((ValueError, TypeError)):
                    Journal(p)
            p.write_bytes(b'{"id":"x","status":"ok"}')
            self.assertTrue(Journal(p).done("x"))
            self.assertTrue(p.read_bytes().endswith(b"\n"))

    def test_output_hash_missing_corrupt_and_escape(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "artifact.bin"
            p.write_bytes(b"saved output")
            row = {"id": "x", "status": "ok", "output": {"path": p.name, "sha256": sha256_file(p)}}
            self.assertTrue(validate_output(row, t))
            p.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                validate_output(row, t)
            p.unlink()
            with self.assertRaises(ValueError):
                validate_output(row, t)
            row["output"]["path"] = "../outside.bin"
            with self.assertRaises(ValueError):
                validate_output(row, t)
            with self.assertRaises(ValueError):
                validate_output({"status": "ok"}, t)
            self.assertFalse(validate_output({"status": "safety_blocked"}, t))
            self.assertTrue(validate_output({"status": "ok", "artifact_required": False}, t))

    def test_majority_all_missingness_assignments(self):
        for vals in itertools.product((False, True, None), repeat=3):
            completions = [x for x in itertools.product((False, True), repeat=3)
                           if all(v is None or v == c for v, c in zip(vals, x))]
            results = [sum(x) >= 2 for x in completions]
            self.assertEqual(majority_bounds(vals), (all(results), any(results)))
        for vals in ([True], [1, False, None], [None] * 4):
            with self.assertRaises(ValueError):
                majority_bounds(vals)

    def test_predicates_semantic_read_vs_recomputation_and_exact(self):
        d = {"semantic": {"found": True, "content_match": True, "read": False, "decoded_code": "a"},
             "instance": {"found": False, "read": True, "decoded_code": "f"}, "outcome": "both_match"}
        p = predicates(d, {"q": 10, "h": 15})
        self.assertTrue(p["S"] and p["F"] and p["recomputed_only_S"])
        self.assertFalse(p["C"] or p["Q"] or p["J"] or p["D"])
        d["semantic"]["read"] = True
        p = predicates(d, {"q": 10, "h": 15})
        self.assertTrue(all(p[k] for k in ("C", "Q", "J", "H", "D", "F", "A")))
        self.assertEqual(p["q_bit_errors"], 0)
        p = predicates(d, {"q": 11, "h": 15})
        self.assertTrue(p["C"])
        self.assertFalse(p["Q"] or p["J"] or p["D"])
        self.assertEqual(p["q_bit_errors"], 1)
        p = predicates(d)
        self.assertIsNone(p["q_bit_errors"])
        self.assertFalse(p["Q"])
        self.assertFalse(predicates(d, {"q": True, "h": True})["D"])

    def test_strict_quality_boundaries_and_nonfinite(self):
        q = {"psnr_db": 36., "ssim_rgb": .91, "lpips": .09}
        self.assertTrue(strict_quality(q))
        for key, bound in (("psnr_db", 35.), ("ssim_rgb", .9), ("lpips", .1)):
            self.assertFalse(strict_quality(dict(q, **{key: bound})))
            for invalid in (None, float("nan"), float("inf"), True):
                self.assertFalse(strict_quality(dict(q, **{key: invalid})))
        self.assertTrue(strict_quality(dict(q, psnr_db=None, psnr_infinite=True)))
        self.assertFalse(strict_quality(dict(q, psnr_db=0, psnr_infinite=True)))
        self.assertTrue(quality_eligible({"psnr_db": 26, "ssim_rgb": .8, "lpips": .12},25,.75,.15))

    def test_frozen_sources_and_inventory(self):
        config, manifest = load_json(TD / "frozen-config.json"), load_json(TD / "source-manifest.json")
        pool = load_json(ROOT / manifest["source_file"])
        self.assertTrue(validate_sources(manifest, pool))
        self.assertEqual(sha256_file(ROOT / manifest["source_file"]), manifest["source_file_sha256"])
        self.assertEqual(sha256_file(TD / "source-manifest.json"), config["source_manifest_sha256"])
        ids = [r["source_id"] for r in manifest["screen_donors"]]
        self.assertEqual(len(set(planned_output_ids(config, ids))), 1536)
        self.assertEqual(len(clean_ids(config, ids)), 128)
        self.assertEqual(len(secondary_ids(config, ids)), 1024)
        self.assertIn(f"native:R0-0.2:{ids[0]}:0:f6-noise", planned_output_ids(config, ids))
        bad = copy.deepcopy(manifest)
        bad["screen_targets"][0] = bad["screen_donors"][0]
        with self.assertRaises(ValueError):
            validate_sources(bad, pool)
        bad = copy.deepcopy(manifest)
        bad["screen_donors"].reverse()
        with self.assertRaises(ValueError):
            validate_sources(bad, pool)
        with self.assertRaises(ValueError):
            planned_output_ids(config, ids + ids)

    def test_seed_streams_and_resume_identity(self):
        self.assertEqual(stable_seed("opt", 1, 2), stable_seed("opt", 1, 2))
        self.assertNotEqual(stable_seed("opt", 1, 2), stable_seed("diag", 1, 2))
        self.assertNotEqual(stable_seed("ab", "c"), stable_seed("a", "bc"))
        with tempfile.TemporaryDirectory() as t:
            paths = [Path(t) / str(i) for i in range(4)]
            for p in paths:
                p.write_bytes(b"frozen")
            a = runtime_identity(paths[0], paths[1], [paths[2]], [paths[3]])
            for p in paths:
                p.write_bytes(b"changed")
                self.assertNotEqual(a, runtime_identity(paths[0], paths[1], [paths[2]], [paths[3]]))
                p.write_bytes(b"frozen")

    def test_budget_clock_reserve_restart_and_forecast(self):
        now = [100.]
        b = Budget(100, clock=lambda: now[0], reserve_seconds=20)
        self.assertTrue(b.can_start(80))
        now[0] += 1
        self.assertFalse(b.can_start(80))
        with self.assertRaises(ResourceStop):
            b.require(80)
        resumed = Budget(100, clock=lambda: now[0], reserve_seconds=20, elapsed_seconds=30)
        self.assertEqual(resumed.remaining, 70)
        self.assertEqual(Budget.forecast(100, 100, 50, 300), {"forecast_seconds": 300., "within_budget": True})
        self.assertFalse(Budget.forecast(100, 101, 50, 300)["within_budget"])
        with self.assertRaises(ValueError):
            b.can_start(float("nan"))


if __name__ == "__main__":
    unittest.main()

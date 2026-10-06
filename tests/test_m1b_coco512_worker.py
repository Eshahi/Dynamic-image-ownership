"""CPU tests for the M1b COCO512 worker with an injected fake runtime (no models, no held-out data)."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import m1b_coco512_worker as W  # noqa: E402

UIDS = [f"synthetic:{i}" for i in range(6)]


def plan(**over):
    p = dict(schema=W.PLAN_SCHEMA, data_split="development", methods=list(W.METHODS),
             f5_config=dict(path="configs/f5-r2.json", sha256="0" * 64),
             profile=dict(path="experiments/c4-v5-two-tier-regeneration-v1/profile.json", sha256="0" * 64),
             assets_root="unused",
             sources=dict(inline=[dict(uid=u, group_id=f"g{i}", raw_path=f"unused/{i}.png", raw_sha256="a" * 64)
                                  for i, u in enumerate(UIDS)]),
             t3_uids=UIDS[:2],
             t4_pairs=[dict(pair_index=0, donor_uid=UIDS[0], recipient_uid=UIDS[1]),
                       dict(pair_index=1, donor_uid=UIDS[2], recipient_uid=UIDS[3])],
             t5=dict(selector="fixture-categories", max_pairs=2, categories={u: [1] for u in UIDS}),
             strengths=list(W.STRENGTHS), seeds=list(W.SEEDS), patch_sizes=list(W.PATCH_SIZES))
    p.update(over)
    return p


class FakeRuntime:
    """Marks survive VAE and strengths <= .1; detections read a registry keyed by pixel hash."""

    marks = {}  # content-addressed, so a resumed runtime reads the same pixels the same way

    def __init__(self, plan, fail=None):
        self.fail = fail or set()
        self.calls = []

    def _key(self, rgb):
        return hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest()

    def canonical(self, s):
        if ("canon", s["uid"]) in self.fail:
            raise ValueError("decode failed")
        seed = int(hashlib.sha256(s["uid"].encode()).hexdigest()[:8], 16)
        rgb = np.random.default_rng(seed).integers(0, 256, (512, 512, 3), dtype=np.uint8)
        return rgb, dict(rgb8_sha256=self._key(rgb))

    def phash(self, rgb):
        return int(self._key(rgb)[:8], 16)

    def embed(self, method, rgb, uid, owner):
        if ("embed", uid, method) in self.fail:
            raise RuntimeError("optimizer diverged")
        out = rgb.copy()
        out[0, 0, 0] ^= 1 if method == "f5-r2" else 2
        self.marks[self._key(out)] = (owner, True)
        return out, dict(verification=dict(outcome="both_match"))

    def detect(self, method, rgb, claim):
        self.calls.append(method)
        owner, fragile = self.marks.get(self._key(rgb), (None, False))
        hit = owner == claim
        sem = dict(found=hit, read=hit, content_match=hit)
        inst = dict(found=hit and fragile, read=hit and fragile, content_match=hit and fragile)
        outcome = "both_match" if hit and fragile else ("semantic_only" if hit else "neither_match")
        return dict(outcome=outcome, semantic=sem, instance=inst)

    def attack(self, rgb, dose):
        if dose == "ddim-0.2-1":
            raise RuntimeError("safety_checker_blocked_output")
        out = rgb.copy()
        out[1, 1, 1] ^= 4 + W.DOSES.index(dose)
        owner, _ = self.marks.get(self._key(rgb), (None, False))
        if owner and (dose == "vae" or dose.startswith(("ddim-0.05", "ddim-0.1"))):
            self.marks[self._key(out)] = (owner, False)
        return out, dict(dose=dose)

    def patch(self, rec, donor, size, control):
        out = rec.copy()
        a = (512 - size) // 2
        out[a:a + size, a:a + size] = donor[a:a + size, a:a + size]
        return out, dict(size=size, donor_control=control)

    def quality(self, ref, rgb):
        mse = float(np.mean((ref.astype(float) - rgb) ** 2))
        return dict(psnr_db=None if mse == 0 else 10 * np.log10(255 ** 2 / mse), psnr_infinite=mse == 0,
                    ssim_rgb=0.99, lpips=0.01)

    def categories(self, uids, t5):
        return {u: tuple(t5["categories"][u]) for u in uids}


def run(p, out, rt=None, clock=None):
    p, sources = W.validate_plan(p)
    rt = rt or FakeRuntime(p)
    kw = {} if clock is None else dict(clock=clock)
    worker = W.Worker(p, sources, out, rt, **kw)
    status, selected = worker.run()
    return status, selected, W.analyse(p, sources, worker.journal.rows, selected), worker


class PlanTests(unittest.TestCase):
    def test_valid_plan_and_owner_schedule(self):
        p, sources = W.validate_plan(plan())
        from a4_protocol_reference import owner_and_seed
        self.assertEqual(sources[0]["owner"], owner_and_seed(UIDS[0])[0])

    def test_rejects_grid_changes_and_bad_pairs(self):
        for bad in (dict(strengths=[0.1, 0.2]), dict(seeds=[0, 1]), dict(patch_sizes=[128]),
                    dict(methods=["f5-r2"]), dict(t3_uids=["nope"]),
                    dict(t4_pairs=[dict(pair_index=0, donor_uid=UIDS[0], recipient_uid=UIDS[0])]),
                    dict(t4_pairs=[dict(pair_index=0, donor_uid=UIDS[0], recipient_uid=UIDS[1]),
                                   dict(pair_index=1, donor_uid=UIDS[2], recipient_uid=UIDS[1])])):
            with self.assertRaises(ValueError, msg=str(bad)):
                W.validate_plan(plan(**bad))

    def test_owner_mismatch_rejected(self):
        p = plan()
        p["sources"]["inline"][0]["owner"] = "thesis:owner:99"
        with self.assertRaises(ValueError):
            W.validate_plan(p)

    def test_test_split_needs_index_annotations_and_approval(self):
        with self.assertRaises(ValueError):
            W.validate_plan(plan(data_split="test"))

    def test_science_digest_ignores_operational_fields(self):
        a = plan()
        b = plan(max_wall_seconds=600, resume_from="x")
        self.assertEqual(W.science_digest(a), W.science_digest(b))
        self.assertNotEqual(W.science_digest(a), W.science_digest(plan(t3_uids=UIDS[:1])))

    def test_planned_inventory_counts(self):
        p, s = W.validate_plan(plan())
        ids = W.planned_ids(p, s, [dict(left=UIDS[0], right=UIDS[1])])
        per_source = 1 + 2 * 5
        per_t3 = 13 * (1 + 2 + 2 * 3)
        per_t4 = 2 * (1 + 4 + 2 * 3)
        self.assertEqual(len(ids), 6 * per_source + 2 * per_t3 + 2 * per_t4 + 1 + 8)

    def test_full_draft_counts_per_method(self):
        # 30 T3 sources: 780 attack outputs/method in the draft = 30*13*(C0 + C1); C0 is shared here.
        ids = W.t3_ids("u")
        self.assertEqual(sum(i.startswith("atk:") for i in ids), 13 * 3)
        self.assertEqual(sum(i.startswith("t3:") and ":f5-r2:" in i for i in ids), 13 * 3)  # 1170/30 calls/method
        self.assertEqual(sum(i.startswith("t4:") and ":f5-r2:" in i for i in W.t4_ids(0)), 8)  # 240/30


class RunTests(unittest.TestCase):
    def test_complete_run_and_endpoints(self):
        with tempfile.TemporaryDirectory() as d:
            status, selected, res, _ = run(plan(), Path(d))
            self.assertEqual(status, "finished")
            inv = res["inventory"]
            self.assertTrue(inv["complete"], inv)
            # one blocked dose per T3 input retained adversely, never substituted
            self.assertEqual(inv["states"]["safety_blocked"], 2 * 3)
            f5 = res["methods"]["f5-r2"]
            self.assertEqual(f5["clean"]["C1_correct_both_match"]["observed_events"], 6)
            self.assertEqual(f5["clean"]["C0_correct_any_found"]["observed_events"], 0)
            t3 = f5["t3"]
            self.assertEqual(t3["vae"]["rows"]["semantic"]["observed_events"], 2)
            self.assertEqual(t3["ddim-0.1"]["source_majority_semantic"]["observed_events"], 2)
            self.assertEqual(t3["ddim-0.4"]["source_majority_semantic"]["observed_events"], 0)
            # .2 seed 1 blocked: 2 of 3 rows missing-as-miss -> majority fails
            self.assertEqual(t3["ddim-0.2"]["rows"]["semantic"]["missing"], 2)
            self.assertEqual(f5["t4"]["false_donor_attribution_rows"]["observed_events"], 0)
            self.assertEqual(res["methods"]["v5-r3"]["t5"]["selected_pairs"], len(selected))
            self.assertEqual(len(selected), 2)

    def test_failures_propagate_as_missing_not_replaced(self):
        with tempfile.TemporaryDirectory() as d:
            p = plan()
            rt = FakeRuntime(p, fail={("embed", UIDS[0], "f5-r2"), ("canon", UIDS[5])})
            status, selected, res, worker = run(p, Path(d), rt)
            rows = worker.journal.rows
            self.assertEqual(rows[f"src:{UIDS[0]}:f5-r2:embed"]["outcome"], "failed")
            self.assertEqual(rows[f"src:{UIDS[0]}:f5-r2:clean:C1:correct"]["outcome"], "missing_dependency")
            self.assertEqual(rows[f"t4img:0:128:C1-f5-r2"]["outcome"], "missing_dependency")
            self.assertEqual(rows[f"src:{UIDS[5]}:v5-r3:embed"]["outcome"], "missing_dependency")
            self.assertTrue(res["inventory"]["complete"])
            clean = res["methods"]["f5-r2"]["clean"]["C1_correct_both_match"]
            self.assertEqual((clean["planned"], clean["valid"], clean["observed_events"]), (6, 4, 4))
            neg = res["methods"]["f5-r2"]["clean"]["C0_wrong_any_found"]
            self.assertEqual(neg["conservative_events"], 1)  # missing negative counts adversely

    def test_cooperative_stop_then_resume_reaches_same_result(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            _, _, full, _ = run(plan(), Path(d1))
            ticks = iter(range(10 ** 6))
            p = plan(max_wall_seconds=60)
            status, _, part, w = run(p, Path(d2), clock=lambda: next(ticks) * 0.5)
            self.assertEqual(status, "checkpointed")
            self.assertFalse(part["inventory"]["complete"])
            n = len(w.journal.rows)
            status2, _, res, w2 = run(plan(), Path(d2))
            self.assertEqual(status2, "finished")
            self.assertGreater(len(w2.journal.rows), n)
            def strip(r):
                m = json.loads(json.dumps(r["methods"]))
                for v in m.values():
                    v["clean"]["quality"].pop("seconds_mean")
                return m
            self.assertEqual(strip(res), strip(full))

    def test_torn_last_line_is_dropped_and_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            run(plan(), out)
            j = out / "outputs" / "journal.jsonl"
            lines = j.read_text(encoding="utf-8").splitlines()
            last = json.loads(lines[-1])["id"]
            j.write_text("\n".join(lines[:-1]) + "\n" + lines[-1][:20], encoding="utf-8")
            journal = W.Journal(out)
            self.assertEqual(journal.torn_lines, 1)
            self.assertNotIn(last, journal)
            _, _, res, _ = run(plan(), out)
            self.assertTrue(res["inventory"]["complete"])

    def test_corruption_before_last_line_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            run(plan(), out)
            j = out / "outputs" / "journal.jsonl"
            lines = j.read_text(encoding="utf-8").splitlines()
            lines[3] = lines[3][:10]
            j.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                W.Journal(out)

    def test_changed_saved_image_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            p = plan(t3_uids=[], t4_pairs=[], max_wall_seconds=60)
            ticks = iter(range(10 ** 6))
            run(p, out, clock=lambda: next(ticks) * 2.0)
            png = next((out / "outputs" / "images").glob("*-C0.png"))
            from PIL import Image
            arr = np.asarray(Image.open(png)).copy()
            arr[5, 5, 0] ^= 1
            Image.fromarray(arr).save(png)
            with self.assertRaises(RuntimeError):
                run(plan(t3_uids=[], t4_pairs=[]), out)


class RuleTests(unittest.TestCase):
    def test_event_rules(self):
        det = dict(outcome="semantic_only", semantic=dict(found=True, read=False, content_match=True),
                   instance=dict(found=False))
        self.assertTrue(W.event(det, "semantic"))
        self.assertTrue(W.event(det, "semantic_assumed"))
        self.assertFalse(W.event(det, "semantic_checked"))
        self.assertFalse(W.event(det, "both_match"))
        self.assertTrue(W.event(det, "any_found"))
        with self.assertRaises(ValueError):
            W.event(det, "best_seed")

    def test_sign_test(self):
        self.assertIsNone(W._sign_test(0, 0))
        self.assertAlmostEqual(W._sign_test(5, 0), 0.0625)
        self.assertEqual(W._sign_test(3, 3), 1.0)

    def test_coco_categories(self):
        data = dict(images=[dict(id=7), dict(id=9)],
                    annotations=[dict(image_id=7, iscrowd=0, category_id=3), dict(image_id=7, iscrowd=1, category_id=5),
                                 dict(image_id=7, iscrowd=0, category_id=1), dict(image_id=11, iscrowd=0, category_id=2)])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "ann.json"
            raw = json.dumps(data).encode()
            path.write_bytes(raw)
            out = W.coco_categories(["c:val2017:7", "c:val2017:9", "c:val2017:12", "bad"], path,
                                    hashlib.sha256(raw).hexdigest())
            self.assertEqual(out["c:val2017:7"], (1, 3))
            self.assertEqual(out["c:val2017:9"], ())
            self.assertEqual(out["c:val2017:12"], "image_missing_from_annotations")
            self.assertEqual(out["bad"], "uid_has_no_coco_image_id")
            with self.assertRaises(ValueError):
                W.coco_categories(["c:val2017:7"], path, "0" * 64)


if __name__ == "__main__":
    unittest.main()

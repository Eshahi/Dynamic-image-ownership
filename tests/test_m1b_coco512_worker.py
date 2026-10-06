"""CPU tests for the M1b COCO512 worker and analysis with an injected fake runtime (no models, no held-out data)."""
import hashlib
import io
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
import m1b_coco512_analysis as A  # noqa: E402

UIDS = [f"synthetic:{i}" for i in range(6)]


def plan(uids=UIDS, **over):
    p = dict(schema=W.PLAN_SCHEMA, data_split="development", methods=list(W.METHODS),
             f5_config=dict(path="configs/f5-r2.json", sha256="0" * 64),
             profile=dict(path="experiments/c4-v5-two-tier-regeneration-v1/profile.json", sha256="0" * 64),
             assets_root="unused",
             sources=dict(inline=[dict(uid=u, group_id=f"g-{u}", raw_path=f"unused/{i}.png", raw_sha256="a" * 64)
                                  for i, u in enumerate(uids)]),
             t3_uids=list(uids[:2]),
             t4_pairs=[dict(pair_index=0, donor_uid=uids[0], recipient_uid=uids[1]),
                       dict(pair_index=1, donor_uid=uids[2], recipient_uid=uids[3])],
             t5=dict(selector="fixture-categories", max_pairs=2, categories={u: [1] for u in uids}),
             strengths=list(W.STRENGTHS), seeds=list(W.SEEDS), patch_sizes=list(W.PATCH_SIZES))
    p.update(over)
    return p


class FakeRuntime:
    """Marks survive VAE and strengths <= .1; detections read a content-addressed registry."""

    marks = {}  # content-addressed, so a resumed runtime reads the same pixels the same way

    def __init__(self, plan, fail=None):
        self.fail = fail or set()

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

    def clip_vector(self, rgb, views):
        v = np.frombuffer(bytes.fromhex(self._key(rgb)), dtype=np.uint8).astype(float) - 127.5
        return list(v / np.linalg.norm(v))

    def embed(self, method, rgb, uid, owner):
        if ("embed", uid, method) in self.fail:
            raise RuntimeError("optimizer diverged")
        out = rgb.copy()
        out[0, 0, 0] ^= 1 if method == "f5-r2" else 2
        self.marks[self._key(out)] = (owner, True)
        return out, dict(verification=dict(outcome="both_match"))

    def detect(self, method, rgb, claim):
        owner, fragile = self.marks.get(self._key(rgb), (None, False))
        hit = owner == claim
        sem = dict(found=hit, read=hit, content_match=hit)
        inst = dict(found=hit and fragile, read=hit and fragile, content_match=hit and fragile)
        outcome = "both_match" if hit and fragile else ("semantic_only" if hit else "neither_match")
        return dict(outcome=outcome, semantic=sem, instance=inst, semantic_code=self._key(rgb)[:8],
                    perceptual_hash=self._key(rgb)[8:16])

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
    status, selected, error = worker.run()
    res = A.analyse(p, sources, worker.journal.rows, selected) if status == "finished" else \
        dict(inventory=A.inventory(W.planned_ids(p, sources, selected), worker.journal.rows))
    return status, selected, res, worker, error


def strip(res):
    m = json.loads(json.dumps(res["methods"]))
    for v in m.values():
        v["clean"]["quality"].pop("embed_seconds_mean")
    return m


class PlanTests(unittest.TestCase):
    def test_valid_plan_and_owner_schedule(self):
        p, sources = W.validate_plan(plan())
        from a4_protocol_reference import owner_and_seed
        self.assertEqual(sources[0]["owner"], owner_and_seed(UIDS[0])[0])

    def test_rejects_grid_changes_and_bad_pairs(self):
        for bad in (dict(strengths=[0.1, 0.2]), dict(seeds=[0, 1]), dict(patch_sizes=[128]),
                    dict(methods=["f5-r2"]), dict(t3_uids=["nope"]), dict(official_runtime="x"),
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

    def test_frozen_test_plan_validates(self):
        p = json.loads((ROOT / "research/m1b-coco512-test.m1b-plan.json").read_text(encoding="utf-8"))
        _, sources = W.validate_plan(p)
        self.assertEqual(len(sources), 300)
        for change in (dict(t3_uids=p["t3_uids"][::-1]), dict(approval_path=None),
                       dict(fault_injection=[dict(unit="t5:selection", kind="oserror")]),
                       dict(t5=dict(p["t5"], max_pairs=29)), dict(schedule=None)):
            with self.assertRaises(ValueError, msg=str(change)):
                W.validate_plan(dict(p, **change))

    def test_non_test_plans_cannot_touch_held_out(self):
        p = json.loads((ROOT / "research/m1b-coco512-test.m1b-plan.json").read_text(encoding="utf-8"))
        for split in ("development", "rehearsal"):
            with self.assertRaises(ValueError):
                W.validate_plan(dict(p, data_split=split))
        index = json.loads((ROOT / W.HELD_OUT_INDEX).read_text(encoding="utf-8"))["entries"][0]
        cases = [
            lambda q: q["sources"]["inline"][0].update(uid=index["source_uid"]),
            lambda q: q["sources"]["inline"][0].update(group_id=index["group_id"]),
            lambda q: q["sources"]["inline"][0].update(raw_sha256=index["raw_sha256"]),
            lambda q: q["sources"]["inline"][0].update(raw_path=W.HELD_OUT_RAW_ROOT + "/x/y.jpg"),
            lambda q: q.update(t5=dict(selector="coco-instances", max_pairs=2,
                                       annotations=dict(path="x.json", sha256=W.HELD_OUT_ANNOTATION_SHA256))),
        ]
        for i, mutate in enumerate(cases):
            q = plan()
            mutate(q)
            with self.assertRaises(ValueError, msg=f"case {i}"):
                W.validate_plan(q)

    def test_science_digest_ignores_operational_fields(self):
        a = plan()
        b = plan(max_wall_seconds=600, resume_from="x", label="y")
        self.assertEqual(W.science_digest(a), W.science_digest(b))
        self.assertNotEqual(W.science_digest(a), W.science_digest(plan(t3_uids=UIDS[:1])))

    def test_core_covers_the_import_closure(self):
        closure = set(W.code_closure())
        for f in ("revised_watermark_v4", "revised_watermark_v5", "f5_latent_codec", "a6_clip_visual",
                  "m1_latent_reconstruction", "m1_blind_noise", "m1_confirmatory_image_operations",
                  "m1b_coco512_analysis", "m1b_canonical_source", "three_threat_models", "verify_science_assets",
                  "check_a6_lpips_assets", "m1_confirmatory_t5_pairs", "m1_confirmatory_endpoints"):
            self.assertIn(f"scripts/{f}.py", closure)
        core = W.scientific_core(json.loads((ROOT / "research/m1b-coco512-test.m1b-plan.json").read_text(encoding="utf-8")))
        self.assertIn(W.ASSET_LOCK, core["data_sha256"])
        self.assertIn(W.HELD_OUT_SCHEDULE, core["data_sha256"])

    def test_planned_inventory_counts(self):
        p, s = W.validate_plan(plan())
        ids = W.planned_ids(p, s, [dict(left=UIDS[0], right=UIDS[1])])
        per_source, per_t3, per_t4 = 1 + 2 * 5, 13 * (1 + 2 + 2 * 3), 2 * (1 + 4 + 2 * 3)
        self.assertEqual(len(ids), 6 * per_source + 2 * per_t3 + 2 * per_t4 + 1 + 9)

    def test_full_draft_counts_per_method(self):
        ids = W.t3_ids("u")
        self.assertEqual(sum(i.startswith("atk:") for i in ids), 13 * 3)
        self.assertEqual(sum(i.startswith("t3:") and ":f5-r2:" in i for i in ids), 13 * 3)  # 1170/30 calls/method
        self.assertEqual(sum(i.startswith("t4:") and ":f5-r2:" in i for i in W.t4_ids(0)), 8)  # 240/30


class RunTests(unittest.TestCase):
    def test_complete_run_and_endpoints(self):
        with tempfile.TemporaryDirectory() as d:
            status, selected, res, _, _ = run(plan(), Path(d))
            self.assertEqual(status, "finished")
            inv = res["inventory"]
            self.assertTrue(inv["complete"], inv)
            self.assertEqual(inv["states"]["safety_blocked"], 2 * 3)  # retained, never substituted
            f5 = res["methods"]["f5-r2"]
            self.assertEqual(f5["clean"]["C1_correct_both_match"]["observed_events"], 6)
            self.assertEqual(f5["clean"]["C0_correct_any_found"]["role"], "primary")
            self.assertEqual(f5["clean"]["C0_correct_any_found"]["observed_events"], 0)
            t3 = f5["t3"]
            self.assertEqual(t3["vae"]["rows"]["semantic"]["observed_events"], 2)
            self.assertIsNone(t3["vae"]["rows"]["semantic"]["meets_numerical_target"])
            self.assertEqual(t3["ddim-0.1"]["source_majority_semantic"]["observed_events"], 2)
            self.assertEqual(t3["ddim-0.4"]["source_majority_semantic"]["observed_events"], 0)
            self.assertEqual(t3["ddim-0.2"]["rows"]["semantic"]["missing"], 2)
            self.assertEqual(t3["ddim-0.2"]["per_seed"]["ddim-0.2-1"]["semantic"]["missing"], 2)
            self.assertEqual(f5["t4"]["false_donor_full_attribution_rows"]["observed_events"], 0)
            self.assertEqual(len(selected), 2)
            self.assertEqual(len(f5["t5"]["collision_descriptors"]), 2)
            self.assertIsNotNone(f5["t5"]["collision_descriptors"][0]["clip_cosine_views7"])
            self.assertIn("semantic_checked", res["paired_t3_source_majority"])

    def test_scientific_failures_propagate_as_missing_not_replaced(self):
        with tempfile.TemporaryDirectory() as d:
            p = plan()
            rt = FakeRuntime(p, fail={("embed", UIDS[0], "f5-r2"), ("canon", UIDS[5])})
            status, selected, res, worker, _ = run(p, Path(d), rt)
            rows = worker.journal.rows
            self.assertEqual(status, "finished")
            self.assertEqual(rows[f"src:{UIDS[0]}:f5-r2:embed"]["outcome"], "failed")
            self.assertEqual(rows[f"src:{UIDS[0]}:f5-r2:clean:C1:correct"]["outcome"], "missing_dependency")
            self.assertEqual(rows["t4img:0:128:C1-f5-r2"]["outcome"], "missing_dependency")
            self.assertEqual(rows[f"src:{UIDS[5]}:v5-r3:embed"]["outcome"], "missing_dependency")
            clean = res["methods"]["f5-r2"]["clean"]["C1_correct_both_match"]
            self.assertEqual((clean["planned"], clean["valid"], clean["observed_events"]), (6, 4, 4))
            self.assertEqual(res["methods"]["f5-r2"]["clean"]["C0_wrong_any_found"]["conservative_events"], 1)

    def test_infrastructure_fault_stops_without_row_then_resumes_identically(self):
        for kind in ("oserror", "cuda"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
                _, _, full, _, _ = run(plan(), Path(d1))
                unit = f"atk:{UIDS[1]}:C1-f5-r2:ddim-0.1-0"
                status, _, part, w, error = run(plan(fault_injection=[dict(unit=unit, kind=kind)]), Path(d2))
                self.assertEqual(status, "infrastructure_stop")
                self.assertIn(unit, error)
                self.assertNotIn(unit, w.journal)
                self.assertFalse(part["inventory"]["complete"])
                status2, _, res, _, _ = run(plan(), Path(d2))
                self.assertEqual(status2, "finished")
                self.assertEqual(strip(res), strip(full))

    def test_consecutive_failures_stop_the_run(self):
        with tempfile.TemporaryDirectory() as d:
            units = [f"src:{UIDS[0]}:f5-r2:clean:{a}:{c}" for a, c in (("C0", "correct"), ("C0", "wrong"), ("C1", "correct"))]
            status, _, _, w, error = run(plan(fault_injection=[dict(unit=u, kind="scientific") for u in units]), Path(d))
            self.assertEqual(status, "infrastructure_stop")
            self.assertIn("consecutive", error)
            self.assertEqual([w.journal.get(u)["outcome"] for u in units[:2]], ["failed", "failed"])
            self.assertNotIn(units[2], w.journal)

    def test_cooperative_stop_then_resume_reaches_same_result(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            _, _, full, _, _ = run(plan(), Path(d1))
            ticks = iter(range(10 ** 6))
            status, _, part, w, _ = run(plan(max_wall_seconds=60), Path(d2), clock=lambda: next(ticks) * 0.5)
            self.assertEqual(status, "checkpointed")
            self.assertNotIn("methods", part)
            n = len(w.journal.rows)
            status2, _, res, w2, _ = run(plan(), Path(d2))
            self.assertEqual(status2, "finished")
            self.assertGreater(len(w2.journal.rows), n)
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
            self.assertTrue(run(plan(), out)[2]["inventory"]["complete"])

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

    def test_changed_saved_image_is_a_storage_fault(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            ticks = iter(range(10 ** 6))
            run(plan(t3_uids=[], t4_pairs=[], max_wall_seconds=60), out, clock=lambda: next(ticks) * 2.0)
            png = next((out / "outputs" / "images").glob("*-C0.png"))
            from PIL import Image
            arr = np.asarray(Image.open(png)).copy()
            arr[5, 5, 0] ^= 1
            Image.fromarray(arr).save(png)
            with self.assertRaises(OSError):
                run(plan(t3_uids=[], t4_pairs=[]), out)

    def test_same_owner_t4_pair_excluded_from_cross_owner_cells(self):
        from a4_protocol_reference import owner_and_seed
        pool = [f"synthetic:{i}" for i in range(200)]
        by_owner = {}
        for u in pool:
            by_owner.setdefault(owner_and_seed(u)[0], []).append(u)
        a, b = next(v for v in by_owner.values() if len(v) >= 2)[:2]
        rest = [u for u in pool if owner_and_seed(u)[0] != owner_and_seed(a)[0]][:2]
        uids = [a, b] + rest
        p = plan(uids=uids, t3_uids=[], t4_pairs=[dict(pair_index=0, donor_uid=a, recipient_uid=b),
                                                   dict(pair_index=1, donor_uid=rest[0], recipient_uid=rest[1])],
                 t5=dict(selector="fixture-categories", max_pairs=1, categories={u: [1] for u in uids}))
        with tempfile.TemporaryDirectory() as d:
            _, _, res, _, _ = run(p, Path(d))
            t4 = res["methods"]["f5-r2"]["t4"]
            self.assertEqual(t4["same_owner_pairs"], [0])
            self.assertEqual(t4["recipient_claim_any_found_rows"]["planned"], 2)
            self.assertEqual(t4["donor_semantic_consistent_rows"]["planned"], 2)
            self.assertEqual(t4["recipient_claim_any_found_rows"]["observed_events"], 0)

    def test_full_scale_bookkeeping(self):
        """300 sources, 30 T3 sources, 30 T4 pairs and the 44,850-pair T5 ledger on the fake runtime."""
        uids = [f"synthetic-scale:{i}" for i in range(300)]
        p = plan(uids=uids, t3_uids=uids[:30],
                 t4_pairs=[dict(pair_index=i, donor_uid=uids[100 + i], recipient_uid=uids[200 + i]) for i in range(30)],
                 t5=dict(selector="fixture-categories", max_pairs=30, categories={u: [1] for u in uids}))
        with tempfile.TemporaryDirectory() as d:
            status, selected, res, worker, _ = run(p, Path(d))
            self.assertEqual(status, "finished")
            self.assertEqual(len(worker.journal.get("t5:selection")["selection"]["ledger"]), 44850)
            self.assertEqual(len(selected), 30)
            self.assertTrue(res["inventory"]["complete"])
            self.assertEqual(res["inventory"]["planned"], 300 * 11 + 30 * 117 + 30 * 22 + 1 + 30 * 9)


class AnalysisTests(unittest.TestCase):
    def test_none_and_nan_metrics_fail_targets_without_crashing(self):
        q = A.quality_summary([dict(psnr_db=None, psnr_infinite=False, ssim_rgb=None, lpips=None),
                               dict(psnr_db=float("nan"), ssim_rgb=float("nan"), lpips=float("nan")),
                               dict(psnr_db=40.0, ssim_rgb=0.95, lpips=0.02), None], 4)
        self.assertEqual(q["joint"]["count"], 1)
        self.assertEqual(q["psnr_gt_35"]["count"], 1)
        self.assertEqual(q["lpips_max"], 0.02)

    def test_event_rules(self):
        det = dict(outcome="semantic_only", semantic=dict(found=True, read=False, content_match=True),
                   instance=dict(found=False))
        self.assertTrue(A.event(det, "semantic"))
        self.assertTrue(A.event(det, "semantic_assumed"))
        self.assertFalse(A.event(det, "semantic_checked"))
        self.assertFalse(A.event(det, "both_match"))
        self.assertTrue(A.event(det, "any_found"))
        with self.assertRaises(ValueError):
            A.event(det, "best_seed")

    def test_sign_test(self):
        self.assertIsNone(A.sign_test(0, 0))
        self.assertAlmostEqual(A.sign_test(5, 0), 0.0625)
        self.assertEqual(A.sign_test(3, 3), 1.0)

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


class CanonicalTests(unittest.TestCase):
    def _encode(self, image, fmt="JPEG", **kw):
        buf = io.BytesIO()
        image.save(buf, format=fmt, **kw)
        raw = buf.getvalue()
        return raw, hashlib.sha256(raw).hexdigest()

    def test_rgb_parity_with_v1(self):
        import m1_canonical_source as v1
        import m1b_canonical_source as v2
        from PIL import Image
        y, x = np.indices((300, 400))
        img = Image.fromarray(np.stack((x % 256, y % 256, (x + y) % 256), -1).astype(np.uint8))
        exif = Image.Exif()
        exif[274] = 6
        raw, digest = self._encode(img, exif=exif)
        a, ra = v1.canonicalize(raw, digest)
        b, rb = v2.canonicalize(raw, digest)
        np.testing.assert_array_equal(a, b)
        self.assertIsNone(rb["mode_conversion"])

    def test_grayscale_and_cmyk_converted_with_receipt_alpha_rejected(self):
        import m1b_canonical_source as v2
        from PIL import Image
        for mode in ("L", "CMYK"):
            raw, digest = self._encode(Image.new(mode, (64, 48)))
            rgb, receipt = v2.canonicalize(raw, digest)
            self.assertEqual(rgb.shape, (512, 512, 3))
            self.assertEqual(receipt["mode_conversion"]["from_mode"], mode)
        raw, digest = self._encode(Image.new("RGBA", (8, 8)), fmt="PNG")
        with self.assertRaises(ValueError):
            v2.canonicalize(raw, digest)


class ApprovalTests(unittest.TestCase):
    """The worker's fail-closed check, with a synthetic fixture (not a real approval)."""

    def _pair(self, d, split="rehearsal", resume=False, **approval_over):
        from datetime import datetime, timedelta, timezone
        manifest = dict(schema_version="1.0", experiment_id="fixture", run_id="fixture-run", stage_id="s", task_id="t",
                        execution_target="local", reviewed_script=W.ENTRY, script_sha256="0" * 64,
                        git_commit="0" * 40, seeds=[0], datasets=[], inputs=[], outputs=["outputs/run.json"],
                        metrics=["m"], budget=dict(max_seconds=100, max_usd=0, hourly_usd=0),
                        resources=dict(vram_mib=0, ram_mib=1, disk_mib=1), cleanup_policy="stop-for-recovery")
        now = datetime.now(timezone.utc)
        approval = dict(schema_version="1.0", experiment_id="fixture", run_id="fixture-run", execution_target="local",
                        manifest_sha256=W.object_digest(manifest), decision="approve",
                        timestamp=(now - timedelta(minutes=1)).isoformat(), expires_at=(now + timedelta(hours=1)).isoformat(),
                        max_seconds=100, max_usd=0, actor="synthetic test fixture", source_ref="unit test")
        approval.update(approval_over)
        path = Path(d) / "approval.json"
        path.write_text(json.dumps(approval), encoding="utf-8")
        p = dict(approval_path=str(path), data_split=split)
        if resume:
            p["resume_from"] = "x"
        return p, manifest

    def test_matching_approval_passes(self):
        with tempfile.TemporaryDirectory() as d:
            p, manifest = self._pair(d)
            self.assertEqual(W.check_approval(p, manifest)["actor"], "synthetic test fixture")

    def test_mismatch_or_reject_fails_closed(self):
        for over in (dict(manifest_sha256="1" * 64), dict(decision="reject"), dict(run_id="other")):
            with tempfile.TemporaryDirectory() as d:
                p, manifest = self._pair(d, **over)
                with self.assertRaises(Exception, msg=str(over)):
                    W.check_approval(p, manifest)

    def test_first_held_out_run_refuses_delegated_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p, manifest = self._pair(d, split="test", actor="delegated:agent")
            with self.assertRaises(ValueError):
                W.check_approval(p, manifest)
            p, manifest = self._pair(d, split="test", resume=True, actor="delegated:agent")
            self.assertTrue(W.check_approval(p, manifest)["delegated"])


if __name__ == "__main__":
    unittest.main()

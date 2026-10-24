"""CPU-only checks of amendment 2b (stage 2b): schedule, inherited cells, scopes, reductions, seeding.

Written by Claude (Opus 5.5), 2026-10-24. No model, image or outcome is touched; the P5 checks need numpy.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import encoder_transfer_test as et
import encoder_transfer_amend_2b as amend

CORE = ["f5-r2", "v5-r3", "wam", "vine-r"]
STUDY = et.ROOT / "research/encoder-transfer-20261019"


def build():
    if not hasattr(build, "cached"):
        config = amend.build_config("0" * 64, {"sentencepiece": "X", "protobuf": "Y"}, 25.9, 14.48, None)
        stage2a, sources = et.load_contract(STUDY / "stage2a-config.json")
        build.cached = config, stage2a, sources
    return copy.deepcopy(build.cached[0]), build.cached[1], build.cached[2]


def cell(unit):
    return (unit["channel"], unit["strength"], unit["arm"])


class Stage2bScheduleTests(unittest.TestCase):
    def test_stage2a_units_are_inherited_and_keep_their_identities(self):
        config, stage2a, sources = build()
        old = {u["id"] for u in et.plan(stage2a, sources)}
        units = list(et.plan(config, sources))
        self.assertEqual(len({u["id"] for u in units}), len(units))
        self.assertTrue(old <= {u["id"] for u in units})
        inherited = {tuple(c) for c in config["inherited_cells"]}
        self.assertEqual({u["id"] for u in units if cell(u) in inherited}, old)
        new = [u for u in units if cell(u) not in inherited]
        self.assertEqual(len(new), 60 * 3 * 5 * (2 + 2 + 1 + 1 + 2))  # R0 .1/.4, R1 .1/.4, rinse, R3, P5 pair
        self.assertEqual({u["arm"] for u in new}, {"unmarked", *CORE})
        self.assertEqual({(u["channel"], u["strength"]) for u in new},
                         {("R0", .1), ("R0", .4), ("R1", .1), ("R1", .4), ("R1-rinse", .1), ("R3", .2), ("R1-smooth", .2), ("R1-mode", .2)})

    def test_extra_baselines_stay_in_their_approved_r1_cell(self):
        config, _, sources = build()
        for arm in ("trustmark-q", "pixelseal"):
            self.assertEqual({(u["channel"], u["strength"]) for u in et.plan(config, sources) if u["arm"] == arm and u["channel"] == "R1"}, {("R1", .2)})
        unit = dict(channel="R1", arm="unmarked", strength=.1)
        self.assertEqual(et.read_methods(config, unit), CORE)
        self.assertEqual(et.read_methods(config, {**unit, "strength": .2}), config["arms"])

    def test_contract_is_an_executable_amendment_of_the_reviewed_freeze(self):
        config, _, _ = build()
        self.assertEqual(et.contract_status(config), "user-amended-pre-outcome")
        self.assertEqual(config["amendment"]["previous_amendment"]["sha256"], amend.STAGE2A_SHA256)
        self.assertEqual(config["amendment"]["stage2a_decision"]["label"], "FAILS")
        self.assertAlmostEqual(config["budget"]["max_instance_hours"], 9.1)
        self.assertAlmostEqual(config["budget"]["max_usd"], 15.52)
        for key in ("n", "seeds", "primary", "decision_external_arms", "holm_arms", "payload_bits"):
            self.assertEqual(config[key] if key != "primary" else {k: v for k, v in config[key].items() if k != "negative_scope"},
                             build.cached[1][key] if key != "primary" else {k: v for k, v in build.cached[1][key].items() if k != "negative_scope"}, key)

    def test_negative_gate_counts_only_planned_calls(self):
        config, _, sources = build()
        result = et.analyze(config, sources, {})
        negatives = result["primary_negatives"]
        self.assertEqual(negatives["f5-r2/C0"]["planned"], 540)
        self.assertEqual(negatives["f5-r2/wrong_owner"]["planned"], 540)
        self.assertEqual(negatives["trustmark-q/C0"]["planned"], 180)
        self.assertEqual(negatives["pixelseal/C0"]["planned"], 180)


class Stage2bReductionTests(unittest.TestCase):
    def test_declared_order_p5_then_p4_then_strength_point_one(self):
        config, _, _ = build()
        self.assertEqual(et.reduction_steps(config), ("channel:R1-smooth,R1-mode", "channel:R3", "strength_0.1"))
        reduced = copy.deepcopy(config)
        states = []
        for step in et.reduction_steps(config):
            et.apply_reduction(reduced, step)
            et.validate_effective(config, reduced)
            states.append({c["id"]: (c.get("enabled", True), c.get("strengths")) for c in reduced["channels"]})
        self.assertFalse(states[0]["R1-smooth"][0] or states[0]["R1-mode"][0])
        self.assertTrue(states[0]["R3"][0])
        self.assertFalse(states[1]["R3"][0])
        self.assertEqual(states[2]["R1"][1], [.2, .4])
        self.assertEqual(states[2]["R0"][1], [.2, .4])
        self.assertFalse(states[2]["R1-rinse"][0])
        with self.assertRaises(ValueError):
            et.apply_reduction(copy.deepcopy(config), "channel:R1")
        skipped = et.apply_reduction(copy.deepcopy(config), "channel:R3")
        with self.assertRaises(ValueError):
            et.validate_effective(config, skipped)


class Stage2bProjectionTests(unittest.TestCase):
    def test_inherited_cells_are_neither_timed_nor_charged(self):
        import encoder_transfer_runtime as runtime
        config, _, sources = build()
        rows = {}
        for unit in et.plan(config, sources, True):
            calls = {m: {et.ALPHA: dict(status="ok"), et.BETA: dict(status="ok")} for m in et.read_methods(config, unit)}
            rows[unit["id"]] = dict(unit, status="ok", distortion=dict(status="ok"), detections=calls, generation_seconds=1.)
        self.assertAlmostEqual(runtime.projected_seconds(config, sources, rows), 1.3 * 7200 + 900)
        # An inherited cell that is broken in the smoke does not block the stage-2b projection.
        unit = next(u for u in et.plan(config, sources, True) if u["channel"] == "D1")
        rows[unit["id"]]["status"] = "error"
        self.assertAlmostEqual(runtime.projected_seconds(config, sources, rows), 1.3 * 7200 + 900)


class Stage2bP5Tests(unittest.TestCase):
    def test_public_arrays_are_fixed_by_the_contract(self):
        import encoder_transfer_runtime as runtime
        config, _, _ = build()
        arrays = runtime.p5_perturbations(config["p5"])
        self.assertEqual(arrays.shape, (4, 3, 1024, 1024))
        self.assertAlmostEqual(float(arrays.std()), 2 / 255, places=5)
        broken = dict(config["p5"], noise_sha256="0" * 64)
        with self.assertRaises(ValueError):
            runtime.p5_perturbations(broken)


class Stage2bSeedingTests(unittest.TestCase):
    def journal(self, config, sources, folder):
        rows = []
        for unit in et.plan(config, sources):
            if tuple(cell(unit)) not in {tuple(c) for c in config["inherited_cells"]}:
                continue
            row = dict(unit, status="ok")
            if unit["channel"] == "clean":
                path = Path(folder) / "images" / (unit["id"].replace(":", "_") + ".png")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(unit["id"].encode())
                row["output"] = dict(path=str(path), sha256=et.digest(path))
            rows.append(row)
        (Path(folder) / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def test_seed_copies_the_journal_and_checks_inputs(self):
        import encoder_transfer_seed_2b as seeding
        config, _, sources = build()
        # The real stage-2b asset plan exists only after the server download; borrow stage 2a's.
        config["asset_plan_file"] = "research/encoder-transfer-20261019/stage2a-asset-plan.json"
        config["asset_plan_sha256"] = et.digest(STUDY / "stage2a-asset-plan.json")
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "stage2b-config.json"
            et.write(manifest, config)
            source, target = Path(tmp) / "stage2a-full", Path(tmp) / "stage2b-full"
            source.mkdir()
            self.journal(config, sources, source)
            receipt = seeding.seed(manifest, source, target)
            self.assertEqual(receipt["new_units"], 7200)
            self.assertEqual(receipt["checked_inputs"], 300)
            self.assertEqual((target / "rows.jsonl").read_bytes(), (source / "rows.jsonl").read_bytes())
            self.assertEqual(seeding.seed(manifest, source, target)["new_units"], 7200)  # idempotent
            victim = source / "images" / "clean_30_f5-r2_None_None.png"
            victim.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                seeding.seed(manifest, source, Path(tmp) / "other")


if __name__ == "__main__":
    unittest.main()

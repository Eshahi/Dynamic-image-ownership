"""CPU-only checks of amendment 1d (stage 2a): scopes, reductions, decision isolation, budget.

Written by Claude (Opus 5.5), 2026-10-23. No model, image or outcome is touched.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import encoder_transfer_test as et

STUDY = et.ROOT / "research/encoder-transfer-20261019"
CORE = ["f5-r2", "v5-r3", "wam", "vine-r"]


BUILT = (STUDY / "stage2a-config.json").exists()


def stage2a():
    return et.load_contract(STUDY / "stage2a-config.json")


@unittest.skipUnless(BUILT, "stage2a-config.json is built on the server once the new asset hashes exist")
class Stage2aContractTests(unittest.TestCase):
    def test_amendment_is_recorded_against_the_reviewed_freeze(self):
        config, _ = stage2a()
        self.assertEqual(et.contract_status(config), "user-amended-pre-outcome")
        self.assertEqual(config["amendment"]["base_config_sha256"], et.digest(STUDY / "frozen-config.json"))
        self.assertTrue(config["amendment"]["pre_outcome"])
        base = et.read(STUDY / "frozen-config.json")
        for key in ("n", "f5", "seeds", "message_seed", "wrong_message_seed", "implementation_seed", "profile_sha256", "sources_sha256"):
            self.assertEqual(config[key], base[key], key)
        self.assertEqual(config["primary"]["transfer_cut"], 45)
        self.assertEqual(config["primary"]["fail_below"], 30)
        self.assertEqual(config["decision_external_arms"], ["wam", "vine-r"])

    def test_schedule_scopes_and_counts(self):
        config, sources = stage2a()
        units = list(et.plan(config, sources))
        self.assertEqual(len(units), 60 * (7 + 3 * 5 + 3 * 7 + 6 + 5 + 5 + 5))
        self.assertEqual(len({u["id"] for u in units}), len(units))
        cells = {(u["arm"], u["channel"], u["strength"]) for u in units}
        self.assertEqual({c[1:] for c in cells if c[0] == "trustmark-q"}, {("clean", None), ("D1", None), ("R1", .2)})
        self.assertEqual({c[1:] for c in cells if c[0] == "pixelseal"}, {("clean", None), ("R1", .2)})
        self.assertEqual({(c[1], c[2]) for c in cells if c[0] == "unmarked"},
                         {("clean", None), ("R0", .2), ("R1", .2), ("D1", None), ("X1", None), ("X2", None), ("D3", None)})
        self.assertFalse(any(u["channel"] == "R1-rinse" or u["strength"] in (.1, .4) for u in units))
        self.assertEqual(len(list(et.plan(config, sources, True))), 2 * 64)

    def test_core_cells_keep_their_frozen_unit_identities(self):
        config, sources = stage2a()
        base, _ = et.load_contract(STUDY / "frozen-config.json")
        frozen = {u["id"] for u in et.plan(base, sources)}
        for unit in et.plan(config, sources):
            if unit["arm"] in ["unmarked", *CORE] and unit["channel"] != "D3":
                self.assertIn(unit["id"], frozen)

    def test_read_methods_follow_channel_scope(self):
        config, _ = stage2a()
        def unit(channel, arm="unmarked"):
            return dict(channel=channel, arm=arm)
        self.assertEqual(et.read_methods(config, unit("clean")), config["arms"])
        self.assertEqual(et.read_methods(config, unit("R0")), CORE)
        self.assertEqual(et.read_methods(config, unit("D1")), [*CORE, "trustmark-q"])
        self.assertEqual(et.read_methods(config, unit("R1")), config["arms"])
        self.assertEqual(et.read_methods(config, unit("D3")), CORE)
        self.assertEqual(et.read_methods(config, unit("R1", "pixelseal")), ["pixelseal"])


class ReductionTests(unittest.TestCase):
    @unittest.skipUnless(BUILT, "needs stage2a-config.json")
    def test_declared_order_only(self):
        import copy
        config, _ = stage2a()
        first = et.apply_reduction(copy.deepcopy(config), "channel:D3")
        et.validate_effective(config, first)
        both = et.apply_reduction(copy.deepcopy(first), "arm:trustmark-q")
        et.validate_effective(config, both)
        self.assertNotIn("trustmark-q", both["arms"])
        self.assertNotIn("trustmark-q", next(c for c in both["channels"] if c["id"] == "D1")["arms"])
        skipped = et.apply_reduction(copy.deepcopy(config), "arm:pixelseal")
        with self.assertRaises(ValueError):
            et.validate_effective(config, skipped)
        with self.assertRaises(ValueError):
            et.apply_reduction(copy.deepcopy(config), "arm:f5-r2")
        with self.assertRaises(ValueError):
            et.apply_reduction(copy.deepcopy(config), "channel:R1")

    def test_legacy_order_is_unchanged_for_the_frozen_core(self):
        import copy
        base = et.read(STUDY / "frozen-config.json")
        self.assertEqual(et.reduction_steps(base), ("R2", "D2", "strength_0.1"))
        reduced = copy.deepcopy(base)
        for step in et.reduction_steps(base):
            et.apply_reduction(reduced, step)
        et.validate_effective(base, reduced)
        self.assertFalse(next(c for c in reduced["channels"] if c["id"] == "R1-rinse")["enabled"])
        self.assertEqual(next(c for c in reduced["channels"] if c["id"] == "R1")["strengths"], [.2, .4])


class DecisionIsolationTests(unittest.TestCase):
    def config(self):
        return dict(n=60, arms=[*CORE, "trustmark-q", "pixelseal"], payload_bits={"wam": 32, "vine-r": 100, "trustmark-q": 61, "pixelseal": 256},
                    decision_external_arms=["wam", "vine-r"], holm_arms=["v5-r3", "wam", "vine-r"],
                    channels=[dict(id="R1", strengths=[.2], seeds=[12, 13, 14], arms=[*CORE, "trustmark-q", "pixelseal"])])

    def sources(self):
        return dict(sources=[dict(source_id=i) for i in range(60)], smoke=[dict(source_id=60), dict(source_id=61)])

    def test_extra_baselines_never_enter_the_route_or_holm_family(self):
        rows = {}
        for sid in range(60):
            for seed in (12, 13, 14):
                for arm in ("trustmark-q", "pixelseal"):
                    rows[et.unit_id(sid, "R1", .2, seed, arm)] = dict(status="generated", detections={arm: {et.ALPHA: dict(
                        status="ok", presence=dict(present=True, accuracy=1.), native=dict(present=True, exact_payload=True), raw={})}})
        result = et.analyze(self.config(), self.sources(), rows)
        self.assertEqual(result["decision"]["best_external"], 0)
        self.assertEqual(set(result["paired_primary_comparisons"]), {"v5-r3", "wam", "vine-r"})
        self.assertEqual(set(result["descriptive_comparisons"]), {"trustmark-q", "pixelseal"})
        for comparison in result["paired_primary_comparisons"].values():
            self.assertEqual(comparison["holm_family_size"], 3)
        self.assertEqual(result["cells"]["trustmark-q/R1/0.2/presence"]["positive_sources"], 60)
        operating = result["reporting"]["external_operating_points"]["trustmark-q/R1/0.2"]["source_operating_points"]
        self.assertEqual(operating["native_bch_detected"]["positive_sources"], 60)
        self.assertEqual(operating["native_exact_payload"]["positive_sources"], 60)
        self.assertIn("pixelseal/R1/0.2", result["reporting"]["external_operating_points"])


class BudgetTests(unittest.TestCase):
    def test_amended_ceiling_is_hours_or_dollars_whichever_first(self):
        import time
        from datetime import datetime, timezone
        import encoder_transfer_runtime as runtime
        start = datetime.fromtimestamp(time.time() - 60, timezone.utc).isoformat()
        cheap = runtime.Budget(start, .74, 1800, 35, 30)
        self.assertAlmostEqual(cheap.deadline - cheap.start, 35 * 3600, places=3)
        dear = runtime.Budget(start, 1.25, 1800, 35, 30)
        self.assertAlmostEqual(dear.deadline - dear.start, 24 * 3600, places=3)
        legacy = runtime.Budget(start, .74)
        self.assertAlmostEqual(legacy.deadline - legacy.start, 15 * 3600, places=3)


if __name__ == "__main__":
    unittest.main()

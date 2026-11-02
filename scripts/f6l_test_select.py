"""Lean F6 rules on synthetic journals in the runtime's own row format. Standard library only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f6l_common as lean_common
import f6l_select as select
import tifs_common as common

ALPHA, BETA = select.ALPHA, select.BETA
GOOD = dict(psnr_db=44.0, ssim_rgb=.98, lpips=.03)
BAD = dict(psnr_db=44.0, ssim_rgb=.98, lpips=.12)
CELLS = ("R0-0.2", "R1-0.1", "R1-0.2", "K3-0.2")


def endpoints(c=False, j=False, f=False):
    return dict(C=c, J=j, F=f, Q=j, H=False, D=False, S=c, A=c, D_and_F=False)


def row(method, item, *, c=False, j=False, f=False, score=3.0, wrong=None):
    calls = {ALPHA: dict(status="ok", endpoints=endpoints(c, j, f), raw=dict(semantic=dict(decoded_score=score, read=c))),
             BETA: dict(status="ok", endpoints=wrong or endpoints(), raw=dict(semantic=dict(decoded_score=2.0, read=False)))}
    return dict(id=f"det:{method}:{item}", status="ok", calls=calls)


class Build:
    """Writes detector, quality and producer journals into one phase folder."""
    def __init__(self, folder, sources, seeds):
        self.folder, self.sources, self.seeds = Path(folder), sources, seeds
        self.det = {}
        self.qual = {}
        self.native = {}

    def arm(self, name, c=None, scores=None, j=None, quality=GOOD, f=True, wrong=None):
        c, j, scores = c or {}, j or {}, scores or {}
        for sid_i, sid in enumerate(self.sources):
            item = f"clean:{sid}:{name}"
            self.det[f"det:{name}:{item}"] = row(name, item, c=True, j=True, f=f, score=15., wrong=wrong)
            self.qual[f"quality:{item}"] = dict(id=f"quality:{item}", status="ok", total=quality)
            for cell in CELLS:
                for seed in self.seeds:
                    item = f"native:{cell}:{sid}:{seed}:{name}"
                    positive = sid_i < c.get(cell, 0)
                    exact = sid_i < j.get(cell, 0)
                    self.det[f"det:{name}:{item}"] = row(name, item, c=positive, j=exact, score=scores.get(cell, 3.0), wrong=wrong)
                    self.native[item] = dict(id=item, status="ok", arm=name, seed=seed)

    def c0(self, event=False):
        for sid in self.sources:
            item = f"clean:{sid}:unmarked"
            self.det[f"det:f5-r2:{item}"] = row("f5-r2", item)
            for cell in CELLS:
                for seed in self.seeds:
                    item = f"native:{cell}:{sid}:{seed}:unmarked"
                    self.det[f"det:f5-r2:{item}"] = row("f5-r2", item, c=event)
                    self.native[item] = dict(id=item, status="ok", arm="unmarked", seed=seed)

    def data(self):
        return dict(detections=self.det, qualities=self.qual, sources=self.sources,
                    producers=dict(native=self.native, clean={}, threats={}, secondary={}))


def config_for(phase, previous=None):
    lean = lean_common.load_lean()
    base = common.load_json(lean_common.ROOT / lean["base_config"])
    return lean_common.stage_config(lean, base, phase, previous=previous)


class Stage1Rules(unittest.TestCase):
    def build(self):
        b = Build(tempfile.mkdtemp(), ["1", "2", "3", "4"], [0])
        b.c0()
        b.arm("f5-r2", scores={"R0-0.2": 13, "R1-0.1": 5, "R1-0.2": 4, "K3-0.2": 6})
        return b

    def decide(self, b, config=None):
        config = config or config_for("stage1")
        summaries = select.phase_summaries(config, b.data(), [a for a in config["arms"] if a in {k.split(":")[1] for k in b.det}])
        c0 = select.c0_events(b.data(), "f5-r2", list(CELLS), config["seeds"], b.sources)
        return select.decide_stage1(summaries, c0, config)

    def test_ranks_by_the_weakest_foreign_cell_and_keeps_two(self):
        b = self.build()
        b.arm("gen-46", scores={"R0-0.2": 12, "R1-0.1": 9, "R1-0.2": 8.0, "K3-0.2": 9})
        b.arm("noise-46", scores={"R0-0.2": 12, "R1-0.1": 10, "R1-0.2": 8.5, "K3-0.2": 9})
        b.arm("ren-38", scores={"R0-0.2": 12, "R1-0.1": 15, "R1-0.2": 5.0, "K3-0.2": 15})
        result = self.decide(b)
        self.assertEqual(result["status"], "ADVANCE")
        self.assertEqual(result["finalists"], ["noise-46", "gen-46"])

    def test_stops_when_no_arm_reaches_sdxl_and_k3(self):
        b = self.build()
        b.arm("gen-46", scores={"R0-0.2": 12, "R1-0.1": 8, "R1-0.2": 5, "K3-0.2": 9})
        result = self.decide(b)
        self.assertEqual(result["status"], "SCIENTIFIC_STOP")
        self.assertEqual(result["finalists"], [])

    def test_strict_quality_and_wrong_owner_reject(self):
        b = self.build()
        scores = {"R0-0.2": 12, "R1-0.1": 10, "R1-0.2": 9, "K3-0.2": 10}
        b.arm("gen-46", scores=scores, quality=BAD)
        b.arm("gen-42", scores=scores, wrong=endpoints(c=True))
        result = self.decide(b)
        self.assertEqual(result["status"], "SCIENTIFIC_STOP")
        self.assertIn("strict clean quality", result["rejected"]["gen-46"])
        self.assertIn("wrong-owner event", result["rejected"]["gen-42"])

    def test_home_family_is_protected(self):
        b = self.build()
        b.arm("noise-46", scores={"R0-0.2": 8, "R1-0.1": 12, "R1-0.2": 11, "K3-0.2": 12})
        result = self.decide(b)
        self.assertIn("home family below the decoded threshold", result["rejected"]["noise-46"])

    def test_missing_reads_are_incomplete_not_failed(self):
        b = self.build()
        b.arm("noise-46", scores={"R0-0.2": 12, "R1-0.1": 10, "R1-0.2": 9, "K3-0.2": 10})
        for sid in b.sources[:2]:
            del b.det[f"det:noise-46:native:R1-0.2:{sid}:0:noise-46"]
        result = self.decide(b)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("noise-46", result["incomplete"])

    def test_a_missing_arm_makes_a_stop_incomplete_not_scientific(self):
        b = self.build()
        result = self.decide_with_missing(b, dict({"noise-46": ["1"]}))
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("noise-46", result["incomplete"])

    def decide_with_missing(self, b, missing):
        config = config_for("stage1")
        summaries = select.phase_summaries(config, b.data(), ["f5-r2"])
        c0 = select.c0_events(b.data(), "f5-r2", list(CELLS), config["seeds"], b.sources)
        return select.decide_stage1(summaries, c0, config, missing)

    def test_c0_event_stops_for_review(self):
        b = self.build()
        b.c0(event=True)
        b.arm("noise-46", scores={"R0-0.2": 12, "R1-0.1": 10, "R1-0.2": 9, "K3-0.2": 10})
        self.assertEqual(self.decide(b)["status"], "SCIENTIFIC_STOP")


class Stage2Rules(unittest.TestCase):
    def setUp(self):
        self.sources = [str(i) for i in range(12)]
        self.config = config_for("stage2", dict(status="ADVANCE", finalists=["noise-46", "ren-38"], digest="x"))

    def decide(self, b):
        names = [a for a in self.config["arms"] if a in {k.split(":")[1] for k in b.det}]
        summaries = select.phase_summaries(self.config, b.data(), names)
        return select.decide_stage2(summaries, select.c0_events(b.data(), "f5-r2", list(CELLS), self.config["seeds"], b.sources), self.config)

    def build(self):
        b = Build(tempfile.mkdtemp(), self.sources, [0, 1, 2])
        b.c0()
        b.arm("f5-r2", c={"R0-0.2": 11, "R1-0.1": 1, "R1-0.2": 0, "K3-0.2": 3})
        return b

    def test_controls_are_matched_to_each_finalist(self):
        self.assertIn("f5b-46", self.config["arms"])
        self.assertNotIn("f5b-52", self.config["arms"])
        self.assertEqual(self.config["seeds"], [0, 1, 2])

    def test_fixed_ranking_uses_c_only(self):
        b = self.build()
        b.arm("noise-46", c={"R0-0.2": 11, "R1-0.1": 10, "R1-0.2": 5, "K3-0.2": 9}, j={"R0-0.2": 0})
        b.arm("ren-38", c={"R0-0.2": 11, "R1-0.1": 9, "R1-0.2": 4, "K3-0.2": 9}, j={"R0-0.2": 12, "R1-0.1": 12, "R1-0.2": 12, "K3-0.2": 12})
        result = self.decide(b)
        self.assertEqual(result["status"], "ADVANCE")
        self.assertEqual(result["winner"], "noise-46")
        self.assertEqual(result["arms"]["ren-38"]["cells"]["R1-0.1"]["j_lower"], 12)

    def test_winner_below_core_bar_stops_without_a_runner_up(self):
        b = self.build()
        b.arm("noise-46", c={"R0-0.2": 11, "R1-0.1": 8, "R1-0.2": 8, "K3-0.2": 12})
        b.arm("ren-38", c={"R0-0.2": 11, "R1-0.1": 7, "R1-0.2": 1, "K3-0.2": 12})
        result = self.decide(b)
        self.assertEqual(result["status"], "SCIENTIFIC_STOP")
        self.assertIsNone(result["winner"])

    def test_home_loss_stops(self):
        b = self.build()
        b.arm("noise-46", c={"R0-0.2": 9, "R1-0.1": 10, "R1-0.2": 8, "K3-0.2": 10})
        result = self.decide(b)
        self.assertEqual(result["status"], "SCIENTIFIC_STOP")

    def test_missing_seeds_that_decide_the_bar_are_incomplete(self):
        b = self.build()
        b.arm("noise-46", c={"R0-0.2": 11, "R1-0.1": 9, "R1-0.2": 8, "K3-0.2": 10})
        for seed in (0, 1):
            del b.det[f"det:noise-46:native:R1-0.1:0:{seed}:noise-46"]
        result = self.decide(b)
        self.assertEqual(result["status"], "INCOMPLETE")


class Stage3Rules(unittest.TestCase):
    def setUp(self):
        self.sources = [str(i) for i in range(16)]
        self.config = config_for("stage3", dict(status="ADVANCE", winner="noise-46", digest="x"))
        self.pairs = [dict(donor=str(i), target=str(100 + i)) for i in range(16)]

    def build(self, winner=None, control=None, j=None, quality=GOOD):
        b = Build(tempfile.mkdtemp(), self.sources, [0, 1, 2])
        b.c0()
        b.arm("f5-r2", c={"R0-0.2": 15, "R1-0.1": 1, "R1-0.2": 0, "K3-0.2": 5})
        b.arm("f5b-46", c=control or {"R0-0.2": 15, "R1-0.1": 6, "R1-0.2": 2, "K3-0.2": 8})
        b.arm("noise-46", c=winner or {"R0-0.2": 15, "R1-0.1": 14, "R1-0.2": 12, "K3-0.2": 13}, j=j, quality=quality)
        for pair in self.pairs:
            for condition in select.CONDITIONS:
                kind = "T5" if condition == "unmodified" else "T4"
                item = f"threat:{kind}:{pair['donor']}:{pair['target']}:noise-46:{condition}"
                b.det[f"det:noise-46:{item}"] = row("noise-46", item)
                b.qual["quality:" + item] = dict(id="quality:" + item, status="ok", recipient_eligible=True)
        return b

    def verdict(self, b):
        data = b.data()
        config = copy.deepcopy(self.config)
        summaries = select.phase_summaries(config, data, ["f5-r2", "f5b-46", "noise-46"])
        threats = select.threat_summary(data, "noise-46", "noise-46", self.pairs)
        c0 = select.c0_events(data, "f5-r2", list(CELLS), config["seeds"], b.sources)
        return select.verdict_stage3(summaries, threats, c0, config)

    def test_full_go_needs_no_j(self):
        result = self.verdict(self.build(j={}))
        self.assertEqual(result["status"], "FULL_GO")
        self.assertEqual(result["arms"]["noise-46"]["cells"]["R1-0.1"]["j_lower"], 0)
        self.assertFalse(any("J" in g["name"].split() for g in result["gates"]))

    def test_core_go_when_only_sdxl_02_is_short(self):
        result = self.verdict(self.build(winner={"R0-0.2": 15, "R1-0.1": 14, "R1-0.2": 7, "K3-0.2": 13}))
        self.assertEqual(result["status"], "CORE_GO")

    def test_kill_when_core_cell_is_short(self):
        result = self.verdict(self.build(winner={"R0-0.2": 15, "R1-0.1": 11, "R1-0.2": 12, "K3-0.2": 13}))
        self.assertEqual(result["status"], "SCIENTIFIC_KILL")

    def test_gain_over_the_budget_control_is_required(self):
        result = self.verdict(self.build(control={"R0-0.2": 15, "R1-0.1": 12, "R1-0.2": 2, "K3-0.2": 8}))
        self.assertEqual(result["status"], "SCIENTIFIC_KILL")
        self.assertIn("gain over matched control R1-0.1", [g["name"] for g in result["gates"] if g["status"] == "fail"])

    def test_one_t4_c_event_kills(self):
        b = self.build()
        item = "threat:T4:0:100:noise-46:patch256"
        b.det[f"det:noise-46:{item}"] = row("noise-46", item, c=True)
        result = self.verdict(b)
        self.assertEqual(result["status"], "SCIENTIFIC_KILL")
        self.assertEqual(result["threats"]["events"], [item])

    def test_t4_c_event_on_ineligible_quality_is_not_an_event(self):
        b = self.build()
        item = "threat:T4:0:100:noise-46:patch256"
        b.det[f"det:noise-46:{item}"] = row("noise-46", item, c=True)
        b.qual["quality:" + item]["recipient_eligible"] = False
        self.assertEqual(self.verdict(b)["status"], "FULL_GO")

    def test_missing_threat_read_is_incomplete(self):
        b = self.build()
        del b.det["det:noise-46:threat:T5:0:100:noise-46:unmodified"]
        self.assertEqual(self.verdict(b)["status"], "INCOMPLETE")

    def test_strict_quality_fails_on_any_source(self):
        result = self.verdict(self.build(quality=BAD))
        self.assertEqual(result["status"], "SCIENTIFIC_KILL")

    def test_resource_stop_never_becomes_a_result(self):
        b = self.build()
        del b.det["det:noise-46:native:R1-0.1:0:0:noise-46"]
        del b.det["det:noise-46:native:R1-0.1:0:1:noise-46"]
        data = b.data()
        summaries = select.phase_summaries(self.config, data, ["f5-r2", "f5b-46", "noise-46"])
        threats = select.threat_summary(data, "noise-46", "noise-46", self.pairs)
        c0 = select.c0_events(data, "f5-r2", list(CELLS), self.config["seeds"], b.sources)
        result = select.verdict_stage3(summaries, threats, c0, self.config, resource_stop=True)
        self.assertEqual(result["status"], "RESOURCE_STOP")


class CommonRules(unittest.TestCase):
    def setUp(self):
        self.lean = lean_common.load_lean()

    def test_receipt_records_c_as_primary_before_outputs(self):
        receipt = common.load_json(lean_common.ROOT / self.lean["user_choice"])
        self.assertEqual(receipt["primary_endpoint"], "C")
        self.assertTrue(receipt["before_server_outputs"])
        self.assertFalse(receipt["run_authorized"])
        self.assertEqual(receipt["planned_ceiling"]["max_instance_hours"], self.lean["caps"]["max_instance_hours"])
        self.assertEqual(receipt["planned_ceiling"]["max_usd"], self.lean["caps"]["max_usd"])

    def test_dollar_cap_limits_hours_at_a_higher_price(self):
        self.assertEqual(lean_common.hours_cap(self.lean, .5512), 18.7 / .5512)
        self.assertEqual(lean_common.hours_cap(self.lean, .4), 34)
        self.assertLess(lean_common.hours_cap(self.lean, .9), 21)
        for price in (0, -1, 1.5, None, True):
            with self.assertRaises(ValueError):
                lean_common.hours_cap(self.lean, price)

    def test_stage1_has_twelve_marked_arms_cheap_first(self):
        arms = self.lean["phases"]["stage1"]["arms"]
        self.assertEqual(len(arms), 13)
        self.assertEqual(arms[:2], ["unmarked", "f5-r2"])
        order = {"f5-budget": 0, "f6-generic": 1, "f6-noise": 2, "f6-x0": 3}
        variants = [order[self.lean["arms"][a]["variant"]] for a in arms[2:]]
        self.assertEqual(variants, sorted(variants))

    def test_reader_and_bar_are_untouched_by_the_lean_config(self):
        base = common.load_json(lean_common.ROOT / self.lean["base_config"])
        config = lean_common.stage_config(self.lean, base, "stage1")
        self.assertEqual(config["writer"]["target_margin"], 4)
        self.assertEqual(config["writer"]["band"], [4, 32])
        self.assertEqual(self.lean["gates"]["stage3"]["c_min"], 12)
        self.assertEqual(config["cells"], base["cells"])
        self.assertEqual(config["owners"], base["owners"])

    def test_control_matches_budget_and_render(self):
        self.assertEqual(lean_common.control_arm("noise-46-ren38", self.lean["arms"]["noise-46-ren38"])[0], "f5b-46-ren38")
        self.assertEqual(lean_common.control_arm("gen-38", self.lean["arms"]["gen-38"])[1]["robust_psnr_db"], 38)
        self.assertEqual(lean_common.control_arm("ren-38", self.lean["arms"]["ren-38"]), (None, None))

    def test_stage2_needs_the_previous_decision(self):
        base = common.load_json(lean_common.ROOT / self.lean["base_config"])
        with self.assertRaises(ValueError):
            lean_common.stage_config(self.lean, base, "stage2")

    def test_partitions_do_not_overlap(self):
        tune = dict(tune_sources=[dict(source_id=i) for i in range(16)])
        one = lean_common.partition_sources(self.lean, "stage1", tune)
        two = lean_common.partition_sources(self.lean, "stage2", tune)
        self.assertEqual(len(one), 4)
        self.assertEqual(len(two), 12)
        self.assertFalse({r["source_id"] for r in one} & {r["source_id"] for r in two})

    def test_policy_rules(self):
        rules = self.lean["probe_rules"]
        def measure(cos=.3, ratio=.9, cosine=.99, fits=True, time_ratio=.9, free=10**10):
            return {"f6-noise": dict(pairwise_cos_median=cos), "f6-x0": dict(pairwise_cos_median=cos),
                    "bf16": dict(time_ratio=ratio, gradient_cos_median=cosine),
                    "no_checkpoint": dict(fits=fits, time_ratio=time_ratio, free_bytes_at_peak=free)}
        policy = lean_common.decide_policy(rules, [measure()])
        self.assertFalse(policy["f6-noise"]["momentum"])
        self.assertFalse(policy["bf16"])
        self.assertTrue(policy["checkpoint"])
        self.assertTrue(lean_common.decide_policy(rules, [measure(cos=.05)])["f6-x0"]["momentum"])
        self.assertTrue(lean_common.decide_policy(rules, [measure(ratio=.6)])["bf16"])
        self.assertFalse(lean_common.decide_policy(rules, [measure(ratio=.6, cosine=.8)])["bf16"])
        self.assertFalse(lean_common.decide_policy(rules, [measure(time_ratio=.7)])["checkpoint"])
        self.assertTrue(lean_common.decide_policy(rules, [measure(time_ratio=.7, fits=False)])["checkpoint"])
        self.assertTrue(lean_common.decide_policy(rules, [measure(time_ratio=.7, free=10**9)])["checkpoint"])
        with self.assertRaises(ValueError):
            lean_common.decide_policy(rules, [{}])

    def test_clean_gate_removes_only_lean_arms(self):
        folder = Path(tempfile.mkdtemp())
        config = config_for("stage1")
        common.atomic_json(folder / "prepared.json", dict(donors=["1", "2"]))
        with (folder / "quality-0-of-1.jsonl").open("w", encoding="utf-8") as stream:
            for arm in config["arms"]:
                for sid in ("1", "2"):
                    uid = f"quality:clean:{sid}:{arm}"
                    good = not (arm == "gen-38" and sid == "2")
                    if arm == "x0-46" and sid == "2":
                        continue
                    stream.write(json.dumps(dict(id=uid, status="ok", total=GOOD if good else BAD)) + "\n")
        report = select.clean_gate(folder, config)
        self.assertEqual(sorted(report["removed"]), ["gen-38"])
        self.assertEqual(report["missing"], dict({"x0-46": ["2"]}))
        self.assertNotIn("x0-46", report["active"])
        self.assertIn("f5-r2", report["active"])
        self.assertEqual(lean_common.active_arms(folder, config), report["active"])

    def test_every_lean_arm_has_a_reader_time_estimate(self):
        config = config_for("stage1")
        estimates = config["budget"]["unit_estimates_seconds"]
        for arm in config["arms"]:
            if config["lean"]["arms"][arm]["kind"] == "lean":
                self.assertEqual(estimates["detect_" + arm], estimates["detect_f5-r2"])

    def test_offload_only_on_small_cards(self):
        self.assertTrue(lean_common.needs_offload(24564 * 1024 ** 2))
        self.assertFalse(lean_common.needs_offload(49140 * 1024 ** 2))

    def test_disk_floor(self):
        self.assertFalse(lean_common.disk_ok(self.lean, 9 * 10 ** 9))
        self.assertTrue(lean_common.disk_ok(self.lean, 10 ** 10))

    def test_only_combined_threat_reads_are_paid_for(self):
        self.assertEqual(config_for("stage1")["threats"]["read_modes"], ["combined"])


if __name__ == "__main__":
    unittest.main()

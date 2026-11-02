"""F7 endpoint and verdict rules. Standard library only."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import f7_dual
import f6l_select as select
from f6l_test_select import Build, config_for, endpoints as basic_endpoints, row, GOOD, BAD, CELLS

PAYLOAD = dict(q="0000abcd", h="0000beef")


def carrier(score, read=True, match=True, code="0000abcd", outcome="none"):
    return dict(semantic=dict(read=read, found=read, content_match=match, decoded_code=code, decoded_score=score),
                instance=dict(read=False, found=False, decoded_code="00000000"), outcome=outcome)


class Endpoints(unittest.TestCase):
    def test_threshold_is_the_frozen_bound(self):
        from scripts import revised_watermark_v5 as v5
        self.assertAlmostEqual(f7_dual.check_threshold(v5), 8.341671, places=5)

    def test_either_carrier_reads_at_the_union_threshold(self):
        raw = dict(f5=carrier(5.0, read=False, match=False), v5=carrier(9.0), combined=dict(decoded_score=9.5, content_match=True))
        e = f7_dual.endpoints(raw, PAYLOAD)
        self.assertTrue(e["C"])
        self.assertFalse(e["C_f5"])
        self.assertTrue(e["C_v5"])
        self.assertTrue(e["J"])

    def test_a_read_between_the_two_thresholds_does_not_count(self):
        raw = dict(f5=carrier(8.30), v5=carrier(4.0, read=False, match=False), combined=dict(decoded_score=8.0))
        e = f7_dual.endpoints(raw, PAYLOAD)
        self.assertTrue(e["C_f5_alpha"])
        self.assertFalse(e["C"])

    def test_content_mismatch_blocks_a_strong_read(self):
        raw = dict(f5=carrier(12.0, match=False), v5=carrier(12.0, match=False), combined={})
        self.assertFalse(f7_dual.endpoints(raw, PAYLOAD)["C"])

    def test_missing_carrier_stays_unknown_unless_the_other_reads(self):
        self.assertIsNone(f7_dual.endpoints(dict(f5=None, v5=carrier(4.0, read=False, match=False)), PAYLOAD)["C"])
        self.assertTrue(f7_dual.endpoints(dict(f5=None, v5=carrier(9.0)), PAYLOAD)["C"])

    def test_wrong_code_is_c_but_not_j(self):
        e = f7_dual.endpoints(dict(f5=carrier(12.0, code="ffff0000"), v5=carrier(3.0, read=False, match=False)), PAYLOAD)
        self.assertTrue(e["C"])
        self.assertFalse(e["J"])

    def test_second_tier_counts_either_reader(self):
        weak, strong = carrier(5.0, read=False, match=False), carrier(12.0, outcome="both_match")
        e = f7_dual.endpoints(dict(f5=weak, v5=strong), PAYLOAD)
        self.assertTrue(e["F"])
        e = f7_dual.endpoints(dict(f5=carrier(5.0, read=False, match=False), v5=carrier(4.0, read=False, match=False)), PAYLOAD)
        self.assertFalse(e["F"])
        self.assertFalse(e["D_and_F"])

    def test_summary_takes_the_stronger_carrier(self):
        raw = dict(f5=carrier(5.0), v5=carrier(11.0, outcome="none"))
        raw["f5"]["outcome"] = "both_match"
        summary = f7_dual.summary_raw(raw)
        self.assertEqual(summary["semantic"]["decoded_score"], 11.0)
        self.assertEqual(summary["outcome"], "both_match")


class Verdict(unittest.TestCase):
    def setUp(self):
        self.config = config_for("f7")
        self.sources = [str(i) for i in range(16)]
        self.pairs = [dict(donor=str(i), target=str(100 + i)) for i in range(16)]

    def build(self, f7=None, quality=GOOD, f7_c0_event=False):
        b = Build(Path("."), self.sources, [0, 1, 2])
        CELLS5 = (*CELLS, "R0-0.4")
        def arm(name, counts):
            for i, sid in enumerate(self.sources):
                item = f"clean:{sid}:{name}"
                b.det[f"det:{name}:{item}"] = row(name, item, c=True, f=True, score=15.)
                b.qual[f"quality:{item}"] = dict(id=f"quality:{item}", status="ok", total=quality if name == "f7" else GOOD)
                for cell in CELLS5:
                    for seed in (0, 1, 2):
                        item = f"native:{cell}:{sid}:{seed}:{name}"
                        b.det[f"det:{name}:{item}"] = row(name, item, c=i < counts.get(cell, 0))
            for method in (name,):
                for sid in self.sources:
                    for item in [f"clean:{sid}:unmarked"] + [f"native:{c}:{sid}:{s}:unmarked" for c in CELLS5 for s in (0, 1, 2)]:
                        b.det[f"det:{method}:{item}"] = row(method, item, c=f7_c0_event and method == "f7")
        arm("f5-r2", {"R0-0.2": 15, "R0-0.4": 11, "R1-0.1": 0, "R1-0.2": 0, "K3-0.2": 2})
        arm("v5-r3", {"R0-0.2": 7, "R0-0.4": 1, "R1-0.1": 13, "R1-0.2": 3, "K3-0.2": 15})
        arm("f7", f7 or {"R0-0.2": 14, "R0-0.4": 10, "R1-0.1": 12, "R1-0.2": 2, "K3-0.2": 14})
        for pair in self.pairs:
            for condition in select.CONDITIONS:
                kind = "T5" if condition == "unmodified" else "T4"
                item = f"threat:{kind}:{pair['donor']}:{pair['target']}:f7:{condition}"
                b.det[f"det:f7:{item}"] = row("f7", item)
                b.qual["quality:" + item] = dict(id="quality:" + item, status="ok", recipient_eligible=True)
        return b

    def verdict(self, b):
        data = b.data()
        cells = [c["id"] for c in self.config["cells"]]
        summaries = select.phase_summaries(self.config, data, ["f5-r2", "v5-r3", "f7"])
        threats = select.threat_summary(data, "f7", "f7", self.pairs)
        c0 = select.c0_events(data, "f7", cells, self.config["seeds"], b.sources)
        return select.verdict_f7(summaries, threats, c0, self.config, data)

    def test_go_when_core_cells_hold(self):
        self.assertEqual(self.verdict(self.build())["status"], "GO")

    def test_sdxl_02_and_sd15_04_are_reported_only(self):
        result = self.verdict(self.build(f7={"R0-0.2": 14, "R0-0.4": 0, "R1-0.1": 12, "R1-0.2": 0, "K3-0.2": 14}))
        self.assertEqual(result["status"], "GO")

    def test_kill_when_a_core_cell_is_short(self):
        self.assertEqual(self.verdict(self.build(f7={"R0-0.2": 14, "R1-0.1": 11, "K3-0.2": 14}))["status"], "SCIENTIFIC_KILL")

    def test_kill_when_f7_loses_three_to_the_better_mark(self):
        result = self.verdict(self.build(f7={"R0-0.2": 12, "R1-0.1": 13, "K3-0.2": 14}))
        self.assertEqual(result["status"], "SCIENTIFIC_KILL")
        self.assertIn("loss to the better single mark R0-0.2, negated", [g["name"] for g in result["gates"] if g["status"] == "fail"])

    def test_c0_event_under_the_f7_reader_kills(self):
        self.assertEqual(self.verdict(self.build(f7_c0_event=True))["status"], "SCIENTIFIC_KILL")

    def test_quality_failure_kills(self):
        self.assertEqual(self.verdict(self.build(quality=BAD))["status"], "SCIENTIFIC_KILL")


if __name__ == "__main__":
    unittest.main()

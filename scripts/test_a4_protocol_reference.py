"""Synthetic A4 contract checks only; no images, models, datasets, or results."""
import unittest

from a4_protocol_reference import (
    Candidate, DOMAINS, GRID, both_match, calibrate, owner_and_seed,
)


class A4ProtocolReferenceTests(unittest.TestCase):
    def setUp(self):
        self.sources = tuple((domain, f"{domain}:synthetic-1") for domain in DOMAINS)
        self.positive = (Candidate(0.5, (0.5,)),)
        self.negative = (Candidate(0.2, (0.2,)),)
        self.observations = {
            (uid, condition): self.positive if condition == "C1" else self.negative
            for _, uid in self.sources
            for condition in ("C1", "C0-source", "C0-reconstruction", "C2")
        }

    def test_grid_and_schedule_vector(self):
        self.assertEqual((len(GRID), GRID[0], GRID[-1]), (101, -1.0, 1.0))
        self.assertEqual(len(set(GRID)), 101)
        self.assertEqual(owner_and_seed("coco:000000000001"),
                         ("thesis:owner:09", "thesis:owner:10", 4369173439443558334))

    def test_schedule_rejects_noncanonical_ids(self):
        for uid in ("", "e\u0301", None):
            with self.subTest(uid=uid), self.assertRaises(ValueError):
                owner_and_seed(uid)

    def test_common_q_and_strict_thresholds(self):
        self.assertFalse(both_match((Candidate(.9, (.1,)), Candidate(.1, (.9,))), .5, .5))
        self.assertFalse(both_match((Candidate(.5, (.5,)),), .5, .4))
        self.assertFalse(both_match((Candidate(.5, (.5,)),), .4, .5))
        self.assertTrue(both_match((Candidate(.5, (None, .6)),), .4, .5))
        self.assertFalse(both_match((Candidate(None, (.9,)),), .1, .1))

    def test_calibration_maximizes_macro_tpr_then_stricter_thresholds(self):
        result = calibrate(self.sources, self.observations)
        self.assertIsNotNone(result)
        self.assertEqual((result.semantic_index, result.instance_index), (74, 74))
        self.assertEqual((result.tau_s, result.tau_i), (.48, .48))
        self.assertEqual(result.positive_counts, {domain: 1 for domain in DOMAINS})
        self.assertTrue(all(value == 0 for cells in result.negative_counts.values()
                            for value in cells.values()))

    def test_missing_negative_is_adverse_not_removed(self):
        del self.observations[(self.sources[0][1], "C2")]
        self.assertIsNone(calibrate(self.sources, self.observations))

    def test_missing_positive_is_miss_not_removed(self):
        del self.observations[(self.sources[0][1], "C1")]
        result = calibrate(self.sources, self.observations)
        self.assertIsNotNone(result)
        self.assertEqual(result.planned_counts, {domain: 1 for domain in DOMAINS})
        self.assertEqual(result.positive_counts[self.sources[0][0]], 0)

    def test_valid_empty_candidates_are_not_failures(self):
        for _, uid in self.sources:
            self.observations[(uid, "C2")] = ()
        result = calibrate(self.sources, self.observations)
        self.assertIsNotNone(result)
        self.assertTrue(all(result.negative_counts[domain]["C2"] == 0 for domain in DOMAINS))

    def test_reject_duplicate_sources_and_bad_scores(self):
        with self.assertRaises(ValueError):
            calibrate(self.sources + (self.sources[0],), self.observations)
        self.observations[(self.sources[0][1], "C1")] = (Candidate(float("nan"), (.5,)),)
        with self.assertRaises(ValueError):
            calibrate(self.sources, self.observations)

    def test_veto_does_not_hide_malformed_negative_output(self):
        uid = self.sources[0][1]
        for malformed in (float("nan"), "bad", 10 ** 1000):
            with self.subTest(malformed=malformed):
                self.observations[(uid, "C2")] = (Candidate(None, (malformed,)),)
                with self.assertRaises(ValueError):
                    calibrate(self.sources, self.observations)
        with self.assertRaises(ValueError):
            both_match((Candidate(None, (float("nan"),)),), .48, .48)


if __name__ == "__main__":
    unittest.main()

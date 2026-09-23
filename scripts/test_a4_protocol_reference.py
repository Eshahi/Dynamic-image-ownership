"""Synthetic A4 contract checks only; no images, models, datasets, or results."""
import unittest

from a4_protocol_reference import (
    Candidate, DOMAINS, GRID, both_match, calibrate, exact_one_sided_bound,
    owner_and_seed, primary_joint_objective,
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

    def test_exact_bounds_match_boundary_formulas_and_small_cells(self):
        self.assertEqual(exact_one_sided_bound(0, 300, lower=True), 0)
        self.assertEqual(exact_one_sided_bound(300, 300, lower=False), 1)
        self.assertAlmostEqual(exact_one_sided_bound(0, 300, lower=False),
                               1 - .05 ** (1 / 300), places=12)
        self.assertAlmostEqual(exact_one_sided_bound(300, 300, lower=True),
                               .05 ** (1 / 300), places=12)
        # At n=2, x=1 both bounds have closed-form solutions.
        self.assertAlmostEqual(exact_one_sided_bound(1, 2, lower=True),
                               1 - .95 ** .5, places=12)
        self.assertAlmostEqual(exact_one_sided_bound(1, 2, lower=False),
                               .95 ** .5, places=12)
        self.assertGreater(exact_one_sided_bound(0, 298, lower=False), .01)
        self.assertLessEqual(exact_one_sided_bound(0, 299, lower=False), .01)
        self.assertGreater(exact_one_sided_bound(1, 300, lower=False), .01)
        for x, n in ((-1, 3), (4, 3), (0, 0), (True, 3), (0, 3.0)):
            with self.subTest(x=x, n=n), self.assertRaises(ValueError):
                exact_one_sided_bound(x, n, lower=False)

    def test_joint_objective_requires_every_domain_and_negative_cell(self):
        planned = {domain: 300 for domain in DOMAINS}
        positives = {domain: 300 for domain in DOMAINS}
        negatives = {domain: {condition: 0 for condition in
                             ("C0-source", "C0-reconstruction", "C2")}
                     for domain in DOMAINS}
        passed, bounds = primary_joint_objective(planned, positives, negatives)
        self.assertTrue(passed)
        self.assertEqual(len(bounds), 3)
        negatives["DIV2K"]["C2"] = 1
        self.assertFalse(primary_joint_objective(planned, positives, negatives)[0])
        negatives["DIV2K"]["C2"] = 0
        positives["MS-COCO"] = 0
        self.assertFalse(primary_joint_objective(planned, positives, negatives)[0])
        del negatives["DIV2K"]["C2"]
        with self.assertRaises(ValueError):
            primary_joint_objective(planned, positives, negatives)


if __name__ == "__main__":
    unittest.main()

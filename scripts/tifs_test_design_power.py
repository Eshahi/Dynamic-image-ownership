"""Pure-logic tests, executable using the approved stdlib interpreter with -I."""

import importlib.util
import math
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "tifs_design_power", Path(__file__).with_name("tifs_design_power.py"))
power = importlib.util.module_from_spec(spec)
spec.loader.exec_module(power)


class PlanningTests(unittest.TestCase):
    def test_pmf_and_degenerate_cases(self):
        for n in (0, 3, 80, 200):
            for p in (0, 0.05, 0.5, 0.9, 1):
                self.assertAlmostEqual(sum(power.binomial_pmf(n, p)), 1, places=12)
        self.assertEqual(power.mcnemar_power(120, 0, 0), 0)
        self.assertEqual(power.binomial_power(120, 1), 1)

    def test_cutoff_is_smallest_valid_inclusive_tail(self):
        for n in (80, 120, 160, 200):
            k = power.critical_successes(n, 0.7)
            pmf = power.binomial_pmf(n, 0.7)
            self.assertLessEqual(math.fsum(pmf[k:]), power.ALPHA)
            self.assertGreater(math.fsum(pmf[k - 1:]), power.ALPHA)
            self.assertLessEqual(power.binomial_power(n, 0.7), power.ALPHA)
            self.assertLessEqual(power.mcnemar_power(n, 0.15, 0.15), power.ALPHA)

    def test_mcnemar_small_case_independent_enumeration(self):
        # At alpha=.25 and n=3 only (X,Y)=(2,0),(3,0) reject.
        # The other source, if any, must be concordant.
        expected = 3 * 0.3 ** 2 * 0.6 + 0.3 ** 3
        self.assertAlmostEqual(power.mcnemar_power(3, 0.3, 0.1, 0.25), expected)

    def test_direction_and_planning_grid_monotonicity(self):
        for n in (80, 120, 160, 200):
            a, b, c = [power.binomial_power(n, p) for p in (0.8, 0.85, 0.9)]
            self.assertLess(a, b)
            self.assertLess(b, c)
            self.assertGreater(power.mcnemar_power(n, 0.25, 0.05),
                               power.mcnemar_power(n, 0.20, 0.10))
            self.assertGreater(power.mcnemar_power(n, 0.35, 0.05),
                               power.mcnemar_power(n, 0.25, 0.05))
        # This prespecified grid increases; exact tests can have local sawtooth power.
        rows = power.planning_table()
        for left, right in zip(rows, rows[1:]):
            for key in left["absolute"]:
                self.assertLess(left["absolute"][key], right["absolute"][key])
            for key in left["paired"]:
                self.assertLess(left["paired"][key], right["paired"][key])

    def test_specificity_sample_sizes_are_minimal(self):
        for target in (0.01, 0.001, 0.0001):
            n = power.zero_event_sample_size(target)
            self.assertLessEqual(power.zero_event_upper(n), target)
            self.assertGreater(power.zero_event_upper(n - 1), target)

    def test_invalid_probabilities(self):
        with self.assertRaises(ValueError):
            power.mcnemar_power(10, 0.8, 0.8)
        with self.assertRaises(ValueError):
            power.binomial_pmf(-1, 0.5)


if __name__ == "__main__":
    unittest.main()

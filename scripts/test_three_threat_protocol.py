"""Ordinary synthetic tests only: no study pixels/models/detection/dispatch."""
import copy
from collections import Counter
import unittest

from three_threat_protocol import (EXPANDED_IDS, ORIGINAL_IDS, REGEN_SETTINGS,
                                  binding_distance, center_patch, inventory, residual_transfer)


class ProtocolTests(unittest.TestCase):
    def test_complete_fixed_inventory(self):
        rows = inventory()
        self.assertEqual(Counter(row["axis"] for row in rows), {"clean": 24, "T4": 120, "T3": 120, "T5": 66})
        self.assertEqual(len(rows), len({row["id"] for row in rows}))
        self.assertEqual(Counter(row["arm"] for row in rows if row["axis"] == "T4"),
                         {"public_patch": 40, "unmarked_patch_sham": 40, "clean_donor_residual": 40})
        transfers = [row for row in rows if row["axis"] == "T4"]
        self.assertTrue(all(row["donor_id"] != row["recipient_id"] and row["recipient_control"] == "C0" and row["query_budget"] == 0 for row in transfers))
        self.assertEqual(len({(row["donor_id"], row["recipient_id"]) for row in transfers}), 20)
        self.assertEqual({row["recipient_id"] for row in transfers}, set(ORIGINAL_IDS))

    def test_matched_regeneration(self):
        rows = [row for row in inventory() if row["axis"] == "T3"]
        paired = Counter((row["source_id"], row["strength"], row["seed"]) for row in rows)
        self.assertEqual(len(paired), 60)
        self.assertEqual(set(paired.values()), {2})
        self.assertEqual(Counter(row["control"] for row in rows), {"C0": 60, "C1": 60})
        self.assertEqual({row["source_id"] for row in rows}, set(ORIGINAL_IDS))
        self.assertTrue(REGEN_SETTINGS["safety_checker_required"])
        self.assertEqual(REGEN_SETTINGS["guidance_scale"], 1.0)

    def test_expanded_pairs_and_clean_only(self):
        rows = inventory()
        self.assertEqual({row["source_id"] for row in rows if row["axis"] == "clean"}, set(EXPANDED_IDS))
        pairs = [row for row in rows if row["axis"] == "T5"]
        self.assertEqual(len(pairs), 66)
        self.assertTrue(all(row["left"] < row["right"] for row in pairs))

    def test_central_exact_copy_immutable(self):
        recipient = [[[1, 2, 3] for _ in range(4)] for _ in range(4)]
        donor = [[[4, 5, 6] for _ in range(4)] for _ in range(4)]
        originals = copy.deepcopy((recipient, donor))
        observed = center_patch(recipient, donor, 2)
        for y in range(4):
            for x in range(4):
                self.assertEqual(observed[y][x], [4, 5, 6] if y in (1, 2) and x in (1, 2) else [1, 2, 3])
        observed[0][0][0] = 99
        self.assertEqual((recipient, donor), originals)

    def test_residual_clip_then_ties_even(self):
        recipient, marked, clean = [[[0, 254, 10]]], [[[0, 255, 1]]], [[[255, 0, 0]]]
        self.assertEqual(residual_transfer(recipient, marked, clean, 0.5), [[[0, 255, 10]]])
        self.assertEqual(residual_transfer(recipient, marked, clean, 1.0), [[[0, 255, 11]]])
        self.assertEqual(residual_transfer([[[1, 2, 3]]], marked, marked, 1.0), [[[1, 2, 3]]])

    def test_reject_invalid_rgb_shape_and_parameters(self):
        rgb = [[[1, 2, 3]]]
        for malformed in ([], [[]], [[[1, 2]]], [[[True, 2, 3]]], [[[1.0, 2, 3]]], [[[256, 2, 3]]]):
            with self.assertRaises(ValueError):
                center_patch(rgb, malformed, 1)
        for size in (0, 2, True, 1.0):
            with self.assertRaises(ValueError):
                center_patch(rgb, rgb, size)
        for scale in (0, 0.25, True, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                residual_transfer(rgb, rgb, rgb, scale)
        with self.assertRaises(ValueError):
            residual_transfer(rgb, rgb, [[*rgb[0], *rgb[0]]], 1.0)

    def test_binding_width_and_known_answer(self):
        self.assertEqual(binding_distance(0, 4095), 12)
        self.assertEqual(binding_distance(0, 7), 3)
        self.assertEqual(binding_distance(2048, 2048), 0)
        for value in (-1, 4096, True, 1.0):
            with self.assertRaises(ValueError):
                binding_distance(0, value)


if __name__ == "__main__":
    unittest.main()

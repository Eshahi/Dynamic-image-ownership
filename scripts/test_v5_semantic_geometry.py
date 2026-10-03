"""Model-free, hand-checkable semantic ranking and validation tests."""
import copy
import json
import unittest

from scripts.analyze_v5_semantic_geometry import (CHECKPOINT, LABELS, OWNER, PROFILE, RUN,
                                                 analyze, codec, empirical_auc, feature_hash,
                                                 inventory, omit_source, validate_feature, validate_inputs)


class GeometryTests(unittest.TestCase):
    def test_perfect_and_reversed_auc(self):
        perfect = empirical_auc([3, 4], [1, 2])
        self.assertEqual((perfect["auc"], perfect["wins"], perfect["ties"], perfect["losses"]), (1, 4, 0, 0))
        reversed_scores = empirical_auc([1, 2], [3, 4])
        self.assertEqual((reversed_scores["auc"], reversed_scores["losses"]), (0, 4))

    def test_ties_and_mixed_auc(self):
        self.assertEqual(empirical_auc([1, 1], [1, 1])["auc"], .5)
        mixed = empirical_auc([1, 3], [1, 2])
        self.assertEqual((mixed["auc"], mixed["wins"], mixed["ties"], mixed["losses"]), (.625, 2, 1, 1))

    def test_empty_class_explicitly_undefined(self):
        result = empirical_auc([], [1])
        self.assertIsNone(result["auc"])
        self.assertEqual(result["comparisons"], 0)
        self.assertTrue(result["undefined_reason"])

    def test_source_omission_removes_all_incident_edges(self):
        pairs = [{"left": 1, "right": 2}, {"left": 2, "right": 3}, {"left": 1, "right": 3}, {"left": 3, "right": 4}]
        self.assertEqual(omit_source(pairs, 2), pairs[2:])
        self.assertEqual(len(pairs), 4)

    def feature_row(self):
        values = [1.0] + [0.0] * 511
        pixels = "a" * 64
        return {"image": {"pixel_sha256": pixels}, "clip": {"dimension": 512, "values": values,
                "feature_sha256": feature_hash(values), "l2_normalized": True,
                "checkpoint_sha256": CHECKPOINT, "pixel_sha256": pixels}, "detections": [{
                "claimed_owner": OWNER, "binding_mode": "combined", "pixel_sha256": pixels,
                "feature_origin": "same saved suspect RGB8", "result": {"owner_id": OWNER,
                "binding_mode": "combined", "semantic_source": "external:clip-vit-b32-a6-40d365715913",
                "semantic_code": "00000000", "perceptual_hash": "00000000"}}]}

    def test_rejects_feature_corruption_and_pixel_mislink(self):
        row = self.feature_row()
        self.assertEqual(len(validate_feature(row)[0]), 512)
        corrupted = copy.deepcopy(row)
        corrupted["clip"]["values"][0] = .9
        with self.assertRaisesRegex(ValueError, "feature hash"):
            validate_feature(corrupted)
        corrupted = copy.deepcopy(row)
        corrupted["detections"][0]["pixel_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "linkage"):
            validate_feature(corrupted)

    def test_rejects_rehashed_non_normalized_and_nonfinite_vectors(self):
        row = self.feature_row()
        row["clip"]["values"][0] = .9
        row["clip"]["feature_sha256"] = feature_hash(row["clip"]["values"])
        with self.assertRaisesRegex(ValueError, "normalization"):
            validate_feature(row)
        row["clip"]["values"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            validate_feature(row)

    def synthetic_inventory(self):
        labels = json.loads(LABELS.read_text(encoding="utf-8"))
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        rows = inventory(labels["pairs"])
        template = self.feature_row()
        q = codec.semantic_code(template["clip"]["values"], profile=profile)
        template["detections"][0]["result"]["semantic_code"] = f"{q:08x}"
        for row in rows:
            if row["axis"] == "clean" and row["control"] in ("C0", "C1"):
                row.update(copy.deepcopy(template), detection_complete=True)
                if row["control"] == "C1":
                    row["same_instance_distances"] = {"semantic": 0, "instance": 0}
            if row["axis"] == "T5":
                row.update(distances_C0={"semantic": 0, "instance": 0}, distances_C1={"semantic": 0, "instance": 0},
                           clip_pair_cosine=1.0, status="complete_component_diagnostic")
        return {"run_id": RUN, "rows": rows}, labels, profile

    def test_complete_synthetic_roster_and_rejection(self):
        data, labels, profile = self.synthetic_inventory()
        # A saved embedding failure remains present while its complete features are analyzed.
        data["rows"][1]["errors"] = ["synthetic pre-existing embedding rejection"]
        _, pairs, changes = validate_inputs(data, labels, profile)
        self.assertEqual((len(pairs), len(changes)), (66, 12))
        stats, comparisons = analyze(pairs, labels["source_ids"], changes)
        self.assertEqual(len(comparisons), 399)
        self.assertEqual(stats["arms"]["C0"]["ranking"]["cosine"]["auc"], .5)
        self.assertTrue(all(s["retained_pairs"] == 55 for s in stats["source_omission_sensitivity"]))
        broken = copy.deepcopy(data)
        broken["rows"][-1] = copy.deepcopy(broken["rows"][0])
        with self.assertRaisesRegex(ValueError, "617-row"):
            validate_inputs(broken, labels, profile)
        broken = copy.deepcopy(data)
        result = broken["rows"][0]["detections"][0]["result"]
        result["semantic_code"] = f"{int(result['semantic_code'], 16) ^ 1:08x}"
        with self.assertRaisesRegex(ValueError, "recomputed semantic"):
            validate_inputs(broken, labels, profile)

    def test_rank_comparison_ties_and_reversal_agree_with_auc_difference(self):
        pairs = [{"id": "positive", "left": 1, "right": 2, "label": "same"},
                 {"id": "negative", "left": 2, "right": 3, "label": "different"},
                 {"id": "uncertain", "left": 1, "right": 3, "label": "uncertain"}]
        for pair, cosine, q in zip(pairs, [1., 0., .5], [2, 1, 0]):
            for arm in ("C0", "C1"):
                pair[arm] = {"cosine": cosine, "q": q, "H": 7, "q_le_6": True, "q_le_6_and_H_gt_6": True}
        stats, comparisons = analyze(pairs, [1, 2, 3], [])
        self.assertEqual(stats["arms"]["C0"]["ranking"]["cosine_minus_code_auc"], 1.)
        self.assertTrue(comparisons[0]["C0"]["strict_reversal"])
        self.assertEqual(comparisons[0]["C0"]["auc_contribution_difference"], 1.)
        self.assertEqual(stats["arms"]["C0"]["by_label"]["uncertain"]["pairs"], 1)


if __name__ == "__main__":
    unittest.main()

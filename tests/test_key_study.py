"""C6 owned fixtures only: no study IDs, pixels, checkpoints or model import."""
import json
import sys
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.signatures.key_study import (Sample, Pair, Observation, KeyStudyError,
    validate_plan, dependency_components, evaluate, summarize)
from scripts.check_keys import preview


def feature(axis=0):
    return tuple(1.0 if i == axis else 0.0 for i in range(512))


class KeyStudyTests(unittest.TestCase):
    def setUp(self):
        self.samples = [Sample("a", "owned:a", "ga", "ms-coco", "original"),
                        Sample("ar", "owned:a", "ga", "ms-coco", "repeat"),
                        Sample("b", "owned:b", "gb", "ms-coco", "original"),
                        Sample("c", "owned:c", "gc", "div2k", "original")]
        self.pairs = [Pair("repeat", "a", "ar", "Alice", "Alice", "same_image_repeat", "owned:repeat"),
                      Pair("owner", "a", "a", "Alice", "Bob", "wrong_owner", "owned:roster"),
                      Pair("distinct", "a", "b", "Alice", "Alice", "distinct_unscreened", "owned:ids"),
                      Pair("unrelated", "b", "c", "Alice", "Alice", "unrelated", "owned:annotation")]
        self.observations = {key: Observation("completed", feature(), bytes(4))
                             for key in ("a", "ar", "b", "c")}
        self.seed = bytes(32)

    def test_repeat_exact_pre_post_hash_and_wrong_owner(self):
        rows = evaluate(self.samples, self.pairs, self.observations, self.seed)
        repeat, owner = rows[:2]
        self.assertEqual(repeat["representation_distance"], 0)
        self.assertEqual((repeat["q_distance"], repeat["phash_distance"], repeat["ws_distance"], repeat["wi_distance"]), (0, 0, 0, 0))
        self.assertTrue(repeat["ws_exact_match"] and repeat["wi_exact_match"])
        self.assertEqual((owner["representation_distance"], owner["q_distance"], owner["phash_distance"]), (0, 0, 0))
        self.assertFalse(owner["ws_exact_match"] or owner["wi_exact_match"])
        self.assertGreater(owner["ws_distance"], 0)
        self.assertGreater(owner["wi_distance"], 0)

    def test_phash_one_bit_not_hash_distance_or_detector_success(self):
        self.observations["ar"] = Observation("completed", feature(), b"\x01\0\0\0")
        row = evaluate(self.samples, self.pairs, self.observations, self.seed)[0]
        self.assertEqual(row["phash_distance"], 1)
        self.assertEqual(row["q_distance"], 0)
        self.assertEqual(row["ws_distance"], 0)
        self.assertGreater(row["wi_distance"], 1)
        self.assertNotIn("detector_success", row)

    def test_cosine_distance_orthogonal(self):
        self.observations["ar"] = Observation("completed", feature(1), bytes(4))
        row = evaluate(self.samples, self.pairs, self.observations, self.seed)[0]
        self.assertEqual(row["representation_distance"], 1)

    def test_failed_and_absent_keep_all_planned_rows_and_null(self):
        del self.observations["ar"]
        self.observations["b"] = Observation("failed", error="owned extraction failure")
        rows = evaluate(self.samples, self.pairs, self.observations, self.seed)
        self.assertEqual(len(rows), 4)
        self.assertEqual([r["status"] for r in rows], ["pending", "completed", "failed", "failed"])
        for row in (rows[0], rows[2], rows[3]):
            for field in ("representation_distance", "q_distance", "phash_distance", "ws_distance", "wi_distance", "ws_exact_match", "wi_exact_match"):
                self.assertIsNone(row[field])
        summary = summarize(rows)
        self.assertEqual(sum(c["planned"] for c in summary), 8)  # both components
        self.assertEqual(sum(c["completed"] for c in summary), 2)
        for cell in summary:
            self.assertIsNone(cell["independent_n"])
            self.assertIsNone(cell["confidence_interval"])
            if not cell["completed"]:
                self.assertIsNone(cell["completed_only_exact_rate"])

    def test_pair_dependence_uses_missing_pairs_and_shared_sources(self):
        components = dependency_components(self.samples, self.pairs)
        self.assertEqual(len(set(components.values())), 1)
        self.assertEqual(components["a"], components["ar"])
        self.assertEqual(components, dependency_components(list(reversed(self.samples)), list(reversed(self.pairs))))

    def test_explicit_unscreened_label_not_unrelated_by_domain(self):
        rows = evaluate(self.samples, self.pairs, self.observations, self.seed)
        self.assertEqual(rows[2]["semantic_label"], "unresolved")
        self.assertEqual(rows[2]["instance_label"], "negative")
        # Owned exact-code collision stays visible on a distinct negative pair.
        self.assertTrue(rows[2]["wi_exact_match"])

    def test_plan_rejects_test_split_missing_duplicate_and_relabel(self):
        bad_samples = [replace(self.samples[0], split="test"), *self.samples[1:]]
        with self.assertRaises(KeyStudyError): validate_plan(bad_samples, self.pairs)
        for pairs in ([*self.pairs, self.pairs[0]], [replace(self.pairs[0], right="missing")],
                      [replace(self.pairs[2], relation="same_image_repeat")],
                      [replace(self.pairs[0], right="a")],
                      [replace(self.pairs[1], right="ar")],
                      [replace(self.pairs[1], right_owner="Alice")],
                      [replace(self.pairs[2], right_owner="Bob")]):
            with self.subTest(pairs=pairs), self.assertRaises(KeyStudyError):
                validate_plan(self.samples, pairs)
        with self.assertRaises(KeyStudyError):
            validate_plan([*self.samples, replace(self.samples[0], sample_id="new", group_id="other")], self.pairs)

    def test_invalid_measurements_fail_closed_not_negative(self):
        for observation in (Observation("completed", feature(), b"\0"),
                            Observation("completed", tuple([float("nan")]*512), bytes(4)),
                            Observation("completed", tuple([True]*512), bytes(4)),
                            Observation("completed", feature(), bytes(4), "error"),
                            Observation("failed", feature(), bytes(4), "failure"),
                            Observation("failed"), Observation("unknown")):
            with self.subTest(observation=observation), self.assertRaises(ValueError):
                evaluate(self.samples, self.pairs, {"a": observation}, self.seed)
        with self.assertRaises(KeyStudyError):
            evaluate(self.samples, self.pairs, {"extra": Observation("pending")}, self.seed)

    def test_summary_does_not_convert_missing_to_measured_nonmatch(self):
        rows = evaluate(self.samples, self.pairs, {}, self.seed)
        rows[0]["ws_exact_match"] = False
        with self.assertRaises(KeyStudyError): summarize(rows)

    def test_metadata_preview_no_extraction(self):
        plan = {"schema_version": "c6-pair-preview-v1",
                "samples": [asdict(s) for s in self.samples], "pairs": [asdict(p) for p in self.pairs]}
        with patch("src.signatures.semantic.PinnedClipEncoder.from_checkpoint", side_effect=AssertionError("model forbidden")):
            receipt = preview(json.dumps(plan).encode())
        self.assertEqual(receipt["pair_count"], 4)
        self.assertFalse(receipt["scientific_compute_authorized"])
        self.assertEqual(receipt["extraction_adapter"], "NOT_IMPLEMENTED")
        for payload in (b'{"schema_version":1,"schema_version":2}',
                        json.dumps({**plan, "extra": 1}).encode(),
                        json.dumps({**plan, "samples": [{**asdict(self.samples[0]), "split": "validation"}]}).encode(),
                        b"x"*(2*1024*1024+1)):
            with self.assertRaises(ValueError): preview(payload)


if __name__ == "__main__":
    unittest.main()

"""Owned synthetic saved-result regressions; no pixels, model or GPU."""
import copy
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.signatures.key_study import Sample, Pair, Observation, evaluate, KeyStudyError
from src.signatures.saved_key_results import canonical, plan_digest, read_results, MAX_BYTES


class SavedResultsTests(unittest.TestCase):
    def setUp(self):
        self.samples = [Sample("a", "owned:a", "g", "ms-coco", "original"),
                        Sample("b", "owned:a", "g", "ms-coco", "repeat")]
        self.pairs = [Pair("p", "a", "b", "Alice", "Alice", "same_image_repeat", "owned:test")]
        self.seed = bytes(32)
        self.features = [1.0] + [0.0] * 511
        self.data = {"schema_version": "c6-recorded-results-v1",
                     "plan_sha256": plan_digest(self.samples, self.pairs),
                     "projection_seed": self.seed.hex(), "observations": {
                         k: {"status": "completed", "features": self.features,
                             "phash": "00000000", "error": None} for k in ("a", "b")},
                     "rows": evaluate(self.samples, self.pairs, {
                         k: Observation("completed", tuple(self.features), bytes(4))
                         for k in ("a", "b")}, self.seed)}

    def read(self, data=None, raw=None, digest=None):
        raw = canonical(data if data is not None else self.data) if raw is None else raw
        return read_results(raw, expected_sha256=digest or hashlib.sha256(raw).hexdigest(),
                            samples=self.samples, pairs=self.pairs, projection_seed=self.seed)

    def test_replay_is_descriptive_not_custody(self):
        result = self.read()
        self.assertEqual(result["rows"], self.data["rows"])
        self.assertFalse(result["scientific_acceptance"])
        self.assertEqual(result["extraction_custody"], "NOT_ESTABLISHED")

    def test_each_row_field_is_bound(self):
        for key, value in self.data["rows"][0].items():
            changed = copy.deepcopy(self.data)
            changed["rows"][0][key] = "forged" if value != "forged" else None
            with self.subTest(field=key), self.assertRaises(KeyStudyError): self.read(changed)

    def test_envelope_inventory_and_type_tampering(self):
        mutations = []
        for key in self.data:
            changed = copy.deepcopy(self.data); del changed[key]; mutations.append(changed)
        for field, value in (("plan_sha256", "0"*64), ("projection_seed", "f"*64),
                             ("rows", []), ("observations", {}), ("extra", True)):
            changed = copy.deepcopy(self.data); changed[field] = value; mutations.append(changed)
        for field, value in (("q_distance", False), ("representation_distance", 0),
                             ("ws_exact_match", 1)):
            changed = copy.deepcopy(self.data); changed["rows"][0][field] = value; mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(KeyStudyError): self.read(changed)

    def test_failed_and_pending_are_not_completed_or_suppressed(self):
        for status, error in (("pending", None), ("failed", "owned failure")):
            changed = copy.deepcopy(self.data)
            changed["observations"]["b"] = {"status": status, "features": None, "phash": None, "error": error}
            changed["rows"] = evaluate(self.samples, self.pairs, {
                "a": Observation("completed", tuple(self.features), bytes(4)),
                "b": Observation(status, error=error)}, self.seed)
            self.assertEqual(self.read(changed)["rows"][0]["status"], status)
            changed["rows"][0]["q_distance"] = 0
            with self.assertRaises(KeyStudyError): self.read(changed)

    def test_untrusted_bytes_reject(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff', b'[]', b'x'*(MAX_BYTES+1)):
            with self.assertRaises(KeyStudyError): self.read(raw=raw)
        with self.assertRaises(KeyStudyError): self.read(digest="0"*64)

    def test_bad_observations_reject(self):
        for field, value in (("features", [True]*512), ("features", [0.0]*511),
                             ("phash", "00"), ("error", "unexpected"), ("extra", 1)):
            changed = copy.deepcopy(self.data); changed["observations"]["a"][field] = value
            with self.assertRaises(KeyStudyError): self.read(changed)


if __name__ == "__main__": unittest.main()

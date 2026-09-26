"""Owned synthetic CPU PNGs, no study image or actual semantic/model extraction."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.embedding.output import TrialStore
from src.embedding.proposed import EmbeddingError
from tests import test_embedding as fixtures

torch, SOURCE, SETTINGS, WS, WI, CONFIG = (fixtures.torch, fixtures.SOURCE, fixtures.SETTINGS,
                                         fixtures.WS, fixtures.WI, fixtures.CONFIG)


@unittest.skipIf(torch is None, "owned PNG/tensor tests use existing WSL environment")
class OutputTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.rgb = np.arange(37*43*3, dtype=np.uint8).reshape(37, 43, 3)
        self.kernels = fixtures.TensorContracts()
        self.kernels.setUp()
        from src.data.preprocess import normalized
        self.source = torch.tensor(normalized(self.rgb).transpose(2, 0, 1).copy()).unsqueeze(0)

    def store(self):
        return TrialStore(self.root, source_id="owned-cpu-fixture", seed=7, config_hash="a"*64,
                          source_raw_hash=SOURCE.hex(), source_rgb8=self.rgb)

    def candidate(self):
        from src.embedding.proposed import optimize_existing
        return optimize_existing(self.source, SETTINGS, self.kernels.backend(), seed=7,
            source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG)

    def test_saved_pair_hashes_decoded_safety_and_no_success_claim(self):
        store = self.store()
        before = self.rgb.copy()
        candidate = self.candidate()
        seen = []
        def check(pixels):
            seen.append(pixels.copy())
            return False
        receipt, pair = store.save_pair(candidate, check)
        self.assertFalse(receipt["scientific_acceptance"])
        self.assertEqual(receipt["status"], "saved_pair_pending_metrics_and_blind_verification")
        self.assertEqual(len(seen), 2)
        for row, actual in zip(receipt["rows"], seen):
            saved = (store.directory/row["output_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(saved).hexdigest(), row["output_hash"])
            self.assertTrue((actual == pair[row["kind"]]).all())
            self.assertEqual(row["blind_verification"], "NOT_RUN")
        self.assertTrue((self.rgb == before).all())
        with self.assertRaises(EmbeddingError): store.save_pair(candidate, check)

    def test_safety_flag_retains_unmodified_diagnostic_png_and_failed_status(self):
        store = self.store()
        receipt, pair = store.save_pair(self.candidate(), lambda pixels: True)
        self.assertEqual(receipt["status"], "failed_safety_flagged")
        self.assertTrue(all(row["safety_flagged"] for row in receipt["rows"]))
        self.assertGreater(pair["marked_candidate"].max(), 0)
        self.assertTrue((store.directory/"matched_control.png").exists())
        self.assertTrue((store.directory/"marked_candidate.png").exists())

    def test_interruption_and_failure_are_retained(self):
        store = self.store()
        store.record({"iteration": 0, "loss": .5})
        self.assertTrue((store.directory/"start.json").exists())
        self.assertFalse((store.directory/"pair.json").exists())
        with self.assertRaises(ValueError): store.record({"loss": float("nan")})
        store.fail(OSError("private diagnostic text must not be included"))
        failure = (store.directory/"failed.json").read_text()
        self.assertNotIn("private diagnostic", failure)
        self.assertEqual(json.loads(failure)["error_type"], "OSError")
        with self.assertRaises(EmbeddingError): store.record({"iteration": 1})

    def test_mismatched_identity_or_unknown_safety_result_fails_closed(self):
        store = self.store()
        candidate = self.candidate()
        candidate.metadata["seed"] = 8
        with self.assertRaises(EmbeddingError): store.save_pair(candidate, lambda pixels: False)
        self.assertFalse((store.directory/"marked_candidate.png").exists())
        other = self.store()
        with self.assertRaises(EmbeddingError): other.save_pair(self.candidate(), lambda pixels: None)
        other.fail(ValueError("invalid safety result"))
        self.assertTrue((other.directory/"failed.json").exists())
        self.assertTrue((other.directory/"matched_control.png").exists())


if __name__ == "__main__":
    unittest.main()

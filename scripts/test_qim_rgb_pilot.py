"""Owned RGB/PNG and transform-boundary synthetic engineering checks."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from qim_rgb_pilot import CONDITIONS, OWNERS, luminance, mark_rgb, persist_rgb, quality, summarize, transform
from revised_watermark import DEFAULT_PROFILE, detect


class RGBPilotTests(unittest.TestCase):
    def source(self):
        y, x = np.indices((161, 173))
        plane = ((x * 17 + y * 29 + x * y % 37) % 128 + 64).astype(np.uint8)
        return np.stack([plane, plane, plane], axis=-1)

    def test_saved_rgb_roundtrip_and_true_owner(self):
        source = self.source()
        marked = mark_rgb(source, DEFAULT_PROFILE)
        with tempfile.TemporaryDirectory() as folder:
            observed = persist_rgb(Path(folder) / "marked.png", marked)
        self.assertTrue(np.array_equal(observed, marked))
        self.assertTrue(detect(luminance(observed).tolist(), OWNERS[0], profile=DEFAULT_PROFILE)["present"])
        self.assertGreater(np.count_nonzero(marked != source), 0)

    def test_quantized_quality_exact_error(self):
        source = self.source()
        changed = source.copy()
        changed[0, 0, 0] += 1
        result = quality(source, changed)
        self.assertAlmostEqual(result["mse_rgb255"], 1 / source.size)
        self.assertEqual(quality(source, source)["psnr_db"], None)
        self.assertTrue(quality(source, source)["zero_error"])

    def test_fixed_attacks_deterministic_native_dimensions(self):
        source = self.source()
        for condition in CONDITIONS:
            first = transform(source, condition, 0)
            second = transform(source, condition, 0)
            self.assertEqual(first.shape, source.shape)
            self.assertEqual(first.dtype, np.uint8)
            self.assertTrue(np.array_equal(first, second))
        shifted = transform(source, "shift1_left_restore", 0)
        self.assertTrue(np.array_equal(shifted[:, :-1], source[:, 1:]))
        self.assertTrue(np.array_equal(shifted[:, -1], source[:, -1]))

    def test_failure_and_partial_rows_do_not_gain_primary_success(self):
        calls = [{"condition": "native_png", "control": control, "result": {"present": control == "C1"}} for control in ("C0", "C1", "C2", "C2", "C2")]
        base = {"status": "completed", "detections": calls, "quality": {"zero_error": False, "psnr_db": 40, "ssim_rgb": .95}, "changed_channels": 1}
        rows = [base, {**base, "status": "failed"}, {"status": "NOT_RUN"}]
        result = summarize(rows)
        self.assertEqual(result["native_joint_passes"], 1)
        self.assertEqual(result["native_joint_pass_fraction"], .1)
        self.assertEqual(result["engineering_verdict"], "FAIL_OR_INCOMPLETE")
        self.assertIsNone(result["confidence_interval"])
        self.assertEqual(result["by_condition"]["native_png"]["c0_completed_calls"], 2)
        self.assertEqual(result["by_condition"]["native_png"]["c0_missing_calls"], 8)
        self.assertEqual(result["native_c2_missing_calls"], 24)


if __name__ == "__main__":
    unittest.main()

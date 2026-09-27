"""Synthetic CPU-only quality/drift tests; never load pretrained weights."""
import importlib.util
import math
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import numpy as np
except ImportError:
    np = None
if np is not None:
    from src.embedding.quality import classical, target_checks, hamming, drift, rgb8, _checked_bytes, PAIRS, _structure, _tensor_digest


@unittest.skipIf(np is None, "numpy absent in model-free base venv; covered in existing WSL science venv")
class QualityTests(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((63, 64, 3), dtype=np.uint8)

    @unittest.skipUnless(importlib.util.find_spec("skimage"), "requires existing skimage")
    def test_identical(self):
        result = classical(self.image, self.image)
        self.assertEqual(result["mse_rgb01"], 0.0)
        self.assertIsNone(result["psnr_db"])
        self.assertTrue(result["psnr_positive_infinity"])
        self.assertEqual(result["ssim_rgb"], 1.0)

    @unittest.skipUnless(importlib.util.find_spec("skimage"), "requires existing skimage")
    def test_known_psnr_and_symmetry(self):
        other = np.full_like(self.image, 1)
        result = classical(self.image, other)
        self.assertAlmostEqual(result["psnr_db"], 20 * math.log10(255), places=10)
        self.assertEqual(result, classical(other, self.image))
        self.assertLess(result["ssim_rgb"], 1.0)

    @unittest.skipUnless(importlib.util.find_spec("skimage"), "requires existing skimage")
    def test_no_grid_coercion(self):
        with self.assertRaises(ValueError):
            classical(self.image, np.zeros((64, 64, 3), dtype=np.uint8))

    def test_rgb_validation_and_copy(self):
        for bad in (self.image.astype(float), self.image[:, :, 0], self.image[:62], None):
            with self.assertRaises(ValueError):
                rgb8(bad)
        copied = rgb8(self.image)
        copied[0, 0] = 255
        self.assertEqual(self.image[0, 0, 0], 0)

    def test_strict_boundaries(self):
        record = {"mse_rgb01": 0.1, "psnr_db": 35.0, "psnr_positive_infinity": False,
                  "ssim_rgb": 0.9, "lpips_alex_v01": 0.1}
        result = target_checks(record)
        self.assertFalse(result["all_three_targets"])
        self.assertFalse(any(result[k] for k in ("psnr_gt_35", "ssim_gt_0_9", "lpips_lt_0_1")))
        record.update(mse_rgb01=0.0, psnr_db=None, psnr_positive_infinity=True,
                      ssim_rgb=1.0, lpips_alex_v01=0.0)
        self.assertTrue(target_checks(record)["all_three_targets"])
        self.assertFalse(target_checks(record)["scientific_acceptance"])

    def test_nonfinite_record_rejected(self):
        record = {"mse_rgb01": 0.1, "psnr_db": 36.0, "psnr_positive_infinity": False,
                  "ssim_rgb": 0.91, "lpips_alex_v01": 0.01}
        for key in ("mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01"):
            with self.assertRaises(ValueError):
                target_checks({**record, key: float("nan")})

    def test_radius_and_little_endian(self):
        result = drift(b"\0\0", b"\0" * 4, b"\1\0", b"\3\0\0\0")
        self.assertEqual(result["q_hamming"], 1)
        self.assertEqual(result["h_hamming"], 2)
        self.assertFalse(result["both_source_codes_in_radius1"])
        self.assertEqual(result["blind_detection"], "NOT_RUN")
        self.assertEqual(hamming(b"\xff\x0f", b"\0\0", 12), 12)

    def test_code_canonicality(self):
        for left, right, bits in ((b"\0\x10", b"\0\0", 12),
                                  (b"\0", b"\0", 12),
                                  (bytearray(2), b"\0\0", 12),
                                  (b"\0\0", b"\0\0", True)):
            with self.assertRaises(ValueError):
                hamming(left, right, bits)

    def test_reference_order_frozen(self):
        self.assertEqual(PAIRS, (("control_source", "source", "control"),
                               ("candidate_source", "source", "candidate"),
                               ("candidate_control", "control", "candidate")))

    def test_weight_preflight_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "absent"
            with self.assertRaises(ValueError):
                _checked_bytes(path, "0" * 64)
            # Fixture creation uses a temporary test file, never a real asset.
            path.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                _checked_bytes(path, "0" * 64)
            with self.assertRaises(ValueError):
                _checked_bytes(path, "0" * 64, 1)

    def test_child_profile_mutation_rejected(self):
        child = SimpleNamespace(training=False)
        metric = SimpleNamespace(version="0.1", pnet_type="alex", lpips=True,
                                 spatial=False, pnet_tune=False, pnet_rand=True,
                                 L=5, chns=[64, 192, 384, 256, 256], training=False)
        metric.named_modules = lambda: iter((("", metric), ("dropout", child)))
        original = _structure(metric)
        for key, changed in (("version", "0.0"), ("lpips", False),
                             ("spatial", True), ("L", True)):
            before = getattr(metric, key)
            setattr(metric, key, changed)
            with self.assertRaises(ValueError):
                _structure(metric)
            setattr(metric, key, before)
        child.training = True
        with self.assertRaises(ValueError):
            _structure(metric)
        child.training = False
        self.assertEqual(_structure(metric), original)
        child = SimpleNamespace(training=False)
        self.assertNotEqual(_structure(metric), original)

    def test_tensor_buffer_mutation_and_flags(self):
        class FakeTensor:
            requires_grad = False
            dtype = "torch.float32"
            device = SimpleNamespace(type="cuda")
            shape = (1,)
            def __init__(self):
                self.value = np.array([1.0], dtype=np.float32)
            def detach(self): return self
            def cpu(self): return self
            def contiguous(self): return self
            def numpy(self): return self.value
        buffer = FakeTensor()
        metric = SimpleNamespace(named_parameters=lambda: iter(()),
                                 named_buffers=lambda: iter((("shift", buffer),)))
        original = _tensor_digest(metric)
        buffer.value[0] = 2.0
        self.assertNotEqual(_tensor_digest(metric), original)
        for name, changed in (("dtype", "torch.float16"), ("requires_grad", True),
                              ("device", SimpleNamespace(type="cpu"))):
            before = getattr(buffer, name)
            setattr(buffer, name, changed)
            with self.assertRaises(ValueError):
                _tensor_digest(metric)
            setattr(buffer, name, before)


if __name__ == "__main__":
    unittest.main()

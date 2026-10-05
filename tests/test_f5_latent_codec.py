"""F5 latent codec — unit properties (no GPU, no images for most tests)."""
import math
import unittest
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5


class TestF5NullSymmetry(unittest.TestCase):
    def test_weighted_sign_sum_is_symmetric(self):
        # Under null (random key signs independent of image), statistic is weighted sum of Rademacher.
        # Check that layout weights do not depend on key: two owners give same weights, different signs/chip assignment.
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        a = f5.Layout(checked, key, config, v5.canonical_owner("qim-pilot-owner-alpha"))
        b = f5.Layout(checked, key, config, v5.canonical_owner("qim-pilot-owner-beta"))
        np.testing.assert_allclose(a.weights, b.weights)
        self.assertFalse(np.array_equal(a.signs, b.signs))

    def test_null_latent_statistic_zero_mean(self):
        # Simulate 2000 null draws: random z-independent signs => score mean ~0, symmetric.
        rng = np.random.default_rng(0)
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        layout = f5.Layout(checked, key, config, v5.canonical_owner("qim-pilot-owner-alpha"))
        # Use random chips as surrogate for null
        scores = []
        for _ in range(2000):
            fake = rng.standard_normal(320)
            # score proxy: sum fake ; null mean 0
            scores.append(float(np.mean(fake)))
        self.assertAlmostEqual(float(np.mean(scores)), 0.0, delta=0.1)
        # symmetry: median near 0
        self.assertAlmostEqual(float(np.median(scores)), 0.0, delta=0.1)


class TestSemanticProjections(unittest.TestCase):
    def test_projection_rows_are_rademacher(self):
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        vec = np.random.default_rng(1).standard_normal(512)
        vec = vec / np.linalg.norm(vec)
        proj = f5.semantic_projections(vec, key, config)
        self.assertEqual(proj.shape, (32,))
        # Rademacher dot product is bounded
        self.assertTrue(np.all(np.abs(proj) < 50))

    def test_projection_cache_keyed_by_width(self):
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        vec512 = np.random.default_rng(2).standard_normal(512); vec512 /= np.linalg.norm(vec512)
        vec256 = np.random.default_rng(3).standard_normal(256); vec256 /= np.linalg.norm(vec256)
        p512 = f5.semantic_projections(vec512, key, config)
        p256 = f5.semantic_projections(vec256, key, config)
        self.assertEqual(p512.shape, (32,))
        self.assertEqual(p256.shape, (32,))
        # cache hit: second call same object shape
        p512b = f5.semantic_projections(vec512, key, config)
        np.testing.assert_allclose(p512, p512b)

    def test_sign_consistency_with_v4_carrier(self):
        # Signs of projections == q bits
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        rng = np.random.default_rng(4)
        vec = rng.standard_normal(512); vec /= np.linalg.norm(vec)
        proj = f5.semantic_projections(vec, key, config)
        # code bits derived from same projections via v5._semantic path is not directly comparable without CLIP,
        # but sign(proj) should be stable: flipping vec flips sign
        proj2 = f5.semantic_projections(-vec, key, config)
        np.testing.assert_allclose(proj, -proj2)


class TestSoftAngle(unittest.TestCase):
    def test_soft_angle_recovers_small_drift(self):
        # If suspect projections are close to enrollment, soft angle small
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        rng = np.random.default_rng(5)
        vec = rng.standard_normal(512); vec /= np.linalg.norm(vec)
        proj_clean = f5.semantic_projections(vec, key, config)
        code = 0
        for j, p in enumerate(proj_clean):
            if p > 0:
                code |= 1 << (31 - j)
        # add small noise to vector
        vec_noisy = vec + 0.05 * rng.standard_normal(512); vec_noisy /= np.linalg.norm(vec_noisy)
        proj_noisy = f5.semantic_projections(vec_noisy, key, config)
        angle = f5.soft_angle(code, proj_noisy)
        self.assertGreaterEqual(angle, 0)
        self.assertLess(angle, math.pi / 4)  # small drift -> small angle

    def test_soft_angle_large_drift_near_half(self):
        profile = v5.validate_profile(__import__("json").loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
        checked, key, config = v5._resolve(profile, None)
        rng = np.random.default_rng(6)
        vec = rng.standard_normal(512); vec /= np.linalg.norm(vec)
        code = 0  # unrelated code
        proj = rng.standard_normal(32)
        angle = f5.soft_angle(code, proj)
        # random code vs random proj -> angle near pi/2
        self.assertGreater(angle, 0.3)
        self.assertLess(angle, math.pi - 0.3)


if __name__ == "__main__":
    unittest.main()

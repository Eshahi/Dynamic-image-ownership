"""Synthetic CPU algebra only: no image files, model imports or GPU execution."""
import hashlib
import inspect
import math
import struct
import unittest
from unittest.mock import patch

import numpy as np

from scripts import m1_blind_noise_core as core


class BlindNoiseCoreTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(0)
        self.E = self.rng.normal(size=512)
        self.E /= np.linalg.norm(self.E)
        self.F = self.rng.normal(size=512)
        self.F /= np.linalg.norm(self.F)
        self.owner = core.OWNERS[0]
        self.H = 0x9E12F073

    def test_serialization_bit_order_domains_and_independent_permutation_reference(self):
        def frame(s):
            b = s.encode("utf-8")
            return len(b).to_bytes(4, "big") + b
        prefix = frame(core.VERSION) + frame("semantic-row-signs") + frame(self.owner)
        self.assertEqual(core._prefix("semantic-row-signs", self.owner), prefix)
        first_byte = hashlib.shake_256(prefix).digest(1)[0]
        expected = np.array([1 if first_byte & (1 << j) else -1 for j in range(7, -1, -1)])
        np.testing.assert_array_equal(core._signs("semantic-row-signs", self.owner, 8), expected)
        coordinates_prefix = frame(core.VERSION) + frame("coordinates") + frame(self.owner)
        expected_order = sorted(range(64), key=lambda j: (
            hashlib.sha256(coordinates_prefix + struct.pack(">I", j)).digest(), j))
        np.testing.assert_array_equal(core._permutation("coordinates", self.owner, 64), expected_order)
        self.assertNotEqual(core._prefix("ab", "c"), core._prefix("a", "bc"))
        self.assertFalse(np.array_equal(core._signs("semantic-row-signs", self.owner, 64),
                                       core._signs("instance-row-signs", self.owner, 64)))

    def test_fwht_matches_explicit_reference_and_is_orthonormal(self):
        for n in (1, 2, 8, 32):
            x = self.rng.normal(size=n)
            reference = np.array([[(-1.0)**((a & b).bit_count()) for b in range(n)]
                                  for a in range(n)]) / math.sqrt(n)
            np.testing.assert_allclose(core.fwht(x), reference @ x, atol=2e-14)
            np.testing.assert_allclose(core.fwht(core.fwht(x)), x, atol=2e-14)
            self.assertAlmostEqual(np.linalg.norm(core.fwht(x)), np.linalg.norm(x), places=12)
        for bad in ([], [1, 2, 3], [[1, 2]], [np.nan, 1], [1j, 0]):
            with self.assertRaises(ValueError):
                core.fwht(bad)

    def test_shapes_disjoint_partition_norms_and_exact_semantic_cosine(self):
        first = core.template(self.E, self.H, self.owner)
        second = core.template(self.F, 0, self.owner)
        for key in ("coords_s", "coords_i", "v_s", "v_i", "r_s", "r_i"):
            self.assertEqual(first[key].shape, (8192,))
        self.assertEqual(first["T"].shape, (16384,))
        np.testing.assert_array_equal(np.sort(np.concatenate([first["coords_s"], first["coords_i"]])),
                                      np.arange(16384))
        self.assertAlmostEqual(np.linalg.norm(first["v_s"]), 1, places=13)
        self.assertAlmostEqual(np.linalg.norm(first["v_i"]), 1, places=13)
        self.assertAlmostEqual(np.mean(first["T"]**2), 1, places=13)
        self.assertAlmostEqual(first["v_s"] @ second["v_s"], self.E @ self.F, places=13)
        np.testing.assert_allclose(first["T"][first["coords_s"]],
                                   math.sqrt(8192) * first["r_s"] * first["v_s"], atol=0)
        np.testing.assert_allclose(first["T"][first["coords_i"]],
                                   math.sqrt(8192) * first["r_i"] * first["v_i"], atol=0)

    def test_hash_msb_order_exact_product_kernel_and_complement(self):
        basis = np.zeros(512); basis[0] = 1
        product = core._product(basis, 0x80000000)
        self.assertEqual(product[0], 1 / math.sqrt(32))
        np.testing.assert_array_equal(product[1:32], np.full(31, -1 / math.sqrt(32)))
        for h2 in (0, 0xFFFFFFFF, self.H, self.H ^ 0xFFFFFFFF):
            x = core._product(self.E, self.H)
            y = core._product(self.F, h2)
            expected = (self.E @ self.F) * (1 - 2 * (self.H ^ h2).bit_count() / 32)
            self.assertAlmostEqual(x @ y, expected, places=13)
        np.testing.assert_array_equal(core._product(self.E, self.H ^ 0xFFFFFFFF),
                                      -core._product(self.E, self.H))

    def test_32_fixture_pairs_projection_moments_kernel_and_error_bound(self):
        # Fixed PCG64 seed0, all owners in deterministic cyclic order: no map selection.
        rng = np.random.Generator(np.random.PCG64(0))
        for j in range(32):
            e = rng.normal(size=512); e /= np.linalg.norm(e)
            f = rng.normal(size=512); f /= np.linalg.norm(f)
            h, h2 = [int(a) for a in rng.integers(0, 2**32, size=2, dtype=np.uint64)]
            owner = core.OWNERS[j % 4]
            diagnostic = core.projection_diagnostic(e, h, f, h2, owner)
            first, second = core.template(e, h, owner), core.template(f, h2, owner)
            self.assertAlmostEqual(diagnostic["kernel_exact"],
                                   (e @ f) * (1 - 2 * (h ^ h2).bit_count() / 32), places=13)
            self.assertAlmostEqual(diagnostic["kernel_projected_normalized"],
                                   first["v_i"] @ second["v_i"], places=13)
            self.assertLessEqual(diagnostic["normalized_error"],
                                 diagnostic["normalization_error_bound"] + 1e-14)
            maps = core._owner_maps(owner)
            x = core._product(e, h); y = core._product(f, h2)
            u = core.fwht(maps.pre_signs_i * x); w = core.fwht(maps.pre_signs_i * y)
            # numpy's ddof=1 expression independently verifies finite-population scaling.
            expected_variance = 16384**2 * (1 - 8192/16384) * np.var(u*w, ddof=1) / 8192
            self.assertAlmostEqual(diagnostic["variance_inner"], expected_variance, places=16)
            self.assertGreaterEqual(diagnostic["variance_norm_1"], 0)
            self.assertGreaterEqual(diagnostic["variance_norm_2"], 0)
            self.assertEqual(diagnostic["sampling_fraction"], .5)

    def test_same_feature_and_complement_projected_kernels(self):
        same = core.projection_diagnostic(self.E, self.H, self.E, self.H, self.owner)
        complement = core.projection_diagnostic(self.E, self.H, self.E, self.H ^ 0xFFFFFFFF, self.owner)
        self.assertAlmostEqual(same["kernel_projected_normalized"], 1, places=13)
        self.assertAlmostEqual(complement["kernel_projected_normalized"], -1, places=13)

    def test_public_owner_maps_cached_but_no_feature_template_cache(self):
        alpha = core.template(self.E, self.H, self.owner)
        beta = core.template(self.E, self.H, core.OWNERS[1])
        self.assertFalse(np.array_equal(alpha["T"], beta["T"]))
        self.assertFalse(alpha["coords_s"].flags.writeable)
        self.assertFalse(alpha["r_s"].flags.writeable)
        altered = core.template(self.F, self.H, self.owner)
        self.assertIs(alpha["coords_s"], altered["coords_s"])
        self.assertFalse(np.array_equal(alpha["v_s"], altered["v_s"]))
        alpha["v_s"][:] = 0
        recreated = core.template(self.E, self.H, self.owner)
        self.assertAlmostEqual(np.linalg.norm(recreated["v_s"]), 1, places=13)
        self.assertEqual(core._owner_maps.cache_info().maxsize, 4)

    def test_threshold_inclusive_four_three_states_and_abstentions(self):
        for s, i, expected in ((4, 4, "both_match"), (4, np.nextafter(4., -np.inf), "semantic_only"),
                               (3.9, 3.9, "neither_supported"), (3.9, 4, "ambiguous_instance_only"),
                               (None, 4, "invalid_measurement"), (4, np.inf, "invalid_measurement")):
            self.assertEqual(core.classify_scores(s, i)["state"], expected)
        self.assertEqual(core.classify_scores(4, 4)["flags"], {"s": True, "i": True})

    def test_score_matches_direct_formula_scale_invariance_and_sign(self):
        parts = core.template(self.E, self.H, self.owner)
        latent = self.rng.normal(size=16384) + .2 * parts["T"]
        measured = core.scores(latent, self.E, self.H, self.owner)
        for channel in ("s", "i"):
            weights = latent[parts[f"coords_{channel}"]] * parts[f"v_{channel}"]
            expected = np.sum(weights * parts[f"r_{channel}"]) / math.sqrt(np.sum(weights**2))
            self.assertAlmostEqual(measured[channel], expected, places=13)
        doubled = core.scores(2*latent, self.E, self.H, self.owner)
        negative = core.scores(-latent, self.E, self.H, self.owner)
        for channel in ("s", "i"):
            self.assertAlmostEqual(measured[channel], doubled[channel], places=13)
            self.assertAlmostEqual(measured[channel], -negative[channel], places=13)
        ideal = core.scores(parts["T"], self.E, self.H, self.owner)
        self.assertEqual(ideal["state"], "both_match")

    def test_zero_nonfinite_wrong_shapes_and_invalid_feature_guards(self):
        for latent in (np.zeros(16384), np.full(16384, np.nan), np.zeros((4,64,64)), np.ones(3)):
            result = core.scores(latent, self.E, self.H, self.owner)
            self.assertEqual(result["state"], "invalid_measurement")
            self.assertTrue(result["errors"])
        for bad_e in (np.zeros(512), 2*self.E, self.E[:511], np.full(512, np.nan), self.E.astype(complex)+1j):
            with self.assertRaises(ValueError):
                core.template(bad_e, self.H, self.owner)
            self.assertEqual(core.scores(np.ones(16384), bad_e, self.H, self.owner)["state"],
                             "invalid_measurement")
        for bad_h in (-1, 2**32, True, 5.0):
            with self.assertRaises(ValueError):
                core.template(self.E, bad_h, self.owner)
        with self.assertRaises(ValueError):
            core.template(self.E, self.H, "unknown-owner")
        rounded = core.template(self.E.astype(np.float32), np.uint32(self.H), self.owner)
        self.assertAlmostEqual(np.mean(rounded["T"]**2), 1, places=13)

    def test_zero_projection_is_rejected_and_uninformative_bound_is_null(self):
        original = core.fwht
        with patch.object(core, "fwht", side_effect=lambda a: np.zeros_like(a) if len(a)==16384 else original(a)):
            with self.assertRaisesRegex(ValueError, "projection"):
                core.template(self.E, self.H, self.owner)
        original_projection = core._projection
        def twice_projection(*args):
            x, u, p, norm = original_projection(*args)
            return x, u, 2*p, 4*norm
        with patch.object(core, "_projection", side_effect=twice_projection):
            result = core.projection_diagnostic(self.E, self.H, self.F, 0, self.owner)
            self.assertGreaterEqual(result["delta"], 1)
            self.assertIsNone(result["normalization_error_bound"])

    def test_reference_free_api_and_plain_json_scalar_results(self):
        import json
        self.assertEqual(tuple(inspect.signature(core.template).parameters), ("E", "H", "owner"))
        self.assertEqual(tuple(inspect.signature(core.scores).parameters), ("zflat", "E", "H", "owner"))
        measured = core.scores(np.zeros(16384), self.E, self.H, self.owner)
        json.dumps(measured, allow_nan=False)
        diagnostic = core.projection_diagnostic(self.E, self.H, self.F, 0, self.owner)
        json.dumps(diagnostic, allow_nan=False)


if __name__ == "__main__":
    unittest.main()

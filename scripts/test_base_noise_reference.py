"""Synthetic A6 byte/numeric test vectors; no images or model execution."""

import hashlib
import math
import struct
import unittest

from base_noise_reference import base_noise_f32le


SOURCE = "00" * 32


class BaseNoiseReferenceTests(unittest.TestCase):
    def test_known_answer_and_channel_order(self):
        raw = base_noise_f32le(7, SOURCE, 1, 2, 3)
        self.assertEqual(len(raw), 24)
        self.assertTrue(all(math.isfinite(v) for v in struct.unpack("<6f", raw)))
        self.assertEqual(raw, base_noise_f32le(7, SOURCE, 1, 2, 3))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "1180bb2e44603d3f0db122e8cd0024ec25762ab5df5ad36255df48ebae8a94cd")
        self.assertEqual(struct.unpack("<6f", raw),
                         (0.17093929648399353, 0.9753754734992981,
                          -1.220534324645996, -0.574219286441803,
                          0.6080271005630493, 0.3844108581542969))

    def test_odd_count_and_domain_separation(self):
        first = base_noise_f32le(7, SOURCE, 1, 1, 3)
        self.assertEqual(len(first), 12)
        self.assertNotEqual(first, base_noise_f32le(8, SOURCE, 1, 1, 3))
        self.assertNotEqual(first, base_noise_f32le(7, "01" + "00" * 31, 1, 1, 3))
        self.assertNotEqual(first, base_noise_f32le(7, SOURCE, 3, 1, 1))

    def test_invalid_inputs_fail_before_allocation(self):
        for seed in (-1, 2**64, True, 1.0):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                base_noise_f32le(seed, SOURCE, 1, 1, 1)
        for digest in ("A" * 64, "0" * 63, "gg" * 32, None):
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                base_noise_f32le(0, digest, 1, 1, 1)
        for dims in ((0, 1, 1), (1, True, 1), (1, 1, 2**32), (1, 1001, 1001)):
            with self.subTest(dims=dims), self.assertRaises(ValueError):
                base_noise_f32le(0, SOURCE, *dims)


if __name__ == "__main__":
    unittest.main()

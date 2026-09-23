"""Synthetic B2 comparator reference tests; no datasets or model weights."""

import math
import unittest

from pixel_dct_control import dct8, embed_pixel_dct, idct8


class PixelDCTControlTests(unittest.TestCase):
    def test_orthonormal_transform_round_trip_and_dc(self):
        block = tuple(tuple((x + 8 * y) / 63 for x in range(8)) for y in range(8))
        coefficients = dct8(block)
        restored = idct8(coefficients)
        self.assertAlmostEqual(coefficients[0][0], 8 * (sum(map(sum, block)) / 64), places=12)
        self.assertLess(max(abs(block[y][x] - restored[y][x])
                            for y in range(8) for x in range(8)), 1e-12)

    def test_zero_gain_is_byte_identical_and_insert_is_deterministic(self):
        width, height = 33, 35  # exercises replicated right/bottom block padding
        source = bytes((80 + x % 31 for x in range(width * height * 3)))
        blocks = math.ceil(width / 8) * math.ceil(height / 8)
        semantic = tuple((1, -1, 1, -1) for _ in range(blocks))
        instance = tuple((-1, 1, -1, 1) for _ in range(blocks))
        args = (source, width, height, semantic, instance)
        self.assertEqual(embed_pixel_dct(*args, 0, 0), source)
        marked = embed_pixel_dct(*args, .25, .25)
        self.assertEqual(len(marked), len(source))
        self.assertNotEqual(marked, source)
        self.assertEqual(marked, embed_pixel_dct(*args, .25, .25))

    def test_rejects_bad_dimensions_templates_and_gains(self):
        source = bytes(32 * 32 * 3)
        signs = tuple((1, -1, 1, -1) for _ in range(16))
        args = (source, 32, 32, signs, signs)
        with self.assertRaises(ValueError):
            embed_pixel_dct(source, 31, 32, signs, signs, .1, .1)
        with self.assertRaises(ValueError):
            embed_pixel_dct(source[:-1], 32, 32, signs, signs, .1, .1)
        with self.assertRaises(ValueError):
            embed_pixel_dct(source, 32, 32, signs[:-1], signs, .1, .1)
        with self.assertRaises(ValueError):
            embed_pixel_dct(source, 32, 32, signs, signs[:-1] + ((0, 1, 1, 1),), .1, .1)
        for gain in (-1, float("nan"), float("inf"), True):
            with self.subTest(gain=gain), self.assertRaises(ValueError):
                embed_pixel_dct(*args, gain, .1)


if __name__ == "__main__":
    unittest.main()

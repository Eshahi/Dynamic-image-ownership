"""Synthetic B2 comparator reference tests; no datasets or model weights."""

import math
import unittest

from pixel_dct_control import dct8, embed_pixel_dct, idct8, score_pixel_dct, templates_from_keys


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

    def test_a5_template_packing_bit_order_and_domain_separation(self):
        semantic_key = bytes(range(32))
        instance_key = bytes(range(32, 64))
        config_id = bytes([0xA5]) * 32
        semantic, instance = templates_from_keys(semantic_key, instance_key, config_id, 32, 32)
        # Independently fixed SHAKE256 vector: first eight bytes are
        # b3306f2f582956c0 for the packed semantic input above.
        self.assertEqual(semantic[:4], ((1, 1, -1, -1), (1, 1, -1, 1),
                                        (-1, -1, -1, -1), (1, 1, -1, -1)))
        self.assertEqual(len(semantic), 16)
        self.assertEqual(len(instance), 16)
        self.assertNotEqual(semantic, instance)
        self.assertNotEqual(semantic, templates_from_keys(semantic_key, instance_key,
                                                          config_id, 33, 32)[0])
        self.assertNotEqual(templates_from_keys(semantic_key, instance_key, config_id, 33, 32)[0],
                            templates_from_keys(semantic_key, instance_key, config_id, 34, 32)[0])
        self.assertNotEqual(semantic, templates_from_keys(bytes([1]) + semantic_key[1:],
                                                          instance_key, config_id, 32, 32)[0])
        self.assertNotEqual(semantic, templates_from_keys(semantic_key, instance_key,
                                                          bytes(31) + b"x", 32, 32)[0])
        source = bytes([128] * (32 * 32 * 3))
        self.assertNotEqual(embed_pixel_dct(source, 32, 32, semantic, instance, .1, .1), source)

    def test_a5_template_rejects_hex_text_and_bad_digests(self):
        key = bytes(32)
        for malformed in ("00" * 32, bytes(31), bytearray(32), None):
            with self.subTest(value=type(malformed).__name__), self.assertRaises(ValueError):
                templates_from_keys(malformed, key, key, 32, 32)
        for width, height in ((31, 32), (32, 0), (True, 32), (0x100000000, 32)):
            with self.subTest(size=(width, height)), self.assertRaises(ValueError):
                templates_from_keys(key, key, key, width, height)

    def test_synthetic_component_score_and_zero_variance_veto(self):
        source = bytes([128] * (32 * 32 * 3))
        semantic, instance = templates_from_keys(bytes(range(32)), bytes(range(32, 64)),
                                                  bytes([0xA5]) * 32, 32, 32)
        self.assertEqual(score_pixel_dct(source, 32, 32, semantic, "semantic"), (0.0, True))
        self.assertEqual(score_pixel_dct(source, 32, 32, instance, "instance"), (0.0, True))
        marked = embed_pixel_dct(source, 32, 32, semantic, instance, .2, .2)
        for template, component in ((semantic, "semantic"), (instance, "instance")):
            with self.subTest(component=component):
                score, veto = score_pixel_dct(marked, 32, 32, template, component)
                self.assertFalse(veto)
                self.assertGreater(score, .9)
        flat_template = tuple((1, 1, 1, 1) for _ in range(16))
        self.assertEqual(score_pixel_dct(marked, 32, 32, flat_template, "semantic"),
                         (0.0, True))
        with self.assertRaises(ValueError):
            score_pixel_dct(marked, 32, 32, semantic, "unknown")


if __name__ == "__main__":
    unittest.main()

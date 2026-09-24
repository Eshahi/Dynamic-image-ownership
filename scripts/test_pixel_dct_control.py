"""Synthetic B2 comparator reference tests; no datasets or model weights."""

import hashlib
import math
import unittest
from unittest.mock import patch

import pixel_dct_control as control

from pixel_dct_control import (
    dct8, embed_pixel_dct, evaluate_pixel_control_candidates, idct8,
    keys_from_codes, phash_from_rgb8,
    score_pixel_dct, semantic_code_from_normalized_embedding,
    templates_from_keys,
)


class PixelDCTControlTests(unittest.TestCase):
    def test_a5_semantic_projection_one_hot_bit_order(self):
        seed = bytes(range(32))
        one_hot = (1.0,) + (0.0,) * 511
        domain = b"a5-semproj-v1"
        payload = (len(domain).to_bytes(4, "big") + domain
                   + len(seed).to_bytes(4, "big") + seed)
        stream = hashlib.shake_256(payload).digest(12 * 512 // 8)
        expected = sum(1 << row for row in range(12)
                       if not (stream[row * 64] & 1)).to_bytes(2, "little")
        actual = semantic_code_from_normalized_embedding(one_hot, seed)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[1] & 0xF0, 0)
        self.assertEqual(
            semantic_code_from_normalized_embedding((-1.0,) + (0.0,) * 511, seed),
            (int.from_bytes(actual, "little") ^ 0xFFF).to_bytes(2, "little"),
        )

    def test_a5_semantic_projection_rejects_noncanonical_input(self):
        seed = bytes(32)
        valid = (1.0,) + (0.0,) * 511
        for malformed in (valid[:-1], list(valid), (0.0,) * 512,
                          (float("nan"),) + valid[1:], (True,) + valid[1:]):
            with self.subTest(kind=type(malformed).__name__), self.assertRaises(ValueError):
                semantic_code_from_normalized_embedding(malformed, seed)
        for malformed in (bytes(31), "00" * 32, bytearray(32)):
            with self.subTest(seed=type(malformed).__name__), self.assertRaises(ValueError):
                semantic_code_from_normalized_embedding(valid, malformed)

    def test_phash_constant_and_invalid_canonical_buffer(self):
        for width, height in ((32, 32), (33, 35), (64, 32)):
            with self.subTest(size=(width, height)):
                self.assertEqual(phash_from_rgb8(bytes([23, 45, 67]) * (width * height),
                                                 width, height), bytes(4))
        with self.assertRaises(ValueError):
            phash_from_rgb8(bytes(32 * 32 * 3 - 1), 32, 32)

    def test_phash_against_direct_two_dimensional_dct_vector(self):
        # An independent, unoptimized 2-D summation on a non-symmetric 32x32
        # RGB vector checks transform axes, median set, position order and bits.
        width = height = 32
        source = bytes(channel
                       for y in range(height) for x in range(width)
                       for channel in ((3 * x + 7 * y) % 256,
                                       (5 * x + 11 * y) % 256,
                                       (13 * x + 17 * y) % 256))
        gray = [[sum(weight * source[3 * (y * width + x) + channel] / 255
                     for channel, weight in enumerate((.299, .587, .114)))
                 for x in range(width)] for y in range(height)]
        cosine = [[math.cos(math.pi * (n + .5) * k / 32) for n in range(32)]
                  for k in range(8)]
        coefficient = {}
        for u in range(8):
            for v in range(8):
                if (u, v) == (0, 0):
                    continue
                scale = (math.sqrt(1 / 32) if u == 0 else math.sqrt(2 / 32)) * (
                    math.sqrt(1 / 32) if v == 0 else math.sqrt(2 / 32))
                coefficient[(u, v)] = scale * math.fsum(
                    gray[y][x] * cosine[u][y] * cosine[v][x]
                    for y in range(32) for x in range(32)
                )
        median = sorted(coefficient.values())[31]
        positions = sorted(coefficient, key=lambda pair: (sum(pair), pair[0], pair[1]))[:32]
        expected = sum(1 << index for index, position in enumerate(positions)
                       if coefficient[position] > median).to_bytes(4, "little")
        self.assertEqual(phash_from_rgb8(source, width, height), expected)
        self.assertEqual(len(phash_from_rgb8(source, width, height)), 4)

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

    def test_a5_public_signature_serialization_vector(self):
        q, phash = bytes.fromhex("a503"), bytes.fromhex("12345678")
        semantic_key, instance_key = keys_from_codes(q, phash, "thesis:owner:09")
        self.assertEqual(semantic_key.hex(),
                         "a78246e2ca130a081f3662f285aca26943108c7c62e98b8538a22f8248e73a24")
        self.assertEqual(instance_key.hex(),
                         "f2cc43448a9bcd2ecace0be3c51d0c0c256293d27661c9e549105a58be97a000")
        self.assertNotEqual(semantic_key, keys_from_codes(q, phash, "thesis:owner:10")[0])
        self.assertNotEqual(instance_key, keys_from_codes(q, bytes(4), "thesis:owner:09")[1])
        templates = templates_from_keys(semantic_key, instance_key, bytes([0xA5]) * 32, 32, 32)
        source = bytes([128] * (32 * 32 * 3))
        marked = embed_pixel_dct(source, 32, 32, *templates, .2, .2)
        self.assertGreater(score_pixel_dct(marked, 32, 32, templates[0], "semantic")[0], .9)

    def test_a5_public_signature_rejects_ambiguous_inputs(self):
        q, phash = bytes.fromhex("a503"), bytes(4)
        for malformed in (b"", b"\x00", b"\x00\xf0", "a503"):
            with self.subTest(q=malformed), self.assertRaises(ValueError):
                keys_from_codes(malformed, phash, "owner")
        for malformed in (bytes(3), "00000000"):
            with self.subTest(phash=malformed), self.assertRaises(ValueError):
                keys_from_codes(q, malformed, "owner")
        for malformed in ("", "e\u0301", "a" * 257, None, "\ud800"):
            with self.subTest(owner=repr(malformed)), self.assertRaises(ValueError):
                keys_from_codes(q, phash, malformed)

    def test_supplied_suspect_codes_search_with_one_image_dct_pass(self):
        q, phash = bytes.fromhex("a503"), bytes.fromhex("12345678")
        owner, config_id = "thesis:owner:09", bytes([0xA5]) * 32
        keys = keys_from_codes(q, phash, owner)
        templates = templates_from_keys(*keys, config_id, 32, 32)
        marked = embed_pixel_dct(bytes([128] * (32 * 32 * 3)), 32, 32,
                                 *templates, .2, .2)
        with patch.object(control, "dct8", wraps=control.dct8) as dct:
            result = evaluate_pixel_control_candidates(
                marked, 32, 32, q, phash, owner, config_id, .85, .85)
        self.assertEqual(dct.call_count, 16)
        self.assertEqual((result["semantic_candidates"], result["instance_candidates"]), (13, 429))
        self.assertTrue(result["both_match"])
        self.assertEqual(result["first_joint_candidate"], {"q": q.hex(), "h": phash.hex()})

    def test_cached_score_rejects_nonfinite_and_unbounded_observations(self):
        template = ((1, -1, 1, -1),)
        for value in (float("nan"), float("inf"), True, 10**1000):
            with self.subTest(value=type(value).__name__), self.assertRaises(ValueError):
                control.score_observations(((value, 0, 0, 0),), template)


if __name__ == "__main__":
    unittest.main()

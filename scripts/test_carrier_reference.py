"""Synthetic tests for A5 carrier domain, bit order and float32 framing."""

import hashlib
import math
import struct
import unittest

from base_noise_reference import unit_carrier_f32le


SIGNATURE = "01" * 32
CONFIG = "ab" * 32


class CarrierReferenceTests(unittest.TestCase):
    def test_known_answer_and_sign_order(self):
        raw = unit_carrier_f32le("s", SIGNATURE, 7, 2, 2, 3, CONFIG)
        self.assertEqual(len(raw), 48)
        self.assertEqual(raw, unit_carrier_f32le("s", SIGNATURE, 7, 2, 2, 3, CONFIG))
        values = struct.unpack("<12f", raw)
        amplitude = struct.unpack("<f", struct.pack("<f", 1 / math.sqrt(12)))[0]
        self.assertTrue(all(abs(value) == amplitude for value in values))
        self.assertLess(abs(sum(value * value for value in values) - 1), 2e-7)
        self.assertEqual("".join("1" if value > 0 else "0" for value in values),
                         "000100110011")
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "39c035801126715dbc0cd021b60ff6406b2ae6254cf6d140be099415a90ecb32")

    def test_distinct_carrier_domains_and_shape(self):
        first = unit_carrier_f32le("s", SIGNATURE, 7, 2, 2, 3, CONFIG)
        self.assertNotEqual(first, unit_carrier_f32le("i", SIGNATURE, 7, 2, 2, 3, CONFIG))
        self.assertNotEqual(first, unit_carrier_f32le("s", "02" * 32, 7, 2, 2, 3, CONFIG))
        self.assertNotEqual(first, unit_carrier_f32le("s", SIGNATURE, 8, 2, 2, 3, CONFIG))
        self.assertNotEqual(first, unit_carrier_f32le("s", SIGNATURE, 7, 2, 2, 3, "cd" * 32))
        self.assertNotEqual(first, unit_carrier_f32le("s", SIGNATURE, 7, 2, 3, 2, CONFIG))

    def test_invalid_inputs_fail_closed(self):
        for component in ("S", "", "x", None, 1):
            with self.subTest(component=component), self.assertRaises(ValueError):
                unit_carrier_f32le(component, SIGNATURE, 7, 1, 1, 1, CONFIG)
        for signature in ("0" * 63, "G" * 64, None):
            with self.subTest(signature=signature), self.assertRaises(ValueError):
                unit_carrier_f32le("s", signature, 7, 1, 1, 1, CONFIG)
        with self.assertRaises(ValueError):
            unit_carrier_f32le("s", SIGNATURE, 7, 1, 1, 1, "F" * 64)
        with self.assertRaises(ValueError):
            unit_carrier_f32le("s", SIGNATURE, 7, 1, 1001, 1001, CONFIG)


if __name__ == "__main__":
    unittest.main()

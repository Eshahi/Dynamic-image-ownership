"""Model-free contract tests for TrustMark Q/BCH_5 comparison semantics."""

import unittest

from trustmark_profile import classify_decode, payload_for_image, wrong_payload


SEED = "0123456789abcdef" * 4


class TrustMarkProfileTests(unittest.TestCase):
    def test_payload_is_reproducible_and_domain_separated(self):
        first = payload_for_image(SEED, "COCO", "2017-val", "000001")
        self.assertEqual(len(first), 61)
        self.assertRegex(first, r"^[01]{61}$")
        self.assertEqual(first,
                         "0101000111111011101101101001010010111001110100010110110101101")
        self.assertEqual(first, payload_for_image(SEED, "COCO", "2017-val", "000001"))
        self.assertNotEqual(first, payload_for_image(SEED, "COCO", "2017-val", "000002"))
        self.assertNotEqual(first, payload_for_image(SEED, "COCO", "2017-train", "000001"))
        self.assertNotEqual(first, payload_for_image(SEED, "X", "YZ", "A"))
        self.assertNotEqual(payload_for_image(SEED, "X", "YZ", "A"),
                            payload_for_image(SEED, "XY", "Z", "A"))

    def test_payload_rejects_ambiguous_inputs(self):
        for seed in ("0" * 63, "A" * 64, "g" * 64, None):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                payload_for_image(seed, "COCO", "2017", "id")
        for image_id in ("", " id", "id ", None):
            with self.subTest(image_id=image_id), self.assertRaises(ValueError):
                payload_for_image(SEED, "COCO", "2017", image_id)

    def test_presence_is_not_attribution_or_continuous_score(self):
        expected = payload_for_image(SEED, "COCO", "2017", "id")
        other = wrong_payload(expected)
        self.assertNotEqual(other, expected)
        self.assertEqual(classify_decode(expected, True, 1, expected),
                         {"ecc_valid": True, "payload_match": True,
                          "status": "MATCH", "score": None})
        self.assertEqual(classify_decode(other, True, 1, expected)["status"],
                         "VALID_OTHER_PAYLOAD")
        self.assertFalse(classify_decode(other, False, 1, expected)["ecc_valid"])
        self.assertEqual(classify_decode("", False, -1, expected)["status"],
                         "NO_VALID_BCH_5")

    def test_malformed_or_wrong_profile_fails_closed(self):
        expected = "0" * 61
        for decoded, detected, version in (("0" * 60, True, 1),
                                           (expected, True, 2),
                                           (expected, 1, 1),
                                           (expected, False, 2),
                                           ("abc", False, -1)):
            with self.subTest(decoded=decoded, detected=detected, version=version):
                with self.assertRaises(ValueError):
                    classify_decode(decoded, detected, version, expected)


if __name__ == "__main__":
    unittest.main()

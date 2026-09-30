import unittest

try:
    from revised_watermark import DEFAULT_PROFILE, detect, embed, mse, payload_bits, perceptual_bits, validate_profile
except ModuleNotFoundError:
    from scripts.revised_watermark import DEFAULT_PROFILE, detect, embed, mse, payload_bits, perceptual_bits, validate_profile


def texture(size=160, offset=0):
    return [[float((x * 17 + y * 29 + ((x * y) % 37) + offset) % 256) for x in range(size)] for y in range(size)]


class RevisedWatermarkTests(unittest.TestCase):
    def test_round_trip_is_detectable_and_deterministic(self):
        image = texture()
        profile = validate_profile(DEFAULT_PROFILE)
        first = embed(image, "owner-alpha", profile=profile)
        second = embed(image, "owner-alpha", profile=profile)
        self.assertEqual(first, second)
        result = detect(first, "owner-alpha", profile=profile)
        self.assertTrue(result["present"], result)
        self.assertGreaterEqual(result["owner_accuracy"], 0.75)
        self.assertGreaterEqual(result["instance_accuracy"], 0.75)
        self.assertLess(mse(image, first), 6.0)

    def test_profile_rejects_out_of_contract_step(self):
        profile = dict(DEFAULT_PROFILE)
        profile["qim_step"] = 33.0
        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_wrong_owner_is_rejected(self):
        marked = embed(texture(), "owner-alpha")
        result = detect(marked, "owner-beta")
        self.assertFalse(result["present"], result)
        self.assertLess(result["owner_accuracy"], 0.75)

    def test_small_pixel_noise_survives(self):
        marked = embed(texture(), "owner-alpha")
        noisy = [
            [min(255.0, max(0.0, round(value) + ((x * 13 + y * 7) % 3 - 1))) for x, value in enumerate(row)]
            for y, row in enumerate(marked)
        ]
        result = detect(noisy, "owner-alpha")
        self.assertTrue(result["present"], result)

    def test_content_binding_changes_with_content(self):
        source = texture()
        marked = embed(source, "owner-alpha")
        changed = texture(offset=71)
        altered_marked = [row[:] for row in marked]
        for y in range(120):
            altered_marked[y][:120] = changed[y][:120]
        result = detect(altered_marked, "owner-alpha")
        self.assertFalse(result["present"], result)
        self.assertNotEqual(perceptual_bits(source), perceptual_bits(changed))

    def test_invalid_small_input_is_rejected(self):
        with self.assertRaises(ValueError):
            embed([[0.0] * 32 for _ in range(32)], "owner-alpha")

    def test_clipping_limited_flat_inputs_are_explicit_failures(self):
        for value in (0.0, 127.0, 255.0):
            with self.assertRaises(ValueError):
                embed([[value] * 160 for _ in range(160)], "owner-alpha")

    def test_binding_has_declared_width(self):
        value = perceptual_bits(texture())
        self.assertGreaterEqual(value, 0)
        self.assertLess(value, 1 << 16)
        self.assertEqual(len(payload_bits("owner-alpha", texture())), 72)


if __name__ == "__main__":
    unittest.main()

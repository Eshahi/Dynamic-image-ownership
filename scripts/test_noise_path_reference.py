"""Ordinary algebra/guard unit tests; not scientific feasibility experiments."""
import math
import unittest
from noise_path_reference import add_initial_noise, eta_zero_step, leading_suffix


class NoisePathTests(unittest.TestCase):
    def test_leading_suffix(self):
        self.assertEqual(leading_suffix(50, 0.1), [81, 61, 41, 21, 1])
        self.assertEqual(leading_suffix(4, 1), [751, 501, 251, 1])
        self.assertEqual(leading_suffix(1, 1), [1])

    def test_schedule_rejections(self):
        for steps, strength in [(1000, 1), (0, 1), (True, 1), (2.0, 1),
                                (50, 0.001), (50, 0), (50, 1.01),
                                (50, float('nan')), (50, True)]:
            with self.subTest(steps=steps, strength=strength), self.assertRaises(ValueError):
                leading_suffix(steps, strength)

    def test_noise_variable_scaling(self):
        original = add_initial_noise(2, 3, 0, 0.64)
        marked = add_initial_noise(2, 3, 0.5, 0.64)
        self.assertAlmostEqual(original, 3.4)
        self.assertAlmostEqual(marked - original, 0.3)

    def test_eta_zero_consistency(self):
        # Construct a scalar sample from a known clean component and noise.
        sample = add_initial_noise(2, 3, 0, 0.64)
        expected = add_initial_noise(2, 3, 0, 0.81)
        self.assertAlmostEqual(eta_zero_step(sample, 3, 0.64, 0.81), expected)

    def test_final_alpha_is_not_implicitly_one(self):
        a0 = 1 - 0.00085
        sample = add_initial_noise(2, 3, 0, 0.9)
        final = eta_zero_step(sample, 3, 0.9, a0)
        self.assertAlmostEqual(final, math.sqrt(a0) * 2 + math.sqrt(1-a0) * 3)
        self.assertNotAlmostEqual(final, 2)

    def test_scalar_guards(self):
        for alpha in [0, -1, 1.1, float('inf'), True]:
            with self.subTest(alpha=alpha), self.assertRaises(ValueError):
                add_initial_noise(0, 0, 0, alpha)
        with self.assertRaises(ValueError):
            eta_zero_step(0, 0, 0.8, 0.7)
        with self.assertRaises(ValueError):
            eta_zero_step(float('nan'), 0, 0.8, 0.9)


if __name__ == '__main__':
    unittest.main()

"""CPU-only checks for the fixed A6 DCT probe's math and byte contract."""

import math
import unittest

from check_torch_dct_cuda import dct_basis, f32_digest, scalar_reference


class DctCudaReferenceTests(unittest.TestCase):
    def test_basis_is_orthonormal(self):
        basis = dct_basis()
        self.assertEqual(len(basis), 8)
        for row in basis:
            self.assertEqual(len(row), 8)
        for a in range(8):
            for b in range(8):
                self.assertAlmostEqual(sum(basis[a][n] * basis[b][n]
                                           for n in range(8)), float(a == b), places=12)

    def test_digest_contract_rejects_nonfinite_values(self):
        self.assertEqual(len(f32_digest([0.0, 1.0, -1.0])), 64)
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                f32_digest([value])

    def test_scalar_probe_shape_and_gradient(self):
        scores, gradient = scalar_reference()
        self.assertEqual((len(scores), len(gradient)), (4, 64))
        self.assertTrue(all(math.isfinite(value) for value in scores + gradient))
        self.assertTrue(any(value != 0 for value in gradient))


if __name__ == "__main__":
    unittest.main()

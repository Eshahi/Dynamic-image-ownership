import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_phase_residual as residual

class ResidualTests(unittest.TestCase):
    def test_rgb8_cap_and_infeasible_upper(self):
        source=np.full((7,9,3),128,dtype=np.uint8)
        delta=np.random.default_rng(9).normal(size=source.shape)*.2
        marked,receipt=residual.cap(source,delta)
        self.assertLess(receipt['weight'],1)
        self.assertEqual(receipt['iterations'],36)
        self.assertLessEqual(residual.pixel_sse(source,marked)/source.size,receipt['budget_mse_rgb8'])
        self.assertGreater(residual.pixel_sse(source,residual.compose(source,delta,receipt['hi']))/source.size,receipt['budget_mse_rgb8'])
    def test_zero_is_valid_noop(self):
        source=np.arange(60,dtype=np.uint8).reshape(4,5,3)
        marked,receipt=residual.cap(source,np.zeros_like(source,dtype=float))
        np.testing.assert_array_equal(marked,source)
        self.assertEqual(receipt['weight'],1)
        self.assertEqual(receipt['sse_rgb8'],0)
    def test_clipping_and_rounding_are_monotone_in_distortion(self):
        rng=np.random.default_rng(3);source=rng.integers(0,256,(11,13,3),dtype=np.uint8);delta=rng.normal(size=source.shape)
        values=[residual.pixel_sse(source,residual.compose(source,delta,float(w))) for w in np.linspace(0,1,65)]
        self.assertEqual(values,sorted(values))
    def test_signed_pixel_math_not_uint8_wrap(self):
        self.assertEqual(residual.pixel_sse(np.array([0],np.uint8),np.array([255],np.uint8)),65025)
    def test_reject_nonfinite_and_shape(self):
        source=np.zeros((2,2,3),np.uint8)
        for delta in (np.ones((2,2)),np.full(source.shape,np.nan)):
            with self.assertRaises(ValueError):residual.cap(source,delta)
    def test_inventory_keeps_duplicates_logically(self):
        rows=residual.planned()
        self.assertEqual(len(rows),32)
        self.assertEqual(len({r['id'] for r in rows}),32)
        self.assertEqual(sum(r['control']=='C0' for r in rows),16)

if __name__=='__main__':unittest.main()

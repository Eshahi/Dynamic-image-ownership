"""Boundary and accounting tests without GPU or private enrollment."""
import inspect
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_blind_noise as candidate
import m1_blind_noise_core as core

class BoundaryTests(unittest.TestCase):
    def test_fixed_inventory_and_manifest(self):
        rows=candidate.planned()
        self.assertEqual(len(rows),48)
        self.assertEqual(len({r['id'] for r in rows}),48)
        self.assertEqual(candidate.config(),json.loads((candidate.ROOT/'research/m1-blind-noise-dev.json').read_text()))
        self.assertEqual(candidate.config()['data_split'],'development')

    def test_bypass_preserves_exact_source_for_zero_delta(self):
        rng=np.random.default_rng(12)
        source=rng.integers(0,256,(512,512,3),dtype=np.uint8)
        decoded=rng.random(source.shape,dtype=np.float32)
        np.testing.assert_array_equal(candidate.bypass(source,decoded,decoded),source)

    def test_float_difference_is_not_difference_of_rounded_images(self):
        source=np.full((512,512,3),128,np.uint8)
        baseline=np.full(source.shape,100.49/255)
        marked=np.full(source.shape,100.51/255)
        np.testing.assert_array_equal(candidate.bypass(source,marked,baseline),source)
        self.assertFalse(np.array_equal(candidate.rgb8(marked),candidate.rgb8(baseline)))

    def test_blind_boundary_uses_only_public_observations(self):
        E=np.zeros(512);E[0]=1
        H=123
        z=np.random.default_rng(7).normal(size=16384)
        class Public:
            def observations(self,rgb):return E,H,z
        image=np.zeros((512,512,3),np.uint8)
        owner=core.OWNERS[0]
        self.assertEqual(candidate.detect(image,owner,Public()),core.scores(z,E,H,owner))
        self.assertEqual(len(inspect.signature(candidate.detect).parameters),3)
        with self.assertRaises(ValueError):candidate.detect(image.astype(float),owner,Public())

    def test_nonfinite_and_wrong_geometry_rejected(self):
        for value in (np.zeros((4,4,3)),np.full((512,512,3),np.nan)):
            with self.assertRaises(ValueError):candidate.rgb8(value)

if __name__=='__main__':unittest.main()

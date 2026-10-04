"""Pinned generated-byte arithmetic, no models or CUDA initialization."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
import torch
import m1_target_normalization_audit as m
import m1_source_initialization as init


class NormalizationTests(unittest.TestCase):
    def test_all256_symbols_match_independent_numpy_multiply(self):
        rgb=np.resize(np.arange(256,dtype=np.uint8),(512,512,3))
        with patch.object(torch.cuda,'_lazy_init',side_effect=AssertionError('CUDA forbidden')):
            actual=m.target_from_rgb8(rgb,m.POLICY)
        expected=torch.from_numpy(rgb.astype(np.float32)*np.float32(1/255)).permute(2,0,1)[None]
        self.assertTrue(torch.equal(actual,expected));self.assertEqual(actual.dtype,torch.float32)
        self.assertEqual(str(actual.device),'cpu')
        self.assertEqual(int(np.asarray(np.float32(1/255)).view(np.uint32)),0x3b808081)

    def test_generated0_exact_recorded_gpu_digest_without_hash_selection(self):
        from m1_candidate_rehearsal_worker import generated_source
        source,_,_=generated_source(0)
        actual=m.target_from_rgb8(source,m.POLICY)
        direct=torch.from_numpy(source.copy()).permute(2,0,1)[None].float()/255
        self.assertEqual(init.digest(actual),'7c0be0278b495bdd73fcca76fda249e9c7737b1b26c9e4d67441eae60395482e')
        self.assertEqual(init.digest(direct),'5b685af1f0c49f8ef271f0f2ec54b4f21ff62f3674c3eff420445cdfccf6081c')
        self.assertEqual(int((actual!=direct).sum()),360408)
        self.assertEqual(float((actual-direct).abs().max()),2**-24)
        self.assertEqual(len(np.unique(source)),256)

    def test_unknown_runtime_and_noncanonical_input_rejected(self):
        source=np.zeros((512,512,3),np.uint8)
        for policy in [{},dict(m.POLICY,device='cpu'),dict(m.POLICY,torch_version='other'),dict(m.POLICY,cuda_version='other')]:
            with self.assertRaises(ValueError):m.target_from_rgb8(source,policy)
        for value in [source.astype(np.float32),source[:256],None]:
            with self.assertRaises(ValueError):m.target_from_rgb8(value,m.POLICY)

    def test_source_input_is_not_modified(self):
        source=np.resize(np.arange(256,dtype=np.uint8),(512,512,3));original=source.copy()
        result=m.target_from_rgb8(source,m.POLICY);result.fill_(0)
        self.assertTrue(np.array_equal(source,original))


if __name__=='__main__':unittest.main()

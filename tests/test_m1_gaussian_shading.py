"""Finite codec/channel checks; not scientific robustness evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import numpy as np
from m1_gaussian_shading import embed_signs, decode, payload_for, nonce_for


class CodecTests(unittest.TestCase):
    def test_exact_recovery_and_correlated_erasure_boundary(self):
        key="01"*32
        payload=payload_for(1000)
        nonce=nonce_for(1000)
        signs=embed_signs(payload,key,nonce)
        z=(2*signs.astype(float)-1).reshape(4,64,64)
        self.assertTrue(np.array_equal(payload,decode(z,key,nonce)))
        # Exactly31 of64 repeated tiles corrupted: correct strict majority.
        corrupted=z.copy().reshape(4,8,8,8,8)
        for n in range(31):
            corrupted[:,n//8,:,n%8,:]*=-1
        self.assertTrue(np.array_equal(payload,decode(corrupted,key,nonce)))
        # More than half tile errors kills all bits; no false ECC miracle.
        for n in range(31,33):
            corrupted[:,n//8,:,n%8,:]*=-1
        self.assertTrue(np.array_equal(1-payload,decode(corrupted,key,nonce)))

    def test_nonce_separation_and_wrong_key(self):
        p=payload_for(1000)
        key="01"*32
        a=embed_signs(p,key,nonce_for(1000))
        b=embed_signs(p,key,nonce_for(1001))
        self.assertFalse(np.array_equal(a,b))
        wrong=decode(2*a.astype(float)-1,"02"*32,nonce_for(1000))
        self.assertLess(float((wrong==p).mean()),.7)

    def test_invalid_latent(self):
        with self.assertRaises(ValueError):
            decode(np.zeros(100),"01"*32,nonce_for(1000))


if __name__=="__main__":
    unittest.main()

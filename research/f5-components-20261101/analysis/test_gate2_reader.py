"""Pure logic checks. No development outputs are read."""
import copy
import math
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import gate2_reader as b

def raw():
    t=dict(decoded_score=0.,decoded_code='00000000',recomputed_score=0.,read=False,content_match=False,found=False)
    return dict(semantic=copy.deepcopy(t),instance=copy.deepcopy(t),semantic_code='00000000',perceptual_hash='00000000')

class FixedReader(unittest.TestCase):
    def test_bound(self):
        v=b.validate_bound()
        self.assertLess(v['effective_radius_upper'],10)
        self.assertEqual(v['ball'],sum(math.comb(32,j) for j in range(10)))
    def test_threshold_inclusive(self):
        r=raw();r['semantic']['decoded_score']=b.THRESHOLD
        self.assertTrue(b.endpoints(r)['Bs'])
        r['semantic']['decoded_score']=math.nextafter(b.THRESHOLD,0)
        self.assertFalse(b.endpoints(r)['Bs'])
    def test_distance_ball(self):
        for score in (b.THRESHOLD,8.,10.,math.sqrt(320),20.):
            for d in range(33):
                r={'decoded_score':score,'decoded_code':f'{(1<<d)-1:08x}'}
                t=b.tier(r,'00000000')
                if t['passes']:self.assertLessEqual(d,9)
        self.assertEqual(b.corrected(6,20.),6.)
        self.assertTrue(b.tier({'decoded_score':20.,'decoded_code':'0000003f'},'00000000')['passes'])
        self.assertFalse(b.tier({'decoded_score':20.,'decoded_code':'0000007f'},'00000000')['passes'])
    def test_recomputed_only_excluded(self):
        r=raw();r['instance'].update(recomputed_score=8.,found=True,content_match=True)
        e=b.endpoints(r)
        self.assertTrue(e['O']);self.assertTrue(e['O_U']);self.assertFalse(e['B'])
    def test_veto_only_instance(self):
        r=raw();r['instance']['decoded_score']=10.
        self.assertTrue(b.endpoints(r)['B'])
        r['semantic'].update(read=True,content_match=False)
        self.assertFalse(b.endpoints(r)['B'])
        self.assertTrue(b.endpoints(r)['Bi'])
        r['semantic']['decoded_score']=10.
        self.assertTrue(b.endpoints(r)['B'])
    def test_frozen_preserved(self):
        e=b.endpoints(raw(),dict(C=True,J=True))
        self.assertTrue(e['C']);self.assertTrue(e['J']);self.assertFalse(e['B']);self.assertTrue(e['C_or_B'])
    def test_low_score_finite_nonaccept(self):
        self.assertIsNone(b.corrected(0,0))
        self.assertFalse(b.endpoints(raw())['B'])

if __name__=='__main__':unittest.main()

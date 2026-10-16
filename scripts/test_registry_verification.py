"""Scientific decision contracts, independent synthetic records only."""
import unittest
from registry_step2_screen import pointer, identify, auc
from registry_step2_enroll import classify

class RegistryContracts(unittest.TestCase):
    def test_pointer_requires_observed_read(self):
        self.assertFalse(pointer({'semantic':{'found':True,'read':False,'decoded_code':'00000000'}})['recovered'])
        self.assertFalse(pointer({'semantic':{'found':True,'read':True,'decoded_code':None}})['recovered'])
    def test_owner_radius_and_best_record(self):
        records=[dict(record_id='a',owner='alpha',q='00000000'),dict(record_id='b',owner='alpha',q='ffffffff'),dict(record_id='c',owner='beta',q='00000000')]
        pr=dict(recovered=True,q='00000001')
        result=identify([.7,.9,1.],records,.6,pr,6,'alpha')
        self.assertEqual(result['record_id'],'a');self.assertEqual(result['candidates'],1)
        self.assertEqual(identify([.7,.9,1.],records,.6)['record_id'],'c')
    def test_auc_ties(self):
        self.assertEqual(auc([1.,1.],[1.,1.]),.5)
        self.assertEqual(auc([.9],[.1]),1.)
    def test_competing_enrollment_not_ownership_transfer(self):
        from registry_step1_transfer import ALPHA,BETA
        records=[dict(record_id='alpha:1',owner=ALPHA,q='00000000',enrollment_index=0),dict(record_id='beta:1',owner=BETA,q='ffffffff',enrollment_index=1)]
        calls={ALPHA:{'semantic':{'found':True,'read':True,'decoded_code':'00000000'}},BETA:{'semantic':{'found':False,'read':False,'decoded_code':None}}}
        r=classify(records,[.8,1.],.7,calls,6)
        self.assertEqual(r['fingerprint_only']['best_record'],'beta:1')
        self.assertTrue(r['fingerprint_only']['enrollment_order_alone_can_favor_original_owner'])
        self.assertEqual(r['pointer_registry']['attribution'],'original_owner_unique')
        self.assertEqual(r['pointer_registry']['best_record'],'alpha:1')

if __name__=='__main__':unittest.main()

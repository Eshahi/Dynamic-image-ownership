import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_owner_extension_audit as audit
import m1_blind_noise_core as core


class OwnerAuditTests(unittest.TestCase):
    def test_exact_extended_owner_domain_without_aliases(self):
        self.assertEqual(len(core.ACCEPTED_OWNERS),20)
        self.assertEqual(core.OWNERS,core.ACCEPTED_OWNERS[:4])
        self.assertEqual(core.MAP_VERSION,core.VERSION)
        for owner in core.ACCEPTED_OWNERS:
            self.assertEqual(core._owner(owner),owner)
        for owner in (None,0,True,'','thesis:owner:0','thesis:owner:16',
                      'THESIS:OWNER:00','thesis:owner:00 ','thesis:owner:００'):
            with self.assertRaises(ValueError):core._owner(owner)

    def test_exact_comparator_rejects_tiny_changes_and_type_loss(self):
        a={'x':np.array([1.]),'value':1}
        audit.compare_exact(a,{'x':np.array([1.]),'value':1},'same')
        for b in ({'x':np.array([np.nextafter(1.,2.)]),'value':1},
                  {'x':np.array([1.],np.float32),'value':1},
                  {'x':np.array([1.]),'value':True}):
            with self.assertRaises(ValueError):audit.compare_exact(a,b,'changed')

    def test_hash_pinned_immutable_reference_and_rng_fixture(self):
        old,_=audit.load_reference()
        self.assertEqual(old.OWNERS,core.OWNERS)
        a=list(audit.fixtures());b=list(audit.fixtures())
        self.assertEqual(len(a),32)
        for x,y in zip(a,b):audit.compare_exact(x,y,'fixtures')
        rng=np.random.Generator(np.random.PCG64(0))
        e=rng.standard_normal(512);e/=np.linalg.norm(e)
        np.testing.assert_array_equal(e,a[0][0])

    def test_independent_geometry_guard_catches_variance_corruption(self):
        e,h,e2,h2,_=next(audit.fixtures());owner=core.OWNERS[0]
        p=core.template(e,h,owner);d=core.projection_diagnostic(e,h,e2,h2,owner)
        audit.geometry(e,h,e2,h2,owner,p,d)
        d['variance_inner']+=1e-6
        with self.assertRaises(ValueError):audit.geometry(e,h,e2,h2,owner,p,d)

    def test_exact_threshold_boundaries_and_abstentions(self):
        below=np.nextafter(4.,-np.inf);above=np.nextafter(4.,np.inf)
        self.assertEqual(core.classify_scores(4.,4.)['state'],'both_match')
        self.assertEqual(core.classify_scores(above,below)['state'],'semantic_only')
        self.assertEqual(core.classify_scores(below,4.)['state'],'ambiguous_instance_only')
        self.assertEqual(core.classify_scores(below,below)['state'],'neither_supported')
        self.assertEqual(core.classify_scores(None,above)['state'],'invalid_measurement')


if __name__=='__main__':unittest.main()

import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import m1_confirmatory_endpoints as m


class Endpoints(unittest.TestCase):
    def test_exact_boundary_identities_and_small_cohort(self):
        for n in (1, 12, 30, 300):
            self.assertAlmostEqual(m.bounds(0,n)['upper_one_sided'],1-0.05**(1/n),places=13)
            self.assertAlmostEqual(m.bounds(n,n)['lower_one_sided'],0.05**(1/n),places=13)
        self.assertLess(m.bounds(12,12)['lower_one_sided'],0.80)
        self.assertLess(m.bounds(0,300)['upper_one_sided'],0.01)
        self.assertGreater(m.bounds(1,300)['upper_one_sided'],0.01)

    def test_missing_is_adverse_in_both_directions(self):
        ids=[str(i) for i in range(300)]
        negatives={i:False for i in ids[:-1]}
        result=m.cell(ids,negatives,event_kind='negative_error')
        self.assertEqual((result['valid'],result['missing'],result['conservative_events']),(299,1,1))
        self.assertFalse(result['meets_numerical_target'])
        positives=m.cell(['a','b'],{'a':True,'b':None},event_kind='positive_success')
        self.assertEqual(positives['conservative']['rate'],0.5)
        self.assertEqual(positives['observed_valid']['rate'],1)

    def test_empty_not_pass_and_repeats_cannot_inflate_n(self):
        self.assertIsNone(m.cell([],{},event_kind='positive_success')['meets_numerical_target'])
        for ids,obs in [(['a','a'],{'a':True}),(['a'],{'b':True}),(['a'],{'a':1})]:
            with self.assertRaises(ValueError):m.cell(ids,obs,event_kind='positive_success')

    def test_binomial_duality_and_wilson_symmetry(self):
        for x in (1,7,19):
            a,b=m.bounds(x,20),m.bounds(20-x,20)
            self.assertAlmostEqual(a['lower_one_sided'],1-b['upper_one_sided'])
            self.assertAlmostEqual(a['wilson_two_sided'][0],1-b['wilson_two_sided'][1])


if __name__=='__main__':unittest.main()

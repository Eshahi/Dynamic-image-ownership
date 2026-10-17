"""Small scientific failure-mode tests independent of GPU and held-out data."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import m1b_registry_analysis as A


class RegistryAnalysisTests(unittest.TestCase):
    def records(self):
        return [dict(record_id='alpha:1', owner=A.ALPHA, q='00000000', enrollment_index=0),
                dict(record_id='beta:1', owner=A.BETA, q='00000000', enrollment_index=1)]

    def calls(self, beta=False):
        return {owner: dict(outcome='completed', detection=dict(semantic=dict(found=(owner == A.ALPHA or beta),
                    read=True, decoded_code='00000000'))) for owner in (A.ALPHA, A.BETA)}

    def test_pointer_filters_owner_while_fingerprint_retains_competing_copy(self):
        scores = [dict(d1=.8, b1=.99), dict(d1=1., b1=1.)]
        rule = lambda p: p['d1'] > .05 and p['b1'] >= .9
        pointer = A.attribution(self.records(), scores, self.calls(), rule)
        fingerprint = A.attribution(self.records(), scores, self.calls(), rule, False)
        self.assertEqual(pointer['attribution'], 'original_owner_unique')
        self.assertEqual(pointer['best_record'], 'alpha:1')
        self.assertEqual(fingerprint['best_record'], 'beta:1')
        self.assertTrue(fingerprint['enrollment_order_alone_can_favor_original_owner'])

    def test_ambiguous_wrong_owner_is_not_hidden(self):
        p = A.attribution(self.records(), [dict(d1=1., b1=1.)] * 2, self.calls(True), lambda _: True)
        self.assertEqual(p['attribution'], 'ambiguous_owners')
        self.assertTrue(p['wrong_owner_present'])

    def test_q_gate_exact_radius_and_unreadable(self):
        self.assertTrue(A.qmatch('0000003f', '00000000'))
        self.assertFalse(A.qmatch('0000007f', '00000000'))
        self.assertIsNone(A.native_q(dict(detection=dict(semantic=dict(found=True, read=False, decoded_code='00')))))

    def test_missing_similarity_never_matches(self):
        p = A.attribution(self.records(), [None, None], self.calls(True), lambda _: True)
        self.assertEqual(p['match_count'], 0)
        self.assertEqual(p['attribution'], 'no_attribution')

    def test_zero_false_accept_cluster_bound(self):
        self.assertAlmostEqual(A.upper95(0, 300), 1 - .05 ** (1 / 300))
        self.assertIsNone(A.upper95(0, 0))

    def test_near_offsets_share_shot_and_ambiguous_is_excluded(self):
        near = [dict(pair_id='a72', shot='a'), dict(pair_id='a144', shot='a'),
                dict(pair_id='b72', shot='b'), dict(pair_id='c72', shot='c')]
        distances = dict(a72=15., a144=14., b72=27., c72=16.)
        self.assertEqual(A.near_clusters(near, distances, 18., True, ['near:a72', 'near:a144', 'near:b72']), (2, 1))
        self.assertEqual(A.near_clusters(near, distances, 18., False, ['near:b72']), (1, 1))


if __name__ == '__main__':
    unittest.main()

"""Synthetic contract vectors for bounded q/H search and common-q matching."""

import unittest

from candidate_search_reference import candidates, evaluate


Q = bytes.fromhex("a503")
H = bytes.fromhex("12345678")


class CandidateSearchTests(unittest.TestCase):
    def test_radius_one_order_and_cardinality(self):
        q = candidates(Q, 12)
        h = candidates(H, 32)
        self.assertEqual((len(q), len(set(q))), (13, 13))
        self.assertEqual((len(h), len(set(h))), (33, 33))
        self.assertEqual(q[0], Q)
        self.assertEqual(q[1], bytes.fromhex("a403"))
        self.assertEqual(q[-1], bytes.fromhex("a50b"))
        self.assertEqual(h[-1], bytes.fromhex("123456f8"))

    def test_common_q_joint_and_all_attempts(self):
        result = evaluate(Q, H, .5, .5,
                          lambda q: (.8 if q == Q else 0, False),
                          lambda q, h: (.9 if q == Q and h == H else 0, False))
        self.assertTrue(result["both_match"])
        self.assertEqual(result["first_joint_candidate"], {"q": Q.hex(), "h": H.hex()})
        self.assertEqual((result["semantic_candidates"], result["instance_candidates"]), (13, 429))
        self.assertEqual((len(result["semantic_scores"]), len(result["instance_scores"])), (13, 429))

    def test_cross_q_component_hits_are_not_joint(self):
        other = candidates(Q, 12)[1]
        result = evaluate(Q, H, .5, .5,
                          lambda q: (.8 if q == Q else 0, False),
                          lambda q, h: (.9 if q == other and h == H else 0, False))
        self.assertTrue(result["semantic_hit"])
        self.assertTrue(result["instance_hit"])
        self.assertTrue(result["cross_q_only"])
        self.assertFalse(result["both_match"])
        self.assertIsNone(result["first_joint_candidate"])

    def test_strict_threshold_and_zero_variance_veto(self):
        at_threshold = evaluate(Q, H, .5, .5, lambda _: (.5, False), lambda *_: (.5, False))
        self.assertFalse(at_threshold["both_match"])
        veto = evaluate(Q, H, -.5, -.5, lambda _: (0, True), lambda *_: (0, True))
        self.assertFalse(veto["semantic_hit"])
        self.assertFalse(veto["instance_hit"])

    def test_rejects_malformed_codes_thresholds_and_scores(self):
        for q in (b"", b"\x00", b"\x00\xf0", "a503"):
            with self.subTest(q=q), self.assertRaises(ValueError):
                candidates(q, 12)
        for h in (bytes(3), "12345678"):
            with self.subTest(h=h), self.assertRaises(ValueError):
                candidates(h, 32)
        for threshold in (float("nan"), float("inf"), True, 1.1, 10**1000):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                evaluate(Q, H, threshold, 0, lambda _: (0, False), lambda *_: (0, False))
        for score in ((float("nan"), False), (2, False), (10**1000, False),
                      (0, 0), (True, False)):
            with self.subTest(score=score), self.assertRaises(ValueError):
                evaluate(Q, H, 0, 0, lambda _: score, lambda *_: (0, False))


if __name__ == "__main__":
    unittest.main()

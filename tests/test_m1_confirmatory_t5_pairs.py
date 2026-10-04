import hashlib
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import m1_confirmatory_t5_pairs as target


def row(uid, phash, cats=(1,), group=None, error=None):
    return dict(uid=uid, group_id=group or uid, categories=list(cats), phash=phash, error=error)


class PairTests(unittest.TestCase):
    def test_category_signature_crowd_duplicate_and_empty(self):
        self.assertEqual(target.category_signature([dict(category_id=2, iscrowd=0), dict(category_id=1, iscrowd=1), dict(category_id=2, iscrowd=0)]), (2,))
        self.assertEqual(target.category_signature([]), ())
        with self.assertRaises(ValueError):
            target.category_signature([dict(category_id=1, iscrowd=True)])

    def test_rank_framing_utf8_and_order(self):
        a, b = 'a', 'é'
        expected = hashlib.sha256(target.TAG + b'\0' + b'\0\0\0\1a' + b'\0\0\0\2\xc3\xa9').hexdigest()
        self.assertEqual(target.pair_rank(a, b)[0], expected)
        self.assertEqual(target.pair_rank(a, b), target.pair_rank(b, a))
        self.assertNotEqual(target.pair_rank('ab', 'c'), target.pair_rank('a', 'bc'))

    def test_exact_hash_boundary_missing_and_no_rescue(self):
        values = [row('a', 0), row('b', 255), row('c', 127), row('d', 65535, cats=())]
        result = target.schedule(values, ['a', 'b', 'c', 'd', 'missing'])
        pairs = {(x['left'], x['right']): x for x in result['ledger']}
        self.assertTrue(pairs['a', 'b']['eligible'])
        self.assertEqual(pairs['a', 'c']['reason'], 'source_phash_distance_below8')
        self.assertEqual(pairs['a', 'd']['reason'], 'empty_category_signature')
        self.assertEqual(pairs['a', 'missing']['reason'], 'missing_source_observation')
        self.assertEqual(result['enumerated_pairs'], 10)
        self.assertEqual(result['selected_pairs'], 1)
        self.assertEqual(result['shortfall'], 29)

    def test_disjoint_groups_deterministic_under_input_order(self):
        values = [row('a', 0, group='g1'), row('b', 65535), row('c', 0xffff0000), row('d', 0xffffffff, group='g1')]
        result = target.schedule(values, [x['uid'] for x in values])
        reordered = target.schedule(list(reversed(values)), [x['uid'] for x in reversed(values)])
        self.assertEqual(result, reordered)
        selected = [x for p in result['pairs'] for x in (p['left'], p['right'])]
        groups = {r['uid']: r['group_id'] for r in values}
        self.assertEqual(len(selected), len({groups[x] for x in selected}))

    def test_invalid_extra_score_or_unknown_uid_rejected(self):
        value = row('a', 0)
        with self.assertRaises(ValueError):
            target.schedule([dict(value, detector_score=1)], ['a'])
        with self.assertRaises(ValueError):
            target.schedule([value], ['b'])
        with self.assertRaises(ValueError):
            target.schedule([row('a', 2**32)], ['a'])
        with self.assertRaises(ValueError):
            target.schedule([value], ['a'], limit=31)
        with self.assertRaises(ValueError):
            target.schedule([], [str(i) for i in range(301)])


if __name__ == '__main__':
    unittest.main()

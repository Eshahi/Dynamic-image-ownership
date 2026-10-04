import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m1_confirmatory_schedule as subject


def fixtures():
    return [dict(source_uid=f'coco:{i:012d}', group_id=f'group-{i}', domain='ms-coco',
                 study_split='test', primary_group_representative='true') for i in range(600)]


class ScheduleTests(unittest.TestCase):
    def test_order_independent_and_separate_units(self):
        rows = fixtures()
        result = subject.schedule(rows)
        self.assertEqual(result, subject.schedule(list(reversed(rows))))
        clean = {r['source_uid'] for r in result['clean']}
        self.assertEqual(len(clean), 300)
        self.assertEqual(len(set(result['t3_source_uids'])), 30)
        graph = [p[k] for p in result['t4_pairs'] for k in ('donor_uid', 'recipient_uid')]
        self.assertEqual(len(set(graph)), 60)
        self.assertTrue(set(graph) <= clean)
        self.assertTrue(set(result['t3_source_uids']) <= clean)

    def test_no_development_or_nonrepresentative_selection(self):
        rows = fixtures()
        rows += [dict(source_uid='dev', group_id='dev', domain='ms-coco', study_split='development', primary_group_representative='true'),
                 dict(source_uid='other-member', group_id='group-0', domain='ms-coco', study_split='test', primary_group_representative='false')]
        self.assertEqual(subject.schedule(rows), subject.schedule(fixtures()))

    def test_integrity_fails_closed(self):
        for mutation in ('duplicate', 'group', 'short', 'non-nfc', 'flag'):
            rows = fixtures()
            if mutation == 'duplicate': rows.append(rows[0])
            if mutation == 'group': rows[1]['group_id'] = rows[0]['group_id']
            if mutation == 'short': rows = rows[:299]
            if mutation == 'non-nfc': rows[0]['source_uid'] = 'e\u0301'
            if mutation == 'flag': rows[0]['primary_group_representative'] = 'yes'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): subject.schedule(rows)

    def test_uint64_exact_and_no_authority(self):
        result = subject.schedule(fixtures())
        self.assertFalse(result['scientific_run_authorized'])
        self.assertFalse(result['source_contract_accepted'])
        self.assertFalse(result['images_or_annotations_opened'])
        self.assertTrue(any(int(r['seed_uint64_decimal']) > 2**53 for r in result['clean']))
        for row in result['clean']:
            self.assertEqual(int(row['seed_uint64_decimal']), int(row['seed_uint64_hex'], 16))
            self.assertNotEqual(row['owner'], row['wrong_owner'])


if __name__ == '__main__': unittest.main()

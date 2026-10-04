import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m1_owner_interface as api


class OwnerInterfaceTests(unittest.TestCase):
    def test_uint64_boundaries_and_exact_representations(self):
        for value in (0, 1, 2**32-1, 2**32, 2**53-1, 2**53, 2**63, 2**64-1):
            self.assertEqual(api.validate_seed_metadata(str(value), f'{value:016x}'), value)

    def test_malformed_and_lossy_transports_rejected(self):
        for decimal in ('', '01', '-1', '+1', '1.0', ' 1', str(2**64), 1, True, 1.0):
            with self.subTest(decimal=decimal), self.assertRaises(ValueError):
                api.validate_seed_metadata(decimal, '0000000000000001')
        for hex_value in ('1', '0x00000000000001', '000000000000000A', '0000000000000002', 1, None):
            with self.subTest(hex_value=hex_value), self.assertRaises(ValueError):
                api.validate_seed_metadata('1', hex_value)

    def test_documentary_a4_vector_and_wraparound(self):
        row = api.source_schedule('coco:000000000001')
        self.assertEqual((row['owner'], row['wrong_owner']), ('thesis:owner:09', 'thesis:owner:10'))
        self.assertEqual(row['seed_uint64_decimal'], '4369173439443558334')
        self.assertEqual(row['seed_uint64_hex'], '3ca26c18241adfbe')
        for i in range(1000):
            schedule = api.source_schedule(f'synthetic-owner-wrap:{i}')
            if schedule['owner'] == 'thesis:owner:15':
                self.assertEqual(schedule['wrong_owner'], 'thesis:owner:00')
                break
        else:
            self.fail('Fixed synthetic fixture did not cover wraparound')

    def test_metadata_does_not_reach_deterministic_method(self):
        source, configuration = object(), object()
        calls = []
        def embed(*args):
            calls.append(args)
            return 'fixture-output'
        output, row = api.invoke_deterministic_embed(embed, source, 'coco:000000000001', configuration)
        self.assertEqual(output, 'fixture-output')
        self.assertEqual(calls, [(source, 'thesis:owner:09', configuration)])
        self.assertIsNone(row['scientific_embedding_seed'])
        self.assertEqual(row['execution_phase_seed'], 0)
        self.assertEqual(row['execution_rng_policy'], 'fresh_phase_zero_resume_restores_saved_rng')
        self.assertEqual(row['schedule_seed_role'], 'metadata_only_not_consumed_by_ac_e2e')


if __name__ == '__main__':
    unittest.main()

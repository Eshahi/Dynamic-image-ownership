"""Metadata-only portability checks; never open source pixels or annotations."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT)]
import thesis_deployment_paths as P
import m1b_coco512_worker as W
import m1b_e3_s1_runtime as S
import m1b_prepare_package as Prep
from tests.test_m1b_e3_s1_worker import fixture


class PortabilityTests(unittest.TestCase):
    def test_bound_platform_paths(self):
        self.assertEqual(P.deployment_paths('linux')['assets'], '/workspace/thesis-assets/a6')
        self.assertEqual(P.deployment_paths('linux')['official_runtime'], '/workspace/thesis-runtime/scripts/_runtime')
        self.assertEqual(P.deployment_paths('win32')['main'], P.WINDOWS_MAIN)
        with self.assertRaises(RuntimeError): P.deployment_paths('unknown')

    def test_linux_index_is_path_only_translation(self):
        old = json.loads((ROOT / S.FRESH_INDEX).read_text())
        new = json.loads((ROOT / S.LINUX_FRESH_INDEX).read_text())
        self.assertEqual(W.sha_file(ROOT / S.FRESH_INDEX), S.FRESH_INDEX_SHA256)
        self.assertEqual(W.sha_file(ROOT / S.LINUX_FRESH_INDEX), S.LINUX_FRESH_INDEX_SHA256)
        expected = copy.deepcopy(old)
        for row in expected['entries']:
            row['external_raw_path'] = '/workspace/thesis-data/coco2017/val2017/' + row['external_raw_path'].rsplit('/', 1)[1]
        self.assertEqual(new, expected)
        schedule = json.loads((ROOT / S.FRESH_SCHEDULE).read_text())
        self.assertEqual(W.sha_file(ROOT / S.FRESH_SCHEDULE), S.FRESH_SCHEDULE_SHA256)
        self.assertEqual([r['source_uid'] for r in new['entries']], schedule['t3_source_uids'])

    def test_both_raw_roots_are_refused_for_non_test(self):
        for root in P.HELD_OUT_RAW_ROOTS:
            plan = fixture()
            plan['sources']['inline'][0]['raw_path'] = root + '/synthetic.jpg'
            with self.assertRaisesRegex(ValueError, 'held-out'):
                W.validate_plan(plan)

    def test_path_module_is_bound_in_scientific_core(self):
        self.assertIn('scripts/thesis_deployment_paths.py', W.code_closure())

    def test_platform_specific_index_contract_and_unchanged_schedule(self):
        plan = json.loads((ROOT / 'research/journal-upgrade-20261009/e3-s1-test.m1b-plan.json').read_text())
        with patch.object(S.sys, 'platform', 'win32'):
            _, local = W.validate_plan(plan)
        with patch.object(S.sys, 'platform', 'linux'):
            with self.assertRaisesRegex(ValueError, 'frozen metadata'):
                W.validate_plan(plan)
            plan['sources']['index'] = dict(path=S.LINUX_FRESH_INDEX, sha256=S.LINUX_FRESH_INDEX_SHA256)
            _, remote = W.validate_plan(plan)
            self.assertEqual(len(remote), 300)
            self.assertEqual([{k: v for k, v in r.items() if k != 'raw_path'} for r in remote],
                             [{k: v for k, v in r.items() if k != 'raw_path'} for r in local])
            plan['t3_uids'].reverse()
            with self.assertRaises(ValueError): W.validate_plan(plan)

    def test_paid_manifest_budget_and_zero_default(self):
        rel = 'research/journal-upgrade-20261009/e3-s1-test.m1b-plan.json'
        with patch.object(Prep, 'git', side_effect=lambda *a: '' if a[0] == 'status' else 'test-commit'), \
             patch.object(W, 'scientific_core', return_value=dict(data_sha256={})), \
             patch.object(S.sys, 'platform', 'win32'):
            local, _ = Prep.build_manifest(rel, 'test', 28800)
            paid, _ = Prep.build_manifest(rel, 'test', 28800, hourly_usd=.4037037037037037, max_usd=7.50)
        self.assertEqual(local['budget'], dict(max_seconds=28800, max_usd=0, hourly_usd=0))
        self.assertEqual(paid['budget']['max_usd'], 7.50)
        self.assertEqual(paid['budget']['hourly_usd'], .4037037037037037)
        for hourly, cap in ((float('nan'), 7.5), (-1, 7.5), (1, 0), (0, 1), (1, 1)):
            with self.assertRaises(ValueError):
                Prep.build_manifest(rel, 'test', 28800, hourly_usd=hourly, max_usd=cap)


if __name__ == '__main__': unittest.main()

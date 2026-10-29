"""Pure stdlib setup-choice/source/deadline tests; never execute infrastructure.

Decision objects below exist only in memory under mocked reads. No approval
receipt, image, download, package environment or setup artifact is created.
"""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import tifs_stage_s_setup as setup
import tifs_stage_p as stage_p


class SetupRound3Tests(unittest.TestCase):
    def decision_fixture(self, **changes):
        # Synthetic validator input only, never written or accepted as a decision.
        value=dict(schema='tifs-round3-user-choice-v1',decision='approve',recorded_by='Claude',
            config_sha256='a'*64,gate_profile='round3-proposed',stage_p='run',
            k3_optimization='excluded',before_server_outputs=True,
            user_decision_reference='SYNTHETIC UNIT TEST; NOT A HUMAN DECISION',max_instance_hours=126)
        value.update(changes)
        return value

    def read_choices(self, receipt):
        config_path,receipt_path=Path('fixture-base.json'),Path('unwritten-fixture-choice.json')
        def read(path):
            return dict(gate_profile='round1') if Path(path)==config_path else receipt
        def digest(path):
            return 'a'*64 if Path(path)==config_path else 'b'*64
        with patch.object(setup.common,'load_json',side_effect=read), \
             patch.object(setup.common,'sha256_file',side_effect=digest), \
             patch.object(setup.gate_profiles,'load_execution_config',side_effect=AssertionError('Selection must not be loaded pre-P')):
            return setup.setup_choices(config_path,receipt_path)

    def test_default_cap_stays_fifteen_and_requires_no_selection(self):
        with patch.object(setup.gate_profiles,'load_execution_config',side_effect=AssertionError('Selection unexpectedly read')):
            choices=setup.setup_choices()
        self.assertEqual(choices['max_instance_hours'],15)
        self.assertEqual(choices['stage_p'],'decline')
        self.assertIsNone(choices['user_choice_sha256'])
        self.assertEqual(choices['base_config_sha256'],setup.common.sha256_file(setup.BASE_CONFIG))

    def test_external_choice_binds_base_hash_without_p_selection(self):
        choices=self.read_choices(self.decision_fixture())
        self.assertEqual(choices,dict(base_config_sha256='a'*64,max_instance_hours=126,
                                      user_choice_sha256='b'*64,stage_p='run'))
        declined=self.read_choices(self.decision_fixture(stage_p='decline',gate_profile='round1',max_instance_hours=15))
        self.assertEqual(declined['stage_p'],'decline')
        self.assertEqual(declined['max_instance_hours'],15)

    def test_changed_or_incomplete_external_choice_is_rejected(self):
        for changes in (dict(config_sha256='c'*64),dict(before_server_outputs=False),
                        dict(recorded_by='Codex'),dict(stage_p='skip'),dict(k3_optimization='included'),
                        dict(max_instance_hours=float('nan')),dict(max_instance_hours=0),dict(max_instance_hours=True)):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                self.read_choices(self.decision_fixture(**changes))

    def test_external_cap_preserves_one_clock_and_retrieval_reserve(self):
        epoch=1767225600
        clock=[epoch+20*3600]
        default=setup.Deadline('2026-01-01T00:00:00Z',lambda:clock[0])
        with self.assertRaises(setup.common.ResourceStop): default.timeout()
        extended=setup.Deadline('2026-01-01T00:00:00Z',lambda:clock[0],max_hours=126)
        self.assertEqual(extended.timeout(),(126-20)*3600-3630)
        self.assertEqual(extended.start,'2026-01-01T00:00:00+00:00')
        clock[0]=epoch+126*3600-3630
        with self.assertRaises(setup.common.ResourceStop): extended.timeout()
        for invalid in (0,-1,True,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                setup.Deadline('2026-01-01T00:00:00Z',lambda:clock[0],max_hours=invalid)

    def test_all_twenty_four_p_hashes_verified_without_opening_images(self):
        manifest=stage_p.load_manifest(setup.STAGE_P_MANIFEST)
        stage_s=setup.common.load_json(setup.HERE/'source-manifest.json')
        rows=manifest['tune_sources']+manifest['check_sources']
        expected={str(r['source_id'])+'.png':r['canonical_png_sha256'] for r in rows}
        checked=[]
        real_hash=setup.common.sha256_file
        def digest(path):
            path=Path(path)
            if path.name in expected:
                checked.append(path.name)
                return expected[path.name]
            return real_hash(path)
        with tempfile.TemporaryDirectory() as tmp,patch.object(Path,'is_file',return_value=True), \
             patch.object(setup.common,'sha256_file',side_effect=digest):
            records=setup.verify_stage_p_sources(Path(tmp),setup.STAGE_P_MANIFEST,stage_s)
            self.assertEqual(len(records),24)
            self.assertEqual(set(checked),set(expected))
            self.assertEqual(len(checked),24)
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_p_missing_hash_and_s_overlap_fail_before_any_acquisition(self):
        manifest=stage_p.load_manifest(setup.STAGE_P_MANIFEST)
        stage_s=setup.common.load_json(setup.HERE/'source-manifest.json')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'canonical Stage P source'):
                setup.verify_stage_p_sources(Path(tmp),setup.STAGE_P_MANIFEST,stage_s)
            with patch.object(stage_p,'load_manifest',return_value=manifest), \
                 patch.object(Path,'is_file',return_value=True), \
                 patch.object(setup.common,'sha256_file',return_value='0'*64), \
                 self.assertRaisesRegex(ValueError,'canonical Stage P source'):
                setup.verify_stage_p_sources(Path(tmp),setup.STAGE_P_MANIFEST,stage_s)
            self.assertEqual(list(Path(tmp).iterdir()),[])
            changed=copy.deepcopy(manifest)
            changed['tune_sources'][0]['source_id']=stage_s[setup.common.SOURCE_GROUPS[0]][0]['source_id']
            with patch.object(stage_p,'load_manifest',return_value=changed),self.assertRaisesRegex(ValueError,'overlap: source_id'):
                setup.verify_stage_p_sources(Path(tmp),setup.STAGE_P_MANIFEST,stage_s)


if __name__=='__main__':unittest.main()

"""Pure prospective-choice tests; receipt/selection inputs exist only in mocks."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tifs_common as common
import tifs_gate_profiles as profiles


BASE=Path(__file__).resolve().parents[1]/"research/tifs-20261028/stage-s/frozen-config.json"


class GateProfileTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)
        self.path=self.root/"stage-s/frozen-config.json"
        self.original=common.load_json(BASE)
        common.atomic_json(self.path,self.original)
        self.choice=self.root/"NONEXISTENT-TEST-CHOICE.json"
        self.selection=self.root/"NONEXISTENT-TEST-SELECTION.json"
        self.mock_inputs={}
        original_load,original_sha=common.load_json,common.sha256_file
        self.load_patch=patch.object(common,"load_json",side_effect=lambda path:copy.deepcopy(self.mock_inputs[Path(path)]) if Path(path) in self.mock_inputs else original_load(path))
        self.sha_patch=patch.object(common,"sha256_file",side_effect=lambda path:("c"*64 if Path(path)==self.choice else "d"*64) if Path(path) in self.mock_inputs else original_sha(path))
        self.load_patch.start();self.sha_patch.start()

    def tearDown(self):
        self.sha_patch.stop();self.load_patch.stop();self.temporary.cleanup()

    def receipt(self,profile="round1",stage_p="decline",hours=15):
        value=dict(schema="tifs-round3-user-choice-v1",decision="approve",recorded_by="Claude",
            config_sha256=common.sha256_file(self.path),gate_profile=profile,stage_p=stage_p,
            k3_optimization="excluded",before_server_outputs=True,
            user_decision_reference="PURE TEST FIXTURE; NO HUMAN VERDICT",max_instance_hours=hours)
        self.mock_inputs[self.choice]=value
        return value

    def selected(self,profile="round1"):
        value=dict(status="SELECTED",base_config_sha256=common.sha256_file(self.path),
            gate_profile=profile,user_choice_sha256="c"*64,check_status="PASS",
            candidate="f6-x0",writer_psnr_db=42,k3_optimization="excluded")
        self.mock_inputs[self.selection]=value
        return value

    def load(self,choice=False,selection=False):
        return profiles.load_execution_config(self.path,receipt_path=self.choice if choice else None,
            selection_path=self.selection if selection else None)

    def test_default_preserves_round1_noise52_and_fifteen_hours(self):
        result=self.load()
        self.assertEqual((result["gate_profile"],result["candidate"],result["writer"]["psnr_db"],result["budget"]["max_instance_hours"]),
                         ("round1","f6-noise",52,15))
        self.assertEqual(result["execution_choices"]["stage_p"],"not_run_no_choice_receipt")
        self.assertIsNone(result["execution_choices"]["user_choice_sha256"])
        self.assertEqual(common.load_json(self.path),self.original)

    def test_proposed_is_explicit_and_declined_stage_p_keeps_frozen_writer(self):
        self.receipt("round3-proposed",hours=24)
        result=self.load(choice=True)
        self.assertEqual(result["gate_profile"],"round3-proposed")
        self.assertEqual((result["candidate"],result["writer"]["psnr_db"]),("f6-noise",52))
        self.assertEqual(result["budget"]["max_seconds"],86400)
        self.assertEqual(result["execution_choices"]["stage_p"],"declined")
        self.assertEqual(result["execution_choices"]["user_choice_sha256"],"c"*64)
        modified=copy.deepcopy(self.original);modified["gate_profile"]="round3-proposed"
        common.atomic_json(self.path,modified)
        with self.assertRaises(ValueError):self.load()

    def test_stage_p_run_requires_successful_selection_without_fallback(self):
        self.receipt(stage_p="run")
        with self.assertRaises(ValueError):self.load(choice=True)
        self.selected()
        with self.assertRaises(ValueError):self.load(selection=True)
        self.receipt(stage_p="decline")
        with self.assertRaises(ValueError):self.load(choice=True,selection=True)

    def test_successful_selection_consumes_candidate_budget_and_choice(self):
        self.receipt("round3-proposed",stage_p="run",hours=22)
        self.selected("round3-proposed")
        result=self.load(choice=True,selection=True)
        self.assertEqual((result["candidate"],result["writer"]["psnr_db"]),("f6-x0",42))
        self.assertEqual(result["writer"]["refine_psnr_db"],58)
        self.assertEqual(result["budget"]["max_instance_hours"],22)
        provenance=result["execution_choices"]
        self.assertEqual(provenance["stage_p"],"selected")
        self.assertEqual(provenance["user_choice_sha256"],"c"*64)
        self.assertEqual(provenance["selected_config_sha256"],"d"*64)
        self.assertEqual(common.load_json(self.path),self.original)

    def test_malformed_receipt_profile_ceiling_and_base_hash_fail(self):
        for field,value in (("gate_profile","unknown"),("max_instance_hours",float("nan")),
                ("max_instance_hours",float("inf")),("max_instance_hours",True),("max_instance_hours",0),
                ("config_sha256","wrong-base"),("before_server_outputs",False),("recorded_by","Codex")):
            with self.subTest(field=field,value=value):
                receipt=self.receipt();receipt[field]=value
                with self.assertRaises(ValueError):self.load(choice=True)

    def test_invalid_or_failed_check_selection_never_activates(self):
        self.receipt(stage_p="run")
        for field,value in (("status","NOMINATED"),("check_status","FAIL"),("check_status","INCOMPLETE"),
                ("base_config_sha256","wrong-base"),("user_choice_sha256","wrong-choice"),
                ("gate_profile","round3-proposed"),("candidate","f6-codec"),("writer_psnr_db",41),
                ("k3_optimization","included")):
            with self.subTest(field=field,value=value):
                selected=self.selected();selected[field]=value
                with self.assertRaises(ValueError):self.load(choice=True,selection=True)

    def test_round1_keeps_original_new_writers_primary_after_x0_selection(self):
        config=copy.deepcopy(self.original);config["candidate"]="f6-x0"
        result=profiles.profile_config(config,"round1")
        decision=result["decision"]
        self.assertEqual(decision["quality_writers"],list(dict.fromkeys(self.original["new_writers"]+["f6-x0"])))
        self.assertEqual(decision["ablation_arms"],[arm for arm in self.original["new_writers"] if arm!="f6-x0"])
        self.assertTrue(decision["ablation_gains_primary"])
        self.assertEqual(decision["gain_comparators"],["f5-r2"])
        self.assertEqual(decision["quality_comparator"],"f5-r2")
        self.assertEqual(config["decision"],self.original["decision"])

    def test_proposed_uses_budget_control_and_reports_all_other_f6_ablations(self):
        for candidate in ("f6-noise","f6-x0"):
            config=copy.deepcopy(self.original);config["candidate"]=candidate
            decision=profiles.profile_config(config,"round3-proposed")["decision"]
            self.assertEqual(decision["gain_comparators"],["f5-r2","f5-budget"])
            self.assertEqual(decision["quality_writers"],[candidate,"f5-budget"])
            self.assertEqual(decision["quality_comparator"],"f5-budget")
            self.assertFalse(decision["ablation_gains_primary"])
            self.assertEqual(decision["ablation_arms"],[arm for arm in config["arms"] if arm.startswith("f6-") and arm!=candidate])

    def test_invalid_profile_or_threshold_is_rejected(self):
        with self.assertRaises(ValueError):profiles.profile_config(self.original,"unknown")
        for key,value in (("absolute_foreign_count_min",-1),("clean_F_count_min_each_new_writer",14),
                ("max_retained_loss",2),("paired_median_lpips_delta_max",float("nan")),
                ("paired_median_psnr_delta_min",-2),
                ("gain_over_f5",{"R1-0.1":3,"R1-0.2":4,"K3-0.2":3}),
                ("gain_over_each_ablation",{"R1-0.1":3,"R1-0.2":3,"K3-0.2":0})):
            with self.subTest(key=key):
                config=copy.deepcopy(self.original);config["decision"][key]=value
                for profile in profiles.PROFILES:
                    with self.assertRaises(ValueError):profiles.profile_config(config,profile)

    def test_profile_decisions_match_registry_and_reject_changed_registration(self):
        for profile in profiles.PROFILES:
            with self.subTest(profile=profile):
                registered=self.original["gate_profiles"][profile]["decision_overrides"]
                decision=profiles.profile_config(self.original,profile)["decision"]
                for key,value in registered.items():self.assertEqual(decision[key],value)
                changed=copy.deepcopy(self.original)
                changed["gate_profiles"][profile]["decision_overrides"]["gain_comparators"]=["vine-b"]
                with self.assertRaises(ValueError):profiles.profile_config(changed,profile)


if __name__=="__main__":unittest.main()

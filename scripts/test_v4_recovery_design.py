import copy
import sys
import unittest
from itertools import combinations
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v4_study_protocol import EXPANDED_IDS,RUN,claims,inventory
from v4_recovery_design import make_schedule,validate_design_receipt,observed_liveness


def fixture():
    labels=[{"left":a,"right":b,"label":"same" if i<7 else "different"}
            for i,(a,b) in enumerate(combinations(EXPANDED_IDS,2))]
    rows=inventory(labels)
    for row in rows:
        row.update(status="NOT_RUN",detections=[])
        if row["axis"] in ("clean","T4","T5-transfer"):
            row["image"]={"sha256":"0"*64,"path":"fake.png"}
            row["status"]="image_saved"
        if row["axis"]=="clean":
            row["detection_complete"]=True
            row["detections"]=[{"claimed_owner":o,"binding_mode":m,"result":{"owners_tested":n}}
                               for o,m,n in claims(row)]
    return {"run_id":RUN,"rows":rows},labels


class Tests(unittest.TestCase):
    def test_frozen_coverage_small_chunks_and_order(self):
        snapshot,labels=fixture()
        plan=make_schedule(snapshot,labels)
        assigned=[r for u in plan["units"] for r in u["row_ids"]]
        self.assertEqual(len(assigned),537)
        self.assertEqual(len(set(assigned)),537)
        self.assertEqual(plan["planned_detector_calls"],1884)
        self.assertEqual(plan["inherited_detector_calls"],96)
        self.assertTrue(all(len(u["row_ids"])<=9 for u in plan["units"]))
        generation=[u for u in plan["units"] if u["phase"]=="new_generation"]
        self.assertTrue(all(len(u["row_ids"])<=2 for u in generation))
        first=next(i for i,u in enumerate(plan["units"]) if u["phase"]=="new_generation")
        self.assertTrue(all(u["phase"] in ("new_generation","attempt_quarantine") for u in plan["units"][first:]))
        self.assertEqual(plan["units"][-1]["phase"],"attempt_quarantine")
        self.assertEqual([u["phase"] for u in plan["units"][:12]],["clean_evaluation"]*12)

    def test_completed_images_and_safety_failures_never_regenerated(self):
        snapshot,labels=fixture()
        t3=[r for r in snapshot["rows"] if r["axis"]=="T3"]
        t3[0].update(status="image_saved",image={"sha256":"1"*64})
        t3[1].update(status="failed",errors=[{"message":"safety_checker_blocked_output"}])
        plan=make_schedule(snapshot,labels)
        actions={k:v for u in plan["units"] for k,v in u["actions"].items()}
        self.assertEqual(actions[t3[0]["id"]],"evaluate_saved")
        self.assertEqual(actions[t3[1]["id"]],"retain_safety_failure")
        self.assertEqual(plan["known_missing_detector_calls"],4)
        self.assertEqual(plan["inherited_detector_calls"]+plan["new_detector_calls_if_safe"]+
                         plan["known_missing_detector_calls"]+plan["unresolved_detector_calls"],1884)

    def test_first_pending_attempt_quarantined_and_downstream_only_candidates(self):
        snapshot,labels=fixture()
        plan=make_schedule(snapshot,labels)
        t3=[r for r in inventory(labels) if r["axis"]=="T3"]
        actions={k:v for u in plan["units"] for k,v in u["actions"].items()}
        self.assertEqual(actions[t3[0]["id"]],"pending_attempt_disposition")
        self.assertEqual(actions[t3[1]["id"]],"generate_then_evaluate")
        self.assertEqual(plan["unresolved_detector_calls"],4)
        quarantine=plan["units"][-1]
        with self.assertRaises(ValueError):
            validate_design_receipt(quarantine,[{"id":quarantine["row_ids"][0],"status":"EVALUATED"}])

    def test_nonsequential_parent_checkpoint_rejected(self):
        snapshot,labels=fixture()
        t3=[r for r in snapshot["rows"] if r["axis"]=="T3"]
        t3[1].update(status="image_saved",image={"sha256":"1"*64})
        with self.assertRaises(ValueError): make_schedule(snapshot,labels)

    def safety_record(self):
        start={"row_id":"t3-test","attempt_id":"attempt-1","receipt_sha256":"a"*64,
               "recipe_sha256":"b"*64,"input_sha256":"c"*64}
        failure={"row_id":"t3-test","attempt_id":"attempt-1","receipt_sha256":"d"*64,
                 "attempt_start_sha256":"a"*64,"recipe_sha256":"b"*64,"input_sha256":"c"*64,
                 "message":"safety_checker_blocked_output"}
        return {"id":"t3-test","status":"NEW_SAFETY_BLOCKED","attempt_start":start,
                "failure":failure,"detector_calls":0,"missing_detector_calls":4,"scientific_success":False}

    def test_new_safety_failure_seals_evidence_not_success(self):
        self.assertTrue(validate_design_receipt(self.image_unit(),[self.safety_record()]))
        saved={"row_ids":["t3-test"],"actions":{"t3-test":"evaluate_saved"}}
        with self.assertRaises(ValueError): validate_design_receipt(saved,[self.safety_record()])

    def test_new_safety_failure_requires_durable_identity_and_missing_calls(self):
        for field in ("attempt_start","failure","detector_calls","missing_detector_calls","scientific_success"):
            record=self.safety_record()
            record.pop(field)
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_design_receipt(self.image_unit(),[record])
        for section,field,value in (("failure","attempt_id","other"),
                                    ("failure","input_sha256","e"*64),
                                    ("failure","attempt_start_sha256","e"*64),
                                    ("attempt_start","receipt_sha256","not-a-hash")):
            record=self.safety_record()
            record[section][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_design_receipt(self.image_unit(),[record])
        for field,value in (("scientific_success",True),("detector_calls",4),("image_sha256","e"*64)):
            record=self.safety_record()
            record[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_design_receipt(self.image_unit(),[record])

    def test_mutated_or_duplicate_rows_rejected(self):
        for mutation in ("duplicate","recipe","failure"):
            snapshot,labels=fixture()
            if mutation=="duplicate": snapshot["rows"].append(copy.deepcopy(snapshot["rows"][0]))
            if mutation=="recipe": snapshot["rows"][0]["source_id"]=-1
            if mutation=="failure":
                row=next(r for r in snapshot["rows"] if r["axis"]=="T3")
                row.update(status="failed",errors=[{"message":"host crashed"}])
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                make_schedule(snapshot,labels)

    def image_unit(self):
        return {"row_ids":["t3-test"],"actions":{"t3-test":"generate_then_evaluate"}}

    def complete_record(self):
        return {"id":"t3-test","status":"EVALUATED","detector_calls":4,
                "image_sha256":"a"*64,"feature_pixel_binding_verified":True,
                "quality_source":{"psnr":40.,"ssim":.95,"lpips":.02},
                "quality_immediate":{"psnr":40.,"ssim":.95,"lpips":.02}}

    def test_generation_or_detection_alone_never_commits(self):
        for field in ("status","detector_calls","image_sha256","feature_pixel_binding_verified","quality_source","quality_immediate"):
            record=self.complete_record()
            record.pop(field)
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_design_receipt(self.image_unit(),[record])
        self.assertTrue(validate_design_receipt(self.image_unit(),[self.complete_record()]))

    def test_nan_and_infinity_rejected(self):
        for value in (float("nan"),float("inf"),float("-inf"),True):
            record=self.complete_record()
            record["quality_source"]["lpips"]=value
            with self.subTest(value=value),self.assertRaises(ValueError):
                validate_design_receipt(self.image_unit(),[record])

    def test_idempotent_prefix_and_incomplete_chunk_after_kill(self):
        snapshot,labels=fixture()
        units=make_schedule(snapshot,labels)["units"]
        committed={u["unit_id"] for u in units[:3]}
        remaining=[u for u in units if u["unit_id"] not in committed]
        self.assertEqual(remaining[0],units[3])
        unit=self.image_unit()
        for state in ("IMAGE_SAVED","DETECTED","METRICS_WRITTEN_NOT_SEALED"):
            record=self.complete_record()
            record["status"]=state
            with self.subTest(state=state),self.assertRaises(ValueError):
                validate_design_receipt(unit,[record])

    def test_dead_or_stale_owner_never_reported_running(self):
        self.assertEqual(observed_liveness("running",False,1),"INTERRUPTED_OBSERVED_CAUSE_UNKNOWN")
        self.assertEqual(observed_liveness("running",True,121),"STALLED_NEEDS_CHECK")
        self.assertEqual(observed_liveness("running",True,None),"STALLED_NEEDS_CHECK")
        self.assertEqual(observed_liveness("running",True,30),"RUNNING_OBSERVED")

    def test_failure_and_component_receipts_require_evidence(self):
        for kind,status,field in (("retain_safety_failure","INHERITED_SAFETY_BLOCKED","source_failure_sha256"),
                                  ("compare_components","COMPARED","component_artifact_sha256")):
            unit={"row_ids":["x"],"actions":{"x":kind}}
            record={"id":"x","status":status}
            with self.assertRaises(ValueError): validate_design_receipt(unit,[record])
            record[field]="b"*64
            self.assertTrue(validate_design_receipt(unit,[record]))


if __name__=="__main__":
    unittest.main()

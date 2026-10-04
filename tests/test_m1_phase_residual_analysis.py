"""Synthetic metadata only: no model, image or scientific output loaded."""
import copy
import importlib.util
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location("residual_analysis",Path(__file__).resolve().parents[1]/"scripts/m1_analyze_families.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def fixture():
    owners=["alpha","beta","gamma","delta"]
    config=dict(schema="m1-phasemark-residual-v1",ids=[1,2],arms=["APM","IPS"],profiles=["full","quality-cap"],owners=owners,threshold=82,psnr_cap_db=35.2)
    conditions=[]
    q=dict(psnr_db=40,ssim_rgb=.96,lpips=.01)
    for i in config["ids"]:
        for a in config["arms"]:
            for p in config["profiles"]:
                for c in ("C0","C1"):
                    for d in ("clean","vae_cycle"):
                        decisions={o:dict(matches=100 if c=="C1" and o==owners[0] else 64,bit_accuracy=100/128 if c=="C1" and o==owners[0] else .5,present=c=="C1" and o==owners[0]) for o in owners}
                        conditions.append(dict(id=f"{i}-{a}-{p}-{c}-{d}",source_id=i,arm=a,profile=p,control=c,dose=d,outcome="completed",
                            owner_decisions=decisions,quality_vs_source=copy.deepcopy(q),quality_vs_same_arm_clean=copy.deepcopy(q),extract_seconds=.03,
                            composition=dict(weight=1 if p=="full" else .2,budget_mse_rgb8=19.6,mse_rgb8=10,sse_rgb8=100) if c=="C1" else None,
                            extracted=dict(scores=[1]*128,zero_magnitude_coefficients_per_block=[0]*128),image={"path":"never-open.png","sha256":"a"*64}))
    run=dict(schema=config["schema"],config=config,outcome="completed",conditions=conditions)
    return dict(run=run,manifest=config,errors=[],source_outcome="completed",directory="fixture",input_files=[])


class ResidualAnalysisTests(unittest.TestCase):
    def test_complete_denominators_profiles_and_latency_not_query_sample_size(self):
        r=m.analyze_phase_residual(fixture())
        self.assertEqual((r["planned_source_n"],len(r["condition_inventory"]),len(r["raw"])),(2,32,128))
        self.assertEqual(len(r["arm_screen"]),4)
        self.assertTrue(all(s["source_quality_gate"] and s["clean_carrier_gate"] and s["vae_cycle_carrier_gate"] for s in r["arm_screen"]))
        self.assertEqual({r["lambda"] for r in r["raw"] if r["control"]=="C1"},{1,.2})
        self.assertFalse(r["incomplete"])
        self.assertTrue(all("proposal_state" not in row for row in r["raw"]))

    def test_quality_and_carrier_gates_are_separate(self):
        p=fixture();p["run"]["conditions"][2]["quality_vs_source"]["psnr_db"]=20
        r=m.analyze_phase_residual(p);s=r["arm_screen"][0]
        self.assertFalse(s["source_quality_gate"]);self.assertTrue(s["clean_carrier_gate"])
        del p["run"]["conditions"][3]["owner_decisions"]["beta"]
        s=m.analyze_phase_residual(p)["arm_screen"][0]
        self.assertIsNone(s["vae_cycle_carrier_gate"]);self.assertTrue(s["clean_carrier_gate"])

    def test_failed_condition_and_parent_retained_null_gates(self):
        p=fixture();p["run"]["conditions"][2].update(outcome="failed",error="fixture failure")
        r=m.analyze_phase_residual(p)
        self.assertTrue(r["incomplete"]);self.assertEqual(len(r["raw"]),128)
        self.assertEqual(r["raw"][8]["error"],"fixture failure")
        self.assertIsNone(r["arm_screen"][0]["clean_carrier_gate"])
        p=fixture();p["source_outcome"]="started"
        self.assertTrue(all(s["source_quality_gate"] is None for s in m.analyze_phase_residual(p)["arm_screen"]))

    def test_duplicate_unplanned_inconsistent_owner_and_identity_rejected(self):
        for change in (lambda p:p["run"]["conditions"].append(copy.deepcopy(p["run"]["conditions"][0])),
                       lambda p:p["run"]["conditions"][0].update(id="unexpected"),
                       lambda p:p["run"]["conditions"][0].update(profile="other"),
                       lambda p:p["run"]["conditions"][0]["owner_decisions"]["alpha"].update(present=True)):
            p=fixture();change(p)
            with self.assertRaises(ValueError):m.analyze_phase_residual(p)

    def test_missing_condition_stays_in_fixed_denominator(self):
        p=fixture();p["run"]["conditions"].pop()
        r=m.analyze_phase_residual(p)
        self.assertEqual(len(r["raw"]),128);self.assertEqual(len(r["condition_inventory"]),32)
        self.assertIsNone(r["arm_screen"][-1]["vae_cycle_carrier_gate"])

    def test_positive_control_failure_and_exact_threshold_boundary(self):
        p=fixture();decision=p["run"]["conditions"][0]["owner_decisions"]["beta"]
        decision.update(matches=82,bit_accuracy=82/128,present=True)
        r=m.analyze_phase_residual(p)
        self.assertFalse(r["arm_screen"][0]["clean_carrier_gate"])
        self.assertEqual(r["arm_screen"][0]["clean_C0_positive_queries"],1)
        self.assertTrue(r["arm_screen"][0]["source_quality_gate"])

    def test_source_snapshot_and_metadata_receipts_fail_closed_without_image_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=fixture();run=p["run"];config=p["manifest"]
            m.write(root/"input-run.json",{"outcome":"completed"})
            config["input_run_sha256"]=m.sha(root/"input-run.json")
            m.write(root/"manifest.json",config);m.write(root/"conditions.json",run["conditions"])
            (root/"rows.jsonl").write_text("",encoding="utf-8")
            run.update(command=["fixture","--manifest",str(root/"manifest.json")],manifest_sha256=m.sha(root/"manifest.json"),data_split="development",
                input_receipts={"run_sha256":config["input_run_sha256"]},output_hashes={n:m.sha(root/n) for n in ("manifest.json","conditions.json","rows.jsonl")})
            m.write(root/"run.json",run)
            loaded=m.load_family("phase_residual",root)
            self.assertEqual(loaded["errors"],[])
            (root/"input-run.json").write_text("{}",encoding="utf-8")
            loaded=m.load_family("phase_residual",root)
            self.assertTrue(loaded["errors"])
            self.assertTrue(all(s["clean_carrier_gate"] is None for s in m.analyze_phase_residual(loaded)["arm_screen"]))


if __name__=="__main__":unittest.main()

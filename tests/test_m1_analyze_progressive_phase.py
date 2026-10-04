"""Synthetic CPU fixtures only; no models, real run data or scientific images."""
import copy,hashlib,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import m1_analyze_progressive_phase as a

def read(word,intended,coeff=False):
    r=a.words(word,intended)
    for n in ("intended","original","complement"):r[n+"_bit_accuracy"]=r[n+"_matches"]/16
    q=a.wrong_queries(word);r["wrong_payload_queries"]={"queries":64,"denominator":64,"bit_accuracies":q,"false_findings":sum(x>=.875 for x in q)}
    if coeff:
        c=[.5 if b=="1" else -.5 for b in word for _ in range(8)]
        target=[.5 if b=="1" else -.5 for b in intended for _ in range(8)]
        r.update(selected_coefficients=c,target_mse=sum((x-y)**2 for x,y in zip(c,target))/128,coefficient_sign_matches=sum((x>0)==(y>0) for x,y in zip(c,target)),zero_count=0,nonfinite_count=0)
    return r

def q(psnr=36):return dict(psnr_db=psnr,psnr_infinite=False,ssim_rgb=.95,lpips=.05,quality_admissible=psnr>35)

def fixture(directory):
    rows=[];old={}
    for seed in range(1000,1004):
        for arm in a.ARMS:
            ident=f"seed{seed}-{arm}"; intended=a.COMPLEMENT if arm.endswith("complement") else a.ORIGINAL
            word="0000000000000000" if arm==a.ARMS[0] else intended
            artifacts=[];g={"guided_step_indices":[] if arm==a.ARMS[0] else list(range(25)) if arm==a.ARMS[1] else list(range(25,50)),"timesteps":list(range(50)),"safety_flag":False,"clipping_fraction":0,"readout_stages":{}}
            for name in ("initial_latent","terminal_latent","decoder_float","clipped_decoder_float","clipped_float_cycle_latent"):
                receipt={"path":ident+"-"+name+".npy","sha256":"fake","raw_sha256":str(seed),"bytes":1};g[name]=receipt;artifacts.append(receipt)
            for name in a.STAGES:g["readout_stages"][name]=read(word,intended,True)|{"eligible_image_detector":name in a.STAGES[2:]}
            ts=[]
            for i in range(50):
                t=dict(step_index=i,timestep=i,guided=i in g["guided_step_indices"],changed_other_channels_count=0,supplied_epsilon_nonfinite_count=0,stages={n:read(word,intended,True) for n in a.TRACE_STAGES})
                for key in ("q_t","gradient_l2","intended_clean_correction_l2","epsilon_correction_before_cast_l2","epsilon_correction_after_cast_l2","changed_channel0_fraction","local_scheduler_displacement_l2","local_formula_discrepancy_l2"):t[key]=0.
                ts.append(t)
            trace=directory/(ident+"-trace.jsonl");trace.write_text("\n".join(json.dumps(t) for t in ts));artifacts.append({"path":trace.name})
            conditions={}
            for channel in ("clean","vae"):
                receipt={"path":ident+"-"+channel+".png","sha256":ident+channel};artifacts.append(receipt)
                v={"outcome":"completed","artifact":receipt,"native_vae_dct":read(word,intended),"image_dct_diagnostic":read(word,intended),"native_vae_dct_seconds":.1,"image_dct_diagnostic_seconds":.01,"extract_both_seconds":.11,"quality_vs_same_arm_clean":q()}
                if arm in a.ARMS[:2]:
                    old[seed,arm,channel]=receipt["sha256"];v["replay"]={"expected_sha256":receipt["sha256"],"actual_sha256":receipt["sha256"],"matched":True,"original_latent_hash":None}
                conditions[channel]=v
            rows.append(dict(id=ident,seed=seed,arm=arm,intended_payload=intended,original_payload=a.ORIGINAL,outcome="completed",artifacts=artifacts,generation=g,conditions=conditions,paired_initial_latent_matches=True,duration_seconds=1,peak_allocated_bytes=1,quality_to_new_C0=q(),quality_to_old_C0=q()))
    return {"outcome":"completed","rows":rows},old

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name);self.r,self.old=fixture(self.d)
    def tearDown(self):self.tmp.cleanup()
    def analyze(self,errors=()):
        with patch.object(a,"artifact",side_effect=lambda d,r,expected=None:r["path"] if not expected or r["path"]==expected else (_ for _ in ()).throw(ValueError("identity"))):return a.analyze(self.d,self.r,self.old,list(errors))
    def test_complete_fixed_denominator_oracles_separate(self):
        z=self.analyze();self.assertTrue(z["gates"]["necessary_condition"]);self.assertEqual(len(z["conditions"]),32);self.assertEqual(len(z["stages"]),64);self.assertEqual(len(z["traces"]),3200);self.assertEqual(z["independent_source_clusters"],4)
        self.assertTrue(all(x["planned_images"]==4 for x in z["counts"]))
    def test_missing_duplicate_and_extra_keep_planned_inventory(self):
        for mutate in (lambda r:r["rows"].pop(),lambda r:r["rows"].append(copy.deepcopy(r["rows"][0])),lambda r:r["rows"].append({"id":"foreign"})):
            original=copy.deepcopy(self.r);mutate(self.r);z=self.analyze();self.assertFalse(z["gates"]["complete"]);self.assertIsNone(z["gates"]["necessary_condition"]);self.assertEqual(len(z["inventory"]),16);self.assertEqual(len(z["conditions"]),32);self.r=original
    def test_replay_failure_keeps_observations_nulls_attribution(self):
        v=self.r["rows"][0]["conditions"]["clean"];self.old[1000,a.ARMS[0],"clean"]="different";v["replay"].update(expected_sha256="different",matched=False)
        z=self.analyze();self.assertTrue(z["gates"]["complete"]);self.assertFalse(z["gates"]["replay"]);self.assertIsNone(z["gates"]["necessary_condition"]);self.assertIsNone(z["gates"]["quality_attribution"])
    def test_quality_failure_not_carrier_failure(self):
        self.r["rows"][2]["quality_to_new_C0"]=q(30);z=self.analyze();self.assertTrue(z["gates"]["late_carrier"]);self.assertFalse(z["gates"]["late_quality"])
    def test_missing_quality_timing_and_nonfinite_block_complete(self):
        for mutation in (lambda r:r["rows"][2].pop("quality_to_new_C0"),lambda r:r["rows"][2]["conditions"]["clean"].pop("native_vae_dct_seconds"),lambda r:r["rows"][2]["generation"]["readout_stages"]["terminal_predecode"]["selected_coefficients"].__setitem__(0,float("nan"))):
            original=copy.deepcopy(self.r);mutation(self.r);self.assertFalse(self.analyze()["gates"]["complete"]);self.r=original
    def test_initial_noise_mismatch_and_provenance_block(self):
        self.r["rows"][2]["generation"]["initial_latent"]["raw_sha256"]="changed";self.assertFalse(self.analyze()["gates"]["complete"])
        self.assertIsNone(self.analyze(["receipt failure"])["gates"]["necessary_condition"])
    def test_endpoint_primary_disagreement_rejected(self):
        self.r["rows"][2]["conditions"]["clean"]["native_vae_dct"]=read(a.COMPLEMENT,a.ORIGINAL);self.assertFalse(self.analyze()["gates"]["complete"])
    def test_coefficient_votes_tie_and_reference_not_extractor(self):
        s=read(a.ORIGINAL,a.ORIGINAL,True);self.assertEqual(a.readout(s,a.ORIGINAL,True)["intended_matches"],16)
        s["selected_coefficients"][0]=-.5
        with self.assertRaises(ValueError):a.readout(s,a.ORIGINAL,True)
        word="1"*14+"0"*2;self.assertEqual(a.words(word,"1"*16)["intended_matches"],14);self.assertTrue(a.words(word,"1"*16)["intended_present"])
        self.assertEqual(a.words(word,a.COMPLEMENT)["bits"],word)
    def test_corrupt_artifact_and_traversal(self):
        p=self.d/"fixture.bin";p.write_bytes(b"abc");r={"path":p.name,"sha256":a.sha(p),"bytes":3};self.assertEqual(a.artifact(self.d,r),p.name);p.write_bytes(b"abd")
        with self.assertRaises(ValueError):a.artifact(self.d,r)
        with self.assertRaises(ValueError):a.artifact(self.d,{"path":"../fixture.bin"})
    def test_quality_bool_nonfinite_and_strict_boundary(self):
        self.assertFalse(a.quality(q(35))["quality_pass"])
        for bad in (True,float("nan"),float("inf"),"36"):
            v=q();v["psnr_db"]=bad
            with self.assertRaises(ValueError):a.quality(v)
    def test_trace_subset_prevents_completion(self):
        p=self.d/"seed1000-C-L100-trace.jsonl";lines=p.read_text().splitlines();p.write_text("\n".join(lines[:-1]));self.assertFalse(self.analyze()["gates"]["complete"])
if __name__=="__main__":unittest.main()

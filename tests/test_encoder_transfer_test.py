"""CPU-only endpoint, protocol arithmetic and resume tests; no real images."""
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import encoder_transfer_test as et


class ThresholdTests(unittest.TestCase):
    def test_exact_native_thresholds_and_minimality(self):
        for bits,expected in ((32,27),(100,69)):
            k=et.binomial_threshold(bits)
            self.assertEqual(k,expected)
            numerator=sum(math.comb(bits,j) for j in range(k,bits+1))
            previous=sum(math.comb(bits,j) for j in range(k-1,bits+1))
            self.assertLessEqual(numerator*10000,2**bits)
            self.assertGreater(previous*10000,2**bits)

    def test_payload_schedule_and_decoder_failure(self):
        bits=et.message(30,100)
        self.assertEqual(bits,et.message(30,100))
        self.assertNotEqual(bits,et.message(72,100))
        self.assertEqual(set(bits),{0,1})
        self.assertFalse(et.presence(None,bits)["present"])
        self.assertTrue(et.presence(bits,bits)["present"])
        self.assertFalse(et.presence([1-b for b in bits],bits)["present"])
        with self.assertRaises(ValueError): et.presence([0]*99,bits)


class DecisionTests(unittest.TestCase):
    def decide(self,f5,b=45,**kw):
        args=dict(n=60,f5=f5,c0_false=0,wrong_false=0,unresolved_negatives=0,external_counts={"wam":b})
        args.update(kw)
        return et.decision(**args)

    def test_boundary_inequalities_and_margin(self):
        self.assertEqual(self.decide(29)["label"],"FAILS")
        self.assertEqual(self.decide(30)["label"],"PARTIAL")
        self.assertEqual(self.decide(44)["label"],"PARTIAL")
        self.assertEqual(self.decide(45,48)["route"],"ROUTE A")
        self.assertEqual(self.decide(45,49)["route"],"ROUTE B")
        self.assertEqual(self.decide(45,c0_false=1)["label"],"PARTIAL")
        self.assertEqual(self.decide(45,wrong_false=1)["label"],"PARTIAL")
        self.assertEqual(self.decide(45,unresolved_negatives=1)["label"],"PARTIAL")
        self.assertEqual(self.decide(29,unresolved_negatives=100)["route"],"ROUTE C")

    def test_scaled_odd_n_and_unavailable_external(self):
        result=self.decide(46,b=46,n=61)
        self.assertEqual(result["transfer_cut"],46)
        self.assertEqual(result["margin"],4)
        self.assertEqual(self.decide(30,b=40,n=61)["label"],"FAILS")
        self.assertEqual(self.decide(45,external_counts={})["route"],"ROUTE UNDECIDED")

    def test_source_majority_with_missing_calls(self):
        self.assertTrue(et.majority({12:True,13:True}))
        self.assertFalse(et.majority({12:True,13:False,14:None}))
        self.assertFalse(et.majority({12:True}))
        with self.assertRaises(ValueError): et.majority({99:True})


class PredicateTests(unittest.TestCase):
    def test_historical_semantic_read_differs_from_recomputed_match(self):
        d=dict(semantic=dict(found=True,read=False,content_match=True,decoded_code="0000000f"),instance={})
        p=et.endpoints(d,dict(q="0000000f",h="00000001"))
        self.assertTrue(p["S"])
        self.assertTrue(p["recomputed_only_S"])
        self.assertFalse(p["C"])
        self.assertFalse(p["Q"])
        d["semantic"]["read"]=True
        p=et.endpoints(d,dict(q="0000000f"))
        self.assertTrue(p["C"])
        self.assertTrue(p["J"])
        self.assertFalse(p["H"])
        p=et.endpoints(d)
        self.assertTrue(p["C"])
        self.assertFalse(p["Q"])

    def test_presence_and_wrong_owner_are_distinct_endpoints(self):
        d=dict(semantic=dict(found=False,read=True,content_match=False,decoded_code="ff"),
               instance=dict(found=True,read=False))
        p=et.endpoints(d,{"q":"ff"})
        self.assertTrue(p["Q"])
        self.assertTrue(p["A"])
        self.assertFalse(p["C"])
        self.assertFalse(p["J"])


class IntervalTests(unittest.TestCase):
    def test_closed_form_boundaries(self):
        self.assertAlmostEqual(et.cp_interval(0,60)[1],1-.025**(1/60),places=12)
        self.assertAlmostEqual(et.cp_interval(60,60)[0],.025**(1/60),places=12)
        self.assertEqual(et.cp_interval(0,60)[0],0)
        self.assertEqual(et.cp_interval(60,60)[1],1)
        low,high=et.cp_interval(30,60)
        self.assertAlmostEqual(low,1-high,places=12)
        self.assertIsNone(et.cp_interval(0,0))

    def test_paired_test_uses_discordant_sources(self):
        self.assertEqual(et.sign_test([True]*5,[False]*5)["p_two_sided"],.0625)
        self.assertEqual(et.sign_test([True,False],[True,False])["p_two_sided"],1.)


class JournalTests(unittest.TestCase):
    def test_torn_tail_and_terminal_error_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"rows.jsonl"
            path.write_bytes(b'{"id":"a","status":"error"}\n{"id":')
            journal=et.Journal(path)
            self.assertTrue(journal.done("a"))
            self.assertEqual(len(list(Path(temp).glob("interrupted-journal-*.bin"))),1)
            journal.append(dict(id="b",status="ok"))
            self.assertEqual(set(et.Journal(path).latest),{"a","b"})
            self.assertEqual(json.loads(path.read_text().splitlines()[0])["status"],"error")


class InventoryTests(unittest.TestCase):
    def config(self):
        return dict(n=60,arms=["f5-r2","v5-r3","wam","vine-r"],channels=[
            dict(id="R1",strengths=[.1,.2,.4],seeds=[12,13,14])])

    def sources(self):
        return dict(sources=[dict(source_id=i) for i in range(60)],smoke=[dict(source_id=60),dict(source_id=61)])

    def test_unmarked_output_shared_but_read_by_each_detector(self):
        units=list(et.plan(self.config(),self.sources()))
        self.assertEqual(len(units),60*5*(1+9))
        self.assertEqual(len({u["id"] for u in units}),len(units))
        self.assertEqual(sum(u["control"]=="C0" for u in units),60*10)

    def test_missing_inventory_never_disappears_from_denominator(self):
        result=et.analyze(self.config(),self.sources(),{})
        self.assertEqual(result["decision"]["label"],"FAILS")
        self.assertEqual(result["decision"]["unresolved_negatives"],1080)
        self.assertEqual(result["cells"]["f5-r2/R1/0.2/C"]["planned_sources"],60)
        self.assertEqual(result["missing_units"],3000)
        with self.assertRaises(ValueError): et.analyze(self.config(),self.sources(),{"unplanned":{}})

    def test_unavailable_comparison_keeps_holm_slot_without_invented_inference(self):
        rows={}
        for sid in range(60):
            for seed in (12,13,14):
                rows[et.unit_id(sid,"R1",.2,seed,"f5-r2")]=dict(status="generated",
                    detections={"f5-r2":{et.ALPHA:dict(status="ok",endpoints={"C":True})}})
        result=et.analyze(self.config(),self.sources(),rows)
        for comparison in result["paired_primary_comparisons"].values():
            self.assertIsNone(comparison["p_two_sided"])
            self.assertIsNone(comparison["holm_adjusted_p"])
            self.assertEqual(comparison["holm_internal_p"],1.)
            self.assertEqual(comparison["holm_family_size"],3)
            self.assertEqual(comparison["wins"],60)
            self.assertEqual(comparison["paired_difference"],1.)
        self.assertEqual(result["cells"]["wam/R1/0.2/presence"]["positive_sources"],0)


class FrozenContractTests(unittest.TestCase):
    def test_json_hashes_survive_git_lf_checkout(self):
        config=et.read(et.ROOT/"research/encoder-transfer-20261019/frozen-config.json")
        for key in ("sources","asset_plan","profile"):
            data=(et.ROOT/config[key+"_file"]).read_bytes()
            self.assertNotIn(b"\r\n",data)
            self.assertEqual(et.hashlib.sha256(data).hexdigest(),config[key+"_sha256"])
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"manifest.json"
            et.write(path,dict(example=[1,2]))
            self.assertNotIn(b"\r\n",path.read_bytes())

    def test_frozen_roster_assets_and_source_schedule(self):
        config,sources=et.load_contract(et.ROOT/"research/encoder-transfer-20261019/frozen-config.json")
        self.assertEqual(config["n"],60)
        self.assertEqual(len(list(et.plan(config,sources))),7500)
        self.assertEqual(len(list(et.plan(config,sources,True))),250)
        self.assertEqual([x["source_id"] for x in sources["smoke"]],[1790,1822])
        self.assertEqual(config["primary"]["negative_endpoint"],"A")
        assets=et.read(et.ROOT/config["asset_plan_file"])
        self.assertLess(assets["total_file_bytes"],40_000_000_000)
        self.assertEqual(len(assets["files"]),len({x["path"] for x in assets["files"]}))
        self.assertTrue(all(len(x["sha256"])==64 for x in assets["files"]))

    def test_f5_parameters_identical_to_historical_literal(self):
        import ast
        source=ast.parse((et.ROOT/"scripts/registry_step1_transfer.py").read_text())
        call=next(n.value for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="F5_PARAMS" for t in n.targets))
        historical={k.arg:ast.literal_eval(k.value) for k in call.keywords}
        config=et.read(et.ROOT/"research/encoder-transfer-20261019/frozen-config.json")
        self.assertEqual(config["f5"],historical)


class ReportingTests(unittest.TestCase):
    def test_external_native_and_exact_source_majorities_are_separate(self):
        from encoder_transfer_reporting import reporting
        config=dict(arms=["wam"],channels=[dict(id="R1",strengths=[.2],seeds=[12,13,14])])
        sources=dict(sources=[dict(source_id=1)])
        rows={}
        for seed,accuracy,native in ((12,1.,True),(13,.875,True),(14,.5,False)):
            rows[et.unit_id(1,"R1",.2,seed,"wam")]=dict(status="generated",detections={"wam":{et.ALPHA:dict(
                status="ok",presence=dict(present=accuracy>=27/32,accuracy=accuracy),
                native=dict(present=native),raw=dict(native_mask_fraction=.1 if native else .01))}})
        points=reporting(config,sources,rows,{})["external_operating_points"]["wam/R1/0.2"]["source_operating_points"]
        self.assertEqual(points["native_mask_presence"]["positive_sources"],1)
        self.assertEqual(points["common_presence"]["positive_sources"],1)
        self.assertEqual(points["exact_message"]["positive_sources"],0)
        self.assertEqual(points["exact_message"]["planned_sources"],1)

    def test_persisted_detection_survives_interrupted_quality_pass(self):
        from encoder_transfer_reporting import score
        row=dict(status="generated",detections={"f5-r2":{et.ALPHA:dict(status="ok",endpoints={"C":True})},
                    "wam":{et.ALPHA:dict(status="ok",presence=dict(accuracy=.875,present=True),raw=dict(native_mask_fraction=.4))}})
        self.assertIs(et.call_value(row,"f5-r2",et.ALPHA,"C"),True)
        self.assertIs(et.call_value(row,"wam",et.ALPHA,"presence"),True)
        self.assertEqual(score(row,"wam","agreement"),.875)
        self.assertEqual(score(row,"wam","mask"),.4)
        self.assertIsNone(et.call_value(row,"f5-r2",et.BETA,"A"))
        row["detections"]["f5-r2"][et.ALPHA]["status"]="error"
        self.assertIsNone(et.call_value(row,"f5-r2",et.ALPHA,"C"))

    def test_roc_ties_missing_negatives_and_abstention(self):
        from encoder_transfer_reporting import empirical_roc
        self.assertEqual(empirical_roc([.9],[None])["status"],"not_estimable_unresolved_negatives")
        result=empirical_roc([.9,.9,float('-inf')],[.9,.1,.1])
        self.assertEqual(result["strict_fpr_targets"]["0.01"]["tp"],0)
        self.assertEqual(result["points"][1]["fp"],1)
        self.assertEqual(result["points"][1]["tp"],2)
        self.assertEqual(result["points"][-1]["tp"],2)

    def test_quality_match_is_blind_to_success(self):
        from encoder_transfer_reporting import matched_grid
        config=dict(arms=["f5-r2","wam"],channels=[dict(id="R1",strengths=[.1,.2,.4],seeds=[12,13,14])])
        sources=dict(sources=[dict(source_id=1)])
        rows={}
        for arm in config["arms"]:
            for strength in (.1,.2,.4):
                for seed in (12,13,14):
                    rows[et.unit_id(1,"R1",strength,seed,arm)]=dict(distortion=dict(status="ok",psnr_db=30,ssim_rgb=.95,lpips=.08))
        vectors={f'{arm}/R1/{s}/{"C" if arm=="f5-r2" else "presence"}':[arm=="f5-r2"] for arm in config["arms"] for s in (.1,.2,.4)}
        first=matched_grid(config,sources,rows,vectors)["f5-r2/R1 vs wam/R1"][1]["selected_pairs"][0]
        vectors={k:[not v[0]] for k,v in vectors.items()}
        second=matched_grid(config,sources,rows,vectors)["f5-r2/R1 vs wam/R1"][1]["selected_pairs"][0]
        self.assertEqual((first["left_strength"],first["right_strength"]),(.1,.1))
        self.assertEqual((second["left_strength"],second["right_strength"]),(.1,.1))
        self.assertNotEqual(first["left"],second["left"])


class RuntimePlanningTests(unittest.TestCase):
    def test_phase_memory_retains_overall_peak_across_resets_and_resume(self):
        import encoder_transfer_runtime as run
        current={"peak":3}
        cuda=SimpleNamespace(synchronize=lambda:None,reset_peak_memory_stats=lambda:current.update(peak=3),
                             memory_allocated=lambda:3,max_memory_allocated=lambda:current["peak"])
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"memory.json"
            memory=run.PhaseMemory(cuda,path)
            memory.begin("embedding/wam")
            current["peak"]=100
            memory.begin("extraction/wam")
            current["peak"]=20
            memory.finish(incomplete=True)
            resumed=run.PhaseMemory(cuda,path)
            self.assertEqual(resumed.peak,100)
            self.assertEqual([r["peak_allocated_bytes"] for r in resumed.records],[100,20])
            self.assertTrue(resumed.records[-1]["incomplete"])

    def test_vae_guard_rejects_nonfinite_and_wrong_precision_before_quantization(self):
        import torch
        import encoder_transfer_runtime as run
        state={"output":torch.ones(1,dtype=torch.float32)}
        vae=SimpleNamespace(config=SimpleNamespace(force_upcast=True),
            parameters=lambda:[torch.ones(1,dtype=torch.float32)],
            encode=lambda x:SimpleNamespace(latent_dist=SimpleNamespace(parameters=state["output"])),
            decode=lambda x,**kw:(state["output"],))
        run.guard_vae(vae,torch,require_fp32=True)
        vae.encode(torch.ones(1))
        vae.decode(torch.ones(1))
        for invalid in (float("nan"),float("inf")):
            state["output"]=torch.tensor([invalid])
            with self.assertRaisesRegex(ValueError,"Nonfinite"): vae.decode(torch.ones(1))
            with self.assertRaisesRegex(ValueError,"Nonfinite"): vae.encode(torch.ones(1))
        with self.assertRaisesRegex(ValueError,"entirely in fp32"):
            vae.decode(torch.ones(1,dtype=torch.float16))

    def test_budget_uses_instance_start_and_dollar_cap(self):
        import encoder_transfer_runtime as run
        with patch.object(run.time,"time",return_value=1_000_000):
            b=run.Budget("1970-01-12T13:46:40+00:00",2.)
            self.assertEqual(b.deadline-b.start,7.5*3600)
            self.assertEqual(b.compute_deadline,b.deadline-1800)
            b.check()
            with self.assertRaises(ValueError): run.Budget("1970-01-12T13:46:40",1.)

    def test_projection_drops_only_allowed_cells(self):
        import encoder_transfer_runtime as run
        config,sources=et.load_contract(et.ROOT/"research/encoder-transfer-20261019/frozen-config.json")
        rows={u["id"]:{**u,"status":"ok","generation_seconds":1.,"distortion":{"status":"ok"}} for u in et.plan(config,sources,True)}
        for row in rows.values():
            row["detections"]={m:{o:{"status":"ok"} for o in (et.ALPHA,et.BETA)} for m in config["arms"]}
        complete=run.projected_seconds(config,sources,rows)
        effective,projection=run.budget_contract(config,sources,rows,complete-100)
        self.assertEqual(next(c for c in effective["channels"] if c["id"]=="R1")["strengths"],[.2,.4])
        self.assertEqual(next(c for c in effective["channels"] if c["id"]=="R0")["strengths"],[.2,.4])
        self.assertFalse(next(c for c in effective["channels"] if c["id"]=="R1-rinse")["enabled"])
        self.assertEqual(config["channels"][0]["strengths"],[.1,.2,.4])
        et.validate_effective(config,effective)
        effective["n"]=61
        with self.assertRaises(ValueError): et.validate_effective(config,effective)
        with self.assertRaises(TimeoutError): run.budget_contract(config,sources,rows,1)
        rows.pop(next(iter(rows)))
        with self.assertRaisesRegex(ValueError,"missing a planned unit"):
            run.projected_seconds(config,sources,rows)

    def test_rinse_reuses_saved_first_pass_and_resume_preserves_errors(self):
        import encoder_transfer_runtime as run
        config=dict(arms=["wam"],implementation_seed=42,payload_bits={"wam":32},message_seed=1,channels=[
            dict(id="R1",kind="diffusion",family="sdxl",resolution=1024,strengths=[.1],seeds=[12,13,14]),
            dict(id="R1-rinse",kind="rinse",family="sdxl",base_channel="R1",resolution=1024,strengths=[.1],pass_strength=.1,seeds=[12,13,14],seed_offset=100)])
        sources=dict(sources=[],smoke=[dict(source_id=1)])
        calls=[]
        class WamFake:
            def __init__(self,*a): pass
            def embed(self,rgb,bits): return rgb+["mark"]
        class GeneratorFake:
            def __init__(self,*a): pass
            def __call__(self,rgb,strength,seed):
                calls.append((list(rgb),seed))
                if seed==13: raise RuntimeError("fixture failed generation")
                return rgb+[seed]
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            journal=et.Journal(out/"rows.jsonl")
            def save(path,rgb):
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps(rgb))
                return dict(path=str(path),sha256=et.digest(path))
            def load(path):
                return json.loads(Path(path).read_text()) if Path(path).exists() else ["source"]
            with patch.multiple(run,Wam=WamFake,Regenerator=GeneratorFake,seed_everything=lambda x:None,
                                release=lambda:None,resize_rgb=lambda x,size:x,load_rgb=load,save_rgb=save):
                run.produce_images(config,sources,out,out,journal,SimpleNamespace(check=lambda:None),True)
                count=len(calls)
                run.produce_images(config,sources,out,out,journal,SimpleNamespace(check=lambda:None),True)
            self.assertEqual(len(calls),count)
            self.assertTrue(any(seed==112 and 12 in rgb for rgb,seed in calls))
            self.assertFalse(any(seed==113 for rgb,seed in calls))
            self.assertEqual(journal.latest[et.unit_id(1,"R1",.1,13,"wam")]["status"],"error")
            self.assertEqual(journal.latest[et.unit_id(1,"R1-rinse",.1,13,"wam")]["status"],"input_missing")


if __name__ == "__main__":
    unittest.main()

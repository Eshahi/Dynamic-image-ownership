"""CPU receipt and fixed-denominator analysis for the frozen C-L100 diagnostic."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,subprocess,sys,time,traceback
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path(r"W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ARMS=("C0-replay","C-E100-replay","C-L100","C-L100-complement")
ORIGINAL="1011010001101001"
COMPLEMENT="0100101110010110"
STAGES=("terminal_predecode","clipped_float_cycle","clean_rgb8","additional_vae_rgb8")
TRACE_STAGES=("ordinary_predicted_clean","corrected_predicted_clean","effective_fp16_predicted_clean","actual_noisy_scheduler_output")
SOURCE_SHA="c3436690fd0ae549d0a2a3ac71c00e43105d753697f0b26ce61984ccee62ff94"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finite(v):return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
def require(v,message):
    if not v:raise ValueError(message)
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def words(word,intended):
    require(isinstance(word,str) and len(word)==16 and set(word)<=set("01"),"binary16 word required")
    result={"bits":word}
    for name,target in (("intended",intended),("original",ORIGINAL),("complement",COMPLEMENT)):
        n=sum(a==b for a,b in zip(word,target));result.update({name+"_matches":n,name+"_present":n>=14})
    return result

@lru_cache(maxsize=128)
def wrong_queries(word):
    values=[]
    for i in range(64):
        counter=0
        while True:
            h=hashlib.shake_256(f"m1-progressive-wrong-payload-v1:{i}:{counter}".encode()).digest(2)
            other="".join(f"{b:08b}" for b in h)
            if other!=ORIGINAL:break
            counter+=1
        values.append(sum(a==b for a,b in zip(word,other))/16)
    return values

def readout(value,intended,coefficients=False):
    require(isinstance(value,dict),"missing readout")
    result=words(value.get("bits"),intended)
    for key,v in result.items():require(value.get(key)==v and (not key.endswith("_present") or isinstance(value.get(key),bool)),"readout mismatch: "+key)
    for name in ("intended","original","complement"):
        require(value.get(name+"_bit_accuracy")==result[name+"_matches"]/16,"accuracy mismatch")
    q=value.get("wrong_payload_queries",{});expected=wrong_queries(result["bits"])
    require(q.get("bit_accuracies")==expected and q.get("queries")==64 and q.get("denominator")==64 and q.get("false_findings")==sum(x>=.875 for x in expected),"wrong-query mismatch")
    result["wrong64_positive_queries"]=sum(x>=.875 for x in expected)
    if coefficients:
        c=value.get("selected_coefficients")
        require(isinstance(c,list) and len(c)==128 and all(finite(x) for x in c),"missing/nonfinite coefficients")
        word="".join(str(int(sum(x>0 for x in c[i:i+8])>4)) for i in range(0,128,8))
        require(word==result["bits"],"coefficient vote mismatch")
        target=[.5 if b=="1" else -.5 for b in intended for _ in range(8)]
        mse=sum((a-b)**2 for a,b in zip(c,target))/128
        require(finite(value.get("target_mse")) and math.isclose(mse,value["target_mse"],rel_tol=2e-5,abs_tol=1e-6),"coefficient MSE mismatch")
        sign_matches=sum((a>0)==(b>0) for a,b in zip(c,target))
        require(value.get("coefficient_sign_matches")==sign_matches and value.get("zero_count")==sum(x==0 for x in c) and value.get("nonfinite_count")==0,"coefficient diagnostics mismatch")
        result.update(target_mse=mse,coefficient_sign_matches=sign_matches,zero_count=sum(x==0 for x in c))
    return result

def quality(q):
    require(isinstance(q,dict) and isinstance(q.get("psnr_infinite"),bool),"missing quality")
    require(q["psnr_infinite"] or finite(q.get("psnr_db")),"nonfinite PSNR")
    require(finite(q.get("ssim_rgb")) and finite(q.get("lpips")),"nonfinite quality")
    passed=(q["psnr_infinite"] or q["psnr_db"]>35) and q["ssim_rgb"]>.9 and q["lpips"]<.1
    require(isinstance(q.get("quality_admissible"),bool) and q["quality_admissible"]==passed,"quality flag mismatch")
    return {k:q.get(k) for k in ("psnr_db","psnr_infinite","ssim_rgb","lpips")}|{"quality_pass":passed}

def artifact(directory,receipt,expected=None):
    require(isinstance(receipt,dict),"missing artifact receipt")
    name=receipt.get("path");require(isinstance(name,str) and Path(name).name==name,"unsafe artifact path")
    if expected:require(name==expected,"artifact identity mismatch")
    p=directory/name;require(p.is_file() and sha(p)==receipt.get("sha256") and p.stat().st_size==receipt.get("bytes"),"artifact hash/size mismatch: "+name)
    if name.endswith(".npy"):
        import numpy as np
        a=np.load(p,allow_pickle=False)
        require(list(a.shape)==receipt.get("shape") and str(a.dtype)==receipt.get("dtype","").replace("torch.",""),"array shape/dtype mismatch")
        require(hashlib.sha256(a.tobytes()).hexdigest()==receipt.get("raw_sha256"),"array raw hash mismatch")
        require(bool(np.isfinite(a).all()),"array nonfinite")
    return name

def provenance(directory,record):
    errors=[];receipts=[]
    def check():
        manifest=directory/"manifest.json";frozen=ROOT/"research/m1-progressive-phase-dev.json"
        require(load(manifest)==load(frozen)==record.get("config"),"frozen manifest/config mismatch")
        require(sha(manifest)==record.get("manifest_sha256"),"manifest receipt mismatch")
        require(record.get("schema_version")=="m1-progressive-phase-diagnostic-v1" and record.get("data_split")=="synthetic" and record.get("seeds")==list(range(1000,1004)),"run schema/split/seeds mismatch")
        committed=record.get("committed_files",{});required={"scripts/m1_progressive_phase.py","research/m1-progressive-phase-dev.json","research/m1-progressive-diagnosis.md","research/m1-progressive-synthetic.json","scripts/m1_progressive_latent.py","scripts/m1_gaussian_shading.py","scripts/m1_phasemark.py","scripts/three_threat_models.py","scripts/three_threat_protocol.py","scripts/m1_latent_reconstruction.py","scripts/check_a6_lpips_assets.py","scripts/verify_science_assets.py","scripts/a6_clip_visual.py","research/a6-candidate-model-assets.json"}
        require(set(committed)==required,"missing/unexpected committed dependencies")
        require("scripts/m1_progressive_phase.py" in committed and "research/m1-progressive-phase-dev.json" in committed,"missing runner/manifest commits")
        for relative,v in committed.items():
            path=ROOT/relative;require(path.resolve().is_relative_to(ROOT.resolve()),"unsafe committed path")
            oid=subprocess.check_output(["git","rev-parse",record["commit"]+":"+relative],cwd=ROOT,text=True).strip()
            current=subprocess.check_output(["git","hash-object","--path="+relative,str(path)],cwd=ROOT,text=True).strip()
            require(oid==v.get("git_blob_oid")==current and sha(path)==v.get("working_sha256"),"committed input mismatch: "+relative)
            receipts.append({"path":str(path),"sha256":sha(path),"git_blob_oid":oid})
        source=Path(record["config"]["source_run"]);require(sha(source/"run.json")==SOURCE_SHA==record.get("source_receipts",{}).get("run_sha256"),"old source receipt mismatch")
        old=load(source/"run.json");require(old.get("outcome")=="completed" and old.get("script_sha256")==record["config"]["original_script_sha256"],"old source/script outcome mismatch")
        expected={}
        for seed in range(1000,1004):
            for arm,ident in ((ARMS[0],f"seed{seed}-C0"),(ARMS[1],f"seed{seed}-a0.5-e100.0")):
                candidates=[r for r in old["rows"] if r["id"]==ident and r["outcome"]=="completed"];require(len(candidates)==1,"old replay row missing/duplicate")
                for channel in ("clean","vae"):
                    candidates2=[x for x in candidates[0]["artifacts"] if x["path"].endswith("-"+channel+".png")];require(len(candidates2)==1,"old replay artifact missing/duplicate")
                    x=candidates2[0];require(sha(source/x["path"])==x["sha256"],"old replay PNG hash mismatch");expected[(seed,arm,channel)]=x["sha256"]
        mapped=record["source_receipts"].get("replay_pngs",{})
        require(set(mapped)=={str(k) for k in expected},"old receipt mapping membership")
        require(all(mapped[str(k)]["sha256"]==h for k,h in expected.items()),"old receipt mapping mismatch")
        receipts.append({"path":str(source/"run.json"),"sha256":SOURCE_SHA})
        return expected
    try:return check(),errors,receipts
    except Exception as e:errors.append(str(e));return {},errors,receipts

def analyze(directory,record,expected_old,provenance_errors):
    directory=Path(directory);inventory=[];images=[];stages=[];traces=[];errors=list(provenance_errors);replays=[];initial={};artifact_names=set()
    rows=record.get("rows",[])
    if record.get("outcome")!="completed":errors.append("source run not completed")
    expected_ids={f"seed{s}-{a}" for s in range(1000,1004) for a in ARMS}
    extra=[r for r in rows if not isinstance(r,dict) or r.get("id") not in expected_ids]
    if extra:errors.append("unexpected generation rows")
    for seed in range(1000,1004):
        for arm in ARMS:
            ident=f"seed{seed}-{arm}"; intended=COMPLEMENT if arm.endswith("complement") else ORIGINAL
            candidates=[r for r in rows if isinstance(r,dict) and r.get("id")==ident];unit_errors=[];valid=False
            r=candidates[0] if len(candidates)==1 else {}
            inv={"id":ident,"seed":seed,"arm":arm,"source_n":1,"outcome":r.get("outcome","missing"),"complete":False,"error":r.get("error")}
            try:
                require(len(candidates)==1,"missing/duplicate generation")
                require(r.get("seed")==seed and r.get("arm")==arm and r.get("intended_payload")==intended and r.get("original_payload")==ORIGINAL,"generation identity mismatch")
                for x in r.get("artifacts",[]):
                    name=artifact(directory,x);require(name.startswith(ident+"-"),"artifact generation mismatch");require(name not in artifact_names,"duplicate artifact path");artifact_names.add(name)
                require(r.get("outcome")=="completed","noncompleted generation")
                expected_names={ident+"-"+n+".npy" for n in ("initial_latent","terminal_latent","decoder_float","clipped_decoder_float","clipped_float_cycle_latent")}|{ident+"-trace.jsonl",ident+"-clean.png",ident+"-vae.png"}
                require({x.get("path") for x in r.get("artifacts",[])}==expected_names and len(r["artifacts"])==8,"generation artifact inventory mismatch")
                require(finite(r.get("duration_seconds")) and r["duration_seconds"]>=0 and finite(r.get("peak_allocated_bytes")),"missing generation timing/budget")
                g=r.get("generation",{});require(g.get("guided_step_indices")==([] if arm==ARMS[0] else list(range(25)) if arm==ARMS[1] else list(range(25,50))),"guidance interval mismatch")
                require(len(g.get("timesteps",[]))==50,"missing timesteps")
                for name in ("initial_latent","terminal_latent","decoder_float","clipped_decoder_float","clipped_float_cycle_latent"):
                    receipt=g.get(name);artifact(directory,receipt,ident+"-"+name+".npy");require(receipt["path"] in artifact_names,"array absent from artifact inventory")
                initial.setdefault(seed,[]).append(g["initial_latent"]["raw_sha256"])
                require(r.get("paired_initial_latent_matches") is True and g.get("safety_flag") is False and finite(g.get("clipping_fraction")) and 0<=g["clipping_fraction"]<=1,"pair/safety/clipping metadata")
                inv.update(quality(r.get("quality_to_new_C0")));inv["old_C0_quality"]=quality(r.get("quality_to_old_C0"))
                require(set(g.get("readout_stages",{}))==set(STAGES),"endpoint stage inventory")
                for name in STAGES:
                    s=g["readout_stages"][name];require(s.get("eligible_image_detector")== (name in STAGES[2:]),"oracle eligibility mismatch")
                    stages.append({"id":ident,"seed":seed,"arm":arm,"stage":name,"eligible_image_detector":name in STAGES[2:],"complete":True,**readout(s,intended,True)})
                trace_path=directory/(ident+"-trace.jsonl");require(trace_path.name in artifact_names,"trace receipt missing")
                trows=[json.loads(line) for line in trace_path.read_text().splitlines()];require(len(trows)==50 and [t.get("step_index") for t in trows]==list(range(50)),"trace missing/duplicate steps")
                for t in trows:
                    require(t.get("timestep")==g["timesteps"][t["step_index"]] and t.get("guided")== (t["step_index"] in g["guided_step_indices"]),"trace schedule mismatch")
                    require(set(t.get("stages",{}))==set(TRACE_STAGES),"trace stage inventory")
                    for key in ("q_t","gradient_l2","intended_clean_correction_l2","epsilon_correction_before_cast_l2","epsilon_correction_after_cast_l2","changed_channel0_fraction","local_scheduler_displacement_l2","local_formula_discrepancy_l2"):
                        require(finite(t.get(key)),"missing/nonfinite trace "+key)
                    require(isinstance(t.get("changed_other_channels_count"),int) and not isinstance(t.get("changed_other_channels_count"),bool) and t["changed_other_channels_count"]>=0 and t.get("supplied_epsilon_nonfinite_count")==0,"malformed/nonfinite epsilon trace")
                    for name,s in t["stages"].items():traces.append({"id":ident,"seed":seed,"arm":arm,"step_index":t["step_index"],"timestep":t["timestep"],"guided":t["guided"],"stage":name,"q_t":t["q_t"],"local_formula_discrepancy_l2":t["local_formula_discrepancy_l2"],"complete":True,**{k:t[k] for k in ("gradient_l2","intended_clean_correction_l2","epsilon_correction_before_cast_l2","epsilon_correction_after_cast_l2","changed_channel0_fraction","changed_other_channels_count","local_scheduler_displacement_l2")},**readout(s,intended,True)})
                require(set(r.get("conditions",{}))=={"clean","vae"},"condition channel inventory")
                valid=True
            except Exception as e:unit_errors.append(str(e))
            for channel in ("clean","vae"):
                v=r.get("conditions",{}).get(channel,{}) if isinstance(r.get("conditions",{}),dict) else {};ir={"id":ident,"seed":seed,"arm":arm,"channel":channel,"complete":False,"outcome":v.get("outcome","missing"),"error":v.get("error")}
                try:
                    require(valid,"generation incomplete: "+"; ".join(unit_errors))
                    require(v.get("outcome")=="completed","noncompleted image condition");artifact(directory,v.get("artifact"),ident+"-"+channel+".png");require(v["artifact"]["path"] in artifact_names,"PNG not in artifact inventory")
                    for decoder in ("native_vae_dct","image_dct_diagnostic"):
                        ir[decoder]=readout(v.get(decoder),intended)
                        require(finite(v.get(decoder+"_seconds")) and v[decoder+"_seconds"]>=0,"missing extraction time");ir[decoder+"_seconds"]=v[decoder+"_seconds"]
                    require(finite(v.get("extract_both_seconds")),"missing total extraction timing")
                    ir["quality_vs_same_arm_clean"]=quality(v.get("quality_vs_same_arm_clean"))
                    endpoint=next(s for s in stages if s["id"]==ident and s["stage"]==("clean_rgb8" if channel=="clean" else "additional_vae_rgb8"));require(endpoint["bits"]==ir["native_vae_dct"]["bits"],"endpoint/primary native word mismatch")
                    if arm in ARMS[:2]:
                        expected=expected_old.get((seed,arm,channel));rp=v.get("replay",{});require(expected is not None,"old replay unavailable")
                        matched=expected==v["artifact"]["sha256"];require(rp.get("expected_sha256")==expected and rp.get("actual_sha256")==v["artifact"]["sha256"] and rp.get("matched") is matched and rp.get("original_latent_hash") is None,"replay metadata mismatch")
                        ir["replay_matched"]=matched;replays.append(matched)
                    ir["complete"]=True
                except Exception as e:ir["validation_error"]=str(e)
                images.append(ir)
            inv["complete"]=valid and all(x["complete"] for x in images[-2:]);inv["validation_errors"]=unit_errors;inventory.append(inv)
    for seed,h in initial.items():
        if len(h)!=4 or len(set(h))!=1:errors.append(f"seed{seed}: paired initial hashes missing/differ")
    stage_map={(x["id"],x["stage"]):x for x in stages}
    stages=[stage_map.get((f"seed{s}-{arm}",name),{"id":f"seed{s}-{arm}","seed":s,"arm":arm,"stage":name,"complete":False,"intended_matches":None,"original_matches":None,"complement_matches":None,"eligible_image_detector":name in STAGES[2:]}) for s in range(1000,1004) for arm in ARMS for name in STAGES]
    trace_map={(x["id"],x["step_index"],x["stage"]):x for x in traces}
    traces=[trace_map.get((f"seed{s}-{arm}",i,name),{"id":f"seed{s}-{arm}","seed":s,"arm":arm,"step_index":i,"stage":name,"complete":False,"intended_matches":None}) for s in range(1000,1004) for arm in ARMS for i in range(50) for name in TRACE_STAGES]
    complete=not errors and len(inventory)==16 and all(x["complete"] for x in inventory) and len(images)==32 and all(x["complete"] for x in images)
    replay=all(replays) if complete and len(replays)==16 else None
    late=[x for x in images if x["arm"] in ARMS[2:]];c0=[x for x in images if x["arm"]==ARMS[0]]
    carrier=all(x["native_vae_dct"]["intended_present"] for x in late) if complete else None
    absence=all(not x["native_vae_dct"]["original_present"] and not x["native_vae_dct"]["complement_present"] for x in c0) if complete else None
    q=all(x["quality_pass"] for x in inventory if x["arm"] in ARMS[2:]) if complete else None
    gates={"complete":complete,"replay":replay,"late_carrier":carrier,"c0_absence":absence,"late_quality":q,"necessary_condition":carrier and absence if complete and replay else None,"quality_attribution":q if complete and replay else None}
    counts=[]
    for arm in ARMS:
        for channel in ("clean","vae"):
            xs=[x for x in images if x["arm"]==arm and x["channel"]==channel];observed=[x for x in xs if x["complete"]]
            for decoder in ("native_vae_dct","image_dct_diagnostic"):
                counts.append({"arm":arm,"channel":channel,"decoder":decoder,"planned_images":4,"source_clusters":4,"observed_complete":len(observed),"intended_positive_n":sum(x[decoder]["intended_present"] for x in observed),"intended_exact_n":sum(x[decoder]["intended_matches"]==16 for x in observed),"wrong_query_denominator_observed":64*len(observed),"wrong_positive_queries":sum(x[decoder]["wrong64_positive_queries"] for x in observed)})
    return dict(gates=gates,planned_generations=16,planned_image_conditions=32,independent_source_clusters=4,errors=errors,inventory=inventory,conditions=images,stages=stages,traces=traces,counts=counts,unexpected_rows=extra,source_outcome=record.get("outcome"),source_error=record.get("error"),budgets={"observed_artifact_bytes":sum(x.get("bytes",0) for r in rows if isinstance(r,dict) for x in r.get("artifacts",[]) if finite(x.get("bytes"))),"observed_peak_allocated_bytes":max((r.get("peak_allocated_bytes",0) for r in rows if isinstance(r,dict) and finite(r.get("peak_allocated_bytes"))),default=None),"declared":record.get("config",{}),"effective_gpu_budget_bytes":record.get("effective_gpu_budget_bytes"),"duration_seconds":record.get("duration_seconds"),"observed_ram_peak":None},caveat="Generated counterfactual only. Oracle stages are ineligible. Fixed SHAKE queries/repeated conditions are dependent. Missing values are not failures or passes; failed attribution gives null scientific gates. No human verdict.")

def csv_write(path,rows):
    flat=[]
    for row in rows:
        out={}
        for k,v in row.items():
            if isinstance(v,dict):out.update({k+"_"+a:b for a,b in v.items() if not isinstance(b,(dict,list))})
            elif not isinstance(v,list):out[k]=v
        flat.append(out)
    with path.open("w",newline="",encoding="utf-8") as f:
        keys=sorted({k for row in flat for k in row});w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(flat)

def run(input_dir,output_dir):
    start=time.monotonic();input_dir=Path(input_dir).resolve();output_dir=Path(output_dir).resolve()
    require(output_dir.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()),"fresh MAIN dev-runs output required")
    output_dir.mkdir(parents=True,exist_ok=False)
    receipt={"schema_version":"m1-progressive-phase-analysis-v1","commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"command":sys.argv,"config":{"inventory":[16,32],"presence_matches":14,"quality":{"psnr_gt":35,"ssim_gt":.9,"lpips_lt":.1}},"data_split":"synthetic","seeds":list(range(1000,1004)),"outcome":"started","duration_seconds":0,"input_files":[]}
    write(output_dir/"run.json",receipt)
    try:
        for name in ("run.json","conditions.json","rows.jsonl","manifest.json"):
            p=input_dir/name
            if p.exists():receipt["input_files"].append({"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size})
        record=load(input_dir/"run.json");expected,errors,provenance_receipts=provenance(input_dir,record)
        try:
            expected_conditions=[dict(generation_id=r["id"],channel=c,**v) for r in record["rows"] for c,v in r["conditions"].items()]
            require(load(input_dir/"conditions.json")==expected_conditions,"run/conditions mismatch")
        except Exception as e:errors.append(str(e))
        result=analyze(input_dir,record,expected,errors);receipt["scientific_input_receipts"]=provenance_receipts
        write(output_dir/"analysis.json",result)
        for key in ("inventory","conditions","stages","traces","counts"):csv_write(output_dir/(key+".csv"),result[key])
        receipt["outcome"]="completed_descriptive_analysis" if result["gates"]["complete"] else "incomplete_descriptive_analysis"
        receipt["source_outcome"]=record.get("outcome");receipt["gates"]=result["gates"];receipt["output_hashes"]={p.name:sha(p) for p in output_dir.iterdir() if p.name!="run.json"}
    except Exception as e:receipt.update(outcome="failed",error=str(e),traceback=traceback.format_exc())
    finally:receipt["duration_seconds"]=time.monotonic()-start;write(output_dir/"run.json",receipt)
    return 0 if receipt["outcome"]!="failed" else 1

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input-dir",required=True,type=Path);p.add_argument("--output-dir",required=True,type=Path);a=p.parse_args();return run(a.input_dir,a.output_dir)
if __name__=="__main__":raise SystemExit(main())

"""Read-only descriptive M1 development-family aggregation; never opens images.

Missing/failed planned cells stay in tables. No method acceptance or human verdict.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
CONFIG={"quality":{"psnr_gt":35,"ssim_gt":.9,"lpips_lt":.1},
        "reconstruction_steps":[0,50,100,200],"semantic_retention_proxy_clip_floor":.85,
        "mode":"exploratory descriptive; no acceptance verdict"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def distribution(values):
    values=[v for v in values if finite(v)]
    return {"n":len(values),"min":min(values) if values else None,
            "mean":statistics.mean(values) if values else None,
            "median":statistics.median(values) if values else None,"max":max(values) if values else None}


def quality(q):
    lp=q.get("lpips",q.get("lpips_alex"))
    ps=q.get("psnr_db")
    ss=q.get("ssim_rgb",q.get("ssim"))
    valid=(finite(ps) or q.get("psnr_infinite") is True) and finite(ss) and finite(lp)
    conjunction=valid and (q.get("psnr_infinite") is True or ps>35) and ss>.9 and lp<.1
    return {"psnr_db":ps,"psnr_infinite":q.get("psnr_infinite",False),"ssim_rgb":ss,
            "lpips":lp,"quality_complete":valid,"quality_all_three":bool(conjunction)}


def attack_quality(q, detected):
    metrics=quality(q)
    cosine=q.get("clip_cosine")
    return {**{"attack_"+k:v for k,v in metrics.items()},"attack_clip_cosine":cosine,
            "detect_and_semantic_retention_proxy":detected and cosine>=CONFIG["semantic_retention_proxy_clip_floor"] if type(detected) is bool and finite(cosine) else None}


def csv_table(path,rows):
    flattened=[]
    for row in rows:
        item={}
        for key,value in row.items():
            if isinstance(value,dict) and value and set(value)<=set(("n","min","mean","median","max")):
                item.update({key+"_"+stat:val for stat,val in value.items()})
            else:item[key]=value
        flattened.append(item)
    rows=flattened
    keys=sorted({k for row in rows for k in row})
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def load_family(name,directory):
    package={"family":name,"directory":str(directory),"input_files":[],"errors":[],"journal":[]}
    def pin(path):
        if not path.is_file():
            package["errors"].append({"path":str(path),"error":"missing file"});return None
        raw=path.read_bytes()
        package["input_files"].append({"path":str(path),"sha256":hashlib.sha256(raw).hexdigest(),"size_bytes":len(raw)})
        return raw.decode("utf-8")
    raw=pin(directory/"run.json")
    try:
        package["run"]=json.loads(raw) if raw else {}
    except Exception as error:
        package["errors"].append({"error":"invalid run.json","detail":str(error)});package["run"]={}
    run=package["run"]
    package["source_outcome"]=run.get("outcome","missing")
    if run and run.get("data_split") not in ("synthetic","development"):
        package["errors"].append({"error":"unsupported split; no journal/scoring analysis"})
        package["excluded"]=True;return package
    command=run.get("command",[])
    manifest_path=None
    if "--manifest" in command:
        try:
            manifest_path=Path(command[command.index("--manifest")+1])
            if not manifest_path.is_absolute(): manifest_path=ROOT/manifest_path
        except Exception as error: package["errors"].append({"error":"manifest command malformed","detail":str(error)})
    if manifest_path:
        raw_manifest=pin(manifest_path)
        if raw_manifest:
            try:
                package["manifest"]=json.loads(raw_manifest)
                package["manifest_hash_matches_run"]=sha(manifest_path)==run.get("manifest_sha256")
                if not package["manifest_hash_matches_run"]:
                    package["errors"].append({"error":"manifest hash mismatch; planned cases unknown"});package["manifest"]={}
            except Exception as error: package["errors"].append({"error":"manifest parse failure","detail":str(error)})
    else: package["errors"].append({"error":"exact manifest path unavailable; no inferred planned cohort"})
    journal_name={"reconstruction":"images.jsonl","gs":"rows.jsonl","progressive":"journal.jsonl"}[name]
    raw_journal=pin(directory/journal_name)
    for number,line in enumerate((raw_journal or "").splitlines(),1):
        try: package["journal"].append(json.loads(line))
        except Exception as error: package["errors"].append({"error":"invalid journal line","line":number,"detail":str(error)})
    return package


def aggregate(rows,keys):
    groups={}
    for row in rows:
        key=tuple(row.get(k) for k in keys);groups.setdefault(key,[]).append(row)
    output=[]
    for group,items in sorted(groups.items(),key=lambda x:str(x[0])):
        valid=[r for r in items if r.get("status") in ("observed","observed_partial")]
        summary={**dict(zip(keys,group)),"planned":len(items),"observed":len(valid),
                 "missing_or_failed":len(items)-len(valid),
                 "observed_from_failed_parent":sum(r.get("status")=="observed_partial" for r in valid),
                 "n_quality_complete":sum(bool(r.get("quality_complete")) for r in valid),
                 "n_quality_all_three":sum(bool(r.get("quality_all_three")) for r in valid)}
        for metric in ("psnr_db","ssim_rgb","lpips","bit_accuracy","detector_seconds","native_seconds","diagnostic_seconds",
                       "attack_psnr_db","attack_ssim_rgb","attack_lpips","attack_clip_cosine"):
            summary[metric]=distribution([r.get(metric) for r in valid])
        summary["psnr_infinite_n"]=sum(bool(r.get("psnr_infinite")) for r in valid)
        for flag in ("detected","wrong_detected","detect_and_semantic_retention_proxy"):
            measured=[r for r in valid if type(r.get(flag)) is bool]
            summary[flag+"_n"]=len(measured)
            summary[flag+"_positive"]=sum(r[flag] for r in measured)
        summary["wrong_query_false_findings"]=sum(r.get("wrong_query_false_findings",0) for r in valid)
        summary["wrong_query_denominator"]=sum(r.get("wrong_query_denominator",0) for r in valid)
        output.append(summary)
    return output


def qualify_pause(packages, receipt_path):
    """Verify all receipt-listed artifacts inside relevant runs, without decoding images."""
    if receipt_path is None:
        return None
    receipt_path=receipt_path.resolve()
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    provenance={"path":str(receipt_path),"sha256":sha(receipt_path),"validated_files":[]}
    seen=set()
    for item in receipt.get("files",[]):
        path=Path(item["path"]).resolve()
        if path in seen:raise ValueError("Duplicate pause receipt artifact: "+str(path))
        seen.add(path)
        relevant=[p for p in packages if path.is_relative_to(Path(p["directory"]).resolve())]
        if not relevant:continue
        if not path.is_file() or path.stat().st_size!=item["bytes"] or sha(path)!=item["sha256"]:
            raise ValueError("Pause receipt artifact hash/size mismatch: "+str(path))
        provenance["validated_files"].append(item)
    for package in packages:
        directory=Path(package["directory"]).resolve()
        entries={Path(x["path"]).resolve() for x in provenance["validated_files"] if Path(x["path"]).resolve().is_relative_to(directory)}
        if entries:
            if not {directory/"run.json",directory/"images.jsonl"}<=entries:
                raise ValueError("Pause receipt must pin run.json and images.jsonl: "+str(directory))
            package["pause_receipt"]=provenance
            package["pause_qualified"]=package["source_outcome"]=="started"
    return provenance


def analyze_reconstruction(packages, receipt_path=None):
    """CLI order is chronology; replacement requires pinned manifest recovery metadata."""
    if isinstance(packages,dict):packages=[packages]
    for package in packages:
        package.pop("pause_receipt",None)
        package.pop("pause_qualified",None)
    receipt=qualify_pause(packages,receipt_path)
    selected={};specs={};attempts=[];errors=[];known_directories={}
    baseline_config=None;cohort_unknown=False
    for sequence,package in enumerate(packages):
        directory=Path(package["directory"]).resolve();run=package["run"]
        manifest=package.get("manifest",{});cases=manifest.get("cases",[])
        config=manifest.get("config")
        if not cases:
            cohort_unknown=True
            errors.append("Exact planned cohort unavailable: "+str(directory));continue
        if config is None or config!=run.get("config") or config.get("steps")!=CONFIG["reconstruction_steps"]:
            raise ValueError("Reconstruction run/manifest config or four checkpoint steps mismatch")
        if baseline_config is None:baseline_config=config
        if config!=baseline_config:raise ValueError("Reconstruction attempt configurations differ")
        if directory in known_directories.values():raise ValueError("Repeated reconstruction directory")
        if directory.name in known_directories:raise ValueError("Ambiguous reconstruction directory basename")
        recovery=manifest.get("recovery")
        previous=None
        if recovery:
            previous=known_directories.get(recovery.get("previous_run"))
            if previous is None:raise ValueError("Recovery previous_run must precede this run in CLI order")
            if not receipt or recovery.get("receipt_sha256")!=receipt["sha256"]:
                raise ValueError("Recovery mapping requires matching explicit pause receipt")
            previous_package=next(p for p in packages[:sequence] if Path(p["directory"]).resolve()==previous)
            if not previous_package.get("pause_qualified"):
                raise ValueError("Recovery predecessor is not a receipt-qualified interrupted started run")
            previous_ids={c["id"] for c in previous_package.get("manifest",{}).get("cases",[])}
            if any(c["id"] not in previous_ids for c in cases):
                raise ValueError("Recovery contains a source not planned by its predecessor")
        known_directories[directory.name]=directory
        run_sha=next((x["sha256"] for x in package["input_files"] if Path(x["path"]).resolve()==directory/"run.json"),None)
        if not run_sha:raise ValueError("Reconstruction run.json hash unavailable")
        planned_ids=[c["id"] for c in cases]
        if len(set(planned_ids))!=len(planned_ids):raise ValueError("Duplicate reconstruction planned case IDs")
        if any(c.get("id") not in planned_ids for c in run.get("cases",[])):
            errors.append("Unplanned actual reconstruction case: "+str(directory))
        for spec in cases:
            ident=spec["id"]
            if ident in specs and spec!=specs[ident]:raise ValueError("Recovery source identity/hash mismatch")
            specs[ident]=spec
            matching=[c for c in run.get("cases",[]) if c.get("id")==ident]
            case=matching[0] if len(matching)==1 else {}
            cells=[]
            for step in CONFIG["reconstruction_steps"]:
                points=[p for p in case.get("checkpoints",[]) if p.get("step")==step]
                point=points[0] if len(points)==1 else None
                status="ambiguous_duplicate" if len(matching)>1 or len(points)>1 else "observed" if point and case.get("outcome")=="completed" else "observed_partial" if point else "missing_or_failed"
                cell={"family":"reconstruction","case":ident,"step":step,"status":status,
                      "attempt_sequence":sequence,"chosen_run_directory":str(directory),"chosen_run_sha256":run_sha,
                      "source_sha256":spec.get("sha256"),"source_run_outcome":package["source_outcome"],
                      "pause_qualified":bool(package.get("pause_qualified")),
                      "parent_outcome":case.get("outcome","not_attempted"),"error":case.get("error"),
                      **quality(point or {}),"measurement_seconds":(point or {}).get("seconds")}
                cells.append(cell);attempts.append(cell.copy())
            if ident in selected:
                prior=Path(selected[ident][0]["chosen_run_directory"]).resolve()
                if previous!=prior:
                    raise ValueError("Overlapping reconstruction case requires explicit recovery mapping: "+str(ident))
            selected[ident]=cells
        errors.extend(package["errors"])
        if package["source_outcome"]!="completed" and not package.get("pause_qualified"):
            errors.append("Unqualified noncompleted reconstruction run: "+str(directory))
    rows=[row for cells in selected.values() for row in cells]
    for row in attempts:
        row["selected_final_attempt"]=row["attempt_sequence"]==selected[row["case"]][0]["attempt_sequence"]
    return {"raw":rows,"summary":aggregate(rows,["step"]),"attempt_inventory":attempts,
            "pause_receipt":receipt,"errors":errors,"planned_source_n":None if cohort_unknown else len(specs),
            "known_planned_source_n":len(specs),
            "incomplete":bool(errors) or not rows or any(r["status"]!="observed" for r in rows),
            "caveat":"Pure decoder optimization; chronology and declared recovery select whole cases, never favorable scores. Historical partial attempts are retained separately. No universal ceiling or watermark result."}


def analyze_gs(package):
    run=package["run"];config=run.get("config",{});cases=package.get("manifest",{}).get("cases",[])
    actual=package["journal"]
    cases=cases or [{"id":x} for x in sorted({r.get("case") for r in actual if r.get("case")})]
    channels=["clean","vae"]+[f"regen-{s:g}-seed{a}" for s in config.get("strengths",[]) for a in config.get("attack_seeds",[])]
    rows=[]
    for case in cases:
        for channel in channels:
            for arm in ("C0","C1"):
                matches=[r for r in actual if (r.get("case"),r.get("channel"),r.get("arm"))==(case["id"],channel,arm)]
                result=matches[0] if len(matches)==1 else {}
                rows.append({"family":"gs","case":case["id"],"arm":arm,"condition":channel,
                             "status":"observed" if result else "ambiguous_duplicate" if matches else "missing_or_failed",
                             "source_outcome":package["source_outcome"],"source_error":run.get("error"),
                             "bit_accuracy":result.get("bit_accuracy"),"detected":result.get("detected"),
                             "wrong_detected":result.get("wrong_key_detected"),"wrong_bit_accuracy":result.get("wrong_key_bit_accuracy"),
                             "detector_seconds":result.get("detector_seconds"),"detector_unet_evaluations":result.get("detector_unet_evaluations"),
                             "row_duration_seconds":result.get("duration_seconds"),
                             **attack_quality(result.get("quality_vs_same_arm_original",{}),result.get("detected")),
                             **quality(result.get("C1_quality_vs_paired_C0_clean",{})),
                             "quality_reference":"generation counterfactual C0/C1; not fixed-source imperceptibility"})
    return {"raw":rows,"summary":aggregate(rows,["condition","arm"]),
            "caveat":"C1 positives are exploratory survival; C0 positives and C1 wrong-key positives are false findings. C0/C1 differ in initial signs; paired pixel quality is generation-counterfactual distortion, not photographic imperceptibility. DDIM inversion50 UNet calls is side information/cost."}


def analyze_progressive(package):
    run=package["run"];config=run.get("config",{});cases=package.get("manifest",{}).get("cases",[])
    seeds=[c["seed"] for c in cases] or sorted({r.get("seed") for r in run.get("rows",[]) if r.get("seed") is not None})
    conditions=["clean","vae"]+[f"t3-{s}" for s in config.get("attack_strengths",[])]
    rows=[]
    for seed in seeds:
        variants=[("C0",None,None,f"seed{seed}-C0")]+[("C1",a,e,f"seed{seed}-a{a}-e{e}") for a in config.get("alphas",[]) for e in config.get("etas",[])]
        for arm,alpha,eta,ident in variants:
            attempts=[r for r in run.get("rows",[]) if r.get("id")==ident]
            completed=[r for r in attempts if r.get("outcome")=="completed"]
            row=completed[0] if len(completed)==1 else attempts[-1] if attempts and not completed else {}
            for condition in conditions:
                result=row.get("conditions",{}).get(condition,{})
                for extractor,key in (("native","native_vae_dct"),("image_diagnostic","image_dct_diagnostic")):
                    score=result.get(key,{})
                    query=score.get("wrong_payload_queries",{})
                    status="ambiguous_duplicate" if len(completed)>1 else "observed" if score and row.get("outcome")=="completed" else "observed_partial" if score else "missing_or_failed"
                    rows.append({"family":"progressive","case":seed,"arm":arm,"alpha":alpha,"eta":eta,"condition":condition,"extractor":extractor,"status":status,
                                 "attempts":len(attempts),"failed_attempts":sum(r.get("outcome") in ("failed","interrupted") for r in attempts),
                                 "parent_outcome":row.get("outcome","not_attempted"),"error":row.get("error"),
                                 "bit_accuracy":score.get("bit_accuracy"),"detected":score.get("found_descriptive"),
                                 "wrong_detected":score.get("wrong_payload_found_descriptive"),
                                 "wrong_query_false_findings":query.get("false_findings",0),"wrong_query_denominator":query.get("denominator",0),
                                 "wrong_query_accuracies":query.get("bit_accuracies",[]),
                                 "native_seconds":result.get("native_vae_dct_seconds"),"diagnostic_seconds":result.get("image_dct_diagnostic_seconds"),
                                 **attack_quality(result.get("quality_vs_same_arm_clean",{}),score.get("found_descriptive")),
                                 **quality(row.get("quality_to_matched_C0",{})),"quality_reference":"clean matched same-initial-noise C0; duplicated across condition/extractor tables"})
    # Quality unique per seed/variant, not repeated extractors/attacks.
    quality_rows=[r for r in rows if r["arm"]=="C1" and r["condition"]=="clean" and r["extractor"]=="native"]
    return {"raw":rows,"summary":aggregate(rows,["arm","alpha","eta","condition","extractor"]),
            "quality_summary":aggregate(quality_rows,["alpha","eta"]),
            "attempt_inventory":run.get("rows",[]),
            "caveat":"Native extractor includes VAE weights; image DCT is a separate diagnostic. Public16bit carrier lacks content/OwnerID binding. Wrong-payload64 queries share each extracted word and reused hypotheses; counts are correlated descriptive query outcomes, never independent image-level FPR."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruction-dir",type=Path,action="append")
    parser.add_argument("--reconstruction-pause-receipt",type=Path)
    for name in ("gs","progressive"):parser.add_argument("--"+name+"-dir",type=Path)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args();started=time.monotonic()
    sources={name:getattr(args,name+"_dir") for name in ("reconstruction","gs","progressive") if getattr(args,name+"_dir") is not None}
    if not sources:parser.error("At least one family directory required")
    output=args.output_dir.resolve()
    if not output.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):parser.error("Output must be MAIN/.thesis-build/dev-runs")
    output.mkdir(parents=True,exist_ok=False)
    record={"schema_version":"m1-family-analysis-v1","commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
            "command":sys.argv,"config":CONFIG,"data_split":"development/synthetic inputs only",
            "script_sha256":sha(__file__),"duration_seconds":0,"outcome":"started","families":{},"errors":[],"seeds":[]}
    write(output/"run.json",record)
    try:
        analyses={}
        for name,directory in sources.items():
            if name=="reconstruction":
                packages=[load_family(name,p.resolve()) for p in directory]
                record["families"][name]={"attempts":[{**{k:v for k,v in p.items() if k not in ("journal","run","manifest")},
                    "source_commit":p["run"].get("commit"),"source_config":p["run"].get("config"),
                    "source_split":p["run"].get("data_split"),"source_duration_seconds":p["run"].get("duration_seconds"),
                    "source_errors":{k:p["run"].get(k) for k in ("error","error_type","traceback") if p["run"].get(k)}} for p in packages]}
                for p in packages:record["seeds"]+=p["run"].get("seeds",[])
                try:
                    if any(p.get("excluded") for p in packages):raise ValueError("Unsupported reconstruction split excluded")
                    result=analyze_reconstruction(packages,args.reconstruction_pause_receipt)
                    analyses[name]=result
                    record["families"][name]["pause_receipt"]=result["pause_receipt"]
                    for suffix,key in (("raw","raw"),("summary","summary"),("attempts","attempt_inventory")):
                        csv_table(output/(name+"-"+suffix+".csv"),result[key])
                except Exception as error:
                    analyses[name]={"raw":[],"summary":[],"incomplete":True,"error":str(error),"traceback":traceback.format_exc()}
                continue
            package=load_family(name,directory.resolve())
            record["families"][name]={k:v for k,v in package.items() if k not in ("journal","run","manifest")}
            record["families"][name]["source_commit"]=package["run"].get("commit")
            record["families"][name]["source_config"]=package["run"].get("config")
            record["families"][name]["source_split"]=package["run"].get("data_split")
            record["families"][name]["source_duration_seconds"]=package["run"].get("duration_seconds")
            record["families"][name]["source_errors"]={k:package["run"].get(k) for k in ("error","error_type","traceback") if package["run"].get(k)}
            record["seeds"]+=package["run"].get("seeds",[])
            if package.get("excluded"):
                analyses[name]={"raw":[],"summary":[],"incomplete":True,"caveat":"Unsupported split excluded"};continue
            try:
                result={"reconstruction":analyze_reconstruction,"gs":analyze_gs,"progressive":analyze_progressive}[name](package)
                result["incomplete"]=bool(package["errors"]) or package["source_outcome"]!="completed" or any(r["status"] not in ("observed",) for r in result["raw"])
                analyses[name]=result
                csv_table(output/(name+"-raw.csv"),result["raw"])
                csv_table(output/(name+"-summary.csv"),result["summary"])
                if "quality_summary" in result:csv_table(output/(name+"-quality-summary.csv"),result["quality_summary"])
                if "attempt_inventory" in result:csv_table(output/(name+"-attempts.csv"),result["attempt_inventory"])
            except Exception as error:
                analyses[name]={"raw":[],"summary":[],"incomplete":True,"error":str(error),"traceback":traceback.format_exc()}
        write(output/"analysis.json",analyses)
        record["outcome"]="incomplete" if any(v["incomplete"] for v in analyses.values()) else "completed_descriptive_analysis"
        record["interpretation"]="Analysis completion is not experiment acceptance; no human assessment or method verdict inferred."
    except Exception as error:
        record.update(outcome="failed",error=str(error),traceback=traceback.format_exc())
    finally:
        record["duration_seconds"]=time.monotonic()-started
        record["seeds"]=sorted(set(record["seeds"]))
        write(output/"run.json",record)
        write(output/"manifest.json",{k:record[k] for k in ("script_sha256","config","families","command","commit","data_split","seeds","duration_seconds","outcome")})
    return 1 if record["outcome"]=="failed" else 0


if __name__=="__main__":
    raise SystemExit(main())

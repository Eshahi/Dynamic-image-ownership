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
    if name=="phasemark" and run.get("manifest_path"):
        manifest_path=Path(run["manifest_path"])
        if not manifest_path.is_absolute():manifest_path=ROOT/manifest_path
    elif "--manifest" in command:
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
    if name=="dual" and package.get("manifest",{}).get("cohort_manifest"):
        cohort=(ROOT/package["manifest"]["cohort_manifest"]).resolve()
        if cohort!=(ROOT/"research/m1-reconstruction-dev.json").resolve():
            package["errors"].append({"error":"Unsupported reserved cohort metadata path"})
        else:
            raw_cohort=pin(cohort)
            try:
                metadata=json.loads(raw_cohort) if raw_cohort else {}
                if metadata.get("data_split")!="development":raise ValueError("Development cohort metadata required")
                package["reserved_cohort"]=metadata
            except Exception as error:package["errors"].append({"error":"reserved cohort metadata unavailable","detail":str(error)})
    if name=="gs_lightweight":
        if not {"run.json","artifacts.json","rows.jsonl","rows-receipt.json"}<=set(run.get("source_receipts",{})):
            package["errors"].append({"error":"incomplete native snapshot receipts"})
        if run.get("outcome")=="completed" and not {"conditions.json","rows.jsonl"}<=set(run.get("output_hashes",{})):
            package["errors"].append({"error":"incomplete completed assessor receipts"})
        raw_conditions=pin(directory/"conditions.json")
        try:package["conditions"]=json.loads(raw_conditions) if raw_conditions else []
        except Exception as error:package["errors"].append({"error":"invalid conditions.json","detail":str(error)})
        for filename,receipt in run.get("source_receipts",{}).items():
            if Path(filename).name!=filename:raise ValueError("Invalid source receipt filename")
            copied=directory/("source-"+filename)
            pinned=pin(copied)
            if pinned is not None and sha(copied)!=receipt.get("sha256"):
                package["errors"].append({"error":"source snapshot hash mismatch","path":str(copied)})
        for filename,digest in run.get("output_hashes",{}).items():
            if Path(filename).name!=filename:raise ValueError("Invalid output receipt filename")
            copied=directory/filename
            if not copied.is_file() or sha(copied)!=digest:
                package["errors"].append({"error":"assessor output hash mismatch","path":str(copied)})
    if name=="phase_residual":
        raw_input=pin(directory/"input-run.json")
        raw_conditions=pin(directory/"conditions.json")
        try:
            if raw_conditions is None or json.loads(raw_conditions)!=run.get("conditions",[]):
                package["errors"].append({"error":"residual conditions snapshot/run mismatch"})
        except Exception as error:package["errors"].append({"error":"invalid residual conditions snapshot","detail":str(error)})
        expected=run.get("config",{}).get("input_run_sha256")
        if raw_input is None or sha(directory/"input-run.json")!=expected:
            package["errors"].append({"error":"residual input-run snapshot hash mismatch/missing"})
        if run.get("input_receipts",{}).get("run_sha256")!=expected:
            package["errors"].append({"error":"residual input receipt/config mismatch"})
        for filename in ("manifest.json","conditions.json","rows.jsonl"):
            path=directory/filename;digest=run.get("output_hashes",{}).get(filename)
            if run.get("outcome")=="completed" and (not path.is_file() or sha(path)!=digest):
                package["errors"].append({"error":"residual metadata output receipt mismatch","path":str(path)})
    if name=="phase_residual_expansion":
        raw_conditions=pin(directory/"conditions.json")
        try:
            if raw_conditions is None or json.loads(raw_conditions)!=run.get("conditions",[]):
                package["errors"].append({"error":"expansion conditions snapshot/run mismatch"})
        except Exception as error:package["errors"].append({"error":"invalid expansion conditions snapshot","detail":str(error)})
        for filename in ("manifest.json","conditions.json","rows.jsonl"):
            path=directory/filename;digest=run.get("output_hashes",{}).get(filename)
            if run.get("outcome")=="completed" and (not path.is_file() or sha(path)!=digest):
                package["errors"].append({"error":"expansion metadata output receipt mismatch","path":str(path)})
    journal_name={"reconstruction":"images.jsonl","gs":"rows.jsonl","progressive":"journal.jsonl","dual":"journal.jsonl","phasemark":"rows.jsonl","gs_lightweight":"rows.jsonl","phase_residual":"rows.jsonl","phase_residual_expansion":"rows.jsonl"}[name]
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


def pilot_provenance(package):
    directory=Path(package["directory"]).resolve()
    return {"source_directory":str(directory),"source_run_sha256":next((x["sha256"] for x in package["input_files"] if Path(x["path"]).resolve()==directory/"run.json"),None),
            "source_outcome":package["source_outcome"],"source_error":package["run"].get("error")}


def nullable_quality(value):
    result=quality(value or {})
    if not result["quality_complete"]:result["quality_all_three"]=None
    return result


def dual_detector(result,prefix):
    output={}
    for key in ("watermark_found","present","outcome","proposal_state","qualified_state","extractor_domain","timing_ms"):
        output[prefix+"_"+key]=result.get(key)
    for channel in ("semantic","instance"):
        value=result.get(channel,{})
        for key in ("found","content_status","content_match","corrected_distance","score"):
            output[prefix+"_"+channel+"_"+key]=value.get(key)
        output[prefix+"_"+channel+"_raw"]=value
    return output


def analyze_dual(packages):
    if isinstance(packages,dict):packages=[packages]
    rows=[];seen=set();declared=set();reserved={};errors=[];source_rows=[]
    for package in packages:
        if package.get("excluded"):raise ValueError("Unsupported dual split excluded")
        run=package["run"];manifest=package.get("manifest",{});ids=manifest.get("case_ids",[])
        config=manifest.get("config",{})
        if not ids or not config.get("routes"):
            errors.append("Exact dual case/route declaration unavailable: "+package["directory"]);continue
        if len(set(ids))!=len(ids) or len(set(config["routes"]))!=len(config["routes"]):raise ValueError("Duplicate dual declared case/route")
        if config!=run.get("config"):raise ValueError("Dual run/manifest configuration mismatch")
        cohort=package.get("reserved_cohort",{}).get("cases",[])
        if not cohort:errors.append("Reserved dual coverage metadata unavailable: "+package["directory"])
        for spec in cohort:
            ident=spec["id"]
            if ident in reserved and reserved[ident]!=spec:raise ValueError("Conflicting reserved source metadata")
            reserved[ident]=spec
        if cohort and any(i not in reserved for i in ids):raise ValueError("Unreserved dual case declaration")
        actual=run.get("cases",[])
        if any(c.get("id") not in ids for c in actual):raise ValueError("Unplanned actual dual case")
        for ident in ids:
            declared.add(ident);matches=[c for c in actual if c.get("id")==ident]
            if len(matches)>1:raise ValueError("Duplicate actual dual source")
            case=matches[0] if matches else {}
            routes=case.get("routes",[])
            if len({r["route"] for r in routes})!=len(routes) or any(r["route"] not in config["routes"] for r in routes):raise ValueError("Duplicate/unplanned actual dual route")
            for route in config["routes"]:
                identity=(ident,route)
                if identity in seen:raise ValueError("Overlapping dual source/route requires explicit rejection; no automatic merge")
                seen.add(identity)
                entry=next((r for r in routes if r["route"]==route),{})
                source_rows.append({"case":ident,"route":route,"case_outcome":case.get("outcome","not_attempted"),"route_outcome":entry.get("outcome","not_attempted"),
                                    "source_sha256":reserved.get(ident,{}).get("sha256"),"raw_sha256":case.get("raw_sha256"),"initialization":case.get("initialization"),
                                    "enrollment":case.get("enrollment"),"optimization":entry.get("optimization"),**pilot_provenance(package)})
                for condition in ("C0_source","C0_matched","C1","C0_VAE_cycle","C1_VAE_cycle"):
                    value=case.get(condition,{}) if condition=="C0_source" else entry.get(condition,{})
                    parent=case if condition=="C0_source" else entry
                    status="observed" if value and parent.get("outcome")=="completed" else "observed_partial" if value else "missing_or_failed"
                    optimization=entry.get("optimization",{})
                    rows.append({"family":"dual","case":ident,"route":route,"condition":condition,"status":status,
                        "parent_outcome":parent.get("outcome","not_attempted"),"error":parent.get("error"),
                        "source_sha256":reserved.get(ident,{}).get("sha256"),"raw_sha256":case.get("raw_sha256"),"source_rgb8_sha256":case.get("source_rgb8_sha256"),
                        **pilot_provenance(package),**nullable_quality(value),"quality_reference":"saved resized source RGB8",
                        "paired_quality":value.get("quality_vs_paired_C0",entry.get("paired_C1_vs_C0_quality") if condition=="C1" else None),
                        "recorded_quality_admissible":value.get("quality_admissible"),
                        **dual_detector(value.get("correct_owner",{}),"correct"),**dual_detector(value.get("wrong_owner",{}),"wrong"),
                        "optimization_seconds":optimization.get("seconds"),"surrogate_semantic":optimization.get("surrogate_semantic"),
                        "surrogate_instance":optimization.get("surrogate_instance"),"surrogate_cycle_semantic":optimization.get("surrogate_cycle_semantic"),
                        "optimizer_events":[e for e in package["journal"] if e.get("id")==ident and e.get("route")==route and e.get("phase")=="optimizer_step"],
                        "image_receipt":{"path":value.get("png_path",case.get("source_png") if condition=="C0_source" else None),"sha256":value.get("png_sha256",case.get("source_png_sha256") if condition=="C0_source" else None)}})
        errors.extend(package["errors"])
    coverage=[{"case":i,"source_sha256":reserved[i].get("sha256"),"declared_in_supplied_pilots":i in declared,
               "completed_routes":sorted({r["route"] for r in source_rows if r["case"]==i and r["route_outcome"]=="completed"}),
               "status":"pilot_declared" if i in declared else "reserved_not_declared"} for i in sorted(reserved)]
    summaries=aggregate(rows,["route","condition"])
    for summary in summaries:
        cells=[r for r in rows if r["route"]==summary["route"] and r["condition"]==summary["condition"]]
        for owner in ("correct","wrong"):
            for suffix in ("watermark_found","present","semantic_found","semantic_content_match","instance_found","instance_content_match"):
                key=owner+"_"+suffix;measured=[r[key] for r in cells if type(r[key]) is bool]
                summary[key+"_n"]=len(measured);summary[key+"_positive"]=sum(measured)
            for suffix in ("proposal_state","qualified_state","semantic_content_status","instance_content_status"):
                key=owner+"_"+suffix;counts={}
                for r in cells:
                    if r[key] is not None:counts[r[key]]=counts.get(r[key],0)+1
                summary[key+"_counts"]=counts
            summary[owner+"_detector_total_ms"]=distribution([(r[owner+"_timing_ms"] or {}).get("total") for r in cells])
    return {"raw":rows,"summary":summaries,"source_route_inventory":source_rows,"coverage":coverage,
            "declared_pilot_source_n":len(declared),"reserved_source_n":len(reserved) if reserved else None,
            "declared_pilot_completed_source_n":sum(all(r["route_outcome"]=="completed" for r in source_rows if r["case"]==i) for i in declared),
            "reserved_not_declared_n":len(set(reserved)-declared) if reserved else None,"errors":errors,
            "incomplete":bool(errors) or not rows or any(p["source_outcome"]!="completed" for p in packages) or any(r["status"]!="observed" for r in rows),
            "caveat":"Declared pilot coverage and reserved cohort coverage are separate. Source quality never implies paired-counterfactual quality. States are recorded operational outputs, not causal/cryptographic ownership verdicts. Duplicate source/route attempts are rejected; no best-attempt selection."}


def analyze_phasemark(package):
    run=package["run"];manifest=package.get("manifest",{});config=manifest.get("config",{});cases=manifest.get("cases",[])
    if not cases or not config.get("arms") or not config.get("owners"):raise ValueError("Exact PhaseMark planned metadata unavailable")
    if config!=run.get("config"):raise ValueError("PhaseMark run/manifest configuration mismatch")
    ids=[c["id"] for c in cases];arms=config["arms"];owners=config["owners"]
    if len(set(ids))!=len(ids) or len(set(arms))!=len(arms) or len(set(owners))!=len(owners):raise ValueError("Duplicate PhaseMark declarations")
    planned=[(i,a,c,d,f"{i}-{a}-{c}-{d}") for i in ids for a in arms for c in ("C0","C1") for d in ("clean","vae_cycle")]
    actual=run.get("conditions",[]);identities=[r["id"] for r in actual]
    if len(set(identities))!=len(identities):raise ValueError("Duplicate PhaseMark condition; no attempt selection")
    if set(identities)-{p[4] for p in planned}:raise ValueError("Unplanned PhaseMark condition")
    rows=[];conditions=[];threshold=config.get("presence_matches")
    for ident,arm,control,dose,key in planned:
        value=next((r for r in actual if r["id"]==key),{})
        if value and any(value.get(k)!=v for k,v in (("source_id",ident),("arm",arm),("control",control),("dose",dose))):raise ValueError("PhaseMark condition identity mismatch")
        decisions=value.get("owner_decisions",{})
        if set(decisions)-set(owners):raise ValueError("Unplanned PhaseMark owner query")
        complete=value.get("outcome")=="completed" and all(finite(decisions.get(o,{}).get("matches")) and finite(decisions.get(o,{}).get("bit_accuracy")) for o in owners)
        status="observed" if complete else "observed_partial" if decisions else "missing_or_failed"
        shared={"family":"phasemark","case":ident,"id":key,"arm":arm,"control":control,"dose":dose,"status":status,
                "parent_outcome":value.get("outcome","not_attempted"),"error":value.get("error"),**pilot_provenance(package),
                "source_sha256":next(c.get("sha256") for c in cases if c["id"]==ident),"image_receipt":value.get("image"),"source_receipt":value.get("source"),
                **nullable_quality(value.get("quality_vs_source")),"quality_reference":"saved resized source RGB8",
                "same_arm_quality":value.get("quality_vs_same_arm_clean"),"paired_quality":value.get("paired_C1_vs_C0_quality"),
                "extract_seconds":value.get("extract_seconds"),"extracted_scores":value.get("extracted",{}).get("scores"),
                "zero_magnitude_coefficients_per_block":value.get("extracted",{}).get("zero_magnitude_coefficients_per_block"),
                "embedding":value.get("embedding"),"human_visual_verdict":None}
        conditions.append(shared)
        for owner in owners:
            decision=decisions.get(owner,{})
            observed=finite(decision.get("matches")) and finite(decision.get("bit_accuracy"))
            rows.append({**shared,"status":"observed" if complete else "observed_partial" if observed else "missing_or_failed",
                         "owner_query":owner,"correct_owner_query":owner==owners[0],"matches":decision.get("matches"),"bit_accuracy":decision.get("bit_accuracy"),
                         "detected":decision["matches"]>=threshold if finite(decision.get("matches")) and finite(threshold) else None,
                         "pilot_state":decision.get("pilot_state"),"descriptive_threshold_decisions":decision.get("descriptive_threshold_decisions"),
                         "query_observed":observed})
    screens=[]
    for arm in arms:
        cells=[c for c in conditions if c["arm"]==arm];queries=[r for r in rows if r["arm"]==arm]
        complete=all(c["status"]=="observed" and c["quality_complete"] for c in cells)
        carrier=all(r["detected"] is (r["control"]=="C1" and r["correct_owner_query"]) for r in queries) if complete and finite(threshold) else None
        clean=[c for c in cells if c["control"]=="C1" and c["dose"]=="clean"]
        qgate=all(c["quality_all_three"] for c in clean) if complete and all(c["quality_complete"] for c in clean) else None
        screens.append({"arm":arm,"planned_sources":len(ids),"planned_conditions":len(cells),"planned_queries":len(queries),"observed_conditions":sum(c["status"]=="observed" for c in cells),
                        "observed_queries":sum(r["query_observed"] for r in queries),"complete":complete,"carrier_gate":carrier,"source_quality_gate":qgate,
                        "recorded_arm_screen":run.get("arm_screen",{}).get(arm),"human_visual_verdict":None})
    summaries=aggregate(rows,["arm","control","dose","owner_query"])
    for summary in summaries:
        cells=[r for r in rows if all(r[k]==summary[k] for k in ("arm","control","dose","owner_query"))]
        summary["matches"]=distribution([r["matches"] for r in cells]);summary["extract_seconds"]=distribution([r["extract_seconds"] for r in cells])
    return {"raw":rows,"condition_inventory":conditions,"summary":summaries,"arm_screen":screens,
            "planned_source_n":len(ids),"planned_conditions":len(planned),"planned_queries":len(rows),"errors":package["errors"],
            "incomplete":bool(package["errors"]) or package["source_outcome"]!="completed" or not all(c["status"]=="observed" and c["quality_complete"] for c in conditions),
            "caveat":"Public phase carrier pilot with owner-hypothesis queries. No three-state/content/cryptographic ownership claim. Four queries and repeated arms/cycles do not multiply source N; quality/latency inventory is unique per condition."}


def analyze_phase_residual(package):
    """Fixed residual diagnostic: two source clusters, not 128 independent trials."""
    run=package["run"];config=package.get("manifest",{})
    schema=config.get("schema");expansion=schema=="m1-phasemark-residual-expansion-v1"
    if schema not in ("m1-phasemark-residual-v1","m1-phasemark-residual-expansion-v1") or run.get("schema")!=schema or config!=run.get("config"):
        raise ValueError("Exact residual schema/configuration required")
    ids=config.get("ids",[]);arms=config.get("arms",[]);profiles=config.get("profiles",[]);owners=config.get("owners",[])
    source_n=10 if expansion else 2
    if len(ids)!=source_n or len(set(ids))!=source_n or arms!=(["IPS"] if expansion else ["APM","IPS"]) or profiles!=(["quality-cap"] if expansion else ["full","quality-cap"]) or len(owners)!=4 or len(set(owners))!=4 or config.get("threshold")!=82:
        raise ValueError("Fixed residual/expansion source-arm-profile-owner design required")
    cases=config.get("cases",[])
    if expansion and [c.get("id") for c in cases]!=ids:raise ValueError("Expansion source manifest identities unavailable")
    planned=[(i,a,p,c,d,f"{i}-{a}-{p}-{c}-{d}") for i in ids for a in arms for p in profiles for c in ("C0","C1") for d in ("clean","vae_cycle")]
    actual=run.get("conditions",[]);lookup={r["id"]:r for r in actual}
    if len(lookup)!=len(actual):raise ValueError("Duplicate residual condition; no attempt selection")
    if set(lookup)-{p[-1] for p in planned}:raise ValueError("Unplanned residual condition")
    rows=[];conditions=[];screens=[]
    for ident,arm,profile,control,dose,key in planned:
        value=lookup.get(key,{})
        if value and any(value.get(k)!=v for k,v in (("source_id",ident),("arm",arm),("profile",profile),("control",control),("dose",dose))):raise ValueError("Residual identity mismatch")
        if expansion and value.get("outcome")=="completed":
            declared=next(c for c in cases if c["id"]==ident)
            if value.get("source",{}).get("raw_sha256")!=declared.get("sha256"):raise ValueError("Expansion raw source receipt mismatch")
        decisions=value.get("owner_decisions",{})
        if set(decisions)-set(owners):raise ValueError("Unplanned residual owner")
        for decision in decisions.values():
            matches=decision.get("matches")
            if type(matches) is not int or not 0<=matches<=128 or decision.get("bit_accuracy")!=matches/128 or decision.get("present") is not (matches>=82):
                raise ValueError("Residual owner decision inconsistent with frozen threshold")
        complete=value.get("outcome")=="completed" and set(decisions)==set(owners)
        status="observed" if complete else "observed_partial" if decisions else "missing_or_failed"
        composition=value.get("composition") or {}
        weight=composition.get("weight")
        if weight is not None and (not finite(weight) or not 0<=weight<=1):raise ValueError("Residual lambda outside interval")
        shared={"family":"phase_residual_expansion" if expansion else "phase_residual","case":ident,"id":key,"arm":arm,"profile":profile,"control":control,"dose":dose,
                "status":status,"parent_outcome":value.get("outcome","not_attempted"),"error":value.get("error"),"traceback":value.get("traceback"),
                **pilot_provenance(package),**nullable_quality(value.get("quality_vs_source",{})),"quality_reference":"saved resized source RGB8",
                "same_arm_quality":value.get("quality_vs_same_arm_clean"),"image_receipt":value.get("image"),"source_receipt":value.get("source"),
                "composition":value.get("composition"),"latent_receipts":value.get("latent_receipts"),"embedding":value.get("embedding"),"lambda":weight,"pixel_cap_db":config.get("psnr_cap_db"),
                "pixel_cap_mse_rgb8":composition.get("budget_mse_rgb8"),"composition_mse_rgb8":composition.get("mse_rgb8"),
                "composition_sse_rgb8":composition.get("sse_rgb8"),"extract_seconds":value.get("extract_seconds"),
                "extracted_scores":value.get("extracted",{}).get("scores"),"zero_magnitude_coefficients_per_block":value.get("extracted",{}).get("zero_magnitude_coefficients_per_block"),
                "human_visual_verdict":None}
        conditions.append(shared)
        for owner in owners:
            decision=decisions.get(owner,{})
            rows.append({**shared,"status":status if decision else "missing_or_failed","owner_query":owner,"correct_owner_query":owner==owners[0],
                         "query_observed":bool(decision),"matches":decision.get("matches"),"bit_accuracy":decision.get("bit_accuracy"),"detected":decision.get("present")})
    trustworthy=not package["errors"] and package["source_outcome"]=="completed"
    for arm in arms:
        for profile in profiles:
            cells=[c for c in conditions if c["arm"]==arm and c["profile"]==profile]
            queries=[r for r in rows if r["arm"]==arm and r["profile"]==profile]
            clean=[c for c in cells if c["control"]=="C1" and c["dose"]=="clean"]
            screen={"arm":arm,"profile":profile,"planned_sources":source_n,"planned_conditions":len(cells),"planned_queries":len(queries),
                    "observed_conditions":sum(c["status"]=="observed" for c in cells),"observed_queries":sum(r["query_observed"] for r in queries),
                    "source_quality_gate":all(c["quality_all_three"] for c in clean) if trustworthy and all(c["status"]=="observed" and c["quality_complete"] for c in clean) else None,
                    "clean_quality_pass_n":sum(c["status"]=="observed" and c["quality_all_three"] is True for c in clean),"human_visual_verdict":None}
            for dose in ("clean","vae_cycle"):
                group=[r for r in queries if r["dose"]==dose]
                screen[dose+"_carrier_gate"]=all(r["detected"] is (r["control"]=="C1" and r["correct_owner_query"]) for r in group) if trustworthy and all(r["status"]=="observed" for r in group) else None
                screen[dose+"_C1_correct_present_n"]=sum(r["detected"] is True for r in group if r["control"]=="C1" and r["correct_owner_query"])
                screen[dose+"_C1_wrong_positive_queries"]=sum(r["detected"] is True for r in group if r["control"]=="C1" and not r["correct_owner_query"])
                screen[dose+"_C0_positive_queries"]=sum(r["detected"] is True for r in group if r["control"]=="C0")
            screens.append(screen)
    summaries=aggregate(rows,["arm","profile","control","dose","owner_query"])
    for summary in summaries:
        group=[r for r in rows if all(r[k]==summary[k] for k in ("arm","profile","control","dose","owner_query"))]
        for metric in ("matches","extract_seconds","lambda"):summary[metric]=distribution([r[metric] for r in group])
    return {"raw":rows,"condition_inventory":conditions,"summary":summaries,"arm_screen":screens,"planned_source_n":source_n,"planned_conditions":len(planned),"planned_queries":len(rows),
            "model_identity":{"vae_scaling_factor":run.get("vae_scaling_factor"),"phase_code_sha256":run.get("committed_files",{}).get("scripts/m1_phasemark.py",{}).get("working_sha256"),
                              "asset_inventory_sha256":run.get("committed_files",{}).get("research/a6-candidate-model-assets.json",{}).get("working_sha256")},
            "input_receipts":run.get("input_receipts"),"output_hashes":run.get("output_hashes"),"errors":package["errors"],
            "incomplete":not trustworthy or any(c["status"]!="observed" or not c["quality_complete"] for c in conditions),
            "caveat":"Declared source clusters with shared C0 across arms/profiles and four correlated owner queries. Source-bypass phase residual, not pure latent or three-state/content binding; no population FPR or human verdict."}


def combine_phase_residual(pilot,expansion,pilot_config,expansion_config):
    """Combine only fixed IPS/quality-cap, retaining source/condition provenance."""
    for key in ("owners","threshold","psnr_cap_db","bisection_steps"):
        if pilot_config.get(key)!=expansion_config.get(key):raise ValueError("Incompatible residual operating profile: "+key)
    if pilot_config.get("schema")!="m1-phasemark-residual-v1" or expansion_config.get("schema")!="m1-phasemark-residual-expansion-v1":
        raise ValueError("Exact pilot then expansion schemas required")
    identity=pilot.get("model_identity",{})
    if identity.get("vae_scaling_factor")!=.18215 or not identity.get("phase_code_sha256") or not identity.get("asset_inventory_sha256") or identity!=expansion.get("model_identity"):
        raise ValueError("Combined pinned VAE scale/phase-code identity unavailable or changed")
    ids=pilot_config.get("ids",[])+expansion_config.get("ids",[])
    if len(ids)!=12 or len(set(ids))!=12:raise ValueError("Combined sources overlap or fixed twelve unavailable")
    for result in (pilot,expansion):
        if "raw" not in result or "condition_inventory" not in result:raise ValueError("Missing residual adapter inventory")
    choose=lambda rows:[r for r in rows if r["arm"]=="IPS" and r["profile"]=="quality-cap"]
    rows=choose(pilot["raw"])+choose(expansion["raw"])
    conditions=choose(pilot["condition_inventory"])+choose(expansion["condition_inventory"])
    if len(rows)!=192 or len(conditions)!=48 or len({r["id"] for r in conditions})!=48:
        raise ValueError("Combined fixed48 conditions/192queries required")
    coverage=[{"case":i,"planned_conditions":4,"observed_conditions":sum(c["status"]=="observed" for c in conditions if c["case"]==i),
               "run_directory":next(c.get("run_directory",c.get("source_directory")) for c in conditions if c["case"]==i)} for i in ids]
    trustworthy=not pilot.get("errors") and not expansion.get("errors") and not pilot["incomplete"] and not expansion["incomplete"]
    clean=[c for c in conditions if c["control"]=="C1" and c["dose"]=="clean"]
    gates=[{"kind":"clean_source_quality","planned_sources":12,"pass_n":sum(c["quality_all_three"] is True and c["status"]=="observed" for c in clean),
            "gate":all(c["quality_all_three"] for c in clean) if trustworthy and all(c["quality_complete"] for c in clean) else None,"human_visual_verdict":None}]
    for dose in ("clean","vae_cycle"):
        group=[r for r in rows if r["dose"]==dose]
        gates.append({"kind":dose+"_carrier","planned_sources":12,"correct_C1_present_n":sum(r["detected"] is True for r in group if r["control"]=="C1" and r["correct_owner_query"]),
            "C1_wrong_positive_queries":sum(r["detected"] is True for r in group if r["control"]=="C1" and not r["correct_owner_query"]),
            "C0_positive_queries":sum(r["detected"] is True for r in group if r["control"]=="C0"),
            "gate":all(r["detected"] is (r["control"]=="C1" and r["correct_owner_query"]) for r in group) if trustworthy and all(r["status"]=="observed" for r in group) else None})
    return {"raw":rows,"condition_inventory":conditions,"summary":aggregate(rows,["control","dose","owner_query"]),"coverage":coverage,"gates":gates,
            "planned_source_n":12,"planned_conditions":48,"planned_queries":192,"incomplete":not trustworthy,
            "caveat":"Prespecified IPS quality-cap only. Two pilot sources plus ten disjoint expansion sources; no best-arm/attempt selection. Correlated owner queries do not increase source N; no population FPR or three-state method claim."}


def analyze_gs_lightweight(package):
    """Describe fixed B-LW1 pairs without opening or hashing any image."""
    run=package["run"];config=run.get("config",{})
    if run.get("schema_version")!="m1-gs-terminal-sign-v1" or config.get("presence_matches")!=180:
        raise ValueError("Frozen B-LW1 version and 180/256 threshold required")
    if run.get("data_split")!="synthetic":raise ValueError("B-LW1 synthetic split required")
    channels=[("clean",None,None),("vae",None,None)]+[(f"regen-{s}-seed{seed}",s,seed) for s in (.05,.1,.2,.4) for seed in (0,1,2)]
    planned=[(f"prompt-{i}",1000+i,arm,channel,strength,seed) for i in range(4) for arm in ("C0","C1") for channel,strength,seed in channels]
    actual=package.get("conditions",[])
    index={r["id"]:r for r in actual}
    if len(index)!=len(actual):raise ValueError("Duplicate B-LW1 condition")
    ids={f"{case}-{arm}-{channel}" for case,_,arm,channel,_,_ in planned}
    if set(index)-ids:raise ValueError("Unplanned B-LW1 condition")
    if run.get("expected_conditions")!=112:raise ValueError("B-LW1 denominator differs")
    raw=[];paired=[]
    for case,seed,arm,channel,strength,attack_seed in planned:
        ident=f"{case}-{arm}-{channel}";value=index.get(ident,{})
        if value and any(value.get(k)!=v for k,v in (("case",case),("generation_seed",seed),("arm",arm),("channel",channel),("strength",strength),("attack_seed",attack_seed))):
            raise ValueError("B-LW1 condition identity mismatch")
        native=value.get("native",{})
        if native:
            digest=hashlib.sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            if digest!=value.get("source_row_sha256") or value.get("image_sha256")!=native.get("image_sha256"):
                raise ValueError("B-LW1 native/LW row or image hash join mismatch")
            if any(native.get(k)!=v for k,v in (("case",case),("arm",arm),("channel",channel))):raise ValueError("Native pair identity mismatch")
        shared={"family":"gs_lightweight","id":ident,"case":case,"generation_seed":seed,"arm":arm,"channel":channel,"strength":strength,"attack_seed":attack_seed,
            "parent_outcome":value.get("outcome","missing_condition"),"error":value.get("error"),"image_sha256":value.get("image_sha256"),"source_row_sha256":value.get("source_row_sha256"),
            "reference_payload_sha256":value.get("reference_payload_sha256"),"key_identifiers":value.get("key_identifiers"),"nonce":value.get("nonce"),
            "preprocessing":value.get("preprocessing"),"vae_asset_receipt_id":value.get("vae_asset_receipt_id"),"diagnostics":value.get("diagnostics"),
            "first_call":value.get("first_call"),"peak_allocated_bytes":value.get("peak_allocated_bytes"),"human_visual_verdict":None}
        scores={}
        for decoder in ("native","lightweight"):
            row=dict(shared,decoder=decoder)
            for query in ("correct","wrong"):
                if decoder=="lightweight":
                    score=value.get(query+"_key",{}) if value.get("outcome")=="completed" else {}
                    matches=score.get("matches");accuracy=score.get("bit_accuracy");present=score.get("present");exact=score.get("exact_message")
                    if score and (type(matches) is not int or not 0<=matches<=256 or accuracy!=matches/256 or present!=(matches>=180) or exact!=(matches==256)):
                        raise ValueError("Inconsistent B-LW1 lightweight decision")
                    row[query+"_tie_count"]=score.get("tie_count")
                else:
                    accuracy=native.get("bit_accuracy" if query=="correct" else "wrong_key_bit_accuracy")
                    matches=round(accuracy*256) if finite(accuracy) and 0<=accuracy<=1 else None
                    present=native.get("detected" if query=="correct" else "wrong_key_detected")
                    exact=native.get("exact_payload") if query=="correct" else matches==256 if matches is not None else None
                    if matches is not None and (accuracy!=matches/256 or type(present) is not bool or present!=(matches>=180) or type(exact) is not bool or exact!=(matches==256)):
                        raise ValueError("Inconsistent B-LW1 native decision")
                observed=type(matches) is int and type(present) is bool and type(exact) is bool
                row.update({query+"_matches":matches,query+"_bit_accuracy":accuracy,query+"_present":present if observed else None,query+"_exact":exact if observed else None,query+"_observed":observed})
            row["status"]="observed" if row["correct_observed"] and row["wrong_observed"] else "missing_or_failed"
            row["detector_seconds"]=native.get("detector_seconds") if decoder=="native" else value.get("diagnostics",{}).get("total_seconds")
            row["unet_evaluations"]=native.get("detector_unet_evaluations") if decoder=="native" else value.get("diagnostics",{}).get("unet_evaluations")
            raw.append(row);scores[decoder]=row
        n=scores["native"];l=scores["lightweight"];complete=n["status"]==l["status"]=="observed"
        paired.append({**shared,"status":"observed" if complete else "missing_or_failed","native_matches_minus_lightweight":n["correct_matches"]-l["correct_matches"] if complete else None,
            "presence_cell":("both" if n["correct_present"] and l["correct_present"] else "native-only" if n["correct_present"] else "lightweight-only" if l["correct_present"] else "neither") if complete else None})
    summary=[]
    for channel,_,_ in channels:
        for decoder in ("native","lightweight"):
            group=[r for r in raw if r["channel"]==channel and r["decoder"]==decoder]
            c1=[r for r in group if r["arm"]=="C1" and r["status"]=="observed"];c0=[r for r in group if r["arm"]=="C0" and r["status"]=="observed"]
            pair=[r for r in paired if r["channel"]==channel and r["arm"]=="C1"]
            summary.append({"channel":channel,"decoder":decoder,"prompt_clusters":4,"planned_per_arm":4,"observed_C1":len(c1),"observed_C0":len(c0),"missing_C1":4-len(c1),"missing_C0":4-len(c0),
                "C1_present":sum(r["correct_present"] for r in c1),"C1_exact":sum(r["correct_exact"] for r in c1),"C0_positive":sum(r["correct_present"] for r in c0),"C1_wrong_positive":sum(r["wrong_present"] for r in c1),
                "C0_wrong_positive":sum(r["wrong_present"] for r in c0),"C1_accuracies":[{"case":r["case"],"accuracy":r["correct_bit_accuracy"]} for r in c1],"C1_bit_accuracy":distribution([r["correct_bit_accuracy"] for r in c1]),
                "paired_C1_missing":sum(r["status"]!="observed" for r in pair),"paired_C1_presence_cells":{cell:sum(r["presence_cell"]==cell for r in pair) for cell in ("both","native-only","lightweight-only","neither")}})
    gates=[{"channel":r["channel"],"decoder":r["decoder"],"carrier_gate":None if r["missing_C1"] or r["missing_C0"] or package["errors"] or package["source_outcome"]!="completed" else r["C1_present"]==4 and r["C0_positive"]==0 and r["C1_wrong_positive"]==0} for r in summary if r["channel"] in ("clean","vae")]
    return {"raw":raw,"summary":summary,"paired":paired,"gates":gates,"planned_conditions":112,"prompt_clusters":4,
        "source_receipts":run.get("source_receipts"),"output_hashes":run.get("output_hashes"),"errors":package["errors"],
        "incomplete":bool(package["errors"]) or package["source_outcome"]!="completed" or any(r["status"]!="observed" for r in raw),
        "caveat":"Four synthetic prompt clusters; repeated channels are not independent sources. Paired native/LW matches compare identical saved images. No population FPR, content binding, three-state decision or human verdict."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruction-dir",type=Path,action="append")
    parser.add_argument("--reconstruction-pause-receipt",type=Path)
    parser.add_argument("--dual-dir",type=Path,action="append")
    for name in ("gs","progressive","phasemark","gs_lightweight","phase_residual","phase_residual_expansion"):parser.add_argument("--"+name.replace("_","-")+"-dir",type=Path)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args();started=time.monotonic()
    sources={name:getattr(args,name+"_dir") for name in ("reconstruction","gs","progressive","dual","phasemark","gs_lightweight","phase_residual","phase_residual_expansion") if getattr(args,name+"_dir") is not None}
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
            if name=="dual":
                packages=[load_family(name,p.resolve()) for p in directory]
                record["families"][name]={"attempts":[{**{k:v for k,v in p.items() if k not in ("journal","run","manifest","reserved_cohort")},
                    "source_commit":p["run"].get("commit"),"source_config":p["run"].get("config"),"source_errors":{k:p["run"].get(k) for k in ("error","error_type","traceback") if p["run"].get(k)}} for p in packages]}
                for p in packages:record["seeds"]+=p["run"].get("seeds",[])
                try:
                    result=analyze_dual(packages);analyses[name]=result
                    for suffix,key in (("raw","raw"),("summary","summary"),("coverage","coverage"),("source-routes","source_route_inventory")):
                        csv_table(output/(name+"-"+suffix+".csv"),result[key])
                except Exception as error:
                    analyses[name]={"raw":[],"summary":[],"incomplete":True,"error":str(error),"traceback":traceback.format_exc()}
                continue
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
                result={"reconstruction":analyze_reconstruction,"gs":analyze_gs,"progressive":analyze_progressive,"phasemark":analyze_phasemark,"gs_lightweight":analyze_gs_lightweight,"phase_residual":analyze_phase_residual,"phase_residual_expansion":analyze_phase_residual}[name](package)
                result["incomplete"]=result.get("incomplete",False) or bool(package["errors"]) or package["source_outcome"]!="completed" or any(r["status"] not in ("observed",) for r in result["raw"])
                analyses[name]=result
                csv_table(output/(name+"-raw.csv"),result["raw"])
                csv_table(output/(name+"-summary.csv"),result["summary"])
                if "quality_summary" in result:csv_table(output/(name+"-quality-summary.csv"),result["quality_summary"])
                if "attempt_inventory" in result:csv_table(output/(name+"-attempts.csv"),result["attempt_inventory"])
                if "condition_inventory" in result:csv_table(output/(name+"-conditions.csv"),result["condition_inventory"])
                if "arm_screen" in result:csv_table(output/(name+"-arm-screen.csv"),result["arm_screen"])
                for key in ("paired","gates"):
                    if key in result:csv_table(output/(name+"-"+key+".csv"),result[key])
            except Exception as error:
                analyses[name]={"raw":[],"summary":[],"incomplete":True,"error":str(error),"traceback":traceback.format_exc()}
        if "phase_residual" in analyses and "phase_residual_expansion" in analyses:
            try:
                result=combine_phase_residual(analyses["phase_residual"],analyses["phase_residual_expansion"],
                    record["families"]["phase_residual"].get("source_config",{}),record["families"]["phase_residual_expansion"].get("source_config",{}))
                analyses["phase_residual_combined"]=result
                for suffix,key in (("raw","raw"),("conditions","condition_inventory"),("summary","summary"),("coverage","coverage"),("gates","gates")):
                    csv_table(output/("phase_residual_combined-"+suffix+".csv"),result[key])
            except Exception as error:
                analyses["phase_residual_combined"]={"incomplete":True,"error":str(error),"traceback":traceback.format_exc()}
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

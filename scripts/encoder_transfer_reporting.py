"""Prespecified descriptive summaries; no imports of scientific model code."""
import math
from statistics import median
from encoder_transfer_test import ALPHA,BETA,RULES,unit_id,call_value,plan,channel_arms,binomial_threshold

INTERNAL=("f5-r2","v5-r3")

METRICS=("psnr_db","ssim_rgb","lpips")
BINS=(0,.05,.10,.20,.30,.50,math.inf)
CARRIER_STATES=("missing_call","raw_unavailable","not_found","found_not_read",
                "read_content_mismatch","C_success")


def carrier_state(row,method):
    """Describe a persisted semantic read without changing historical endpoints."""
    if not row or row.get("status") not in ("generated","ok"):
        return "missing_call",False
    call=row.get("detections",{}).get(method,{}).get(ALPHA,{})
    if call.get("status")!="ok":
        return "missing_call",False
    raw=call.get("raw")
    semantic=raw.get("semantic") if isinstance(raw,dict) else None
    if not isinstance(semantic,dict) or any(type(semantic.get(k)) is not bool
                                          for k in ("found","read","content_match")):
        return "raw_unavailable",False
    # C literally depends on read/content_match, not found. Preserve that order.
    if semantic["read"]:
        return ("C_success" if semantic["content_match"] else "read_content_mismatch",
                not semantic["found"])
    return ("found_not_read" if semantic["found"] else "not_found"),False


def carrier_summary(ids,seeds,rows,method,cid,strength):
    """Retain source clustering; these are descriptive call states, not trials."""
    totals=dict.fromkeys(CARRIER_STATES,0)
    grouped=[]
    for sid in ids:
        counts=dict.fromkeys(CARRIER_STATES,0)
        read_without_found=0
        q_values=[]
        for seed in seeds:
            row=rows.get(unit_id(sid,cid,strength,seed,method))
            state,anomaly=carrier_state(row,method)
            counts[state]+=1
            read_without_found+=anomaly
            q_values.append(call_value(row,method,ALPHA,"Q"))
        for state in CARRIER_STATES:
            totals[state]+=counts[state]
        grouped.append(dict(source_id=sid,counts=counts,read_without_found=read_without_found,
                            Q_true=sum(v is True for v in q_values),
                            Q_observed=sum(v is not None for v in q_values)))
    return dict(planned_sources=len(ids),planned_calls=len(ids)*len(seeds),counts=totals,
                read_without_found=sum(g["read_without_found"] for g in grouped),
                Q_true=sum(g["Q_true"] for g in grouped),
                Q_observed=sum(g["Q_observed"] for g in grouped),by_source=grouped)


def quantiles(values):
    x=sorted(v for v in values if v is not None and math.isfinite(v))
    def q(p):
        index=(len(x)-1)*p
        low=int(index)
        return x[low]+(x[min(low+1,len(x)-1)]-x[low])*(index-low)
    return dict(observed=len(x),minimum=x[0],q1=q(.25),median=q(.5),q3=q(.75),maximum=x[-1]) if x else dict(observed=0)


def metric_vector(rows,sid,arm,cid,strength,seeds,field="distortion"):
    values=[rows.get(unit_id(sid,cid,strength,seed,arm),{}).get(field,{}) for seed in seeds]
    if any(v.get("status")!="ok" or any(not isinstance(v.get(k),(int,float)) or not math.isfinite(v[k]) for k in METRICS) for v in values):
        return None
    return {k:median([v[k] for v in values]) for k in METRICS}


def score(row,method,kind):
    if not row or row.get("status") not in ("generated","ok"):
        return None
    call=row.get("detections",{}).get(method,{}).get(ALPHA,{})
    if call.get("status")!="ok":
        return None
    if kind=="mask":
        return call["raw"]["native_mask_fraction"]
    # An empty mask is a defined abstention, distinct from a missing call.
    value=call.get("presence",{}).get("accuracy")
    return -math.inf if value is None else value


def empirical_roc(positive,negative):
    if any(v is None for v in negative) or not negative:
        return dict(status="not_estimable_unresolved_negatives",unresolved=sum(v is None for v in negative))
    thresholds=sorted({v for v in positive+negative if v is not None and math.isfinite(v)},reverse=True)
    points=[dict(threshold=None,reject_all=True,tp=0,fp=0,tpr=0.,fpr=0.)]
    for cut in thresholds:
        tp=sum(v is not None and v>=cut for v in positive)
        fp=sum(v>=cut for v in negative)
        points.append(dict(threshold=cut,tp=tp,fp=fp,tpr=tp/len(positive),fpr=fp/len(negative)))
    selected={}
    for target in (.001,.01):
        feasible=[p for p in points if p["fpr"]<target]
        # Highest TPR; fewer FP and then higher threshold on exact ties.
        selected[str(target)]=max(feasible,key=lambda p:(p["tpr"],-p["fp"],p["threshold"] if p["threshold"] is not None else math.inf))
    return dict(status="descriptive_only",positive_planned=len(positive),negative_planned=len(negative),
                missing_positives=sum(v is None for v in positive),points=points,strict_fpr_targets=selected)


def matched_grid(config,sources,rows,vectors):
    active={c["id"]:c for c in config["channels"] if c.get("enabled",True)}
    comparisons=[]
    for cid in ("R0","R1"):
        if cid in active:
            comparisons.extend([(("f5-r2",cid),(arm,cid)) for arm in channel_arms(config,active[cid]) if arm!="f5-r2"])
    if "R0" in active and "R1" in active:
        both=set(channel_arms(config,active["R0"]))&set(channel_arms(config,active["R1"]))
        comparisons.extend([((arm,"R0"),(arm,"R1")) for arm in config["arms"] if arm in both])
    result={}
    ids=[s["source_id"] for s in sources["sources"]]
    for (left,lc),(right,rc) in comparisons:
        bins=[]
        for low,high in zip(BINS,BINS[1:]):
            selected=[]
            for index,sid in enumerate(ids):
                candidates=[]
                for ls in active[lc]["strengths"]:
                    a=metric_vector(rows,sid,left,lc,ls,active[lc]["seeds"])
                    if not a or not low<=a["lpips"]<high:
                        continue
                    for rs in active[rc]["strengths"]:
                        b=metric_vector(rows,sid,right,rc,rs,active[rc]["seeds"])
                        if not b or not low<=b["lpips"]<high:
                            continue
                        delta={k:abs(a[k]-b[k]) for k in METRICS}
                        if delta["psnr_db"]<=1 and delta["ssim_rgb"]<=.02 and delta["lpips"]<=.02:
                            distance=delta["psnr_db"]**2+(delta["ssim_rgb"]/.02)**2+(delta["lpips"]/.02)**2
                            candidates.append((distance,ls,rs,delta))
                if not candidates:
                    continue
                _,ls,rs,delta=min(candidates,key=lambda v:v[:3])
                # Read detector outcomes only AFTER the quality-only match.
                endpoint=lambda arm:"C" if arm in ("f5-r2","v5-r3") else "presence"
                a=vectors[f"{left}/{lc}/{ls}/{endpoint(left)}"][index]
                b=vectors[f"{right}/{rc}/{rs}/{endpoint(right)}"][index]
                ca=metric_vector(rows,sid,left,"clean",None,[None])
                cb=metric_vector(rows,sid,right,"clean",None,[None])
                clean_match=left==right or bool(ca and cb and abs(ca["psnr_db"]-cb["psnr_db"])<=1 and abs(ca["ssim_rgb"]-cb["ssim_rgb"])<=.01 and abs(ca["lpips"]-cb["lpips"])<=.01)
                selected.append(dict(source_id=sid,left_strength=ls,right_strength=rs,left=a,right=b,delta=delta,embedding_also_matched=clean_match))
            def summary(items):
                n=len(items)
                return dict(n=n,left=sum(x["left"] for x in items),right=sum(x["right"] for x in items),
                            paired_difference=sum(int(x["left"])-int(x["right"]) for x in items)/n if n else None,
                            wins=sum(x["left"] and not x["right"] for x in items),losses=sum(x["right"] and not x["left"] for x in items),
                            status="no_matched_overlap" if not n else "sparse_descriptive_subset" if n<20 else "descriptive_subset")
            bins.append(dict(lpips_bin=[low,None if math.isinf(high) else high],attack_match=summary(selected),
                             embedding_and_attack_match=summary([s for s in selected if s["embedding_also_matched"]]),selected_pairs=selected))
        result[f"{left}/{lc} vs {right}/{rc}"]=bins
    return result


def reporting(config,sources,rows,vectors):
    ids=[s["source_id"] for s in sources["sources"]]
    negatives,quality,external,roc,carrier={}, {}, {}, {}, {}
    active=[dict(id="clean"),*[c for c in config["channels"] if c.get("enabled",True)]]
    for spec in active:
        cid=spec["id"]
        for strength in spec.get("strengths",[None]):
            seeds=spec.get("seeds",[None])
            scoped=channel_arms(config,spec)
            for arm in ["unmarked",*scoped]:
                units=[rows.get(unit_id(sid,cid,strength,seed,arm),{}) for sid in ids for seed in seeds]
                prefix=f"{arm}/{cid}/{strength}"
                quality[prefix]={}
                for field in ("distortion","total_distortion",*(["incremental_distortion"] if cid=="R1-rinse" else [])):
                    quality[prefix][field]={}
                    for metric in METRICS:
                        data=[r.get(field,{}).get(metric) for r in units if r.get(field,{}).get("status")=="ok"]
                        source_medians=[]
                        for sid in ids:
                            values=[rows.get(unit_id(sid,cid,strength,seed,arm),{}).get(field,{}) for seed in seeds]
                            scalars=[v.get(metric) for v in values]
                            if all(v.get("status")=="ok" and isinstance(x,(int,float)) and math.isfinite(x) for v,x in zip(values,scalars)):
                                source_medians.append(median(scalars))
                        quality[prefix][field][metric]=dict(available_output=quantiles(data),complete_source_medians=quantiles(source_medians),planned_sources=len(ids),planned_outputs=len(units),
                                                            infinite_outputs=sum(r.get(field,{}).get("psnr_infinite") is True for r in units) if metric=="psnr_db" else 0)
                if cid=="clean":
                    quality[prefix]["strict_quality"]=dict(pass_count=sum(r.get("strict_quality") is True for r in units),planned=len(ids))
            for method in scoped:
                keys=RULES if method in ("f5-r2","v5-r3") else ["presence"]
                if method in ("f5-r2","v5-r3"):
                    carrier[f"{method}/{cid}/{strength}"]=carrier_summary(ids,seeds,rows,method,cid,strength)
                for control in (["C0","wrong_owner"] if method in ("f5-r2","v5-r3") else ["C0"]):
                    arm="unmarked" if control=="C0" else method
                    owner=ALPHA if control=="C0" else BETA
                    for key in keys:
                        grouped=[[call_value(rows.get(unit_id(sid,cid,strength,seed,arm)),method,owner,key) for seed in seeds] for sid in ids]
                        flat=[v for group in grouped for v in group]
                        negatives[f"{method}/{cid}/{strength}/{control}/{key}"]=dict(planned=len(flat),observed=sum(v is not None for v in flat),positives=sum(v is True for v in flat),unresolved=sum(v is None for v in flat),
                            source_any_positive=sum(any(v is True for v in group) for group in grouped),source_unresolved=sum(any(v is None for v in group) for group in grouped),planned_sources=len(ids))
                if method in INTERNAL:
                    continue
                # Frozen native lengths when a config predates explicit payload_bits (WAM 32, VINE-R 100).
                bits=config.get("payload_bits",{}).get(method,{"wam":32,"vine-r":100}.get(method))
                cutoff=binomial_threshold(bits)/bits
                prefix=f"{method}/{cid}/{strength}"
                calls=[rows.get(unit_id(sid,cid,strength,seed,method),{}).get("detections",{}).get(method,{}).get(ALPHA,{}) for sid in ids for seed in seeds]
                accuracies=[c.get("presence",{}).get("accuracy") if c.get("status")=="ok" else None for c in calls]
                external[prefix]=dict(bit_accuracy=quantiles(accuracies),exact_message=sum(v==1 for v in accuracies),
                    native_mask_present=sum(c.get("status")=="ok" and c.get("native",{}).get("present") is True for c in calls) if method=="wam" else None,planned=len(calls),
                    independent_wrong_message_present=sum(c.get("wrong_message_presence",{}).get("present") is True for c in calls),
                    wrong_message_complement_present=sum(v is not None and 1-v>=cutoff for v in accuracies),
                    empty_mask_abstentions=sum(c.get("status")=="ok" and c.get("presence",{}).get("accuracy") is None for c in calls))
                source_points={}
                predicates={"common_presence":lambda c:c.get("presence",{}).get("present"),
                            "exact_message":lambda c:c.get("presence",{}).get("accuracy")==1}
                if method=="wam":
                    predicates["native_mask_presence"]=lambda c:c.get("native",{}).get("present")
                elif method=="trustmark-q":
                    predicates["native_bch_detected"]=lambda c:c.get("native",{}).get("present")
                    predicates["native_exact_payload"]=lambda c:c.get("native",{}).get("exact_payload")
                for endpoint,predicate in predicates.items():
                    values=[predicate(c) if c.get("status")=="ok" else None for c in calls]
                    groups=[values[i:i+len(seeds)] for i in range(0,len(values),len(seeds))]
                    needed=2 if len(seeds)==3 else 1
                    source_points[endpoint]=dict(positive_sources=sum(sum(v is True for v in g)>=needed for g in groups),
                        planned_sources=len(ids),observed_calls=sum(v is not None for v in values),
                        missing_calls=sum(v is None for v in values),
                        optimistic_sources_missing_as_success=sum(sum(v is not False for v in g)>=needed for g in groups))
                external[prefix]["source_operating_points"]=source_points
                for kind in (["agreement","mask"] if method=="wam" else ["agreement"]):
                    groups={arm:[[score(rows.get(unit_id(sid,cid,strength,seed,arm)),method,kind) for seed in seeds] for sid in ids] for arm in (method,"unmarked")}
                    roc[prefix+"/"+kind+"/outputs"]=empirical_roc([v for g in groups[method] for v in g],[v for g in groups["unmarked"] for v in g])
                    # Missing positives are -inf failures; any missing negative
                    # leaves the complete source-level ROC unresolved.
                    p=[median([-math.inf if v is None else v for v in g]) for g in groups[method]]
                    n=[None if any(v is None for v in g) else median(g) for g in groups["unmarked"]]
                    roc[prefix+"/"+kind+"/sources"]=empirical_roc(p,n)
    return dict(negatives=negatives,quality=quality,internal_carrier_states=carrier,
                external_operating_points=external,empirical_roc=roc,
                matched_distortion=matched_grid(config,sources,rows,vectors),
                captions=dict(roc="Outcome-selected descriptive ROC; no calibration claim",
                              matched="Fixed calipers and bins; no inferential tests; no decision override",
                              carrier="Read-first descriptive states; binding mismatch is not carrier absence; missing raw fields remain unresolved"))

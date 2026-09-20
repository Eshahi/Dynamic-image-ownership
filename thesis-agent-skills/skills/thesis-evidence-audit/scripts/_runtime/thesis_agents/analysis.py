"""Seed-aware deterministic descriptive analysis; no unsupported significance tests."""
import csv
import html
import io
import json
import math
import random
import re
import statistics
from pathlib import Path
from .common import ContractError, digest, fresh_dir, object_digest, parser, read, validate, write

def read_metrics(path):
    if Path(path).suffix.lower()=="csv":
        with Path(path).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
    data=read(path)
    return data if isinstance(data,list) else [data]

def percentile(values,q):
    values=sorted(values); position=(len(values)-1)*q
    lo=int(position); hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(position-lo)

def analyze(spec, metric_files, out):
    validate(spec,"experiment"); plan=spec["analysis"]
    expected={r["run_id"]:r for r in plan["expected_runs"]}
    if len(expected)!=len(plan["expected_runs"]): raise ContractError("Duplicate preregistered run IDs")
    if len({(r['condition'],r['seed']) for r in expected.values()})!=len(expected): raise ContractError("Repeated condition/seed in design; aggregate within-seed replicates explicitly first")
    rows=[]
    for file in metric_files: rows.extend(read_metrics(file))
    seen=set(); observed={}; failures=[]
    for row in rows:
        if set(row)!={"run_id","seed","condition","status",plan["metric"]}: raise ContractError("Metric columns disagree with preregistration")
        rid=row["run_id"]
        if rid in seen or rid not in expected: raise ContractError("Duplicate or unexpected run ID: "+rid)
        seen.add(rid); ref=expected[rid]
        raw_seed=row["seed"]
        if isinstance(raw_seed,bool) or not (isinstance(raw_seed,int) or isinstance(raw_seed,str) and re.fullmatch(r"-?(0|[1-9][0-9]*)",raw_seed)):
            raise ContractError("Seed must be an integer, never a truncated numeric value")
        try: seed=int(raw_seed)
        except (ValueError,TypeError): raise ContractError("Malformed seed") from None
        if seed!=ref["seed"] or row["condition"]!=ref["condition"]: raise ContractError("Run seed/condition mismatch")
        if row["status"] not in ("completed","failed","interrupted"): raise ContractError("Unknown run status")
        if row["status"]!="completed":
            failures.append({"run_id":rid,"status":row["status"]}); continue
        try: value=float(row[plan["metric"]])
        except (ValueError,TypeError): raise ContractError("Malformed metric") from None
        if not math.isfinite(value): raise ContractError("Non-finite metric")
        observed[(row["condition"],seed)]=value
    missing=sorted(set(expected)-seen)
    summaries={}
    for cond in plan["conditions"]:
        values=[v for (c,s),v in observed.items() if c==cond]
        summaries[cond]={"n":len(values),"mean":statistics.mean(values) if values else None,"median":statistics.median(values) if values else None,"sd":statistics.stdev(values) if len(values)>1 else None,"min":min(values) if values else None,"max":max(values) if values else None}
    warnings=[]; comparison=None
    if missing or failures: warnings.append("Incomplete/failed runs: descriptive results only; no superiority conclusion")
    if any(x["n"]<5 for x in summaries.values()): warnings.append("Few independent seeds; comparison may be underpowered")
    if plan["comparison"]:
        first,second=plan["comparison"]
        if first not in summaries or second not in summaries or first==second: raise ContractError("Invalid comparison conditions")
        seeds=sorted(s for c,s in observed if c==first and (second,s) in observed)
        differences=[observed[(second,s)]-observed[(first,s)] for s in seeds]
        comparison={"first":first,"second":second,"paired_seeds":seeds,"n":len(seeds),"mean_difference":statistics.mean(differences) if differences else None,"cohens_dz":None,"confidence_interval":None,"p_value":None}
        if len(differences)>1:
            sd=statistics.stdev(differences)
            comparison["cohens_dz"]=statistics.mean(differences)/sd if sd else None
        if plan["confidence_interval"]=="paired-bootstrap" and len(differences)>=5 and not missing and not failures:
            rng=random.Random(plan["random_seed"])
            estimates=[statistics.mean(rng.choices(differences,k=len(differences))) for _ in range(plan["bootstrap_samples"])]
            comparison["confidence_interval"]={"method":"paired-seed percentile bootstrap","level":0.95,"low":percentile(estimates,.025),"high":percentile(estimates,.975)}
        elif plan["confidence_interval"]!="none": warnings.append("Requested CI withheld: fewer than five complete seed pairs or incomplete runs")
    result={"experiment_id":spec["experiment_id"],"mode":plan["mode"],"metric":plan["metric"],"expected_count":len(expected),"observed_count":len(rows),"missing_runs":missing,"failed_runs":failures,"summaries":summaries,"comparison":comparison,"warnings":warnings,"conclusion":"No significance or superiority claim generated","multiple_comparisons":"Single prespecified comparison only; familywise analysis requires a reviewed extension"}
    out=fresh_dir(out); write(out/"statistics.json",result)
    stream=io.StringIO(newline=""); w=csv.writer(stream); w.writerow(["condition","n","mean","median","sd","min","max"])
    for cond,v in summaries.items(): w.writerow([cond,*[v[k] for k in ("n","mean","median","sd","min","max")]])
    write(out/"tables/descriptive.csv",stream.getvalue())
    # Deterministic standalone SVG, no graphics dependency. Each point is one independent seed.
    vals=list(observed.values()); low=min(vals,default=0); high=max(vals,default=1); span=high-low or 1
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="400" viewBox="0 0 760 400">','<rect width="760" height="400" fill="white"/>',f'<text x="20" y="24">{html.escape(plan["metric"])} by condition and seed</text>']
    for i,cond in enumerate(plan["conditions"]):
        x=100+i*min(150,550/max(1,len(plan["conditions"])-1))
        svg.append(f'<text x="{x}" y="370">{html.escape(cond)}</text>')
        for (c,seed),value in sorted(observed.items()):
            if c==cond:
                y=330-(value-low)/span*260
                svg.append(f'<circle cx="{x}" cy="{y:.4f}" r="4" fill="#146C94"><title>seed {seed}: {value}</title></circle>')
    svg.extend([f'<text x="15" y="65">{high:.5g}</text>',f'<text x="15" y="330">{low:.5g}</text>',"</svg>"])
    write(out/"figures/seed-values.svg","\n".join(svg))
    write(out/"exclusions.json",{"rule":"none","excluded":[],"failed_runs_retained":failures,"missing_runs":missing})
    outputs=[{"path":str(p.relative_to(out)).replace("\\","/"),"sha256":digest(p)} for p in sorted(out.rglob("*")) if p.is_file()]
    write(out/"provenance.json",{"schema_version":"1.0","script":"thesis_agents.analysis","script_sha256":digest(__file__),"specification":spec,"specification_sha256":object_digest(spec),"inputs":[{"path":str(Path(p).resolve()),"sha256":digest(p)} for p in metric_files],"parameters":plan,"outputs":outputs,"run_ids":sorted(seen)})
    write(out/"analysis-report.md","# Analysis\n\n"+json.dumps(result,indent=2)+"\n\nNo outliers removed. Seed pairs, not individual observations, are the unit of comparison. Negative and failed runs remain in the report.\n")
    return result

def main():
    p=parser("Analyze only the preregistered run inventory")
    p.add_argument("spec"); p.add_argument("metrics",nargs="+"); p.add_argument("--out",required=True)
    a=p.parse_args(); return analyze(read(a.spec),a.metrics,a.out)

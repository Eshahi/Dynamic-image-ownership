"""Independent evidence classification; never repairs or approves evidence."""
import csv
import io
import json
from pathlib import Path
from .common import ContractError, contained, digest, fresh_dir, object_digest, parser, read, validate, write
from .compute import verify_artifacts
from .research import validate_sources

def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def audit(claims,papers,ledger,run_root,analysis_root,evidence_root,expected_runs,reviewer,out,input_root=None):
    source_check=validate_sources(papers,ledger,evidence_root)
    evidence={}
    for item in ledger: evidence.setdefault(item["claim_id"],[]).append(item)
    run_manifests={}; run_errors={}
    for path in sorted(Path(run_root).glob("*/*/manifest.json")):
        m=read(path)
        try:
            validate(m,"run")
            if m["run_id"] in run_manifests: raise ContractError("Duplicate run manifest")
            run_manifests[m["run_id"]]=(m,path.parent)
            verify_artifacts(path.parent,m["output_artifacts"])
            if m["input_artifacts"]:
                if input_root is None: raise ContractError("Original input root unavailable; input checksums cannot be verified")
                verify_artifacts(input_root,m["input_artifacts"])
            if m["git_dirty"] or not m["seeds"] or not m["command"] or not m["environment"] or not m["approval_reference"]: raise ContractError("Incomplete reproducibility or approval provenance")
            if not m["output_artifacts"]: raise ContractError("No collected outputs")
        except (ContractError,OSError) as exc: run_errors[m.get("run_id","unknown")]=str(exc)
    findings=[]; matrix=[]
    for rid,error in run_errors.items(): findings.append({"severity":"blocking","code":"run-provenance","message":rid+": "+error})
    for error in source_check["errors"]: findings.append({"severity":"blocking","code":"source-contract","message":error})
    missing=set(expected_runs)-set(run_manifests)
    failed={rid for rid,(m,_) in run_manifests.items() if m["status"]!="completed"}
    if missing: findings.append({"severity":"blocking","code":"missing-runs","message":"Expected runs absent: "+", ".join(sorted(missing))})
    claim_ids=set()
    paper_map={p["paper_id"]:p for p in papers}
    for c in claims:
        validate(c,"claims")
        if c["claim_id"] in claim_ids: raise ContractError("Duplicate claim ID")
        claim_ids.add(c["claim_id"])
        if c["author_id"]==reviewer: raise ContractError("Reviewer cannot audit their own claims")
        supporting=[]; contrary=[]; unknown=[]
        for eid in c["evidence_ids"]:
            if eid not in evidence: unknown.append("Missing evidence entry: "+eid)
            for e in evidence.get(eid,[]):
                p=paper_map.get(e["source_id"])
                if not p or p["verification"]!="verified": unknown.append("Unverified source: "+e["source_id"])
                elif e["stance"]=="contradicting": contrary.append(eid)
                elif e["stance"]=="supporting" and e["kind"] in ("direct-evidence","author-interpretation"): supporting.append(eid)
                else: unknown.append("Inconclusive or inferential evidence: "+eid)
        for rid in c["run_ids"]:
            if rid not in run_manifests: unknown.append("Missing run: "+rid)
            elif rid in run_errors: unknown.append(run_errors[rid])
            elif run_manifests[rid][0]["status"]!="completed": unknown.append("Failed/unfinished run: "+rid)
            else: supporting.append(rid)
        if c["run_ids"] and (missing or failed-set(c["run_ids"])):
            unknown.append("Claim omits expected/failed runs; assess selection bias")
        for rel in c["analysis_paths"]:
            try:
                file=contained(analysis_root,rel)
                # Find the nearest provenance file within the declared analysis root.
                parent=file.parent
                while not (parent/"provenance.json").exists() and parent!=Path(analysis_root).resolve(): parent=parent.parent
                provenance=read(parent/"provenance.json")
                from . import analysis as analysis_module
                if provenance.get("script")!="thesis_agents.analysis" or provenance.get("script_sha256")!=digest(analysis_module.__file__): raise ContractError("Analysis script identity/checksum mismatch; supply reviewed original version")
                specification=provenance.get("specification")
                if specification is None or provenance.get("specification_sha256")!=object_digest(specification): raise ContractError("Analysis specification checksum mismatch")
                validate(specification,"experiment")
                if provenance.get("parameters")!=specification["analysis"]: raise ContractError("Analysis parameters disagree with specification")
                expected=[e for e in provenance["outputs"] if contained(parent,e["path"])==file]
                if len(expected)!=1 or digest(file)!=expected[0]["sha256"]: raise ContractError("Figure/table checksum mismatch or absent provenance")
                for inp in provenance["inputs"]:
                    if digest(inp["path"])!=inp["sha256"]: raise ContractError("Analysis input checksum mismatch")
                if set(expected_runs)-set(provenance["run_ids"]): raise ContractError("Analysis omits expected runs")
                supporting.append(rel)
            except (OSError,ContractError,KeyError) as exc: unknown.append(str(exc))
        if contrary: classification="conflicting"
        elif supporting and not unknown and not source_check["errors"]: classification="verified"
        elif supporting: classification="partially supported"
        elif unknown: classification="unverifiable"
        else: classification="unsupported"
        matrix.append({"claim_id":c["claim_id"],"classification":classification,"support":supporting,"contradictions":contrary,"unresolved":unknown})
        if classification!="verified": findings.append({"severity":"blocking","code":classification,"claim_id":c["claim_id"],"message":"; ".join(unknown) or classification})
    for warning in source_check["warnings"]: findings.append({"severity":"non-blocking","code":"source-warning","message":warning})
    result={"schema_version":"1.0","reviewer":reviewer,"approval":"not-granted","blocking":[f for f in findings if f["severity"]=="blocking"],"non_blocking":[f for f in findings if f["severity"]!="blocking"],"claims":matrix,"expected_runs":expected_runs,"failed_runs":sorted(failed),"missing_runs":sorted(missing)}
    out=fresh_dir(out); write(out/"findings.json",result)
    stream=io.StringIO(newline=""); w=csv.writer(stream); w.writerow(["claim_id","classification","support","contradictions","unresolved"])
    for row in matrix: w.writerow([row["claim_id"],row["classification"],json.dumps(row["support"]),json.dumps(row["contradictions"]),json.dumps(row["unresolved"])])
    write(out/"claim-matrix.csv",stream.getvalue())
    write(out/"audit-report.md","# Independent audit\n\n"+json.dumps(result,indent=2)+"\n\nVerified means traceability checks passed; human scientific review must assess whether evidence entails the claim. This audit is not human acceptance.\n")
    write(out/"reproducibility-checklist.md",f"# Reproducibility\n\nRun manifests found: {len(run_manifests)}\n\nMissing expected runs: {len(missing)}\n\nRun provenance errors: {json.dumps(run_errors)}\n\nChecked source identity, output hashes, seeds, environment, commit, command and approval references. Dataset properties require independent review.\n")
    write(out/"unresolved-items.md","# Blocking items\n\n"+"\n".join("- "+f["message"] for f in result["blocking"])+"\n")
    return result

def main():
    p=parser("Audit evidence independently without modifying source evidence")
    for arg in ("claims","response","runs","analysis","evidence-root","expected-runs","reviewer","out"): p.add_argument("--"+arg,required=True)
    p.add_argument("--input-root",help="Original experiment input root for checksum verification")
    a=p.parse_args(); data=read(a.response)
    return audit(load_jsonl(a.claims),data["papers"],data["evidence"],a.runs,a.analysis,a.evidence_root,read(a.expected_runs),a.reviewer,a.out,a.input_root)

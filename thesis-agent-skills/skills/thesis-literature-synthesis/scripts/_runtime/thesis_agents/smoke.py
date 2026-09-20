"""Synthetic artifacts for the official Spec Kit smoke workflow.

Synthetic compute is explicitly separate from approved real execution. Gate
decisions are provided by a human or an isolated test harness, never here.
"""
import json
from pathlib import Path
from .common import ContractError, digest, identifier, now, object_digest, parser, read, write
from .research import request, synthesize
from .design import design
from .analysis import analyze
from .audit import audit

def sample_spec():
    return {"schema_version":"1.0","experiment_id":"synthetic-noop","task_id":"smoke","question":"Does the synthetic no-op emit every declared run?","hypothesis":"All declared synthetic runs emit the fixed value zero.","primary_outcome":"value","secondary_outcomes":[],"datasets":[],"leakage_risks":["Synthetic fixture; no scientific interpretation"],"preprocessing":"None","baselines":["Fixed zero"],"controls":["No network and no GPU"],"ablations":[],"seeds":[1,2,3,4,5],"stopping_rule":"Five synthetic records only","acceptance_rule":"Every declared run is present; this tests infrastructure only","negative_result_policy":"Preserve all failed or missing records","analysis":{"mode":"preregistered","metric":"value","direction":"lower","conditions":["noop"],"expected_runs":[{"run_id":f"seed-{i}","condition":"noop","seed":i} for i in range(1,6)],"comparison":None,"confidence_interval":"none","bootstrap_samples":1000,"random_seed":0,"multiple_comparisons":"none-single-comparison","exclusion_rule":"none"}}

def sample_execution():
    return {"schema_version":"1.0","experiment_id":"synthetic-noop","run_id":"synthetic-run","stage_id":"smoke","task_id":"smoke","execution_target":"mock","reviewed_script":"scripts/noop.py","script_sha256":"0"*64,"git_commit":"0"*40,"seeds":[1,2,3,4,5],"datasets":[],"inputs":[],"outputs":["metrics/values.json"],"metrics":["value"],"budget":{"max_seconds":30,"max_usd":0,"hourly_usd":0},"resources":{"vram_mib":0,"ram_mib":64,"disk_mib":5},"cleanup_policy":"delete-after-verified"}

def stage(action,project,run_id):
    identifier(run_id); root=Path(project)/"smoke-output"/run_id; root.mkdir(parents=True,exist_ok=True)
    done=root/(action+".receipt.json")
    if done.exists():
        receipt=read(done)
        for item in receipt["outputs"]:
            if digest(root/item["path"])!=item["sha256"]: raise ContractError("Completed smoke stage artifact changed")
        return receipt
    before={p for p in root.rglob("*") if p.is_file()}
    if action=="research":
        task={"id":"smoke","title":"Synthetic infrastructure test","evidence_requirements":["All synthetic records retained"],"inputs":[],"outputs":[["response.json","Synthetic research contract"]],"dependencies":[],"gates":["Human review required"]}
        request(task,"smoke-request",root/"research")
        write(root/"research/evidence-review.md","# Evidence review\n\nInfrastructure-only synthetic data. No paper findings, thesis claims or scientific evidence. Review this boundary before continuing.\n")
    elif action=="design":
        design(sample_spec(),sample_execution(),root/"experiments/synthetic-noop")
    elif action=="execute":
        rows=[{"run_id":f"seed-{i}","seed":i,"condition":"noop","status":"completed","value":0.0} for i in range(1,6)]
        write(root/"metrics.json",rows)
        write(root/"mock-execution.json",{"schema_version":"1.0","backend":"synthetic-noop","real_experiment":False,"rows":len(rows),"network_calls":0,"gpu_work":False})
    elif action=="analysis":
        analyze(sample_spec(),[root/"metrics.json"],root/"analysis/synthetic-noop")
    elif action=="audit":
        # Audit infrastructure observations, not invented literature or scientific runs.
        c={"claim_id":"smoke-integrity","text":"Synthetic no-op records were analyzed without exclusion","evidence_ids":[],"run_ids":[],"analysis_paths":["synthetic-noop/tables/descriptive.csv"],"kind":"result","author_id":"smoke-worker"}
        audit([c],[],[],root/"artifacts",root/"analysis",root,[],"smoke-reviewer",root/"audits/smoke-audit")
    elif action=="complete":
        finding=read(root/"audits/smoke-audit/findings.json")
        if finding["blocking"]: raise ContractError("Smoke audit has blocking findings")
        write(root/"completion.json",{"status":"completed","scope":"Infrastructure only","live_services_contacted":False})
    else: raise ContractError("Unknown smoke action")
    outputs=[{"path":p.relative_to(root).as_posix(),"sha256":digest(p)} for p in sorted(root.rglob("*")) if p.is_file() and p not in before]
    result={"stage":action,"run_id":run_id,"outputs":outputs}
    write(done,result); return result

def main():
    p=parser("Run a single allowlisted synthetic stage; this does not issue approvals")
    p.add_argument("action",choices=["research","design","execute","analysis","audit","complete"]); p.add_argument("--project",required=True); p.add_argument("--run-id",required=True)
    a=p.parse_args(); return stage(a.action,a.project,a.run_id)

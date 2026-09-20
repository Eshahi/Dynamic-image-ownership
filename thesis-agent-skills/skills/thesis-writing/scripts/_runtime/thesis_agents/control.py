"""Thin allowlisted adapter to Spec Kit; it never owns workflow state."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import re
from .common import ContractError, contained, digest, identifier, object_digest, parser, read, redact, safe_env, timestamp, validate, write

WORKFLOWS={"thesis-lifecycle","thesis-smoke"}
CLI=[sys.executable,"-c","from specify_cli import main; main()"]

def invoke(project,args):
    # A Windows NUL handle may report isatty() true. An empty PIPE is reliably
    # noninteractive on all supported systems, so unattended gates pause.
    p=subprocess.run([*CLI,"workflow",*args,"--json"],cwd=project,capture_output=True,text=True,encoding="utf-8",errors="replace",input="",timeout=3600,env=safe_env())
    try: data=json.loads(p.stdout)
    except json.JSONDecodeError: raise ContractError("Spec Kit did not return JSON: "+redact(p.stderr)[:500]) from None
    if p.returncode and data.get("status") not in ("failed","aborted"):
        raise ContractError("Spec Kit error: "+redact(p.stderr)[:500])
    return data

def load_workflow(project,wid):
    if wid not in WORKFLOWS: raise ContractError("Unknown workflow ID")
    import yaml
    file=contained(project,".specify/workflows/"+wid+"/workflow.yml")
    data=yaml.safe_load(file.read_text(encoding="utf-8"))
    if data["workflow"]["id"]!=wid: raise ContractError("Installed workflow ID mismatch")
    # Control adapter intentionally rejects overlays: changes require explicit review
    # and installation of the reviewed workflow version before controller operation.
    overlays=Path(project)/".specify/workflows/overlays"/wid
    if overlays.exists() and any(overlays.rglob("*.yml")): raise ContractError("Review and flatten overlays before controller use")
    return data

def status(project,run_id):
    identifier(run_id); data=invoke(project,["status",run_id])
    if data.get("run_id")!=run_id: raise ContractError("Spec Kit changed run ID")
    data["workflow_sha256"]=object_digest(load_workflow(project,data["workflow_id"]))
    return data

def fingerprint(data):
    return object_digest({k:data.get(k) for k in ("run_id","workflow_id","workflow_sha256","status","current_step_id","steps","gate","error")})

def summarize(data):
    text=f"{data['workflow_id']} | {data['run_id']} | {data['status']}"
    if data.get("current_step_id"): text+=" | step "+data["current_step_id"]
    if data.get("gate"): text+="\nHuman decision required: "+", ".join(data["gate"].get("options") or [])
    if data.get("error"): text+="\n"+redact(data["error"])
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]","",text)[:1500]

def watch_once(data,previous=None):
    token=fingerprint(data)
    if previous==token: return None
    return {"notification":summarize(data),"token":token,"run_id":data["run_id"],"status":data["status"]}

def gate_package(project,data):
    definition=load_workflow(project,data["workflow_id"])
    steps=[s for s in definition["steps"] if s["id"]==data.get("current_step_id")]
    if data["status"]!="paused" or len(steps)!=1 or steps[0].get("type")!="gate": raise ContractError("Run is not paused at a known human gate")
    step=steps[0]
    if set(step["options"])-{"approve","reject"}: raise ContractError("This adapter supports approve/reject gates only; revise/retry/stop need explicit workflow semantics")
    if step.get("on_reject")!="abort": raise ContractError("Unexpected reject behavior")
    return {"run_id":data["run_id"],"workflow_id":data["workflow_id"],"step_id":step["id"],"state_sha256":fingerprint(data),"workflow_sha256":object_digest(definition),"allowed_verdicts":step["options"],"message":step["message"],"evidence_to_review":step.get("show_file"),"verdict_input":step["verdict_input"],"approval":"not-granted"}

def resume(project,run_id,decision,execute=False,stop=False):
    validate(decision,"gate-decision")
    data=status(project,run_id); package=gate_package(project,data)
    if decision["run_id"]!=run_id or decision["step_id"]!=package["step_id"]: raise ContractError("Decision run/step mismatch")
    if decision["state_sha256"]!=package["state_sha256"]: raise ContractError("Stale decision: workflow state changed")
    current=datetime.now(timezone.utc)
    if not timestamp(decision["timestamp"])<=current<timestamp(decision["expires_at"]): raise ContractError("Expired or future gate decision")
    verdict=decision["verdict"]
    if stop:
        if verdict!="reject": raise ContractError("Stop at a gate requires explicit reject; active-run stop is unsupported upstream")
    if verdict not in package["allowed_verdicts"]: raise ContractError("Unsupported verdict for this workflow")
    args=["resume",run_id,"--input",package["verdict_input"]+"="+verdict]
    if not execute: return {"dry_run":True,"argv":["specify","workflow",*args,"--json"],"approval":package}
    # Archive the original decision. An agent must never fabricate it.
    decisions=contained(project,".specify/thesis-decisions/"+run_id+"-"+package["step_id"]+"-"+object_digest(decision)+".json")
    if decisions.exists(): raise ContractError("Decision already consumed; inspect current state")
    write(decisions,decision)
    return invoke(project,args)

def main():
    p=parser("Control only known installed thesis Spec Kit workflows")
    p.add_argument("--project",required=True)
    sub=p.add_subparsers(dest="action",required=True)
    q=sub.add_parser("start"); q.add_argument("workflow",choices=sorted(WORKFLOWS)); q.add_argument("--execute",action="store_true")
    sub.add_parser("list")
    for action in ("status","summarize","watch-once","prepare-approval","resume","stop"):
        q=sub.add_parser(action); q.add_argument("run_id")
        if action=="watch-once": q.add_argument("--previous-token")
        if action in ("resume","stop"): q.add_argument("--decision",required=True); q.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if a.action=="start":
        load_workflow(a.project,a.workflow)
        return invoke(a.project,["run",a.workflow]) if a.execute else {"dry_run":True,"workflow":a.workflow}
    if a.action=="list":
        data=invoke(a.project,["status"])
        return {"runs":[r for r in data["runs"] if r["workflow_id"] in WORKFLOWS]}
    if a.action in ("resume","stop"): return resume(a.project,a.run_id,read(a.decision),a.execute,a.action=="stop")
    data=status(a.project,a.run_id)
    if a.action=="status": return data
    if a.action=="summarize": return {"message":summarize(data)}
    if a.action=="watch-once": return watch_once(data,a.previous_token)
    return gate_package(a.project,data)

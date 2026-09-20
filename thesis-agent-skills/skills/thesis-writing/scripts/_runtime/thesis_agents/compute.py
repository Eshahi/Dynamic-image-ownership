"""Approved local and provider-isolated execution. Dry-run is the default."""
from __future__ import annotations
import csv
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from .common import ContractError, contained, digest, fresh_dir, identifier, now, object_digest, parser, read, redact, relative, safe_env, timestamp, validate, write
from .design import recommend

def parse_gpu(text):
    result=[]
    for row in csv.reader(io.StringIO(text)):
        if len(row)!=5: raise ContractError("Malformed nvidia-smi CSV")
        try:
            index,name,total,free,driver=[s.strip() for s in row]
            item={"index":int(index),"name":name,"total_mib":int(total),"free_mib":int(free),"driver":driver}
            if not 0<=item["free_mib"]<=item["total_mib"]: raise ValueError()
            result.append(item)
        except ValueError: raise ContractError("Invalid GPU memory values") from None
    return result

def gpu_info():
    exe=shutil.which("nvidia-smi")
    if not exe: return []
    p=subprocess.run([exe,"--query-gpu=index,name,memory.total,memory.free,driver_version","--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=15,env=safe_env())
    if p.returncode: return []
    return parse_gpu(p.stdout)

def approval_check(approval, manifest):
    validate(approval,"approval"); validate(manifest,"execution")
    for key in ("experiment_id","run_id","execution_target"):
        if approval[key]!=manifest[key]: raise ContractError("Approval scope mismatch: "+key)
    if approval["manifest_sha256"]!=object_digest(manifest): raise ContractError("Approval manifest hash mismatch")
    current=datetime.now(timezone.utc)
    if not timestamp(approval["timestamp"])<=current<timestamp(approval["expires_at"]): raise ContractError("Approval expired or issued in the future")
    if approval["decision"]!="approve": raise ContractError("Execution not approved")
    if manifest["budget"]["max_seconds"]>approval["max_seconds"] or manifest["budget"]["max_usd"]>approval["max_usd"]: raise ContractError("Approval budget/duration exceeded")
    return True

def verify_artifacts(root, entries):
    for item in entries:
        file=contained(root,item["path"])
        if not file.is_file() or digest(file)!=item["sha256"]: raise ContractError("Artifact missing or checksum mismatch: "+item["path"])
    return True

def collect(source, out, declared):
    records=[]
    for name in declared:
        src=contained(source,name); dest=contained(out,name)
        if not src.is_file(): raise ContractError("Declared artifact missing: "+name)
        sha=digest(src)
        if src.resolve()!=dest.resolve():
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists(): raise ContractError("Artifact destination already exists")
            shutil.copyfile(src,dest)
        if digest(dest)!=sha: raise ContractError("Artifact changed during collection")
        records.append({"path":name.replace("\\","/"),"sha256":sha})
    return records

class FakeProvider:
    """No network calls. Exact in-memory identity and intentional failure injection."""
    def __init__(self, fail_collection=False):
        self.pods={}; self.calls=[]; self.fail_collection=fail_collection
    def create(self,m):
        pid="mock-"+m["run_id"]
        if pid in self.pods: raise ContractError("Duplicate Pod")
        self.pods[pid]={"id":pid,"name":"thesis-"+m["run_id"],"status":"completed"}; self.calls.append(("create",pid)); return pid
    def status(self,pid):
        self.calls.append(("status",pid)); return self.pods[pid].copy()
    def collect(self,pid,m,out):
        if self.fail_collection: raise ContractError("Mock transfer interrupted")
        for path in m["outputs"]:
            file=contained(out,path)
            write(file, {"synthetic":True,"run_id":m["run_id"],"seed":m["seeds"][0],"condition":"noop","status":"completed","value":0.0})
        return collect(out,out,m["outputs"])
    def stop(self,pid):
        self.pods[pid]["status"]="stopped"; self.calls.append(("stop",pid))
    def delete(self,pid):
        del self.pods[pid]; self.calls.append(("delete",pid))

def exact_cleanup(provider, pid, run_id, delete=False):
    info=provider.status(pid)
    if info.get("id")!=pid or info.get("name")!="thesis-"+run_id: raise ContractError("Refusing cleanup: exact Pod identity mismatch")
    provider.delete(pid) if delete else provider.stop(pid)

def git_state(repo):
    def call(args):
        p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,text=True,timeout=20,env=safe_env())
        if p.returncode: raise ContractError("A version-controlled repository is required")
        return p.stdout.strip()
    return call(["rev-parse","HEAD"]), bool(call(["status","--porcelain"]))

def check_execution(m,repo):
    validate(m,"execution")
    if len(m["seeds"])!=len(set(m["seeds"])): raise ContractError("Duplicate seeds")
    if len(m["outputs"])!=len(set(m["outputs"])): raise ContractError("Duplicate outputs")
    script=contained(repo,m["reviewed_script"])
    if script.suffix!=".py" or digest(script)!=m["script_sha256"]: raise ContractError("Reviewed Python script hash mismatch")
    for name in m["outputs"]:
        p=contained(repo,name)
        if relative(name).parts[0] not in ("logs","metrics","checkpoints","outputs"):
            raise ContractError("Outputs must belong to artifact contract directories")
    verify_artifacts(repo,m["inputs"])
    if m["budget"]["hourly_usd"]*m["budget"]["max_seconds"]/3600>m["budget"]["max_usd"]: raise ContractError("Estimated cost exceeds declared cap")
    return script

def dispatch(m,repo,artifact_root,execute=False,approval=None,target=None,provider=None):
    if target and target!=m["execution_target"]: raise ContractError("Target override changes scope: revise manifest and obtain matching approval")
    script=check_execution(m,repo)
    target=m["execution_target"]
    if approval is not None: approval_check(approval,m)
    if not execute:
        return {"dry_run":True,"target":target,"manifest_sha256":object_digest(m),"requires_approval":True,"recommendation":recommend(m["resources"]),"command":["python",m["reviewed_script"],"--manifest","execution-manifest.json","--output-dir","run artifact directory"]}
    if approval is None: raise ContractError("Explicit matching human approval required for execution")
    approval_check(approval,m)
    if target=="runpod" and "remote" not in m: raise ContractError("Remote contract missing")
    actual_commit,dirty=git_state(repo)
    if actual_commit!=m["git_commit"] or dirty: raise ContractError("Execution requires exact clean reviewed Git commit")
    tracked=subprocess.run(["git","-C",str(repo),"ls-files","--error-unmatch","--",m["reviewed_script"]],capture_output=True,env=safe_env(),timeout=15)
    if tracked.returncode: raise ContractError("Reviewed script is not version-controlled")
    gpu=[] if target!="local" else gpu_info()
    if target=="local" and m["resources"]["vram_mib"]:
        if not gpu or recommend(m["resources"],max(g["free_mib"] for g in gpu))["target"]!="local": raise ContractError("Insufficient measured local GPU availability")
    out=fresh_dir(Path(artifact_root)/m["stage_id"]/m["run_id"])
    for folder in ("logs","metrics","checkpoints","outputs"):
        (out/folder).mkdir()
        write(out/folder/"contract.json",{"declared":[p for p in m["outputs"] if p.startswith(folder+"/")],"note":"Empty declared list means no such artifact required"})
    write(out/"execution-manifest.json",m)
    record={"schema_version":"1.0","run_id":m["run_id"],"stage_id":m["stage_id"],"task_id":m["task_id"],"experiment_id":m["experiment_id"],"status":"running","executor":"thesis-agents-1.0.0","execution_target":target,"created_at":now(),"started_at":now(),"ended_at":None,"git_commit":actual_commit,"git_dirty":dirty,"command":["python",m["reviewed_script"],"--manifest","execution-manifest.json","--output-dir","run artifact directory"],"environment":{"python":platform.python_version(),"platform":platform.platform()},"system":{"gpu":gpu,"cpu_count":os.cpu_count()},"seeds":m["seeds"],"datasets":m["datasets"],"input_artifacts":m["inputs"],"output_artifacts":[],"declared_metrics":m["metrics"],"budget_limits":m["budget"],"approval_reference":object_digest(approval),"execution_manifest_sha256":object_digest(m),"errors":[],"cleanup_status":"not-applicable","pod_id":None,"exit_status":None}
    write(out/"manifest.json",record)
    pod=None
    try:
        if target=="local":
            command=[sys.executable,str(script),"--manifest",str((out/"execution-manifest.json").resolve()),"--output-dir",str(out.resolve())]
            proc=subprocess.run(command,cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=m["budget"]["max_seconds"],env=safe_env())
            write(out/"logs/process.log",redact(proc.stdout+"\n"+proc.stderr))
            record["exit_status"]=proc.returncode
            record["output_artifacts"]=collect(out,out,m["outputs"])
            record["status"]="completed" if proc.returncode==0 else "failed"
            if proc.returncode: record["errors"].append("Reviewed script returned nonzero status")
        else:
            if provider is None:
                if target=="mock": provider=FakeProvider()
                else:
                    from .runpod import RunpodProvider
                    provider=RunpodProvider()
            pod=provider.create(m); record["pod_id"]=pod; record["cleanup_status"]="pending"; write(out/"manifest.json",record,True)
            deadline=time.monotonic()+m["budget"]["max_seconds"]
            while True:
                state=provider.status(pod)
                if state.get("status") in ("completed","failed"): break
                if time.monotonic()>=deadline: raise ContractError("Execution time budget exhausted")
                time.sleep(min(5,max(0,deadline-time.monotonic())))
            record["output_artifacts"]=provider.collect(pod,m,out)
            verify_artifacts(out,record["output_artifacts"])
            if {x["path"] for x in record["output_artifacts"]}!={x.replace('\\','/') for x in m["outputs"]}: raise ContractError("Provider omitted declared artifacts")
            record["status"]=state["status"]; record["exit_status"]=0 if state["status"]=="completed" else 1
            exact_cleanup(provider,pod,m["run_id"],delete=m["cleanup_policy"]=="delete-after-verified")
            record["cleanup_status"]="deleted" if m["cleanup_policy"]=="delete-after-verified" else "stopped"
    except (Exception,KeyboardInterrupt) as exc:
        record["status"]="interrupted" if isinstance(exc,KeyboardInterrupt) else "failed"
        record["errors"].append(redact(type(exc).__name__+": "+str(exc)))
        if pod:
            record["status"]="recovery-required"
            try:
                exact_cleanup(provider,pod,m["run_id"])
                record["cleanup_status"]="stopped-for-recovery"
            except Exception as cleanup:
                record["cleanup_status"]="cleanup-failed"; record["errors"].append(redact(cleanup))
            write(out/"recovery.json",{"pod_id":pod,"run_id":m["run_id"],"required_outputs":m["outputs"],"instruction":"Recover declared artifacts before termination deadline. Stopped storage may bill. Do not create another Pod. Cleanup may only use this persisted exact Pod ID and run name."})
    finally:
        record["ended_at"]=now(); validate(record,"run"); write(out/"manifest.json",record,True)
        write(out/"summary.md",f"# Run {m['run_id']}\n\nStatus: {record['status']}\n\nCleanup: {record['cleanup_status']}\n\nErrors: {'; '.join(record['errors']) or 'none'}\n")
    return record

def main():
    p=parser("Preview or explicitly execute a reviewed experiment")
    sub=p.add_subparsers(dest="action",required=True)
    q=sub.add_parser("gpu"); q.add_argument("--fixture")
    q=sub.add_parser("validate-approval"); q.add_argument("manifest"); q.add_argument("approval")
    q=sub.add_parser("collect"); q.add_argument("manifest"); q.add_argument("--source",required=True); q.add_argument("--out",required=True)
    q=sub.add_parser("dispatch"); q.add_argument("manifest"); q.add_argument("--repo",required=True); q.add_argument("--artifacts",required=True); q.add_argument("--approval"); q.add_argument("--target",choices=["local","runpod","mock"]); q.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if a.action=="gpu": return parse_gpu(Path(a.fixture).read_text()) if a.fixture else gpu_info()
    if a.action=="validate-approval": return {"valid":approval_check(read(a.approval),read(a.manifest))}
    if a.action=="collect": return collect(a.source,a.out,read(a.manifest)["outputs"])
    result=dispatch(read(a.manifest),a.repo,a.artifacts,a.execute,read(a.approval) if a.approval else None,a.target)
    if result.get("status") in ("failed","interrupted","recovery-required"):
        print(json.dumps(result)); raise ContractError("Execution failed; see persisted manifest")
    return result

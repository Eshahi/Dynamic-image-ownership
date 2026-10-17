"""Approved local and provider-isolated execution. Dry-run is the default."""
from __future__ import annotations
import csv
import io
import importlib.util
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

def development_rehearsal_check(m, repo):
    """Narrow USD-0 registry exception; never an approval for held-out work."""
    if m["execution_target"] != "local" or any(m["budget"][k] != 0 for k in ("max_usd", "hourly_usd")):
        raise ContractError("Development rehearsal requires local execution at USD 0")
    if m["reviewed_script"] != "scripts/m1b_coco512_worker.py":
        raise ContractError("Development rehearsal requires the exact reviewed M1b entry")
    if not m["datasets"] or any(d["split"] != "development" for d in m["datasets"]):
        raise ContractError("Development rehearsal datasets must all be development, never test")
    plans = [i for i in m["inputs"] if i["path"].endswith(".m1b-plan.json")]
    if len(plans) != 1:
        raise ContractError("Development rehearsal requires exactly one bound .m1b-plan.json")
    plan = read(contained(repo, plans[0]["path"]))
    if plan.get("data_split") != "development" or plan.get("protocol") != "registry-two-factor-v1":
        raise ContractError("Development rehearsal requires registry-two-factor-v1 development plan")
    index = plan.get("sources", {}).get("index", {})
    if index not in m["inputs"]:
        raise ContractError("Development source index must be a bound manifest input")
    validator_path = "scripts/m1b_registry_runtime.py"
    if not any(i["path"] == validator_path for i in m["inputs"]):
        raise ContractError("Registry validator must be a bound manifest input")
    # Load the validator from this reviewed checkout, never a cached/import-path copy.
    spec = importlib.util.spec_from_file_location("_thesis_registry_rehearsal_validator", contained(repo, validator_path))
    module = importlib.util.module_from_spec(spec)
    old_module = sys.modules.get(spec.name)
    old_path = list(sys.path)
    old_bytecode = sys.dont_write_bytecode
    try:
        sys.modules[spec.name] = module
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(Path(repo).resolve() / "scripts"))
        spec.loader.exec_module(module)
        module.validate_plan(plan, Path(repo).resolve())
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        raise ContractError("Registry development plan validation failed: " + str(exc)) from exc
    finally:
        sys.path[:] = old_path
        sys.dont_write_bytecode = old_bytecode
        if old_module is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = old_module
    return {"mode": "development-rehearsal", "protocol": "registry-two-factor-v1",
            "data_split": "development", "execution_target": "local", "max_usd": 0,
            "authorization_source": "REGISTRY-M1B-PACKAGE-BRIEF-20261017.md, Claude clarification 3",
            "human_approval": None, "plan_sha256": plans[0]["sha256"],
            "source_index": index}


def process_alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        raise ContractError("Invalid persisted child process identity")
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: PID absent
                return False
            raise ContractError("Cannot establish that the prior child is inactive")
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise ContractError("Cannot query prior child process")
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        raise ContractError("Cannot establish that the prior child is inactive") from None


def local_artifact_directory(path, manifest, resume):
    """Hold an OS lock across execution; preserve every preceding attempt."""
    out = Path(path)
    if not resume:
        fresh_dir(out)
    elif not out.is_dir() or out.is_symlink():
        raise ContractError("Resume requires an existing exact local artifact directory")
    lock = (out / "dispatcher.lock").open("a+b")
    try:
        if os.name == "nt":
            import msvcrt
            if lock.seek(0, 2) == 0:
                lock.write(b"0"); lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        if resume:
            if object_digest(read(out / "execution-manifest.json")) != object_digest(manifest):
                raise ContractError("Resume execution manifest differs from the exact stored manifest")
            prior = read(out / "manifest.json")
            if prior["execution_manifest_sha256"] != object_digest(manifest) or prior["run_id"] != manifest["run_id"]:
                raise ContractError("Resume prior run identity does not match manifest")
            if prior["status"] == "completed":
                raise ContractError("Completed runs cannot resume")
            state = read(out / "dispatcher-state.json")
            if state.get("status") not in ("running", "exited") or (state.get("status") == "running" and state.get("child_pid") is None):
                raise ContractError("Prior child launch state is uncertain; resume refused")
            child = state.get("child_pid")
            if child is not None and process_alive(child):
                raise ContractError("Prior child process is still active; resume refused")
            attempts = out / "attempts"
            attempts.mkdir(exist_ok=True)
            number = 1
            while (attempts / f"attempt-{number:03d}").exists():
                number += 1
            archive = fresh_dir(attempts / f"attempt-{number:03d}")
            for name in ("manifest.json", "dispatcher-state.json", "logs/process.log", "summary.md"):
                src = out / name
                if src.is_file():
                    dest = archive / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dest)
        return out, lock
    except (OSError, ValueError, KeyError) as exc:
        lock.close()
        if isinstance(exc, ContractError):
            raise
        raise ContractError("Cannot safely reopen local artifact directory: " + str(exc)) from exc


def dispatch(m,repo,artifact_root,execute=False,approval=None,target=None,provider=None,development_rehearsal=False,resume_incomplete=False):
    if target and target!=m["execution_target"]: raise ContractError("Target override changes scope: revise manifest and obtain matching approval")
    script=check_execution(m,repo)
    target=m["execution_target"]
    if resume_incomplete and target != "local":
        raise ContractError("Resume-incomplete is available only for local execution")
    rehearsal_context = None
    if development_rehearsal:
        if approval is not None:
            raise ContractError("Development rehearsal cannot consume a human approval")
        # A validator is executable reviewed code: check cleanliness before loading it.
        actual_commit,dirty=git_state(repo)
        if actual_commit!=m["git_commit"] or dirty:
            raise ContractError("Execution requires exact clean reviewed Git commit")
        rehearsal_context = development_rehearsal_check(m, repo)
    if approval is not None: approval_check(approval,m)
    if not execute:
        return {"dry_run":True,"target":target,"manifest_sha256":object_digest(m),"requires_approval":not development_rehearsal,"recommendation":recommend(m["resources"]),"command":["python",m["reviewed_script"],"--manifest","execution-manifest.json","--output-dir","run artifact directory"]}
    if not development_rehearsal:
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
    output_path=Path(artifact_root)/m["stage_id"]/m["run_id"]
    directory_lock = None
    if target == "local":
        out, directory_lock = local_artifact_directory(output_path, m, resume_incomplete)
    else:
        out = fresh_dir(output_path)
    if not resume_incomplete:
        for folder in ("logs","metrics","checkpoints","outputs"):
            (out/folder).mkdir()
            write(out/folder/"contract.json",{"declared":[p for p in m["outputs"] if p.startswith(folder+"/")],"note":"Empty declared list means no such artifact required"})
        write(out/"execution-manifest.json",m)
    if rehearsal_context is not None and not resume_incomplete:
        write(out/"rehearsal-context.json", rehearsal_context)
    record={"schema_version":"1.0","run_id":m["run_id"],"stage_id":m["stage_id"],"task_id":m["task_id"],"experiment_id":m["experiment_id"],"status":"running","executor":"thesis-agents-1.2.0","execution_target":target,"created_at":now(),"started_at":now(),"ended_at":None,"git_commit":actual_commit,"git_dirty":dirty,"command":["python",m["reviewed_script"],"--manifest","execution-manifest.json","--output-dir","run artifact directory"],"environment":{"python":platform.python_version(),"platform":platform.platform()},"system":{"gpu":gpu,"cpu_count":os.cpu_count()},"seeds":m["seeds"],"datasets":m["datasets"],"input_artifacts":m["inputs"],"output_artifacts":[],"declared_metrics":m["metrics"],"budget_limits":m["budget"],"approval_reference":object_digest(approval),"execution_manifest_sha256":object_digest(m),"errors":[],"cleanup_status":"not-applicable","pod_id":None,"exit_status":None}
    if development_rehearsal:
        record["approval_reference"] = None
    write(out/"manifest.json",record,resume_incomplete)
    pod=None
    try:
        if target=="local":
            command=[sys.executable,str(script),"--manifest",str((out/"execution-manifest.json").resolve()),"--output-dir",str(out.resolve())]
            write(out/"dispatcher-state.json", {"dispatcher_pid": os.getpid(), "child_pid": None, "status": "starting"}, True)
            proc = None
            try:
                proc=subprocess.Popen(command,cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",env=safe_env())
                write(out/"dispatcher-state.json", {"dispatcher_pid": os.getpid(), "child_pid": proc.pid, "status": "running"}, True)
                stdout, stderr = proc.communicate(timeout=m["budget"]["max_seconds"])
            except BaseException:
                if proc is not None:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                else:
                    stdout, stderr = "", "Child process could not start"
                write(out/"dispatcher-state.json", {"dispatcher_pid": os.getpid(), "child_pid": None, "status": "exited"}, True)
                write(out/"logs/process.log",redact(stdout+"\n"+stderr),resume_incomplete)
                raise
            write(out/"dispatcher-state.json", {"dispatcher_pid": os.getpid(), "child_pid": None, "status": "exited", "exit_status": proc.returncode}, True)
            write(out/"logs/process.log",redact(stdout+"\n"+stderr),resume_incomplete)
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
        try:
            record["ended_at"]=now(); validate(record,"run"); write(out/"manifest.json",record,True)
            write(out/"summary.md",f"# Run {m['run_id']}\n\nStatus: {record['status']}\n\nCleanup: {record['cleanup_status']}\n\nErrors: {'; '.join(record['errors']) or 'none'}\n",resume_incomplete)
        finally:
            if directory_lock is not None:
                directory_lock.close()
    return record

def main():
    p=parser("Preview or explicitly execute a reviewed experiment")
    sub=p.add_subparsers(dest="action",required=True)
    q=sub.add_parser("gpu"); q.add_argument("--fixture")
    q=sub.add_parser("validate-approval"); q.add_argument("manifest"); q.add_argument("approval")
    q=sub.add_parser("collect"); q.add_argument("manifest"); q.add_argument("--source",required=True); q.add_argument("--out",required=True)
    q=sub.add_parser("dispatch"); q.add_argument("manifest"); q.add_argument("--repo",required=True); q.add_argument("--artifacts",required=True); q.add_argument("--approval"); q.add_argument("--target",choices=["local","runpod","mock"]); q.add_argument("--execute",action="store_true"); q.add_argument("--development-rehearsal",action="store_true"); q.add_argument("--resume-incomplete",action="store_true")
    a=p.parse_args()
    if a.action=="gpu": return parse_gpu(Path(a.fixture).read_text()) if a.fixture else gpu_info()
    if a.action=="validate-approval": return {"valid":approval_check(read(a.approval),read(a.manifest))}
    if a.action=="collect": return collect(a.source,a.out,read(a.manifest)["outputs"])
    result=dispatch(read(a.manifest),a.repo,a.artifacts,a.execute,read(a.approval) if a.approval else None,a.target,development_rehearsal=a.development_rehearsal,resume_incomplete=a.resume_incomplete)
    if result.get("status") in ("failed","interrupted","recovery-required"):
        print(json.dumps(result)); raise ContractError("Execution failed; see persisted manifest")
    return result

"""Synthetic-only M1 lifecycle harness; official --manifest/--output-dir interface.

No scientific adapter, images, annotations, model or approval handling exists here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from m1_windows_job import OwnedJobProcess
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
OUTPUTS=["outputs/results.json","outputs/heartbeat.json","checkpoints/journal.json","outputs/harness-run.json"]
FIELDS={"schema_version","experiment_id","run_id","stage_id","task_id","execution_target","reviewed_script",
        "script_sha256","git_commit","seeds","datasets","inputs","outputs","metrics","budget","resources","cleanup_policy"}


def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("w",encoding="utf-8",newline="\n") as handle:
        json.dump(value,handle,sort_keys=True,indent=2,allow_nan=False)
        handle.write("\n");handle.flush();os.fsync(handle.fileno())
    temp.replace(path)


def read(path):return json.loads(path.read_text(encoding="utf-8"))


def contained(root,name):
    if not isinstance(name,str) or Path(name).is_absolute():raise ValueError("Relative contained path required")
    path=(root/name).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError("Path escapes root")
    return path


def validate_manifest(manifest,root):
    # Official schema remains authoritative; this is a deliberately narrower worker contract.
    if set(manifest)!=FIELDS or manifest["schema_version"]!="1.0":raise ValueError("Official manifest fields required")
    for key in ("experiment_id","run_id","stage_id","task_id"):
        if not isinstance(manifest[key],str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}",manifest[key]):raise ValueError("Invalid identifier")
    if manifest["execution_target"]!="local" or manifest["cleanup_policy"]!="stop-for-recovery":raise ValueError("Local retained rehearsal only")
    if manifest["datasets"]!=[{"id":"m1-synthetic-lifecycle","version":"1","license":"generated-fixture","split":"synthetic"}]:raise ValueError("Synthetic fixture dataset only")
    if set(manifest["outputs"])!=set(OUTPUTS) or len(manifest["outputs"])!=len(OUTPUTS):raise ValueError("Exact harness outputs required")
    if manifest["metrics"]!=["synthetic_units_completed"]:raise ValueError("No scientific metrics supported")
    budget=manifest["budget"]
    if set(budget)!={"max_seconds","max_usd","hourly_usd"} or type(budget["max_seconds"]) is not int or not 1<=budget["max_seconds"]<=3600 or budget["max_usd"]!=0 or budget["hourly_usd"]!=0:raise ValueError("Bounded USD0 budget required")
    resources=manifest["resources"]
    if set(resources)!={"vram_mib","ram_mib","disk_mib"} or resources["vram_mib"]!=0 or not 0<resources["ram_mib"]<=1024 or not 0<resources["disk_mib"]<=100:raise ValueError("CPU fixture resource bounds required")
    script=contained(root,manifest["reviewed_script"])
    if script!=Path(__file__).resolve() or file_sha(script)!=manifest["script_sha256"]:raise ValueError("Reviewed script hash/path mismatch")
    if not re.fullmatch(r"[a-f0-9]{40}",manifest["git_commit"]):raise ValueError("Commit required")
    if len(manifest["inputs"])!=1:raise ValueError("Exactly one synthetic plan input; no image inputs")
    item=manifest["inputs"][0]
    if set(item)!={"path","sha256"}:raise ValueError("Invalid input receipt")
    path=contained(root,item["path"])
    # Reject held-out paths before any read/hash of their bytes.
    if path.suffix!=".json" or not path.is_relative_to((root/".thesis-build/rehearsal").resolve()):raise ValueError("Plan must be synthetic JSON under rehearsal root")
    if file_sha(path)!=item["sha256"]:raise ValueError("Plan hash mismatch")
    plan=read(path)
    if set(plan)!={"schema_version","mode","candidate_status","unit_timeout_seconds","units"} or plan["schema_version"]!="m1-harness-plan-v1" or plan["mode"]!="synthetic-only" or plan["candidate_status"]!="UNRESOLVED":raise ValueError("Synthetic unresolved-candidate plan required")
    timeout=plan["unit_timeout_seconds"]
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not 0<timeout<=60:raise ValueError("Unit timeout bound invalid")
    if not isinstance(plan["units"],list) or not 1<=len(plan["units"])<=1000:raise ValueError("Bounded unit inventory required")
    ids=set();seeds=[]
    for unit in plan["units"]:
        if set(unit)!={"id","seed","delay_seconds","action"} or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",unit["id"]) or unit["id"] in ids:raise ValueError("Unit identity conflict")
        ids.add(unit["id"])
        if type(unit["seed"]) is not int or not 0<=unit["seed"]<2**64:raise ValueError("uint64 seed required")
        if isinstance(unit["delay_seconds"],bool) or not isinstance(unit["delay_seconds"],(int,float)) or not 0<=unit["delay_seconds"]<=60 or unit["action"] not in ("complete","fail"):raise ValueError("Fixture action/delay invalid")
        seeds.append(unit["seed"])
    if manifest["seeds"]!=sorted(set(seeds)):raise ValueError("Exact seed inventory required")
    return plan


def synthetic_unit(unit,path):
    if not any(path.resolve().is_relative_to((base/".thesis-build/rehearsal").resolve()) for base in (ROOT,MAIN)):
        raise ValueError("Internal fixture output must stay under rehearsal root")
    time.sleep(unit["delay_seconds"])
    if unit["action"]=="fail":raise RuntimeError("Prespecified synthetic failure")
    # Fabricated deterministic token, never an image/feature/detector outcome.
    atomic(path,{"unit_id":unit["id"],"seed":unit["seed"],"synthetic":True,
                 "fixture_token":object_sha([unit["id"],unit["seed"]]),"candidate_status":"UNRESOLVED"})


def verify_completed(output,journal,units):
    planned={u["id"]:u for u in units};completed={}
    for entry in journal["attempts"]:
        if entry["unit_id"] not in planned:raise ValueError("Unplanned journal unit")
        if entry["status"]=="completed":
            if entry["unit_id"] in completed:raise ValueError("Duplicate completed unit")
            path=contained(output,entry["path"])
            if not path.is_file() or file_sha(path)!=entry["sha256"]:raise ValueError("Completed unit artifact missing/corrupt")
            expected=planned[entry["unit_id"]]
            result=read(path)
            if result!={"unit_id":expected["id"],"seed":expected["seed"],"synthetic":True,"fixture_token":object_sha([expected["id"],expected["seed"]]),"candidate_status":"UNRESOLVED"}:raise ValueError("Unit content/seed mismatch")
            completed[entry["unit_id"]]=entry
    return completed


def verify_initial_output(output,manifest,lock):
    """Accept an empty directory or exactly the installed runner's launch envelope."""
    existing={p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() and p!=lock}
    if not existing:return
    envelope={"execution-manifest.json","manifest.json"}|{f"{d}/contract.json" for d in ("logs","metrics","checkpoints","outputs")}
    if existing!=envelope:raise ValueError("Nonempty unjournaled output refused")
    if read(output/"execution-manifest.json")!=manifest:raise ValueError("Runner envelope execution manifest mismatch")
    for folder in ("logs","metrics","checkpoints","outputs"):
        expected={"declared":[p for p in manifest["outputs"] if p.startswith(folder+"/")],"note":"Empty declared list means no such artifact required"}
        if read(output/folder/"contract.json")!=expected:raise ValueError("Runner output contract mismatch")
    record=read(output/"manifest.json")
    for key in ("run_id","stage_id","task_id","experiment_id","execution_target","git_commit","seeds","datasets"):
        if record.get(key)!=manifest[key]:raise ValueError("Runner envelope provenance mismatch: "+key)
    if record.get("status")!="running" or record.get("git_dirty") is not False or record.get("execution_manifest_sha256")!=object_sha(manifest):
        raise ValueError("Runner envelope status/commit/digest mismatch")


def run(manifest_path,output,recover=False,root=ROOT,rehearsal_root=None):
    started=time.monotonic();manifest=read(manifest_path);plan=validate_manifest(manifest,root)
    actual_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    if actual_commit!=manifest["git_commit"]:raise ValueError("Manifest commit differs from current checkout")
    allowed=(rehearsal_root or MAIN/".thesis-build/rehearsal").resolve()
    if not output.resolve().is_relative_to(allowed):raise ValueError("Synthetic outputs exclusively under rehearsal root")
    fingerprint={"manifest_sha256":object_sha(manifest),"script_sha256":file_sha(__file__),"plan_sha256":object_sha(plan),"git_commit":manifest["git_commit"],
        "containment_sha256":file_sha(ROOT/'scripts/m1_windows_job.py')}
    output.mkdir(parents=True,exist_ok=True)
    lock=output/"harness.lock"
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise ValueError("Live/stale lock preserved; host-loss recovery needs reviewed receipt/new attempt directory")
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    journal_path=output/"checkpoints/journal.json";run_path=output/"outputs/harness-run.json"
    process=None;record=None
    previous_handlers={}
    try:
        if journal_path.exists():
            journal=read(journal_path);prior=read(run_path)
            if journal.get("fingerprint")!=fingerprint or prior.get("fingerprint")!=fingerprint:raise ValueError("Recovery provenance mismatch")
            if file_sha(journal_path)!=prior.get("journal_sha256"):raise ValueError("Journal receipt mismatch; retained without repair")
            if prior["outcome"] not in ("completed","interrupted","timeout","failed"):raise ValueError("Unknown/stale parent state; no automatic recovery")
            if prior["outcome"]!="completed" and not recover:raise ValueError("Explicit --recover required")
            if any(e["status"]=="started" for e in journal["attempts"]):raise ValueError("Unknown in-flight attempt preserved; no automatic retry")
        else:
            verify_initial_output(output,manifest,lock)
            journal={"schema_version":"m1-harness-journal-v1","fingerprint":fingerprint,"attempts":[]}
        completed=verify_completed(output,journal,plan["units"])
        if journal_path.exists() and prior["outcome"]=="completed":
            if len(completed)!=len(plan["units"]) or file_sha(output/"outputs/results.json")!=prior["results_sha256"]:raise ValueError("Completed inventory mismatch")
            return 0
        record={"schema_version":"m1-harness-run-v1","fingerprint":fingerprint,"outcome":"started","synthetic":True,"candidate_status":"UNRESOLVED","pid":os.getpid(),"duration_seconds":0,"command":sys.argv}
        atomic(run_path,record);atomic(journal_path,journal)
        def interrupted(signum,frame):raise KeyboardInterrupt("termination signal "+str(signum))
        for signum in (signal.SIGINT,signal.SIGTERM):
            previous_handlers[signum]=signal.signal(signum,interrupted)
        deadline=started+manifest["budget"]["max_seconds"]-min(3,manifest["budget"]["max_seconds"]*.2)
        for unit in plan["units"]:
            if unit["id"] in completed:continue
            if time.monotonic()>=deadline:raise TimeoutError("Shard cooperative deadline")
            number=1+sum(e["unit_id"]==unit["id"] for e in journal["attempts"])
            relative=f"outputs/units/{unit['id']}-attempt{number}.json"
            target=output/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():raise ValueError("Attempt artifact overwrite refused")
            entry={"unit_id":unit["id"],"attempt":number,"status":"started","path":relative}
            journal["attempts"].append(entry);atomic(journal_path,journal)
            command=[sys.executable,str(Path(__file__).resolve()),"--synthetic-unit",json.dumps(unit),"--unit-output",str(target)]
            log=output/f"logs/{unit['id']}-attempt{number}.log";log.parent.mkdir(parents=True,exist_ok=True)
            with log.open("x",encoding="utf-8") as handle:
                def ownership(value):
                    entry['containment']=value;atomic(journal_path,journal)
                process=OwnedJobProcess(command,handle,cwd=root,receipt=ownership)
                unit_deadline=min(deadline,time.monotonic()+plan["unit_timeout_seconds"])
                atomic(output/"outputs/heartbeat.json",{"pid":os.getpid(),"child_pid":process.pid,"unit":unit["id"],"elapsed_seconds":time.monotonic()-started,"synthetic":True})
                while process.poll() is None:
                    atomic(output/"outputs/heartbeat.json",{"pid":os.getpid(),"child_pid":process.pid,"unit":unit["id"],"elapsed_seconds":time.monotonic()-started,"synthetic":True})
                    if time.monotonic()>=unit_deadline:raise TimeoutError("Unit/shard process deadline")
                    time.sleep(.05)
                if process.returncode:raise RuntimeError("Synthetic worker exit "+str(process.returncode))
            process.close();entry['containment']=dict(process.ownership)
            entry.update(status="completed",sha256=file_sha(target));atomic(journal_path,journal)
            completed=verify_completed(output,journal,plan["units"]);process=None
        result={"synthetic":True,"candidate_status":"UNRESOLVED","planned_units":len(plan["units"]),"completed_units":len(completed),"scientific_verdict":"NOT_EVIDENCE"}
        atomic(output/"outputs/results.json",result)
        record.update(outcome="completed",results_sha256=file_sha(output/"outputs/results.json"))
        return 0
    except (Exception,KeyboardInterrupt) as exc:
        if record is not None:
            status="interrupted" if isinstance(exc,KeyboardInterrupt) else "timeout" if isinstance(exc,TimeoutError) else "failed"
            if journal["attempts"] and journal["attempts"][-1]["status"]=="started":
                journal["attempts"][-1].update(status=status,error=str(exc));atomic(journal_path,journal)
            record.update(outcome=status,error_type=type(exc).__name__,error=str(exc))
        raise
    finally:
        if process is not None:
            process.close()
            journal['attempts'][-1]['containment']=dict(process.ownership);atomic(journal_path,journal)
        if record is not None:
            record["duration_seconds"]=time.monotonic()-started
            record["journal_sha256"]=file_sha(journal_path);atomic(run_path,record)
        for signum,handler in previous_handlers.items():signal.signal(signum,handler)
        lock.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path);parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--recover",action="store_true")
    parser.add_argument("--synthetic-unit");parser.add_argument("--unit-output",type=Path)
    args=parser.parse_args()
    if args.synthetic_unit is not None:
        if args.manifest or args.output_dir or args.unit_output is None:parser.error("Internal fixture worker arguments only")
        return synthetic_unit(json.loads(args.synthetic_unit),args.unit_output)
    if args.manifest is None or args.output_dir is None:parser.error("--manifest and --output-dir required")
    return run(args.manifest.resolve(),args.output_dir.resolve(),args.recover)


if __name__=="__main__":main()

"""Evaluation-only recovery phase; scientific entry via exact-approved runner."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import resource
import threading
import time
from v4_evaluation_journal import Journal, atomic_json, file_sha, object_sha, evaluate_units, summarize_journal

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/"experiments/c4-v4-three-threat-recovery-v1"
RUN = "c4-v4-saved-evaluation-002"


def host_path(value):
    value = str(value).replace("\\", "/")
    return Path("/mnt/"+value[0].lower()+value[2:]) if len(value)>2 and value[1:3]==":/" else Path(value)


def run(manifest_path, output_path):
    from three_threat_models import block_network
    block_network()
    manifest = json.loads(host_path(manifest_path).read_text())
    if (manifest["run_id"], manifest["experiment_id"], manifest["execution_target"]) != (RUN,"c4-v4-three-threat-recovery-v1","local"):
        raise ValueError("unexpected execution identity")
    if manifest["seeds"] != [0,1,2] or manifest["resources"] != {"ram_mib":6144,"vram_mib":0,"disk_mib":2048}:
        raise ValueError("evaluation CPU/resource contract differs")
    if manifest["budget"] != {"max_seconds":86400,"max_usd":0,"hourly_usd":0}:
        raise ValueError("evaluation budget differs")
    output = host_path(output_path)
    expected = host_path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/v4-recovery-runs")/manifest["stage_id"]/RUN
    if output.resolve() != expected.resolve():
        raise ValueError("fixed one-shot scientific output root required")
    runner_receipt = json.loads((output/"manifest.json").read_text())
    if (runner_receipt["status"] != "running" or runner_receipt["run_id"] != RUN or
        runner_receipt["execution_manifest_sha256"] != object_sha(manifest) or
        runner_receipt["git_commit"] != manifest["git_commit"] or runner_receipt["git_dirty"]):
        raise ValueError("matching actual official-runner receipt required")
    outputs = output/"outputs"
    outputs.mkdir(exist_ok=True)
    # Exclusive worker lease is retained even after interruption; never auto-steal.
    with (outputs/"worker-lease.json").open("x") as lease:
        json.dump({"pid":os.getpid(),"run_id":RUN,"started_ns":time.time_ns()},lease)
        lease.flush()
        os.fsync(lease.fileno())
    started = time.monotonic()
    manifest_hash = object_sha(manifest)
    journal = Journal(outputs/"journal", manifest_hash)
    state = {"run_id":RUN,"pid":os.getpid(),"process_start_ticks":Path("/proc/self/stat").read_text().split()[21],
             "boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
             "unit":None,"phase":"VERIFYING_INPUTS","last_sealed_unit":None}
    stop = threading.Event()
    heartbeat_error = []
    def pulse():
        try:
            while not stop.is_set():
                atomic_json(outputs/"heartbeat.json",{**state,"observed_at":datetime.now(timezone.utc).isoformat()})
                stop.wait(5)
        except BaseException as error:
            heartbeat_error.append(str(error))
    thread = threading.Thread(target=pulse, daemon=True)
    thread.start()
    adapter = None
    failure = None
    rows = {}
    units = []
    unit_start = time.monotonic()
    def guard():
        if heartbeat_error:
            raise OSError("heartbeat writer failed: "+heartbeat_error[0])
        if time.monotonic()-started > 86000 or time.monotonic()-unit_start > 1800:
            raise TimeoutError("bounded evaluation watchdog reached")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 6144*1024:
            raise MemoryError("polled CPU RAM ceiling reached")
        if sum(p.stat().st_size for p in outputs.rglob("*") if p.is_file()) > 2000*1024**2:
            raise OSError("output disk allowance reached")
    try:
        for item in manifest["inputs"]:
            if file_sha(ROOT/item["path"]) != item["sha256"]:
                raise ValueError("manifest input changed: "+item["path"])
        lock = json.loads((PACKAGE/"parent-input-lock.json").read_text())
        parent = host_path(lock["parent_root"])
        for entry in lock["artifacts"]:
            path = parent/entry["path"]
            if not path.resolve().is_relative_to(parent.resolve()) or file_sha(path) != entry["sha256"]:
                raise ValueError("bound parent artifact changed: "+entry["path"])
        snapshot = json.loads((parent/"outputs/results.json").read_text())
        rows = {r["id"]:r for r in snapshot["rows"]}
        from v4_recovery_design import make_schedule
        labels = json.loads((ROOT/"experiments/c4-three-threat-small-v1/semantic-labels.json").read_text())["pairs"]
        replay = make_schedule(snapshot,labels)
        if replay != json.loads((PACKAGE/"schedule.json").read_text()):
            raise ValueError("frozen schedule replay differs")
        units = [u for u in replay["units"] if u["phase"] not in ("new_generation","attempt_quarantine")]
        if len(units) != 209 or sum(len(u["row_ids"]) for u in units) != 483:
            raise ValueError("evaluation-only unit inventory differs")
        runtime_path = ROOT/"experiments/c4-three-threat-small-v1/runtime-files-v2.json"
        runtime = json.loads(runtime_path.read_text())
        for entry in runtime["files"]:
            guard()
            if file_sha(host_path(entry["path"])) != entry["sha256"]:
                raise ValueError("pinned runtime changed: "+entry["path"])
        parent_runtime = json.loads((parent/"outputs/runtime.json").read_text())
        if (parent_runtime["runtime_inventory_sha256"] != file_sha(runtime_path) or
            parent_runtime["profile_sha256"] != file_sha(ROOT/"experiments/c4-v4-three-threat-small-v1/profile.json")):
            raise ValueError("inherited runtime/profile binding differs")
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise ValueError("deterministic environment absent")
        import torch
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        torch.set_num_threads(1)
        from v4_saved_evaluation_adapter import SavedEvaluation
        state["phase"] = "LOADING_CPU_EVALUATORS"
        adapter = SavedEvaluation(parent, rows, host_path(lock["asset_root"]),
                                  ROOT/"experiments/c4-v4-three-threat-small-v1/profile.json",guard)
        atomic_json(outputs/"runtime.json",{"run_id":RUN,"manifest_sha256":manifest_hash,
                    "parent_results_sha256":lock["results_sha256"], "runtime_sha256":file_sha(runtime_path),
                    "asset_files":adapter.assets["files"],"cuda_used":False,"no_generation":True,
                    "scientific_acceptance":False})
        for unit in units:
            unit_start = time.monotonic()
            state.update(unit=unit["unit_id"],phase="EVALUATING")
            def boundary(identity, phase):
                state.update(row=identity,phase=phase)
                guard()
            evaluate_units([unit],rows,journal,adapter,guard,boundary,boundary)
            state.update(last_sealed_unit=unit["unit_id"],phase="SEALED")
            write_results(outputs,rows,units,journal,started,None)
        state["phase"] = "EVALUATION_PHASE_COMPLETE_STUDY_INCOMPLETE"
    except BaseException as error:
        failure = {"type":type(error).__name__,"message":str(error),"unit":state.get("unit"),
                   "row":state.get("row"),"phase":state["phase"]}
        atomic_json(outputs/"failure.json",failure)
        state["phase"] = "FAILED_PARTIAL_EVIDENCE_PRESERVED"
    finally:
        stop.set()
        thread.join(10)
        if adapter is not None:
            adapter.close()
        if heartbeat_error and failure is None:
            failure = {"type":"OSError","message":heartbeat_error[0]}
        final_errors = write_results(outputs,rows,units,journal,started,failure,tolerate_corruption=True)
        if final_errors and failure is None:
            failure = {"type":"ValueError","message":"final evidence integrity failed","integrity_errors":final_errors}
            state["phase"] = "FAILED_PARTIAL_EVIDENCE_PRESERVED"
            atomic_json(outputs/"failure.json",failure)
        if not (outputs/"runtime.json").exists():
            atomic_json(outputs/"runtime.json",{"run_id":RUN,"manifest_sha256":manifest_hash,"verification_incomplete":True})
        atomic_json(outputs/"heartbeat.json",{**state,"observed_at":datetime.now(timezone.utc).isoformat()})
        catalog = [{"path":p.relative_to(output).as_posix(),"sha256":file_sha(p)}
                   for p in sorted(outputs.rglob("*")) if p.is_file() and p.name!="artifact-index.json"]
        atomic_json(outputs/"artifact-index.json",{"run_id":RUN,"manifest_sha256":manifest_hash,"files":catalog})
    return 1 if failure else 0


def write_results(outputs, rows, units, journal, started, failure, tolerate_corruption=False):
    summary = summarize_journal(units,journal,tolerate_corruption)
    complete = len(summary["sealed_units"])==209 and len(summary["rows"])==483 and failure is None and not summary["integrity_errors"]
    atomic_json(outputs/"results.json",{"run_id":RUN,**summary,
        "evaluation_phase_complete":complete,"whole_study_complete":False,"method_acceptance":False,
        "scientific_verdict":"PENDING_ANALYSIS_AND_VISUAL_REVIEW_INCOMPLETE_ORIGINAL_CONTROLS",
        "planned_original_rows":537,"planned_original_detector_calls":1884,
        "withheld_generation_calls":212,"unresolved_parent_attempt_calls":4,
        "retained_safety_missing_calls":64,"failure":failure,"elapsed_seconds":time.monotonic()-started})
    return summary["integrity_errors"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest,args.output_dir))

"""Evaluation-only recovery phase; scientific entry via exact-approved runner."""
import argparse
from datetime import datetime, timezone
import faulthandler
import json
import os
from pathlib import Path
import re
import resource
import signal
import sys
import threading
import time
import traceback
from prepare_v4_saved_evaluation import contract, core_sha256, run_root
from run_v4_saved_evaluation import WORKER_MARGIN
from v4_evaluation_journal import (Journal, PENDING_PREFIX, atomic_json, file_sha, object_sha,
                                   evaluate_units, summarize_journal, tree_bytes)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/"experiments/c4-v4-three-threat-recovery-v1"
COMPLETE = "EVALUATION_PHASE_COMPLETE_STUDY_INCOMPLETE"
FAILED = "FAILED_PARTIAL_EVIDENCE_PRESERVED"


class Terminated(BaseException):
    """The first stop signal, raised once in the main thread while evaluation is interruptible."""


def host_path(value):
    value = str(value).replace("\\", "/")
    return Path("/mnt/"+value[0].lower()+value[2:]) if len(value)>2 and value[1:3]==":/" else Path(value)


def run(manifest_path, output_path, rehearsal=None):
    """`rehearsal` is passed only by the rehearsal script; the command line is always scientific.

    A rehearsal is confined to `.thesis-build/rehearsal/`, a `rehearsal-*` run id and its own
    synthetic parent, and marks every output and journal record as not evidence.
    """
    from three_threat_models import block_network
    block_network()
    rehearsing = rehearsal is not None
    manifest = json.loads(host_path(manifest_path).read_text())
    core = contract(manifest,rehearsing)
    run_id = manifest["run_id"]
    output = host_path(output_path)
    if output.resolve() != host_path(run_root(manifest,rehearsing)).resolve():
        raise ValueError("fixed one-shot output root required")
    manifest_hash = object_sha(manifest)
    receipt = json.loads((output/"manifest.json").read_text())
    if (receipt.get("status") != "running" or receipt.get("run_id") != run_id or
        receipt.get("execution_manifest_sha256") != manifest_hash):
        raise ValueError("matching running receipt required")
    if rehearsing:
        if receipt.get("rehearsal") is not True or "approval_reference" in receipt:
            raise ValueError("rehearsal receipt required")
    elif ("rehearsal" in receipt or receipt.get("git_commit") != manifest["git_commit"] or
          receipt.get("git_dirty") is not False or
          not re.fullmatch(r"[a-f0-9]{64}",str(receipt.get("approval_reference"))) or
          receipt.get("budget_limits") != manifest["budget"] or receipt.get("seeds") != manifest["seeds"]):
        raise ValueError("matching actual official-runner receipt required")
    outputs = output/"outputs"
    outputs.mkdir(exist_ok=True)
    # Exclusive worker lease is retained even after interruption; never auto-steal.
    with (outputs/"worker-lease.json").open("x") as lease:
        json.dump({"pid":os.getpid(),"run_id":run_id,"started_ns":time.time_ns()},lease)
        lease.flush()
        os.fsync(lease.fileno())
    started = time.monotonic()
    options = rehearsal or {}
    marker = {"rehearsal":True,"scientific_evidence":False} if rehearsing else {}
    core_hash = core_sha256(manifest)
    journal = Journal(outputs/"journal",("REHEARSAL-" if rehearsing else "")+manifest_hash)
    baseline = tree_bytes(outputs)
    written = [0]
    disk_limit = (core["resources"]["disk_mib"]-core["disk_reserve_mib"])*1024**2
    ram_limit = core["resources"]["ram_mib"]*1024
    deadline = options.get("deadline_seconds",manifest["budget"]["max_seconds"]-WORKER_MARGIN)
    unit_seconds = options.get("unit_seconds",core["unit_watchdog_seconds"])
    state = {"run_id":run_id,"pid":os.getpid(),"process_start_ticks":Path("/proc/self/stat").read_text().split()[21],
             "boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
             "unit":None,"phase":"VERIFYING_INPUTS","last_sealed_unit":None,"sealed_units":0,"signals":[],**marker}
    launcher = os.getppid()
    channel = [True]
    def log(**event):
        try:
            print(json.dumps(event,sort_keys=True),flush=True)
        except (OSError,ValueError):
            channel[0] = False
    def emit(name, value):
        written[0] += atomic_json(outputs/name,value)
    stop = threading.Event()
    heartbeat_error = []
    def pulse():
        misses = 0
        try:
            while not stop.is_set():
                try:
                    atomic_json(outputs/"heartbeat.json",{**state,"observed_at":datetime.now(timezone.utc).isoformat()})
                    misses = 0
                except OSError as error:
                    # A monitor briefly holding the file must not end an evaluation.
                    misses += 1
                    if misses >= 6:
                        raise OSError("six consecutive heartbeat writes failed: "+str(error))
                stop.wait(options.get("heartbeat_seconds",5))
        except BaseException as error:
            heartbeat_error.append(str(error))
    thread = threading.Thread(target=pulse, daemon=True)
    thread.start()
    signals = []
    interruptible = [False]
    raised = [False]
    def on_signal(number, frame):
        signals.append(signal.Signals(number).name)
        state["signals"] = list(signals)
        if interruptible[0] and not raised[0]:
            raised[0] = True
            raise Terminated(signals[-1])
    previous = {number:signal.signal(number,on_signal) for number in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP)}
    faulthandler.enable()
    adapter = None
    failure = None
    rows = {}
    units = []
    expected = (core["evaluation_units"],core["evaluation_rows"])
    unit_start = [None]
    def guard():
        if heartbeat_error:
            raise OSError("heartbeat writer failed: "+heartbeat_error[0])
        if not channel[0] or os.getppid() != launcher:
            raise OSError("launcher process or log channel lost")
        now = time.monotonic()
        if now-started > deadline or (unit_start[0] is not None and now-unit_start[0] > unit_seconds):
            raise TimeoutError("bounded evaluation watchdog reached")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > ram_limit:
            raise MemoryError("polled CPU RAM ceiling reached")
        if baseline+journal.bytes+written[0] > disk_limit:
            raise OSError("output disk allowance reached")
    try:
        interruptible[0] = True
        log(event="verifying",run_id=run_id,pid=os.getpid(),**marker)
        execution = core["execution"]
        if sys.prefix != execution["python_prefix"] or any(os.environ.get(k) != v for k,v in execution["env"].items()):
            raise ValueError("pinned interpreter or deterministic environment differs")
        for item in manifest["inputs"]:
            if file_sha(ROOT/item["path"]) != item["sha256"]:
                raise ValueError("manifest input changed: "+item["path"])
        lock = json.loads(((output if rehearsing else PACKAGE)/"parent-input-lock.json").read_text())
        parent = host_path(lock["parent_root"])
        synthetic = lock.get("rehearsal_synthetic") is True
        if rehearsing:
            if not synthetic or not parent.resolve().is_relative_to(output.resolve()):
                raise ValueError("a rehearsal evaluates only its own synthetic parent")
        elif synthetic or "rehearsal" in parent.as_posix().lower():
            raise ValueError("scientific evaluation refuses a rehearsal parent")
        for entry in lock["artifacts"]:
            guard()
            path = parent/entry["path"]
            if not path.resolve().is_relative_to(parent.resolve()) or file_sha(path) != entry["sha256"]:
                raise ValueError("bound parent artifact changed: "+entry["path"])
        snapshot = json.loads((parent/"outputs/results.json").read_text())
        if (snapshot.get("rehearsal_synthetic") is True) != rehearsing:
            raise ValueError("parent snapshot kind differs from run kind")
        rows = {r["id"]:r for r in snapshot["rows"]}
        from v4_recovery_design import make_schedule
        labels = json.loads((ROOT/"experiments/c4-three-threat-small-v1/semantic-labels.json").read_text())["pairs"]
        replay = make_schedule(snapshot,labels)
        if replay != json.loads((PACKAGE/"schedule.json").read_text()):
            raise ValueError("frozen schedule replay differs")
        units = [u for u in replay["units"] if u["phase"] not in core["excluded_phases"]]
        if (len(units),sum(len(u["row_ids"]) for u in units)) != expected:
            raise ValueError("evaluation-only unit inventory differs")
        if options.get("units") is not None:
            chosen = set(options["units"])
            units = [u for u in units if u["unit_id"] in chosen]
            if len(units) != len(chosen):
                raise ValueError("unknown rehearsal unit")
            expected = (len(units),sum(len(u["row_ids"]) for u in units))
        runtime_path = ROOT/"experiments/c4-three-threat-small-v1/runtime-files-v2.json"
        runtime = json.loads(runtime_path.read_text())
        if (runtime["python_prefix"] != execution["python_prefix"] or
            os.path.realpath(sys.executable) not in {entry["path"] for entry in runtime["files"]}):
            raise ValueError("running interpreter is outside the pinned runtime inventory")
        for entry in runtime["files"]:
            guard()
            if file_sha(host_path(entry["path"])) != entry["sha256"]:
                raise ValueError("pinned runtime changed: "+entry["path"])
        parent_runtime = json.loads((parent/"outputs/runtime.json").read_text())
        profile_path = ROOT/"experiments/c4-v4-three-threat-small-v1/profile.json"
        if (parent_runtime["runtime_inventory_sha256"] != file_sha(runtime_path) or
            parent_runtime["profile_sha256"] != file_sha(profile_path)):
            raise ValueError("inherited runtime/profile binding differs")
        import torch
        torch.manual_seed(execution["torch"]["manual_seed"])
        torch.use_deterministic_algorithms(execution["torch"]["deterministic_algorithms"])
        torch.set_num_threads(execution["torch"]["num_threads"])
        state["phase"] = "LOADING_CPU_EVALUATORS"
        log(event="loading",units=len(units),rows=expected[1],elapsed_seconds=time.monotonic()-started)
        if options.get("adapter") is not None:
            adapter = options["adapter"](parent,rows,guard)
            assets = {"rehearsal_fake_adapter":True}
        else:
            from v4_saved_evaluation_adapter import SavedEvaluation
            adapter = SavedEvaluation(parent,rows,host_path(lock["asset_root"]),profile_path,guard)
            assets = adapter.assets["files"]
        emit("runtime.json",{"run_id":run_id,"manifest_sha256":manifest_hash,"scientific_core_sha256":core_hash,
             "parent_results_sha256":lock["results_sha256"],"runtime_sha256":file_sha(runtime_path),
             "asset_files":assets,"execution":execution,"cuda_used":False,"no_generation":True,
             "scientific_acceptance":False,**marker})
        faulthandler.dump_traceback_later(600,repeat=True)
        for index,unit in enumerate(units,1):
            unit_start[0] = time.monotonic()
            state.update(unit=unit["unit_id"],phase="EVALUATING")
            def boundary(identity, phase):
                state.update(row=identity,phase=phase)
                guard()
            evaluate_units([unit],rows,journal,adapter,guard,boundary,boundary)
            state.update(last_sealed_unit=unit["unit_id"],phase="SEALED",sealed_units=index)
            log(event="sealed",unit=unit["unit_id"],index=index,of=len(units),
                unit_seconds=time.monotonic()-unit_start[0],elapsed_seconds=time.monotonic()-started)
        unit_start[0] = None
        interruptible[0] = False
        state["phase"] = COMPLETE
    except BaseException as error:
        interruptible[0] = False
        failure = {"type":type(error).__name__,"message":str(error),"unit":state.get("unit"),
                   "row":state.get("row"),"phase":state["phase"],"elapsed_seconds":time.monotonic()-started,
                   "signals":list(signals),"traceback":traceback.format_exc(),**marker}
        state["phase"] = FAILED
        # The cause reaches disk before anything slower can be interrupted.
        try:
            emit("failure.json",failure)
        except OSError:
            pass
        log(event="failed",type=failure["type"],message=failure["message"],phase=failure["phase"],
            unit=failure["unit"],row=failure["row"],traceback=failure["traceback"])
    faulthandler.cancel_dump_traceback_later()
    final_phase = state["phase"]
    if final_phase != COMPLETE and failure is None:
        failure = {"type":"RuntimeError","message":"evaluation ended without completion or a recorded failure",
                   "phase":final_phase,**marker}
        final_phase = FAILED
    if heartbeat_error and failure is None:
        failure = {"type":"OSError","message":heartbeat_error[0],**marker}
        final_phase = FAILED
    state["phase"] = "FINALISING"
    log(event="finalising",sealed_units=state["sealed_units"],elapsed_seconds=time.monotonic()-started)
    problems = []
    def step(name, action):
        try:
            return action()
        except Exception as problem:
            problems.append({"step":name,"type":type(problem).__name__,"message":str(problem)})
    # One summary for the whole run: it re-verifies every seal and dependency.
    integrity = step("results",lambda:write_results(emit,run_id,units,journal,started,failure,core,core_hash,
                                                    expected,baseline+journal.bytes+written[0],marker))
    if integrity and failure is None:
        failure = {"type":"ValueError","message":"final evidence integrity failed","integrity_errors":integrity,**marker}
        final_phase = FAILED
    if adapter is not None:
        step("adapter",adapter.close)
    stop.set()
    thread.join(10)
    if not (outputs/"runtime.json").exists():
        step("runtime",lambda:emit("runtime.json",{"run_id":run_id,"manifest_sha256":manifest_hash,
             "scientific_core_sha256":core_hash,"verification_incomplete":True,**marker}))
    if problems and failure is None:
        failure = {"type":"OSError","message":"final evidence could not be written","problems":problems,**marker}
        final_phase = FAILED
    if failure is not None:
        step("failure",lambda:emit("failure.json",{**failure,"finalisation_problems":problems}))
    state["phase"] = final_phase
    if thread.is_alive():
        problems.append({"step":"heartbeat","type":"TimeoutError","message":"heartbeat writer did not stop"})
    else:
        step("heartbeat",lambda:atomic_json(outputs/"heartbeat.json",
             {**state,"observed_at":datetime.now(timezone.utc).isoformat()}))
    def catalogue():
        files, errors = [], []
        for path in sorted(outputs.rglob("*")):
            if path.name == "artifact-index.json" or path.name.startswith(PENDING_PREFIX):
                continue
            try:
                if path.is_file():
                    files.append({"path":path.relative_to(output).as_posix(),"sha256":file_sha(path)})
            except OSError as problem:
                errors.append({"path":path.relative_to(output).as_posix(),"type":type(problem).__name__})
        atomic_json(outputs/"artifact-index.json",{"run_id":run_id,"manifest_sha256":manifest_hash,
                    "files":files,"errors":errors,**marker})
        if errors:
            raise OSError("artifact catalogue incomplete")
    step("catalogue",catalogue)
    for number,handler in previous.items():
        signal.signal(number,handler)
    log(event="finished",phase=final_phase,failure=None if failure is None else failure["type"],
        problems=problems,signals=list(signals),elapsed_seconds=time.monotonic()-started)
    return 1 if failure or problems else 0


def write_results(emit, run_id, units, journal, started, failure, core, core_hash, expected, counted, marker):
    summary = summarize_journal(units,journal,tolerate_corruption=True)
    complete = ((len(summary["sealed_units"]),len(summary["rows"])) == expected and len(units) == expected[0]
                and failure is None and not summary["integrity_errors"])
    verdict = ("REHEARSAL_SYNTHETIC_INPUT_NOT_EVIDENCE" if marker else
               "PENDING_ANALYSIS_AND_VISUAL_REVIEW_INCOMPLETE_ORIGINAL_CONTROLS")
    emit("results.json",{"run_id":run_id,**summary,
        "evaluation_phase_complete":complete,"whole_study_complete":False,"method_acceptance":False,
        "scientific_verdict":verdict,"scientific_core_sha256":core_hash,**core["accounting"],
        "expected_units":expected[0],"expected_rows":expected[1],"output_bytes_counted":counted,
        "journal_bytes":journal.bytes,
        "failure":failure,"elapsed_seconds":time.monotonic()-started,**marker})
    return summary["integrity_errors"]


def single_stream():
    """wsl.exe relays stdout and stderr into the one Windows log at separate offsets,
    so stderr output overwrites earlier lines. Send both through stdout."""
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(1,2)


if __name__ == "__main__":
    single_stream()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest,args.output_dir))

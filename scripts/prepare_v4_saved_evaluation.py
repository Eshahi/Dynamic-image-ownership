"""Read-only metadata builder: exact CPU evaluation and harmless host preflight.

Also the single definition of run identity, the fixed output roots and the
scientific-core hash, shared by the launcher, the worker and the rehearsal.
"""
import argparse
from datetime import datetime, timezone
import fnmatch
import json
from pathlib import Path
import re
import subprocess
from v4_evaluation_journal import file_sha, object_sha

ROOT = Path(__file__).resolve().parents[1]
EXP = "c4-v4-three-threat-recovery-v1"
PACKAGE = ROOT/"experiments"/EXP
CORE_FILE = "experiments/"+EXP+"/evaluation-core.json"
BUILD = "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build"
RUN_PATTERN = r"c4-v4-saved-evaluation-[0-9]{3}"
REHEARSAL_PATTERN = r"rehearsal-[a-z0-9]+(-[a-z0-9]+)*"
REHEARSAL_COMMIT = "0"*40
MAX_RERUNS = 2
PINNED = ("experiment_id","stage_id","task_id","execution_target","reviewed_script","seeds",
          "resources","budget","cleanup_policy","outputs","metrics")


def state():
    if subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain"],text=True).strip():
        raise ValueError("exact clean code commit required")
    return subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()


def core():
    """Hashed scientific constants and the core/harness file classification."""
    value = json.loads((ROOT/CORE_FILE).read_text())
    listed = value["core_inputs"]+value["harness_inputs"]
    if len(set(listed)) != len(listed) or CORE_FILE not in value["core_inputs"]:
        raise ValueError("core and harness inputs must be disjoint and self-binding")
    return value


def files():
    value = core()
    return sorted(value["core_inputs"]+value["harness_inputs"])


def datasets():
    return json.loads((PACKAGE/"experiment-spec.yaml").read_text())["datasets"]


def contract(manifest, rehearsal=False):
    """Fail closed unless the manifest is exactly one listed evaluation; returns the core."""
    value = core()
    run = manifest.get("run_id")
    if (not isinstance(run,str) or len(run) > 64 or
            not re.fullmatch(REHEARSAL_PATTERN if rehearsal else RUN_PATTERN,run)):
        raise ValueError("unlisted evaluation identity")
    for key in PINNED:
        if manifest.get(key) != value[key]:
            raise ValueError("evaluation contract differs: "+key)
    if manifest.get("datasets") != datasets():
        raise ValueError("evaluation contract differs: datasets")
    if [item["path"] for item in manifest["inputs"]] != files():
        raise ValueError("manifest input inventory differs")
    if (manifest["git_commit"] == REHEARSAL_COMMIT) != bool(rehearsal):
        raise ValueError("rehearsal manifests alone carry the null commit")
    # The official runner hashes without ASCII escaping; keep both digests equal.
    if not json.dumps(manifest,ensure_ascii=False).isascii():
        raise ValueError("ASCII-only manifest required")
    return value


def run_root(manifest, rehearsal=False):
    """The only output directory a run may use, as a Windows path string."""
    run = manifest["run_id"]
    if not isinstance(run,str) or not re.fullmatch(REHEARSAL_PATTERN if rehearsal else RUN_PATTERN,run):
        raise ValueError("unlisted evaluation identity")
    if rehearsal:
        return BUILD+"/rehearsal/"+run
    return BUILD+"/v4-recovery-runs/"+core()["stage_id"]+"/"+run


def core_record(manifest, definition=None):
    """Everything that can change a scientific number; excludes run id, commit and harness."""
    value = definition or core()
    paths = [item["path"] for item in manifest["inputs"]]
    if sorted(paths) != sorted(value["core_inputs"]+value["harness_inputs"]):
        raise ValueError("manifest inputs are not exactly core plus harness")
    listed = set(value["core_inputs"])
    record = {key:manifest[key] for key in ("experiment_id","stage_id","task_id","execution_target","seeds",
                                            "datasets","metrics","resources","budget","cleanup_policy")}
    record.update(definition=value["definition"],
                  inputs=sorted([item["path"],item["sha256"]] for item in manifest["inputs"] if item["path"] in listed))
    return record


def core_sha256(manifest, definition=None):
    return object_sha(core_record(manifest,definition))


def base(run, stage, script, budget, resources):
    spec = json.loads((ROOT/"experiments"/EXP/"experiment-spec.yaml").read_text())
    return {"schema_version":"1.0","experiment_id":EXP,"run_id":run,"stage_id":stage,"task_id":"C4",
            "execution_target":"local","reviewed_script":"scripts/"+script,
            "script_sha256":file_sha(ROOT/"scripts"/script),"git_commit":state(),"seeds":[0,1,2],
            "datasets":spec["datasets"],"inputs":[{"path":p,"sha256":file_sha(ROOT/p)} for p in files()],
            "budget":budget,"resources":resources,"cleanup_policy":"stop-for-recovery"}


def build_fixture():
    result = base("c4-v4-recovery-host-check-003","C4-v4-recovery-host-preflight","v4_host_fixture.py",
                  {"max_seconds":60,"max_usd":0,"hourly_usd":0},{"ram_mib":128,"vram_mib":0,"disk_mib":16})
    result.update(outputs=["outputs/fixture.json","outputs/survival.json"],metrics=["model_free_detached_official_runner_survival"])
    return result


def build(run_id, rehearsal=False):
    value = core()
    if not rehearsal:
        lock = json.loads((PACKAGE/"parent-input-lock.json").read_text())
        parent = Path(lock["parent_root"])
        for item in lock["artifacts"]:
            path = parent/item["path"]
            if not path.resolve().is_relative_to(parent.resolve()) or file_sha(path) != item["sha256"]:
                raise ValueError("parent artifact changed")
    result = {"schema_version":"1.0","run_id":run_id,**{key:value[key] for key in PINNED},
              "script_sha256":file_sha(ROOT/value["reviewed_script"]),
              "git_commit":REHEARSAL_COMMIT if rehearsal else state(),"datasets":datasets(),
              "inputs":[{"path":p,"sha256":file_sha(ROOT/p)} for p in files()]}
    contract(result,rehearsal)
    return result


def package_record(manifest):
    value = core()
    hashes = {item["path"]:item["sha256"] for item in manifest["inputs"]}
    return {"run_id":manifest["run_id"],"git_commit":manifest["git_commit"],"manifest_sha256":object_sha(manifest),
            "scientific_core_sha256":core_sha256(manifest),"max_infrastructure_reruns":MAX_RERUNS,
            "core_inputs":{p:hashes[p] for p in value["core_inputs"]},
            "harness_inputs":{p:hashes[p] for p in value["harness_inputs"]},
            "harness_only":value["harness_only"]}


def harness_path(path, definition):
    return path not in definition["core_inputs"] and (
        path in definition["harness_inputs"] or
        any(fnmatch.fnmatchcase(path,pattern) for pattern in definition["harness_only"]))


def attempt(directory):
    def load(name):
        path = directory/name
        return json.loads(path.read_text()) if path.is_file() else {}
    receipt, runtime, results, failure, heartbeat = (load(n) for n in
        ("manifest.json","outputs/runtime.json","outputs/results.json","outputs/failure.json","outputs/heartbeat.json"))
    age = None
    if heartbeat.get("observed_at"):
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(heartbeat["observed_at"])).total_seconds()
    return {"run_id":directory.name,"status":receipt.get("status"),"git_commit":receipt.get("git_commit"),
            "heartbeat_age_seconds":age,
            "scientific_core_sha256":runtime.get("scientific_core_sha256"),
            "evaluation_phase_complete":results.get("evaluation_phase_complete"),
            "sealed_units":len(results.get("sealed_units",[])),
            "failure_type":failure.get("type"),"failure_phase":failure.get("phase")}


def check_rerun(original, run_id):
    """Mechanical part of the infrastructure-only rerun allowance; a reviewer judges the rest.

    `original` is the run directory of the user-approved first attempt. The official
    runner's own files there are the anchor, not any record written by a preparer.
    """
    original = Path(original)
    reasons = []
    previous = json.loads((original/"execution-manifest.json").read_text())
    receipt = json.loads((original/"manifest.json").read_text())
    if object_sha(previous) != receipt.get("execution_manifest_sha256"):
        reasons.append("original receipt does not bind its execution manifest")
    commit = str(receipt.get("git_commit",""))
    definition = approved = None
    if not re.fullmatch(r"[a-f0-9]{40}",commit) or commit == REHEARSAL_COMMIT:
        reasons.append("original receipt has no approved commit")
    else:
        shown = subprocess.run(["git","-C",str(ROOT),"show",commit+":"+CORE_FILE],capture_output=True,text=True)
        if shown.returncode:
            reasons.append("approved commit has no scientific-core definition")
        else:
            definition = json.loads(shown.stdout)
            approved = core_sha256(previous,definition)
    candidate = build(run_id)
    current = core_sha256(candidate)
    if approved != current:
        reasons.append("scientific core differs from the approved one")
    changed = outside = []
    if definition is not None:
        changed = [p for p in subprocess.check_output(
            ["git","-C",str(ROOT),"diff","--name-only","--no-renames",commit,"HEAD"],text=True).splitlines() if p]
        outside = [p for p in changed if not harness_path(p,definition)]
        if outside:
            reasons.append("changed paths outside the approved harness list")
    attempts = [attempt(d) for d in sorted(original.parent.iterdir()) if d.is_dir()]
    attempts = [a for a in attempts if approved is not None and a["scientific_core_sha256"] == approved]
    if original.name not in [a["run_id"] for a in attempts]:
        reasons.append("original attempt does not record this scientific core")
    if any(a["status"] == "completed" or a["evaluation_phase_complete"] for a in attempts):
        reasons.append("an attempt with this scientific core already completed")
    # A stale running receipt without its process is not live execution; a fresh heartbeat is.
    if any(a["status"] == "running" and a["heartbeat_age_seconds"] is not None and
           a["heartbeat_age_seconds"] < 300 for a in attempts):
        reasons.append("an attempt with this scientific core is still live")
    if len(attempts) > MAX_RERUNS:
        reasons.append("both infrastructure-only reruns are already used")
    if (original.parent/run_id).exists():
        reasons.append("run id already used")
    return {"eligible":not reasons,"reasons":reasons,"approved_commit":commit,"approved_core_sha256":approved,
            "candidate_run_id":run_id,"candidate_commit":candidate["git_commit"],
            "candidate_manifest_sha256":object_sha(candidate),"candidate_core_sha256":current,
            "changed_paths":changed,"outside_harness_list":outside,"attempts":attempts,
            "rerun_ordinal":len(attempts),
            "reviewer_must_confirm":"latest failure is infrastructure, not scientific validation; evidence preserved and not reused"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture",action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--core",action="store_true",help="print the package record instead of the manifest")
    parser.add_argument("--check-rerun",metavar="ORIGINAL_RUN_DIR")
    args = parser.parse_args()
    if not args.fixture and not args.run_id:
        parser.error("--run-id is required")
    if args.check_rerun:
        result = check_rerun(args.check_rerun,args.run_id)
        print(json.dumps(result,sort_keys=True,indent=2))
        raise SystemExit(0 if result["eligible"] else 1)
    manifest = build_fixture() if args.fixture else build(args.run_id)
    print(json.dumps(package_record(manifest) if args.core else manifest,sort_keys=True,indent=2))

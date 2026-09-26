"""Read-only scientific-artifact verification and retained failed-run analysis.

No model, image decode, GPU, execution/retry or mutable source artifact writes.
Output is exclusive in a new analysis directory; original run stays untouched.
"""
import argparse
import hashlib
import json
from pathlib import Path

RUN = "c4-embedding-dev-001"
COMMIT = "1432fdfdaab8426c97ec81198c281b909f8a7e88"
DIGEST = "c311c6989809328e5c4c2583bce1355fafd1e00d7556a2542e23adce04809f86"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_bytes())
def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()


def summarize(root, repo):
    execution = read(root/"execution-manifest.json")
    record = read(root/"manifest.json")
    if (hashlib.sha256(canonical(execution)).hexdigest() != DIGEST or
        record["execution_manifest_sha256"] != DIGEST or record["run_id"] != RUN or
        record["git_commit"] != COMMIT or record["git_dirty"] is not False or
        record["status"] != "failed" or record["exit_status"] != 2):
        raise ValueError("exact retained failed C4 run required")
    for item in execution["inputs"]:
        if sha(repo/item["path"]) != item["sha256"]: raise ValueError("run input changed")
    if {item["path"] for item in record["output_artifacts"]} != set(execution["outputs"]):
        raise ValueError("declared output inventory incomplete")
    for item in record["output_artifacts"]:
        if sha(root/item["path"]) != item["sha256"]: raise ValueError("declared output digest mismatch")
    report = read(root/"outputs/c4-development.json")
    if report["status"] != "failed" or report["error_type"] != "OutOfMemoryError":
        raise ValueError("recorded failure differs")
    trials = list((root/"outputs").glob("c4-trial-*"))
    if len(trials) != 1: raise ValueError("one retained trial required")
    trial = trials[0]; failure = read(trial/"failed.json")
    rows = [json.loads(row) for row in (trial/"trajectory.jsonl").read_bytes().splitlines()]
    phases = [json.loads(row) for row in (root/"logs/c4-progress.jsonl").read_bytes().splitlines()]
    if (len(rows) != 1 or rows[0]["phase"] != "source_enrollment" or
            any(trial.glob("*.png")) or (trial/"pair.json").exists()):
        raise ValueError("unexpected optimization/output evidence; review separately")
    if sha(root/"checkpoints/source-snapshot.bin") != failure["source_raw_hash"]:
        raise ValueError("retained source snapshot changed")
    if failure["error_type"] != "OutOfMemoryError": raise ValueError("trial failure mismatch")
    resources = report["resources"]
    if resources["peak_torch_allocated_bytes"] > resources["torch_allocation_limit_bytes"]:
        raise ValueError("reported Torch allocation exceeded approved limit")
    selected = read(repo/"experiments/c4-embedding-development-v1/frozen-case.json")["selected"]
    if failure["source_id"] != selected["source_uid"] or failure["source_pixel_hash"] != selected["canonical_pixel_sha256"]:
        raise ValueError("source identity mismatch")
    retained = ["manifest.json","execution-manifest.json","summary.md","logs/process.log",
                *execution["outputs"], "checkpoints/source-snapshot.bin", "checkpoints/source-checked.json",
                "checkpoints/model-load.json", "checkpoints/c4-config-validation.json",
                *[str(p.relative_to(root)).replace("\\","/") for p in sorted(trial.iterdir()) if p.is_file()]]
    return {"schema_version":"c4-failed-run-analysis-v1", "run_id":RUN,
        "execution_manifest_sha256":DIGEST,"execution_commit":COMMIT,"status":"failed",
        "error_type":"OutOfMemoryError", "source_uid":failure["source_id"],
        "started_at":record["started_at"],"ended_at":record["ended_at"],
        "worker_failure_elapsed_seconds":phases[-1]["elapsed_seconds"],
        "last_completed_phase":"model_load_completed",
        "faulting_operation":"not_recorded_within_preupdate_optimization_path",
        "gradient_observations":0,"optimization_updates":0,"PNG_outputs":0,
        "gradient_norm":None,"quality":"NOT_RUN","blind_verification":"NOT_RUN",
        "scientific_acceptance":False,"retry_authorized":False,"resources":resources,
        "artifacts":[{"path":name,"bytes":(root/name).stat().st_size,"sha256":sha(root/name)} for name in retained]}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root",required=True,type=Path)
    parser.add_argument("--repo",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args(); result=summarize(args.run_root,args.repo)
    args.out.mkdir(parents=True,exist_ok=False)
    for name,value in (("failed-run-analysis.json",result),("metric-row.json",{
        "run_id":RUN,"seed":0,"condition":"fixed_mechanism_trial","status":"failed","gradient_norm":None})):
        with (args.out/name).open("x",encoding="utf-8",newline="\n") as handle:
            json.dump(value,handle,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False);handle.write("\n")
    print(json.dumps({"status":"failed_retained","gradient_observations":0,"PNG_outputs":0,
        "analysis_sha256":sha(args.out/"failed-run-analysis.json")}))

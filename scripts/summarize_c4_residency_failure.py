"""Read-only exact run002 failure verifier; no model/pixel/GPU or retry.

Only this retained outcome is supported. A changed/successful outcome blocks
rather than being silently relabeled. Output uses an exclusive new directory.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from scripts.summarize_c4_failed_run import checkout_bytes

RUN = "c4-embedding-dev-002"
COMMIT = "4db4f96453ddaba81ab5ec7b1978b354ed215066"
DIGEST = "a43ccae7b11a857fd213b79f9eaf1707cc8388151d58f5338fbe48e8157ab052"
PHASES = ["worker_started", "exact_inputs_checked", "source_and_resources_started",
          "source_and_resources_checked", "model_load_started", "model_load_completed",
          "idle_residency_started", "idle_residency_completed", "worker_failed"]

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_bytes())

def journal_evidence(rows):
    """Match nested observed operation boundaries, not asynchronous CUDA kernels."""
    if not rows or rows[0].get("phase") != "source_enrollment":
        raise ValueError("source enrollment must precede operations")
    stack, completed, resources = [], [], {}
    for row in rows[1:]:
        phase = row.get("phase")
        if phase in ("operation_started", "operation_completed"):
            token = {key: row[key] for key in ("operation", "iteration", "timestep") if key in row}
            if not isinstance(token.get("operation"), str) or not token["operation"]:
                raise ValueError("named operation required")
            if any(type(token[key]) is not int or token[key] < 0 for key in ("iteration", "timestep") if key in token):
                raise ValueError("integer operation context required; no bool aliases")
            if phase == "operation_started": stack.append(token)
            elif not stack or stack.pop() != token:
                raise ValueError("operation completion does not match its nested start")
            else: completed.append(token)
        elif phase in ("residency_resources_before_idle", "residency_resources_after_idle"):
            if stack or phase in resources:
                raise ValueError("resource record out of order or duplicate")
            resource = row["resources"]
            for field in ("current_torch_allocated_bytes", "current_torch_reserved_bytes"):
                if type(resource[field]) is not int or resource[field] < 0:
                    raise ValueError("integer measured resource bytes required")
            resources[phase] = resource
        else:
            raise ValueError("unexpected trajectory/gradient/update; review this outcome separately")
    if (stack != [{"operation": "optimization_render", "iteration": 0}, {"operation": "vae_decode"}] or
        sum(t["operation"] == "vae_decode" for t in completed) != 1 or
        sum(t["operation"] == "matched_control_render" for t in completed) != 1 or
        sum(t["operation"] == "idle_components_to_cpu" for t in completed) != 1 or
        list(resources) != ["residency_resources_before_idle", "residency_resources_after_idle"]):
        raise ValueError("exact observed residency/control/unfinished render boundaries required")
    before = resources["residency_resources_before_idle"]
    after = resources["residency_resources_after_idle"]
    return {"last_completed_operation": completed[-1], "unfinished_operation_stack": stack,
            "faulting_kernel": "unknown; CUDA errors may be asynchronous",
            "before_idle_allocated_bytes": before["current_torch_allocated_bytes"],
            "after_idle_allocated_bytes": after["current_torch_allocated_bytes"],
            "observed_idle_allocation_reduction_bytes": before["current_torch_allocated_bytes"]-after["current_torch_allocated_bytes"],
            "before_idle_reserved_bytes": before["current_torch_reserved_bytes"],
            "after_idle_reserved_bytes": after["current_torch_reserved_bytes"],
            "recorded_gradient_observations": 0, "recorded_optimization_updates": 0,
            "unrecorded_internal_progress": "unknown", "gradient_norm": None}

def summarize(root, repo):
    execution, record = read(root/"execution-manifest.json"), read(root/"manifest.json")
    if (hashlib.sha256(canonical(execution)).hexdigest() != DIGEST or
        record["execution_manifest_sha256"] != DIGEST or record["run_id"] != RUN or
        record["git_commit"] != COMMIT or record["git_dirty"] is not False or
        record["status"] != "failed" or record["exit_status"] != 2):
        raise ValueError("exact retained failed run002 required")
    if record["input_artifacts"] != execution["inputs"]:
        raise ValueError("runner input inventory differs from execution pins")
    original_case = None
    for item in execution["inputs"]:
        raw = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{COMMIT}:{item['path']}"],
                             check=True, capture_output=True).stdout
        raw = checkout_bytes(raw, item["path"], item["sha256"])
        if item["path"].endswith("/frozen-case.json"): original_case = json.loads(raw)
    artifacts = record["output_artifacts"]
    if len(artifacts) != len(execution["outputs"]) or {a["path"] for a in artifacts} != set(execution["outputs"]):
        raise ValueError("complete exact declared output inventory required")
    for item in artifacts:
        if sha(root/item["path"]) != item["sha256"]: raise ValueError("declared output hash mismatch")
    report = read(root/"outputs/c4-development.json")
    if report["status"] != "failed" or report["error_type"] != "OutOfMemoryError":
        raise ValueError("exact failure outcome required")
    phases = [json.loads(line) for line in (root/"logs/c4-progress.jsonl").read_bytes().splitlines()]
    if [p["phase"] for p in phases] != PHASES or phases[-1]["error_type"] != "OutOfMemoryError":
        raise ValueError("ordered failure phases differ")
    times = [p["elapsed_seconds"] for p in phases]
    if any(type(t) not in (int, float) or not math.isfinite(t) or t < 0 for t in times) or times != sorted(times):
        raise ValueError("ordered finite elapsed measurements required")
    trials = list((root/"outputs").glob("c4-trial-*"))
    if len(trials) != 1: raise ValueError("one retained trial required")
    trial = trials[0]
    failure = read(trial/"failed.json")
    if failure["error_type"] != "OutOfMemoryError" or any(trial.glob("*.png")) or (trial/"pair.json").exists():
        raise ValueError("unexpected output/failure outcome; review separately")
    selected = original_case["selected"]
    if (failure["source_id"] != selected["source_uid"] or
        failure["source_pixel_hash"] != selected["canonical_pixel_sha256"] or
        sha(root/"checkpoints/source-snapshot.bin") != failure["source_raw_hash"] or
        failure["source_raw_hash"] != selected["raw_sha256"]):
        raise ValueError("retained source differs from executed case")
    evidence = journal_evidence([json.loads(line) for line in (trial/"trajectory.jsonl").read_bytes().splitlines()])
    resource = report["resources"]
    if (resource["torch_allocation_limit_bytes"] != 8192*1024*1024 or
        resource["peak_torch_allocated_bytes"] > resource["torch_allocation_limit_bytes"]):
        raise ValueError("resource profile differs")
    retained = ["manifest.json", "execution-manifest.json", "summary.md", "logs/process.log",
                *execution["outputs"], "checkpoints/source-snapshot.bin", "checkpoints/source-checked.json",
                "checkpoints/model-load.json", "checkpoints/c4-config-validation.json",
                *[str(p.relative_to(root)).replace("\\", "/") for p in sorted(trial.iterdir()) if p.is_file()]]
    return {"schema_version": "c4-residency-failed-analysis-v1", "run_id": RUN,
            "execution_manifest_sha256": DIGEST, "execution_commit": COMMIT,
            "analysis_script_sha256": sha(Path(__file__)),
            "status": "failed", "error_type": "OutOfMemoryError", "source_uid": selected["source_uid"],
            "started_at": record["started_at"], "ended_at": record["ended_at"],
            "worker_failure_elapsed_seconds": times[-1], "last_completed_phase": phases[-2]["phase"],
            **evidence, "resources": resource, "PNG_outputs": 0, "quality": "NOT_RUN",
            "blind_verification": "NOT_RUN", "scientific_acceptance": False, "retry_authorized": False,
            "artifacts": [{"path": name, "bytes": (root/name).stat().st_size, "sha256": sha(root/name)} for name in retained]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run-root", "repo", "out"): parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    result = summarize(args.run_root, args.repo)
    args.out.mkdir(parents=True, exist_ok=False)
    metric = {"run_id": RUN, "seed": 0, "condition": "explicit_residency_trial", "status": "failed", "gradient_norm": None}
    for name, value in (("failed-run-analysis.json", result), ("metric-row.json", metric)):
        with (args.out/name).open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
    print(json.dumps({"status": "failed_retained", "analysis_sha256": sha(args.out/"failed-run-analysis.json"),
                      "observed_idle_allocation_reduction_bytes": result["observed_idle_allocation_reduction_bytes"]}))

if __name__ == "__main__": main()

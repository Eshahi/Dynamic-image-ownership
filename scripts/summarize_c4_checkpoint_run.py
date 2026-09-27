"""Verify retained run003 metadata/bytes only; no model, GPU, retry or scalar selection.

Two gradients are dependent observations. No within-trial scalar aggregation was
preregistered, so preserve both and do not manufacture a seed-level mean/CI.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from scripts.summarize_c4_failed_run import checkout_bytes

RUN = "c4-embedding-dev-003"
COMMIT = "0ac89f587554c27b4fd6b143f270a65770c6d11f"
DIGEST = "6681e972a7fb249e66d6cb31f0e0b09f4bc6e6e6890e45ce4df0cc4816d3156e"
RECORD_SHA = "e3b54a21cc594a6eacd445b2f6772ebf97ed0e579275cee20339e6c324c40539"
TRAJECTORY_SHA = "7b024cb2ce6bb5f8a11d5a39625d6882fc22842d0c7db30fa5ec80f5bb0507a7"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def read(path): return json.loads(path.read_bytes())


def journal_evidence(rows):
    """Require the exact completed forward/update/safety sequence, not replay-kernel parity."""
    expected = []
    def pair(op, **context):
        expected.extend([{"phase": p, "operation": op, **context}
                         for p in ("operation_started", "operation_completed")])
    def render(op, **context):
        expected.append({"phase": "operation_started", "operation": op, **context})
        pair("scheduler_add_noise")
        for step in (101, 1):
            pair("unet_forward", timestep=step); pair("scheduler_step", timestep=step)
        pair("vae_decode")
        expected.append({"phase": "operation_completed", "operation": op, **context})
    pair("idle_components_to_cpu")
    expected.append({"phase": "operation_started", "operation": "source_encoding"})
    pair("vae_encode")
    expected.append({"phase": "operation_completed", "operation": "source_encoding"})
    render("matched_control_render")
    for iteration in (0, 1):
        render("optimization_render", iteration=iteration)
        for op in ("objective", "backward_and_gradient_check", "optimizer_step", "perturbation_projection"):
            pair(op, iteration=iteration)
    render("final_render"); pair("final_objective")
    pair("active_components_to_cpu_and_safety_to_cuda")
    operations = [r for r in rows if r.get("phase") in ("operation_started", "operation_completed")]
    if operations != expected: raise ValueError("exact completed operation sequence differs")
    phases = [r["phase"] for r in rows]
    if (phases[0] != "source_enrollment" or
        phases.count("pre_update_loss_post_projection_norm") != 2 or phases.count("final") != 1 or
        phases.count("png_saved_before_safety") != 2 or phases.count("output_safety_completed") != 2):
        raise ValueError("required trajectory records differ")
    allowed = {"source_enrollment", "operation_started", "operation_completed",
               "residency_resources_before_idle", "residency_resources_after_idle",
               "residency_resources_before_safety", "pre_update_loss_post_projection_norm",
               "final", "png_saved_before_safety", "output_safety_completed"}
    if set(phases) - allowed: raise ValueError("unknown trajectory phase")
    updates = [r for r in rows if r["phase"] == "pre_update_loss_post_projection_norm"]
    if [r["iteration"] for r in updates] != [0, 1]: raise ValueError("two ordered updates required")
    for row in updates:
        if (type(row["gradient_norm"]) not in (int, float) or not math.isfinite(row["gradient_norm"])
            or row["gradient_norm"] <= 0): raise ValueError("finite nonzero gradient required")
        if not 0 <= row["perturbation_norm"] <= 0.01 + 1e-8: raise ValueError("projection bound exceeded")
    final = next(r for r in rows if r["phase"] == "final")
    if final["iteration"] != 2 or not 0 <= final["perturbation_norm"] <= 0.01 + 1e-8:
        raise ValueError("bounded final observation required")
    return {"gradient_observations": updates, "final_observation": final,
            "recorded_updates": 2, "recorded_gradient_observations": 2,
            "independent_trials": 1, "scalar_gradient_aggregation": "not_preregistered_not_computed",
            "confidence_interval": "none", "SD_checkpoint_numerical_parity": "NOT_PROVEN"}


def summarize(root, repo):
    if sha(root/"manifest.json") != RECORD_SHA: raise ValueError("retained runner record changed")
    execution, record = read(root/"execution-manifest.json"), read(root/"manifest.json")
    if (hashlib.sha256(canonical(execution)).hexdigest() != DIGEST or
        record["execution_manifest_sha256"] != DIGEST or record["run_id"] != RUN or
        record["git_commit"] != COMMIT or record["git_dirty"] is not False or
        record["status"] != "completed" or record["exit_status"] != 0 or
        record["input_artifacts"] != execution["inputs"] or len(execution["inputs"]) != 48):
        raise ValueError("exact retained completed run003 required")
    selected, asset_lock = None, None
    for item in execution["inputs"]:
        raw = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{COMMIT}:{item['path']}"],
                             check=True, capture_output=True).stdout
        raw = checkout_bytes(raw, item["path"], item["sha256"])
        if item["path"].endswith("/frozen-case.json"): selected = json.loads(raw)["selected"]
        if item["path"].endswith("/a6-candidate-model-assets.json"): asset_lock = json.loads(raw)
    if {a["path"] for a in record["output_artifacts"]} != set(execution["outputs"]) or len(record["output_artifacts"]) != 3:
        raise ValueError("complete declared output inventory required")
    for item in record["output_artifacts"]:
        if sha(root/item["path"]) != item["sha256"]: raise ValueError("declared output hash mismatch")
    report = read(root/"outputs/c4-development.json")
    if report["status"] != "completed_diagnostic_only" or report["scientific_acceptance"] is not False:
        raise ValueError("only diagnostic completion supported")
    result = report["result"]
    trial = root/"outputs"/result["trial_directory"]
    if trial.parent != root/"outputs" or not trial.name.startswith("c4-trial-"):
        raise ValueError("unsafe trial path")
    if report["selected_case"] != selected or sha(root/"checkpoints/source-snapshot.bin") != selected["raw_sha256"]:
        raise ValueError("source binding differs")
    if read(trial/"pair.json") != result["pair"] or (trial/"failed.json").exists():
        raise ValueError("retained pair/report mismatch")
    pair_rows = result["pair"]["rows"]
    if [r["kind"] for r in pair_rows] != ["matched_control", "marked_candidate"]:
        raise ValueError("one matched pair required")
    for row in pair_rows:
        name = row["output_path"]
        if name not in ("matched_control.png", "marked_candidate.png"): raise ValueError("unexpected PNG path")
        if (sha(trial/name) != row["output_hash"] or (trial/name).stat().st_size != row["output_bytes"] or
            row["source_raw_hash"] != selected["raw_sha256"] or row["safety_flagged"] is not False):
            raise ValueError("PNG custody/safety mismatch")
    if sha(trial/"trajectory.jsonl") != TRAJECTORY_SHA: raise ValueError("retained trajectory changed")
    rows = [json.loads(line) for line in (trial/"trajectory.jsonl").read_bytes().splitlines()]
    evidence = journal_evidence(rows)
    if [r["result"] for r in rows if r["phase"] == "output_safety_completed"] != pair_rows:
        raise ValueError("saved-pixel safety rows differ")
    snapshots = list((root/"checkpoints").glob("c4-sd-snapshot-*"))
    if len(snapshots) != 1: raise ValueError("one retained SD snapshot required")
    for entry in asset_lock["files"]:
        if entry["path"].startswith("sd15-fp16/"):
            path = snapshots[0]/entry["path"]
            if path.stat().st_size != entry["size_bytes"] or sha(path) != entry["sha256"]:
                raise ValueError("retained model snapshot changed")
    resource = result["resources"]
    if (resource["torch_allocation_limit_bytes"] != 9216*1024**2 or
        resource["peak_torch_allocated_bytes"] > resource["torch_allocation_limit_bytes"]):
        raise ValueError("allocation profile differs")
    phases = [json.loads(line) for line in (root/"logs/c4-progress.jsonl").read_bytes().splitlines()]
    if phases[-1]["phase"] != "worker_completed" or phases[-1]["elapsed_seconds"] > 1200:
        raise ValueError("terminal worker evidence absent/out of budget")
    retained = ["manifest.json", "execution-manifest.json", "summary.md", "logs/process.log",
                *execution["outputs"], "checkpoints/source-snapshot.bin", "checkpoints/source-checked.json",
                "checkpoints/model-load.json", "checkpoints/c4-config-validation.json",
                *[p.relative_to(root).as_posix() for p in sorted(trial.iterdir()) if p.is_file()]]
    return {"schema_version": "c4-checkpoint-retained-analysis-v1", "run_id": RUN,
            "execution_manifest_sha256": DIGEST, "execution_commit": COMMIT,
            "analysis_script_sha256": sha(Path(__file__)), "status": "completed_diagnostic_only",
            "source_uid": selected["source_uid"], "worker_seconds": phases[-1]["elapsed_seconds"],
            "started_at": record["started_at"], "ended_at": record["ended_at"], **evidence,
            "resources": resource, "PNG_outputs": 2, "quality": "NOT_RUN",
            "blind_verification": "NOT_RUN", "scientific_acceptance": False, "retry_authorized": False,
            "artifacts": [{"path": name, "bytes": (root/name).stat().st_size, "sha256": sha(root/name)} for name in retained]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run-root", "repo", "out"): parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    result = summarize(args.run_root, args.repo)
    args.out.mkdir(parents=True, exist_ok=False)
    with (args.out/"retained-run-analysis.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False); handle.write("\n")
    print(json.dumps({"status": result["status"], "analysis_sha256": sha(args.out/"retained-run-analysis.json"),
                      "gradients": [r["gradient_norm"] for r in result["gradient_observations"]]}))


if __name__ == "__main__": main()

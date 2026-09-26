"""Read-only descriptive C2 evidence replay; no model, tuning or inference."""
import argparse
import collections
import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def summary(values):
    return {"n": len(values), "mean": statistics.mean(values),
            "median": statistics.median(values),
            "sample_sd_descriptive_only": statistics.stdev(values) if len(values) > 1 else None,
            "min": min(values), "max": max(values)} if values else {"n": 0}


def selection(repo):
    config_raw = (repo / "configs/semantic-dev.json").read_bytes()
    config = json.loads(config_raw)
    for path, pin in (("source_manifest", "manifest_sha256"), ("development_ids", "development_ids_sha256"), ("splits", "splits_sha256")):
        if digest((repo / config[path]).read_bytes()) != config[pin]:
            raise ValueError("metadata pin mismatch")
    uid = lambda row: ":".join(row[k] for k in ("domain", "release_id", "source_split", "source_id"))
    reserved = json.loads((repo/config["development_ids"]).read_bytes())["images"]
    with (repo/config["splits"]).open(newline="") as handle:
        splits = {row["source_uid"]: row for row in csv.DictReader(handle)}
    if len(reserved) != 32 or len({uid(row) for row in reserved}) != 32:
        raise ValueError("reservation cardinality")
    for row in reserved:
        entry = splits[uid(row)]
        if entry["study_split"] != "development" or entry["canonical_status"] != "canonical_pass" or entry["raw_sha256"] != row["raw_sha256"]:
            raise ValueError("nondevelopment or unbound image")
    return digest(config_raw), [(uid(row), row, splits[uid(row)], None) for row in sorted(reserved, key=uid)]


def analyze(root, repo):
    root, repo = Path(root), Path(repo)
    manifest_raw = (root / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    execution_raw = (root / "execution-manifest.json").read_bytes()
    execution = json.loads(execution_raw)
    if (manifest["run_id"] != "c2-semantic-dev-001" or
            manifest["experiment_id"] != "c2-semantic-development-v1" or
            manifest["execution_target"] != "local" or manifest["seeds"] != [0] or
            manifest["git_dirty"] or manifest["execution_manifest_sha256"] != digest(canonical(execution))):
        raise ValueError("unexpected run or execution binding")
    for item in manifest["input_artifacts"]:
        if digest((repo / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError("changed prospective input: " + item["path"])
    outputs = {item["path"]: item["sha256"] for item in manifest["output_artifacts"]}
    required = {"outputs/semantic-examples.json", "logs/case-progress.jsonl"}
    if set(outputs) != required:
        raise ValueError("missing declared evidence")
    for name, expected in outputs.items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError("output digest mismatch")
    report = json.loads((root / "outputs/semantic-examples.json").read_bytes())
    events = [json.loads(line) for line in (root / "logs/case-progress.jsonl").read_text().splitlines()]
    if not events or events[0].get("event") != "prospective_inventory":
        raise ValueError("missing prospective inventory")
    # Uses only tracked metadata, never raw images or model weights.
    from scripts.c2_dev_probe import planned_cases
    config_hash, selected = selection(repo)
    planned = planned_cases(selected)
    if len(planned) != 96 or events[0]["cases"] != planned:
        raise ValueError("case identities/pairs differ from original32 recipe")
    replay = {row["case_id"]: dict(row, config_hash=config_hash) for row in planned}
    for event in events[1:]:
        key = event["case_id"]
        if key not in replay or replay[key]["status"] != "pending":
            raise ValueError("unexpected or duplicate terminal event")
        if event["status"] not in ("completed", "failed"):
            raise ValueError("nonterminal progress event")
        for field in ("image_id", "paired_image_id", "transform", "config_hash"):
            if event[field] != replay[key][field]:
                raise ValueError("rewritten case identity")
        replay[key] = event
    cases = list(replay.values())
    completed = [row for row in cases if row["status"] == "completed"]
    failed = [row for row in cases if row["status"] == "failed"]
    pending = [row for row in cases if row["status"] == "pending"]
    if (report["cases"] != cases or report["examples"] != completed or report["failures"] != failed or
            report["pending_cases"] != len(pending) or report["planned_cases"] != 96 or
            report["config_hash"] != config_hash or not report["development_only"] or
            not report["no_threshold_selection"] or report["scientific_method_success"]):
        raise ValueError("report differs from durable journal or scope")
    for row in completed:
        for metric, lower, upper in (("feature_distance", -1e-5, 2.00001),
                                     ("semantic_code_distance", 0, 12), ("key_distance", 0, 256)):
            value = row[metric]
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not lower <= value <= upper:
                raise ValueError("invalid metric")
            if metric != "feature_distance" and not isinstance(value, int):
                raise ValueError("noninteger Hamming distance")
        if (row["semantic_code_distance"] == 0) != (row["key_distance"] == 0):
            raise ValueError("q/Ws equality inconsistency in observed cases")
    groups = {}
    for condition in ("same_image_uncached_repeat", "jpeg_quality95_subsampling0", "different_content"):
        rows = [r for r in completed if r["transform"] == condition]
        groups[condition] = {
            "completed_cases": len(rows),
            "q_histogram": dict(sorted(collections.Counter(r["semantic_code_distance"] for r in rows).items())),
            "q_unchanged_count": sum(r["semantic_code_distance"] == 0 for r in rows),
            "metrics": {key: summary([r[key] for r in rows]) for key in
                        ("feature_distance", "semantic_code_distance", "key_distance")},
            "by_domain": {domain: {"cases": len(part), "q_unchanged": sum(r["semantic_code_distance"] == 0 for r in part)}
                          for domain in sorted({r["image_id"].split(":")[0] for r in rows})
                          for part in [[r for r in rows if r["image_id"].split(":")[0] == domain]]}}
    repeat = [r for r in completed if r["transform"] == "same_image_uncached_repeat"]
    mismatches = [r["case_id"] for r in repeat if not r.get("exact_features_equal") or r["semantic_code_distance"] != 0]
    return {"schema_version": "c2-descriptive-analysis-v1", "run_id": manifest["run_id"],
            "run_status": manifest["status"], "report_status": report["status"],
            "planned": 96, "completed": len(completed), "failed": failed, "pending": pending,
            "same_image_mismatches": mismatches, "conditions": groups,
            "jpeg_drift_cases": [r for r in completed if r["transform"] == "jpeg_quality95_subsampling0" and r["semantic_code_distance"]],
            "different_content_collision_cases": [r for r in completed if r["transform"] == "different_content" and not r["semantic_code_distance"]],
            "worker_elapsed_seconds": report.get("elapsed_seconds"),
            "peak_torch_allocated_bytes": report.get("peak_torch_allocated_bytes"),
            "independent_runs": 1, "independent_images_not_asserted": 32,
            "no_inferential_statistics": True, "no_threshold_selection": True,
            "limitations": ["Descriptive summaries chosen after results; not a new confirmatory analysis rule.",
                            "96 dependent cases from32 development images, one fixed seed/run; no CI, p-value or population claim.",
                            "Feature distance is the recorded1-dot product of approximately unit float32 features; tiny negative repeat values are retained, not clamped.",
                            "Ws digest Hamming distance is not semantic similarity; no held-out method/robustness/legal claim."],
            "provenance": {"git_commit": manifest["git_commit"], "execution_manifest_sha256": manifest["execution_manifest_sha256"],
                           "approval_reference": manifest["approval_reference"], "runner_manifest_sha256": digest(manifest_raw),
                           "output_hashes": outputs, "analysis_script_sha256": digest(Path(__file__).read_bytes()),
                           "prospective_spec_sha256": digest((repo / "experiments/c2-semantic-development-v1/experiment-spec.yaml").read_bytes())}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--copy-report", type=Path)
    args = parser.parse_args()
    result = analyze(args.artifacts, args.repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    if args.copy_report:
        # Verbatim mechanical publication of the verified report, never reconstructed cases.
        args.copy_report.write_bytes((args.artifacts / "outputs/semantic-examples.json").read_bytes())
    print(json.dumps({"completed": result["completed"], "failed": len(result["failed"]),
                      "pending": len(result["pending"]), "output": str(args.output)}))

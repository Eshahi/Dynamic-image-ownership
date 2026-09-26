"""Preview-only exact clean C4 manifest builder. No model/data load or approval."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import worker, validation_bridge


def build(root=ROOT):
    root = root.resolve()
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                            check=True, capture_output=True, text=True)
    if status.stdout.strip(): raise ValueError("manifest requires exact clean checkout")
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            check=True, capture_output=True, text=True).stdout.strip()
    names = sorted(worker.REQUIRED | validation_bridge.REQUIRED)
    for name in names:
        subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", name],
                       check=True, capture_output=True)
    spec = json.loads((root/"experiments/c4-embedding-development-v1/experiment-spec.yaml").read_bytes())
    manifest = {"schema_version": "1.0", "experiment_id": spec["experiment_id"],
        "run_id": "c4-embedding-dev-001", "stage_id": "C4-development", "task_id": "C4",
        "execution_target": "local", "reviewed_script": worker.SCRIPT,
        "script_sha256": hashlib.sha256((root/worker.SCRIPT).read_bytes()).hexdigest(),
        "git_commit": commit, "seeds": [0], "datasets": spec["datasets"],
        "inputs": [{"path": name, "sha256": hashlib.sha256((root/name).read_bytes()).hexdigest()} for name in names],
        "outputs": worker.OUTPUTS, "metrics": ["gradient_norm", "u_norm",
            "peak_torch_allocated_bytes", "peak_worker_rss_bytes"],
        "budget": worker.BUDGET, "resources": worker.RESOURCES, "cleanup_policy": "stop-for-recovery"}
    checked, snapshots, _ = validation_bridge.check_inputs(json.dumps(manifest).encode(), root)
    worker.check_recipe(checked, snapshots)
    return manifest


def write_manifest(path, manifest):
    path = path.absolute()
    validation_bridge._no_links(path)
    # Never dirty the approved checkout or permit a circular manifest input.
    if path.is_relative_to(ROOT): raise ValueError("manifest must be outside checkout")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    return hashlib.sha256(validation_bridge._json(manifest)).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(); manifest = build()
    digest = write_manifest(args.output, manifest)
    print(json.dumps({"manifest_sha256": digest, "git_commit": manifest["git_commit"],
                      "approval": "not_requested_or_granted"}))

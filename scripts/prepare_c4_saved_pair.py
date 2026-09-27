"""Build exact clean saved-pair manifest only; cannot grant/execute approval."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import quality_package as package


def build(root=ROOT):
    root = package.unlinked(root.resolve())
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    if git("status", "--porcelain"): raise ValueError("exact clean checkout required")
    for name in package.REQUIRED: git("ls-files", "--error-unmatch", "--", name)
    snapshots = {name: package.read(root/name) for name in package.REQUIRED}
    spec = json.loads(snapshots[package.SPEC+"/experiment-spec.yaml"])
    manifest = {"schema_version": "1.0", "experiment_id": package.EXPERIMENT,
        "run_id": package.RUN, "stage_id": "C4-quality-development", "task_id": "C4",
        "execution_target": "local", "reviewed_script": package.SCRIPT,
        "script_sha256": package.sha(snapshots[package.SCRIPT]), "git_commit": git("rev-parse", "HEAD"),
        "seeds": [0], "datasets": spec["datasets"], "outputs": package.OUTPUTS,
        "metrics": package.METRICS, "budget": package.BUDGET, "resources": package.RESOURCES,
        "cleanup_policy": "stop-for-recovery", "inputs": [{"path": name,
        "sha256": package.sha(snapshots[name])} for name in sorted(package.REQUIRED)]}
    package.inputs(package.canonical(manifest), root)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    target = package.unlinked(args.output.absolute())
    if target.is_relative_to(ROOT): raise ValueError("external manifest required")
    manifest = build()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream: stream.write(package.canonical(manifest))
    print(json.dumps({"manifest_sha256": package.sha(package.canonical(manifest)),
                      "git_commit": manifest["git_commit"], "approval": "not_requested_or_granted"}))

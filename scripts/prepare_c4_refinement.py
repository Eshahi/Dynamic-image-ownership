"""Build a clean external exact manifest; never execute or create approval."""
import argparse
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import refinement_package as package
from src.embedding.quality_package import canonical, sha, read, unlinked, strict_json_bytes


def build(root=ROOT):
    root = unlinked(root.resolve())
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    if git("status", "--porcelain"): raise ValueError("clean commit required")
    for name in package.REQUIRED: git("ls-files", "--error-unmatch", "--", name)
    snapshots = {name: read(root/name) for name in package.REQUIRED}
    spec = strict_json_bytes(snapshots[package.SPEC+"/experiment-spec.yaml"])
    manifest = {"schema_version": "1.0", "experiment_id": package.EXPERIMENT, "run_id": package.RUN,
        "stage_id": package.STAGE, "task_id": "C4", "execution_target": "local", "seeds": [0],
        "git_commit": git("rev-parse", "HEAD"), "reviewed_script": package.SCRIPT,
        "script_sha256": sha(snapshots[package.SCRIPT]), "datasets": spec["datasets"],
        "outputs": package.OUTPUTS, "metrics": package.METRICS, "budget": package.BUDGET,
        "resources": package.RESOURCES, "cleanup_policy": "stop-for-recovery",
        "inputs": [{"path": name, "sha256": sha(snapshots[name])} for name in sorted(package.REQUIRED)]}
    package.inputs(canonical(manifest), root)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(); target = unlinked(args.output.absolute())
    if target.is_relative_to(ROOT): raise ValueError("external manifest required")
    result = build(); target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream: stream.write(canonical(result))
    print(canonical({"manifest_sha256": sha(canonical(result)), "git_commit": result["git_commit"],
                     "approval": "not_requested_or_granted"}).decode())

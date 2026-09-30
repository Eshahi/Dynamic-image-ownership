"""Metadata-only exact manifest builder; never creates approval or runs images."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXP = "c4-three-threat-small-v1"
RUN = "c4-three-threat-small-dev-001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build():
    if subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True).strip():
        raise ValueError("exact manifest requires a clean committed checkout")
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    package = ROOT / "experiments" / EXP
    spec = json.loads((package / "experiment-spec.yaml").read_text())
    original = json.loads((ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json").read_text())["cases"]
    extra = json.loads((package / "development-expansion.json").read_text())["new_cases"]
    for row in original + extra:
        if sha(row["path"]) != row["raw_sha256"]:
            raise ValueError("reserved raw bytes changed")
    scripts = ["revised_watermark.py", "qim_rgb_pilot.py", "a6_clip_visual.py", "verify_science_assets.py",
               "check_a6_lpips_assets.py", "three_threat_protocol.py", "three_threat_models.py",
               "three_threat_worker.py", "run_three_threat_study.py", "freeze_three_threat_runtime.py",
               "prepare_three_threat_study.py", "test_three_threat_protocol.py", "test_three_threat_models.py",
               "test_three_threat_launcher.py"]
    files = ["scripts/" + name for name in scripts]
    files += ["configs/revised-watermark.example.json", "configs/revised-watermark.schema.json",
              "research/a6-candidate-model-assets.json", "research/proposal-aligned-plan-20260930.md",
              "experiments/c4-qim-rgb-development-v1/cohort.json"]
    files += [path.relative_to(ROOT).as_posix() for path in package.iterdir() if path.is_file()]
    return {"schema_version": "1.0", "experiment_id": EXP, "run_id": RUN,
            "stage_id": "C4-three-threat-development", "task_id": "C4", "execution_target": "local",
            "reviewed_script": "scripts/run_three_threat_study.py",
            "script_sha256": sha(ROOT / "scripts/run_three_threat_study.py"), "git_commit": commit,
            "seeds": [0, 1, 2], "datasets": spec["datasets"],
            "inputs": [{"path": path, "sha256": sha(ROOT / path)} for path in sorted(set(files))],
            "outputs": ["outputs/results.json", "outputs/runtime.json", "logs/study-worker.log"],
            "metrics": ["clean_quality_psnr_ssim_lpips", "intended_wrong_owner_detection",
                        "transfer_false_attribution", "regeneration_retention_survival",
                        "semantic_binding_distance"],
            "budget": {"max_seconds": 86400, "max_usd": 0, "hourly_usd": 0},
            "resources": {"vram_mib": 8192, "ram_mib": 8192, "disk_mib": 2048},
            "cleanup_policy": "stop-for-recovery"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = build()
    destination = Path(args.out)
    if destination.resolve().is_relative_to(ROOT):
        raise ValueError("retain manifest outside clean checkout")
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    print(json.dumps({"manifest_sha256": hashlib.sha256(canonical).hexdigest(),
                      "git_commit": manifest["git_commit"], "run_id": RUN, "execute": False}))

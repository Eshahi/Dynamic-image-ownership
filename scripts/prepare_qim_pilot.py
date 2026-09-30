"""Metadata-only freeze/builder; never decodes source images or executes codec."""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = "c4-qim-rgb-development-v1"
CASE_IDS = [6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768]
STABLE = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--freeze-cohort", action="store_true")
    args = parser.parse_args()
    package = ROOT / "experiments" / EXP
    reservation = json.loads((package / "development-reservation.json").read_text())
    selected = {int(row["source_id"]): row for row in reservation["images"] if row["domain"] == "ms-coco"}
    if sorted(selected) != CASE_IDS:
        raise ValueError("reservation differs from fixed ten-source development census")
    with (package / "source-manifest.csv").open(encoding="utf-8", newline="") as stream:
        rows = {int(row["source_id"]): row for row in csv.DictReader(stream) if row["domain"] == "ms-coco"}
    cases = []
    for identity in CASE_IDS:
        row = rows[identity]
        if row["raw_sha256"] != selected[identity]["raw_sha256"] or row["relative_path"] != selected[identity]["relative_path"]:
            raise ValueError("reservation/admission disagree")
        path = STABLE / "data/raw" / row["relative_path"]
        if sha(path) != row["raw_sha256"]:
            raise ValueError("source bytes mismatch")
        cases.append({"source_id": identity, "path": path.as_posix(), "raw_sha256": row["raw_sha256"], "width": int(row["width"]), "height": int(row["height"]), "license_reference": row["license_reference"], "rights_status": row["rights_status"], "use_limitations": row["use_limitations"]})
    cohort = {"cases": cases, "selection": "all ten reserved COCO development sources, numeric order", "independent_confirmatory_sample": False}
    if args.freeze_cohort:
        if (package / "cohort.json").exists():
            raise ValueError("cohort already frozen")
        write(package / "cohort.json", cohort)
    elif json.loads((package / "cohort.json").read_text()) != cohort:
        raise ValueError("frozen cohort differs from metadata/bytes")
    files = ["scripts/revised_watermark.py", "scripts/qim_rgb_pilot.py", "scripts/run_qim_rgb_pilot.py", "scripts/prepare_qim_pilot.py", "scripts/test_qim_rgb_pilot.py", "configs/revised-watermark.example.json", "configs/revised-watermark.schema.json", "research/method-amendment-v2.md", "research/method-amendment-decision-20260929.md"]
    files += [path.relative_to(ROOT).as_posix() for path in sorted(package.iterdir()) if path.is_file()]
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    spec = json.loads((package / "experiment-spec.yaml").read_text())
    manifest = {"schema_version": "1.0", "experiment_id": EXP, "run_id": "c4-qim-rgb-dev-001", "stage_id": "C4-QIM-RGB-development", "task_id": "C4", "execution_target": "local", "reviewed_script": "scripts/run_qim_rgb_pilot.py", "script_sha256": sha(ROOT / "scripts/run_qim_rgb_pilot.py"), "git_commit": commit, "seeds": [0], "datasets": spec["datasets"], "inputs": [{"path": path, "sha256": sha(ROOT / path)} for path in sorted(set(files))], "outputs": ["outputs/results.json", "outputs/runtime.json", "logs/cpu-worker.log"], "metrics": ["native_c1_detection", "native_c0_false_positive", "native_c2_false_positive", "psnr_db", "ssim_rgb", "attack_c1_detection", "attack_c0_false_positive"], "budget": {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0}, "resources": {"vram_mib": 0, "ram_mib": 4096, "disk_mib": 512}, "cleanup_policy": "stop-for-recovery"}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    write(out / "execution-manifest.json", manifest)
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    print(json.dumps({"manifest_sha256": digest, "git_commit": commit, "cases": len(cases), "out": str(out)}))


if __name__ == "__main__":
    main()

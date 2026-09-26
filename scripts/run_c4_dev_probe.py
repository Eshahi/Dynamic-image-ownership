"""Official-runner-only Windows parent for one bounded offline C4 WSL child.

No approval creation, execute toggle or alternate command/target supported.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding.validation_bridge import check_inputs, write_validation_receipt, _read, _no_links
from src.embedding.development_case import validate_frozen_case
from src.embedding.worker import check_recipe, CASE


def linux_path(path):
    value = str(Path(path).absolute()).replace("\\", "/")
    if not re.fullmatch(r"[A-Za-z]:/.*", value) or "\x00" in value:
        raise ValueError("absolute Windows drive path required")
    return "/mnt/"+value[0].lower()+value[2:]


def command(manifest_path, output_path):
    return ["C:/Windows/System32/wsl.exe", "-d", "Ubuntu", "--cd", linux_path(ROOT), "--",
        "/usr/bin/timeout", "--signal=TERM", "--kill-after=10s", "1140s",
        "/usr/bin/env", "-i", "PYTHONNOUSERSITE=1", "HF_HUB_OFFLINE=1",
        "TRANSFORMERS_OFFLINE=1", "DIFFUSERS_OFFLINE=1", "CUBLAS_WORKSPACE_CONFIG=:4096:8",
        "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python", "scripts/c4_dev_probe.py",
        "--manifest", linux_path(manifest_path), "--output-dir", linux_path(output_path)]


def launch(manifest_path, output_path):
    manifest_path, output_path = _no_links(Path(manifest_path)), _no_links(Path(output_path))
    # Path conversion before receipt generation; reject Linux/UNC aliases.
    args = command(manifest_path, output_path)
    journal = output_path/"logs/c4-launcher.jsonl"
    _no_links(journal)
    start = time.monotonic()
    with journal.open("xb") as handle:
        def record(**row):
            row["elapsed_seconds"] = time.monotonic()-start
            handle.write(json.dumps(row, sort_keys=True).encode()+b"\n")
            handle.flush(); os.fsync(handle.fileno())
        record(phase="launcher_started", authority="official-runner-only-no-approval-here")
        try:
            manifest, snapshots, _ = check_inputs(_read(manifest_path), ROOT)
            check_recipe(manifest, snapshots)
            validate_frozen_case(ROOT, snapshots[CASE])
            write_validation_receipt(manifest_path, output_path/"checkpoints", root=ROOT)
            remaining = 1190-(time.monotonic()-start)
            # Child's 1140s+10s escalation must precede remaining parent cap.
            if remaining < 1160: raise TimeoutError("parent validation consumed startup allowance")
            record(phase="full_C1_validation_completed_child_starting", child_timeout_seconds=1140,
                   child_kill_after_seconds=10, parent_remaining_seconds=remaining)
            result = subprocess.run(args, check=False, timeout=remaining)
            record(phase="child_exited", returncode=result.returncode)
            return result.returncode
        except Exception as error:
            record(phase="launcher_failed", error_type=type(error).__name__)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(launch(args.manifest, args.output_dir))

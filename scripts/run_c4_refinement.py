"""Official-runner-only bounded Windows refined-target launcher."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import refinement_package as package
from src.embedding.quality_package import unlinked, read, canonical
from src.embedding.validation_bridge import write_validation_receipt
from scripts.run_c4_saved_pair import linux_path


def command(manifest, output):
    return ["C:/Windows/System32/wsl.exe", "-d", "Ubuntu", "--cd", linux_path(ROOT), "--",
        "/usr/bin/timeout", "--signal=TERM", "--kill-after=10s", "1140s", "/usr/bin/env", "-i",
        "PYTHONNOUSERSITE=1", "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1", "DIFFUSERS_OFFLINE=1",
        "CUBLAS_WORKSPACE_CONFIG=:4096:8", "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python",
        package.CHILD, "--manifest", linux_path(manifest), "--output-dir", linux_path(output)]


def launch(manifest, output):
    manifest, output = unlinked(manifest), unlinked(output)
    args = command(manifest, output); started = time.monotonic()
    with unlinked(output/"logs/refinement-launcher.jsonl").open("xb") as journal:
        def record(**row):
            journal.write(canonical({"elapsed_seconds": time.monotonic()-started, **row})+b"\n")
            journal.flush(); os.fsync(journal.fileno())
        record(phase="launcher_started", authority="official-runner-only")
        try:
            package.inputs(read(manifest), ROOT)
            write_validation_receipt(manifest, output/"checkpoints", root=ROOT)
            remaining = 1190-(time.monotonic()-started)
            if remaining < 1160: raise TimeoutError("validation consumed startup allowance")
            record(phase="validated_child_starting", child_seconds=1140, kill_after_seconds=10)
            result = subprocess.run(args, timeout=remaining, check=False)
            record(phase="child_exited", returncode=result.returncode)
            return result.returncode
        except Exception as error:
            record(phase="failed", error_type=type(error).__name__); raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(); raise SystemExit(launch(args.manifest, args.output_dir))

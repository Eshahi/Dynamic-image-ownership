"""Read-only, allowlisted environment inventory for A6; no model execution."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGES = (
    "accelerate", "diffusers", "jsonschema", "lpips", "numpy", "Pillow",
    "PyYAML", "safetensors", "scikit-image", "scipy", "specify-cli",
    "thesis-agent-skills", "torch", "torchvision", "transformers",
)


def parse_gpus(raw: str) -> list[dict[str, object]]:
    devices = []
    for row in csv.reader(io.StringIO(raw)):
        if len(row) != 6:
            raise ValueError("unexpected nvidia-smi CSV shape")
        index, name, driver, total, free, capability = (field.strip() for field in row)
        if not name or not driver or not capability:
            raise ValueError("missing GPU identity")
        device = {
            "index": int(index), "name": name, "driver": driver,
            "total_mib": int(total), "free_mib": int(free),
            "compute_capability": capability,
        }
        if device["index"] < 0 or not 0 <= device["free_mib"] <= device["total_mib"]:
            raise ValueError("invalid GPU memory or index")
        devices.append(device)
    if not devices:
        raise ValueError("nvidia-smi returned no devices")
    return devices


def gpu_snapshot() -> dict[str, object]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return {"status": "nvidia-smi-not-found", "devices": []}
    try:
        result = subprocess.run(
            [executable, "--query-gpu=index,name,driver_version,memory.total,memory.free,compute_cap",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        if result.returncode != 0:
            return {"status": "nvidia-smi-failed", "devices": []}
        return {"status": "observed", "devices": parse_gpus(result.stdout)}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {"status": "nvidia-smi-failed", "devices": []}


def git_output(project: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *args], capture_output=True,
            text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def capture(project: Path) -> dict[str, object]:
    project = project.resolve()
    lock = project / "requirements.lock"
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    dirty = git_output(project, "status", "--porcelain", "--untracked-files=normal")
    return {
        "schema_version": "1.0",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "git_commit": git_output(project, "rev-parse", "HEAD"),
        "git_dirty": None if dirty is None else bool(dirty),
        "requirements_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None,
        "packages": versions,
        "gpu": gpu_snapshot(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(capture(args.project), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

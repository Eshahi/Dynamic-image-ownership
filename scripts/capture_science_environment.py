"""Read-only A6 science-venv receipt; no model import, weights or network."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

from capture_environment import git_output, gpu_snapshot


LOCK_FILES = (
    "requirements.lock",
    "requirements-science-stage2.txt",
    "requirements-science-stage2-win312-hashes.txt",
    "requirements-science-lpips-win312-hashes.txt",
    "requirements-science-clip.txt",
    "research/a6-candidate-model-assets.json",
)


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def distribution_versions(distributions: object | None = None) -> dict[str, str]:
    source = importlib.metadata.distributions() if distributions is None else distributions
    versions: dict[str, str] = {}
    for dist in source:
        name = dist.metadata.get("Name")
        if not name or not dist.version:
            raise ValueError("installed distribution lacks name or version")
        key = canonical(name)
        if key in versions:
            raise ValueError(f"duplicate installed distribution: {key}")
        versions[key] = dist.version
    return dict(sorted(versions.items()))


def lock_digests(project: Path) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for relative in LOCK_FILES:
        path = project / relative
        if path.is_symlink() or path.is_junction():
            raise ValueError(f"linked lock file: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def capture(project: Path) -> dict[str, object]:
    project = project.resolve()
    dirty = git_output(project, "status", "--porcelain", "--untracked-files=normal")
    return {
        "schema_version": "a6-science-environment-v1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_output(project, "rev-parse", "HEAD"),
        "git_dirty": None if dirty is None else bool(dirty),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "lock_sha256": lock_digests(project),
        "installed_distributions": distribution_versions(),
        "gpu": gpu_snapshot(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(capture(args.project), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

"""Read-only A6 installed-distribution versus cached-wheel inventory.

This is not a complete environment lock: VCS sources, bootstrap packages,
uncached wheels, model bytes and runtime numerical behavior remain separate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import zipfile
from email.parser import BytesParser
from pathlib import Path


LOCK_LINE = re.compile(
    r"^([A-Za-z0-9_.-]+)==([^\s]+)\s+--hash=sha256:([0-9a-f]{64})$"
)


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def parse_lock(text: str) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LOCK_LINE.fullmatch(line)
        if not match:
            raise ValueError(f"unsupported lock line: {line[:100]}")
        key = canonical(match[1]), match[2]
        if key in result:
            raise ValueError(f"duplicate locked distribution: {key}")
        result[key] = match[3]
    if not result:
        raise ValueError("empty distribution lock")
    return result


def wheel_identity(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            # A wheel may vendor other distributions under its package tree.
            # Only the wheel's top-level dist-info identifies this artifact.
            members = [name for name in archive.namelist()
                       if name.count("/") == 1
                       and name.endswith(".dist-info/METADATA")]
            if len(members) != 1:
                raise ValueError("wheel must contain exactly one METADATA")
            metadata = BytesParser().parsebytes(archive.read(members[0]))
    except zipfile.BadZipFile as error:
        raise ValueError("invalid wheel ZIP") from error
    name, version = metadata.get("Name"), metadata.get("Version")
    if not name or not version or "/" in name or "/" in version:
        raise ValueError("wheel has invalid Name/Version metadata")
    return canonical(name), version


def audit(
    installed: dict[str, str],
    wheel_roots: list[Path],
    locked: dict[tuple[str, str], str],
    http_cache_roots: list[Path] | None = None,
    built_cache_roots: list[Path] | None = None,
) -> dict[str, object]:
    wheels: dict[tuple[str, str], set[str]] = {}
    files_seen = 0
    for root in wheel_roots:
        if not root.is_dir() or root.is_symlink() or root.is_junction():
            raise ValueError("wheel root must be a non-link directory")
        for path in sorted(root.glob("*.whl")):
            if path.is_symlink() or path.is_junction() or not path.is_file():
                raise ValueError("wheel entry is not a regular non-link file")
            key = wheel_identity(path)
            wheels.setdefault(key, set()).add(digest(path))
            files_seen += 1
    cache_wheels_seen = 0
    for root in http_cache_roots or []:
        if not root.is_dir() or root.is_symlink() or root.is_junction():
            raise ValueError("HTTP cache root must be a non-link directory")
        for path in root.rglob("*.body"):
            if path.is_symlink() or path.is_junction() or not path.is_file():
                raise ValueError("HTTP cache entry is not a regular non-link file")
            if not zipfile.is_zipfile(path):
                continue
            try:
                key = wheel_identity(path)
            except ValueError:
                continue  # Cached ZIP payload was not a distribution wheel.
            wheels.setdefault(key, set()).add(digest(path))
            cache_wheels_seen += 1
    built_wheels_seen = 0
    for root in built_cache_roots or []:
        if not root.is_dir() or root.is_symlink() or root.is_junction():
            raise ValueError("built-wheel cache root must be a non-link directory")
        for path in root.rglob("*.whl"):
            if path.is_symlink() or path.is_junction() or not path.is_file():
                raise ValueError("built-wheel cache entry is not a regular non-link file")
            key = wheel_identity(path)
            wheels.setdefault(key, set()).add(digest(path))
            built_wheels_seen += 1
    missing_cache = []
    installed_candidates: dict[str, list[str]] = {}
    for name, version in sorted(installed.items()):
        key = f"{name}=={version}"
        candidates = sorted(wheels.get((name, version), set()))
        installed_candidates[key] = candidates
        if not candidates:
            missing_cache.append(f"{name}=={version}")
    locked_failures = []
    for key, expected in sorted(locked.items()):
        if installed.get(key[0]) != key[1]:
            locked_failures.append(f"{key[0]}=={key[1]}:not-installed")
        elif expected not in wheels.get(key, set()):
            locked_failures.append(f"{key[0]}=={key[1]}:wheel-hash-missing")
    return {
        "status": "partial_inventory" if missing_cache else "cached_wheels_present",
        "installed_distribution_count": len(installed),
        "wheel_file_count": files_seen,
        "http_cached_wheel_body_count": cache_wheels_seen,
        "built_cached_wheel_count": built_wheels_seen,
        "unique_wheel_distribution_count": len(wheels),
        "locked_distribution_count": len(locked),
        "locked_failures": locked_failures,
        "installed_without_cached_wheel": missing_cache,
        "installed_wheel_candidates": installed_candidates,
        "installed_with_multiple_candidates": [
            key for key, candidates in installed_candidates.items()
            if len(candidates) > 1
        ],
    }


def installed_distributions() -> dict[str, str]:
    result = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name")
        if not name:
            raise ValueError("installed distribution lacks Name metadata")
        key = canonical(name)
        if key in result and result[key] != dist.version:
            raise ValueError(f"multiple installed versions: {key}")
        result[key] = dist.version
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-root", type=Path, action="append", required=True)
    parser.add_argument("--pip-http-cache-root", type=Path, action="append")
    parser.add_argument("--pip-built-wheel-cache-root", type=Path, action="append")
    parser.add_argument("--hash-lock", type=Path, required=True)
    args = parser.parse_args()
    raw_lock = args.hash_lock.read_bytes()
    locked = parse_lock(raw_lock.decode("utf-8"))
    report = audit(installed_distributions(), args.wheel_root, locked,
                   args.pip_http_cache_root, args.pip_built_wheel_cache_root)
    report["hash_lock_sha256"] = hashlib.sha256(raw_lock).hexdigest()
    print(json.dumps(report, sort_keys=True))
    if report["locked_failures"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

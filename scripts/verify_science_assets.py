"""Offline byte-identity receipt for an explicit A6 asset lock; never downloads or loads a model.

This proves only that the listed local regular files match the declared size and
SHA-256. It does not prove publisher custody, license, completeness, runtime
compatibility, or authorization to execute a scientific experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SCHEMA_VERSION = "a6-asset-lock-v1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _relative_parts(value: object) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("asset path must be a relative POSIX path")
    parts = tuple(value.split("/"))
    if any(part in ("", ".", "..") for part in parts) or value.startswith("/"):
        raise ValueError("asset path contains an unsafe segment")
    return parts


def _entries(lock: object) -> list[dict[str, object]]:
    if not isinstance(lock, dict) or set(lock) != {"schema_version", "files"}:
        raise ValueError("asset lock has unexpected fields")
    if lock["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported asset-lock schema")
    files = lock["files"]
    if not isinstance(files, list) or not files:
        raise ValueError("asset lock must list at least one file")
    seen = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "size_bytes", "sha256"}:
            raise ValueError("asset entry has unexpected fields")
        parts = _relative_parts(entry["path"])
        if parts in seen:
            raise ValueError("duplicate asset path")
        seen.add(parts)
        if type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0:
            raise ValueError("invalid asset size")
        if not isinstance(entry["sha256"], str) or not SHA256.fullmatch(entry["sha256"]):
            raise ValueError("invalid lowercase SHA-256")
    return files


def _linklike(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def verify(asset_root: Path, lock: object) -> dict[str, object]:
    """Fail closed on absent/mismatched files, symlinks and path escapes."""
    entries = _entries(lock)
    if _linklike(asset_root) or not asset_root.is_dir():
        raise ValueError("asset root must be an existing non-link directory")
    receipts = []
    for entry in entries:
        path = asset_root
        for part in _relative_parts(entry["path"]):
            path = path / part
            if _linklike(path):
                raise ValueError(f"linked asset path: {entry['path']}")
        if not path.is_file():
            raise ValueError(f"missing or non-regular asset: {entry['path']}")
        if path.stat().st_size != entry["size_bytes"]:
            raise ValueError(f"asset size mismatch: {entry['path']}")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError(f"asset SHA-256 mismatch: {entry['path']}")
        receipts.append({"path": entry["path"], "size_bytes": entry["size_bytes"],
                         "sha256": digest.hexdigest()})
    return {"schema_version": "a6-asset-identity-receipt-v1", "scope": "listed-files-only",
            "files": receipts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = args.lock.read_bytes()
        lock = json.loads(raw)
        receipt = verify(args.asset_root, lock)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"asset verification failed: {error}\n")
    receipt["lock_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

"""Compare installed Stage-2 package payload bytes with hash-locked wheels.

Read-only, model-free check. Wheel metadata and .data installation transforms are
excluded and reported, so a pass is not a complete environment reconstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import zipfile
from pathlib import Path, PurePosixPath

from audit_science_wheels import canonical, digest, parse_lock, wheel_identity


def stream_digest(handle) -> str:
    result = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        result.update(chunk)
    return result.hexdigest()


def compare_payload(wheel: Path, installed_root: Path) -> dict[str, object]:
    if installed_root.is_symlink():
        raise ValueError("installed root must be a non-link directory")
    root = installed_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("installed root must be a non-link directory")
    compared = 0
    excluded_metadata = 0
    excluded_data = 0
    failures: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        members = archive.infolist()
        names = [entry.filename for entry in members]
        if len(names) != len(set(names)):
            raise ValueError("wheel has duplicate member names")
        for entry in members:
            if entry.is_dir():
                continue
            name = entry.filename
            path = PurePosixPath(name)
            if (path.is_absolute() or not path.parts or
                    any(part in ("", ".", "..") for part in name.split("/")) or
                    "\\" in name or ":" in name):
                raise ValueError("wheel has unsafe member path")
            first = path.parts[0]
            if first.endswith(".dist-info"):
                excluded_metadata += 1
                continue
            if first.endswith(".data"):
                excluded_data += 1
                continue
            target = root.joinpath(*path.parts)
            if not target.is_relative_to(root):
                raise ValueError("wheel member escapes installed root")
            if not target.is_file() or target.is_symlink():
                failures.append(name + ":missing-or-linked")
                continue
            if not target.resolve().is_relative_to(root):
                failures.append(name + ":linked-outside-root")
                continue
            with archive.open(entry) as source, target.open("rb") as installed:
                if stream_digest(source) != stream_digest(installed):
                    failures.append(name + ":byte-mismatch")
                else:
                    compared += 1
    if compared == 0 and not failures:
        failures.append("no-package-payload-files")
    return {
        "compared_payload_files": compared,
        "excluded_metadata_files": excluded_metadata,
        "excluded_data_files": excluded_data,
        "failure_count": len(failures),
        "failure_examples": failures[:10],
    }


def audit_locked_payload(lock: dict[tuple[str, str], str], wheel_root: Path,
                         distributions=None) -> dict[str, object]:
    if not wheel_root.is_dir() or wheel_root.is_symlink() or wheel_root.is_junction():
        raise ValueError("wheel root must be a non-link directory")
    expected_by_hash = {value: key for key, value in lock.items()}
    if len(expected_by_hash) != len(lock):
        raise ValueError("lock reuses a wheel hash")
    found: dict[tuple[str, str], Path] = {}
    for wheel in sorted(wheel_root.glob("*.whl")):
        if not wheel.is_file() or wheel.is_symlink() or wheel.is_junction():
            raise ValueError("wheel entry is not a regular non-link file")
        wheel_hash = digest(wheel)
        if wheel_hash not in expected_by_hash:
            continue
        key = wheel_identity(wheel)
        if key != expected_by_hash[wheel_hash] or key in found:
            raise ValueError("locked wheel identity is wrong or duplicated")
        found[key] = wheel
    rows = []
    for key, expected_hash in sorted(lock.items()):
        name, version = key
        if key not in found:
            rows.append({"distribution": f"{name}=={version}",
                         "status": "locked-wheel-missing"})
            continue
        dist = (distributions or importlib.metadata).distribution(name)
        if canonical(dist.metadata["Name"]) != name or dist.version != version:
            rows.append({"distribution": f"{name}=={version}",
                         "status": "installed-version-mismatch"})
            continue
        row = compare_payload(found[key], Path(dist.locate_file("")))
        row.update({"distribution": f"{name}=={version}",
                    "wheel_sha256": expected_hash,
                    "status": "payload-mismatch" if row["failure_count"] else
                              "payload-partial" if row["excluded_data_files"] else
                              "payload-match"})
        rows.append(row)
    return {
        "status": "payload-match" if rows and all(
            row["status"] == "payload-match" for row in rows) else "partial-or-failed",
        "locked_distribution_count": len(lock),
        "payload_match_count": sum(row["status"] == "payload-match" for row in rows),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-root", type=Path, required=True)
    parser.add_argument("--hash-lock", type=Path, required=True)
    args = parser.parse_args()
    lock_bytes = args.hash_lock.read_bytes()
    report = audit_locked_payload(parse_lock(lock_bytes.decode("utf-8")),
                                  args.wheel_root)
    report["hash_lock_sha256"] = hashlib.sha256(lock_bytes).hexdigest()
    print(json.dumps(report, sort_keys=True))
    if report["status"] != "payload-match":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

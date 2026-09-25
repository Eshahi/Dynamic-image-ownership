"""Fail-closed, read-only identity check for a future B3 image manifest.

This verifies local bytes and declared fields, not image rights or study splits.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


FIELDS = (
    "domain", "release_id", "source_split", "source_id", "relative_path",
    "raw_sha256", "raw_size_bytes", "width", "height", "group_id",
    "source_url", "license_reference", "rights_status", "use_limitations",
)
DOMAINS = {"ms-coco", "div2k", "diffusiondb"}
RIGHTS = {"pending-image-rights", "reviewed-restrictions"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*\Z")


def safe_relative_path(value: str) -> PurePosixPath:
    if not value or "\\" in value or ":" in value or value.startswith("/"):
        raise ValueError("relative_path is not a safe POSIX relative path")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("relative_path has empty or traversal component")
    return PurePosixPath(*parts)


def positive_int(value: str, field: str) -> int:
    if not value.isdecimal() or value.startswith("0"):
        raise ValueError(f"{field} must be a canonical positive integer")
    number = int(value)
    if number <= 0:
        raise ValueError(f"{field} must be positive")
    return number


def public_https(value: str, field: str) -> None:
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
    except ValueError as error:
        raise ValueError(f"{field} has invalid URL") from error
    if (parsed.scheme != "https" or not host or parsed.username or
            parsed.password or parsed.query or parsed.fragment or
            any(ord(char) < 33 for char in value)):
        raise ValueError(f"{field} must be public HTTPS without URL credentials or query")


def digest_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def validate(manifest: Path, asset_root: Path) -> dict[str, object]:
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("manifest must be a regular file")
    if asset_root.is_symlink() or asset_root.is_junction() or not asset_root.is_dir():
        raise ValueError("asset root must be a non-link directory")
    root = asset_root.resolve(strict=True)
    counts: Counter[str] = Counter()
    rights: Counter[str] = Counter()
    seen_ids: set[tuple[str, str, str, str]] = set()
    seen_paths: set[str] = set()
    digest_groups: dict[str, str] = {}
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("manifest columns do not match B3 contract")
        for line, row in enumerate(reader, start=2):
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("malformed CSV row")
                domain = row["domain"]
                if domain not in DOMAINS:
                    raise ValueError("unknown domain")
                for field in ("release_id", "source_split", "source_id", "group_id"):
                    if not SAFE_ID.fullmatch(row[field]):
                        raise ValueError(f"invalid {field}")
                key = tuple(row[field] for field in
                            ("domain", "release_id", "source_split", "source_id"))
                if key in seen_ids:
                    raise ValueError("duplicate source image ID")
                seen_ids.add(key)
                relative = safe_relative_path(row["relative_path"])
                if str(relative) in seen_paths:
                    raise ValueError("duplicate local image path")
                seen_paths.add(str(relative))
                if not HEX64.fullmatch(row["raw_sha256"]):
                    raise ValueError("invalid raw SHA-256")
                size = positive_int(row["raw_size_bytes"], "raw_size_bytes")
                positive_int(row["width"], "width")
                positive_int(row["height"], "height")
                if row["rights_status"] not in RIGHTS:
                    raise ValueError("unknown rights status")
                public_https(row["source_url"], "source_url")
                public_https(row["license_reference"], "license_reference")
                if not row["use_limitations"].strip():
                    raise ValueError("use limitations must be explicit")
                path = root.joinpath(*relative.parts)
                if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
                    raise ValueError("image is missing, linked or outside asset root")
                if path.stat().st_size != size or digest_file(path) != row["raw_sha256"]:
                    raise ValueError("image size or SHA-256 mismatch")
                prior_group = digest_groups.get(row["raw_sha256"])
                if prior_group is not None and prior_group != row["group_id"]:
                    raise ValueError("identical bytes assigned to different groups")
                digest_groups[row["raw_sha256"]] = row["group_id"]
                counts[domain] += 1
                rights[row["rights_status"]] += 1
            except ValueError as error:
                raise ValueError(f"line {line}: {error}") from error
    if not seen_ids:
        raise ValueError("manifest has no image rows")
    return {
        "status": "listed-bytes-verified-rights-not-certified",
        "row_count": len(seen_ids),
        "counts_by_domain": dict(sorted(counts.items())),
        "rights_status_counts": dict(sorted(rights.items())),
        "unique_byte_hash_count": len(digest_groups),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.manifest, args.asset_root), sort_keys=True))


if __name__ == "__main__":
    main()

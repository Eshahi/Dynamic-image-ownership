"""Metadata-only C4 case freeze. Never open pixels, models or C2 outcomes.

This is a prospective engineering selection, not approval or rights clearance.
All original 32 reservations are validated before size eligibility or ranking.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath

from src.runtime.config import strict_json_bytes

PINS = {
    "data/b4-admission-20260926/source-manifest.csv": "40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4",
    "data/b4-admission-20260926/development-reservation.json": "0bfd4178a1929e26d12401000c1eda0c549034c348458844e72f0c5b0a8f79ae",
    "data/splits.csv": "60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f",
}
SOURCE, RESERVATION, SPLITS = tuple(PINS)
IDENTITY = ("domain", "release_id", "source_split", "source_id")
COUNTS = {"diffusiondb": 12, "div2k": 10, "ms-coco": 10}
RULE = "minimum_native_metadata_pad64_area_then_source_uid_no_feature_or_output_selection"


def _uid(row):
    fields = [row[k] for k in IDENTITY]
    if any(not isinstance(v, str) or not v or ":" in v for v in fields):
        raise ValueError("invalid source identity")
    return ":".join(fields)


def _digest(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value) or value == "0"*64:
        raise ValueError("invalid artifact digest")
    return value


def _path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("invalid relative source path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
        raise ValueError("noncanonical source path")
    return value


def _integer(value):
    if not isinstance(value, str) or not re.fullmatch("[1-9][0-9]*", value):
        raise ValueError("invalid positive metadata integer")
    result = int(value)
    if result > 100_000_000:
        raise ValueError("unbounded metadata integer")
    return result


def _rows(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError("missing or duplicate CSV headers")
    result = {}
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("malformed CSV row")
        name = _uid(row)
        if name in result:
            raise ValueError("duplicate metadata source UID")
        result[name] = row
    return result


def select_case(source_bytes, reservation_bytes, split_bytes, *, maximum_side):
    """Pure selector for checked snapshots; owned fixtures may test all branches.

    The public production entrypoint additionally enforces immutable B4 hashes.
    This function does not accept features, outcomes or a preferred UID.
    """
    if type(maximum_side) is not int or not 64 <= maximum_side <= 1024:
        raise ValueError("bounded native maximum side required")
    sources, splits = _rows(source_bytes), _rows(split_bytes)
    reservation = strict_json_bytes(reservation_bytes)
    images = reservation["images"]
    if (reservation.get("b4_must_reserve_all_linked_groups_for_development") is not True
            or reservation.get("counts_by_domain") != COUNTS
            or not isinstance(images, list) or len(images) != 32):
        raise ValueError("original 32 development reservation required")
    names, counts, ranked = set(), dict.fromkeys(COUNTS, 0), []
    for row in images:
        name = _uid(row)
        if name in names or name not in sources or name not in splits:
            raise ValueError("duplicate or missing reserved source")
        names.add(name)
        if row["domain"] not in counts:
            raise ValueError("unexpected reserved domain")
        counts[row["domain"]] += 1
        source, split = sources[name], splits[name]
        for field in (*IDENTITY, "raw_sha256"):
            if row[field] != source[field] or row[field] != split[field]:
                raise ValueError("reserved source identity mismatch")
        _digest(row["raw_sha256"])
        canonical = _digest(split["canonical_pixel_sha256"])
        if (source["relative_path"] != _path(row["relative_path"])
                or source["group_id"] != row["group_id"]
                or split["study_split"] != "development" or split["split"] != "development"
                or split["source_uid"] != name or split["image_id"] != name
                or split["canonical_status"] != "canonical_pass"
                or split["canonical_rejection_reason"]
                or (row["domain"] == "div2k" and row["source_split"] != "train")):
            raise ValueError("not an admitted native development source")
        group = split["group_id"]
        if not group or any(other["study_split"] != "development" or other["split"] != "development"
                            for other in splits.values() if other["group_id"] == group):
            raise ValueError("reserved dependence group leaks into held-out split")
        width, height, size = (_integer(source[k]) for k in ("width", "height", "raw_size_bytes"))
        padded_width, padded_height = ((v+63)//64*64 for v in (width, height))
        ranked.append({"source_uid": name, "domain": row["domain"],
            "source_split": row["source_split"], "relative_path": row["relative_path"],
            "raw_sha256": row["raw_sha256"], "raw_size_bytes": size,
            "canonical_pixel_sha256": canonical, "group_id": group,
            "metadata_width": width, "metadata_height": height,
            "padded_area": padded_width*padded_height,
            "eligible": max(width, height) <= maximum_side,
            "rights_status": source["rights_status"], "use_limitations": source["use_limitations"]})
    if counts != COUNTS:
        raise ValueError("original reserved domain counts changed")
    ranked.sort(key=lambda row: (row["padded_area"], row["source_uid"]))
    eligible = [row for row in ranked if row["eligible"]]
    if not eligible:
        raise ValueError("no size-eligible native development case; no resize or replacement")
    return {"schema_version": "c4-metadata-case-freeze-v1", "rule": RULE,
        "maximum_side": maximum_side, "reserved_count": 32, "eligible_count": len(eligible),
        "selected": eligible[0],
        "ranking": [{k: row[k] for k in ("source_uid", "metadata_width", "metadata_height", "padded_area", "eligible")} for row in ranked],
        "metadata_only": True, "actual_pixels_revalidated": False,
        "scientific_execution_authorized": False, "rights_clearance": False,
        "no_fallback_after_failure": True}


def freeze_case(repo, *, maximum_side=1024):
    repo = Path(repo).absolute()
    snapshots = {}
    for name, digest in PINS.items():
        path = repo/name
        if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
            raise ValueError("linked metadata input")
        if not path.is_file() or path.stat().st_size > 16*1024*1024:
            raise ValueError("metadata snapshot must be a bounded regular file")
        with path.open("rb") as handle:
            raw = handle.read(16*1024*1024+1)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("immutable B4 metadata digest mismatch: " + name)
        snapshots[name] = raw
    result = select_case(snapshots[SOURCE], snapshots[RESERVATION], snapshots[SPLITS], maximum_side=maximum_side)
    result["input_sha256"] = dict(PINS)
    return result


def validate_frozen_case(repo, raw):
    """Replay the exact prospective recipe; a future worker cannot prefer a UID.

    No file named by the receipt is opened. Pixel byte/canonical checks remain
    mandatory downstream and cannot be replaced by this metadata check.
    """
    value = strict_json_bytes(raw)
    expected = freeze_case(repo, maximum_side=1024)
    # JSON types matter: Python equality otherwise admits False == 0 and
    # integer dimensions == floating dimensions in a relabeled receipt.
    canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if canonical(value) != canonical(expected):
        raise ValueError("frozen case differs from exact metadata selection recipe")
    return value

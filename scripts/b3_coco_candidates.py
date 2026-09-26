"""Offline COCO source candidates, not rights clearance or study allocation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ANNOTATION_SHA256 = "e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f"
INVENTORY_SHA256 = "bd849697919a1bba5101319ded0401f14be8e8ea150629187fd692389698fe18"
LICENSE_URLS = {4: "http://creativecommons.org/licenses/by/2.0/",
                5: "http://creativecommons.org/licenses/by-sa/2.0/"}
TARGET = 1000
MIN_DIMENSION = 64


class CandidateError(ValueError):
    pass


def positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise CandidateError(f"{name} must be a positive integer")
    return value


def candidate_frame(annotation, inventory, *, expected_count=5000, target=TARGET):
    """Validate the whole supplied frame before ranking an eligible subset.

    Test parameters are only for small synthetic frames; CLI fixes 5000/1000.
    The namespace binds ordering to the checked local annotation snapshot.
    """
    positive_int(expected_count, "expected_count")
    positive_int(target, "target")
    licenses = annotation.get("licenses")
    images = annotation.get("images")
    if not isinstance(licenses, list) or not isinstance(images, list):
        raise CandidateError("annotation licenses/images must be lists")
    license_map = {}
    for item in licenses:
        if not isinstance(item, dict):
            raise CandidateError("license record must be a mapping")
        identity = positive_int(item.get("id"), "license id")
        if identity in license_map:
            raise CandidateError("duplicate license id")
        license_map[identity] = item.get("url")
    if any(license_map.get(identity) != url for identity, url in LICENSE_URLS.items()):
        raise CandidateError("eligible license definitions differ from pinned policy")
    by_id = {}
    for item in inventory:
        if item.get("source") != "coco2017-val":
            continue
        identity = item.get("source_id")
        if not isinstance(identity, str) or not re.fullmatch(r"[1-9][0-9]{0,11}", identity):
            raise CandidateError("inventory source_id must be a canonical positive decimal ID")
        if identity in by_id:
            raise CandidateError("duplicate inventory source_id")
        by_id[identity] = item
    seen = set()
    eligible = []
    exclusions = {"license_label": 0, "native_dimensions": 0}
    digests = set()
    for image in images:
        if not isinstance(image, dict):
            raise CandidateError("image record must be a mapping")
        number = positive_int(image.get("id"), "image id")
        identity = str(number)
        filename = f"{number:012d}.jpg"
        if number >= 10**12 or identity in seen:
            raise CandidateError("duplicate/out-of-range annotation image id")
        seen.add(identity)
        if image.get("file_name") != filename or identity not in by_id:
            raise CandidateError("annotation filename/inventory identity mismatch")
        row = by_id[identity]
        width = positive_int(image.get("width"), "width")
        height = positive_int(image.get("height"), "height")
        license_id = positive_int(image.get("license"), "image license")
        if license_id not in license_map:
            raise CandidateError("undefined image license")
        for name, expected in (("width", width), ("height", height), ("license_id", license_id)):
            if row.get(name) != str(expected):
                raise CandidateError("annotation/inventory dimension or license mismatch")
        if row.get("format") != "JPEG" or row.get("mode") not in ("RGB", "L"):
            raise CandidateError("unsupported recorded image format/mode")
        size = row.get("bytes")
        if not isinstance(size, str) or not re.fullmatch(r"[1-9][0-9]*", size):
            raise CandidateError("invalid recorded image byte size")
        digest = row.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise CandidateError("invalid recorded image digest")
        if digest in digests:
            raise CandidateError("identical-byte COCO records require grouping before selection")
        digests.add(digest)
        path = row.get("relative_path", "")
        parts = PurePosixPath(path).parts
        if (not path or "\\" in path or ":" in path or path.startswith("/")
                or ".." in parts or "." in path.split("/") or "" in path.split("/")
                or parts[-1] != filename or parts[0] != "val2017"):
            raise CandidateError("unsafe/non-COCO recorded image path")
        flickr = image.get("flickr_url")
        parsed = urlsplit(flickr) if isinstance(flickr, str) else None
        if (not parsed or parsed.scheme not in ("http", "https") or parsed.username
                or parsed.password or parsed.port or parsed.query or parsed.fragment
                or not parsed.hostname or not parsed.hostname.endswith(".staticflickr.com")):
            raise CandidateError("invalid annotation Flickr attribution hook")
        if license_id not in LICENSE_URLS:
            exclusions["license_label"] += 1
            continue
        if min(width, height) < MIN_DIMENSION:
            exclusions["native_dimensions"] += 1
            continue
        rank = hashlib.sha256(b"b3-coco-source-candidate-v1\x00"
                              + bytes.fromhex(ANNOTATION_SHA256)
                              + number.to_bytes(8, "big")).hexdigest()
        eligible.append({"source_id": identity, "rank_sha256": rank,
                         "relative_path": path, "raw_sha256": digest,
                         "raw_size_bytes": int(size), "width": width, "height": height,
                         "license_id": license_id, "license_reference": LICENSE_URLS[license_id],
                         "flickr_attribution_hook": flickr,
                         "rights_status": "pending-image-rights"})
    if len(images) != expected_count or len(by_id) != expected_count or seen != set(by_id):
        raise CandidateError("whole COCO frame cardinality/identity mismatch")
    eligible.sort(key=lambda row: (row["rank_sha256"], row["source_id"]))
    if len(eligible) < target:
        raise CandidateError("insufficient eligible candidates; commitment cannot shrink")
    return {"status": "source_candidates_only_not_study_manifest",
            "annotation_sha256": ANNOTATION_SHA256, "inventory_sha256": INVENTORY_SHA256,
            "source_count": expected_count, "target_count": target,
            "eligible_count": len(eligible), "exclusions": exclusions,
            "rights_cleared": False, "study_ids_frozen": False,
            "scientific_compute_authorized": False,
            "candidates": eligible[:target], "ordered_reserves": eligible[target:]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payloads = []
    for path, digest in ((args.annotation, ANNOTATION_SHA256), (args.inventory, INVENTORY_SHA256)):
        if path.is_symlink() or not path.is_file():
            raise CandidateError("input must be a regular nonsymlink file")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            raise CandidateError("input snapshot digest differs from intake")
        payloads.append(payload)
    annotation = json.loads(payloads[0])
    inventory = csv.DictReader(io.StringIO(payloads[1].decode("utf-8")))
    result = candidate_frame(annotation, inventory)
    # Never overwrite an earlier receipt or follow an output link.
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("candidates", "ordered_reserves")}, sort_keys=True))


if __name__ == "__main__":
    main()

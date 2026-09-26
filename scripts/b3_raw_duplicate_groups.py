"""Hash-bound inventory overlap audit; not decoded/near duplicates or study splits."""

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from b3_diffusiondb_selection import _canonical_image_name, ranked_parts, MAX_PARTS
from b3_local_data_receipt import checked_bytes

RAW_FIELDS = {"source", "source_id", "relative_path", "bytes", "sha256", "width", "height",
              "mode", "format", "license_id"}
ZIP_FIELDS = {"part_id", "image_name", "bytes", "sha256", "width", "height", "mode"}


def positive_decimal(value):
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*", value):
        raise ValueError("invalid positive decimal inventory value")
    return int(value)


def inventory_records(payload):
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8")))
    if (reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames))
            or set(reader.fieldnames) not in (RAW_FIELDS, ZIP_FIELDS)):
        raise ValueError("unknown/duplicate inventory columns")
    is_zip = set(reader.fieldnames) == ZIP_FIELDS
    approved_parts = set(ranked_parts()[:MAX_PARTS])
    records = []
    counts = Counter()
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("malformed CSV record")
        size, width, height = (positive_decimal(row[key]) for key in ("bytes", "width", "height"))
        digest = row["sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid raw image digest")
        if is_zip:
            part = positive_decimal(row["part_id"])
            if part not in approved_parts:
                raise ValueError("part outside approved candidate frame")
            name = _canonical_image_name(row["image_name"])
            domain = f"diffusiondb2m-part-{part:06d}"
            identity = name
        else:
            domain, identity = row["source"], row["source_id"]
            if domain == "coco2017-val":
                positive_decimal(identity)
            elif domain in ("DIV2K_train_HR", "DIV2K_valid_HR"):
                if not re.fullmatch(r"[0-9]{4}", identity):
                    raise ValueError("invalid DIV2K source ID")
                lower, upper = (1, 800) if domain == "DIV2K_train_HR" else (801, 900)
                if not lower <= int(identity) <= upper:
                    raise ValueError("DIV2K ID outside source split")
            else:
                raise ValueError("unknown inventory source")
        counts[domain] += 1
        records.append({"id": domain + ":" + identity, "domain": domain,
                        "sha256": digest, "bytes": size, "width": width, "height": height})
    if is_zip:
        if len(counts) != 1 or list(counts.values()) != [1000]:
            raise ValueError("ZIP CSV must cover exactly one complete 1000-image part")
    elif dict(counts) != {"coco2017-val": 5000, "DIV2K_train_HR": 800, "DIV2K_valid_HR": 100}:
        raise ValueError("extracted CSV source-frame cardinality mismatch")
    return records


def overlap_groups(records):
    identities = set()
    buckets = defaultdict(list)
    counts = Counter()
    for row in records:
        if row["id"] in identities:
            raise ValueError("duplicate source-qualified image identity")
        identities.add(row["id"])
        counts[row["domain"]] += 1
        buckets[row["sha256"]].append(row)
    groups = []
    for digest, members in sorted(buckets.items()):
        if len({(m["bytes"], m["width"], m["height"]) for m in members}) != 1:
            raise ValueError("identical-byte records have conflicting size/dimensions")
        if len(members) > 1:
            domains = {m["domain"] for m in members}
            sources = {"diffusiondb2m" if d.startswith("diffusiondb2m-part-")
                       else "DIV2K" if d.startswith("DIV2K_") else d for d in domains}
            groups.append({"group_id": hashlib.sha256(b"b3-raw-byte-group-v1\0"
                                                       + bytes.fromhex(digest)).hexdigest(),
                           "raw_sha256": digest, "members": sorted(m["id"] for m in members),
                           "cross_source": len(sources) > 1,
                           "cross_inventory_domain": len(domains) > 1})
    return {"status": "bound_inventories_raw_byte_overlap_only",
            "images_examined": len(identities), "source_counts": dict(sorted(counts.items())),
            "duplicate_groups": groups, "duplicate_group_count": len(groups),
            "images_in_duplicate_groups": sum(len(g["members"]) for g in groups),
            "cross_source_group_count": sum(g["cross_source"] for g in groups),
            "cross_inventory_domain_group_count": sum(g["cross_inventory_domain"] for g in groups),
            "all_candidate_parts_present": all(f"diffusiondb2m-part-{p:06d}" in counts
                                                for p in ranked_parts()[:MAX_PARTS]),
            "decoded_or_near_duplicates_checked": False,
            "rights_cleared": False, "study_ids_frozen": False, "scientific_compute": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", action="append", required=True, type=Path)
    parser.add_argument("--sha256", action="append", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if len(args.inventory) != len(args.sha256):
        raise ValueError("every input needs one exact digest")
    records = []
    inputs = []
    for path, digest in zip(args.inventory, args.sha256):
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("inventory exceeds resource ceiling")
        payload = checked_bytes(path, path.parent)
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError("inventory snapshot digest mismatch")
        records.extend(inventory_records(payload))
        inputs.append({"sha256": digest, "bytes": len(payload)})
    result = overlap_groups(records)
    result["input_snapshots"] = inputs
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

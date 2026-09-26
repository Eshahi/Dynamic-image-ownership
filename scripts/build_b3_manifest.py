"""Build real source inventory/development reservations, not scientific approval."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from b3_coco_candidates import INVENTORY_SHA256
from b3_diffusiondb_selection import REVISION
from b3_observed_dependence import bound_snapshot
from validate_data_manifest import FIELDS, validate

COCO_SHA = "37dbd65045497b54a02d14b965824c2155606a0a39d194eced4bc5bdfceff270"
PROPOSAL_SHA = "caa20e7952da822fe1e46b141e59c0cfe03b13d97b79498e909f32cc8315abbd"
DEV_SEED = "b3-development-reservation-v1"
LOCAL = "Local restricted academic research only; no redistribution/public figures; no legal or visual-content certification"


def manifest_row(domain, release, split, identity, path, digest, size, width, height, url, license_ref, limits):
    return dict(zip(FIELDS, (domain, release, split, identity, path, digest, str(size),
                            str(width), str(height), "raw-" + digest, url, license_ref,
                            "pending-image-rights", limits)))


def build_rows(inventory, coco, proposal):
    counts = Counter(row["source"] for row in inventory)
    if counts != {"coco2017-val": 5000, "DIV2K_train_HR": 800, "DIV2K_valid_HR": 100}:
        raise ValueError("original inventory commitments differ")
    if len(coco["candidates"]) != 1000 or len(proposal["selected"]) != 5000:
        raise ValueError("selected source commitments differ")
    rows = []
    for item in coco["candidates"]:
        rows.append(manifest_row("ms-coco", "coco-2017", "val2017", item["source_id"],
            item["relative_path"], item["raw_sha256"], item["raw_size_bytes"], item["width"], item["height"],
            "https://images.cocodataset.org/zips/val2017.zip", item["license_reference"].replace("http://", "https://", 1),
            LOCAL + "; recorded image license_id=" + str(item["license_id"]) +
            "; annotation license is not image ownership; original archive identity unproved; creator/title/public attribution pending"))
    for item in inventory:
        if item["source"] not in ("DIV2K_train_HR", "DIV2K_valid_HR"):
            continue
        split = "train" if item["source"] == "DIV2K_train_HR" else "valid"
        rows.append(manifest_row("div2k", "div2k-2017", split, item["source_id"], item["relative_path"],
            item["sha256"], item["bytes"], item["width"], item["height"],
            "https://data.vision.ee.ethz.ch/cvl/DIV2K/" + item["source"] + ".zip",
            "https://data.vision.ee.ethz.ch/cvl/DIV2K/",
            LOCAL + "; maintainers academic-only terms; original owners retain copyright; original archive identity unproved; source split is not study split"))
    for item in proposal["selected"]:
        part = f"part-{item['part_id']:06d}"
        rows.append(manifest_row("diffusiondb", "diffusiondb-2m-" + REVISION, part,
            item["image_name"][:-4], "diffusiondb-2m/selected-20260926/" + part + "/" + item["image_name"],
            item["raw_sha256"], item["raw_size_bytes"], item["width"], item["height"],
            "https://huggingface.co/datasets/poloclub/diffusiondb/resolve/" + REVISION + "/images/" + part + ".zip",
            "https://huggingface.co/datasets/poloclub/diffusiondb/blob/" + REVISION + "/README.md",
            LOCAL + "; curator CC0/terms claim not independent rights clearance; image/prompt NSFW scores strictly below0.10; metadata-screened not visually reviewed; no prompts/users; canonical/near/user dependence pending"))
    if Counter(row["domain"] for row in rows) != {"ms-coco":1000,"div2k":900,"diffusiondb":5000}:
        raise ValueError("manifest commitments differ")
    return sorted(rows, key=lambda row: (row["domain"], row["source_split"], row["source_id"]))


def reserve_development(rows, manifest_sha, *, allocation=None):
    allocation = allocation or {"ms-coco": 10, "div2k": 10, "diffusiondb": 12}
    selected, seen = [], set()
    def rank(row):
        identity = ":".join(row[field] for field in ("domain", "release_id", "source_split", "source_id"))
        return hashlib.sha256(DEV_SEED.encode() + b"\0" + identity.encode()).hexdigest(), identity
    for domain, count in sorted(allocation.items()):
        available = sorted((row for row in rows if row["domain"] == domain and
                           (domain != "div2k" or row["source_split"] == "train")), key=rank)
        chosen = 0
        for row in available:
            if row["group_id"] in seen:
                continue
            selected.append({key:row[key] for key in ("domain", "release_id", "source_split", "source_id",
                                                      "relative_path", "raw_sha256", "group_id")})
            seen.add(row["group_id"])
            chosen += 1
            if chosen == count:
                break
        if chosen != count:
            raise ValueError("insufficient distinct provisional development groups")
    return {"status":"development_reservation_not_study_split_or_compute_approval", "seed":DEV_SEED,
            "manifest_sha256":manifest_sha, "counts_by_domain":allocation, "reserved_count":len(selected),
            "images":selected, "b4_must_reserve_all_linked_groups_for_development":True,
            "stronger_dependence_checked":False, "scientific_compute_authorized":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inventory", "coco", "proposal", "asset-root", "manifest", "dev-output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    if args.manifest.exists() or args.dev_output.exists():
        raise ValueError("outputs already exist; preserve earlier artifacts")
    inventory = list(csv.DictReader(io.StringIO(bound_snapshot(args.inventory, INVENTORY_SHA256).decode())))
    coco = json.loads(bound_snapshot(args.coco, COCO_SHA))
    proposal = json.loads(bound_snapshot(args.proposal, PROPOSAL_SHA))
    rows = build_rows(inventory, coco, proposal)
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    payload = csv_buffer.getvalue().encode()
    manifest_sha = hashlib.sha256(payload).hexdigest()
    dev = reserve_development(rows, manifest_sha)
    # Generated artifacts, exclusive writes; retain a partial artifact if validation fails.
    with args.manifest.open("xb") as stream:
        stream.write(payload)
    report = validate(args.manifest, args.asset_root)
    if report["row_count"] != 6900:
        raise ValueError("actual manifest count differs")
    with args.dev_output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(dev, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps(report | {"manifest_sha256":manifest_sha,
          "dev_sha256":hashlib.sha256(args.dev_output.read_bytes()).hexdigest(),
          "reserved_development_count":dev["reserved_count"], "scientific_compute":False}, sort_keys=True))


if __name__ == "__main__":
    main()

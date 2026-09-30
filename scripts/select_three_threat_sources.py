"""Metadata-only source expansion; no image decoding or numerical inference."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def candidates(annotation, splits, raw_root):
    data = json.loads(Path(annotation).read_text(encoding="utf-8"))
    cat = next(row["id"] for row in data["categories"] if row["name"] == "cat")
    ids = {row["image_id"] for row in data["annotations"] if row["category_id"] == cat}
    with Path(splits).open(encoding="utf-8-sig", newline="") as stream:
        frozen = [r for r in csv.DictReader(stream) if r["domain"] == "ms-coco"]
    excluded_ids = {int(r["source_id"]) for r in frozen}
    excluded_hashes = {r["raw_sha256"] for r in frozen}
    licenses = {row["id"]: row for row in data["licenses"]}
    result = []
    for row in sorted(data["images"], key=lambda r: r["id"]):
        if row["id"] not in ids or row["id"] in excluded_ids or min(row["width"], row["height"]) < 160:
            continue
        path = Path(raw_root) / row["file_name"]
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in excluded_hashes:
            continue
        result.append({"source_id": row["id"], "path": str(path), "raw_sha256": digest,
                       "width": row["width"], "height": row["height"],
                       "license": licenses[row["license"]], "source_metadata": row,
                       "status": "metadata_candidate_not_admitted_or_reserved",
                       "selection": "ascending_numeric_id_cat_annotation_outside_all_frozen_coco_ids_and_raw_hashes"})
        if len(result) == 8:
            break
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", required=True)
    p.add_argument("--splits", required=True)
    p.add_argument("--raw-root", required=True)
    args = p.parse_args()
    print(json.dumps(candidates(args.annotations, args.splits, args.raw_root), indent=2))

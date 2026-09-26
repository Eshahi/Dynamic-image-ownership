"""Read-only extracted-source intake; not a study manifest or rights approval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


class IntakeError(ValueError):
    pass


def source_folder(root: Path, name: str) -> Path:
    """Admit direct files or a single same-named archive wrapper directory."""
    folder = root / name
    if folder.is_symlink() or folder.is_junction():
        raise IntakeError("source folder is linked")
    entries = list(folder.iterdir())
    if len(entries) == 1 and entries[0].name == name and entries[0].is_dir():
        folder = entries[0]
        if folder.is_symlink() or folder.is_junction():
            raise IntakeError("source wrapper folder is linked")
    return folder


def checked_bytes(path: Path, root: Path) -> bytes:
    root = root.resolve(strict=True)
    if path.is_symlink() or not path.is_file():
        raise IntakeError("source is not a regular nonsymlink file")
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise IntakeError("source escapes declared root")
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink() or parent.is_junction():
            raise IntakeError("source uses a linked directory")
    return resolved.read_bytes()


def image_record(path: Path, root: Path, source: str, identity: str,
                 license_id: int | str) -> dict:
    from PIL import Image

    payload = checked_bytes(path, root)
    with Image.open(io.BytesIO(payload)) as image:
        width, height = image.size
        mode, fmt = image.mode, image.format
        if getattr(image, "n_frames", 1) != 1:
            raise IntakeError("multi-frame image is outside intake contract")
        image.verify()
    with Image.open(io.BytesIO(payload)) as image:
        image.load()  # Full decode, no transform or model evaluation.
    if fmt not in ("JPEG", "PNG") or width <= 0 or height <= 0:
        raise IntakeError("unsupported image metadata")
    return {"source": source, "source_id": identity,
            "relative_path": path.relative_to(root).as_posix(),
            "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
            "width": width, "height": height, "mode": mode, "format": fmt,
            "license_id": license_id}


def intake(root: Path) -> tuple[list[dict], dict]:
    root = root.resolve(strict=True)
    ann_root = root / "annotations_trainval2017" / "annotations"
    ann_receipts = []
    for name in ("captions_train2017.json", "captions_val2017.json",
                 "instances_train2017.json", "instances_val2017.json",
                 "person_keypoints_train2017.json", "person_keypoints_val2017.json"):
        payload = checked_bytes(ann_root / name, root)
        ann_receipts.append({"name": name, "bytes": len(payload),
                             "sha256": hashlib.sha256(payload).hexdigest()})
    annotations = json.loads(checked_bytes(ann_root / "instances_val2017.json", root))
    images = annotations["images"]
    if len(images) != 5000 or len({r["id"] for r in images}) != 5000:
        raise IntakeError("COCO val image IDs must be 5000 unique records")
    licenses = {entry["id"]: entry for entry in annotations["licenses"]}
    coco_folder = source_folder(root, "val2017")
    names = set()
    records = []
    for info in sorted(images, key=lambda item: item["id"]):
        name = info["file_name"]
        if not re.fullmatch(r"[0-9]{12}\.jpg", name) or name in names:
            raise IntakeError("COCO filename invalid or duplicated")
        names.add(name)
        if info["license"] not in licenses:
            raise IntakeError("COCO license reference missing")
        row = image_record(coco_folder / name, root, "coco2017-val",
                           str(info["id"]), info["license"])
        if (row["width"], row["height"]) != (info["width"], info["height"]):
            raise IntakeError("COCO dimensions disagree with annotation")
        records.append(row)
    if {p.name for p in coco_folder.iterdir()} != names:
        raise IntakeError("COCO folder members disagree with annotation")
    for folder, first, last in (("DIV2K_train_HR", 1, 800),
                                ("DIV2K_valid_HR", 801, 900)):
        expected = {f"{number:04d}.png" for number in range(first, last + 1)}
        image_folder = source_folder(root, folder)
        if {p.name for p in image_folder.iterdir()} != expected:
            raise IntakeError("DIV2K folder members disagree with expected IDs")
        for name in sorted(expected):
            records.append(image_record(image_folder / name, root, folder,
                                        name[:-4], "academic-only-source-terms"))
    tree = hashlib.sha256()
    for row in records:
        tree.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode() + b"\n")
    digest_counts = Counter(row["sha256"] for row in records)
    summary = {"status": "extracted_source_intake_pass", "archive_hashes_available": False,
               "inventory_sha256": tree.hexdigest(), "images": len(records),
               "source_counts": dict(Counter(row["source"] for row in records)),
               "exact_duplicate_byte_groups": sum(n > 1 for n in digest_counts.values()),
               "coco_license_counts": dict(sorted(Counter(
                   str(row["license_id"]) for row in records
                   if row["source"] == "coco2017-val").items())),
               "coco_license_definitions": list(licenses.values()),
               "annotations": ann_receipts, "full_decode": True,
               "rights_cleared": False, "study_ids_frozen": False,
               "scientific_compute": False}
    return records, summary


def main() -> None:
    import PIL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    try:
        records, summary = intake(args.root)
        summary["pillow_version"] = PIL.__version__
        with (args.output_dir / "images.csv").open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        with (args.output_dir / "receipt.json").open("x", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
        print(json.dumps(summary, sort_keys=True))
    except Exception as error:
        # Avoid publishing raw source paths or annotation text on failure.
        with (args.output_dir / "failure.json").open("x", encoding="utf-8") as stream:
            json.dump({"status": "intake_failed", "error_type": type(error).__name__}, stream)
        raise


if __name__ == "__main__":
    main()

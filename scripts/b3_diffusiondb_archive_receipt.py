"""Read-only bound ZIP/PNG integrity; no extraction, model, content/rights verdict."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import stat
import warnings
import zipfile
from pathlib import Path

from b3_diffusiondb_selection import REVISION, _canonical_image_name
from b3_local_data_receipt import checked_bytes
from b3_read_diffusiondb_metadata import EXPECTED_SHA256

MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_PART_BYTES = 2 * 1024 * 1024 * 1024
MAX_PIXELS = 64 * 1024 * 1024


def validate_directory(entries, part, expected):
    """Admit only 1000 metadata-bound root PNGs and one observed part JSON."""
    if len(expected) != 1000 or len(entries) != 1001:
        raise ValueError("ZIP/index cardinality mismatch")
    for name, dimensions in expected.items():
        _canonical_image_name(name)
        for field in ("width", "height"):
            n = dimensions.get(field)
            if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
                raise ValueError("invalid expected image dimensions")
        if dimensions["width"] * dimensions["height"] > MAX_PIXELS:
            raise ValueError("image dimensions exceed declared inspection resource ceiling")
    names = set()
    total = 0
    json_name = f"part-{part:06d}.json"
    for entry in entries:
        name = entry.filename
        if name in names:
            raise ValueError("duplicate ZIP member")
        names.add(name)
        if name != json_name and name not in expected:
            raise ValueError("unexpected or unsafe ZIP member path")
        if entry.is_dir() or entry.flag_bits & 0x41:
            raise ValueError("directory/encrypted ZIP member is forbidden")
        mode = entry.external_attr >> 16
        if stat.S_IFMT(mode) not in (0, stat.S_IFREG) or entry.external_attr & 0x10:
            raise ValueError("linked/nonregular ZIP member is forbidden")
        if entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise ValueError("unsupported ZIP compression")
        limit = MAX_JSON_BYTES if name == json_name else MAX_MEMBER_BYTES
        if not 0 < entry.file_size <= limit or entry.compress_size < 0:
            raise ValueError("ZIP member exceeds declared byte ceiling")
        total += entry.file_size
    if names != set(expected) | {json_name} or total > MAX_PART_BYTES:
        raise ValueError("ZIP membership or total byte ceiling mismatch")
    return total


def inspect_archive(payload, part, expected):
    from PIL import Image

    records = []
    archive_json_hash = None
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        total = validate_directory(archive.infolist(), part, expected)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            for entry in archive.infolist():
                # Fully reading exercises ZIP CRC before decoding; central sizes cap output.
                with archive.open(entry) as stream:
                    image_bytes = stream.read(entry.file_size + 1)
                if len(image_bytes) != entry.file_size:
                    raise ValueError("ZIP member actual size differs")
                digest = hashlib.sha256(image_bytes).hexdigest()
                if entry.filename.endswith(".json"):
                    archive_json_hash = digest  # Hash/CRC only; never parse/export prompt metadata.
                    continue
                dimensions = expected[entry.filename]
                with Image.open(io.BytesIO(image_bytes)) as image:
                    if (image.format != "PNG" or image.size != (dimensions["width"], dimensions["height"])
                            or getattr(image, "n_frames", 1) != 1 or image.width * image.height > MAX_PIXELS):
                        raise ValueError("PNG format/dimensions/frame mismatch")
                    mode = image.mode
                    if mode not in ("RGB", "RGBA", "L", "P"):
                        raise ValueError("unsupported PNG mode")
                    image.verify()
                with Image.open(io.BytesIO(image_bytes)) as image:
                    image.load()
                records.append({"part_id": part, "image_name": entry.filename,
                                "bytes": len(image_bytes), "sha256": digest,
                                "width": dimensions["width"], "height": dimensions["height"], "mode": mode})
    records.sort(key=lambda row: row["image_name"])
    return records, {"images": len(records), "zip_members": 1001,
                     "total_uncompressed_bytes": total, "archive_json_sha256": archive_json_hash}


def main():
    from PIL import __version__ as pillow_version

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--index-sha256", required=True)
    parser.add_argument("--output-prefix", required=True, type=Path)
    args = parser.parse_args()
    inventory_payload = checked_bytes(args.inventory, args.inventory.parent)
    if hashlib.sha256(inventory_payload).hexdigest() != "97d858ed38918f502e50b7ef122410e5406486483a731e3fc727d5b4900261ab":
        raise ValueError("pinned archive inventory differs")
    inventory = json.loads(inventory_payload)
    name = args.archive.name
    matches = [row for row in inventory["files"] if row["path"] == "images/" + name]
    if len(matches) != 1 or inventory["revision"] != REVISION:
        raise ValueError("archive is outside approved inventory")
    contract = matches[0]
    part = int(name[5:11])
    if args.index.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("private index exceeds declared resource ceiling")
    index_payload = checked_bytes(args.index, args.index.parent)
    if hashlib.sha256(index_payload).hexdigest() != args.index_sha256:
        raise ValueError("private index snapshot hash differs")
    index = json.loads(index_payload)
    if index["revision"] != REVISION or index["metadata_sha256"] != EXPECTED_SHA256:
        raise ValueError("private index source identity differs")
    if args.archive.stat().st_size != contract["size"]:
        raise ValueError("archive size differs before snapshot allocation")
    payload = checked_bytes(args.archive, args.archive.parent)
    if len(payload) != contract["size"] or hashlib.sha256(payload).hexdigest() != contract["lfs"]["oid"]:
        raise ValueError("archive byte identity mismatch")
    records, receipt = inspect_archive(payload, part, index["parts"][str(part)])
    output_csv = Path(str(args.output_prefix) + ".csv")
    output_json = Path(str(args.output_prefix) + ".json")
    if output_csv.exists() or output_json.exists():
        raise ValueError("receipt outputs already exist; preserve them")
    with output_csv.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    receipt.update({"status": "archive_crc_and_png_decode_only", "part_id": part,
                    "revision": REVISION, "archive_bytes": len(payload),
                    "archive_sha256": contract["lfs"]["oid"], "index_sha256": args.index_sha256,
                    "image_inventory_sha256": hashlib.sha256(output_csv.read_bytes()).hexdigest(),
                    "pillow_version": pillow_version, "raw_prompts_exported": False,
                    "rights_cleared": False, "content_reviewed": False,
                    "study_ids_frozen": False, "scientific_compute": False})
    with output_json.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

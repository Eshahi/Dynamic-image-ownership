"""Explicit selected-member staging; not source admission, rights or compute."""

import argparse
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

from b3_diffusiondb_archive_receipt import inspect_archive, verified_archive_snapshot
from b3_diffusiondb_selection import _canonical_image_name
from b3_observed_dependence import bound_snapshot


def unique_selected_mapping(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate selected JSON key")
        result[key] = value
    return result


def stage_selected(payload, part, expected, selected, output_root, *, execute=False):
    """Preview by default; after full inspection copy only exact named raw bytes."""
    if not isinstance(selected, dict) or not selected:
        raise ValueError("selected member digest mapping must be nonempty")
    if not output_root.is_absolute():
        raise ValueError("output root must be absolute for ancestor checks")
    records, _ = inspect_archive(payload, part, expected)
    by_name = {row["image_name"]: row for row in records}
    for name, digest in selected.items():
        _canonical_image_name(name)
        if name not in by_name or by_name[name]["sha256"] != digest:
            raise ValueError("selected member is absent or its raw digest differs")
    if (output_root.is_symlink() or output_root.is_junction() or not output_root.is_dir()):
        raise ValueError("output root must be an existing unlinked directory")
    for parent in output_root.parents:
        if parent.is_symlink() or parent.is_junction():
            raise ValueError("linked output ancestor is forbidden")
    root = output_root.resolve(strict=True)
    destination = root / f"part-{part:06d}"
    if destination.exists() or destination.is_symlink():
        raise ValueError("destination already exists; preserve prior files")
    required = sum(by_name[name]["bytes"] for name in selected)
    if shutil.disk_usage(root).free < required + 1024 * 1024:
        raise ValueError("insufficient declared staging storage")
    receipt = {"status": "selected_member_staging_preview", "part_id": part,
               "members": len(selected), "raw_bytes": required, "files_written": 0,
               "source_ids_frozen": False, "rights_cleared": False, "scientific_compute": False}
    if not execute:
        return receipt
    # No extractall(), archive paths, metadata JSON or source transformations.
    # Failures preserve the new partial directory; it is not a completed receipt.
    destination.mkdir()
    if destination.is_symlink() or destination.is_junction() or destination.resolve() != destination:
        raise ValueError("staging destination changed to a link")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in sorted(selected):
            row = by_name[name]
            with archive.open(name) as handle:
                image_bytes = handle.read(row["bytes"] + 1)
            if len(image_bytes) != row["bytes"] or hashlib.sha256(image_bytes).hexdigest() != selected[name]:
                raise ValueError("selected bytes changed after inspection")
            with (destination / name).open("xb") as handle:
                handle.write(image_bytes)
            receipt["files_written"] += 1
    receipt["status"] = "selected_raw_members_staged_not_accepted_source"
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--index-sha256", required=True)
    parser.add_argument("--selected", required=True, type=Path)
    parser.add_argument("--selected-sha256", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    selected = json.loads(bound_snapshot(args.selected, args.selected_sha256),
                          object_pairs_hook=unique_selected_mapping)
    payload, part, expected, contract = verified_archive_snapshot(
        args.archive, args.inventory, args.index, args.index_sha256)
    result = stage_selected(payload, part, expected, selected, args.output_root, execute=args.execute)
    result.update({"archive_sha256": contract["lfs"]["oid"], "selected_sha256": args.selected_sha256})
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

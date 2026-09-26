"""Private, hash-bound image-name/dimension index; never exports prompts/users."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from b3_diffusiondb_selection import MAX_PARTS, REVISION, _canonical_image_name, ranked_parts
from b3_read_diffusiondb_metadata import EXPECTED_SHA256, EXPECTED_SIZE


def local_index(path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    if pa.__version__ != "21.0.0" or path.is_symlink() or not path.is_file():
        raise ValueError("requires checked local file and PyArrow 21.0.0")
    payload = path.read_bytes()
    if len(payload) != EXPECTED_SIZE or hashlib.sha256(payload).hexdigest() != EXPECTED_SHA256:
        raise ValueError("pinned metadata byte identity mismatch")
    parquet = pq.ParquetFile(pa.BufferReader(payload))
    if parquet.metadata.num_rows != 2000000:
        raise ValueError("full metadata row count mismatch")
    parts = ranked_parts()[:MAX_PARTS]
    records = {str(part): {} for part in parts}
    counts = Counter()
    names = set()
    for batch in parquet.iter_batches(columns=["part_id", "image_name", "width", "height"],
                                      batch_size=32768, use_threads=False):
        for row in batch.to_pylist():
            part = row["part_id"]
            if isinstance(part, bool) or not isinstance(part, int) or not 1 <= part <= 2000:
                raise ValueError("invalid part ID")
            counts[part] += 1
            if part not in parts:
                continue
            name = _canonical_image_name(row["image_name"])
            if name in names:
                raise ValueError("duplicate candidate image name")
            names.add(name)
            width, height = row["width"], row["height"]
            if any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in (width, height)):
                raise ValueError("invalid candidate dimensions")
            records[str(part)][name] = {"width": width, "height": height}
    if set(counts) != set(range(1, 2001)) or any(n != 1000 for n in counts.values()):
        raise ValueError("full metadata part cardinality mismatch")
    if any(len(records[str(part)]) != 1000 for part in parts):
        raise ValueError("candidate index cardinality mismatch")
    return {"status": "private_integrity_index_not_eligible_selection", "revision": REVISION,
            "metadata_sha256": EXPECTED_SHA256, "part_cap": MAX_PARTS,
            "parts": records, "raw_prompts_exported": False, "user_identifiers_read": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = local_index(args.metadata)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "parts": len(result["parts"]),
                      "images": sum(len(rows) for rows in result["parts"].values())}))


if __name__ == "__main__":
    main()

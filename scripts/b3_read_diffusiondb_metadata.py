"""Offline hash-bound Parquet adapter; emits aggregates, never prompts/users."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from b3_diffusiondb_selection import MAX_PARTS, PART_COUNT, ROWS_PER_PART, SelectionError, candidate_part_handoff

EXPECTED_SIZE = 194548652
EXPECTED_SHA256 = "eecd341187bc91c07f5994ad0660d40228ea025616fd57a509bef8323677c68f"
COLUMNS = ("part_id", "image_name", "prompt", "width", "height", "image_nsfw", "prompt_nsfw")


def select_local_metadata(path: Path, candidate_observer=None) -> dict:
    import pyarrow as pa
    import pyarrow.parquet as pq

    if pa.__version__ != "21.0.0":
        raise SelectionError("metadata adapter requires PyArrow 21.0.0")
    if path.is_symlink() or not path.is_file() or path.stat().st_size != EXPECTED_SIZE:
        raise SelectionError("metadata file type or size mismatch")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256 or len(payload) != EXPECTED_SIZE:
        raise SelectionError("metadata SHA-256 mismatch")
    # Parse the SAME verified immutable in-memory bytes, not a reopened path.
    parquet = pq.ParquetFile(pa.BufferReader(payload))
    schema = parquet.schema_arrow
    if parquet.metadata.num_rows != PART_COUNT * ROWS_PER_PART:
        raise SelectionError("metadata row count is not the pinned 2M release")
    if any(schema.names.count(column) != 1 for column in COLUMNS):
        raise SelectionError("required metadata schema columns missing or duplicated")
    counts = Counter()

    def rows():
        for batch in parquet.iter_batches(batch_size=32768, columns=list(COLUMNS), use_threads=False):
            for row in batch.to_pylist():
                part = row["part_id"]
                if isinstance(part, bool) or not isinstance(part, int) or not 1 <= part <= PART_COUNT:
                    raise SelectionError("invalid part_id in full metadata")
                counts[part] += 1
                if candidate_observer is not None:
                    candidate_observer(row)
                yield row

    result = candidate_part_handoff(rows())
    if len(counts) != PART_COUNT or any(counts[p] != ROWS_PER_PART for p in range(1, PART_COUNT + 1)):
        raise SelectionError("full release part cardinality mismatch")
    result.update({"metadata_sha256": digest, "metadata_bytes": len(payload),
                   "production_part_cap": MAX_PARTS,
                   "metadata_rows": parquet.metadata.num_rows, "parts_checked": len(counts),
                   "rows_per_part": ROWS_PER_PART, "pyarrow_version": pa.__version__,
                   "raw_prompts_exported": False, "user_identifiers_read": False})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = select_local_metadata(args.metadata)
    except SelectionError as error:
        result = {"status": "blocked_metadata_error", "reason": str(error),
                  "selected_part_ids": [], "image_ids_frozen": False}
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "candidate_parts_ready":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

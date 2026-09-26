"""Reproduce capacity diagnostics only; never emits a download-list approval."""
import argparse
import hashlib
import json
import math
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from b3_diffusiondb_selection import ranked_parts
from b3_read_diffusiondb_metadata import EXPECTED_SHA256, EXPECTED_SIZE

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--metadata", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
import pyarrow as pa
import pyarrow.parquet as pq
assert pa.__version__ == "21.0.0"
payload = args.metadata.read_bytes()
assert len(payload) == EXPECTED_SIZE and hashlib.sha256(payload).hexdigest() == EXPECTED_SHA256
order = ranked_parts()[:14]
groups = {part: set() for part in order}
counts = Counter()
parquet = pq.ParquetFile(pa.BufferReader(payload))
assert parquet.metadata.num_rows == 2000000
for batch in parquet.iter_batches(batch_size=32768, use_threads=False,
        columns=["part_id", "prompt", "image_nsfw", "prompt_nsfw", "width", "height"]):
    for row in batch.to_pylist():
        part = row["part_id"]
        counts[part] += 1
        if part not in groups:
            continue
        scores = (row["image_nsfw"], row["prompt_nsfw"])
        # Sentinel 2.0 and every other invalid score are ineligible in diagnostics.
        if any(value is None or not math.isfinite(value) or not 0 <= value < .10
               for value in scores):
            continue
        if min(row["width"], row["height"]) < 64:
            continue
        prompt = row["prompt"]
        if not isinstance(prompt, str):
            continue
        normalized = " ".join(unicodedata.normalize("NFC", prompt).casefold().split())
        if normalized:
            groups[part].add(normalized)
assert set(counts) == set(range(1, 2001)) and set(counts.values()) == {1000}
accumulated = set()
prefixes = []
for position, part in enumerate(order, 1):
    accumulated.update(groups[part])
    prefixes.append({"prefix": position, "distinct_prompt_groups": len(accumulated)})
result = {"status": "diagnostic_only_not_accepted_handoff", "metadata_sha256": EXPECTED_SHA256,
          "metadata_bytes": EXPECTED_SIZE, "parts_checked": len(counts),
          "prefix_counts": prefixes, "raw_prompts_exported": False,
          "images_downloaded": False, "image_ids_frozen": False}
with args.output.open("x", encoding="utf-8") as stream:
    json.dump(result, stream, sort_keys=True, indent=2)
print(json.dumps(result, sort_keys=True))

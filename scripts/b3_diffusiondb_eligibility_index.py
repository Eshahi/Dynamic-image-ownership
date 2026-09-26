"""Private metadata eligibility ledger, not content/rights or final source IDs."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from b3_diffusiondb_selection import (MAX_PARTS, NSFW_CEILING, REVISION, SelectionError,
                                    _canonical_image_name, _prompt_group, _score, ranked_parts)
from b3_read_diffusiondb_metadata import select_local_metadata


def eligibility_record(row):
    """Same strict source criteria as production; no prompt text is retained."""
    name = _canonical_image_name(row.get("image_name"))
    width, height = row.get("width"), row.get("height")
    if any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in (width, height)):
        raise SelectionError("image dimensions must be positive integers")
    image_score = _score(row.get("image_nsfw"), "image_nsfw")
    prompt_score = _score(row.get("prompt_nsfw"), "prompt_nsfw")
    group = _prompt_group(row.get("prompt"))
    # Preserve production precedence: score/size exclusion precedes empty text.
    if min(width, height) < 64 or image_score >= NSFW_CEILING or prompt_score >= NSFW_CEILING:
        reason = "score_or_size"
    elif group is None:
        reason = "empty_prompt"
    else:
        reason = "metadata_eligible"
    return name, {"reason": reason,
                  "prompt_group_sha256": group if reason == "metadata_eligible" else None}


def build_index(path):
    parts = ranked_parts()[:MAX_PARTS]
    records = {str(part): {} for part in parts}

    def observe(row):
        part = row["part_id"]
        if part not in parts:
            return
        name, record = eligibility_record(row)
        if name in records[str(part)]:
            raise SelectionError("duplicate candidate image in eligibility index")
        records[str(part)][name] = record

    production = select_local_metadata(path, candidate_observer=observe)
    if production["status"] != "candidate_parts_ready" or production["selected_part_ids"] != list(parts):
        raise SelectionError("strict production receipt does not cover the approved fourteen-part frame")
    if any(len(part_rows) != 1000 for part_rows in records.values()):
        raise SelectionError("eligibility index candidate cardinality mismatch")
    counts = Counter(record["reason"] for rows in records.values() for record in rows.values())
    groups = {record["prompt_group_sha256"] for rows in records.values() for record in rows.values()
              if record["reason"] == "metadata_eligible"}
    if (len(groups) != production["distinct_prompt_groups"]
            or counts["score_or_size"] != production["rows_excluded_by_score_or_size"]
            or counts["empty_prompt"] != production["rows_excluded_by_empty_prompt"]):
        raise SelectionError("item ledger and strict production aggregate disagree")
    return {"status": "private_metadata_eligibility_not_final_selection", "revision": REVISION,
            "production_receipt": production, "parts": records,
            "eligibility_counts": dict(sorted(counts.items())),
            "distinct_eligible_prompt_groups": len(groups), "raw_prompts_exported": False,
            "user_identifiers_read": False, "image_bytes_checked": False,
            "content_reviewed": False, "rights_cleared": False,
            "source_ids_frozen": False, "study_ids_frozen": False, "scientific_compute": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_index(args.metadata)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(json.dumps({"status": result["status"], "index_sha256": digest,
                      "parts": len(result["parts"]), "eligibility_counts": result["eligibility_counts"],
                      "distinct_eligible_prompt_groups": result["distinct_eligible_prompt_groups"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()

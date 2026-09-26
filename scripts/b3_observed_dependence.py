"""Private observed raw-byte/prompt components, not canonical independence/splits."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from b3_diffusiondb_selection import MAX_PARTS, ranked_parts
from b3_local_data_receipt import checked_bytes
from b3_raw_duplicate_groups import inventory_records, overlap_groups

ELIGIBILITY_SHA256 = "8c465e630e299a57ab7979c358a5cff614e78923a4eeceee339fa363f2a38049"


def connected_components(rows):
    """Union both edge types transitively; do not choose a representative image."""
    parents = {row["id"]: row["id"] for row in rows}
    if len(parents) != len(rows):
        raise ValueError("duplicate component input identity")

    def find(node):
        while parents[node] != node:
            parents[node] = parents[parents[node]]
            node = parents[node]
        return node

    first = {}
    for row in sorted(rows, key=lambda item: item["id"]):
        for kind, digest in (("raw", row["sha256"]), ("prompt", row["prompt_group_sha256"])):
            key = (kind, digest)  # Distinct domains, even when hex strings coincide.
            if key in first:
                left, right = find(row["id"]), find(first[key])
                parents[max(left, right)] = min(left, right)
            else:
                first[key] = row["id"]
    buckets = defaultdict(list)
    for node in sorted(parents):
        buckets[find(node)].append(node)
    result = []
    for members in sorted(buckets.values()):
        digest = hashlib.sha256(b"b3-observed-byte-prompt-component-v1\0"
                                + "\n".join(members).encode("utf-8")).hexdigest()
        result.append({"component_id": digest, "members": members})
    return result


def join_observed(records, ledger):
    raw = overlap_groups(records)  # Identity/conflicting byte metadata checks apply to all rows.
    counts = Counter()
    eligible = []
    present = set()
    for row in records:
        if not row["domain"].startswith("diffusiondb2m-part-"):
            raise ValueError("join admits only completed DiffusionDB part inventories")
        part = str(int(row["domain"].removeprefix("diffusiondb2m-part-")))
        name = row["id"].split(":", 1)[1]
        present.add(int(part))
        try:
            evidence = ledger["parts"][part][name]
        except KeyError as error:
            raise ValueError("image identity missing from bound eligibility ledger") from error
        reason = evidence["reason"]
        if reason not in ("metadata_eligible", "score_or_size", "empty_prompt"):
            raise ValueError("unknown eligibility reason")
        counts[reason] += 1
        if reason == "metadata_eligible":
            eligible.append(dict(row, prompt_group_sha256=evidence["prompt_group_sha256"]))
    components = connected_components(eligible)
    order = ranked_parts()[:MAX_PARTS]
    return {"status": "private_partial_observed_dependence_not_final_selection",
            "observed_part_ids": [p for p in order if p in present],
            "all_candidate_parts_present": present == set(order),
            "images_examined": len(records), "eligibility_counts": dict(sorted(counts.items())),
            "eligible_exact_prompt_groups": len({r["prompt_group_sha256"] for r in eligible}),
            "eligible_raw_byte_groups": len({r["sha256"] for r in eligible}),
            "eligible_observed_components": len(components),
            "multi_image_component_count": sum(len(c["members"]) > 1 for c in components),
            "components": components, "raw_duplicate_group_count_all_observed": raw["duplicate_group_count"],
            "eligible_component_coverage": len(eligible), "images_removed": 0,
            "canonical_or_near_duplicates_checked": False, "user_dependence_checked": False,
            "content_reviewed": False, "rights_cleared": False, "source_ids_frozen": False,
            "study_ids_frozen": False, "scientific_compute": False}


def bound_snapshot(path, digest):
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("snapshot exceeds declared resource ceiling")
    payload = checked_bytes(path, path.parent)
    if len(payload) > 16 * 1024 * 1024 or hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError("snapshot digest or resource ceiling mismatch")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility", required=True, type=Path)
    parser.add_argument("--inventory", required=True, action="append", type=Path)
    parser.add_argument("--sha256", required=True, action="append")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if len(args.inventory) != len(args.sha256):
        raise ValueError("one exact digest required per inventory")
    ledger = json.loads(bound_snapshot(args.eligibility, ELIGIBILITY_SHA256))
    records = []
    for path, digest in zip(args.inventory, args.sha256):
        records.extend(inventory_records(bound_snapshot(path, digest)))
    result = join_observed(records, ledger)
    result["eligibility_index_sha256"] = ELIGIBILITY_SHA256
    result["inventory_sha256"] = args.sha256
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    summary = {key: value for key, value in result.items() if key != "components"}
    summary["output_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

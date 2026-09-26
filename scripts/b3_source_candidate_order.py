"""Prospective private candidate order; never selects/approves final source IDs."""

import argparse
import hashlib
import json
import re
import uuid
from collections import defaultdict
from pathlib import Path

from b3_diffusiondb_selection import REVISION, _canonical_image_name
from b3_observed_dependence import ELIGIBILITY_SHA256, bound_snapshot


def group_rank(group):
    if not isinstance(group, str) or not re.fullmatch(r"[0-9a-f]{64}", group):
        raise ValueError("invalid prompt-group digest")
    return hashlib.sha256(b"b3-diffusiondb-source-group-v1\0" + bytes.fromhex(REVISION)
                          + bytes.fromhex(group)).hexdigest()


def member_rank(name):
    _canonical_image_name(name)
    return hashlib.sha256(b"b3-diffusiondb-source-member-v1\0" + bytes.fromhex(REVISION)
                          + uuid.UUID(name[:-4]).bytes).hexdigest()


def candidate_order(ledger):
    groups = defaultdict(list)
    seen = set()
    for part, rows in ledger["parts"].items():
        for name, evidence in rows.items():
            _canonical_image_name(name)
            if name in seen:
                raise ValueError("duplicate candidate source identity")
            seen.add(name)
            reason = evidence["reason"]
            if reason not in ("metadata_eligible", "score_or_size", "empty_prompt"):
                raise ValueError("unknown metadata eligibility reason")
            if reason != "metadata_eligible":
                continue
            group = evidence["prompt_group_sha256"]
            group_rank(group)  # Validate every included group before ranking.
            groups[group].append({"part_id": int(part), "image_name": name,
                                  "member_rank_sha256": member_rank(name)})
    ordered = []
    for group in sorted(groups, key=lambda value: (group_rank(value), value)):
        members = sorted(groups[group], key=lambda item: (item["member_rank_sha256"], item["image_name"]))
        ordered.append({"prompt_group_sha256": group, "group_rank_sha256": group_rank(group),
                        "ordered_members": members})
    return {"status": "private_prospective_source_order_not_final_ids", "revision": REVISION,
            "ranked_prompt_groups": ordered, "group_count": len(ordered),
            "eligible_member_count": sum(len(group["ordered_members"]) for group in ordered),
            "source_ids_frozen": False, "study_ids_frozen": False, "images_removed": 0,
            "content_reviewed": False, "rights_cleared": False, "scientific_compute": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    ledger = json.loads(bound_snapshot(args.eligibility, ELIGIBILITY_SHA256))
    result = candidate_order(ledger)
    if (result["group_count"] != ledger["distinct_eligible_prompt_groups"]
            or result["eligible_member_count"] != ledger["eligibility_counts"]["metadata_eligible"]):
        raise ValueError("candidate pool and bound production ledger disagree")
    result["eligibility_index_sha256"] = ELIGIBILITY_SHA256
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "group_count": result["group_count"],
                      "eligible_member_count": result["eligible_member_count"],
                      "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

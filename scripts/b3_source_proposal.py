"""Private complete-frame source proposal; not rights, splits or compute approval."""

import argparse
import hashlib
import json
from pathlib import Path

from b3_diffusiondb_selection import REVISION
from b3_observed_dependence import ELIGIBILITY_SHA256, bound_snapshot, join_observed
from b3_raw_duplicate_groups import inventory_records
from b3_source_candidate_order import candidate_order


def propose_sources(pool, records, *, target=5000):
    if isinstance(target, bool) or not isinstance(target, int) or target <= 0:
        raise ValueError("invalid source count")
    by_key = {}
    for row in records:
        part = int(row["domain"].removeprefix("diffusiondb2m-part-"))
        name = row["id"].split(":", 1)[1]
        key = (part, name)
        if key in by_key:
            raise ValueError("duplicate image identity")
        by_key[key] = row
    # Check every prospective member before consuming even the first group.
    seen = set()
    for group in pool["ranked_prompt_groups"]:
        for member in group["ordered_members"]:
            key = (member["part_id"], member["image_name"])
            if key not in by_key or key in seen:
                raise ValueError("missing or repeated prospective member")
            seen.add(key)
    chosen, skipped, raw_seen = [], [], set()
    for group in pool["ranked_prompt_groups"]:
        if len(chosen) == target:
            break
        for member in group["ordered_members"]:
            row = by_key[(member["part_id"], member["image_name"])]
            if row["sha256"] in raw_seen:
                skipped.append(dict(member, reason="selected_raw_byte_duplicate"))
                continue
            chosen.append(dict(member, raw_sha256=row["sha256"],
                               raw_size_bytes=int(row["bytes"]), width=int(row["width"]),
                               height=int(row["height"]),
                               rights_status="pending-image-rights",
                               content_status="curator_metadata_screened_not_visual_review",
                               use_limitations="local_restricted_academic_research_only_no_public_images_prompts_or_users"))
            raw_seen.add(row["sha256"])
            break
    if len(chosen) != target:
        raise ValueError("insufficient distinct sources; do not shrink commitment")
    return {"status": "private_source_proposal_requires_admission_review",
            "revision": REVISION, "proposed_source_count": target,
            "selected": chosen, "skipped_members": skipped,
            "raw_byte_duplicate_skips": len(skipped),
            "unselected_prompt_groups": pool["group_count"] - target,
            "source_ids_frozen": False, "study_ids_frozen": False,
            "rights_cleared": False, "content_visually_reviewed": False,
            "canonical_near_user_independence_proven": False,
            "scientific_compute": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility", required=True, type=Path)
    parser.add_argument("--inventory", required=True, action="append", type=Path)
    parser.add_argument("--sha256", required=True, action="append")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if len(args.inventory) != len(args.sha256) or len(args.inventory) != 14:
        raise ValueError("exactly fourteen paired complete inventories required")
    ledger = json.loads(bound_snapshot(args.eligibility, ELIGIBILITY_SHA256))
    records = []
    for path, digest in zip(args.inventory, args.sha256):
        records.extend(inventory_records(bound_snapshot(path, digest)))
    observed = join_observed(records, ledger)
    if not observed["all_candidate_parts_present"] or observed["images_examined"] != 14000:
        raise ValueError("all fourteen actual image frames required before selection")
    pool = candidate_order(ledger)
    if (pool["group_count"] != ledger["distinct_eligible_prompt_groups"] or
            pool["eligible_member_count"] != observed["eligible_component_coverage"]):
        raise ValueError("complete image/metadata prospective pool mismatch")
    result = propose_sources(pool, records)
    result.update(eligibility_index_sha256=ELIGIBILITY_SHA256,
                  inventory_sha256=args.sha256)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("selected", "skipped_members", "inventory_sha256")}
                     | {"output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

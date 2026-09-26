"""Private full-observed metadata bridge audit; not final independence or splits."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from b3_diffusiondb_selection import _canonical_image_name, _prompt_group, ranked_parts, MAX_PARTS
from b3_raw_duplicate_groups import inventory_records
from b3_local_data_receipt import checked_bytes

METADATA_SHA = "eecd341187bc91c07f5994ad0660d40228ea025616fd57a509bef8323677c68f"
MANIFEST_SHA = "5665665b51d5020df00fe1db1dc090a5e8b007c65fda65021c72c6ba709ce71b"
DEV_SHA = "7cc2a4c827fd1c64b2f6d529a3726b843a0c635077982deb87725fbc3ac7f0bc"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def private_record(row):
    name = _canonical_image_name(row["image_name"])
    prompt = _prompt_group(row["prompt"])  # Includes excluded rows; do not omit bridges.
    seed = row["seed"]
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("invalid generation seed")
    user = row["user_name"]
    # The pinned data has literal curator typo 'deleted_acount'; its schema/README
    # documents 'deleted_account'. Both mean missing identity, never a real user.
    if user is None or user in ("deleted_account", "deleted_acount"):
        producer, status = None, "unknown-or-deleted"
    elif isinstance(user, str) and re.fullmatch(r"[0-9a-f]{64}", user):
        producer, status = sha(b"b4-private-producer-v1\0" + user.encode("ascii")), "known-hash"
    else:
        raise ValueError("invalid producer metadata")
    return {"id": "diffusiondb:" + name[:-4], "part_id": row["part_id"],
            "prompt_group": prompt, "producer_group": producer, "producer_status": status,
            "prompt_seed_group": sha(b"b4-prompt-seed-v1\0" + bytes.fromhex(prompt)
                                     + seed.to_bytes(4, "big")) if prompt else None}


def components(nodes, include_producer=False):
    parents = {r["id"]: r["id"] for r in nodes}
    if len(parents) != len(nodes):
        raise ValueError("duplicate dependence node")
    def find(node):
        while parents[node] != node:
            parents[node] = parents[parents[node]]
            node = parents[node]
        return node
    first = {}
    for row in sorted(nodes, key=lambda r: r["id"]):
        keys = [("raw", row.get("raw_sha256")), ("prompt", row.get("prompt_group")),
                ("prompt-seed", row.get("prompt_seed_group"))]
        if include_producer:
            keys.append(("producer", row.get("producer_group")))
            if row.get("producer_status") == "unknown-or-deleted":
                # Conservative quarantine cohort, NOT an assertion of same real producer.
                keys.append(("unknown-producer-quarantine", "one-unresolved-cohort"))
        for kind, digest in keys:
            if digest is None:
                continue
            key = (kind, digest)
            if key in first:
                left, right = find(row["id"]), find(first[key])
                parents[max(left, right)] = min(left, right)
            else:
                first[key] = row["id"]
    groups = defaultdict(list)
    for node in sorted(parents):
        groups[find(node)].append(node)
    return sorted(groups.values())


def summarize(groups, selected, reserved):
    sizes, dev_members, dev_groups, memberships = [], 0, 0, {}
    for group in groups:
        keep = sorted(set(group) & selected)
        if not keep:
            continue
        digest = sha(b"b4-observed-component-v1\0" + "\n".join(group).encode())
        memberships[digest] = keep
        sizes.append(len(keep))
        if set(keep) & reserved:
            dev_members += len(keep); dev_groups += 1
    return {"observed_components": len(groups), "selected_components": len(sizes),
            "selected_members": sum(sizes), "largest_selected_component": max(sizes, default=0),
            "selected_multimember_components": sum(n > 1 for n in sizes),
            "selected_component_size_histogram": dict(sorted(Counter(sizes).items())),
            "forced_development_members": dev_members, "forced_development_components": dev_groups,
            "private_selected_component_memberships": memberships}


def bound(path, expected, maximum):
    if path.stat().st_size > maximum:
        raise ValueError("input resource ceiling exceeded")
    raw = checked_bytes(path, path.parent)
    if len(raw) > maximum or sha(raw) != expected:
        raise ValueError("input pin mismatch")
    return raw


def run(metadata, manifest, dev, provenance, stable_root):
    import pyarrow.parquet as pq
    metadata_bytes = bound(metadata, METADATA_SHA, 512*1024*1024)
    manifest_bytes = bound(manifest, MANIFEST_SHA, 8*1024*1024)
    dev_bytes = bound(dev, DEV_SHA, 64*1024)
    prov = json.loads(provenance.read_bytes())
    if prov["manifest_sha256"] != MANIFEST_SHA or len(prov["diffusiondb"]["parts"]) != 14:
        raise ValueError("decode provenance frame mismatch")
    parts = set(ranked_parts()[:MAX_PARTS]); nodes = {}; examined = 0
    table = pq.ParquetFile(io.BytesIO(metadata_bytes))
    for batch in table.iter_batches(batch_size=65536,
                                   columns=["image_name", "part_id", "prompt", "seed", "user_name"]):
        for row in batch.to_pylist():
            examined += 1
            if row["part_id"] not in parts:
                continue
            record = private_record(row)
            if record["id"] in nodes:
                raise ValueError("duplicate candidate metadata identity")
            nodes[record["id"]] = record
    if examined != 2000000 or len(nodes) != 14000 or Counter(r["part_id"] for r in nodes.values()) != Counter({p:1000 for p in parts}):
        raise ValueError("metadata frame cardinality mismatch")
    inventory_pins = {}
    seen = set()
    for part in prov["diffusiondb"]["parts"]:
        split = part["source_split"]; pid = int(split[5:])
        path = stable_root / (".thesis-build/b3-diffusiondb-integrity-20260926/" + split + ".csv")
        digest = part["image_inventory_sha256"]
        inventory_pins[split] = digest
        for row in inventory_records(bound(path, digest, 2*1024*1024)):
            name = row["id"].split(":", 1)[1]
            uid = "diffusiondb:" + name[:-4]
            if uid not in nodes or uid in seen or nodes[uid]["part_id"] != pid:
                raise ValueError("image-metadata full-frame mismatch")
            seen.add(uid); nodes[uid]["raw_sha256"] = row["sha256"]
    if seen != set(nodes):
        raise ValueError("incomplete image-metadata join")
    rows = list(csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8"))))
    selected = {"diffusiondb:" + r["source_id"] for r in rows if r["domain"] == "diffusiondb"}
    reserved = {"diffusiondb:" + r["source_id"] for r in json.loads(dev_bytes)["images"] if r["domain"] == "diffusiondb"}
    if len(selected) != 5000 or len(reserved) != 12 or not reserved <= selected <= set(nodes):
        raise ValueError("selected/reserved source membership mismatch")
    for row in rows:
        if row["domain"] == "diffusiondb" and nodes["diffusiondb:"+row["source_id"]]["raw_sha256"] != row["raw_sha256"]:
            raise ValueError("selected byte identity mismatch")
    content = summarize(components(list(nodes.values())), selected, reserved)
    producer = summarize(components(list(nodes.values()), True), selected, reserved)
    return {"status": "private_full_observed_metadata_bridge_not_final_splits",
            "metadata_sha256": METADATA_SHA, "manifest_sha256": MANIFEST_SHA, "dev_ids_sha256": DEV_SHA,
            "inventory_sha256": inventory_pins, "examined_metadata_rows": examined,
            "observed_candidate_images": len(nodes), "selected_images": len(selected),
            "producer_status_counts": dict(Counter(r["producer_status"] for r in nodes.values())),
            "selected_producer_status_counts": dict(Counter(nodes[n]["producer_status"] for n in selected)),
            "known_producer_count_observed": len({r["producer_group"] for r in nodes.values() if r["producer_group"]}),
            "all_row_prompt_raw_components": content, "conservative_producer_components": producer,
            "private_nodes": nodes, "raw_prompts_exported": False, "upstream_user_hashes_exported": False,
            "canonical_and_near_checked": False, "study_ids_frozen": False, "scientific_compute": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("metadata", "manifest", "dev", "provenance", "stable-root", "output"):
        parser.add_argument("--"+name, required=True, type=Path)
    a = parser.parse_args()
    if a.output.exists():
        raise ValueError("prior private output retained; use a fresh exact filename")
    result = run(a.metadata, a.manifest, a.dev, a.provenance, a.stable_root)
    with a.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, indent=2); handle.write("\n")
    summary = {k:v for k,v in result.items() if k not in ("private_nodes",)}
    for key in ("all_row_prompt_raw_components", "conservative_producer_components"):
        summary[key] = {k:v for k,v in result[key].items() if k != "private_selected_component_memberships"}
    summary["private_output_sha256"] = sha(a.output.read_bytes())
    print(json.dumps(summary, sort_keys=True))

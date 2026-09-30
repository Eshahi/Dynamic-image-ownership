"""Read-only replay of the existing B4 metadata graph for new development IDs.

No images are decoded and no method/model/metric is run. The graph is an
operational leakage screen, not certification of population independence.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path


PINS = {
    "canonical": "f867a38c0a8fce164fd01290378425ea674a9f4609061f38f7b81abb66b87b15",
    "metadata": "e54e3e4a82d7938ffbd2f6d9c77aaec0b6126dc983be19f2ae8218152a6d3d23",
    "module": "b9a1a27539c64874ac97bd7b6b993eba57f79b18af455c141f366624c8180f70",
    "splits": "60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f",
}


def bound(path, pin):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError("pinned input changed: " + str(path))
    return raw


def check(stable, reference, ids):
    stable, reference = Path(stable), Path(reference)
    canonical = [json.loads(line) for line in bound(
        stable / ".thesis-build/b4-private-canonical-20260926.jsonl", PINS["canonical"]).splitlines()]
    metadata = json.loads(bound(stable / ".thesis-build/b4-private-metadata-bridge-20260926.json", PINS["metadata"]))
    module_path = reference / "src/data/splits.py"
    bound(module_path, PINS["module"])
    module_spec = importlib.util.spec_from_file_location("existing_b4_graph", module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    bound(reference / "data/splits.csv", PINS["splits"])
    with (reference / "data/splits.csv").open(encoding="utf-8-sig", newline="") as stream:
        selected = list(csv.DictReader(stream))
    config = json.loads((reference / "configs/splits-admitted-v2.json").read_text())
    rule = config["grouping"]
    if [rule[k] for k in ("near_dhash64_max_hamming", "near_color8_mean_absolute_difference_max_rgb8", "near_aspect_relative_difference_max_percent")] != [6, 4, 5]:
        raise ValueError("operational graph rule changed")
    groups, edges = module.grouped_frame(canonical, metadata["private_nodes"], rule)
    if len(groups) != 7627 or len(canonical) != 19900:
        raise ValueError("graph replay frame differs")
    lookup = {uid: group for group in groups for uid in group["members"]}
    selected_by_id = {r["domain"] + ":" + r["source_id"]: r for r in selected}
    canonical_by_id = {r["id"]: r for r in canonical}
    rows = []
    for source_id in ids:
        uid = "ms-coco:" + str(source_id)
        group = lookup[uid]
        overlaps = [{"source_uid": selected_by_id[m]["source_uid"], "split": selected_by_id[m]["study_split"]}
                    for m in group["members"] if m in selected_by_id]
        observation = canonical_by_id[uid]
        eligible = not overlaps and observation["status"] == "canonical_pass"
        rows.append({"source_id": source_id, "group_id": group["group_id"],
                     "observed_members": group["members"], "frozen_selected_overlaps": overlaps,
                     "raw_sha256": observation["raw_sha256"],
                     "canonical_pixel_sha256": observation.get("canonical_pixel_sha256"),
                     "canonical_status": observation["status"], "eligible_for_separate_development_reservation": eligible})
    return {"status": "read_only_existing_graph_replay", "input_pins": PINS,
            "grouping_rule": rule, "observed_frame": 19900, "observed_components": len(groups),
            "edges": edges, "candidates": rows, "independence_certified": False,
            "scientific_compute": False, "frozen_splits_modified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stable", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--ids", nargs="+", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.stable, args.reference, args.ids), sort_keys=True, indent=2))

"""Pure metadata-only planned inventory; never opens external source paths.

This is neither a scientific worker nor an execution/approval manifest.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

SCHEMA = "m1-confirmatory-planned-inventory-v1"
SCHEDULE_SHA256 = "83c023bc3e0acb2a38142e8ef6e6a27f9216b7dacb5d885ab778b8799469f35d"
METHODS = ("candidate", "v5")


def object_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def validate_schedule(schedule):
    if schedule.get("schema_version") != "m1-coco512-metadata-schedule-v1":
        raise ValueError("Unknown frozen schedule schema")
    if schedule.get("candidate") != "UNRESOLVED" or any(schedule.get(k) is not False for k in
        ("source_contract_accepted", "scientific_run_authorized", "images_or_annotations_opened")):
        raise ValueError("Preparation requires unresolved candidate and locked scientific access")
    clean = schedule.get("clean")
    if not isinstance(clean, list) or len(clean) != 300:
        raise ValueError("Exactly 300 planned source representatives required")
    uids, groups = set(), set()
    for row in clean:
        if not isinstance(row, dict): raise ValueError("Malformed source metadata")
        for field in ("source_uid", "group_id", "owner", "wrong_owner"):
            if type(row.get(field)) is not str or not row[field] or "\0" in row[field]:
                raise ValueError("Missing source/group/claim metadata")
        uid, group = row["source_uid"], row["group_id"]
        if uid in uids or group in groups: raise ValueError("Duplicate source/final group")
        uids.add(uid); groups.add(group)
        hx, dec = row.get("seed_uint64_hex"), row.get("seed_uint64_decimal")
        if type(hx) is not str or not re.fullmatch("[0-9a-f]{16}", hx) or type(dec) is not str or not dec.isdecimal() or int(dec) != int(hx,16):
            raise ValueError("Exact uint64 decimal/hex seed identity required")
        if row["owner"] == row["wrong_owner"]: raise ValueError("Wrong-owner clean claim must differ")
    t3 = schedule.get("t3_source_uids")
    if not isinstance(t3,list) or len(t3) != 30 or len(set(t3)) != 30 or not set(t3) <= uids:
        raise ValueError("Exactly 30 distinct frozen T3 sources required")
    pairs = schedule.get("t4_pairs")
    if not isinstance(pairs,list) or len(pairs) != 30: raise ValueError("Exactly 30 T4 pairs required")
    endpoints = []
    for n,pair in enumerate(pairs):
        if pair.get("pair_index") != n or type(pair.get("pair_index")) is not int:
            raise ValueError("Ordered exact T4 pair indices required")
        ends = [pair.get("donor_uid"),pair.get("recipient_uid")]
        if any(x not in uids for x in ends) or ends[0] == ends[1]: raise ValueError("Invalid T4 endpoints")
        endpoints.extend(ends)
    if len(set(endpoints)) != 60: raise ValueError("Frozen T4 requires 60 distinct endpoints")
    expected_t5 = {"status":"post-approval-only", "design":"bounded disjoint30 pairs",
        "annotation_signature":"identical nonempty noncrowd COCO category sets",
        "minimum_source_phash_hamming":8, "maximum_pairs":30,
        "selection_tag":"m1-coco512-t5-v1", "no_replacement":True}
    if schedule.get("t5") != expected_t5: raise ValueError("T5 design differs from frozen draft")
    return clean


def validate_index(index, clean):
    if index.get("schema_version") != "m1-confirmatory-external-index-v1" or index.get("candidate") != "UNRESOLVED":
        raise ValueError("Unknown external index or resolved candidate")
    for flag in ("source_contract_accepted", "scientific_split_accepted", "scientific_unlock",
                 "scientific_compute_authorized", "images_annotations_features_opened"):
        if index.get(flag) is not False: raise ValueError("External index must retain locked scientific flags")
    entries = index.get("entries")
    if not isinstance(entries,list) or len(entries) != 300: raise ValueError("Index must retain all 300 sources")
    for n,(row, entry) in enumerate(zip(clean,entries)):
        if entry.get("schedule_index") != n or type(entry.get("schedule_index")) is not int:
            raise ValueError("Index order differs")
        for key in ("source_uid", "group_id", "owner", "wrong_owner", "seed_uint64_hex", "seed_uint64_decimal"):
            if entry.get(key) != row[key]: raise ValueError("External index/schedule identity differs")
    # Receipt deficiencies remain explicit blockers, never erase planned units.
    errors=index.get("input_errors")
    if not isinstance(errors,list): raise ValueError("Explicit external index error inventory required")
    return errors


def build_inventory(schedule, external_index):
    """No I/O: only versioned schedule/index metadata. No scientific parameter selection."""
    clean = validate_schedule(schedule)
    index_errors = validate_index(external_index,clean)
    by_uid = {r["source_uid"]:r for r in clean}
    source_number = {r["source_uid"]:n for n,r in enumerate(clean)}
    units = []
    def add(method, ident, row, axis, arm, kind, deps=(), owner=None, **meta):
        unit = dict(id=method+"-"+ident, source_uid=row["source_uid"], group_id=row["group_id"],
            method=method, axis=axis, arm=arm, owner=owner or row["owner"],
            seed_uint64_hex=row["seed_uint64_hex"], dependencies=list(deps), kind=kind,
            outcome="planned", reason="scientific_unlock_and_adapter_pending",
            artifact_namespace=("outputs" if kind=="image" else "metrics" if kind=="query" else "checkpoints")+"/units/"+method+"-"+ident+"/", **meta)
        units.append(unit)
        return unit["id"]
    def image_id(method,uid,arm): return f"{method}-s{source_number[uid]:03d}-{arm}"
    channels = [{"id":"VAE-mode", "attack":"VAE-posterior-mode", "attack_seed":None}] + [
        {"id":f"DDIM-s{int(strength*100):02d}-r{seed}", "attack":"SD1.5-DDIM-img2img",
         "strength":strength,"attack_seed":seed,"steps":20,"cfg":1,"eta":0,
         "positive_prompt":"","negative_prompt":"","safety_checker":"retained"}
        for strength in (.05,.1,.2,.4) for seed in (0,1,2)]
    for method in METHODS:
        for n,row in enumerate(clean):
            prefix=f"s{n:03d}"
            source=add(method,prefix+"-C0-source",row,"clean","C0-source","image", image_role="canonical-source", preprocessing="pending_frozen_adapter")
            deps=[source]
            if method == "candidate":
                init=add(method,prefix+"-initialization",row,"clean","C0-source","stage",deps,
                         stage_role="unmarked-initialization", scientific_config=None)
                deps=[init]
            c0=add(method,prefix+"-C0",row,"clean","C0","image",deps, image_role="matched-unmarked", scientific_config=None)
            c1=add(method,prefix+"-C1",row,"clean","C1","image",deps, image_role="marked", scientific_config=None)
            for label,arm,image,owner in (("source-correct","C0-source",source,row["owner"]),
                 ("matched-correct","C0",c0,row["owner"]),("marked-correct","C1",c1,row["owner"]),
                 ("marked-wrong","C1",c1,row["wrong_owner"])):
                add(method,prefix+"-q-"+label,row,"clean",arm,"query",[image],owner, claim_role=label,
                    source_cluster=row["group_id"])
        for uid in schedule["t3_source_uids"]:
            row=by_uid[uid]; n=source_number[uid]
            for arm in ("C0","C1"):
                for channel in channels:
                    prefix=f"s{n:03d}-T3-{arm}-{channel['id']}"
                    image=add(method,prefix,row,"T3",arm,"image",[image_id(method,uid,arm)],
                        attack_channel=channel, source_cluster=row["group_id"], starts_at="saved_untouched_arm")
                    for claim,owner in [("correct",row["owner"])] + ([("wrong",row["wrong_owner"])] if arm=="C1" else []):
                        add(method,prefix+"-q-"+claim,row,"T3",arm,"query",[image],owner,
                            claim_role=claim, attack_channel=channel, source_cluster=row["group_id"])
        for pair in schedule["t4_pairs"]:
            donor=by_uid[pair["donor_uid"]]; recipient=by_uid[pair["recipient_uid"]]
            for size in (128,256):
                for donor_arm in ("C1","C0"):
                    prefix=f"p{pair['pair_index']:02d}-T4-patch{size}-{donor_arm}"
                    arm="C1" if donor_arm=="C1" else "sham"
                    context=dict(pair_index=pair["pair_index"], donor_uid=donor["source_uid"],
                        recipient_uid=recipient["source_uid"], donor_group_id=donor["group_id"],
                        recipient_group_id=recipient["group_id"], donor_arm=donor_arm, patch_size=size,
                        placement="centered-identical-coordinates", blending=False, detector_feedback_queries=0)
                    image=add(method,prefix,recipient,"T4",arm,"image",
                        [image_id(method,donor["source_uid"],donor_arm),image_id(method,recipient["source_uid"],"C0-source")],**context)
                    for claim,owner in (("donor",donor["owner"]),("recipient",recipient["owner"])):
                        add(method,prefix+"-q-"+claim,recipient,"T4",arm,"query",[image],owner,
                            claim_role=claim, same_public_owner=donor["owner"]==recipient["owner"],**context)
    # All unordered pairs are metadata candidates, NOT eligible/selected scientific pairs.
    ledger=[dict(pair_id=f"T5-{a:03d}-{b:03d}", left_source_index=a,right_source_index=b,
                 eligibility=None,selected=None,reason="annotation_and_source_phash_locked")
            for a,b in itertools.combinations(range(300),2)]
    counts={method:{"clean":{"images":900,"queries":1200,"source_clusters":300},
        "T3":{"images":780,"queries":1170,"source_clusters":30,"channels_per_arm":13},
        "T4":{"images":120,"queries":240,"fixed_graph_pairs":30,"distinct_endpoint_groups":60},
        "T5":{"pair_universe":44850,"maximum_disjoint_pairs":30,"maximum_queries":120,
              "selected_pairs":None,"actual_planned_queries":None},
        "initialization_stages":300 if method=="candidate" else 0} for method in METHODS}
    result=dict(schema_version=SCHEMA,status="draft_metadata_only_not_executable",candidate="UNRESOLVED",
        scientific_unlock=False, scientific_run_authorized=False,source_contract_accepted=False,
        images_annotations_features_opened=False, methods=list(METHODS),sources=clean,counts=counts,
        units=units, total_materialized_units=len(units), t5_pair_eligibility_ledger=ledger,
        t5_post_unlock=dict(schedule=schedule["t5"],query_slots_per_pair=4,
            unmarked_endpoint_artifact="C0-source",
            endpoint_mapping="each C0-source and C1 endpoint queried against the other endpoint enrolled owner",
            human_verdict=None, selected_pair_ids=None, shortfall_policy="retain_requested30_and_all_missing_reasons"),
        scientific_config=None, external_index_errors=index_errors,
        dependency_contract="m1-worker-contract-v1 unit field projection; structural DAG only, no fixture/scientific execution plan",
        independence=dict(clean="300 operational source groups per method; same sources reused across methods",
            T3="30 source clusters; arms/seeds/severities are paired repeats",
            T4="30 graph pairs; repeated sizes/arms/claims and reused endpoint groups remain dependent",
            T5="44850 candidate pairs are dependent; at most30 disjoint selected operational group pairs"),
        blockers=["candidate/config/core freeze unresolved","source/group/rights acceptance pending",
                  "scientific approval/unlock absent","scientific adapters/budgets/rehearsals pending",
                  "T5 annotation/phash eligibility pending after scientific unlock"],
        payload_sha256=None)
    validate_inventory(result)
    result["payload_sha256"]=object_sha({k:v for k,v in result.items() if k != "payload_sha256"})
    return result


def validate_inventory(inventory):
    """Project unit identities/dependencies into existing contract to validate bounded DAG."""
    from m1_confirmatory_worker_contract import UNIT_FIELDS, validate_plan
    units=inventory["units"]
    validate_plan(dict(schema="m1-worker-contract-v1",mode="synthetic-only",candidate="UNRESOLVED",
                       units=[{k:u[k] for k in UNIT_FIELDS} for u in units]))
    if len(units) != 9120: raise ValueError("Materialized denominator differs")
    for method in METHODS:
        for axis,images,queries in (("clean",900,1200),("T3",780,1170),("T4",120,240)):
            subset=[u for u in units if u["method"]==method and u["axis"]==axis]
            if sum(u["kind"]=="image" for u in subset)!=images or sum(u["kind"]=="query" for u in subset)!=queries:
                raise ValueError("Per-method image/query denominator differs")
    ledger=inventory["t5_pair_eligibility_ledger"]
    if len(ledger)!=44850 or {(r["left_source_index"],r["right_source_index"]) for r in ledger} != set(itertools.combinations(range(300),2)):
        raise ValueError("Complete T5 pair universe required")
    if any(r["eligibility"] is not None or r["selected"] is not None for r in ledger):
        raise ValueError("No T5 scientific eligibility before unlock")
    return inventory


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule",required=True)
    parser.add_argument("--external-index",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    # Only explicit contained metadata inputs and this builder's code are read.
    root=Path(__file__).resolve().parents[1]
    expected={"schedule":root/"research/m1-confirmatory-schedule-draft.json",
              "external_index":root/"research/m1-confirmatory-external-index.json"}
    output=Path(args.output).resolve()
    if not output.is_relative_to(root/"research") or output.suffix != ".json":
        raise ValueError("New contained research metadata JSON output required")
    if output.exists(): raise ValueError("New output only; retained file overwrite refused")
    receipts={}
    values=[]
    for role,name in (("schedule",args.schedule),("external_index",args.external_index)):
        path=Path(name).resolve()
        if path != expected[role]: raise ValueError("Only the two declared contained metadata inputs")
        raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
        if role=="schedule" and digest!=SCHEDULE_SHA256: raise ValueError("Exact frozen schedule hash required")
        receipts[role]=dict(path=str(path),sha256=digest,size_bytes=len(raw))
        values.append(json.loads(raw))
    result=build_inventory(*values)
    receipts["builder"]=dict(path=__file__,sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    for name in ("research/m1-confirmatory-draft.md", "research/m1-confirmatory-interface.md",
                 "scripts/m1_confirmatory_worker_contract.py", "scripts/m1_confirmatory_t5_pairs.py"):
        raw=(root/name).read_bytes()
        receipts[name]=dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),size_bytes=len(raw))
    result["provenance"]=dict(inputs=receipts,command=[sys.executable,*sys.argv],
        raw_paths_followed=False,annotation_values_opened=False,features_opened=False)
    # Structural payload excludes command/receipt envelope, enabling exact deterministic rebuilds.
    result["payload_sha256"]=object_sha({k:v for k,v in result.items() if k not in ("payload_sha256","provenance")})
    output.write_text(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(output=str(output),units=len(result["units"]),T5_metadata_pairs=len(result["t5_pair_eligibility_ledger"]),scientific_unlock=False)))
    return 0

if __name__=="__main__": raise SystemExit(main())

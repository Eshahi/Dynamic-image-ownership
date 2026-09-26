"""Prospective canonical source admission using existing ordered COCO reserves.

Preserves original engineering artifacts/rejects and every development reservation.
No scientific result, source-rights certification or compute approval is produced.
"""
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path

from b4_metadata_dependence import MANIFEST_SHA, DEV_SHA, bound, sha
from build_b4_splits import CANONICAL_SUMMARY_SHA
from build_b3_manifest import COCO_SHA, LOCAL, manifest_row
from validate_data_manifest import FIELDS, validate


def admit(original, candidates, canonical, reserved, target=1000):
    ordered=candidates["candidates"]+candidates["ordered_reserves"]
    ids=[r["source_id"] for r in ordered]
    if len(ids)!=len(set(ids)):
        raise ValueError("duplicate candidate identities")
    old_coco={r["source_id"]:r for r in original if r["domain"]=="ms-coco"}
    if set(old_coco)!={r["source_id"] for r in candidates["candidates"]} or len(old_coco)!=target:
        raise ValueError("original COCO candidates mismatch")
    for item in ordered:
        observed=canonical["ms-coco:"+item["source_id"]]
        if (item["raw_sha256"]!=observed["raw_sha256"] or
            [item["width"],item["height"]]!=[observed["source_width"],observed["source_height"]]):
            raise ValueError("candidate canonical identity/dimension mismatch")
        if observed["status"] not in ("canonical_pass","canonical_rejected_coverage_failure"):
            raise ValueError("unknown canonical admission status")
        if observed["status"]!="canonical_pass" and not observed.get("reason"):
            raise ValueError("missing rejection evidence")
        if item["source_id"] in old_coco:
            old=old_coco[item["source_id"]]
            if old["raw_sha256"]!=item["raw_sha256"] or old["relative_path"]!=item["relative_path"]:
                raise ValueError("original candidate source mismatch")
    accepted=[r for r in ordered if canonical["ms-coco:"+r["source_id"]]["status"]=="canonical_pass"][:target]
    if len(accepted)!=target:
        raise ValueError("insufficient canonical-admissible candidates; no relaxed policy")
    chosen={r["source_id"] for r in accepted}
    rows=[dict(r) for r in original if r["domain"]!="ms-coco"]
    for item in accepted:
        if item["source_id"] in old_coco:
            rows.append(dict(old_coco[item["source_id"]]))
        else:
            rows.append(manifest_row("ms-coco","coco-2017","val2017",item["source_id"],
                item["relative_path"],item["raw_sha256"],item["raw_size_bytes"],item["width"],item["height"],
                "https://images.cocodataset.org/zips/val2017.zip",
                item["license_reference"].replace("http://","https://",1),
                LOCAL+"; recorded image license_id="+str(item["license_id"])+
                "; annotation license is not image ownership; original archive identity unproved; creator/title/public attribution pending"))
    index={(r["domain"],r["source_id"]):r for r in rows}
    for item in reserved:
        observed=index.get((item["domain"],item["source_id"]))
        if observed is None or any(observed[k]!=item[k] for k in
                ("release_id","source_split","relative_path","raw_sha256","group_id")):
            raise ValueError("original development reservation changed or excluded")
    if len(rows)!=len(index) or len({r["raw_sha256"] for r in rows})!=len(rows):
        raise ValueError("duplicate admitted source identity/raw bytes")
    exclusions=[{"source_id":r["source_id"],"raw_sha256":r["raw_sha256"],
                 "reason":canonical["ms-coco:"+r["source_id"]]["reason"],
                 "was_original_candidate":r["source_id"] in old_coco}
                for r in ordered if canonical["ms-coco:"+r["source_id"]]["status"]!="canonical_pass"]
    replacements=[{"source_id":r["source_id"],"raw_sha256":r["raw_sha256"],
                   "ordered_reserve_index":ids.index(r["source_id"])-target}
                  for r in accepted if r["source_id"] not in old_coco]
    if any(r["source_id"] not in chosen for r in reserved if r["domain"]=="ms-coco"):
        raise ValueError("development candidate excluded")
    return sorted(rows,key=lambda r:(r["domain"],r["source_split"],r["source_id"])),exclusions,replacements


def output_json(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(value,handle,sort_keys=True,indent=2,allow_nan=False);handle.write("\n")


def run(manifest,dev,coco,canonical,summary,asset_root,output_root):
    names=("source-manifest.csv","development-reservation.json","admission.json")
    if any((output_root/name).exists() for name in names):
        raise ValueError("existing admission artifacts retained")
    old_raw=bound(manifest,MANIFEST_SHA,8*1024*1024)
    dev_raw=bound(dev,DEV_SHA,64*1024)
    coco_raw=bound(coco,COCO_SHA,2*1024*1024)
    summary_raw=bound(summary,CANONICAL_SUMMARY_SHA,64*1024)
    evidence=json.loads(summary_raw)
    canonical_raw=bound(canonical,evidence["output_sha256"],32*1024*1024)
    observations=[json.loads(line) for line in canonical_raw.splitlines()]
    index={r["id"]:r for r in observations}
    if len(index)!=19900 or len(observations)!=19900:
        raise ValueError("full observed canonical frame required")
    original=list(csv.DictReader(io.StringIO(old_raw.decode())))
    old_dev=json.loads(dev_raw); candidates=json.loads(coco_raw)
    if len(candidates["candidates"])!=1000 or len(candidates["ordered_reserves"])!=274:
        raise ValueError("candidate/reserve commitments differ")
    rows,exclusions,replacements=admit(original,candidates,index,old_dev["images"])
    if Counter(r["domain"] for r in rows)!={"ms-coco":1000,"div2k":900,"diffusiondb":5000}:
        raise ValueError("source counts changed")
    buffer=io.StringIO(newline="");writer=csv.DictWriter(buffer,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader();writer.writerows(rows);payload=buffer.getvalue().encode()
    new_dev={**old_dev,"manifest_sha256":sha(payload),"original_reservation_sha256":DEV_SHA,
             "selection_rerun":False,"original_32_identities_preserved":True}
    output_root.mkdir(parents=True,exist_ok=True)
    with (output_root/"source-manifest.csv").open("xb") as handle: handle.write(payload)
    # Fresh local byte validation is not canonical reprocessing or scientific compute.
    check=validate(output_root/"source-manifest.csv",asset_root)
    output_json(output_root/"development-reservation.json",new_dev)
    receipt={"status":"prospective_canonical_source_admission_pending_independent_review",
             "original_manifest_sha256":MANIFEST_SHA,"original_dev_sha256":DEV_SHA,
             "candidate_sha256":COCO_SHA,"canonical_summary_sha256":CANONICAL_SUMMARY_SHA,
             "canonical_inventory_sha256":evidence["output_sha256"],
             "manifest_sha256":sha(payload),
             "development_reservation_sha256":sha((output_root/"development-reservation.json").read_bytes()),
             "source_count":6900,"counts_by_domain":dict(Counter(r["domain"] for r in rows)),
             "exclusions":exclusions,"replacements":replacements,
             "rule":"first1000_canonical_pass_in_existing_full_candidate_then_reserve_order_before_method_outcomes",
             "source_eligibility_rule_changed":False,"original_development_ids_preserved":True,
             "original_artifacts_and_rejects_preserved":True,"local_byte_validation":check,
             "rights_cleared":False,"scientific_split_accepted":False,"scientific_compute_authorized":False}
    output_json(output_root/"admission.json",receipt)
    print(json.dumps({"manifest_sha256":receipt["manifest_sha256"],
                      "development_reservation_sha256":receipt["development_reservation_sha256"],
                      "admission_sha256":sha((output_root/"admission.json").read_bytes()),
                      "exclusions":exclusions,"replacements":replacements,"validation":check},sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","dev","coco","canonical","summary","asset-root","output-root"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args();run(args.manifest,args.dev,args.coco,args.canonical,args.summary,args.asset_root,args.output_root)

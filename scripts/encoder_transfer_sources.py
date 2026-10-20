"""Freeze development source IDs and recorded hashes, without opening any image.

This stage-1 helper reads metadata receipts only. It never traverses image pools.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
DOCS = ROOT / "research/journal-upgrade-20261009"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(n=60):
    if not 60 <= n <= 120:
        raise ValueError("Stage-1 n is restricted to 60..120")
    first = read(DOCS/"fresh-development-selection.json")
    registry = read(DOCS/"registry-fresh-development-selection.json")
    round3 = read(DOCS/"round3-development-selection.json")
    inputs = [DOCS/"fresh-development-inputs.json",
              MAIN/".thesis-build/assets/registry-fresh-20261016/sources.json",
              MAIN/".thesis-build/assets/registry-round3-20261017/sources-ready.json"]
    receipts = {}
    for path in inputs:
        receipts.update({int(r["source_id"]):r for r in read(path)["sources"]})
    identities, hashes = set(), set(first["raw_sha256_exclusions"])
    def inspect(value):
        if isinstance(value, dict):
            for key,item in value.items():
                if key in ("source_id","coco_id") and str(item).isdigit() and value.get("domain","ms-coco") == "ms-coco":
                    identities.add(int(item))
                if key in ("source_ids","fixed_twelve_ids") and isinstance(item,list):
                    identities.update(int(i) for i in item if str(i).isdigit())
                if "sha256" in key and isinstance(item,str) and re.fullmatch("[0-9a-f]{64}",item):
                    hashes.add(item)
                inspect(item)
        elif isinstance(value,list):
            for item in value:
                inspect(item)
        elif isinstance(value,str):
            identities.update(int(m.group(1)) for m in re.finditer(r"ms-coco:coco-2017:(?:train2017|val2017):(\d+)",value))
    inventories=[]
    paths=[Path(x["path"]) for x in first["exclusion_inventories"]]
    paths += [ROOT/"research/registry-confirmation/heldout-index.json",
              ROOT/"research/registry-confirmation/div2k-heldout-index.json",
              MAIN/".thesis-build/assets/registry-fresh-20261016/m2-supplemental-exclusions.json"]
    for path in paths:
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig",newline="") as handle:
                value=list(csv.DictReader(handle))
        else:
            value=read(path)
        inspect(value)
        inventories.append(dict(path=str(path),sha256=sha(path),access="metadata identity/hash only"))
    ordered = sorted(first["selected"],key=lambda r:int(r["source_id"]))
    existing={int(s["source_id"]) for s in ordered}
    for pool in (registry,round3):
        for s in sorted(pool["selected"],key=lambda r:int(r["source_id"])):
            if int(s["source_id"]) not in existing:
                ordered.append(s)
                existing.add(int(s["source_id"]))
    chosen, exclusions=[],[]
    for row in ordered:
        sid=int(row["source_id"])
        receipt=receipts.get(sid)
        if receipt is None:
            raise ValueError(f"Missing prior acquisition metadata for {sid}; no outcome-based substitution")
        png=receipt.get("canonical_png_sha256",receipt.get("sha256"))
        pixel=receipt["canonicalization"]["rgb8_sha256"]
        raw=receipt["raw_sha256"]
        if sid in identities or {raw,png,pixel} & hashes:
            exclusions.append(dict(source_id=sid,reason="identity or recorded-hash exclusion"))
            if sid in {int(s["source_id"]) for s in first["selected"]}:
                raise ValueError(f"Required first-24 source {sid} conflicts with a reserved index")
            continue
        if any(not re.fullmatch("[0-9a-f]{64}",h or "") for h in (raw,png,pixel)):
            raise ValueError(f"Missing raw/canonical/pixel identity for {sid}")
        chosen.append(dict(source_id=sid,source_uid=row["source_uid"],data_split="development",
                           url=row["url"],filename=row["filename"],license=row["license"],
                           license_url=row["license_url"],flickr_attribution_hook=row["flickr_attribution_hook"],
                           raw_sha256=raw,canonical_png_sha256=png,rgb8_sha256=pixel,
                           raw_bytes=receipt["size_bytes"],canonicalization="m1b-canonical-rgb512-v2"))
        if len(chosen)==n+2:
            break
    if len(chosen)!=n+2:
        raise ValueError("Insufficient fixed-order sources and disjoint smoke sources")
    return dict(schema="encoder-transfer-sources-v1",data_split="development",n=n,
                rule="All original24, then ascending numeric source_id from registry60, then round3 if needed; two next eligible IDs for smoke",
                sources=chosen[:n],smoke=chosen[n:],excluded=exclusions,
                metadata_only=True,image_files_opened=0,
                acquisition_receipts=[dict(path=str(p),sha256=sha(p)) for p in inputs],
                exclusion_inventories=inventories,excluded_identity_count=len(identities),excluded_hash_count=len(hashes))


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n",type=int,default=60)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=freeze(a.n)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(dict(n=a.n,smoke=[r["source_id"] for r in result["smoke"]],sha256=sha(a.output),images_opened=0)))

"""Fresh development cohort for the F7 registry replication (f7c), chosen by a rule fixed before any download.

  --mode select    metadata only: the next 128 eligible COCO train2017 IDs strictly above 4020 (round 3's last ID),
                   under the original rule (CC BY 2.0 licence id 4, shorter side >= 256, train2017 URL, Flickr hook),
                   excluding every identity, Flickr photo and recorded hash in all prior inventories.
  --mode acquire   download, raw-hash check before decoding, m1b-canonical-rgb512-v2, PNG/pixel-hash check.
  --mode manifest  Stage S schema: order by SHA-256(prefix + source_uid); first 64 donors (records), next 64 targets
                   (copy-paste hosts). Rehearsal rows are the Stage S rehearsal rows, unchanged (smoke test only).

No image content, caption, category or outcome informs selection, ordering or the donor/target split.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
DOCS = ROOT / "research/journal-upgrade-20261009"
HERE = ROOT / "research/f7-dual-carrier-20261102/replication"
FLOOR, COUNT, DONORS = 4020, 128, 64
PREFIX = "f7c-replication-v1/20261107/"
STAGE_S = ROOT / "research/tifs-20261028/stage-s/source-manifest.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventories():
    prior = json.loads((DOCS / "fresh-development-selection.json").read_text(encoding="utf-8"))
    paths = [Path(x["path"]) for x in prior["exclusion_inventories"]]
    paths += [DOCS / n for n in ("fresh-development-inputs.json", "fresh-development-selection.json",
                                 "registry-fresh-development-selection.json", "round3-development-selection.json",
                                 "registry-near-duplicate-selection.json", "round3-near-duplicate-selection.json")]
    paths += [ROOT / "research/encoder-transfer-20261019/source-list.json", STAGE_S,
              ROOT / "research/tifs-20261028/stage-p/source-manifest.json"]
    paths += sorted((MAIN / ".thesis-build/assets").glob("*/acquisition.jsonl"))
    paths += sorted((MAIN / ".thesis-build/assets").glob("*/acquisition-config.json"))
    return prior, paths


def scan(paths):
    """Identities, Flickr photo IDs and 64-hex hashes in every inventory (the registry_fresh_sources rule)."""
    ids, flickr, hashes, read = set(), set(), set(), []

    def inspect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ("source_id", "coco_id") and str(item).isdigit() and value.get("domain", "ms-coco") == "ms-coco":
                    ids.add(int(item))
                if key in ("source_ids", "fixed_twelve_ids") and isinstance(item, list):
                    ids.update(int(x) for x in item if str(x).isdigit())
                if "sha256" in key and isinstance(item, str) and re.fullmatch("[0-9a-f]{64}", item):
                    hashes.add(item)
                if key == "flickr_photo_id" and str(item).isdigit():
                    flickr.add(str(item))
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
        elif isinstance(value, str):
            for m in re.finditer(r"(?:ms-coco:coco-2017:(?:train2017|val2017):|(?:train2017|val2017)/)(\d+)", value):
                ids.add(int(m.group(1)))
            m = re.search(r"/([0-9]+)_[^/]+\.(?:jpg|png)", value)
            if m and "flickr" in value:
                flickr.add(m.group(1))

    for path in paths:
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as f:
                data = list(csv.DictReader(f))
        elif path.suffix == ".jsonl":
            data = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        inspect(data)
        read.append(dict(path=str(path), sha256=digest(path)))
    for name in ("fresh-development-selection.json", "registry-fresh-development-selection.json",
                 "round3-development-selection.json"):
        hashes.update(json.loads((DOCS / name).read_text(encoding="utf-8")).get("raw_sha256_exclusions", []))
    return ids, flickr, hashes, read


def select(out):
    prior, paths = inventories()
    ids, flickr, hashes, read = scan(paths)
    meta = Path(prior["source_metadata"]["path"])
    raw = meta.read_bytes()
    if hashlib.sha256(raw).hexdigest() != prior["source_metadata"]["sha256"]:
        raise ValueError("COCO metadata changed")
    text = raw.decode("utf-8")
    images, _ = json.JSONDecoder().raw_decode(text, re.search(r'"images"\s*:\s*', text).end())
    selected = []
    for image in sorted(images, key=lambda x: x["id"]):
        sid, hook = image["id"], image.get("flickr_url", "")
        photo = re.search(r"/([0-9]+)_[^/]+\.", hook)
        if sid <= FLOOR or sid in ids or image.get("license") != 4:
            continue
        if min(image["width"], image["height"]) < 256 or not photo or photo.group(1) in flickr:
            continue
        url = image.get("coco_url", "")
        if not url.startswith("http://images.cocodataset.org/train2017/"):
            continue
        selected.append(dict(source_id=sid, source_uid=f"ms-coco:coco-2017:train2017:{sid}", filename=image["file_name"],
                             url=url.replace("http://images.cocodataset.org/", "https://s3.amazonaws.com/images.cocodataset.org/"),
                             original_coco_url=url, license_id=4, license="CC BY 2.0",
                             license_url="https://creativecommons.org/licenses/by/2.0/", flickr_attribution_hook=hook,
                             flickr_photo_id=photo.group(1), width=image["width"], height=image["height"]))
        flickr.add(photo.group(1))
        if len(selected) == COUNT:
            break
    if len(selected) != COUNT:
        raise ValueError("Too few eligible identities")
    doc = dict(schema="f7c-fresh-selection-v1", prepared_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               selection_rule=f"Next {COUNT} eligible ascending train2017 IDs strictly >{FLOOR} (round 3's last ID); "
                              "original licence/dimension/URL/Flickr rule unchanged; every identity, Flickr photo and "
                              "recorded hash in the listed inventories excluded. Metadata only.",
               source_metadata=prior["source_metadata"], exclusion_inventories=read, excluded_identity_count=len(ids),
               excluded_flickr_count=len(flickr) - COUNT, raw_sha256_exclusions=sorted(hashes),
               images_downloaded=0, selected=selected)
    HERE.mkdir(parents=True, exist_ok=True)
    path = HERE / "fresh-selection.json"
    if path.exists():
        raise ValueError("Selection already fixed; refuse to overwrite")
    path.write_bytes((json.dumps(doc, indent=1) + "\n").encode())
    print(json.dumps(dict(selected=[r["source_id"] for r in selected], excluded_ids=len(ids), hashes=len(hashes))))


def acquire(out):
    sys.path.insert(0, str(ROOT / "scripts"))
    from m1b_canonical_source import canonicalize
    from PIL import Image
    sel = json.loads((HERE / "fresh-selection.json").read_text(encoding="utf-8"))
    hashes = set(sel["raw_sha256_exclusions"])
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "canonical").mkdir(exist_ok=True)
    log = out / "acquisition.jsonl"
    done = {}
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            e = json.loads(line)
            if e.get("kind") == "prepared":
                done[e["receipt"]["source_id"]] = e["receipt"]
    receipts = []
    for row in sel["selected"]:
        if row["source_id"] in done:
            receipts.append(done[row["source_id"]])
            continue
        raw_path = out / "raw" / row["filename"]
        if not raw_path.exists():
            with urllib.request.urlopen(row["url"], timeout=60) as r:
                data = r.read()
            raw_path.write_bytes(data)
        raw = raw_path.read_bytes()
        raw_hash = hashlib.sha256(raw).hexdigest()
        event = dict(kind="prepared", receipt=None)
        if raw_hash in hashes:
            event = dict(kind="excluded", source_id=row["source_id"], reason="raw SHA-256 in exclusions; no substitution")
        else:
            rgb, canon = canonicalize(raw, raw_hash)
            buf = io.BytesIO()
            Image.fromarray(rgb).save(buf, format="PNG")
            png = buf.getvalue()
            png_hash, pixel_hash = hashlib.sha256(png).hexdigest(), hashlib.sha256(rgb.tobytes()).hexdigest()
            if png_hash in hashes or pixel_hash in hashes:
                event = dict(kind="excluded", source_id=row["source_id"], reason="canonical hash in exclusions; no substitution")
            else:
                path = out / "canonical" / f"{row['source_id']}.png"
                path.write_bytes(png)
                hashes.update((raw_hash, png_hash, pixel_hash))
                event["receipt"] = dict(row, raw_sha256=raw_hash, raw_bytes=len(raw), canonical_png_sha256=png_hash,
                                        rgb8_sha256=pixel_hash, canonicalization="m1b-canonical-rgb512-v2",
                                        canonical_receipt=canon, data_split="development", development_reserved=True)
                receipts.append(event["receipt"])
        with log.open("ab") as f:
            f.write((json.dumps(event) + "\n").encode())
        print(event["kind"], row["source_id"], flush=True)
    (out / "sources.json").write_bytes((json.dumps(dict(schema="f7c-fresh-acquired-v1",
        selection_sha256=digest(HERE / "fresh-selection.json"), sources=receipts), indent=1) + "\n").encode())
    print(len(receipts), "acquired of", len(sel["selected"]))


def manifest(out):
    acquired = json.loads((out / "sources.json").read_text(encoding="utf-8"))["sources"]
    stage_s = json.loads(STAGE_S.read_text(encoding="utf-8"))
    keep = ("source_id", "source_uid", "filename", "license", "license_url", "flickr_attribution_hook", "raw_sha256",
            "raw_bytes", "canonical_png_sha256", "rgb8_sha256", "canonicalization", "data_split")
    rows = sorted(({k: r[k] for k in keep} for r in acquired),
                  key=lambda r: hashlib.sha256((PREFIX + r["source_uid"]).encode()).hexdigest())
    if len(rows) < 2 * DONORS:
        raise ValueError("Fewer acquired sources than the fixed donor and target counts")
    doc = dict(schema="tifs-stage-s-sources-v1", data_split="development", held_out_allowed=False,
               selection_prefix=PREFIX, source_file="research/f7-dual-carrier-20261102/replication/fresh-selection.json",
               source_file_sha256=digest(HERE / "fresh-selection.json"),
               selection_rule=f"Sort acquired fresh sources ascending SHA256 UTF8(selection_prefix + source_uid); first "
                              f"{DONORS} screen donors, next {DONORS} screen targets; rehearsal rows are the Stage S "
                              "rehearsal rows; no image or outcome inspection.",
               group_counts=[DONORS, DONORS, 2, 2], screen_donors=rows[:DONORS], screen_targets=rows[DONORS:2 * DONORS],
               rehearsal_donors=stage_s["rehearsal_donors"], rehearsal_targets=stage_s["rehearsal_targets"],
               targets_human_distinctness="MISSING; identifier/hash distinctness only")
    path = HERE / "source-manifest.json"
    if path.exists():
        raise ValueError("Manifest already fixed; refuse to overwrite")
    path.write_bytes((json.dumps(doc, indent=1) + "\n").encode())
    print(path, digest(path))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("select", "acquire", "manifest"), required=True)
    ap.add_argument("--out", type=Path, default=MAIN / ".thesis-build/assets/f7c-fresh-20261107")
    a = ap.parse_args()
    dict(select=select, acquire=acquire, manifest=manifest)[a.mode](a.out)


if __name__ == "__main__":
    main()

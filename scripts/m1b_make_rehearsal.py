"""Synthetic, test-shaped rehearsal inputs for the M1b worker (rehearsal tier; no study image is read).

    python scripts/m1b_make_rehearsal.py data        # images + annotations under .thesis-build/rehearsal, indexes in research/rehearsal
    python scripts/m1b_make_rehearsal.py approve --manifest M --out A   # delegated rehearsal approval, refused for non-rehearsal plans

Images are generated (smooth colour fields, shapes, mild noise) as JPEGs of mixed sizes with EXIF
orientations, an embedded sRGB ICC profile, grayscale and CMYK cases. A synthetic COCO-format
annotation file gives shared category signatures (so T5 has eligible pairs), one empty signature and
one image missing from the annotations. Index entries use the same schema as the held-out index.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import m1b_coco512_worker as W  # noqa: E402

OUT = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/rehearsal/m1b-synthetic")
SIZES = [(640, 480), (480, 640), (500, 375), (427, 640), (640, 427), (612, 612), (640, 360), (375, 500)]


def image(i: int):
    import numpy as np
    from PIL import Image, ImageDraw
    w, h = SIZES[i % len(SIZES)]
    rng = np.random.default_rng(1000 + i)
    y, x = np.mgrid[0:h, 0:w] / max(w, h)
    rgb = np.zeros((h, w, 3))
    for c in range(3):
        for _ in range(4):
            fx, fy, ph = rng.uniform(0.5, 4, 2).tolist() + [rng.uniform(0, 6.3)]
            rgb[..., c] += rng.uniform(20, 50) * np.sin(2 * np.pi * (fx * x + fy * y) + ph)
        rgb[..., c] += rng.uniform(70, 180)
    img = Image.fromarray(np.clip(rgb + rng.normal(0, 4, rgb.shape), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x0, y0 = int(rng.uniform(0, w - 60)), int(rng.uniform(0, h - 60))
        box = [x0, y0, x0 + int(rng.uniform(30, w / 3)), y0 + int(rng.uniform(30, h / 3))]
        fill = tuple(int(v) for v in rng.integers(0, 256, 3))
        (d.ellipse if rng.random() < .5 else d.rectangle)(box, fill=fill)
    return img


def encode(i: int, img) -> bytes:
    from PIL import Image, ImageCms
    kw = dict(format="JPEG", quality=90)
    if i % 7 == 3:
        img = img.convert("L")
    elif i % 11 == 5:
        img = img.convert("CMYK")
    if img.mode == "RGB" and i % 5 == 1:
        kw["icc_profile"] = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    if i % 4:
        exif = Image.Exif()
        exif[274] = (1, 3, 6, 8)[i % 4]
        kw["exif"] = exif
    buf = io.BytesIO()
    img.save(buf, **kw)
    return buf.getvalue()


def make_data(n: int, small: int) -> None:
    from m1_confirmatory_schedule import rank
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    entries, images, annotations = [], [], []
    for i in range(n):
        image_id = 900000 + i
        uid = f"rehearsal-synthetic:coco-2017:val2017:{image_id}"
        raw = encode(i, image(i))
        path = OUT / "raw" / f"{image_id:012d}.jpg"
        path.write_bytes(raw)
        owner, wrong = W.owner_pair(uid)
        entries.append(dict(schedule_index=i, source_uid=uid, group_id=f"rehearsal-group-{i:03d}", owner=owner,
                            wrong_owner=wrong, external_raw_path=str(path).replace("\\", "/"),
                            raw_sha256=hashlib.sha256(raw).hexdigest(), raw_size_bytes=len(raw)))
        if i != n - 1:  # the last image is absent from the annotations
            images.append(dict(id=image_id, file_name=path.name))
        if i % 9 != 8:  # every ninth image has an empty signature
            for k, cat in enumerate((1 + i % 3, 10 + i % 2)):
                annotations.append(dict(id=image_id * 10 + k, image_id=image_id, category_id=cat, iscrowd=0))
            annotations.append(dict(id=image_id * 10 + 9, image_id=image_id, category_id=77, iscrowd=1))
    ann = json.dumps(dict(images=images, annotations=annotations, categories=[], info=dict(synthetic=True))).encode()
    (OUT / "instances_synthetic.json").write_bytes(ann)
    (ROOT / "research/rehearsal").mkdir(parents=True, exist_ok=True)
    for name, subset in (("full", entries), ("small", entries[:small])):
        index = dict(schema_version="m1b-rehearsal-index-v1", status="synthetic rehearsal data, not a study cohort",
                     entries=subset)
        (ROOT / f"research/rehearsal/m1b-synthetic-{name}-index.json").write_bytes((json.dumps(index, indent=1) + "\n").encode())
        uids = [e["source_uid"] for e in subset]
        k = max(1, len(uids) // 3)
        t3 = sorted(uids, key=lambda u: rank("m1-coco512-t3-v1", u))[:k]
        t4 = sorted(uids, key=lambda u: rank("m1-coco512-t4-v1", u))[:2 * k]
        print(name, len(uids), "sources; T3", len(t3), "; T4 pairs", len(t4) // 2,
              "; annotation sha", hashlib.sha256(ann).hexdigest())


def approve(manifest_path: str, out: str) -> None:
    """Write a delegated approval for a rehearsal manifest only (synthetic data, rehearsal tier)."""
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    hit = next(i for i in m["inputs"] if i["path"].endswith(".m1b-plan.json"))
    plan = json.loads((ROOT / hit["path"]).read_text(encoding="utf-8"))
    if plan["data_split"] != "rehearsal" or m["datasets"][0]["split"] != "rehearsal":
        raise SystemExit("delegated approvals are written only for rehearsal-split manifests")
    W.validate_plan(plan)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    approval = dict(schema_version="1.0", experiment_id=m["experiment_id"], run_id=m["run_id"], execution_target="local",
                    manifest_sha256=W.object_digest(m), decision="approve",
                    timestamp=(now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
                    expires_at=(now + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
                    max_seconds=m["budget"]["max_seconds"], max_usd=0,
                    actor="delegated:Claude Code agent (rehearsal tier, synthetic data only) under user standing decision 2026-10-02",
                    source_ref="research/approval-policy.md rehearsal tier; no study image")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(approval, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(dict(approval=out, approval_sha256=W.object_digest(approval)), indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("data")
    d.add_argument("--n", type=int, default=16)
    d.add_argument("--small", type=int, default=4)
    p = sub.add_parser("approve")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    make_data(a.n, a.small) if a.cmd == "data" else approve(a.manifest, a.out)


if __name__ == "__main__":
    main()

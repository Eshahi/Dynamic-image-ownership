"""Independent recheck of T0, T3, T4, TQ and the T4 event from Codex's raw outputs and the original images."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

import numpy as np
from PIL import Image

RD = Path(r"C:\Users\Soroush\.codex\worktrees\codex-f5-components\research\f5-components-20261101")
MAIN = Path(r"W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5")
sys.path.insert(0, str(RD / "judge"))
from loss_budget import OWNER, load  # noqa: E402


def spearman(a, b):
    def rank(x):
        x = np.asarray(x, float)
        order = np.argsort(x)
        r = np.zeros(len(x))
        r[order] = np.arange(len(x))
        for v in np.unique(x):
            m = x == v
            r[m] = r[m].mean()
        return r
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


rows = load()
sources = sorted({x["source_id"] for x in rows.values() if x.get("channel") == "clean"})
split = {s: "DESIGN" if j % 2 == 0 else "EVALUATE" for j, s in enumerate(sources)}

print("== T4: writer margin vs mean foreign decoded score")
meta = {}
for r in csv.DictReader(open(RD / "results/wp1-writer-metadata/sources.csv", encoding="utf-8", newline="")):
    meta[int(r["source"] if "source" in r else r["source_id"])] = r
print("  metadata columns", list(next(iter(meta.values())).keys())[:14])
scores = defaultdict(list)
for x in rows.values():
    if x.get("arm") != "f5-r2" or x.get("status") != "ok":
        continue
    if (x.get("channel"), x.get("strength")) in (("R1", 0.1), ("R1", 0.2), ("R1", 0.4), ("R3", 0.2)):
        call = x["detections"].get("f5-r2", {}).get(OWNER)
        if call and call.get("status") == "ok":
            scores[x["source_id"]].append(call["raw"]["semantic"]["decoded_score"])
key = next(k for k in next(iter(meta.values())) if "median" in k.lower() and "margin" in k.lower())
for half in ("DESIGN", "EVALUATE"):
    s = [v for v in sources if split[v] == half]
    m = [float(meta[v][key]) for v in s]
    y = [float(np.mean(scores[v])) for v in s]
    cut = median(float(meta[v][key]) for v in sources if split[v] == "DESIGN")
    hi = [b for a, b in zip(m, y) if a >= cut]
    lo = [b for a, b in zip(m, y) if a < cut]
    print(f"  {half}: rho {spearman(m, y):.4f} cut {cut:.4f} high {len(hi)} low {len(lo)} gap {np.mean(hi) - np.mean(lo):+.4f}")

print("\n== T3: medians recomputed from T3-pairs.csv")
tp = list(csv.DictReader(open(RD / "results/wp4-pixel-summary/T3-pairs.csv", encoding="utf-8", newline="")))
print("  columns", list(tp[0].keys()))
print("  first row", {k: tp[0][k] for k in list(tp[0].keys())[:14]})

print("\n== the T4 event: same-owner residual moved onto another image")
event = None
for path in sorted((RD / "results/wp4-pixels").glob("f5-r2-*.jsonl")):
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        if row.get("id") == "t4-residual-177015-25394-0.5":
            event = row
call = next(c for c in event["calls"] if c["role"] == "marked")
raw = call["raw"]
i, s = raw["instance"], raw["semantic"]
d_i = bin(int(i["decoded_code"], 16) ^ int(raw["perceptual_hash"], 16)).count("1")
print("  outcome", raw["outcome"], "instance candidate", i["candidate"], "read", i["read"], "found", i["found"], "content", i["content_status"])
print("  decoded", round(i["decoded_score"], 4), "threshold", round(i["decoded_threshold"], 4), "recomputed", round(i["recomputed_score"], 4), "threshold", round(i["recomputed_threshold"], 4))
print("  decoded word", i["decoded_code"], "recipient h", raw["perceptual_hash"], "hamming", d_i, "| ratio rec/dec", round(i["recomputed_score"] / i["decoded_score"], 3), "share expected", round((32 - d_i) / 32, 3))
hist = json.loads((MAIN / ".thesis-build/dev-runs/20261005-0700-f5r2-t4/run.json").read_text(encoding="utf-8"))
h = next(r for r in hist["rows"] if r["donor_id"] == 177015 and r["recipient_id"] == 25394 and r["scale"] == 0.5)
print("  historic row", {k: h[k] for k in ("recipient_psnr_db", "recipient_ssim") if k in h}, "combined", h["calls"]["combined"] if "calls" in h else None)
img = np.asarray(Image.open(event["path"]).convert("RGB"), float)
print("  image", event["path"], img.shape)

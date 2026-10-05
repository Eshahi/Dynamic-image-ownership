"""Binding ceiling: is F5's T3 binding loss caused by the 32-bit sketch or by CLIP drift itself?

For the F5 r2 stress baseline (development data only), compute 7-view CLIP
vectors of the twelve covers and of every C1 T3 image, then
  - the true angle between cover and regenerated image (infinite code length),
  - the soft ML distance with the true code q (no carrier error), 32 bits,
  - simulated longer codes (64/128/256 random Rademacher rows, same estimator),
against the inter-image pairs (distinct covers, 132 ordered) at matched FPR.
"""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT))
from scripts import f5_latent_codec as f5  # noqa
from scripts import revised_watermark_v5 as v5  # noqa
from f4_transfer_probe import SOURCES, ASSETS  # noqa
from f5_gate import semantic_feature  # noqa
import three_threat_models as models  # noqa
from a6_clip_visual import load_visual_encoder  # noqa
from PIL import Image
import torch

torch.set_num_threads(8)
RUN = Path(sys.argv[1])
OUT = Path(sys.argv[2])
run = json.loads((RUN / "run.json").read_text(encoding="utf-8"))
import ast
prof = run["profile"]
prof = prof if isinstance(prof, dict) else ast.literal_eval(prof)
checked, key, config = v5._resolve(v5.validate_profile(prof), None)
clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")


def feat(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), np.uint8)
    return np.asarray(semantic_feature(models, clip, transform, rgb, 7))


rows = [json.loads(l) for l in (RUN / "rows.jsonl").open(encoding="utf-8")]
cover = {sid: feat(p) for sid, p in SOURCES.items()}
reported = {r["source_id"]: r["report"]["semantic_code"] for r in rows if r.get("outcome") == "embedded"}
code = {}
for sid, f in cover.items():
    p = f5.semantic_projections(f, key, config)
    bits = (p > 0).astype(int)
    code[sid] = int("".join(map(str, bits)), 2)
    print(sid, "q from cover", f"{code[sid]:08x}", "reported", reported.get(sid))

t3 = []
for r in rows:
    if r.get("axis") != "T3" or r.get("control") != "C1" or r.get("outcome") != "completed" or r.get("strength") is None:
        continue
    a = r["calls"]["qim-pilot-owner-alpha"]
    status = "ok" if a["semantic_found"] and a["semantic_content_match"] else ("bind" if a["semantic_found"] else "carrier")
    t3.append(dict(id=r["id"], sid=r["source_id"], s=r["strength"], status=status, f=feat(r["image"]["path"])))
print("T3 rows", len(t3))

GRID = np.linspace(1e-3, math.pi - 1e-3, 1500)
COT = np.cos(GRID) / np.sin(GRID)


def soft_bits(cbits, proj):
    """ML angle (in units of 32-bit 'bits' = theta*32/pi) for a code c (+-1) given suspect projections."""
    t = cbits * proj
    ll = norm.logcdf(t[None, :] * COT[:, None]).sum(1)
    return GRID[int(np.argmax(ll))] * 32 / math.pi


def ang(a, b):
    return math.degrees(math.acos(float(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))


rng = np.random.default_rng(0)
sids = sorted(cover)
res = dict(intra=[], inter=[])
for item in t3:
    res["intra"].append(dict(id=item["id"], s=item["s"], status=item["status"], angle=ang(item["f"], cover[item["sid"]])))
for i in sids:
    for j in sids:
        if i != j:
            res["inter"].append(dict(i=i, j=j, angle=ang(cover[i], cover[j])))

# Code-length simulation: random +-1 projection rows, L bits, soft ML estimator with true code, no carrier error.
for L in (32, 64, 128, 256):
    for rep in range(5):
        R = 1.0 - 2.0 * rng.integers(0, 2, size=(L, 512))
        def proj(f):
            return R @ (f / np.linalg.norm(f))
        cb = {sid: np.sign(proj(cover[sid])) for sid in sids}
        for k, item in enumerate(t3):
            res["intra"][k].setdefault(f"L{L}", []).append(soft_bits(cb[item["sid"]], proj(item["f"])))
        for k, pr in enumerate(res["inter"]):
            pr.setdefault(f"L{L}", []).append(soft_bits(cb[pr["i"]], proj(cover[pr["j"]])))
# Actual keyed 32-bit code (what F5 r2 uses), true q, no carrier error
for k, item in enumerate(t3):
    c = np.array([1.0 if (code[item["sid"]] >> (31 - b)) & 1 else -1.0 for b in range(32)])
    res["intra"][k]["keyed32"] = soft_bits(c, f5.semantic_projections(item["f"], key, config))
for pr in res["inter"]:
    c = np.array([1.0 if (code[pr["i"]] >> (31 - b)) & 1 else -1.0 for b in range(32)])
    pr["keyed32"] = soft_bits(c, f5.semantic_projections(cover[pr["j"]], key, config))
OUT.write_text(json.dumps(res), encoding="utf-8")
print("saved", OUT)

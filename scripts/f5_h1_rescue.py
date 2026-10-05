"""H1 rescue: does a per-chip matched filter rescue any .4 failures?  CPU + VAE re-read."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path("C:/Users/Soroush/.codex/worktrees/claude-f5-research")
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
import sys as _sys
_sys.path.insert(0, str(ROOT / "scripts"))
_sys.path.insert(0, str(ROOT))
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
from f4_transfer_probe import SOURCES  # noqa
ASSETS = MAIN / ".thesis-build/assets/a6"
GATE = MAIN / ".thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7"
H1 = ROOT / "research/h1-probe.json"

profile = v5.validate_profile(json.loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8")))
checked, key, config = v5._resolve(profile, None)
owner = v5.canonical_owner("qim-pilot-owner-alpha")
h1 = json.loads(H1.read_text(encoding="utf-8"))
band, whitening = (4,32), 1.0
layout = f5.Layout(checked, key, config, owner, band, whitening)
reader = f5.Reader(ASSETS)
rows = [json.loads(l) for l in (GATE / "rows.jsonl").open(encoding="utf-8")]
from PIL import Image
import three_threat_models as models
from a6_clip_visual import load_visual_encoder
clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")

def feature(rgb, views=7):
    from PIL import Image as PILImage
    if views==1:
        return models.clip_feature(clip, transform, rgb).reshape(-1).tolist()
    img = PILImage.fromarray(rgb)
    w,h = img.size
    s = int(round(w*7/8))
    boxes=[(0,0,s,s),(w-s,0,w,s),(0,h-s,s,h),(w-s,h-s,w,h),((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)]
    images=[img, img.transpose(PILImage.FLIP_LEFT_RIGHT)]+[img.crop(b) for b in boxes]
    vectors=[np.asarray(models.clip_feature(clip, transform, np.asarray(v,np.uint8)).reshape(-1),np.float64) for v in images]
    mean=np.mean(vectors,0)
    return (mean/np.linalg.norm(mean)).tolist()

# weights from h1 at .4
a = np.array(h1["per_strength"]["0.4"]["a"], float)
var = np.array(h1["per_strength"]["0.4"]["v"], float)
w_matched = a / var  # per-chip weight
w_uniform = np.ones_like(w_matched)
# Normalize to same sum-square
w_matched = w_matched / np.sqrt((w_matched**2).mean())
w_uniform = w_uniform / np.sqrt((w_uniform**2).mean())

# For each failed row at .4, recompute carrier scores both ways
fails = []
for r in rows:
    if r.get("control")!="C1" or r.get("axis")!="T3" or r.get("dose")!="diffusion" or r.get("strength")!=0.4: continue
    if r.get("outcome")!="completed": continue
    c = r["calls"]["qim-pilot-owner-alpha"]
    if c["semantic_found"] and c["semantic_content_match"]:
        continue
    # recompute chips
    rgb = np.asarray(Image.open(r["image"]["path"]).convert("RGB"), np.uint8)
    z = reader.latent(rgb)
    chips = np.array(layout.projections(z), float)
    # Need Ws for this source: reconstruct via f5 internals
    # Use _semantic_pattern logic: need source CLIP vector (from clean mark's source)
    # Instead approximate Ws as sign of chips that would be expected — use decoded Ws via key tables
    # Simpler: compute semantic code q from source, then Ws tables
    # Source CLIP: use clean C0
    # Since we have many sources, load source image for q
    # For now use sign(chips) as proxy: margin Weighted vs unweighted relative ordering only
    # Better: retrieve Ws from layout signs? layout.signs is per slot, chip sign aggregation already in projections.
    # Actually projections already include signs*weights/norm: chips_i = sum slot in chip w_s*s*coeff /norm
    # The semantic Ws is chip assignment: ws_i = table[bit]. For carrier test, Ws_i is the true code bit's chip sign.
    # We can get true Ws via v5 tables: need q from source. Use feature of source image.
    src_rgb = np.asarray(Image.open(str(MAIN / f".thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7/images/clean-{r['source_id']}-C0.png")).convert("RGB"), np.uint8) if False else None
    # Easier: use the row's reported semantic score vs threshold to infer carrier margin directly — already weighted uniformly in codec.
    # So compare uniform score vs matched score scaled by correlation.
    # Approximate scored margin: score = sum ws_i * chips_i  ; ws_i = unknown but chips_i = ws_i * margin_i
    # So score_uniform = sum margin_i ; score_matched = sum w_matched_i * margin_i (if ws_i * chips_i = margin_i)
    # Use chips magnitude as proxy margin (since chips_i should be positive if correct)
    margins = chips  # if Ws was embedded correctly, chips ~ positive margin after atten
    # But some chips may be negative (bit errors). Use absolute? keep signed for score
    # Use uniform score proxy: sum clips? Instead compute both weighted sums of chips weighted by sign of clean chips
    clean_chips = np.array(layout.projections(reader.latent(np.asarray(Image.open(str(GATE / f"images/clean-{r['source_id']}-C1.png")).convert("RGB"),np.uint8))), float)
    ws_sign = np.sign(clean_chips)  # true Ws sign (embedded direction)
    ws_sign[ws_sign==0]=1
    s_unif = float((ws_sign * chips).sum() / np.sqrt(320))
    s_match = float((ws_sign * w_matched * chips).sum() / np.sqrt((w_matched**2).sum()))
    # thresholds from codec: use row's thresholds
    fails.append(dict(id=r["id"], source=r["source_id"], s_unif=s_unif, s_match=s_match, score_reported=c["semantic_score"], thr=c["semantic_threshold"], rec_score=c["semantic_recomputed_score"]))

print(json.dumps(fails, indent=1))
# correlation between matched and uniform
import math
print("fails at .4:", len(fails))
for f in fails:
    print(f["id"], f"s_unif={f['s_unif']:.2f} s_match={f['s_match']:.2f} reported={f['score_reported']:.2f} thr={f['thr']:.2f} rec={f['rec_score']:.2f}")

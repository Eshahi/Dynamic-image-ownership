"""H4a: analyze soft binding distances on stress baseline; propose calibrated threshold."""
import json, math, sys
from pathlib import Path
import numpy as np
ROOT = Path("C:/Users/Soroush/.codex/worktrees/claude-f5-research")
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
from f4_transfer_probe import SOURCES  # noqa

PROFILE = ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json"
GATE = MAIN / ".thesis-build/dev-runs/20261005-1200-f5-stress-baseline-f5r2"

profile = v5.validate_profile(json.loads(PROFILE.read_text(encoding="utf-8")))
checked, key, config = v5._resolve(profile, None)
owner = v5.canonical_owner("qim-pilot-owner-alpha")

rows = [json.loads(l) for l in (GATE / "rows.jsonl").open(encoding="utf-8")]
from PIL import Image
import three_threat_models as models
from a6_clip_visual import load_visual_encoder
clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
reader = f5.Reader(ASSETS)

def feat7(rgb):
    from PIL import Image as PILImage
    img = PILImage.fromarray(rgb)
    w,h = img.size
    s=int(round(w*7/8))
    boxes=[(0,0,s,s),(w-s,0,w,s),(0,h-s,s,h),(w-s,h-s,w,h),((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)]
    images=[img, img.transpose(PILImage.FLIP_LEFT_RIGHT)]+[img.crop(b) for b in boxes]
    vectors=[np.asarray(models.clip_feature(clip, transform, np.asarray(v,np.uint8)).reshape(-1),np.float64) for v in images]
    mean=np.mean(vectors,0)
    return (mean/np.linalg.norm(mean)).tolist()

# collect per-row soft distance by re-running detection locally (needs z)
# Use saved images
out=[]
for r in rows:
    if r.get("axis")!="T3" or r.get("dose")!="diffusion" or r.get("control")!="C1" or r.get("outcome")!="completed": continue
    path = r["image"]["path"]
    rgb = np.asarray(Image.open(path).convert("RGB"), np.uint8)
    z = reader.latent(rgb)
    vec = feat7(rgb)
    # need semantic table to get decoded_code ; use detect_rgb with binding soft/hard
    res_soft = f5.detect_rgb(rgb, z, "qim-pilot-owner-alpha", profile, vec, band=(4,32), whitening=1.0, binding="soft")
    res_hard = f5.detect_rgb(rgb, z, "qim-pilot-owner-alpha", profile, vec, band=(4,32), whitening=1.0, binding="hard")
    # semantic soft_distance
    soft_d = res_soft["semantic"].get("soft_distance")
    hard_d = res_hard["semantic"].get("corrected_distance") if res_hard["semantic"]["found"] else None
    out.append(dict(id=r["id"], strength=r["strength"], seed=r["seed"], source_id=r["source_id"],
                    soft_distance=soft_d, hard_distance=hard_d,
                    soft_found=res_soft["semantic"]["found"], soft_match=res_soft["semantic"]["content_match"],
                    hard_found=res_hard["semantic"]["found"], hard_match=res_hard["semantic"]["content_match"],
                    score=res_soft["semantic"]["score"], thr=res_soft["semantic"]["threshold"]))

# summarize
for s in [0.4,0.5,0.6]:
    sel=[x for x in out if x["strength"]==s]
    soft_ok=sum(1 for x in sel if x["soft_found"] and x["soft_match"])
    hard_ok=sum(1 for x in sel if x["hard_found"] and x["hard_match"])
    print(f"strength {s}: soft {soft_ok}/{len(sel)} hard {hard_ok}/{len(sel)}")
    # distribution of soft distances among successes vs fails
    succ=[x["soft_distance"] for x in sel if x["soft_found"] and x["soft_distance"] is not None]
    fails=[x["soft_distance"] for x in sel if not (x["soft_found"] and x["soft_match"]) and x["soft_distance"] is not None]
    if succ: print(f"  soft succ median {np.median([x for x in succ if x is not None]):.2f} p90 {np.percentile([x for x in succ if x is not None],90):.2f}")
    if fails: print(f"  soft fails median {np.median(fails):.2f} min {min(fails):.2f}")
    # where would raising radius to 7 or 8 help? count fails with soft_distance 6-8
    print(f"  fails in (6,8]: {sum(1 for x in fails if 6 < x <= 8)}  (8,10]: {sum(1 for x in fails if 8 < x <= 10)}")

# save
Path(ROOT / "research/h4-soft-distances.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("saved to research/h4-soft-distances.json")

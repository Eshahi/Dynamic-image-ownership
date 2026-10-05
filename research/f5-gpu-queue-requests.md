# GPU queue requests (m1b)

Worker branch: `claude/f5-m1b` · Commit: 0cfb528 base + m1b runner (pending commit) · Date: 2026-10-05 UTC
GPU lead reads this with: `git fetch && git show claude/f5-m1b:research/f5-gpu-queue-requests.md`

## Request 1 — short GPU smoke for m1b rehearsal (DEVELOPMENT ONLY, no held-out)

Purpose: verify the frozen `configs/f5-r2.json` through `scripts/f5_latent_codec.py` end-to-end on two development images only. No held-out pixels, no held-out manifest.

Selection rule: the two canonical development cleans from `scripts/f4_transfer_probe.py:SOURCES` — IDs 1675 and 4795 (`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-1102-e2e-1675/1675-C0-clean.png` and `20261004-1122-e2e-4795/4795-C0-clean.png`). Never held-out.

Exact command (science venv, pinned assets, frozen config). Run from the worktree `C:/Users/Soroush/.codex/worktrees/claude-f5-m1b`:

```powershell
$wt = "C:/Users/Soroush/.codex/worktrees/claude-f5-m1b"
$py = "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe"
& $py -c @"
import sys, json, hashlib
from pathlib import Path
WT = Path(r'C:/Users/Soroush/.codex/worktrees/claude-f5-m1b')
MAIN = Path(r'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
sys.path.insert(0, str(WT / 'scripts'))
sys.path.insert(0, str(WT))
from PIL import Image
import numpy as np, scripts.f5_latent_codec as f5, scripts.revised_watermark_v5 as v5
from scripts import f5_latent_codec as _f5m
import three_threat_models as ttm
from a6_clip_visual import load_visual_encoder
cfg = json.loads((WT / 'configs/f5-r2.json').read_text(encoding='utf-8'))
profile = v5.validate_profile(json.loads((WT / 'experiments/c4-v5-two-tier-regeneration-v1/profile.json').read_text(encoding='utf-8')))
assets = MAIN / '.thesis-build/assets/a6'
reader = f5.Reader(assets)
clip, tr = load_visual_encoder(assets / 'clip/ViT-B-32.pt', device='cpu')
def feat(rgb, views=7):
    if views==1: return ttm.clip_feature_wrapper(clip, tr, rgb)
    from PIL import Image as Im
    img=Im.fromarray(rgb); w,h=img.size; s=int(round(w*7/8))
    boxes=[(0,0,s,s),(w-s,0,w,s),(0,h-s,s,h),(w-s,h-s,w,h),((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)]
    imgs=[img, img.transpose(Im.FLIP_LEFT_RIGHT)]+[img.crop(b) for b in boxes]
    vecs=[np.asarray(ttm.clip_feature_wrapper(clip,tr,np.asarray(v,np.uint8)).reshape(-1),np.float64) for v in imgs]
    m=np.mean(vecs,0); return (m/np.linalg.norm(m)).tolist()
for sid,rel in [('dev-1675', r'.thesis-build/dev-runs/20261004-1102-e2e-1675/1675-C0-clean.png'), ('dev-4795', r'.thesis-build/dev-runs/20261004-1122-e2e-4795/4795-C0-clean.png')]:
    rgb=np.asarray(Image.open(MAIN/rel).convert('RGB'), np.uint8)
    for owner in ['thesis:owner:00','thesis:owner:01']:
        f=feat(rgb,7)
        out,rep=f5.embed_rgb(rgb, owner, profile, f, reader, psnr_db=52, steps=150, target_margin=4.0, mask_power=0, band=(4,32), whitening=1.0, refine_rounds=1, binding='soft')
        print(sid, owner, 'both_match' if rep['verified'] else rep['verification']['outcome'], f\"psnr={rep['rgb_psnr_db']:.1f} margin_min={rep['margin_min']:.1f}\")
"@
```

Expected: both-marked images self-verify as `both_match`, PSNR ~44 dB, margins >0, and `scripts/m1_confirmatory_endpoints.py` bounds identities (0/300 -> 0.009936, 1/300 -> 0.0157) hold. Log output to `research/m1b-rehearse-two/gpu-smoke.log` (development only). On success the GPU lead writes a short receipt; no held-out work is queued.

Selection criteria for this request: development-only, two images, frozen config, no held-out manifest.

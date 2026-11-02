"""CPU only, development PNGs. Does an image carrying both the F5 and the v5 mark still read on each carrier?
Clean: original + F5 residual + v5 residual. Regenerated (linear estimate, same seed and tape): C0 out + (F5 out - C0 out)
+ (v5 out - C0 out). Each carrier is read by its own unchanged reader. Separate-mark C comes from the saved journals."""
import json,sys,os,time,collections,math,importlib.metadata
import numpy as np,torch
from pathlib import Path
from PIL import Image
ROOT=Path("C:/Users/Soroush/.codex/worktrees/claude-f6-lean");sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"scripts"))
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5");ASSETS=MAIN/".thesis-build/assets/a6"
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
import f5_gate,a6_clip_visual,three_threat_models as models,m1_latent_reconstruction as m1
import tifs_common as common
torch.set_num_threads(8);assert not torch.cuda.is_available()
R=str(MAIN/".thesis-build/dev-runs")+"/"
IM=[R+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/",R+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images/"]
J=[R+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl",R+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl"]
SRC=[544,1355,902,599,370,1779,1637,309,723,1180,693,508,1397,1670,1398,1323]
CELLS=[("clean","None","None"),("R0","0.2","12"),("R1","0.1","12"),("R1","0.2","12"),("R3","0.2","12")]
A="qim-pilot-owner-alpha"
latest={}
for p in J:
    for l in open(p,encoding="utf-8"):
        r=json.loads(l);latest[r["id"]]=r
def journal_c(sid,arm,ch,s,seed):
    key=f"clean:{sid}:{arm}:None:None" if ch=="clean" else f"{ch}:{sid}:{arm}:{s}:{seed}"
    r=latest.get(key);c=((r or {}).get("detections") or {}).get(arm,{}).get(A)
    return None if not c or c.get("status")!="ok" else bool(c["endpoints"].get("C"))
def load(n):
    for d in IM:
        if os.path.exists(d+n): return np.asarray(Image.open(d+n).convert("RGB"),np.float64)
profile=json.loads((ROOT/"experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
reader=f5.Reader(ASSETS,device="cpu")
clip,transform=a6_clip_visual.load_visual_encoder(ASSETS/"clip/ViT-B-32.pt",device="cpu");clip.eval()
lp=models.load_lpips(ASSETS,Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
def read_f5(rgb):
    raw=f5.detect_rgb(rgb,reader.latent(rgb),A,profile,f5_gate.semantic_feature(models,clip,transform,rgb,7),band=[4,32],whitening=1.0,binding="soft")
    return common.predicates(raw)["C"],raw["semantic"].get("decoded_score")
def read_v5(rgb):
    raw=v5.detect(v5.luminance_from_rgb(rgb.tolist()),A,profile=profile,semantic_features=f5_gate.semantic_feature(models,clip,transform,rgb,1))
    return common.predicates(raw)["C"],raw["semantic"].get("decoded_score")
tab=collections.defaultdict(lambda:collections.Counter());qual=[];t0=time.time()
for sid in SRC:
    for ch,s,seed in CELLS:
        name=lambda arm:(f"clean_{sid}_{arm}_None_None.png" if ch=="clean" else f"{ch}_{sid}_{arm}_{s}_{seed}.png")
        u,a,b=load(name("unmarked")),load(name("f5-r2")),load(name("v5-r3"))
        if u is None or a is None or b is None or min(u.max(),a.max(),b.max())==0: tab[(ch,s)]["missing"]+=1;continue
        both=np.clip(np.rint(u+(a-u)+(b-u)),0,255).astype(np.uint8)
        cf,sf=read_f5(both);cv,sv=read_v5(both)
        jf,jv=journal_c(sid,"f5-r2",ch,s,seed),journal_c(sid,"v5-r3",ch,s,seed)
        t=tab[(ch,s)];t["n"]+=1;t["F5 alone"]+=bool(jf);t["v5 alone"]+=bool(jv);t["either alone"]+=bool(jf or jv)
        t["F5 in both"]+=bool(cf);t["v5 in both"]+=bool(cv);t["either in both"]+=bool(cf or cv)
        if ch=="clean":
            orig=load(f"clean_{sid}_unmarked_None_None.png").astype(np.uint8)
            q=m1.quality(orig,both);q["lpips"]=models.lpips_score(lp,orig,both);qual.append(q)
    print(sid,"%.0fs"%(time.time()-t0),flush=True)
print("cell | n | F5 alone | v5 alone | either alone | F5 in both | v5 in both | either in both   (seed 12, per image)")
for k,t in tab.items():
    print(k,t["n"],t["F5 alone"],t["v5 alone"],t["either alone"],t["F5 in both"],t["v5 in both"],t["either in both"],"missing",t["missing"])
ps=[q["psnr_db"] for q in qual];ls=[q["lpips"] for q in qual];ss=[q["ssim_rgb"] for q in qual]
print("clean both-marked quality: PSNR median %.2f min %.2f | SSIM min %.3f | LPIPS median %.4f max %.4f | strict pass %d/%d"%(np.median(ps),min(ps),min(ss),np.median(ls),max(ls),sum(common.strict_quality(q) for q in qual),len(qual)))

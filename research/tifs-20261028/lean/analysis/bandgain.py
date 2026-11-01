"""CPU only, saved dev PNGs. Which frequency bands of F5's residual actually drive the F5 reader, what do they cost in LPIPS,
and how much of the residual is the gray (fragile plus robust) versus chroma (robust only) part."""
import json,os,sys,time,numpy as np,torch
from pathlib import Path
from PIL import Image
ROOT=Path("C:/Users/Soroush/.codex/worktrees/codex-f5-components");sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"scripts"))
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5");ASSETS=MAIN/".thesis-build/assets/a6"
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
torch.set_num_threads(6);assert not torch.cuda.is_available()
IM=str(MAIN/".thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images")+"/"
RW=MAIN/".thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl"
SRC=[544,1355,902,599,370,1779]
q={}
for line in open(RW,encoding="utf-8"):
    if '"channel": "clean"' in line[:200] and '"arm": "f5-r2"' in line[:200]:
        r=json.loads(line);q[r["source_id"]]=int(r["embedding_report"]["semantic_code"],16)
profile=json.loads((ROOT/"experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
checked,key,config=v5._resolve(profile,None);own=v5.canonical_owner("qim-pilot-owner-alpha")
layout=f5.Layout(checked,key,config,own);table=v5._semantic_table(own,key,config)
reader=f5.Reader(ASSETS,device="cpu")
import lpips as L
sys.path.insert(0,str(ROOT/"scripts"))
net=L.LPIPS(net="alex",verbose=False).eval()
def lp(a,b):
    t=lambda x:torch.from_numpy(np.ascontiguousarray(x.astype(np.float32)/127.5-1).transpose(2,0,1))[None]
    with torch.inference_mode(): return float(net(t(a),t(b)))
def chips(img,w):
    return np.asarray(w)*np.asarray(layout.projections(reader.latent(np.clip(np.rint(img),0,255))))
edges=[0,8,16,32,64,128,256,363]
fy=np.fft.fftfreq(512,1/512)[:,None];fx=np.fft.rfftfreq(512,1/512)[None,:];R=np.hypot(fx,fy)
def bp(d,lo,hi):
    return np.fft.irfft2(np.fft.rfft2(d,axes=(0,1))*((R>=lo)&(R<hi))[...,None],s=(512,512),axes=(0,1))
tot=np.zeros(len(edges)-1);lps=np.zeros(len(edges)-1);res=[];t0=time.time();gc=[]
for sid in SRC:
    u=np.asarray(Image.open(IM+f"clean_{sid}_unmarked_None_None.png").convert("RGB"),np.float64)
    m=np.asarray(Image.open(IM+f"clean_{sid}_f5-r2_None_None.png").convert("RGB"),np.float64)
    d=m-u
    w=[c for seg in range(v5.CODE_BITS) for c in table[seg][v5._bit(q[sid],seg)]]
    base=chips(u,w);full=(chips(m,w)-base).mean()
    row=[]
    for i in range(len(edges)-1):
        x=bp(d,edges[i],edges[i+1]);row.append(((chips(u+x,w)-base).mean()/full,lp(u,np.clip(u+x,0,255)),float(np.sqrt((x**2).mean()))))
    gray=d.mean(2,keepdims=True);chroma=d-gray
    gc.append(((chips(u+gray,w)-base).mean()/full,(chips(u+chroma,w)-base).mean()/full,lp(u,np.clip(u+gray,0,255)),lp(u,np.clip(u+chroma,0,255)),float(np.sqrt((gray**2).mean())),float(np.sqrt((chroma**2).mean())),lp(u,m)))
    res.append(row);print(sid,"done %.0fs"%(time.time()-t0),flush=True)
res=np.array(res);gc=np.array(gc)
print("band c/i | chip share mean | LPIPS alone mean | RMS mean")
for i in range(len(edges)-1):
    print(f"{edges[i]:>3}-{edges[i+1]:<3} | {res[:,i,0].mean():+.3f} (sd {res[:,i,0].std():.3f}) | {res[:,i,1].mean():.4f} | {res[:,i,2].mean():.3f}")
print("gray chip share %.3f chroma chip share %.3f | LPIPS gray %.4f chroma %.4f full %.4f | RMS gray %.3f chroma %.3f"%tuple(gc.mean(0)[[0,1,2,3,6,4,5]]))

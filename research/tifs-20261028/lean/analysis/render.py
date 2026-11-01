"""CPU only, saved dev PNGs. A: which bands hold the reader signal that survives each regenerator (F5 marks).
B: reader response and LPIPS of a low-frequency pattern rendered through the SD1.5 decoder at 38 and 36 dB. No PGD, no diffusion."""
import json,sys,time,numpy as np,torch
from pathlib import Path
from PIL import Image
ROOT=Path("C:/Users/Soroush/.codex/worktrees/codex-f5-components");sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"scripts"))
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5");ASSETS=MAIN/".thesis-build/assets/a6"
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
torch.set_num_threads(6);assert not torch.cuda.is_available()
R_=MAIN/".thesis-build/dev-runs/"
A=str(R_/"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images")+"/";B=str(R_/"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images")+"/"
SRC=[544,1355,902,599,370,1779]
q={}
for line in open(R_/"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl",encoding="utf-8"):
    if '"channel": "clean"' in line[:200] and '"arm": "f5-r2"' in line[:200]:
        r=json.loads(line);q[r["source_id"]]=int(r["embedding_report"]["semantic_code"],16)
profile=json.loads((ROOT/"experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
checked,key,config=v5._resolve(profile,None);own=v5.canonical_owner("qim-pilot-owner-alpha")
L=f5.Layout(checked,key,config,own);table=v5._semantic_table(own,key,config)
reader=f5.Reader(ASSETS,device="cpu")
import lpips as LP
net=LP.LPIPS(net="alex",verbose=False).eval()
def lp(a,b):
    t=lambda x:torch.from_numpy(np.ascontiguousarray(np.clip(x,0,255).astype(np.float32)/127.5-1).transpose(2,0,1))[None]
    with torch.inference_mode(): return float(net(t(a),t(b)))
def load(n):
    import os
    for d in (A,B):
        if os.path.exists(d+n): return np.asarray(Image.open(d+n).convert("RGB"),np.float64)
def chips(img): return np.asarray(L.projections(reader.latent(np.clip(np.rint(img),0,255))))
edges=[0,8,16,32,64,128,256,363]
fy=np.fft.fftfreq(512,1/512)[:,None];fx=np.fft.rfftfreq(512,1/512)[None,:];R=np.hypot(fx,fy)
def bp(d,lo,hi): return np.fft.irfft2(np.fft.rfft2(d,axes=(0,1))*((R>=lo)&(R<hi))[...,None],s=(512,512),axes=(0,1))
t0=time.time();K=len(edges)-1;part={}
wof=lambda sid:np.array([c for seg in range(v5.CODE_BITS) for c in table[seg][v5._bit(q[sid],seg)]])
print("A. share of surviving reader signal by band of the output difference (F5, seed 12)")
for fam,s in (("R1","0.2"),("R1","0.1"),("R3","0.2"),("R0","0.2")):
    S=[];F=[]
    for sid in SRC:
        y1,y0=load(f"{fam}_{sid}_f5-r2_{s}_12.png"),load(f"{fam}_{sid}_unmarked_{s}_12.png")
        if y1 is None or y0 is None or y1.max()==0 or y0.max()==0: continue
        w=wof(sid);c0=chips(y0);full=float((w*(chips(y1)-c0)).mean());d=y1-y0
        S.append([float((w*(chips(y0+bp(d,edges[k],edges[k+1]))-c0)).mean()) for k in range(K)]);F.append(full)
    S=np.array(S);F=np.array(F)
    print(f"  {fam} {s}: n={len(F)} mean margin kept {F.mean():+.3f} | by band "+" ".join(f"{edges[k]}-{edges[k+1]}:{S[:,k].mean():+.3f}" for k in range(K)),"| %.0fs"%(time.time()-t0),flush=True)
print("B. decoder-rendered pattern, added to the original")
ch,u_,v_=L.ch,L.u,L.v
def pattern(w,rmax):
    P=np.zeros((4,64,64));keep=np.hypot(u_,v_)<rmax
    vals=(L.weights*L.signs)*(w[L.chip]/L.norms[L.chip]);np.add.at(P,(ch[keep],u_[keep],v_[keep]),vals[keep])
    return L.dct.T@P@L.dct  # inverse orthonormal DCT per channel
rows={}
for sid in SRC:
    u=load(f"clean_{sid}_unmarked_None_None.png");m=load(f"clean_{sid}_f5-r2_None_None.png");w=wof(sid)
    c0=chips(u);c=chips(m);noise=float(np.std(c0));f5rec=float((w*c).sum()/np.linalg.norm(c))
    z=torch.from_numpy(reader.latent(u).astype(np.float32))[None]
    with torch.inference_mode(): base=reader.vae.decode(z/f5.SCALE).sample
    rows.setdefault("F5 mark",[]).append(((w*(c-c0)).mean(),f5rec,lp(u,m),np.sqrt(((m-u)**2).mean()),noise,0.))
    for rmax in (32,16):
        p=torch.from_numpy(pattern(w,rmax).astype(np.float32))[None];alpha=None
        with torch.inference_mode():
            probe=reader.vae.decode((z+p*0.02)/f5.SCALE).sample
        rms1=float((((probe-base)/2*255)**2).mean().sqrt());
        for db in (38.,36.):
            target=255*10**(-db/20);a=0.02*target/rms1
            with torch.inference_mode(): out=reader.vae.decode((z+p*a)/f5.SCALE).sample
            d=((out-base)/2*255)[0].permute(1,2,0).numpy().astype(np.float64)
            d*=target/np.sqrt((d**2).mean());x=u+d;cc=chips(x)
            low=(bp(d,0,32)**2).sum()/(d**2).sum()
            rows.setdefault(f"render r<{rmax} {db:.0f} dB",[]).append(((w*(cc-c0)).mean(),float((w*cc).sum()/np.linalg.norm(cc)),lp(u,x),np.sqrt(((np.clip(np.rint(x),0,255)-u)**2).mean()),noise,low))
    print(sid,"%.0fs"%(time.time()-t0),flush=True)
print("variant | mean margin | recomputed score | LPIPS mean (max) | RMS | chip noise sd | energy share below 32 c/i")
for k,v in rows.items():
    a=np.array(v);print(f"{k:22s} {a[:,0].mean():+.3f} {a[:,1].mean():6.2f}  {a[:,2].mean():.4f} ({a[:,2].max():.4f})  {a[:,3].mean():.2f}  {a[:,4].mean():.3f}  {a[:,5].mean():.2f}")

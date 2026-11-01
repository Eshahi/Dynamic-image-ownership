"""CPU only, saved unmarked dev PNGs. One reader gradient per source, then a band-limited step along it.
For each pixel band and RMS: mean chip margin gained (finite, through the real encoder) and LPIPS cost.
This maps the reader's response by frequency for the best first-order direction. No writer, no diffusion."""
import json,sys,time,numpy as np,torch
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
L=f5.Layout(checked,key,config,own);table=v5._semantic_table(own,key,config)
reader=f5.Reader(ASSETS,device="cpu")
import lpips as LP
net=LP.LPIPS(net="alex",verbose=False).eval()
def lp(a,b):
    t=lambda x:torch.from_numpy(np.ascontiguousarray(np.clip(x,0,255).astype(np.float32)/127.5-1).transpose(2,0,1))[None]
    with torch.inference_mode(): return float(net(t(a),t(b)))
D=torch.from_numpy(L.dct.astype(np.float32));ch,u_,v_=(torch.from_numpy(a) for a in (L.ch,L.u,L.v))
coeff=torch.from_numpy((L.weights*L.signs).astype(np.float32));chip=torch.from_numpy(L.chip);norms=torch.from_numpy(L.norms.astype(np.float32))
def proj(x):
    z=reader.encode(x);c=torch.einsum("ij,cjk,lk->cil",D,z,D)
    return torch.zeros(v5.CHANNEL_CHIPS).index_add(0,chip,c[ch,u_,v_]*coeff)/norms
edges=[0,8,16,32,64,128,256,363];RMS=[1.,2.,4.]
fy=np.fft.fftfreq(512,1/512)[:,None];fx=np.fft.rfftfreq(512,1/512)[None,:];R=np.hypot(fx,fy)
def bp(d,lo,hi): return np.fft.irfft2(np.fft.rfft2(d,axes=(0,1))*((R>=lo)&(R<hi))[...,None],s=(512,512),axes=(0,1))
K=len(edges)-1;G=np.zeros((len(SRC),K));M=np.zeros((len(SRC),K,len(RMS)));P=np.zeros((len(SRC),K,len(RMS)));t0=time.time();full=np.zeros((len(SRC),len(RMS),2))
for i,sid in enumerate(SRC):
    u=np.asarray(Image.open(IM+f"clean_{sid}_unmarked_None_None.png").convert("RGB"),np.float64)
    w=torch.tensor([c for seg in range(v5.CODE_BITS) for c in table[seg][v5._bit(q[sid],seg)]],dtype=torch.float32)
    x=torch.from_numpy(np.ascontiguousarray((u/255).astype(np.float32).transpose(2,0,1)))[None].requires_grad_(True)
    m0=(w*proj(x)).mean();g,=torch.autograd.grad(m0,x);g=g[0].permute(1,2,0).numpy().astype(np.float64)/255.0  # margin per byte level
    base=float(m0.detach())
    def margin(img):
        with torch.inference_mode():
            t=torch.from_numpy(np.ascontiguousarray((np.clip(img,0,255)/255).astype(np.float32).transpose(2,0,1)))[None];return float((w*proj(t)).mean())
    for k in range(K):
        d=bp(g,edges[k],edges[k+1]);rms=np.sqrt((d**2).mean())
        G[i,k]=np.sqrt((d**2).sum())  # tangent margin gain per unit L2 at unit-norm step
        for j,r in enumerate(RMS):
            step=d/rms*r;M[i,k,j]=margin(u+step)-base;P[i,k,j]=lp(u,u+step)
    d=g;rms=np.sqrt((d**2).mean())
    for j,r in enumerate(RMS):
        step=d/rms*r;full[i,j]=(margin(u+step)-base,lp(u,u+step))
    print(sid,"%.0fs"%(time.time()-t0),flush=True)
print("all-band one-step: RMS | margin | LPIPS");[print(RMS[j],"%.3f %.4f"%tuple(full[:,j].mean(0))) for j in range(len(RMS))]
print("band | share of squared gradient | margin at RMS 1,2,4 | LPIPS at RMS 1,2,4")
gs=(G**2).mean(0);gs=gs/gs.sum()
for k in range(K):
    print(f"{edges[k]:>3}-{edges[k+1]:<3} | {gs[k]:.3f} | "+" ".join(f"{x:+.3f}" for x in M[:,k].mean(0))+" | "+" ".join(f"{x:.4f}" for x in P[:,k].mean(0))+" | max LPIPS "+" ".join(f"{x:.4f}" for x in P[:,k].max(0)))
np.savez(sys.argv[1],G=G,M=M,P=P,full=full,edges=edges,RMS=RMS,SRC=SRC)

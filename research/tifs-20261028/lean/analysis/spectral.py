"""Coherent frequency response of each regenerator, from saved development PNGs only.
For arm a, cell c: In=marked_clean-unmarked_clean; Out=marked_regen-unmarked_regen (same seed).
H(f)=sum Re(Out conj In)/sum |In|^2 per radial band, in cycles per image at 512 px. No models."""
import json,os,sys,numpy as np
from PIL import Image
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/"
A=M+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/"
B=M+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images/"
SRC=[544,1355,902,599,370,1779,1637,309,723,1180,693,508,1397,1670,1398,1323]
ARMS=["f5-r2","v5-r3","vine-r","wam"]
CELLS=[("R0","0.2"),("R1","0.1"),("R1","0.2"),("R3","0.2"),("D1","None"),("D3","None"),("X1","None"),("R1-mode","0.2")]
SEEDS=["12","13","14"]
edges=np.array([0,2,4,8,16,32,64,128,256,363])
names=[f"{edges[i]}-{edges[i+1]}" for i in range(len(edges)-1)]
fy=np.fft.fftfreq(512,1/512)[:,None];fx=np.fft.rfftfreq(512,1/512)[None,:]
R=np.hypot(fx,fy);band=np.digitize(R,edges)-1
w=np.ones_like(R);w[:,1:-1]=2  # rfft weighting
def load(name):
    for d in (A,B):
        p=d+name
        if os.path.exists(p): return np.asarray(Image.open(p).convert("RGB"),np.float64)
    return None
def spec(x): return np.fft.rfft2(x,axes=(0,1),norm="ortho")
def accum(idx,v,n=len(names)): return np.array([v[idx==i].sum() for i in range(n)])
out={}
for arm in ARMS:
    Ein=np.zeros(len(names));res={}
    for sid in SRC:
        mc,uc=load(f"clean_{sid}_{arm}_None_None.png"),load(f"clean_{sid}_unmarked_None_None.png")
        if mc is None or uc is None: print("missing clean",sid,arm);continue
        I=spec(mc-uc);e=(np.abs(I)**2).sum(2)*w;Ein+=accum(band,e)
        for fam,s in CELLS:
            key=f"{fam}-{s}";t=res.setdefault(key,dict(cross=np.zeros(len(names)),eout=np.zeros(len(names)),ein=np.zeros(len(names)),n=0))
            for seed in (SEEDS if s!="None" else SEEDS+["None"]):
                mr,ur=load(f"{fam}_{sid}_{arm}_{s}_{seed}.png"),load(f"{fam}_{sid}_unmarked_{s}_{seed}.png")
                if mr is None or ur is None or mr.shape!=mc.shape or mr.max()==0 or ur.max()==0: continue
                O=spec(mr-ur)
                t["cross"]+=accum(band,(O*np.conj(I)).real.sum(2)*w);t["eout"]+=accum(band,(np.abs(O)**2).sum(2)*w);t["ein"]+=accum(band,e);t["n"]+=1
    out[arm]=dict(ein=Ein.tolist(),cells={k:dict(n=v["n"],H=(v["cross"]/np.maximum(v["ein"],1e-9)).round(4).tolist(),coh=(v["cross"]/np.sqrt(np.maximum(v["ein"]*v["eout"],1e-9))).round(4).tolist(),leak=(v["eout"]/np.maximum(v["ein"],1e-9)).round(3).tolist(),Htot=round(float(v["cross"].sum()/max(v["ein"].sum(),1e-9)),4)) for k,v in res.items()})
    tot=Ein.sum();N=512*512*3*len(SRC)
    print(f"\n{arm}: residual RMS {np.sqrt(tot/N):.3f} levels; energy share by band (cycles/image)")
    print("  "+"  ".join(f"{a}:{b/tot*100:5.1f}%" for a,b in zip(names,Ein)))
    for k,v in out[arm]["cells"].items():
        print(f"  {k:12s} n={v['n']:3d} Htot={v['Htot']:+.3f}  H: "+" ".join(f"{x:+.2f}" for x in v["H"]))
json.dump(dict(bands=names,arms=out,sources=SRC),open(sys.argv[1],"w"),indent=1)

"""Does the part of a mark that looks like the image's own structure survive better?
Per 16x16 window and RGB channel, regress Delta_in on (high-pass image, d/dx, d/dy): gain plus small warp.
Coherent part Dc = fitted, rest Di. Report the energy share of Dc and H on each part. Saved dev PNGs only."""
import os,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/"
D=[M+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/",M+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images/"]
SRC=[544,1355,902,599,370,1779,1637,309,723,1180,693,508,1397,1670,1398,1323]
ARMS=["f5-r2","v5-r3","vine-r","wam"];CELLS=[("R1","0.2"),("R1","0.1"),("R3","0.2"),("R0","0.2")];SEEDS=["12","13","14"];W=16
def load(n):
    for d in D:
        if os.path.exists(d+n): return np.asarray(Image.open(d+n).convert("RGB"),np.float64)
def split(I,X):
    Dc=np.zeros_like(X)
    for c in range(3):
        hp=I[...,c]-gaussian_filter(I[...,c],4);gy,gx=np.gradient(gaussian_filter(I[...,c],1))
        for y in range(0,512,W):
            for x in range(0,512,W):
                A=np.stack([hp[y:y+W,x:x+W].ravel(),gx[y:y+W,x:x+W].ravel(),gy[y:y+W,x:x+W].ravel()],1)
                b=X[y:y+W,x:x+W,c].ravel()
                sol,*_=np.linalg.lstsq(A,b,rcond=None)
                Dc[y:y+W,x:x+W,c]=(A@sol).reshape(W,W)
    return Dc,X-Dc
print("chance share of energy explained = %.1f%%"%(3/256*100))
for arm in ARMS:
    Ec=Ei=0;t={}
    for sid in SRC:
        mc,uc=load(f"clean_{sid}_{arm}_None_None.png"),load(f"clean_{sid}_unmarked_None_None.png")
        Dc,Di=split(uc,mc-uc);Ec+=(Dc**2).sum();Ei+=(Di**2).sum()
        for fam,s in CELLS:
            k=fam+s;v=t.setdefault(k,np.zeros(4))
            for seed in SEEDS:
                mr,ur=load(f"{fam}_{sid}_{arm}_{s}_{seed}.png"),load(f"{fam}_{sid}_unmarked_{s}_{seed}.png")
                if mr is None or ur is None or mr.max()==0 or ur.max()==0: continue
                O=mr-ur;v+=np.array([(O*Dc).sum(),(Dc**2).sum(),(O*Di).sum(),(Di**2).sum()])
    print(f"{arm}: coherent energy share {Ec/(Ec+Ei)*100:.1f}%   "+"  ".join(f"{k}: Hc={v[0]/v[1]:+.2f} Hi={v[2]/v[3]:+.2f}" for k,v in t.items()))

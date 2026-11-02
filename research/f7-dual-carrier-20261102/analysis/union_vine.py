"""Development Stage 2 journals only. (1) F5 or v5 union ceiling with no interference. (2) VINE-R raw bit errors
per cell, for blind decoding with error correction. (3) VINE-R and v5 clean quality from saved PNGs."""
import json,hashlib,collections,math,os,statistics as st
import numpy as np
from PIL import Image
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/"
J=[M+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl",M+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl"]
IM=[M+"20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/",M+"20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images/"]
A="qim-pilot-owner-alpha"
def message(sid,bits=100,seed=20261019):
    raw=hashlib.shake_256(f"encoder-transfer-v1:{seed}:{sid}".encode()).digest((bits+7)//8)
    return [(b>>s)&1 for b in raw for s in range(7,-1,-1)][:bits]
C=collections.defaultdict(dict); E=collections.defaultdict(list); E0=collections.defaultdict(list); P=collections.defaultdict(list)
latest={}
for path in J:
    for line in open(path,encoding="utf-8"):
        r=json.loads(line);latest[r["id"]]=r
for r in latest.values():
    if True:
        cell=(r["channel"],r.get("strength"));arm=r["arm"];det=r.get("detections") or {}
        if arm in("f5-r2","v5-r3") and r.get("seed") is not None:
            c=(det.get(arm) or {}).get(A)
            if c and c.get("status")=="ok": C[(cell,arm)][(r["source_id"],r["seed"])]=bool(c["endpoints"].get("C"))
        v=(det.get("vine-r") or {}).get(A)
        if v and v.get("status")=="ok" and arm in("vine-r","unmarked"):
            dec=v["raw"].get("decoded_message");prob=v["raw"].get("probabilities")
            if dec is None: continue
            k=message(r["source_id"])
            err=sum(int(a)!=b for a,b in zip(dec,k))
            (E if arm=="vine-r" else E0)[cell].append(err)
            if arm=="vine-r": P[cell].append(float(np.mean(np.abs(np.asarray(prob)-.5))))
def maj(d,sid):
    v=[d.get((sid,s)) for s in (12,13,14)]
    return sum(bool(x) for x in v)>=2
print("== (1) source-majority C over 60 dev sources: F5, v5, either (no interference)")
cells=sorted({k[0] for k in C},key=str)
for cell in cells:
    f=C.get((cell,"f5-r2"),{});v=C.get((cell,"v5-r3"),{})
    sids=sorted({s for s,_ in f}|{s for s,_ in v})
    if not sids: continue
    u={(s,seed):(f.get((s,seed)) or v.get((s,seed))) for s in sids for seed in (12,13,14)}
    print(f"  {str(cell):22s} F5 {sum(maj(f,s) for s in sids):2d}  v5 {sum(maj(v,s) for s in sids):2d}  either {sum(maj(u,s) for s in sids):2d}  of {len(sids)}")
print("== (2) VINE-R bit errors of 100 (marked), share with at most t errors; unmarked minimum errors")
for cell in sorted(E,key=str):
    e=np.array(E[cell]);z=np.array(E0.get(cell,[50]))
    print(f"  {str(cell):22s} n={len(e):3d} median {np.median(e):5.1f} p90 {np.percentile(e,90):5.1f} | "+" ".join(f"<={t}:{(e<=t).mean():.2f}" for t in (4,6,8,10,12,15))+f" | unmarked min {z.min()} | mean |p-.5| {np.mean(P[cell]):.3f}")
print("== (3) clean quality against the unmarked original, 60 dev sources")
def load(n):
    for d in IM:
        if os.path.exists(d+n): return np.asarray(Image.open(d+n).convert("RGB"),np.float64)
for arm in ("vine-r","v5-r3","f5-r2"):
    ps=[]
    for sid in sorted({s for (s,_) in C.get((("R0",0.2),"f5-r2"),{})}):
        u,m=load(f"clean_{sid}_unmarked_None_None.png"),load(f"clean_{sid}_{arm}_None_None.png")
        if u is None or m is None: continue
        mse=((u-m)**2).mean();ps.append(10*math.log10(255**2/mse))
    ps=np.array(ps);print(f"  {arm:7s} PSNR median {np.median(ps):.2f} min {ps.min():.2f} share above 35 dB {(ps>35).mean():.2f} (n={len(ps)})")

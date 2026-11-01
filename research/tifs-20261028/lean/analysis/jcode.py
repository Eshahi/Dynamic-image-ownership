"""Why does J (exact original q) lag C? Segment code distance versus per-bit decode error, dev journals only. No pixels, no models."""
import json,sys,collections,numpy as np
from pathlib import Path
ROOT=Path("C:/Users/Soroush/.codex/worktrees/codex-f5-components");sys.path.insert(0,str(ROOT))
from scripts import revised_watermark_v5 as v5
profile=json.loads((ROOT/"experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
checked,key,config=v5._resolve(profile,None);own=v5.canonical_owner("qim-pilot-owner-alpha")
T=v5._semantic_table(own,key,config)
print("segments",len(T),"options",len(T[0]),"chips per option",len(T[0][0]))
dist=[int(sum(a!=b for a,b in zip(T[s][0],T[s][1]))) for s in range(len(T))]
print("per-segment distance between bit 0 and bit 1:",dist)
print("distance histogram",sorted(collections.Counter(dist).items()))
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl"
OWNER="qim-pilot-owner-alpha"
orig={};rows=[]
for line in open(M,encoding="utf-8"):
    r=json.loads(line)
    if r.get("arm")!="f5-r2": continue
    if r.get("channel")=="clean": orig[r["source_id"]]=int(r["embedding_report"]["semantic_code"],16)
    c=((r.get("detections") or {}).get("f5-r2") or {}).get(OWNER)
    if c and c.get("status")=="ok": rows.append((r["channel"],r.get("strength"),r["source_id"],c))
print("sources",len(orig),"keys of endpoints",list(rows[0][3].get("endpoints",{}).keys()))
tab=collections.defaultdict(lambda:dict(n=0,C=0,J=0,read=0,seg=np.zeros(32),hd=[],sc=[]))
for ch,st,sid,c in rows:
    s=c["raw"]["semantic"];k=(ch,st);t=tab[k];t["n"]+=1
    t["C"]+=bool(c["endpoints"].get("C"));t["J"]+=bool(c["endpoints"].get("J"));t["read"]+=bool(s.get("read"))
    dc=s.get("decoded_code")
    if dc is None: continue
    x=int(dc,16)^orig[sid]
    for b in range(32):
        if (x>>(31-b))&1: t["seg"][b]+=1
    t["hd"].append(bin(x).count("1"));t["sc"].append(s.get("decoded_score",0))
d=np.array(dist)
print("cell | n | read | C | J | J/C | mean bit errors | error rate in distance<=4 segs vs distance>=8 segs")
for k in sorted(tab,key=str):
    t=tab[k];n=max(t["n"],1)
    low=t["seg"][d<=4].mean()/n if (d<=4).any() else float("nan");hi=t["seg"][d>=8].mean()/n if (d>=8).any() else float("nan")
    print(k,t["n"],"%.2f %.2f %.2f %.2f"%(t["read"]/n,t["C"]/n,t["J"]/n,t["J"]/max(t["C"],1)),"hd %.2f"%np.mean(t["hd"]),"low %.3f hi %.3f"%(low,hi))
# high-score rows only: is exact recovery still limited?
for cell in (("clean",None),("X1",None),("R0",0.1),("R0",0.2)):
    t=tab[cell];hd=np.array(t["hd"]);sc=np.array(t["sc"])
    for lo,hi in ((8.26,12),(12,14),(14,16),(16,18)):
        m=(sc>=lo)&(sc<hi)
        if m.sum(): print(cell,"score",lo,hi,"n",int(m.sum()),"exact %.2f mean bit errors %.2f"%((hd[m]==0).mean(),hd[m].mean()))

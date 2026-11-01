"""How much do the three seeds add? Agreement of C and of score across seeds, per cell, F5 and v5, dev journal only."""
import json,collections,statistics as st
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl"
OWNER="qim-pilot-owner-alpha"
tab=collections.defaultdict(lambda:collections.defaultdict(dict))
bins=collections.defaultdict(lambda:[0,0,0])
for line in open(M,encoding="utf-8"):
    r=json.loads(line)
    a=r.get("arm")
    if a not in("f5-r2","v5-r3") or r.get("seed") is None: continue
    c=((r.get("detections") or {}).get(a) or {}).get(OWNER)
    if not c or c.get("status")!="ok": continue
    s=c["raw"]["semantic"]
    tab[(a,r["channel"],r["strength"])][r["source_id"]][r["seed"]]=(bool(c["endpoints"].get("C")),s.get("decoded_score") or 0)
    if a=="f5-r2":
        d=s.get("decoded_score") or 0
        b=min(int(d//2)*2,16);bins[b][0]+=1;bins[b][1]+=bool(c["endpoints"].get("C"));bins[b][2]+=bool(c["endpoints"].get("J"))
print("cell | sources | all three seeds agree on C | seed-0-only majority error | between-source sd / within-source sd of score")
for k in sorted(tab,key=str):
    v=tab[k];agree=wrong=n=0;means=[];within=[]
    for sid,x in v.items():
        if len(x)!=3: continue
        n+=1;cs=[y[0] for y in x.values()];maj=sum(cs)>=2
        agree+=len(set(cs))==1;wrong+=cs[0]!=maj
        sc=[y[1] for y in x.values()];means.append(st.mean(sc));within.append(st.pstdev(sc))
    if n and st.pstdev(means)>0:
        print(k,n,"agree %.2f"%(agree/n),"one-seed error %.3f"%(wrong/n),"between %.2f within %.2f"%(st.pstdev(means),st.mean(within)))
print("F5 decoded score bin | n | P(C) | P(J)")
for b in sorted(bins):
    n,c,j=bins[b];print(f"{b:>2}-{b+2:<2} {n:5d} {c/n:.2f} {j/n:.2f}")

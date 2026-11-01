import json,statistics as st,collections
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl"
OWNER="qim-pilot-owner-alpha"
SRC={544,1355,902,599,370,1779,1637,309,723,1180,693,508,1397,1670,1398,1323}
tab=collections.defaultdict(lambda:collections.defaultdict(list))
first=True
for line in open(M,encoding="utf-8"):
    r=json.loads(line)
    if r.get("arm") not in("f5-r2","v5-r3","unmarked"): continue
    det=r.get("detections") or {}
    for reader in("f5-r2","v5-r3"):
        if r["arm"] not in(reader,"unmarked"): continue
        c=(det.get(reader) or {}).get(OWNER)
        if not c or c.get("status")!="ok": continue
        s=c["raw"]["semantic"]
        k=(r["channel"],r.get("strength"),reader,r["arm"])
        all_=tab[k]
        all_["dec"].append(s.get("decoded_score") or 0)
        all_["rec"].append(s.get("recomputed_score") if s.get("recomputed_score") is not None else s.get("score",0) or 0)
        all_["C"].append(bool((c.get("endpoints") or {}).get("C")))
        if first and r["arm"]=="f5-r2" and r["channel"]=="clean":
            print(json.dumps({k:v for k,v in s.items() if not isinstance(v,(list,dict))})[:900]); first=False
for k in sorted(tab,key=str):
    v=tab[k]
    d=sorted(v["dec"]);rr=sorted(x for x in v["rec"] if x is not None)
    print(k,"n",len(d),"dec p10 %.2f med %.2f p90 %.2f"%(d[len(d)//10],st.median(d),d[int(.9*len(d))]),"rec med %.2f"%st.median(rr) if rr else "","C %.3f"%(sum(v["C"])/len(v["C"])))

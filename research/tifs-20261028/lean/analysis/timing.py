import json,statistics as st,collections,sys
M="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/"
for run,name in (("20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl","2a"),("20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl","2b")):
    gen=collections.defaultdict(list);det=collections.defaultdict(list);keys=None;sample=None;neg=0
    for line in open(M+run,encoding="utf-8"):
        r=json.loads(line)
        k=(r.get("channel"),r.get("strength"),r.get("arm"))
        if r.get("generation_seconds") is not None: gen[k].append(r["generation_seconds"])
        if r.get("channel")=="clean" and r.get("arm")=="f5-r2" and sample is None: sample=r
    print("==",name)
    for k in sorted(gen,key=str):
        v=gen[k]
        if k[2] in("f5-r2","v5-r3","vine-r","unmarked","wam"):
            print(k,len(v),"med %.2f p90 %.2f"%(st.median(v),sorted(v)[int(.9*len(v))]))
    if sample:
        print(json.dumps({k:(v if not isinstance(v,(dict,list)) else "...") for k,v in sample.items()}))
        er=sample.get("embedding_report") or {}
        print({k:er.get(k) for k in("rgb_psnr_db","margin_median","margin_min","negative_chips","seconds")})
        print(list(sample.get("detections",{}).keys())[:6])

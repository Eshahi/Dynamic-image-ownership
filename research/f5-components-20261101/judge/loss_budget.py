"""Where does each method lose detections? Attribute every failed call to a pipeline stage.

Development journal only (Stage 2 union, 60 sources, seeds 12-14). Standard library only.
Each owner-alpha call on a marked image falls in exactly one class:

  C          read succeeded and the content check matched (the primary endpoint)
  binding    read succeeded but the content check did not match: descriptor, code or decision stage
  undecoded  key found only with the code recomputed from the suspect: carrier alive but too weak to decode
  lost       neither test passed: carrier gone
  missing    no usable call (safety block or unresolved)

The ceilings are counterfactual counts, not predictions.
"""
import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

PATH = Path(r"W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl")
CELLS = [("R0", 0.1), ("R0", 0.2), ("R0", 0.4), ("R1", 0.1), ("R1", 0.2), ("R1", 0.4), ("R3", 0.2)]
ARMS = ["f5-r2", "v5-r3"]
OWNER = "qim-pilot-owner-alpha"


def load():
    last = {}
    with open(PATH, encoding="utf-8") as fh:
        for raw in fh:
            row = json.loads(raw)
            if row.get("status") in ("ok", "safety_blocked"):
                last[row["id"]] = row
    return last


def classify(row, arm):
    if row.get("status") != "ok":
        return "missing", None
    call = (row.get("detections") or {}).get(arm, {}).get(OWNER)
    if not call or call.get("status") != "ok":
        return "missing", None
    sem = call["raw"]["semantic"]
    ep = call["endpoints"]
    if ep.get("C"):
        return "C", sem
    if sem.get("read"):
        return "binding", sem
    if sem.get("found"):
        return "undecoded", sem
    return "lost", sem


def main():
    rows = load()
    probe = next(r for r in rows.values() if r.get("arm") == "f5-r2" and r.get("channel") == "R1" and r.get("status") == "ok")
    sem = probe["detections"]["f5-r2"][OWNER]["raw"]["semantic"]
    print("semantic fields:", sorted(sem))
    out = {}
    for arm in ARMS:
        print(f"\n== {arm}: share of seed-level calls by class")
        print("cell      calls     C  binding undecoded  lost missing | med decoded margin | med recomputed margin | C by source | if binding perfect | if any found counted")
        for chan, strength in CELLS:
            counts = Counter()
            dec, rec = [], []
            per_source = defaultdict(Counter)
            for r in rows.values():
                if r.get("arm") == arm and r.get("channel") == chan and r.get("strength") == strength:
                    cls, sem = classify(r, arm)
                    counts[cls] += 1
                    per_source[r["source_id"]][cls] += 1
                    if sem is not None:
                        d, dt = sem.get("decoded_score"), sem.get("decoded_threshold")
                        s, t = sem.get("recomputed_score"), sem.get("recomputed_threshold")
                        if d is not None and dt is not None:
                            dec.append(d - dt)
                        if s is not None and t is not None:
                            rec.append(s - t)
            n = sum(counts.values())
            c_src = sum(1 for v in per_source.values() if v["C"] >= 2)
            read_src = sum(1 for v in per_source.values() if v["C"] + v["binding"] >= 2)
            any_src = sum(1 for v in per_source.values() if v["C"] + v["binding"] + v["undecoded"] >= 2)
            md = st.median(dec) if dec else float("nan")
            mr = st.median(rec) if rec else float("nan")
            print(f"{chan}-{strength:<4} {n:6d} {counts['C']:5d} {counts['binding']:8d} {counts['undecoded']:9d} {counts['lost']:5d} {counts['missing']:7d} | {md:18.2f} | {mr:21.2f} | {c_src:11d} | {read_src:18d} | {any_src:20d}")
            out[f"{arm}|{chan}-{strength}"] = dict(counts=dict(counts), c_sources=c_src, read_sources=read_src, any_sources=any_src,
                                                   median_decoded_margin=md, median_recomputed_margin=mr)
    Path(__file__).with_name("loss-budget.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

"""Which tier carries the owner where? Judge's check after Codex's fragile-tier accounting.

Stage 2 development journal only, standard library. Counts source majorities /60 and also
negative calls: unmarked images (C0) and marked images read for the wrong owner. A negative
hit here means the tier's own test fired, whatever the content status.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from loss_budget import CELLS, OWNER, load

WRONG = "qim-pilot-owner-beta"


def main():
    rows = load()
    out = {}
    for arm in ("f5-r2", "v5-r3"):
        print(f"\n== {arm}: source majority /60")
        print("cell      robust found | fragile found | fragile found+content ok | either found | C | C or fragile found+content ok | outcomes (seed calls)")
        for chan, strength in CELLS:
            c = defaultdict(lambda: defaultdict(int))
            outcomes = Counter()
            for x in rows.values():
                if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
                    continue
                call = x["detections"].get(arm, {}).get(OWNER)
                if not call or call.get("status") != "ok":
                    continue
                raw, e = call["raw"], call["endpoints"]
                s, i = raw["semantic"], raw["instance"]
                src = x["source_id"]
                outcomes[raw.get("outcome")] += 1
                inst_ok = bool(i.get("found")) and bool(i.get("content_match"))
                c["sf"][src] += int(bool(s.get("found")))
                c["if"][src] += int(bool(i.get("found")))
                c["io"][src] += int(inst_ok)
                c["any"][src] += int(bool(s.get("found")) or bool(i.get("found")))
                c["C"][src] += int(bool(e.get("C")))
                c["CI"][src] += int(bool(e.get("C")) or inst_ok)
            v = {k: sum(1 for n in c[k].values() if n >= 2) for k in ("sf", "if", "io", "any", "C", "CI")}
            print(f"{chan}-{strength:<4} {v['sf']:12d} | {v['if']:13d} | {v['io']:24d} | {v['any']:12d} | {v['C']:1d} | {v['CI']:29d} | {dict(outcomes.most_common(4))}")
            out[f"{arm}|{chan}-{strength}"] = {**v, "outcomes": dict(outcomes)}
        neg = Counter()
        for x in rows.values():
            if x.get("status") != "ok" or x.get("seed") is None:
                continue
            if x.get("arm") == "unmarked" and (x.get("channel"), x.get("strength")) in CELLS:
                call = x["detections"].get(arm, {}).get(OWNER)
                key = "C0"
            elif x.get("arm") == arm and (x.get("channel"), x.get("strength")) in CELLS:
                call = x["detections"].get(arm, {}).get(WRONG)
                key = "wrong-owner"
            else:
                continue
            if not call or call.get("status") != "ok":
                continue
            s, i = call["raw"]["semantic"], call["raw"]["instance"]
            neg[key + " calls"] += 1
            neg[key + " robust found"] += int(bool(s.get("found")))
            neg[key + " fragile found"] += int(bool(i.get("found")))
            neg[key + " fragile found+content ok"] += int(bool(i.get("found")) and bool(i.get("content_match")))
        print("negative controls, seven cells:", dict(neg))
        out[f"{arm}|negatives"] = dict(neg)
    Path(__file__).with_name("two-tiers.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

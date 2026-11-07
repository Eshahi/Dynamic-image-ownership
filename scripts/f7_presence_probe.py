"""Exploratory, development data only: an owner-presence fallback for the F7 registry pointer.

Question: when the 32-bit code cannot be read (SDXL .2, SD1.5 .4), the owner's keyed presence test often still
fires. If presence alone is used to restrict the registry search to that owner's records, how many regenerated
copies are accepted, and do copy-paste, false-claim, wrong-source, unmarked and wrong-owner queries stay at zero?

Pointers compared on the stage-B screen (saved detect rows, no detector rerun):
  P1  the frozen section-2 pointer (found, read, decoded score >= 8.341671, record q within Hamming 6);
  P2  P1, else owner presence: the semantic tier `found` under the owner's key in any of the three tests the
      F7 reader already runs (F5 carrier, v5 carrier, combined), each at its own frozen false-positive target.
      Presence opens every record of that owner; the frozen round-3 rule then decides each (query, record) pair.

This is post hoc on data already scored; it designs a rule, it confirms nothing.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f7_registry_test as t  # noqa: E402

TESTS = ("f5", "v5", "combined")


def presence(call):
    """The owner's semantic-tier presence in any of the three saved tests; None when the row has no carriers."""
    car = ((call or {}).get("raw") or {}).get("carriers")
    if not isinstance(car, dict):
        return None
    found = []
    for name in TESTS:
        x = car.get(name) or {}
        s = x if name == "combined" else (x.get("semantic") or {})
        found.append(s.get("found") is True)
    return any(found)


class Probe(t.Scorer):
    def accepted(self, p, call, owner_records, skip=()):
        """(P1 accepts, P2 accepts) over one owner's records, skipping record ids in skip."""
        codes = t.carried(call)
        here = presence(call)
        p1, p2, fp = [], [], []
        for sid, rec in owner_records.items():
            if sid in skip or rec["path"] is None:
                continue
            if self.rule(self.pair(p, rec["path"])):
                fp.append(sid)
                if t.selects(codes, rec["q"]):
                    p1.append(sid)
                    p2.append(sid)
                elif here:
                    p2.append(sid)
        return dict(p1=p1, p2=p2, fingerprint=fp, presence=bool(here), pointer=bool(codes))

    def run(self):
        out = dict(positives={}, negatives={}, wrong_owner={})
        rows = []
        for cell in t.CELLS:
            flags = {k: {} for k in ("P1", "P2", "presence", "rule")}
            amb = Counter()
            for sid in self.sids:
                for seed in t.SEEDS:
                    nid = f"native:{cell}:{sid}:{seed}:f7"
                    status, p, det = self.query(nid, self.native.get(nid))
                    e = dict(id=nid, cell=cell, source=sid, seed=seed, status=status)
                    if status == "ok":
                        a = self.accepted(p, det["calls"][t.ALPHA], self.records)
                        e.update(a, P1=sid in a["p1"], P2=sid in a["p2"], rule=sid in a["fingerprint"])
                        amb[len(a["p2"])] += 1
                    for k in flags:
                        flags[k][(sid, seed)] = bool(e.get(k))
                    rows.append(e)
            out["positives"][cell] = dict({f"{k}_source_majority": t.majority(v) for k, v in flags.items()},
                                          P2_records_accepted_per_seed=dict(sorted(amb.items())),
                                          P2_other_record_seeds=sum(1 for e in rows if e["cell"] == cell and e.get("p2")
                                                                    and set(e["p2"]) - {e["source"]}))
        # Negatives, each under P1 and P2.
        neg = defaultdict(lambda: dict(n=0, ok=0, presence=0, p1=[], p2=[], fingerprint=0, unknown=0, blocked=0))

        def add(name, qid, status, a=None):
            f = neg[name]
            f["n"] += 1
            if status != "ok":
                f[status] += 1
                return
            f["ok"] += 1
            f["presence"] += a["presence"]
            f["fingerprint"] += len(a["fingerprint"])
            if a["p1"]:
                f["p1"].append(dict(id=qid, records=a["p1"]))
            if a["p2"]:
                f["p2"].append(dict(id=qid, records=a["p2"]))

        for tid, row in sorted(self.threat.items()):
            if row.get("arm") != "f7" or row.get("kind") not in ("T4", "T5"):
                continue
            status, p, det = self.query(tid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.records, skip={row["target"]}) if status == "ok" else None
            add(("N1_T4:" + str(row.get("condition"))) if row["kind"] == "T4" else "N2_T5", tid, status, a)
        for e in rows:
            status, p, det = self.query(e["id"], self.native.get(e["id"]))
            a = self.accepted(p, det["calls"][t.ALPHA], self.records, skip={e["source"]}) if status == "ok" else None
            add("N3_wrong_source:" + e["cell"], e["id"], status, a)
        c0 = [(f"clean:{sid}:unmarked", self.clean.get(f"clean:{sid}:unmarked")) for sid in self.sids]
        c0 += [(f"native:{cell}:{sid}:{seed}:unmarked", self.native.get(f"native:{cell}:{sid}:{seed}:unmarked"))
               for cell in t.CELLS for sid in self.sids for seed in t.SEEDS]
        for qid, row in c0:
            status, p, det = self.query(qid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.records) if status == "ok" else None
            add("N4_C0", qid, status, a)
        out["negatives"] = {k: dict(v, p1_accepts=len(v["p1"]), p2_accepts=len(v["p2"])) for k, v in sorted(neg.items())}
        # N5: beta enrols the seed-0 copy; presence under beta opens every beta record.
        for cell in t.CELLS:
            n, wrong, beta_presence, orig = 0, 0, 0, 0
            for sid in self.sids:
                nid = f"native:{cell}:{sid}:0:f7"
                status, p, det = self.query(nid, self.native.get(nid))
                if status != "ok":
                    continue
                n += 1
                q = ((det["calls"][t.BETA].get("raw") or {}).get("carriers") or {}).get("f5", {}).get("semantic_code")
                beta_records = {sid: dict(path=p, q=q)}
                b = self.accepted(p, det["calls"][t.BETA], beta_records)
                a = self.accepted(p, det["calls"][t.ALPHA], self.records)
                beta_presence += b["presence"]
                wrong += bool(b["p2"])
                orig += a["p2"] == [sid]
            out["wrong_owner"][cell] = dict(evaluable=n, beta_presence=beta_presence, wrong_owner_p2=wrong,
                                            original_unique_p2=orig)
        return out, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    result, rows = Probe(a.screen, []).run()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parent).stdout.strip()
    (a.out / "rows.json").write_text(json.dumps(rows, indent=1, default=str))
    (a.out / "run.json").write_text(json.dumps(dict(
        purpose="exploratory owner-presence pointer probe on the stage-B screen (development data, post hoc)",
        command=sys.argv, commit=commit, device="cpu", usd=0, started_at_utc=started,
        finished_at_utc=datetime.now(timezone.utc).isoformat(), result=result), indent=1, default=str))
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()

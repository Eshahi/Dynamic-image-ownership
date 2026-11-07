"""F7 registry replication (f7c) scorer: research/f7-dual-carrier-20261102/REPLICATION-PROTOCOL.md.

CPU only, USD 0, on the fetched screen outputs; no detector or model run. Two pointers, one frozen round-3 rule:
  P1  the stage-B pointer (found, read, decoded score >= 8.341671, record q within Hamming 6);
  P2  P1, else owner presence (semantic-tier `found` under the owner's key in the F5, v5 or combined test), which
      opens every record of that owner, the fresh records and the distractor records alike.
The owner's registry holds the 64 fresh F7 clean marks plus the fixed distractor records (section 3 of the protocol).
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f7_registry_test as t  # noqa: E402
from f7_presence_probe import presence  # noqa: E402

BAR = 55  # of 64: one-sided 95% Clopper-Pearson lower bound .767 >= .75
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
DISTRACTOR_ROOTS = ("registry-round3-20261017/canonical", "registry-fresh-20261016/canonical", "fresh-development-20261013")


def distractor_paths(assets):
    paths = []
    for root in DISTRACTOR_ROOTS:
        paths += sorted(p for p in (assets / root).rglob("*.png"))
    return paths


def mcnemar_one_sided(b, c):
    """Exact one-sided p for 'P2 recovers more sources than P1': b sources P2-only, c sources P1-only."""
    from math import comb
    n = b + c
    return 1.0 if n == 0 else sum(comb(n, k) for k in range(b, n + 1)) / 2 ** n


class Score(t.Scorer):
    def __init__(self, screen, image_dirs, distractors):
        super().__init__(screen, image_dirs)
        # A distractor must be another image: drop any whose bytes equal a screen source or target original.
        prepared = json.loads((Path(screen) / "prepared.json").read_text())
        own = {r["canonical_png_sha256"] for r in prepared["sources"].values()}
        kept = [p for p in distractors if t.sha256(p) not in own]
        self.dropped_distractors = [str(p) for p in distractors if p not in kept]
        self.registry = dict(self.records)
        for i, p in enumerate(kept):
            self.registry[f"distractor:{i}"] = dict(path=p, q=None)
        self.distractors = kept
        self.n_distractors = len(kept)

    def accepted(self, p, call, records, skip=()):
        codes, here = t.carried(call), presence(call)
        out = dict(p1=[], p2=[], fingerprint=[], presence=bool(here), pointer=bool(codes))
        for rid, rec in records.items():
            if rid in skip or rec["path"] is None:
                continue
            if self.rule(self.pair(p, rec["path"])):
                out["fingerprint"].append(rid)
                if rec["q"] is not None and t.selects(codes, rec["q"]):
                    out["p1"].append(rid)
                    out["p2"].append(rid)
                elif here:
                    out["p2"].append(rid)
        return out

    def run(self):
        res = dict(positives={}, negatives={}, wrong_owner={})
        rows = []
        for cell in t.CELLS:
            flags = {k: {} for k in ("P1", "P2", "presence", "pointer", "rule")}
            for sid in self.sids:
                for seed in t.SEEDS:
                    nid = f"native:{cell}:{sid}:{seed}:f7"
                    status, p, det = self.query(nid, self.native.get(nid))
                    e = dict(id=nid, cell=cell, source=sid, seed=seed, status=status)
                    if status == "ok" and self.records[sid]["path"] is not None:
                        a = self.accepted(p, det["calls"][t.ALPHA], self.registry)
                        s = self.pair(p, self.records[sid]["path"])
                        e.update(a, d1=s["d1"], b1=s["b1"], P1=sid in a["p1"], P2=sid in a["p2"],
                                 rule=sid in a["fingerprint"], other_p2=[r for r in a["p2"] if r != sid])
                    for k in flags:
                        flags[k][(sid, seed)] = bool(e.get(k))
                    rows.append(e)
            by = {k: t.majority(v) for k, v in flags.items()}
            maj = {k: {sid: sum(flags[k][(sid, s)] for s in t.SEEDS) >= 2 for sid in self.sids} for k in ("P1", "P2")}
            b = sum(maj["P2"][s] and not maj["P1"][s] for s in self.sids)
            c = sum(maj["P1"][s] and not maj["P2"][s] for s in self.sids)
            ok = [e for e in rows if e["cell"] == cell and e["status"] == "ok" and "d1" in e]
            res["positives"][cell] = dict({f"{k}_source_majority": v for k, v in by.items()}, n_sources=len(self.sids),
                                          p2_only_sources=b, p1_only_sources=c, mcnemar_one_sided_p=mcnemar_one_sided(b, c),
                                          other_record_accepts_p2=sum(bool(e.get("other_p2")) for e in ok),
                                          units=dict(ok=len(ok), not_ok=sum(1 for e in rows if e["cell"] == cell) - len(ok)),
                                          lowest_d1=min((e["d1"] for e in ok if e["d1"] is not None), default=None),
                                          lowest_b1=min((e["b1"] for e in ok if e["b1"] is not None), default=None))
        neg = defaultdict(lambda: dict(n=0, ok=0, unknown=[], blocked=[], presence=0, p1=[], p2=[], fingerprint=0))

        def add(name, qid, status, a=None):
            f = neg[name]
            f["n"] += 1
            if status != "ok":
                f[status].append(qid)
                return
            f["ok"] += 1
            f["presence"] += a["presence"]
            f["fingerprint"] += len(a["fingerprint"])
            for k in ("p1", "p2"):
                if a[k]:
                    f[k].append(dict(id=qid, records=a[k]))

        for tid, row in sorted(self.threat.items()):
            if row.get("arm") != "f7" or row.get("kind") not in ("T4", "T5"):
                continue
            status, p, det = self.query(tid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.registry, skip={row["target"]}) if status == "ok" else None
            add("N1_T4" if row["kind"] == "T4" else "N2_T5", tid, status, a)
        queries = [(f"clean:{sid}:f7", sid, self.clean.get(f"clean:{sid}:f7")) for sid in self.sids]
        queries += [(e["id"], e["source"], self.native.get(e["id"])) for e in rows]
        for qid, sid, row in queries:
            status, p, det = self.query(qid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.registry, skip={sid}) if status == "ok" else None
            add("N3_wrong_source", qid, status, a)
        c0 = [(f"clean:{sid}:unmarked", self.clean.get(f"clean:{sid}:unmarked")) for sid in self.sids]
        c0 += [(f"native:{cell}:{sid}:{seed}:unmarked", self.native.get(f"native:{cell}:{sid}:{seed}:unmarked"))
               for cell in t.CELLS for sid in self.sids for seed in t.SEEDS]
        for qid, row in c0:
            status, p, det = self.query(qid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.registry) if status == "ok" else None
            add("N4_C0", qid, status, a)
        res["negatives"] = {k: dict(v, p1_accepts=len(v["p1"]), p2_accepts=len(v["p2"]), unknown_n=len(v["unknown"]),
                                    blocked_n=len(v["blocked"])) for k, v in sorted(neg.items())}
        for cell in t.CELLS:
            out = dict(evaluable=0, unknown=0, blocked=0, beta_presence=0, wrong_owner_p1=0, wrong_owner_p2=0,
                       original_unique_p2=0, fingerprint_beta=0)
            for sid in self.sids:
                nid = f"native:{cell}:{sid}:0:f7"
                status, p, det = self.query(nid, self.native.get(nid))
                if status != "ok":
                    out[status] += 1
                    continue
                out["evaluable"] += 1
                q = ((det["calls"][t.BETA].get("raw") or {}).get("carriers") or {}).get("f5", {}).get("semantic_code")
                b = self.accepted(p, det["calls"][t.BETA], {"beta": dict(path=p, q=q)})
                a = self.accepted(p, det["calls"][t.ALPHA], self.registry)
                out["beta_presence"] += b["presence"]
                out["wrong_owner_p1"] += bool(b["p1"])
                out["wrong_owner_p2"] += bool(b["p2"])
                out["fingerprint_beta"] += bool(b["fingerprint"])
                out["original_unique_p2"] += a["p2"] == [sid]
            res["wrong_owner"][cell] = out
        core = {c: res["positives"][c]["P2_source_majority"] >= BAR for c in t.CORE}
        zero = {k: v["p2_accepts"] == 0 and v["p1_accepts"] == 0 for k, v in res["negatives"].items()}
        zero["N5_wrong_owner"] = all(res["wrong_owner"][c]["wrong_owner_p2"] == 0 and res["wrong_owner"][c]["wrong_owner_p1"] == 0
                                     for c in t.CELLS)
        unknown = {k: v["unknown_n"] for k, v in res["negatives"].items() if v["unknown_n"]}
        unknown.update({f"N5:{c}": v["unknown"] for c, v in res["wrong_owner"].items() if v["unknown"]})
        verdict = ("SCIENTIFIC_KILL" if not all(zero.values()) or not all(core.values())
                   else "INCOMPLETE" if unknown else "PASS")
        res.update(gates=dict({f"F_R_P2 {c} >= {BAR}/64": v for c, v in core.items()}, **zero), unknown_negatives=unknown,
                   secondary=dict(H_fix_R1_0_2=dict(p=res["positives"]["R1-0.2"]["mcnemar_one_sided_p"],
                                                     supported=res["positives"]["R1-0.2"]["mcnemar_one_sided_p"] < .05)),
                   verdict=verdict, n_sources=len(self.sids), n_distractors=self.n_distractors)
        return res, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--images", type=Path, action="append", default=[])
    ap.add_argument("--assets", type=Path, default=MAIN / ".thesis-build/assets")
    ap.add_argument("--no-distractors", action="store_true", help="dry run on another screen only")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    scorer = Score(a.screen, a.images, [] if a.no_distractors else distractor_paths(a.assets))
    result, rows = scorer.run()
    distractors = scorer.distractors
    result["dropped_distractors"] = scorer.dropped_distractors
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parent).stdout.strip()
    (a.out / "rows.json").write_text(json.dumps(rows, indent=1, default=str))
    (a.out / "run.json").write_text(json.dumps(dict(protocol="research/f7-dual-carrier-20261102/REPLICATION-PROTOCOL.md",
        command=sys.argv, commit=commit, device="cpu", usd=0, started_at_utc=started,
        finished_at_utc=datetime.now(timezone.utc).isoformat(), distractors=[str(p) for p in distractors], result=result),
        indent=1, default=str))
    print(json.dumps(dict(verdict=result["verdict"], gates=result["gates"],
                          positives={c: {k: v[k] for k in ("P1_source_majority", "P2_source_majority", "rule_source_majority")}
                                     for c, v in result["positives"].items()}), indent=1))


if __name__ == "__main__":
    main()

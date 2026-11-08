"""VINE-R + registry comparison (f7v) scorer: research/f7-dual-carrier-20261102/REPLICATION-VINE-ADDENDUM.md.

The same frozen round-3 rule, the same 64 fresh sources, copy-paste pairs and distractor records as f7c; VINE-R
replaces F7 as the pointer. VINE-R's payload is a public 100-bit message per source (encoder_transfer_test.message),
so the decoded message itself points at a record:
  V   record r is selected when the decoded message agrees with r's message in at least K bits, K the frozen
      VINE-R threshold binomial_threshold(100) (exact P[Bin(100, .5) >= K] <= 1e-4 per record).
Wrong owner: the attacker enrols each seed-0 copy under a record whose message is the wrong-owner message
(wrong_message_seed), and is selected only if the copy decodes to it.
CPU only, USD 0. The f7c scorer is untouched; this file reuses its distractor handling and gates.
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
import f7c_registry_score as s  # noqa: E402
from encoder_transfer_test import binomial_threshold, message  # noqa: E402

ARM, BITS = "vine-r", 100
K = binomial_threshold(BITS)
SEEDS_CONFIG = Path(__file__).resolve().parents[1] / "research/encoder-transfer-20261019/stage2b-config.json"


def matches(decoded, bits):
    if not isinstance(decoded, list) or bits is None or len(decoded) != len(bits):
        return None
    return sum(bool(a) == bool(b) for a, b in zip(decoded, bits))


def decoded_message(call):
    return (((call or {}).get("raw")) or {}).get("decoded_message")


class VScore(s.Score):
    def __init__(self, screen, image_dirs, distractors):
        t.Scorer.__init__(self, screen, image_dirs)  # loads journals and images; its F7 records stay empty here
        cfg = json.loads(SEEDS_CONFIG.read_text())
        self.wrong_seed = cfg["wrong_message_seed"]
        self.detect = t.journal(self.screen / f"detect-{ARM}-*-of-*.jsonl")
        self.sids = sorted({r["source"] for r in self.clean.values() if r.get("arm") == ARM}, key=int)
        self.records = {}
        for sid in self.sids:
            row = self.clean.get(f"clean:{sid}:{ARM}", {})
            self.records[sid] = dict(path=self.images.path(row) if row.get("status") == "ok" else None, q=None,
                                     bits=(row.get("payload") or {}).get("bits"))
        prepared = json.loads((Path(screen) / "prepared.json").read_text())
        own = {r["canonical_png_sha256"] for r in prepared["sources"].values()}
        kept = [p for p in distractors if t.sha256(p) not in own]
        self.dropped_distractors = [str(p) for p in distractors if p not in kept]
        self.registry = dict(self.records)
        for i, p in enumerate(kept):
            self.registry[f"distractor:{i}"] = dict(path=p, q=None, bits=None)
        self.distractors, self.n_distractors = kept, len(kept)

    def accepted(self, p, call, records, skip=()):
        decoded = decoded_message(call)
        out = dict(p1=[], p2=[], fingerprint=[], presence=False, pointer=False)
        pointed = {rid for rid, rec in records.items() if (matches(decoded, rec.get("bits")) or 0) >= K}
        out["presence"] = out["pointer"] = bool(pointed)
        for rid, rec in records.items():
            if rid in skip or rec["path"] is None:
                continue
            if self.rule(self.pair(p, rec["path"])):
                out["fingerprint"].append(rid)
                if rid in pointed:
                    out["p1"].append(rid)
                    out["p2"].append(rid)
        return out

    def run(self, f7c_rows=None):
        res = dict(positives={}, negatives={}, wrong_owner={}, K=K)
        rows = []
        for cell in t.CELLS:
            flags = {k: {} for k in ("V", "pointer", "rule")}
            for sid in self.sids:
                for seed in t.SEEDS:
                    nid = f"native:{cell}:{sid}:{seed}:{ARM}"
                    status, p, det = self.query(nid, self.native.get(nid))
                    e = dict(id=nid, cell=cell, source=sid, seed=seed, status=status)
                    if status == "ok" and self.records[sid]["path"] is not None:
                        call = det["calls"][t.ALPHA]
                        a = self.accepted(p, call, self.registry)
                        sc = self.pair(p, self.records[sid]["path"])
                        own = matches(decoded_message(call), self.records[sid]["bits"])
                        e.update(a, d1=sc["d1"], b1=sc["b1"], own_bits=own, V=sid in a["p1"],
                                 pointer=own is not None and own >= K, rule=sid in a["fingerprint"],
                                 other=[r for r in a["p1"] if r != sid])
                    for k in flags:
                        flags[k][(sid, seed)] = bool(e.get(k))
                    rows.append(e)
            ok = [e for e in rows if e["cell"] == cell and e["status"] == "ok" and "d1" in e]
            res["positives"][cell] = dict({f"{k}_source_majority": t.majority(v) for k, v in flags.items()},
                                          n_sources=len(self.sids), other_record_accepts=sum(bool(e.get("other")) for e in ok),
                                          units=dict(ok=len(ok), not_ok=sum(1 for e in rows if e["cell"] == cell) - len(ok)),
                                          median_own_bits=sorted(e["own_bits"] for e in ok if e["own_bits"] is not None)[len(ok) // 2] if ok else None)
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
            if a["p1"]:
                f["p1"].append(dict(id=qid, records=a["p1"]))
                f["p2"].append(dict(id=qid, records=a["p1"]))

        for tid, row in sorted(self.threat.items()):
            if row.get("arm") != ARM or row.get("kind") not in ("T4", "T5"):
                continue
            status, p, det = self.query(tid, row)
            a = self.accepted(p, det["calls"][t.ALPHA], self.registry, skip={row["target"]}) if status == "ok" else None
            add("N1_T4" if row["kind"] == "T4" else "N2_T5", tid, status, a)
        queries = [(f"clean:{sid}:{ARM}", sid, self.clean.get(f"clean:{sid}:{ARM}")) for sid in self.sids]
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
                nid = f"native:{cell}:{sid}:0:{ARM}"
                status, p, det = self.query(nid, self.native.get(nid))
                if status != "ok":
                    out[status] += 1
                    continue
                out["evaluable"] += 1
                call = det["calls"][t.ALPHA]
                b = self.accepted(p, call, {"beta": dict(path=p, q=None, bits=message(sid, BITS, self.wrong_seed))})
                a = self.accepted(p, call, self.registry)
                out["beta_presence"] += b["presence"]
                out["wrong_owner_p1"] += bool(b["p1"])
                out["wrong_owner_p2"] += bool(b["p1"])
                out["fingerprint_beta"] += bool(b["fingerprint"])
                out["original_unique_p2"] += a["p1"] == [sid]
            res["wrong_owner"][cell] = out
        core = {c: res["positives"][c]["V_source_majority"] >= s.BAR for c in t.CORE}
        zero = {k: v["p1_accepts"] == 0 for k, v in res["negatives"].items()}
        zero["N5_wrong_owner"] = all(res["wrong_owner"][c]["wrong_owner_p1"] == 0 for c in t.CELLS)
        unknown = {k: v["unknown_n"] for k, v in res["negatives"].items() if v["unknown_n"]}
        unknown.update({f"N5:{c}": v["unknown"] for c, v in res["wrong_owner"].items() if v["unknown"]})
        res.update(gates=dict({f"F_R_V {c} >= {s.BAR}/64": v for c, v in core.items()}, **zero), unknown_negatives=unknown,
                   label=("FAILS_GATES" if not all(zero.values()) or not all(core.values())
                          else "INCOMPLETE" if unknown else "PASSES_GATES"),
                   n_sources=len(self.sids), n_distractors=self.n_distractors)
        if f7c_rows is not None:
            res["paired_vs_f7"] = paired(rows, f7c_rows)
        return res, rows


def majority_by_source(rows, key):
    by = defaultdict(int)
    for e in rows:
        by[(e["cell"], e["source"])] += bool(e.get(key))
    return {k: v >= 2 for k, v in by.items()}


def paired(vrows, frows):
    """Per cell, source majority: VINE-R + registry (V) against F7 + registry (P2), exact two-sided McNemar."""
    from math import comb
    v, f = majority_by_source(vrows, "V"), majority_by_source(frows, "P2")
    out = {}
    for cell in t.CELLS:
        keys = [k for k in v if k[0] == cell and k in f]
        b = sum(v[k] and not f[k] for k in keys)
        c = sum(f[k] and not v[k] for k in keys)
        n = b + c
        tail = sum(comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n if n else 1.0
        out[cell] = dict(sources=len(keys), vine=sum(v[k] for k in keys), f7=sum(f[k] for k in keys),
                         vine_only=b, f7_only=c, mcnemar_two_sided_p=min(1.0, 2 * tail))
    return out


def clean_quality(screen):
    latest = {}
    for line in open(Path(screen) / "quality-0-of-1.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            latest[r["id"]] = r
    q = [r["original"] for r in latest.values() if r["id"].startswith("quality:clean:") and r["id"].endswith(":" + ARM)]
    strict = sum(x["psnr_db"] > 35 and x["ssim_rgb"] > .9 and 0 <= x["lpips"] < .1 for x in q)
    med = lambda k: sorted(x[k] for x in q)[len(q) // 2] if q else None
    return dict(n=len(q), strict=strict, psnr_median=med("psnr_db"), ssim_median=med("ssim_rgb"), lpips_median=med("lpips"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--images", type=Path, action="append", default=[])
    ap.add_argument("--assets", type=Path, default=s.MAIN / ".thesis-build/assets")
    ap.add_argument("--distractor-features", type=Path, help="server: precomputed distractor D1/B1 (f7c_remote_score)")
    ap.add_argument("--profile-run", type=Path)
    ap.add_argument("--f7c-rows", type=Path, help="f7c score rows.json for the paired comparison")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.profile_run:
        import claude_two_factor_instance as tf
        tf.PROFILE_RUN = a.profile_run
    started = datetime.now(timezone.utc).isoformat()
    if a.distractor_features:
        import f7c_remote_score as remote
        drows = remote.load(a.distractor_features)
        pseudo = [Path("distractor") / r["root"] / r["name"] for r in drows]
        sha = {str(p): r["sha256"] for p, r in zip(pseudo, drows)}
        real = t.sha256
        t.sha256 = lambda p: sha.get(str(p)) or real(p)
        scorer = VScore(a.screen, a.images, pseudo)
        for p, r in zip(pseudo, drows):
            scorer.F.memo[str(p)] = dict(D1=r["D1"], B1=r["B1"], g64=None)
    else:
        scorer = VScore(a.screen, a.images, s.distractor_paths(a.assets))
    f7c_rows = json.loads(a.f7c_rows.read_text()) if a.f7c_rows else None
    result, rows = scorer.run(f7c_rows)
    result["dropped_distractors"] = scorer.dropped_distractors
    result["vine_clean_quality"] = clean_quality(a.screen)
    a.out.mkdir(parents=True, exist_ok=False)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parent).stdout.strip()
    (a.out / "rows.json").write_text(json.dumps(rows, indent=1, default=str))
    (a.out / "run.json").write_text(json.dumps(dict(protocol="research/f7-dual-carrier-20261102/REPLICATION-VINE-ADDENDUM.md",
        command=sys.argv, commit=commit, device="cpu", usd=0, started_at_utc=started,
        finished_at_utc=datetime.now(timezone.utc).isoformat(), distractors=[str(p) for p in scorer.distractors],
        result=result), indent=1, default=str))
    print(json.dumps(dict(label=result["label"], gates=result["gates"], paired=result.get("paired_vs_f7"),
                          quality=result["vine_clean_quality"]), indent=1, default=str))


if __name__ == "__main__":
    main()

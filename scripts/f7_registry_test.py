"""F7 as the registry pointer: the frozen round-3 registry rule on the F7 screen's saved outputs.

Protocol: research/f7-dual-carrier-20261102/REGISTRY-PROTOCOL.md. CPU only, USD 0, no detector or model run.
  --mode proxy     section 5 early futility stop, from the laptop's unmarked seed-0 natives
  --mode manifest  the screen images still to fetch from the stopped instance
  --mode score     sections 2-4, the gated test
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import glob
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claude_round3_two_factor as r3  # noqa: E402  (imports claude_two_factor_instance, which hides the GPU)
import claude_two_factor_instance as tf  # noqa: E402
from f7_dual import UNION_THRESHOLD  # noqa: E402

ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
CORE, REPORTED, SEEDS = ("R0-0.2", "R1-0.1", "K3-0.2"), ("R1-0.2", "R0-0.4"), (0, 1, 2)
CELLS = CORE + REPORTED
FROZEN = tf.ROOT / "research/claude-round3-frozen-20261017.json"
BAR, PROXY_BAR, RADIUS = 12, 10, 6
PROTOCOL = "research/f7-dual-carrier-20261102/REGISTRY-PROTOCOL.md"


def journal(*patterns):
    """Latest row per id (journals append retries); detect rows are keyed by the item they read."""
    out = {}
    for pattern in patterns:
        for p in sorted(glob.glob(str(pattern))):
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    out[r.get("item") if r.get("kind") == "detect" else r["id"]] = r
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class Images:
    """Server paths resolve by file name to local copies whose SHA-256 must equal the journal row's."""

    def __init__(self, dirs):
        self.index = {p.stem: p for d in dirs for p in Path(d).glob("*.png")}
        self.checked, self.mismatch = {}, []

    def path(self, row):
        out = (row or {}).get("output") or {}
        p = self.index.get(Path(str(out.get("path", ""))).stem)
        if p is None:
            return None
        if p not in self.checked:
            self.checked[p] = sha256(p) == out.get("sha256")
            if not self.checked[p]:
                self.mismatch.append(str(p))
        return p if self.checked[p] else None


def distance(a, b):
    return (int(a, 16) ^ int(b, 16)).bit_count()


def carried(call):
    """Section 2 pointer: each carrier's decoded q when found, read, valid and at the F7 union threshold."""
    out = {}
    for name in ("f5", "v5"):
        s = (((call or {}).get("raw") or {}).get("carriers") or {}).get(name, {}).get("semantic") or {}
        word, score = s.get("decoded_code"), s.get("decoded_score")
        try:
            valid = isinstance(word, str) and len(word) == 8 and 0 <= int(word, 16) < 2 ** 32
        except ValueError:
            valid = False
        if s.get("found") is True and s.get("read") is True and valid and isinstance(score, (int, float)) and score >= UNION_THRESHOLD:
            out[name] = word
    return out


def selects(codes, q, carriers=("f5", "v5")):
    return q is not None and any(distance(codes[c], q) <= RADIUS for c in carriers if c in codes)


def majority(flags):
    """Sources with at least 2 of 3 seeds true; flags maps (source, seed) to bool."""
    by = defaultdict(int)
    for (sid, _), ok in flags.items():
        by[sid] += bool(ok)
    return sum(v >= 2 for v in by.values())


class Scorer:
    def __init__(self, screen, image_dirs):
        self.screen = Path(screen)
        fr = json.loads(FROZEN.read_text())
        self.taus = (fr["tau1_d1"], fr["tau2_b1"], fr["tauF_b1_fallback"])
        self.clean = journal(self.screen / "clean.jsonl")
        self.native = journal(self.screen / "native.jsonl")
        self.threat = journal(self.screen / "threats.jsonl")
        self.detect = journal(self.screen / "detect-f7-*-of-*.jsonl")
        self.images = Images([self.screen / "images", *image_dirs])
        self.F = tf.Features([])
        self.sids = sorted({r["source"] for r in self.clean.values() if r.get("arm") == "f7"}, key=int)
        self.records = {}
        for sid in self.sids:
            row = self.clean.get(f"clean:{sid}:f7", {})
            self.records[sid] = dict(path=self.images.path(row) if row.get("status") == "ok" else None,
                                     q=(row.get("payload") or {}).get("q"))

    def pair(self, q, r):
        x, y = self.F.get(q), self.F.get(r)
        return dict(d1=tf.cos(x["D1"], y["D1"]), b1=tf.cos(x["B1"], y["B1"]))

    def rule(self, p):
        return r3.rule(p, *self.taus)

    def query(self, row_id, row):
        """(status, image path, detect row); status is ok, blocked or unknown."""
        if row is None:
            return "unknown", None, None
        if row.get("status") == "safety_blocked":
            return "blocked", None, None
        p = self.images.path(row) if row.get("status") == "ok" else None
        det = self.detect.get(row_id)
        return ("ok", p, det) if p is not None and det is not None and det.get("status") == "ok" else ("unknown", p, det)

    def against(self, p, codes, skip=()):
        """Registry accepts of query p over every record not in skip, with and without the pointer."""
        out = dict(accepts=[], fingerprint_accepts=[])
        for sid in self.sids:
            rec = self.records[sid]
            if sid in skip or rec["path"] is None:
                continue
            ok = self.rule(self.pair(p, rec["path"]))
            if ok:
                out["fingerprint_accepts"].append(sid)
                if selects(codes, rec["q"]):
                    out["accepts"].append(sid)
        return out

    def positives(self):
        cells, rows = {}, []
        for cell in CELLS:
            flags = {k: {} for k in ("F_R", "F_R_f5", "F_R_v5", "pointer", "rule")}
            counts = Counter()
            for sid in self.sids:
                rec = self.records[sid]
                for seed in SEEDS:
                    nid = f"native:{cell}:{sid}:{seed}:f7"
                    status, p, det = self.query(nid, self.native.get(nid))
                    counts[status] += 1
                    e = dict(id=nid, cell=cell, source=sid, seed=seed, status=status)
                    if status == "ok" and rec["path"] is not None:
                        codes = carried(det["calls"][ALPHA])
                        s = self.pair(p, rec["path"])
                        ok = self.rule(s)
                        e.update(s, d1_abstain=s["d1"] is None, rule=ok, codes=codes,
                                 pointer_f5=selects(codes, rec["q"], ("f5",)), pointer_v5=selects(codes, rec["q"], ("v5",)))
                        e["pointer"] = e["pointer_f5"] or e["pointer_v5"]
                        e.update(F_R=ok and e["pointer"], F_R_f5=ok and e["pointer_f5"], F_R_v5=ok and e["pointer_v5"])
                    for k in flags:
                        flags[k][(sid, seed)] = bool(e.get(k))
                    rows.append(e)
            ok_rows = [e for e in rows if e["cell"] == cell and e["status"] == "ok"]
            cells[cell] = dict({f"{k}_source_majority": majority(v) for k, v in flags.items()},
                               F_R_seeds=sum(flags["F_R"].values()), units=dict(counts),
                               d1_abstain_seeds=sum(e.get("d1_abstain", False) for e in ok_rows),
                               d1=sorted(e["d1"] for e in ok_rows if e.get("d1") is not None),
                               b1=sorted(e["b1"] for e in ok_rows if e.get("b1") is not None))
        clean = {}
        for sid in self.sids:
            cid = f"clean:{sid}:f7"
            status, p, det = self.query(cid, self.clean.get(cid))
            clean[sid] = status == "ok" and self.rule(self.pair(p, self.records[sid]["path"])) and selects(carried(det["calls"][ALPHA]), self.records[sid]["q"])
        return cells, rows, dict(F_R=sum(clean.values()), of=len(clean))

    def negatives(self, positive_rows):
        fam = {}

        def add(name, row_id, status, result=None, **extra):
            f = fam.setdefault(name, dict(n=0, ok=0, unknown=[], blocked=[], accepts=[], fingerprint_accepts=0, pointer_any=0))
            f["n"] += 1
            if status != "ok":
                f[status].append(row_id)
                return
            f["ok"] += 1
            f["fingerprint_accepts"] += len(result["fingerprint_accepts"])
            f["pointer_any"] += bool(extra.pop("pointer_any", False))
            if result["accepts"]:
                f["accepts"].append(dict(id=row_id, records=result["accepts"], **extra))

        # N1 and N2: copies and false claims; the recipient's own record is not a false accept.
        for tid, row in sorted(self.threat.items()):
            if row.get("arm") != "f7" or row.get("kind") not in ("T4", "T5"):
                continue
            status, p, det = self.query(tid, row)
            res, codes = None, {}
            if status == "ok":
                codes = carried(det["calls"][ALPHA])
                res = self.against(p, codes, skip={row["target"]})
            add("N1_T4" if row["kind"] == "T4" else "N2_T5", tid, status, res, condition=row.get("condition"),
                donor=row.get("donor"), pointer_any=bool(codes))
        # N3: every F7 query against every other source's record.
        queries = [(f"clean:{sid}:f7", sid, self.clean.get(f"clean:{sid}:f7")) for sid in self.sids]
        queries += [(e["id"], e["source"], self.native.get(e["id"])) for e in positive_rows]
        for qid, sid, row in queries:
            status, p, det = self.query(qid, row)
            res = self.against(p, carried(det["calls"][ALPHA]), skip={sid}) if status == "ok" else None
            add("N3_wrong_source", qid, status, res)
        # N4: unmarked images against every record, their own source's included.
        c0 = [(f"clean:{sid}:unmarked", self.clean.get(f"clean:{sid}:unmarked")) for sid in self.sids]
        c0 += [(f"native:{cell}:{sid}:{seed}:unmarked", self.native.get(f"native:{cell}:{sid}:{seed}:unmarked"))
               for cell in CELLS for sid in self.sids for seed in SEEDS]
        for qid, row in c0:
            status, p, det = self.query(qid, row)
            codes = carried(det["calls"][ALPHA]) if status == "ok" else {}
            res = self.against(p, codes) if status == "ok" else None
            add("N4_C0", qid, status, res, pointer_any=bool(codes))
        return fam

    def wrong_owner(self):
        """N5, held-out E3 exact-copy case: beta enrols each seed-0 F7 native under its own q."""
        out = {}
        for cell in CORE:
            beta, entries = {}, []
            for sid in self.sids:
                nid = f"native:{cell}:{sid}:0:f7"
                status, p, det = self.query(nid, self.native.get(nid))
                q = ((((det or {}).get("calls", {}).get(BETA) or {}).get("raw") or {}).get("carriers") or {}).get("f5", {}).get("semantic_code")
                beta[sid] = dict(status=status, path=p, det=det, q=q)
            records = [dict(owner=ALPHA, sid=s, path=self.records[s]["path"], q=self.records[s]["q"]) for s in self.sids]
            records += [dict(owner=BETA, sid=s, path=b["path"], q=b["q"]) for s, b in beta.items() if b["status"] == "ok"]
            for sid, b in beta.items():
                if b["status"] != "ok":
                    entries.append(dict(source=sid, status=b["status"]))
                    continue
                codes = {o: carried(b["det"]["calls"][o]) for o in (ALPHA, BETA)}
                matched, fp = [], []
                for r in records:
                    if r["path"] is None or r["q"] is None:
                        continue
                    if self.rule(self.pair(b["path"], r["path"])):
                        fp.append(f"{r['owner'][-5:]}:{r['sid']}")
                        if selects(codes[r["owner"]], r["q"]):
                            matched.append(f"{r['owner'][-5:]}:{r['sid']}")
                entries.append(dict(source=sid, status="ok", matched=matched, fingerprint_matched=fp,
                                    beta_pointer=bool(codes[BETA]), wrong_owner=any(m.startswith("beta:") for m in matched)))
            ok = [e for e in entries if e["status"] == "ok"]
            out[cell] = dict(entries=entries, wrong_owner=sum(e["wrong_owner"] for e in ok),
                             unknown=[e["source"] for e in entries if e["status"] == "unknown"],
                             blocked=[e["source"] for e in entries if e["status"] == "blocked"],
                             original_unique=sum(e["matched"] == [f"alpha:{e['source']}"] for e in ok),
                             fingerprint_beta_matched=sum(any(m.startswith("beta:") for m in e["fingerprint_matched"]) for e in ok))
        return out

    def single_arm_pointer(self):
        """Reported only: pointer-alone source majority for the F5 r2 and v5 r3 arms (upper bound on their F_R)."""
        out = {}
        for arm in ("f5-r2", "v5-r3"):
            det = journal(self.screen / f"detect-{arm}-*-of-*.jsonl")
            q = {sid: ((self.clean.get(f"clean:{sid}:{arm}") or {}).get("payload") or {}).get("q") for sid in self.sids}
            cells = {}
            for cell in CELLS:
                flags = {}
                for sid in self.sids:
                    for seed in SEEDS:
                        raw = (((det.get(f"native:{cell}:{sid}:{seed}:{arm}") or {}).get("calls") or {}).get(ALPHA) or {}).get("raw") or {}
                        s = raw.get("semantic") or {}
                        w = s.get("decoded_code")
                        flags[(sid, seed)] = bool(s.get("found") is True and s.get("read") is True and isinstance(w, str)
                                                  and len(w) == 8 and q[sid] is not None and distance(w, q[sid]) <= RADIUS)
                cells[cell] = majority(flags)
            out[arm] = cells
        return out


def proxy(screen):
    """Section 5: frozen rule without pointer, seed-0 native against the same arm's clean image."""
    S = Scorer(screen, [])
    out = {}
    for arm in ("unmarked", "f5-r2"):
        cells = {}
        for cell in CELLS:
            passed, d1, abst, missing = 0, [], 0, []
            for sid in S.sids:
                p = S.images.path(S.native.get(f"native:{cell}:{sid}:0:{arm}"))
                ref = S.images.path(S.clean.get(f"clean:{sid}:{arm}"))
                if p is None or ref is None:
                    missing.append(sid)
                    continue
                s = S.pair(p, ref)
                passed += S.rule(s)
                abst += s["d1"] is None
                if s["d1"] is not None:
                    d1.append(round(s["d1"], 4))
            cells[cell] = dict(rule_pass=passed, missing=missing, d1_abstain=abst, d1=sorted(d1))
        out[arm] = cells
    gate = {c: out["unmarked"][c]["rule_pass"] >= PROXY_BAR for c in ("R1-0.1", "K3-0.2")}
    return dict(proxy=out, gate=gate, verdict="CONTINUE" if all(gate.values()) else "SCIENTIFIC_STOP",
                sha_mismatch=S.images.mismatch)


def manifest(screen):
    S = Scorer(screen, [])
    need = []
    for rid, row in S.native.items():
        if row.get("arm") in ("f7", "unmarked") and row.get("cell") in CELLS and row.get("status") == "ok" and S.images.path(row) is None:
            need.append(row["output"])
    for rid, row in S.threat.items():
        if row.get("arm") == "f7" and row.get("status") == "ok" and S.images.path(row) is None:
            need.append(row["output"])
    for row in S.clean.values():
        if row.get("arm") in ("f7", "unmarked") and S.images.path(row) is None:
            need.append(row["output"])
    uniq = {o["path"]: o["sha256"] for o in need}
    return dict(files=[dict(path=k, sha256=v) for k, v in sorted(uniq.items())], count=len(uniq))


def score(screen, image_dirs):
    S = Scorer(screen, image_dirs)
    cells, rows, clean = S.positives()
    fam = S.negatives(rows)
    n5 = S.wrong_owner()
    gates = {f"F_R {c}": cells[c]["F_R_source_majority"] >= BAR for c in CORE}
    for name in ("N1_T4", "N2_T5", "N3_wrong_source", "N4_C0"):
        gates[name] = not fam.get(name, {}).get("accepts")
    gates["N5_wrong_owner"] = all(v["wrong_owner"] == 0 for v in n5.values())
    unknown = {k: v["unknown"] for k, v in fam.items() if v["unknown"]}
    unknown.update({f"N5 {c}": v["unknown"] for c, v in n5.items() if v["unknown"]})
    verdict = "SCIENTIFIC_KILL" if not all(gates.values()) else ("INCOMPLETE" if unknown else "PASS")
    return dict(verdict=verdict, gates=gates, unknown_negatives=unknown, positives=cells, clean_F_R=clean, negatives=fam,
                wrong_owner=n5, single_arm_pointer=S.single_arm_pointer(), positive_rows=rows,
                frozen=dict(zip(("tau1_d1", "tau2_b1", "tauF_b1_fallback"), S.taus)), union_threshold=UNION_THRESHOLD,
                sha_mismatch=S.images.mismatch, d1_computed=S.F.computed_d1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("proxy", "manifest", "score"), required=True)
    ap.add_argument("--screen", type=Path, required=True, help="the F7 screen run folder (journals and images/)")
    ap.add_argument("--images", type=Path, action="append", default=[], help="extra folders of fetched screen images")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    tick = time.monotonic()
    res = dict(protocol=PROTOCOL, mode=a.mode, command=sys.argv, device="cpu", usd=0,
               commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tf.ROOT, text=True).strip(),
               started_at_utc=datetime.now(timezone.utc).isoformat())
    res.update(proxy(a.screen) if a.mode == "proxy" else manifest(a.screen) if a.mode == "manifest" else score(a.screen, a.images))
    res["duration_seconds"] = time.monotonic() - tick
    (a.out / "run.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    if a.mode == "manifest":
        (a.out / "fetch-list.txt").write_text("".join(f["path"] + "\n" for f in res["files"]))
    shown = {k: v for k, v in res.items() if k not in ("positive_rows", "negatives", "wrong_owner", "files", "command")}
    print(json.dumps(shown, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()

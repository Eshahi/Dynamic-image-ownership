"""Phase-B analysis under amendment B1: 13-slot Holm family, negative gates, exploratory B1 law, descriptive tables.

Written by Claude (Opus 5.5) on 2026-10-26, before any Phase-B outcome exists. It implements
analysis/confirmatory-statistics.md as amended by phase-b/AMENDMENT-B1.md:
  H1  p1 = max(Lower(k+_R1.1; .10), Lower(k+_R1.2; .10))  F5 possible-majority counts (unresolved calls positive)
  H2  p2 = Upper(k_R0.2; .80)                              F5 all-attempt source majority
  H3  p3 = Upper(k_joint; .80)                             joint retain/lose/strictly-milder-quality event
  H4  p4 = 1  UNEVALUATED_PREREQUISITE_FAILURE (comparator BASELINE_UNAVAILABLE at the Phase-A freeze)
  H5  eight slots p = 1  (attacks A and B INACTIVE_QUALITY_INELIGIBLE)
  H6  p6 = max_c Upper(k_c; .90)  VINE-R known-message presence at R0 .2, R1 .1, R1 .2
Holm at alpha .05 with the lexical slot-ID tie rule. Binomial tails are exact rationals. The denominator is the
planned 200; a source without a row contributes unresolved calls. Stdlib only.

Usage: python -I analyze_phase_b.py RUN_FOLDER AMENDMENT_JSON OUT_JSON OUT_MD
"""
import json
import math
import statistics
import sys
from fractions import Fraction
from pathlib import Path

N = 200
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from encoder_transfer_test import ALPHA, BETA  # noqa: E402  (stdlib-only module)
MARKS = ["f5-r2", "v5-r3", "wam", "vine-r"]
CELLS = ["R0-0.1", "R0-0.2", "R0-0.4", "R1-0.1", "R1-0.2", "R1-0.4", "K3-0.2"]
SEEDS = (12, 13, 14)
SLOTS = ["H1", "H2", "H3", "H4"] + [f"H5-{a}-{m}" for a in "AB" for m in MARKS] + ["H6"]


def journal(path):
    rows = {}
    if Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rows[r["id"]] = r
    return rows


def binom_upper(k, p0, n=N):
    p0 = Fraction(p0).limit_denominator(1000)
    return float(sum(Fraction(math.comb(n, j)) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def binom_lower(k, p0, n=N):
    p0 = Fraction(p0).limit_denominator(1000)
    return float(sum(Fraction(math.comb(n, j)) * p0 ** j * (1 - p0) ** (n - j) for j in range(0, k + 1)))


def cdf_float(k, p, n):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(0, k + 1))


def cp_upper(f, n, conf):
    """One-sided Clopper-Pearson upper bound for f events of n at confidence conf (bisection)."""
    if f >= n:
        return 1.0
    lo, hi = f / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf_float(f, mid, n) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


class Calls:
    def __init__(self, det, owners):
        self.det, self.alpha, self.beta = det, owners[0], owners[1]

    def row(self, method, item):
        r = self.det.get(f"det:{method}:{item}")
        return r if r and r.get("status") == "ok" else None

    def positive(self, method, item):
        """Frozen positive endpoint: C (F5/v5, correct owner) or known-message presence (WAM/VINE-R); None = unresolved."""
        r = self.row(method, item)
        if r is None:
            return None
        c = r["calls"].get(self.alpha)
        if not c or c.get("status") != "ok":
            return None
        if method in ("f5-r2", "v5-r3"):
            return bool(c["endpoints"]["C"])
        return bool(c["presence"]["present"])

    def negative_event(self, method, item, kind):
        """Negative-battery event: any-carrier A (F5/v5) or presence (WAM/VINE-R); kind C0 or wrong; None = unresolved."""
        r = self.row(method, item)
        if r is None:
            return None
        if method in ("f5-r2", "v5-r3"):
            c = r["calls"].get(self.alpha if kind == "C0" else self.beta)
            if not c or c.get("status") != "ok":
                return None
            return bool(c["endpoints"]["A"])
        c = r["calls"].get(self.alpha)
        if not c or c.get("status") != "ok":
            return None
        p = c["presence"] if kind == "C0" else c.get("wrong_message_presence")
        return None if p is None else bool(p["present"])

    def margin(self, item):
        r = self.row("f5-r2", item)
        try:
            sem = r["calls"][self.alpha]["raw"]["semantic"]
            m = float(sem["decoded_score"]) - float(sem["decoded_threshold"])
            return m if math.isfinite(m) else None
        except (TypeError, KeyError, ValueError):
            return None


def majority(vals):
    pos, unres = sum(v is True for v in vals), sum(v is None for v in vals)
    return int(pos >= 2), int(pos + unres >= 2), pos, unres


def finite_q(q):
    return q is not None and all(isinstance(q.get(k), (int, float)) and math.isfinite(q[k]) for k in ("lpips", "psnr_db", "ssim_rgb")) \
        and not q.get("psnr_infinite")


def med(xs):
    xs = [x for x in xs if x is not None and math.isfinite(x)]
    return statistics.median(xs) if xs else None


def main():
    run, amend = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    src = json.loads((run / "phase-b-sources.json").read_text(encoding="utf-8"))
    ids = [s["source_id"] for s in src["sources"]]
    clean, fc, oc = journal(run / "clean.jsonl"), journal(run / "forecast.jsonl"), journal(run / "outcome.jsonl")
    det, qual = journal(run / "detect.jsonl"), journal(run / "quality.jsonl")
    owners = [ALPHA, BETA]
    calls = Calls(det, owners)
    absent = N - len(ids)  # sources never acquired: every call unresolved, every quality missing

    def cell_calls(method, cell, s, arm=None):
        return [calls.positive(method, f"native:{cell}:{s}:{seed}:{arm or method}") for seed in SEEDS]

    # Descriptive endpoint grid.
    grid = {}
    for cell in CELLS:
        for m in MARKS:
            y = yp = pos = unres = 0
            for s in ids:
                a, b, p, u = majority(cell_calls(m, cell, s))
                y, yp, pos, unres = y + a, yp + b, pos + p, unres + u
            yp += absent
            grid[f"{cell}|{m}"] = dict(Y=y, Yplus=yp, positive_calls=pos, unresolved_calls=unres + 3 * absent, n=N)
    clean_pos = {m: sum(calls.positive(m, f"clean:{s}:{m}:None:None") is True for s in ids) for m in MARKS}
    codec_pos = {m: sum(calls.positive(m, f"ctrlB-codec:{s}:{m}") is True for s in ids) for m in MARKS}

    # H1, H2, H6.
    k1 = {c: grid[f"{c}|f5-r2"]["Yplus"] for c in ("R1-0.1", "R1-0.2")}
    p1 = max(binom_lower(k, .10) for k in k1.values())
    k2 = grid["R0-0.2|f5-r2"]["Y"]
    p2 = binom_upper(k2, .80)
    k6 = {c: grid[f"{c}|vine-r"]["Y"] for c in ("R0-0.2", "R1-0.1", "R1-0.2")}
    p6 = max(binom_upper(k, .90) for k in k6.values())

    # H3: joint event per source, qualities against the same final F5 marked input u.
    def triples(cell, s):
        out = []
        for seed in SEEDS:
            q = (qual.get(f"q:native:{cell}:{s}:{seed}:f5-r2") or {})
            q = q.get("attack") if q.get("status") == "ok" else None
            out.append(q if finite_q(q) else None)
        return out
    joint, h3_rows = 0, {"R1 lost (Y+=0)": 0, "R0 retained (Y=1)": 0, "qualities complete": 0, "strictly milder all three": 0}
    for s in ids:
        _, yp_r1, _, _ = majority(cell_calls("f5-r2", "R1-0.1", s))
        y_r0, _, _, _ = majority(cell_calls("f5-r2", "R0-0.2", s))
        t1, t0 = triples("R1-0.1", s), triples("R0-0.2", s)
        complete = all(t is not None for t in t1 + t0)
        milder = complete and med([t["lpips"] for t in t1]) < med([t["lpips"] for t in t0]) and \
            med([t["psnr_db"] for t in t1]) > med([t["psnr_db"] for t in t0]) and med([t["ssim_rgb"] for t in t1]) > med([t["ssim_rgb"] for t in t0])
        h3_rows["R1 lost (Y+=0)"] += yp_r1 == 0
        h3_rows["R0 retained (Y=1)"] += y_r0 == 1
        h3_rows["qualities complete"] += complete
        h3_rows["strictly milder all three"] += bool(milder)
        joint += int(yp_r1 == 0 and y_r0 == 1 and milder)
    p3 = binom_upper(joint, .80)

    pvals = {"H1": p1, "H2": p2, "H3": p3, "H4": 1.0, "H6": p6, **{f"H5-{a}-{m}": 1.0 for a in "AB" for m in MARKS}}
    order = sorted(SLOTS, key=lambda h: (pvals[h], h))
    holm, running, rejecting = {}, 0.0, True
    for j, h in enumerate(order, start=1):
        running = max(running, min(1.0, (14 - j) * pvals[h]))
        rejecting = rejecting and pvals[h] <= .05 / (14 - j)
        holm[h] = dict(rank=j, p=pvals[h], threshold=.05 / (14 - j), adjusted=running, rejected=rejecting)
    status = {"H4": "UNEVALUATED_PREREQUISITE_FAILURE (comparator BASELINE_UNAVAILABLE)",
              **{f"H5-{a}-{m}": "UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible)" for a in "AB" for m in MARKS}}
    for h in ("H1", "H2", "H3", "H6"):
        status[h] = "SUPPORTED" if holm[h]["rejected"] else "INCONCLUSIVE_SUPPORT"

    # Negative gates: source-any events over every executed item of the declared battery.
    gates = {}
    for m in MARKS:
        for kind in ("C0", "wrong"):
            f = u = 0
            for s in ids:
                arm = "unmarked" if kind == "C0" else m
                battery = [f"clean:{s}:{arm}:None:None", f"ctrlB-codec:{s}:{arm}"] + \
                          [f"native:{c}:{s}:{seed}:{arm}" for c in CELLS for seed in SEEDS]
                ev = [calls.negative_event(m, it, kind) for it in battery]
                if any(e is True for e in ev):
                    f += 1
                elif any(e is None for e in ev):
                    u += 1
            u += absent
            gates[f"{m}|{kind}"] = dict(events=f, unresolved_sources=u, passed=f == 0 and u == 0,
                                       cp95_upper=cp_upper(f, N, .95), cp95_upper_bonferroni8=cp_upper(f, N, 1 - .05 / 8),
                                       cp95_upper_with_unresolved=cp_upper(f + u, N, .95))

    # Exploratory B1 law (outside Holm): R0 cells only.
    q90 = amend["q90_R0"]["value"]
    b1 = {}
    for cell in ("R0-0.1", "R0-0.2", "R0-0.4"):
        ident = mism = brier_n = brier = covered = margin_n = 0
        bias_sum = 0
        law_pos = act_pos = 0
        for s in ids:
            bits, actual = [], cell_calls("f5-r2", cell, s)
            for seed in SEEDS:
                f = (fc.get(f"c0:{cell}:{s}:{seed}") or {}).get("forecast") or {}
                bits.append(bool(f["C"]) if f.get("status") == "ok" else None)
                m_act = calls.margin(f"native:{cell}:{s}:{seed}:f5-r2")
                if f.get("status") == "ok" and f.get("margin") is not None and m_act is not None:
                    margin_n += 1
                    covered += abs(m_act - f["margin"]) <= q90
            a_lo, a_hi = int(sum(b is True for b in bits) >= 2), int(sum(b is not False for b in bits) >= 2)
            y_lo, y_hi, _, _ = majority(actual)
            mism += int(max(abs(a - y) for a in {a_lo, a_hi} for y in {y_lo, y_hi}) > 0)
            if a_lo == a_hi:
                ident += 1
                law_pos += a_lo
                act_pos += y_lo
                bias_sum += a_lo - y_lo
                brier += (a_lo - y_lo) ** 2
                brier_n += 1
        b1[cell] = dict(identified_sources=ident, law_positive=law_pos, actual_positive_all_attempt=act_pos,
                        rate_error_identified=bias_sum / ident if ident else None, worst_mismatch=mism + absent,
                        brier_identified=brier / brier_n if brier_n else None,
                        margin_coverage=covered / margin_n if margin_n else None, margin_trajectories=margin_n)

    # Quality (T7, descriptive): medians over all available outputs.
    qtab = {}
    for cell in CELLS + ["ctrlB-codec"]:
        for arm in ["unmarked", *MARKS]:
            rows = [r for r in qual.values() if r.get("status") == "ok" and r["arm"] == arm and
                    (r["item"].startswith(f"native:{cell}:") if cell != "ctrlB-codec" else r["item"].startswith("ctrlB-codec:"))]
            if rows:
                qtab[f"{cell}|{arm}"] = dict(n=len(rows), **{f"{ref}_{k}": med([r[ref][k] for r in rows]) for ref in ("attack", "total")
                                                            for k in ("lpips", "psnr_db", "ssim_rgb")})
    cq = {m: [clean[f"clean:{s}:{m}:None:None"].get("distortion") for s in ids if f"clean:{s}:{m}:None:None" in clean] for m in MARKS}
    clean_quality = {m: dict(n=len([d for d in v if d]), lpips=med([d["lpips"] for d in v if d]), psnr=med([d["psnr_db"] for d in v if d]),
                             ssim=med([d["ssim_rgb"] for d in v if d])) for m, v in cq.items()}

    from collections import Counter
    accounting = dict(sources=len(ids), planned=N, absent_sources=absent,
                      c0=Counter(f"{r['cell']}|{r['status']}" for r in fc.values() if r.get("kind") == "c0"),
                      outcome=Counter(f"{r.get('cell', r['kind'])}|{r['status']}" for r in oc.values()),
                      detect=Counter(f"{r['method']}|{r['status']}" for r in det.values()),
                      quality=Counter(r["status"] for r in qual.values()),
                      forecasts=Counter((r.get("forecast") or {}).get("status", "none") for r in fc.values()
                                        if r.get("kind") == "c0" and r["family"] == "R0"))
    result = dict(schema="et-final-phase-b-results-v1", grid=grid, clean_positive=clean_pos, codec_positive=codec_pos,
                  h1=dict(kplus=k1, p=p1), h2=dict(k=k2, p=p2), h3=dict(k_joint=joint, components=h3_rows, p=p3),
                  h6=dict(k=k6, p=p6), holm=holm, status=status, negative_gates=gates, b1_law=b1, quality=qtab,
                  clean_quality=clean_quality, accounting={k: dict(v) if isinstance(v, Counter) else v for k, v in accounting.items()},
                  owners=owners)
    Path(sys.argv[3]).write_text(json.dumps(result, indent=1), encoding="utf-8")

    md = ["# Phase B results (amendment B1)", "", f"Sources {len(ids)} of {N} planned.", "", "## Confirmatory family (Holm, alpha .05)", "",
          "| Slot | Count | p | Holm rank | threshold | adjusted | status |", "|---|---|---|---|---|---|---|"]
    counts = {"H1": f"k+ R1 .1 {k1['R1-0.1']}, R1 .2 {k1['R1-0.2']}", "H2": f"{k2}/200", "H3": f"{joint}/200",
              "H6": ", ".join(f"{c} {k}" for c, k in k6.items())}
    for h in SLOTS:
        x = holm[h]
        md.append(f"| {h} | {counts.get(h, '–')} | {x['p']:.3g} | {x['rank']} | {x['threshold']:.4g} | {x['adjusted']:.3g} | {status[h]} |")
    md += ["", "## Source majorities by cell and arm (Y all-attempt / Y+ possible-majority)", "",
           "| Cell | " + " | ".join(MARKS) + " |", "|---|" + "---|" * len(MARKS)]
    for cell in CELLS:
        md.append(f"| {cell} | " + " | ".join(f"{grid[f'{cell}|{m}']['Y']} / {grid[f'{cell}|{m}']['Yplus']}" for m in MARKS) + " |")
    md.append("| clean | " + " | ".join(str(clean_pos[m]) for m in MARKS) + " |")
    md.append("| B-codec | " + " | ".join(str(codec_pos[m]) for m in MARKS) + " |")
    md += ["", "## Negative gates (source-any events over the executed battery)", "", "| Stratum | events | unresolved sources | passed | 95% CP upper | Bonferroni-8 upper |",
           "|---|---|---|---|---|---|"]
    for k, g in gates.items():
        md.append(f"| {k} | {g['events']} | {g['unresolved_sources']} | {g['passed']} | {g['cp95_upper']:.4f} | {g['cp95_upper_bonferroni8']:.4f} |")
    md += ["", "## Exploratory B1 law (outside Holm)", "", "| Cell | identified | law positive | actual positive | rate error | worst mismatch | Brier | margin coverage (q90_R0) |",
           "|---|---|---|---|---|---|---|---|"]
    for cell, b in b1.items():
        md.append(f"| {cell} | {b['identified_sources']} | {b['law_positive']} | {b['actual_positive_all_attempt']} | "
                  f"{b['rate_error_identified'] if b['rate_error_identified'] is None else round(b['rate_error_identified'], 3)} | {b['worst_mismatch']} | "
                  f"{b['brier_identified'] if b['brier_identified'] is None else round(b['brier_identified'], 3)} | "
                  f"{b['margin_coverage'] if b['margin_coverage'] is None else round(b['margin_coverage'], 3)} ({b['margin_trajectories']}) |")
    md += ["", "## H3 components", ""] + [f"- {k}: {v}" for k, v in h3_rows.items()]
    md += ["", "## Quality medians (attack d(y,u) / total d(y,x)): LPIPS, PSNR, SSIM", "", "| Cell | arm | n | attack | total |", "|---|---|---|---|---|"]
    for k, q in qtab.items():
        c, a = k.split("|")
        f = lambda p: "–" if q[f"{p}_lpips"] is None else f"{q[f'{p}_lpips']:.3f}, {q[f'{p}_psnr_db']:.2f}, {q[f'{p}_ssim_rgb']:.3f}"
        md.append(f"| {c} | {a} | {q['n']} | {f('attack')} | {f('total')} |")
    md += ["", "Clean embedding quality d(u,x) medians: " + "; ".join(f"{m} LPIPS {v['lpips']}, PSNR {v['psnr']}, SSIM {v['ssim']} (n {v['n']})"
                                                             for m, v in clean_quality.items()), "",
           "## Accounting", "", "```", json.dumps(result["accounting"], indent=1), "```"]
    Path(sys.argv[4]).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(dict(status=status, p={h: holm[h]["p"] for h in ("H1", "H2", "H3", "H6")}), indent=1))


if __name__ == "__main__":
    main()

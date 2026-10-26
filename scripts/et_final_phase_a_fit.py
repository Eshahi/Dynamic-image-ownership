"""Final-study Phase A, stages 3-4: detector release (after the attack freeze), kappa, q90, quality comparator, freeze.

Written by Claude (Opus 5.5) on 2026-10-26 under the user's Phase-A approval (option (a)).

detect: runs the unchanged stage-2 detectors (F5 r2, v5 r3, WAM, VINE-R adapters of encoder_transfer_runtime) on
    every Phase-A native output (each arm's own outputs with its own detector; C0 with all four) and on the frozen
    attacks' outputs and controls. It refuses to start unless attack-freeze.json exists. For C0 native outputs it also
    stores the seven-view semantic descriptor f0 (the law's C0 proxy) and the C0-versus-original quality.
fit: kappa (training-missingness-design.md section 2), quality comparator (quality-baseline-contract.md), q90
    (section 4, calibration sources, native score units), development law/comparator diagnostics, and the freeze file.

Usage: python scripts/et_final_phase_a_fit.py --stage detect|fit --assets ... --images ... --out ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
import et_final_phase_a as pa  # noqa: E402
from encoder_transfer_test import ALPHA, BETA, ROOT  # noqa: E402

MARKS = ["f5-r2", "v5-r3", "wam", "vine-r"]
CELLS = [f"{f}-{s}" for f, s in pa.CELLS]


def stage2a_rows(path):
    rows = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            r = json.loads(line)
            rows[r["id"]] = r
    return rows


def detection_items(native, attacks, freeze):
    """(item id, image path, arm of the image, control) for every output the frozen protocol reads."""
    items = []
    for r in native.latest.values():
        if r["kind"] == "native" and r.get("status") == "ok":
            items.append((r["id"], r["output"]["path"], r["arm"], "C0" if r["arm"] == "unmarked" else "C1", r["source"]))
    a_sel = (freeze.get("A") or {}).get("selected")
    b_sel = (freeze.get("B") or {}).get("selected")
    for r in attacks.latest.values():
        if r.get("status") != "ok":
            continue
        keep = (r["kind"] == "gridA" and a_sel and r["strength"] == a_sel[0]) or r["kind"] == "ctrlA" or \
               (r["kind"] == "gridB" and b_sel and [r["epsilon"], r["lam"]] == list(b_sel)) or r["kind"].startswith("ctrlB-")
        if not keep:
            continue
        control = "C0" if r["arm"] == "unmarked" else "C1"
        items.append((r["id"], r["output"]["path"], r["arm"], control, r["source"]))
        if r.get("first"):
            items.append((r["id"] + ":first", r["first"]["path"], r["arm"], control, r["source"]))
    return items


def detect(args):
    import torch
    torch.set_num_threads(14)
    freeze_path = args.out / "attack-freeze.json"
    if not freeze_path.exists():
        raise SystemExit("detector release requires the attack freeze (05-informed-attacks.md)")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    native = pa.Journal(args.out / "native.jsonl")
    attacks = pa.Journal(args.out / "attacks.jsonl")
    journal = pa.Journal(args.out / "detect.jsonl")
    config, _ = pilot.channel_specs()
    s2a = stage2a_rows(args.stage2a)
    items = detection_items(native, attacks, freeze)
    for method in MARKS:
        todo = [it for it in items if (it[2] == method or it[2] == "unmarked") and not journal.done(f"det:{method}:{it[0]}")]
        if not todo:
            continue
        adapter = rt.Internal(args.assets, config) if method in ("f5-r2", "v5-r3") else rt.Wam(args.assets) if method == "wam" else rt.Vine(args.assets)
        quality = None
        if method == "f5-r2":
            from m1_latent_reconstruction import quality as q
            import three_threat_models as models
            import importlib.metadata
            lp = models.load_lpips(args.assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
            quality = (q, models, lp)
        for n, (uid, path, arm, control, source) in enumerate(todo):
            row = dict(id=f"det:{method}:{uid}", kind="detect", method=method, item=uid, arm=arm, control=control, source=source)
            tick = time.monotonic()
            try:
                rgb = rt.load_rgb(path)
                if method in ("f5-r2", "v5-r3"):
                    payload = s2a[f"clean:{source}:{method}:None:None"].get("payload") if control == "C1" else None
                    if method == "f5-r2" and control == "C0" and uid.startswith("native:"):
                        # The law's C0 proxy: the seven-view descriptor, and C0-versus-original quality.
                        features = adapter.features(rgb, 7)
                        latent = adapter.reader.latent(rgb)
                        result = adapter._detect(rgb, "f5", ALPHA, features, latent)
                        calls = {ALPHA: dict(status="ok", raw=result, endpoints=rt.endpoints(result, None))}
                        row["f0"] = [float(x) for x in features]
                        original = rt.load_rgb(args.assets / "sources" / f"{source}.png")
                        q, models, lp = quality
                        row["c0_quality"] = {**q(original, rgb), "lpips": models.lpips_score(lp, original, rgb)}
                    else:
                        calls = adapter.detect(rgb, method, payload, control)
                else:
                    bits = rt.message(source, config["payload_bits"][method], config["message_seed"])
                    calls = {ALPHA: adapter.detect(rgb, bits)}
                    wrong = rt.message(source, config["payload_bits"][method], config["wrong_message_seed"])
                    calls[ALPHA]["wrong_message_presence"] = rt.presence(calls[ALPHA]["raw"].get("decoded_message"), wrong)
                row["calls"] = calls
                row["status"] = "ok"
            except Exception:
                row["status"] = "error_terminal"
                row["error"] = traceback.format_exc()[-2000:]
            row["seconds"] = time.monotonic() - tick
            journal.append(row)
            if n % 200 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] {method} {n}/{len(todo)}", flush=True)
        adapter = None
        rt.release()


# ---------------------------------------------------------------- fit

def semantic_predict(chips, features, profile):
    """The unchanged F5 semantic reader applied to a predicted chip vector and the C0 descriptor (soft binding)."""
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    base = v5.base
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(ALPHA)
    decision = checked["decision"]
    q_now = v5._semantic(None, checked, key, config, features, binding=False)
    semantic = v5._channel_result(v5._key_test([float(c) for c in chips], v5._semantic_table(owner, key, config), q_now),
                                  float(decision["false_positive_target"]), 1, q_now)
    status = None
    if semantic["found"]:
        limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
        status, _ = f5._semantic_status(semantic, features, key, config, limits, True, "soft")
    content_match = bool(semantic["found"] and base._STATUS_RANK[status] == 0)
    margin = None
    if semantic.get("decoded_score") is not None and semantic.get("decoded_threshold") is not None:
        margin = float(semantic["decoded_score"]) - float(semantic["decoded_threshold"])
    return dict(C=bool(semantic.get("read") and content_match), read=bool(semantic.get("read")), found=bool(semantic["found"]),
                content_match=content_match, margin=margin)


def logistic_fit(X, y, w):
    """Weighted binary NLL + .5*sum(beta_j^2) (intercept unpenalized), Newton with backtracking (contract)."""
    import numpy as np
    n, p = X.shape
    Z = np.hstack([np.ones((n, 1)), X])
    beta = np.zeros(p + 1)
    pen = np.r_[0.0, np.ones(p)]

    def objective(b):
        eta = Z @ b
        return float(np.sum(w * (np.logaddexp(0, eta) - y * eta)) + .5 * np.sum(pen * b * b))
    status = "max_iterations"
    for it in range(200):
        mu = 1 / (1 + np.exp(-(Z @ beta)))
        grad = Z.T @ (w * (mu - y)) + pen * beta
        if np.max(np.abs(grad)) <= 1e-8:
            status = "converged"
            break
        H = (Z * (w * mu * (1 - mu))[:, None]).T @ Z + np.diag(pen)
        step = np.linalg.solve(H, grad)
        t, f0 = 1.0, objective(beta)
        while objective(beta - t * step) > f0 - 1e-4 * t * grad @ step and t > 1e-10:
            t /= 2
        beta = beta - t * step
    return beta, dict(status=status, iterations=it + 1, gradient_inf=float(np.max(np.abs(grad))), objective=objective(beta))


def fit(args):
    import numpy as np
    native = pa.Journal(args.out / "native.jsonl")
    det = pa.Journal(args.out / "detect.jsonl")
    config, _ = pilot.channel_specs()
    profile = pilot.read(ROOT / config["profile_file"])
    order = pa.development_order()
    fit_ids, cal_ids = order[:30], order[30:]
    s2a = stage2a_rows(args.stage2a)
    seeds = pa.SEEDS
    out = dict(fit_sources=fit_ids, calibration_sources=cal_ids, cells=CELLS,
               option_a="native trajectories use the derivative path's classic attention and explicit LayerNorm (pilot report)")

    def f5_c(cell, source, seed):
        """Operational F5 C of the marked native output (blocked/missing = None)."""
        r = det.latest.get(f"det:f5-r2:native:{cell}:{source}:{seed}:f5-r2")
        n = native.latest.get(f"native:{cell}:{source}:{seed}:f5-r2")
        if not n or n.get("status") != "ok":
            return None
        if not r or r.get("status") != "ok" or r["calls"][ALPHA].get("status") != "ok":
            return None
        return bool(r["calls"][ALPHA]["endpoints"]["C"])

    # Kappa on the 30 fit sources.
    num = den = 0.0
    avail = defaultdict(int)
    rows = []
    for cell in CELLS:
        for source in fit_ids:
            for seed in seeds:
                law = native.latest.get(f"law:{cell}:{source}:{seed}")
                if law and law.get("status") == "ok":
                    v, b, p1 = (np.asarray(law[k]) for k in ("v", "b", "p1"))
                    num += (1 / 18) * float(v @ (p1 - b))
                    den += (1 / 18) * float(v @ v)
                    avail[(cell, source)] += 1
    per_cell = {cell: sum(avail[(cell, s)] for s in fit_ids) for cell in CELLS}
    triplets_ok = all(avail[(cell, s)] >= 2 for cell in CELLS for s in fit_ids)
    cells_ok = all(per_cell[c] >= 81 for c in CELLS)
    kappa = num / den if den > 0 else None
    k_status = "FIT_UNAVAILABLE" if not (triplets_ok and cells_ok and kappa is not None and math.isfinite(kappa)) else \
        ("FIT_COMPLETE" if all(per_cell[c] == 90 for c in CELLS) else "FIT_QUALIFIED_INCOMPLETE")
    out["kappa"] = dict(value=kappa, status=k_status, numerator=num, denominator=den, vectors_per_cell=per_cell,
                        triplets_with_two_or_more=triplets_ok, planned_vectors=540, available_vectors=sum(per_cell.values()))

    # Quality comparator on the fit sources.
    def c0_quality(cell, source):
        vals = []
        for seed in seeds:
            r = det.latest.get(f"det:f5-r2:native:{cell}:{source}:{seed}:unmarked")
            q = (r or {}).get("c0_quality")
            if not q or q.get("psnr_db") is None or q.get("lpips") is None or q.get("ssim_rgb") is None:
                return None
            vals.append((q["lpips"], q["psnr_db"], q["ssim_rgb"]))
        return [float(np.median([v[i] for v in vals])) for i in range(3)]

    def input_quality(source):
        d = s2a.get(f"clean:{source}:f5-r2:None:None", {}).get("distortion") or {}
        if d.get("status") != "ok" or d.get("psnr_db") is None:
            return None
        return [float(d["lpips"]), float(d["psnr_db"]), float(d["ssim_rgb"])]

    def target(cell, source):
        vals = [f5_c(cell, source, seed) for seed in seeds]
        return int(sum(v is True for v in vals) >= 2)  # all-attempt source majority; missing counts as failure

    X, y, w, keys = [], [], [], []
    for source in fit_ids:
        iq = input_quality(source)
        for cell in CELLS:
            cq = c0_quality(cell, source)
            if cq is None or iq is None:
                continue
            X.append(cq + iq); y.append(target(cell, source)); w.append(1 / 6); keys.append((cell, source))
    X, y, w = np.asarray(X, float), np.asarray(y, float), np.asarray(w, float)
    feat_rows = defaultdict(int)
    for cell, source in keys:
        feat_rows[(cell, source)] += 1
    per_source = {s: sum(feat_rows[(c, s)] for c in CELLS) for s in fit_ids}
    per_cell_q = {c: sum(feat_rows[(c, s)] for s in fit_ids) for c in CELLS}
    q_cov = all(v >= 5 for v in per_source.values()) and all(v >= 27 for v in per_cell_q.values())
    mean = (w[:, None] * X).sum(0) / w.sum()
    var = (w[:, None] * (X - mean) ** 2).sum(0) / w.sum()
    scale = np.where(var > 0, np.sqrt(var), 1.0)
    Xs = np.where(var > 0, (X - mean) / scale, 0.0)
    both = len(set(y.tolist())) == 2
    beta, diag = logistic_fit(Xs, y, w) if both else (None, dict(status="degenerate_single_class"))
    b_status = "BASELINE_UNAVAILABLE" if not (q_cov and both and diag.get("status") == "converged") else \
        ("FIT_COMPLETE" if len(y) == 180 else "FIT_QUALIFIED_INCOMPLETE")
    out["quality_comparator"] = dict(status=b_status, features=["c0_lpips_median", "c0_psnr_median", "c0_ssim_median",
                                                                "input_lpips", "input_psnr", "input_ssim"],
                                     coefficients=None if beta is None else beta.tolist(), means=mean.tolist(), scales=scale.tolist(),
                                     zero_variance=(var <= 0).tolist(), rows=len(y), positives=int(y.sum()), diagnostics=diag,
                                     rows_per_source=per_source, rows_per_cell=per_cell_q)

    # q90 on the 30 calibration sources (only after kappa is fixed above).
    scores = []
    for source in cal_ids:
        worst, complete = 0.0, True
        for cell in CELLS:
            for seed in seeds:
                law = native.latest.get(f"law:{cell}:{source}:{seed}")
                d = det.latest.get(f"det:f5-r2:native:{cell}:{source}:{seed}:f5-r2")
                f0 = (det.latest.get(f"det:f5-r2:native:{cell}:{source}:{seed}:unmarked") or {}).get("f0")
                try:
                    if kappa is None or not law or law.get("status") != "ok" or f0 is None or not d or d.get("status") != "ok":
                        raise ValueError
                    sem = d["calls"][ALPHA]["raw"]["semantic"]
                    m_act = float(sem["decoded_score"]) - float(sem["decoded_threshold"])
                    pred = semantic_predict(np.asarray(law["b"]) + kappa * np.asarray(law["v"]), f0, profile)
                    if pred["margin"] is None or not math.isfinite(m_act):
                        raise ValueError
                    worst = max(worst, abs(m_act - pred["margin"]))
                except Exception:
                    complete = False
        scores.append(dict(source=source, complete=complete, score=worst if complete else None))
    finite = sorted(s["score"] for s in scores if s["complete"])
    n_complete = len(finite)
    ranked = finite + [math.inf] * (30 - n_complete)
    q90 = ranked[27]
    out["q90"] = dict(value=None if math.isinf(q90) else q90, infinite=math.isinf(q90),
                      status="RADIUS_COMPLETE_FINITE" if n_complete == 30 else "RADIUS_CONSERVATIVE_FINITE" if n_complete >= 28 else "RADIUS_UNINFORMATIVE_INFINITE",
                      complete_sources=n_complete, source_scores=scores, units="native decoded score units")

    # Development diagnostics (descriptive): law and comparator on all 60 sources, per cell.
    diag_rows = []
    for source in order:
        iq = input_quality(source)
        for cell in CELLS:
            preds, actual = [], []
            for seed in seeds:
                law = native.latest.get(f"law:{cell}:{source}:{seed}")
                f0 = (det.latest.get(f"det:f5-r2:native:{cell}:{source}:{seed}:unmarked") or {}).get("f0")
                if kappa is not None and law and law.get("status") == "ok" and f0 is not None:
                    preds.append(semantic_predict(np.asarray(law["b"]) + kappa * np.asarray(law["v"]), f0, profile)["C"])
                else:
                    preds.append(None)
                actual.append(f5_c(cell, source, seed))
            law_major = None if sum(p is None for p in preds) > 1 else int(sum(p is True for p in preds) >= 2)
            cq = c0_quality(cell, source)
            qprob = None
            if beta is not None and cq is not None and iq is not None:
                z = (np.asarray(cq + iq) - mean) / scale
                z = np.where(var > 0, z, 0.0)
                qprob = float(1 / (1 + np.exp(-(beta[0] + z @ beta[1:]))))
            diag_rows.append(dict(source=source, cell=cell, split="fit" if source in fit_ids else "calibration",
                                  actual_majority=int(sum(a is True for a in actual) >= 2), law_majority=law_major, quality_prob=qprob))
    by_cell = {}
    for cell in CELLS:
        rows_c = [r for r in diag_rows if r["cell"] == cell]
        law_ok = [r for r in rows_c if r["law_majority"] is not None]
        q_ok = [r for r in rows_c if r["quality_prob"] is not None]
        by_cell[cell] = dict(actual_rate=sum(r["actual_majority"] for r in rows_c) / len(rows_c),
                             law_rate=None if not law_ok else sum(r["law_majority"] for r in law_ok) / len(law_ok),
                             law_brier=None if not law_ok else sum((r["law_majority"] - r["actual_majority"]) ** 2 for r in law_ok) / len(law_ok),
                             quality_brier=None if not q_ok else sum((r["quality_prob"] - r["actual_majority"]) ** 2 for r in q_ok) / len(q_ok),
                             law_available=len(law_ok), quality_available=len(q_ok))
    out["development_diagnostics"] = dict(note="descriptive, reused development data; not an H4 test", by_cell=by_cell)
    out["frozen_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path = args.out / "phase-a-fit.json"
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    (args.out / "phase-a-diagnostic-rows.json").write_text(json.dumps(diag_rows), encoding="utf-8")
    print(json.dumps(dict(kappa=out["kappa"]["value"], kappa_status=k_status, q90=out["q90"]["value"], q90_status=out["q90"]["status"],
                          comparator=b_status, by_cell=by_cell), indent=1, default=str))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("detect", "fit"), required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stage2a", type=Path, default=Path("/workspace/runs/stage2a-full/rows.jsonl"))
    args = parser.parse_args()
    detect(args) if args.stage == "detect" else fit(args)


if __name__ == "__main__":
    main()

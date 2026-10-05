"""H1 probe: per-chip attenuation and noise under img2img, for matched-filter detector.

Reads an existing f5_gate run's saved PNGs, re-encodes each with the pinned
SD1.5 VAE (fp32) and computes chip projections p_i (Layout.projections).
For clean-C1 (marked) images: p_i are the embedded margins times norms.
For each attacked image (strength/seed): p'_i.
Reports per-chip mean attenuation a_i = E[p'_i / p_i] over completed pairs,
and per-chip variance v_i = Var[p'_i - a_i p_i]. Detector weight ∝ a_i / v_i.

Also estimates blind-channel noise on unmarked cleans for FPR check.
Development data only.
"""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from scripts import f5_latent_codec as f5  # noqa: E402
from scripts import revised_watermark_v5 as v5  # noqa: E402

PROFILE_PATH = ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json"

def load_profile():
    return v5.validate_profile(json.loads(PROFILE_PATH.read_text(encoding="utf-8")))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True, help="f5_gate run dir (must have images/ and rows.jsonl)")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--owner", default="qim-pilot-owner-alpha")
    a = p.parse_args()

    gate_run = a.gate_run
    run_meta = json.loads((gate_run / "run.json").read_text(encoding="utf-8"))
    params = run_meta["params"]
    band = tuple(params["band"])
    whitening = float(params.get("whitening", 1.0))
    binding = params.get("binding", "soft")

    profile = load_profile()
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(a.owner)
    layout = f5.Layout(checked, key, config, owner, band, whitening)

    reader = f5.Reader(ASSETS)

    rows = [json.loads(l) for l in (gate_run / "rows.jsonl").open(encoding="utf-8")]

    # Map source -> clean-C1 projections
    from PIL import Image

    def proj_of_path(png_path: str) -> np.ndarray:
        rgb = np.asarray(Image.open(png_path).convert("RGB"), np.uint8)
        z = reader.latent(rgb)
        chips = np.asarray(layout.projections(z), float)
        return chips

    clean_chips: dict[int, np.ndarray] = {}
    clean_unmarked: dict[int, np.ndarray] = {}
    attacked: list[dict] = []

    for r in rows:
        if r.get("outcome") != "completed":
            continue
        img_path = r.get("image", {}).get("path")
        if not img_path:
            continue
        if r.get("axis") == "clean":
            if r.get("control") == "C1":
                clean_chips[r["source_id"]] = proj_of_path(img_path)
            elif r.get("control") == "C0":
                clean_unmarked[r["source_id"]] = proj_of_path(img_path)
        elif r.get("axis") == "T3" and r.get("dose") == "diffusion":
            if r.get("control") == "C1":
                attacked.append(dict(source_id=r["source_id"], strength=float(r["strength"]), seed=int(r["seed"]),
                                     path=img_path, row=r))

    if not clean_chips:
        raise SystemExit("no clean C1 found in gate run")

    # Per-chip stats per strength
    import collections
    strengths = sorted(set(x["strength"] for x in attacked))
    per_strength: dict[float, dict] = {}
    for s in strengths:
        pairs = [x for x in attacked if x["strength"] == s]
        if not pairs:
            continue
        # Stack: clean p_i and attacked p'_i
        P = np.stack([clean_chips[x["source_id"]] for x in pairs])  # n x 320
        Pp = np.stack([proj_of_path(x["path"]) for x in pairs])
        # Per-chip attenuation via linear regression atten_i = sum(P*Pp)/sum(P^2)
        denom = (P * P).sum(axis=0) + 1e-12
        atten = (P * Pp).sum(axis=0) / denom
        residual = Pp - atten * P
        var = residual.var(axis=0) + 1e-12
        snr = (atten * np.abs(P).mean(axis=0)) / np.sqrt(var)
        # Correlation kept
        corr = np.array([np.corrcoef(P[:, i], Pp[:, i])[0, 1] if P[:, i].std() > 1e-9 else 0 for i in range(P.shape[1])])
        per_strength[str(s)] = dict(n=len(pairs), a_median=float(np.median(atten)), a_mean=float(atten.mean()),
                                     v_median=float(np.median(var)), snr_median=float(np.median(snr)),
                                     corr_median=float(np.median(corr)),
                                     a=atten.tolist(), v=var.tolist(), corr=corr.tolist())

    # Blind noise on unmarked cleans
    if clean_unmarked:
        U = np.stack(list(clean_unmarked.values()))
        blind_std = float(U.std())
        blind_per_chip_std = U.std(axis=0).tolist()
    else:
        blind_std = None
        blind_per_chip_std = None

    # Quick re-read simulation: would a weighted detector rescue any failures at .4?
    # Weighted score = sum a_i * w_true_i * p'_i / v_i  vs unweighted sum w_true_i * p'_i
    # We have true Ws via _semantic_pattern; compute for one owner/seed family using clean-C1 code
    # Use the same Ws that was embedded (derived from source CLIP). Approximate by using clean-C1's Ws.
    # For simplicity, skip semantic layer here — report carrier margin separation.
    # Carrier margin per image: assume Ws is the sign of clean p_i (true for embedded chips at high margin)
    # So weighted margin = a/v weighted vs unweighted.

    out = dict(schema="f5-h1-probe-v1", gate_run=str(gate_run), band=list(band), whitening=whitening,
               binding=binding, commit=__import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               per_strength=per_strength, blind_std=blind_std, blind_per_chip_std=blind_per_chip_std,
               sources=list(clean_chips.keys()), strengths=strengths)

    # Write
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("n","a_median","a_mean","v_median","snr_median","corr_median")} for k, v in per_strength.items()}, indent=1))
    if blind_std is not None:
        print(f"blind_std (unmarked C0 chips): {blind_std:.4f}")

if __name__ == "__main__":
    main()

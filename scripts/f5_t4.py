"""Family 5 copy-paste check (T4 residual arms) on a completed f5_gate run.

For the twenty directed donor/recipient pairs of the v5 dev-001 study, the
donor's mark residual (saved C1 minus C0) is added to the recipient at scales
.5 and 1 with v5's own `residual_transfer` (clip, then round).  Each output is
read blind for owner alpha in two binding modes: `combined` (the decision the
method reports) and `none` (delivery control: is the mark there at all).  A
`combined` both_match on a recipient is a false attribution.  The public
projection arm of v5 is not reproduced here.  The latent is read with the
pinned fp32 VAE encoder on the GPU.
"""
from __future__ import annotations

import argparse, json, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import f5_latent_codec as f5  # noqa: E402
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_gate import V5_RESULTS, ASSETS  # noqa: E402
from three_threat_protocol import residual_transfer  # noqa: E402

ALPHA = "qim-pilot-owner-alpha"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder
    from m1_latent_reconstruction import quality

    gate = json.loads((a.gate_run / "run.json").read_text(encoding="utf-8"))
    profile = v5.validate_profile(gate["profile"])
    band, whitening = tuple(gate["params"]["band"]), gate["params"]["whitening"]
    binding, views = gate["params"].get("binding", "hard"), gate["params"].get("semantic_views", 1)
    from f5_gate import semantic_feature
    reader = f5.Reader(ASSETS)
    v5rows = json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"]
    pairs = sorted({(r["donor_id"], r["recipient_id"]) for r in v5rows if r.get("axis") == "T4"})
    v5_outcomes = {}
    for r in v5rows:
        if r.get("axis") == "T4" and r.get("arm") == "clean_donor_residual":
            for d in r["detections"]:
                if d["claimed_owner"] == ALPHA:
                    v5_outcomes[(r["donor_id"], r["recipient_id"], r["scale"], d["binding_mode"])] = d["result"]["outcome"]
    a.output_dir.mkdir(parents=True, exist_ok=False)
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    images = a.gate_run / "images"

    def load(name):
        return np.asarray(Image.open(images / f"{name}.png").convert("RGB"), np.uint8)

    rows, started = [], time.monotonic()
    for donor, recipient in pairs:
        d1, d0, r0 = load(f"clean-{donor}-C1"), load(f"clean-{donor}-C0"), load(f"clean-{recipient}-C0")
        for scale in (0.5, 1.0):
            out = np.asarray(residual_transfer(r0.tolist(), d1.tolist(), d0.tolist(), scale), np.uint8)
            Image.fromarray(out).save(a.output_dir / f"t4-residual-{donor}-{recipient}-{scale}.png")
            vector = semantic_feature(models, clip, transform, out, views)
            z = reader.latent(out)
            calls = {}
            for mode in ("combined", "none"):
                r = f5.detect_rgb(out, z, ALPHA, profile, vector, binding_mode=mode, band=band, whitening=whitening,
                                  binding=binding)
                calls[mode] = dict(outcome=r["outcome"], semantic_found=r["semantic"]["found"],
                                   semantic_score=r["semantic"]["score"], instance_found=r["instance"]["found"])
            q = quality(r0, out)
            rows.append(dict(donor_id=donor, recipient_id=recipient, scale=scale, calls=calls,
                             recipient_psnr_db=q["psnr_db"], recipient_ssim=q["ssim_rgb"],
                             v5_combined=v5_outcomes.get((donor, recipient, scale, "combined")),
                             v5_none=v5_outcomes.get((donor, recipient, scale, "none"))))
    summary = {}
    for scale in (0.5, 1.0):
        sel = [r for r in rows if r["scale"] == scale]
        summary[str(scale)] = dict(
            pairs=len(sel),
            f5_combined={o: sum(r["calls"]["combined"]["outcome"] == o for r in sel) for o in sorted({r["calls"]["combined"]["outcome"] for r in sel})},
            f5_none={o: sum(r["calls"]["none"]["outcome"] == o for r in sel) for o in sorted({r["calls"]["none"]["outcome"] for r in sel})},
            f5_false_attribution=sum(r["calls"]["combined"]["outcome"] == "both_match" for r in sel),
            f5_delivered=sum(r["calls"]["none"]["semantic_found"] for r in sel),
            v5_combined={o: sum(r["v5_combined"] == o for r in sel) for o in sorted({str(r["v5_combined"]) for r in sel})},
            v5_none={o: sum(r["v5_none"] == o for r in sel) for o in sorted({str(r["v5_none"]) for r in sel})})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    run = dict(schema="f5-t4-residual-v1", data_split="development", commit=commit, command=sys.argv,
               gate_run=str(a.gate_run), band=list(band), whitening=whitening, binding=binding, semantic_views=views, duration_seconds=time.monotonic() - started,
               outcome="completed", summary=summary, rows=rows, human_visual_verdict=None)
    (a.output_dir / "run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

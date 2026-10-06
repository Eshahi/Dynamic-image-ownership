"""T5 semantic-collision check for F5 r3-256 on a completed stress-gate run (development data).

For every ordered pair (i, j) of distinct development sources:
- **Code distance.** The soft distance (32-bit units) between i's 256-bit sketch, used as an exact code, and the projections of image j. This is the r3 analogue of the q Hamming distance in `f4_t5.py`.
- **Carrier distance.** The soft distance the r3 detector would compute if i's mark were read on j, using the carrier LLRs of i's clean C1 latent.
- **H distance.** The Hamming distance of the 32-bit perceptual hashes H.

A joint near collision is code (or carrier) distance <= 6 together with H <= 6: the instance tier could not tell the pair apart. Distances are computed on the clean C1 images and, for the code and H, also on the unmarked C0 images. GPU only for the VAE latents.
"""
from __future__ import annotations

import argparse, json, math, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import f5_latent_codec as f5  # noqa: E402
from scripts import f5_r3_codec as r3  # noqa: E402
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_transfer_probe import ASSETS  # noqa: E402

ALPHA = "qim-pilot-owner-alpha"
EXACT_LLR = 40.0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder
    from f5_gate import semantic_feature

    gate = json.loads((a.gate_run / "run.json").read_text(encoding="utf-8"))
    profile = v5.validate_profile(gate["profile"])
    checked, key, config = v5._resolve(profile, None)
    layout = r3.Layout256(key, config, v5.canonical_owner(ALPHA))
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    reader = f5.Reader(ASSETS)
    sources = sorted({r["source_id"] for r in (json.loads(l) for l in (a.gate_run / "rows.jsonl").open(encoding="utf-8"))
                      if r.get("outcome") == "embedded"})
    info, started = {}, time.monotonic()
    for sid in sources:
        entry = {}
        for control in ("C0", "C1"):
            rgb = np.asarray(Image.open(a.gate_run / "images" / f"clean-{sid}-{control}.png").convert("RGB"), np.uint8)
            vec = np.asarray(semantic_feature(models, clip, transform, rgb, 7))
            luma = v5.luminance_from_rgb(rgb.tolist())
            fragile = v5._Fragile(checked, key, config, v5.canonical_owner(ALPHA), len(luma), len(luma[0]))
            means, coefficients = v5.base._analyse(luma, fragile.analysis)
            entry[control] = dict(p=r3.sketch_projections(vec, key, config),
                                  h=v5.base._perceptual_hash(means, coefficients, key, config))
            if control == "C1":
                entry["llr"] = r3.carrier_llrs(layout.chips(reader.latent(rgb)))[0]
        info[sid] = entry

    def soft(llr, proj):
        return r3.soft_angle(llr, proj) * v5.CODE_BITS / math.pi

    rows = []
    for i in sources:
        for j in sources:
            if i == j:
                continue
            row = dict(i=i, j=j)
            for control in ("C0", "C1"):
                code_i = np.where(info[i][control]["p"] > 0, EXACT_LLR, -EXACT_LLR)
                row[f"code_{control}"] = soft(code_i, info[j][control]["p"])
                row[f"h_{control}"] = v5.base._distance(info[i][control]["h"], info[j][control]["h"])
            row["carrier_C1"] = soft(info[i]["llr"], info[j]["C1"]["p"])
            rows.append(row)

    def count(key, limit=6.0):
        return sum(r[key] <= limit for r in rows)

    unordered = [r for r in rows if r["i"] < r["j"]]
    summary = dict(
        ordered_pairs=len(rows),
        code_le6={c: count(f"code_{c}") for c in ("C0", "C1")},
        carrier_le6_C1=count("carrier_C1"),
        h_le6={c: count(f"h_{c}") for c in ("C0", "C1")},
        joint_code_h_le6_unordered={c: sum(r[f"code_{c}"] <= 6 and r[f"h_{c}"] <= 6 for r in unordered) for c in ("C0", "C1")},
        joint_carrier_h_le6_ordered_C1=sum(r["carrier_C1"] <= 6 and r["h_C1"] <= 6 for r in rows),
        min_code_C1=min(r["code_C1"] for r in rows), min_carrier_C1=min(r["carrier_C1"] for r in rows))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    a.output.write_text(json.dumps(dict(schema="f5-r3-t5-v1", data_split="development", commit=commit, gate_run=str(a.gate_run),
                                        duration_seconds=time.monotonic() - started, summary=summary, rows=rows), indent=1),
                        encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

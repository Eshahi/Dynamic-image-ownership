"""Colour attacks on a completed f4_gate run: the obvious way to remove a chroma mark.

Applied to the saved clean C1 (marked) and C0 (unmarked) images of every
source: grayscale (R=G=B=BT.601 luma, which leaves luminance unchanged),
saturation x0.5 about luma, hue rotation by 10 degrees in YCbCr, and JPEG
quality 75 with 4:2:0 chroma subsampling.  Owner alpha is read blind
(combined binding) with the attacked image's own CLIP features; CLIP cosine
to the source records how much content the attack keeps.  CPU only.
"""
from __future__ import annotations

import argparse, io, json, math, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import f4_chroma_codec as f4  # noqa: E402
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_gate import ASSETS  # noqa: E402
from f4_transfer_probe import SOURCES  # noqa: E402

ALPHA = "qim-pilot-owner-alpha"


def ycbcr(rgb):
    x = rgb.astype(np.float64)
    y = 0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2]
    cb = -0.168736 * x[..., 0] - 0.331264 * x[..., 1] + 0.5 * x[..., 2]
    cr = 0.5 * x[..., 0] - 0.418688 * x[..., 1] - 0.081312 * x[..., 2]
    return y, cb, cr


def rgb_of(y, cb, cr):
    r = y + 1.402 * cr
    g = y - 0.344136 * cb - 0.714136 * cr
    b = y + 1.772 * cb
    return np.clip(np.rint(np.stack([r, g, b], -1)), 0, 255).astype(np.uint8)


def attacks():
    def gray(rgb):
        y, _, _ = ycbcr(rgb)
        return rgb_of(y, 0 * y, 0 * y)

    def saturation(rgb):
        y, cb, cr = ycbcr(rgb)
        return rgb_of(y, 0.5 * cb, 0.5 * cr)

    def hue(rgb):
        y, cb, cr = ycbcr(rgb)
        t = math.radians(10)
        return rgb_of(y, math.cos(t) * cb - math.sin(t) * cr, math.sin(t) * cb + math.cos(t) * cr)

    def jpeg(rgb):
        from PIL import Image
        buffer = io.BytesIO()
        Image.fromarray(rgb).save(buffer, format="JPEG", quality=75, subsampling=2)
        return np.asarray(Image.open(io.BytesIO(buffer.getvalue())).convert("RGB"), np.uint8)

    return {"grayscale": gray, "saturation_0.5": saturation, "hue_10deg": hue, "jpeg_q75_420": jpeg}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder

    gate = json.loads((a.gate_run / "run.json").read_text(encoding="utf-8"))
    profile, planes = v5.validate_profile(gate["profile"]), tuple(gate.get("planes", ["Cr"]))
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    started, rows = time.monotonic(), []
    for sid in SOURCES:
        source = np.asarray(Image.open(a.gate_run / "images" / f"clean-{sid}-C0.png").convert("RGB"), np.uint8)
        source_vector = np.asarray(models.clip_feature(clip, transform, source).reshape(-1))
        for control in ("C1", "C0"):
            image = np.asarray(Image.open(a.gate_run / "images" / f"clean-{sid}-{control}.png").convert("RGB"), np.uint8)
            for name, attack in attacks().items():
                out = attack(image)
                vector = models.clip_feature(clip, transform, out).reshape(-1)
                r = f4.detect_rgb(out.tolist(), ALPHA, profile, vector.tolist(), planes=planes)
                rows.append(dict(source_id=sid, control=control, attack=name, outcome=r["outcome"],
                                 semantic_success=bool(r["semantic"]["found"] and r["semantic"]["content_match"]),
                                 semantic_score=r["semantic"]["score"],
                                 clip_cosine_to_source=float(np.dot(np.asarray(vector), source_vector))))
    summary = {}
    for name in attacks():
        for control in ("C1", "C0"):
            sel = [r for r in rows if r["attack"] == name and r["control"] == control]
            summary[f"{name}|{control}"] = dict(n=len(sel), semantic_success=sum(r["semantic_success"] for r in sel),
                                                median_clip_cosine=float(np.median([r["clip_cosine_to_source"] for r in sel])))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(dict(schema="f4-colour-attacks-v1", data_split="development", commit=commit,
                                        command=sys.argv, gate_run=str(a.gate_run), planes=planes,
                                        duration_seconds=time.monotonic() - started, summary=summary, rows=rows),
                                   indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

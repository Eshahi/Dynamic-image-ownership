"""Family 4 semantic-collision check (T5) on a completed f4_gate run.

Repeats the v5 dev-001 T5 component diagnostic on the family-4 images: for
every unordered pair of the twelve development sources, the Hamming distance
between their semantic codes q (CLIP) and between their perceptual hashes H
(luminance), on the unmarked (C0) and the marked (C1) clean images.  A pair of
distinct images with q distance <= 6 and H distance <= 6 is a joint near
collision (the instance tier could not tell them apart); q <= 6 with H > 6 is
the wanted case for same-topic pairs (semantics agree, instance differs).
Semantic labels and the v5 distances come from the v5 dev-001 rows, so the
comparison is pair by pair.  CPU only.
"""
from __future__ import annotations

import argparse, json, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_gate import V5_RESULTS, ASSETS  # noqa: E402
from f4_transfer_probe import SOURCES  # noqa: E402
from v5_study_protocol import distance  # noqa: E402


def summarise(pairs, key):
    d = [p[key] for p in pairs]
    return dict(pairs=len(d), q_le_6=sum(x["semantic"] <= 6 for x in d),
                q_le_6_and_h_gt_6=sum(x["semantic"] <= 6 and x["instance"] > 6 for x in d),
                joint_near_collision=sum(x["semantic"] <= 6 and x["instance"] <= 6 for x in d),
                exact_q=sum(x["semantic"] == 0 for x in d), exact_h=sum(x["instance"] == 0 for x in d))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder

    gate = json.loads((a.gate_run / "run.json").read_text(encoding="utf-8"))
    profile = v5.validate_profile(gate["profile"])
    v5rows = [r for r in json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"] if r.get("axis") == "T5"]
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    started, codes = time.monotonic(), {}
    for sid in SOURCES:
        for control in ("C0", "C1"):
            rgb = np.asarray(Image.open(a.gate_run / "images" / f"clean-{sid}-{control}.png").convert("RGB"), np.uint8)
            vector = models.clip_feature(clip, transform, rgb).reshape(-1).tolist()
            codes[sid, control] = (v5.semantic_code(vector, profile=profile),
                                   v5.perceptual_hash(v5.luminance_from_rgb(rgb.tolist()), profile=profile))
    rows = []
    for r in v5rows:
        left, right = r["left"], r["right"]
        if (left, "C0") not in codes or (right, "C0") not in codes:
            continue
        row = dict(id=r["id"], left=left, right=right, semantic_label=r["semantic_label"],
                   v5_C0=r.get("distances_C0"), v5_C1=r.get("distances_C1"))
        for control in ("C0", "C1"):
            x, y = codes[left, control], codes[right, control]
            row["f4_" + control] = {"semantic": distance(x[0], y[0]), "instance": distance(x[1], y[1])}
        rows.append(row)
    same_instance = {str(s): {"semantic": distance(codes[s, "C0"][0], codes[s, "C1"][0]),
                              "instance": distance(codes[s, "C0"][1], codes[s, "C1"][1])} for s in SOURCES}
    summary = {}
    for label in sorted({r["semantic_label"] for r in rows}):
        sel = [r for r in rows if r["semantic_label"] == label]
        summary[label] = {k: summarise(sel, k) for k in ("f4_C1", "v5_C1", "f4_C0", "v5_C0")}
    summary["C0_distances_equal_to_v5"] = sum(r["f4_C0"] == r["v5_C0"] for r in rows)
    summary["same_instance_C0_vs_C1_both_le_6"] = sum(x["semantic"] <= 6 and x["instance"] <= 6 for x in same_instance.values())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(dict(schema="f4-t5-collision-v1", data_split="development", commit=commit,
                                        command=sys.argv, gate_run=str(a.gate_run),
                                        duration_seconds=time.monotonic() - started, summary=summary,
                                        same_instance=same_instance, rows=rows), indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

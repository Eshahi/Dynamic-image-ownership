"""Family 5: where do the regeneration failures come from, carrier or semantic binding?

For every completed C1 row of an f5_gate run: whether the robust key was found
(carrier), whether the content check matched (binding), the Hamming distance
between the decoded code and the code recomputed from the attacked image, and
the CLIP cosine of the attacked image to its unmarked source.  The thesis T3
protocol counts content as retained at CLIP cosine >= .90
(`experiments/c4-three-threat-small-v1/plan.md`), so failures are split by
that line.  Descriptive, development data only; CPU.
"""
from __future__ import annotations

import argparse, json, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from f4_gate import ASSETS  # noqa: E402

ALPHA = "qim-pilot-owner-alpha"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder

    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    rows = [json.loads(line) for line in (a.gate_run / "rows.jsonl").open(encoding="utf-8")]
    images = a.gate_run / "images"
    feature = {}

    def vec(name):
        if name not in feature:
            rgb = np.asarray(Image.open(images / f"{name}.png").convert("RGB"), np.uint8)
            feature[name] = np.asarray(models.clip_feature(clip, transform, rgb).reshape(-1))
        return feature[name]

    out, table = [], defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r.get("control") != "C1" or r.get("outcome") != "completed" or r.get("axis") != "T3":
            continue
        c = r["calls"][ALPHA]
        cos = float(np.dot(vec(r["id"]), vec(f"clean-{r['source_id']}-C0")))
        key = "vae" if r["dose"] == "vae_mode" else str(r["strength"])
        retained = cos >= 0.90
        state = "success" if c["semantic_found"] and c["semantic_content_match"] else (
            "binding" if c["semantic_found"] else "carrier")
        table[key][f"{'retained' if retained else 'not_retained'}|{state}"] += 1
        out.append(dict(id=r["id"], strength=key, clip_cosine_to_source=cos, retained=retained, state=state,
                        outcome=c["outcome"], semantic_score=c["semantic_score"]))
    # The same split for the v5 r3 comparator (its own attacked images and recorded CLIP cosines).
    from f4_gate import V5_RESULTS
    v5table = defaultdict(lambda: defaultdict(int))
    for r in json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"]:
        if r.get("axis") == "T3" and r.get("control") == "C1" and r.get("status") == "metrics_complete":
            det = next(d["result"] for d in r["detections"] if d["claimed_owner"] == ALPHA and d["binding_mode"] == "combined")
            s = det["semantic"]
            state = "success" if s["found"] and s["content_match"] else ("binding" if s["found"] else "carrier")
            cos = r.get("clip_source_cosine")
            retained = "retained" if cos is not None and cos >= 0.90 else ("not_retained" if cos is not None else "no_clip")
            key = "vae" if r.get("dose") == "vae_mode" else str(r.get("strength"))
            v5table[key][f"{retained}|{state}"] += 1
    summary = {k: dict(v) for k, v in sorted(table.items())}
    v5summary = {k: dict(v) for k, v in sorted(v5table.items())}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(dict(schema="f5-binding-diagnostic-v1", gate_run=str(a.gate_run), summary=summary,
                                        v5_summary=v5summary, rows=out), indent=1), encoding="utf-8")
    print(json.dumps(dict(f5=summary, v5=v5summary), indent=1))


if __name__ == "__main__":
    main()

"""Family 5, semantic binding: can the content check survive regeneration better?

After F5, every T3 failure is a binding failure: the mark is read, but the
32-bit CLIP code q recomputed from the regenerated image is more than 6 bits
from the code the mark carries.  The code bits are signs of 32 keyed
Rademacher projections p_j = r_j . b of the unit CLIP vector b, so two
vectors at angle theta disagree per bit with probability theta / pi.  The
detector, however, sees more than the suspect's signs: it sees p_j itself.  A
disagreement on a bit whose projection is near zero is expected under small
drift; one on a bit with a large |p_j| is not.

Rules compared, all with v5's own angles (match at theta <= 6 pi / 32,
mismatch at theta >= 10 pi / 32, uncertain in between; nothing is tuned):

* hard: theta_hat = pi * Hamming(c, sign(p)) / 32 (the current detector);
* soft: maximum-likelihood theta from P(c_j | p_j, theta) = Phi(c_j p_j cot theta)
  (b' = cos(theta) b + sin(theta) n with n independent of the projection);

each with plain CLIP features (the pinned single view) and with a test-time
average over seven fixed views (full, mirrored, four corner crops and a centre
crop at 7/8 size), re-normalized.  The view average changes the carried code,
so it is evaluated here with the code the embedder would have carried (the
carrier reads it exactly in every F5 row); it needs a real re-embedding run to
be adopted.

Data, development only: (T3) every completed C1 row of an f5_gate run against
the source's code; (T4 binding) the donor's code against every other
recipient's unmarked image, 132 ordered pairs, by v5's semantic label;
(T5) joint near collision of two distinct marked images = semantic match under
the rule (either direction) and perceptual-hash distance <= 6 (from an f4_t5
run).

Selection rule, declared before the run: a rule replaces "hard, plain" only if
it raises the T3 match count at .2 and .4 together, does not raise semantic
matches on different-label T4 pairs, and keeps T5 joint collisions at zero.
"""
from __future__ import annotations

import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_gate import ASSETS, V5_RESULTS  # noqa: E402

base = v5.base
BITS = v5.CODE_BITS
MATCH, FAR = 6 * math.pi / BITS, 10 * math.pi / BITS
GRID = np.linspace(1e-3, math.pi - 1e-3, 2000)


def projection_rows(key, config, width=512):
    row_bytes = (width + 7) // 8
    material = base._stream(key, config, base._pack(b"semantic-projection", width.to_bytes(4, "big")), BITS * row_bytes)
    rows = np.empty((BITS, width))
    for row in range(BITS):
        chunk = material[row * row_bytes:(row + 1) * row_bytes]
        rows[row] = [-1.0 if (chunk[i >> 3] >> (i & 7)) & 1 else 1.0 for i in range(width)]
    return rows


def code_of(p):
    return [1 if value > 1e-9 else -1 for value in p]


def theta_hard(c, p):
    return math.pi * sum(a != b for a, b in zip(c, code_of(p))) / BITS


def theta_soft(c, p):
    t = np.asarray(c, float) * np.asarray(p, float)
    cot = np.cos(GRID) / np.sin(GRID)
    loglik = norm.logcdf(t[None, :] * cot[:, None]).sum(1)
    return float(GRID[int(np.argmax(loglik))])


def status(theta):
    return "match" if theta <= MATCH + 1e-12 else ("mismatch" if theta >= FAR - 1e-12 else "uncertain")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gate-run", type=Path, required=True)
    p.add_argument("--t5-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder

    gate = json.loads((a.gate_run / "run.json").read_text(encoding="utf-8"))
    checked, key, config = v5._resolve(v5.validate_profile(gate["profile"]), None)
    R = projection_rows(key, config)
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    images = a.gate_run / "images"

    def views(img):
        w, h = img.size
        s = int(round(w * 7 / 8))
        boxes = [(0, 0, s, s), (w - s, 0, w, s), (0, h - s, s, h), (w - s, h - s, w, h),
                 ((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)]
        return [img, img.transpose(Image.FLIP_LEFT_RIGHT)] + [img.crop(b) for b in boxes]

    cache = {}

    def features(name):
        if name not in cache:
            img = Image.open(images / f"{name}.png").convert("RGB")
            vs = [np.asarray(models.clip_feature(clip, transform, np.asarray(v, np.uint8)).reshape(-1), float) for v in views(img)]
            tta = np.mean(vs, 0)
            cache[name] = {"plain": vs[0], "tta": tta / np.linalg.norm(tta)}
        return cache[name]

    def proj(name, kind):
        return R @ features(name)[kind]

    # Consistency: the plain projections reproduce the codec's q bit for bit.
    sid0 = gate["sources"][0]
    q_codec = v5.semantic_code(features(f"clean-{sid0}-C0")["plain"].tolist(), profile=gate["profile"])
    q_here = int("".join("1" if c > 0 else "0" for c in code_of(proj(f"clean-{sid0}-C0", "plain"))), 2)
    assert q_codec == q_here, (hex(q_codec), hex(q_here))

    rules = [(kind, est) for kind in ("plain", "tta") for est in ("hard", "soft")]
    estimators = {"hard": theta_hard, "soft": theta_soft}
    rows = [json.loads(line) for line in (a.gate_run / "rows.jsonl").open(encoding="utf-8")]

    # T3: carried code = code of the source's (unmarked) features, as the embedder bound it.
    t3 = defaultdict(lambda: defaultdict(int))
    t3_rows = []
    for r in rows:
        if r.get("control") != "C1" or r.get("outcome") != "completed" or r.get("axis") not in ("clean", "T3"):
            continue
        key_name = "clean" if r["axis"] == "clean" else ("vae" if r["dose"] == "vae_mode" else str(r["strength"]))
        src = f"clean-{r['source_id']}-C0"
        cos = float(features(r["id"])["plain"] @ features(src)["plain"])
        entry = dict(id=r["id"], strength=key_name, clip_cosine_to_source=cos)
        for kind, est in rules:
            theta = estimators[est](code_of(proj(src, kind)), proj(r["id"], kind))
            entry[f"{kind}|{est}"] = theta
            t3[f"{kind}|{est}"][f"{key_name}|{status(theta)}"] += 1
        t3_rows.append(entry)

    # Labels of source pairs from the v5 T5 inventory.
    labels = {}
    for r in json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"]:
        if r.get("axis") == "T5":
            labels[frozenset((r["left"], r["right"]))] = r["semantic_label"]
    sources = gate["sources"]

    # T4 binding: donor code against every other recipient (unmarked image).
    t4 = defaultdict(lambda: defaultdict(int))
    for d in sources:
        for rcp in sources:
            if d == rcp:
                continue
            label = labels.get(frozenset((d, rcp)), "unlabelled")
            for kind, est in rules:
                theta = estimators[est](code_of(proj(f"clean-{d}-C0", kind)), proj(f"clean-{rcp}-C0", kind))
                t4[f"{kind}|{est}"][f"{label}|{status(theta)}"] += 1

    # T5: joint near collision of distinct marked images (semantic match either way and H distance <= 6).
    t5run = json.loads(a.t5_run.read_text(encoding="utf-8"))
    hdist = {frozenset((r["left"], r["right"])): r["f4_C1"]["instance"] for r in t5run["rows"]}
    t5 = defaultdict(lambda: defaultdict(int))
    for pair, h in hdist.items():
        left, right = sorted(pair)
        for kind, est in rules:
            matched = any(status(estimators[est](code_of(proj(f"clean-{x}-C0", kind)), proj(f"clean-{y}-C1", kind))) == "match"
                          for x, y in ((left, right), (right, left)))
            t5[f"{kind}|{est}"]["semantic_match_pairs"] += matched
            t5[f"{kind}|{est}"]["joint_near_collision"] += matched and h <= 6
            t5[f"{kind}|{est}"]["min_h_among_semantic_matches"] = min(t5[f"{kind}|{est}"].get("min_h_among_semantic_matches", 99), h if matched else 99)

    summary = {rule: dict(T3=dict(t3[rule]), T4=dict(t4[rule]), T5=dict(t5[rule])) for rule in (f"{k}|{e}" for k, e in rules)}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(dict(schema="f5-binding-experiment-v1", data_split="development", gate_run=str(a.gate_run),
                                        t5_run=str(a.t5_run), command=sys.argv, angles=dict(match=MATCH, far=FAR),
                                        summary=summary, t3_rows=t3_rows), indent=1), encoding="utf-8")
    for rule, s in summary.items():
        print(rule)
        for part in ("T3", "T4", "T5"):
            print("  ", part, dict(sorted(s[part].items())))


if __name__ == "__main__":
    main()

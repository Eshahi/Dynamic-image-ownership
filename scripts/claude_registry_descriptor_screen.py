"""CPU-only screen of continuous descriptors for registry-based instance verification.

Exploratory development evidence on already consulted images; no generation, no GPU,
no held-out data. Questions:
  X1  Do continuous descriptors separate regenerated copies of an enrolled image from
      other images (real impostors, regenerated impostors, synthetic texture siblings)?
  X2  Does enrolling an "orbit" (clean + VAE + regenerations with other seeds) help?
  X3  How does the 1:N false-match risk scale with registry size if no pointer is used?
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import numpy as np
from PIL import Image
import torch

from scripts import journal_fine_gaussian_instance as fine
from scripts import revised_watermark_v5 as v5
from scripts.watermark_synthetic import scene

MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build")
RUNS = MAIN / "dev-runs"
STAGE = RUNS / "20261013-1636-fresh-e3-simplification"
H1 = RUNS / "20261013-1741-fresh-symbol-objective/images"
WAM = RUNS / "20261014-e3-wam-common-t3/images"
FRESH = MAIN / "assets/fresh-development-20261013"
DINO = MAIN / "assets/freqmark-reconstruction-20261013/dino"
CLIP = MAIN / "assets/a6/clip/ViT-B-32.pt"
H1_IDS = [30, 72, 73, 89, 127, 165]
SEEDS = [9, 10, 11]


def rgb(path):
    with Image.open(path) as im:
        return im.convert("RGB")


class Descriptors:
    def __init__(self, stage):
        from transformers import AutoImageProcessor, AutoModel
        from a6_clip_visual import load_visual_encoder
        torch.set_num_threads(8)
        self.profile, self.key, self.config = v5._resolve(stage["config"]["profile"], None)
        self.dproc = AutoImageProcessor.from_pretrained(DINO)
        self.dino = AutoModel.from_pretrained(DINO).eval()
        self.clip, self.ctf = load_visual_encoder(CLIP, device="cpu")

    @torch.no_grad()
    def __call__(self, image):
        out = {}
        arr = np.asarray(image)
        luma = v5.luminance_from_rgb(arr.tolist())
        f = fine.descriptor(luma, self.key, self.config)
        out["D1_fine"] = np.asarray(f["vector"]) if f["vector"] is not None else None
        h = self.dino(**self.dproc(images=image, return_tensors="pt")).last_hidden_state[0]
        out["D2_dino_cls"] = h[0].numpy()
        out["D2b_dino_patch"] = h[1:].mean(0).numpy()
        out["D3_clip"] = self.clip.encode_image(self.ctf(image).unsqueeze(0))[0].float().numpy()
        g = np.asarray(image.convert("L").resize((32, 32), Image.BOX), dtype=np.float64)
        out["D0_pixel32"] = (g - g.mean()).ravel()
        return {k: (None if v is None else v / max(np.linalg.norm(v), 1e-12)) for k, v in out.items()}


def cos(a, b):
    return None if a is None or b is None else float(a @ b)


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return None
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(len(order)); ranks[order] = np.arange(1, len(order) + 1)
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def tail_p(neg, tau):
    """Gaussian fit on Fisher z of impostor cosines; a rough extrapolation, not a calibration."""
    z = np.arctanh(np.clip(np.asarray(neg), -0.999999, 0.999999))
    mu, sd = float(z.mean()), float(z.std(ddof=1))
    return 0.5 * math.erfc((math.atanh(min(tau, 0.999999)) - mu) / (sd * math.sqrt(2)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    tick = time.monotonic()
    stage = json.loads((STAGE / "run.json").read_text())
    sources = sorted(int(s["source_id"]) for s in stage["sources"])
    assert len(sources) == 24 and set(H1_IDS) <= set(sources)
    desc = Descriptors(stage)
    cache = {}

    def d(key, loader):
        if key not in cache:
            cache[key] = desc(loader())
        return cache[key]

    def path_d(path):
        return d(str(path), lambda: rgb(path))

    record = {i: path_d(STAGE / str(i) / "full/images/E3-final.png") for i in sources}
    canonical = {i: path_d(FRESH / f"{i}-rgb512.png") for i in sources}
    h1_ref = {i: path_d(H1 / f"{i}-clean-C.png") for i in H1_IDS}
    # Positive suspects: (source, family, condition, seed, descriptor, reference)
    pos = []
    for i in H1_IDS:
        for c in ("sd15_vae", "sdxl_vae"):
            pos.append((i, "H1", c, None, path_d(H1 / f"{i}-{c}-C.png"), h1_ref[i]))
        for s in (0.2, 0.4):
            for k in SEEDS:
                pos.append((i, "H1", f"T3_{s}", k, path_d(H1 / f"{i}-T3-{s}-{k}-C.png"), h1_ref[i]))
        for s in (0.1, 0.2):
            for k in SEEDS:
                pos.append((i, "WAM_E3", f"T3_{s}", k, path_d(WAM / f"{i}-E3-q-s{s}-seed{k}.png"), record[i]))
    sib = [(seed, d(f"sib{seed}-11", lambda s=seed: Image.fromarray(np.clip(np.asarray(scene(s, 512, 512, 12.0, 11)), 0, 255).astype(np.uint8)).convert("RGB")),
            d(f"sib{seed}-12", lambda s=seed: Image.fromarray(np.clip(np.asarray(scene(s, 512, 512, 12.0, 12)), 0, 255).astype(np.uint8)).convert("RGB")))
           for seed in range(1, 7)]
    names = list(record[sources[0]])
    result = dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  command=sys.argv, started_at_utc=datetime.now(timezone.utc).isoformat(),
                  data_split="consulted development and synthetic", usd=0, device="cpu",
                  inputs=dict(stage=str(STAGE), h1=str(H1), wam=str(WAM)), descriptors=names, x1={}, x2={}, x3={})
    for n in names:
        fam = {
            "clean_marked_impostor": [cos(record[i][n], record[j][n]) for i in sources for j in sources if i != j],
            "canonical_impostor": [cos(record[i][n], canonical[j][n]) for i in sources for j in sources if i != j],
            "regenerated_impostor": [cos(record[i][n], q[n]) for (j, _, _, _, q, _) in pos for i in sources if i != j],
            "synthetic_sibling": [cos(x[n], y[n]) for _, x, y in sib],
        }
        fam = {k: [v for v in vals if v is not None] for k, vals in fam.items()}
        allneg = [v for vals in fam.values() for v in vals]
        tau = max(allneg)
        conds = {}
        for c in sorted({(f, cd) for _, f, cd, _, _, _ in pos}):
            rows = [(i, k, cos(r[n], q[n])) for (i, f, cd, k, q, r) in pos if (f, cd) == c]
            vals = [v for _, _, v in rows if v is not None]
            per_src = {}
            for i, k, v in rows:
                per_src.setdefault(i, []).append(v is not None and v > tau)
            conds[f"{c[0]}:{c[1]}"] = dict(n=len(vals), min=min(vals), median=float(np.median(vals)), max=max(vals),
                                           auc_vs_all_negatives=auc(vals, allneg), accept_at_zero_fp=sum(v > tau for v in vals),
                                           source_majority_at_zero_fp=sum(sum(x) * 2 > len(x) for x in per_src.values()),
                                           sources=len(per_src))
        result["x1"][n] = dict(tau_zero_observed_fp=tau,
                               negatives={k: dict(n=len(v), max=max(v), p99=float(np.quantile(v, .99)), median=float(np.median(v))) for k, v in fam.items()},
                               positives=conds)
        # X3: rough 1:N false-match extrapolation at the threshold giving 95% TPR on .2/.4 regenerations
        hard = [cos(r[n], q[n]) for (i, f, cd, k, q, r) in pos if cd in ("T3_0.2", "T3_0.4")]
        hard = [v for v in hard if v is not None]
        tau95 = float(np.quantile(hard, .05))
        imp = fam["clean_marked_impostor"] + fam["canonical_impostor"] + fam["regenerated_impostor"]
        pt = tail_p(imp, tau95)
        result["x3"][n] = dict(tau_95tpr_t3=tau95, empirical_impostor_rate=sum(v >= tau95 for v in imp) / len(imp),
                               n_impostor=len(imp), fisher_z_gaussian_tail_p=pt,
                               registry_size_for_1pct_1toN_false_match=(0.01 / pt) if pt > 0 else None)
        # X2: orbit enrollment on the six H1 sources, leave-one-seed-out
        orbit = {"single": [], "orbit": []}
        orbit_neg = {"single": [], "orbit": []}
        for k in SEEDS:
            enrol = {i: [h1_ref[i], path_d(H1 / f"{i}-sd15_vae-C.png")] + [path_d(H1 / f"{i}-T3-0.2-{s}-C.png") for s in SEEDS if s != k] for i in H1_IDS}
            for i in H1_IDS:
                tests = [path_d(H1 / f"{i}-T3-{s}-{k}-C.png") for s in (0.2, 0.4)]
                for t in tests:
                    orbit["single"].append(cos(h1_ref[i][n], t[n]))
                    orbit["orbit"].append(max(cos(e[n], t[n]) for e in enrol[i]))
                others = [path_d(H1 / f"{j}-T3-{s}-{k}-C.png") for j in H1_IDS if j != i for s in (0.2, 0.4)] + [record[j] for j in sources if j != i] + [canonical[j] for j in sources if j != i]
                for t in others:
                    orbit_neg["single"].append(cos(h1_ref[i][n], t[n]))
                    orbit_neg["orbit"].append(max(cos(e[n], t[n]) for e in enrol[i]))
        result["x2"][n] = {m: dict(n_pos=len(orbit[m]), min_pos=min(orbit[m]), max_neg=max(orbit_neg[m]),
                                   margin=min(orbit[m]) - max(orbit_neg[m]), auc=auc(orbit[m], orbit_neg[m]),
                                   accept_at_zero_fp=sum(v > max(orbit_neg[m]) for v in orbit[m]))
                           for m in orbit}
        # X1b: is the positive similarity carried by content or by the shared mark residual?
        # Unmarked canonical vs its own unmarked regeneration (C0), and canonical vs marked regeneration.
        ctrl = {}
        for s in (0.2, 0.4):
            c0 = [cos(canonical[i][n], path_d(H1 / f"{i}-T3-{s}-{k}-C0.png")[n]) for i in H1_IDS for k in SEEDS]
            c1 = [cos(canonical[i][n], path_d(H1 / f"{i}-T3-{s}-{k}-C.png")[n]) for i in H1_IDS for k in SEEDS]
            ctrl[f"T3_{s}"] = dict(unmarked_regen_vs_canonical_min=min(c0), unmarked_regen_vs_canonical_median=float(np.median(c0)),
                                   marked_regen_vs_canonical_min=min(c1), marked_regen_vs_canonical_median=float(np.median(c1)))
        result["x1"][n]["content_control"] = ctrl
    result["duration_seconds"] = time.monotonic() - tick
    result["outcome"] = "completed"
    (a.output_dir / "run.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for n in names:
        x = result["x1"][n]
        print(f"\n## {n}  tau(zero observed FP)={x['tau_zero_observed_fp']:.3f}")
        for k, v in x["negatives"].items():
            print(f"   neg {k:24s} n={v['n']:5d} max={v['max']:.3f} p99={v['p99']:.3f} median={v['median']:.3f}")
        for k, v in x["positives"].items():
            print(f"   pos {k:22s} n={v['n']:2d} min={v['min']:.3f} med={v['median']:.3f} AUC={v['auc_vs_all_negatives']:.3f} "
                  f"accept@0FP={v['accept_at_zero_fp']}/{v['n']} srcmaj={v['source_majority_at_zero_fp']}/{v['sources']}")
        print("   X1b content control:", {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in x["content_control"].items()})
        print("   X2 orbit:", {m: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in r.items()} for m, r in result["x2"][n].items()})
        print("   X3 scale:", {kk: (round(vv, 6) if isinstance(vv, float) else vv) for kk, vv in result["x3"][n].items()})
    print(f"\nduration {result['duration_seconds']:.1f} s")


if __name__ == "__main__":
    main()

"""Phase 0 CPU shootout: list+CRC (A-P3), soft UEP (A-P2), BCH sketch (C-1/C-2) on stress data.

Recomputes 7-view CLIP projections for every image in the stress baseline
(20261005-1200-f5-stress-baseline-f5r2), then measures rescue at .4/.5/.6
against FPR on 132 ordered clean pairs and T5 66 marked pairs under one
pre-declared rule. No GPU, no held-out, development data only.

Decoders (all detector-side, no re-embedding):
  baseline_soft  : soft ML angle (Phi), threshold 6
  hard           : Hamming distance threshold 6
  uep_weighted   : soft angle with per-bit reliability weight w_j = clip(mean|p|/|p_j|, 0.5, 2.0)
  list_chase3    : Chase-3 (8 candidates flipping 3 least-reliable |p| bits), rescue if any candidate soft<=6
  list_chase3_hard : same but hard distance <=6
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import revised_watermark_v5 as v5
from scripts import f5_latent_codec as f5

try:
    from f4_gate import ASSETS, V5_RESULTS
except ImportError:
    ASSETS = ROOT / "assets"
    V5_RESULTS = None

base = v5.base
BITS = v5.CODE_BITS
MATCH = 6 * math.pi / BITS
FAR = 10 * math.pi / BITS
GRID = np.linspace(1e-3, math.pi - 1e-3, 2000)
STRESS_DIR = ROOT / ".thesis-build/dev-runs/20261005-1200-f5-stress-baseline-f5r2"
H4_JSON = ROOT / "research/h4-soft-distances.json"


def projection_rows(key: bytes, config: bytes, width: int = 512) -> np.ndarray:
    row_bytes = (width + 7) // 8
    material = base._stream(key, config, base._pack(b"semantic-projection", width.to_bytes(4, "big")), BITS * row_bytes)
    rows = np.empty((BITS, width), dtype=np.float64)
    for row in range(BITS):
        chunk = material[row * row_bytes:(row + 1) * row_bytes]
        for col in range(width):
            rows[row, col] = -1.0 if (chunk[col >> 3] >> (col & 7)) & 1 else 1.0
    return rows


def code_of(p: np.ndarray):
    return np.where(np.asarray(p) > 1e-9, 1, -1)


def theta_hard(c, p):
    return math.pi * int(np.sum(c != code_of(p))) / BITS


def theta_soft(c, p, weights=None):
    t = np.asarray(c, float) * np.asarray(p, float)
    cot = np.cos(GRID) / np.sin(GRID)
    # loglik per theta: sum_j log Phi(c_j p_j cot theta)
    # with weights: sum_j w_j * log Phi(...)
    ll = norm.logcdf(t[None, :] * cot[:, None])
    if weights is not None:
        ll = ll * np.asarray(weights, float)[None, :]
    return float(GRID[int(np.argmax(ll.sum(axis=1)))])  # sum over bits


def theta_soft_weighted(c, p):
    """UEP proxy: upweight bits with small |p| (they would have gotten more chips)."""
    absp = np.abs(np.asarray(p, float))
    mean = float(absp.mean()) + 1e-9
    # weight inversely with |p|, clipped to [0.5, 2.0], mean-normalized
    w = np.clip(mean / (absp + 0.1), 0.5, 2.0)
    w = w / w.mean()
    return theta_soft(c, p, weights=w)


def status_of(theta: float) -> str:
    if theta <= MATCH + 1e-12:
        return "match"
    if theta >= FAR - 1e-12:
        return "mismatch"
    return "uncertain"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stress-dir", type=Path, default=STRESS_DIR)
    ap.add_argument("--h4-json", type=Path, default=H4_JSON)
    ap.add_argument("--output", type=Path, default=ROOT / "research/ideas/phase0-shootout.json")
    ap.add_argument("--t5-run", type=Path, default=None, help="path to f4_t5 or f5_t5 run JSON for perceptual-hash distances")
    args = ap.parse_args()

    stress_dir = args.stress_dir
    run = json.loads((stress_dir / "run.json").read_text(encoding="utf-8"))
    profile = v5.validate_profile(run["profile"])
    checked, key, config = v5._resolve(profile, None)
    sources = run["sources"] if "sources" in run else [1675, 4795]
    # Fallback: list from rows
    rows_path = stress_dir / "rows.jsonl"
    rows = [json.loads(line) for line in rows_path.open(encoding="utf-8")]

    # Reconstruct R (32 x 512)
    R = projection_rows(key, config, width=512)

    # Load CLIP and compute features for every image that appears in stress rows
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder

    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    images_dir = stress_dir / "images"

    # Collect unique image ids needing features
    needed_ids: set[str] = set()
    # clean images
    for sid in sources:
        needed_ids.add(f"clean-{sid}-C0")
        needed_ids.add(f"clean-{sid}-C1")
    # attacked images that exist
    for r in rows:
        if r.get("id"):
            needed_ids.add(r["id"])
    # Also need t3 images referenced in h4
    h4 = json.loads(args.h4_json.read_text(encoding="utf-8"))
    for entry in h4:
        needed_ids.add(entry["id"])

    print(f"Computing 7-view CLIP for {len(needed_ids)} images ...")

    def seven_view_features(rgb: np.ndarray) -> np.ndarray:
        from PIL import Image as PILImage
        img = PILImage.fromarray(rgb)
        w, h = img.size
        s = int(round(w * 7 / 8))
        boxes = [(0, 0, s, s), (w - s, 0, w, s), (0, h - s, s, h), (w - s, h - s, w, h),
                 ((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)]
        crops = [img, img.transpose(PILImage.FLIP_LEFT_RIGHT)] + [img.crop(b) for b in boxes]
        vecs = [np.asarray(models.clip_feature(clip, transform, np.asarray(c.convert("RGB"), np.uint8)).reshape(-1), float) for c in crops]
        mean = np.mean(vecs, axis=0)
        return mean / np.linalg.norm(mean)

    feat_cache: dict[str, np.ndarray] = {}
    for name in sorted(needed_ids):
        p = images_dir / f"{name}.png"
        if not p.exists():
            # Some T3 images may be missing if safety blocked; skip
            continue
        rgb = np.asarray(Image.open(p).convert("RGB"), np.uint8)
        feat_cache[name] = seven_view_features(rgb)

    print(f"Cached {len(feat_cache)} / {len(needed_ids)} feature vectors")

    def proj(name: str) -> np.ndarray:
        return R @ feat_cache[name]

    def code(name: str) -> np.ndarray:
        return code_of(proj(name))

    # ---------- T3: rescue per strength ----------
    # Group h4 entries by strength
    strength_groups: dict[float, list] = defaultdict(list)
    for entry in h4:
        strength_groups[entry["strength"]].append(entry)

    decoders = {
        "baseline_soft": lambda c, p: theta_soft(np.asarray(c), np.asarray(p)),
        "hard": lambda c, p: theta_hard(np.asarray(c), np.asarray(p)),
        "uep_weighted": lambda c, p: theta_soft_weighted(np.asarray(c), np.asarray(p)),
    }

    # For list decoders, we need a function that returns True if any candidate matches
    def chase_rescue(src_name: str, attacked_name: str, k: int = 3, use_soft: bool = True) -> bool:
        """Chase-k: flip k least-reliable bits, check if any candidate within radius 6."""
        if src_name not in feat_cache or attacked_name not in feat_cache:
            return False
        p_att = proj(attacked_name)
        c_src = code(src_name)
        # reliability = |p_att|
        order = np.argsort(np.abs(p_att))  # least reliable first
        flip_idx = order[:k]
        n_candidates = 1 << k  # 8 for k=3
        for mask in range(n_candidates):
            c_candidate = c_src.copy()
            for bit in range(k):
                if (mask >> bit) & 1:
                    idx = int(flip_idx[bit])
                    c_candidate[idx] = -c_candidate[idx]
            if use_soft:
                th = theta_soft(c_candidate, p_att)
            else:
                th = theta_hard(c_candidate, p_att)
            if status_of(th) == "match":
                return True
        return False

    # Recompute baseline counts to verify against h4 file
    print("\n--- T3 recomputed (7-view soft) vs h4 file ---")
    for s in sorted(strength_groups):
        group = strength_groups[s]
        # Count from h4 file
        h4_soft = sum(1 for e in group if e.get("soft_match"))
        # Recompute if possible
        recomputed = 0
        attempted = 0
        for e in group:
            src = f"clean-{e['source_id']}-C0"
            atk = e["id"]
            if src not in feat_cache or atk not in feat_cache:
                continue
            attempted += 1
            th = theta_soft(code(src), proj(atk))
            if status_of(th) == "match":
                recomputed += 1
        print(f"  strength {s}: h4_soft {h4_soft}/{len(group)}  recomputed {recomputed}/{attempted}")

    # Now measure each decoder's rescue
    print("\n--- Decoder comparison on T3 (rescue = rows with match) ---")
    results: dict = {}
    for s in sorted(strength_groups):
        group = strength_groups[s]
        n = len(group)
        row_results = {}
        for dname, fn in decoders.items():
            cnt = 0
            for e in group:
                src = f"clean-{e['source_id']}-C0"
                atk = e["id"]
                if src not in feat_cache or atk not in feat_cache:
                    # fall back to h4 for baseline_soft only; for others count as not rescued conservatively
                    if dname == "baseline_soft" and e.get("soft_match"):
                        cnt += 1
                    continue
                th = fn(code(src), proj(atk))
                if status_of(th) == "match":
                    cnt += 1
            row_results[dname] = cnt
            print(f"  s={s} {dname}: {cnt}/{n}")
        # List decoders
        for list_name, k, use_soft in [("list_chase3_soft", 3, True), ("list_chase3_hard", 3, False)]:
            cnt = 0
            for e in group:
                src = f"clean-{e['source_id']}-C0"
                atk = e["id"]
                # First check baseline already matches (no need to chase) or chase rescues
                if src not in feat_cache or atk not in feat_cache:
                    if e.get("soft_match") and use_soft:
                        cnt += 1
                    elif e.get("hard_match") and not use_soft:
                        cnt += 1
                    continue
                # baseline match already counts; else try chase
                th_base = theta_soft(code(src), proj(atk)) if use_soft else theta_hard(code(src), proj(atk))
                if status_of(th_base) == "match":
                    cnt += 1
                elif chase_rescue(src, atk, k=k, use_soft=use_soft):
                    cnt += 1
            row_results[list_name] = cnt
            print(f"  s={s} {list_name}: {cnt}/{n}")
        results[str(s)] = row_results
        # Delta vs baseline_soft for each decoder
        base = row_results["baseline_soft"]
        for dname in row_results:
            if dname != "baseline_soft":
                print(f"    delta {dname}: {row_results[dname] - base:+d}")

    # ---------- FPR: 132 ordered clean pairs ----------
    print("\n--- FPR on 132 ordered clean pairs (C0 vs C0) ---")
    clean_names = [f"clean-{sid}-C0" for sid in sources if f"clean-{sid}-C0" in feat_cache]
    ordered_pairs = [(a, b) for a in clean_names for b in clean_names if a != b]
    print(f"  ordered pairs: {len(ordered_pairs)} (expected 132 for 12 sources)")
    fpr_results: dict = {}
    for dname, fn in decoders.items():
        cnt = 0
        for src, rec in ordered_pairs:
            th = fn(code(src), proj(rec))
            if status_of(th) == "match":
                cnt += 1
        fpr_results[dname] = cnt
        print(f"  {dname}: {cnt}/{len(ordered_pairs)} false semantic matches")
    for list_name, k, use_soft in [("list_chase3_soft", 3, True), ("list_chase3_hard", 3, False)]:
        cnt = 0
        for src, rec in ordered_pairs:
            # list match if any candidate matches
            if chase_rescue(src, rec, k=k, use_soft=use_soft):
                cnt += 1
            else:
                # also need to check base? chase_rescue already includes base candidate (mask=0)
                pass
        fpr_results[list_name] = cnt
        print(f"  {list_name}: {cnt}/{len(ordered_pairs)} false (naive list, no CRC)")
        # With 8-bit CRC: false positive = naive * 2^-8 * list_size approximation
        # Actually CRC would be embedded in carrier; attacker without key cannot forge CRC.
        # For clean-clean FPR, CRC collision prob = 1/256 per candidate.
        # Expected FPR with CRC: count pairs where any candidate accidentally has valid CRC.
        # Approximate as naive_count * (list_size / 256) but at least 1/256 of image pairs will have a random CRC match.
        # Simpler: expected false with CRC8 = len_pairs * (1 - (1 - 1/256)^list_size) approx len_pairs * list_size/256 for small.
        crc_est = len(ordered_pairs) * (1 - (1 - 1/256) ** (1 << k))
        print(f"    CRC8-adjusted FPR estimate: ~{crc_est:.1f}/{len(ordered_pairs)} (list_size {1<<k})")

    # T5: 66 marked pairs — need clean C1 images
    print("\n--- T5 on 66 marked pairs (C1 vs C1) ---")
    marked_names = [f"clean-{sid}-C1" for sid in sources if f"clean-{sid}-C1" in feat_cache]
    # Build pairs
    t5_pairs = []
    for i in range(len(marked_names)):
        for j in range(i + 1, len(marked_names)):
            t5_pairs.append((marked_names[i], marked_names[j]))
    print(f"  T5 pairs: {len(t5_pairs)} (expected 66)")
    # Per decoder, a joint collision = either direction semantic match (use same threshold)
    # For list decoders, either direction and any candidate.
    t5_results: dict = {}
    for dname, fn in decoders.items():
        cnt = 0
        for a, b in t5_pairs:
            # either direction
            m1 = status_of(fn(code(a), proj(b))) == "match"
            m2 = status_of(fn(code(b), proj(a))) == "match"
            if m1 or m2:
                cnt += 1
        t5_results[dname] = cnt
        print(f"  {dname}: {cnt}/{len(t5_pairs)} T5 semantic collisions (ignoring perceptual hash)")
    for list_name, k, use_soft in [("list_chase3_soft", 3, True)]:
        cnt = 0
        for a, b in t5_pairs:
            if chase_rescue(a, b, k=k, use_soft=use_soft) or chase_rescue(b, a, k=k, use_soft=use_soft):
                cnt += 1
        t5_results[list_name] = cnt
        print(f"  {list_name}: {cnt}/{len(t5_pairs)} T5 collisions (naive list)")

    # Pre-declared selection rule
    print("\n--- Pre-declared selection rule ---")
    print("  Winner maximizes T3 rescue at .5 (primary) then .4 secondary, subject to:")
    print("  FPR on 132 ordered clean pairs <= 4 (was 2 for baseline) and T5 semantic collisions <= 2 (baseline ~0-2).")
    print("  If naive list FPR exceeds 4, CRC8-adjusted estimate is used (threshold 4 with CRC).")
    # Rank by .5 delta
    ranking = []
    for dname in list(decoders.keys()) + ["list_chase3_soft", "list_chase3_hard"]:
        delta_05 = results.get("0.5", {}).get(dname, 0) - results.get("0.5", {}).get("baseline_soft", 0)
        delta_04 = results.get("0.4", {}).get(dname, 0) - results.get("0.4", {}).get("baseline_soft", 0)
        fpr = fpr_results.get(dname, 999)
        t5c = t5_results.get(dname, 999)
        passes_fpr = fpr <= 4 or (dname.startswith("list") and (len(ordered_pairs) * (1 - (1 - 1/256) ** 8)) <= 4)
        ranking.append((dname, delta_05, delta_04, fpr, t5c, passes_fpr))
    ranking.sort(key=lambda x: (x[5], x[1], x[2]), reverse=True)  # passes_fpr then delta
    for r in ranking:
        print(f"  {r[0]}: delta .5 {r[1]:+d} delta .4 {r[2]:+d} FPR {r[3]} T5 {r[4]} passes {r[5]}")

    winner = ranking[0][0] if ranking else "none"
    print(f"\nWinner: {winner}")

    output = {
        "schema": "f5-phase0-shootout-v1",
        "data_split": "development",
        "stress_dir": str(stress_dir),
        "sources": sources,
        "ordered_pairs": len(ordered_pairs),
        "t5_pairs": len(t5_pairs),
        "T3": {str(k): dict(v) for k, v in results.items()},
        "FPR_132": dict(fpr_results),
        "T5": dict(t5_results),
        "ranking": [{"decoder": r[0], "delta_05": r[1], "delta_04": r[2], "fpr": r[3], "t5": r[4], "passes_fpr": r[5]} for r in ranking],
        "winner": winner,
        "notes": "All T3 counts /58 at .4 and .5, /57 at .6. FPR threshold 4/132. T5 ignores perceptual-hash distance (conservative).",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

"""Frozen F5 delivered-payload binding diagnostic; development pixels only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from journal_vae_probe import Evaluator, compact, checked, F5_RUN, SOURCES, write
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
from f5_gate import OWNERS

MODES = ("combined", "semantic_only", "perceptual_only", "none")
ARMS = ("donor_positive", "recipient_sham", "residual_0.5", "residual_1.0", "public_donor_synthesis")
PARAMS = dict(psnr_db=52.0, steps=150, target_margin=4.0, mask_power=0.0, refine_rounds=1)


def pairs():
    ids = sorted(SOURCES)
    if len(ids) != 12:
        raise ValueError("This frozen protocol requires exactly twelve development sources")
    return list(zip(ids[::2], ids[1::2]))


def delivery(result, q, h):
    """Never equate recomputation fallback with delivery of a fixed donor payload."""
    def errors(tier, target):
        return None if target is None else (int(result[tier]["decoded_code"], 16) ^ target).bit_count()
    qe, he = errors("semantic", q), errors("instance", h)
    sem = q is not None and bool(result["semantic"]["read"]) and qe == 0
    full = sem and h is not None and bool(result["instance"]["read"]) and he == 0
    return dict(semantic_exact=sem, both_exact=full, q_bit_errors=qe, h_bit_errors=he,
                semantic_presence=bool(result["semantic"]["found"]),
                both_presence=bool(result["semantic"]["found"] and result["instance"]["found"]))


def extracted_controls(result, profile):
    """Ablate predicates on the exact same combined-mode extracted signals.

    Instance read remains conditioned on F5's q_bound; this is not a factorial
    detector. Report its own h predicate before semantic-status propagation.
    """
    d = profile["decision"]
    s, i = result["semantic"], result["instance"]
    h_status = (f5.base._content_status(i["corrected_distance"], int(d["instance_radius"]),
                                      int(d["instance_mismatch_distance"]), True) if i["found"] else None)
    return dict(semantic_rejection=s["found"] and s["content_status"] != "match",
                instance_own_content_status=h_status,
                instance_own_rejection=i["found"] and h_status != "match",
                semantic_disabled_presence=bool(s["found"]),
                semantic_disabled_read_presence=bool(s["found"] and s["read"]),
                both_disabled_presence=bool(s["found"] and i["found"]),
                both_disabled_read_presence=bool(s["found"] and s["read"] and i["found"] and i["read"]))


def synthesize(ev, rgb, q, h):
    """Write FIXED q/h; ordinary embed_rgb would recompute recipient h."""
    profile, key, config = v5._resolve(ev.profile, None)
    owner = v5.canonical_owner(OWNERS[0])
    luma = v5.luminance_from_rgb(rgb.tolist())
    height, width = f5.base._check_image(luma, int(profile["minimum_side"]))
    table = v5._semantic_table(owner, key, config)
    ws = [chip for segment in range(v5.CODE_BITS) for chip in table[segment][v5._bit(q, segment)]]
    layout = f5.Layout(profile, key, config, owner)
    current = np.clip(np.rint(f5.robust_pgd(ev.reader, rgb / 255.0, layout, ws,
                           PARAMS["psnr_db"], PARAMS["steps"], PARAMS["target_margin"]) * 255), 0, 255)
    fragile_reports = []
    for round_index in range(1 + PARAMS["refine_rounds"]):
        if h is not None:
            before = v5.luminance_from_rgb(current.astype(np.uint8).tolist())
            marked = [[float(value) for value in row] for row in before]
            fragile = v5._Fragile(profile, key, config, owner, height, width)
            itable = v5._instance_table(owner, key, config)
            wi = [chip for segment in range(v5.CODE_BITS)
                  for chip in itable[segment][v5._bit(q, segment)][v5._bit(h, segment)]]
            fragile_reports.append(v5._embed_fragile(marked, fragile, wi, profile, False, True))
            current = np.clip(np.rint(current + (np.asarray(marked) - np.asarray(before))[..., None]), 0, 255)
        if round_index < PARAMS["refine_rounds"]:
            current = np.clip(np.rint(f5.robust_pgd(ev.reader, current / 255.0, layout, ws,
                                max(PARAMS["psnr_db"] + 6, 50), max(PARAMS["steps"] // 3, 20),
                                PARAMS["target_margin"]) * 255), 0, 255)
    return current.astype(np.uint8), dict(fixed_q=f"{q:08x}", fixed_h=None if h is None else f"{h:08x}",
                                         fragile_reports=fragile_reports, semantic_only=h is None)


def summary(rows):
    out = {}
    for arm in (*ARMS, "public_recipient_authorization_demo"):
        group = [r for r in rows if r["arm"] == arm]
        good = [r for r in group if r["status"] == "ok"]
        stats = dict(planned_attempts=len(group), completed=len(good), failed=len(group) - len(good),
                     semantic_exact=sum(r["delivery"]["semantic_exact"] for r in good),
                     both_exact=sum(r["delivery"]["both_exact"] for r in good),
                     semantic_found=sum(r["delivery"]["semantic_presence"] for r in good),
                     both_found=sum(r["delivery"]["both_presence"] for r in good),
                     checked_semantic=sum(r["checked_semantic"] for r in good),
                     combined_both_match=sum(r["combined_both_match"] for r in good),
                     false_donor_full=sum(r["false_donor_full"] for r in good),
                     mode_outputs={mode: {outcome: sum(r["calls"][mode]["outcome"] == outcome for r in good)
                                   for outcome in sorted({r["calls"][mode]["outcome"] for r in good})} for mode in MODES})
        stats["subsets"] = {}
        for name, subset in (("all", good), ("strict_semantic_delivered", [r for r in good if r["delivery"]["semantic_exact"]]),
                             ("strict_both_delivered", [r for r in good if r["delivery"]["both_exact"]])):
            stats["subsets"][name] = dict(denominator=len(group) if name == "all" else len(subset),
                completed=len(subset),
                checked_semantic=sum(r["checked_semantic"] for r in subset),
                combined_both_match=sum(r["combined_both_match"] for r in subset),
                **{key: sum(r["extracted_controls"][key] for r in subset) for key in
                   ("semantic_rejection", "instance_own_rejection", "semantic_disabled_read_presence", "both_disabled_read_presence")})
        stats["proxy"] = {str(limit): dict(qualified=len(sel),
            semantic_exact=sum(r["delivery"]["semantic_exact"] for r in sel),
            both_exact=sum(r["delivery"]["both_exact"] for r in sel),
            checked_semantic=sum(r["checked_semantic"] for r in sel),
            combined_both_match=sum(r["combined_both_match"] for r in sel))
            for limit in (.2, .3) for sel in [[r for r in good if r["quality_recipient"]["lpips"] <= limit]]}
        out[arm] = stats
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    from PIL import Image
    started = time.monotonic()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "images").mkdir()
    plan = [(d, r, arm) for d, r in pairs() for arm in ARMS]
    plan.append((*pairs()[0], "public_recipient_authorization_demo"))
    record = dict(schema="journal-binding-probe-v1", commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), command=sys.argv, seeds=[],
        data_split="development", sources=sorted(SOURCES), pairs=pairs(),
        config=dict(**PARAMS, modes=MODES, owners=list(OWNERS[:2]), semantic_views=7, binding="soft",
                    roster_size=1, saved_marks=str(F5_RUN), residual_scales=[.5, 1.0],
                    primary_proxy_lpips=.2, sensitivity_proxy_lpips=.3,
                    public_synthesis_local_model_access=True, external_detector_queries=0,
                    human_admissibility="missing", synthesis_attempts_per_pair=1),
        outcome="running", duration_seconds=None)
    write(args.output_dir / "run.json", record)
    rows = []
    try:
        ev = Evaluator()
        record["config"]["profile"] = ev.profile
        write(args.output_dir / "run.json", record)
        cache = {}
        def load(sid, control):
            return np.asarray(Image.open(F5_RUN / "images" / f"clean-{sid}-{control}.png").convert("RGB"), np.uint8)
        def donor_payload(d):
            if d not in cache:
                rgb = load(d, "C1")
                result = ev.detect(rgb, "f5", OWNERS[0])
                cache[d] = (rgb, result,
                    int(result["semantic"]["decoded_code"], 16) if result["semantic"]["read"] else None,
                    int(result["instance"]["decoded_code"], 16) if result["instance"]["read"] else None)
            return cache[d]
        for donor, recipient, arm in plan:
            row = dict(donor_id=donor, recipient_id=recipient, donor_claim=OWNERS[0],
                       recipient_scenario_label=OWNERS[1], arm=arm, status="running")
            try:
                d1, positive, q, h = donor_payload(donor)
                d0, r0 = load(donor, "C0"), load(recipient, "C0")
                row["donor_decoding"] = compact(positive)
                row["payload_origin"] = "saved donor D1 decoded under alpha"
                if arm == "donor_positive":
                    rgb = d1
                elif arm == "recipient_sham":
                    rgb = r0
                elif arm.startswith("residual_"):
                    scale = float(arm.split("_")[1])
                    rgb = np.clip(np.rint(r0.astype(float) + scale * (d1.astype(float) - d0.astype(float))), 0, 255).astype(np.uint8)
                else:
                    if arm == "public_recipient_authorization_demo":
                        own = ev.detect(r0, "f5", OWNERS[0])
                        q, h = int(own["semantic_code"], 16), int(own["perceptual_hash"], 16)
                        row["payload_origin"] = "public recipient feature/hash recomputation under alpha; no authorization"
                    if q is None:
                        raise ValueError("Donor q unreadable: public donor synthesis cannot silently use oracle q")
                    rgb, row["synthesis"] = synthesize(ev, r0, q, h)
                row["intended_payload"] = dict(q=None if q is None else f"{q:08x}", h=None if h is None else f"{h:08x}")
                path = args.output_dir / "images" / f"{donor}-{recipient}-{arm}.png"
                Image.fromarray(rgb).save(path)
                saved = np.asarray(Image.open(path).convert("RGB"), np.uint8)
                features, latent = ev.features(saved, 7), ev.reader.latent(saved)
                calls = {mode: ev.detect(saved, "f5", OWNERS[0], features, latent, mode) for mode in MODES}
                combined = calls["combined"]
                row.update(image=str(path), calls={mode: compact(call) for mode, call in calls.items()},
                           delivery=delivery(combined, q, h), extracted_controls=extracted_controls(combined, ev.profile),
                           quality_recipient=ev.metrics(r0, saved), quality_donor=ev.metrics(d0, saved),
                           checked_semantic=checked(combined), combined_both_match=combined["outcome"] == "both_match",
                           false_donor_full=arm in ("residual_0.5", "residual_1.0", "public_donor_synthesis") and combined["outcome"] == "both_match",
                           status="ok")
            except Exception:
                row.update(status="failed", error=traceback.format_exc())
            rows.append(row)
            with (args.output_dir / "rows.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, allow_nan=False) + "\n")
            write(args.output_dir / "summary.json", summary(rows))
            print(json.dumps({k: row[k] for k in ("donor_id", "recipient_id", "arm", "status")}), flush=True)
            if row["status"] == "failed":
                print(row["error"], flush=True)
        record.update(outcome="completed" if all(r["status"] == "ok" for r in rows) else "completed_with_failures",
                      rows=len(rows), summary=summary(rows))
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
        for donor, recipient, arm in plan[len(rows):]:
            row = dict(donor_id=donor, recipient_id=recipient, arm=arm, status="failed", error="Run setup/fatal failure; see run.json")
            rows.append(row)
            with (args.output_dir / "rows.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row) + "\n")
        write(args.output_dir / "summary.json", summary(rows))
        raise
    finally:
        record["duration_seconds"] = time.monotonic() - started
        write(args.output_dir / "run.json", record)


if __name__ == "__main__":
    main()

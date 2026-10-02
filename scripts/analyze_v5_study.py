"""Descriptive analysis of a v5 two-tier study run; stdlib only, reads results.json, writes nothing into the run.

Applies experiments/c4-v5-two-tier-regeneration-v1/acceptance-criteria.md mechanically
where the run itself can decide a criterion. Criteria that need two independent
human content assessments are reported as NOT_EVALUABLE, never as passed.
"""
import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ALPHA = "qim-pilot-owner-alpha"
STRENGTHS = (0.05, 0.1, 0.2, 0.4)


def admissible(q):
    if not q:
        return None
    psnr = q.get("psnr_db")
    lp = q.get("lpips", {}).get("value")
    if lp is None:
        return None
    return bool((q.get("zero_error") or (psnr is not None and psnr > 35)) and q["ssim_rgb"] > .9 and lp < .1)


def describe(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return {"n": len(values), "mean": statistics.fmean(values), "median": statistics.median(values),
            "sd": statistics.stdev(values) if len(values) > 1 else 0.0, "min": min(values), "max": max(values)}


def detections(row, owner=None, mode=None):
    return [d["result"] for d in row.get("detections", [])
            if (owner is None or d["claimed_owner"] == owner) and (mode is None or d["binding_mode"] == mode)]


def one(row, owner, mode):
    found = detections(row, owner, mode)
    return found[0] if len(found) == 1 else None


def clean_axis(index, sources):
    out = {"per_source": {}, "c1_both_match": 0, "c1_admissible": 0, "c1_changed": 0,
           "c0_watermark_found_calls": 0, "c0_calls": 0, "wrong_owner_found_calls": 0, "wrong_owner_calls": 0}
    for s in sources:
        c0, c1 = index[f"clean-{s}-C0"], index[f"clean-{s}-C1"]
        r = one(c1, ALPHA, "combined")
        q = c1.get("quality")
        entry = {"c1_status": c1["status"], "c1_outcome": r and r["outcome"], "changed_channels": c1.get("changed_channels"),
                 "psnr": q and q["psnr_db"], "ssim": q and q["ssim_rgb"], "lpips": q and q["lpips"].get("value"),
                 "admissible": admissible(q), "embed_report_verified": (c1.get("source_feature_embedding_report") or {}).get("verified"),
                 "c0_outcomes": [d["outcome"] for d in detections(c0)],
                 "wrong_owner_outcomes": [d["outcome"] for d in detections(c1) if d["owner_id"] != ALPHA]}
        out["per_source"][s] = entry
        out["c1_both_match"] += int(entry["c1_outcome"] == "both_match")
        out["c1_admissible"] += int(bool(entry["admissible"]))
        out["c1_changed"] += int((entry["changed_channels"] or 0) > 0)
        for d in detections(c0):
            out["c0_calls"] += 1
            out["c0_watermark_found_calls"] += int(d["watermark_found"])
        for d in detections(c1):
            if d["owner_id"] != ALPHA:
                out["wrong_owner_calls"] += 1
                out["wrong_owner_found_calls"] += int(d["watermark_found"])
    n = len(sources)
    out["prerequisite_numeric_pass"] = (out["c1_both_match"] == n and out["c1_admissible"] == n and out["c1_changed"] == n
                                        and out["c0_calls"] == 4 * n and out["c0_watermark_found_calls"] == 0
                                        and out["wrong_owner_calls"] == 3 * n and out["wrong_owner_found_calls"] == 0)
    return out


def t3_axis(rows, marked="C1"):
    """One stratum per dose for the marked control ``marked`` (C1 default profile, C2 strong profile) against C0."""
    strata = defaultdict(lambda: {"C0": [], "C1": [], "C2": []})
    for r in rows:
        if r["axis"] != "T3":
            continue
        key = "vae_mode" if r["dose"] == "vae_mode" else f"strength_{r['strength']}"
        strata[key][r["control"]].append(r)
    out = {}
    for key, groups in sorted(strata.items()):
        c1, c0 = groups[marked], groups["C0"]
        outcomes = Counter()
        sem_ok = Counter()
        found_any = Counter()
        clip_ok = Counter()
        per_source = defaultdict(list)
        failed = Counter()
        clip_values, q_imm, q_src = [], [], []
        scores1, scores0, states = [], [], Counter()
        for r in c1:
            res = one(r, ALPHA, "combined")
            if r["status"] == "failed" and not r.get("detections"):
                failed[r["source_id"]] += 1
            if res is None:
                per_source[r["source_id"]].append(None)
                continue
            outcomes[res["outcome"]] += 1
            states[res["proposal_state"]] += 1
            scores1.append(res["semantic"]["recomputed_score"])
            ok = bool(res["semantic"]["found"] and res["semantic"]["content_match"])
            sem_ok[r["source_id"]] += int(ok)
            found_any[r["source_id"]] += int(res["watermark_found"])
            cos = r.get("clip_source_cosine")
            clip_values.append(cos)
            clip_ok[r["source_id"]] += int(cos is not None and cos >= .90)
            q_imm.append((r.get("quality_immediate") or {}).get("psnr_db"))
            q_src.append((r.get("quality_source") or {}).get("psnr_db"))
            per_source[r["source_id"]].append(res["outcome"])
        seeds = 1 if key == "vae_mode" else 3
        groups_semantic_all = sum(1 for s in per_source if sem_ok[s] == seeds)
        groups_clip_all = sum(1 for s in per_source if clip_ok[s] == seeds)
        c0_found = sum(int(d["watermark_found"]) for r in c0 for d in detections(r, ALPHA, "combined"))
        c0_calls = sum(len(detections(r, ALPHA, "combined")) for r in c0)
        c0_any_owner_found = sum(int(d["watermark_found"]) for r in c0 for d in detections(r))
        scores0 = [d["semantic"]["recomputed_score"] for r in c0 for d in detections(r, ALPHA, "combined")]
        out[key] = {"c1_rows": len(c1), "c1_with_detection": sum(outcomes.values()),
                    "c1_failed_rows": sum(1 for r in c1 if r["status"] == "failed" and not r.get("detections")),
                    "c0_failed_rows": sum(1 for r in c0 if r["status"] == "failed" and not r.get("detections")),
                    "c1_outcomes": dict(outcomes), "c1_proposal_states": dict(states),
                    "c1_semantic_recomputed_score": describe(scores1), "c0_semantic_recomputed_score": describe(scores0),
                    "c1_watermark_found": sum(found_any.values()),
                    "c1_semantic_found_and_content_match": sum(sem_ok.values()),
                    "source_groups_semantic_on_all_seeds": groups_semantic_all,
                    "source_groups_clip_ge_090_on_all_seeds": groups_clip_all,
                    "c0_alpha_calls": c0_calls, "c0_alpha_watermark_found": c0_found,
                    "c0_any_owner_watermark_found": c0_any_owner_found,
                    "clip_source_cosine": describe(clip_values),
                    "psnr_vs_immediate_input": describe(q_imm), "psnr_vs_source": describe(q_src),
                    "per_source_outcomes": {s: v for s, v in sorted(per_source.items())},
                    "visual_assessment": "NOT_EVALUABLE: two independent human content assessments missing"}
    return out


def strong_clean(index):
    """Secondary arm: marked images of the strong profile; descriptive, outside numeric admissibility by design."""
    out = {}
    for _identity, row in sorted(index.items()):
        if row["axis"] != "clean" or row.get("control") != "C2":
            continue
        result = one(row, ALPHA, "combined")
        q = row.get("quality")
        out[row["source_id"]] = {"status": row["status"], "outcome": result and result["outcome"],
                                 "psnr": q and q["psnr_db"], "ssim": q and q["ssim_rgb"], "lpips": q and q["lpips"].get("value"),
                                 "admissible": admissible(q),
                                 "wrong_owner_found": sum(int(d["watermark_found"]) for d in detections(row) if d["owner_id"] != ALPHA)}
    return out


def ordinary_axis(rows):
    """Supplementary axis: ordinary processing of marked and unmarked images; no pass rule attached."""
    out = {}
    for operation in sorted({r["operation"] for r in rows if r["axis"] == "T1s"}):
        group = [r for r in rows if r["axis"] == "T1s" and r["operation"] == operation]
        c1 = [one(r, ALPHA, "combined") for r in group if r["control"] == "C1"]
        c0 = [d for r in group if r["control"] == "C0" for d in detections(r)]
        out[operation] = {"c1_rows": len(c1), "c1_outcomes": dict(Counter(d["outcome"] if d else "missing" for d in c1)),
                          "c1_semantic_found_and_content_match": sum(1 for d in c1 if d and d["semantic"]["found"] and d["semantic"]["content_match"]),
                          "c0_calls": len(c0), "c0_watermark_found": sum(int(d["watermark_found"]) for d in c0)}
    return out


def transfer_axis(rows, axis):
    arms = defaultdict(list)
    for r in rows:
        if r["axis"] != axis:
            continue
        label = r["arm"]
        if r["arm"] in ("public_patch", "unmarked_patch_sham"):
            label += f"_{r['patch_size']}"
        if r["arm"] == "clean_donor_residual":
            label += f"_{r['scale']}"
        arms[label].append(r)
    out = {}
    for label, group in sorted(arms.items()):
        stats = Counter()
        recipients_delivered_adm = set()
        recipients_fa = set()
        mode_outcomes = defaultdict(Counter)
        psnr = []
        for r in group:
            stats["attempts"] += 1
            if not r.get("detections"):
                stats["no_detection"] += 1
                continue
            adm = admissible(r.get("quality"))
            stats["admissible"] += int(bool(adm))
            psnr.append((r.get("quality") or {}).get("psnr_db"))
            none = one(r, ALPHA, "none")
            comb = one(r, ALPHA, "combined")
            for d in detections(r):
                mode_outcomes[d["binding_mode"]][d["outcome"]] += 1
            delivered = bool(none and none["watermark_found"])
            stats["delivered"] += int(delivered)
            if delivered and adm:
                stats["admissible_delivered"] += 1
                recipients_delivered_adm.add(r["recipient_id"])
            if comb and comb["outcome"] == "both_match":
                stats["combined_both_match"] += 1
                if adm:
                    stats["admissible_false_attribution"] += 1
                    recipients_fa.add(r["recipient_id"])
            if delivered and comb and comb["outcome"] == "content_mismatch":
                stats["content_mismatch_given_delivery"] += 1
            if delivered and comb and comb["outcome"] == "content_uncertain":
                stats["content_uncertain_given_delivery"] += 1
        out[label] = {**dict(stats), "distinct_recipients_admissible_delivered": len(recipients_delivered_adm),
                      "distinct_recipients_admissible_false_attribution": len(recipients_fa),
                      "outcomes_by_mode": {m: dict(c) for m, c in mode_outcomes.items()},
                      "recipient_psnr": describe(psnr)}
    return out


def t5_axis(index, rows, sources):
    pairs = [r for r in rows if r["axis"] == "T5"]
    by_label = defaultdict(list)
    for r in pairs:
        by_label[r["semantic_label"]].append(r)
    out = {}
    for label, group in sorted(by_label.items()):
        d1 = [r.get("distances_C1") for r in group if r.get("distances_C1")]
        out[label] = {"pairs": len(group), "with_distances": len(d1),
                      "q_le_6": sum(d["semantic"] <= 6 for d in d1),
                      "q_le_6_and_h_gt_6": sum(d["semantic"] <= 6 and d["instance"] > 6 for d in d1),
                      "joint_near_collision": sum(d["semantic"] <= 6 and d["instance"] <= 6 for d in d1),
                      "exact_q": sum(d["semantic"] == 0 for d in d1), "exact_h": sum(d["instance"] == 0 for d in d1),
                      "q_distance": describe([d["semantic"] for d in d1]),
                      "h_distance": describe([d["instance"] for d in d1]),
                      "clip_pair_cosine": describe([r.get("clip_pair_cosine") for r in group])}
    same_instance = [index[f"clean-{s}-C1"].get("same_instance_distances") for s in sources]
    out["same_instance_C0_vs_C1"] = {"available": sum(x is not None for x in same_instance),
                                     "both_le_6": sum(1 for x in same_instance if x and x["semantic"] <= 6 and x["instance"] <= 6),
                                     "values": same_instance}
    same = out.get("same", {})
    out["component_support_numeric"] = bool(same.get("q_le_6_and_h_gt_6", 0) >= 5 and out.get("different", {}).get("pairs", 0) >= 5
                                            and out["same_instance_C0_vs_C1"]["both_le_6"] == len(sources)
                                            and same.get("joint_near_collision", 1) == 0)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    rows = data["rows"]
    index = {r["id"]: r for r in rows}
    sources = sorted({r["source_id"] for r in rows if r["axis"] == "clean" and r["control"] != "C2"})
    timing = defaultdict(list)
    for r in rows:
        for d in r.get("detections", []):
            timing["detector_seconds"].append(d["elapsed_seconds"])
        if "clip" in r:
            timing["clip_seconds"].append(r["clip"]["elapsed_seconds"])
        if "embedding_seconds" in r:
            timing["embedding_seconds"].append(r["embedding_seconds"])
        if "attack_seconds_including_save" in r:
            timing[f"attack_{r['axis']}_seconds"].append(r["attack_seconds_including_save"])
    analysis = {
        "run_id": data["run_id"], "elapsed_seconds": data["elapsed_seconds"],
        "planned_detector_calls": data["planned_detector_calls"], "completed_detector_calls": data["completed_detector_calls"],
        "stage_failures": data["stage_failures"], "row_status": dict(Counter(r["status"] for r in rows)),
        "row_errors": dict(Counter(e["message"][:120] for r in rows for e in r.get("errors", []))),
        "label": data.get("label"),
        "clean": clean_axis(index, sources), "T3": t3_axis(rows), "T3_strong_arm": t3_axis(rows, "C2"),
        "clean_strong_arm": strong_clean(index), "T1_supplementary": ordinary_axis(rows),
        "T4": transfer_axis(rows, "T4"),
        "T5": t5_axis(index, rows, sources), "T5_transfer": transfer_axis(rows, "T5-transfer"),
        "timing": {k: describe(v) for k, v in timing.items()},
        "claim_limits": "Exploratory, image-domain comparator only; no latent, legal, population-FPR or publication claim. "
                        "Visual retention criteria need two independent human assessments and are not evaluated here.",
    }
    Path(args.out).write_text(json.dumps(analysis, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: analysis[k] for k in ("completed_detector_calls", "row_status", "stage_failures")}))


if __name__ == "__main__":
    main()

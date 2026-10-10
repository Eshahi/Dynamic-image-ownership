"""Independent CPU endpoint analysis of the fixed D2-V1 Stage A screen."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)
CONDITIONS = ("clean", "sd15_vae", "sdxl_vae")
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
READ, PRESENCE = 8.259326826136963, 4.982033056390042
RANK = {"match": 0, "unchecked": 0, "uncertain": 1, "mismatch": 2}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def errors(word, target):
    return (int(word, 16) ^ int(target, 16)).bit_count()


def strict(q):
    return bool((q.get("psnr_infinite") or q.get("psnr_db", 0) > 35)
                and q["ssim_rgb"] > .9 and q["lpips"] < .1)


def content(distance):
    return "match" if distance <= 6 else "mismatch" if distance >= 10 else "uncertain"


def verify_call(call, label, discrepancies):
    """Recompute score decisions and content/outcome from retained scalar evidence."""
    channels = {}
    for name in ("semantic", "instance"):
        c = call[name]
        read = c["decoded_score"] >= READ
        found = read or c["recomputed_score"] >= PRESENCE
        distance = c.get("soft_distance") if name == "semantic" and read else c.get("corrected_distance")
        if distance is None and found:
            distance = c["corrected_distance"]
        status = content(distance) if found else None
        if name == "instance" and found and channels["semantic"]["found"]:
            status = max(status, channels["semantic"]["status"], key=RANK.get)
        match = found and status == "match"
        for key, value in (("read", read), ("found", found), ("content_status", status), ("content_match", match),
                           ("decoded_threshold", READ), ("recomputed_threshold", PRESENCE)):
            if c.get(key) != value:
                discrepancies.append({"identity": label, "field": name + "." + key, "stored": c.get(key), "recomputed": value})
        channels[name] = {"read": read, "found": found, "match": match, "status": status,
                          "decoded_code": c["decoded_code"]}
    s, i = channels["semantic"], channels["instance"]
    any_found = s["found"] or i["found"]
    outcome = ("neither_match" if not any_found else "content_mismatch" if
               (s["found"] and s["status"] == "mismatch") or (i["found"] and i["status"] == "mismatch") else
               "both_match" if s["match"] and i["match"] else "semantic_only" if s["match"] and not i["found"] else
               "instance_only" if i["match"] and not s["found"] else "content_uncertain")
    for key, value in (("watermark_found", any_found), ("outcome", outcome)):
        if call.get(key) != value:
            discrepancies.append({"identity": label, "field": key, "stored": call.get(key), "recomputed": value})
    return {**channels, "any": any_found, "both": outcome == "both_match"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    record = load(args.run / "run.json")
    original_path = Path(record["config"]["cached_writer"])
    original_rows = rows(original_path)
    original = {r["source_id"]: r for r in original_rows}
    observed = rows(args.run / "rows.jsonl")
    discrepancies = []
    if len(original_rows) != 12 or set(original) != set(IDS) or any(r["status"] != "ok" for r in original_rows):
        raise ValueError("D2 comparator must contain exactly the fixed twelve successful sources")
    expected = {(sid, cond, ctl) for sid in IDS for cond in CONDITIONS for ctl in ("C1", "C0")}
    expected_calls = {(sid, cond, ctl, owner) for sid, cond, ctl in expected
                      for owner in ((ALPHA, BETA) if ctl == "C1" else (ALPHA,))}
    keyed = {}
    duplicates = []
    call_keys = set()
    failed_calls = []
    failed_images = []
    endpoints = {}
    for row in observed:
        key = (row["source_id"], row["condition"], row["control"])
        if key in keyed:
            duplicates.append(key)
        keyed[key] = row
        if row["status"] != "ok":
            failed_images.append(key)
        for owner, call in row.get("calls", {}).items():
            ck = (*key, owner)
            call_keys.add(ck)
            try:
                endpoints[ck] = verify_call(call, list(ck), discrepancies)
            except (KeyError, TypeError, ValueError) as exc:
                failed_calls.append({"identity": ck, "error": str(exc)})
    stats = {"scope": "Exploratory cached development Stage A; correlated twelve-source evidence; no population FPR, bootstrap, M1a or independent confirmation",
             "provenance": {"run": str(args.run), "run_code_commit": record["commit"], "comparator_rows": str(original_path),
                            "analysis_script": str(Path(__file__).resolve()), "analysis_code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True).strip()},
             "inventory": {"planned_unique_images": 72, "planned_unique_calls": 108, "row_count": len(observed),
                           "unique_images": len(keyed), "unique_calls": len(call_keys), "duplicates": duplicates,
                           "missing_images": sorted(expected - set(keyed)), "extra_images": sorted(set(keyed) - expected),
                           "missing_calls": sorted(expected_calls - call_keys), "extra_calls": sorted(call_keys - expected_calls),
                           "failed_images": failed_images, "failed_calls": failed_calls}, "conditions": {}, "discrepancies": discrepancies}
    quality_ids = [sid for sid in IDS if strict(original[sid]["conditions"]["clean"]["quality_source"])]
    stats["strict_clean_quality"] = len(quality_ids)
    stats["strict_clean_quality_source_ids"] = quality_ids
    diagnostics = []
    for cond in CONDITIONS:
        joint, old_joint, clean_exact, both, exact_h, checked = [], [], [], [], [], []
        negatives = {"c0_any": [], "wrong_owner_any": []}
        old_negatives = {"c0_any": [], "wrong_owner_any": []}
        hist = {k: Counter() for k in ("q0", "qV", "view1", "view2")}
        bit_counts = {k: [0] * 32 for k in hist}
        changed = []
        for sid in IDS:
            target = original[sid]["payload"]
            old_cell = original[sid]["conditions"][cond]
            old_call = old_cell["calls"][ALPHA]
            old_ep = verify_call(old_call, ["D2", sid, cond, ALPHA], discrepancies)
            old_s = old_ep["semantic"]
            old_j = old_s["read"] and old_s["found"] and old_s["match"] and old_s["decoded_code"] == target["q"]
            if bool(old_cell["joint_fixed_q"]) != bool(old_j):
                discrepancies.append({"identity": ["D2", sid, cond], "field": "joint_fixed_q", "stored": old_cell["joint_fixed_q"], "recomputed": bool(old_j)})
            if old_j:
                old_joint.append(sid)
            for owner, old_negative, name in ((ALPHA, old_cell["c0_call"], "c0_any"),
                                             (BETA, old_cell["calls"][BETA], "wrong_owner_any")):
                old_negative_ep = verify_call(old_negative, ["D2", sid, cond, name, owner], discrepancies)
                if old_negative_ep["any"]:
                    old_negatives[name].append(sid)
            ck = (sid, cond, "C1", ALPHA)
            ep = endpoints.get(ck)
            if ep is not None and keyed[ck[:3]]["status"] == "ok":
                call = keyed[ck[:3]]["calls"][ALPHA]
                s, i = ep["semantic"], ep["instance"]
                if s["found"] and s["read"] and s["match"]:
                    checked.append(sid)
                    if s["decoded_code"] == target["q"]:
                        joint.append(sid)
                if i["read"] and i["decoded_code"] == target["h"]:
                    exact_h.append(sid)
                if ep["both"]:
                    both.append(sid)
                if sid in joint and sid in exact_h and ep["both"]:
                    clean_exact.append(sid)
                v = call["semantic"]
                words = [v["original_q"], v["selected_q"], *v["view_words"][1:]]
                biterrs = [errors(w, target["q"]) for w in words]
                for name, word, value in zip(hist, words, biterrs):
                    hist[name][value] += 1
                    error_mask = int(word, 16) ^ int(target["q"], 16)
                    for bit in range(32):
                        bit_counts[name][bit] += (error_mask >> (31 - bit)) & 1
                changes = errors(words[0], words[1])
                if changes:
                    changed.append(sid)
                selected = 0
                for bit in range(32):
                    gap = sorted(v["view_normalized_gaps"][view][bit] for view in range(3))[1]
                    choose = (int(words[0], 16) >> (31 - bit)) & 1 if gap == 0 else int(gap > 0)
                    selected = (selected << 1) | choose
                if selected != int(words[1], 16) or changes != v["changed_bits"] or v["original_selected_score"] > v["original_maxscore"] + 1e-12 or words[1] != s["decoded_code"]:
                    discrepancies.append({"identity": list(ck), "field": "multiview_logged_selection_invariants", "recomputed": False})
                diagnostics.append({"source_id": sid, "condition": cond, "target_q_evaluator_only": target["q"],
                                    "q0": words[0], "qV": words[1], "view_words": v["view_words"],
                                    "q0_qV_view1_view2_bit_errors": biterrs, "changed_bits": changes,
                                    "corrected_error_bit_positions_msb0": [bit for bit in range(32) if
                                        ((int(words[0], 16) ^ int(target["q"], 16)) >> (31 - bit)) & 1 and
                                        not ((int(words[1], 16) ^ int(target["q"], 16)) >> (31 - bit)) & 1],
                                    "introduced_error_bit_positions_msb0": [bit for bit in range(32) if
                                        not ((int(words[0], 16) ^ int(target["q"], 16)) >> (31 - bit)) & 1 and
                                        ((int(words[1], 16) ^ int(target["q"], 16)) >> (31 - bit)) & 1],
                                    "was_joint": bool(old_j), "is_joint": sid in joint,
                                    "original_selected_score": v["original_selected_score"], "original_maxscore": v["original_maxscore"]})
            for ctl, owner, name in (("C0", ALPHA, "c0_any"), ("C1", BETA, "wrong_owner_any")):
                neg = endpoints.get((sid, cond, ctl, owner))
                if neg and neg["any"]:
                    negatives[name].append(sid)
        stats["conditions"][cond] = {"semantic_checked": len(checked), "exact_checked_q": len(joint), "joint_source_ids": joint,
                                     "old_joint_source_ids": old_joint, "lost_old_joint": sorted(set(old_joint) - set(joint)),
                                     "gained_joint": sorted(set(joint) - set(old_joint)), "changed_q_source_ids": changed,
                                     "both_match": len(both), "exact_read_h": len(exact_h), "exact_q_h_both_match": len(clean_exact),
                                     "c0_any": len(negatives["c0_any"]), "wrong_owner_any": len(negatives["wrong_owner_any"]),
                                     "negative_positive_source_ids": negatives,
                                     "old_negative_positive_source_ids": old_negatives,
                                     "per_bit_error_counts_msb0_all_decoded_words": bit_counts,
                                     "bit_error_histograms_all_decoded_words": {k: dict(sorted(v.items())) for k, v in hist.items()}}
    stats["bit_diagnostics"] = diagnostics
    stats["resources"] = {"reported_inclusive_seconds": record.get("duration_seconds"), "reported_cuda_peak_allocated_bytes": record.get("cuda_peak_allocated_bytes"),
                          "cap_seconds": 300, "cap_cuda_bytes": 10 * 1024**3,
                          "timing_scope": "Run metadata inclusive clock; parent external wall timing reported separately, not invented by analysis"}
    stats["resource_budget_pass"] = bool(isinstance(record.get("duration_seconds"), (int, float)) and record["duration_seconds"] <= 300
                                          and isinstance(record.get("cuda_peak_allocated_bytes"), int) and record["cuda_peak_allocated_bytes"] <= 10 * 1024**3)
    inv = stats["inventory"]
    inventory_pass = inv["row_count"] == 72 and inv["unique_images"] == 72 and inv["unique_calls"] == 108 and not any(inv[k] for k in ("duplicates", "missing_images", "extra_images", "missing_calls", "extra_calls", "failed_images", "failed_calls"))
    c = stats["conditions"]
    stats["prerequisite_eligible"] = bool(inventory_pass and stats["resource_budget_pass"] and record["outcome"] == "completed" and not discrepancies
        and stats["strict_clean_quality"] == 12 and c["clean"]["exact_q_h_both_match"] == 12
        and c["sd15_vae"]["exact_checked_q"] == 12 and c["sdxl_vae"]["exact_checked_q"] >= 11
        and all(not v["lost_old_joint"] and v["c0_any"] == v["wrong_owner_any"] == 0 for v in c.values()))
    summary = load(args.run / "summary.json")
    for key in ("strict_clean_quality", "resource_budget_pass", "prerequisite_eligible"):
        if summary.get(key) != stats[key]:
            discrepancies.append({"identity": "summary", "field": key, "stored": summary.get(key), "recomputed": stats[key]})
    for cond, values in c.items():
        for key in ("semantic_checked", "exact_checked_q", "both_match", "exact_read_h", "c0_any", "wrong_owner_any", "lost_old_joint"):
            if summary["conditions"][cond].get(key) != values[key]:
                discrepancies.append({"identity": ["summary", cond], "field": key, "stored": summary["conditions"][cond].get(key), "recomputed": values[key]})
    if discrepancies:
        stats["prerequisite_eligible"] = False
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "statistics.json").write_text(json.dumps(stats, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# D2-V1 cached Stage A results", "", "Exploratory development evidence on twelve correlated sources. Targets are used only by this evaluator; operational h is a frozen clean-decoded target, not a known original embedded h.", "",
             f"Stage A {'passes; eligible only for the fixed cached T3 screen' if stats['prerequisite_eligible'] else 'fails; the fixed V1 rule closes immediately'}. This is not M1a/M1b, independent confirmation, or a substantially different design-family failure.", "",
             f"Inventory: {inv['unique_images']}/72 unique image identities; {inv['unique_calls']}/108 unique calls. Missing images/calls {len(inv['missing_images'])}/{len(inv['missing_calls'])}; failed images/calls {len(failed_images)}/{len(failed_calls)}; duplicates {len(duplicates)}. Strict inherited clean quality {len(quality_ids)}/12. Scalar/summary discrepancies: {len(discrepancies)}.", "",
             "| Condition | checked semantic | exact checked q | D2 exact checked q | exact h | both match | lost D2 joint IDs | gained IDs |", "|---|---:|---:|---:|---:|---:|---|---|"]
    for cond, v in c.items():
        lines.append(f"| {cond} | {v['semantic_checked']}/12 | {v['exact_checked_q']}/12 | {len(v['old_joint_source_ids'])}/12 | {v['exact_read_h']}/12 | {v['both_match']}/12 | {v['lost_old_joint']} | {v['gained_joint']} |")
    lines += ["", f"Observed any-channel negative detections: {sum(v['c0_any'] + v['wrong_owner_any'] for v in c.values())}/72 planned calls. Any-channel is recomputed as semantic found OR instance found and checked against watermark_found. No nominal FPR or independence claim is inferred.", "",
              "The selected word is independently reconstructed from logged normalized-gap medians and ties. Full scalar score thresholds, content distances/statuses and both-match outcomes are recomputed; original carrier pixels/features are not rerun. See statistics.json for all changed IDs, per-view errors, target-only word diagnostics, inventory and discrepancy details.", ""]
    for d in diagnostics:
        if d["changed_bits"] or d["q0_qV_view1_view2_bit_errors"][0]:
            lines.append(f"- {d['source_id']} {d['condition']}: errors q0/qV/view1/view2 = {d['q0_qV_view1_view2_bit_errors']}; changed {d['changed_bits']} bits; joint {d['was_joint']} -> {d['is_joint']}.")
    lines += ["", f"Reported inclusive runtime {record.get('duration_seconds')} seconds; allocated CUDA peak {record.get('cuda_peak_allocated_bytes')} bytes. Resource gate {'passes' if stats['resource_budget_pass'] else 'fails'}. Parent external wall timing is a separate receipt.", "",
              f"Run: `{args.run}`; run code `{record['commit']}`; D2 comparator: `{original_path}`. Analysis code commit `{stats['provenance']['analysis_code_commit']}`; analysis source `{stats['provenance']['analysis_script']}`."]
    (args.output_dir / "v1-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"eligible": stats["prerequisite_eligible"], "discrepancies": len(discrepancies), "joint": {k: v["exact_checked_q"] for k, v in c.items()}, "output": str(args.output_dir)}))


if __name__ == "__main__":
    main()

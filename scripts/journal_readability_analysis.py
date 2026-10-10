"""Recompute exploratory readability endpoints from JSON only (no GPU/images).

Usage: python scripts/journal_readability_analysis.py --diagnostic-run PATH
       [--screen-run PATH] [--output-dir PATH]
Incomplete configurations retain the fixed twelve-source denominator.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import statistics

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
CONDITIONS = ("clean", "sd15_vae", "sdxl_vae")
CONFIGS = ("R1", "R2", "R3", "R4")
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def read_rows(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON row {number} in {path}") from error
    return rows


def inventory(rows, planned, key):
    indexed = {}
    for row in rows:
        identity = key(row)
        if identity not in planned:
            raise ValueError(f"Unplanned identity: {identity}")
        if identity in indexed:
            raise ValueError(f"Duplicate identity: {identity}; no last-row selection permitted")
        indexed[identity] = row
    return indexed


def errors(decoded, target):
    return (int(decoded, 16) ^ int(target, 16)).bit_count()


def endpoints(call, payload):
    semantic, instance = call["semantic"], call["instance"]
    if call.get("native_q_bound") is not None:
        bound = semantic["decoded_code"] if semantic["found"] and semantic["content_status"] != "match" else call["semantic_code"]
        if int(bound, 16) != int(call["native_q_bound"], 16):
            raise ValueError("Recorded native q_bound contradicts frozen conditioning rule")
    qe = errors(semantic["decoded_code"], payload["q"])
    he = errors(instance["decoded_code"], payload["h"])
    exact_q = bool(semantic["read"] and qe == 0)
    exact_h = bool(instance["read"] and he == 0)
    return dict(q_bit_errors=qe, h_bit_errors=he, q_exact_read=exact_q,
        h_exact_read=exact_h, both_exact_read=exact_q and exact_h,
        joint_fixed_q=exact_q and bool(semantic["content_match"]),
        native_checked=bool(semantic["read"] and semantic["content_match"]),
        native_both_match=call["outcome"] == "both_match",
        q_target=payload["q"], h_target=payload["h"],
        decoded_q=semantic["decoded_code"], decoded_h=instance["decoded_code"],
        q_now=call.get("semantic_code"), h_now=call.get("perceptual_hash"),
        native_q_bound=call.get("native_q_bound"),
        native_q_bound_rule=call.get("native_q_bound_rule"),
        native_semantic=semantic, native_instance=instance, native_outcome=call["outcome"])


def strict_quality(quality):
    psnr = quality.get("psnr_db")
    return bool((quality.get("psnr_infinite") or psnr is not None and psnr > 35)
                and quality["ssim_rgb"] > .9 and quality["lpips"] < .1)


def any_detection(call):
    # Any tier presence counts, even if full attribution is rejected.
    return bool(call["semantic"]["found"] or call["instance"]["found"])


def finite_mean(values):
    values = [x for x in values if x is not None]
    return statistics.mean(values) if values else None


def decomposition(entry, clean):
    d, reference = entry["decomposition"], clean["decomposition"]
    host, mark, observed = (d[name] for name in
                           ("host_bit_gaps", "mark_bit_gaps", "raw_bit_gaps"))
    if not all(len(v) == 32 for v in (host, mark, observed)):
        raise ValueError("Expected exactly 32 bit gaps")
    sigma = max(d["projection_norm"] / math.sqrt(320), 1e-8)
    discrepancy = max(abs(h + m - o) for h, m, o in zip(host, mark, observed))
    normalized_error = max(abs(o / sigma - n) for o, n in
                           zip(observed, d["normalized_bit_gaps"]))
    failed = []
    for bit, gap in enumerate(observed):
        if gap <= 0:
            dh = host[bit] - reference["host_bit_gaps"][bit]
            dm = mark[bit] - reference["mark_bit_gaps"][bit]
            failed.append(dict(bit_index=bit, observed_gap=gap, host_gap=host[bit],
                mark_gap=mark[bit], normalized_gap=gap/sigma,
                host_gap_change_from_clean=dh, mark_gap_change_from_clean=dm,
                adverse_host_change=dh < 0, reduced_mark_contribution=dm < 0,
                description="both" if dh < 0 and dm < 0 else
                    "adverse host change" if dh < 0 else
                    "reduced mark contribution" if dm < 0 else "pre-existing or other geometry"))
    return dict(d, sigma=sigma, failed_bits=failed,
        recomputed_decomposition_max_error=discrepancy,
        recomputed_normalization_max_error=normalized_error,
        host_normalized_bit_gaps=[x/sigma for x in host],
        mark_normalized_bit_gaps=[x/sigma for x in mark])


def condition_summary(rows):
    fields = ("native_checked", "q_exact_read", "joint_fixed_q", "h_exact_read",
              "both_exact_read", "native_both_match")
    answer = {field: sum(r[field] for r in rows) for field in fields}
    answer.update(planned_denominator=12, evaluated=len(rows),
        q_bit_errors_total=sum(r["q_bit_errors"] for r in rows),
        h_bit_errors_total=sum(r["h_bit_errors"] for r in rows),
        minimum_fixed_q_score=min((r["decomposition"]["fixed_q_score"] for r in rows), default=None),
        mean_signed_carrier_gain=finite_mean([r["decomposition"]["carrier_gain"] for r in rows]),
        mean_displacement_alignment=finite_mean([r["decomposition"]["displacement_alignment"] for r in rows]),
        mean_signed_alpha=finite_mean([r["decomposition"]["alpha"] for r in rows]),
        mean_signed_host_projection=finite_mean([r["decomposition"]["host_signed_projection"] for r in rows]),
        maximum_gap_decomposition_error=max((r["decomposition"]["recomputed_decomposition_max_error"] for r in rows), default=None),
        failed_bit_descriptions=dict(Counter(bit["description"] for r in rows
            for bit in r["decomposition"]["failed_bits"])),
        failed_bit_count=sum(len(r["decomposition"]["failed_bits"]) for r in rows))
    return answer


def diagnostic(path):
    run = read_json(path / "run.json")
    if run["phase"] != "diagnostic" or sorted(run["sources"]) != sorted(IDS):
        raise ValueError("Diagnostic phase/source inventory differs from fixed protocol")
    rows = read_rows(path / "rows.jsonl")
    indexed = inventory(rows, set(IDS), lambda r: r["source_id"])
    discovery_path = Path(run["config"]["frozen_discovery"])
    discovery = read_rows(discovery_path / "rows.jsonl")
    frozen = inventory([r for r in discovery if r["method"] == "f5"],
        {(sid, c, b) for sid in IDS for c in ("C0", "C1") for b in CONDITIONS},
        lambda r: (r["source_id"], r["control"], r["condition"]))
    output = []
    negatives = []
    for sid in IDS:
        row = indexed.get(sid, dict(source_id=sid, status="not_completed"))
        out = dict(source_id=sid, status=row["status"])
        if row["status"] != "ok":
            out.update(error=row.get("error"), reason=row.get("reason"))
        else:
            if (row["payload"]["original_h_known"] is not False or
                    not row["payload"]["frozen_extraction_confirmed"] or
                    row["payload"]["q"] != row["payload"]["original_semantic_code"]):
                raise ValueError(f"Payload provenance invalid for {sid}")
            out["payload"] = row["payload"]
            out["conditions"] = {}
            for b in CONDITIONS:
                entry = row["conditions"][b]
                result = endpoints(entry["native"], row["payload"])
                result["decomposition"] = decomposition(entry, row["conditions"]["clean"])
                reference = frozen[(sid, "C1", b)]
                result["quality_source"] = reference["quality_source"]
                result["quality_input"] = reference["quality_input"]
                result["recorded_joint_agrees"] = result["joint_fixed_q"] == entry["joint_fixed_q"]
                if not result["recorded_joint_agrees"]:
                    raise ValueError(f"Joint endpoint mismatch for diagnostic {sid}/{b}")
                out["conditions"][b] = result
        output.append(out)
        for b in CONDITIONS:
            for control, owner in (("C0", ALPHA), ("C1", BETA)):
                r = frozen.get((sid, control, b))
                c = r.get("calls", {}).get(owner) if r and r["status"] == "ok" else None
                negatives.append(dict(source_id=sid, condition=b, control=control, owner=owner,
                                      status="ok" if c else "not_completed",
                                      detection=any_detection(c) if c else None))
    conditions = {b: condition_summary([r["conditions"][b] for r in output if r["status"] == "ok"])
                  for b in CONDITIONS}
    clean = [r["conditions"]["clean"] for r in output if r["status"] == "ok"]
    return dict(run_path=str(path), commit=run["commit"], run_outcome=run["outcome"],
        duration_seconds=run.get("duration_seconds"), planned_sources=list(IDS),
        inventory_status=dict(Counter(r["status"] for r in output)), rows=output,
        conditions=conditions, strict_clean_quality=sum(strict_quality(r["quality_source"]) for r in clean),
        baseline_clean_eligibility=sum(strict_quality(r["quality_source"]) and r["both_exact_read"]
                                      and r["native_both_match"] for r in clean),
        negatives=negatives, negative_calls_evaluated=sum(n["status"] == "ok" for n in negatives),
        negative_detections=sum(n["detection"] is True for n in negatives),
        quality_and_negatives_source=str(discovery_path))


def screen(path):
    run = read_json(path / "run.json")
    if run["phase"] != "screen" or sorted(run["sources"]) != sorted(IDS):
        raise ValueError("Screen phase/source inventory differs from fixed protocol")
    planned = {(config, sid) for config in CONFIGS for sid in IDS}
    indexed = inventory(read_rows(path / "rows.jsonl"), planned,
                        lambda r: (r["config"], r["source_id"]))
    output, configurations = [], {}
    for config in CONFIGS:
        crows = []
        for sid in IDS:
            row = indexed.get((config, sid), dict(config=config, source_id=sid, status="not_completed"))
            out = {k: row.get(k) for k in ("config", "source_id", "status", "error", "reason")}
            # Failed evaluations may retain partial conditions; their observations
            # stay available but cannot contribute successful source endpoints.
            out["partial_conditions_retained"] = row.get("conditions") if row["status"] != "ok" else None
            out["refinement"] = row.get("refinement")
            for k in ("evaluation_seconds", "restoration_rms", "final_c1_relative_rms"):
                out[k] = row.get(k)
            if row["status"] == "ok":
                out["payload"] = row["payload"]
                out["conditions"] = {}
                for b in CONDITIONS:
                    entry = row["conditions"][b]
                    result = endpoints(entry["calls"][ALPHA], row["payload"])
                    result["decomposition"] = decomposition(entry, row["conditions"]["clean"])
                    result.update(quality_source=entry["quality_source"], quality_input=entry["quality_input"],
                        negative_c0=any_detection(entry["c0_call"]),
                        negative_wrong_owner=any_detection(entry["calls"][BETA]))
                    if result["joint_fixed_q"] != entry["joint_fixed_q"]:
                        raise ValueError(f"Joint endpoint mismatch: {config}/{sid}/{b}")
                    out["conditions"][b] = result
            crows.append(out)
            output.append(out)
        good = [r for r in crows if r["status"] == "ok"]
        sums = {b: condition_summary([r["conditions"][b] for r in good]) for b in CONDITIONS}
        clean = [r["conditions"]["clean"] for r in good]
        clean_eligible = sum(strict_quality(r["quality_source"]) and r["both_exact_read"]
                             and r["native_both_match"] for r in clean)
        negatives = sum(r["conditions"][b][name] for r in good for b in CONDITIONS
                        for name in ("negative_c0", "negative_wrong_owner"))
        # Keep partial negative calls too. They never rescue incomplete source
        # eligibility, but a failure must not hide an already observed detection.
        partial_negative_calls, partial_negative_detections = 0, 0
        for r in crows:
            for entry in (r.get("partial_conditions_retained") or {}).values():
                calls = [entry.get("c0_call"), entry.get("calls", {}).get(BETA)]
                for call in calls:
                    if call is not None:
                        partial_negative_calls += 1
                        partial_negative_detections += any_detection(call)
        negatives += partial_negative_detections
        eligible = (len(good) == 12 and clean_eligible == 12 and negatives == 0
                    and sums["sd15_vae"]["joint_fixed_q"] == 12
                    and sums["sdxl_vae"]["joint_fixed_q"] >= 11)
        configurations[config] = dict(status_counts=dict(Counter(r["status"] for r in crows)),
            conditions=sums, strict_clean_quality=sum(strict_quality(r["quality_source"]) for r in clean),
            clean_eligible=clean_eligible, negative_detections=negatives,
            negative_calls_evaluated=len(good)*6 + partial_negative_calls, planned_negative_calls=72,
            partial_negative_calls_evaluated=partial_negative_calls,
            survivor=eligible, advancement_status="survivor" if eligible else
                "killed" if len(good) == 12 else "incomplete; not eligible for advancement",
            minimum_reconstructed_fixed_q_score=min((r["conditions"][b]["decomposition"]["fixed_q_score"]
                for r in good for b in CONDITIONS[1:]), default=None),
            mean_clean_lpips=finite_mean([r["quality_source"]["lpips"] for r in clean]),
            attack_input_lpips_proxy_counts={b: {str(limit): sum(r["conditions"][b]["quality_input"]["lpips"] <= limit
                for r in good) for limit in (.30, .20)} for b in CONDITIONS[1:]},
            physical_steps=sum((r.get("refinement") or {}).get("physical_steps", 0) for r in crows),
            logical_steps=sum((r.get("refinement") or {}).get("logical_steps", 0) for r in crows),
            skipped_stationary_steps=sum((r.get("refinement") or {}).get("skipped_stationary_steps", 0) for r in crows))
    ranked = sorted((c for c in CONFIGS if configurations[c]["survivor"]), key=lambda c:
        (-configurations[c]["conditions"]["sdxl_vae"]["joint_fixed_q"],
         -configurations[c]["minimum_reconstructed_fixed_q_score"],
         configurations[c]["mean_clean_lpips"], CONFIGS.index(c)))
    return dict(run_path=str(path), commit=run["commit"], run_outcome=run["outcome"],
        planned_refinements=48, rows=output, configurations=configurations, ranked_survivors=ranked,
        first_continuity_candidate=ranked[0] if ranked else None,
        optimization_seconds=run.get("optimization_seconds"), evaluation_seconds=run.get("evaluation_seconds"),
        duration_seconds=run.get("duration_seconds"),
        physical_steps=sum(c["physical_steps"] for c in configurations.values()),
        logical_steps=sum(c["logical_steps"] for c in configurations.values()),
        planned_logical_steps=4800,
        skipped_stationary_steps=sum(c["skipped_stationary_steps"] for c in configurations.values()))


def f(value):
    return "undefined" if value is None else f"{value:.4f}"


def report(result):
    base = result["diagnostic"]
    lines = ["# Readability diagnostic and bounded screen", "", "Exploratory twelve-source development evidence only. The native frozen detector is unchanged. q_target is the recorded intended semantic payload; h_target is the confirmed saved-clean native-decoded operational instance target. Original embedded h is unknown. No held-out inference, population FPR estimate, independent diffusion claim or official gate transition follows.", "",
        f"Diagnostic `{base['run_path']}` at commit `{base['commit']}`: {base['inventory_status']}; {f(base['duration_seconds'])} seconds. The fixed inventory is twelve unique planned IDs. Failed/missing rows retain the denominator. Earlier protocol-aborted diagnostics are retained elsewhere and are not primary evidence.", "",
        "| Condition | Native checked | Exact intended q + read | Joint exact q + read + content | Native h-target exact + read | Joint q/h exact + read | Min fixed-q score |", "|---|---:|---:|---:|---:|---:|---:|"]
    for b, s in base["conditions"].items():
        lines.append(f"| {b} | {s['native_checked']}/12 | {s['q_exact_read']}/12 | {s['joint_fixed_q']}/12 | {s['h_exact_read']}/12 | {s['both_exact_read']}/12 | {f(s['minimum_fixed_q_score'])} |")
    lines += ["", f"Reused unchanged-pixel quality: strict PSNR >35 dB, SSIM >.9, LPIPS <.1 on {base['strict_clean_quality']}/12. Full new clean eligibility (quality, both native reads, exact declared q/h and both_match): {base['baseline_clean_eligibility']}/12. Negative any-channel detections: {base['negative_detections']}/{base['negative_calls_evaluated']} calls (36 C0 alpha and 36 C1 beta across three conditions, reusing twelve sources). Quality/negative source: `{base['quality_and_negatives_source']}`.", "",
        "Normalized correlation is dot(w,p)/norm(p), with 320 chips. Bit gaps are correct-minus-alternative dot products; normalized gaps divide by sigma=max(norm(p)/sqrt(320),1e-8). Alpha is signed dot(w,p-b)/320; carrier gain divides by clean alpha and preserves sign. Host and mark gap components sum to the observed gap; they are an exact measured finite-difference decomposition, not a causal or linear-VAE model. A searched score above threshold can coexist with wrong q.", "",
        "| Source | Condition | q errors | h errors | q_bound | Fixed-q / searched score | Signed gain | Alignment | Minimum gap |", "|---|---|---:|---:|---|---:|---:|---:|---:|"]
    for r in base["rows"]:
        if r["status"] != "ok":
            lines.append(f"| {r['source_id']} | {r['status']} | unresolved | unresolved | — | — | — | — | — |")
            continue
        for b, c in r["conditions"].items():
            d = c["decomposition"]
            lines.append(f"| {r['source_id']} | {b} | {c['q_bit_errors']} | {c['h_bit_errors']} | {c['native_q_bound']} | {f(d['fixed_q_score'])} / {f(c['native_semantic']['decoded_score'])} | {f(d['carrier_gain'])} | {f(d['displacement_alignment'])} | {f(d['minimum_bit_gap'])} |")
    lines += ["", "## Failed bit geometry", "", "Bit indices follow the recorded 0–31 segment order. Changes below compare with the same source's clean intended-q geometry. Negative observed gaps explain the selected alternative descriptively; a clean error need not be newly caused by a reconstruction. All raw and normalized gaps, native flags, q_now/h_now and q_bound are retained in the JSON.", "", "| Source / condition / bit | Host gap | Mark gap | Observed gap | Host change | Mark change | Descriptive change |", "|---|---:|---:|---:|---:|---:|---|"]
    for r in base["rows"]:
        for b, c in r.get("conditions", {}).items():
            for bit in c["decomposition"]["failed_bits"]:
                lines.append(f"| {r['source_id']} / {b} / {bit['bit_index']} | {f(bit['host_gap'])} | {f(bit['mark_gap'])} | {f(bit['observed_gap'])} | {f(bit['host_gap_change_from_clean'])} | {f(bit['mark_gap_change_from_clean'])} | {bit['description']} |")
    for b, s in base["conditions"].items():
        lines += ["", f"{b}: mean signed alpha {f(s['mean_signed_alpha'])}, mean signed host projection {f(s['mean_signed_host_projection'])}, mean signed carrier gain {f(s['mean_signed_carrier_gain'])}, mean displacement alignment {f(s['mean_displacement_alignment'])}; {s['failed_bit_count']} nonpositive gaps, {s['q_bit_errors_total']} decoded q errors across 384 bits. Failed-gap descriptions: {s['failed_bit_descriptions']}. Maximum independently recomputed host-plus-mark gap discrepancy {s['maximum_gap_decomposition_error']}. These geometry averages are descriptive and do not rank population robustness."]
    scr = result.get("screen")
    lines += ["", "## R1–R4 screen", ""]
    if scr is None:
        lines += ["Screen not supplied to this analysis. All 48 planned source/configuration identities remain not evaluated here; no survivor or candidate ranking is asserted. Re-run this same script with --screen-run after completion."]
    else:
        lines += [f"Run `{scr['run_path']}` at `{scr['commit']}`: {scr['run_outcome']}.", "", "| Config | Status counts (12 planned) | Strict quality | Clean eligible | SD1.5 joint | SDXL joint | Negative detections / evaluated | Advancement |", "|---|---|---:|---:|---:|---:|---:|---|"]
        for config, s in scr["configurations"].items():
            lines.append(f"| {config} | {s['status_counts']} | {s['strict_clean_quality']}/12 | {s['clean_eligible']}/12 | {s['conditions']['sd15_vae']['joint_fixed_q']}/12 | {s['conditions']['sdxl_vae']['joint_fixed_q']}/12 | {s['negative_detections']} / {s['negative_calls_evaluated']} | {s['advancement_status']} |")
        lines += ["", f"Ranked survivors: {scr['ranked_survivors']}. Rank order is SDXL joint exact count, minimum reconstructed fixed-q score, lower mean clean LPIPS, then R1–R4 order. A VAE-screen survivor still requires matched T3 continuity and T4/T5/delivered-binding follow-up; this report cannot promote a final method.", "", f"Measured physical steps: {scr['physical_steps']}; accounted logical steps: {scr['logical_steps']}/4800; skipped stationary steps: {scr['skipped_stationary_steps']}. Active optimization {f(scr['optimization_seconds'])} s; evaluation {f(scr['evaluation_seconds'])} s; invocation wall duration {f(scr['duration_seconds'])} s. Resumed wall durations may exclude earlier invocations; active counters are cumulative. Proxy LPIPS <=.30/<=.20 subsets retain twelve-source denominators in JSON; human admissibility remains missing."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic-run", required=True, type=Path)
    parser.add_argument("--screen-run", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research/journal-upgrade-20261009")
    args = parser.parse_args()
    result = dict(schema="journal-readability-analysis-v1", diagnostic=diagnostic(args.diagnostic_run),
                  screen=screen(args.screen_run) if args.screen_run else None)
    if result["screen"]:
        targets = {r["source_id"]: r["payload"] for r in result["diagnostic"]["rows"] if r["status"] == "ok"}
        for row in result["screen"]["rows"]:
            if row["status"] == "ok":
                target = targets.get(row["source_id"])
                if target is None or any(row["payload"][tier] != target[tier] for tier in ("q", "h")):
                    raise ValueError("Screen target differs from definitive diagnostic")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "readability-statistics.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (args.output_dir / "readability-results.md").write_text(report(result), encoding="utf-8")
    print(json.dumps(dict(diagnostic={b: s["joint_fixed_q"] for b, s in result["diagnostic"]["conditions"].items()},
                          screen_survivors=result["screen"]["ranked_survivors"] if result["screen"] else None)))


if __name__ == "__main__":
    main()

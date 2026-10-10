"""Fixed F5-RC1 T3 development measurement; reused controls are not replicates."""
from __future__ import annotations

import time
IMPORT_STARTED = time.monotonic()

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from journal_vae_probe import Evaluator, F5_RUN, write
from journal_readability_probe import IDS, load
from journal_read_conditioning_probe import read_rows, screen_summary, binding_summary, CONFIGS
from f4_transfer_probe import MAIN, ASSETS, SOURCES
from f5_gate import OWNERS, V5_RESULTS
from scripts import journal_read_conditioning as rc

STRENGTHS = (.1, .2)
SEEDS = (0, 1, 2)
CAP = 5400.
SCREEN = MAIN / ".thesis-build/dev-runs/20261010-1035-rc-screen"
BINDING = MAIN / ".thesis-build/dev-runs/20261010-1040-rc-binding"
D2_PRIOR = MAIN / ".thesis-build/dev-runs/20261010-1051-rc3-t3"
D2_CAP = 1800.
D2_DESCRIPTIVE_CAP = 900.
D2_WRITER = MAIN / ".thesis-build/dev-runs/20261010-1212-native-writer"
D2_WRITER_COMMIT = "569f4835dd5a1ddd4282a078ea46d82f583ecc84"
GPU_CAP_BYTES = 10 * 1024**3


def d2_prerequisites(screen, binding, prior_path, descriptive=False):
    from journal_native_writer import summarize as writer_summary
    from journal_binding_probe import pairs, ARMS
    sr = json.loads((screen / "run.json").read_text(encoding="utf-8"))
    rows = read_rows(screen / "rows.jsonl")
    if (len(rows) != 12 or {r.get("source_id") for r in rows} != set(IDS) or
            any(r.get("status") != "ok" or r.get("config") != "D2" for r in rows)):
        raise ValueError("D2 requires the exact twelve unique completed writer sources")
    for row in rows:
        sid = row["source_id"]
        if (row.get("source_image") != str(SOURCES[sid]) or
                Path(row["conditions"]["clean"]["image"]).resolve() !=
                (screen / "images" / f"D2-{sid}-C1-clean.png").resolve()):
            raise ValueError("D2 source/clean-image paths differ from fixed writer output")
    counts = writer_summary(rows)
    if (sr.get("schema") != "journal-native-writer-v1" or
            sr.get("config", {}).get("candidate") != "D2" or sr.get("outcome") != "completed" or
            not 0 <= float(sr["duration_seconds"]) <= 3300 or sr.get("budget_overrun") or
            (not descriptive and not counts["prerequisite_pass"])):
        raise ValueError("D2 writer must independently pass all clean/VAE prerequisites within 3300 seconds")
    if descriptive:
        if (screen.resolve() != D2_WRITER.resolve() or sr.get("commit") != D2_WRITER_COMMIT or
                sr.get("data_split") != "development" or sr.get("usd") != 0 or
                sr.get("sources") != list(IDS) or sr.get("seeds") != list(SEEDS) or
                counts["prerequisite_pass"] or counts["strict_clean_quality"] != 12 or
                counts["clean_exact_q_h_both_match"] != 12 or counts["final_feasible"] != 12 or
                counts["joint_fixed_q"] != dict(clean=12, sd15_vae=12, sdxl_vae=10) or
                counts["c0_any"] != 0 or counts["wrong_owner_any"] != 0):
            raise ValueError("Descriptive D2 requires the frozen 569f483 writer and retained failed SDXL prerequisite")
    # These panels establish unchanged decoder compatibility, not new-writer T4 efficacy.
    cached = read_rows(SCREEN / "rows.jsonl")
    cr = json.loads((SCREEN / "run.json").read_text(encoding="utf-8"))
    compatibility = [r for r in cached if r.get("arm") == "frozen_clean_compatibility"]
    br = json.loads((binding / "run.json").read_text(encoding="utf-8"))
    binding_rows = read_rows(binding / "rows.jsonl")
    expected = {(d, r, arm) for d, r in pairs() for arm in ARMS} | {(*pairs()[0], "public_recipient_authorization_demo")}
    actual = [(r["donor_id"], r["recipient_id"], r["arm"]) for r in binding_rows]
    if (len(compatibility) != 12 or {r["source_id"] for r in compatibility} != set(IDS) or
            any(r.get("status") != "ok" or
                r["calls"]["combined"]["outcome"] != "both_match" for r in compatibility) or
            len(actual) != 31 or set(actual) != expected or
            any(r.get("status") != "ok" for r in binding_rows)):
        raise ValueError("D2 requires unchanged twelve decoder checks and exact 31-row cached binding panel")
    bc = binding_summary(binding_rows)
    if (binding.resolve() != BINDING.resolve() or cr.get("method") != "F5-RC1" or
            cr.get("phase") != "screen" or br.get("method") != "F5-RC1" or
            br.get("phase") != "cached-binding" or
            any(r.get("outcome") != "completed" or r.get("budget_overrun") for r in (cr, br)) or
            float(cr["duration_seconds"])+float(br["duration_seconds"]) > 1800 or not bc["continuity_pass"]):
        raise ValueError("Unchanged cached decoder/binding prerequisites do not pass")
    if prior_path is None or prior_path.resolve() != D2_PRIOR.resolve():
        raise ValueError("D2 requires the fixed completed RC3 T3 run as shared evidence")
    prior = json.loads((prior_path / "run.json").read_text(encoding="utf-8"))
    if (prior.get("schema") != "journal-rc-t3-v1" or prior.get("method") != "F5-RC1" or
            prior.get("config", {}).get("candidate") != "RC3" or prior.get("outcome") != "completed" or
            prior.get("screen_run") != str(SCREEN) or prior.get("binding_run") != str(binding)):
        raise ValueError("D2 shared evidence must be completed RC3 with unchanged decoder prerequisites")
    return rows, counts, dict(cached_binding=bc, frozen_clean_compatibility=screen_summary(cached)["frozen_clean_compatibility"],
        scope="unchanged decoder cached evidence; not D2 writer T4/T5 qualification"), prior


def identity(row):
    return (int(row["source_id"]), float(row["strength"]), int(row["seed"]))


def key_text(key):
    return f"{key[0]}|{key[1]}|{key[2]}"


def endpoint(call, payload):
    s, h = call["semantic"], call["instance"]
    q_exact = bool(s["read"] and s["decoded_code"] == payload["q"])
    h_exact = bool(h["read"] and h["decoded_code"] == payload["h"])
    success = bool(s["found"] and s["content_match"])
    return dict(A=bool(s["found"] or h["found"]), S=success,
        R=bool(s["read"]), C=bool(s["read"] and s["content_match"]),
        Q=q_exact, J=bool(q_exact and s["content_match"]),
        U=bool(success and not s["read"]), H=h_exact, D=q_exact and h_exact,
        F=call["outcome"] == "both_match",
        q_bit_errors=None if not s["read"] or s.get("decoded_code") is None else
            (int(s["decoded_code"], 16) ^ int(payload["q"], 16)).bit_count(),
        h_bit_errors=None if not h["read"] or h.get("decoded_code") is None else
            (int(h["decoded_code"], 16) ^ int(payload["h"], 16)).bit_count(),
        signed_bit_margins={tier: {key: value for key, value in call[tier].items()
            if key in ("signed_bit_margins", "bit_margins", "bit_scores")}
            for tier in ("semantic", "instance")})


def paired_calls(ev, rgb):
    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
    new, native = {}, {}
    for owner in OWNERS:
        new[owner] = rc.detect_rgb(rgb, latent, owner, ev.profile, features,
            binding="soft", roster_size=1)
        old = ev.detect(rgb, "f5", owner, features, latent)
        # Preserve native routing and own-h status which frozen code does not expose.
        semantic = old["semantic"]
        use_read = semantic["found"] and semantic["content_status"] != "match"
        old["native_q_bound"] = semantic["decoded_code"] if use_read else old["semantic_code"]
        old["native_q_bound_rule"] = "decoded_q_on_found_content_nonmatch_else_suspect_q"
        limits = ev.profile["decision"]
        old["instance_own_content_status"] = rc.base._content_status(
            old["instance"]["corrected_distance"], int(limits["instance_radius"]),
            int(limits["instance_mismatch_distance"]), True) if old["instance"]["found"] else None
        native[owner] = old
    return new, native


def prerequisites(screen, binding, config, prior_path):
    sr = json.loads((screen / "run.json").read_text(encoding="utf-8"))
    br = json.loads((binding / "run.json").read_text(encoding="utf-8"))
    rows = read_rows(screen / "rows.jsonl")
    expected = {(c, sid) for c in CONFIGS for sid in IDS}
    actual = [(r.get("config"), r.get("source_id")) for r in rows if "config" in r]
    compatibility = [r for r in rows if r.get("arm") == "frozen_clean_compatibility"]
    if len(actual) != 24 or set(actual) != expected or len(compatibility) != 12 or {r["source_id"] for r in compatibility} != set(IDS):
        raise ValueError("Cached screen must contain the exact 36 unique planned rows")
    from journal_binding_probe import pairs, ARMS
    binding_rows = read_rows(binding / "rows.jsonl")
    expected_binding = {(d, r, arm) for d, r in pairs() for arm in ARMS} | {(*pairs()[0], "public_recipient_authorization_demo")}
    actual_binding = [(r["donor_id"], r["recipient_id"], r["arm"]) for r in binding_rows]
    if len(actual_binding) != 31 or set(actual_binding) != expected_binding:
        raise ValueError("Binding requires all 31 exact unique planned rows")
    counts, bc = screen_summary(rows), binding_summary(binding_rows)
    if sr.get("method") != "F5-RC1" or br.get("method") != "F5-RC1" or sr.get("phase") != "screen" or br.get("phase") != "cached-binding":
        raise ValueError("Prerequisite method/phase mismatch")
    if sr["outcome"] != "completed" or br["outcome"] != "completed" or any(r["status"] != "ok" for r in rows+binding_rows):
        raise ValueError("Both cached panels must finish without missing/failed rows")
    if float(sr["duration_seconds"])+float(br["duration_seconds"]) > 1800 or sr.get("budget_overrun") or br.get("budget_overrun"):
        raise ValueError("Cached stage exceeded its independent 1800-second cap")
    if not bc["continuity_pass"] or not counts[config]["survivor"]:
        raise ValueError("Candidate is not eligible under independently recomputed prerequisites")
    prior = None
    if prior_path:
        prior = json.loads((prior_path / "run.json").read_text(encoding="utf-8"))
        if prior.get("schema") != "journal-rc-t3-v1" or prior.get("config", {}).get("candidate") != "RC2" or config != "RC3":
            raise ValueError("Only RC3 may reuse an earlier RC2 T3 panel")
        if prior.get("screen_run") != str(screen) or prior.get("binding_run") != str(binding):
            raise ValueError("Prior run must have identical prerequisites")
        if prior["outcome"] != "completed" or prior["summary"]["measured_t3_continuity_pass"]:
            raise ValueError("RC3 follows only a completed failing RC2 T3 grid")
    elif counts["ranked_survivors"][0] != config:
        raise ValueError("Run the first pre-ranked survivor before its alternate")
    return rows, counts, bc, prior


def frozen_sets():
    rows = [r for r in read_rows(F5_RUN / "rows.jsonl") if r.get("dose") == "diffusion" and r.get("strength") in STRENGTHS]
    expected = {(sid, s, seed) for sid in IDS for s in STRENGTHS for seed in SEEDS}
    lookup = {}
    for control in ("C0", "C1"):
        selected = [r for r in rows if r["control"] == control]
        if len(selected) != 72 or {identity(r) for r in selected} != expected:
            raise ValueError("Frozen T3 grid must contain all fixed identities, including blocks")
        if any(r["outcome"] not in ("completed", "safety_blocked") for r in selected):
            raise ValueError("Frozen rows must preserve completions and genuine safety blocks, not failed rows")
        lookup[control] = {identity(r): r for r in selected}
    v5 = {}
    for r in json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"]:
        if r.get("axis") == "T3" and r.get("control") == "C1" and r.get("dose") == "diffusion" and r.get("strength") in STRENGTHS and r.get("status") == "metrics_complete":
            c = next(d["result"] for d in r["detections"] if d["claimed_owner"] == OWNERS[0] and d["binding_mode"] == "combined")
            if identity(r) in v5:
                raise ValueError("Duplicate v5 comparison identity")
            v5[identity(r)] = bool(c["semantic"]["found"] and c["semantic"]["content_match"])
    sets = {}
    for s, n, successes in ((.1, 29, 27), (.2, 28, 18)):
        f = {k for k, r in lookup["C1"].items() if k[1] == s and r["outcome"] == "completed"}
        i = f & set(v5)
        if len(f) != 35 or len(i) != n or sum(v5[k] for k in i) != successes:
            raise ValueError("Retained comparator identities/counts differ from frozen mapping")
        if not all(lookup["C1"][k]["calls"][OWNERS[0]]["semantic_found"] and
                   lookup["C1"][k]["calls"][OWNERS[0]]["semantic_content_match"] for k in f):
            raise ValueError("Retained frozen F5 requires semantic success on all 35 completed identities")
        if sum(r["outcome"] == "completed" for k, r in lookup["C0"].items() if k[1] == s) != 33:
            raise ValueError("Expected 33 retained C0 completions per strength")
        sets[str(s)] = dict(P=sorted(k for k in expected if k[1] == s), F=sorted(f), I=sorted(i))
    return lookup, v5, sets


def summarize(rows, sets, v5, budget_overrun=False):
    alpha = OWNERS[0]
    candidate = {identity(r): r for r in rows if r["arm"] == "candidate_C1"}
    frozen = {identity(r): r for r in rows if r["arm"] == "frozen_C1_enrichment"}
    result = {"strengths": {}}
    discrepancies = [key_text(identity(r)) for r in frozen.values() if r.get("status") == "ok" and r["old_S"] != r["endpoints"]["native"]["S"]]
    for s in STRENGTHS:
        declared = sets[str(s)]
        p, f, i = (list(map(tuple, declared[k])) for k in ("P", "F", "I"))
        good = {k: r for k, r in candidate.items() if k[1] == s and r["status"] == "ok"}
        old_good = {k: r for k, r in frozen.items() if k[1] == s and r["status"] == "ok"}
        counts = {e: sum(r["endpoints"]["rc"][e] for r in good.values()) for e in ("A", "S", "R", "C", "Q", "J", "U", "H", "D", "F")}
        retention = {}
        for e in ("Q", "J", "C", "R"):
            positives = [k for k in f if k in old_good and old_good[k]["endpoints"]["native"][e]]
            lost = [k for k in positives if k not in good or not good[k]["endpoints"]["rc"][e]]
            gained = [k for k in f if k in old_good and not old_good[k]["endpoints"]["native"][e] and k in good and good[k]["endpoints"]["rc"][e]]
            retention[e] = dict(frozen_positive=len(positives), retained=len(positives)-len(lost), lost=list(map(key_text, lost)), gained=list(map(key_text, gained)))
        paired = []
        for k in p:
            r, old = good.get(k), old_good.get(k)
            paired.append(dict(identity=key_text(k), in_frozen_completed=k in f, in_frozen_intersection=k in i,
                candidate_status=candidate.get(k, {}).get("status", "missing"), v5_S=v5.get(k),
                frozen_native=None if old is None else old["endpoints"]["native"],
                frozen_RC=None if old is None else old["endpoints"]["rc"],
                candidate_RC=None if r is None else r["endpoints"]["rc"],
                candidate_native=None if r is None else r["endpoints"]["native"]))
        intersection_success=sum(k in good and good[k]["endpoints"]["rc"]["S"] for k in i)
        historical_pass=intersection_success == len(i) and intersection_success > sum(v5[k] for k in i)
        exact_pass=len(old_good) == len(f) and not any(retention[e]["lost"] for e in ("Q", "J"))
        result["strengths"][str(s)] = dict(planned=36, completed=len(good),
            blocked=sum(r["status"] == "safety_blocked" for k, r in candidate.items() if k[1] == s),
            failed=sum(r["status"] == "failed" for k, r in candidate.items() if k[1] == s),
            missing=36-sum(k[1] == s for k in candidate), successes=counts,
            endpoint_denominators=dict(planned=36, completed=len(good)), frozen_completed=len(f), frozen_enriched=len(old_good),
            intersection=dict(fixed_identities=len(i), candidate_S=intersection_success, v5_S=sum(v5[k] for k in i), frozen_S=len(i)),
            full_frozen_endpoints={e:sum(r["endpoints"]["native"][e] for r in old_good.values()) for e in counts},
            candidate_on_frozen_completed={e:sum(k in good and good[k]["endpoints"]["rc"][e] for k in f) for e in counts},
            retention=retention, paired_identities=paired, historical_semantic_continuity_pass=historical_pass,
            enriched_exact_q_continuity_pass=exact_pass)
    negatives = {}
    for method in ("rc", "native"):
        observed = errors = c0_observed = wrong_observed = 0
        for r in rows:
            if r.get("status") != "ok" or r["arm"] not in ("shared_C0", "candidate_C1"):
                continue
            owners=OWNERS if r["arm"] == "shared_C0" else OWNERS[1:]
            calls=r["calls"] if method == "rc" else r["native_calls"]
            observed += len(owners)
            c0_observed += len(owners) if r["arm"] == "shared_C0" else 0
            wrong_observed += len(owners) if r["arm"] == "candidate_C1" else 0
            errors += sum(bool(calls[o]["semantic"]["found"] or calls[o]["instance"]["found"]) for o in owners)
        negatives[method]=dict(planned=504, observed=observed, any_detections=errors,
            c0_planned=288,c0_observed=c0_observed,c0_retained_blocked_call_slots=24,
            wrong_owner_planned=216,wrong_owner_observed=wrong_observed, unavailable=504-observed,
            scope="paired decoder rules on reused suspects; not independent samples or validated population FPR")
    candidate_available=sum(r["status"] == "ok" for r in candidate.values())
    expected_observed=264+3*candidate_available
    candidate_grid_recorded=(len(candidate) == 72 and all(r["status"] in ("ok", "safety_blocked") for r in candidate.values()))
    result.update(negatives=negatives, frozen_S_discrepancies=discrepancies,
        observed_negative_pass=negatives["rc"]["any_detections"] == 0,
        negative_panel_available_complete=negatives["rc"]["observed"] == expected_observed and negatives["rc"]["c0_observed"] == 264,
        expected_observed_negative_calls=expected_observed,
        exhaustive_planned_negative_panel=negatives["rc"]["observed"] == 504,
        candidate_grid_recorded_without_operational_failures=candidate_grid_recorded,
        budget_overrun=budget_overrun, literal_T5_attribution_status="not evaluable in inherited all-alpha/source-blind design",
        complete_amendment_gate="not granted by T3 adapter")
    result["measured_t3_continuity_pass"] = (not budget_overrun and not discrepancies and
        result["observed_negative_pass"] and result["negative_panel_available_complete"] and
        candidate_grid_recorded and all(x["historical_semantic_continuity_pass"] and x["enriched_exact_q_continuity_pass"] for x in result["strengths"].values()))
    return result


def descriptive_summary(summary, outcome, gpu_peak):
    """Fixed interpretation only; failed writer eligibility is never restored."""
    summary["descriptive_measured_t3_continuity_pass"] = summary["measured_t3_continuity_pass"]
    summary["measured_t3_continuity_pass"] = False
    summary.update(scientific_status="descriptive_D2_ineligible",
        writer_prerequisite_pass=False, candidate_eligible=False,
        m1a_status="not evaluable; failed SDXL prerequisite and unmeasured T4/T5",
        gpu_budget_overrun=gpu_peak is not None and gpu_peak > GPU_CAP_BYTES)
    complete = (outcome == "completed" and not summary["budget_overrun"] and
        gpu_peak is not None and not summary["gpu_budget_overrun"] and
        summary["candidate_grid_recorded_without_operational_failures"] and
        summary["negative_panel_available_complete"] and not summary["frozen_S_discrepancies"] and
        all(x["frozen_enriched"] == x["frozen_completed"] for x in summary["strengths"].values()))
    signal = (complete and summary["strengths"]["0.2"]["successes"]["J"] > 20 and
        all(not x["retention"][e]["lost"] for x in summary["strengths"].values() for e in ("Q", "J")) and
        all(summary["strengths"][str(s)]["intersection"]["candidate_S"] == n
            for s, n in ((.1, 29), (.2, 28))) and
        all(n["any_detections"] == 0 for n in summary["negatives"].values()))
    summary["diagnostic_interpretation"] = ("incomplete_with_errors" if not complete else
        "signal_worth_preserving" if signal else "no_strict_continuity_improvement")
    summary["interpretation_scope"] = "In-sample descriptive diffusion endpoint; SDXL prerequisite still failed; no candidate promotion"
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, choices=(*CONFIGS, "D2"))
    parser.add_argument("--descriptive-d2", action="store_true")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--screen-run", type=Path, default=SCREEN)
    parser.add_argument("--binding-run", type=Path, default=BINDING)
    parser.add_argument("--prior-run", type=Path)
    args=parser.parse_args()
    if args.descriptive_d2 and args.config != "D2":
        parser.error("--descriptive-d2 requires --config D2")
    invocation_started=IMPORT_STARTED if args.descriptive_d2 else time.monotonic()
    d2 = args.config == "D2"
    check = d2_prerequisites if d2 else prerequisites
    cached, qualification, compatibility, prior = (check(args.screen_run,args.binding_run,args.prior_run,descriptive=args.descriptive_d2) if d2 else
        check(args.screen_run,args.binding_run,args.config,args.prior_run))
    cap = D2_DESCRIPTIVE_CAP if args.descriptive_d2 else D2_CAP if d2 else CAP
    old, v5, sets=frozen_sets()  # Freeze old comparison identities before any candidate call.
    lookup={r["source_id"]:r for r in cached if r.get("config") == args.config}
    shared={}
    if prior:
        if prior.get("frozen_run") != str(F5_RUN) or prior.get("v5_results") != str(V5_RESULTS) or prior.get("comparison_sets") != json.loads(json.dumps(sets)):
            raise ValueError("Prior frozen pixel origin or fixed comparison identities differ")
        for r in read_rows(args.prior_run/"rows.jsonl"):
            if r["arm"] in ("frozen_C1_enrichment", "shared_C0"):
                k=(r["arm"], identity(r))
                if k in shared:
                    raise ValueError("Duplicate prior shared identity")
                shared[k]=r
        expected={("frozen_C1_enrichment",k) for k,r in old["C1"].items() if r["outcome"] == "completed"}|{("shared_C0",k) for k in old["C0"]}
        if set(shared) != expected or any(r["status"] != "ok" for r in shared.values() if r["arm"] == "frozen_C1_enrichment"):
            raise ValueError("Prior shared enrichment/C0 panel incomplete")
        for (arm,k),r in shared.items():
            source=old["C0" if arm == "shared_C0" else "C1"][k]
            expected_status="ok" if source["outcome"] == "completed" else "safety_blocked"
            if r["status"] != expected_status:
                raise ValueError("Prior shared status mismatch")
            if r.get("payload") != lookup[k[0]]["payload"] or r.get("source_record") != str(F5_RUN/"rows.jsonl"):
                raise ValueError("Prior shared target/source metadata differs")
            if expected_status == "ok" and r.get("image") != source["image"]["path"]:
                raise ValueError("Prior shared suspect path differs")
    evidence_prior_seconds=0. if prior is None else float(prior["shared_duration_seconds"])
    prior_seconds=0. if d2 else evidence_prior_seconds
    started=invocation_started if d2 else time.monotonic()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/"images").mkdir()
    record=dict(schema="journal-rc-t3-v1",method="F5-RC1",routing_revision=1,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=sys.argv,
        config=dict(candidate=args.config,writer_config="D2" if d2 else CONFIGS[args.config],owners=list(OWNERS),semantic_views=7,
            roster_size=1,binding="soft",shared_active_seconds_cap=cap),seeds=list(SEEDS),strengths=list(STRENGTHS),
        data_split="development",usd=0,screen_run=str(args.screen_run),binding_run=str(args.binding_run),
        prior_run=None if args.prior_run is None else str(args.prior_run),prior_active_seconds=prior_seconds,
        shared_evidence_prior_duration_seconds=evidence_prior_seconds,
        budget_scope="fresh D2 official T3 and summaries only; inherited RC3 evidence cost excluded" if d2 else "shared RC T3 active time",
        frozen_run=str(F5_RUN),v5_results=str(V5_RESULTS),comparison_sets=sets,
        qualification=qualification,compatibility=compatibility,outcome="running",
        scientific_status="exploratory paired development continuity; not an official lifecycle verdict",
        fpr_status="legacy bounds unvalidated for routed system",human_visual_verdict=None,
        attack="pinned SD1.5 DDIM img2img; 20 steps; empty prompts; CFG 1; eta 0; retained RGB conversion and safety checks")
    if args.descriptive_d2:
        record.update(scientific_status="descriptive_D2_ineligible", writer_prerequisite_pass=False,
            candidate_eligible=False, writer_commit=D2_WRITER_COMMIT,
            budget_scope="900 seconds inclusive of imports, prerequisite validation, fresh attacks and final summaries; inherited evidence cost excluded",
            gpu_allocated_cap_bytes=GPU_CAP_BYTES, planned_candidate_calls=72, planned_shared_rows=142)
    rows=[]
    write(args.output_dir/"run.json",record)
    plan=[("frozen_C1_enrichment",k) for k,r in old["C1"].items() if r["outcome"] == "completed"]
    plan += [("shared_C0",k) for k in old["C0"]]
    plan += [("candidate_C1",(sid,s,seed)) for sid in IDS for s in STRENGTHS for seed in SEEDS]

    def current_summary():
        summary = summarize(rows,sets,v5,record["shared_duration_seconds"]>cap)
        return descriptive_summary(summary, record["outcome"], record.get("gpu_peak_allocated_bytes")) if args.descriptive_d2 else summary

    def emit(row):
        rows.append(row)
        with (args.output_dir/"rows.jsonl").open("a",encoding="utf-8") as handle:
            handle.write(json.dumps(row,allow_nan=False)+"\n")
        record["duration_seconds"]=time.monotonic()-started
        record["shared_duration_seconds"]=prior_seconds+record["duration_seconds"]
        record["summary"]=current_summary()
        write(args.output_dir/"summary.json",record["summary"])
        write(args.output_dir/"run.json",record)
        print(json.dumps({k:row[k] for k in ("arm","source_id","strength","seed","status")}),flush=True)

    ev=pipe=None
    try:
        from PIL import Image
        import numpy as np
        if args.descriptive_d2:
            import torch
            torch.cuda.set_per_process_memory_fraction(min(1., GPU_CAP_BYTES / torch.cuda.get_device_properties(0).total_memory))
            torch.cuda.reset_peak_memory_stats()
        ev=Evaluator()
        record["profile"]=ev.profile
        for arm,k in plan:
            tick=time.monotonic()
            sid,s,seed=k
            row=dict(arm=arm,source_id=sid,strength=s,seed=seed)
            try:
                if args.descriptive_d2 and ev.torch.cuda.max_memory_allocated() > GPU_CAP_BYTES:
                    raise RuntimeError("Descriptive D2 10-GiB peak allocated GPU cap exceeded")
                if prior_seconds+time.monotonic()-started >= cap:
                    raise RuntimeError(f"{'Fresh D2 official T3' if d2 else 'Shared RC T3/T4/T5/synthesis'} {cap:g}-second cap exhausted")
                if (arm,k) in shared:
                    row=dict(shared[(arm,k)],shared_origin=str(args.prior_run/"rows.jsonl"),
                        reuse_interpretation="exact same frozen pixels/method/targets; shared evidence, not replicate")
                    row["original_duration_seconds"]=row.get("duration_seconds")
                else:
                    payload=lookup[sid]["payload"]
                    row["payload"]=payload
                    if arm == "candidate_C1":
                        if pipe is None:
                            pipe=ev.models.load_regenerator(ASSETS)
                        mark_path=lookup[sid]["conditions"]["clean"]["image"]
                        with ev.torch.inference_mode():
                            result=pipe(prompt="",negative_prompt="",image=Image.fromarray(load(mark_path)),strength=s,
                                num_inference_steps=20,eta=0.,guidance_scale=1.,
                                generator=ev.torch.Generator(device="cuda").manual_seed(seed),
                                num_images_per_prompt=1,output_type="pil",return_dict=True)
                        rgb=np.asarray(ev.models.validate_generated(result),np.uint8)
                        path=args.output_dir/"images"/f"{args.config}-{sid}-{s}-{seed}.png"
                        Image.fromarray(rgb).save(path)
                        rgb=load(path)
                        row.update(image=str(path),marked_input=mark_path,target_source_record=str(args.screen_run/"rows.jsonl"),
                            quality_input=ev.metrics(load(mark_path),rgb),
                            quality_source=ev.metrics(load(SOURCES[sid]),rgb),
                            quality_interpretation="descriptive attack distortion; no filtering or added quality gate",
                            human_admissibility_verdict=None)
                    else:
                        source=old["C0" if arm == "shared_C0" else "C1"][k]
                        row.update(source_record=str(F5_RUN/"rows.jsonl"),retained_outcome=source["outcome"])
                        if source["outcome"] != "completed":
                            row.update(status="safety_blocked",error=source.get("error"),reuse_interpretation="retained C0 block; no retry, no synthetic negative")
                            row["duration_seconds"]=time.monotonic()-tick
                            emit(row)
                            continue
                        row["image"]=source["image"]["path"]
                        rgb=load(row["image"])
                        if arm == "frozen_C1_enrichment":
                            c=source["calls"][OWNERS[0]]
                            row["old_S"]=bool(c["semantic_found"] and c["semantic_content_match"])
                    if args.descriptive_d2 and ev.torch.cuda.max_memory_allocated() > GPU_CAP_BYTES:
                        raise RuntimeError("Descriptive D2 10-GiB peak allocated GPU cap exceeded")
                    new,native=paired_calls(ev,rgb)
                    row.update(calls=new,native_calls=native,status="ok")
                    if arm != "shared_C0":
                        row["endpoints"]={"rc":endpoint(new[OWNERS[0]],payload),"native":endpoint(native[OWNERS[0]],payload)}
            except Exception as error:
                row.update(status="safety_blocked" if "safety_checker_blocked_output" in str(error) else "failed",error=traceback.format_exc())
                ev.torch.cuda.empty_cache()
            row["duration_seconds"]=time.monotonic()-tick
            emit(row)
        record["outcome"]="completed" if all(r["status"] in ("ok","safety_blocked") for r in rows) else "completed_with_failures"
        record["gpu_peak_allocated_bytes"]=ev.torch.cuda.max_memory_allocated()
    except Exception:
        record.update(outcome="failed",error=traceback.format_exc())
        for arm,k in plan[len(rows):]:
            emit(dict(arm=arm,source_id=k[0],strength=k[1],seed=k[2],status="failed",error="Fatal/setup failure; see run.json",duration_seconds=0.))
        raise
    finally:
        record["duration_seconds"]=time.monotonic()-started
        record["shared_duration_seconds"]=prior_seconds+record["duration_seconds"]
        record["remaining_active_seconds"]=max(0.,cap-record["shared_duration_seconds"])
        record["budget_overrun"]=record["shared_duration_seconds"]>cap
        if ev is not None:
            record["gpu_peak_allocated_bytes"]=ev.torch.cuda.max_memory_allocated()
        record["summary"]=current_summary()
        write(args.output_dir/"summary.json",record["summary"])
        write(args.output_dir/"run.json",record)
        if d2:
            # Include final endpoint summarization/I/O in this study's fresh cap.
            record["duration_seconds"]=time.monotonic()-started
            record["shared_duration_seconds"]=record["duration_seconds"]
            record["remaining_active_seconds"]=max(0.,cap-record["duration_seconds"])
            record["budget_overrun"]=record["duration_seconds"]>cap
            record["summary"]["budget_overrun"]=record["budget_overrun"]
            if record["budget_overrun"]:
                record["summary"]["measured_t3_continuity_pass"]=False
            if args.descriptive_d2:
                record["summary"]=current_summary()
            write(args.output_dir/"summary.json",record["summary"])
            write(args.output_dir/"run.json",record)


if __name__ == "__main__":
    main()

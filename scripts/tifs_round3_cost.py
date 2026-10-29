"""Analytical Round 3 inventory and declared cost scenarios; stdlib only.

No benchmark, simulation, model import, scientific output or approval is made.
Counts are maximum planned work. Scenario seconds are explicit assumptions.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def s_inventory(n):
    arms, marked, cells, seeds, threats, secondary = 11, 10, 4, 3, 7, 8
    clean = n*arms
    native = n*arms*cells*seeds
    attack = n*arms*threats
    other = n*arms*secondary
    producer = clean+native+attack+other
    return dict(sources=n, marked=marked*n, new_writer_marks=5*n,
        clean=clean, native=native, threats=attack, secondary=other,
        producer=producer, detector=n*marked*2*(1+cells*seeds+threats+secondary),
        quality_rows=producer, metric_pairs=producer+native+other,
        tapes=n*cells*seeds)


def inventory():
    p_marks = 8*4+4*4+2*8+8
    p_f5, p_budget = 24, 2*16+8
    marks = p_marks+p_f5+p_budget
    p = dict(candidate_marks=p_marks, retained_f5_marks=p_f5, budget_f5_marks=p_budget,
        marked=marks, c0_source_directory_units=marks, unique_original_sources=24,
        clean=2*marks, native=2*marks*12, producer=2*marks*13,
        detector=2*marks*13, quality_rows=2*marks*13, metric_pairs=2*marks*25,
        tapes=marks*12, max_x0_marks=4*4+4*4+2*8+8, min_x0_marks=4*4,
        calibration_reused_marked=6, calibration_reused_clean=12,
        calibration_reused_native=144)
    screen, rehearsal = s_inventory(16), s_inventory(2)
    combined = {key: p.get(key, 0)+screen.get(key, 0)+rehearsal.get(key, 0)
                for key in ("marked", "clean", "native", "threats", "secondary", "producer", "detector", "quality_rows", "metric_pairs", "tapes")}
    combined["unique_marking_source_images"] = p["unique_original_sources"]+screen["sources"]+rehearsal["sources"]
    combined["additional_unmarked_threat_target_images"] = screen["sources"]+rehearsal["sources"]
    combined["unique_original_images_including_threat_targets"] = (combined["unique_marking_source_images"]
        +combined["additional_unmarked_threat_target_images"])
    combined["raw_rgb8_bytes"] = combined["producer"]*512*512*3
    combined["internal_detector_rows"] = p["detector"]+7*18*2*28
    combined["external_detector_rows_each"] = 18*2*28
    combined["additional_internal_binding_mode_calls"] = 7*18*2*7*3
    combined["vine_b_owner_queries"] = 2*combined["external_detector_rows_each"]
    combined["vine_b_q_candidate_checks"] = 41449*combined["vine_b_owner_queries"]
    combined["reader_gradient_evaluations"] = 350*(72+4*18)+200*(40+24+2*18)
    combined["codec_gradient_graphs"] = 150*(72+3*18)
    combined["generic_transform_gradient_graphs"] = 150*18
    combined["max_x0_marks"] = p["max_x0_marks"]+18
    combined["max_x0_unet_gradient_graphs"] = 150*combined["max_x0_marks"]
    combined["min_x0_marks"] = p["min_x0_marks"]+18
    combined["min_x0_unet_gradient_graphs"] = 150*combined["min_x0_marks"]
    # P calibration has two variant-specific gradient-check invocations per
    # source; S has one combined four-variant invocation per rehearsal source.
    diagnostics = dict(stage_p_clean_reader_gradients=4, stage_p_surrogate_reader_gradients=12,
        stage_p_codec_gradients=12, stage_p_x0_full_graphs=6, stage_p_epsilon_extra_backwards=6,
        stage_s_clean_reader_gradients=2, stage_s_surrogate_reader_gradients=24,
        stage_s_codec_gradients=18, stage_s_generic_graphs=6,
        stage_s_x0_full_graphs=6, stage_s_epsilon_extra_backwards=6,
        reader_projection_forward_checks=12, source_invocations=6,
        stage_p_c0_native_replay_trajectories=72, stage_s_c0_native_replay_trajectories=24,
        stage_p_extra_native_epsilon_forwards=18, stage_s_extra_native_epsilon_forwards=6,
        replay_policy="Conservative: P calibration replay in all three directories; S replay every rehearsal C0. No extra saved producer identity.")
    # Candidate cohort segments: 8+4+2+1=15. F5: 3 tune increments + check.
    # Budget controls: two finalist budgets + selected budget check. Calibration
    # is three extra initial invocations whose outputs count in first rung.
    segments_p = 15+4+3+3
    loads = dict(stage_p_segments=segments_p, stage_s_segments=2,
        native_family_loads=3*(segments_p+2), writer_loads=segments_p+10*2,
        reader_loads=segments_p+10*2, quality_loads=segments_p+2)
    loads["total_model_phase_loads"] = sum(loads[k] for k in ("native_family_loads", "writer_loads", "reader_loads", "quality_loads"))
    return dict(stage_p=p, stage_s_screen=screen, stage_s_rehearsal=rehearsal,
        combined=combined, diagnostics=diagnostics, assumed_invocation_inventory=loads)


SCENARIOS = {
    "fast_assumption": dict(reader_gradient=.595, writer_fixed=35, generic_graph=.03,
        codec_r0=.25, codec_r1=1., codec_r1_transfer=.05,
        unet_r0=.7, unet_r1=3., unet_transfer_r0=.05, unet_transfer_r1=.25,
        retained_f5_writer=119., budget_f5_writer=130., v5_writer=30., wam_writer=2., vine_writer=4.,
        native_r0=2., native_r1_01=4., native_r1_02=7., native_k3=10.,
        internal_detector_row=.75, wam_detector_row=.1, vine_detector_row=.25,
        vine_b_feature_decoder_row=.75, vine_b_owner_decode=.25, binding_mode_call=.01,
        metric_pair=.25, light_transform=.05, image_journal_hash=.05,
        native_epsilon_forward_r0=.2, native_epsilon_forward_r1=.8,
        model_phase_load=30., diagnostic_fixed=10., setup_seconds=3600., freeze_seconds=900.),
    "middle_assumption": dict(reader_gradient=.9, writer_fixed=60, generic_graph=.06,
        codec_r0=.6, codec_r1=2.5, codec_r1_transfer=.2,
        unet_r0=2., unet_r1=8., unet_transfer_r0=.2, unet_transfer_r1=.8,
        retained_f5_writer=180., budget_f5_writer=200., v5_writer=60., wam_writer=5., vine_writer=10.,
        native_r0=4., native_r1_01=8., native_r1_02=14., native_k3=20.,
        internal_detector_row=1.5, wam_detector_row=.3, vine_detector_row=.5,
        vine_b_feature_decoder_row=1.5, vine_b_owner_decode=.5, binding_mode_call=.03,
        metric_pair=.5, light_transform=.15, image_journal_hash=.15,
        native_epsilon_forward_r0=.6, native_epsilon_forward_r1=2.,
        model_phase_load=60., diagnostic_fixed=30., setup_seconds=7200., freeze_seconds=1800.),
    "stress_assumption": dict(reader_gradient=1.5, writer_fixed=120, generic_graph=.12,
        codec_r0=1.2, codec_r1=5., codec_r1_transfer=.5,
        unet_r0=5., unet_r1=20., unet_transfer_r0=.5, unet_transfer_r1=2.,
        retained_f5_writer=300., budget_f5_writer=360., v5_writer=120., wam_writer=15., vine_writer=30.,
        native_r0=8., native_r1_01=16., native_r1_02=28., native_k3=40.,
        internal_detector_row=4., wam_detector_row=1., vine_detector_row=1.5,
        vine_b_feature_decoder_row=4., vine_b_owner_decode=1.5, binding_mode_call=.1,
        metric_pair=1.2, light_transform=.4, image_journal_hash=.4,
        native_epsilon_forward_r0=1.5, native_epsilon_forward_r1=5.,
        model_phase_load=120., diagnostic_fixed=90., setup_seconds=10800., freeze_seconds=3600.)}


def writer_seconds(s):
    clean = 350*s["reader_gradient"]+s["writer_fixed"]
    codec = 50*s["codec_r0"]+100*(s["codec_r1"]+s["codec_r1_transfer"])
    unet = 50*(s["unet_r0"]+s["unet_transfer_r0"])+100*(s["unet_r1"]+s["unet_transfer_r1"])
    return dict(noise=clean+codec, codec=clean+codec, generic=clean+150*s["generic_graph"],
        x0=clean+codec+unet, f5=s["retained_f5_writer"], budget=s["budget_f5_writer"])


def diagnostic_seconds(s, inv):
    d = inv["diagnostics"]
    reader = sum(d[k] for k in ("stage_p_clean_reader_gradients", "stage_p_surrogate_reader_gradients",
        "stage_s_clean_reader_gradients", "stage_s_surrogate_reader_gradients"))*s["reader_gradient"]
    codec = (d["stage_p_codec_gradients"]+d["stage_s_codec_gradients"])/3*(s["codec_r0"]+2*(s["codec_r1"]+s["codec_r1_transfer"]))
    # Two backwards through each diagnostic epsilon graph: read loss and an
    # extra epsilon-input test. Charge a full graph for each for conservatism.
    unet = 8*(s["unet_r0"]+s["unet_transfer_r0"])+16*(s["unet_r1"]+s["unet_transfer_r1"])
    epsilon = 8*s["native_epsilon_forward_r0"]+16*s["native_epsilon_forward_r1"]
    native_sum = sum(s[k] for k in ("native_r0", "native_r1_01", "native_r1_02", "native_k3"))
    return reader+codec+unet+epsilon+24*native_sum+6*s["generic_graph"]+6*s["diagnostic_fixed"]


def forecast(s, inv):
    w, c = writer_seconds(s), inv["combined"]
    # Respect the allocation: x0+noise=72. Both cannot attain 56 at once.
    x0_p = 56 if w["x0"] >= w["noise"] else 16
    p_writer = x0_p*w["x0"]+(72-x0_p)*w["noise"]+24*w["f5"]+40*w["budget"]
    s_writer = 18*(w["x0"]+w["noise"]+w["codec"]+w["generic"]+w["budget"]+w["f5"]
        +s["v5_writer"]+s["wam_writer"]+2*s["vine_writer"])
    native_sum = sum(s[k] for k in ("native_r0", "native_r1_01", "native_r1_02", "native_k3"))
    work = dict(stage_p_writers=p_writer, stage_s_writers=s_writer,
        stage_p_native=inv["stage_p"]["native"]/4*native_sum,
        stage_s_native=(inv["stage_s_screen"]["native"]+inv["stage_s_rehearsal"]["native"])/4*native_sum,
        internal_readers=c["internal_detector_rows"]*s["internal_detector_row"],
        external_wam=c["external_detector_rows_each"]*s["wam_detector_row"],
        external_vine_r=c["external_detector_rows_each"]*s["vine_detector_row"],
        external_vine_b=c["external_detector_rows_each"]*s["vine_b_feature_decoder_row"]+c["vine_b_owner_queries"]*s["vine_b_owner_decode"],
        binding_modes=c["additional_internal_binding_mode_calls"]*s["binding_mode_call"],
        metric_pairs=c["metric_pairs"]*s["metric_pair"],
        threats_secondary=18*11*15*s["light_transform"],
        image_journal_hash=c["producer"]*s["image_journal_hash"],
        model_loading=inv["assumed_invocation_inventory"]["total_model_phase_loads"]*s["model_phase_load"],
        diagnostics_and_parity=diagnostic_seconds(s, inv))
    variable = math.fsum(work.values())
    fixed = s["setup_seconds"]+s["freeze_seconds"]+3600
    total = fixed+1.5*variable
    return dict(assumed_seconds=s, derived_writer_seconds=w, maximum_cost_stage_p_x0_marks=x0_p,
        budget_control_timing_assumption=dict(independent_full_write_seconds=w["budget"],
            ratio_to_retained_f5=w["budget"]/w["f5"],
            additional_seconds_per_write=w["budget"]-w["f5"],
            status="UNMEASURED: checkpoint/precision/budget overhead may differ; neither time is a guaranteed bound"),
        variable_work_seconds=work, variable_total_seconds=variable, setup_freeze_collection_seconds=fixed,
        conservative_total_seconds=total, conservative_total_hours=total/3600,
        whole_hour_scenario_cap=math.ceil(total/3600),
        usd_at_assumed_hourly_rates=[.45*math.ceil(total/3600), .60*math.ceil(total/3600)],
        status="UNMEASURED_SCENARIO_NOT_EXECUTION_AUTHORIZATION")


def minimum_measured_cap_hours(elapsed, fixed_remaining, remaining_work, collection=3600, factor=1.5):
    """Ideal whole-hour reservation conditional on a complete measured forecast.

    Already elapsed successful/failed/calibration work belongs only in elapsed.
    The runtime may conservatively reserve more by using the full P allocation
    again. Neither formula establishes a deterministic completion guarantee.
    """
    values = (elapsed, fixed_remaining, remaining_work, collection, factor)
    if any(not math.isfinite(x) or x < 0 for x in values) or factor < 1:
        raise ValueError("Finite nonnegative time and factor>=1 required")
    return math.ceil((elapsed+fixed_remaining+factor*remaining_work+collection)/3600)


def report():
    inv = inventory()
    return dict(schema="tifs-round3-cost-design-v2", scientific_measurements=False,
        execution_authorized=False, rates_are_assumed_not_live_quotes=True, inventory=inv,
        scenarios={name:forecast(s, inv) for name,s in SCENARIOS.items()},
        policy=dict(effective_cap_hours=15, cap_change_requires_user_decision=True,
            proposed_planning_cap_hours=126,
            planning_cap_basis="Whole-hour rounding of declared middle assumptions only; not an empirically established minimum.",
            formula="ceil((elapsed_paid_seconds + fixed_remaining_seconds + 1.5*remaining_variable_seconds + 3600)/3600)",
            formula_scope="Ideal nonduplicating minimum conditional on complete measured remaining-work inputs; engineering allowance, not a guaranteed bound.",
            completed_work_accounting="Deduct already completed/calibration work from remaining work only when explicitly accounted; retain all spent wall time in elapsed.",
            runtime_stage_p_reservation="Conservative full 136-mark/136-C0-unit P allocation reserved after calibration, while elapsed includes calibration; deliberate over-reservation, not repeated scientific execution.",
            runtime_forecast_refresh="One frozen post-calibration P forecast; no automatic refresh after each rung. Per-unit paid-deadline and collection-reserve checks still apply.",
            runtime_writer_proxy="All 72 candidates charged at max(measured noise, measured x0); all 40 budget controls charged at max(candidate proxy, measured retained F5). Budget-control proxy is conservative by intent, not a measured bound.",
            runtime_load_allowance="Full repeated model-load cycles and measured overhead both reserved; may over-reserve compared with nominal scenario.",
            budget_control_timing="Independent 130/200/360 s full-write assumptions versus retained F5 119/180/300 s. Checkpoint overhead is unmeasured; equal update counts do not establish equal cost.",
            floor_role="119 s/source is a historical F5 proxy anchor, not a certified lower bound or F6 benchmark.",
            stage_p_cannot_certify_stage_s="P calibration qualifies remaining P only. S requires its disjoint complete all-arm rehearsal before full screen, using the same paid clock.",
            stage_s_forecast_failure="Retain P evidence, collect and stop with RESOURCE_STOP; no fractional S or scientific-negative label.",
            partial_inventory_go=False),
        disk=dict(raw_rgb8_bytes=inv["combined"]["raw_rgb8_bytes"],
            tapes=inv["combined"]["tapes"], model_reference_decimal_gb=48.598,
            projected_rule="free_bytes >= 1.5*remaining_measured_output_and_tape_bytes + peak_temporary_bytes + 0.2*filesystem_total_bytes",
            omissions=["PNG overhead/compression", "original/canonical source and threat-target files", "model or package staging duplication", "native intermediate/temp files", "tape sizes", "logs and receipts", "existing retained outputs"],
            volume_size_is_not_free_space=True))


def self_test():
    i = inventory()
    assert i["stage_p"]["marked"] == 136 and i["stage_p"]["native"] == 3264
    assert i["stage_s_screen"]["producer"] == 4928 and i["stage_s_screen"]["detector"] == 8960
    assert i["stage_s_rehearsal"]["producer"] == 616 and i["stage_s_rehearsal"]["detector"] == 1120
    assert i["combined"]["producer"] == 9080 and i["combined"]["detector"] == 13616
    assert i["combined"]["metric_pairs"] == 16304
    assert i["combined"]["unique_marking_source_images"] == 42
    assert i["combined"]["additional_unmarked_threat_target_images"] == 18
    assert i["combined"]["unique_original_images_including_threat_targets"] == 60
    assert i["combined"]["threats"] == 1386 and i["combined"]["secondary"] == 1584
    assert i["combined"]["reader_gradient_evaluations"] == 70400
    assert i["combined"]["max_x0_unet_gradient_graphs"] == 11100
    assert minimum_measured_cap_hours(0, 0, 0) == 1
    assert minimum_measured_cap_hours(3600, 1800, 7200) == 6
    costs = [forecast(s, i)["conservative_total_seconds"] for s in SCENARIOS.values()]
    assert costs[0] < costs[1] < costs[2]
    assert forecast(SCENARIOS["middle_assumption"], i)["whole_hour_scenario_cap"] == 126
    for s in SCENARIOS.values():
        w = writer_seconds(s)
        enumeration = [x*w["x0"]+(72-x)*w["noise"] for x in range(16, 57)]
        chosen = forecast(s, i)["maximum_cost_stage_p_x0_marks"]
        assert chosen*w["x0"]+(72-chosen)*w["noise"] == max(enumeration)
        # Budget-control timing is an independent scenario input. There are
        # 40 P + 18 S budget writes; all are charged once before the factor.
        changed = dict(s, budget_f5_writer=s["budget_f5_writer"]+60)
        delta = forecast(changed, i)["conservative_total_seconds"]-forecast(s, i)["conservative_total_seconds"]
        assert math.isclose(delta, 58*60*1.5, rel_tol=1e-12, abs_tol=1e-7)
    # Deliberate reservation of completed work can only raise this ideal cap.
    assert minimum_measured_cap_hours(1800, 900, 7200) <= minimum_measured_cap_hours(1800, 900, 9000)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print("Pure inventory/cost identities passed; no timing or scientific run.")
    if args.output:
        args.output.write_text(json.dumps(report(), indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(str(args.output))
    if not args.self_test and not args.output:
        parser.error("Specify --self-test and/or --output")


if __name__ == "__main__":
    main()

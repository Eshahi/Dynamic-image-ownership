"""Project the full final-study schedule from the Phase-A pilot's measured path times. Stdlib only.

Written by Claude (Opus 5.5) on 2026-10-26. Inputs: the pilot journal (pilot.jsonl) and the planned counts of
07-final-experiment.md / 05-informed-attacks.md / analysis/mechanism-server-spec.md. Historical native-generation
and detector times come from analysis/cost-analysis.json (stage-2 journals, RTX 4090), as Codex's cost audit used.
Every count below is quoted from those files; every measured time is the maximum over the pilot's repetitions of
that path (the protocol asks for maximum measured path times), with a 30% margin applied at the end.

Usage: python -I project_schedule.py pilot.jsonl > projection.json
"""
import json
import sys
from collections import defaultdict

MARGIN = 1.3


def load(path):
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    return [r for r in rows if r.get("status") == "ok"], rows


def main():
    ok, rows = load(sys.argv[1])
    jvp = defaultdict(list)          # (family, strength) -> chain seconds
    step = defaultdict(list)         # family -> per-step JVP seconds
    decode = defaultdict(list)       # family -> decode+reader JVP seconds
    enc = defaultdict(list)          # family -> encoder JVP seconds
    attack_a = defaultdict(list)     # strength -> SDXL+SD1.5 seconds
    attack_b, inversion = [], []
    for r in ok:
        d = r.get("details") or {}
        if r["check"] == "jvp_chain":
            jvp[(r["family"], r["strength"])].append(r["seconds"])
            step[r["family"]] += [s["seconds"] for s in d["steps"]]
            decode[r["family"]].append(d["decode_reader_jvp_seconds"])
        elif r["check"] == "encoder_jvp":
            enc[r["family"]].append(d["seconds"])
        elif r["check"] == "attack_a":
            for x in d["rows"]:
                attack_a[x["strength"]].append(x["sdxl_seconds"] + x["sd15_seconds"])
        elif r["check"] == "attack_b":
            attack_b.append(d["timing"]["optimization_seconds"])
            inversion.append(d["timing"]["inversion_seconds"])
    executed = {"R0": {.1: 2, .2: 4, .4: 8}, "R1": {.1: 2, .2: 4, .4: 8}, "K3": {.2: 4}}
    # Per-unit full-chain JVP time per cell: native C0 latent call + steps x max step JVP + max decode JVP.
    native_latent = defaultdict(list)
    for r in ok:
        if r["check"] == "jvp_chain":
            native_latent[r["family"]].append(r["details"]["native_latent_call_seconds"])
    cell_jvp = {}
    for fam, cells in executed.items():
        if not step.get(fam):
            continue
        for s, n in cells.items():
            cell_jvp[f"{fam} {s}"] = max(native_latent[fam]) + n * max(step[fam]) + max(decode[fam])
    missing = sorted(set(f"{f} {s}" for f, c in executed.items() for s in c) - set(cell_jvp))
    hours = {}
    # Phase A law: 60 sources x six R0/R1 cells x 3 seeds = 1,080 (07 section 4); per cell 180.
    a_law = sum(180 * cell_jvp.get(f"{f} {s}", float("nan")) for f in ("R0", "R1") for s in (.1, .2, .4)) / 3600
    # Phase B law: 200 x 7 cells x 3 seeds = 4,200; per cell 600.
    b_law = sum(600 * cell_jvp.get(c, float("nan")) for c in ["R0 0.1", "R0 0.2", "R0 0.4", "R1 0.1", "R1 0.2", "R1 0.4", "K3 0.2"]) / 3600
    # Mechanism module: 720 mode-encoder JVPs (12 x 4 arms x 3 encoders x 5 directions) and 540 differential
    # full-chain JVPs at .2 (12 x 3 families x 3 seeds x 5 directions); 1,620 stage-primal outputs at native cost.
    enc_max = {f: max(v) for f, v in enc.items()}
    mech_enc = sum(240 * enc_max.get(f, float("nan")) for f in ("R0", "R1", "K3")) / 3600
    mech_chain = sum(180 * cell_jvp.get(c, float("nan")) for c in ("R0 0.2", "R1 0.2", "K3 0.2")) / 3600
    mech_stage = 1620 * 1.3 / 3600  # historical R1 .2 native unit (1.30 s) as the per-output upper reference
    # Attack A grid (Phase A): 60 x 4 marks x 4 strengths x 3 seeds = 2,880 chained outputs.
    a_grid = sum(720 * max(v) for v in attack_a.values()) / 3600 if attack_a else float("nan")
    # Attack A selected (Phase B): 200 x 5 inputs x 3 seeds = 3,000 at the slowest strength (unknown selection).
    a_sel = 3000 * max(max(v) for v in attack_a.values()) / 3600 if attack_a else float("nan")
    # Attack B grid (Phase A): 240 inversions + 2,160 optimizations; B-fidelity 240 + B-codec 240 (negligible).
    b_opt, b_inv = (max(attack_b), max(inversion)) if attack_b else (float("nan"), float("nan"))
    b_grid = (240 * b_inv + 2160 * b_opt + 240 * b_opt) / 3600
    # Attack B selected (Phase B): 1,000 inversions + 1,000 optimizations + 1,000 B-fidelity optimizations.
    b_sel = (1000 * b_inv + 2000 * b_opt) / 3600
    # Historical subtotals (Codex cost audit, analysis/server-costs.md): Phase B native+clean+assessment+A proxy
    # 25.02 h, of which the A generation proxy is 1.43 h (replaced here by the measured a_sel); Phase A historical
    # native/A/selected-assessment subtotal about 5.8 h.
    hours["phase_A"] = dict(historical_native_and_assessment=5.8, law_jvps=a_law, mechanism_encoder_jvps=mech_enc,
                            mechanism_chain_jvps=mech_chain, mechanism_stage_outputs=mech_stage,
                            attack_A_grid=a_grid, attack_B_grid=b_grid)
    hours["phase_B"] = dict(historical_native_clean_assessment=25.02 - 1.43, law_jvps=b_law,
                            attack_A_selected=a_sel, attack_B_selected_and_fidelity=b_sel)
    # Retrieval at the measured home download rate of about 0.85 MB/s (stage 2b), saved outputs about 0.41 MB each:
    # Phase A about 12,000 outputs (5,400 native + 2,880 A + 2,160 B + 1,620 stage) ~ 5 GB ~ 1.6 h;
    # Phase B about 31,000 outputs ~ 12.7 GB ~ 4.2 h. Noise bundles and states stay on the server (receipts only).
    fixed = {"phase_A": dict(setup_downloads_loading=1.5, retrieval=2.0),
             "phase_B": dict(setup_downloads_loading=1.5, retrieval=4.5)}
    out = dict(cell_full_chain_jvp_seconds=cell_jvp, cells_without_measurement=missing,
               per_step_jvp_seconds_max={f: max(v) for f, v in step.items()},
               decode_reader_jvp_seconds_max={f: max(v) for f, v in decode.items()},
               encoder_jvp_seconds_max=enc_max, attack_A_seconds_max={str(k): max(v) for k, v in attack_a.items()},
               attack_B_seconds_max=dict(optimization=b_opt, inversion=b_inv), components_hours=hours,
               fixed_hours_per_phase=fixed, margin=MARGIN)
    for phase, comp in hours.items():
        compute = sum(comp.values())
        out[f"{phase}_projected_hours"] = dict(compute=compute, with_margin=compute * MARGIN,
                                               with_margin_and_fixed=compute * MARGIN + sum(fixed[phase].values()))
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()

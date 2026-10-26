"""Assemble the Phase-A freeze record (07-final-experiment.md section 4) from the retrieved run folder.

Written by Claude (Opus 5.5) on 2026-10-26. Every frozen value is copied from the files the frozen stages wrote
(phase-a-fit.json, attack-freeze.json) and hashed; nothing is recomputed here.

Usage: python -I write_freeze.py RUN_FOLDER REPO_ROOT > PHASE-A-FREEZE.json
"""
import hashlib
import json
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def infinity_safe(score):
    return {"kind": "positive_infinity", "value": None} if score is None else score


def main():
    run, root = Path(sys.argv[1]), Path(sys.argv[2])
    fit = json.loads((run / "phase-a-fit.json").read_text(encoding="utf-8"))
    freeze = json.loads((run / "attack-freeze.json").read_text(encoding="utf-8"))
    study = root / "research" / "encoder-transfer-20261019"
    code = ["scripts/et_final_phase_a.py", "scripts/et_final_phase_a_attacks.py", "scripts/et_final_phase_a_fit.py",
            "scripts/et_final_phase_a_mechanism.py", "scripts/et_final_phase_a_driver.sh", "scripts/et_final_pilot.py",
            "scripts/encoder_transfer_runtime.py", "scripts/encoder_transfer_test.py"]
    q = fit["q90"]
    out = dict(
        record="final-study Phase-A freeze", protocol="07-final-experiment.md section 4; analysis/training-missingness-design.md; "
        "analysis/quality-baseline-contract.md; 05-informed-attacks.md",
        approval="user, 2026-10-26: Phase A with option (a), total cap 22 instance-hours; development sources only",
        amendment_option_a="native trajectories run inside the derivative path's kernels (classic attention processor, explicit "
                           "fp32-internal LayerNorm), so the law's C0 primal equals the native output (max primal error 0.0); see pilot/PILOT-REPORT.md",
        machine="vast.ai 57583551, RTX 4090 24 GB, Ryzen 9 5950X, 62 GB RAM; USD .448/h",
        timeline_utc=dict(instance_start="2026-10-26T08:08Z", stage1_start="2026-10-26T08:59Z", stage1_end="2026-10-26T10:57Z",
                          attack_freeze=freeze["frozen_utc"], detector_release_start="2026-10-26T13:34Z",
                          fit_freeze=fit["frozen_utc"], instance_stop="2026-10-26T15:26Z", instance_hours=7.3),
        code_sha256={c: sha(root / c) for c in code},
        config_sha256={"source-list.json": sha(study / "source-list.json"), "stage2b-config.json": sha(study / "stage2b-config.json")},
        run_files_sha256={f: sha(run / f) for f in ("native.jsonl", "attacks.jsonl", "detect.jsonl", "mechanism.jsonl", "mechanism-e.json",
                                                   "attack-freeze.json", "phase-a-fit.json", "phase-a-diagnostic-rows.json")},
        native_settings="R0 SD1.5 and R1 SDXL img2img, DDIM 20 leading, eta 0, empty prompt, CFG 1, strengths .1/.2/.4, seeds 12/13/14; "
                        "marked outputs replay the C0 trajectory's recorded noise (Tape) with seed label +1000",
        noise_convention="pilot.Tape records every diffusers randn_tensor draw of the C0 call in call order and replays it for the four marks",
        cells=fit["cells"], training_weight="1/18 per seed vector (kappa); 1/6 per source-cell row (comparator)",
        fit_sources=fit["fit_sources"], calibration_sources=fit["calibration_sources"],
        kappa=fit["kappa"],
        q90=dict(value=q["value"], status=q["status"], complete_sources=q["complete_sources"], units=q["units"],
                 source_scores=[dict(source=s["source"], complete=s["complete"], score=infinity_safe(s["score"])) for s in q["source_scores"]]),
        quality_comparator=fit["quality_comparator"],
        attacks={k: dict(status=freeze[k]["status"], selected=freeze[k]["selected"], candidates=freeze[k]["candidates"],
                         planned_grid_rows=freeze[k]["planned_grid_rows"], observed_grid_rows=freeze[k]["observed_grid_rows"])
                 for k in ("A", "B")},
        attack_rule=freeze["rule"],
        semantic_proxy="predicted 320-chip vector b + kappa v read by the unchanged F5 soft-binding semantic reader with the C0 output's "
                       "seven-view CLIP descriptor in place of the unknown marked-output descriptor; C = read and content match; three-seed majority",
        development_diagnostics=fit["development_diagnostics"],
        missingness="safety-checker blocks are recorded as safety_blocked, never retried or bypassed; an unavailable law vector keeps "
                    "its weight in the ledger; unchanged rules of training-missingness-design.md",
        engineering_events=[
            "mechanism R1 encoder gains first ended error_terminal (fp16 encode refused by the official SDXL VAE wrapper); "
            "fixed in 55f4159 and rerun with --retry-errors (48/48 ok); no stage-1, attack, detector or fit row was affected",
            "the driver's mechanism process ran out of GPU memory loading K3 after SDXL (SDXL references kept); fixed in 5072221 "
            "and K3 ran in its own process (84/84 ok)",
            "two R0 mechanism stage rows (stage:R0:459:12 and stage:R0:72:12, the same C0 safety blocks as stage 1 at R0 .2) are recorded as error_terminal by the "
            "mechanism script; they are descriptive only"],
        h4_consequence="BASELINE_UNAVAILABLE prevents primary H4 evaluation (training-missingness-design.md); H4 keeps p=1 in Phase B",
        h5_consequence="both attacks inactive: the four A and four B H5 slots keep p=1 (07 section 6)",
        phase_b_forecast="phase-b-forecast.json",
    )
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()

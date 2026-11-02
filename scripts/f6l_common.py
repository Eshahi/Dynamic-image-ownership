"""Lean F6 shared rules: arm lists, paid caps, probe policy, stage configs. Standard library only."""
from __future__ import annotations

import copy
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tifs_common as common

LEAN = ROOT / "research/tifs-20261028/lean"
LEAN_CONFIG = LEAN / "lean-config.json"
PHASES = ("probe", "stage1", "stage2", "stage3", "f7")


def load_lean():
    return common.load_json(LEAN_CONFIG)


def hours_cap(lean, hourly_usd):
    """The smaller of the hour cap and the dollar cap at the actual price."""
    caps = lean["caps"]
    if type(hourly_usd) not in (int, float) or not 0 < hourly_usd <= caps["max_hourly_usd"]:
        raise ValueError("Actual hourly price is missing or above the prospective limit")
    return min(float(caps["max_instance_hours"]), caps["max_usd"] / hourly_usd)


def control_arm(arm, spec):
    """Matched control: unchanged F5 objective at the same robust budget and render."""
    if spec.get("kind") != "lean" or spec["variant"] == "f5-budget":
        return None, None
    render = spec["render_db"]
    name = f"f5b-{spec['robust_psnr_db']}" + (f"-ren{render}" if render is not None else "")
    return name, dict(kind="lean", variant="f5-budget", robust_psnr_db=spec["robust_psnr_db"], render_db=render)


def phase_arms(lean, phase, previous=None):
    """Arm specs for one phase. Stage 2 and 3 arms come only from the previous decision."""
    specs = lean["arms"]
    if phase in ("probe", "stage1", "f7"):
        names = list(lean["phases"][phase]["arms"])
        return names, {name: specs[name] for name in names}
    if previous is None:
        raise ValueError(phase + " needs the previous stage decision")
    selected = previous["finalists"] if phase == "stage2" else [previous["winner"]]
    names, result = ["unmarked", "f5-r2"], {"unmarked": specs["unmarked"], "f5-r2": specs["f5-r2"]}
    for arm in selected:
        control, spec = control_arm(arm, specs[arm])
        if control and control not in result:
            names.append(control)
            result[control] = spec
    for arm in selected:
        names.append(arm)
        result[arm] = specs[arm]
    if phase == "stage3":
        for arm in lean["phases"]["stage3"]["baselines"]:
            names.append(arm)
            result[arm] = specs[arm]
    return names, result


def partition_sources(lean, phase, manifest):
    """Committed partition order only; the rest of Stage P's tuning order stays fixed."""
    rule = lean["phases"][phase]["sources"]
    return manifest[rule["partition"] + "_sources"][rule["start"]:rule["stop"]]


def stage_config(lean, base, phase, *, previous=None):
    """A copy of the frozen Stage S config with only the lean inventory changed."""
    if phase not in PHASES:
        raise ValueError("Unknown lean phase")
    names, specs = phase_arms(lean, phase, previous)
    config = copy.deepcopy(base)
    config.update(arms=names, seeds=lean["phases"][phase]["seeds"], study="F6 lean " + phase,
                  candidate=None, new_writers=[n for n in names if specs[n]["kind"] == "lean"],
                  execution_authorized=False, gate_profile="lean-c-primary")
    estimates = dict(lean["unit_estimates_seconds"])
    # Every lean arm is read by the F5 reader, so it has the F5 row time.
    estimates.update({"detect_" + name: estimates["detect_f5-r2"] for name in names if specs[name]["kind"] == "lean"})
    config["budget"] = dict(max_instance_hours=lean["caps"]["max_instance_hours"],
                            retrieval_reserve_seconds=lean["caps"]["retrieval_reserve_seconds"],
                            unit_estimates_seconds=estimates)
    config["threats"] = dict(config["threats"], read_modes=lean["read_modes"])
    config["cells"] = list(config["cells"]) + list(lean["phases"][phase].get("extra_cells", []))
    config["lean"] = dict(phase=phase, arms=specs, writer=lean["writer"], cells=lean["cells"],
                          gates=lean["gates"], primary_endpoint=lean["primary_endpoint"],
                          previous_digest=previous.get("digest") if previous else None)
    if phase == "stage2":
        config["lean"]["finalists"] = previous["finalists"]
    elif phase == "stage3":
        config["lean"]["winner"] = previous["winner"]
        config["lean"]["control"] = control_arm(previous["winner"], lean["arms"][previous["winner"]])[0]
    for key in ("gate_profiles", "stage_p_selection", "article_decision", "decision"):
        config.pop(key, None)
    return config


def needs_offload(device_total_bytes):
    """Under 40 GiB the writer moves its models off the card between steps, as the approved F6 did. Cost only."""
    return device_total_bytes < 40 * 1024 ** 3


def disk_ok(lean, free_bytes):
    return free_bytes >= lean["caps"]["min_free_disk_bytes"]


def active_arms(out, config):
    """The arm list after the clean gate, or the whole list before it has run."""
    path = Path(out) / "arm-gate.json"
    return common.load_json(path)["active"] if path.exists() else list(config["arms"])


def within_cushion(lean, metrics):
    limit = lean["writer"]["quality_cushion"]
    return common.quality_eligible(metrics, limit["psnr_db_gt"], limit["ssim_rgb_gt"], limit["lpips_lt"])


def decide_policy(rules, measures):
    """Fixed before any native outcome exists. Inputs are timing and gradients only."""
    def med(key, *path):
        rows = []
        for measure in measures:
            value = measure
            for part in (key, *path):
                value = value.get(part) if isinstance(value, dict) else None
            if value is None:
                return None
            rows.append(value)
        return statistics.median(rows)
    policy = {}
    for variant in ("f6-noise", "f6-x0"):
        agreement = med(variant, "pairwise_cos_median")
        if agreement is None:
            raise ValueError("Probe lacks gradient agreement for " + variant)
        policy[variant] = dict(momentum=agreement < rules["momentum_if_median_pairwise_cos_below"],
                               pairwise_cos_median=agreement)
    ratio, cosine = med("bf16", "time_ratio"), med("bf16", "gradient_cos_median")
    policy["bf16"] = bool(ratio is not None and cosine is not None
                          and ratio <= rules["bf16_if_time_ratio_at_most"]
                          and cosine >= rules["bf16_if_gradient_cos_at_least"])
    fits = all(m.get("no_checkpoint", {}).get("fits") is True for m in measures)
    time_ratio = med("no_checkpoint", "time_ratio")
    free = med("no_checkpoint", "free_bytes_at_peak")
    policy["checkpoint"] = not (fits and time_ratio is not None and free is not None
                                and time_ratio <= rules["no_checkpoint_if_time_ratio_at_most"]
                                and free >= rules["no_checkpoint_free_margin_bytes"])
    return policy

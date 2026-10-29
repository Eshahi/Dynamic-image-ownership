"""Prospective thesis gate profiles. Pure stdlib; proposals never self-activate."""
from __future__ import annotations

import copy
import math
from pathlib import Path

import tifs_common as common


PROFILES = ("round1", "round3-proposed")

FIXED_THRESHOLDS = dict(absolute_foreign_count_min=12,
    clean_F_count_min_each_new_writer=15, max_retained_loss=1,
    gain_over_f5={"R1-0.1":4,"R1-0.2":4,"K3-0.2":3},
    gain_over_each_ablation={"R1-0.1":3,"R1-0.2":3,"K3-0.2":1},
    paired_median_lpips_delta_max=.005, paired_median_psnr_delta_min=-1)


def profile_config(config, name):
    if name not in PROFILES:
        raise ValueError("Unknown gate profile")
    result = copy.deepcopy(config)
    candidate = result["candidate"]
    decision = result["decision"]
    if any(decision.get(k) != v for k,v in FIXED_THRESHOLDS.items()):
        raise ValueError("Unregistered numerical gate threshold change")
    registry = result.get("gate_profiles", {})
    registered = registry.get(name, {})
    overrides = dict(ablation_gains_primary=name == "round1",
        gain_comparators=["f5-r2"] if name == "round1" else ["f5-r2","f5-budget"],
        quality_comparator="f5-r2" if name == "round1" else "f5-budget")
    if registered.get("decision_overrides") != overrides:
        raise ValueError("Gate profile registry differs from the preregistered comparison")
    result["gate_profile"] = name
    decision.update(copy.deepcopy(overrides))
    decision["ablation_arms"] = [a for a in config["new_writers"] if a != candidate]
    decision["quality_writers"] = list(dict.fromkeys([*config["new_writers"], candidate]))
    if name == "round3-proposed":
        decision["quality_writers"] = [candidate, "f5-budget"]
        decision["ablation_arms"] = [a for a in ("f6-noise","f6-x0","f6-codec","f6-generic")
                                    if a != candidate and a in config["arms"]]
    return result


def validate_decision_receipt(receipt, config_sha256):
    """Validate a later externally recorded choice; this is not authentication.

    Codex never creates this receipt. Claude records the user's actual choice
    and commits it BEFORE any server output, including Stage P. Hash binding
    prevents accidental use with a different protocol; it cannot prove consent.
    """
    if (receipt.get("schema") != "tifs-round3-user-choice-v1"
            or receipt.get("decision") != "approve"
            or receipt.get("recorded_by") != "Claude"
            or receipt.get("config_sha256") != config_sha256
            or receipt.get("gate_profile") not in PROFILES
            or receipt.get("stage_p") not in ("run", "decline")
            or receipt.get("k3_optimization") != "excluded"
            or receipt.get("before_server_outputs") is not True
            or not isinstance(receipt.get("user_decision_reference"), str)
            or not receipt["user_decision_reference"].strip()):
        raise ValueError("Missing or incompatible externally recorded pre-output user choice")
    hours = receipt.get("max_instance_hours")
    if type(hours) not in (int, float) or not math.isfinite(hours) or hours <= 0:
        raise ValueError("Invalid user-chosen paid-session ceiling")
    return receipt["gate_profile"]


def load_execution_config(config_path, *, selection_path=None, receipt_path=None):
    """Resolve immutable choices without changing the committed default config."""
    config_path = Path(config_path)
    config = common.load_json(config_path)
    digest = common.sha256_file(config_path)
    if config.get("stage_p"):
        # Stage P materialization owns its parent-config/choice binding.
        return config
    if config.get("gate_profile", "round1") != "round1":
        raise ValueError("Committed default must remain round1; supply a user choice separately")
    receipt = common.load_json(receipt_path) if receipt_path else None
    profile = validate_decision_receipt(receipt, digest) if receipt else "round1"
    if selection_path is None:
        default = config_path.parent.parent / "stage-p/selected-config.json"
        selection_path = default if default.exists() else None
    selection = common.load_json(selection_path) if selection_path else None
    provenance = dict(gate_profile=profile, config_sha256=digest,
                      user_choice_sha256=common.sha256_file(receipt_path) if receipt_path else None,
                      selected_config_sha256=None, stage_p="not_run")
    if selection is not None:
        if receipt is None or receipt["stage_p"] != "run":
            raise ValueError("A Stage P selection requires the same pre-output user choice")
        if (selection.get("status") != "SELECTED"
                or selection.get("base_config_sha256") != digest
                or selection.get("gate_profile") != profile
                or selection.get("user_choice_sha256") != provenance["user_choice_sha256"]
                or selection.get("check_status") != "PASS"
                or selection.get("candidate") not in ("f6-noise", "f6-x0")
                or selection.get("writer_psnr_db") not in (52, 46, 42, 38)
                or selection.get("k3_optimization") != "excluded"):
            raise ValueError("Stage P selection is incomplete, incompatible, or failed its untouched check")
        config["candidate"] = selection["candidate"]
        config["writer"]["psnr_db"] = selection["writer_psnr_db"]
        provenance.update(selected_config_sha256=common.sha256_file(selection_path), stage_p="selected")
    elif receipt is not None and receipt["stage_p"] == "run":
        raise ValueError("Stage P was chosen: missing selection cannot fall back to the frozen writer")
    else:
        provenance["stage_p"] = "declined" if receipt else "not_run_no_choice_receipt"
    config = profile_config(config, profile)
    if receipt:
        hours = receipt["max_instance_hours"]
        config["budget"]["max_instance_hours"] = hours
        config["budget"]["max_seconds"] = hours * 3600
    config["execution_choices"] = provenance
    return config

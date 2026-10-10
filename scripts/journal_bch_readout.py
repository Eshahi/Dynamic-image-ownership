"""E1-BCH59-A suspect-only semantic decoding and one RC1 instance route.

All sign-bound fields are hypothetical; public construction is not authorization.
"""
from __future__ import annotations

import math
import time
import numpy as np
from scripts import f5_latent_codec as f5
from scripts import journal_bch_carrier as codec

v5, base = f5.v5, f5.base
FAMILY, REVISION = "f5-bch59-antipodal", 1
METHOD = "E1-BCH59-A"


def semantic_channel(projections, profile, owner_id, q_now, roster_size=1):
    """One bounded-distance candidate; no known payload enters this function."""
    if roster_size != 1:
        raise ValueError("Fixed E1 development protocol requires one claimed owner")
    p = np.asarray(projections, np.float64)
    if p.shape != (320,) or not np.isfinite(p).all():
        raise ValueError("Expected 320 finite native carrier projections")
    r = np.asarray(codec.signs(profile, owner_id), np.float64)
    u = [float(r[a:b] @ p[a:b]) for a, b in zip(codec.BOUNDS[:-1], codec.BOUNDS[1:])]
    raw = sum(int(value < 0) << i for i, value in enumerate(u))
    decoded = codec.decode(raw)
    norm = float(np.linalg.norm(p))

    def score(q):
        return float(np.asarray(codec.pattern(profile, owner_id, q)) @ p / norm) if norm > 0 else 0.0

    alpha = float(profile["decision"]["false_positive_target"])
    read_threshold = math.sqrt(2 * math.log(2 * roster_size * 2**32 / alpha))
    single_threshold = math.sqrt(2 * math.log(2 * roster_size / alpha))
    decoded_score = score(decoded["q"]) if decoded["success"] else None
    recomputed_score = score(q_now)
    read = bool(decoded["success"] and decoded_score >= read_threshold)
    recomputed = recomputed_score >= single_threshold
    found = read or recomputed
    if read:
        distance = (decoded["q"] ^ q_now).bit_count()
        corrected = float(distance)
        candidate = "decoded" if distance else "recomputed"
    elif recomputed:
        distance, corrected, candidate = 0, 0.0, "recomputed"
    else:
        distance = corrected = candidate = None
    active_score = decoded_score if read else recomputed_score
    multiplicity = roster_size * (2**32 if read else 1)
    return {
        "found": found, "read": read, "candidate": candidate,
        "score": active_score, "threshold": read_threshold if read else single_threshold,
        "decoded_score": decoded_score, "decoded_threshold": read_threshold,
        "recomputed_score": recomputed_score, "recomputed_threshold": single_threshold,
        "decoded_code": f"{decoded['q']:08x}" if decoded["success"] else None,
        "code_distance": distance, "corrected_distance": corrected,
        "decoding_error_rate": 0.0 if read else None,
        "decoding_error_rate_status": "zero_means_no_heuristic_subtraction_not_estimated_BER",
        "content_convention": "raw_message_distance_and_soft_angle_error_parameter_zero",
        "log10_false_positive_bound": None,
        "hypothetical_log10_sign_bound": min(0.0, math.log10(multiplicity) - active_score**2 / (2 * math.log(10))) if active_score >= 0 else 0.0,
        "fpr_fields_status": "hypothetical_independent_sign_bound_unvalidated_for_public_adaptive_images",
        "raw_coded_word": f"{raw:015x}",
        "corrected_coded_word": f"{decoded['code']:015x}" if decoded["success"] else None,
        "coded_symbol_scores": u, "projection_norm": norm,
        "bch_success": decoded["success"], "bch_reason": decoded["reason"],
        "bch_error_positions": decoded["error_positions"], "bch_syndromes": decoded["syndromes"],
        "bch_correction_radius": 5, "payload_bits": 32, "coded_bits": 59, "carrier_chips": 320,
    }


def detect_rgb(rgb, z, owner_id, profile, semantic_features,
               binding_mode="combined", roster_size=1, binding="soft"):
    """Decode only the suspect; writer/evaluator payload targets are absent."""
    if binding not in f5.BINDINGS:
        raise ValueError("binding must be hard or soft")
    started = time.perf_counter()
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(owner_id)
    luma = v5.luminance_from_rgb(np.asarray(rgb).tolist())
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(luma, fragile.analysis)
    instance_p = fragile.projections(coefficients)
    robust_p = f5.Layout(checked, key, config, owner).projections(z)
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)
    decision = checked["decision"]
    semantic_limits = int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"])
    instance_limits = int(decision["instance_radius"]), int(decision["instance_mismatch_distance"])
    check_s = binding_mode in ("combined", "semantic_only")
    check_i = binding_mode in ("combined", "perceptual_only")
    semantic = semantic_channel(robust_p, checked, owner_id, q_now, roster_size)
    s_found = semantic["found"]
    s_status = soft_distance = None
    if s_found:
        s_status, soft_distance = f5._semantic_status(semantic, semantic_features, key, config, semantic_limits, check_s, binding)
    semantic["soft_distance"] = soft_distance
    q_bound = int(semantic["decoded_code"], 16) if semantic["read"] else q_now
    table = v5._instance_table(owner, key, config)
    options = [table[j][v5._bit(q_bound, j)] for j in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_p, options, h_now),
                                  float(decision["false_positive_target"]), roster_size, h_now)
    instance["fpr_fields_status"] = "legacy_model_based_unvalidated_for_selected_q_route"
    i_found = instance["found"]
    own_i_status = base._content_status(instance["corrected_distance"], *instance_limits, check_i) if i_found else None
    i_status = max(own_i_status, s_status if s_found else "unchecked", key=base._STATUS_RANK.get) if i_found else None
    outcome, state = base._decide(s_found, s_status, i_found, i_status)

    def public(value, status):
        return {**value, "content_status": status,
                "content_match": bool(value["found"] and base._STATUS_RANK[status] == 0)}

    return {
        "outcome": outcome, "proposal_state": state, "watermark_found": bool(s_found or i_found),
        "semantic": public(semantic, s_status), "instance": public(instance, i_status),
        "semantic_code": f"{q_now:08x}", "perceptual_hash": f"{h_now:08x}",
        "binding_mode": binding_mode, "binding": binding,
        "owner_id": owner.decode("utf-8"), "owners_tested": roster_size,
        "family": FAMILY, "revision": REVISION, "method": METHOD,
        "band": list(f5.BAND), "whitening": f5.WHITENING, "detector_config_id": config.hex(),
        "q_bound": f"{q_bound:08x}",
        "routing": "decoded_semantic_read" if semantic["read"] else "suspect_semantic_recomputed",
        "instance_own_content_status": own_i_status,
        "side_information": ["public OwnerID", "profile", "pinned CLIP weights", "pinned SD1.5 VAE encoder"],
        "fpr_fields_status": "no_calibrated_or_certified_system_FPR",
        "seconds": time.perf_counter() - started,
    }

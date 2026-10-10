"""V1 source-blind three-view VAE-cycle majority readout on unchanged D2 pixels.

Legacy BER and false-positive bound fields are unvalidated for this readout.
"""
from __future__ import annotations
import time
from typing import Mapping, Sequence
import numpy as np
from scripts import f5_latent_codec as f5
v5, base = f5.v5, f5.base
Layout, _semantic_status, BINDINGS = f5.Layout, f5._semantic_status, f5.BINDINGS
BAND, WHITENING = f5.BAND, f5.WHITENING
FAMILY, REVISION = "f5-multiview-majority", 1
READ_THRESHOLD = 8.259326826136963
PRESENCE_THRESHOLD = 4.982033056390042

def extract_views(reader, rgb, return_timings=False):
    """Encode each RGB8 view once; roundtrip posterior mode, decode, clamp/round."""
    views, latents, timings = [np.asarray(rgb, np.uint8)], [], []
    with reader.torch.inference_mode():
        for index in range(3):
            started = time.perf_counter()
            x = reader.tensor(views[index].astype(np.float64) / 255.0)
            unscaled = reader.vae.encode(x * 2 - 1).latent_dist.mode()
            latents.append((unscaled[0] * f5.SCALE).double().cpu().numpy())
            if index < 2:
                y = reader.vae.decode(unscaled).sample[0].permute(1, 2, 0).cpu().numpy()
                views.append(np.rint(np.clip(y * .5 + .5, 0, 1) * 255).astype(np.uint8))
            timings.append(time.perf_counter() - started)
    return (latents, timings) if return_timings else latents


def majority_readout(projections, options, q_now):
    """Select by median normalized gap; exact median tie keeps native q0 bit."""
    if len(projections) != 3 or any(len(p) != v5.CHANNEL_CHIPS for p in projections):
        raise ValueError("Expected three native 320-chip projection vectors")
    native = v5._key_test(projections[0], options, q_now)
    original_q = int(native["code"])
    words, gaps, normalized = [], [], []
    for view in projections:
        word, view_gaps = 0, []
        for segment in range(v5.CODE_BITS):
            chips = view[segment * v5.SEGMENT_CHIPS:(segment + 1) * v5.SEGMENT_CHIPS]
            scores = [sum(sign * value for sign, value in zip(options[segment][bit], chips)) for bit in (0, 1)]
            gap = scores[1] - scores[0]
            bit = v5._bit(original_q, segment) if gap == 0 else int(gap > 0)
            word = (word << 1) | bit
            view_gaps.append(gap)
        words.append(word)
        gaps.append(view_gaps)
        energy = sum(value * value for value in view) ** .5
        normalized.append([gap / energy if energy > 0.0 else 0.0 for gap in view_gaps])
    selected = 0
    for segment in range(v5.CODE_BITS):
        middle = sorted(normalized[v][segment] for v in range(3))[1]
        bit = v5._bit(original_q, segment) if middle == 0 else int(middle > 0)
        selected = (selected << 1) | bit
    selected_score = float(v5._key_test(projections[0], options, selected)["recomputed"])
    if selected_score > float(native["decoded"]) + 1e-12:
        raise AssertionError("Selected pattern exceeds native all-code maximum")
    return {"selected_q": f"{selected:08x}", "original_q": f"{original_q:08x}",
            "view_words": [f"{w:08x}" for w in words], "view_gaps": gaps,
            "view_normalized_gaps": normalized, "changed_bits": (selected ^ original_q).bit_count(),
            "original_selected_score": selected_score, "original_maxscore": float(native["decoded"]),
            "original_recomputed_score": float(native["recomputed"]),
            "q_selection": "median_normalized_native_gaps_exact_zero_tie_original_native_bit"}


def self_check():
    """Small CPU invariants; no encoder, model weights or target q access."""
    import inspect
    options = [[[1.0] * 10, [-1.0] * 10] for _ in range(32)]
    original = [1.0] * 320
    duplicate = majority_readout([original] * 3, options, 0xffffffff)
    native = v5._key_test(original, options, 0xffffffff)
    assert duplicate["selected_q"] == f"{native['code']:08x}"
    assert duplicate["original_selected_score"] == native["decoded"]
    assert (duplicate["original_selected_score"] >= READ_THRESHOLD) == (native["decoded"] >= READ_THRESHOLD)
    tied = majority_readout([original, [0.0] * 320, [-1.0] * 320], options, 0xffffffff)
    assert tied["view_words"][1] == tied["original_q"]
    assert tied["selected_q"] == tied["original_q"]
    assert "q_target" not in inspect.signature(detect_rgb).parameters
    return {"duplicate_native_q_and_read": True, "gap_tie_original_native": True,
            "original_score_bounded_by_native_max": True, "no_target_q_parameter": True}


def detect_rgb(rgb, latents, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float],
               binding_mode: str = "combined", roster_size: int = 1, band=BAND, whitening=WHITENING,
               binding: str = "hard") -> dict[str, object]:
    """Three-view read-conditioned variant of v5 :func:`detect` with the robust tier read from three VAE latents of the suspect (see :class:`Reader`).

    ``binding="soft"`` compares a read semantic code with the suspect's
    features by the maximum-likelihood angle (:func:`soft_angle`, expressed in
    bits) instead of the Hamming distance; radii and decision table unchanged.
    """
    if binding not in BINDINGS:
        raise ValueError("binding must be hard or soft")
    started = time.perf_counter()
    checked, key, config = v5._resolve(profile, None)
    luma = v5.luminance_from_rgb(np.asarray(rgb).tolist())
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    owner = v5.canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(luma, fragile.analysis)
    instance_projections = fragile.projections(coefficients)
    if len(latents) != 3:
        raise ValueError("V1 requires exactly original, first-cycle, second-cycle latents")
    layout = Layout(checked, key, config, owner, band, whitening)
    robust_views = [layout.projections(z) for z in latents]
    robust_chips = robust_views[0]
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)

    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))
    if roster_size != 1:
        raise ValueError("V1 fixed development protocol uses roster_size=1")
    options = v5._semantic_table(owner, key, config)
    evidence = majority_readout(robust_views, options, q_now)
    test = {"recomputed": evidence["original_recomputed_score"],
            "decoded": evidence["original_selected_score"], "code": int(evidence["selected_q"], 16)}
    semantic = v5._channel_result(test, target, roster_size, q_now)
    if semantic["decoded_threshold"] != READ_THRESHOLD or semantic["recomputed_threshold"] != PRESENCE_THRESHOLD:
        raise ValueError("Profile thresholds differ from frozen V1 protocol")
    semantic.update(evidence)
    semantic["decoding_error_rate_status"] = "legacy_heuristic_unvalidated_for_multiview_selection"
    semantic["legacy_fields_status"] = "BER_and_false_positive_bounds_unvalidated_for_multiview_readout"
    s_found = bool(semantic["found"])
    s_status = soft_distance = None
    if s_found:
        s_status, soft_distance = _semantic_status(semantic, semantic_features, key, config, semantic_limits, check_semantic, binding)
    q_bound = int(semantic["decoded_code"], 16) if semantic["read"] else q_now
    routing = "decoded_semantic_read" if semantic["read"] else "suspect_semantic_recomputed"
    table = v5._instance_table(owner, key, config)
    options = [table[segment][v5._bit(q_bound, segment)] for segment in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_projections, options, h_now), target, roster_size, h_now)
    i_found = bool(instance["found"])
    i_status = (
        max(base._content_status(instance["corrected_distance"], *instance_limits, check_instance),
            s_status if s_found else "unchecked",
            key=base._STATUS_RANK.get)
        if i_found else None)
    outcome, state = base._decide(s_found, s_status, i_found, i_status)

    semantic["soft_distance"] = soft_distance

    def public(result, status):
        entry = dict(result)
        entry["content_status"] = status
        entry["content_match"] = bool(result["found"] and base._STATUS_RANK[status] == 0)
        return entry

    return {"outcome": outcome, "proposal_state": state, "watermark_found": bool(s_found or i_found),
            "semantic": public(semantic, s_status), "instance": public(instance, i_status),
            "semantic_code": f"{q_now:08x}", "perceptual_hash": f"{h_now:08x}", "binding_mode": binding_mode,
            "owner_id": owner.decode("utf-8"), "owners_tested": roster_size, "family": FAMILY, "revision": REVISION,
            "band": list(band), "whitening": whitening, "binding": binding, "detector_config_id": config.hex(),
            "side_information": ["public OwnerID", "profile", "pinned CLIP weights", "pinned SD1.5 VAE posterior-mode encoder and decoder"],
            "method": "V1", "routing_revision": 1, "q_bound": f"{q_bound:08x}",
            "routing": routing, "fpr_fields_status": "legacy_model_based_BER_and_false_positive_bounds_unvalidated_for_multiview_readout",
            "instance_own_content_status": base._content_status(instance["corrected_distance"],
                *instance_limits, check_instance) if i_found else None,
            "legacy_profile_family": f5.FAMILY, "legacy_profile_revision": f5.REVISION,
            "seconds": time.perf_counter() - started}

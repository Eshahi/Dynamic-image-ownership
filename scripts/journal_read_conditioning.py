"""F5-RC1 source-blind routed decoder; frozen F5 profile bytes unchanged.

One extraction: read semantic q selects its instance table; otherwise suspect q.
Legacy channel bound fields do not certify this routed system's FPR.
"""
from __future__ import annotations
import time
from typing import Mapping, Sequence
import numpy as np
from scripts import f5_latent_codec as f5
v5, base = f5.v5, f5.base
Layout, _semantic_status, BINDINGS = f5.Layout, f5._semantic_status, f5.BINDINGS
BAND, WHITENING = f5.BAND, f5.WHITENING
FAMILY, REVISION = "f5-read-conditioned-instance", 1

def detect_rgb(rgb, z, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float],
               binding_mode: str = "combined", roster_size: int = 1, band=BAND, whitening=WHITENING,
               binding: str = "hard") -> dict[str, object]:
    """Read-conditioned variant of v5 :func:`detect` with the robust tier read from the VAE latent ``z`` of the suspect (see :class:`Reader`).

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
    robust_chips = Layout(checked, key, config, owner, band, whitening).projections(z)
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)

    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))
    semantic = v5._channel_result(v5._key_test(robust_chips, v5._semantic_table(owner, key, config), q_now),
                                  target, roster_size, q_now)
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
            "side_information": ["public OwnerID", "profile", "pinned CLIP weights", "pinned SD1.5 VAE encoder"],
            "method": "F5-RC1", "routing_revision": 1, "q_bound": f"{q_bound:08x}",
            "routing": routing, "fpr_fields_status": "legacy_model_based_unvalidated_for_routed_system",
            "instance_own_content_status": base._content_status(instance["corrected_distance"],
                *instance_limits, check_instance) if i_found else None,
            "legacy_profile_family": f5.FAMILY, "legacy_profile_revision": f5.REVISION,
            "seconds": time.perf_counter() - started}

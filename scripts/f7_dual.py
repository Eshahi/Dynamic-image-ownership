"""F7: one content-bound code on two carriers, v5's pixel block-DCT carrier and F5's encoder-amplified latent carrier.

Both writers and both readers are the unchanged retained ones. Import needs the standard library only;
embed and read take an encoder_transfer_runtime.Internal, which loads the models.
"""
from __future__ import annotations

import math

import tifs_common as common

UNION_THRESHOLD = 8.341671  # frozen Bentkus-Dzindzalieta bound, 1e-6/2 over 2**32 patterns
COMBINED_SPLIT = 3
SCALES = (1.0, .9, .8, .7)
CUSHION = dict(psnr_db_gt=35.05, ssim_rgb_gt=.901, lpips_lt=.098)


def within_cushion(metrics):
    return common.quality_eligible(metrics, CUSHION["psnr_db_gt"], CUSHION["ssim_rgb_gt"], CUSHION["lpips_lt"])


def embed(internal, rgb, base, owner_id, scales=SCALES, f5_overrides=None):
    """v5 first, then F5 on top with the same features, so one q rides on both carriers."""
    import numpy as np
    source = np.asarray(rgb, np.uint8)
    features = internal.features(source, 7)
    v5_list, v5_report = internal.v5.embed_rgb(source.tolist(), owner_id, profile=internal.profile,
                                               semantic_features=features, strict=False)
    v5_marked = np.asarray(v5_list, np.float64)
    params = dict(base["f5"], **(f5_overrides or {}))
    params.pop("semantic_views")
    attempts = []
    for scale in scales:
        start = np.clip(np.rint(source + scale * (v5_marked - source)), 0, 255).astype(np.uint8)
        marked, report = internal.f5.embed_rgb(start, owner_id, internal.profile, features, internal.reader, **params)
        metrics = internal.metrics(source, marked)
        attempts.append(dict(v5_scale=scale, metrics=metrics))
        if within_cushion(metrics):
            break
    payload = dict(q=report["semantic_code"], h=report["verification"]["instance"].get("decoded_code"),
                   v5_q=v5_report["semantic_code"], h_target_basis="native clean decoded h after the F5 second tier")
    summary = dict(family="f7-dual-carrier", v5_scale=attempts[-1]["v5_scale"], attempts=attempts,
                   v5=dict((k, v5_report.get(k)) for k in ("semantic_code", "rgb_psnr_db", "robust_psnr_db", "verified")),
                   f5=dict((k, report.get(k)) for k in ("semantic_code", "rgb_psnr_db", "margin_median", "margin_min",
                                                         "negative_chips", "verified")),
                   same_q=payload["q"] == payload["v5_q"])
    return marked, payload, summary


def combined(internal, rgb, latent, owner_id, features):
    """Key test on the sum of the two unit-length chip vectors, normalized by its own length (exploratory)."""
    import numpy as np
    v5, f5 = internal.v5, internal.f5
    checked, key, config = v5._resolve(internal.profile, None)
    owner = v5.canonical_owner(owner_id)
    luma = v5.luminance_from_rgb(np.asarray(rgb).tolist())
    a = np.asarray(f5.Layout(checked, key, config, owner).projections(latent), np.float64)
    carrier = v5._robust_carrier(key, config, owner, len(checked["robust_frequencies"]))
    b = np.asarray(v5._Robust(v5._coarse(luma), luma, checked, carrier).projections, np.float64)
    if not (np.linalg.norm(a) > 0 and np.linalg.norm(b) > 0):
        return dict(read=False, found=False, decoded_score=0.0, content_match=False, status="zero projections")
    chips = (a / np.linalg.norm(a) + b / np.linalg.norm(b)).tolist()
    q_now = v5._semantic(v5.base._analyse(luma, ())[0], checked, key, config, features, binding=False)
    target = float(checked["decision"]["false_positive_target"]) / COMBINED_SPLIT
    result = v5._channel_result(v5._key_test(chips, v5._semantic_table(owner, key, config), q_now), target, 1, q_now)
    limits = (int(checked["decision"]["semantic_radius"]), int(checked["decision"]["semantic_mismatch_distance"]))
    status, distance = (f5._semantic_status(result, features, key, config, limits, True, "soft") if result["read"]
                        else (None, None))
    return dict(result, content_status=status, soft_distance=distance,
                content_match=bool(result["read"] and status == "match"))


def read(internal, rgb, owner_id, features=None, latent=None, mode="combined"):
    """Both unchanged readers on the same suspect, with 7-view features, plus the exploratory combined test."""
    features = features if features is not None else internal.features(rgb, 7)
    latent = latent if latent is not None else internal.reader.latent(rgb)
    raw = dict(f5=internal._detect(rgb, "f5", owner_id, features, latent, mode=mode),
               v5=internal._detect(rgb, "v5", owner_id, features, None, mode=mode))
    raw["combined"] = combined(internal, rgb, latent, owner_id, features)
    return raw


def carrier_c(raw, payload, threshold=UNION_THRESHOLD):
    """C of one carrier at the union threshold; J likewise. Missing data stays None."""
    if not isinstance(raw, dict) or not isinstance(raw.get("semantic"), dict):
        return None, None
    score = raw["semantic"].get("decoded_score")
    if not common._finite(score):
        return None, None
    rules = common.predicates(raw, payload)
    strong = score >= threshold
    return rules["C"] and strong, rules["J"] and strong


def endpoints(raw, payload):
    """F7's frozen endpoints. C and J are either carrier at the union threshold. F, H and A count either reader,
    since both read the one shared second tier; D is H and J."""
    per = {name: carrier_c(raw.get(name), payload) for name in ("f5", "v5")}
    rules = {name: common.predicates(raw[name], payload) if isinstance(raw.get(name), dict) else None for name in ("f5", "v5")}
    def either(values):
        return True if True in values else None if None in values else False
    def both(values):
        return False if False in values else None if None in values else True
    def tier(key):
        return either([None if r is None else r[key] for r in rules.values()])
    j = either([value for _, value in per.values()])
    combined_raw = raw.get("combined") or {}
    combined_score = combined_raw.get("decoded_score")
    return dict(C=either([value for value, _ in per.values()]), J=j, F=tier("F"), H=tier("H"), A=tier("A"),
                D=both([tier("H"), j]), D_and_F=both([tier("H"), j, tier("F")]),
                C_f5=per["f5"][0], C_v5=per["v5"][0],
                C_f5_alpha=None if rules["f5"] is None else rules["f5"]["C"],
                C_v5_alpha=None if rules["v5"] is None else rules["v5"]["C"],
                C_combined=bool(combined_raw.get("content_match")) if common._finite(combined_score) else None,
                decoded_scores=dict(f5=(raw.get("f5") or {}).get("semantic", {}).get("decoded_score"),
                                    v5=(raw.get("v5") or {}).get("semantic", {}).get("decoded_score"),
                                    combined=combined_score))


def summary_raw(raw):
    """A semantic block for the shared summaries: the stronger carrier's decoded score."""
    scores = [(raw.get(n) or {}).get("semantic", {}).get("decoded_score") for n in ("f5", "v5")]
    scores = [s for s in scores if common._finite(s)]
    best = max(scores) if scores else None
    matched = any((raw.get(n) or {}).get("outcome") == "both_match" for n in ("f5", "v5"))
    return dict(semantic=dict(decoded_score=best, read=bool(best is not None and best >= UNION_THRESHOLD)),
                carriers=raw, outcome="both_match" if matched else (raw.get("f5") or {}).get("outcome"))


def check_threshold(v5_module):
    """The constant above must equal the frozen bound; called once at server start."""
    value = v5_module._threshold(1e-6 / 2, 2 ** 32)
    if not math.isclose(value, UNION_THRESHOLD, abs_tol=1e-5):
        raise ValueError("Union threshold differs from the frozen bound: %.6f" % value)
    return value

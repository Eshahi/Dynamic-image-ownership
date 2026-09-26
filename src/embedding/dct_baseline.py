"""C7 classical pixel-domain comparator, not the proposed latent method.

Native canonical RGB8 and already-extracted enrollment codes are caller inputs.
No model/file/dataset access, threshold, image-derived semantic extraction,
calibration, full blind detection, approval creation or execution CLI.
"""
from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass

from scripts.pixel_dct_control import embed_pixel_dct, templates_from_keys, dct_observations, score_observations
from src.runtime.config import strict_json_bytes
from src.signatures.owner import derive_public_signatures, wrong_owner_control

FIXED = {"schema_version":"c7-pixel-dct-component-v1",
    "role":"classical_positive_control_not_proposed_latent_method",
    "output":"native_rgb8_clamp_nearest_ties_even",
    "score":"enrollment_template_diagnostic_only_no_threshold",
    "calibration":"absent_decision_prohibited"}


@dataclass(frozen=True)
class BaselineConfig:
    raw: bytes
    sha256: str


def _config(raw):
    if not isinstance(raw, bytes) or len(raw) > 8192:
        raise ValueError("bounded immutable baseline JSON required")
    value = strict_json_bytes(raw)
    if not isinstance(value, dict) or set(value) != set(FIXED)|{"semantic_gain","instance_gain","maximum_native_side"}:
        raise ValueError("exact baseline component fields required")
    if any(value[k] != v for k, v in FIXED.items()):
        raise ValueError("baseline role or decision boundary changed")
    for key in ("semantic_gain", "instance_gain"):
        gain = value[key]
        if type(gain) not in (int, float) or not math.isfinite(gain) or not 0 < gain <= 1:
            raise ValueError("positive finite DCT coefficient gain <=1 required")
    side = value["maximum_native_side"]
    if type(side) is not int or not 32 <= side <= 1024:
        raise ValueError("bounded native dimension required; no implicit resize")
    return value


def load_config_bytes(raw):
    _config(raw)
    return BaselineConfig(raw, hashlib.sha256(raw).hexdigest())


def _checked(config):
    if type(config) is not BaselineConfig or hashlib.sha256(config.raw).hexdigest() != config.sha256:
        raise ValueError("exact baseline config bytes required")
    return _config(config.raw)


def pixel_identity(rgb8, width, height):
    if (type(width) is not int or type(height) is not int or not 32 <= width <= 1024
            or not 32 <= height <= 1024 or not isinstance(rgb8, bytes) or len(rgb8) != 3*width*height):
        raise ValueError("immutable native RGB8 dimensions32..1024 required")
    return hashlib.sha256(b"b5-rgb8-srgb-v1\0"+struct.pack(">II", width, height)+rgb8).hexdigest()


def _digest(digest):
    if not isinstance(digest, bytes) or len(digest) != 32 or not any(digest):
        raise ValueError("nonzero caller-validated detector digest required")


@dataclass(frozen=True)
class ControlPair:
    source: bytes
    marked: bytes
    receipt: dict


def embed_control(rgb8, width, height, q, h, owner_id, detector_id, config):
    """Pure component: same public protocol, templates/grid, two fixed gains.

    q/h are explicitly source enrollment inputs; their image linkage and the
    static detector digest must be validated by a future reviewed orchestration.
    Returned scores are NOT the proposal-faithful blind detector.
    """
    value = _checked(config)
    source_hash = pixel_identity(rgb8, width, height)
    if max(width, height) > value["maximum_native_side"]:
        raise ValueError("unsupported native resolution; no resize/fallback")
    _digest(detector_id)
    keys = derive_public_signatures(q, h, owner_id)
    templates = templates_from_keys(keys.semantic, keys.instance, detector_id, width, height)
    marked = embed_pixel_dct(rgb8, width, height, *templates,
        semantic_gain=value["semantic_gain"], instance_gain=value["instance_gain"])
    marked_hash = pixel_identity(marked, width, height)
    mse = math.fsum(((a-b)/255)**2 for a, b in zip(rgb8, marked))/len(rgb8)
    # JSON cannot represent infinite PSNR. Identity is explicit, not an error
    # or a fabricated zero-distortion efficacy score.
    quality = {"rgb_mse":mse, "PSNR_dB":None if mse == 0 else -10*math.log10(mse),
               "PSNR_status":"infinite_identity" if mse == 0 else "finite",
               "SSIM":"NOT_RUN", "LPIPS":"NOT_RUN"}
    blocks = ((width+7)//8)*((height+7)//8)
    return ControlPair(rgb8, marked, {"schema_version":"c7-control-pair-v1",
        "role":FIXED["role"], "configuration_sha256":config.sha256,
        "detector_config_id":detector_id.hex(), "owner_id":keys.owner_id,
        "source_q":q.hex(), "source_h":h.hex(), "Ws":keys.semantic.hex(), "Wi":keys.instance.hex(),
        "code_origin":"caller_supplied_enrollment_not_image_extraction",
        "detector_identity_validation":"caller_obligation_not_completed_by_component",
        "width":width, "height":height, "source_pixel_sha256":source_hash,
        "marked_pixel_sha256":marked_hash, "unmarked_control_pixel_sha256":source_hash,
        "semantic_gain":value["semantic_gain"], "instance_gain":value["instance_gain"],
        "coefficient_slots_per_component":4*blocks,
        "capacity_interpretation":"repeated_public_digest_template_not_independent_payload_bits",
        "numerical_profile":"b2-scalar-byte255-f64-luminance-fsum-dct8-v1",
        "quality_versus_source_rgb8":quality, "PNG_custody":"NOT_RUN",
        "calibrated_decision":"PROHIBITED", "blind_verification":"NOT_RUN",
        "scientific_acceptance":False})


def oracle_component_scores(rgb8, width, height, q, h, owner_id, detector_id, *, wrong_owner=None):
    """One supplied-code oracle diagnostic, never image-based key recomputation."""
    pixel_identity(rgb8, width, height); _digest(detector_id)
    keys = derive_public_signatures(q, h, owner_id)
    owners = [("supplied_owner", keys)]
    if wrong_owner is not None:
        _, wrong = wrong_owner_control(q, h, owner_id, wrong_owner)
        owners.append(("wrong_owner", wrong))
    observations = dct_observations(rgb8, width, height)
    rows = []
    for label, signatures in owners:
        templates = templates_from_keys(signatures.semantic, signatures.instance, detector_id, width, height)
        row = {"owner_condition":label, "owner_id":signatures.owner_id}
        for component, template in zip(("semantic", "instance"), templates):
            score, zero_variance = score_observations(observations[component], template)
            row[component] = {"score":score, "zero_variance":zero_variance}
        rows.append(row)
    return {"knowledge_profile":"enrollment_codes_oracle_diagnostic_not_blind",
            "numerical_profile":"b2-scalar-byte255-f64-luminance-fsum-dct8-v1",
            "rows":rows, "tested_owner_count":len(rows), "decision":"PROHIBITED",
            "scientific_acceptance":False}

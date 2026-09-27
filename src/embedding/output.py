"""Local-only C4 diagnostic PNG pair custody; no scientific success verdict.

Only an approved worker may use this on study/model outputs. Owned synthetic
tests may exercise byte custody and failure retention without a model.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .proposed import ContinuousCandidate, EmbeddingError
from .config_binding import bind_settings, validate_loaded_snapshot


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False,
                      ensure_ascii=True).encode("ascii")


def _write_new(path, raw):
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def enroll_canonical(rgb8, encoder, projection_seed, owner_id):
    """Real source C2/C3b extraction only inside an approved worker.

    No supplied/oracle feature vector, image caption or final-output re-signing.
    """
    from src.data.preprocess import pixel_sha
    from src.signatures.semantic import extract_features, quantize_features
    from src.signatures.instance import bind_canonical_image
    pixels = rgb8.copy()
    identity = pixel_sha(pixels)
    features = extract_features(pixels, encoder)
    q = quantize_features(features, projection_seed)
    h, keys = bind_canonical_image(pixels.tobytes(), pixels.shape[1], pixels.shape[0], q.packed, owner_id)
    return {"canonical_pixel_sha256": identity, "q": q.packed.hex(), "h": h.packed.hex(),
            "Ws": keys.semantic.hex(), "Wi": keys.instance.hex(), "OwnerID": keys.owner_id,
            "semantic_projection_margins": list(q.projections),
            "phash_minimum_margin": h.minimum_selected_margin,
            "profile": "source-extraction-public-derived-not-ownership-authentication"}


class TrialStore:
    """Output custody under an existing runner artifact root, not a scheduler.

    Every trial starts before model computation. Failed/partial files are never
    overwritten or cleaned. File-system adversarial concurrent mutation is not
    a security guarantee; callers serialize writers and own the artifact root.
    """
    def __init__(self, parent: Path, *, source_id, seed, method_config, source_raw_hash, source_rgb8):
        from src.data.preprocess import no_links, pixel_sha, normalized
        if not isinstance(source_id, str) or not 1 <= len(source_id) <= 256:
            raise EmbeddingError("source_id must be bounded text")
        if type(seed) is not int or not 0 <= seed < 2**64:
            raise EmbeddingError("seed must be uint64")
        from .proposed import Settings
        config = validate_loaded_snapshot(method_config)
        config_hash = method_config.sha256
        for digest in (config_hash, source_raw_hash):
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise EmbeddingError("trial digests must be lowercase SHA-256")
        parent = Path(parent)
        no_links(parent)
        if not parent.is_dir():
            raise EmbeddingError("existing runner artifact directory required")
        self._source = source_rgb8.copy()
        pixel_hash = pixel_sha(self._source)
        if min(self._source.shape[:2]) < 32:
            raise EmbeddingError("native image too small")
        source_tensor_hash = hashlib.sha256(normalized(self._source).transpose(2, 0, 1).astype("<f4").tobytes(order="C")).hexdigest()
        self._binding = bind_settings(method_config, Settings.from_embedding_config(config["embedding"]),
            seed, bytes.fromhex(config["dct"]["config_id"]), source_tensor_sha256=source_tensor_hash)
        self.directory = Path(tempfile.mkdtemp(prefix="c4-trial-", dir=parent))
        self.identity = {"source_id": source_id, "seed": seed, "config_hash": config_hash,
                         "config_profile": config["profile"], "calibration": config["calibration"],
                         "schema_hash": self._binding.schema_hash,
                         "detector_config_id": self._binding.detector_config_id,
                         "settings_hash": hashlib.sha256(self._binding.settings_json).hexdigest(),
                         "source_tensor_hash": source_tensor_hash,
                         "source_raw_hash": source_raw_hash, "source_pixel_hash": pixel_hash,
                         "native_hwc": list(self._source.shape), "scope": "local-only-diagnostic-candidate"}
        self._identity_bytes = _json(self.identity)
        self._finished = False
        _write_new(self.directory/"method-config.json", method_config.raw)
        _write_new(self.directory/"start.json", _json({**self.identity, "status": "started_before_computation"}))
        _write_new(self.directory/"trajectory.jsonl", b"")

    def record(self, row):
        if self._finished:
            raise EmbeddingError("trial already finalized")
        raw = _json(row)+b"\n"
        with (self.directory/"trajectory.jsonl").open("ab") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())

    def fail(self, error):
        if self._finished:
            raise EmbeddingError("trial already finalized")
        # Keep exception type, never raw model/prompt metadata or private text.
        _write_new(self.directory/"failed.json", _json({**json.loads(self._identity_bytes),
                    "status": "failed", "error_type": type(error).__name__}))
        self._finished = True

    def save_pair(self, candidate: ContinuousCandidate, safety_checker):
        """Save/decode both PNGs and check those decoded pixels, not floats.

        Candidate status never becomes success merely from file/safety checks.
        Full q/h drift, blind detector, SSIM/LPIPS and target acceptance pending.
        """
        import numpy as np
        import torch
        from src.data.preprocess import encode_output, normalized, pixel_sha
        if self._finished or not isinstance(candidate, ContinuousCandidate):
            raise EmbeddingError("new typed candidate required")
        if _json(self.identity) != self._identity_bytes:
            raise EmbeddingError("trial identity mutated")
        h, w = self._source.shape[:2]
        if (candidate.metadata.get("native_shape") != [1, 3, h, w]
                or candidate.metadata.get("seed") != self.identity["seed"]
                or candidate.metadata.get("source_sha256") != self.identity["source_raw_hash"]
                or candidate.metadata.get("control") is not False):
            raise EmbeddingError("candidate/source trial identity mismatch")
        if (candidate.config_binding != self._binding
                or candidate.metadata.get("method_config_sha256") != self._binding.config_hash
                or candidate.metadata.get("detector_config_id") != self._binding.detector_config_id
                or candidate.metadata.get("settings_sha256") != self.identity["settings_hash"]
                or candidate.metadata.get("source_tensor_sha256") != self.identity["source_tensor_hash"]):
            raise EmbeddingError("candidate computation configuration differs from trial binding")
        rows, decoded_pair = [], {}
        for label, tensor in (("matched_control", candidate.matched_control), ("marked_candidate", candidate.image)):
            if not isinstance(tensor, torch.Tensor) or tuple(tensor.shape) != (1, 3, h, w) or tensor.dtype != torch.float32:
                raise EmbeddingError("native float32 output pair required")
            pixels = tensor.detach().cpu()[0].permute(1, 2, 0).numpy()
            raw, decoded = encode_output(pixels)
            path = self.directory/(label+".png")
            _write_new(path, raw)
            # Reopen the persisted bytes; don't substitute a pre-save image.
            saved = path.read_bytes()
            if saved != raw:
                raise EmbeddingError("persisted PNG differs from encoder output")
            self.record({"phase": "png_saved_before_safety", "kind": label,
                         "output_path": path.name, "output_hash": hashlib.sha256(saved).hexdigest(),
                         "output_pixel_hash": pixel_sha(decoded)})
            flag = safety_checker(decoded.copy())
            if type(flag) is not bool:
                raise EmbeddingError("safety checker must return one explicit boolean")
            decoded_pair[label] = decoded
            original = normalized(self._source).astype(np.float64)
            output = normalized(decoded).astype(np.float64)
            mse = float(np.mean((output-original)**2))
            rows.append({**self.identity, "kind": label, "output_path": path.name,
                         "output_hash": hashlib.sha256(saved).hexdigest(), "output_bytes": len(saved),
                         "output_pixel_hash": pixel_sha(decoded), "safety_flagged": flag,
                         "mse_vs_source_decoded_png": mse,
                         "SSIM": "NOT_RUN", "LPIPS": "NOT_RUN", "blind_verification": "NOT_RUN"})
            self.record({"phase": "output_safety_completed", "result": rows[-1]})
        status = "failed_safety_flagged" if any(row["safety_flagged"] for row in rows) else "saved_pair_pending_metrics_and_blind_verification"
        receipt = {"schema_version": "c4-local-output-pair-v1", "status": status, "rows": rows,
                   "candidate_metadata": candidate.metadata, "scientific_acceptance": False}
        _write_new(self.directory/"pair.json", _json(receipt))
        self._finished = True
        return receipt, decoded_pair

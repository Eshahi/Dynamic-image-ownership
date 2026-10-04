"""Tensor-only adapter for the original unmarked 200-update reconstruction.

No source resolver, dataset admission, model loading or scientific authorization.
Checkpoint hashes detect accidental corruption, not hostile forgery.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import random

import numpy as np
import torch
from torch.utils.checkpoint import checkpoint

CONFIG = {"updates": 200, "learning_rate": 0.02, "precision": "float32",
          "objective": "RGB pixel MSE before clamp", "decoder_checkpoint": True,
          "observation_steps": [0, 50, 100, 200],
          "latent_units": "unscaled VAE posterior mode; decoder receives same units",
          "rgb8": "clamp0..1, HWC numpy float32 times255, numpy round, uint8"}
SCHEMA = "m1-original-source-initialization-v1"


def digest(value):
    """Stable content digest including every tensor byte; independent of torch.save."""
    h = hashlib.sha256()
    def visit(v):
        if isinstance(v, torch.Tensor):
            x = v.detach().cpu().contiguous()
            h.update(b"tensor" + str(x.dtype).encode())
            visit(list(x.shape))
            h.update(x.reshape(-1).view(torch.uint8).numpy().tobytes())
        elif isinstance(v, dict):
            h.update(b"dict")
            for k in sorted(v, key=lambda k: (type(k).__name__, str(k))):
                visit(k); visit(v[k])
        elif isinstance(v, (list, tuple)):
            h.update(type(v).__name__.encode())
            visit(len(v))
            for item in v:
                visit(item)
        else:
            h.update(type(v).__name__.encode() + b":" +
                     json.dumps(v, allow_nan=False, sort_keys=True).encode() + b";")
    visit(value)
    return h.hexdigest()


def _cpu_tree(value):
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {k: _cpu_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_cpu_tree(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_cpu_tree(v) for v in value)
    return copy.deepcopy(value)


def _rng():
    n = np.random.get_state()
    return {"python": random.getstate(), "numpy": [n[0], n[1].tolist(), n[2], n[3], n[4]],
            "torch": torch.get_rng_state().clone(),
            "cuda": [v.cpu().clone() for v in torch.cuda.get_rng_state_all()]
                    if torch.cuda.is_initialized() else []}


def _restore_rng(state):
    random.setstate(state["python"])
    n = state["numpy"]
    np.random.set_state((n[0], np.asarray(n[1], dtype=np.uint32), n[2], n[3], n[4]))
    torch.set_rng_state(state["torch"])
    if state["cuda"]:
        if not torch.cuda.is_initialized() or len(state["cuda"]) != torch.cuda.device_count():
            raise ValueError("CUDA RNG device topology differs")
        torch.cuda.set_rng_state_all(state["cuda"])


def _runtime(target):
    cuda_initialized = torch.cuda.is_initialized()
    device = torch.cuda.get_device_properties(target.device) if cuda_initialized and target.device.type == "cuda" else None
    return {"torch_version": str(torch.__version__), "numpy_version": np.__version__,
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "cuda_version": torch.version.cuda,
            # cuDNN version lookup initializes CUDA on this bundled Torch build.
            # Never perform it for a CPU session with no existing CUDA context.
            "cudnn_version": torch.backends.cudnn.version() if cuda_initialized else None,
            "cuda_device_name": device.name if device is not None else None,
            "cuda_device_capability": [device.major, device.minor] if device is not None else None,
            "device": str(target.device), "threads": torch.get_num_threads(),
            "deterministic": torch.are_deterministic_algorithms_enabled(),
            "deterministic_warn_only": torch.is_deterministic_algorithms_warn_only_enabled(),
            "matmul_tf32": torch.backends.cuda.matmul.allow_tf32,
            "cudnn_tf32": torch.backends.cudnn.allow_tf32,
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "cuda_rng_devices": torch.cuda.device_count() if cuda_initialized else 0}


def _validate_payload(payload, identity, target_hash, runtime):
    if not isinstance(payload, dict):
        raise ValueError("Checkpoint must be a dictionary")
    body = {k: v for k, v in payload.items() if k != "integrity_sha256"}
    if payload.get("integrity_sha256") != digest(body):
        raise ValueError("Checkpoint content integrity mismatch")
    if payload.get("schema") != SCHEMA or payload.get("config") != CONFIG:
        raise ValueError("Checkpoint schema/config differs")
    if payload.get("identity") != identity or payload.get("target_sha256") != target_hash:
        raise ValueError("Checkpoint source/model identity differs")
    if payload.get("runtime") != runtime:
        raise ValueError("Checkpoint runtime differs")
    step = payload.get("step")
    if type(step) is not int or not 0 <= step <= 200:
        raise ValueError("Invalid completed-update count")
    observations = payload.get("observations")
    if not isinstance(observations, dict) or set(observations) != {
            s for s in CONFIG["observation_steps"] if s <= step}:
        raise ValueError("Observation coverage differs from step")
    for key in ("z", "initial"):
        x = payload.get(key)
        if not isinstance(x, torch.Tensor) or x.dtype != torch.float32 or not torch.isfinite(x).all():
            raise ValueError("Invalid FP32 latent checkpoint")
    if payload["z"].shape != payload["initial"].shape:
        raise ValueError("Latent shapes differ")
    optim = payload.get("optimizer", {})
    groups = optim.get("param_groups", [])
    expected = torch.optim.Adam([torch.zeros(1, requires_grad=True)], lr=.02).state_dict()["param_groups"]
    if groups != expected:
        raise ValueError("Adam parameter configuration differs")
    state = optim.get("state", {})
    if step == 0:
        if state:
            raise ValueError("Adam state exists before first update")
    else:
        if set(state) != {0} or set(state[0]) != {"step", "exp_avg", "exp_avg_sq"}:
            raise ValueError("Incomplete Adam state")
        if float(state[0]["step"]) != step:
            raise ValueError("Adam completed-update count differs")
        for key in ("exp_avg", "exp_avg_sq"):
            x = state[0][key]
            if x.shape != payload["z"].shape or x.dtype != torch.float32 or not torch.isfinite(x).all():
                raise ValueError("Invalid Adam moment")


class ReconstructionSession:
    """Own exactly one latent; caller supplies an admitted canonical target/model.

    ``step`` counts completed Adam updates. Observation step200 is the final
    updated latent, never a best checkpoint. Tiny RGB shapes are supported only
    to permit CPU mechanics fixtures; scientific canonicalization belongs upstream.
    """
    def __init__(self, target, vae, identity, *, resume=None):
        if (not isinstance(target, torch.Tensor) or target.dtype != torch.float32 or
                target.ndim != 4 or target.shape[0:2] != (1, 3) or target.requires_grad or
                not torch.isfinite(target).all() or not bool(((target >= 0) & (target <= 1)).all())):
            raise ValueError("Target must be finite detached FP32 NCHW RGB batch1 in [0,1]")
        if (not isinstance(identity, dict) or not identity.get("source_id") or
                not identity.get("model_sha256") or not identity.get("source_rgb8_sha256")):
            raise ValueError("Explicit source ID/canonical RGB8 hash/model hash required")
        json.dumps(identity, sort_keys=True, allow_nan=False)
        if vae.training or any(p.requires_grad or p.dtype != torch.float32 or p.device != target.device
                               for p in vae.parameters()):
            raise ValueError("VAE must be eval, frozen FP32, on target device")
        self.target = target.detach().clone()
        self.vae = vae
        self.identity = copy.deepcopy(identity)
        self.target_hash = digest(self.target)
        self.runtime = _runtime(target)
        if resume is not None:
            _validate_payload(resume, self.identity, self.target_hash, self.runtime)
            self.initial = resume["initial"].to(target.device).clone()
            self.z = resume["z"].to(target.device).clone().requires_grad_(True)
            self.optimizer = torch.optim.Adam([self.z], lr=.02)
            self.optimizer.load_state_dict(copy.deepcopy(resume["optimizer"]))
            self.step = resume["step"]
            self.observations = _cpu_tree(resume["observations"])
            _restore_rng(resume["rng"])
        else:
            with torch.no_grad():
                self.initial = vae.encode(self.target*2-1).latent_dist.mode().detach().clone()
            if self.initial.dtype != torch.float32 or not torch.isfinite(self.initial).all():
                raise ValueError("Posterior mode must be finite FP32")
            self.z = self.initial.detach().clone().requires_grad_(True)
            self.optimizer = torch.optim.Adam([self.z], lr=.02)
            self.step = 0
            self.observations = {}
            self._observe()

    def decode(self, latent):
        return (self.vae.decode(latent, return_dict=False)[0]+1)/2

    def _observe(self):
        if self.step in CONFIG["observation_steps"] and self.step not in self.observations:
            with torch.no_grad():
                raw = self.decode(self.z)
                if raw.shape != self.target.shape or not torch.isfinite(raw).all():
                    raise RuntimeError("Invalid decoded RGB observation")
                rgb = (raw.clamp(0,1)[0].permute(1,2,0).cpu().numpy()*255).round().astype(np.uint8)
                self.observations[self.step] = {
                    "rgb8": torch.from_numpy(rgb.copy()),
                    "objective_float_mse": float((raw-self.target).square().mean().item()),
                    "latent_displacement_l2": float(torch.linalg.vector_norm(self.z-self.initial).item())}

    def advance(self, to_step=200, *, on_update=None):
        if type(to_step) is not int or not self.step <= to_step <= 200:
            raise ValueError("Requested step must be between current step and200")
        while self.step < to_step:
            self.optimizer.zero_grad(set_to_none=True)
            decoded = checkpoint(self.decode, self.z, use_reentrant=False)
            loss = (decoded-self.target).square().mean()
            if not bool(torch.isfinite(loss)):
                raise RuntimeError("Nonfinite loss")
            loss.backward()
            if self.z.grad is None or not bool(torch.isfinite(self.z.grad).all()):
                raise RuntimeError("Missing/nonfinite latent gradient")
            self.optimizer.step()
            if not bool(torch.isfinite(self.z).all()):
                raise RuntimeError("Nonfinite latent after optimizer update")
            self.step += 1
            self._observe()
            if on_update is not None:
                on_update(self)
        return self

    def state_dict(self):
        body = {"schema": SCHEMA, "config": copy.deepcopy(CONFIG),
                "identity": copy.deepcopy(self.identity), "target_sha256": self.target_hash,
                "runtime": copy.deepcopy(self.runtime), "step": self.step,
                "initial": _cpu_tree(self.initial), "z": _cpu_tree(self.z),
                "optimizer": _cpu_tree(self.optimizer.state_dict()),
                "observations": _cpu_tree(self.observations), "rng": _rng()}
        return {**body, "integrity_sha256": digest(body)}

    def save(self, path):
        path = Path(path)
        temp = path.with_name(path.name + ".tmp")
        if path.exists() or temp.exists():
            raise FileExistsError("Checkpoint destination or temporary file already exists")
        # Exclusive creation preserves retained temporary receipts. Windows rename
        # refuses an existing destination; hard-link commit provides that same
        # no-overwrite boundary on other hosts while retaining atomic visibility.
        with temp.open("xb") as handle:
            torch.save(self.state_dict(), handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp, path)
        temp.unlink()

    def final(self):
        if self.step != 200:
            raise ValueError("Final reconstruction requires exactly200 updates")
        return {"z": _cpu_tree(self.z), "initial": _cpu_tree(self.initial),
                "step": 200, "latent_units": CONFIG["latent_units"],
                **_cpu_tree(self.observations[200])}


def load_checkpoint(path):
    """Load a locally owned receipt without enabling pickle code execution."""
    return torch.load(Path(path), map_location="cpu", weights_only=True)


def reconstruct_source(target, vae, identity, *, resume=None, on_update=None):
    session = ReconstructionSession(target, vae, identity, resume=resume)
    session.advance(200, on_update=on_update)
    return session.final()

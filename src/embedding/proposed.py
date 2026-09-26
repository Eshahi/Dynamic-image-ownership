"""A5 differentiable existing-image component path, not a detector or runner.

No weights, files, images, network, or GPU are loaded at import. Callers must
bind verified components, a validated method config and approved execution
manifest. Returned continuous tensors are NOT accepted watermarked images:
PNG roundtrip, safety, quality metrics and blind verification remain mandatory.
Arithmetic profile: float32 model path, float64 centered DCT objective, explicit
Adam and L2 projection. Only the perturbation u is optimized.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from scripts.base_noise_reference import base_noise_f32le, unit_carrier_f32le
from scripts.noise_path_reference import leading_suffix
from scripts.pixel_dct_control import template_from_key


class EmbeddingError(ValueError):
    """Fail-closed component error; retain the caller's failed case record."""


def _torch():
    import torch
    return torch


def _finite_tensor(tensor, name):
    torch = _torch()
    if not isinstance(tensor, torch.Tensor) or not torch.isfinite(tensor).all().item():
        raise EmbeddingError(f"{name}: nonfinite or non-tensor")


def _digest(value, name):
    if not isinstance(value, bytes) or len(value) != 32:
        raise EmbeddingError(f"{name} must be raw SHA-256 bytes")


@dataclass(frozen=True)
class Settings:
    """Explicit component parameters, not a substitute for C1 full validation."""
    inference_steps: int
    strength: float
    vae_scale: float
    maximum_side: int
    alpha_s: float
    alpha_i: float
    rho: float
    learning_rate: float
    iterations: int
    lambda_q: float
    lambda_r: float
    lambda_s: float
    lambda_i: float
    margin_s: float
    margin_i: float

    def __post_init__(self):
        leading_suffix(self.inference_steps, self.strength)
        if type(self.maximum_side) is not int or not 256 <= self.maximum_side <= 8192 or self.maximum_side % 64:
            raise EmbeddingError("maximum_side must be 256..8192, multiple of 64")
        if type(self.iterations) is not int or not 1 <= self.iterations <= 10000:
            raise EmbeddingError("iterations must be 1..10000")
        for name in ("vae_scale", "alpha_s", "alpha_i", "rho", "learning_rate",
                     "lambda_q", "lambda_r", "lambda_s", "lambda_i", "margin_s", "margin_i"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise EmbeddingError(f"{name} must be a finite real number")
        if not 0 < self.vae_scale <= 1 or min(self.alpha_s, self.alpha_i) < 0:
            raise EmbeddingError("invalid scale or carrier gains")
        if min(self.rho, self.learning_rate, self.lambda_q, self.lambda_r, self.lambda_s, self.lambda_i) <= 0:
            raise EmbeddingError("radius, learning rate and loss weights must be positive")
        if not -1 <= self.margin_s <= 1 or not -1 <= self.margin_i <= 1:
            raise EmbeddingError("margins must be in [-1,1]")

    @classmethod
    def from_embedding_config(cls, value):
        # Call only after C1 load_method_config validates the entire object.
        return cls(value["scheduler"]["inference_steps"], value["scheduler"]["strength"],
                   value["vae_scale"], value["working_image"]["maximum_side"],
                   value["alpha_s"], value["alpha_i"], value["rho"],
                   value["optimizer"]["learning_rate"], value["optimizer"]["iterations"],
                   **value["loss"])


def padded_source(source, maximum_side):
    torch = _torch()
    _finite_tensor(source, "source")
    if source.dtype != torch.float32 or source.ndim != 4 or tuple(source.shape[:2]) != (1, 3):
        raise EmbeddingError("source must be float32 [1,3,H,W]")
    height, width = source.shape[-2:]
    if min(height, width) < 32 or max(height, width) > maximum_side:
        raise EmbeddingError("unsupported_input_resolution")
    if source.min().item() < 0 or source.max().item() > 1 or source.requires_grad:
        raise EmbeddingError("source must be fixed canonical pixels in [0,1]")
    return torch.nn.functional.pad(source, (0, (-width) % 64, 0, (-height) % 64), mode="replicate")


def latent_streams(seed, source_digest, ws, wi, config_id, height, width, device):
    """Reuse the A6 byte-tested stream, capped at one million elements."""
    torch = _torch()
    for value, name in ((source_digest, "source"), (ws, "Ws"), (wi, "Wi"), (config_id, "config ID")):
        _digest(value, name)
    if type(height) is not int or type(width) is not int or min(height, width) < 1:
        raise EmbeddingError("invalid latent shape")
    def tensor(raw):
        # bytearray avoids a writable view onto immutable bytes; clone owns data.
        return torch.frombuffer(bytearray(raw), dtype=torch.float32).clone().reshape(1, 4, height, width).to(device)
    try:
        base = tensor(base_noise_f32le(seed, source_digest.hex(), 4, height, width))
        ps = tensor(unit_carrier_f32le("s", ws.hex(), seed, 4, height, width, config_id.hex()))
        pi = tensor(unit_carrier_f32le("i", wi.hex(), seed, 4, height, width, config_id.hex()))
    except (ValueError, OverflowError) as error:
        raise EmbeddingError(f"latent stream rejected: {error}") from error
    return base, ps, pi


def dct_coefficients(image):
    """Differentiable native-grid edge-padded float64 orthonormal DCT-II."""
    torch = _torch()
    _finite_tensor(image, "DCT image")
    if image.ndim != 4 or tuple(image.shape[:2]) != (1, 3) or min(image.shape[-2:]) < 32:
        raise EmbeddingError("DCT image must be [1,3,H,W], H/W >=32")
    if image.min().item() < 0 or image.max().item() > 1:
        raise EmbeddingError("DCT pixels out of range")
    pixels = image.to(torch.float64)
    y = .299 * pixels[:, 0:1] + .587 * pixels[:, 1:2] + .114 * pixels[:, 2:3]
    height, width = y.shape[-2:]
    y = torch.nn.functional.pad(y, (0, (-width) % 8, 0, (-height) % 8), mode="replicate")
    blocks = y.unfold(2, 8, 8).unfold(3, 8, 8).reshape(-1, 8, 8)
    basis = torch.tensor([[(math.sqrt(1/8) if k == 0 else math.sqrt(2/8))
                           * math.cos(math.pi * (n+.5)*k/8) for n in range(8)]
                          for k in range(8)], dtype=torch.float64, device=image.device)
    return basis @ blocks @ basis.T


def centered_score(coefficients, template, frequencies):
    torch = _torch()
    selected = torch.stack([coefficients[:, u, v] for u, v in frequencies], dim=1)
    target = torch.as_tensor(template, dtype=torch.float64, device=coefficients.device)
    if target.shape != selected.shape or not torch.all((target == 1) | (target == -1)).item():
        raise EmbeddingError("template shape or signs invalid")
    c = (selected - selected.mean(dim=0)).flatten()
    t = (target - target.mean(dim=0)).flatten()
    cn, tn = torch.linalg.vector_norm(c), torch.linalg.vector_norm(t)
    if cn.item() <= 1e-12 or tn.item() <= 1e-12:
        return c.sum() * 0, True  # preserve graph; zero norm cannot be a match
    score = torch.dot(c, t) / (cn * tn)
    _finite_tensor(score, "score")
    return score.clamp(-1, 1), False


class DiffusersComponents:
    """Concrete pinned DDIM/UNet/VAE path using already verified loaded modules.

    Does not load modules or prove custody. Fixed empty-token text embeddings
    must be produced by the manifest-bound upstream tokenizer/encoder adapter.
    No CFG, prompt conditioning, offload, autocast or inference-mode pipeline.
    """
    def __init__(self, vae, unet, empty_condition, settings):
        import diffusers
        from diffusers import DDIMScheduler
        torch = _torch()
        if diffusers.__version__ != "0.35.1":
            raise EmbeddingError("requires Diffusers 0.35.1")
        _finite_tensor(empty_condition, "empty text condition")
        if empty_condition.dtype != torch.float32 or tuple(empty_condition.shape) != (1, 77, 768):
            raise EmbeddingError("empty condition must be float32 [1,77,768]")
        if float(vae.config.scaling_factor) != settings.vae_scale:
            raise EmbeddingError("resolved VAE scale differs from configuration")
        if unet.config.in_channels != 4 or unet.config.out_channels != 4 or unet.config.cross_attention_dim != 768:
            raise EmbeddingError("UNet configuration incompatible")
        for model in (vae, unet):
            model.eval()
            for parameter in model.parameters():
                if parameter.dtype != torch.float32 or parameter.device != empty_condition.device:
                    raise EmbeddingError("model parameters require condition-matched float32 profile")
                parameter.requires_grad_(False)
        self.vae, self.unet = vae, unet
        self.condition = empty_condition.detach().clone()
        self.settings = settings
        self.scheduler = DDIMScheduler(num_train_timesteps=1000, beta_start=.00085, beta_end=.012,
            beta_schedule="scaled_linear", prediction_type="epsilon", timestep_spacing="leading",
            steps_offset=1, set_alpha_to_one=False, clip_sample=False, thresholding=False,
            rescale_betas_zero_snr=False)
        self.scheduler.set_timesteps(settings.inference_steps, device=empty_condition.device)
        self.times = tuple(leading_suffix(settings.inference_steps, settings.strength))
        if self.scheduler.timesteps.tolist()[-len(self.times):] != list(self.times):
            raise EmbeddingError("installed DDIM time schedule mismatch")

    def encode(self, source):
        torch = _torch()
        with torch.no_grad():
            v = self.vae.encode(source * 2 - 1).latent_dist.mode() * self.settings.vae_scale
        _finite_tensor(v, "VAE mode")
        expected = (1, 4, source.shape[-2]//8, source.shape[-1]//8)
        if tuple(v.shape) != expected or v.dtype != torch.float32:
            raise EmbeddingError("VAE encoded shape/dtype mismatch")
        return v.detach()

    def reconstruct(self, latent, noise):
        torch = _torch()
        t = torch.tensor([self.times[0]], device=latent.device, dtype=torch.long)
        z = self.scheduler.add_noise(latent, noise, t)
        for timestep in self.times:
            prediction = self.unet(z, timestep, encoder_hidden_states=self.condition).sample
            _finite_tensor(prediction, "UNet prediction")
            if prediction.shape != z.shape:
                raise EmbeddingError("UNet prediction shape mismatch")
            z = self.scheduler.step(prediction, timestep, z, eta=0, return_dict=False)[0]
            _finite_tensor(z, "DDIM state")
        decoded = self.vae.decode(z / self.settings.vae_scale).sample
        _finite_tensor(decoded, "VAE decoded")
        if tuple(decoded.shape) != (1, 3, latent.shape[-2]*8, latent.shape[-1]*8):
            raise EmbeddingError("VAE decoded shape mismatch")
        return ((decoded + 1) / 2).clamp(0, 1)


@dataclass
class ContinuousCandidate:
    image: object
    matched_control: object
    perturbation: object
    trajectory: list
    metadata: dict
    status: str = "continuous_candidate_requires_safety_png_quality_blind_verification"


def optimize_existing(source, settings, backend, *, seed, source_digest, ws, wi, config_id,
                      control=False, record=None):
    """Component kernel only. Supplied keys must come from C2/C3b source extraction.

    A caller must journal case creation/failure before entry. `record` receives
    each pre-update loss/gradient and post-update projected norm; final row is
    after the last update. Any callback failure aborts, not silently ignored.
    Control always means both gains AND u are zero, not just u=0.
    """
    torch = _torch()
    if not isinstance(settings, Settings) or type(control) is not bool:
        raise EmbeddingError("typed settings and boolean control required")
    if isinstance(backend, DiffusersComponents) and backend.settings != settings:
        raise EmbeddingError("component settings differ from optimization settings")
    padded = padded_source(source, settings.maximum_side)
    height, width = source.shape[-2:]
    # Guard seeds/digests/stream cap before any learned component computation.
    base, ps, pi = latent_streams(seed, source_digest, ws, wi, config_id,
                                  padded.shape[-2]//8, padded.shape[-1]//8, source.device)
    latent = backend.encode(padded)
    _finite_tensor(latent, "source latent")
    if tuple(latent.shape) != (1, 4, padded.shape[-2]//8, padded.shape[-1]//8) or latent.dtype != torch.float32 or latent.requires_grad or latent.device != source.device:
        raise EmbeddingError("backend latent contract invalid")
    def render(noise):
        result = backend.reconstruct(latent, noise)
        _finite_tensor(result, "reconstruction")
        if tuple(result.shape) != tuple(padded.shape) or result.dtype != torch.float32:
            raise EmbeddingError("reconstruction shape/dtype mismatch")
        if result.min().item() < 0 or result.max().item() > 1:
            raise EmbeddingError("reconstruction outside [0,1]")
        return result[:, :, :height, :width]
    with torch.no_grad():
        reference = render(base).detach().clone()
    u = torch.zeros_like(latent, requires_grad=True)
    templates = [template_from_key(component, key, config_id, width, height)
                 for component, key in (("semantic", ws), ("instance", wi))]
    frequencies = (((1, 2), (2, 1), (2, 2), (1, 3)), ((3, 1), (2, 3), (3, 2), (1, 4)))
    trajectory = []
    def objective(image):
        coefficients = dct_coefficients(image)
        (ss, zs), (si, zi) = [centered_score(coefficients, template, freq)
                               for template, freq in zip(templates, frequencies)]
        qloss = ((image.to(torch.float64) - source)**2).mean()
        rloss = ((image.to(torch.float64) - reference)**2).mean()
        loss = (settings.lambda_q*qloss + settings.lambda_r*rloss
                + settings.lambda_s*torch.relu(settings.margin_s-ss)**2
                + settings.lambda_i*torch.relu(settings.margin_i-si)**2)
        _finite_tensor(loss, "loss")
        return loss, {"loss": loss.item(), "mse_source": qloss.item(), "mse_control": rloss.item(),
                      "score_s": ss.item(), "score_i": si.item(), "zero_variance_s": zs, "zero_variance_i": zi}
    def append(row):
        trajectory.append(row)
        if record is not None:
            record(dict(row))
    if control:
        image = reference
    else:
        optimizer = torch.optim.Adam([u], lr=settings.learning_rate, betas=(.9, .999), eps=1e-8,
                                     weight_decay=0, amsgrad=False, foreach=False, fused=False)
        for index in range(settings.iterations):
            optimizer.zero_grad(set_to_none=True)
            image = render(base + settings.alpha_s*ps + settings.alpha_i*pi + u)
            loss, row = objective(image)
            if not loss.requires_grad:
                raise EmbeddingError("detached reverse/decoder graph")
            loss.backward()
            if u.grad is None:
                raise EmbeddingError("missing perturbation gradient")
            _finite_tensor(u.grad, "perturbation gradient")
            row["gradient_norm"] = torch.linalg.vector_norm(u.grad.to(torch.float64)).item()
            optimizer.step()
            with torch.no_grad():
                _finite_tensor(u, "updated perturbation")
                norm = torch.linalg.vector_norm(u.to(torch.float64))
                if norm.item() > settings.rho:
                    u.mul_(settings.rho / norm)
            row.update(iteration=index, phase="pre_update_loss_post_projection_norm",
                       perturbation_norm=torch.linalg.vector_norm(u.to(torch.float64)).item())
            if row["perturbation_norm"] > settings.rho * (1 + 1e-6):
                raise EmbeddingError("projected perturbation exceeds declared numeric tolerance")
            append(row)
        with torch.no_grad():
            image = render(base + settings.alpha_s*ps + settings.alpha_i*pi + u)
    with torch.no_grad():
        _, final = objective(image)
    final.update(iteration=0 if control else settings.iterations, phase="final", control=control,
                 perturbation_norm=torch.linalg.vector_norm(u.to(torch.float64)).item())
    append(final)
    metadata = {"native_shape": list(source.shape), "padded_shape": list(padded.shape),
                "latent_shape": list(latent.shape), "seed": seed, "source_sha256": source_digest.hex(),
                "detector_config_id": config_id.hex(), "timesteps": leading_suffix(settings.inference_steps, settings.strength),
                "mask": "all-one", "control": control, "effective_alpha_s": 0 if control else settings.alpha_s,
                "effective_alpha_i": 0 if control else settings.alpha_i, "optimized_variable": "initial_noise_u_only",
                "base_f32le_sha256": hashlib.sha256(base.detach().cpu().numpy().astype("<f4").tobytes()).hexdigest(),
                "projection_absolute_tolerance": settings.rho * 1e-6,
                "u_norm": torch.linalg.vector_norm(u.to(torch.float64)).item(),
                "total_noise_displacement_norm": torch.linalg.vector_norm(
                    (torch.zeros_like(u) if control else settings.alpha_s*ps+settings.alpha_i*pi+u).to(torch.float64)).item(),
                "numerical_profile": "model-f32-dct-centered-f64-adam-projected-v1",
                "final_discrete_verification": "NOT_RUN", "safety": "NOT_RUN", "quality_metrics": "NOT_RUN"}
    if isinstance(backend, DiffusersComponents):
        initial_alpha = float(backend.scheduler.alphas_cumprod[backend.times[0]].item())
        metadata["initial_cumulative_alpha"] = initial_alpha
        metadata["initial_latent_displacement_norm"] = math.sqrt(1-initial_alpha) * metadata["total_noise_displacement_norm"]
    else:
        metadata["initial_latent_displacement_norm"] = None
    return ContinuousCandidate(image.detach().clone(), reference, u.detach().clone(), trajectory, metadata)

"""Optional embedder stage for v5: refine the robust-tier change through a frozen latent-diffusion channel.

Experimental and separately labelled.  The detector does not change and needs
no model: this stage only chooses, inside the same visibility budget, a robust
change whose key correlation is higher *after* the image has passed the frozen
autoencoder (and, optionally, one noising and denoising step).  It starts from
the closed-form change of :func:`revised_watermark_v5.robust_plan` and hands
its result back through ``robust_change``, where the codec checks the budget.

Needs torch and a locally available Stable Diffusion 1.5 pipeline (the science
interpreter); the reference codec and its tests do not import this module.
The surrogate channel is the same model family as the regeneration attack of
the study, so a gain measured with it says nothing about other models.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import revised_watermark_v5 as codec  # noqa: E402

BLOCK = codec.BLOCK
SIDE = codec.CANONICAL_SIDE


def _dct(points: int, device) -> torch.Tensor:
    index = torch.arange(points, dtype=torch.float64)
    matrix = torch.cos((2 * index[None, :] + 1) * index[:, None] * math.pi / (2 * points)) * math.sqrt(2.0 / points)
    matrix[0] *= math.sqrt(0.5)
    return matrix.float().to(device)


class Refiner:
    """Gradient ascent on the post-channel key score, projected onto the profile's visibility budget."""

    def __init__(self, pipe, steps: int = 30, learning_rate: float = 0.1, timesteps: tuple[int, ...] = (100,), clean_weight: float = 0.1, seed: int = 1234):
        self.device = pipe.unet.device
        self.vae = pipe.vae.requires_grad_(False)
        self.unet = pipe.unet.requires_grad_(False)
        # Recomputing activations in the backward pass keeps the peak memory within a 12 GB card.
        self.vae.enable_gradient_checkpointing()
        self.unet.enable_gradient_checkpointing()
        self.scaling = self.vae.config.scaling_factor
        self.alphas = pipe.scheduler.alphas_cumprod.to(self.device).float()
        with torch.no_grad():
            tokens = pipe.tokenizer("", padding="max_length", max_length=pipe.tokenizer.model_max_length, return_tensors="pt")
            self.empty_prompt = pipe.text_encoder(tokens.input_ids.to(self.device))[0]
        self.steps, self.learning_rate, self.timesteps, self.clean_weight, self.seed = steps, learning_rate, tuple(timesteps), clean_weight, seed
        self.dct8 = _dct(BLOCK, self.device)

    # -- the frozen channel -------------------------------------------------

    def _encode(self, rgb: torch.Tensor) -> torch.Tensor:
        with torch.autocast("cuda", dtype=torch.float16):
            return self.vae.encode((rgb / 127.5 - 1.0)[None].half()).latent_dist.mode()

    def _decode(self, latent: torch.Tensor) -> torch.Tensor:
        with torch.autocast("cuda", dtype=torch.float16):
            decoded = self.vae.decode(latent.half(), return_dict=False)[0][0]
        return ((decoded.float() + 1.0) * 127.5).clamp(0, 255)

    def round_trip(self, rgb: torch.Tensor) -> torch.Tensor:
        return self._decode(self._encode(rgb))

    def one_step(self, rgb: torch.Tensor, timestep: int, generator: torch.Generator) -> torch.Tensor:
        """Noise the latent to ``timestep`` and return the denoiser's one-step estimate of the clean image."""
        latent = self._encode(rgb).float() * self.scaling
        alpha = self.alphas[timestep]
        noise = torch.randn(latent.shape, generator=generator, device=self.device)
        noisy = alpha.sqrt() * latent + (1 - alpha).sqrt() * noise
        with torch.autocast("cuda", dtype=torch.float16):
            predicted = self.unet(noisy.half(), torch.tensor([timestep], device=self.device), encoder_hidden_states=self.empty_prompt).sample
        return self._decode((noisy - (1 - alpha).sqrt() * predicted.float()) / alpha.sqrt() / self.scaling)

    # -- the detector's statistic, in torch ----------------------------------

    def _score(self, rgb: torch.Tensor, plan: dict) -> torch.Tensor:
        luma = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        coarse = torch.nn.functional.avg_pool2d(luma[None, None], plan["kernel"])[0, 0]
        blocks = coarse.unfold(0, BLOCK, BLOCK).unfold(1, BLOCK, BLOCK)
        coefficients = (self.dct8 @ blocks @ self.dct8.T)[:, :, plan["us"], plan["vs"]].reshape(-1, len(plan["us"]))
        whitened = coefficients * plan["weights"]
        values = (whitened / torch.sqrt(plan["floor"] ** 2 + (whitened**2).mean(dim=1, keepdim=True))).reshape(-1)
        projections = torch.zeros(codec.CHANNEL_CHIPS, device=self.device).index_add(0, plan["chip"], plan["sign"] * values) / plan["norms"]
        return (plan["pattern"] * projections).sum() / projections.norm()

    def _render(self, change: torch.Tensor, plan: dict) -> torch.Tensor:
        amplitudes = change / plan["gains"]
        pixels = torch.einsum("bp,pi,pj->bij", amplitudes, plan["basis_y"], plan["basis_x"])
        rows, columns = pixels.shape[1], pixels.shape[2]
        count = SIDE // BLOCK
        return pixels.reshape(count, count, rows, columns).permute(0, 2, 1, 3).reshape(count * rows, count * columns)

    def _ratios(self, change: torch.Tensor, plan: dict) -> torch.Tensor:
        return torch.sqrt(((change / plan["gains"]) ** 2).sum(dim=1) / (BLOCK * BLOCK)) / plan["mask"]

    # -- refinement ----------------------------------------------------------

    def refine(self, rgb: np.ndarray, owner_id: str, profile=None, secret_key=None, semantic_features=None):
        """Return ``(robust_change, info)`` for :func:`revised_watermark_v5.embed_rgb`."""
        height, width = rgb.shape[:2]
        if height % SIDE or width % SIDE:
            raise ValueError("the refinement stage needs image sides that are multiples of 128")
        contract = codec.robust_plan(codec.luminance_from_rgb(rgb.tolist()), owner_id, secret_key, profile, semantic_features)
        device = self.device
        tensor = lambda values: torch.tensor(values, dtype=torch.float32, device=device)  # noqa: E731
        positions = contract["positions"]
        kernel = (height // SIDE, width // SIDE)

        def basis(scale: int, indices) -> torch.Tensor:
            local = (torch.arange(BLOCK * scale, dtype=torch.float64) + 0.5) / scale
            rows = [(math.sqrt(1.0 / BLOCK) if u == 0 else math.sqrt(2.0 / BLOCK)) * torch.cos(local * u * math.pi / BLOCK) for u in indices]
            return torch.stack(rows).float().to(device)

        plan = {
            "kernel": kernel,
            "us": torch.tensor([pair[0] for pair in positions], device=device),
            "vs": torch.tensor([pair[1] for pair in positions], device=device),
            "weights": tensor(contract["whitening_weights"]),
            "floor": float(contract["floor"]),
            "chip": torch.tensor(contract["chip_of_slot"], device=device),
            "sign": tensor(contract["sign_of_slot"]),
            "norms": tensor(contract["chip_norms"]),
            "pattern": tensor(contract["pattern"]),
            "mask": tensor(contract["mask"]),
            "gains": tensor(contract["averaging_gains"]),
            "basis_y": basis(kernel[0], [pair[0] for pair in positions]),
            "basis_x": basis(kernel[1], [pair[1] for pair in positions]),
        }
        start = tensor(contract["change"])
        budget = float(contract["limits"]["ratio_rms"])  # what the closed form spent: the visibility, or less at the PSNR floor
        block_cap = float(contract["block_ratio_cap"]) * float(contract["visibility"])
        host = torch.tensor(rgb, dtype=torch.float32, device=device).permute(2, 0, 1)
        variable = (start / plan["mask"][:, None]).requires_grad_(True)
        optimiser = torch.optim.Adam([variable], lr=self.learning_rate)
        generator = torch.Generator(device=device).manual_seed(self.seed)

        def project(value: torch.Tensor) -> torch.Tensor:
            change = value * plan["mask"][:, None]
            with torch.no_grad():
                ratios = self._ratios(change, plan)
                block = torch.clamp(block_cap / (ratios + 1e-9), max=1.0)
                total = min(1.0, budget / float(torch.sqrt(((ratios * block) ** 2).mean())))
            return change * block[:, None] * total

        def marked(value: torch.Tensor) -> torch.Tensor:
            return (host + self._render(project(value), plan)[None]).clamp(0, 255)

        with torch.no_grad():
            before = {"clean": float(self._score(marked(variable), plan)), "round_trip": float(self._score(self.round_trip(marked(variable)), plan))}
        terms = [lambda image: self.clean_weight * self._score(image, plan), lambda image: self._score(self.round_trip(image), plan)]
        terms += [(lambda image, t=t: self._score(self.one_step(image, t, generator), plan) / len(self.timesteps)) for t in self.timesteps]
        skipped = 0
        for _step in range(self.steps):
            optimiser.zero_grad()
            for term in terms:  # one graph at a time: the peak memory is that of the largest term
                (-term(marked(variable)) * 256.0).backward()  # the factor keeps half-precision gradients away from underflow
            if not torch.isfinite(variable.grad).all():
                skipped += 1
                optimiser.zero_grad()
                continue
            optimiser.step()
        with torch.no_grad():
            change = project(variable)
            after = {"clean": float(self._score(marked(variable), plan)), "round_trip": float(self._score(self.round_trip(marked(variable)), plan))}
            ratios = self._ratios(change, plan)
        info = {
            "steps": self.steps,
            "timesteps": list(self.timesteps),
            "skipped_steps": skipped,
            "score_before": before,
            "score_after": after,
            "ratio_rms": float(torch.sqrt((ratios**2).mean())),
            "ratio_max": float(ratios.max()),
        }
        return change.cpu().tolist(), info

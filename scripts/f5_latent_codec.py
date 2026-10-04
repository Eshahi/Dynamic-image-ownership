"""Family 5: encoder-amplified latent carrier.

The v5 r3 dual-key structure is kept: semantic code q from CLIP selects the
semantic key Ws carried by the robust tier; perceptual hash H and the instance
key Wi live in v5's fragile full-resolution luminance tier; same key tables,
key test, Bentkus-Dzindzalieta threshold and decision table.  One thing
changes: the robust tier is read in the latent space of the pinned SD1.5 VAE
(the attacker's own first stage) and written by a pixel change found with
gradients through that encoder.

Why: `research/f5-encoder-amplified-latent.md`.  Regeneration adds its noise in
this latent, so what survives depends on the latent displacement, not on the
pixel change.  The SD VAE encoder is not robust (PhotoGuard's encoder attack):
a pixel change at a fixed PSNR found by gradient ascent moves a chosen latent
pattern about fifteen times further than the decoder rendering of that pattern
(A-C's way of writing), and img2img keeps a low-frequency latent pattern well.

Robust tier: the scaled posterior-mode latent z (4 x 64 x 64) of the suspect,
orthonormal 2-D DCT per channel, the coefficients whose index radius lies in
``BAND``, each multiplied by a fixed public weight (radius ** WHITENING).
Slots are assigned to the 320 chips with keyed signs by v4's carrier.  The
weights never depend on the key, so for an unmarked image the key statistic
is still a weighted sum of independent random signs and the false-positive
bound holds unchanged.  The detector is blind: suspect RGB, claimed OwnerID,
profile, the suspect's own CLIP features and the pinned VAE.
Image-domain comparator; not the proposal's latent generation method.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import revised_watermark_v5 as v5  # noqa: E402

base = v5.base
FAMILY = "f5-encoder-amplified-latent"
REVISION = 1
LATENT = 64
SCALE = 0.18215
BAND = (4, 32)        # DCT index radius on the 64 x 64 latent (about 2-16 cycles/image)
WHITENING = 1.0
LABEL = b"f5-latent"


def dct_matrix(n: int = LATENT) -> np.ndarray:
    k, i = np.arange(n)[:, None], np.arange(n)[None, :]
    c = np.sqrt(2.0 / n) * np.cos(np.pi * (2 * i + 1) * k / (2 * n))
    c[0] /= np.sqrt(2.0)
    return c


def slots(band=BAND, whitening=WHITENING):
    """(channel, u, v) index arrays of the band and their public weights, in fixed order."""
    u, v = np.meshgrid(np.arange(LATENT), np.arange(LATENT), indexing="ij")
    r = np.hypot(u, v)
    keep = (r >= band[0]) & (r < band[1])
    uu, vv = u[keep], v[keep]
    ch = np.repeat(np.arange(4), uu.size)
    weights = np.tile((r[keep] / band[0]) ** whitening, 4)
    return ch, np.tile(uu, 4), np.tile(vv, 4), weights


class Layout:
    """Everything of the robust tier that depends only on owner, key, configuration and band."""

    def __init__(self, checked, key: bytes, config: bytes, owner: bytes, band=BAND, whitening=WHITENING):
        self.band, self.whitening = tuple(band), float(whitening)
        self.ch, self.u, self.v, self.weights = slots(band, whitening)
        bit_of_slot, signs, _ = base._carrier(key, config, owner, LABEL + bytes(band), LATENT, LATENT, self.weights.size)
        self.chip = np.asarray(bit_of_slot, np.int64)
        self.signs = np.asarray(signs, np.float64)
        squares = np.bincount(self.chip, weights=self.weights ** 2, minlength=v5.CHANNEL_CHIPS)
        self.norms = np.sqrt(squares)
        self.dct = dct_matrix()

    def projections(self, z: np.ndarray) -> list[float]:
        coef = np.einsum("ij,cjk,lk->cil", self.dct, np.asarray(z, np.float64), self.dct)
        values = coef[self.ch, self.u, self.v] * self.weights * self.signs
        return (np.bincount(self.chip, weights=values, minlength=v5.CHANNEL_CHIPS) / self.norms).tolist()


class Reader:
    """The pinned SD1.5 VAE encoder, fp32, on the GPU: RGB8 -> scaled posterior-mode latent."""

    def __init__(self, assets: Path, device: str = "cuda"):
        import torch
        from diffusers import AutoencoderKL
        self.torch, self.device = torch, device
        self.vae = AutoencoderKL.from_pretrained(Path(assets) / "sd15-fp16/vae", variant="fp16", use_safetensors=True,
                                                 local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).to(device)

    def tensor(self, rgb01: np.ndarray):
        return self.torch.from_numpy(np.ascontiguousarray(np.asarray(rgb01, np.float32).transpose(2, 0, 1)))[None].to(self.device)

    def encode(self, x01):
        """Differentiable: (1,3,H,W) tensor in [0,1] -> (4,h,w) scaled latent."""
        return self.vae.encode(x01 * 2 - 1).latent_dist.mode()[0] * SCALE

    def latent(self, rgb8) -> np.ndarray:
        with self.torch.inference_mode():
            return self.encode(self.tensor(np.asarray(rgb8, np.float64) / 255.0)).double().cpu().numpy()


def _semantic_pattern(checked, key, config, owner, semantic_features, luma):
    q = v5._semantic(base._analyse(luma, ())[0], checked, key, config, semantic_features, binding=True)
    table = v5._semantic_table(owner, key, config)
    return q, [chip for segment in range(v5.CODE_BITS) for chip in table[segment][v5._bit(q, segment)]]


def _activity_mask(rgb01: np.ndarray, power: float) -> np.ndarray:
    """Public texture mask in [0.25, 4]: local luminance standard deviation (5 px), normalised to mean 1, ** power."""
    if power <= 0:
        return np.ones(rgb01.shape[:2])
    from scipy.ndimage import uniform_filter
    y = rgb01 @ np.array([0.299, 0.587, 0.114])
    sd = np.sqrt(np.maximum(uniform_filter(y * y, 5) - uniform_filter(y, 5) ** 2, 0)) + 2.0 / 255
    m = (sd / sd.mean()) ** power
    return np.clip(m / m.mean(), 0.25, 4.0)


def robust_pgd(reader: Reader, rgb01: np.ndarray, layout: Layout, ws: Sequence[float], psnr_db: float,
               steps: int, target_margin: float, mask_power: float = 0.0):
    """Pixel change at a PSNR budget that drives every chip margin ws_i * p_i towards ``target_margin``.

    Squared hinge on the margins, normalised-gradient ascent with an L2 ball
    (in the mask-weighted metric) and the [0,1] box.  Returns the float image.
    """
    torch = reader.torch
    dev = reader.device
    x = reader.tensor(rgb01)
    mask = torch.from_numpy(_activity_mask(rgb01, mask_power).astype(np.float32))[None, None].to(dev)
    budget = 10 ** (-psnr_db / 20) * math.sqrt(rgb01.size)
    D = torch.from_numpy(layout.dct.astype(np.float32)).to(dev)
    ch, u, v = (torch.from_numpy(a).to(dev) for a in (layout.ch, layout.u, layout.v))
    coeff = torch.from_numpy((layout.weights * layout.signs).astype(np.float32)).to(dev)
    chip = torch.from_numpy(layout.chip).to(dev)
    norms = torch.from_numpy(layout.norms.astype(np.float32)).to(dev)
    w = torch.from_numpy(np.asarray(ws, np.float32)).to(dev)
    eta = torch.zeros_like(x, requires_grad=True)  # delta = mask * eta; budget applies to delta

    def margins(delta):
        z = reader.encode((x + delta).clamp(0, 1))
        c = torch.einsum("ij,cjk,lk->cil", D, z, D)
        totals = torch.zeros(v5.CHANNEL_CHIPS, device=dev).index_add(0, chip, c[ch, u, v] * coeff)
        return w * totals / norms

    for step in range(steps):
        lr = budget * (0.2 if step < steps // 2 else 0.05)
        m = margins(mask * eta)
        loss = torch.relu(target_margin - m).pow(2).mean()
        g, = torch.autograd.grad(loss, eta)
        with torch.no_grad():
            eta -= lr * g / (g.norm() + 1e-12)
            delta = (x + mask * eta).clamp(0, 1) - x
            n = delta.norm()
            if n > budget:
                delta *= budget / n
            eta.copy_(delta / mask)
    with torch.no_grad():
        out = (x + mask * eta).clamp(0, 1)[0].permute(1, 2, 0).double().cpu().numpy()
    return out


def embed_rgb(rgb, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float], reader: Reader,
              psnr_db: float = 46.0, steps: int = 150, target_margin: float = 4.0, mask_power: float = 0.0,
              band=BAND, whitening=WHITENING, refine_rounds: int = 1):
    """Return (RGB8 array, report); the report verifies the saved pixels with :func:`detect_rgb`."""
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(owner_id)
    source = np.asarray(rgb, np.uint8)
    luma = v5.luminance_from_rgb(source.tolist())
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    q, ws = _semantic_pattern(checked, key, config, owner, semantic_features, luma)
    layout = Layout(checked, key, config, owner, band, whitening)

    x01 = source.astype(np.float64) / 255.0
    current = np.clip(np.rint(robust_pgd(reader, x01, layout, ws, psnr_db, steps, target_margin, mask_power) * 255), 0, 255)
    fragile_report = None
    for round_index in range(1 + refine_rounds):
        # Fragile tier on the luminance of the robust-marked image; its luma change is added to R, G and B.
        robust_rgb = current.copy()
        before = v5.luminance_from_rgb(robust_rgb.astype(np.uint8).tolist())
        marked_luma = [[float(value) for value in row] for row in before]
        fragile = v5._Fragile(checked, key, config, owner, height, width)
        means, coefficients = base._analyse(marked_luma, fragile.analysis)
        h = base._perceptual_hash(means, coefficients, key, config)
        itable = v5._instance_table(owner, key, config)
        wi = [chip for segment in range(v5.CODE_BITS) for chip in itable[segment][v5._bit(q, segment)][v5._bit(h, segment)]]
        fragile_report = v5._embed_fragile(marked_luma, fragile, wi, checked, False, True)
        change = np.asarray(marked_luma) - np.asarray(before)
        current = np.clip(np.rint(robust_rgb + change[..., None]), 0, 255)
        if round_index < refine_rounds:
            # The fragile change perturbs the latent; re-run the robust tier briefly from the combined image.
            start = current / 255.0
            refined = robust_pgd(reader, start, layout, ws, max(psnr_db + 6.0, 50.0), max(steps // 3, 20), target_margin, mask_power)
            current = np.clip(np.rint(refined * 255), 0, 255)
    output = current.astype(np.uint8)
    mse = float(np.mean((output.astype(np.float64) - source) ** 2))
    z = reader.latent(output)
    result = detect_rgb(output, z, owner_id, checked, semantic_features, band=band, whitening=whitening)
    margins = np.asarray(ws) * np.asarray(layout.projections(z))
    report = dict(family=FAMILY, revision=REVISION, semantic_code=f"{q:08x}", band=list(band), whitening=whitening,
                  psnr_target_db=psnr_db, steps=steps, target_margin=target_margin, mask_power=mask_power,
                  refine_rounds=refine_rounds, rgb_psnr_db=None if mse == 0 else 10 * math.log10(255.0**2 / mse),
                  margin_median=float(np.median(margins)), margin_min=float(margins.min()),
                  negative_chips=int((margins < 0).sum()), instance_channel=fragile_report,
                  verification=result, verified=result["outcome"] == "both_match")
    return output, report


def detect_rgb(rgb, z, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float],
               binding_mode: str = "combined", roster_size: int = 1, band=BAND, whitening=WHITENING) -> dict[str, object]:
    """v5 :func:`detect` with the robust tier read from the VAE latent ``z`` of the suspect (see :class:`Reader`)."""
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
    s_status = base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else None
    carries_other = s_found and base._content_status(semantic["corrected_distance"], *semantic_limits, True) != "match"
    q_bound = int(semantic["decoded_code"], 16) if carries_other else q_now
    table = v5._instance_table(owner, key, config)
    options = [table[segment][v5._bit(q_bound, segment)] for segment in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_projections, options, h_now), target, roster_size, h_now)
    i_found = bool(instance["found"])
    i_status = (
        max(base._content_status(instance["corrected_distance"], *instance_limits, check_instance),
            base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else "unchecked",
            key=base._STATUS_RANK.get)
        if i_found else None)
    outcome, state = base._decide(s_found, s_status, i_found, i_status)

    def public(result, status):
        entry = dict(result)
        entry["content_status"] = status
        entry["content_match"] = bool(result["found"] and base._STATUS_RANK[status] == 0)
        return entry

    return {"outcome": outcome, "proposal_state": state, "watermark_found": bool(s_found or i_found),
            "semantic": public(semantic, s_status), "instance": public(instance, i_status),
            "semantic_code": f"{q_now:08x}", "perceptual_hash": f"{h_now:08x}", "binding_mode": binding_mode,
            "owner_id": owner.decode("utf-8"), "owners_tested": roster_size, "family": FAMILY, "revision": REVISION,
            "band": list(band), "whitening": whitening, "detector_config_id": config.hex(),
            "side_information": ["public OwnerID", "profile", "pinned CLIP weights", "pinned SD1.5 VAE encoder"],
            "seconds": time.perf_counter() - started}

"""Family 5 revision 3 (r3-256): a 256-bit semantic sketch in the encoder-amplified latent carrier.

Everything of F5 r2 is kept except the robust semantic channel:
- **Pixel side:** same pixel change found through the pinned SD1.5 VAE encoder (PGD, same PSNR budget).
- **Carrier:** same latent DCT band and public weights.
- **Fragile tier:** the 32-bit q and H tier is unchanged.

Why (`research/ideas/binding-ceiling.md` on `claude/f5-ideas`): F5's T3 binding loss at .4/.5 comes from the 32-bit sign sketch of the CLIP vector, not from CLIP drift. A 256-bit sketch reaches the ideal CLIP-angle ceiling on the development stress data.

Robust semantic channel, in place of v5's 32 segments x 10 chips with two option patterns:
- **Sketch.** q256_j = sign(R_j . e), where R is a keyed 256 x 512 Rademacher matrix (profile key) and e is the unit 7-view CLIP vector.
- **Bit chips.** The 3272 band slots are split by a keyed permutation into 256 chips of 12-13 slots, with keyed slot signs k_i. The chip value is y_j = sum_i k_i w_i c_i / sqrt(sum_i w_i^2).
  - Each bit is antipodal: the embedder drives q256_j * y_j towards a target margin.
  - The keyed signs never depend on the image.
- **Owner found.** The detector:
  - recomputes the suspect's projections p'_j;
  - weights each chip by a_j = sign(p'_j) * (2 Phi(|p'_j| cot theta0) - 1), with theta0 the match radius (6 of 32 bits, 33.75 degrees);
  - scores S = sum_i k_i b_i / ||b||, where b_i = a_j(i) w_i c_i / n_j(i).

  For an unmarked image or another owner, the k_i are independent of b, so S is a normalised Rademacher sum. The v5 single-pattern Bentkus-Dzindzalieta threshold (4.982 at 1e-6) therefore applies unchanged. There is no search over codes, so the threshold does not grow with the sketch length.
- **Binding.** Only once the owner is found:
  1. A symmetric two-Gaussian fit to the 256 chip values gives the per-bit carrier LLRs, 2 mu y_j / sigma^2.
  2. The maximum-likelihood angle between the vector the sketch was made from and the suspect's vector maximises sum_j log[Phi(p'_j cot t) e^{L_j/2} + Phi(-p'_j cot t) e^{-L_j/2}].
  3. It is expressed in 32-bit units (t * 32 / pi), so the v5 radii (match <= 6, mismatch >= 10) and the decision table stay unchanged.

Development-only research prototype; not a frozen candidate.
"""
from __future__ import annotations

import math
import time
from typing import Mapping, Sequence

import numpy as np
from scipy.stats import norm

from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5

base = v5.base
FAMILY = "f5-encoder-amplified-latent"
REVISION = "3-256"
SKETCH_BITS = 256
THETA0 = 6 * math.pi / v5.CODE_BITS
TARGET_MARGIN = 4.5   # energy-matched to r2: 320 chips x 4.0^2 = 256 chips x ~4.47^2
_ANGLES = np.linspace(1e-3, math.pi - 1e-3, 2000)
_COT = np.cos(_ANGLES) / np.sin(_ANGLES)
_ROWS = {}


def _keyed_rng(key: bytes, config: bytes, *fields: bytes) -> np.random.Generator:
    seed = base._stream(key, config, base._pack(b"f5r3", *fields), 32)
    return np.random.Generator(np.random.PCG64(int.from_bytes(seed, "big")))


def sketch_projections(features: Sequence[float], key: bytes, config: bytes) -> np.ndarray:
    """p_j = R_j . e for the keyed 256 x width Rademacher rows (profile key, not owner)."""
    vector = np.asarray(features, np.float64)
    width = vector.size
    if (key, config, width) not in _ROWS:
        rng = _keyed_rng(key, config, b"semantic-projection-256", width.to_bytes(4, "big"))
        _ROWS[(key, config, width)] = 1.0 - 2.0 * rng.integers(0, 2, size=(SKETCH_BITS, width))
    return _ROWS[(key, config, width)] @ (vector / np.linalg.norm(vector))


class Layout256:
    """The robust tier of r3: 256 antipodal bit chips over the F5 band slots (owner-keyed)."""

    def __init__(self, key: bytes, config: bytes, owner: bytes, band=f5.BAND, whitening=f5.WHITENING):
        self.band, self.whitening = tuple(band), float(whitening)
        self.ch, self.u, self.v, self.weights = f5.slots(band, whitening)
        n = self.weights.size
        rng = _keyed_rng(key, config, b"chips", owner, bytes(band))
        order = rng.permutation(n)
        self.chip = np.empty(n, np.int64)
        self.chip[order] = np.arange(n) % SKETCH_BITS
        self.signs = 1.0 - 2.0 * rng.integers(0, 2, size=n)
        self.norms = np.sqrt(np.bincount(self.chip, weights=self.weights ** 2, minlength=SKETCH_BITS))
        self.dct = f5.dct_matrix()

    def coefficients(self, z: np.ndarray) -> np.ndarray:
        coef = np.einsum("ij,cjk,lk->cil", self.dct, np.asarray(z, np.float64), self.dct)
        return coef[self.ch, self.u, self.v]

    def chips(self, z: np.ndarray) -> np.ndarray:
        values = self.coefficients(z) * self.weights * self.signs
        return np.bincount(self.chip, weights=values, minlength=SKETCH_BITS) / self.norms


def owner_score(layout: Layout256, z: np.ndarray, projections: np.ndarray) -> float:
    """Normalised Rademacher sum over slots with image-derived weights (see module docstring)."""
    a = np.sign(projections) * (2.0 * norm.cdf(np.abs(projections) / math.tan(THETA0)) - 1.0)
    b = a[layout.chip] * layout.weights * layout.coefficients(z) / layout.norms[layout.chip]
    energy = float(np.sqrt(np.sum(b * b)))
    return 0.0 if energy <= 1e-12 else float(np.sum(layout.signs * b) / energy)


def carrier_llrs(y: np.ndarray, iterations: int = 50) -> tuple[np.ndarray, float, float]:
    """Per-bit LLRs from a symmetric two-Gaussian fit y ~ 1/2 N(mu, s^2) + 1/2 N(-mu, s^2)."""
    y = np.asarray(y, np.float64)
    mu = float(np.mean(np.abs(y)))
    s2 = max(float(np.var(y)) - mu * mu, 1e-6 * float(np.mean(y * y)) + 1e-12)
    for _ in range(iterations):
        r = 1.0 / (1.0 + np.exp(np.clip(-2.0 * mu * y / s2, -60, 60)))  # P(s=+1 | y)
        mu = max(float(np.mean((2.0 * r - 1.0) * y)), 0.0)
        s2 = max(float(np.mean(y * y)) - mu * mu, 1e-6 * float(np.mean(y * y)) + 1e-12)
    return 2.0 * mu * y / s2, mu, math.sqrt(s2)


def soft_angle(llrs: np.ndarray, projections: np.ndarray) -> float:
    """ML angle t maximising sum_j log[Phi(p_j cot t) e^{L_j/2} + Phi(-p_j cot t) e^{-L_j/2}]."""
    p = np.asarray(projections, np.float64)[None, :]
    half = np.asarray(llrs, np.float64)[None, :] / 2.0
    up = norm.logcdf(p * _COT[:, None]) + half
    down = norm.logcdf(-p * _COT[:, None]) - half
    return float(_ANGLES[int(np.argmax(np.logaddexp(up, down).sum(1)))])


def robust_pgd(reader, rgb01: np.ndarray, layout: Layout256, q: np.ndarray, psnr_db: float, steps: int,
               target_margin: float):
    """F5's PGD with the 256 antipodal chips as targets: drive q_j * y_j towards ``target_margin``."""
    torch = reader.torch
    dev = reader.device
    x = reader.tensor(rgb01)
    budget = 10 ** (-psnr_db / 20) * math.sqrt(rgb01.size)
    D = torch.from_numpy(layout.dct.astype(np.float32)).to(dev)
    ch, u, v = (torch.from_numpy(a).to(dev) for a in (layout.ch, layout.u, layout.v))
    coeff = torch.from_numpy((layout.weights * layout.signs).astype(np.float32)).to(dev)
    chip = torch.from_numpy(layout.chip).to(dev)
    norms = torch.from_numpy(layout.norms.astype(np.float32)).to(dev)
    qq = torch.from_numpy(np.asarray(q, np.float32)).to(dev)
    eta = torch.zeros_like(x, requires_grad=True)

    def margins(delta):
        z = reader.encode((x + delta).clamp(0, 1))
        c = torch.einsum("ij,cjk,lk->cil", D, z, D)
        totals = torch.zeros(SKETCH_BITS, device=dev).index_add(0, chip, c[ch, u, v] * coeff)
        return qq * totals / norms

    for step in range(steps):
        lr = budget * (0.2 if step < steps // 2 else 0.05)
        loss = torch.relu(target_margin - margins(eta)).pow(2).mean()
        g, = torch.autograd.grad(loss, eta)
        with torch.no_grad():
            eta -= lr * g / (g.norm() + 1e-12)
            delta = (x + eta).clamp(0, 1) - x
            n = delta.norm()
            if n > budget:
                delta *= budget / n
            eta.copy_(delta)
    with torch.no_grad():
        return (x + eta).clamp(0, 1)[0].permute(1, 2, 0).double().cpu().numpy()


def embed_rgb(rgb, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float], reader,
              psnr_db: float = 52.0, steps: int = 150, target_margin: float = TARGET_MARGIN, refine_rounds: int = 1,
              band=f5.BAND, whitening=f5.WHITENING, **_unused):
    """Return (RGB8 array, report); same pipeline as F5 r2's embed_rgb with the r3 robust tier."""
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(owner_id)
    source = np.asarray(rgb, np.uint8)
    luma = v5.luminance_from_rgb(source.tolist())
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    q32 = v5._semantic(base._analyse(luma, ())[0], checked, key, config, semantic_features, binding=True)
    p = sketch_projections(semantic_features, key, config)
    q256 = np.where(p > 0, 1.0, -1.0)
    layout = Layout256(key, config, owner, band, whitening)

    current = np.clip(np.rint(robust_pgd(reader, source / 255.0, layout, q256, psnr_db, steps, target_margin) * 255), 0, 255)
    fragile_report = None
    for round_index in range(1 + refine_rounds):
        robust_rgb = current.copy()
        before = v5.luminance_from_rgb(robust_rgb.astype(np.uint8).tolist())
        marked_luma = [[float(value) for value in row] for row in before]
        fragile = v5._Fragile(checked, key, config, owner, height, width)
        means, coefficients = base._analyse(marked_luma, fragile.analysis)
        h = base._perceptual_hash(means, coefficients, key, config)
        itable = v5._instance_table(owner, key, config)
        wi = [c for segment in range(v5.CODE_BITS) for c in itable[segment][v5._bit(q32, segment)][v5._bit(h, segment)]]
        fragile_report = v5._embed_fragile(marked_luma, fragile, wi, checked, False, True)
        change = np.asarray(marked_luma) - np.asarray(before)
        current = np.clip(np.rint(robust_rgb + change[..., None]), 0, 255)
        if round_index < refine_rounds:
            refined = robust_pgd(reader, current / 255.0, layout, q256, max(psnr_db + 6.0, 50.0), max(steps // 3, 20), target_margin)
            current = np.clip(np.rint(refined * 255), 0, 255)
    output = current.astype(np.uint8)
    mse = float(np.mean((output.astype(np.float64) - source) ** 2))
    z = reader.latent(output)
    result = detect_rgb(output, z, owner_id, checked, semantic_features, band=band, whitening=whitening)
    margins = q256 * layout.chips(z)
    report = dict(family=FAMILY, revision=REVISION, semantic_code=f"{q32:08x}", sketch_bits=SKETCH_BITS, band=list(band),
                  whitening=whitening, psnr_target_db=psnr_db, steps=steps, target_margin=target_margin,
                  refine_rounds=refine_rounds, rgb_psnr_db=None if mse == 0 else 10 * math.log10(255.0 ** 2 / mse),
                  margin_median=float(np.median(margins)), margin_min=float(margins.min()),
                  negative_chips=int((margins < 0).sum()), instance_channel=fragile_report,
                  verification=result, verified=result["outcome"] == "both_match")
    return output, report


def detect_rgb(rgb, z, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float],
               binding_mode: str = "combined", roster_size: int = 1, band=f5.BAND, whitening=f5.WHITENING,
               **_unused) -> dict[str, object]:
    """Blind r3 detection; same inputs, decision table and output keys as F5 r2's detect_rgb."""
    started = time.perf_counter()
    checked, key, config = v5._resolve(profile, None)
    luma = v5.luminance_from_rgb(np.asarray(rgb).tolist())
    base._check_image(luma, int(checked["minimum_side"]))
    height, width = len(luma), len(luma[0])
    owner = v5.canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    layout = Layout256(key, config, owner, band, whitening)
    p = sketch_projections(semantic_features, key, config)
    score = owner_score(layout, z, p)
    threshold = v5._threshold(target, roster_size)
    s_found = score >= threshold
    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))
    s_status = distance = mu = sigma = None
    if s_found:
        llrs, mu, sigma = carrier_llrs(layout.chips(z))
        distance = soft_angle(llrs, p) * v5.CODE_BITS / math.pi
        s_status = base._content_status(distance, *semantic_limits, check_semantic)

    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(luma, fragile.analysis)
    instance_projections = fragile.projections(coefficients)
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)
    table = v5._instance_table(owner, key, config)
    options = [table[segment][v5._bit(q_now, segment)] for segment in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_projections, options, h_now), target, roster_size, h_now)
    i_found = bool(instance["found"])
    i_status = (max(base._content_status(instance["corrected_distance"], *instance_limits, check_instance),
                    s_status if s_found else "unchecked", key=base._STATUS_RANK.get) if i_found else None)
    outcome, state = base._decide(s_found, s_status, i_found, i_status)
    semantic = dict(found=bool(s_found), read=bool(s_found), score=score, threshold=threshold, recomputed_score=score,
                    soft_distance=distance, carrier_mu=mu, carrier_sigma=sigma, content_status=s_status,
                    content_match=bool(s_found and base._STATUS_RANK[s_status] == 0))
    inst = dict(instance)
    inst["content_status"] = i_status
    inst["content_match"] = bool(i_found and base._STATUS_RANK[i_status] == 0)
    return {"outcome": outcome, "proposal_state": state, "watermark_found": bool(s_found or i_found),
            "semantic": semantic, "instance": inst, "semantic_code": f"{q_now:08x}", "perceptual_hash": f"{h_now:08x}",
            "binding_mode": binding_mode, "owner_id": owner.decode("utf-8"), "owners_tested": roster_size,
            "family": FAMILY, "revision": REVISION, "sketch_bits": SKETCH_BITS, "band": list(band),
            "whitening": whitening, "detector_config_id": config.hex(),
            "side_information": ["public OwnerID", "profile", "pinned CLIP weights", "pinned SD1.5 VAE encoder"],
            "seconds": time.perf_counter() - started}

# Two-factor instance check: frozen development protocol (Claude, 2026-10-17)

Frozen before any step-2b evaluation outcome was read; Claude did not open Codex's evaluation scores or report. The calibration split is the only data used to set thresholds. The user asked Claude to continue autonomously until the next important step.

## Hypothesis

The registry's instance check, D1 (E3's native fine-detail features, cosine), fails two kinds of look-alikes in opposite ways:
- **Synthetic texture siblings** (same layout, different fine texture): D1 rejects them (cosine at most .052), while layout descriptors call them identical (.99).
- **Real near-duplicate frames** (Tears of Steel, 3 s apart): pixel layout differs a lot (PSNR 16-18 dB, SSIM .35-.81 on the seven calibration pairs), yet D1 rates one pair at .587. That pair alone forced D1's calibrated threshold from .059 to .587.

A regenerated copy at img2img strength .1-.4 keeps the original's pixel-aligned layout and loses some fine texture. **Prediction:** requiring both D1 ≥ τ1 and an aligned-layout similarity B1 ≥ τ2 rejects both look-alike kinds while accepting more regenerated copies than D1 alone at τ .587.

## Fixed definitions

- **D1:** unchanged native vector. Codex's cached vectors are used where available; otherwise the same function `journal_fine_gaussian_instance.descriptor`. Native weak-detail abstention counts as rejection.
- **B1:** the 512 RGB8 image converted to Pillow "L", box-resized to 32 × 32, mean-subtracted, L2-normalized; cosine.
- **B2:** SSIM on 64 × 64 grey (scikit-image defaults, data range 255). Descriptive only.
- **Accept rule:** D1 cosine ≥ τ1 **and** B1 cosine ≥ τ2.
- **Records:** F5 r2 marked clean images (`supplier-attempt1/F5-bootstrap.png`).
- **Near-duplicate negative:** record frame 0, query frame 1.
- **Synthetic siblings:** the six fixed `watermark_synthetic.scene(seed, 512, 512, 12.0, d)` pairs, d = 11 against d = 12, added as negatives.

## Threshold selection (calibration split only)

Calibration negatives: every wrong-source pair Codex enumerated, the calibration T4 residual transfers, the seven calibration near-duplicate pairs and the six synthetic siblings.

For each τ2 in {0.50, 0.51, …, 0.99}:
- τ1(τ2) = max(nextafter(max D1 over negatives with B1 ≥ τ2), 0.0594367), where 0.0594367 is the 2a screen threshold.
- Score = calibration C1 positives accepted by source majority (at least 2 of 3 seeds) at strength .2, summed over SD1.5 and SD2.1 (out of 40).

Choose the τ2 with the highest score. Ties go to the higher .4 sum, then to the larger τ2. Freeze (τ1, τ2) in a committed JSON before evaluation.

## Evaluation (untouched split)

Untouched split: the 40 evaluation sources, the 13 evaluation near-duplicate pairs, the evaluation T4 transfers and all ordered wrong-source pairs.

**Report:**
- descriptor-level source-majority acceptance per regenerator × strength;
- joint acceptance with Codex's recorded pointer outcome (F_R);
- false accepts per negative family;
- the D1-only τ .587 baseline on the same rows.

**Development pass:** source-majority joint F_R ≥ 36/40 at .2 on both SD1.5 and SD2.1, with zero observed false accepts. This is the same bar as the brief. Strength .4 is reported whatever it shows.

**Limits:** this is development evidence, and the rule was designed after seeing calibration data. Human admissibility is missing, and no held-out data are used.

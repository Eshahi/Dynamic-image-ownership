# H5 — L/Δ/σ sketch and FPR check (draft, CPU only)

## 1. Zhao et al. mapping for F5

Theorem 4.3 in Zhao et al. (arXiv 2306.01953): for a watermark with embedding
φ: x → z and additive Gaussian noise N(0, σ²I) in representation space,
detection after x' = A(φ(x_w)+N) has Type-II error governed by L·Δ/σ where
Δ = ‖x_w−x‖_pixel and L is the local watermark-specific Lipschitz constant
‖φ(x_w)−φ(x)‖ ≤ L·Δ. The bound is an *upper* bound on detector advantage;
large L·Δ makes the bound vacuous (no guarantee of removal).

For SD1.5 img2img:
- φ = VAE encoder E (pinned, public), z ∈ R^{4×64×64}.
- The attacker adds noise in latent scaled by `strength` s (VLB schedule); σ(s) ≈ schedule_std(s) · sqrt(1−ᾱ) — linear in s for small s.
- L is *directional*: F5 chooses Δ to maximise ‖E(x+Δ)−E(x)‖ at fixed ‖Δ‖ (encoder gain). Measured L_eff ≈ 20–27× the decoder-rendering L_nat at equal PSNR (see f5-encoder-amplified-latent §Probe, median at 52 dB: latent signal 15.9 vs 0.6; at 46 dB: 26.5 vs 1.3).

So F5's post-attack displacement is a_eff·‖Ws‖ where a(s) is per-strength attenuation (≈1.0 at .05, .91 at .1, .80 at .2, .57 at .4 from h1-probe). Per-chip SNR ≈ a·margin / sqrt(v). With 320 chips, semantic score = sum margins / sqrt(320) ≈ a·4.0·sqrt(320)/sqrt(v) — but v grows with s, so SNR(s) ≈ SNR(0)·a(s)/sqrt(1+ c·s²). Empirically SNR median (h1-probe): .05 7.0, .1 4.5, .2 2.8, .4 1.4. Threshold for carrier found is ~5 (Bentkus-Dzindzalieta at FPR 1e-6, roster 1). So carrier stays above threshold to ~.2, marginal at .4 — matches gate: .2 28/28, .4 23/28, failures mostly binding not carrier.

## 2. Capacity sketch

Robust tier: 320 chips, each chips carries one bit of the 32-bit code with redundancy ~10. Rate R = 32/320 = 0.1. Shannon capacity of AWGN channel with per-chip SNR(s) is 0.5·log2(1+SNR²). At s=.2, SNR≈2.8 → C≈1.5 bits/chip → plenty. Bottleneck is semantic binding (code drift under regeneration), not channel capacity. At s=.4, SNR≈1.4 → C≈0.8 bits/chip → still above 0.1, but margin thin → occasional carrier misses.

## 3. FPR check on unmarked

Claims: robust key statistic is weighted sum of independent random signs → null symmetric, zero-mean, false-positive bound from Bentkus-Dzindzalieta holds; regenerated unmarked images should not increase the statistic.

h1-probe: blind_std on 12 unmarked C0 chips = 0.73, while embedded margins ≈ 4.0/√320 per chip? Actually per-chip margin ≈ 4.0/√(?) — need exact normalisation. But separation is ~5σ.

Empirical check: gate r2 reports 0 detections on 159 C0 rows × 4 owners and 0 wrong-owner detections (all strengths), and T5 joint collisions 0/66. H1 blind per-chip std measured, but full detector FPR on ~200 C0/C2 images is the direct check — passes.

Full empirical FPR on regenerated unmarked: gate includes C0+T3 rows (unmarked attacked); none found. So regenerated unmarked does not inflate statistic — host spread σ_h ≈ 0.73 unchanged by attack (host cancels in differential measurement).

## 4. Prediction vs measurement

Predicted post-attack score ≈ clean_score · a(s). Clean score median ~13.3 at psnr52; predicted at .4: 13.3·0.57 ≈ 7.6; measured median at .4 ~10.4? Actually diagnostic median 10.4 includes survivors only. Slight underestimate — suggests PGD margin 4.0 gives headroom beyond linear attenuation. Need to measure clean vs attacked score pairs directly for calibration.

TODO: after stress baseline, compute per-source predicted vs measured curve and log residuals.

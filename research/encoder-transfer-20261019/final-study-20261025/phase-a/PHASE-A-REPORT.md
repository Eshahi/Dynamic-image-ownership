# Final study, Phase A: report and freeze

Written by Claude (Opus 5.5) on 2026-10-26. Phase A ran on development sources only, under the user's approval of 2026-10-26: Phase A with option (a), with a cap of 22 instance-hours. No held-out (Phase-B) pixel was acquired or used. The frozen values are in [PHASE-A-FREEZE.json](PHASE-A-FREEZE.json). The full descriptive tables are in [phase-a-tables.md](phase-a-tables.md), and the revised resource forecast is in [phase-b-forecast.json](phase-b-forecast.json). The protocol says to stop for the user before Phase B, so this report ends there.

## 1. What ran

- **Machine:** vast.ai instance 57583551 (RTX 4090, USD .448/h), up from 08:08 to 15:26 UTC. That is about 7.3 instance-hours, or about USD 3.3, of the 22-hour cap. The instance is stopped, not destroyed.
- **Stage 1 (08:59–10:57):** 60 development sources × six R0/R1 cells × three seeds × five inputs, giving 5,400 native outputs. The 1,080 F5 full-chain law tangents were computed with the option-(a) kernels. The maximum primal error is 0.0 in every cell.
- **Attack quality grids (10:57–13:33) and selection freeze (13:33):** 2,880 A outputs and 2,160 B outputs. Selection used quality only; no detector output existed at that point.
- **After the freeze:** controls, then the detector release (13:34–15:01): 9,080 detector rows, none in error. The mechanism module covered 12 sources × three encoders.
- **Fit (15:01):** κ, q90 and the quality comparator.
- **Retrieval:** everything was fetched home in hash-checked byte ranges into `.thesis-build/dev-runs/20261026-0855-et-final-phase-a/`. The tar and journal hashes are in its `run.json`.

**Engineering events.** None of these changed a stage-1, attack, detector or fit row.

- The 48 SDXL encoder-gain rows of the mechanism module first failed, because the official SDXL VAE wrapper refuses fp16 encodes. They were fixed (commit 55f4159) and rerun: 48/48 ok.
- The mechanism process then ran out of GPU memory when loading K3 after SDXL. It was fixed (commit 5072221), and K3 ran in its own process: 84/84 ok.
- **Safety-checker blocks** (SD1.5 only, never bypassed or retried):
  - native outputs: 3 at .1, 9 at .2 and 10 at .4;
  - unavailable law vectors: 2 at .1, 3 at .2 and 4 at .4;
  - 10 attack-A grid rows.

## 2. Frozen results

| Item | Value | Status |
|---|---|---|
| κ (pooled, 30 fit sources) | 0.02865 | `FIT_QUALIFIED_INCOMPLETE`: 533/540 vectors, every triplet has ≥2/3, every cell has ≥87/90 |
| q90 (30 calibration sources, native decoded-score units) | 15.10 | `RADIUS_CONSERVATIVE_FINITE`: 28/30 complete; sources 1398 and 1536 are +∞ |
| Six-feature quality comparator | converged, 176 rows, 73 positives | **`BASELINE_UNAVAILABLE`**: source 459 has only 4/6 feature-complete cells (C0 safety blocks), and the contract requires ≥5/6 for every source |
| Attack A (SDXL→SD1.5 two-pass) | no eligible strength | **`INACTIVE_QUALITY_INELIGIBLE`** |
| Attack B (latent decorrelation) | no eligible (ε, λ) | **`INACTIVE_QUALITY_INELIGIBLE`** |

**Attack eligibility.** Eligibility needs ≥48/60 passing source majorities in every arm under LPIPS ≤ .15, PSNR ≥ 25 and SSIM ≥ .75 against the marked input.

- The best A setting (.05) reached 24–27 sources per arm.
- The best B settings (ε = .225, λ ≤ 1) reached 30–37 sources per arm.
- The binding limit is SSIM. The median SSIM of A at .05 is .737, and B stays at .733–.759 across all nine settings. The regeneration and inversion codecs alone already sit at the threshold.

**Consequences under the frozen protocol, before any Phase-B data:**

- **H4:** unavailable comparator coverage prevents primary H4 evaluation (training-missingness-design.md), so H4 keeps p = 1.
- **H5:** both attacks are inactive, so all eight A/B H5 slots keep p = 1 (07 section 6).
- **Still open in Phase B:** H1, H2, H3 and H6.

## 3. Development detector results (descriptive)

These are source majorities over 60 development sources, each mark read by its own detector (C0 read by all four).

| Cell | F5 r2 | v5 r3 | WAM | VINE-R |
|---|---|---|---|---|
| R0 .1 | 60 | 47 | 42 | 60 |
| R0 .2 | 57 | 27 | 18 | 60 |
| R0 .4 | 39 | 3 | 1 | 47 |
| R1 .1 | 0 | 50 | 49 | 60 |
| R1 .2 | 0 | 11 | 2 | 60 |
| R1 .4 | 0 | 0 | 0 | 45 |
| B-codec control | 60 | 60 | 55 | 60 |

**Negatives.** F5, v5 and WAM have no C0 or wrong-owner/wrong-message event in any cell. VINE-R has **one C0 known-message event**: `native:R1-0.1:1295:14:unmarked`, with 69/100 bits at a threshold of 69. Under the negative-gate rule (07 section 6), its C0 stratum would therefore fail on development data. Historical VINE false detections already exist, and a fresh gate cannot erase them.

**Development direction of the open hypotheses.** These are not tests.

- **H1:** F5 retention at R1 .1 and .2 is 0/60, against a required rate below .10.
- **H2:** F5 at R0 .2 is 57/60 = .95. At n = 200 the sufficient count is ≥175.
- **H6:** VINE-R is at 60/60 in R0 .2, R1 .1 and R1 .2. At n = 200 the sufficient count is ≥191.
- **H3:** this needs native quality against the marked input, which Phase A did not compute, so it has no development estimate here.

## 4. The law: why it fails, from development data

The frozen pooled law predicts no F5 survival in any cell, while actual development survival is 1.00 / .95 / .65 at R0 .1 / .2 / .4. On R0, the law Brier score is therefore equal to the actual rate. The fit-split decomposition below is descriptive and reads no calibration source ([kappa_decomposition.py](kappa_decomposition.py), [kappa-decomposition.json](kappa-decomposition.json)).

| Cell | Cell κ | Median cos(v, p1−b) | Median ‖v‖/‖p1−b‖ |
|---|---|---|---|
| R0 .1 | 1.08 | .90 | .83 |
| R0 .2 | 0.98 | .83 | .80 |
| R0 .4 | 0.61 | .68 | .93 |
| R1 .1 | .0046 | .047 | 7.7 |
| R1 .2 | .0010 | .016 | 14.8 |
| R1 .4 | .0001 | .013 | 14.2 |

- **SD1.5 behaves like a first-order law with κ ≈ 1.** The family κ is .94. The tangent points the right way and has about the right size, except at .4, where the remainder grows.
- **The SDXL tangent is not informative.** It is 8–15 times larger than the actual chip change and almost orthogonal to it. This matches the pilot's finite-difference check: at h = 1, SDXL's response is nonlinear (cos .03), while SD1.5 stays near-linear.
- **SDXL dominates the pooled κ.** SDXL is 97% of the pooled denominator Σ‖v‖², so the single global κ follows SDXL's 0.001 rather than SD1.5's 0.94.

The protocol forbids family coefficients and says that development outcomes "may falsify the law, but cannot trigger undeclared model rescue". This is that falsification. A family-specific κ would be a declared amendment, and the user would decide it before Phase B (section 7).

## 5. Mechanism module (12 sources, descriptive)

**Encoder gain** is latent norm per unit pixel norm, along the actual mark residual, against norm-matched Gaussian and Fourier-phase controls. Values are medians.

| Encoder | F5 actual | Controls | v5 | WAM | VINE-R |
|---|---|---|---|---|---|
| SD1.5 VAE | 15.0 | 4.8–6.4 | 7.4 | 6.3 | 6.0 |
| SDXL VAE (1024 Lanczos) | 392 | 178–249 | 136 | 31 | 63 |
| K3 MoVQ (1024 Lanczos) | 43.3 | 20–27 | 15.5 | 10.6 | 7.5 |

F5's residual is the most amplified direction in all three encoders: 2.3–3.1× its controls in SD1.5 and 1.6–2.2× in SDXL and K3. Encoder amplification transfers. Survival does not.

**Stagewise F5 retention** at strength .2 is e·Δchips relative to the clean value, as a median.

| Stage | SD1.5 | SDXL | K3 |
|---|---|---|---|
| Mode codec | .98 | .66 | .72 |
| Sampled codec | .98 | .66 | – |
| Noise only (decode of the noised latent) | .92 | **.08** | .34 |
| Mode + reverse steps | .74 | .08 | – |
| Native output | .74 | .08 | .17 |

The SDXL loss happens at the noise-injection stage, not in the codec. The denoising steps neither restore nor further remove the mark. The differential chain tangents agree:

- e·v along the actual direction is positive in every family (4.2 / 10.1 / 1.7), and controls sit near 0 in SD1.5 and K3.
- e·v/‖v‖ is .28 in SD1.5, .016 in SDXL and .08 in K3.

None of this is causal evidence. The comparisons are paired, within source and descriptive.

## 6. Revised Phase-B forecast (measured)

The forecast comes from [forecast_phase_b.py](forecast_phase_b.py), using p90 per-unit times and a 30% margin.

- **Native + law units:**
  - R0/R1: 2.0–12.8 s each (median), 6.8 h;
  - K3: 1.7 h, from the pilot's chain JVP plus five historical natives (6.6 h on the conservative mechanism-row bound).
- **Detection:** 6.2 h. It is CPU-bound and could overlap GPU work.
- **Clean embedding:** 7.0 h. This is historical: F5 takes 119 s per source.
- **Quality metrics:** 2.7 h.
- **B-codec:** 0.1 h.

**Total: about 36 h, or USD 16.** That is 31.7 h with margin, plus 1.5 h setup and 3.1 h retrieval for about 23,000 outputs at the measured 0.85 MB/s. It rises to about 43 h on the K3 upper bound. The protocol's proposed Phase-B ceiling was ≤60 h.

## 7. Decisions for the user before Phase B

1. **Run Phase B at all.** It can still confirm H1, H2, H3 and H6 on 200 fresh POTD sources: F5 holds under SD1.5, F5 fails under SDXL, and VINE-R holds. H4 and the eight H5 slots are already fixed at p = 1 by the freeze.
2. **The law's derivatives in Phase B.** H4 cannot be evaluated, so the 4,200 law JVPs would only feed descriptive tables. Options:
   - **(a) keep them as frozen** (descriptive);
   - **(b) declared amendment: drop them**, saving about 4–5 h;
   - **(c) declared exploratory amendment:** keep only the cheap R0 JVPs and add a family-specific κ fitted on the 30 fit sources, reported outside the Holm family as an explicitly post-falsification model.
3. **H3 quality.** H3 needs native quality against the marked input for every R0 .2 and R1 .1 output. It is already in the protocol, and the forecast includes it.

## 8. Files

| File | What it is |
|---|---|
| `PHASE-A-FREEZE.json` | Every frozen value, code/config/run-file hashes, events and consequences |
| `phase-a-tables.md` | Full descriptive tables, including every arm and attack-grid quality |
| `kappa-decomposition.json` | Fit-split κ by family and cell |
| `phase-b-forecast.json` | Measured timers and forecast components |
| `summarize_phase_a.py`, `kappa_decomposition.py`, `forecast_phase_b.py`, `write_freeze.py` | Generators, stdlib + numpy |
| `scripts/et_final_phase_a*.py`, `scripts/et_final_phase_a_driver.sh` | Server code, hashes as in the freeze |

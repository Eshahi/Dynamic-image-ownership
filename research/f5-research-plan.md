# F5 research plan — claude/f5-research (2026-10-05)

Base: `513e887` (F5 r2: encoder-amplified latent, soft binding, 7-view CLIP; psnr 52 dB).
Threat scope: T3/T4/T5 only (`AGENTS.md`). Existing gate (`.1/.2` vs v5 r3) is non-regression.

## 0. Frozen stress grid (development only, document before selection)

Purpose: `.1/.2` is near-saturated (F5 r2: 29/29, 28/28). Selection on `.4/.5/.6` where headroom remains (F5 r2 vs v5: `.4` 23 vs 2, `.5/.6` untested). Keep gate as regression check; stress grid is for ranking new candidates.

Pinned attacker: `runwayml/stable-diffusion-v1-5`, DDIM, `strength ∈ {.4,.5,.6}`, `guidance_scale = 1` (keep) plus a second family at `guidance_scale = 7.5` with an automatic caption (BLIP or fixed prompt "a photo") and `num_inference_steps = 50` (vs 20 in gate). Seeds `{0,1,2,3,4}` (5 vs 3). Same 12 development sources, matched identities vs v5 where possible; new v5 baselines on the extended grid for comparison.

Implemented as: `scripts/f5_stress_gate.py` (wrapper over `f5_gate.py` with `--strengths`/`--seeds`/`--steps`/`--cfg`/`--caption`) + `scripts/f5_stress_assess.py` reusing `m1_assess_*`. Runs under `.thesis-build/dev-runs/`. No held-out data. Commit the grid script and this section before any selection run.

Metrics for selection: paired C1 `both_match` count (primary), `semantic-only` count, carrier-only count, distribution of latent score margin and soft distance, CLIP cosine retention rate (<.90 = not retained). T4/T5 unchanged (must stay 0 false attribution/collisions).

Replacement criteria (from prompt, frozen here):
- T3 improves on stress grid AND gate (`.1` 29/29, `.2` 28/28, `.4` ≥23/28) without regression;
- T4 0/20, T5 0/66, C0/wrong-owner 0;
- clean quality not worse than F5 r2: LPIPS mean ≤.0173, max ≤.050, PSNR mean ≥44 dB, else visual comparison and user verdict.

## 1. Ranked hypotheses (test cheapest decisive first)

All hypotheses state a kill criterion. Variants counted; failed runs kept.

**H1 — Carrier geometry: matched filter / band retuning.**
Claim: under T3, post-attack noise is coloured; weighting chips by post-attack SNR raises margin. Also band 4–32 may include bins the denoiser removes.
Test: measure post-attack noise covariance of chip projections (F5 r2 images, `.4/.5`, 12×5 rows): per-chip mean attenuation `a_i = E[p'_i / p_i]` and variance `v_i`. Detector: whitened statistic `s = sum a_i w_i p'_i / v_i`. No re-embedding needed (re-read). Second test: re-embed with narrower bands (8–28, 6–24, 4–24) vs 4–32, equal PSNR 52.
Kill: re-read gain < +1 paired match at `.5` (p≈.5 with n=60, need ≥+2 to claim) or any LPIPS regression; band change must beat 4–32 on `.4` and `.5` paired.
Cost: 1 GPU re-read + 3 embeddings (≈15 min).

**H2 — Attack-aware PGD (expectation over attack).**
Claim: optimizing through encoder + K DDIM steps for post-attack margin beats pure encoder gain, at higher cost.
Test: PGD loop: `encode(x+δ) → add scaled noise per strength → K=3 UNet denoising steps → decode → encode → margin loss`; expectation over strengths {.4,.5} and 2 seeds. Compare to pure encoder PGD at same PSNR, same steps (150). First run K=1 and K=3, then decide.
Kill: no paired gain at `.5` over pure encoder at equal LPIPS, or ≥2× embedding time without ≥+2 at `.5`, or T4 copy-paste starts to carry (semantic delivered >1/20).
Cost: high (requires UNet graph); run last.

**H3 — Quality per robustness: perceptual budget.**
Claim: same robustness at lower pixel budget via LPIPS-in-loop or texture mask (`mask_power` already in codec, untested; worst image 147498 sky).
Test: (a) mask_power ∈ {0.5,1.0,1.5} at psnr 52; (b) at psnr 50 with mask vs psnr 52 without, matched LPIPS. Re-embed only.
Kill: no LPIPS mean drop ≥15% at equal paired T3 count, or mask raises T4/T5.
Cost: 4 embeddings.

**H4 — Binding under strong regeneration.**
H4a Longer semantic code: 32 bits → 48 bits by adding 16 projections (capacity exists; carrier has 320 chips). Re-derive Bentkus radius for FPR target.
H4b More invariant pooling: CLIP augmentations beyond 7 views (scale 0.9/0.75, colour jitter).
H4c Calibrated decision: per-codeword soft threshold (learn φ→t map on dev unmarked).
Test each on re-read where possible; re-embed only for code-length change.
Kill per sub-variant: no paired gain at `.5` over F5 r2 soft/7-view at equal FPR (different-label matches ≤2/114, T5 0/66).
Cost: low (re-read) except H4a.

**H5 — Theory: L/Δ/σ prediction and FPR bound check.**
Derive post-attack score prediction from budget and strength; bound capacity. Empirically check latent key statistic on unmarked images (including regenerated) is symmetric/zero-mean as claimed.
Kill: theory mismatch > 3 dB or FPR bound violated on dev unmarked (≈200 images).
Cost: analysis only.

## 2. Order

1. Freeze and commit stress grid (today).
2. H1 re-read, then H1 band re-embed if re-read shows promise.
3. H3 (cheap perceptual sweeps).
4. H4 re-read variants.
5. H5 analysis in parallel.
6. H2 only if H1/H3/H4 plateau and thesis contribution needs it.

Stop after ~3 consecutive well-founded failures or readiness (hard stop 1), then M1b.

## 3. Provenance

Every run: committed code, `.thesis-build/dev-runs/<ts>-<slug>/run.json`, one line in `experiments/dev-log.md`. One GPU job at a time. No held-out touch.

## 4. Risks

- Other VAE/UNet families untested — note as limitation.
- Stress grid at CFG 7.5 may be caption-sensitive; report per-caption if used.

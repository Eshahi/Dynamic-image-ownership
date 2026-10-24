# ROUTE C article skeleton (draft, not submission-ready)

Written by Claude (Opus 5.5) on 2026-10-24, after stage 2a gave FAILS, ROUTE C. This is a planning skeleton built on development evidence (60 development sources, one SDXL setting).
- It is not a manuscript, and it does not claim Q1 readiness or novelty.
- Every number below comes from `../results.md` and `../report/tables.md`.
- Every citation must come from a card under `../design-research/*/cards/` that was actually opened; nothing here may be cited from memory.

## Working titles (pick one later)

1. *Same-family regeneration overstates the robustness of encoder-directed image watermarks: a pre-registered cross-encoder test*
2. *Surviving your own autoencoder is not surviving regeneration: an SD1.5-directed watermark under SDXL img2img*
3. *Where an encoder-amplified watermark dies: autoencoder round trips, same-family and cross-family diffusion regeneration*

## Abstract (draft; numbers are development evidence)

**Problem.** Image watermarks are often tested for "regeneration" robustness with diffusion models that share the writer's autoencoder. We test whether an encoder-directed image-domain watermark (F5), optimized through the Stable Diffusion 1.5 encoder, survives regeneration by a model with an independently trained autoencoder.

**Design.** A pre-registered, frozen design with 60 development sources and three seeds. The primary endpoint is semantic-bound detection at SDXL img2img, strength .2, with a fixed decision rule.

**Results:**
- **Within the family:** F5 survives SD1.5 img2img in 57/60 sources (SD2.1-base 24/24 in an earlier cohort, which shares the SD1.x encoder).
- **Under SDXL img2img:** it survives in 0/60 (CP95 0 to .06), with zero false detections in 360 negative calls.
- **Autoencoder round trips alone:** it survives the SDXL VAE and Kandinsky 3 MoVQ round trips (55/60 each).
- **Baselines under SDXL img2img:** VINE-R survives (60/60), while WAM (2/60), TrustMark Q (0/60) and Pixel Seal (0/60) do not. All of them survive the SDXL VAE round trip.

**Conclusion.** Two practical cautions follow, bounded to the tested configuration:
- same-family regeneration does not certify cross-family robustness;
- autoencoder round-trip robustness is not a proxy for diffusion regeneration.

## Contributions (bounded)

1. **A pre-registered cross-encoder test** of an encoder-directed watermark: a frozen decision rule, negative gates and controls that separate the resize, autoencoder and diffusion components (X1, X2, D1, D3 against R1).
2. **Evidence of family-bound robustness:** F5's margin falls by 12% under SD1.5 img2img and by 82% under SDXL img2img (post-hoc and descriptive, Figure A1). The primary label is FAILS.
3. **Autoencoder round trips mispredict regeneration survival in this setting:** every arm survives D1 (55–60/60), but only VINE-R survives R1.
4. **Fair-reporting practice:** fixed operating points, source majority with CP intervals, unresolved-negative handling, matched-distortion bins reported even when empty, and empirical ROC labelled as outcome-selected.

## Section plan

### 1. Introduction
- Regeneration attacks as the main threat to pixel-domain marks. Cite from `T4-mechanism/cards/zhao.md`, `saberi.md` and `diffpure.md`, and from `T1-attack-standards/cards/` (benchmark cards, VINE/W-Bench).
- The gap: "unseen regenerator" tests that share the writer's encoder. Step 1 used SD2.1-base, which keeps the SD1.x encoder (`T2-encoder-landscape/cards/sdxl.md`, `ldm.md`).
- The question and what is pre-registered. State that the image-domain F5 is a labelled comparator, not a latent-space method.

### 2. Related work
- **Pixel-domain and learned marks:** WAM, TrustMark, Pixel Seal and StegaStamp (`T3-baseline-fidelity/cards/`).
- **Generative-attack-trained marks:** VINE (`T3-baseline-fidelity/cards/VINE.md`).
- **Regeneration and purification attacks:** `T1-attack-standards/cards/`, `T4-mechanism/cards/`.
- **The encoder landscape:** which diffusion families share autoencoders (`T2-encoder-landscape/`).

### 3. Threat model and scope
- **T3 regeneration only:** img2img at fixed strength, no prompt, CFG 1. The attacker does not know the key.
- **Not in scope:** adaptive attacks, T1/T2 signal attacks and forgery.
- **Detector side information:** Table 1. F5 and v5 use the claimed owner, a public profile, pinned CLIP and the SD1.5 VAE; the external arms use the candidate message.

### 4. Method
- **Arms and operating points:** Table 1; F5 r2 settings frozen from earlier work, with no retuning.
- **Channels:** R0 SD1.5, R1 SDXL (img2img .2, DDIM 20, 4 executed steps, seeds 12, 13 and 14); D1 SDXL VAE; D3 MoVQ; X1 and X2 resize controls.
- **Endpoints:** C for F5 and v5; common known-message presence for the external arms. Success is a source majority (at least 2 of 3 seeds); blocked positives count as failures.
- **Decision rule, fixed before outcomes (BRIEF section 3):**
  - TRANSFERS needs C ≥ 45/60 and zero false detections;
  - FAILS means C < 30;
  - otherwise PARTIAL.
  - The route uses B = max(WAM, VINE-R).
- **Statistics:** CP95 intervals and three paired exact sign tests with Holm adjustment; everything else is descriptive (T6).
- **Quality ledger:** embedding, attack and total distortion are reported separately, with the strict gate PSNR > 35 dB, SSIM > .9 and LPIPS < .1 (T7).
- **Pre-registration history, stated plainly:**
  - the stage-1b freeze and the amendment 1d (user decisions);
  - four implementation-only fixes before any outcome;
  - an independent review of the results.

### 5. Results
1. **Primary decision** (Table 2, Figure 1): F5 0/60 at R1 .2, negatives 0/360, so FAILS. B = 60.
2. **Same family against an independent family** (Table 8):
   - SD1.5 57/60 overall, 22/24 on the step-1 sources;
   - SD2.1 24/24 in the earlier cohort;
   - SDXL 0/60 overall, 0/24 on the step-1 sources.
3. **Where the mark is lost** (Table 3a, Figure 6, Figure A1):
   - resize keeps 60/60;
   - D1 and D3 keep 55/60;
   - R1 gives 0/60.
   - The D1/R1 contrast is compound (posterior mode in fp32 against a sample after fp16 rounding, plus denoising), so no single cause is claimed.
4. **Baselines** (Table 3b): every arm survives D1; only VINE-R survives R1, with median bit accuracy .90. WAM abstains on 136 of 180 R1 calls because of empty masks.
5. **Negatives** (Table 5): all zero, with R0 unresolved calls only from safety blocks. The ROC is outcome-selected and descriptive, and at R0 it is not estimable.
6. **Quality and distortion** (Table 4, Figures 2 to 4, Table 6):
   - R1 is milder than R0 in median pixel terms, yet more destructive for F5;
   - the matched R0-against-R1 comparison has 0 pairs;
   - clean quality is unmatched: VINE-R passes the strict gate on 31/60, F5 on 60/60.
7. **Cost** (Table 7): the F5 embedding takes about 118 s per image on an RTX 4090; the full run took 4.8 h.

### 6. Discussion
- **Robustness tied to the writing encoder:** F5's semantic margin holds through SD1.5 regeneration but not through SDXL. Its two tiers behave in opposite directions (Figure A1); this is post-hoc, and no design may be tuned on it.
- **Autoencoder round trip against regeneration:** a cheap VAE test passed by every arm says little about diffusion regeneration here.
- **Why VINE-R may survive:** only as a literature-grounded hypothesis (its training against generative edits and its SD-Turbo-based design, `VINE.md`). It was not tested here.
- **Implications for evaluation practice:**
  - name the regenerator's autoencoder family;
  - include at least one independently trained autoencoder;
  - report autoencoder-only controls next to full regeneration.

### 7. Limitations (keep them all)
- One SDXL configuration (strength .2 only); 60 development sources from a convenience cohort, not a probability sample; no held-out confirmation.
- Strengths .1 and .4, the rinse, FLUX (gated), full Kandinsky regeneration and encoder-aware smoothing were not run (stage 2b by design).
- Clean quality is unmatched across arms, and the matched-quality frontier is unestablished. Human perceptual ratings are missing.
- The external presence rules for TrustMark and Pixel Seal are uncalibrated binomial rules.
- The image-domain F5 is not the proposal's latent method (RQ-02/HYP-02 remain open).
- The independent review is by a fresh Claude agent, not the reviewer the brief names.

## What a Q1 reviewer is likely to ask for (gap list for the extension decision)

| Gap | Why it matters | Possible remedy |
|---|---|---|
| One SDXL strength | A single point cannot show whether F5 fails at weak SDXL strengths too | SDXL strength sweep (for example .05, .1, .3, .4) on the frozen arms |
| One independent family | "Cross-family" needs more than SDXL | A second independently trained regenerator (for example SD3 or full Kandinsky 3 img2img; FLUX is gated) |
| Development cohort only | n = 60 dev sources, convenience | Fresh pre-assigned held-out sources, with a confirmatory protocol and the user's approval |
| Unmatched quality | VINE-R's PSNR is 35.1 dB, against 45.0 for F5 | A matched-quality frontier or a documented native-setting argument |
| Mechanism | The D1/R1 contrast is compound | Optional diagnostics, such as SDXL with the posterior mode at strength 0, or noise-only without denoising, pre-registered as descriptive |
| Figures from development data only | Article figures need the confirmatory run | Rerun `scripts/encoder_transfer_report.py` on the confirmatory outputs |

Any extension needs a new pre-outcome amendment and the user's decision. SDXL outputs from this run must not be used to tune F5 or any threshold.

## Figure and table map

| Article item | Source |
|---|---|
| Table: design | `../report/tables.md` Table 1 |
| Table: primary and baselines | Table 2 |
| Table: endpoint grid (appendix) | Table 3 |
| Table: quality (appendix) | Table 4 |
| Table: negatives and ROC (appendix) | Table 5 |
| Table: matching (appendix) | Table 6 |
| Table: cost | Table 7 |
| Table: same family against an independent family | Table 8 |
| Figure: success by channel | `../report/figures/fig1-success-by-strength.pdf` |
| Figure: controls | `fig6-controls.pdf` |
| Figure: margins (post-hoc) | `figA1-signal-margins.pdf` |
| Figure: quality | `fig3-clean-quality.pdf` |
| Appendix figures | `fig2`, `fig4`, `fig5`, `fig7` |

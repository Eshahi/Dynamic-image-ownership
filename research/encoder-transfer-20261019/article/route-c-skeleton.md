# ROUTE C article skeleton (draft, not submission-ready)

Written by Claude (Opus 5.5) on 2026-10-24, after stage 2a gave FAILS, ROUTE C. Updated on 2026-10-25 with the stage-2b results and the claims as corrected by the stage-2b review. This is a planning skeleton built on development evidence: 60 development sources, three SDXL strengths, one Kandinsky 3 setting.
- It is not a manuscript, and it does not claim Q1 readiness or novelty.
- Every number below comes from `../results.md`, `../results-2b.md` and `../report/tables.md`, which now renders the union of stages 2a and 2b. The claim wording follows `../review.md` and `../review-2b.md`.
- Every citation must come from a card under `../design-research/*/cards/` that was actually opened; nothing here may be cited from memory.

## Working titles (pick one later)

1. *Same-family regeneration overstates the robustness of encoder-directed image watermarks: a pre-registered cross-encoder test*
2. *Surviving your own autoencoder is not surviving regeneration: an SD1.5-directed watermark under SDXL and Kandinsky 3 img2img*
3. *Where an encoder-amplified watermark dies: autoencoder round trips, same-family and cross-family diffusion regeneration*

## Abstract (draft; numbers are development evidence)

**Problem.** Image watermarks are often tested for "regeneration" robustness with diffusion models that share the writer's autoencoder. We test whether an encoder-directed image-domain watermark (F5), optimized through the Stable Diffusion 1.5 encoder, survives regeneration by models with independently trained autoencoders.

**Design.** A pre-registered, frozen design with 60 development sources and three seeds. The primary endpoint is semantic-bound detection at SDXL img2img, strength .2, with a fixed decision rule. A descriptive extension adds:
- strengths .1 and .4;
- a two-pass SDXL rinse;
- full Kandinsky 3 img2img;
- one fixed encoder-aware smoothing attack with a matched control.

**Results:**
- **Within the family:** F5 survives SD1.5 img2img in 60, 57 and 39 of 60 sources at strengths .1, .2 and .4. SD2.1-base, which shares the SD1.x encoder, gave 24/24 in an earlier cohort.
- **Under SDXL img2img:** it survives in 0/60 at every tested strength (CP95 0 to .06 each), with zero false detections in 1,080 negative calls.
- **Not explained by distortion:** in every complete source, SDXL at .1 is milder than SD1.5 at .2 and .4 on PSNR, SSIM and LPIPS, yet removes the mark.
- **Under full Kandinsky 3 img2img at .2:** F5 survives in 5/60, where the v5 comparator keeps 57/60 and WAM 44/60.
- **Autoencoder round trips alone:** F5 survives the SDXL VAE and Kandinsky 3 MoVQ round trips (55/60 each).
- **Baselines:** VINE-R keeps at least 45/60 in every tested cell. The other baselines (v5, WAM) survive light SDXL (.1) and Kandinsky 3 but not SDXL at .2 or more, or the rinse.

**Conclusion.** Two practical cautions follow, bounded to the tested configuration:
- same-family regeneration does not certify cross-family robustness;
- autoencoder round-trip robustness is not a proxy for diffusion regeneration.

## Contributions (bounded)

1. **A pre-registered cross-encoder test** of an encoder-directed watermark:
   - a frozen decision rule and negative gates;
   - controls that separate the resize, autoencoder and diffusion components (X1, X2, D1, D3 against R1 and R3);
   - a pre-specified descriptive extension, run after the primary label was fixed.
2. **Evidence of family-bound robustness across strengths.** Under SDXL, F5 C is 0/60 at .1, .2 and .4; under SD1.5 it is 60, 57 and 39. F5's median semantic margin falls from 1.85 (clean) as follows (post-hoc and descriptive, Figure A1):

   | Regenerator | .1 | .2 | .4 |
   |---|---|---|---|
   | SD1.5 | 1.76 | 1.62 | 1.29 |
   | SDXL | .71 | .33 | .14 |

   The primary label is FAILS.
3. **A second regenerator family.** Full Kandinsky 3 img2img at .2 largely removes F5 (5/60) while v5 and WAM survive it. F5 is the only core arm below 30/60 under both SDXL .2 and Kandinsky 3 .2.
4. **Autoencoder round trips mispredict regeneration survival in this setting.** Every arm survives the D1 and D3 round trips (55–60/60), but at SDXL .2 only VINE-R survives.
5. **Fair-reporting practice:** fixed operating points, source majority with CP intervals, unresolved-negative handling, and empirical ROC labelled as outcome-selected.
   - The matched-distortion grid is reported even where it is nearly empty: across regenerator families the within-source calipers rarely overlap (F5 m = 2/60). That is itself a reporting lesson.
   - Equal numeric strength is shown not to be equal severity.

## Section plan

### 1. Introduction
- Regeneration attacks as the main threat to pixel-domain marks. Cite from `T4-mechanism/cards/zhao.md`, `saberi.md` and `diffpure.md`, and from `T1-attack-standards/cards/` (benchmark cards, VINE/W-Bench).
- The gap: "unseen regenerator" tests that share the writer's encoder. Step 1 used SD2.1-base, which keeps the SD1.x encoder (`T2-encoder-landscape/cards/sdxl.md`, `ldm.md`).
- The question and what is pre-registered. State that the image-domain F5 is a labelled comparator, not a latent-space method, and that only one encoder-amplified method was tested.

### 2. Related work
- **Pixel-domain and learned marks:** WAM, TrustMark, Pixel Seal and StegaStamp (`T3-baseline-fidelity/cards/`).
- **Generative-attack-trained marks:** VINE (`T3-baseline-fidelity/cards/VINE.md`).
- **Regeneration and purification attacks:** `T1-attack-standards/cards/`, `T4-mechanism/cards/`.
- **The encoder landscape:** which diffusion families share autoencoders, and how independent Kandinsky 3's MoVQ is (`T2-encoder-landscape/`; qualified, see `budget-and-proposals.md` P4).

### 3. Threat model and scope
- **T3 regeneration only:** img2img at fixed strengths, no prompt, CFG 1, plus a two-pass rinse. The attacker does not know the key.
- **One fixed encoder-aware smoothing attack (P5)** with a matched posterior-mode control; no tuned or learned adaptive attack.
- **Not in scope:** T1/T2 signal attacks and forgery.
- **Detector side information:** Table 1. F5 and v5 use the claimed owner, a public profile, pinned CLIP and the SD1.5 VAE; the external arms use the candidate message.

### 4. Method
- **Arms and operating points:** Table 1; F5 r2 settings frozen from earlier work, with no retuning.
- **Channels:**
  - R0 SD1.5 and R1 SDXL img2img at .1, .2 and .4 (DDIM 20; 2, 4 and 8 executed steps; seeds 12, 13 and 14);
  - the R1 rinse (.1 then .1, seeds 12+112, 13+113, 14+114);
  - R3, full Kandinsky 3 img2img at .2 (its native DDPM cosine schedule, 4 executed steps);
  - R1-smooth (P5) and R1-mode (control);
  - D1 SDXL VAE; D3 MoVQ; X1 and X2 resize controls.
- **Endpoints:** C for F5 and v5; common known-message presence for the external arms. Success is a source majority (at least 2 of 3 seeds); blocked positives count as failures.
- **Decision rule, fixed before outcomes (BRIEF section 3):**
  - TRANSFERS needs C ≥ 45/60 and zero false detections;
  - FAILS means C < 30;
  - otherwise PARTIAL.
  - The route uses B = max(WAM, VINE-R).
  - The rule applies to R1 .2 only; every other cell is descriptive.
- **Statistics:** CP95 intervals and three paired exact sign tests with Holm adjustment; everything else is descriptive (T6).
- **Quality ledger:** embedding, attack and total distortion are reported separately, with the strict gate PSNR > 35 dB, SSIM > .9 and LPIPS < .1 (T7). The rinse also has its second-pass-against-first-pass increment.
- **Pre-registration history, stated plainly:**
  - the stage-1b freeze and amendment 1d (user decisions);
  - four implementation-only fixes before any stage-2a outcome;
  - amendment 2b. The decision to run stage 2b was taken after the stage-2a label, as a scope decision. Its settings were fixed before any stage-2 output, at e318757 or in the approved proposals. Its analysis reproduces the stage-2a label from the inherited rows;
  - one independent review per stage.

### 5. Results
1. **Primary decision** (Table 2):
   - F5 is 0/60 at R1 .2, so FAILS; B = 60 (VINE-R).
   - The F5 negative gate over the full R1 grid is 0/540 C0 and 0/540 wrong owner.
2. **Strength curve** (Figure 1, Table 3):

   | Arm | SD1.5 .1 / .2 / .4 | SDXL .1 / .2 / .4 |
   |---|---|---|
   | F5 C | 60 / 57 / 39 | 0 / 0 / 0 |
   | v5 C | 47 / 27 / 3 | 50 / 12 / 0 |
   | WAM | 42 / 18 / 1 | 48 / 2 / 0 |
   | VINE-R | 60 / 60 / 47 | 60 / 60 / 45 |

   - At SDXL .1, F5's semantic tier is found in 26/180 calls (23 with a content match) but never read with a content match; at .2 and .4 it is never found.
   - At SD1.5 .4, F5 has 25 content mismatches.
3. **Not accounted for by larger attack distortion** (Figure 2, Table 4, Table 6):
   - **Within source:** in every complete source (58/58), F5's SDXL .1 output is milder than its SD1.5 .2 and .4 outputs on all three metrics, yet only SD1.5 keeps the mark. 39 sources succeed at SD1.5 .4 and fail at SDXL .1.
   - **Matched grid:** the pre-specified R0-against-R1 matched grid is too sparse to test this. F5 has m = 2 (SD1.5 2/2, SDXL 0/2); the SSIM and PSNR calipers rarely hold across families. So it stays descriptive.
4. **A second family** (Table 8, Figure 1):
   - **Results:** at Kandinsky 3 img2img .2, F5 is 5/60 (CP .028–.184; S 21, A 29), v5 57/60, WAM 44/60, VINE-R 60/60.
   - **Severity:** its .2 noises less than SDXL's .2 (ᾱ ≈ .94 against .83 at the same starting timestep), so equal numeric strength is not equal severity.
   - **Independence:** MoVQ's training independence is qualified.
5. **Where the mark is lost** (Table 3a, Figure 6, Figure A1):
   - **Controls:** resize keeps 60/60; D1 and D3 keep 55/60; R1 gives 0/60 at every strength and R3 5/60.
   - **Compound contrasts:** both the D1/R1 and the D3/R3 contrasts are compound (deterministic fp32 round trip against the fp16 pipeline with noising and denoising), so no single cause is claimed.
6. **Rinse** (Figure 6): a second SDXL .1 pass removes most of what survives the first.
   - **Counts:** v5 falls from 50 to 4, WAM from 48 to 21, F5 A from 52 to 34; VINE-R keeps 59.
   - **Distortion:** the rinse's LPIPS against the mark (about .14) is close to one .2 pass. It is not equated with .2.
7. **P5 smoothing** (Table 3; descriptive):
   - **Effect against its matched control:** F5's residual any-tier A (either tier found) falls from 32 to 16, and v5 A from 52 to 42. No source gains.
   - **Distortion:** smoothing also raises attack distortion, so the counts are not distortion-matched.
   - **F5's primary endpoint:** already at zero.
   - **R1-mode against sampled R1:** compound (precision, posterior mode and noise draw).
8. **Baselines** (Table 3b):
   - **VINE-R:** keeps at least 45/60 in every cell, with median bit accuracy .90 at SDXL .2.
   - **WAM:** abstains on 136 of 180 SDXL .2 calls because of empty masks.
   - **TrustMark Q and Pixel Seal:** 0/60 at SDXL .2.
9. **Negatives** (Table 5):
   - **F5 and v5:** zero false detections on every endpoint in every cell.
   - **VINE-R:** one false detection at exactly its threshold, in 2,094 C0 calls, consistent with its nominal tail.
   - **Unresolved calls:** only at R0, from safety blocks.
   - **ROC:** outcome-selected and descriptive; at R0 .2 it is not estimable.
10. **Quality and cost** (Table 4, Figure 3, Table 7):
    - **Clean quality is unmatched:** VINE-R passes the strict gate on 31/60, F5 on 60/60.
    - **F5 embedding cost:** about 118 s per image on an RTX 4090.
    - **Runs:** 4.8 h (stage 2a) and 4.0 h (stage 2b).

### 6. Discussion
- **Robustness tied to the writing encoder family.**
  - F5's semantic margin holds through SD1.5 regeneration across strengths. It collapses under SDXL at every strength and largely under Kandinsky 3, even where those passes are milder in pixel terms.
  - Its two tiers behave in opposite directions under SD1.5 and SDXL (Figure A1). This is post-hoc, and no design may be tuned on it.
- **Autoencoder round trip against regeneration:** a cheap autoencoder test, passed by every arm under both independent autoencoders, says little about diffusion regeneration here.
- **What the extension narrows, and what it does not:**
  - **It rules out within the grid** the explanations "SDXL is simply stronger" and "only .2 was tested".
  - **It does not isolate the encoder:** R0, R1 and R3 also differ in model family, resolution, scheduler and pipeline.
- **Why VINE-R may survive:** only as a literature-grounded hypothesis (its training against generative edits and its SD-Turbo-based design, `VINE.md`). It was not tested here.
- **Implications for evaluation practice:**
  - name the regenerator's autoencoder family;
  - include at least one independently trained autoencoder;
  - report autoencoder-only controls next to full regeneration;
  - report strength curves rather than one strength;
  - do not equate numeric strengths across schedulers.

### 7. Limitations (keep them all)
- **Scope of the tests:**
  - two regenerator families with independently trained autoencoders, three SDXL strengths and one Kandinsky 3 setting (.2);
  - MoVQ's independence from SD1.5 is qualified, and Kandinsky 3's .2 noises less than SDXL's;
  - FLUX was not run (gated);
  - only one encoder-amplified method (F5 r2) was tested.
- **Cohort:** 60 development sources from a convenience cohort, not a probability sample; no held-out confirmation.
- **Compound contrasts:** D1/R1, D3/R3, R1-mode/R1 and R0/R1 all differ in more than the encoder. No mechanism is tested.
- **Matched distortion:** the cross-family matched-distortion overlap is nearly empty (m = 2/60 for F5), so distortion-matched superiority is unestablished.
- **P5:** one fixed smoothing setting; no certified or tuned adaptive attack; P5 is not distortion-matched to its control.
- **Rinse:** not an independent replicate, and not equivalent to a single .2 pass.
- **Quality:** clean quality is unmatched across arms, and the matched-quality frontier is unestablished. Human perceptual ratings are missing.
- **Detection rules:** the external presence rules for TrustMark and Pixel Seal are uncalibrated binomial rules. VINE-R's one false detection supports no calibration claim.
- **Method:** the image-domain F5 is not the proposal's latent method (RQ-02/HYP-02 remain open).
- **Review:** the independent reviews are by fresh Claude agents, not the reviewer the brief names.

## What a Q1 reviewer is likely to ask for (gap list)

**Closed or narrowed by stage 2b** (`../results-2b.md`, reviewed):

| Gap | Status after stage 2b | What remains |
|---|---|---|
| One SDXL strength | **Closed within the grid:** F5 0/60 at .1, .2 and .4, with 0/1,080 negatives | Strengths below .1 (for example .05) are untested |
| One independent family | **Narrowed:** full Kandinsky 3 img2img .2 gives F5 5/60 while v5 57 and WAM 44 survive | MoVQ independence is qualified, and only one Kandinsky setting was run. A family with explicit from-scratch training beyond SDXL (for example SD3; FLUX is gated) would strengthen it |
| Strength or distortion as the explanation | **Narrowed:** SDXL .1 is milder than SD1.5 .2 and .4 in every complete source yet removes F5 | The matched grid cannot test it (m = 2), so it remains descriptive |
| Multi-pass regeneration | **Closed for one rinse:** v5 50 to 4, WAM 48 to 21, VINE-R 59 | Other pass counts and strengths |
| Encoder-aware adaptive attack | **Partly addressed:** one fixed P5 setting lowers residual signal against a matched control | No tuned or learned adaptive attack; P5 is not distortion-matched |

**Still open:**

| Gap | Why it matters | Possible remedy |
|---|---|---|
| Development cohort only | n = 60 dev sources, convenience | Fresh pre-assigned held-out sources, with a confirmatory protocol and the user's approval |
| Unmatched quality | VINE-R's PSNR is 35.1 dB, against 45.0 for F5 | A matched-quality frontier or a documented native-setting argument |
| Mechanism | All family contrasts are compound | Optional diagnostics, pre-registered as descriptive: for example SDXL with the posterior mode at strength 0, or noise-only without denoising |
| One method of the class | Only F5 r2 was tested | A second encoder-amplified writer, or the proposal's latent method |
| Figures from development data only | Article figures need the confirmatory run | Rerun `scripts/encoder_transfer_report.py` on the confirmatory outputs |

Any further extension needs a new pre-outcome amendment and the user's decision. SDXL and Kandinsky 3 outputs from these runs must not be used to tune F5 or any threshold.

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
| Table: same family against independent families (SD1.5, SD2.1, SDXL, Kandinsky 3) | Table 8 |
| Figure: success by strength, controls and the rinse, P5 and R3 cells | `../report/figures/fig1-success-by-strength.pdf` |
| Figure: robustness against achieved distortion | `fig2-robustness-vs-distortion.pdf` |
| Figure: controls and rinse against their parents | `fig6-controls.pdf` |
| Figure: margins by cell (post-hoc) | `figA1-signal-margins.pdf` |
| Figure: quality | `fig3-clean-quality.pdf` |
| Appendix figures | `fig4`, `fig5`, `fig7` (with the rinse pair) |

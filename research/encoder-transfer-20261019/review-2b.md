# Stage 2b independent review

Reviewer: a fresh Claude agent, independent of the author session. Date: 2026-10-25.

Under review: the untracked `results-2b.md` and the modified `report/` files and `scripts/encoder_transfer_report.py` on `claude/encoder-transfer-stage2` (HEAD 66d6944). I wrote only this file. I touched no server or network resource.

## Verdict

**ACCEPT WITH CORRECTIONS.** I recomputed the label from the final-state journal rows: it is **FAILS, ROUTE C**, the same as stage 2a.

- **Numbers:** every count, interval, discordant pair, carrier state, margin and negative in `results-2b.md` matches my recomputation, with two exceptions. One quality median is misrounded (C11). The wrong-message denominators are misstated at R0 (C12).
- **Claims:** three claims in the "may be claimed" list overreach (C1–C3). They repeat two wordings that the stage-2a review had already corrected, and they must be fixed before `results-2b.md` or its article frame is cited.
- **The label:** no finding affects it.

## What I recomputed (independently of `metrics.json`)

I wrote my own stdlib scripts. They keep the last journal line per unit `id`, and they recompute S, C, Q and A from the raw `semantic` and `instance` fields and the row payload. For WAM and VINE-R, they recompute presence from the decoded bits: for VINE-R from `round(probabilities)`, against SHAKE-256 messages with seed 20261019 and thresholds 27/32 and 69/100. Only then do I compare with `metrics.json`.

| Check | Result |
|---|---|
| Journal | 39,896 lines, 11,040 ids = 11,040 planned. Final statuses: 11,017 ok, 23 safety-blocked, all R0 (13 new: R0 .1 4, R0 .4 9) |
| Stored endpoints and presence against my recomputation from raw fields | 0 mismatches on every call |
| Source-majority S/C/Q/A (F5, v5) and presence (WAM, VINE-R), with missing calls, in all 10 R0/R1/rinse/R3/P5 cells | All equal `metrics.json` `cells` and every table in `results-2b.md` (strength curve, rinse, R3, P5, F5 S/A at R3) |
| CP95 (own bisection) | R0 .1 [.940, 1]; R0 .4 [.516, .769]; R1 .1 and .4 [0, .060]; R3: F5 [.028, .184], v5 [.861, .990], WAM [.603, .839], VINE-R [.940, 1]. All match |
| Rinse lost/gained (R1 .1 → rinse) | F5 A 18/0; v5 C 46/0; WAM 27/0; VINE-R 1/0. Match |
| P5 smooth-only/mode-only | F5 A 0/16; v5 C 0/2; v5 A 0/10. R1-only/R1-mode-only for v5 C: 7/1. Match |
| F5 read-first states | R1 .1: 154 not found, 23 found not read, 3 mismatch, 0 C; R1 .4, rinse, smooth and mode: 180 not found each; R3: 112, 46, 6, 16. Match |
| F5 primary negative gate, R1 .1/.2/.4, endpoint A, every call | C0 0/540, wrong owner 0/540, 0 unresolved; the same for v5. No F5 or v5 negative is positive on any of the 8 endpoints in any cell |
| R0 unresolved negatives | .1: C0 2 for every arm, F5 wrong owner 1, v5 wrong owner 0; .4: 2 each (C0 and wrong owner, F5 and v5; C0 for WAM and VINE-R). Match |
| VINE-R C0 false positive | One call, `R1:1295:unmarked:0.1:14`, 69/100 matches (threshold 69), out of 2,094 observed VINE-R C0 calls across both stages. WAM: 0 of 2,094 |
| Margins (median score/threshold) | Every value in the margins table matches. C0 medians run from −.092 to −.034, maximum .629 |
| Quality (complete-source medians, attack distortion) | All PSNR/LPIPS values in the distortion and strength-curve tables match except R1-mode F5 PSNR (C11). Rinse incremental LPIPS .069/.069/.070/.067 match. Complete-source counts (R0 .1 59/59/60, R0 .4 58/58/59) match |
| Matched grid (own implementation of the T7 algorithm) | All 72 comparison×bin cells equal `metrics.json`: F5 R0 vs R1 m = 2 ([.1, .2), R0 2/2, R1 0/2, both pairs .1/.2); v5 0; WAM 1; VINE-R 3 distinct sources (89, 723, 1647); F5 vs v5 within R0 [.1, .2) 38/60 |
| Images | All 7,187 new images in `stage2b-full/images/` match their journal SHA-256 |
| Input linkage | Every rinse row reads its R1 .1 parent output and references the original mark (`distortion`) and the parent (`incremental_distortion`); every P5/R3 row reads its clean mark |
| Tar hashes | results d423a1d8…, extras 97599e99… verified |

**Inheritance.**
- **Journal prefix:** the first 50,399,571 bytes of the stage-2b journal hash to 26b69451…, the SHA-256 of the stage-2a journal in MAIN and of `seeded-from.json`.
- **No overrides:** no inherited id has a later line, and all 3,840 inherited final rows are identical.
- **`metrics.json`:** the stage-2b file equals stage 2a's in the decision block, all 131 cells, the 3 Holm and 2 descriptive comparisons, all 40 quality, 243 negative, 19 external-operating-point, 52 ROC and 14 carrier-state blocks.
- **`matched_distortion`:** it differs in 9 of 12 comparisons, by design, because .1 and .4 now enter the grid.
- **Run guard:** the runner checks the label and route against `amendment.stage2a_decision` (`encoder_transfer_runtime.py`, about line 891).

**Report.** Rerunning `scripts/encoder_transfer_report.py --run <2b> --prior-run <2a>` into a scratch folder reproduces `tables.md` and all 20 figure files byte for byte.
- **Row coverage:** Tables 3, 4, 5a, 5b, 5c and 6 have exactly the number of rows that the `metrics.json` blocks imply (30 + 35, 158, 155, 35, 182 and 72), so no cell is silently dropped.
- **Spot checks:** I checked rows of Tables 2, 3, 5 and 8 against my recomputation, and they agree, including Table 8's R3 split (F5 0/24 + 5/36; v5 24/24 + 33/36).
- **`arms_by_strength`:** it is honoured: TrustMark Q and Pixel Seal appear only at R1 .2 (and D1).
- **Table 8:** it filters strength .2.

**Execution record.**
- **Instance and run clock:** instance start 00:11:36Z; driver start 00:42:14Z; full run 01:28:05Z to 05:29:21Z (14,474 s, 4.02 h).
- **Budget clock at the end of the run:** 19,064 s, or 5.30 h, USD 2.37 at USD 0.448/h (`stage2b-full/run.json`).
- **Projection:** 20,979 s (5.83 h) against 26,370 s (7.33 h), with nothing dropped.
- **Peak CUDA:** 21,879,599,616 B, or 20.38 GiB, in R3.
- **To the stop at about 06:37Z:** 6.42 h, about USD 2.88. Added to the user-chosen 25.9 h / USD 14.48, that gives 32.3 h / USD 17.4. All of these match the text.

## Corrections

### Blocking (claims discipline; fix before citing; none changes the label)

**C1. "Not a distortion effect" overstates what the design can show.**
- **Location:** Strength curve, the sentence "The F5 loss is therefore not a strength or pixel-distortion effect within the tested grid", and the "May be claimed" bullet headed "Not a distortion effect".
- **Evidence:**
  - T7 says that matching cell medians are insufficient to claim matched distortion, and that matching "does not estimate a causal encoder effect". The pre-specified R0/R1 match has m = 2 for F5 and 0 for v5.
  - Stage-2a review C10 already required the softer wording "not accounted for by larger median pixel distortion".
  - "Not a strength effect" is also wrong as worded: under SD1.5, F5 itself declines with strength (C 60, 57, 39).
- **Fix (Strength curve):** "Within the tested grid, the SDXL loss is not accounted for by strength or by larger attack distortion. For F5's own outputs, R1 .1 is milder than R0 .2 and R0 .4 on PSNR, SSIM and LPIPS in every complete source (58/58), yet it removes F5, while R0 .4 keeps 39/60. Under SD1.5, F5 itself declines with strength (60, 57, 39). This is descriptive and tests no cause."
- **Fix (bullet):** rename it "Not accounted for by larger attack distortion" and keep its last sentence ("…too sparse (m = 2) to test this, so it stays descriptive").

**C2. "Two independently trained regenerator families" drops the qualification on Kandinsky 3.**
- **Location:**
  - R3 section: "F5 is the only arm that fails both independent-family regenerators";
  - "May be claimed", Allowed article frame: "It fails under two independently trained regenerator families".
- **Evidence:**
  - `budget-and-proposals.md` P4 says that the "separate-training evidence is qualified, weaker than SDXL's explicit from-scratch statement". The R3 section itself repeats this.
  - Stage-2a review C5 asked to "qualify 'independently trained' for MoVQ".
  - "Fails" is defined only for F5's primary cell (< 30/60).
- **Fix (R3):** "F5 is the only core arm below 30/60 under both R1 .2 and R3 .2 (v5 12 and 57, WAM 2 and 44, VINE-R 60 and 60)."
- **Fix (frame):** "It fails under SDXL img2img, whose encoder was trained from scratch, at every tested strength. It largely fails (5/60) under full Kandinsky 3 img2img at .2, whose MoVQ training independence from SD1.5 is qualified."

**C3. "SD1.5 holds across the strength curve" and the article frame overreach at strength .4, and generalize beyond F5.**
- **Location:**
  - "May be claimed", SD1.5 holds: "F5's SD1.5 robustness extends across the strength curve";
  - the frame: "Encoder-amplified image-domain marking survives img2img within its encoder family across the tested strengths … VINE-R survives all of them".
- **Evidence:**
  - At R0 .4 F5 C is 39/60 (CP .516–.769), below the 45-source bar the decision rule uses for TRANSFERS. Its read-first states there include 25 content mismatches (N4).
  - VINE-R is 47/60 and 45/60 at .4.
  - Only one encoder-amplified method (F5 r2) was tested, and T7 bounds ROUTE C to the tested configuration.
- **Fix (bullet):** "SD1.5 largely holds. F5 keeps 60/60 and 57/60 at .1 and .2 and 39/60 at .4 (CP .516–.769). It is the most robust tested arm under SD1.5 except VINE-R."
- **Fix (frame):** "Frozen F5 r2, an encoder-amplified image-domain mark, survives SD1.5 img2img at .1 and .2 (60 and 57/60) and keeps 39/60 at .4. It fails … [C2 wording]. A generative-attack-trained baseline (VINE-R) keeps at least 45/60 in every tested cell."

### Minor

**C4. "Posterior-mode substitution alone" is a compound contrast.**
- **Location:** P5 section, "Posterior-mode substitution alone lowers v5 C from 12 to 6, against the sampled posterior."
- **Evidence:**
  - **The R1-mode side:** `posterior_mode` encodes the fp32 input.
  - **The R1 side:** it passes a PIL image to `StableDiffusionXLImg2ImgPipeline`. Its `prepare_latents` (diffusers 0.35.1) first casts the image to the fp16 pipeline dtype, then samples the posterior with the seed's generator, and only then draws the noise. The latent path draws the noise first.
  - **So the noise draws differ:** for the same seed, R1 and R1-mode use different noise tensors.
  - **Seed variability is of the same size:** v5 C per seed is 8/15/15 under R1 and 8/3/13 under R1-mode. Within R1 .2 alone, seed 12 against seed 13 is discordant 2/9.
  - **The smoothing contrast is clean:** R1-smooth and R1-mode share precision and noise, so "It isolates smoothing from posterior-mode substitution" is correct.
- **Fix:** "Against sampled R1, R1-mode lowers v5 C from 12 to 6 (7 sources only under R1, 1 only under R1-mode). This contrast is compound: posterior mode against a sample, fp32 against fp16-rounded input, and a different noise draw for the same seed. Seed-to-seed discordance within R1 .2 alone reaches 2/9."

**C5. The P5 claim lacks its distortion caveat, and "mechanism probe" clashes with "may not claim any mechanism".**
- **Location:** "May be claimed", P5; Status, item 4.
- **Evidence:** smoothing raises attack LPIPS against the control in every arm: C0 .149 against .136, F5 .171 against .155, v5 .165 against .150, WAM .152 against .140, VINE-R .150 against .139.
- **Fix (P5 bullet):** append "The control shares the pipeline and the seed's noise but not the achieved distortion, so the lower counts are not distortion-matched."
- **Fix (Status):** replace "a mechanism probe:" with "an encoder-aware adaptive attack:".

**C6. v5 and WAM do not lose "about as much under SD1.5 as under SDXL".**
- **Location:** Strength curve, the v5 and WAM bullet.
- **Evidence:**
  - At .1, SDXL removes slightly less: v5 50 against 47, WAM 48 against 42.
  - At .2 it removes much more: v5 12 against 27, WAM 2 against 18.
  - At .4 it removes a little more: v5 0 against 3, WAM 0 against 1.
  - And it does so at lower median LPIPS in each cell.
- **Fix:** "They lose more at higher strength under both regenerators. At .1 SDXL removes slightly less than SD1.5 (v5 50 against 47, WAM 48 against 42); at .2 it removes much more (12 against 27, 2 against 18); at .4 both are near zero."

**C7. The D3/R3 contrast is compound.**
- **Location:** R3 section, "So, as with SDXL, the loss comes with the full img2img pipeline, not with the autoencoder round trip."
- **Evidence:**
  - D3 is a deterministic `movq.encode(x).latents` / `decode(force_not_quantize=True)` round trip in fp32 (contract `D3.semantics`).
  - R3 runs the fp16 pipeline, adds noise at timestep 151 and takes 4 stochastic DDPM steps.
  - Stage 2a stated the analogous D1/R1 caveat (stage-2a review C4).
- **Fix:** "So, as with SDXL, the autoencoder round trip alone does not remove F5. The D3/R3 contrast is compound (fp32 deterministic round trip against the fp16 pipeline with noising and denoising), so the loss cannot be attributed to the diffusion step alone."

**C8. "Its semantic tier … is gone at all three" repeats the overstatement corrected in stage 2a (review C3).**
- **Location:** Strength curve, the paragraph on F5's instance tier.
- **Evidence:** at R1 .1 the semantic tier is found in 23/180 calls (S 6/60 sources) and read with a mismatch in 3; median ratio .71, maximum 1.31.
- **Fix:** "Its semantic tier, which C needs, is never read with a content match (C 0/180 calls at each strength). It is found in 23 of 180 calls at .1 and in none at .2 or .4."

**C9. An unsupported causal clause about F5's attack distortion.**
- **Location:** Achieved distortion, "…a little higher than C0's, because the F5 mark changes how the image regenerates."
- **Evidence:** no test addresses the cause. Attack distortion is measured against the marked input, so removal of the embedded residual itself would also raise it.
- **Fix:** "F5's attack LPIPS is consistently a little higher than C0's (for example .152 against .133 at R1 .2). No cause was tested."

**C10. The matched grid fails on SSIM as much as on PSNR.**
- **Location:** Strength curve, "because at equal LPIPS R1 keeps a higher PSNR".
- **Evidence:** over the 827 same-bin R0/R1 candidate pairs of the four arms:
  - the SSIM caliper fails in 746 and the PSNR caliper in 666;
  - PSNR alone fails in 15 and SSIM alone in 14;
  - 6 pairs pass.
- **Fix:** "because at equal LPIPS R1 keeps a higher PSNR and SSIM".

**C11. A misrounded quality median.**
- **Location:** Achieved distortion table, R1-mode row.
- **Evidence:** the F5 attack PSNR median is 24.8946 (Table 4 prints 24.89). The 24.90 in the text is F5's total-distortion median.
- **Fix:** "24.99 / 24.89 / 24.84".

**C12. The wrong-message denominators are not 180 everywhere.**
- **Location:** Negatives, "0/180 for WAM and VINE-R in every new cell".
- **Evidence:** safety blocks leave fewer observed calls: WAM 179 at R0 .1 and 178 at R0 .4; VINE-R 179 at R0 .4. Table 5b prints the planned count (180) as its denominator.
- **Fix (text):** "0 in every new cell (of 180 observed calls; at R0, WAM 179 and 178, VINE-R 179 at .4, because of safety blocks)".
- **Fix (report script):** optionally label the Table 5b denominator "of planned".

**C13. The "conservative total" is a user-chosen basis, not an upper bound.**
- **Location:** Execution table, Cost.
- **Evidence:**
  - The 25.9 h / USD 14.48 was read when the stage-2a run ended (19:19Z on 10-24, at an assumed USD 0.56/h).
  - The stage-2a fetch-and-stop period after that is not in it (the stage-2a image copy was still running at about 19:40Z).
  - It conversely prices the stopped period at GPU rate.
- **Fix:** "On the user-chosen basis (the stage-2a clock at the end of its run, 25.9 h / USD 14.48) plus about 6.4 h / USD 2.9 for stage 2b: about 32.3 h / USD 17.4, within the 35 h / USD 30 ceiling. The vast.ai bills are authoritative."

**C14. The run-folder `run.json` carries a stale budget block.**
- **Location:** MAIN `…/20261025-0128-encoder-transfer-stage2b/run.json`, which `results-2b.md` cites as the run record.
- **Evidence:** its `budget` (4,586.6 s, USD 0.57) is the smoke-timing value at the start of the full run. `stage2b-full/run.json` has 19,064 s and USD 2.37.
- **Fix:** relabel the block "at full-run start (smoke-timing.json)", or replace it with the end-of-run figures plus the estimated instance total (00:11:36Z to about 06:37Z, 6.4 h, about USD 2.9).

**C15. The blob-identity check has no receipt.**
- **Location:** Execution table, run commit: "all 1,001 blobs were checked against the laptop's `ls-tree`".
- **Evidence:** the run folder has only `results/runs/server-git.txt` (two commit lines). Stage 2a kept `server-tree-19b322c.txt`, after stage-2a review C9.
- **Fix:** save the server `git ls-tree -r 61904a1` (or 19ad306) and the comparison output in the run folder. Otherwise, state that the check is not recorded.

**C16. Small report and wording inaccuracies.**
- **"Tables 3–7 cover every cell":** Table 6 covers only the R0/R1 grid, by design. Fix: "Tables 3–5 and 7 cover every cell; Table 6 the R0/R1 strength grid (T7)".
- **The strength note is wrong for two comparisons:**
  - `strength_note()` (Table 6 caption, Figure 4 footnote) says that each side's strengths are .1, .2 and .4.
  - That is false for F5 against TrustMark Q and against Pixel Seal at R1, whose right side has .2 only.
  - Fix: add "(TrustMark Q and Pixel Seal: .2 only)".
- **Table 2 repeats "no majority":** the template text and the contract's `negative_scope` both say it. Fix: drop it from the template.

**C17. "Reproduces the label from the 3,840 inherited rows" is imprecise.**
- **Location:** Status.
- **Evidence:** the F5 count and B come from inherited rows, but the negative gate now spans 540 + 540 calls, including the new R1 .1 and .4 rows.
- **Fix:** "The stage-2b analysis reproduces the label. The F5 count and B come from the inherited rows; the F5 negative gate now also covers the new R1 .1 and .4 calls, all negative."

## Notes (non-blocking, useful for the article)

- **N1. A within-source fact stronger than the medians.** For F5's outputs, in every complete source (58/58), R1 .1 has lower attack LPIPS, higher PSNR and higher SSIM than both R0 .2 and R0 .4. 39 sources succeed at R0 .4 and fail at R1 .1. This is the cleanest descriptive support for C1's wording, and it is still not causal.
- **N2. R3's ".2" is a lighter noising than R0/R1's ".2".**
  - Both start at timestep 151 (leading spacing, 4 of 20 steps).
  - Kandinsky 3's shipped schedule (`squaredcos_cap_v2`) gives ᾱ ≈ .939 there (noise std ≈ .25). The R0/R1 `scaled_linear` schedule gives ᾱ ≈ .826 (std ≈ .42).
  - This agrees with R3's lower attack LPIPS (.116) and v5's 57/60. It makes F5's 5/60 more striking, and it shows again that equal numeric strength is not equal severity (T7).
- **N3. P5 pairing.** R1-smooth and R1-mode use the same latent path, so for a given seed they share the noise draw. Their 0/16, 0/2 and 0/10 discordances are a clean paired comparison. R1 against R1-mode is not (C4).
- **N4. Content mismatches appear at R0 .4.** F5 there has 117 C successes, 25 read content mismatches, 26 found but not read, 10 not found and 2 missing, against 3 mismatches at R0 .2 and 0 at R0 .1. The carrier paragraph's "content mismatches stay rare" holds for the SDXL and R3 cells it lists. The R0 .4 states are worth reporting next to the SD1.5 claim.
- **N5. The VINE-R false detection.** One event, at exactly the threshold. Under the nominal tail (.0000916), 2,094 calls give an expected .19 events (P(≥ 1) ≈ .17 if the calls were independent; they are correlated by source). It is consistent with nominal behaviour, and it supports no calibration claim either way. It does not touch the label: B uses positives only.
- **N6. Undisclosed disk deviation.** The machine had 76 GB of disk against the amendment's "Disk ≥ 120 GB". It caused no problem, but it should be disclosed.
- **N7. The stage-2a "0 matched pairs" no longer holds for the union.** With .1 and .4 the R0/R1 overlap is F5 2, WAM 1, VINE-R 3 and v5 0. Stage-2a `results.md` stays correct for its own grid. The article should cite the union figures.
- **N8. Stage-2a mode of the new script.** It no longer reproduces the 8b3a9b6 `tables.md` byte for byte: the changes are cosmetic labels and a longer "not run" list. That is consistent with "the stage-2a-only report remains at commit 8b3a9b6".
- **N9. Small Table 7 and Table 1 gaps:**
  - Table 7c "Calls" counts rows with a detector timing, not owner calls (pre-existing).
  - Table 7 gives the stage-2b clock at the end of the run (5.3 h), not the instance total (about 6.4 h).
  - Table 1 states neither R1's sampled posterior with fp16 input (against R1-mode's fp32 mode) nor R3's cosine schedule. Both matter for C4 and N2.
- **N10. Rinse against R1 .2.** At similar attack LPIPS (about .14 against .15), the rinse leaves v5 at 4/60 against 12/60 for a single .2 pass. This is a descriptive contrast only; the protocol forbids equating .1 + .1 with .2.
- **N11. The label guard runs after the write.** It checks label and route after `metrics.json` is written. On a mismatch the run would end `interrupted_or_failed`, with the metrics file present. This is harmless here.

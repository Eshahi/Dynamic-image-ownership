# Encoder-transfer study, stage 2b: results

Written by Claude (Opus 5.5) on 2026-10-25 from the completed stage-2b run (amendment 2b). This is a development study on the same 60 development sources as stage 2a, not a confirmation. No held-out or test data were used.

## Status

**The study label is unchanged: FAILS, ROUTE C.** Stage 2a fixed it (`results.md`). Stage 2b is descriptive by design (`amendment-2b.md`): it adds no decision and changes no threshold or rule.

- **Label reproduced:** the stage-2b analysis reproduces the label; the runner refuses to finish otherwise.
  - The F5 count and B come from the 3,840 inherited stage-2a rows. The F5 negative gate now also covers the new R1 .1 and .4 calls, all negative.
  - The stage-2b `metrics.json` is identical to stage 2a's in all 131 stage-2a cells and in the decision block. The same holds for the three Holm-family paired tests and the two descriptive comparisons, and for all 40 quality, 243 negative and 19 external-operating-point blocks. Only the matched-distortion grid differs, by design, because .1 and .4 now enter it.
- **The four gaps it fills, all with every planned cell run and nothing dropped:**
  1. a strength curve: R0 and R1 at .1 and .4;
  2. the SDXL rinse (.1 then .1);
  3. a second regenerator family: full Kandinsky 3 img2img (P4);
  4. an encoder-aware adaptive attack: P5 smoothing with its matched posterior-mode control.

## Execution

| Item | Value |
|---|---|
| Contract | `stage2b-config.json`, status `user-amended-pre-outcome`, sha 6217e495…; asset plan a21a53af…; laptop commit 66d6944. Previous amendment: stage 2a (87e4142f…) |
| Budget basis | The user could not find the billed stage-2a figures and chose the conservative stage-2a clock, 25.9 h / USD 14.48, with the declared drop order. That left 9.1 h / USD 15.52 for stage 2b |
| Run commit | server 61904a1. The server repository is the byte-identical `git archive` of 0a1dc27: all 1,001 blobs were checked against the laptop's `ls-tree`, with 0 mismatches and no untracked extras. The receipt is `server-tree-check-61904a1.txt` in the run folder, holding the check's output and the laptop tree it was compared with. On top of it are the two contract files, built on the server and hash-identical to laptop 66d6944 |
| Hardware | vast.ai container 57583551: RTX 4090 24 GB, Ryzen 9 5950X, 64 GB RAM, 76 GB disk, USD 0.448/h. The disk was below the amendment's planned 120 GB. Peak use was about 58 GB, and results were fetched in byte ranges without staging copies. Python 3.11.17, torch 2.7.1+cu128, the stage-2a pins, plus sentencepiece 0.2.2 and protobuf 7.36.2 for the Kandinsky 3 tokenizer |
| Full run | 2026-10-25 01:28:05Z to 05:29:21Z, 4.02 h. Peak CUDA allocation 20.4 GiB, in the R3 phase: the 21.7 GB text encoder on the GPU for the one empty-prompt encode |
| Reductions | none. The smoke projection was 5.83 h with 7.33 h available |
| Units | 11,040 planned (3,840 inherited, 7,200 new) and 11,040 terminal: 11,017 ok, 23 safety-blocked (13 of them new, all R0), 0 errors, 0 missing |
| Cost | The budget clock read 5.3 h / USD 2.37 at the end of the run. The instance stopped about 06:37Z, after the results were home, so about 6.4 instance-hours and USD 2.9. Total for both stages on the user-chosen basis: 32.3 h / USD 17.4, within the 35 h / USD 30 ceiling. That basis is the stage-2a clock at the end of its run, 25.9 h / USD 14.48. It is not an upper bound: it leaves out stage 2a's fetch-and-stop period and prices its stopped period at the GPU rate. The vast.ai bills are authoritative |
| Run folder | MAIN `.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/` |

### Operations

**No implementation fix was needed.** The run commit is the prepared 0a1dc27 plus the contract, and there is no `BUGFIX_NOTE`. The adapter check and the smoke were the first GPU runs of the new code, and both passed on their first attempt:
- Kandinsky 3 output PSNR 28.8 dB against its input;
- R1-smooth 28.9 dB;
- R1-mode 29.0 dB.

Three operational events, none affecting any setting:
1. **Prefetch.** The stage-2a assets were prefetched while Kandinsky 3 downloaded. They were fetched with the frozen hash-checked fetcher. `ready.json` was then removed, so the stage-2b prepare re-verified every file.
2. **Network hold.** The stage-2b prepare held after three failed attempts: TLS handshake timeouts to Hugging Face, and a GitHub reset on the VideoSeal clone. After connectivity returned the hold was removed, and the next attempt passed. No code changed.
3. **One retried download.** One SDXL UNet download ended early during the prefetch and was caught by the size and hash check, then fetched again.

**Inputs and outputs:**
- **Stage-2a inputs:** the stage-2a journal (`rows.jsonl`, SHA-256 26b69451…) and the 300 clean inputs were uploaded and hash-checked. The seeder verified each clean input against the hash its stage-2a row records.
- **Smoke:** it used only the two reserved smoke sources, and no setting was chosen from it.
- **Results:** they came home in hash-checked byte ranges; results.tar d423a1d8…, images.tar 08f7d0d9…. All 7,187 new images match their journal SHA-256.

## Strength curve

Source-majority counts out of 60 (at least 2 of seeds 12, 13 and 14), with median attack LPIPS (output against its input, over complete sources):

| Cell | Executed steps | F5 C | v5 C | WAM presence | VINE-R presence | LPIPS F5 / C0 |
|---|---|---|---|---|---|---|
| R0 SD1.5 .1 | 2 | **60** | 47 | 42 | 60 | .128 / .105 |
| R0 SD1.5 .2 (stage 2a) | 4 | **57** | 27 | 18 | 60 | .183 / .151 |
| R0 SD1.5 .4 | 8 | **39** | 3 | 1 | 47 | .294 / .254 |
| R1 SDXL .1 | 2 | **0** | 50 | 48 | 60 | .097 / .089 |
| R1 SDXL .2 (stage 2a, primary) | 4 | **0** | 12 | 2 | 60 | .152 / .133 |
| R1 SDXL .4 | 8 | **0** | 0 | 0 | 45 | .236 / .217 |

**95% Clopper-Pearson intervals for F5 C:**
- R0 .1: [.940, 1];
- R0 .4: [.516, .769];
- R1 .1 and R1 .4: [0, .060] each.

The intervals are model-based and exploratory (independent exchangeable sources in a development convenience cohort). Safety-blocked R0 positives count as failures: F5 R0 .1 is missing 1 call and R0 .4 2.

**What the curve shows:**
- **F5 under SDXL:** it gives 0/60 at every tested strength, including .1, which runs two denoising steps and has a median LPIPS of .097. At .1 under SDXL, v5 keeps 50/60 and WAM 48/60.
- **F5 under SD1.5:** it holds at .1 (60/60) and .2 (57/60), and keeps 39/60 at .4, where the median LPIPS is .294. That is three times the LPIPS of the R1 .1 cell that removes it.
- **v5 and WAM:** they lose more at higher strength under both regenerators.
  - At .1, SDXL removes slightly less than SD1.5: v5 50 against 47, WAM 48 against 42.
  - At .2 it removes much more: 12 against 27, and 2 against 18.
  - At .4 both are near zero.
- **VINE-R:** it keeps 60/60 at .1 and .2 under both regenerators, and 47 and 45 at .4.

**Within the tested grid, the SDXL loss is not accounted for by strength or by larger attack distortion.**
- **The within-source comparison:** in every complete source (58/58), F5's R1 .1 output is milder than its R0 .2 and R0 .4 outputs on PSNR, SSIM and LPIPS. Yet R1 .1 removes F5, while R0 .4 keeps 39/60, and 39 sources succeed at R0 .4 but fail at R1 .1.
- **Under SD1.5,** F5 itself declines with strength (60, 57, 39).

This is descriptive, like everything in stage 2b, and it tests no cause. R0 and R1 also differ in resolution, model family and pipeline, not only in the encoder (`results.md`, diagnostics).

**F5's any-tier endpoint A ("either tier found") under SDXL** falls with strength: 52/60 at .1, 30/60 at .2, 5/60 at .4. A is the conservative negative-gate endpoint, not an ownership claim.

**Its semantic tier, which C needs,** is never read with a content match: C is 0/180 calls at each strength.
- **At .1:** it is found in 26 of 180 calls. 23 of those have a content match but are not read (the S endpoint), and 3 are read with a content mismatch.
- **At .2 and .4:** it is found in none.

**The pre-specified matched-distortion grid (T7) is almost empty for R0 against R1** (Table 6 of the report). Within source, the calipers (|ΔLPIPS| ≤ .02, |ΔPSNR| ≤ 1 dB, |ΔSSIM| ≤ .02) rarely hold across the two regenerators, because at equal LPIPS R1 keeps a higher PSNR and SSIM. In the reviewer's count, of 827 same-bin candidate pairs over the four arms, the SSIM caliper fails in 746 and the PSNR caliper in 666. The union replaces stage 2a's "0 matched pairs":
- **F5:** 2/60 sources in the [.1, .2) bin; F5 succeeds on R0 in 2 of 2 and on R1 in 0 of 2.
- **v5:** no overlap in any bin.
- **WAM:** 1 source.
- **VINE-R:** 3 sources.

So the matched analysis cannot carry the R0/R1 contrast; the unmatched curve above does, and descriptively only. Within each regenerator, the F5-against-baseline matched comparisons have usable overlap (for example 38/60 in the [.1, .2) bin for F5 against v5 under R0). These are in the report.

## Rinse (R1 .1, then a second .1 pass; seeds 12+112, 13+113, 14+114)

| Arm | R1 .1 (first pass) | Rinse | Lost / gained sources | Rinse LPIPS against the original mark / second pass against first |
|---|---|---|---|---|
| F5 C | 0 | 0 | — | .146 / .069 |
| F5 A | 52 | 34 | 18 / 0 | |
| v5 C | 50 | **4** | 46 / 0 | .142 / .069 |
| WAM presence | 48 | 21 | | .137 / .070 |
| VINE-R presence | 60 | 59 | | .133 / .067 |

A second light SDXL pass removes most of what survives the first:
- v5 falls from 50/60 to 4/60;
- WAM falls from 48/60 to 21/60.

Its achieved distortion (LPIPS about .14 against the original mark) is close to a single .2 pass (about .15). Per the protocol, the rinse is not an independent replicate, and .1+.1 is not assumed to equal .2. Two comparisons for v5 C, both descriptive contrasts only:
- rinse 4/60 against R1 .2 12/60;
- rinse 4/60 against R0 .2 27/60.

VINE-R loses one source.

## Full Kandinsky 3 img2img (R3, P4)

R3 is the full Kandinsky 3 pipeline at revision bf79e6c: native DDPM scheduler, 20 scheduled steps at strength .2 (4 executed), empty prompt without guidance, fp16 variant, 1024 internal.

| Arm | Endpoint | R3 .2 | CP95 | R1 SDXL .2 for reference |
|---|---|---|---|---|
| F5 r2 | C | **5/60** | [.028, .184] | 0/60 |
| v5 r3 | C | 57/60 | [.861, .990] | 12/60 |
| WAM | presence | 44/60 | [.603, .839] | 2/60 |
| VINE-R | presence | 60/60 | [.940, 1] | 60/60 |

**F5's other endpoints at R3:**
- S: 21/60;
- A: 29/60;
- calls: 16/180 C successes, 46 found but not read, 6 content mismatches, 112 not found.

Median attack LPIPS is .116 for F5 and .108 for C0, milder than R1 .2.

**R3's ".2" noises less than R0/R1's ".2".**
- **Same starting point:** both start at timestep 151 (leading spacing, 4 of 20 steps).
- **Different noise there:** Kandinsky 3's shipped cosine schedule gives ᾱ ≈ .94 (noise std ≈ .24); the R0/R1 scaled-linear schedule gives ᾱ ≈ .83 (std ≈ .42).

Equal numeric strength is not equal severity (T7). This makes F5's 5/60 more notable, not less.

**Kandinsky 3 is a second regenerator family under which F5 falls far below its SD1.5 level (5/60 against 57/60).** This happens while v5 and WAM survive the same channel much better than under SDXL. F5 is the only core arm below 30/60 under both R1 .2 and R3 .2:

| Arm | R1 .2 | R3 .2 |
|---|---|---|
| v5 | 12 | 57 |
| WAM | 2 | 44 |
| VINE-R | 60 | 60 |

Two qualifications:
- **MoVQ independence:** MoVQ's training independence from SD1.5 is itself qualified (`budget-and-proposals.md`, P4). It is weaker evidence than SDXL's explicit from-scratch training.
- **Autoencoder round trip:** the MoVQ round trip alone (D3) keeps F5 at 55/60. So, as with SDXL, the autoencoder round trip alone does not remove F5.
  - The D3/R3 contrast is compound: an fp32 deterministic round trip against the fp16 pipeline with noising and denoising.
  - So the loss cannot be attributed to the diffusion step alone.

## P5: encoder-aware smoothing and its matched control

- **R1-smooth:** the mean SDXL posterior mode over 4 antithetic Gaussian pairs (σ = 2/255, public arrays fixed by the contract), then R1's .2 path from that latent.
- **R1-mode:** the same path from the posterior mode of the unperturbed input. It isolates smoothing from posterior-mode substitution.

| Arm | Endpoint | R1 .2 (sampled posterior) | R1-mode .2 | R1-smooth .2 | Smooth-only / mode-only sources |
|---|---|---|---|---|---|
| F5 r2 | C | 0 | 0 | 0 | — |
| F5 r2 | A | 30 | 32 | **16** | 0 / 16 |
| v5 r3 | C | 12 | 6 | 4 | 0 / 2 |
| v5 r3 | A | 52 | 52 | 42 | 0 / 10 |
| WAM | presence | 2 | 2 | 0 | |
| VINE-R | presence | 60 | 60 | 60 | |

- **F5 C:** it is at the floor under plain R1 .2, so P5 cannot show any additional removal on the primary endpoint.
- **Effect against the matched control:** smoothing removes part of what remains.
  - F5's any-tier A (either tier found) falls from 32 to 16 sources.
  - v5's A falls from 52 to 42.
  - No source succeeds under smoothing that fails under the control.
- **R1-mode against sampled R1:** R1-mode lowers v5 C from 12 to 6. Seven sources succeed only under R1, and one only under R1-mode.
  - This contrast is compound: the posterior mode against a sample, fp32 against fp16-rounded input, and a different noise draw for the same seed.
  - Seed-to-seed discordance within R1 .2 alone reaches 2/9.
  - The smoothing contrast, by contrast, is clean: R1-smooth and R1-mode share the latent path, the precision and the noise draw.
- **VINE-R:** unaffected.
- **Distortion:** smoothing raises attack LPIPS against the control in every arm. The control shares the pipeline and the seed's noise, but not the achieved distortion, so the lower counts are not distortion-matched.

| | C0 | F5 | v5 | WAM | VINE-R |
|---|---|---|---|---|---|
| R1-smooth | .149 | .171 | .165 | .152 | .150 |
| R1-mode | .136 | .155 | .150 | .140 | .139 |

These are descriptive counts on one fixed smoothing setting; no smoothing certificate or tuned attack is implied.

## Carrier states and margins (descriptive)

**F5 read-first states (180 calls per cell):**
- R1 .1: 154 not found, 23 found but not read, 3 content mismatches, 0 C successes.
- R1 .4, rinse, R1-smooth and R1-mode: all 180 not found.
- R3: 112 not found, 46 found but not read, 6 mismatches, 16 C successes.

In these SDXL and R3 cells, as at R1 .2 in stage 2a, the carrier is not mis-bound: content mismatches stay rare.

**Under SD1.5, mismatches appear only at .4.** F5 at R0 .4 has 117 C successes, 26 found but not read, 25 read with a content mismatch, 10 not found and 2 missing calls. That is against 3 mismatches at R0 .2 and 0 at R0 .1.

**Median F5 semantic score/threshold ratio** (owner alpha, own marked outputs; 1 = threshold):

| Cell | Ratio |
|---|---|
| clean | 1.85 |
| R0 .1 / .2 / .4 | 1.76 / 1.62 / 1.29 |
| R1 .1 / .2 / .4 | .71 / .33 / .14 |
| rinse | .23 |
| R1-smooth / R1-mode | .26 / .35 |
| R3 | .81 |

C0 stays near 0 in every cell: median between −.09 and −.03, maximum at most .63.

**F5's instance tier** keeps the stage-2a pattern: near null under SD1.5 (.12, .06 and .02) but near threshold under SDXL at .1 and .2 (1.19 and 1.00). **v5's semantic margin** at R3 (1.50) is higher than at R0 .2 (1.16).

All of this is post-hoc and descriptive (Figure A1 of the report), and none of it may be used to tune any method on these outputs.

## Negatives

Every new negative call is observed, except calls lost to R0 safety blocks, which are unresolved:
- **F5 primary negative gate, now the full R1 grid (.1, .2 and .4):** C0 0/540 and wrong owner 0/540, both on endpoint A, none unresolved. The same holds for v5.
- **R0 .1 and .4:** for F5 and v5 every C0 and wrong-owner endpoint is 0. R0 .1 has 2 unresolved C0 calls for each, and F5 also 1 unresolved wrong-owner call. At R0 .4 every C0 and wrong-owner endpoint has 2 unresolved calls, for both arms.
- **External C0:**
  - WAM: 0 in every new cell. R0 .1 and .4 each have 2 unresolved calls (safety blocks), as for VINE-R.
  - VINE-R: one false detection, unit `R1:1295:unmarked:0.1:14`, at exactly 69/100 matches (the threshold). That is 1 of 2,094 observed VINE-R C0 calls across every cell of both stages; stage 2a had none.
  - Under the nominal random-message tail (.0000916 per call), 2,094 calls give an expected .19 events. If the calls were independent, P(at least 1) would be about .17; they are not, because calls share sources. It is consistent with nominal behaviour, and it supports no calibration claim either way. It does not touch the label, because B uses positives only.
- **Wrong-message presence** (independent message or complement): 0 for WAM and VINE-R in every new cell. The denominator is 180 observed calls, except at R0, where safety blocks leave WAM 179 (.1) and 178 (.4) and VINE-R 179 (.4). Table 5b prints the planned count.
- **Rinse, P5 and R3 negatives:** 0, none unresolved.

The F5 count stays at zero false detections on every endpoint in every cell.

## Achieved distortion (attack: output against its own input; complete-source medians)

| Cell | PSNR dB (C0 / F5 / VINE-R) | LPIPS (C0 / F5 / VINE-R) |
|---|---|---|
| R0 .1 | 24.12 / 24.09 / 24.04 | .105 / .128 / .105 |
| R0 .4 | 20.12 / 19.98 / 19.97 | .254 / .294 / .261 |
| R1 .1 | 27.56 / 27.43 / 27.47 | .089 / .097 / .089 |
| R1 .4 | 22.38 / 22.36 / 22.13 | .217 / .236 / .222 |
| rinse (against the mark) | 26.06 / 25.93 / 25.89 | .134 / .146 / .133 |
| R1-smooth | 24.93 / 24.87 / 24.78 | .149 / .171 / .150 |
| R1-mode | 24.99 / 24.89 / 24.84 | .136 / .155 / .139 |
| R3 | 25.98 / 25.90 / 25.84 | .108 / .116 / .111 |

**Every new cell has 60/60 complete sources,** except R0. R0 .1 has 59 for C0 and F5 and 60 for VINE-R. R0 .4 has 58 for C0 and F5 and 59 for VINE-R.

**F5's attack LPIPS is consistently a little higher than C0's,** for example .152 against .133 at R1 .2. No cause was tested; attack distortion is measured against the marked input, so removal of the embedded residual would also raise it. Total distortion and the other arms are in Table 4 of the report.

## What may and may not be claimed

**May be claimed** (development evidence, 60 sources, the tested settings):
- **Strength curve.** Frozen F5 r2 gives 0/60 under SDXL img2img at strengths .1, .2 and .4, with no false detections (0/540 C0, 0/540 wrong owner). The SDXL failure is not confined to strength .2.
- **SD1.5 largely holds.** F5 keeps 60/60 and 57/60 at .1 and .2, and 39/60 at .4 (CP .516–.769). It is the most robust tested arm under SD1.5 except VINE-R.
- **Not accounted for by larger attack distortion.** Within the tested grid, the SDXL loss does not follow achieved distortion. In every complete source, F5's R1 .1 output is milder than its R0 .2 and R0 .4 outputs on all three metrics. Yet R1 .1 removes F5, while R0 .4 keeps 39/60. The pre-specified within-source matched comparison is too sparse (m = 2) to test this, so it stays descriptive.
- **Second family.** F5 also largely fails full Kandinsky 3 img2img at .2 (5/60), where v5 (57/60) and WAM (44/60) survive. MoVQ's training independence is qualified, and R3's .2 noises less than SDXL's .2. The Kandinsky 3 MoVQ round trip alone does not remove F5 (55/60).
- **Rinse.** A two-pass light SDXL rinse removes most v5 (4/60) and much WAM (21/60) signal that survives a single .1 pass. VINE-R keeps 59/60.
- **P5.** Encoder-aware posterior smoothing lowers the residual F5 any-tier A and v5 signals against a matched posterior-mode control.
  - The control shares the pipeline and the seed's noise but not the achieved distortion, so the lower counts are not distortion-matched.
  - It cannot be assessed on F5's primary endpoint, which is already at zero.
- **Allowed article frame (ROUTE C).** Bounded to the tested configuration:
  - Frozen F5 r2, an encoder-amplified image-domain mark, survives SD1.5 img2img at .1 and .2 (60 and 57/60) and keeps 39/60 at .4.
  - It fails under SDXL img2img, whose encoder was trained from scratch, at every tested strength.
  - It largely fails (5/60) under full Kandinsky 3 img2img at .2, whose MoVQ training independence from SD1.5 is qualified.
  - A generative-attack-trained baseline (VINE-R) keeps at least 45/60 in every tested cell.
  - Only one encoder-amplified method was tested.

**May not be claimed:**
- that encoder-amplified marking in general fails: only F5 r2 was tested;
- that F5 fails under all independent encoders, or all diffusion regenerators: two families, one Kandinsky setting and three SDXL strengths were tested;
- that SD1.5 robustness holds at every strength: at .4 F5 is 39/60, below the 45-source TRANSFERS bar, with 25 content mismatches;
- any mechanism: R0, R1 and R3 differ in model family, resolution, scheduler and pipeline, not only in the encoder. The D1/D3 round trips and P5 narrow the attribution but test no cause;
- that the strength-curve contrast is a matched-distortion result (the matched overlap is 2/60);
- that the rinse equals a .2 pass, or that its second pass is an independent replicate;
- that P5 is an optimal or certified smoothing attack;
- that VINE-R dominates F5 at matched quality. Clean quality is unmatched, VINE-R passes the strict clean gate on 31/60, and it showed one false detection at its threshold;
- that the any-tier A signal gives ownership evidence;
- any population-level, held-out or calibrated false-positive result;
- anything about FLUX (gated) or the declined proposals.

## T7 tables and figures (union)

`report/tables.md` and `report/figures/` now render the union of stages 2a and 2b. `scripts/encoder_transfer_report.py` was extended for this and reads only the saved outputs:
- **Figure 1:** shows R0 and R1 at .1, .2 and .4, with segments joining measured settings, and a fourth panel for the rinse, P5 and R3 cells.
- **Figure 2:** connects the strengths.
- **Figure 6:** adds the rinse against its R1 .1 parent.
- **Figure 7:** adds the prescribed rinse pair: R1 .1 seed 12 and the rinse with seeds 12 and 112.
- **Figure A1:** covers every cell.
- **Tables 3–5 and 7:** cover every cell. Table 6 covers the R0/R1 strength grid (T7).
- **Table 8:** adds Kandinsky 3 at .2.
- **Not changed:** the R0 .2 empirical ROC stays not estimable (2 unresolved C0 negatives). Figure 5 stays at R0/R1 .2, with every other cell's ROC summary in Table 5c.

The stage-2a-only report remains at commit 8b3a9b6. The full-resolution Figure 7 panels are in the stage-2b run folder (`report-full/figures/`).

## Review

One independent review is in `review-2b.md`. It was written by a fresh Claude (Opus 5.5) agent; BRIEF section 6 names a `gpt-6-astra` reviewer, but the user had no Codex access.
- **Verdict:** ACCEPT WITH CORRECTIONS. Its recomputation from `rows.jsonl` reproduces FAILS, ROUTE C and every count, and matches `metrics.json` on every call.
- **Corrections:** C1–C17 are applied in this version:
  - C1–C3, C17: claims and status wording;
  - C4–C10: caveats and wording;
  - C11–C12: one median and the wrong-message denominators;
  - C13: the cost basis;
  - C14: the run-folder budget block;
  - C15: a blob-check receipt;
  - C16: report labels.
- **Notes:** N1, N2, N4–N7 and N10 are reflected above.
- **One deviation:** C8's evidence counts the SDXL .1 semantic tier as found in 23 calls. A recount gives 26: 23 with a content match, plus the 3 read with a mismatch. This version uses 26.

## Files

- `metrics.json`, `rows.jsonl`, `run.json`, `effective-config.json`, `memory-phases.json` and `seeded-from.json`: MAIN `.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/`. The smoke is in `results/stage2b-smoke/`, the logs, setup scripts and package freeze in `results/`.
- `stage2b-results.tar`: SHA-256 d423a1d8…; `stage2b-extras.tar`: 97599e99…; both verified after the copy.
- `stage2b-images.tar`: SHA-256 08f7d0d9…, 3.05 GB, copied in 46 hash-checked byte ranges. It was verified whole, extracted, and checked image by image against the journal (7,187 of 7,187), then removed.
- Run record: `run.json` in the run folder.

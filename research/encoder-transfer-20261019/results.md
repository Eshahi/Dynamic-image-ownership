# Encoder-transfer study, stage 2a: results

Written by Claude (Opus 5.5) on 2026-10-24 from the completed stage-2a run. This is a development study on 60 development sources, not a confirmation. No held-out or test data were used.

**Update, 2026-10-25:** stage 2b has since run (`results-2b.md`, reviewed in `review-2b.md`). It reproduces this label. Its cells (.1/.4, rinse, full Kandinsky 3, P5) supersede the "not run by design" statements below. With .1 and .4 in the grid, the R0/R1 matched-distortion overlap is no longer zero (F5 m = 2). The T7 report now renders the union.

## Decision

**Label: FAILS. Route: ROUTE C**, the bounded empirical article (BRIEF section 3).

The primary cell is F5 r2 at R1 (SDXL img2img, strength .2), counting source-majority C.
- **F5:** 0/60 sources (CP95 0 to .060), below the fail threshold of 30.
- **Negative gate:** zero false detections, 0/180 C0 calls and 0/180 wrong-owner calls, none unresolved. The label rests on the positives alone.
- **B = max(WAM, VINE-R) = 60** (VINE-R 60/60). It gives route context only, because FAILS sends the study to ROUTE C whatever B is.
- **Stage 2b (strengths .1 and .4, rinse, full P4 and P5):** not run by design (stage-2a result), per BRIEF section 1d. Those cells are not failures.

## Execution

| Item | Value |
|---|---|
| Contract | `stage2a-config.json`, status `user-amended-pre-outcome`, sha 87e4142f… (laptop commit cb634d5); base freeze e318757 |
| Run commit | server 19b322c (tree 83b2dc3d). The server repository is a 969-file subset that travels from the laptop as a git archive, because the GitHub repository is private. Every one of its 969 blobs equals laptop b4b2810 on `claude/encoder-transfer-stage2`, and its working tree is clean (`server-tree-19b322c.txt` in the run folder) |
| Hardware | vast.ai container 57402655, RTX 4090 24 GB, Python 3.11.17, torch 2.7.1+cu128 |
| Full run | 2026-10-24 14:31:22Z to 19:19:26Z, 4.80 h of compute; peak CUDA memory 11.9 GB in the smoke |
| Units | 3,840 planned, 3,840 terminal: 3,830 ok, 10 safety-blocked (R0 only), 0 errors, 0 missing |
| Reductions | none. The smoke projection was 6.52 h with 13.4 h available, so nothing was dropped |
| Run folder | MAIN `.thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/` |

### Implementation-only fixes before any outcome

The stage-2a driver started on 2026-10-23 at 18:18Z. Its first adapter check failed at 18:29Z, so it held without generating any study image. The laptop could not reach the server until 2026-10-24, because the Hotspot Shield VPN answered every TCP connection locally. These fixes followed. Each is recorded in the driver log. cb634d5 is the base commit of the smoke record (server 384d975) and is documented in `amendment-1d.md`. 90f9888 and b4b2810 are recorded through the runner's `--bugfix-note` (smoke `run.json`, `bug_fixes`: server 1f4b388 and 19b322c). The full run started fresh at 19b322c, after all four fixes.
1. **PyAV pin.** The pinned VideoSeal import chain imports `av`, which was missing. av 18.1.0 was installed, and the contract was rebuilt with it in `packages`; nothing else in the contract changed (amendment-1d.md, cb634d5).
2. **Python 3.11 link check.** `Path.is_junction` exists only from Python 3.12, and the protocol's server runs 3.11. On 3.11 the check now falls back to False; junctions exist only on Windows (90f9888).
3. **CLIP package.** The pinned openai/CLIP source package was missing from the server environment. It was installed at commit d05afc436d78f1c48dc0dbf8e5980a9d471f35f6, the laptop's version, with `--no-deps`. `a6_clip_visual`'s own hash checks of `clip.py`, `model.py` and the ViT-B/32 checkpoint pass. No repository change.
4. **Smoke projection.** R0's frozen SD1.5 safety checker blocked 9 of smoke source 1790's 15 R0 outputs, including all three C0 seeds. The projection had refused these blocks as implementation failures. They are now skipped for timing, and the cell is timed from the other smoke source (b4b2810, two tests). In five R0 cells, therefore, the projection uses only source 1822, not the slower of two sources. At 6.52 h against 13.4 h available this changed nothing.

`clip` is not in `requirements-stage2.txt` or the contract's `packages`, so the runtime pin check does not cover it; `a6_clip_visual`'s byte and SHA checks do. The smoke `run.json` still holds a stale `error` traceback from an earlier attempt next to `outcome: smoke_completed`.

No scientific setting, threshold or decision rule changed. The smoke reads only the two reserved smoke sources, and no setting was chosen from them.

## Primary and anchor endpoints (source majority, at least 2 of seeds 12, 13 and 14)

| Arm | Endpoint | R1 SDXL .2 | R0 SD1.5 .2 (anchor) |
|---|---|---|---|
| F5 r2 | C | **0/60** [0, .060] | 57/60 [.861, .990]; 3 calls blocked, optimistic 58 |
| v5 r3 | C | 12/60 [.108, .323] | 27/60 [.321, .584]; 1 call blocked, optimistic 28 |
| WAM | common presence | 2/60 [.004, .115] | 18/60 [.188, .432]; 2 calls blocked, optimistic 19 |
| VINE-R | common presence | **60/60** [.940, 1] | 60/60 [.940, 1]; 2 calls blocked, optimistic 60 |
| TrustMark Q (descriptive) | native BCH and binomial | 0/60 [0, .060] | not in scope |
| Pixel Seal (descriptive) | binomial on 256 bits | 0/60 [0, .060] | not in scope |

Intervals are two-sided 95% Clopper-Pearson intervals. They are model-based and exploratory, assuming independent exchangeable sources in a development convenience cohort. Safety-blocked positives count as failures; R1 has no safety checker.

**Paired exact sign tests on the primary cell (one Holm family of three; exploratory, no override of the rule):**
- **F5 vs v5:** 0 wins and 12 losses; Holm p = .00098.
- **F5 vs WAM:** 0 wins and 2 losses; Holm p = .5.
- **F5 vs VINE-R:** 0 wins and 60 losses; Holm p = 5.2e-18.

TrustMark and Pixel Seal tie F5 at 0/60. They are descriptive only and sit outside both the family and the route rule.

## Diagnostics: where the F5 carrier is lost

F5 source-majority counts, all of them descriptive:

| Channel | What it does | S | C | Q | A |
|---|---|---|---|---|---|
| clean | none | 60 | 60 | 52 | 60 |
| X1 / X2 | resize-only controls | 60 / 60 | 60 / 60 | 46 / 41 | 60 / 60 |
| D1 | SDXL VAE round trip, no diffusion | 60 | 55 | 31 | 60 |
| D3 | Kandinsky 3 MoVQ round trip, no diffusion | 60 | 55 | 35 | 60 |
| R0 .2 | SD1.5 img2img | 58 | 57 | 38 | 59 |
| R1 .2 | SDXL img2img | **0** | **0** | 0 | 30 |

Predicates follow `m1b_e3_s1_analysis.predicates`:
- **S:** semantic found and content match;
- **C:** semantic read and content match;
- **Q:** read q exactly equals the target;
- **A:** either tier found.

**Read-first carrier states:**
- **F5 at R1 .2:** all 180 calls are `not_found`, with no content mismatch. The semantic score is below its threshold in every call; the carrier is not mis-bound.
  - A sub-threshold shift remains, descriptively. The F5 semantic score/threshold ratio has median .33 (IQR .17 to .48, maximum .97), against C0 at R1 with median −.04 and maximum .52.
  - 171 of the 180 F5 calls exceed the C0 median, and 39 exceed the C0 maximum.
- **v5 at R1 .2:** 64 `not_found`, 74 `found_not_read`, 4 `read_content_mismatch` and 38 `C_success`.

What this shows:
- **Autoencoder round trips alone do not remove F5.** Both D1, the SDXL autoencoder, and D3, the Kandinsky 3 MoVQ autoencoder, keep C at 55/60. MoVQ's training independence from SD1.5 is itself qualified (`budget-and-proposals.md`, P4).
- **The full SDXL img2img pipeline at .2 does.** C falls to 0/60.
  - The contrast with D1 is compound (protocol). D1 uses the posterior mode with direct fp32 input, while R1 samples the posterior after fp16 input rounding and then noises and denoises.
  - The loss therefore cannot be attributed to the denoising step alone.
- **The same strength through SD1.5 keeps F5.** C is 57/60, the encoder family F5 writes through.

This localizes the loss to SDXL img2img as a whole, not to SDXL's autoencoder round trip. It is a descriptive observation, not a tested mechanism.

**F5's A predicate at R1 .2:** 30/60 sources. A is the conservative negative-gate endpoint (either tier found), and it has 0/180 C0 and 0/180 wrong-owner false calls.
- **Per source:** 24 sources fire on 3 of 3 seeds, 6 on 2, 8 on 1 and 22 on none.
- **Instance content:** of the 92 instance-found calls, 47 match, 17 mismatch and 28 are uncertain.
- **Opposite of R0:** the instance tier sits near its threshold at R1 (median ratio 1.00) but near null at R0 (.06). The semantic tier does the reverse.

Some instance-tier signal therefore survives in about half of the sources, but without the semantic tier the method cannot claim ownership. These counts come from the independent review (`review.md`, N4). It is post-hoc and descriptive, and no claim may rest on it.

**External arms on the diagnostic channels (common presence, source majority):**
- **WAM:** D1, D3, X1 and X2 all 60/60; R0 18/60, R1 2/60.
- **VINE-R:** 60/60 on every channel.
- **TrustMark Q:** D1 58/60, R1 0/60.
- **Pixel Seal:** R1 0/60, and its median bit agreement at R1 is .52, near chance.
- **Median bit accuracy at R1 .2:**
  - VINE-R: .90 over 180 calls.
  - WAM: .625 over only 44 calls; 136 of 180 had an empty mask and abstained. At R0 the WAM median is .8125 over 120 calls, with 58 abstentions.
  - TrustMark: decodes no BCH codeword at R1.

## Signal margins by channel (post-hoc, descriptive)

The table gives the median detector score/threshold ratio over each arm's own marked outputs, read with owner alpha; 1 is the detection threshold. Added on 2026-10-24 after the label was fixed. No setting is chosen from it, and it must not be used to tune any method on SDXL outputs.

| Channel | F5 semantic | F5 instance | v5 semantic | C0 (F5 semantic) |
|---|---|---|---|---|
| clean | 1.85 | 2.13 | 2.01 | — |
| X1 / X2 | 1.76 / 1.69 | — | 2.01 / 2.01 | −.09 / −.09 |
| D1 (SDXL VAE) | 1.57 | 1.63 | 2.00 | −.09 |
| D3 (MoVQ) | 1.64 | 1.70 | 1.97 | −.08 |
| R0 SD1.5 .2 | 1.62 | .06 | 1.16 | −.08 |
| R1 SDXL .2 | **.33** | 1.00 | 1.05 | −.04 |

- **F5's semantic tier:** it loses about 12% of its clean margin under SD1.5 img2img and about 82% under SDXL img2img. The two autoencoder round trips cost 11–15%.
- **F5's two tiers move in opposite directions:** the instance tier collapses under SD1.5 (.06) but sits at its threshold under SDXL (1.00). That is why A is 30/60 at R1 while C is 0/60.
- **v5:** its margin falls by a similar amount under both regenerators (1.16 and 1.05), without the SD1.5 advantage.
- **Same-channel C0:** it stays near 0 everywhere.

These are descriptive regularities in one cohort and one setting; they are not tested mechanisms.

## Negatives

Every negative call is observed except the R0 calls lost to safety blocks, which are unresolved:
- **F5 and v5, R1 .2:** C0 0/180 and wrong-owner 0/180 on every predicate, A included.
- **F5 and v5, R0 .2:** C0 0/180 (2 unresolved) and wrong-owner 0/180 (3 unresolved for F5, 1 for v5).
- **External C0 at R1 .2:** WAM, VINE-R, TrustMark Q and Pixel Seal are each 0/180, none unresolved.
- **External C0 at R0 .2:** WAM and VINE-R are each 0/180, with 2 unresolved (safety blocks).
- **Clean, D1, D3, X1 and X2:** every negative is 0/60.

The presence rules for TrustMark and Pixel Seal are binomial rules that were never calibrated; their negatives are observed counts only.

## Clean quality and cost

Medians over complete sources, marked image against source:

| Arm | PSNR dB | SSIM | LPIPS | Strict gate |
|---|---|---|---|---|
| F5 r2 | 44.96 | .983 | .020 | 60/60 |
| v5 r3 | 36.85 | .978 | .019 | 60/60 |
| WAM | 38.44 | .985 | .034 | 58/60 |
| VINE-R | 35.14 | .996 | .006 | 31/60 |
| TrustMark Q | 41.76 | .994 | .002 | 60/60 |
| Pixel Seal | 46.24 | .996 | .002 | 60/60 |

The strict clean-quality gate is PSNR > 35 dB, SSIM > .9 and LPIPS < .1; human ratings are missing. Clean quality is unmatched across methods, because each arm runs at its frozen or native setting.

**Embedding cost:** F5 takes about 118 s per image on the RTX 4090 (60 images, about 2 h). Every other arm takes a few seconds.

**Cost:**
- **Wall-clock budget clock:** it counts from the first instance creation (2026-10-23 17:28Z) and includes the stopped period. At the end of the run it read 25.9 h, USD 14.5 at the assumed USD 0.56/h.
- **Billed GPU time:** lower, because a stopped instance bills storage only. The exact amount is on the vast.ai bill.
- **Against the ceiling:** both figures are within the 35 h / USD 30 ceiling.

## Achieved distortion of the channels

Medians over complete sources, output against its own input:

| Channel | PSNR dB (C0 / F5 / VINE-R) | LPIPS (C0 / F5 / VINE-R) |
|---|---|---|
| R0 .2 | 22.46 / 22.35 / 22.26 | .151 / .183 / .153 |
| R1 .2 | 24.99 / 24.90 / 24.83 | .133 / .152 / .135 |
| D1 | 32.69 / 32.43 / 32.64 | .029 / .033 / .029 |
| D3 | 33.13 / 32.83 / 33.06 | .022 / .025 / .022 |
| X1 | 44.45 / 44.33 / 44.42 | .004 / .005 / .004 |
| X2 | 40.37 / 40.26 / 40.35 | .012 / .013 / .012 |

In median pixel terms R1 .2 is milder than R0 .2 (higher PSNR, lower LPIPS), yet it removes F5 while R0 does not. The loss is not accounted for by larger median pixel distortion. The pre-specified within-arm R0-against-R1 matched comparison found 0 pairs for every arm, so it is not estimable. Full per-arm tables are in `metrics.json` (`reporting.quality`, `reporting.matched_distortion`).

## Comparison with step 1: SD1.5 vs SD2.1 vs SDXL at strength .2

F5 r2, source-majority C:

| Regenerator | Encoder family | Cohort | F5 C | v5 C |
|---|---|---|---|---|
| SD1.5 img2img (step 1) | SD1.x | 24 development sources | 22/24 | 5/24 |
| SD2.1-base img2img (step 1) | SD1.x (same encoder) | 24 development sources | 24/24 | 5/24 |
| SD1.5 img2img, R0 (this study) | SD1.x | 60 sources: step 1's 24 + 36 new | 57/60 (24: 22/24; 36: 35/36) | 27/60 (24: 5/24; 36: 22/36) |
| SDXL img2img, R1 (this study) | independent SDXL encoder | 60 sources: step 1's 24 + 36 new | **0/60** (24: 0/24) | 12/60 (24: 3/24) |

The 60 sources include all 24 step-1 sources. On those 24, R0 reproduces step 1 exactly (F5 22/24, v5 5/24).

Step 1's "unseen regenerator" result (`research/journal-upgrade-20261009/unseen-regenerator-results.md`) kept F5 at 24/24 on SD2.1. That model reuses the SD1.x encoder. With SDXL img2img at .2, F5 gives 0/24 on the same 24 sources and 0/60 overall.

## What may and may not be claimed

**May be claimed** (development evidence, 60 sources, one SDXL setting):
- **No transfer to SDXL.** Frozen F5 r2 does not transfer to SDXL img2img at strength .2: 0/60 by source-majority C, with no false detections.
- **The SD1.5 path holds.** F5's robustness to SD1.5 img2img .2 holds on the 60-source cohort (57/60). The cohort includes the 24 step-1 sources, where it reproduces 22/24, and adds 36 new sources at 35/36.
- **Autoencoder round trips alone do not remove F5.** It survives round trips through the SDXL VAE and the Kandinsky 3 MoVQ autoencoder (55/60 each); MoVQ's independence from SD1.5 is qualified.
- **VINE-R does survive SDXL.** On the same R1 channel (each arm regenerates its own marked image) it keeps 60/60. Clean quality differs on both sides:
  - VINE-R has the better LPIPS (.006 against F5's .020);
  - but the lower PSNR (35.14 against 44.96);
  - and it passes the strict clean gate on 31/60, against F5's 60/60.
  - WAM, TrustMark Q and Pixel Seal do not survive SDXL.
- **Allowed article frame:** a bounded empirical study (ROUTE C), limited to the tested SDXL configuration.
  - Encoder-amplified image-domain marking survives img2img within its encoder family (SD1.5; SD2.1 in step 1).
  - It fails under SDXL img2img at .2 in this cohort.
  - A generative-attack-trained baseline (VINE-R) survives both.

**May not be claimed:**
- that F5 is robust to "regeneration" or to "diffusion models" in general;
- that F5 fails "across encoder families" in general: only one SDXL img2img setting was tested;
- that VINE-R dominates F5 at matched quality: clean quality is unmatched, and VINE-R passes the strict clean gate on 31/60;
- any result for strengths .1 or .4, the rinse, FLUX, full Kandinsky regeneration or encoder-aware smoothing (not run);
- that the instance-tier A signal (30/60) gives ownership evidence;
- a mechanism: the D1/R1 contrast localizes the loss but tests no cause;
- any population-level or held-out performance;
- calibrated false-positive rates for TrustMark or Pixel Seal;
- that the image-domain F5 is the proposal's latent method (RQ-02/HYP-02 stay open).

## T7 tables and figures

The protocol makes T7's eight-table, seven-figure reporting plan binding. All of it is rendered in `report/tables.md` and `report/figures/` by `scripts/encoder_transfer_report.py`, which reads only the saved outputs. Two items deviate by design:
- the rinse panels are marked "not run by design";
- the R0 empirical ROC is marked not estimable, because of 2 unresolved C0 negatives (safety blocks).

It adds Figure A1, the post-hoc margins. The Figure 7 previews use 144-pixel tiles; full-resolution panels are in the run folder (`report-full/figures/`). A skeleton of the ROUTE C article is in `article/route-c-skeleton.md`.

## Review

One independent review is in `review.md`. It was written by a fresh Claude (Opus 5.5) agent; BRIEF section 6 names a `gpt-6-astra` reviewer, but the user had no Codex access for stage 2.
- **Verdict:** ACCEPT WITH CORRECTIONS. Its recomputation from `rows.jsonl` confirms FAILS, ROUTE C, with no blocking finding.
- **Corrections:** all twelve are applied in this version.
- **Notes:** N1 to N6 are reflected above.

## Files

- `metrics.json`, `rows.jsonl`, `run.json`, `effective-config.json` and `memory-phases.json`: MAIN `.thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/results/stage2a-full/`, with the smoke run in `results/stage2a-smoke/`.
- `stage2a-results.tar`: SHA-256 d5669bee…, verified after the copy.
- `stage2a-images.tar`: SHA-256 f02701c5…, 1.67 GB, copied in 16 hash-checked parts, then reassembled and verified.
- Driver, phase and adapter-check logs, BUGFIX_NOTE and package freezes: `results/` and `results/extras/`.

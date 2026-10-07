# M2: confirmatory results, F5 r2 vs v5 r3 on narrow COCO512

Status 2026-10-07. Inventory, analysis and the original claims audit were prepared by Claude Code (Opus 5.5). Codex applied the five corrections from the [independent M2 review](m2-independent-review.md), verdict **ACCEPT WITH CORRECTIONS**, after the user's instruction to continue. All measured counts remain unchanged. The original report is retained at commit `2a31ed1`; the independent review is retained at `e01d63c`. This corrected report supports draft writing and does not record human M2 acceptance or a lifecycle transition.

## 1. Run and provenance

- **Approval.** The user approved the single confirmatory run in chat on 2026-10-06 at about 22:15 UTC and asked Claude Code to write the approval: `C:/Users/Soroush/thesis-approvals/m1b-coco512-approval.json`, actor Soroush, sha256 d0d1f12c….
  - The user waived the final independent pre-run review.
  - The approval passed the official `approval_check`.
- **Manifest.** Execution manifest 95ac3183… at commit 711d2f3; scientific core be2aa571… (24 code files); plan `research/m1b-coco512-test.m1b-plan.json`.
- **Parent run `coco512-confirm-1`.**
  - Laptop RTX 5070 Ti Laptop GPU (Windows), dispatcher started 22:17 UTC.
  - The approval reference and continuation label attribute the interruption at about 22:27 UTC to the user's request to move to a rented GPU. The parent has no finalized `outputs/run.json`; its dispatcher record remains `running`. These records are consistent with a manual stop but cannot independently establish that no crash occurred.
  - Journal: 155 rows (14 sources fully embedded and tested, plus the fifteenth canonicalized), sha256 54f6c41a….
- **Continuation `coco512-confirm-rerun-1`** (infrastructure-only rerun, depth 1):
  - Plan `research/m1b-coco512-test-continuation-1.m1b-plan.json` at e26bd4b, sha256 3ecfbc30…; manifest d8e98e51…; same scientific core be2aa571….
  - Hardware: vast.ai instance 54613667 (RTX 5070 Ti 16 GB, AMD Ryzen 9 9950X, Linux). Windows absolute paths were mirrored inside the checkout, so the code was byte-identical.
  - The held-out photos were downloaded on the server from images.cocodataset.org; all 300 photos and the annotation file matched the plan's hashes before the run.
  - `rerun-check` reports passing automatic checks for the same core, unchanged core files, preserved incomplete approved parent, matching resume plan, dispatcher budget, unexpired approval and depth at most 2. Independent inspection confirms numerical lineage integrity, rather than unconditional compliance with every standing-policy clause.
  - This was a scientifically unchanged continuation under the recorded direct user exception, with retrospective independent review. Parent approval expires `2026-10-13T22:17:11Z`; continuation approval expires `2026-10-14T09:21:20Z` and names `Soroush` rather than a delegated actor. The run ended before the original expiry. Original chat, stop-command and paid-resource decisions were not independently authenticated beyond the transcribed references.
  - `execution_target=local` and `max_usd=0` in the dispatcher records describe its route and budget check; they do not establish that the rented server incurred no cost. The specific continuation authorization allows journal reuse, which must not be presented as literal compliance with conflicting older blanket wording.
  - The journal's first 155 lines are byte-identical to the parent journal (sha256 of that prefix 54f6c41a…).
- **Run record.**
  - Status `finished` and dispatcher status `completed`; no infrastructure error and 0 torn journal lines.
  - Wall time 9,625 s (2 h 40 min) for the continuation; started 09:21:21 and ended 12:01:47 UTC on 2026-10-07.
  - Output 1.04 GB.
- **Inventory:** 7,741 planned rows, 7,741 completed, no extra rows, complete.
- **Re-analysis.** `scripts/m1b_coco512_analysis.py` was run on the retained journal on Windows; `plan_path` points to the server checkout, so the plan file was taken from e26bd4b after checking its sha256 against `run.json`.
  - All event counts are identical to the in-run endpoints.
  - 192 bound values differ in the last bit (at most 2.2e-16, Linux vs Windows floating point).
- **Retained files** under MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-rerun-1/` (sha256):

  | File | sha256 |
  |---|---|
  | `outputs/journal.jsonl` | 4254d503795f669867d26862d893054a29b94766d5cf0eff1a39e836ab545b04 |
  | `outputs/run.json` | 5defb0230712d7ac5782fb689ecfdebc531b65436a7c2a9f42220cdba7d304af |
  | `metrics/endpoints.json` | 59d90d0f7d11aff86f11674a3c0c31061663d9212dbcfd9d739a7b724d6d36bd |
  | `metrics/endpoints-reanalysis.json` | 75950d0f020a1697cb93faff09c3e78d4e44beaa80bf6ca4e6c6a2d98c9c0a66 |

  Server logs, manifests and the `rerun-check` output are in `.thesis-build/m1b-confirm/remote-54613667/`.

## 2. Results

All rates are conservative (missing rows count adversely; none were missing). Bounds are one-sided 95% Clopper-Pearson, per cell, without simultaneous coverage.

### 2.1 Clean, 300 independent sources (primary)

| Cell | F5 r2 | v5 r3 | Target | F5 r2 meets |
|---|---|---|---|---|
| C1 correct owner, `both_match` (TPR) | 299/300 (LB .984) | 300/300 (LB .990) | LB ≥ .80 | yes |
| C0 correct owner, `any_found` | 0/300 (UB .010) | 0/300 | UB ≤ .01 | yes |
| C0 wrong owner, `any_found` | 0/300 | 0/300 | UB ≤ .01 | yes |
| C1 wrong owner, `any_found` | 0/300 | 0/300 | UB ≤ .01 | yes |
| Same three negatives, `both_match` (secondary) | 0/300 each | 0/300 each | UB ≤ .01 | yes |

**Quality of the marked images, against the proposal's targets:**

| Quality measure | F5 r2 | v5 r3 |
|---|---|---|
| PSNR > 35 dB | 300/300 (mean 44.5, min 41.6) | 300/300 (mean 37.5, min 35.2) |
| SSIM > .9 | 300/300 (mean .983, min .959) | 300/300 (mean .979, min .963) |
| LPIPS < .1 | 298/300 (mean .022, max .104) | 300/300 (mean .021, max .082) |
| All three together | 298/300 | 300/300 |
| Embed time | mean 22.4 s | mean 2.3 s |
| Self-verification `both_match` | 300/300 | 300/300 |

These are quality counts under the approved confirmatory protocol, rather than an all-sample quality acceptance gate. F5 did **not** achieve LPIPS < .1 on every held-out image: IDs `553094` and `134886` have LPIPS .10222657 and .10419527. Its mean LPIPS is .02175893, so the development freeze limits (mean <= .0173, max <= .050) also did not carry over. The primary detection endpoints below must not be read as a universal quality pass. Self-verification uses source semantic features; the primary clean queries recompute features from the marked image and give the actual 299/300 result. The clean miss, ID `399205`, is `content_uncertain` with semantic distance 6.04136 against radius 6.

### 2.2 T3 regeneration (30 sources, descriptive)

The regenerator is SD1.5, as a VAE cycle and as DDIM20 img2img at strengths .05/.1/.2/.4 with seeds 0/1/2. A source succeeds at a strength when at least 2 of its 3 seeds do.

The semantic success counts split into two parts:
- **checked:** the semantic code was decoded and compared;
- **assumed:** owner found by the recomputed pattern only.

| Strength | F5 r2 rows: semantic (checked + assumed) | v5 r3 rows | F5 r2 sources | v5 r3 sources | F5 checked sources | v5 checked sources |
|---|---|---|---|---|---|---|
| VAE cycle | 30/30 (30 + 0) | 30/30 (30 + 0) | 30/30 | 30/30 | 30/30 | 30/30 |
| .05 | 90/90 (90 + 0) | 90/90 (90 + 0) | 30/30 | 30/30 | 30/30 | 30/30 |
| .1 | 90/90 (90 + 0) | 87/90 (71 + 16) | 30/30 | 29/30 | 30/30 | 24/30 |
| .2 | 87/90 (79 + 8) | 62/90 (30 + 32) | 30/30 | 22/30 (LB .570) | 27/30 (LB .761) | 10/30 |
| .4 | 60/90 (51 + 9) | 14/90 (7 + 7) | 21/30 (LB .535) | 5/30 | 17/30 | 3/30 |

**Paired sources, F5 r2 vs v5 r3** (exact two-sided sign test on discordant sources):

| Rule | Strength | F5 only | v5 only | Both | Neither | p |
|---|---|---|---|---|---|---|
| Semantic | .05 | 0 | 0 | 30 | 0 | n/a |
| Semantic | .1 | 1 | 0 | 29 | 0 | 1.0 |
| Semantic | .2 | 8 | 0 | 22 | 0 | .0078 |
| Semantic | .4 | 16 | 0 | 5 | 9 | 3.1e-5 |
| Semantic, checked only | .1 | 6 | 0 | 24 | 0 | .031 |
| Semantic, checked only | .2 | 17 | 0 | 10 | 3 | 1.5e-5 |
| Semantic, checked only | .4 | 14 | 0 | 3 | 13 | 1.2e-4 |

- v5 r3 never succeeded on a source where F5 r2 failed.
- **Negatives after regeneration**, both methods at every strength:
  - wrong-owner `any_found`: 0 rows and 0 sources;
  - C0 `any_found`: 0 rows and 0 sources (per-source UB .095).
- `both_match` after regeneration is 0/90 for both methods at every strength. The fragile instance tier is designed to break when the content is regenerated, so a regenerated image carries the semantic tier only.

### 2.3 T4 copy-paste (30 donor/recipient pairs, descriptive)

| Cell | F5 r2 | v5 r3 |
|---|---|---|
| False donor full attribution, per pair (both patch sizes) | 0/29 (UB .098) | 0/29 |
| Same, per row | 0/58 | 0/58 |
| Recipient claim `any_found` | 0/58 | 0/58 |
| Sham (C0 donor) `any_found` | 0/120 | 0/120 |
| Donor semantic consistency (error rows) | 3/58 | 5/58 |
| Donor delivery witness (pairs) | 4/30 | 8/30 |

- **Final states of the marked donor claim** (60 rows):
  - F5 r2: neither_match 56, semantic_only 3, content_uncertain 1;
  - v5 r3: neither_match 52, semantic_only 6, content_mismatch 1, content_uncertain 1.
- **Pair 5** shares a public owner and is reported separately, as declared before the run (F5 neither_match on all four claims).

### 2.4 T5 semantic collision (30 selected pairs, descriptive)

- 30 eligible pairs were selected by `m1-coco512-t5-v1`. Pairs 9, 20 and 29 share a public owner and are excluded from the false-match rate, as declared; this leaves 27 different-owner pairs.
- For both methods:
  - false full match: C0 0/27, C1 0/27;
  - `any_found`: C0 0/27, C1 0/27;
  - per-pair UB .105.
- The collision descriptors (pHash distance, CLIP cosines, semantic-code distance) are in `endpoints.json`.

## 3. What the numbers support

1. **Primary clean detection endpoints:** F5 r2 meets all of them: TPR lower bound .984 against the .80 target, and zero detections in **900 distinct clean negative queries**, comprising three cells of 300 (UB ≤ .010 per cell). v5 r3 also has zero in its 900 calls. The secondary `both_match` rule reuses these calls; 1,800 is the count across both methods.
2. **Regeneration (RQ-02/HYP-02):** on 30 held-out sources, the complete frozen F5 r2 system kept semantic-tier owner detection through SD1.5 img2img more often than the complete v5 r3 comparator at strengths .2 and .4.
   - Semantic sources: 30 vs 22 at .2 and 21 vs 5 at .4.
   - Checked-only sources: 27 vs 10 at .2 and 17 vs 3 at .4.
   - The paired sign tests run 8-0 at .2 and 16-0 at .4.
   - No false attributions appeared after regeneration.
   - This is descriptive evidence with 30 units and per-cell bounds, not a powered test. No multiplicity correction is part of the frozen protocol.
   - The experiment does not isolate carrier location: F5 also changes CLIP pooling (seven views rather than one), semantic matching, embedding machinery and perturbation strength. Both methods modify pixels; F5 optimizes and reads the VAE encoder latent. The original causal latent-versus-pixel hypothesis is therefore partially supported by this whole-system comparison.
3. **Copy-paste and semantic collision:** zero false full attributions for both methods.
   - With 29 and 27 units the upper bounds are .098 and .105, so these show no observed failure, not a demonstrated rate below 1%.
   - On the copy-paste delivery witness F5 r2 is weaker than v5 r3 (4/30 vs 8/30): it less often reveals that a patch came from the donor.
   - F5 has zero `content_mismatch` states in the 60 marked donor claims. Most rejection coincides with an absent/undelivered mark, so the run does not isolate rejection caused by content binding. T5's cross-owner negatives also do not isolate semantic/perceptual binding from public owner conditioning or establish improvement over semantic-only signatures.
4. **Quality:** F5 r2 meets PSNR and SSIM targets on all 300 photos and LPIPS on 298 (max .104). Its embedding costs about 10 times v5's time.

## 4. Claims audit (against `research/claims.csv`, read only)

| Claim | Status after this run |
|---|---|
| PROB-02, OBJ-02, RQ-02, HYP-02, METRIC-05 (survival under regeneration; latent vs pixel) | Partially supported: descriptive whole-system F5-versus-v5 evidence for one regenerator (SD1.5 VAE cycle and DDIM img2img up to .4), on 30 sources. Carrier location is not isolated from pooling, matching and embedding changes. F5 is a pixel-domain change optimized through the SD1.5 VAE encoder so that the encoder latent carries the pattern; it is not an initial-noise or generation-time latent method (METHOD-06 deviation). |
| PROB-01, OBJ-04, RQ-04, HYP-04 (copy-paste rejection) | Partially supported by thresholded rejection: no false donor full attribution (0/29 pairs), but donor delivery is only 4/30 and no F5 splice reports content_mismatch. Comparative binding efficacy is not established. The proposal's ACC/AUC (METRIC-06) is not computed; only fixed-threshold rates exist. |
| PROB-03 (semantic collisions) | No false match in 27 different-owner pairs (UB .105), for both methods. This is not an isolated test of the benefit of content binding or of a combined versus semantic-only signature. |
| METHOD-09 (three-outcome detector) | Decision table implemented and exercised, not validated as a classifier of attack cause. F5 clean marked images give both_match on 299/300 primary queries. T3 gives semantic_only in 357 of 390 correct-owner rows (v5: 283), otherwise content_uncertain 21, neither_match 11, content_mismatch 1 (v5: 13, 91, 3). Splices mostly give neither_match. Output labels alone do not identify regeneration or forgery. |
| METRIC-01..03 (PSNR > 35, SSIM > .9, LPIPS < .1) | F5 r2: 300/300, 300/300 and 298/300 (joint 298/300). |
| DATA-01 (1,000-image COCO subset) | Deviation: 300 COCO val2017 test representatives (narrow COCO512 cohort, user decision 2026-10-06). |
| DATA-02 (DIV2K), DATA-03 (DiffusionDB), SCOPE-02 (generated images) | Not evaluated. |
| METRIC-04 (benign attacks) | Out of scope by the user's three-threat decision (2026-10-05). |
| OBJ-03, RQ-03, HYP-03, METRIC-07, CLAIM-01 (DCT vs neural decoders; latency vs SEAL) | Not tested. Detection time is logged per row, but there is no comparison with a neural decoder or an inversion method. F5 detection also runs the VAE encoder, so "without inversion" holds but "lightweight DCT only" does not. |
| HYP-01, OBJ-01, RQ-01 (combined vs semantic-only signature) | Not tested as a separate ablation in this run. |
| SCOPE-03 (ownership transfer) | Not addressed. |
| NOVELTY-01 (semantic binding plus DCT extraction without inverse diffusion) | The binding computation is implemented and extraction uses no diffusion inversion; comparative binding efficacy and novelty are not established. DCT is applied to the VAE latent, not the 8x8 image-domain DCT of METHOD-08. |

## 5. Deviations and limitations

- **Mixed hardware.** 14 sources were embedded on the laptop GPU (Windows) and 286 on the rented RTX 5070 Ti (Linux). GPU embedding is not bit-reproducible (package §4.7), so this is one realization across two machines. The move was infrastructure-only, labelled in e26bd4b before any outcome was seen.
- **Data location.** Held-out data was processed on a rented server at the user's decision.
- **Review timing.** The final independent pre-run review was waived by the user.
- **Continuation provenance.** The independent review is retrospective. Parent termination cause is not independently provable from the missing finalized stop record. Changed expiry/actor and rented-server accounting remain explicit; no retained evidence was rewritten to make it match older policy clauses.
- **Quality and causality.** Universal LPIPS attainment and the development LPIPS limits did not carry over. The whole-system comparison does not isolate the latent carrier or demonstrate comparative binding efficacy.
- **Statistics.** T3/T4/T5 rest on 30, 29 and 27 units: zero errors give upper bounds near 10%. Per-cell bounds have no simultaneous coverage.
- **Threat coverage.**
  - Only the pinned SD1.5 regenerator was tested; other regenerators, prompts and pixel pre-filters were not.
  - Keys are public-derived: no cryptographic unforgeability.
- **Unsettled questions.**
  - COCO test-image rights are pending (local research use only).
  - Human visual and semantic verdicts are missing.

## 6. Review completion and remaining decisions

1. **Independent M2 review completed:** [review](m2-independent-review.md), Codex fresh reviewer, verdict ACCEPT WITH CORRECTIONS at `e01d63c`. C1-C5 are applied in this revision. It confirms scientific continuation integrity and supplies item 5 retrospectively; item 4 remains bounded by the missing finalized parent stop record. No scientific rerun is required. No additional independent per-step review was created.
2. **The user's decisions:**
   - accept the results;
   - whether to add labelled secondary analyses (bootstrap, Holm), which are not in the frozen protocol (issues #31-#33);
   - final chapter and institutional acceptance. The user authorized continuation after the review; corrected reporting and local draft writing are proceeding without recording a formal acceptance verdict.

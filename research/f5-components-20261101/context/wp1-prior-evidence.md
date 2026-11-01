# WP1 prior experiment evidence: K1–K12 crosswalk

[SOURCE] This is a report-only inventory for WP1, prepared on 2026-11-01. The permitted boundary is development evidence plus committed, frozen reports of held-out studies; Phase B per-source journals, held-out images/journals and Stage C/reserve identifiers are excluded (`research/f5-components-20261101/BRIEF.md:22-26`). No experiment was run for this inventory. Any evaluative conclusion below is **PROPOSED**, not a judge ruling.

[SOURCE] Locator convention: ordinary paths are relative to the current checkout. `R3:` means the blob on branch `claude/f5-r3-256`, `IDEAS:` means `claude/f5-ideas`, and `M2:` means `claude/m2-coco512-results`; these blobs were read with `git show`, without checking out or changing branches. `RL:` is relative to `C:/Users/Soroush/.codex/worktrees/codex-rl/`. `J09/` abbreviates `research/journal-upgrade-20261009/`; `ET/` abbreviates `research/encoder-transfer-20261019/`; `PA` and `PB` abbreviate `ET/final-study-20261025/phase-a/PHASE-A-REPORT.md` and `ET/final-study-20261025/phase-b/PHASE-B-REPORT.md`. Bare `BRIEF.md` and `JUDGE-FINDINGS.md` mean `research/f5-components-20261101/BRIEF.md` and its `judge/JUDGE-FINDINGS.md`. Every number below is copied from an inspected report, not independently rescored.

## 1. Crosswalk for component documents

[SOURCE] K1–K12 follow the judge's starting map (`research/f5-components-20261101/BRIEF.md:54-67`). The references in this table point to the detailed evidence entries below; component attribution is a proposed interpretation, not an isolated causal result.

| Component | Prior evidence to carry into section B | What the evidence actually constrains |
|---|---|---|
| K1 semantic descriptor | [SOURCE] E02 r1→r2 pooling; E06 noiseless binding ceiling; E10 E3 and unseen transfer; E11 descriptor round; E12 registry. | [JUDGMENT, PROPOSED] Pooling already recovered real T3 errors. Better transport alone cannot repair unstable instance features. Representation, dimension and tolerance are confounded in the descriptor replacements. |
| K2 content code | [SOURCE] E02 soft ML; E05 H4; E06 true-feature/random-sketch diagnostics; E07 r3-256; E10 E3 BCH; E11 FG128. | [JUDGMENT, PROPOSED] A 32-bit fixed sketch can lose separability; replacing it with 256 weak antipodal chips failed the actual carrier. Neither observation proves all longer codes fail. |
| K3 payload/channel code | [SOURCE] E01 v5 32×10 construction; E07 r3-256; E10 E3 BCH(59,32); E13 recomputed-only versus read losses; E11 unbuilt conditional BCH carrier. | [JUDGMENT, PROPOSED] Read failures are consequential, but payload expansion must pay for physical transport and multiple-testing cost. A planned carrier is not a measured capacity result. |
| K4 carrier space | [SOURCE] E01 low-frequency image carrier; E02 natural versus encoder-amplified latent; E03 H1 band; E08 F4 chroma; E13 foreign-family losses; E14 stagewise transfer; E17 coarse lattice. | [JUDGMENT, PROPOSED] The tested 8–28 band failed to improve 4–32; this is not an exhaustive frequency/geometry rejection. Foreign losses occur after substantial codec survival. |
| K5 encoder/surrogate | [SOURCE] E02 equal-PSNR amplification; E10 E3 multi-branch writer; E13 codec-only versus full regeneration; E14 transfer/noise diagnostics; E16 F6 design. | [JUDGMENT, PROPOSED] Encoder gain transfers to SDXL/K3, but survival does not. Codec exposure is insufficient evidence of protection against independently trained full regeneration. |
| K6 optimizer | [SOURCE] E01 historical refinement; E02 PGD versus natural rendering; E07 changed r3 margin; E10 E3 minimax and eligibility selection; E11 reissue accumulation; E16 F6/RL designs. | [JUDGMENT, PROPOSED] Writer/objective choices change outcomes, but there is no isolated convergence/step-count experiment establishing that current 150-step F5 optimization is optimal or limiting. |
| K7 quality budget/allocation | [SOURCE] E02 50→52 dB choice and quality; E04 H3 full mask/budget sweep; E08 F4 distortion tradeoff; E10 E3 quality cost; E11 reissue drift; E13 unmatched method quality; E15 frozen quality tails; E17 visual defects. | [JUDGMENT, PROPOSED] Budget and masking do not map monotonically to T3 or perceptual quality. Nominal component budgets are not measured additive distortion shares. |
| K8 fragile tier/write order | [SOURCE] E01 two-tier decision; E02 shared fragile/refinement; E08 T4 delivery versus attribution; E09 frozen F5 full-match collapse; E10 E3 H/F and exact-H sensitivity; E11 old-h oracle; E13 any-tier foreign detections. | [JUDGMENT, PROPOSED] Fragile transmission, recomputed instance consistency, clean exact-h eligibility and full attribution are different endpoints. Removing the tier changes T4/T5 and clean-instance semantics even if it helps T3 budget. |
| K9 statistic/threshold | [SOURCE] E01 analytic-null qualifications and recomputed-only weakness; E05 H4 radius specificity; E07 recomputed-only dependence; E13 weak residual signal; E14 failed pooled linear law; E15 unresolved empirical negatives. | [JUDGMENT, PROPOSED] Threshold failure is not proof of zero signal. A less expensive search may recover some calls, but changed tests require new T4/T5 specificity evidence and cannot be relabelled frozen C. |
| K10 binding decision | [SOURCE] E02 binding-dominant r1 and successful r2 repair; E05 H4; E06 fixed-feature ceilings; E09 legacy semantic/checked/full endpoints; E10 C/J/H/F distinctions; E11 descriptor conjunctions; E12 registry two-factor gate. | [JUDGMENT, PROPOSED] Current-r2 carrier-conditional binding ceilings are useful local accounting, not intrinsic limits on binding research or future stronger carriers. |
| K11 keys/side information | [SOURCE] E01 public-key null caveat; E02 public VAE/CLIP reader; E10 public projection and alpha-only E3; E12 trusted registry; E16 VINE-Bq design; E17 secret-key lattice difference. | [JUDGMENT, PROPOSED] Public-profile detection, known-message presence, payload reading, trusted-record matching and cryptographic ownership are distinct tasks. |
| K12 protocol | [SOURCE] All entries, especially E03/E04 safety-blocked denominators, E07 early kill, E09/E15 frozen held-out reports, E10 target/gate asymmetry, E12 near-duplicate challenges, E13/K3 unequal noise, E14 attack eligibility and calibration failure. | [JUDGMENT, PROPOSED] Keep source-majority and per-seed counts separate, preserve failed/unevaluable cells, and do not transfer a development ceiling or an endpoint name into a different study. |

## 2. Development and historical evidence entries

### E01. v5 established lower-frequency survival, threshold assumptions and the two-tier tradeoff

[SOURCE] Relevant components: K3/K4/K6/K7/K8/K9/K10/K11. The v5 amendment reports that the preceding v4 r2 kept no key on 121 regeneration cases from 12 development photographs. Its subsequent carrier probes and v5 variant counts were predominantly synthetic/generator studies, not the later real-photo F5 cohort (`research/method-amendment-v5.md:9-31,55`).

[SOURCE] On those early probes, full-resolution DCT signal response through a VAE was .02–.21 with noise 12–16 and host 16–49; 4×4 averaging gave .41–.87 with noise about 4, and 8×8 averaging .66–.95 with noise 2–3. At SD1.5 strength .2 the 4×4 gain was .16–.24. On 16 development synthetic images, successive baseline/allocation/whitening/cap changes moved VAE/.1/.2 successes from 9/16,5/16,2/16 to 12/16,6/16,4/16, then 14/16,9/16,6/16, then 16/16,14/16,9/16. Later r3 constant-chromaticity work reached all-seed .1=14/16 and .2=10/16 with SSIM at least .975 and LPIPS at most .023 (`research/method-amendment-v5.md:13-21,61-65,99-106`).

[SOURCE] v5 changed robust frequency allocation, whitening, block caps and the tail bound; it kept a separate fragile tier and used 32 semantic segments with 10 chips each. `semantic_only` was interpreted as regenerated, `both_match` as intact, and `instance_only` as abstention. The report explicitly says the same semantic-only state can follow ordinary low-pass processing, so it is not a unique causal diagnosis of regeneration (`research/method-amendment-v5.md:35-47,190-197`).

[SOURCE] The analytic bound assumes a fixed image with independent fair random patterns; decoded search incurs a union over 2^32 candidate codes, while a recomputed-code test searches one. Public adaptive construction is outside that null. The report also documents that recomputed-only success effectively assigns the suspect's code, can allow a transferred code at distance 7–9, and can pass on approximately half-aligned segments when a clean mark is strong. It therefore retained the decoded code for an actual content decision (`research/method-amendment-v5.md:203-212`).

[SOURCE] Historical optional VAE/one-step writer refinement improved one synthetic .2 count from 6/48 to 10/48, while .4 stayed zero. A stronger robust pattern could also move perceptual hashes toward one another: in one copied same-composition case the h distance decreased from 11 to 9, and r3 residual-copy outcomes changed from 2 mismatch/9 uncertain/5 both to 3/7/6 (`research/method-amendment-v5.md:117,223,351-365`).

[JUDGMENT, PROPOSED] This history rejects the particular earlier high-frequency carrier on its tested channels, not all high-frequency or chroma designs. It also warns against treating K3, K7, K9 and K10 as independent knobs: amplitude, payload decoding and recomputed binding interact. None of these synthetic counts supplies an independent-encoder F5 performance bound (E01 sources above).

### E02. F5 r1→r2: binding was a major real bottleneck and was successfully improved

[SOURCE] Relevant components: K1/K2/K4/K5/K6/K7/K8/K9/K10/K11. The natural-rendering versus encoder-amplified probe used the same nominal PSNR and 11 completed cases per strength, with one safety-blocked source. At 52 dB, natural rendering gave median/max LPIPS .0003/.0005, clean latent signal .6 and strength-.4 informed/blind scores .5/.2; encoder optimization gave .0054/.015, latent signal 15.9 and scores 18.8/10.3. At 46 dB the latent signals were 1.3 versus 26.5 and informed .4 scores .9 versus 37.4. This was matched SD1.5 evidence; it did not establish independent-encoder survival (`research/f5-encoder-amplified-latent.md:13-22`).

[SOURCE] F5 changed v5's robust tier while retaining q, h, the fragile tier and key test. Its deployed sequence used 150 PGD steps in SD1.5 posterior-latent DCT space, rounding, fragile insertion, refinement and final fragile insertion. The reader required public OwnerID/profile, CLIP and the SD1.5 VAE. The 52 dB choice followed a two-source 50 dB smoke result whose mean LPIPS .021 exceeded the then .0176 comparator target (`research/f5-encoder-amplified-latent.md:26-28`).

[SOURCE] On the original 12 development sources, r1 clean quality was mean/min PSNR 44.7/43.3, minimum SSIM .975 and mean/max LPIPS .0172/.051; clean both-match was 12/12. Paired SD1.5 successes were .1=29/29 versus v5 27/29, .2=25/28 versus 18/28 and .4=21/28 versus 2/28. All 159 unmarked calls in each of four reported configurations and wrong-owner calls were zero. The paired denominators excluded safety-blocked identities (`research/f5-encoder-amplified-latent.md:34-45`).

[SOURCE] In the r1 diagnostic on all completed calls, .2 had 30 successes, 5 binding failures and **0 carrier failures**; .4 had 25 successes, 9 binding failures and **0 carrier failures**. One of the .2 binding failures and six of the .4 failures were classified not retained. Scores were .2=8.9–16.4, median 13.3 and .4=5.0–14.8, median 10.4; some successes used recomputation only. These are the old report's success/failure definitions, not the current four-way C/binding/undecoded/lost partition (`research/f5-encoder-amplified-latent.md:49-56`).

[SOURCE] The r2 change combined soft ML using projection magnitudes with a seven-view CLIP embedding; radii stayed fixed. Offline assumed-correct-code counts at .2/.4 were hard-one-view 31/35 and 28/34, soft-one-view 35/35 and 28/34, hard-seven-view 35/35 and 29/34, soft-seven-view 35/35 and 31/34. Different-label matches were respectively 2,0,6,2 of 114; the hard-seven-view variant failed the specificity criterion. No joint collision appeared in that screen (`research/f5-encoder-amplified-latent.md:81-95`).

[SOURCE] The actual paired comparison was r1/soft-one-view/r2 at .2 = 25/28,26/28,28/28 and .4 = 21/28,21/28,23/28. All-completed .2/.4 improved from 30/35,25/34 to 35/35,29/34. r2 clean both-match stayed 12/12 and LPIPS mean/max .0173/.050. Its five .4 failures comprised two not-retained, two retained binding failures and one retained carrier failure; retained-content success was .2=34/34 and .4=14/17 (`research/f5-encoder-amplified-latent.md:101-114`).

[SOURCE] r2 T4 full donor attribution stayed 0/20 at both residual strengths, while semantic delivery was 0/20 and 1/20. T5 joint collisions were 0/66, despite four semantic matches separated by h distances at least 11. The report records a human acceptance only for the displayed **r1** 52 dB montage; it does not provide a new r2 or future-writer human verdict (`research/f5-encoder-amplified-latent.md:60-69,110-114`).

[JUDGMENT, PROPOSED] This directly refutes an intrinsic-small-binding interpretation: a real deployment changed K1/K2 and recovered paired .2 from 25 to 28 and .4 from 21 to 23 without a new carrier. A small residual K1/K2/K10 ceiling in present r2 foreign-family cells is conditional on the improved descriptor and current carrier bottleneck. Conversely, the r1 partition cannot be copied into today's stricter C loss accounting because it allowed recomputed-only success (E02 sources above).

### E03. H1 carrier geometry: the tested narrow band did not improve regeneration

[SOURCE] Relevant components: K4/K7/K9. The four-development-source, five-seed H1 comparison used baseline radial band 4–32 versus 8–28. At strengths .4/.5/.6, baseline successes were 13/18,10/18,2/17; narrow-band successes were 13/17,9/18,1/16. Mean PSNR/LPIPS were 44.71/.0172 and 45.06/.0107. The historical matched-filter calculation suggested only approximately 1 dB available improvement (`R3:research/H1-band-result.md:3-12`).

[SOURCE] The plateau report estimates .4 attenuation near .57 and correlation .79, with per-band variability .12–.35 and optimal attenuation/variance weighting worth about 1.1 dB. The research plan listed additional bands 6–24 and 4–24, but this inspected result reports the 8–28 test; a plan is not evidence those other bands were run (`research/f5-plateau-20261005.md:7`; `research/f5-research-plan.md:25-29`).

[JUDGMENT, PROPOSED] H1 ruled out **the tested 8–28 replacement as a robustness gain on that small SD1.5 panel**. It did not rule out learned/nonradial allocation, another carrier space, chroma allocation or foreign-family-specific geometry. The lower LPIPS is real evidence of a quality tradeoff, not the required T3 improvement (E03 sources above).

### E04. H3 texture-mask sweep: quality savings did not preserve equal T3

[SOURCE] Relevant components: K4/K6/K7/K10. The fuller killed H3 result is on `claude/f5-r3-256`, beyond the brief plateau summary. It used the same 12 development-source stress panel; variable denominators reflect safety blocks. All reported C0/wrong-owner calls were zero (`R3:research/f5-H3-equalT3-result.md:3,11-18`).

| Configuration | .4 | .5 | .6 | .4+.5 | Mean PSNR | LPIPS mean/max |
|---|---:|---:|---:|---:|---:|---:|
| [SOURCE] mask 0, robust 52 dB | 49/58 | 37/58 | 10/57 | 86/116 | 44.71 | .0172/.050 |
| [SOURCE] mask .5, 52 dB | 38/58 | 23/59 | 6/57 | 61/117 | 44.64 | .0131/.043 |
| [SOURCE] mask .5, 50 dB | 47/58 | 31/59 | 11/57 | 78/117 | 43.72 | .0165/.049 |
| [SOURCE] mask .5, 48 dB | 44/58 | 33/59 | 20/57 | 77/117 | 42.60 | .0216/.057 |
| [SOURCE] mask 1, 50 dB | 11/57 | 4/56 | 0/58 | 15/113 | 43.72 | .0133/.043 |
| [SOURCE] mask 1, 48 dB | 21/58 | 12/57 | 3/57 | 33/115 | 42.62 | .0166/.050 |

[SOURCE] Table locator: `R3:research/f5-H3-equalT3-result.md:11-18`. Failure attribution at .4/.5/.6 was baseline carrier 3/7/38 and binding 6/14/9; mask .5/52 carrier 17/31/49 and binding 3/5/2; mask .5/50 carrier 4/18/38 and binding 7/10/8; mask .5/48 carrier 2/7/24 and binding 12/19/13 (`R3:research/f5-H3-equalT3-result.md:24-27`).

[SOURCE] All tested variants failed the preset joint goal of at least 15% LPIPS reduction without loss of paired T3. The closest comparable candidate saved only about 4% LPIPS; raising energy repaired some carrier losses but exposed more binding losses (`R3:research/f5-H3-equalT3-result.md:33-46`; threshold of the goal in `research/f5-research-plan.md:37-40`).

[JUDGMENT, PROPOSED] This kills those mask-power/budget combinations, not perceptual allocation as a class. It is especially relevant to the binding-ceiling argument: under mask .5, moving 52→48 dB changed .5 carrier failures 31→7 while binding failures grew 5→19. The latter count is conditional on which signals became observable, so component-loss ceilings are not independent or additive (E04 sources above).

### E05. H4 threshold relaxation: local rescues cost natural-image specificity

[SOURCE] Relevant components: K1/K2/K9/K10/K12. On the 12-source stress run, soft versus hard decoding produced .4=49/58 versus 42/58, .5=37/58 versus 35/58 and .6=10/57 for both. This gain was already incorporated in r2 (`R3:research/H4-binding-result.md:10-12`).

[SOURCE] On 132 ordered clean cross-source pairs, the number within semantic distance 6/7/8/10 was 4/10/21/62. Relaxing the radius from 6 to 7 or 8 rescued .4 binding failures 4/6 or 5/6, .5 failures 0/14 or 4/14, and .6 failures 1/9 or 4/9 (`R3:research/H4-binding-result.md:24-30`).

[JUDGMENT, PROPOSED] The equal-specificity relaxation criterion failed. These counts are semantic code proximity, not a measured full-system T5 false-attribution table; do not convert the report's warning about future joint collisions into an observed joint failure. Nor does H4 reject a different estimator, calibrated decision family or payload code. The rejected one-view/seven-view configurations and this radius sweep are finite interventions, not evidence that every additional view is useless (E02 and `R3:research/H4-binding-result.md:32-37`).

### E06. Noiseless semantic binding ceilings: informative but conditional

[SOURCE] Relevant components: K1/K2/K3/K9/K10/K12. A saved-development CPU study used 173 completed attacks on 12 sources, compared the seven-view 512-dimensional true feature with 32/64/128/256-bit sketches, and held carrier-lost cases fixed. Thresholds matched either zero or four of 132 ordered clean cross-source false pairs. The 32/64/128/256 random-sketch experiments used five projection draws (`IDEAS:research/ideas/binding-ceiling.md:3,11-17,78-81`).

[SOURCE] Production .4/.5/.6 successes were 49/37/10, with binding failures 6/14/9 and carrier failures 3/7/38. Median positive feature angles were 22°/29°/44° (maxima 40°/50°/61°), while clean inter-source median was 59°, minimum 32.7° and fifth percentile 45.6° (`IDEAS:research/ideas/binding-ceiling.md:21,27-32`).

| Fixed false-pair budget k=4/132 | .4 | .5 | .6 |
|---|---:|---:|---:|
| [SOURCE] True feature angle | 55 | 44 | 14 |
| [SOURCE] Keyed 32-bit true-q diagnostic | 51 | 30 | 6 |
| [SOURCE] Random 32 bits, five-draw range | 33–50 | 17–33 | 0–7 |
| [SOURCE] Random 64 bits | 47–54 | 29–45 | 5–11 |
| [SOURCE] Random 128 bits | 48–54 | 30–44 | 8–13 |
| [SOURCE] Random 256 bits | 54–55 | 44–48 | 12–15 |

[SOURCE] Table locator: `IDEAS:research/ideas/binding-ceiling.md:38-44`. At .5 the true-angle AUC was .985, the keyed 32-bit AUC .91 and random 256-bit AUC about .98 (`IDEAS:research/ideas/binding-ceiling.md:50-55`).

[SOURCE] A second DDIM family (50 steps, CFG 7.5, prompt “a photo”) produced baseline .4/.5/.6=38/59,17/59,12/56, with binding failures 17/22/5 and carrier failures 4/20/39. At the same k=4 diagnostic, true-angle counts were 53/32/10 and 256-bit ranges 52–53/27–33/7–11. Production .6 exceeded the “ideal” true-angle count because production and diagnostic thresholds were not actually equivalent operating points (`IDEAS:research/ideas/binding-ceiling.md:98-119`).

[JUDGMENT, PROPOSED] This is a **noiseless fixed-representation/fixed-panel diagnostic**, not an upper bound on every possible binding design, and not a realizable 256-bit watermark. It shows meaningful latent descriptor headroom: the second family's .5 true-feature comparison was 32 versus production 17, subject to the operating-point qualification. The historical phrase “no binding change of any kind” overstates what was tested. T3 feature estimation, transport cost, T5 natural-image collision probability and adaptive-owner forgery are separate problems (E06 sources above, especially :59 and :78-81).

### E07. r3-256: the physical implementation lost more than the noiseless sketch gained

[SOURCE] Relevant components: K2/K3/K4/K6/K7/K9/K10. The r3 candidate replaced 32×10 owner-conditioned segments with 256 antipodal chips and soft angular likelihood; it retained the nominal writer budget/fragile tier but used margin 4.5 rather than baseline 4. It retained the recomputed threshold 4.982 and expressed binding radii 6/10 on the old 32-bit scale. Selection required a combined .4+.5 gain of at least eight calls, no family loss greater than two, zero negatives, clean 12/12 and bounded quality loss (`R3:research/f5-r3-256-selection.md:3,7-11,24-27,37-48`).

[SOURCE] In the first regeneration family, the simultaneous remote r2 baseline was .4=49/58, .5=36/58, .6=10/57 (combined .4+.5=85). r3 was 39/58,26/57,2/57 (combined 65). Mean PSNR was 44.69/44.70; LPIPS mean/max .0173/.0502 versus .0171/.0507; both had clean 12/12 and zero reported negatives. The twenty-call deficit triggered the kill: the second baseline was interrupted, the second r3 family was not run, and candidate T4/T5 were not run (`R3:research/f5-r3-256-result.md:11-28`).

[SOURCE] r2 carrier failures at .4/.5/.6 were 2/8/39 and binding failures 7/14/8; r3 carrier failures were 3/21/50 and binding failures 16/10/5. Seventeen of r2's 36 .5 successes depended on recomputed-only detection, versus one of 49 at .4. On a checked-only endpoint, .4 was r2/r3=48/39 while .5 was 19/26: r3 improved that narrower .5 endpoint while failing the declared overall selector (`R3:research/f5-r3-256-result.md:23-39`).

[SOURCE] The report's mechanism account is that antipodal flips attenuate coherent signal as 1−2θ/π rather than the orthogonal-segment 1−θ/π, the median .5 owner score was only 5.45 against 4.98, and the weakest positions around chips 12–13 had median margins near 1.5. Clean code distance 0–2 became approximately 2 after VAE and median 4.6 after .4, with 16 binding failures across radius 6 (`R3:research/f5-r3-256-result.md:43-48`).

[JUDGMENT, PROPOSED] This rules out that 256-antipodal-chip writer/code/reader package at that budget and first-family gate. It does not prove an intrinsic 32-bit or 256-bit capacity limit, and it does not reject a shorter proper ECC, pilot-assisted or orthogonal construction. Nor may its unrun T4/T5 cells be represented as passing. The lower old composite detection but higher checked-only .5 count is a useful warning about endpoint substitution (E07 sources above; options explicitly distinguished at :52-56).

### E08. F4 chroma: better raw channel response did not yield a clean equal-quality winner

[SOURCE] Relevant components: K4/K7/K8/K9/K10/K11. The F4 development probe completed 792/795 paired attacks on 12 sources. At an extrapolated 35.5 dB budget, low-band 8–16 mean/min scores for luma/red–green/blue–yellow were 1.7/1.0,15.6/5.9,7.8/4.8; at 16–32 they were 3.5/2.7,22.5/7.2,16.9/7.5. High-band chroma gain could be only .02. These were fixed-pattern probes, not a finished content-bound watermark (`research/f4-chroma-carrier.md:9-17`).

[SOURCE] F4 changed the image-domain robust tier to Cr, optionally Cr/Cb and smoothing, with the shared fragile tier. Its selected r4 (mask 2, smoothing 4) had mean PSNR 43.4 and LPIPS mean/max .017/.048, but paired F4/v5 success **numerators** at .1/.2/.4 were 25/25,13/17,2/2. The r2 mask-1.5 setting gave 27/25,21/18,13/2 but LPIPS max .116 failed one image. Cr/Cb r3 gave 27/26,23/17,5/2 but max .105 failed one. A post-hoc r5 (mask 2.5, smoothing 3) gave 27/26,23/17,6/2 at mean PSNR 40.3 and LPIPS .041/.083. These slash pairs compare methods; they are not success fractions (`research/f4-chroma-carrier.md:21,29-39`).

[SOURCE] F4 clean both-match was 12/12 and reported negative detections zero. T4 full attribution was 0/20 at both residual strengths, despite semantic delivery 20/20. T5 joint collisions were 0/66. Six of 57 different-label semantic comparisons matched, but the unmarked F4 profile already had eight versus v5's one because changing the profile changed the projection draw; h separated the observed joint decisions. Post-hoc r5 had minimum PSNR 40.1 and SSIM .967, but was the seventh variant and had no human acceptance (`research/f4-chroma-carrier.md:37,45-59`).

[JUDGMENT, PROPOSED] F4 failed the intended equal-perceptual-quality improvement, while the post-hoc quality-feasible r5 was not a prospectively selected or human-approved result. Its 20/20 delivery with 0/20 attribution is particularly useful for K8/K10: detecting a transferred donor mark and rejecting full donor attribution are distinct achievements. The study does not reject every chroma mechanism or prove foreign-family transfer (E08 sources above).

### E09. Original F5 M2: frozen held-out evidence, not a tuning pool

[SOURCE] Relevant components: K4/K5/K7/K8/K9/K10/K11/K12. **FROZEN HELD-OUT REPORT ONLY.** The approved COCO512 study completed 7,741 planned rows. Clean evaluation used 300 sources; T3 used 30 sources and three seeds with two-of-three source-majority success; T4/T5 were small descriptive subsets (`M2:research/m2-coco512-results.md:7-25,44,65-67`).

[SOURCE] Clean F5/v5 both-match was 299/300 versus 300/300. F5 met strict quality on 298/300 (mean/min PSNR 44.5/41.6, minimum SSIM .959, mean/max LPIPS .022/.104), compared with v5 300/300 (37.5/35.2, .963, .021/.082). Embed time means were 22.4 versus 2.3 seconds. Each of the three clean negative query classes had zero of 300 (`M2:research/m2-coco512-results.md:48-63`).

[SOURCE] T3 F5/v5 semantic row counts were .1=90/90 versus 87/90, .2=87/90 versus 62/90, .4=60/90 versus 14/90. “Semantic” included checked decoded q plus assumed recomputed-only success: F5 .2=79+8 and .4=51+9; v5 .2=30+32 and .4=7+7. Source-majority semantic counts were .1=30/30 versus 29/30, .2=30/30 versus 22/30, .4=21/30 versus 5/30; checked-only source counts were .2=27/30 versus 10/30 and .4=17/30 versus 3/30 (`M2:research/m2-coco512-results.md:69-91`).

[SOURCE] The legacy full `both_match` endpoint after regeneration was 0/90 at each strength. T4 false full donor attribution was 0/29 pairs (0/58 rows), while delivery witnesses were F5 4/30 versus v5 8/30 and donor semantic consistency 3/58 versus 5/58. T5 false full match was 0/27 different-owner pairs; the corresponding one-sided upper bounds were .098 for T4 and .105 for T5, not below 1% (`M2:research/m2-coco512-results.md:94-121,133-136`).

[JUDGMENT, PROPOSED] This supports the historical SD1.5-family advantage and exposes quality-tail and delivery limitations. It does not establish universal foreign-family survival or universal disappearance of all instance-related observables. In particular, the old full `both_match` includes fragile-tier transmission and cannot be substituted for later J, which must be interpreted using its own endpoint definition. The report itself calls F5 an image-domain modification optimized through the encoder, not the proposal's generation-time latent method (`M2:research/m2-coco512-results.md:142-150`).

### E10. E3: real coding/objective gains, costly writing and endpoint-sensitive comparisons

[SOURCE] Relevant components: K1/K2/K3/K5/K6/K7/K8/K9/K10/K11/K12. E3 S1 used a BCH(59,32), t=5 semantic code within 320 chips; the reader still had no original image or registry. Its writer started from an F5 bootstrap, used the **decoded operational h**, then a fixed initializer and a 20-step minimax objective spanning clean, SD1.5 VAE, SDXL VAE and SD1.5 DDIM .1/.2 at three seeds. Rounded/reloaded proposals were accepted only under quality, exact-q/h and objective eligibility; one .8 quality contraction was permitted. SDXL VAE exposure was not SDXL full-diffusion training (`J09/e3-s1-method-freeze.md:7-31,45`).

[SOURCE] E3's fresh 12-source development M1a had strict quality on 12/12 (minimum PSNR 40.36345, SSIM .95645766, max LPIPS .07625771), clean exact q/h and both-VAE semantic success 12/12. Paired .1/.2 were 29/29 and 28/28 versus v5 27/29 and 18/28. Full observed calls gave S/Q/J=36/36 at .1 and 35/36 at .2 with one safety block; H/F were zero. Negatives were 0/477 observed of 504 planned. Residual T4 full attribution was 0/20; public-projection T4 delivered exact q/h on 20/20 but full attribution 0/20; analogous T5 delivered exact q/h 7/7 and full attribution 0/7. Writer mean/median were 131.8268/130.422 seconds (`J09/e3-s1-m1a-assessment.md:7-25`).

[SOURCE] The subsequent fixed 24-source development unseen-regenerator selector retained F5: at SD2.1 .2 E3 and F5 were both C=24/24, so E3 did not reach the required three-source advantage. All three arms passed strict quality on 24/24, at unmatched distortion. E3/F5 median LPIPS was .0392575/.0144277 and median writer time 130.133/52.4685 seconds; minimum PSNR was 39.6952/42.1568 (`J09/unseen-regenerator-results.md:3-5,17-19`).

[SOURCE] The same study still found informative E3 advantages: at SD1.5 .4 source C/J was E3 19/19 versus F5 12/4; at SD2.1 .4 it was E3 22/22 versus F5 12/4. At SD2.1 .2 both had C=24 but J was E3 24 versus F5 12. H and full F remained zero after regeneration. The .4 C comparison had adjusted p=.00976562, but the prespecified .2 selection remained F5 (`J09/unseen-regenerator-results.md:25,54-71,117`).

[SOURCE] **FROZEN E3 M2 REPORT ONLY:** Original composite source counts were E3/v5 .1=281/300 versus 151/300 and .2=278/300 versus 129/300. Clean exact-q counts were 300 versus 296, exact-h 300 versus 162, strict quality 294 versus 298 and full eligibility 294 versus 159. E3 LPIPS median/max was .047652/.184441 with six strict-quality failures; v5 .018316/.102785 with two. These composite counts were not pure T3 survival (`J09/e3-s1-m2-results.md:23-42`).

[SOURCE] Frozen ungated E3/v5 counts were S .1=287/283, .2=284/232; C .1=287/243, .2=284/112; Q .1=294/81, .2=297/17; J .1=287/80, .2=284/17. H/D/F were zero after regeneration. Negative clean calls were zero of 300, but T3 negative evidence had ten unresolved source units for E3 versus three for v5 (`J09/e3-s1-m2-results.md:48-62`).

[SOURCE] A declared **post-hoc sensitivity**, removing only the clean exact-h gate, changed v5 eligibility 159→293 while E3 stayed 294. Composite .1 became 281 versus 278 (p=.364), and .2 became 278 versus 229 (p=1.15e-8). This does not replace the frozen gate or the separate ungated C/J comparison (`J09/e3-s1-m2-sensitivity.md:3,11,33-42`).

[SOURCE] Frozen public-projection T4 and T5 delivered E3 Q/H/D=30/30/30 with full F=0/30. Residual transfer did not have equivalent delivery: at half strength E3 Q/H/D=2/0/0 and at full strength 6/2/2. In the same combined-call audit, E3 semantic-only T4 acceptance was 1/30 and T5 9/30, while perceptual-only and combined acceptance were zero. These mode-switch outcomes were not isolated writer ablations, and human admissibility remained missing (`J09/e3-s1-m2-results.md:70-79`).

[JUDGMENT, PROPOSED] E3 shows that coding/objective/write-order packages can substantially improve strict read and exact-checked-semantic endpoints. Here J means **exact checked semantic**, not joint recovery of q and h; D and F carry those separate two-part requirements (`J09/e3-s1-m2-results.md:48-54`). The study does not isolate BCH from objective, additional distortion, initialization or eligibility selection. Its equal SD2.1-.2 result supports retaining F5 under the fixed selector, not E3 inferiority everywhere. Exact-h eligibility had a large comparator-dependent effect, making “fragile is useless” and “E3 wins regeneration by 43 percentage points” both misleading simplifications (E10 sources above).

### E11. Descriptor/reissue round: stability and specificity are separate from transport

[SOURCE] Relevant components: K1/K2/K3/K6/K7/K8/K10/K11. The reissue diagnostic found LPIPS values .0887/.0203/.0319/.0088/.0728/.0665 rising to .2581/.0547/.0729/.0209/.1729/.1904. MSE ranges moved 2.95–6.40→10.34–14.62. The new budget was anchored to an already marked input, the fragile target was recomputed and canonical-reference quality selection was absent; residual alignment cosines .42–.59 were consistent with accumulation. This did not isolate a unique cause or find a metric bug (`J09/next-round-results.md:7-9`).

[SOURCE] A perfect-old-h-transport oracle on six consulted development sources/54 saved regeneration identities could only reach SD1.5 VAE 3/6, .2=6/18 (one source majority) and .4=4/18. Actual J on those cells was 6/6,18/18,16/18 while actual transported H/F was zero; these are different success requirements (`J09/next-round-results.md:13-23,59`).

| Descriptor screen, perfect transport | SD1.5 VAE | .2 oracle / source majorities | New texture-sibling matches | Canonical / marked real-impostor matches |
|---|---:|---:|---:|---:|
| [SOURCE] CD1 coarse-only, 32 bits | 6/6 | 18/18; 6/6 | 4/6 | 0/552; 0/552 |
| [SOURCE] BI1 equal-energy, 32 bits | 5/6 | 10/18; 3/6 | 2/6 | 0/552; 0/552 |
| [SOURCE] FG128 fine-only Gaussian | 6/6 | 17/18; 6/6 | 0/6 | 2/552; 0/552 |

[SOURCE] Table locator: `J09/next-round-results.md:57-62`. Fine-feature positive cosines .5406–.7913 (mean .6614) remained separated from texture-sibling cosines .0155–.0521, while coarse positive cosines .9656–.9965 overlapped siblings .9957–.9996. Thus some useful fine detail survived, even though the tested fixed descriptors failed (`J09/next-round-results.md:31-39`).

[SOURCE] FG128 changed representation, projection distribution, bit count, weak-detail abstention and tolerance together. Its match radius 44 of 128 had an ideal independent-bit ball mass .000257892, close to .000267526 for 32/6, but that did not match natural-image FPR. Its two ordered canonical matches were the two directions of one pair at distance 44, not two independent failures or a measured full-system false attribution. The old h rejected that pair at distance 13; its uncompressed fine-feature cosine .01019995 corresponded to hypothetical Gaussian mean distance 63.5844. No post-outcome threshold/seed rescue or GPU carrier was built (`J09/next-round-results.md:45-51`).

[SOURCE] The independent review accepted the evidence package and closed these fixed protocols; it explicitly rejected the interpretation that one finite collision proves intrinsic 128-bit insufficiency, that the combined interventions isolate capacity, or that these variants count as three independent failed design families (`J09/next-round-results.md:64-68`; `J09/descriptor-round-independent-review.md:44-55`).

[JUDGMENT, PROPOSED] Perfect transport is not enough for the old h, but regeneration has not been shown to erase all instance information. Coarse invariance can discard exactly the detail T5 needs. FG128 suggests combined representation/capacity headroom, not a deployable improvement or permission to reopen the closed line; any such proposal must be labelled REOPENS-CLOSED-LINE under the current brief (E11 sources; `research/f5-components-20261101/BRIEF.md:38`).

### E12. Registry: additional side information helps a different task, with hard near-negative limits

[SOURCE] Relevant components: K1/K2/K8/K9/K10/K11/K12. Registry verification uses trusted enrolled continuous descriptors and owner/record lookup. Its F_R requires a found/read pointer, q within six of the record, and a correct descriptor match above a frozen threshold. This is additional detector side information, not the reference-free F5 task (`J09/registry-verification-results.md:18-22`).

[SOURCE] An initial consulted 24-source screen selected D1: source-majority F_R was SD1.5 .1/.2/.4=24/22/15 and SD2.1=24/24/15; D1 screening threshold was .0594367 with zero of 43,917 observed negative comparisons and 345 blocked. That screening result did not survive the fresh amended development evaluation (`J09/registry-verification-results.md:30-34,51-59`).

[SOURCE] Fresh 40-source evaluation at frozen tau .586548254817741 gave F_R SD1.5 .1/.2/.4=35/30/7 and SD2.1=37/32/8. The primary target was 36/40 at .2, so deficits were six and four sources. Fingerprint-only counts were respectively 35/30/8 and 37/32/9. Observed registry false accepts were zero, with 819 blocked wrong-source comparisons unresolved. A near-duplicate calibration pair set max cosine .5865482548177409 versus .05467683669602197 outside that family; no threshold rescue followed (`J09/registry-verification-results.md:3,7-14`; `J09/article-claim-map.md:3`).

[SOURCE] Fingerprint-only accepted 4/13 real near-duplicate evaluation pairs versus registry zero; eleven were finite and two abstained. However, all 13 were unmarked original-frame comparisons with `pointer_candidate=false`. Thus this does not demonstrate descriptor discrimination conditional on a valid owner pointer. The final wrong-source accounting was 52,630 evaluable of 59,280 planned, 5,831 abstentions and 819 blocked; known T4 was 76/80 plus four abstentions, with zero accepted (`J09/registry-verification-results.md:14-20,419-422`; `J09/article-claim-map.md:3`).

[SOURCE] Registry costs were measurable: D1 stored 2,555,904 bytes for N=40, with 39 searchable records; 3,040 dot products took .016 seconds and 368 image extractions 56.1892 seconds. These historical small-bank costs do not establish large-bank scaling or a reference-free reader cost (`J09/registry-verification-results.md:438`).

[SOURCE] **FROZEN LATER HELD-OUT REVIEW ONLY:** A later registry package reached source-majority F_R SD1.5 .2=277/300 (lower bound .89313049), SD2.1 .2=280/300 (.90459802). Wrong-source comparison was zero of 3,343,081 evaluable versus 3,408,600 planned, with 65,519 missing; T4 was zero of 594/600 observed rows from 297 donor clusters. The real-lookalike challenge nevertheless had 3/45 false accepts affecting two of sixteen eligible shots, plus 2/15 ambiguous-real and 4/12 synthetic accepts. The millions of comparisons are dependent on a fixed record bank (`research/q1-dossier-20261018/01b-heldout-registry-m2-review.md:21,31-48`).

[SOURCE] In that review's regenerate-and-enroll test, original/none/attacker pointer outcomes were: SD1.5 .2 exact 280/14/0 of 294, further-regenerated 242/52/0 of 294; SD1.5 .4 exact 201/93/0 of 294, further 81/212/0 of 293; SD2.1 .2 exact 282/15/0 of 297, further 249/48/0 of 297; SD2.1 .4 exact 199/98/0 of 297, further 81/216/0 of 297. The frozen registry **experiment E3** pass flag remained false, with all 2,400 entries unknown due to unavailable records; this experiment label does not mean the E3-S1 writer. The approved pre-outcome complete-case amendment was distinct. Strict marked quality was 291/297 observed with three marks missing, six LPIPS failures and max LPIPS .149810; human acceptance was missing (`research/q1-dossier-20261018/01b-heldout-registry-m2-review.md:62-89`).

[JUDGMENT, PROPOSED] The fresh development gate failed and the later held-out package did not establish universal near-duplicate specificity. Neither the initially successful consulted screen nor the later positive T3 count licenses retuning. The record-bank pointer supplies provenance discrimination in a changed information model; fingerprint matching alone does not become cryptographic ownership. These studies bear strongly on K1/K8/K10/K11 even though their numeric thresholds cannot be imported into reference-free F5 (E12 sources above).

### E13. Development transfer Stage 2: F5 is family-specific, with observable subthreshold signal

[SOURCE] Relevant components: K3/K4/K5/K7/K8/K9/K10/K12. Stage 2 used 60 development sources and seeds 12/13/14, source-majority success at two of three. Stage 2b F5/v5 C counts were SD1.5 .1/.2/.4=60/47,57/27,39/3; SDXL .1/.2/.4=0/50,0/12,0/0; K3 .2=5/57. These method comparisons used unmatched distortion (`ET/results.md:41,45-52`; `ET/results-2b.md:51-60,124-132`).

[SOURCE] Clean F5 had S=C=A=60/60 but exact Q=52/60. SDXL VAE-only produced S=A=60/60, C=55/60, Q=31/60; K3 MoVQ-only produced C=55/60,Q=35/60. Full SD1.5 .2 had S=58,C=57,Q=38,A=59; SDXL .2 had S=C=Q=0,A=30. The report defines S as found+content, C as read+content, Q as exact q and A as either tier found (`ET/results.md:67-78`).

[SOURCE] All 180 F5 SDXL-.2 calls failed the semantic find test. Their normalized correlation ratio still had median .33, IQR .17–.48 and maximum .97, versus unmarked median −.04/max .52: 171/180 exceeded the unmarked median and 39/180 exceeded its maximum. Thus the report explicitly distinguishes failed operating-point detection from literally absent residual signal (`ET/results.md:81-90`).

[SOURCE] For all 58 complete sources, SDXL .1 was milder than SD1.5 .2 and .4 on all three image-quality metrics, yet F5 C was zero; all 39 sources succeeding on SD1.5 .4 failed SDXL .1. Resolution, pipeline and model family changed together. F5 any-tier A remained SDXL .1/.2/.4=52/60,30/60,5/60. These are not C or full instance-binding successes (`ET/results-2b.md:79-84`).

[SOURCE] At K3 .2 the seed-level F5 partition was 16 C,46 found-not-read,6 binding failures,112 not-found; source S=21/60 and A=29/60. K3 effective noise standard deviation was .24 versus SD1.5/SDXL .42 despite a shared nominal strength/timestep index, so nominal strengths were not equal noise exposures. SDXL mode and modest smoothing both kept F5 C at zero; A was 30 sampled,32 mode and16 smoothed (`ET/results-2b.md:124-152,163-168`).

[SOURCE] Stage 2a median F5 PSNR/SSIM/LPIPS was 44.96/.983/.020, with strict quality 60/60; v5 36.85/.978/.019, also 60/60. VINE-R was 35.14/.996/.006, but only 31/60 passed strict quality because of the PSNR bound. F5 writer cost was about 118 seconds per image on the reported RTX4090 environment; human acceptance was missing (`ET/results.md:149-158`).

[JUDGMENT, PROPOSED] “Carrier lost” should mean **neither current detector passed**, not physical annihilation of every signal. The codec-only/full-regeneration contrast rejects codec round-trip failure as the sole explanation, but does not alone isolate noise injection from reverse denoising. A=52/60 at SDXL .1 also prevents the universal statement that the fragile tier never survives any regeneration. It does not prove content identity from those detections (E13 sources above).

### E14. Phase A mechanism: foreign encoder gain exists; survival collapses around noise injection

[SOURCE] Relevant components: K4/K5/K6/K7/K9/K12. Phase A's development native panel broadly reproduced Stage 2; report-specific comparator counts differ in small cells (e.g. v5 SDXL .2=11/60 here versus 12/60 in Stage 2, WAM SDXL .1=49 versus48), so they must not be silently merged. A VINE known-message C0 call scored 69/100 at threshold 69; other reported known-message negatives were zero (`PA:49-59`).

[SOURCE] The pooled local-linear model estimated kappa=.02865 on 533/540 fit observations, with 30 fit and 30 calibration sources; it predicted zero source successes on all native cells despite actual F5 SD1.5 rates 1.00/.95/.65. Cell kappas SD1.5 .1/.2/.4 were 1.08/.98/.61, with cosines .90/.83/.68 and norm ratios .83/.80/.93. SDXL kappas were .0046/.0010/.0001, cosines .047/.016/.013 and norm ratios 7.7/14.8/14.2. SDXL accounted for 97% of the pooled denominator (`PA:27-28,70-83`).

[SOURCE] The 12-source mechanism panel found F5 encoder gain larger than control directions in all tested encoder families: SD1.5 15 versus 4.8–6.4, SDXL 392 versus178–249, K3 43.3 versus20–27. The report's conclusion is that amplification transfers, while post-regeneration survival does not (`PA:87-97`).

| Stage, signed chip-projection retention at .2 | SD1.5 | SDXL | K3 where reported |
|---|---:|---:|---:|
| [SOURCE] Posterior-mode codec | .98 | .66 | .72 |
| [SOURCE] Sampled codec | .98 | .66 | — |
| [SOURCE] Noise-injection point | .92 | .08 | .34 |
| [SOURCE] Mode plus reverse process | .74 | .08 | — |
| [SOURCE] Native full pipeline | .74 | .08 | .17 |

[SOURCE] Table locator: `PA:103-107`. The report interprets the steep foreign loss as occurring around noise injection rather than at codec encode/decode, but explicitly labels this within-source mechanism panel descriptive rather than causal (`PA:109-114`).

[SOURCE] The candidate attacks A/B did not pass the prescribed quality/coverage eligibility: the minimum was 48/60 per arm satisfying LPIPS≤.15, PSNR≥25 and SSIM≥.75; best A coverage was 24–27 and best B 30–37. The empirical quality comparator was also BASELINE_UNAVAILABLE with four of six required cells and one setting instead of five. These are failed or incomplete calibration/attack-validity results, not successful eligible attacks (`PA:29-37`).

[JUDGMENT, PROPOSED] The most defensible correction is “SD1.5-optimized perturbations amplify under foreign encoders but align poorly with surviving foreign regeneration directions.” Saying “foreign encoder gain is absent” contradicts the measurements. The nonlinear, nearly orthogonal SDXL response also blocks a reliable linear extrapolation from twice the robust amplitude to twice the final detector score. This panel does not prove what F6, another surrogate or another reader would do (E14 sources above).

### E15. Phase B: frozen independent-transfer validation and unresolved negatives

[SOURCE] Relevant components: K4/K5/K7/K9/K10/K12. **FROZEN REPORT ONLY; NO PER-SOURCE JOURNALS.** On 200 held-out sources, conservative F5/v5 C source counts were SD1.5 .1=186/163, .2=182/122, .4=140/28; SDXL .1=19/173, .2=0/47, .4=0/0; K3 .2=61/189. F5 clean C was 196, v5 199; the F5 codec-only control had 194/200. Missing-case upper possibilities differ for some SD1.5 cells, e.g. .2 F5 186 versus conservative182 (`PB:95-103`).

[SOURCE] H2 F5 SD1.5-.2 C=182/200 supported the specified >.80 hypothesis after Holm correction (p=1.8e-5). H3 J count 163/200=.815 did **not** establish >.80 (p=.335). H1's near-total SDXL-loss test was also inconclusive: SDXL-.1 possible count 19/200=.095 produced p=.466 against its <.10 criterion. Development 0/60 did not predict the held-out .095 rate (`PB:56-59,73`).

[SOURCE] Every negative gate was incomplete, with four to eight unresolved source cases; observed F5 C0/wrong-owner errors were zero with four/eight unresolved. VINE wrong-owner had one observed failure plus its earlier known-message C0 finding. No empirical negative gate was a complete matched-FPR demonstration (`PB:77-87`).

[SOURCE] Median F5 PSNR/SSIM/LPIPS was 45.1/.982/.035 versus v5 36.5/.976/.030 and VINE 34.7/.995/.008. F5 also had larger median regenerated distortion to the unmarked input in some cells, e.g. SD1.5 .2 LPIPS .187 versus unmarked regeneration .154. This correlation is not a mechanism experiment. Development K3 5/60 versus held-out61/200 and SDXL .1 0/60 versus19/200 are population/study differences, not evidence from a matched intervention (`PB:128-153`).

[JUDGMENT, PROPOSED] Phase B supports narrow independent-transfer limitations while refusing two stronger conclusions: the <.10 SDXL hypothesis was not confirmed, and zero observed errors with unresolved negatives is not a fully passed false-positive gate. Frozen held-out numbers are context and claim limits, never a basis for tuning a component (E15 sources above; `BRIEF.md:25-26`).

### E16. F6 and RL: existing proposals, no efficacy evidence to inherit

[SOURCE] Relevant components: K3/K5/K6/K7/K9/K10/K11/K12. The F6 final report proposes noise-aware writing through finite codec/noise transforms while keeping the F5 reader, plus a distinct predicted-clean Px0 objective through a frozen epsilon predictor. The Px0/noise difference also changes timestep selection, so it is not a pure denoiser ablation. It explicitly has no positive F6 experimental result (`research/tifs-20261028/FINAL-REPORT.md:34-38,83`).

[SOURCE] Its planned candidate comparison requires C and J plus clean-quality and T4/T5 gates; F5 has a nominal 200-gradient budget versus F6 350 plus surrogate costs. These are planned computational budgets, not demonstrated equal achieved perceptual quality. VINE-Bq adds a public 32-bit owner-q tag plus 36 q-masked h bits and a radius-four tag reader, without an original/registry; public checks are not cryptographic authentication (`research/tifs-20261028/FINAL-REPORT.md:59-67`).

[SOURCE] The separate RL report is a completed assessment, **not an RL efficacy experiment**. C03 proposes state/order selection between robust gradient and quality repair, while C18 concerns acquisition efficiency. A saved fixed-menu oracle improved 275/420 to276/420 by source-cell selection, only a one-case gain; that says nothing about unmeasured new actions/objectives. VINE presence 60/60 did not imply strict feasibility because quality passed only31/60. Strong classical state-informed controls are required before crediting an effect to RL (`RL:research/rl-20261030/FINAL-REPORT.md:5-7,35-41`).

[JUDGMENT, PROPOSED] These packages identify relevant open K5/K6 hypotheses but cannot be cited as prior successful improvements or as proof that K6 is unimportant. Their actual method floors and frozen status remain unchanged; this inventory makes no amendment and allocates no run (`research/f5-components-20261101/BRIEF.md:34`; E16 sources above).

### E17. Coarse lattice: saved-channel diagnostics and a candidate, not measured T3 of the new mark

[SOURCE] Relevant components: K4/K7/K8/K10/K11/K12. The saved luma-band64–96 residual gains for image content/VINE/v5/F5 were SD1.5 .2=.74/.44/.29/1.76, SDXL=.82/.62/.33/.35 and K3=.87/.74/.48/.60. Corresponding red–green noise levels were 33/28/25 versus luma132/98/78. These are channel measurements of existing marks/content, not measured gain of the proposed lattice perturbation (`research/coarse-lattice-20261030/PROPOSAL.md:20-32`).

[SOURCE] The lattice's saved-pixel T4 tests reported chroma0/300 and luma0/150 false attribution for patch128 and256, but patch384 gave2/300 and2/150. Residual-transfer tests gave chroma0/300 after binding versus73/450 before binding and luma0/150; never-marked regeneration negatives were0/180. The new mark itself had not undergone real regeneration; T3 results in that proposal were simulations (`research/coarse-lattice-20261030/PROPOSAL.md:42-64`).

[SOURCE] Chroma marked PSNR median/min was39.86/37.97, SSIM .994/.918 and LPIPS .028/.071. Nevertheless flat-area pink/green blotches were visible in the report's 3× inspection. Luma had median/min PSNR42.16/38.01, SSIM .983/.947 and LPIPS .016/.172, passing the LPIPS gate on59/60. The proposal requires a secret owner key, unlike F5's public profile, and leaves real perturbation gain unknown (`research/coarse-lattice-20261030/PROPOSAL.md:47-49,76-80`).

[JUDGMENT, PROPOSED] Chroma's lower measured channel noise motivates examination but neither proves the lattice will survive nor negates the F4 failure. The T4 pre-/post-binding contrast is direct evidence that binding can matter when carrier delivery exists. The visible defect observation is not a fabricated human acceptance verdict. The only cheap extra-removal limitation to carry unweighted is the chroma design's grayscale vulnerability, as already recorded in the F4 discussion (`research/f4-chroma-carrier.md:53,60`).

## 3. Proposed corrections to the four preliminary findings

### A. “Foreign carrier failure dominates” is useful accounting; “binding is intrinsically small” is not

[SOURCE] The judge's Stage2 seed partition assigns F5 SDXL .2/.4 all180 calls to lost, SDXL .1 to3 binding/23 undecoded/154 lost, K3 .2 to16 C/6 binding/46 undecoded/112 lost, and SD1.5 .4 to117 C/25 binding/26 undecoded/10 lost/2 missing. Its fixed-carrier perfect-binding ceiling is SD1.5 .4 source39→47, with three or fewer added sources elsewhere (`research/f5-components-20261101/judge/JUDGE-FINDINGS.md:20-41`).

[DERIVED] That ceiling is conditional on the **current decoder passing**. It says which present failures can be rescued without changing detectability; it cannot count the binding failures a stronger carrier would expose. H3 provides an observed example of that dependence (E04), and r1→r2 proves earlier binding improvement was valuable (E02). The .4 ceiling of eight sources is also 8/60=13.3 percentage points in that particular cell, not automatically negligible (`JUDGE-FINDINGS.md:41`; E02/E04 sources).

[JUDGMENT, PROPOSED] Keep K4/K5 high for current foreign-family failure, but change “carrier gone” to “both current semantic tests below threshold.” Attribute losses to an interface until an isolated ablation separates K3 coding, K4 geometry, K5 surrogate, K6 writer and K9 test. K1/K2/K10 are small **immediate fixed-reader** T3 budgets in some cells, with potentially substantial T4/T5 duties and downstream duties after carrier improvement (E02/E04/E06/E13/E14).

### B. The 2^32 search penalty is a real candidate cost, but local search changes evidence semantics

[SOURCE] The judge's proposed radius-limited search has lower analytic thresholds and saved-score lower-bound counts, but explicitly changes the endpoint and has no new T4/T5 measurement. r=0 is the old recomputed-only route (`research/f5-components-20261101/judge/JUDGE-FINDINGS.md:43-59`).

[DERIVED] Historical recomputed-only dependence was substantial: r3-selection baseline had17/36 .5 successes by that route, and the frozen F5 M2 .2/.4 semantic counts included8/87 and9/60 assumed successes. Thus raising the count through a content-conditioned query need not raise actual payload reading or independent content verification by the same amount (E07; `M2:research/m2-coco512-results.md:69-79`).

[JUDGMENT, PROPOSED] K9 has a credible low-writer-cost hypothesis, but its null must state what is conditioned on, and public adaptive forgery is outside the old random-key bound. H4's natural-image collisions, v5's strong-mark recomputation caveat and the registry's real-near negatives are the relevant prior failure modes. A new local-search count must be reported beside frozen C/J, not substituted for them (E01/E05/E12; `BRIEF.md:46`).

### C. Fragile budget arithmetic is an upper-resource scenario, not a measured useless-energy fraction

[SOURCE] The judge labels the .41 robust and1.30 fragile MSE shares as **derived budgets, not separately measured**, uses total median PSNR44.96 (MSE about2.08), and suggests approximately2.2× robust amplitude if that total were reallocated. It cites legacy M2 both_match0/90 and acknowledges nonlinear SDXL response and a T4/instance-binding price (`research/f5-components-20261101/judge/JUDGE-FINDINGS.md:61-65`).

[DERIVED] On an 8-bit scale, PSNR52/47/58 dB corresponds to MSE caps approximately .410/1.297/.103. PSNR44.96 corresponds to approximately2.076, so sqrt(2.076/.410)=2.25 is the nominal amplitude ratio. However, sequential robust/fragile/refinement changes obey ||a+b||²=||a||²+||b||²+2a·b; projected budgets, clipping, RGB8 rounding and overwritten fragile content do not supply an observed orthogonal decomposition. The exact percentage reclaimed by deleting a stage is UNKNOWN without the saved stage deltas or a permitted ablation (`BRIEF.md:61-64`; E02 write order; judge arithmetic above).

[SOURCE] The fragile tier is not universally undetectable under regeneration: Stage2 SDXL any-tier A was52/60 at.1 and30/60 at.2 while semantic C waszero. Conversely, E3 and original F5 had full H/F collapse on their SD1.5 cases, even when later J was positive. T4 F4 delivered donor semantics20/20 yet full attribution stayedzero; E3 public projection delivered exact q/h30/30 yet full attribution stayedzero (E08/E09/E10/E13).

[JUDGMENT, PROPOSED] K8 can be a large reallocation opportunity for a **changed T3-only or altered-instance task**, but current evidence does not label the tier useless under the three-threat contract. A decision to reduce/remove it requires explicit reporting of clean-instance behavior, T4/T5 attribution and the new endpoint. The old-h oracle also warns that moving h to a robust carrier alone would not make h regeneration-stable. The 2.25× calculation is not a prediction that SDXL C will clear threshold (E11/E14 and arithmetic above).

### D. Perturbation appearance affects channel response, without giving a ready design winner

[SOURCE] Equal-PSNR natural versus optimized latent probes, H3's quality/robustness tradeoff, F4's failed equal-quality selector, Phase A's geometry and the coarse-lattice saved gains all support that the direction/structure of a perturbation matters, not merely its norm (E02/E04/E08/E14/E17).

[JUDGMENT, PROPOSED] No inspected report identifies one universally transferable appearance statistic or demonstrates that the new lattice perturbation inherits the reported content/chroma gains. Different negative constructions and side information matter as much as the channel: a secret-key lattice, public F5 and trusted registry must not share an ownership claim by analogy. Keep the lattice at candidate status and retain human visual verdicts as MISSING unless the specific artifact was explicitly rated (E02/E12/E17).

## 4. Ceiling and claim discipline to preserve in WP1

| Ceiling or limitation | Status and valid scope |
|---|---|
| Current fixed-reader perfect semantic binding | [SOURCE] Judge reports at most+8/60 F5 SD1.5 .4, ≤3 elsewhere on Stage2; parent WP1 accounting is the appropriate source for the expanded development/PhaseA table. Historical reports do not provide per-source identities needed to recompute every cell (`JUDGE-FINDINGS.md:41`). |
| Carrier/payload/statistic repair | [JUDGMENT, PROPOSED] UNKNOWN as a deployable gain from reports alone. Reclassifying every undecoded/lost call as recoverable assumes a successful new test/carrier and adequate T4/T5 specificity (E07/E13/E14). |
| True-feature or long-sketch semantic binding | [SOURCE] E06 supplies fixed-panel noiseless estimates, not physical payload ceilings or population-FPR bounds. r3's failed transport is the counterexample to treating the oracle as a guaranteed implementation gain. |
| Robust old-h transport | [SOURCE] At most6/18 .2 cases under the E11 six-source perfect-transport oracle for that frozen h/decision; not a ceiling for a redesigned descriptor or registry. |
| Removing fragile tier / increasing robust budget | [DERIVED] Nominal amplitude resource about2.25× at the reported median total PSNR, but outcome ceiling UNKNOWN because stage deltas, nonlinear channel response and changed threat semantics are unmeasured (section3C). |
| Optimizer improvement | [JUDGMENT, PROPOSED] UNKNOWN: E3, r3 and historical refinement combine objective/code/budget changes; no isolated current-F5 convergence optimum was shown (E01/E07/E10/E16). |
| T4/T5 population error | [SOURCE] Zero observed errors in small/dependent panels does not prove a sub-1% rate: old F5 M2 bounds were.098/.105; later negative gates had unresolved units, registry near-negatives had actual accepts (E09/E12/E15). |
| General impossibility or best-method claim | [JUDGMENT, PROPOSED] Unsupported. Failed fixed candidates constrain tested mechanisms/settings; they do not prove arbitrary encoders, descriptors, coding schemes or public/adaptive attacks impossible. F5 is the retained base under its selection rules, not a winner on every family/endpoint (E07/E10/E13/E15). |

[JUDGMENT, PROPOSED] The prior-evidence inventory is complete for this bounded handoff. It does not satisfy the new-paper floors, choose a new method, reopen a closed family, allocate compute or issue a gate ruling. Its main corrective is to keep **observable detection, payload reading, content matching, full instance attribution and ownership claims separate**, and to attach each ceiling to its actual information, distortion, threshold, data-split and threat conditions.

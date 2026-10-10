# Journal development plan

Prepared 2026-10-09 by Codex agent. Evidence base: corrected M2 package at `7f222fe3db7235e3508eac991031222dbd066626`, primary-source refresh, and a fresh methodological design review. This is a prospective research roadmap, not an execution manifest, preregistration, official lifecycle transition, or revised M2 verdict. Numerical targets below are proposed engineering decisions, not journal acceptance rules. Scope remains T3 regeneration, T4 copy-paste, and T5 semantic collision.

Updated 2026-10-10 after the supplied-payload E3 assessment and E3-S1 Stage A. Earlier failed candidates and intermediate findings are preserved in the [development history](plan-development-history-20261010.md).

## Current decision

**E3-S1 now passes the full end-to-end comparative M1a development assessment.** See the [complete assessment](e3-s1-m1a-assessment.md) and [recorded-call analysis](e3-s1-m1a/analysis.json): strict quality and exact q/h/full12/12; both VAE checked q12/12; T3 S/Q/J36/36 and35/36, fixed semantic29/29 and28/28 versus v527/29 and18/28; zero observed negative detections and no T4/T5 regression. One C1 and six C0 T3 safety blocks remain unavailable. Continue directly to M1b freeze, tests, one independent review, a metadata-only fresh confirmatory inventory and synthetic existing-runner rehearsals. No held-out execution is approved and no official or human verdict is recorded.

The earlier supplied-payload E3 operator passes the original comparative M1a under the explicit safety-availability convention: strict clean quality/exact q/h/full 12/12, T3 semantic/exact-q 36/36 at .1 and 35/36 at .2, with one unavailable C1 image; fixed matched semantic counts 29/29 and 28/28 versus v5 27/29 and 18/28. Negative T3 calls are 0/477 observed of 504 planned; 27 calls from seven blocked images are unavailable. T4/T5 show no additional measured false full acceptance. The [complete assessment](e3-m1a-assessment.md) is specific to that supplied-payload operator. S1 must qualify its own newly constructed pixels. Strict extra E3-B remains failed, and historical M2 is unchanged.

The current method is an image-domain comparator with VAE/CLIP extraction. It does not establish the proposal's latent method, lightweight extraction, cryptographic authorization, or reference-specific same-owner attribution. Public donor transfers deliver exact q/h in 20/20 cases but none pass combined acceptance; perceptual-only also rejects all, so an incremental advantage of combining signatures remains unproved. These scope limits travel with any package.

The initial request is answered by the ranges, evidence targets and revised sequence below, the [primary-source comparison](literature-comparison.md), and the [autoresearch assessment](autoresearch-assessment.md). Q1 placement cannot be inferred from a development gate or a single published percentage. [Archived development history](plan-development-history-20261010.md) preserves failed rounds and earlier decisions without making their old next steps current.

## What the present numbers establish

Counts below come from the [corrected M2 report](../m2-coco512-results.md) and [independent review](../m2-independent-review.md). T3 units are 30 sources, each summarized by success on at least two of three seeds; 90 seed rows are not 90 independent sources.

| Endpoint | F5 r2 | v5 | Interpretation |
|---|---:|---:|---|
| Clean full `both_match` | 299/300 | 300/300 | Strong clean recovery, with one F5 failure |
| All three strict quality limits | 298/300 | 300/300 | F5 does not meet an all-image quality claim |
| T3 semantic, strength .2 | 30/30 | 22/30 | Strong internal comparison |
| T3 **checked** semantic, .2 | 27/30 | 10/30 | 90%; one-sided 95% lower bound 76.14% |
| T3 semantic, .4 | 21/30 | 5/30 | Survival falls as regeneration increases |
| T3 **checked** semantic, .4 | 17/30 | 3/30 | 56.67%; lower bound 40.16% |
| T4 false donor full attribution | 0/29 | 0/29 | F5 donor delivery only 4/30; no isolated binding benefit |
| T5 false match, different owner | 0/27 | 0/27 | Limited precision and no component ablation |

F5 mean PSNR is about 44.49 dB; mean/max LPIPS are .02176/.10420. The embedding mean is about 22.4 seconds versus 2.3 seconds for v5. This is not a measured detector-speed comparison. F5 uses a VAE encoder, seven CLIP views and latent DCT; omitting diffusion inversion does not make their costs disappear. Full `both_match` is absent after T3, consistent with the fragile tier. Semantic survival must not be described as full-instance authentication.

Each method has three negative cells of 300 calls, all zero, sharing sources. The individual upper 95% bound is .994% per cell; the calls do not establish a 0.1% or 1e-6 population bound. T4/T5 zero-event upper bounds are 9.81%/10.50%, assuming independent pair units. See [recomputed planning statistics](planning-statistics.json) and its [arithmetic script](recompute-planning-statistics.py). These are uncertainty calculations from reviewed counts, not new runs.

## Literature changes the comparison and novelty claim

The [comparison matrix](literature-comparison.md) separates task, metric, operating point and side information. Nine inspected primary sources have [versioned cards and evidence](../literature/journal-upgrade-20261009/synthesis/findings.md). The root bibliography already contains their keys; no duplicate entries are added. This is a focused refresh, not an exhaustive novelty determination.

Comparators are **FreqMark**, **Watermark Anything**, and **ZoDiac**, alongside v5 and matched internal ablations. They offer post-hoc latent-frequency, neural/localized, and inversion-based reference points. The October 10 [feasibility inspection](baseline-feasibility.md) prioritizes WAM's explicitly named SA-1B MIT checkpoint for implementation; it differs from the paper's COCO checkpoint. Calibrate methods separately and compare under the same quality budget, attack identities and sample units. Show their native quality-performance curves too; a baseline unable to satisfy our strict quality limit is infeasible there, not secretly retuned on test data or assigned an invented detection score.

Do not rank F5's source-majority detection against published bit accuracy, AUC, or a different FPR. For example, ZoDiac's Table 3 reports detection .988 at FPR .062 and .938 at FPR .004. Neither is a matched competitor to a detector calibrated at .001. [ZoDiac v2](https://arxiv.org/html/2401.04247v2#S4).

Latent-frequency marking and inversion-free extraction have precedents in FreqMark, Latent Watermark and GROW. Semantic binding has precedents including SEAL. The contribution must therefore be an experimentally isolated improvement or a well-characterized limitation, not merely the use of latent features, two signatures, or no inversion. Generative methods belong in a separate optional arm; they cannot replace the existing-photo benchmark. [FreqMark](https://arxiv.org/html/2410.20824v1), [Latent Watermark](https://arxiv.org/html/2404.00230v3), [GROW](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html), [SEAL](https://arxiv.org/html/2503.12172v4).

## Thresholds and attack ranges for the next study

Separate detector calibration, attack intensity, admissibility and acceptance. A strength of .4 is an img2img parameter, not a 40% successful attack. The following values are prospective proposals, chosen before the next results; preserve all historical M2 settings.

| Item | Proposed primary setting | Secondary/sensitivity |
|---|---|---|
| Detector operating point | Nominal FPR .001 (0.1%), threshold selected using calibration negatives only | .01 and .0001, clearly separated; rare-event uncertainty reported |
| Clean marked quality | PSNR >35 dB, SSIM >.9, LPIPS <.1 on every evaluated image | Continuous distributions, worst cases and failure counts |
| T3 regeneration | VAE-only; strengths .05/.1/.2/.3/.4/.5/.6; seeds 0-2 | SD1.5 continuity, another backbone sharing a VAE, and independently trained VAE/backbone; controlled regeneration after the cheap tests |
| T3 admissibility | LPIPS <=.30 versus marked input **and** blinded human majority preserving entities, actions and scene identity | LPIPS <=.20; report PSNR/SSIM and independent semantic similarity continuously |
| T4 transfer | Patch area 1/64, 1/16, 1/4; alpha .25/.5/1; two fixed positions; K=18 | No-transfer sham and separately labelled residual-transfer diagnostic |
| T4 admissibility | LPIPS <=.20 versus recipient and blinded majority preserving recipient identity | .30 sensitivity; report actual donor delivery before binding |
| T5 collision | One independently selected semantic-nearest distinct instance, K=1 | K=10/100 search budgets, dissimilar controls, same/different owner |
| Attacker access | One claimed owner R=1, no detector feedback Q=0; fixed candidate budget K | R=10/100 roster and feedback-enabled attacks require separate endpoints/calibration |

Use three raters with blinded order for human admissibility. No missing human response counts as a pass. Human judgments remain pending until actually collected. The LPIPS caps are explicit engineering choices, not validated perceptual truths; report coverage and sensitivity rather than treating them as universal semantic thresholds. Do not use the detector's own CLIP to determine semantic eligibility. Equal strength across pipelines is not equal severity: pin checkpoints, effective timesteps, sampler, guidance, prompt policy and resolution, and compare performance versus achieved distortion. The fixed-FPR and quality-performance approach follows [WAVES v2](https://arxiv.org/html/2401.08573v2#S3), restricted here to the three thesis threats.

For every attack report admissibility coverage, joint admissible attack success over **all** attempts, and success conditional on admissibility. T3 success means loss of the declared checked-semantic endpoint; T4 success means false donor attribution; T5 success requires the precisely defined false-instance or false-owner claim. Also report all-source survival and paired comparisons on the common admissible subset. Retain all failed seeds, rejected outputs and denominators.

Report random-seed average and per-source any-attempt attack success separately. With K=3 seeds a source-majority endpoint is not a best-of-three defense. Across seven strengths K=21 per model for an any-attempt summary. For T4/T5, binomial units are independent disjoint donor/recipient or target/candidate clusters, with success defined as any allowed attempt. Reusing one target across many donors does not increase the independent sample size. Full details are in the [threshold design review](threshold-design-review.md).

## Scientific targets and sample-size decisions

| Claim | Proposed future evidence requirement |
|---|---|
| Reliable clean marking | Strict quality on every observed image; clean full-match lower one-sided 95% bound >=.95 |
| Low false-positive detection | Each declared primary negative cell has simultaneous one-sided upper bound <=.001 |
| Cross-model regeneration improvement | Checked source-majority point estimates >=90% at .2 and >=70% at .4; >=10 percentage-point improvement over the matched pixel ablation, with adjusted paired lower difference bound >0 |
| Effective content binding | At least 100 independent **delivered** pairs; >=10-point false-acceptance reduction versus disabled binding on identical signals, with adjusted lower difference bound >0 |
| Low T4/T5 attack success | Simultaneous upper bound <=1% for each of three prespecified attack cells at fixed K |

The T3 90%/70% targets are point-estimate milestones, not claims that the population rate exceeds them with 95% confidence. The 100-pair binding experiment tests a mechanism; it does not certify a rare error rate. No gate compensates for another through a weighted score.

For zero events in n independent units, an individual upper 95% bound is `1 - .05^(1/n)`. A below-1% bound needs 299 zero-error units for one cell, or 408 per cell for three simultaneous Bonferroni-adjusted cells. A below-.1% bound needs 2,995 or 4,093 respectively. Plan 10,000 calibration negatives and 5,000 fresh confirmation groups per target population, applying all three negative conditions. Zero/5,000 suffices for the three-cell .1% bound; any errors require the actual exact bound. Calibration at nominal .001 does not guarantee that confidence bound: choose a conservative development operating point, then report the confirmation result without retuning.

Plan at least 300 independent positive sources per declared domain for future confirmation, with paired power analysis from development effects before freezing the final count. Expand the multiplicity family or narrow the claims if adding domains/endpoints. Use exact paired tests/source-cluster intervals and Holm adjustment for a small prespecified family of primary comparisons. Secondary grids remain descriptive. Sample-size arithmetic is not a substitute for power analysis, diverse source sampling or independence.

## Revised sequence of work

These are ordered work packages, not promised calendar dates. Current original M1a qualification and stronger prospective article targets are distinct; passing the former does not silently pass the latter.

1. **Preserve the completed E3-S1 science.** B on all twelve development sources, C on the fixed SD1.5 .1/.2 seed identities, and D on residual/public transfer and collision geometry have passed. Reuse only unchanged controls with explicit references. Preserve failed construction, unavailable safety outputs, complete denominators and resource cost including payload supply. Use the frozen [full development protocol](e3-s1-full-development.md). If it fails, diagnose the measured failure before declaring a different method or budget; no silent retries or historic payload fallback.
2. **Package only after qualification.** Freeze supplier/writer/reader and all configuration, scientific scope, thresholds, data rule and primary comparisons. Use existing tests, existing runner rehearsals and one fresh independent review. Prepare an unexposed held-out inventory by IDs/hashes only. The [metadata-only availability memo](fresh-cohort-availability.md) identifies a conditional 300-image COCO remainder, not a validated rare-event cohort. The user reviews the concrete M1b package once before held-out execution. No new runner is needed.
3. **Perform approved confirmation and claims audit.** Count all admissions, failures, negatives and planned attacks; report raw and admissibility-filtered endpoints, paired source-level uncertainty and runtime. Do not tune on this result. The original M2 sources stay historical for E3-S1. Distinguish the alpha-only owner claim from cross-owner generalization; human verdicts stay missing until actually provided.
4. **Close the article-specific gaps.** Independently reserved development sources and an untouched model/seed panel are needed because current sources, both VAE models and the six DDIM channels have informed design. Match carrier/component ablations on payload, extraction and achieved distortion. Freeze total attempts before pursuing at least 100 delivered pairs; retain unsuccessful deliveries and report any shortfall. Define an enrollment-aware instance test only through a separate method decision. The all-alpha 66-pair geometry panel cannot become a false-owner or false-instance trial by renaming it.
5. **Establish external competitiveness at a common operating point.** The pinned WAM SA-1B MIT [matched T3 baseline](wam-t3/wam-t3-results.md) gives native exact message recovery 3/36 and 0/36 at .1/.2 versus historical F5 27/36 and 20/36. It is descriptive, with different payloads and no matched-FPR presence rule. Reproduce free pinned FreqMark/ZoDiac assets where feasible; otherwise disclose reproduction limits. Compare native and strict-quality frontiers, calibrated FPR, T3 quality-performance curves, relevant T4/T5 endpoints, total embedding/extraction time and memory. No state-of-the-art ranking from unmatched paper percentages.
6. **Write the bounded article.** Center the paper on a demonstrated mechanism or measured limit supported by independent data, complete ablations and failure accounting. Keep the noisy payload, public-access authorization limitation and non-identifiable reference claim explicit. Align unprotected chapters with measured scope; proposal, claim ledger and source plan remain unchanged. Venue/category/year verification and submission are later human decisions, not consequences of these numerical targets.

The initial finite readability round is closed, with failures preserved in [the improvement summary](improvement-summary.md); subsequent coded-carrier and E3 decisions are in the archived history and linked run reports. New rounds require a falsifiable hypothesis and finite configuration/resource budget before results. No scalar objective trades away quality, negative detection or T4/T5 constraints. SDXL is now a seen development transformation, and repeated seeds are clustered within a source. The standing 2026-10-13 state report remains due.

## What to borrow from autoresearch

The inspected [official repository](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117) is an agent-guided GPT-pretraining experiment, not a watermark research package. Borrow its short hypothesis/commit/measure/log cycle and frozen evaluator. Replace scalar improvement with hard quality/FPR constraints and a Pareto comparison; retain failed results; keep calibration and fresh confirmation outside the search loop. Its five-minute training counter excludes other runtime, and repeated validation queries remain adaptive development.

Do not install its language-model stack or add a new orchestration layer. The existing development command, assessors, `run.json` and dev log are sufficient. The [full code assessment](autoresearch-assessment.md) records the pinned revision, source archive, Windows limitations and license declaration caveat. No repository code was executed.

## Completion record

Discovery, source inspection, attack-range design, the autoresearch review, WAM descriptive reproduction and the supplied-payload E3 comparative assessment are complete. The S1 two-source supplier/callable screen is complete, with its technical failure and narrow unexecuted-stage completion retained. Full S1 qualification is complete and passes its bounded development assessment; M1b is underway. New confirmation, matched-FPR external ranking and article acceptance remain unfinished. All evidence is exploratory unless its own report explicitly identifies the historical approved confirmatory study. No human or official lifecycle verdict is fabricated.

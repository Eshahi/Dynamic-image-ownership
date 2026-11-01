# K07 — Quality budget and allocation

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — Main robust L2 radius in [0,1] coordinates is `10^(-PSNR/20)*sqrt(number_of_RGB_entries)`. Frozen r2 uses 52 dB and mask power zero. Each robust stage is rounded to RGB8; each fragile change is added equally to R/G/B and then rounded/clipped (`scripts/f5_latent_codec.py:164-172,186,208-215,231-250`).
- DERIVED — Even for a nonzero mask, the code projects the actual pixel delta, not an unconstrained mask-weighted norm. With the retained all-ones mask this distinction disappears. The 52 dB constraint applies before first rounding, relative to the source of that one solve. The 58 dB constraint applies relative to its later combined starting image. Neither is a final end-to-end PSNR guarantee.
- SOURCE — Fragile design MSE is `255^2/10^(47/10)` with a `1/12` rounding reserve; host rejection chooses an expected spread-spectrum cost using host power (`scripts/revised_watermark_v5.py:842-853`; `scripts/revised_watermark_v4.py:86,762-779`; profile `embedding.instance_psnr_db`). DERIVED — This is approximately 1.30 byte-squared before reserve, while the 52 dB robust budget is about .41 and the 58 dB refinement budget about .103. These are design budgets, not measured orthogonal residual energies. The actual host-change cost has a pattern/host cross term, and the final image has two fragile fitting stages, clipping, rounding, and cross terms between stages.
- JUDGMENT — The judge's roughly 60% fragile share is a useful hypothetical allocation, not an identified share of final distortion. A robust-only 2.2x amplitude gain is not an established feasible gain. DERIVED — Uniformly multiplying all chip projections by a positive constant leaves the detector score exactly unchanged (`scripts/revised_watermark_v5.py:1186-1199`); increasing only watermark signal relative to host/noise requires a channel model, and the foreign channel need not be linear. SOURCE — Phase A reports this nonlinearity for SDXL (`research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:74-83`).
- DERIVED — Quality/visibility adds no isolated recovery ceiling: all per-cell improvement ceilings are UNKNOWN without new residual/quality measurements. A global L2 budget is not a bound on maximum local artifact or human invisibility. The frozen spec's accepted historical image set and the transfer study's missing human ratings are different evidence populations (`research/f5-r2-spec.md:12,29-30`; `research/encoder-transfer-20261019/results.md:156`).

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E03: H1 carrier-band kill](../context/wp1-prior-evidence.md#e03-h1-carrier-geometry-the-tested-narrow-band-did-not-improve-regeneration) (inventory line 60) | Four-source panel baseline 4–32 vs 8–28 at .4:13/18 vs 13/17; .5:10/18 vs 9/18; .6:2/17 vs 1/16. Mean LPIPS .0172→.0107. | Tested narrower band did not improve T3; other bands, geometry and foreign channels remain untested. |
| [E04: H3 mask and budget kill](../context/wp1-prior-evidence.md#e04-h3-texture-mask-sweep-quality-savings-did-not-preserve-equal-t3) (inventory line 68) | 12-source .4+.5: unmasked 52 dB 86/116; mask .5 at 52/50/48 dB 61/117,78/117,77/117. Closest comparable setting saved about 4% LPIPS, below 15% target. | Kills those mask/budget packages, not all allocation. Repairing carrier losses exposed more binding losses. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
| [E08: F4 chroma](../context/wp1-prior-evidence.md#e08-f4-chroma-better-raw-channel-response-did-not-yield-a-clean-equal-quality-winner) (inventory line 128) | Selected r4 F4/v5 success numerators .1/.2/.4=25/25,13/17,2/2. Stronger post-hoc r5=27/26,23/17,6/2 with LPIPS mean/max.041/.083; T4 delivery20/20 but full attribution0/20. | Equal-perceptual-quality winner not established; post-hoc r5 lacks prospective selection/human acceptance. Chroma not categorically ruled out. |
| [E09: Original F5 M2 — FROZEN REPORT](../context/wp1-prior-evidence.md#e09-original-f5-m2-frozen-held-out-evidence-not-a-tuning-pool) (inventory line 138) | Held-out clean strict quality298/300; .2/.4 legacy semantic source30/30,21/30, checked-only27/30,17/30; full both_match0/90 per strength. | Frozen claim context only. Legacy semantic/full endpoints cannot be substituted for C/J; no retuning from these numbers. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |
| [E17: Coarse lattice and morphology](../context/wp1-prior-evidence.md#e17-coarse-lattice-saved-channel-diagnostics-and-a-candidate-not-measured-t3-of-the-new-mark) (inventory line 268) | Existing-mark F5 luma-band gain 1.76/.35/.60 on SD1.5/SDXL/K3 .2. Candidate patch384 T4 chroma2/300,luma2/150; real candidate T3 unrun; reported flat-region blotches. | Slopes/capacity proxies are not achievable bits or new-mark survival; secret-key side information differs. Candidate has no priority privilege. |

### Current saved-development accounting and per-cell ceilings

DERIVED: Saved endpoints do not isolate this physical intervention. Its recovery ceiling is UNKNOWN in every observed cell; 60 minus current C is only the arithmetic maximum headroom. Where C=60 there is no positive C count headroom, although J, quality and safety can still differ.

DERIVED: All ceilings are source-level potential increments relative to frozen C/J, not sums of per-call failures. Shared ceilings must not be added across components. Missing calls remain failures in baseline C/J. Every unconstrained new design and every joint strict-quality/T4/T5-safe recovery ceiling is UNKNOWN; current scores contain no new-method negatives or human visual verdict. Protocol: [accounting specification](../analysis/WP1-ACCOUNTING-SPEC.md); endpoint source: scripts/m1b_e3_s1_analysis.py:70–84.

| Study/cell | C /60 | J /60 | Restricted C ceiling (gain) | Restricted J ceiling (gain) | Missing-C upper | Trivial C gain cap |
|---|---:|---:|---|---|---:|---:|
| phase-a / R0-0.1 | 60 | 41 | UNKNOWN | UNKNOWN | 60 | 0 |
| phase-a / R0-0.2 | 57 | 38 | UNKNOWN | UNKNOWN | 58 | 3 |
| phase-a / R0-0.4 | 39 | 14 | UNKNOWN | UNKNOWN | 40 | 21 |
| phase-a / R1-0.1 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| phase-a / R1-0.2 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| phase-a / R1-0.4 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| phase-a / ctrlB-codec | 60 | 47 | UNKNOWN | UNKNOWN | 60 | 0 |
| stage2-union / D1 | 55 | 31 | UNKNOWN | UNKNOWN | 55 | 5 |
| stage2-union / D3 | 55 | 35 | UNKNOWN | UNKNOWN | 55 | 5 |
| stage2-union / R0-0.1 | 60 | 41 | UNKNOWN | UNKNOWN | 60 | 0 |
| stage2-union / R0-0.2 | 57 | 38 | UNKNOWN | UNKNOWN | 58 | 3 |
| stage2-union / R0-0.4 | 39 | 14 | UNKNOWN | UNKNOWN | 40 | 21 |
| stage2-union / R1-0.1 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R1-0.2 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R1-0.4 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R1-mode-0.2 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R1-rinse-0.1 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R1-smooth-0.2 | 0 | 0 | UNKNOWN | UNKNOWN | 0 | 60 |
| stage2-union / R3-0.2 | 5 | 0 | UNKNOWN | UNKNOWN | 5 | 55 |
| stage2-union / X1 | 60 | 46 | UNKNOWN | UNKNOWN | 60 | 0 |
| stage2-union / X2 | 60 | 41 | UNKNOWN | UNKNOWN | 60 | 0 |
| stage2-union / clean | 60 | 52 | UNKNOWN | UNKNOWN | 60 | 0 |

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K07. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K07 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

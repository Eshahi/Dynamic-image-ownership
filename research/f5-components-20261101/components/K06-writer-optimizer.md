# K06 — Writer optimizer and objective

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — The target q/chip pattern is fixed before writing. Main optimization uses squared hinge `mean(relu(4 - signed_chip_margin)^2)`, normalized gradient descent from zero perturbation, and step size `.2*budget` for the first half then `.05*budget` for the second half. It projects actual RGB delta to a global L2 ball after clipping to [0,1] (`scripts/f5_latent_codec.py:158-161,175-215,227`).
- DERIVED — The objective directly targets unnormalized signed chip margins. It does not optimize normalized decoded correlation, soft content binding, exact q recovery, total two-tier quality, negative controls, or foreign-regeneration output. A good surrogate optimum need not be a good C/J optimum. There is no early stopping, best-iterate selection, multistart, or learned optimizer in this implementation.
- SOURCE — Refinement restarts a new optimization centered on the already rounded combined image, using `max(psnr+6,50)` and `max(steps//3,20)`; frozen r2 therefore adds 50 steps at 58 dB (`scripts/f5_latent_codec.py:246-250`). DERIVED — The total is 200 gradients, with a separate halfway switch inside each solve. The reported `steps=150` field is the main-run parameter, not total work.
- SOURCE — The inspected Phase A report supplies a historical 119 s/source write anchor (`research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:124`). DERIVED — This cannot identify per-step, CLIP, fragile, or refinement latency. Optimization-limited loss and additional-step recovery ceiling are UNKNOWN without saved convergence/intervention evidence; the presence of 150 steps does not demonstrate convergence.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E04: H3 mask and budget kill](../context/wp1-prior-evidence.md#e04-h3-texture-mask-sweep-quality-savings-did-not-preserve-equal-t3) (inventory line 68) | 12-source .4+.5: unmasked 52 dB 86/116; mask .5 at 52/50/48 dB 61/117,78/117,77/117. Closest comparable setting saved about 4% LPIPS, below 15% target. | Kills those mask/budget packages, not all allocation. Repairing carrier losses exposed more binding losses. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |

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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K06. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K06 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

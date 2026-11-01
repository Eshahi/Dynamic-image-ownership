# K09 — Reader statistic and thresholds

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — For 320-chip vector p, recomputation scores `p dot w(q_now)/||p||2`; decoding maximizes the same normalized score independently in each segment. Zero energy yields zero scores; ties retain the recomputed bit. Read is decoded score at least 8.259326826136963, while found is read OR recomputed score at least 4.982033056390042 for roster one (`scripts/revised_watermark_v5.py:1178-1199,1244-1278`; `configs/f5-r2.json:38`).
- DERIVED — Scores are not probabilities and are bounded above in magnitude by sqrt(320). Decoded score is always at least recomputed score, but the two pass events have different cutoffs and are not nested. The generic `score` and `threshold` switch to the decoded branch only after it passes; a generic positive margin is not necessarily a C success (`scripts/revised_watermark_v5.py:1260-1272`).
- SOURCE — The code inverts a Bentkus-Dzindzalieta-attributed sign-sum bound with 200 bisection steps, multiplying by roster count for recomputation and `2^32 * roster_count` for decoding. It then infers a decoding error rate by inverting a Gaussian two-option segment-score model and corrects raw Hamming distance as `(d-32e)/(1-2e)`, clipped and rounded to six decimals (`scripts/revised_watermark_v5.py:1149-1175,1202-1257`). DERIVED — e is not a measured bit error rate; option correlation, unequal segment energies, and non-Gaussian/interdependent channel noise are not represented by that model.
- JUDGMENT — Keep K9, but distinguish three subcomponents: statistic, multiplicity/null calibration, and decoding-error model. Their assumptions differ. A changed threshold can move tests without changing carrier energy; old endpoint loss classes cannot establish its safe T4/T5 operating point. See the conditional-null section of the linked code-structure audit and the ceiling table below.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E03: H1 carrier-band kill](../context/wp1-prior-evidence.md#e03-h1-carrier-geometry-the-tested-narrow-band-did-not-improve-regeneration) (inventory line 60) | Four-source panel baseline 4–32 vs 8–28 at .4:13/18 vs 13/17; .5:10/18 vs 9/18; .6:2/17 vs 1/16. Mean LPIPS .0172→.0107. | Tested narrower band did not improve T3; other bands, geometry and foreign channels remain untested. |
| [E05: H4 threshold kill](../context/wp1-prior-evidence.md#e05-h4-threshold-relaxation-local-rescues-cost-natural-image-specificity) (inventory line 87) | Soft/hard .4=49/58 vs 42/58; radius6/7/8/10 admitted4/10/21/62 of132 ordered semantic cross-source pairs. Radius7 rescued4/6 .4 binding failures. | Equal-specificity relaxation failed. Semantic proximity is not measured joint T5 attribution; other calibrated rules remain open. |
| [E06: Noiseless binding/sketch diagnostic](../context/wp1-prior-evidence.md#e06-noiseless-semantic-binding-ceilings-informative-but-conditional) (inventory line 95) | At4/132 false-pair budget, true feature .4/.5/.6=55/44/14 versus production 49/37/10; random256-bit ranges54–55/44–48/12–15 on173 saved identities. | Shows representation/sketch headroom conditional on transport and finite operating point; not a realizable watermark or universal upper bound. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
| [E08: F4 chroma](../context/wp1-prior-evidence.md#e08-f4-chroma-better-raw-channel-response-did-not-yield-a-clean-equal-quality-winner) (inventory line 128) | Selected r4 F4/v5 success numerators .1/.2/.4=25/25,13/17,2/2. Stronger post-hoc r5=27/26,23/17,6/2 with LPIPS mean/max.041/.083; T4 delivery20/20 but full attribution0/20. | Equal-perceptual-quality winner not established; post-hoc r5 lacks prospective selection/human acceptance. Chroma not categorically ruled out. |
| [E09: Original F5 M2 — FROZEN REPORT](../context/wp1-prior-evidence.md#e09-original-f5-m2-frozen-held-out-evidence-not-a-tuning-pool) (inventory line 138) | Held-out clean strict quality298/300; .2/.4 legacy semantic source30/30,21/30, checked-only27/30,17/30; full both_match0/90 per strength. | Frozen claim context only. Legacy semantic/full endpoints cannot be substituted for C/J; no retuning from these numbers. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E12: Registry with trusted records](../context/wp1-prior-evidence.md#e12-registry-additional-side-information-helps-a-different-task-with-hard-near-negative-limits) (inventory line 190) | Fresh 40-source F_R .2 SD1.5/SD2.1=30/40,32/40 below 36/40; fingerprint-only accepted4/13 near-duplicate pairs, registry 0/13 on unmarked no-pointer pairs. Later frozen held-out near-lookalikes 3/45 accepted. | Additional side information changes task; negative result not rescued by earlier screening or dependent millions of unrelated comparisons. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |

### Current saved-development accounting and per-cell ceilings

DERIVED: The restricted envelope converts only calls already semantic-found into successful reads/content checks. Its C ceiling is current semantic-found majorities; this is not a predicted ECC/statistic gain or a safe threshold. A new code/statistic can cross the old found boundary, so its unrestricted ceiling is UNKNOWN. J under this envelope is UNKNOWN because finding a pattern does not identify original q.

DERIVED: All ceilings are source-level potential increments relative to frozen C/J, not sums of per-call failures. Shared ceilings must not be added across components. Missing calls remain failures in baseline C/J. Every unconstrained new design and every joint strict-quality/T4/T5-safe recovery ceiling is UNKNOWN; current scores contain no new-method negatives or human visual verdict. Protocol: [accounting specification](../analysis/WP1-ACCOUNTING-SPEC.md); endpoint source: scripts/m1b_e3_s1_analysis.py:70–84.

| Study/cell | C /60 | J /60 | Restricted C ceiling (gain) | Restricted J ceiling (gain) | Missing-C upper | Trivial C gain cap |
|---|---:|---:|---|---|---:|---:|
| phase-a / R0-0.1 | 60 | 41 | 60 (+0) | UNKNOWN | 60 | 0 |
| phase-a / R0-0.2 | 57 | 38 | 60 (+3) | UNKNOWN | 58 | 3 |
| phase-a / R0-0.4 | 39 | 14 | 58 (+19) | UNKNOWN | 40 | 21 |
| phase-a / R1-0.1 | 0 | 0 | 7 (+7) | UNKNOWN | 0 | 60 |
| phase-a / R1-0.2 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| phase-a / R1-0.4 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| phase-a / ctrlB-codec | 60 | 47 | 60 (+0) | UNKNOWN | 60 | 0 |
| stage2-union / D1 | 55 | 31 | 60 (+5) | UNKNOWN | 55 | 5 |
| stage2-union / D3 | 55 | 35 | 60 (+5) | UNKNOWN | 55 | 5 |
| stage2-union / R0-0.1 | 60 | 41 | 60 (+0) | UNKNOWN | 60 | 0 |
| stage2-union / R0-0.2 | 57 | 38 | 59 (+2) | UNKNOWN | 58 | 3 |
| stage2-union / R0-0.4 | 39 | 14 | 58 (+19) | UNKNOWN | 40 | 21 |
| stage2-union / R1-0.1 | 0 | 0 | 7 (+7) | UNKNOWN | 0 | 60 |
| stage2-union / R1-0.2 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| stage2-union / R1-0.4 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| stage2-union / R1-mode-0.2 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| stage2-union / R1-rinse-0.1 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| stage2-union / R1-smooth-0.2 | 0 | 0 | 0 (+0) | UNKNOWN | 0 | 60 |
| stage2-union / R3-0.2 | 5 | 0 | 23 (+18) | UNKNOWN | 5 | 55 |
| stage2-union / X1 | 60 | 46 | 60 (+0) | UNKNOWN | 60 | 0 |
| stage2-union / X2 | 60 | 41 | 60 (+0) | UNKNOWN | 60 | 0 |
| stage2-union / clean | 60 | 52 | 60 (+0) | UNKNOWN | 60 | 0 |

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K09. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K09 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

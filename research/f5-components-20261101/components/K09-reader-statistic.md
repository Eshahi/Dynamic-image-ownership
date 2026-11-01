# K09 — Reader statistic and thresholds

SOURCE/JUDGMENT: Sections A/B preserve WP1 structure and historical evidence; C-F contain literature, options, tests and the current proposed verdict. Gate-2 corrections and fixed results are in [GATE2-SYNTHESIS](../GATE2-SYNTHESIS.md). Claude remains the judge.

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

## C. Literature since 2024

SOURCE: [Inspected K09 cards, venue evidence and exact queries](../literature/intake/K09.md): five Q1 statistical papers and three TOP watermark papers, 33 conservatively substantive queries plus follow-ups, including ten ruling additions. The statistical cards supply null, dependence and selection tools; none is watermark efficacy evidence.

SOURCE: Wang's admissible e-merging theorem (Biometrika 2025, Theorem 1) does not turn uncalibrated correlations into valid e-values. Safe testing (JRSSB 2024, Propositions 1–2) requires conditional null validity; two channels on one image are not independent sequential samples. Jin and Ren's focal coverage (JRSSB 2025) handles an explicitly specified selection mechanism under exchangeability, not public adaptive watermark forgery. Gaussian Shading, WAM and PRC (CVPR 2024/ICLR 2025) expose different secret-key, distribution and calibration assumptions. PRC's random-KeyGen theorem cannot be read as fixed-public-key security against an image chosen after seeing that key.

DERIVED/JUDGMENT: Exact constrained decoding is computationally cheap because segment scores separate, but its radius-dependent multiplicity and content interpretation must be declared. Combining tier tests requires the budget of the complete rejection event. Frozen C uses decoded semantic reading; O adds two instance routes, so O's conditional union is three tests, not automatically one or four. O_U and the stronger q-enumerated envelope are distinct exploratory endpoints. Lower thresholds, heavy-tailed fusion, or e-values cannot manufacture an adaptive null from the same public keys and finite development negatives. Prioritize the exact-ball test and explicit union accounting before any learned fusion or threshold tuning.

## D. Improvement options

SOURCE/JUDGMENT: Gate-2 R2 withdraws the old 32/12 SDXL recomputed-inclusive values as gains. O1/O2 planning ranges below are historical, unvalidated option records, superseded by the fixed failed-reader results in section E and [GATE2-SYNTHESIS](../GATE2-SYNTHESIS.md). They are not current performance forecasts.
JUDGMENT: [OPTIONS](../OPTIONS.md) applies. Conditional stochastic null bounds do not become public-adaptive security.

### O1. Exact Hamming-ball maximizer at r=3
SOURCE/DERIVED: The segment-separable code in section A and the corrected Gate-1 R4 permit exact top-positive-gain decoding. Search size is sum(C(32,j),j=0..3), not two candidates. Targets found-but-unread and subthreshold constrained words; restricted current-found caps are+19 SD1.5 .4,+0 SDXL .2,+18 K3, but a changed test can exceed that envelope.
JUDGMENT: Planning extra new-endpoint successes/60 over the two-candidate bound:0..+8 SD1.5 .4,0..+5 SDXL .2,0..+8 K3; frozen C/J unchanged. Small 32-element sort, same reader projections and q side information, no writer/quality change. Content tolerance can accept T4/T5 collisions, so a detection gain alone is inadequate. Simpler alternative corrected two-candidate bound.
JUDGMENT: T2 fixes r3 and kills if no EVALUATE extra acceptance or any new negative; score replication and synthetic exactness are required. No radius selection after outcomes. No closed line reopened.

### O2. Familywise-budgeted union
SOURCE: Safe Testing and e-value merging cards clarify assumptions; Gaussian Shading and WAM empirical nulls show why nominal formulas and observed zeros differ. Use the T1 O_U budget with a conservative all-q O_Q sensitivity. Targets evidence discarded by C; current union opportunities and ceilings in K08 O1, not additive to O1 here.
JUDGMENT: New endpoint gains/60 SDXL .1 0..+32,.2 0..+12,.4 0..+3,K3 0..+11, C/J unchanged; all-q enumeration can erase much of the apparent gain. Negligible fusion arithmetic, unchanged writer/quality, existing detector side information. T4/T5 and public-key adaptivity remain open. Simpler alternative report separate tests without an acceptance union.
JUDGMENT: T1 and existing negative panels are decisive available checks. Kill on any new evaluated negative or lost SD1.5 .1/.2 C source, and never choose O_U versus O_Q by better outcomes. Judge must rule on q-selection assumptions. No closed line reopened.

### O3. Calibrated evidence averaging with explicit nulls
SOURCE: Wang Biometrika2025 shows valid e-values may be averaged under arbitrary dependence; it does not make a correlation score or 1/p an e-value. Construct per-tier valid evidence only with an explicit null/key-randomness model, then fixed weights; no empirical EVALUATE fitting.
JUDGMENT: New endpoint gain0..+10/60 SDXL .2 and0..+10 K3 is only a planning range, unrestricted ceiling UNKNOWN. No quality/writer change; calibration data and reference null distributions are additional side information/cost. Fixed-public adaptive T4/T5 is not covered. Simpler alternative O2 Bonferroni union.
JUDGMENT: Cheapest test is the null-assumption audit in T1: without independent valid per-tier e-values, the option is blocked before a performance test. Kill any purported bound based on 1/p or data-selected weights. A future fresh development calibration panel and separate safety test are required; no current sample is large enough to empirically certify1e-6. No closed line reopened.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: O1 exactr3 is algebraically validated by880 exhaustive checks per batch, but F5 has0 extra EVALUATE marked calls/91 and two extra negative wrong-content T5 comparisons; v5 has1/92 extra call,0 extra source-cells and one new T4 negative. Both are killed for promotion under the fixed rule.1100 matched historical scores pass tolerance;312 old-panel calls have no matched reference, not a pass.
MEASURED/DERIVED: O2's O<=3e-6 and O_U<=.75e-6 are conditional union bounds, not public-adaptive security. O_U's new saved F5 T4 accept kills promotion despite zero C0/wrong events. O_Q is sensitivity, not a chosen rescue. O3 has no valid calibrated per-tier e-values; T1 null audit blocks performance claims. No relaxed threshold or learned fusion was selected.

### Gate-2 option O4: fixed decoded-word reader B

SOURCE: R5 fixes alpha/2, radius9 multiplicity, corrected hard distance<=6, exact computed score threshold7.7791330802 and frozen semantic veto. Code/kill rules committed dde7280 before EVALUATE. No recomputed route, no retuning. This adds one judge-required option to the original three.

MEASURED: G2-A gains19/120 foreign EVALUATE source-cells but loses3 distinct SD1.5 .2 sources repeated in both studies; scores pass while hard binding fails frozen soft-compatible calls. G2-B adds2 strict-quality B-not-C transfers/480 from one pair. Both independently KILL promotion. G2-A has no new saved negative/old-T4/reference-assisted T5 event. All22study/cells and both methods remain in raw tables. [Synthesis and locators](../GATE2-SYNTHESIS.md).

DERIVED/JUDGMENT: Conditional-q is primary under domain-separated PRF honest-null assumptions; O_Q is sensitivity, not a requirement selected by outcomes. Neither bound applies to same-owner transplants or adaptive public-key image choice. B hard binding changes F5's frozen soft statistic, contrary to a literal reading of R2's unchanged-binding phrase. The rule was run as written; no soft rescue follows. Five counted K09 journals are statistical foundations only; no Q1 watermark-reader journal was read.

## F. Proposed verdict

JUDGMENT: PROPOSED KEEP, as Gate-2 R5 requires when B dies. Confidence: High for refusing promotion of these tested readers, not for optimality of the retained statistic. Exact r3, O/O_U and fixed B fail their predeclared rules. B's larger residual-transfer failure is independent of its hard-versus-soft SD1.5 regression. No rescue or replacement is selected.

JUDGMENT: A later explicitly authorized, fixed-null reader on fresh disjoint development would need safe T3/T4/T5 gains and no retained low-strength regression. This research run neither designs nor tests another B variant. See [VERDICTS](../VERDICTS.md), [synthesis](../GATE2-SYNTHESIS.md), and [two unchanged-reader designs](../CANDIDATE-DESIGNS.md).

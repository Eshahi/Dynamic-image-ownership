# K03 — Payload and channel code

SOURCE/JUDGMENT: Sections A/B preserve WP1 structure and historical evidence; C-F contain literature, options, tests and the current proposed verdict. Gate-2 corrections and fixed results are in [GATE2-SYNTHESIS](../GATE2-SYNTHESIS.md). Claude remains the judge.

## A. Structure

- SOURCE — Each semantic bit selects one of two independently generated ten-chip sign patterns in its segment. Thirty-two nonoverlapping segments form a 320-chip semantic pattern. The instance table has four ten-chip patterns per segment, selected jointly by q-bit and h-bit (`scripts/revised_watermark_v5.py:338-380`).
- DERIVED — “Repetition only” is imprecise: this is a per-bit binary random codebook/spreading construction, not ten identical copies of a bit or necessarily an antipodal binary code. There is no parity or error correction across the 32 message segments. Distinct choices can have variable Hamming distance, and identical short option patterns are not excluded by generation. The decoded maximizer is separable across segments, so the `2^32` multiplicity is statistical search size, not exponential computational cost (`scripts/revised_watermark_v5.py:1178-1199`).
- SOURCE — q is content-derived, not an arbitrary 32-bit owner identifier; OwnerID conditions both carrier layout and code tables. h is a separate content descriptor. The native reader receives no original q/h (`scripts/f5_latent_codec.py:265-304`; `scripts/encoder_transfer_runtime.py:172-180`). DERIVED — “32 payload bits” is not a certified capacity for identifying 2^32 owners or instances.
- DERIVED — Coding adds small table/projection arithmetic and no separate pixel write; it determines all 320 writer targets and exact-decoding reliability. A changed codebook/ECC normally requires new marks and thresholds, so its T3 recovery ceiling is UNKNOWN from the old endpoint table. The found-but-not-read pool is a target for investigation, not a bound on every possible coding improvement.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E06: Noiseless binding/sketch diagnostic](../context/wp1-prior-evidence.md#e06-noiseless-semantic-binding-ceilings-informative-but-conditional) (inventory line 95) | At4/132 false-pair budget, true feature .4/.5/.6=55/44/14 versus production 49/37/10; random256-bit ranges54–55/44–48/12–15 on173 saved identities. | Shows representation/sketch headroom conditional on transport and finite operating point; not a realizable watermark or universal upper bound. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K03. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K03 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024
SOURCE: [K03 full-text intake](../literature/intake/K03.md), cards and exact queries. The conservative count is 0 Q1J + 2 TOP, with journal and third-TOP access exhaustion; incomplete raster tables and the unavailable TrustMark final supplement are not full inspection. PRC image watermarks (ICLR 2025, methods and security statements) supply global error correction under a keyed latent generator, not a theorem for F5's fixed public codebook. RingID (ECCV 2024, identification/channel ablations) shows that adding channels can reduce identification accuracy. Neither paper isolates a 320-chip foreign-regeneration channel at F5's strict quality.
DERIVED: The intake's generic warning about pattern-dependent normalization does not block this exact decoder: the inspected F5/v5 projection norm is common to all words on a given image. Sorting positive segment gains is therefore exact here. It would cease to be exact if a new code introduced a word-dependent denominator or coupled constraints. CoPaD-Mark and the Evsutin paper remain partial leads, not counted cards; a derived four-symbol subcode is not the full paper's claimed correction capability.

## D. Improvement options
JUDGMENT: Forecasts and the mandatory quality/visibility protocol in [OPTIONS](../OPTIONS.md) apply. These are proposals, not permissions.

### O1. Antipodal ten-chip segment code
SOURCE/DERIVED: Replace each random pair by opposite signs, preserving 32 segments and 320 chips; motivated by the distance problem in section A and the coding contrasts in the K03 intake. Targets ambiguous/incorrect transport in SD1.5 .4 and foreign cells. Under unchanged found events the C gain caps are +19 in SD1.5 .4, +0 in SDXL .2, +18 in K3 .2; physically rewritten gains are UNKNOWN.
JUDGMENT: Planning delta C/60: SD1.5 .4 -5..+10, SDXL .2 0..+5, K3 .2 -5..+10, because greater option distance can help decoding but removes codebook flexibility and cannot create surviving signal. Reader cost remains linear; new writer targets can change all quality and T4/T5 behavior. No new side information. All-image quality, fixed flat-region diagnostics and human MISSING rule apply. Strongest simpler alternative: exact-ball decoding on the current marks.
JUDGMENT: Cheapest test T0 audits minimum option distance; T2 checks recoverable score ambiguity. Prewritten T0 kill rejects a one-chip correction guarantee at distance<3. A server rewrite is killed by no EVALUATE C/J gain at equal final quality or any new T4/T5 acceptance. No closed line reopened; do not present this as an E3 micro-variant.

### O2. Global redundancy at a fixed 320-chip budget
SOURCE: PRC image card and RingID channel ablations motivate parity across segments, not a literal PRC transplant. Test a declared short global code only after a new code/reader is specified; candidate payload is the same q, not a new descriptor. Loss target and conditional caps as O1; unrestricted ceiling UNKNOWN.
JUDGMENT: Delta C/60 SD1.5 .4 0..+10, SDXL .2 0..+5, K3 .2 -5..+10. More redundancy can reduce per-bit energy and thus lose more transport than it repairs, as r3-256 did. Reader decoding and writer optimization increase by unknown measured amounts; fixed public keys remain forgeable, and T4/T5 are not inherited. No extra reference, but the code must be public and thresholds recomputed. Flat-region/all-image checks required. Simpler alternative O1.
JUDGMENT: T0/T2 supply the cheapest current-channel diagnostics, not a replay estimate of new ECC efficacy. Kill the new-code server pilot if the predeclared C/J selector does not beat the same-chip baseline or any strict-quality/T4/T5 gate fails. Designing an E3 variant would be REOPENS-CLOSED-LINE and is not authorized; this generic F5-code option is held pending judge scope ruling.

### O3. Split redundant semantic evidence across the two carriers
SOURCE: RingID's negative channel-count ablation and Gate-1 N1 support a cautious diversity experiment, not guaranteed coding gain. Duplicate protected semantic information in latent and luma carriers rather than counting h as semantic identity. Targets SDXL/K3 no-read losses; all physical caps UNKNOWN.
JUDGMENT: Delta C/60 SDXL .1/.2 0..+15, .4 0..+5, K3 .2 -5..+15; SD1.5 .2 -5..+3. These broad planning ranges reflect useful second-tier transport but uncertain semantic payload, capacity and interference. Changing h allocation can destroy instance binding; reader tests need a joint budget, writer cost/quality can rise. No new secret or reference. Flat-region and all-image checks mandatory. Simpler alternative: keep both payloads and expose a separately named O_U endpoint.
JUDGMENT: T1/T3/T4 test prerequisites; Q-STAGE must measure interference first. Kill if second-carrier benefit vanishes under the complete null budget, T4/T5 fails, or a matched-quality rewrite loses SD1.5 low-strength success. Any new instance descriptor is REOPENS-CLOSED-LINE; merely duplicating q is not permission to reopen one.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: T0 finds minimum within-segment option distance2, including six of64 pairs, so a guaranteed one-chip correction claim is false. T2 finds no extra F5 Stage2 EVALUATE radius3 acceptance beyond the lower bound (0/91 calls); v5 gains1/92 calls but no source-cells and introduces a T4 negative. Reference-assisted T5 adds two F5 negative comparisons. These disfavor a reader-only ambiguity rescue, not new antipodal/ECC marks.
JUDGMENT: O1/O2 require freshly written targets and remain physically UNKNOWN; the fixed320-chip budget must account for transport/quality, not only code distance. O3 is constrained by T1/T3 complementarity but cannot inherit the unsafe O_U union. Duplicating semantic payload needs an explicit h/instance-binding tradeoff; no such rewrite was executed.

## F. Proposed verdict

JUDGMENT: PROPOSED UNKNOWN. Confidence: Medium. Distance2 refutes one-chip guarantee, but exact-ball negatives do not measure a new code's transport.

JUDGMENT: Evidence that would change this verdict: Fixed320-chip antipodal/parity comparison with equal final quality and real T4/T5. This is a proposal to Claude, not approval to replace the method or run a writer. The [joint verdict table](../VERDICTS.md), [interactions](../INTERACTIONS.md), [two integrated designs](../CANDIDATE-DESIGNS.md) and [server queue](../SERVER-QUEUE.md) state the combined assumptions and scope.

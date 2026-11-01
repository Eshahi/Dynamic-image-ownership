# K04 — Carrier space and normalization

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — The writer/reader use the scaled SD1.5 posterior-mode tensor, 4 by 64 by 64 for canonical 512-square RGB. Per-channel orthonormal DCT slots satisfy `4 <= hypot(u,v) < 32` (upper endpoint excluded), with public weight `radius/4`. The frozen configuration records 3,272 slots (`scripts/f5_latent_codec.py:44-66,101-107`; `configs/f5-r2.json:9-18`).
- SOURCE — Slot assignment is a pseudorandom permutation followed by modulo-320 assignment, with keyed signs; F5 recomputes each chip's normalization as the square root of the sum of its assigned squared frequency weights (`scripts/revised_watermark_v4.py:679-692`; `scripts/f5_latent_codec.py:72-85`). DERIVED — At 3,272 slots, chips receive 10 or 11 slots. The denominator is key/layout dependent through grouping, even though each frequency weight is public and key independent. The DCT projection norm and subsequent full-chip energy normalization are separate operations.
- DERIVED — A 64-square DCT is hard-coded; the low-level generic image check only enforces a minimum side and finite luminance, not correct latent shape (`scripts/revised_watermark_v4.py:197-209`; `scripts/f5_latent_codec.py:82-85`). The production adapter supplies the missing shape contract by requiring saved RGB8 inputs to be 512-square (`scripts/encoder_transfer_runtime.py:111-117`). No spatial synchronization is implemented by this latent carrier.
- DERIVED — Cost includes one latent DCT at read time and the DCT/chip graph on every robust gradient step; distortion is incurred through the RGB writer, not by substituting the VAE reconstruction. Its independent improvement ceiling is UNKNOWN: final scores mix carrier geometry, writer optimization, budget, host interference, encoder response, and regeneration. Public weights alone do not establish the null theorem; see the conditional table-sign argument in the linked code-structure audit.

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
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K04. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K04 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024

SOURCE: [Inspected K04 cards and exact search audit](../literature/intake/K04.md). Two Q1J and three TOP cards qualify provisionally, with author-version caveats; the five-journal floor is genuinely exhausted after 55 logged queries, including eleven ruling-specific additions. The centralized floor ledger controls final counts.

SOURCE: GaussMarker (ICML 2025, §4 and Appendix D) demonstrates complementary spatial/frequency noise carriers under its tested pipeline, but its pixel-diffusion results and trained fusion do not establish independent latent-encoder transfer or strict all-image quality. Fourier Integrity (ICCV 2025, §3.2/§5 and supplement) repairs Hermitian symmetry for a real Fourier representation; F5 already uses a real DCT, so copying that repair is not a component improvement. MarkPlugger (TMM 2025, §IV/V) and Latent Watermark (TMM 2025, Tables 2–4) support channel/quality allocation mechanisms, with generator-deployment and version limits. ZoDiac (NeurIPS 2024, Tables 1–3) pays for inversion and has mean clean PSNR 29.41 dB on COCO, below this project's strict 35 dB floor.

JUDGMENT: No inspected paper solves the project's joint foreign-encoder T3, strict per-image quality and content-bound T4/T5 problem. Investigate a complementary carrier pair and family-by-scale behavior jointly with K05/K08; do not infer improvement from moving all energy into the nominally robust latent band. N1 identifies operational complementarity, while N2 prevents attributing it solely to encoder family. A new carrier's physical ceiling remains UNKNOWN; the conditional ceilings in B are not forecasts. The full card locators distinguish measured paper results from transferable mechanisms and missing tests.

## D. Improvement options — PROPOSED

JUDGMENT: Forecast and visibility conventions are in [OPTIONS](../OPTIONS.md). These are planning ranges, not measured gains or confidence bounds. Every writer change has UNKNOWN physical ceiling and must preserve T4/T5; B's conditional ceilings are nonadditive.

### K04-O1 — Resolve scale before choosing a carrier

SOURCE/JUDGMENT: Use the current latent and pixel carriers unchanged, compare their original-pattern response under the saved family/control cells (T3), then cross family with working resolution (Q-RES). N2 and the GaussMarker/RingID limits motivate this diagnosis. Targets the apparent no-found loss on SDXL and the conflicting second-tier survival. Predicted change to existing C/J is exactly 0–0/60 because this is an experiment, not a new mark; its value is rejecting an incorrect carrier attribution. Physical recovery remains UNKNOWN.

JUDGMENT: No new distortion, key or reader side information; CPU reader cost is measured in T3, and Q-RES needs regeneration only. Flat-region checks are unnecessary for unchanged marks. Stronger alternative would be an untested new carrier; the simpler alternative is merely renaming failure, which cannot resolve N2. Cheapest decisive test: T3's preregistered matched response-order rule; causal decision requires Q-RES. Kill the simple response-order account if either EVALUATE ordering fails. No closed line reopened.

### K04-O2 — Preserve complementary carriers at a fixed total quality budget

SOURCE/JUDGMENT: GaussMarker and EditGuard motivate testing jointly allocated carriers while retaining the existing semantic and instance payload meanings. Do not assume the present h-bearing carrier is free q redundancy. Targets foreign no-found/read losses; all per-cell physical ceilings UNKNOWN, arithmetic C caps are B. Planning ΔC range: SDXL .1/.2 0 to +15/60, SDXL .4 0 to +5, K3 .2 −5 to +15; SD1.5 .2 −5 to +3. Reason: observable second-tier survival motivates limited upside, but splitting energy can hurt the first tier. These are deliberately low-confidence, not N1 counts transferred into C.

JUDGMENT: Requires new marks, a joint objective and stage traces; initial writer cost budget up to twice 119 s/mark, unmeasured. Reader retains VAE/CLIP and public profile; any added semantic carrier test needs multiplicity allocation. T4/T5 can worsen through transferable payload or weakened h. Use the fixed flat-region/human checks in OPTIONS. Simpler alternative: current marks with an explicitly labelled two-tier reader. Cheapest current test T1/T3; decisive new-write test Q-STAGE followed by Q-DIVERSITY. Kill if no EVALUATE foreign gain at matched all-image quality, any low-strength SD1.5 loss, or any new T4/T5 accept. No closed line reopened unless h is replaced, which this option does not authorize.

### K04-O3 — Restrict and rebalance the existing latent band

SOURCE/JUDGMENT: Latent Watermark's channel ablation motivates testing allocation across the current real-DCT channels/bands. Fourier Integrity's complex-Fourier correction does not apply directly. Prior H1 already killed one narrower band, so rank low. Targets no-found and underfilled-margin losses, especially SDXL/K3; physical ceilings UNKNOWN. Planning ΔC: foreign .2 −5 to +5/60, SD1.5 .2 −5 to +3; little upside is expected because Phase A loses signal after encoding and the earlier narrow-band test did not help.

JUDGMENT: New marks and recalculated profile/thresholds; similar writer steps but unknown wall time, unchanged model side information, potential visible low-frequency structure. T4/T5 and h interference must be retested; use fixed flat-region checks. Simpler alternative is O1 plus the existing band. Cheapest permitted test T3 can expose where response remains but cannot replay a different writer. Queue only if Q-RES/Q-STAGE identify a specific allocation failure. Kill a later candidate without positive EVALUATE gain under identical total-quality and safety gates. No closed line reopened.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: T3 F5 EVALUATE robust/second alignment retention is.726189/.005154 on SD1.5 .2 and.093426/.269442 on SDXL .2; K3 .2 is.161632/.143618. The prespecified order is compatible on both F5 halves. Six DCT-position energies, robust bands, host norms and matched differences are retained, not inferred from detector score alone. Resize-only second retention near.984/.983 does not reproduce native SD1.5 loss.
JUDGMENT: O1 remains causally unidentified: working resolution and family are aliased, so Q-RES is necessary. O2 has a real complementary response prerequisite but T1's direct union fails a saved T4 attack; joint carrier design is not automatically safe. O3's new band targets require new writing and remain unmeasured, with prior H1 retained. No causal carrier-erasure or scale percentage is claimed.

## F. Proposed verdict

JUDGMENT ? PROPOSED IMPROVE. Confidence: Medium for diagnosis, low for a rewrite. Complementary physical responses justify joint carrier/scale study; direct union is unsafe.

JUDGMENT: Evidence that would change this verdict: Q-RES crosses scale; a joint carrier rewrite must then improve complete endpoint safely. This is a proposal to Claude, not approval to replace the method or run a writer. The [joint verdict table](../VERDICTS.md), [interactions](../INTERACTIONS.md), [two integrated designs](../CANDIDATE-DESIGNS.md) and [server queue](../SERVER-QUEUE.md) state the combined assumptions and scope.

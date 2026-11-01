# K08 — Second carrier, instance code and write order

SOURCE: Gate-1 ruling R1 requires this name: fragile is a hypothesis to test, not an assumed property. Historical filenames and quoted experimental labels remain unchanged for traceability (gates/GATE-1-RULING.md, R1).

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — h combines coarse DCT structure from a 32-square resampled block-mean map with block-gradient detail from (0,1)/(1,0), then takes 32 sign projections. Detail uses a dead zone, saturation, and a floor; coarse/detail nominal squared shares are 1/4 and 3/4 (`scripts/revised_watermark_v4.py:60-67,466-515`). It is not the semantic descriptor and not a cryptographic instance hash.
- SOURCE — The fragile mark occupies six full-resolution block-DCT positions distinct from those hash detail positions. It is fit with host rejection/amplitude and three corrective passes (`scripts/revised_watermark_v5.py:825-887`; profile `instance_frequencies` and `embedding.passes`). F5 computes h after the initial robust mark, embeds Wi(q,h), robust-refines the image, recomputes h, and re-fits Wi(q,h) (`scripts/f5_latent_codec.py:233-250`). q remains the original fixed semantic code.
- DERIVED — The v4 documentation that its embedder does not modify h's feature planes is not globally true of the complete F5 PGD writer. The final fragile stage preserves those planes before rounding/clipping; the unconstrained robust/refinement stages can change them. The second fragile write is corrective, so it should not simply be counted as two independent 47 dB noise additions.
- SOURCE — F5 does not export intended final h. Transfer evaluation substitutes the embed-report clean decoded h, whereas v5 exports intended h (`scripts/encoder_transfer_runtime.py:160-167`). DERIVED — Exact H/D comparisons have this asymmetry; substituting decoded h does not validate intended-payload recovery.
- DERIVED — Read costs include full-resolution DCT/hash extraction even when only C is reported; write cost includes two three-pass fragile fits. The native C/J endpoint does not depend directly on instance acceptance, but K8 alters robust latent chips through its pixel perturbation. Its removal could change C/J physically and would change F/instance interpretation. Recovery/quality/T4/T5 ceilings are UNKNOWN; no claim that this tier is uniformly useless after every regeneration family follows from its design name.
- SOURCE — The main agent's saved-development supplement reports source-majority instance found/read/exact-H/F counts of 52/37/3/5 under Stage 2 SDXL .1, and 30/19/0/0 under SDXL .2, each out of 60; every listed SD1.5 F5 cell has zero instance-found sources (`research/f5-components-20261101/results/wp1-fragile/REPORT.md:27-35`). DERIVED — Family-independent fragile extinction is contradicted. The older “both_match 0/90 by design” observation cannot be substituted for instance presence, instance read, H, or J in these foreign cells. The detector does not receive the attack identity or force the fragile result to zero after regeneration (`scripts/f5_latent_codec.py:265-311`).

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E08: F4 chroma](../context/wp1-prior-evidence.md#e08-f4-chroma-better-raw-channel-response-did-not-yield-a-clean-equal-quality-winner) (inventory line 128) | Selected r4 F4/v5 success numerators .1/.2/.4=25/25,13/17,2/2. Stronger post-hoc r5=27/26,23/17,6/2 with LPIPS mean/max.041/.083; T4 delivery20/20 but full attribution0/20. | Equal-perceptual-quality winner not established; post-hoc r5 lacks prospective selection/human acceptance. Chroma not categorically ruled out. |
| [E09: Original F5 M2 — FROZEN REPORT](../context/wp1-prior-evidence.md#e09-original-f5-m2-frozen-held-out-evidence-not-a-tuning-pool) (inventory line 138) | Held-out clean strict quality298/300; .2/.4 legacy semantic source30/30,21/30, checked-only27/30,17/30; full both_match0/90 per strength. | Frozen claim context only. Legacy semantic/full endpoints cannot be substituted for C/J; no retuning from these numbers. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E12: Registry with trusted records](../context/wp1-prior-evidence.md#e12-registry-additional-side-information-helps-a-different-task-with-hard-near-negative-limits) (inventory line 190) | Fresh 40-source F_R .2 SD1.5/SD2.1=30/40,32/40 below 36/40; fingerprint-only accepted4/13 near-duplicate pairs, registry 0/13 on unmarked no-pointer pairs. Later frozen held-out near-lookalikes 3/45 accepted. | Additional side information changes task; negative result not rescued by earlier screening or dependent millions of unrelated comparisons. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K08. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K08 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024

SOURCE: [Inspected K08 cards and query audit](../literature/intake/K08.md) contains five journal candidates and three TOP papers, with38 substantive queries including ten ruling-specific additions. JUDGMENT: Root counts3 Q1J +3 TOP. Singh et al.'s medical-fusion dual-domain paper is withheld because sequential architecture alone is too weak a transfer to the scoped T3/T4/T5 question. Vaidya is withheld because K10's independent access check could not inspect raster Algorithms1–3, so complete method inspection is unestablished. Both remain visible, with no floor credit. The two-journal shortfall meets the documented exhaustion condition; it is not called a met floor.

SOURCE: EditGuard (CVPR 2024, supplement §9.3/Table 11) reports sequential versus parallel robustness differences under its local-editing pipeline. TAG-WM (ICCV 2025, Table 3) jointly encodes copyright/localization in generation noise and tests SDXL inpainting; that is not global regeneration of an arbitrary F5 mark. GaussMarker (ICML 2025) offers dual-domain complementarity, with its own quality/calibration conditions. Padhi, Ozkaya, Vaidya and Li's journal cards describe authentication/recovery mechanisms: their standard-distortion or collage results do not certify foreign regeneration, exact instance binding, or the project's all-image quality gate. Ozkaya's reported PSNR 33.97 dB fails that gate.

JUDGMENT: Replace the descriptive word fragile with second carrier. N1 is evidence against discarding that carrier as wasted distortion. Its content-ok state when the semantic tier is absent is weaker than independently decoded semantic agreement. Neither tier union nor repeated watermark writing establishes ownership. Compare the current order with controlled stage traces and a matched-quality robust-only arm before reallocating distortion. Preserve the current h descriptor for now; improving it would reopen a closed reference-free instance-descriptor line. Human visibility remains MISSING.

## D. Improvement options
JUDGMENT: [OPTIONS](../OPTIONS.md) applies; the second tier is not assumed fragile.

### O1. Expose a separately budgeted two-tier endpoint
SOURCE: Gate-1 N1; EditGuard, TAG-WM and GaussMarker cards show distinct recovery/identity semantics and fusion costs. Keep existing marks and h. Define O_U as in T1, never rename it C/J. Targets frozen-C omissions on SDXL/K3; current observed O opportunity is32/12/3 on SDXL .1/.2/.4 and+11 on K3, not a safe new-method ceiling.
JUDGMENT: Planning new-endpoint gains/60: SDXL .1 +15..+32, .2 +3..+12, .4 0..+3, K3 0..+11; C/J delta0..0. Higher null thresholds and T4/T5 may erase all gains. Quality/writer cost unchanged; reader already computes both tiers, so fusion arithmetic is negligible. Same public key/CLIP/VAE side information; absent semantic evidence is explicitly weaker content checking. Simpler alternative retain C/J plus descriptive tier reports.
JUDGMENT: T1's precommitted gains/no-SD1.5-loss/no-negative rule applies, followed by available T4 and T5 diagnostics. Any new T4/T5 event kills promotion, and missing adversarial panels keep safety UNKNOWN. No descriptor line reopened.

### O2. Reverse or jointly refine write order
SOURCE: EditGuard's sequential/parallel ablation and N1 motivate measuring order, not importing an inpainting result as global regeneration. Preserve q/h and compare current order with a declared alternative after Q-STAGE. Targets cross-tier damage in every cell, physical ceiling UNKNOWN.
JUDGMENT: Delta C/60 SDXL .2 0..+10, K3 -5..+10, SD1.5 .2 -5..+3; h exact-match may improve or worsen independently. Writer cost at least the same stages, additional refinement unknown; detector unchanged. Flat-region/all-image strict quality and T4/T5 are required. No new side information. Simpler alternative O1.
JUDGMENT: T4/Q-STAGE first; final metadata alone cannot establish order damage. Kill the future order ablation if no EVALUATE useful endpoint gains survive equal quality and budget, or any T4/T5/quality gate fails. No closed descriptor line reopened.

### O3. Protect both tiers without changing the instance descriptor
SOURCE: GaussMarker diversity and its interference ablation motivate a joint constraint preventing a later stage from erasing the earlier tier. Targets physical transport/interference, ceilings UNKNOWN. This is an alternative to deleting the second carrier.
JUDGMENT: Delta C/60 SDXL .1/.2 0..+15, .4 0..+5, K3 -5..+15, SD1.5 .2 -5..+3; there may be no feasible shared-quality solution. Reader unchanged, more writer gradients/constraints, no added reference. h ambiguity and public-copy attacks remain. Mandatory flat-region/all-image/human checks apply. Simpler alternative frozen independent stages.
JUDGMENT: T3 tests complementarity and T4 tests margin prerequisite; Q-STAGE decides whether there is stage interference to constrain. Kill if the joint feasible set cannot preserve current strict quality and SD1.5 behavior, or gains fail real T4/T5. Changing h itself is REOPENS-CLOSED-LINE and remains excluded.

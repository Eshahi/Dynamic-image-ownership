# K10 — Binding decision and endpoints

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — Checked distance <=6 means match; >=10 means mismatch; intermediate values abstain as uncertain. Unchecked has the same status rank as match. F5 replaces semantic corrected-Hamming distance with soft distance on decoded semantic reads (`scripts/revised_watermark_v4.py:978-991`; `scripts/f5_latent_codec.py:148-155`).
- SOURCE — Instance-table selection uses q_now except when the found semantic channel has a nonmatching content status; then it uses decoded q. Instance status inherits the worse semantic status. A found mismatch has priority in the final decision table; both compatible found channels return `both_match` (`scripts/f5_latent_codec.py:294-318`; `scripts/revised_watermark_v4.py:994-1016`). DERIVED — The two tiers' binding decisions are coupled, not independent votes. Labels `authentic`, `regenerated`, and `copy_paste` are inferred output names, not attack ground truth.
- SOURCE — Frozen endpoint code defines C = semantic read AND content_match; Q = semantic read AND exact original q; J = Q AND content_match; H = instance read AND exact original h; D = Q AND H; F = `both_match`; S = semantic found AND content_match; A = either channel found (`scripts/m1b_e3_s1_analysis.py:70-84`; `scripts/encoder_transfer_test.py:72-75`). DERIVED — J does not require H, while F can succeed by recomputation without exact q/h read. A new content-ball result must have its own endpoint name and report frozen C and J separately.
- DERIVED — J contains no fragile-tier content check at all, tolerant or exact. F uses tolerant content statuses of both found channels; exact h is H, not F. SOURCE — Saved-development aggregation makes the distinction material: clean F5 C/J/H/F are 60/52/34/60; SD1.5 .1 C/J are 60/41, .2 57/38, .4 39/14, and K3 .2 5/0. Under SDXL .1 F=5 even though C=0 (`research/f5-components-20261101/results/wp1-fragile/REPORT.md:27-35,45,51`). DERIVED — An exact-semantic-payload deficit already exists on clean saved marks; it is not a fragile-tier deficit, and fixing tolerant binding alone cannot repair it.
- DERIVED — Recomputed-only presence gets distance zero and hence automatic content match in checked mode; it supplies S but not C/J (`scripts/revised_watermark_v5.py:1256-1257`; endpoint definitions above). Lowering a binding distance cannot be interpreted as adding independent content evidence on that route. Decision-only C recovery is bounded by existing reads; J recovery is bounded by existing exact-Q reads. Other component changes are not limited by those bounds.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E04: H3 mask and budget kill](../context/wp1-prior-evidence.md#e04-h3-texture-mask-sweep-quality-savings-did-not-preserve-equal-t3) (inventory line 68) | 12-source .4+.5: unmasked 52 dB 86/116; mask .5 at 52/50/48 dB 61/117,78/117,77/117. Closest comparable setting saved about 4% LPIPS, below 15% target. | Kills those mask/budget packages, not all allocation. Repairing carrier losses exposed more binding losses. |
| [E05: H4 threshold kill](../context/wp1-prior-evidence.md#e05-h4-threshold-relaxation-local-rescues-cost-natural-image-specificity) (inventory line 87) | Soft/hard .4=49/58 vs 42/58; radius6/7/8/10 admitted4/10/21/62 of132 ordered semantic cross-source pairs. Radius7 rescued4/6 .4 binding failures. | Equal-specificity relaxation failed. Semantic proximity is not measured joint T5 attribution; other calibrated rules remain open. |
| [E06: Noiseless binding/sketch diagnostic](../context/wp1-prior-evidence.md#e06-noiseless-semantic-binding-ceilings-informative-but-conditional) (inventory line 95) | At4/132 false-pair budget, true feature .4/.5/.6=55/44/14 versus production 49/37/10; random256-bit ranges54–55/44–48/12–15 on173 saved identities. | Shows representation/sketch headroom conditional on transport and finite operating point; not a realizable watermark or universal upper bound. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
| [E08: F4 chroma](../context/wp1-prior-evidence.md#e08-f4-chroma-better-raw-channel-response-did-not-yield-a-clean-equal-quality-winner) (inventory line 128) | Selected r4 F4/v5 success numerators .1/.2/.4=25/25,13/17,2/2. Stronger post-hoc r5=27/26,23/17,6/2 with LPIPS mean/max.041/.083; T4 delivery20/20 but full attribution0/20. | Equal-perceptual-quality winner not established; post-hoc r5 lacks prospective selection/human acceptance. Chroma not categorically ruled out. |
| [E09: Original F5 M2 — FROZEN REPORT](../context/wp1-prior-evidence.md#e09-original-f5-m2-frozen-held-out-evidence-not-a-tuning-pool) (inventory line 138) | Held-out clean strict quality298/300; .2/.4 legacy semantic source30/30,21/30, checked-only27/30,17/30; full both_match0/90 per strength. | Frozen claim context only. Legacy semantic/full endpoints cannot be substituted for C/J; no retuning from these numbers. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E12: Registry with trusted records](../context/wp1-prior-evidence.md#e12-registry-additional-side-information-helps-a-different-task-with-hard-near-negative-limits) (inventory line 190) | Fresh 40-source F_R .2 SD1.5/SD2.1=30/40,32/40 below 36/40; fingerprint-only accepted4/13 near-duplicate pairs, registry 0/13 on unmarked no-pointer pairs. Later frozen held-out near-lookalikes 3/45 accepted. | Additional side information changes task; negative result not rescued by earlier screening or dependent millions of unrelated comparisons. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |
| [E17: Coarse lattice and morphology](../context/wp1-prior-evidence.md#e17-coarse-lattice-saved-channel-diagnostics-and-a-candidate-not-measured-t3-of-the-new-mark) (inventory line 268) | Existing-mark F5 luma-band gain 1.76/.35/.60 on SD1.5/SDXL/K3 .2. Candidate patch384 T4 chroma2/300,luma2/150; real candidate T3 unrun; reported flat-region blotches. | Slopes/capacity proxies are not achievable bits or new-mark survival; secret-key side information differs. Candidate has no priority privilege. |

### Current saved-development accounting and per-cell ceilings

DERIVED: The restricted oracle changes only the content verdict on already decoded words. Its C ceiling is existing read-majorities and its J ceiling is existing exact-Q majorities. It is a diagnostic for one narrow role of this component, not a bound on a new descriptor, code, or rewritten watermark. A literal accept-all oracle would sacrifice T4/T5.

DERIVED: All ceilings are source-level potential increments relative to frozen C/J, not sums of per-call failures. Shared ceilings must not be added across components. Missing calls remain failures in baseline C/J. Every unconstrained new design and every joint strict-quality/T4/T5-safe recovery ceiling is UNKNOWN; current scores contain no new-method negatives or human visual verdict. Protocol: [accounting specification](../analysis/WP1-ACCOUNTING-SPEC.md); endpoint source: scripts/m1b_e3_s1_analysis.py:70–84.

| Study/cell | C /60 | J /60 | Restricted C ceiling (gain) | Restricted J ceiling (gain) | Missing-C upper | Trivial C gain cap |
|---|---:|---:|---|---|---:|---:|
| phase-a / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| phase-a / R0-0.2 | 57 | 38 | 59 (+2) | 39 (+1) | 58 | 3 |
| phase-a / R0-0.4 | 39 | 14 | 47 (+8) | 15 (+1) | 40 | 21 |
| phase-a / R1-0.1 | 0 | 0 | 1 (+1) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / ctrlB-codec | 60 | 47 | 60 (+0) | 47 (+0) | 60 | 0 |
| stage2-union / D1 | 55 | 31 | 55 (+0) | 31 (+0) | 55 | 5 |
| stage2-union / D3 | 55 | 35 | 55 (+0) | 35 (+0) | 55 | 5 |
| stage2-union / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / R0-0.2 | 57 | 38 | 58 (+1) | 38 (+0) | 58 | 3 |
| stage2-union / R0-0.4 | 39 | 14 | 47 (+8) | 16 (+2) | 40 | 21 |
| stage2-union / R1-0.1 | 0 | 0 | 1 (+1) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-mode-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-rinse-0.1 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-smooth-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R3-0.2 | 5 | 0 | 7 (+2) | 0 (+0) | 5 | 55 |
| stage2-union / X1 | 60 | 46 | 60 (+0) | 46 (+0) | 60 | 0 |
| stage2-union / X2 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / clean | 60 | 52 | 60 (+0) | 52 (+0) | 60 | 0 |

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K10. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K10 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024
SOURCE: [K10 intake](../literature/intake/K10.md):4 Q1J +3 TOP, one journal slot exhausted after30 substantive queries. EditGuard/OmniGuard local tamper recovery differs from whole-image T3. WAM localizes marks but its DiffPure ablation loses message bits. Padhi, Ozkaya and Li supply different authentication/recovery contracts, not adaptive ownership proofs. Vaidya is withheld because raster algorithms were not inspected. MetaSeal is an uncounted TMLR lead; its signature verifies recovered content and does not, by itself, bind the current image to that content.
JUDGMENT: A valid cryptographic signature, a robust detector hit and current-image consistency are three different predicates. Existing public F5 evidence cannot be silently upgraded to instance ownership.

## D. Improvement options
JUDGMENT: Forecasts follow [OPTIONS](../OPTIONS.md).

### O1. Explicit unresolved/conflicting evidence states
SOURCE: K10 intake contrasts differing verification contracts. Preserve C/J and report semantic-consistent, instance-consistent, conflicting and unchecked states instead of collapsing missing semantic evidence into a stronger identity assertion. Targets interpretation/false attribution, not carrier loss; delta C/J0..0 in every cell.
JUDGMENT: No writer, quality or material reader cost; side information unchanged. This can reduce claims/accepts, not prove T4/T5 safety. Simpler alternative retain the current table but show all flags. No flat-region test needed for a reporting-only change.
JUDGMENT: T1 verifies that semantic-absent instance successes are identified; kill any proposed mapping that labels unchecked semantic evidence exact original identity or changes frozen C/J. No closed line reopened.

### O2. Union with content semantics stated and budgeted
SOURCE: Wang's valid-evidence conditions, WAM domain-shifted null rates and N1. Keep the existing q/h definitions and expose O_U/O_Q as new endpoints. Targets omitted second-tier evidence; conditional opportunity is K08 O1, all-safe ceiling UNKNOWN.
JUDGMENT: New endpoint gains/60 SDXL .1 0..+32,.2 0..+12,.4 0..+3,K3 0..+11; frozen C/J0..0. No quality/writer cost; small fusion cost; no reference beyond existing CLIP/VAE/profile. T4/T5 is the central price, especially unchecked semantic cases. Simpler alternative O1 reporting.
JUDGMENT: T1 and existing T4/T5 diagnostics apply with fixed kills. Judge must choose null interpretation before future deployment; empirical convenience is not grounds to select a budget. No closed descriptor line reopened.

### O3. Contradiction veto using existing evidence
SOURCE: EditGuard/OmniGuard recovery contracts motivate refusing an ownership statement when two available descriptors disagree. Use existing q/h consistency only, no new descriptor, and abstain when meaningful evidence conflicts. Targets false attribution, not lost transport.
JUDGMENT: Delta new-endpoint successes -10..0/60 on foreign cells; C/J remain frozen. No write/quality cost, negligible reader logic, same side information. Veto can lose true positives and still miss T5 collisions; absent evidence is not a contradiction. Simpler alternative O1 labels without acceptance change.
JUDGMENT: T1's route/content tables are the cheapest descriptive screen; a future fixed veto must beat the same T4/T5 panel without unacceptable T3 loss, otherwise kill. No fitted veto threshold is authorized now. Signed records/new instance descriptors would be REOPENS-CLOSED-LINE or new detector side information and are not part of this option.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: O1 route/status accounting is complete and preserves C/J. Semantic-absent instance-content successes are separately identified; unchecked is not exact-q agreement. O2 inherits the new EVALUATE T4 accept and is killed as safe promotion.
DERIVED: O3 defined as a contradiction veto cannot remove the observed T4 counterexample because semantic evidence is absent; absent evidence is not a contradiction. This is a decisive logical failure of that proposed sufficient repair, without tuning a veto after the attack. Rejecting all unchecked events would remove valuable N1 successes and requires a new declared tradeoff, not a favorable reinterpretation here.

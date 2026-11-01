# K11 — Keys and side information

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — The deployed profile is `public-derived`; its master key is a fixed SHA-256 constant and streams are domain-separated HMAC-SHA256 expansions. NFC-normalized OwnerID conditions carrier/table labels, but semantic projection rows do not include OwnerID (`scripts/revised_watermark_v5.py:95,304-314,343-359`; `scripts/revised_watermark_v4.py:212-218,344-354`; `scripts/f5_latent_codec.py:123-128`). DERIVED — “Keyed” denotes deterministic indexing, not a secret possessed only by the legitimate owner. Possession of OwnerID is not authorization (`research/threat-model.md:7-9`). No cryptographic unforgeability follows.
- SOURCE — Native inputs are suspect RGB, the latent z supplied by the pinned encoder, claimed owner, profile, and suspect semantic features, with band/whitening/binding parameters (`scripts/f5_latent_codec.py:265-267,323-326`). Evaluation also receives original q/h; those are evaluator side information, not reader side information (`scripts/encoder_transfer_runtime.py:179-180`; endpoint code above). There is no registry in this F5 reader.
- SOURCE — The inherited detector configuration hash covers v5 profile fields but excludes decision thresholds and embedding fields; F5 band, whitening, binding mode, CLIP view count, and VAE weights are not added to that hash (`scripts/revised_watermark_v5.py:138-150,292-301`; `configs/f5-r2.json:8-48`). DERIVED — The hash alone does not identify the entire F5 reader. Conversely, changing inherited `robust` profile settings that F5 does not directly use still changes the seed/config hash and therefore q, tables, and carriers. Such a change is not an isolated physical-parameter perturbation.
- JUDGMENT — Keep K11 as an assumptions and provenance component. Its “sources recovered” ceiling is not a meaningful performance quantity without specifying a changed method. Introducing a secret, registry, or externally supplied original descriptor changes the trust/side-information model and must not silently inherit native C/J or public-derived security claims.

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
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |
| [E17: Coarse lattice and morphology](../context/wp1-prior-evidence.md#e17-coarse-lattice-saved-channel-diagnostics-and-a-candidate-not-measured-t3-of-the-new-mark) (inventory line 268) | Existing-mark F5 luma-band gain 1.76/.35/.60 on SD1.5/SDXL/K3 .2. Candidate patch384 T4 chroma2/300,luma2/150; real candidate T3 unrun; reported flat-region blotches. | Slopes/capacity proxies are not achievable bits or new-mark survival; secret-key side information differs. Candidate has no priority privilege. |

### Current saved-development accounting and per-cell ceilings

DERIVED: With pixels, keys, scores and decisions fixed, documenting side information recovers zero C/J. Changing the key/trust model is a different intervention with UNKNOWN recovery and security implications.

DERIVED: All ceilings are source-level potential increments relative to frozen C/J, not sums of per-call failures. Shared ceilings must not be added across components. Missing calls remain failures in baseline C/J. Every unconstrained new design and every joint strict-quality/T4/T5-safe recovery ceiling is UNKNOWN; current scores contain no new-method negatives or human visual verdict. Protocol: [accounting specification](../analysis/WP1-ACCOUNTING-SPEC.md); endpoint source: scripts/m1b_e3_s1_analysis.py:70–84.

| Study/cell | C /60 | J /60 | Restricted C ceiling (gain) | Restricted J ceiling (gain) | Missing-C upper | Trivial C gain cap |
|---|---:|---:|---|---|---:|---:|
| phase-a / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| phase-a / R0-0.2 | 57 | 38 | 57 (+0) | 38 (+0) | 58 | 3 |
| phase-a / R0-0.4 | 39 | 14 | 39 (+0) | 14 (+0) | 40 | 21 |
| phase-a / R1-0.1 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / ctrlB-codec | 60 | 47 | 60 (+0) | 47 (+0) | 60 | 0 |
| stage2-union / D1 | 55 | 31 | 55 (+0) | 31 (+0) | 55 | 5 |
| stage2-union / D3 | 55 | 35 | 55 (+0) | 35 (+0) | 55 | 5 |
| stage2-union / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / R0-0.2 | 57 | 38 | 57 (+0) | 38 (+0) | 58 | 3 |
| stage2-union / R0-0.4 | 39 | 14 | 39 (+0) | 14 (+0) | 40 | 21 |
| stage2-union / R1-0.1 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-mode-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-rinse-0.1 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-smooth-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R3-0.2 | 5 | 0 | 5 (+0) | 0 (+0) | 5 | 55 |
| stage2-union / X1 | 60 | 46 | 60 (+0) | 46 (+0) | 60 | 0 |
| stage2-union / X2 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / clean | 60 | 52 | 60 (+0) | 52 (+0) | 60 | 0 |

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K11. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K11 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

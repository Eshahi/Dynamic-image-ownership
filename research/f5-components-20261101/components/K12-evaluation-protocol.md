# K12 — Evaluation protocol

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — The Stage 2b contract uses development sources, seeds 12/13/14, SD1.5/SDXL strength grids and Kandinsky 3 .2, with fixed configs; the actual runtime enforces 512-square saved detector input and performs 1024 processing/resampling for the foreign channels (`research/encoder-transfer-20261019/stage2b-config.json`; `scripts/encoder_transfer_runtime.py:105-117,660-676`). DERIVED — Encoder family is coupled to native resolution, resampling, model/scheduler, and noise path. Equal nominal strengths do not isolate a common perturbation budget.
- SOURCE — Majority means at least two true results for the three prescribed seeds. Missing calls count as non-success; optimistic missing-as-success totals are reported separately. Negative endpoint is A, with individual C0/wrong-owner calls and unresolved counts, not a negative source majority (`scripts/encoder_transfer_test.py:78-81,339-367`). Correct/wrong owners are separate roster-one calls; C0 receives only the correct-owner call (`scripts/encoder_transfer_runtime.py:176-180`). DERIVED — This is study aggregation, not a verifier allowed to generate/retry three suspects; source-majority counts cannot be obtained by dividing a seed total by three.
- SOURCE — The historical `f5_t4.py` study uses clean-donor residual access at scales .5 and 1 and tests `both_match`, with a binding-disabled delivery control; it explicitly does not reproduce the public projection attack (`scripts/f5_t4.py:1-10,62-90`). SOURCE — `f5_binding_experiment.py:156-178` also contains descriptor-level T4 comparisons and joint near-collision T5 diagnostics; its h-distance input is imported from the supplied T5 run's `f4_C1` field. DERIVED — These are different estimands from an end-to-end public-patch forgery or a newly modified reader's false acceptance. Historical zero counts cannot automatically certify a new content-ball reader.
- SOURCE — Phase A fit reuses the same internal adapter and original C1 payload; its row timer includes image loading and processing, while owner-call timing begins after shared features/latent (`scripts/et_final_phase_a_fit.py:84-121`; `scripts/encoder_transfer_runtime.py:173-183`). DERIVED — Low-level detector, owner-call, full image read, writer, regeneration, and quality times need separate scopes. No per-component latency decomposition was identified here.
- JUDGMENT — K12 has no algorithmic recovery ceiling. It controls what is identifiable: pair source/seed records, keep failed/missing calls, distinguish C/J/F/A, preserve development versus frozen evidence, and avoid using a change of negative endpoint or source selection to claim method improvement.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E01: v5 carrier and two-tier foundation](../context/wp1-prior-evidence.md#e01-v5-established-lower-frequency-survival-threshold-assumptions-and-the-two-tier-tradeoff) (inventory line 28) | Synthetic 16-source VAE/.1/.2 counts improved 9/5/2 to 16/14/9; r3 .1/.2 all-seed 14/16 and 10/16. Recomputed-only binding and public adaptive-null limits were already documented. | Rejects the specific earlier carrier on tested channels; does not establish independent-encoder survival. |
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E03: H1 carrier-band kill](../context/wp1-prior-evidence.md#e03-h1-carrier-geometry-the-tested-narrow-band-did-not-improve-regeneration) (inventory line 60) | Four-source panel baseline 4–32 vs 8–28 at .4:13/18 vs 13/17; .5:10/18 vs 9/18; .6:2/17 vs 1/16. Mean LPIPS .0172→.0107. | Tested narrower band did not improve T3; other bands, geometry and foreign channels remain untested. |
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
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
| [E16: F6 and RL — proposals, not efficacy](../context/wp1-prior-evidence.md#e16-f6-and-rl-existing-proposals-no-efficacy-evidence-to-inherit) (inventory line 258) | F6 planned 200 vs 350-gradient comparison is unrun. RL fixed-menu oracle 275/420→276/420 is one-case gain; unknown new actions/objectives excluded. | No F6/RL success can be inherited; approved package unchanged. Optimization adequacy not demonstrated. |
| [E17: Coarse lattice and morphology](../context/wp1-prior-evidence.md#e17-coarse-lattice-saved-channel-diagnostics-and-a-candidate-not-measured-t3-of-the-new-mark) (inventory line 268) | Existing-mark F5 luma-band gain 1.76/.35/.60 on SD1.5/SDXL/K3 .2. Candidate patch384 T4 chroma2/300,luma2/150; real candidate T3 unrun; reported flat-region blotches. | Slopes/capacity proxies are not achievable bits or new-mark survival; secret-key side information differs. Candidate has no priority privilege. |

### Current saved-development accounting and per-cell ceilings

DERIVED: Correct accounting with unchanged observations recovers zero algorithmic C/J. The missing-C upper bound below is epistemic: it treats unavailable calls as possible successes, not as measured recovery or permission to retry. Fresh studies cannot be forecast from that range.

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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K12. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K12 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024

SOURCE: [Six inspected K12 cards and 36-query audit](../literature/intake/K12.md): three Q1J and three TOP; 32 substantive searches with four successful scholarly domains. Two journal cards concern statistical protocol validity rather than watermark performance. Published identities and inspected author-version caveats are recorded separately.

SOURCE: WAVES (ICML 2024, Table 3/Appendix F) shows attack and quality dependence but does not isolate independently trained encoders by checkpoint name. Erasing the Invisible (NeurIPS 2025, Table 1/Appendix A) reports superposition results without matched watermark strength/quality; its main and Appendix E score definitions conflict. MarkDiffusion (JMLR 2026, Table 3/Appendix D) standardizes implementations, not the missing family-by-resolution experiment. Black-Box Forgery (CVPR 2025, Tables 1–3/Appendix F) shows why public reference access, key/nonce policy and encoder lineage matter; high detection/attribution can coexist with content forgery. Safe testing and focal selection coverage require their stated null/selection assumptions.

JUDGMENT: Make N2 a primary factorial question. Compare the same existing marks under crossed resolutions, preserving seeds, noise schedules, resizing and quality endpoints. Calibrate or bound the complete reader decision, keep the evaluation half untouched by selection, and treat repeated attack attempts as one declared attack budget. Existing reused development halves support exploration only. No literature result licenses a causal percentage for scale, a new ownership claim, or tuning from Phase-B reports. A fresh disjoint confirmation design belongs after the judge's decision and separate user authorization.

## D. Improvement options
JUDGMENT: [OPTIONS](../OPTIONS.md) applies. Evaluation changes yield delta C/J0..0; they alter what can be inferred, not image quality.

### O1. Cross family and working resolution
SOURCE: Gate-1 N2, WAVES attack-quality accounting and Black-Box Forgery's encoder-lineage warning. Q-RES uses existing F5/v5/VINE-R marks, SD1.5 at1024 and SDXL at512, with existing opposite-scale baselines. Targets the family/scale attribution gap. Physical improvement ceiling UNKNOWN; causal scale fraction unidentifiable in saved native cells.
JUDGMENT: New regeneration/reader cost only, no writing or new detector side information. T4/T5 unchanged and unresolved; output quality must be compared, not assumed equal from nominal strength. Simpler alternative saved resize/control T3, which cannot separate family from scale.
JUDGMENT: T3 precommitted response-order rule is the current screen. Q-RES has a future fixed scale-explanation kill in SERVER-QUEUE. No closed line reopened and no held-out sources are used.

### O2. Separate descriptive fusion from calibrated acceptance
SOURCE: Safe Testing, Jin/Ren selective inference and the Erasing metric-direction inconsistency. Preserve original C/J, publish all missing cells, source halves and joint test counts, and do not select a union/radius after EVALUATE. Targets endpoint/multiplicity bias.
JUDGMENT: No writer/quality change; bookkeeping and per-route reader outputs cost storage. Source-level dependence and fixed public keys limit T4/T5/security inference. Same side information. Strongest simpler alternative a single fixed original endpoint.
JUDGMENT: T1/T2 validate complete route and panel accounting; kill a proposed success claim if it drops failed/missing seeds, selects radius on EVALUATE, counts overlapping Phase A/Stage2 sources as independent, or substitutes a new endpoint for C/J. No closed line reopened.

### O3. Stage-resolved equal-quality ablation
SOURCE: Gate-1 R5 and K06/K07 literature. Q-STAGE compares full writer traces with robust-only at matched total final quality, then checks system endpoints. Targets causal budget attribution and optimizer damage, not merely predictive correlation.
JUDGMENT: Additional writes, regeneration and two-owner reads; exact anchor costs in SERVER-QUEUE. No deployed side-information change. Removing h may worsen T4/T5; all-image quality and flat-region human checks mandatory. Simpler alternative T4 final-margin association.
JUDGMENT: T4's precommitted rule can kill a simple predictive story but cannot approve this causal one. Q-STAGE kills robust-only promotion if no useful equal-quality T3 gain or any quality/safety regression. A stage diagnosis without safety panels is not a completed method comparison. No closed line reopened.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED/DERIVED: O1 T3 leaves family/scale nonidentifiable; Q-RES is mandatory to settle the strong scale account. O2 T1 distinguishes C/J/O/O_U/O_Q and complete error budgets, while T2 demonstrates that reader detection gains can be binding negatives. All missing and failed units are retained; reused seeds/pairs/studies are not counted as independent sources.
MEASURED/JUDGMENT: O3 T4 retains predictive association but no causal stage claim, so Q-STAGE is required. New evaluation reporting itself changes frozen C/J by0. No held-out journals or pixels, Phase-B tuning, diffusion/writer run or automatic lifecycle verdict was used. No later study can claim fresh confirmation from these consumed development sources.

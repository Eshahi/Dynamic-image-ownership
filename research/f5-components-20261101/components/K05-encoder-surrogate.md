# K05 — Reader encoder and writer surrogate

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — `Reader` loads local SD1.5 fp16-variant weights into a frozen fp32 VAE. It maps `2*x-1` through encoder posterior mode and multiplies by .18215; no decoder, posterior sampling, UNet, or attack simulator is used in the robust objective (`scripts/f5_latent_codec.py:88-107,195-205`). SOURCE — The same encoder supplies gradients for writing and latents for reading.
- DERIVED — F5 is an image-domain mark optimized through a latent encoder, not a watermark inserted into a generative sampling trajectory (`scripts/f5_latent_codec.py:218-251`). The original image, registry, regeneration checkpoint, and attack seed are not native reader inputs. Knowing the reader VAE does not imply knowing the actual foreign regenerator.
- SOURCE — The transfer adapter's read shares one VAE encoding across owner calls; the low-level `seconds` starts after z has been provided (`scripts/encoder_transfer_runtime.py:173-183`; `scripts/f5_latent_codec.py:265-276`). DERIVED — Reader costs must include this forward pass separately. Writer cost includes 200 encoder-gradient evaluations in r2 plus final encoding, not 150 alone.
- JUDGMENT — K5 should explicitly include the distinction between reader coordinate system and writer channel model. Replacing the reader, replacing only the differentiable surrogate, and using an ensemble are different interventions. Their ceilings are UNKNOWN from saved fixed-reader detections. SOURCE — Phase A reports encoder gain transferring while robust survival does not, and identifies noise injection as a major SDXL loss stage (`research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:87-112`); “SD1.5 encoder dependence” does not mean the foreign codec alone erased the mark.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E09: Original F5 M2 — FROZEN REPORT](../context/wp1-prior-evidence.md#e09-original-f5-m2-frozen-held-out-evidence-not-a-tuning-pool) (inventory line 138) | Held-out clean strict quality298/300; .2/.4 legacy semantic source30/30,21/30, checked-only27/30,17/30; full both_match0/90 per strength. | Frozen claim context only. Legacy semantic/full endpoints cannot be substituted for C/J; no retuning from these numbers. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E13: Stage2a/2b development transfer](../context/wp1-prior-evidence.md#e13-development-transfer-stage-2-f5-is-family-specific-with-observable-subthreshold-signal) (inventory line 208) | F5 C SD1.5 .1/.2/.4=60/57/39, SDXL0/0/0, K3 .2=5 of60. Codec-only55/60; SDXL .2 all180 semantic tests fail but171 exceed unmarked median score. | Round-trip failure is not sole explanation; failed threshold is not zero signal. Methods' distortion and family noise schedules differ. |
| [E14: Phase A development mechanism](../context/wp1-prior-evidence.md#e14-phase-a-mechanism-foreign-encoder-gain-exists-survival-collapses-around-noise-injection) (inventory line 224) | Encoder gain F5/control SD1.5=15/4.8–6.4, SDXL392/178–249,K3 43.3/20–27. SDXL chip retention .66 codec→.08 noise/native; pooled law predicts zero despite SD1.5 C60/57/39. | Amplification transfers; surviving direction does not. Paired stage diagnostics are descriptive, not isolated causal ablations. Attack grids failed eligibility. |
| [E15: Phase B — FROZEN REPORT](../context/wp1-prior-evidence.md#e15-phase-b-frozen-independent-transfer-validation-and-unresolved-negatives) (inventory line 246) | Held-out200 F5 C SDXL .1=19 and K3 .2=61; J SD1.5 .2=163 did not establish> .80. Every negative gate incomplete (4–8 unresolved sources). | Frozen context only: development0/60 not population extinction. No held-out per-source data opened or tuning performed. |
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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K05. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K05 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.

## C. Literature since 2024

SOURCE: [Inspected K05 cards and search audit](../literature/intake/K05.md). Two proposed Q1J and three TOP cards; journal floor exhausted after 48 logged searches, including explicit domain-filtered follow-ups. Latent Watermark is an inspected author version linked to its final TMM publication, not a verified byte-identical final paper.

SOURCE: VINE (ICLR 2025, methods/ablations and supplement) uses learned robustness and a blur-like proxy within a complete trained system; ROBIN (NeurIPS 2024) exploits latent reconstruction, without a clean isolated foreign-encoder-lineage test. ZoDiac's denoising ablation improves detection within its own machinery while failing this project's clean PSNR condition. DiffMark (Information Fusion 2026, §§4.1.2/4.4.1, Table 5) trains through a noise pipeline for deepfake use; its two stated recovery-weight schedules conflict. Latent Watermark's channel ablation is relevant to allocation, not proof that a different attacker VAE preserves the same code.

JUDGMENT: First retain the pinned reader and test writer-side robustness against the actual noise/reconstruction intervention, then consider changing the reader. A surrogate ensemble that only reconstructs images can optimize the wrong channel. F6 is a related unrun proposal, with no efficacy to inherit. Q-RES must separate scale from model; Q-STAGE must separate underfilled optimization from stage interference. Replacing the public pretrained model or adding a robust VAE would require unavailable weights/training and new marks, and cannot be evaluated by replaying saved endpoints. No closed external-baseline or FreqMark line is reopened.

## D. Improvement options — PROPOSED

JUDGMENT: [OPTIONS](../OPTIONS.md) defines forecast, visibility and scope conventions. All model/writer replacements have UNKNOWN physical ceilings; changing an encoder can change every reader route, not only the currently failed calls.

### K05-O1 — Optimize through the noise/reconstruction channel with the pinned reader retained

SOURCE/JUDGMENT: VINE/ROBIN motivate channel-aware objectives; Phase A and the approved, unrun F6 package identify noise/reconstruction as a distinct intervention from codec reconstruction. Targets foreign no-found/read losses. Planning ΔC at .2: SDXL 0 to +20/60, K3 −5 to +20, SD1.5 −5 to +3; .4 foreign 0 to +5. Low-confidence ranges reflect residual signal but no demonstrated foreign survival of a new writer. This is not a prediction that F6 passes.

JUDGMENT: No detector side-information change if the reader stays pinned; writer gradients through noise/denoising cost materially more than 119 s and require GPU. Quality and flat-region constraints use OPTIONS; h interference and T4/T5 remain mandatory. Simpler alternative: fix stage underfill without a new surrogate. Cheapest saved tests T3/T4; decisive objective comparison remains the existing F6 study, unchanged, after Q-RES/Q-STAGE diagnosis. Kill under F6's approved rule, not a new easier endpoint. No closed line reopened and no approved F6 artifact amended.

### K05-O2 — Use a writer-only ensemble of genuinely independent codec surrogates

SOURCE/JUDGMENT: Latent Watermark and DiffMark support explicit channel modeling but do not prove this ensemble. Penalize the same original payload across distinct codec paths; record lineage and working scale. Targets foreign transport; all physical ceilings UNKNOWN. Planning ΔC foreign .2 0 to +10/60, SD1.5 .2 −5 to +3, with low confidence because codec-only F5 already retains 55/60 on foreign round trips and noise is the larger remaining intervention.

JUDGMENT: Requires additional model assets, new marks and several encoder gradients per step; no reader change or secret required. Competing gradients can increase distortion and hurt both tiers/T4/T5. Flat-region/human checks apply. Simpler alternative is O1 with one actual noise channel. Cheapest saved test T3 compares codec-only versus regeneration response; no ensemble gradient or outcome is recoverable from current outputs. Queue Q-DIVERSITY only after diagnosis. Kill if codec gains do not transfer to native foreign EVALUATE cells at matched strict quality, or if any required safety/SD1.5 preservation gate fails. No closed line reopened.

### K05-O3 — Replace the reader only after a matched-reader ablation

SOURCE/JUDGMENT: ROBIN and ZoDiac motivate reconstruction-aware extraction, but their extra computation and access are not lightweight F5 extraction. Targets the distinction between surviving carrier and a mismatched observation model. Planning gain in a new reader endpoint: 0 to +10/60 on foreign .2; frozen C/J remain unchanged. Physical ceiling UNKNOWN; old found/read ceilings do not constrain another reader.

JUDGMENT: Additional encoders or inversion become detector side information and can multiply latency/memory and tested hypotheses. A learned robust VAE would require training; neither is permitted now. T4/T5 calibration and public adaptive attacks must be repeated; no writer means no new flat-region artifact. Simpler alternative is current-reader exact constrained decoding. Cheapest current evidence T2/T3; no old latent permits a foreign trained-reader evaluation. Rank low and queue only if a predeclared observed-response mismatch remains. Kill if improvement disappears after total-test-budget calibration, or if extra safety accepts occur. No new external baseline or training is authorized.

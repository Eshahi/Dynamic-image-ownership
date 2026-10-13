# Same-source reissue and crossed-payload binding controls

2026-10-13. Prospective, development-only protocol, frozen before construction. One bounded run; no result is asserted. This follows the binding next decision in `no-human-next-study.md` after the third FreqMark implementation attempt closed without a numerical comparison or optimization update. It neither reopens that route nor spends H2. Frozen E3, M1a and M2 remain unchanged.

## Decision and scientific question

Run **E3-RC1: same-source reissue with recipient-consistent instance binding**. Can the semantic predicate reject a physically delivered foreign q when the instance payload is deliberately consistent with the recipient, while accepting the matched same-source reissue?

The old public transfers delivered donor q and donor h together. Their rejection by perceptual-only and combined modes cannot establish the added value of semantic binding. The decisive new cell carries **donor q plus recipient h**, encoded into the actual recipient image with the correct q-conditioned instance carrier. Copying a recipient instance vector under a different q would instead test a broken routing key; do not do that. The reciprocal cell carries recipient q plus donor h. All cells must be actual saved images read by the unchanged suspect-only detector.

This is a component stress experiment within public T4/T5 transfer, not a new robust writer or an ownership-security demonstration. In particular, a donor q may coincide with, or be accepted on, a different recipient. Such a result is retained as a component collision, never relabelled a human semantic error. The experiment does not examine T1/T2 or repeat regeneration.

## Fixed inputs and access

Use the completed Stage A receipt at MAIN `.thesis-build/dev-runs/20261013-1636-fresh-e3-simplification/run.json`, construction commit `546ac1fbf644e3d1ab3f454c9eb8ae736dbd072a`, and `fresh-development-inputs.json`. Only the first twelve numerical source IDs in that reserved cohort enter this study, paired consecutively with the lower ID as recipient:

| Recipient | Donor |
|---:|---:|
| 30 | 72 |
| 73 | 89 |
| 127 | 165 |
| 309 | 370 |
| 436 | 450 |
| 459 | 471 |

No pair is selected, replaced, reversed or excluded using q/h distance, an image inspection, a detector result or a semantic label. Resolve existing canonical and full-E3 image paths from that receipt. Confirm reserved IDs/hashes against existing exclusion receipts; do not inspect held-out pixels or build a new inventory service. The retained clean alpha call must show exact readable q/h and full acceptance for each selected full image, as already reported. Missing source evidence ends execution as an input failure; it does not authorize a replacement.

For each pair, let R and D be the saved full-E3 recipient and donor RGB8 images. Freeze qR and qD from their readable clean alpha semantic payloads. Let **hR and hD be the native `perceptual_hash` fields of those same saved clean calls**, not their operational decoded instance payloads. Thus hR is the recipient's own pre-intervention native content hash; no final-image hash is fed back to the writer. Save all four integers and their receipt fields before any new image is constructed. Also retain the original operational payloads to distinguish a reissued target from the old target.

This is a public read-and-reissue access model: the constructor has both marked images, alpha, the public profile, cached models, and their publicly obtainable q and content hashes. It receives no secret or clean-reference target. Canonical originals are evaluator-only quality references. The reader receives neither original image nor any intended payload.

## Four matched cells, including a real positive

All four cells start independently from the identical recipient **R**, not its canonical unmarked source. They differ only in the fixed supplied q/h:

| Cell | Supplied q | Supplied h | Role |
|---|---|---|---|
| RR | qR | hR | Same-source public reissue, constructed positive |
| DR | qD | hR | Foreign semantic payload with recipient-consistent instance binding; primary contrast |
| RD | qR | hD | Recipient semantic payload with foreign instance binding; reciprocal control |
| DD | qD | hD | Joint foreign-payload transfer, bridges the previous confounded construction |

RR is not an unchanged C1 evaluation. It runs the same rewrite operator and output serialization as the transfer cells, starting from an already marked image and replacing the operational instance target with the image's own current hash. Its positive label is **same source with only a bounded watermark reissue**, declared prospectively. It does not label arbitrary generated content semantically equivalent. Record changed RGB components/pixels, maximum absolute pixel change, and whether the new target differs from the old operational h. If RR happens to be byte-identical to R, retain the call but flag it as an idempotent control; it supplies no new evidence about tolerance to rewriting.

The positive construction preserves coordinates, dimensions and the underlying source raster; only the carrier-writing perturbation is applied. Its admissible envelope is strict quality relative to both R and the canonical recipient: PSNR >35 dB, SSIM >.9, LPIPS <.1. This is an operational construction and quality definition, not proof of human semantic preservation. No human or model-generated semantic verdict is needed or invented.

## Frozen construction, no selection

Use the existing BCH initializer primitives used by E3, not the older F5 `journal_binding_probe.synthesize` and not the full E3 writer's clean-admission selector. The full writer would condition refinement on `both_match`, which is the outcome under investigation. Label generated images **E3-RC1 public initializer reissues**, not admitted E3 outputs.

For each recipient, process qR then qD. For each q:

1. Obtain the BCH layout/pattern through existing `journal_bch_probe.patterns(profile, q)` (also imported by `journal_e3_writer`). From R/255, run `f5_latent_codec.robust_pgd` with PSNR parameter 46, 150 steps, margin 4, mask power 0. Use the existing fp32 native implementation and round with `clip(rint(255*x),0,255).astype(uint8)`.
2. Save this shared first-stage image. From independent copies, process hR then hD. Apply existing `restore_fragile(rgb,q,h,profile)` once; this uses the supplied q-conditioned carrier and fixed supplied h.
3. From that branch's restored image run the same robust PGD with PSNR parameter 52, 50 steps, margin 4, mask power 0. Round exactly as above, apply `restore_fragile` once more, save PNG and reload RGB8. This final saved image is the sole evaluated output.

This is twelve 150-step first stages and twenty-four 50-step branches, exactly 3,000 PGD steps. Share only the q-stage that precedes h insertion. Do not share subsequent gradients or restore results between h branches. Use alpha only, unchanged seven-view features, BCH codec, profile, VAE and thresholds. No minimax/DDIM/SDXL stage, contraction, checkpoint selection, repeated restore, payload redraw, final-h recomputation for writing, detector-driven early stopping, changed budget, or rescue optimization. Save first-stage images and both fragile reports. A zero-gradient step from inactive hinges is not itself a scientific failure; preserve the native update semantics.

Use seed 2026101317 for Python/NumPy/Torch initialization and record it, although the initializer uses no intended random augmentation. Retain the existing science environment; block downloads. Code must call the budget check during PGD through the existing bounded-reader pattern. This protocol needs a thin scientific driver only, not new runner infrastructure.

## Measurement and exact denominators

For every final image compute latent and seven-view features once from its reloaded pixels. Call unchanged `journal_bch_readout.detect_rgb` under alpha with `combined`, `semantic_only`, `perceptual_only`, and `none`; soft binding and roster size 1. Share those suspect features across modes, not source features. Also call beta in combined mode, with no evaluator payload target. Do not inject, replace or override any detector intermediate.

Use `journal_bch_analysis.endpoint` outside detection with the exact supplied q/h. Record A, S, Q, J, H and F for every applicable call; define D = Q and H. `none` D establishes exact readable delivery; `none` F is not an ownership endpoint. Preserve q_bound, routing, q/h decoded bits, both distances, soft semantic distance, the semantic content status, `instance_own_content_status`, and propagated instance content status. If extracted payloads/readability/routing differ across modes on identical cached inputs, stop with an implementation discrepancy. Modes disable predicates; they are not independently randomized detectors, and semantic status propagates into the instance status.

For each of RR, DR, RD and DD report fixed planned N=6, completed images, each quality envelope, Q/H/D, and F by mode. List all pair identities, including equal-q/equal-h coincidences, unavailable calls and delivery failures. Report conditional mode differences among exactly delivered, quality-qualified images as descriptive selected subsets alongside unconditional counts. Do not replace N=6 with the favorable subset in the main table. The 24 images and four modes are paired measurements, not 96 independent samples.

Reference the existing clean full-E3 positives and C0/beta negatives as historical controls without re-running or counting them as new observations. Report the 24 new beta calls separately. Zero beta detections is only the observed panel result, never a calibrated FPR bound.

## Predeclared useful-result criteria and interpretation

The positive-control gate is **six of six RR** complete, within both strict quality envelopes, D true, and combined F true, with at least one nonidentical RR image. Report how many are nonidentical; no general rewriting claim follows from idempotent controls. A missing RR is unresolved, not evidence that the binding rejected a genuine mark. A measured quality/delivery failure is a construction failure; delivered strict RR with F false is a constructed-positive rejection.

A **repeated incremental semantic-binding witness** requires the positive-control gate and at least **two distinct recipient pairs** whose DR images meet both strict quality envelopes, deliver exact supplied q/h, have qD != qR, pass perceptual-only F, and fail combined F specifically through the semantic content predicate while the instance's own predicate matches. The two-pair threshold avoids promoting a solitary illustrative case to the planned study conclusion; it is not a statistical significance threshold. Report a one-pair witness as one observed witness, below this criterion. Any beta A=true prevents an unqualified useful-result conclusion and is separately reported; it is not silently discarded.

The reciprocal RD contrast uses the corresponding delivered/quality-qualified cells with hD != hR, semantic-only F true and combined F false through the instance's own predicate. It is secondary and cannot substitute for the DR primary criterion. DD describes continuity with the old transfer construction; it is not required to reject on every pair because pairs were not selected for dissimilarity. A DR combined acceptance with exact donor q is a same-owner component collision observation, not automatic false attribution: the detector has no claimed source-reference input and q equality/similarity is not human semantics.

If the primary criterion succeeds, the strongest justified finding is that semantic binding adds a measured rejection on this public recipient-consistent reissue panel while retaining its constructed positives. This does not validate arbitrary-owner authentication, genuine donor attribution, T3 full acceptance, population security, semantic admissibility, an external-method advantage or article novelty. No new p-value or rare-event bound is appropriate.

If it fails because exact delivery or positive controls are inadequate, report that this construction did not resolve the ambiguity. If DR is delivered and quality-qualified yet never differs between combined and perceptual-only, report no demonstrated incremental semantic-binding value on this panel. Do not search new pairs, distances, severities or thresholds to force disagreement. Either outcome closes this study, retaining all negatives and failed constructions. Any follow-up scientific allocation must be justified from these results in a new prospective decision; this protocol authorizes no automatic sensitivity branch, H2, held-out run or baseline workaround.

## Execution envelope and provenance

One inclusive **1,800-second** local run, beginning before scientific imports/model loading and including construction, all measurements and serialization. At most 9 GiB allocated GPU, 10 GiB process RSS, at least 3 GiB available RAM, one science GPU process, USD 0. Use MAIN `.thesis-build/a6-science-venv/Scripts/python.exe` and cached models. No new downloads or paid resources. Process pairs in table order and cells by the shared-q schedule above. Finish every prescribed cell even if an early result is unfavorable, unless a resource or execution limit intervenes.

Commit protocol, driver and configuration before execution. Create one new development directory with run.json recording commit, command, frozen inputs/targets, schedule, actual step counts, outputs, per-cell status, duration, resource peaks and terminal reason, plus an ordinary dev-log entry. No hashes of every historical artifact or numerical replay are required. Preserve original receipts and images.

Nonfinite values, model/operation errors, resource breach or deadline end the run without a second launch, altered recipe or resume of a terminal study. Unstarted/partial cells remain explicitly missing; do not assign them zero-bit recovery, failed quality or successful rejection. A deadline near a model call is checked immediately on return, and any overrun is reported. Ordinary measured quality, delivery or predicate failures are results and do not trigger early termination. No protected-file edit, official lifecycle verdict, human assessment or external communication is part of this study.

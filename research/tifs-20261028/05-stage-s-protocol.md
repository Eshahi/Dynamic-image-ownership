# Stage S: frozen development screen for F6 finite noisy-codec writing

STATUS: PROTOCOL COMPLETE; scientific execution remains unauthorized and server rehearsal remains required.

This protocol implements the pre-output selection in [04-selection.md](04-selection.md) and [stage-s/frozen-config.json](stage-s/frozen-config.json). Those frozen numerical gates govern this screen; a discrepancy is an integration error to resolve and commit before outputs, never permission to choose the easier rule afterward. No experiment, model pass, image inspection or timing was performed for this document. A pass supports proposing fresh confirmation; it does not establish TIFS readiness or approve Stage C.

## Question, sources and experimental unit

Does the image-domain F6-noise writer improve original semantic-code retention through native regeneration over F5 and matched codec/generic controls, while preserving quality and the unchanged F5 content-consistency reader? It is a pixel writer with finite surrogates, not the proposal's latent insertion method, cryptographic authentication or proof of lawful ownership.

Use only the existing 60-source encoder-transfer development pool. The committed [source manifest](stage-s/source-manifest.json), SHA256 `0271095638bdcf680d3ba0aac10c0be3468ef408450dd23164b643dea402f463`, orders source UIDs by SHA256 of `tifs-stage-s-v1/20261028/` plus UID: first 16 screen donors, next 16 targets, next two rehearsal donors and next two rehearsal targets. These four partitions are mutually disjoint. Preserve original/canonical hashes and licence receipts; no Phase-B source or reserve is eligible. Rehearsal outcomes never enter the screen denominator. No replacement or source reordering follows an outcome.

A source is the efficacy unit. Fixed seeds 0, 1, 2 are repeated observations, not 48 independent images. A positive source majority requires at least two positives. Report per-seed rows and source-majority counts.

## Arms, writer and native cells

| Arm | Role and unchanged reader |
|---|---|
| F6-noise | Selected new writer, finite native-noise codec objective; F5 reader |
| F6-codec | Matched codec-only objective; F5 reader |
| F6-generic | Specified generic blur/resize/noise augmentation control; F5 reader |
| F5 r2 | Retained image-domain comparator and principal historical control |
| v5 r3 | Retained pixel comparator |
| WAM | Published known-message carrier control, 32 bits |
| VINE-R | Strong published regeneration carrier control, 100 bits |
| C0/unmarked | Same original image, no mark |

Every arm receives every native cell: SD1.5 (R0) .2, SDXL (R1) .1 and .2, Kandinsky 3 (K3) .2, each with all three seeds. This is 16 × 8 × 4 × 3 = 1,536 native attempts, 112 marked clean images, 16 original C0 images and 48 new-writer marks. Rehearsal adds 192 native attempts, 14 clean marks, two C0 and six new-writer marks; it exercises every downstream stage. VINE/WAM need not satisfy F5's C/J task, and an F6 pass does not imply superiority over their carrier retention.

Freeze writer parameters exactly as config: posterior mode for both codec arms; 150 clean-plus-surrogate updates cycling R0 .2/R1 .1/R1 .2 fifty times, followed by 50 clean refinements, two fragile writes, initial robust PSNR budget 52 dB, refinement 58 dB, margin 4, band 4–32, whitening 1, mask_power 0, soft binding and seven semantic views. Each codec writer uses 350 reader-gradient evaluations and 150 codec-gradient evaluations. F6-codec sets a=1, b=0; F6-noise uses the actual native first DDIM timestep's sqrt(alpha_bar), sqrt(1-alpha_bar), correct family latent scaling and no division by a. This deterministic-mode finite surrogate deliberately approximates native posterior sampling and excludes the denoiser. Differentiable resizing has no intermediate RGB8 rounding. Final saved RGB8 reads determine outcomes. F6-generic uses the same update/refinement schedule, cycling reflection-padded sigma 1.5 kernel 11 blur, bilinear 512→256→512 (align_corners=False, antialias=True), and independent RGB sigma .02 noise clipped to [0, 1]. It is a specified local control, not a reproduction of VINE training.

K3 is excluded from writer optimization and selection diagnostics, but historically observed: call it optimization-excluded, never discovery-unseen. No SD3/SD3.5 component enters Stage S. Keep native settings from stage 2b and Phase-A/B option-(a) classic kernels, native prompts/steps/guidance and preprocessing. R1/K3 use retained 512→1024→512 Lanczos paths. Record C0 random draws once per source/cell/seed and replay the full tape for each arm, with exact consumption checks. Changed draw structure is an error, not a seed substitution.

## Endpoints and side information

For the unchanged internal detector, report every endpoint separately:

| Endpoint | Frozen meaning |
|---|---|
| C | semantic.read AND current-suspect content_match |
| Q | semantic.read AND decoded q exactly equals evaluator's original q |
| J | Q AND current-suspect content_match |
| H | instance.read AND decoded h exactly equals evaluator's original h |
| D | Q AND H |
| F | operational detector outcome is both_match |
| A | semantic.found OR instance.found |

Original q/h are evaluator references only. Operational detection receives the suspect, claimed owner label, frozen profile/key/config and suspect-derived semantic features; it receives no original donor image, target q/h or registry. F5's h reference is its clean decoded value under the retained adapter; label that limitation, while preserving F6's intended/final references. Exact-target fields with missing references are unavailable, not demonstrated failures. A missing detector result is never an all-false observation. Also retain found/read distinctions, raw scores, bit errors and recomputed-only semantic indicators.

Positive owner is `qim-pilot-owner-alpha`; true wrong owner is beta. WAM/VINE use known public per-source messages with seed 20261019; wrong messages use 20261020. Retain inclusive exact-binomial random-bit threshold tail ≤ 1e-4 (VINE 69/100). These are known-message presence results with message side information, not owner/content binding; their C/Q/J/H/D/F fields are inapplicable. C0 gets all applicable internal readers plus external known-message tests; it is not an extra watermark reader.

## T4/T5 and negative inventory

Before marking, seal original-only CLIP nearest-unused-target assignments in donor order, with ties by ascending numeric source ID. Sixteen screen donors pair without replacement to 16 other targets; rehearsal 2+2 is separate. Never select neighbors using detection. Metadata/hash distinctness is not a human verdict of an operationally different near-copy.

For every marked arm and unmarked sham, primary T4 copies the published donor's centered 128 or 256 square into the corresponding target square at alpha 1. Matching unmarked-donor patch 128/256 shams share geometry. The attacker needs the published donor, recipient and public owner label. Separately report stronger-access residual transfer `clip(target + s*(marked_donor-original_donor))` at s=.5, 1, rounded once to RGB8: this uses the clean donor and cannot be relabelled as the public-patch threat. T5 is the unmodified target under the donor claim. These seven conditions (two patches, two shams, two residuals, one T5) across 16 pairs × 8 arms give 896 saved threat units before read modes; duplicate target/sham images may share storage but not erase query identities.

Read internal arms in combined, semantic_only, perceptual_only and none binding modes on the same saved suspects. Whole-recipient false-instance predicate is D AND F using donor q/h only for evaluator checks; primary operational results use combined. Report genuine donor-component detection separately: a composite really contains donor content. Eligibility requires PSNR>25 dB, SSIM>.75, LPIPS<.15 against original recipient, plus a supplied operational-distinctness label for an attribution conclusion. Report all attacks and quality eligibility; do not discard ineligible attempts from the attack accounting.

For candidate C0 and beta-owner calls require zero C or F events across applicable clean, native and threat queries. Secondary-distortion negatives are descriptive with zero selection weight. For quality-eligible T4/T5 require zero combined-mode D AND F whole-recipient false-instance events; semantic_only, perceptual_only and none modes are diagnostic with zero selection weight. Combined is the operational mode. An event in a diagnostic mode must be reported, but does not fail the primary security gate. Any observed qualifying primary event is a scientific failure; missing required primary negative reads prevent a complete specificity gate. The full secondary inventory remains required for a complete package even though its outcomes cannot change method selection. Human operational-distinctness labels remain MISSING until supplied: label binding generalization UNRESOLVED and do not claim zero false attribution from metadata. Retain numerical screen status and this separate binding-evidence status. Baseline false events are reported and do not automatically fail F6.

Report donor-carrier delivery, unconditional pair success, and delivery-conditioned acceptance with the same saved unit, arm, condition and read mode. Undefined zero-delivery denominators stay undefined. Low delivery cannot demonstrate strong binding. An any-query pair event clusters all scales/modes per donor/recipient pair; overlapping or repeated queries do not increase independent n. Even zero in 16 independent clusters has an individual one-sided 95% upper bound about .171; this screen cannot certify rare errors.

## Fixed article-only secondary distortions

Apply the following independently to each clean arm, including C0; never compose them with diffusion. Same seeded noise draw across arms of a source. Total 16 × 8 × 8 = 1,024 secondary attempts, plus 128 in rehearsal. Record native-sized input/output hashes and the full endpoint/quality tables separately; selection weight is zero.

| ID | Exact operation |
|---|---|
| jpeg90 / jpeg50 | PIL JPEG quality 90/50, subsampling 2, decode RGB |
| resize384 | PIL Lanczos 512→384→512 |
| crop90 | centered 485-square (floor(512 sqrt(.9))), Lanczos resize 512 |
| noise002 | independent RGB Gaussian sigma .02; stable_seed(secondary-noise, source_uid); clip and floor(x+.5) RGB8 |
| blur1 | PIL GaussianBlur(radius=1), extended-box approximation; not a discrete 7 × 7 convolution |
| brightness12 | PIL ImageEnhance.Brightness factor 1.2 |
| contrast12 | PIL ImageEnhance.Contrast factor 1.2 |

Report per-transform retention, bit accuracy, C/Q/J/H/D/F/A where applicable, external presence, quality against original and clean marked reference, missingness and source-cluster uncertainty. No favorable distortion average repairs a failed T3 gate.

## Frozen decision and failure handling

For both C and J independently, F6-noise must have ≥ 12/16 lower source majorities in each foreign cell. Candidate-lower count minus comparator-upper count must be ≥ 4 against F5 in each SDXL cell and ≥ 3 in K3; ≥ 3 against each new ablation in each SDXL cell and ≥ 1 in K3. On R0 .2 conservative loss against F5 is ≤ 1. Lower majority uses observed positives only; upper majority allows unresolved seeds positive. Preserve the paired source tables even though these fixed screen bars use net counts.

Every source of every new writer must pass strict clean PSNR>35 dB, SSIM>.9, LPIPS<.1; every new writer clean F ≥ 15/16. F6-noise minus F5 paired median clean LPIPS ≤ .005 and PSNR ≥ −1 dB. Missing/nonfinite metrics cannot pass. Publish all arms' clean and post-regeneration quality distributions against both original and marked references; human quality stays MISSING until supplied.

GO requires every numerical gate and complete required negative evidence; report binding-label limitations alongside it. A gate conclusively failed under even optimistic completion is SCIENTIFIC_KILL. A demonstrated memory/time infeasibility is RESOURCE_STOP. Missingness with no conclusive failure is INCOMPLETE. Maintain separate flags if both failure and incompleteness occur. No partial inventory GO. Safety-blocked/error-terminal outputs retain fixed identity and missingness; never change prompt/seed or bypass safety. Infrastructure retry may repeat the identical unfinished operation under journal rules, never a different scientific draw. Hash/config/manifest mismatch stops resume.

## Server sequence, resources and handoff

Only a later user-authorized server run may load scientific libraries or assets. First verify pinned assets/software, manifests, device total/free/reserved/allocated memory and disk. Then original-only pair sealing; disjoint 2-source rehearsal through all writers/families/reads/metrics/threats/distortions; complete resource forecast; full marks; native families serially; endpoint/quality/negative release; separate secondary stage; inventory/analysis; collection. Release graphs and GPU models between families. K3's approximately 21.7 GB prompt encoder requires no writer, reader or LPIPS resident. Begin conservatively with serial readers; report actual memory telemetry, not allocated-only fit.

Retained Phase A took 7.3 instance-hours for a different mechanism study, and Phase B 27.2 instance-hours for 200 sources and 17,686 successful native outputs (plus safety blocks); the latter includes work absent here and omits F6/SD3.5. The reuse audit cites historical F5 writing 119 s/source: 16 F5 marks alone suggest about .53 h, not an F6 forecast. Earlier reuse arithmetic used obsolete n 24/seven-arm inventories and must not be reused. No measured F6 time exists. Stage-specific expected durations are therefore UNQUALIFIED until rehearsal; diffuse-output scaling alone is inadequate.

Require measured one-time/setup plus paid rehearsal plus 1.5 × the complete remaining per-operation inventory forecast plus 3,600 s retrieval reserve ≤ 54,000 s (15 hours). Measure all three new writers, comparator writes, native families, reads, metrics, threats, distortions, hashes and loading. Maintain reserve for next uninterruptible unit and retrieval at each checkpoint. If any operation lacks a conservative measured bound, do not launch. At indicative $.45–.60/h the ceiling is $6.75–$9 excluding separately charged storage/network; actual user-approved price governs. Cheap fallback is preserve the intact screen and report resource NO-GO/redesign proposal, not shrink n/steps/arms after outcomes or automatically run the backup.

Old core assets were estimated 48.6 GB on 76 GB total disk, so nominal 27.4 GB remainder is not free-space evidence. Stage S adds no new model family. Inventory includes 1,536 native + 1,024 secondary + 896 threat units plus 128 clean images and rehearsal, tapes/logs/packages. One 512 RGB8 raw frame is 786,432 bytes (PNG size is unknown); these main image units alone are about 2.82 GB uncompressed, excluding tapes/native intermediates. Measure actual file/tape sizes and temporary peaks in rehearsal; require complete projected occupancy plus 20% filesystem margin below actual free space. Preserve retained outputs, and do not infer cleanup permission.

Deliver raw journals, original assignment seal, config/source/asset/code hashes, RGB8/output hashes, status/safety rows, complete expected-versus-observed inventory, memory/time/resource forecast, per-seed/source tables, conservative gates, secondary table and missingness report. Server runbook supplies commands; syntax/pure-logic checks here do not establish gradients, native equivalence, numerical validity, runtime or GPU fit. No paid execution approval is inferred from this protocol.

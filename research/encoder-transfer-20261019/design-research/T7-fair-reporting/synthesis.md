# T7: fair comparison and frozen reporting contract

Pre-outcome design research, 2026-10-19. No model, image, watermark, detector, or new outcome was run. This extends T1/T3 and the dossier, rather than reopening baseline selection. All numerical calipers below are design choices, not published universal perceptual-equivalence thresholds. Source provenance and inspection levels are in `manifest.json`; search coverage is in `search-log.md`.

## Decision and scope

Keep the immutable primary: F5 r2, R1 SDXL .2, source-majority C, n=60. A source succeeds with at least two of seeds 12/13/14. TRANSFERS requires at least 45 successes and the stipulated zero F5 C0/wrong-owner detections across R1; FAILS is below 30; otherwise PARTIAL. Apply the external margin of three exactly as the brief specifies. None of the quality matching, ROC calculations, intervals, or exploratory tests below can change this decision.

Core reporting covers native F5 r2, v5 r3, WAM SA-1B MIT at scaling_w=2, and VINE-R with 100 random bits. R0/R1 .1/.2/.4 use seeds 12/13/14. D1 is one deterministic SDXL VAE posterior-mode round trip at 1024 per source/arm. Separate one- and two-cycle Lanczos-only controls quantify 512→1024→512 resampling. The single SDXL rinse uses .1 followed by .1, seeds (12,112), (13,113), (14,114); first-pass R1 .1 outputs are reused. Do not treat the second pass as an independent replicate or assume .1+.1 has the severity of .2. FLUX is excluded because its access condition failed; Kandinsky is an optional costed proposal, not a core result column. Diagnostics, rinse, and every nonprimary cell are descriptive.

## What the literature supports

[WAVES](https://arxiv.org/html/2401.08573v3) motivates joint robustness–quality plots and low-FPR reporting. [W-Bench/VINE](https://arxiv.org/html/2410.18775v2) uses native released checkpoints, a common 512 image size, and separate quality and detection metrics. These are benchmark practices, not a guarantee of acceptance by a Q1 journal. We adopt their reporting principles, not their leaderboard, dataset scale, aggregate attack distribution, or numerical ROC calibration.

Use separate PSNR/SSIM/LPIPS panels. Do not call a three-metric average “WAVES NQD”: its published aggregate has four metric categories and a normalization distribution absent here. Do not estimate FID on 60 sources as a replacement for paired fidelity. Detection, content binding, exact-message recovery, and bit accuracy are separate outcomes. The 2026 WAW and DRIFT extensions reinforce that distinction and the need to identify adaptive choices explicitly; the present study has no detector-guided attack search. See the three source cards for bounded evidence.

## Endpoint and capacity fairness

| Arm | Embedded representation | Fixed reported operating point | Interpretation and side information |
|---|---|---|---|
| F5 r2 | Content-derived q32 in robust latent-read tier; H32 in fragile tier; 320 carrier chips per tier | Frozen S/C/Q/J and other step-1 predicates; primary C | Image-domain optimized writer; claimed owner, public profile, pinned CLIP and SD1.5 VAE; C is semantic-bound detection, not arbitrary-message or both-code exact recovery |
| v5 r3 | Same two structured 32-bit codes, 320 chips per tier | Frozen step-1 predicates | Image-domain comparator; owner/profile/CLIP, its image-domain carrier; preserve exact existing side-information fields |
| WAM MIT | Native 32 arbitrary message bits, full-image message | Common known-message presence: matches ≥27/32; native zero-bit image detection: mask fraction >.07 using pixel probability >.5 | Known candidate message for common point; no candidate message for native mask-only point; empty masks abstain |
| VINE-R | Native 100 arbitrary message bits | Common known-message presence: matches ≥69/100; raw bit accuracy/exact recovery; descriptive empirical ROC | Known candidate message; no universal fixed native numeric presence threshold in released evaluation |

F5 is **not a 128-bit message scheme**. Verified directly in `scripts/revised_watermark_v5.py` constants CODE_BITS=32, SEGMENT_CHIPS=10, CHANNEL_CHIPS=320, and `scripts/f5_latent_codec.py` robust/fragile construction. The 128 value is v5's coarse spatial grid side, not payload length. q and H are functions of content, not independent uniformly random payloads; do not market their sum as 64 arbitrary information bits or infer capacity from carrier chips. The reader does not use an enrolled reference image for this transfer endpoint; any later registry-assisted result must identify that additional side information separately.

The common thresholds have nominal one-sided Binomial null tails 0.00005653710104525089 (WAM) and 0.00009157161244117683 (VINE). These are random-message-null calculations, not measured image FPR or identical real operating characteristics across arms. WAM's published native mask operating point was calibrated with different training/data conditions; applying it to the MIT model does not transfer that calibration. Use T3's pinned decoder/quantization semantics exactly. Native quality remains fixed: no WAM strength sweep, VINE variant swap, residual scaling, capacity reduction, F5 retuning, or best-looking seed selection.

## Quality ledger and denominator rules

Let x_i be canonical RGB8 source, w_ia the saved/reopened native mark, and y_iacs the final saved/reopened 512 output. Use the same pinned metric implementation for all arms.

1. **Embedding distortion:** d(w_ia,x_i). One observation per source and arm, planned 60. Report median, Q1/Q3, extrema, observed/planned count, and strict quality-gate count. F5 gate is PSNR>35, SSIM>.9, LPIPS<.1, all strict. Report this same descriptive predicate for other arms without claiming it is their native requirement.
2. **Attack distortion:** d(y_iacs,w_ia). This is the main severity comparison. For C0, reference x_i. Rinse uses the original mark as its primary reference, not merely the first-pass image; retain second-pass-versus-first-pass as an explicitly incremental diagnostic.
3. **Total distortion:** d(y_iacs,x_i). Report separately; useful because otherwise a large native embedding cost is hidden. Never subtract LPIPS or SSIM values to infer attack cost or add them as if distances were additive.

For a stochastic cell, the plotted x coordinate is the median across sources of the within-source median over its three seeds, using only sources with all three valid metric observations. Report that count alongside the planned 60 sources/180 outputs, plus pooled available-output median as a separately named descriptive statistic. Do not compute source-majority from only surviving seeds: missing/blocked positives remain failed attempts. Quality of a missing image is NA, never zero/perfect. No source is removed from primary survival because quality was missing or poor. All blank metrics carry a reason and count.

PSNR can legitimately be +infinity for identical inputs. Preserve that fact using explicit serialization/status rather than clipping; do not feed nonfinite values into matching. For finite metrics, quantiles use linear interpolation at index (m−1)p over sorted observations, fixed p=.25,.5,.75. Matching uses full stored precision, not rounded display values. Pin RGB range, SSIM channel/window behavior, LPIPS network/weights/normalization, versions, image resolutions, and PNG round trip in the protocol.

## Finite-grid matched-distortion analysis

This is descriptive postprocessing of a predeclared finite set, not attack optimization. The original complete-grid table is mandatory even if no pairs match. Same numeric strength and matching cell medians are insufficient to claim matched distortion.

**Fixed comparison families:** (i) F5 versus each of v5/WAM/VINE within R0 and within R1; (ii) R0 versus R1 within each of the four arms. The candidate strengths on each side are only {.1,.2,.4} actually planned and run. Diagnostics and rinse are excluded from this grid; their direct paired fixed-setting contrasts are shown separately. If a setting is budget-dropped, mark it unavailable and never replace it with a new strength.

**Match algorithm, separately for each comparison and bin:**

1. Fixed attack-LPIPS bins: [0,.05), [.05,.10), [.10,.20), [.20,.30), [.30,.50), [.50,+∞). No empirical quantiles, merging, or changed edges after outcomes.
2. Within each source i, enumerate the at most nine pairs of strength settings. Both sides need all three outputs and all finite PSNR/SSIM/LPIPS metrics; use each side's within-source median quality vector. Both LPIPS medians must lie in the same target bin.
3. Require all absolute differences to satisfy: LPIPS≤.02, PSNR≤1 dB, SSIM≤.02. Choose the candidate minimizing (ΔLPIPS/.02)^2+(ΔPSNR/1)^2+(ΔSSIM/.02)^2. Break exact ties lexicographically by the two numeric strengths, lower first. No outcome, detection score, C0 score, bit accuracy, or success label participates in selection.
4. Retain at most one pair per source per bin. Join its two fixed source-majority outcomes only after matching. A source may contribute to more than one bin but never more than once within a bin. Do not pool bins into an apparently larger independent sample.
5. Report m/60 matched sources, exclusions for missing/nonfinite metrics and lack of overlap, the selected strength-pair frequency table, all three actual quality-difference distributions, both success counts /m, paired difference (A−B)/m, discordant counts, and ties. m=0 prints **“No matched overlap; comparison not estimable.”** m<20 prints **“Sparse matched subset; descriptive counts only.”** Never relax calipers to obtain a favorable/nonempty result.

These are approximate matches within stated tolerances. Conditioning on achieved quality changes the target source subset and may select different attack strengths per source; it does not estimate a causal encoder effect or a full-population superiority guarantee. The matching is symmetric and blind to detection, but that does not remove this selection limitation. Do not interpolate, extrapolate, assume monotonicity, or select the lowest-quality attack that happens to fail.

**Embedding-quality qualification:** a single native embedding point per arm cannot supply an equal-quality embedding frontier. Alongside attack-only matched pairs, report a stricter subset requiring native embedding differences ≤1 dB PSNR, ≤.01 SSIM and ≤.01 LPIPS for the same source. Use the same chosen attack pair (do not rematch to improve success). Label it “native embedding + attack approximate match.” If it is empty/sparse, explicitly state that matched native-quality superiority remains unestablished. Across channels within the same arm this added condition is automatically identical. Route B's potential quality/capacity/cost explanation is therefore a hypothesis until supported; native quality medians alone do not prove it.

**Uncertainty:** the integrated design retains only the three primary paired exact sign tests with Holm adjustment from T6. Matched bins have counts, paired differences and discordants, with no additional tests or significance stars. This resolves the draft's proposed extra matched-bin tests before outcomes. No seed-level bootstrap or pixel-level confidence interval is used. Marginal CP intervals on the full source endpoint grid remain exploratory under the stated exchangeability assumption.

## Low-FPR empirical ROC, separately labelled

For WAM/VINE only, compute per-cell raw known-message agreement scores on C1 and paired C0 outputs. WAM also gets a separate native mask-fraction ROC. Do not create an arbitrary continuous surrogate for F5's compound C predicate; retain its frozen operating point. Scores from different endpoints cannot be placed on an unlabeled common leaderboard.

For an empirical ROC sweep, predict positive iff score≥threshold, evaluate every distinct observed finite score plus a reject-all sentinel, keep tied scores as indivisible blocks, and perform no interpolation/random tie splitting. Choose the lowest feasible threshold (maximum TPR) whose empirical FPR is **strictly less than** .001 or .01, matching the released W-Bench evaluation convention. If several thresholds have equal TPR/FPR, report the largest threshold among that equivalent pair. Record the chosen threshold, positives/negative counts, numerator, denominator, and achieved FPR. This outcome-dependent ROC summary is descriptive only and is never exported back to common fixed-threshold detection.

Provide two explicitly different views: (a) image-output ROC, planned 180 positives/180 negatives per stochastic cell (three correlated outputs/source); (b) source-majority ROC using each source's median score over three seeds, 60/60, equivalent to at least two seed scores crossing a threshold. Clean and deterministic controls have 60/60 and only one view. Do not pool channels or strengths to manufacture low-FPR resolution. A VINE/WAM missing positive counts as a failed attempt at every finite threshold; an empty WAM mask is a defined abstention and cannot become a positive even at threshold zero. A missing/unresolved negative makes that ROC view **incomplete/not estimable**, not a presumed true negative. The reject-all point remains (0,0).

At 60 sources, the first positive empirical FPR is 1/60≈.0167: both targets select a zero-observed-FP point. At 180 outputs, the resolution is 1/180≈.00556: .001 still allows zero, .01 permits at most one false positive; these are not 180 independent sources. The zero-of-60 one-sided 95% binomial upper limit is about .0487 under independent-source sampling, vastly above .001. Report no validated .1%, .01%, or universal FPR claim. Frozen-threshold negatives should additionally report source-any-false-positive counts, preserving all seed and owner dependence. Do not attach naive CP confidence limits to the data-selected ROC points.

## Tables and figures to implement

| ID | Mandatory content |
|---|---|
| Table 1 design/operating points | Arms, exact revision, native payload semantics, embedding setting, readout side information, native and common rules; channels, internal/output resolution, steps actually executed, prompts, seeds, controls |
| Table 2 primary decision | F5 C and each comparator's stated endpoint at R1 .2: successes/60, missing/blocked, CP interval, pairwise discordants; F5 negative completeness/counts; external B and margin3; literal decision/route; no quality-selected denominator |
| Table 3 full endpoint grid | Every arm/channel/strength/control including clean/D1/resize/rinse, source-majority k/60 and per-output k/180 separately; F5/v5 S/C/Q/J; WAM native/common/exact; VINE common/exact; bit-accuracy quantiles with empty/missing counts |
| Table 4 quality | Embedding, attack, total PSNR/SSIM/LPIPS separately; source-level median/IQR, observed/planned counts, native strict-quality pass count; no blended scalar |
| Table 5 negatives and ROC | C0, wrong-owner, wrong-message distinct; fixed operating counts and source-any-event counts, unresolveds; ROC threshold/achieved FPR/counts/resolution/view; not a calibration guarantee |
| Table 6 approximate matching | Every fixed pair×LPIPS bin including empty bins, source overlap, selected strength pairs, residual quality differences, matched success/discordance; separate clean-quality-qualified subset |
| Table 7 cost/provenance | Hardware, precision/software pins, per-arm embedding/extraction wall time and peak memory; channel regeneration wall time; warm-up/download/setup/item timing separated; attempted/successful counts and retry costs, total dollars/hour cap |
| Table 8 historical context | Original step-1 population/seed/definition next to this study; do not pool 24-source SD2.1 with 60-source SDXL or attribute differences solely to encoders |
| Figure 1 | Source-majority success versus finite strengths for R0/R1 with arm/endpoint legend, CP bars, 60-source denominator; visually flag R1 .2 primary; diagnostics/rinse separate symbols/panel |
| Figure 2 | Three robustness–attack-quality panels: x=source-summary PSNR, SSIM, LPIPS; y=source-majority fixed-endpoint rate, labeled strength and observed quality-source count; thin segments connect measured settings only, no smooth curve or interpolation claim |
| Figure 3 | Clean native-quality distributions (source dots plus median/IQR), one panel/metric, payload/endpoint differences in caption; no equal-quality claim |
| Figure 4 | Matched-bin paired differences and overlap m/60; empty bins explicit; dual-quality-qualified subset distinct; no pooled effect or inferential stars |
| Figure 5 | Empirical ROC step plots for WAM/VINE known-message and separate WAM mask scores, cell/view faceting, strict .001/.01 reference lines and resolution notice; F5 C shown only as a labelled fixed point elsewhere |
| Figure 6 | D1/resize1/resize2/rinse versus their defined parent controls; show complete counts and distortion; no seed duplication for deterministic controls |
| Figure 7 | Fixed illustration panel: first six final-list source IDs, all arms, seed12 for R0/R1 .2 and the prescribed rinse pair; same crops/scales; failures shown as missing tiles; unamplified images and uniformly labelled ×10 absolute residuals; human imperceptibility verdict remains missing |

All plots are generated from the same metrics ledger as tables, preserve NA/failure counts, and use literal descriptive titles. No best-case examples or outcome-based selection. Additional appendix plots may show all fixed sources, not a selected success montage.

## Allowed conclusion

Route A means that a method-led article remains viable under the brief's development criterion, not Q1 readiness, novelty, cryptographic security, legal ownership, a universal FPR, or robust transfer to all independent encoders. Route C is evidence bounded to the tested SDXL configuration, not a theorem that all independent encoders erase F5. R0/R1 comparisons contain a resolution and model-family intervention as well as encoder change; D1 and resize controls narrow but do not eliminate attribution ambiguity. The fixed primary is evidence about this finite consulted development set. Confirmation, broader baselines, adaptive attacks, and a genuinely matched embedding-quality frontier remain separate work requiring the authorized next decision.

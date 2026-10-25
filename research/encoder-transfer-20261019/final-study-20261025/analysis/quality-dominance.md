# Individual-output quality dominance on retained development records

Status: post-hoc descriptive author sensitivity, 2026-10-25, outside completed WP6/E3 reviews. No new images, detections or metrics were computed. This analysis does not amend the prospective protocol, the retained transfer verdict or the matched-quality calipers.

## Main finding

For F5, **all177 complete same-numeric-seed pairs** have strictly better saved LPIPS, PSNR and SSIM under SDXL .1 than SD1.5 .2. **170/177 pairs** change from compound C positive under SD1.5 to negative under the quality-superior SDXL output. These contradictions occur on **58/60 sources** with at least one available pair. Three scheduled pairs are incomplete because of preserved R0 safety blocks; the remaining seven complete pairs have no positive-to-negative transition. Counts are identical when quality is measured against the marked input and when measured against the original image.

Considering every source-local seed pairing, all531 complete pairs show the same strict three-metric quality ordering, and510 show the positive-to-negative transition. These reuse the same outputs; **531 is not a sample size of independent images, and510 is not additional evidence independent of170**. Numeric seed equality across native pipelines does not establish the same noise tensors.

Among the58 sources with all six outputs complete, there are168 contradictions among174 same-label pairs, on57 sources. This is compatible with the earlier **56/58 source-majority transitions**: a source with one positive R0 output can contribute a per-output contradiction while failing the majority endpoint. The source-summary, output-pair and source-any denominators must not be interchanged.

## Complete planned results

R0 means SD1.5 .2; R1 means SDXL .1. A contradiction means R1 strictly improves all three recorded qualities, but R0 is positive and R1 negative. F5/v5 positivity is compound semantic C; WAM/VINE positivity is their known-message presence. These are separate endpoints, not a fair-method leaderboard.

| Arm | Quality reference | Pairing | Complete / scheduled pairs | R1 strictly milder | Contradictions | Sources with contradiction /60 |
|---|---|---|---:|---:|---:|---:|
| F5 | Marked input | Same label |177/180|177|170|58|
| F5 | Marked input | All local |531/540|531|510|58|
| F5 | Original | Same label |177/180|177|170|58|
| F5 | Original | All local |531/540|531|510|58|
| v5 | Marked input | Same label |179/180|175|7|7|
| v5 | Marked input | All local |537/540|525|20|8|
| v5 | Original | Same label |179/180|171|7|7|
| v5 | Original | All local |537/540|515|20|8|
| WAM | Marked input | Same label |178/180|178|5|3|
| WAM | Marked input | All local |534/540|534|13|3|
| WAM | Original | Same label |178/180|175|2|2|
| WAM | Original | All local |534/540|526|5|3|
| VINE-R | Marked input | Same label |178/180|176|0|0|
| VINE-R | Marked input | All local |534/540|531|0|0|
| VINE-R | Original | Same label |178/180|173|0|0|
| VINE-R | Original | All local |534/540|521|0|0|

Reverse contradictions, where a quality-superior R0 is negative and R1 positive, are zero in every row. Absence of contradictions for an arm does not prove a quality-only explanation.

Across all510 F5 contradictory local pairs, the **minimum** quality advantages for SDXL are: against marked input, LPIPS reduction .018122, PSNR gain3.087704dB and SSIM gain .040955; against original, .037142,3.083391dB and .030764. These are separate coordinate minima, possibly attained by different pairs. They show that the strict inequalities are not merely tiny last-digit ties in these saved values; they are not calibrated perceptual margins or human preference measurements. Full minimum/maximum bounds and complete-source-subset results are in the JSON.

## What this strengthens, and what it does not

The [aggregation note](quality-aggregation-boundary.md) proves that median-quality dominance plus majority-endpoint reversal alone would not establish a per-output contradiction. The newly inspected saved-output comparisons close that particular gap for F5. They rule out an exact deterministic coordinatewise-monotone mapping from these three recorded metrics to the observed endpoint on these outputs, even allowing a separate mapping for each source.

They do **not** rule out arbitrary nonmonotone quality functions, probabilistic monotone models, other unmeasured perceptual variables, detector-specific information or metric uncertainty. They do not identify encoder training as the cause, compare interventions at matched quality, establish a population rate, or create a confirmatory result. The caliper overlap remains only two F5 sources. No p-values are assigned to the overlapping pairs.

A subsequent [exact empirical loss bound](monotone-brier-bound.md), with its own committed premise check, quantifies the complete-subset limitation: every monotone probability score has Brier loss at least 563/2320, and every monotone binary classifier has error at least 14/29, attained by always predicting non-detection. This bound concerns realized marked-output metrics and cannot be applied to the unrestricted, differently informed primary H4 comparator.

## Provenance and execution receipt

- [Plan](quality-dominance-plan.md) and [stdlib-only code](quality-dominance.py) committed before this aggregation as `a2fb944`; existing outcomes were already known, so this ordering is not fresh-data preregistration.
- Input: MAIN `.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl`; SHA-256 `f3b95d3e727d421c29a2a2e42eb1ef5881f55b7d3eb848a237ab51095455fb82`, identical to the earlier WP2 input receipt.
- Last-record-per-ID processing:39,896 journal lines,11,040 final identities,11,017 ok and23 safety-blocked. Selected contrast:1,440 records,1,432 ok and8 blocked. No failure deleted or replaced.
- Executed once at approximately17:51UTC with MAIN `.thesis-build/venv/Scripts/python.exe -I`, completing in under15minutes. Only Python standard-library CSV/hash/JSON/arithmetic operations on saved records were used. No scientific interpreter, model, image, metric or detector was invoked.
- Outputs: [aggregate JSON](quality-dominance.json), [960 per-source summary rows](quality-dominance-sources.csv). Code validates duplicate scientific keys, source count, finite metrics, Boolean endpoints and both detector/quality statuses. Root inspected the code, all16 aggregate rows and F5 gap/subset details. This is author verification, not an extension of either completed independent review.

# Negative-background score analysis

## Plan frozen before reading the raw journal

Prepared 2026-10-25. This is post-hoc AUTHOR analysis of already-known development outcomes. The known aggregate is F5 semantic failure under SDXL, zero F5 negative detections, and one VINE-R C0 detection at 69/100 (source 1295, seed 14). No new endpoint, threshold, model, metric or experiment is introduced.

Read the journal with last record per id; join C1 and C0 by cell/source/base-seed. Inspect internal semantic and instance saved recomputed and decoded score-minus-threshold margins separately. For each cell, method and query type, report exact call coverage and source maxima with available/complete source denominators. Use unique C0 calls per method rather than duplicating them for each marked arm context. Compare matched C1-minus-C0 scores, with per-source seed medians and maxima as descriptive summaries. Compare right and wrong owner on the same marked row to examine query specificity. Summarize saved VINE-R negative bit accuracy relative to its fixed native threshold. Preserve blocked/missing calls, diagnostic/native cell distinctions and rinse base seed labels (second pass adds 100 internally). No fitted model, resampling, tuning or causal inference. Quantiles use linear interpolation. Raw scores describe detector alignment, not absolute carrier energy; C0/wrong-owner Q/H are uninformative by construction.

Analysis and limitations follow after extraction.

## Results

Journal reduction: **39,896 lines -> 11,040 last-state units**, 11,017 ok and 23 safety blocked, covering 60 sources. No saved found/read predicate inconsistency was found. All scores below come from saved detector calls; no images or models were opened.

Each native regeneration cell schedules 180 calls (60 sources x 3 dependent seeds); clean and D/X diagnostics schedule 60. R1, R3, rinse, mode and smooth calls have full score coverage. C0 is counted once per method/cell/source/seed, even though the same unmarked image is queried by several methods. C0 and wrong-owner call types remain separate, as do semantic and instance tiers. Wrong-owner queries here are beta on the method's own marked arm, not all cross-arm combinations.

### Do losses approach background?

Yes, descriptively, with residual score displacement. F5 semantic decoded alignment loses most of its separation from C0 under SDXL. Its paired **median over 60 complete source seed-medians** of C1-minus-C0 score is 12.068 clean, 1.989 at R1 .1, 0.919 at .2 and 0.342 at .4. The matched v5 values are 13.420, 6.485, 3.761 and 1.810. These are paired scores, not differences between unpaired medians. There is no equivalence test and no claim that the distributions become identical.

F5 semantic decoded C1 call-median score-minus-threshold is +7.033 clean and -2.749/-3.946/-4.342 under R1 .1/.2/.4; C0 medians are -4.866/-4.784/-4.755 there. Thus low positive results coexist with negative backgrounds far below threshold, rather than a negative background rising to trigger detections. At R1 .1, the largest F5 semantic decoded margin is +1.000 even though C source-majority is zero: decoded readability alone does not establish content compatibility or original payload recovery. At .2 and .4 even the largest decoded margins are below zero (-1.016 and -2.001).

F5 instance decoded C1-minus-C0 separation remains 6.011/4.064/2.290 at R1 .1/.2/.4. Its surviving instance alignment is not latent semantic survival; endpoint A is the union of semantic and instance found. F5 D1/D3 semantic displacements remain 9.501/9.982, while full R3 gives 2.468; this is a descriptive pipeline contrast, not an isolated encoder mechanism.

### Do wrong-owner margins show query specificity?

Right-minus-wrong semantic decoded source-median differences for F5 are 12.710 clean and 2.821/1.528/0.969 at R1 .1/.2/.4. For v5 they are 13.386 clean and 6.861/4.135/2.128. These are descriptive query-specific score contrasts below threshold in the failed cells, not causal or carrier evidence. They do not imply a successful owner test, lawful ownership, independent channels, or universal specificity against other keys. F5 wrong-owner semantic backgrounds are slightly lower than its C0 backgrounds; marked versus unmarked content can alter alignment, so those two negative controls are not interchangeable.

### Fixed-threshold negative margins, both branches

The table gives the greatest saved margin across all cells and both negative query types. Every maximum is negative. Found is the OR of branch tests, while read uses decoded only; inspecting decoded margins alone would miss a recomputed-only false event. In fact both channels have zero found/read negatives for both internal methods.

| Method | Tier | Maximum decoded margin | Maximum recomputed margin |
|---|---|---:|---:|
| f5-r2 | semantic | -2.616 | -1.848 |
| f5-r2 | instance | -2.095 | -1.712 |
| v5-r3 | semantic | -2.599 | -1.295 |
| v5-r3 | instance | -1.999 | -1.482 |

### Per-cell semantic decoded source maxima

Each median below is over source-wise maximum margins. Complete-source restriction requires every scheduled seed. Coverage columns give observed calls/expected calls and complete sources/60 for C0 and wrong owner, respectively. Source maxima account for within-source repeated queries descriptively; they are not independent false-positive trials. Native cells are R0/R1/R3; clean, D/X, rinse/mode/smooth remain separately labelled diagnostic contrasts.

| Method | Cell | C0 coverage; complete sources | C0 median source max | Wrong coverage; complete sources | Wrong median source max |
|---|---|---|---:|---|---:|
| f5-r2 | D1 | 60/60; 60/60 | -5.012 | 60/60; 60/60 | -5.713 |
| f5-r2 | D3 | 60/60; 60/60 | -4.914 | 60/60; 60/60 | -5.750 |
| f5-r2 | R0@0.1 | 178/180; 59/60 | -4.734 | 179/180; 59/60 | -5.615 |
| f5-r2 | R0@0.2 | 178/180; 58/60 | -4.694 | 177/180; 58/60 | -5.455 |
| f5-r2 | R0@0.4 | 178/180; 58/60 | -4.438 | 178/180; 58/60 | -5.253 |
| f5-r2 | R1-mode@0.2 | 180/180; 60/60 | -4.531 | 180/180; 60/60 | -5.256 |
| f5-r2 | R1-rinse@0.1 | 180/180; 60/60 | -4.680 | 180/180; 60/60 | -5.038 |
| f5-r2 | R1-smooth@0.2 | 180/180; 60/60 | -4.592 | 180/180; 60/60 | -5.237 |
| f5-r2 | R1@0.1 | 180/180; 60/60 | -4.582 | 180/180; 60/60 | -5.079 |
| f5-r2 | R1@0.2 | 180/180; 60/60 | -4.489 | 180/180; 60/60 | -4.963 |
| f5-r2 | R1@0.4 | 180/180; 60/60 | -4.307 | 180/180; 60/60 | -5.006 |
| f5-r2 | R3@0.2 | 180/180; 60/60 | -4.597 | 180/180; 60/60 | -4.932 |
| f5-r2 | X1 | 60/60; 60/60 | -5.054 | 60/60; 60/60 | -5.793 |
| f5-r2 | X2 | 60/60; 60/60 | -5.045 | 60/60; 60/60 | -5.778 |
| f5-r2 | clean | 60/60; 60/60 | -5.021 | 60/60; 60/60 | -5.775 |
| v5-r3 | D1 | 60/60; 60/60 | -5.120 | 60/60; 60/60 | -5.173 |
| v5-r3 | D3 | 60/60; 60/60 | -5.120 | 60/60; 60/60 | -5.162 |
| v5-r3 | R0@0.1 | 178/180; 59/60 | -4.600 | 180/180; 60/60 | -4.704 |
| v5-r3 | R0@0.2 | 178/180; 58/60 | -4.491 | 179/180; 59/60 | -4.614 |
| v5-r3 | R0@0.4 | 178/180; 58/60 | -4.467 | 178/180; 58/60 | -4.681 |
| v5-r3 | R1-mode@0.2 | 180/180; 60/60 | -4.580 | 180/180; 60/60 | -4.651 |
| v5-r3 | R1-rinse@0.1 | 180/180; 60/60 | -4.117 | 180/180; 60/60 | -4.913 |
| v5-r3 | R1-smooth@0.2 | 180/180; 60/60 | -4.551 | 180/180; 60/60 | -4.600 |
| v5-r3 | R1@0.1 | 180/180; 60/60 | -4.587 | 180/180; 60/60 | -4.738 |
| v5-r3 | R1@0.2 | 180/180; 60/60 | -4.631 | 180/180; 60/60 | -4.743 |
| v5-r3 | R1@0.4 | 180/180; 60/60 | -4.569 | 180/180; 60/60 | -4.629 |
| v5-r3 | R3@0.2 | 180/180; 60/60 | -4.564 | 180/180; 60/60 | -4.419 |
| v5-r3 | X1 | 60/60; 60/60 | -5.044 | 60/60; 60/60 | -5.229 |
| v5-r3 | X2 | 60/60; 60/60 | -5.074 | 60/60; 60/60 | -5.201 |
| v5-r3 | clean | 60/60; 60/60 | -5.049 | 60/60; 60/60 | -5.231 |

Full source-max distributions (min, p05, median, p95, max), both available and complete-source versions, call distributions and coverage for **both tiers and both branches in every cell** are in `negative-background-analysis.json`. Paired comparison missingness is separately recorded there; under R0 the paired C1/C0 calls are F5 177/176/177 and v5 178/177/177 at .1/.2/.4. Missing is never changed to a zero score or a negative.

### VINE-R native fixed-threshold negative background

The saved native 100-bit threshold is 69/100, inclusive. Across 4,191 available C0 plus wrong-message scores in these cells, exactly one crosses it: C0 R1 .1, source 1295, base seed 14, accuracy .69, margin zero. Its R1 .1 C0 cell has 180/180 scores: median .49, p95 .57, maximum .69. Across the 60 complete source maxima the median accuracy is .52, p95 .59 and maximum .69. This is an observed boundary event; it does not justify moving the threshold or inferring a population false-positive rate from pooled dependent calls. JSON retains every cell and each wrong-message/C0 denominator separately.

### Interpretation limits

C1-minus-C0 decoded scores may maximize over different decoded words, and recomputed scores may use different output-derived content codes q. These native score contrasts are not a common-pattern linear transported signal, a fixed-pattern signal increment, or evidence of carrier recovery. Right-minus-wrong changes the query direction and may change threshold context; its raw-score contrast does not hold the queried pattern fixed. All analyses are post-hoc author diagnostics of development data whose aggregate outcomes were already known. Scores are normalized alignment statistics (decoded scores include a pattern search); a negative margin or loss of separation cannot measure absolute carrier amplitude or prove destruction. Readable mismatches remain distinct from absent carriers. A nonzero right-minus-wrong score is not a passing owner query. Background distributions under these saved keys/sources do not establish a universal null law, cryptographic security or confirmatory FPR. No causal encoder effect is identified: the pipelines differ in multiple components. Same-source/seed pairing does not guarantee identical random draws across marked/unmarked inputs or pipeline families. Rinse pairs use base seed 12/13/14, with its second pass adding 100 internally.

Reproduce with the permitted stdlib interpreter and `-I negative-background-analysis.py`. Only the saved journal is read; this script writes this report and its JSON sibling.

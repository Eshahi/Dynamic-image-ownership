# Retained v5 semantic geometry: exploratory analysis plan

Issue #18. Author: Codex. This plan is recorded before computing the new aggregate comparisons, after observing dev-001's component failure. It is post-outcome exploratory reanalysis, not retrospective preregistration or a new scientific execution. It applies `research/research-contract.md` and `research/scope-guard.md`; the image-domain comparator does not establish the unresolved latent hypothesis.

## Question and falsifiable prediction

Does the saved continuous semantic representation rank the frozen development labels better than its existing 32-bit code? The directional prediction is AUC(C0 cosine) > AUC(-C0 semantic Hamming distance). Equality or the reverse contradicts this aggregate prediction. A positive difference indicates ranking loss in this particular coding path and cohort; it cannot establish an extractor defect, a causal mechanism, a better deployed method, or generalization. Extractor/cohort/label mismatch and coding limitations may coexist.

## Frozen inputs and provenance

- Input: MAIN `.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json`, SHA256 `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d`.
- Existing profile: `experiments/c4-v5-two-tier-regeneration-v1/profile.json`.
- Existing labels: `experiments/c4-three-threat-small-v1/semantic-labels.json`.
- Freeze all 12 sources and all 66 unordered pairs: seven same, 57 different, two uncertain. Labels are previous agent topic assessments, not new independent human ground truth. Uncertain pairs remain in the output but outside binary ranking comparisons.
- Verify original run identity, complete unique row inventory, full pair roster and label agreement; validate each of the 24 clean C0/C1 feature vectors (512 finite values, saved hash, normalized within 1e-5, checkpoint and saved-pixel linkage). Recompute codes using the unchanged v5 implementation and profile; require agreement with saved claimed-owner combined detections and pair distances. Verify saved C0 dot products within 1e-9. Do not read source images, load models, tune thresholds, replace failed sources or erase any run failure.

## Prespecified descriptive comparisons

1. Primary: empirical AUC for saved C0 cosine and negative C0 q distance; compare each of seven same pairs to each of 57 different pairs, with score ties receiving 0.5. Publish both AUCs, their difference, and win/tie/loss counts over 399 comparisons. These are correlated comparisons, not independent trials.
2. Secondary: the same statistics for C1; complete per-pair C0/C1 cosine, q and H distances and their changes; unchanged q <= 6 and H > 6 coverage by frozen label. Publish rank reversal counts and their paired comparison records.
3. Sensitivity: leave out each source in turn and remove every incident pair before recomputing both AUCs. Publish all 12 subsets with actual label counts; mark undefined metrics explicitly if a class is empty. This is descriptive omission sensitivity, not cross-validation, twelve independent studies or an uncertainty interval.
4. Per-source C0-to-C1 cosine and semantic bit flips characterize change after marking. Do not assign causation to observed ranking changes. No counterfactual embedding or alternative hash family is introduced.

The unit of evidence is this fixed development cohort. Report pair/source counts and descriptive mean, median, sample SD and range for cosine and q by label and arm. No p-values, confidence intervals, significance claims, pair bootstrap, threshold search, code-seed search or multiple-comparison selection. The generic result helper supports paired independent-seed comparisons rather than this correlated graph; use a reviewed stdlib analysis extension with hand-checkable AUC/tie and source-omission tests. In particular, do not use an exact theta/pi or binomial model for the implemented fixed Rademacher projections.

## Outputs, limits and decision rule

Write to a fresh MAIN `.thesis-build/` analysis directory: `statistics.json`, complete pair and comparison tables, `analysis-report.md`, `exclusions.json`, and `provenance.json` with input, plan, script, codec and output hashes. Preserve the original 20 failed T3 rows in the parent inventory and identify their absence from this different, complete T5 component explicitly; this is not recovery of those failures.

If cosine AUC exceeds code AUC, identify the specific ordering losses and report omission sensitivity before proposing a prospective coding intervention. If it does not, do not claim that coding is the primary bottleneck. In either case, AUC is separate from the unchanged component criterion (at least five same pairs with q <= 6 and H > 6); never turn ranking diagnostics into acceptance. Missing independent human quality/content assessment remains missing. Any future image/model experiment requires a separate prospective contract and exact execution provenance.

Resource scope: local CPU analysis of declared saved JSON only, zero cost, no network/downloads, no GPU/model calls. Hard outer analysis timeout 120 seconds (inside the user's 2700-second experiment ceiling); no background process after the turn. This does not consume a new scientific-run approval or authorize a new scientific manifest. Independent technical review is required before presenting this package as reviewed; no Spec Kit gate is advanced.

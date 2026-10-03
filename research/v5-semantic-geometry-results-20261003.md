# Retained v5 semantic geometry

Post-outcome exploratory reanalysis of pinned dev-001; 12 sources, all 66 frozen pairs retained. Seven same and 57 different pairs enter 399 correlated comparisons; two uncertain pairs remain outside binary AUC.

Source run: `c4-v5-two-tier-dev-001`; results SHA256 `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d`. Recorded plan: `research/v5-semantic-geometry-analysis-plan-20261003.md`. MAIN `.thesis-build/v5-semantic-geometry-20261003/provenance.json` records the exact input, plan, script, codec and output hashes.

Labels are earlier agent topic assessments, not independent human ground truth. Cosine/q AUC ranks these labels; it does not prove adequacy of q <= 6. No causal interpretation, inferential statistics, projection null model, threshold/seed search or method acceptance is supplied.

| Arm | Cosine AUC | Negative-q AUC | Difference | Strict rank reversals |
| --- | --- | --- | --- | --- |
| C0 | 0.982456140 | 0.649122807 | 0.333333333 | 116 |
| C1 | 0.972431078 | 0.590225564 | 0.382205514 | 136 |

The directional prediction is supported on this fixed cohort.
A positive difference indicates ordering loss in this coding path and cohort, without establishing an extractor defect, causal mechanism, deployment improvement or generalization.

| Omitted source | Same | Different | Uncertain | C0 AUC difference | C1 AUC difference |
| --- | --- | --- | --- | --- | --- |
| 1675 | 4 | 49 | 2 | 0.18367346938775508 | 0.22193877551020402 |
| 4795 | 4 | 49 | 2 | 0.43112244897959184 | 0.46173469387755106 |
| 6012 | 7 | 46 | 2 | 0.2950310559006212 | 0.327639751552795 |
| 25394 | 7 | 48 | 0 | 0.3348214285714286 | 0.3928571428571429 |
| 80932 | 6 | 48 | 1 | 0.39583333333333326 | 0.46354166666666663 |
| 109798 | 7 | 46 | 2 | 0.31832298136645965 | 0.3571428571428571 |
| 134882 | 4 | 49 | 2 | 0.25765306122448983 | 0.3341836734693877 |
| 147498 | 7 | 46 | 2 | 0.3074534161490684 | 0.3649068322981367 |
| 177015 | 4 | 49 | 2 | 0.3112244897959183 | 0.3622448979591837 |
| 190676 | 7 | 46 | 2 | 0.3695652173913043 | 0.39751552795031053 |
| 468505 | 6 | 48 | 1 | 0.41666666666666663 | 0.46875 |
| 499768 | 7 | 46 | 2 | 0.3354037267080745 | 0.3711180124223603 |

All twelve omission subsets remove every incident pair. They are descriptive sensitivity checks, not cross-validation, independent studies or an uncertainty interval. Undefined metrics are null with their reason in statistics.json.

The unchanged component coverage q <= 6 and H > 6 is reported by label and arm in statistics.json. Ranking diagnostics do not replace the at-least-five same-pair criterion or other component checks. Original parent-run T3 failures remain in exclusions.json and are absent from this complete T5 component; this analysis does not recover them. Independent human quality/content assessment remains missing.

pairs.json contains every pair and C0/C1 change; comparisons.json contains every same/different ordering comparison; statistics.json contains descriptive summaries and all omission subsets. No images, model calls, GPU work or downloads were used.

## Bounded next-step decision

Issue #18. In all twelve source-omission subsets, C0 cosine AUC exceeds code AUC; the smallest difference is about 0.184. This prioritizes a prospective investigation of the feature-to-code mapping before replacing the encoder or repeating image regeneration. The current component criterion remains unmet (2/7 same pairs before marking, 1/7 after; minimum five).

A subsequent method experiment should distinguish limited code length from a particular projection realization using a fixed, prospectively declared comparison and reporting every planned realization. Do not select a winning projection seed, fit thresholds on these frozen pairs, or silently make a longer code a drop-in watermark replacement: code length also changes payload and capacity. Preserve the existing 32-bit baseline. This is a next-step recommendation, not an executed ablation or an approved new scientific manifest.

The full-precision vectors are used only for disclosed offline diagnostics. No reference vectors are added to the deployed detector. Existing topic labels remain agent judgments; independent human quality/content assessments remain outstanding. No workflow gate or method acceptance follows from this result.

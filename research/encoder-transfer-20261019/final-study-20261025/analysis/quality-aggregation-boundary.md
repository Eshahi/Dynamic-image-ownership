# Quality aggregation and the boundary of a monotonicity claim

Status: mathematical clarification, 2026-10-25. Written before inspecting any new per-output dominance counts. This note reads only the authoritative main STATE, `04-mechanism.md` and `state_and_quality.py`. It introduces no experiment, criterion or milestone verdict.

## The existing result concerns source summaries

Orient quality so larger is better: q = (−LPIPS, PSNR, SSIM). For each source and pipeline, the existing script takes a separate median of each coordinate over three scheduled outputs, and separately computes majority C, where C is semantic read AND content match. These are different aggregations.

The reported F5 comparison has 58 complete sources; R1 .1 has strictly better coordinatewise median quality than R0 .2 on all 58, while 56 change from majority C retained to majority C lost. The result is reported separately for quality against the marked input (`distortion`) and against the original image (`total_distortion`). It rules out a deterministic coordinatewise nondecreasing mapping from these source-summary quality vectors to the observed majority endpoint, applicable to both pipelines. The contradiction is already within each affected source, so allowing a different such mapping per source does not remove it.

It does **not**, by aggregation alone, rule out a deterministic coordinatewise monotone rule operating on individual outputs. Coordinate medians can combine coordinates from different outputs; applying a multivariate rule and taking a majority need not equal applying that rule to the coordinatewise median.

## A constructive counterexample

Consider two abstract quality coordinates, both oriented upward, and the same deterministic output rule in both pipelines:

`C(q) = 1 exactly when q1 >= 1 AND q2 >= 1`.

This rule is coordinatewise nondecreasing.

| Pipeline | Output 1 | Output 2 | Output 3 | Coordinatewise median | Output C values | Majority C |
|---|---|---|---|---|---|---|
| A | (1, 3) | (3, 1) | (0, 0) | (1, 1) | 1, 1, 0 | 1 |
| B | (0.5, 4) | (4, 0.5) | (2, 2) | (2, 2) | 0, 0, 1 | 0 |

B's median strictly dominates A's median, yet B loses the majority. Every output still obeys exactly the same monotone rule. No B failure dominates an A success: each failing B output has one coordinate below 1. Thus there is no individual-output monotonicity violation in this example. A third coordinate can be appended as 1 to every A output and 2 to every B output, with the rule ignoring it, giving strict median dominance in three dimensions as well.

The example does not rescue a deterministic monotone **source-summary** mapping. Such a mapping would have to assign 1 to (1, 1) and 0 to its superior vector (2, 2), which is impossible. It establishes the precise level at which the existing contradiction holds.

## What a saved-output sensitivity could establish

For an actual within-source pair, let a be a retained R0 .2 output and b a lost R1 .1 output. If the recorded vector satisfies q(b) >= q(a) coordinatewise, then any deterministic coordinatewise nondecreasing rule f must satisfy f(q(b)) >= f(q(a)). Observing C(a)=1 and C(b)=0 contradicts that rule. Strict improvement in every coordinate is sufficient but not mathematically necessary. A deterministic nondecreasing scalar-quality rule is likewise contradicted when its specified scalar quality improves; a scalar reduction of the vector must itself be coordinatewise nondecreasing for vector dominance to imply this.

This rejects exact monotone quality-only explanations of the observed outputs using the specified recorded metrics. It does not reject an arbitrary nonmonotone deterministic function, an unmeasured quality functional, or a rule using additional detector information. Nor does a finite success/failure reversal logically refute a noisy model whose **probability** of retention increases with quality: individual Bernoulli outcomes need not preserve probability order.

The two reference definitions must be evaluated and reported separately, without mixing original-reference coordinates with marked-reference coordinates. Missing quality or detection values cannot supply a complete observed dominance violation. Matching numeric seeds across native pipelines is an indexing convention, not evidence of identical noise tensors or coupled stochastic trajectories. Within-source pairing controls source identity only; different pipelines still change multiple components.

Any new saved-JSON analysis remains a post-hoc descriptive sensitivity. Counts of overlapping output pairs are not independent replicates. Neither their existence nor their number supplies a causal effect, population generalization, significance result or confirmation claim. Absence of observed violations would not prove a quality-only model. The historical transfer verdict and prospective protocol remain unchanged.

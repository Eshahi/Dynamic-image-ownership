# A finite empirical Brier floor for monotone quality scores

Status: mathematical author extension, 2026-10-25; post-hoc and outside the completed independent reviews. This note proves a bound without fitting a model or introducing a criterion. Its numerical specialization is conditional on the supplied complete-source aggregates, not an independent verification of saved records.

## Assumptions and weighting

Orient recorded quality as q = (−LPIPS, PSNR, SSIM). For one source, R0 denotes SD1.5 .2 and R1 denotes SDXL .1. There are m completed R0 outputs, 1 ≤ m ≤ 3, of which k have compound C = 1; all three completed R1 outputs have C = 0. Every R1 vector dominates every R0 vector coordinatewise. The [saved-output analysis](quality-dominance.md) reports strict dominance for F5 separately against marked input and original image. Either reference supplies the argument; coordinates from different references must not be mixed.

Let f(q) ∈ [0,1] be coordinatewise nondecreasing, common to both cells but permitted to differ by source. Each cell receives weight 1/2: each available R0 output has weight 1/(2m), and each R1 output has weight 1/6. Sources are subsequently averaged equally. These weights define a descriptive empirical loss, not a population sampling model.

## Bound and proof

Let B be weighted empirical Brier loss, the sum of weight × (f(q) − C)². The total weight of positive R0 outputs is A = k/(2m); that of negative R1 outputs is D = 1/2.

For k > 0, set t to the largest score among the positive R0 outputs. Monotonicity makes every R1 score at least t. Since scores lie in [0,1], each positive R0 loss is at least (1 − t)², and each R1 loss is at least t². Dropping all negative R0 losses therefore gives

\[
B \ge A(1-t)^2 + Dt^2
  = (A+D)\left(t-\frac{A}{A+D}\right)^2
    +\frac{AD}{A+D}
  \ge \frac{k}{2(k+m)}.
\]

For k = 0 the bound is zero without requiring a separator. The minimizing relaxed separator is t = k/(k+m). Additional observed partial-order constraints, including those involving negative R0 outputs, can increase the minimum. Consequently, this is a lower bound, with no general claim of attainable equality or sharpness for the observed vectors.

For a deterministic monotone binary classifier, either all positive R0 outputs are misclassified, costing A, or at least one is classified positive, forcing all R1 outputs positive and costing D. Thus weighted empirical classification error is at least min(A,D) = k/(2m). This also applies to thresholding f with a consistent threshold and tie convention within a source.

## Conditional complete-source specialization

The supplied aggregates for 58 sources with m = 3 are: 168 positive R0 calls, 57 sources with any positive call, and 56 with a positive majority. Writing n_j for sources with j positive calls yields

\[
(n_0,n_1,n_2,n_3)=(1,1,1,55).
\]

Indeed n₁ = 57 − 56 = 1, n₂ + n₃ = 56, and n₁ + 2n₂ + 3n₃ = 168. Conditional on those aggregates, equal-source averaging gives

\[
\overline B \ge \frac{55/4+1/5+1/8}{58}
=\frac{563}{2320}\approx0.2426724,
\qquad
\overline{\mathrm{error}}\ge\frac{168}{6\cdot58}
=\frac{14}{29}\approx0.4827586.
\]

These denominators concern the complete-source subset only. Neither incomplete sources nor overlapping pair counts are additional replicates.

## Interpretation boundary

The deterministic contradiction becomes a quantitative obstacle to empirical prediction: every monotone probability-valued quality mapping incurs at least this observed Brier loss, even with source-specific mappings. This restricts a much broader class than a specified monotone logistic form. It does **not** test or reject population monotonicity of retention probabilities: random outcomes can violate probability order, and the calculation supplies neither a null distribution nor a significance claim. Arbitrary nonmonotone quality functions remain unrestricted by this argument.

This is not an H4 forecast result or implication. Realized marked-output quality is forbidden as an H4 forecast input, and the two-cell equal-weight loss here differs from H4's evaluation weights. No future performance, causal encoder attribution, new fit, protocol amendment or changed transfer verdict follows.

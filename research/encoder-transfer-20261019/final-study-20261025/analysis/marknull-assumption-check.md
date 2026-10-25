# Geometry is not a removal guarantee

Status: analytical counterexamples, written during WP3 before any new attack execution. These examples limit an argument; they do not dispute the reported attack measurements or establish that the proposed attack fails.

## Primary-source scope

MarkNull v1 §5.2 and Proposition 3 connect small noise–latent alignment to statistical independence/removal. Assumption 2 requires a common latent parameterization and inversion scheme; Proposition 4 additionally relies on predominantly off-tangent watermark perturbations. The proposed WP3 attack borrows an optimization idea, without importing these conclusions. Source inspected: [MarkNull, arXiv:2608.10166v1](https://arxiv.org/html/2608.10166v1), §§5.2–5.3, 6.2–6.3 and Appendix B.1, 2026-10-25.

## Counterexample 1: exact orthogonality, complete dependence

Let Z ~ N(0, I_(2m)) and let R be block diagonal with m copies of the matrix [[0, -1], [1, 0]]. Put Y = RZ. Then R is orthogonal and skew-symmetric, so:

- Z and Y each have a standard isotropic Gaussian marginal distribution;
- Z^T Y = Z^T RZ = 0 for every realization, not merely with high probability;
- Z = R^T Y, so either vector determines the other exactly.

For a concrete recoverable bit, B = 1[Z_1 > 0] equals 1[Y_2 > 0] almost surely. Thus zero noise–latent cosine can coexist with perfect recovery of a bit from the other variable. For continuous variables the joint measure is singular relative to the product measure, rather than an independent product. The joint Gaussian cross-covariance is R^T, which is nonzero even though its trace vanishes. The familiar Gaussian independence criterion requires a zero cross-covariance matrix, not one zero inner product or zero trace.

Increasing m does not fix this counterexample. Concentration of independent directions implies approximate orthogonality; reversing that implication is invalid. This is a logical limitation of an independence inference, not a prediction of any particular diffusion model's behavior.

## Counterexample 2: imperceptibility does not imply an off-manifold residual

Let a differentiable decoder D have Jacobian J at z, and choose a nonzero tangent vector u = Jv. For any epsilon > 0, the image residual delta = epsilon u can be arbitrarily small while lying entirely in the decoder tangent space. If P_T is its orthogonal projector, then P_T delta = delta. A local least-squares reconstruction therefore need not attenuate its energy at all. Small perturbation amplitude constrains a norm; it does not constrain the angle to a manifold.

When J has deficient rank, the projector is J J^+ (Moore–Penrose inverse); writing J(J^T J)^(-1)J^T additionally assumes full column rank. A perceptually weighted projection can change the projector but not the absence of an implication from small norm to normal-space alignment.

The retained F5 round-trip results (55/60 source-majority C for both SDXL and MoVQ) make this distinction relevant. They do not identify a tangent direction or refute a combined optimization attack. They do prevent us from assuming that every imperceptible post-hoc mark is removed by the autoencoder bottleneck alone.

## Consequences for the proposed server study

1. Treat the proxy alignment objective as a heuristic intervention. Measure its target-reader effect after all attack settings are frozen; do not infer that effect from alignment alone.
2. Retain both a codec-only control and a fidelity-optimization control with the alignment coefficient set to zero. Only their paired differences can attribute an incremental effect to the extra objective.
3. Report per-source proxy cosine change, actual reader margin change and quality together. An alignment decrease without a reader-margin decrease is an informative falsification of the proposed mechanism.
4. Do not call this a MarkNull reproduction: the objective, parameter budget, optimization horizon and experimental arms differ.
5. Keep clean-source residuals, watermark keys, target detector outputs and target-reader gradients unavailable to the attacker. Privileged residual/Jacobian measurements belong to the separate mechanism evaluator.

No pixel, latent, model, detector or metric was computed to obtain these counterexamples.

## Optimization diagnostic, not an extra tuning rule

For c = (z^T n)/(||z|| ||n||), fixed nonzero n, and L = c^2, the gradient is

`grad_z L = (2 c / ||z||) [n / ||n|| - c z / ||z||]`,

whose norm is `2 |c| sqrt(1-c^2) / ||z||`. It vanishes at c = 0 and at exact parallel/antiparallel alignment. In particular, high-dimensional near-orthogonality can make the objective nearly inactive before optimization even starts. RMS-normalizing the full optimization gradient changes step scale but does not create a missing direction or identify a watermark component. Record initial/final c, objective values, projected-step norms and the fraction of coordinates at the radius bound. These diagnostics are frozen outputs, not permission to choose new settings after target-detector outcomes are exposed.

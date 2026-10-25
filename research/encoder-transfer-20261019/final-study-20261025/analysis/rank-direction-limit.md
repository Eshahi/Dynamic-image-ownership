# What rank, energy and readable direction can establish

WP6 author derivation, 2026-10-25. This is algebra, not a new experiment, a fitted model, a novelty claim or a second independent review. It sharpens the limit attached to the [rank-ratio source](../literature/transfer-theory/rank-ratio-unverified.md). The examples below are this session's arguments; they do not assert that the cited paper makes an unrestricted worst-case claim.

## 1. A rank ratio needs a directional probability model

Let P be an orthogonal projector in R^n, of rank r with 0<r<n. For a unit direction U uniform on the sphere and independent of P,

`E ||P U||² = r/n`.

Proof: rotational invariance gives E[UU^T]=I/n; then E[U^T P U]=tr(P)/n. Writing U=G/||G|| for independent standard Gaussian coordinates also gives

`||P U||² ~ Beta(r/2,(n-r)/2)`.

For this specific projector, `cos²(U,P U)=||P U||²` whenever P U is nonzero. The expectation is therefore an average squared alignment, not a deterministic bound on every direction, nor the average cosine itself. Jensen only supplies E[cos]<=sqrt(r/n) for its nonnegative projector cosine. No F5 distribution is asserted to be spherical.

For any fixed nonzero optimized delta in range(P), the retained energy fraction is 1 even if r=1 and n is arbitrarily large. For delta in kernel(P), it is 0. In two dimensions P=diag(1,0) and delta=e1/e2 give the two extremes. Rank alone cannot choose between them. A randomly drawn Haar subspace independent of a fixed delta yields the same Beta law, but independently trained neural weights are not automatically Haar subspaces independent of a writer's structured perturbation.

For a fixed general linear encoder J and a spherical unit U,

`E ||J U||² = ||J||_F²/n = sum_k singular_value_k(J)²/n`.

Rank does not determine this expression unless additional singular-value normalization is imposed. A reconstruction derivative J_D J_E is generally neither symmetric nor an orthogonal projector; a projector identity cannot simply be reused for it.

For mean-zero anisotropic perturbations with covariance Sigma,

`E ||J Delta||² = tr(J Sigma J^T)`.

The ratio of expected output/input energies is tr(J Sigma J^T)/tr(Sigma), when the denominator is positive. It is generally **not** E[||J Delta||²/||Delta||²]. For nonzero mean mu, add ||J mu||² and ||mu||² to the corresponding energies. Optimized residuals can have directional structure correlated with J, in which case even treating Sigma as independent of J requires justification.

## 2. Pixel direction is not detector direction

Let L_c map a small image perturbation to the reader's chip displacement along a specified clean trajectory, and let w be a fixed signed reader direction. The local signal of interest is

`s_c = w^T L_c delta`.

Its magnitude depends on singular values, left/right directions and their alignment with both delta and w. Neither rank(L_c) nor ||L_c delta|| alone gives its sign. For example J=e2 e1^T and delta=e1 have rank one, preserve norm exactly, and give zero pixel cosine between input and output. Yet a readout w=e2 has signal +1. The same output read by w=e1 has zero signal; w=-e2 gives -1. A direction-scrambling statistic can therefore be informative about one explicitly fixed readout, but cannot replace that readout's response.

An idealized unconstrained, single-step L2 writer maximizing w0^T L0 delta over ||delta||<=epsilon chooses

`delta_star = epsilon L0^T w0 / ||L0^T w0||`

when the denominator is nonzero. Its target readout is

`w1^T L1 delta_star = epsilon * (L1^T w1)^T (L0^T w0) / ||L0^T w0||`.

This exposes the signed cross-gradient inner product. Different training or architecture does not determine its sign or magnitude. The actual F5 writer is a constrained, multi-step, active-margin optimization with quantization and an auxiliary tier, so this idealized optimum is explanatory algebra, not an identity for its stored residual. The frozen residual must be measured as it exists.

## 3. Consequences for the planned measurements

The server design compares the actual residual direction with two norm-matched Gaussian and two per-channel spectrum-matched directions for each of twelve fixed development sources. This can reveal a coarse paired directional advantage in the tested draws. It does not estimate a tail percentile over all directions, a top singular space, or the whole singular spectrum. Matching per-channel power does not match cross-channel coherence. Treat these controls as bounded diagnostics with their exact seeds, not as a statistical certificate of isotropy.

These controls are differential vectors: they are not clipped into valid images or presented as practical alternate watermarks. The final rule in [mechanism-server-spec.md](mechanism-server-spec.md) supersedes the early generic box/quantization suggestion in theory-design.md. Native marked trajectories remain exact stored-image comparisons; their finite versus differential discrepancies are part of the approximation check.

The useful mechanism question is therefore whether the observed encoder displacement, downstream directional response, background and unchanged nonlinear reader jointly forecast the fixed endpoint. A small rank ratio, a high latent norm or a high pixel cosine alone supplies neither that forecast nor a causal attribution to encoder training independence. This argument adds no new measurement allocation and changes no hypothesis or threshold.

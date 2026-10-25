# Finite transport: what smoothness and one fitted scalar can establish

Author supplement, 2026-10-25; outside the completed independent-review scope. This is a constructive derivation supporting the frozen predictor, not a review, novelty claim, protocol amendment, new criterion or request for measurements. No experiment, model, scientific interpreter or numerical study ran. MAIN STATE was read once. The governing documents remain [07-final-experiment.md](../07-final-experiment.md), [prediction-contract.md](prediction-contract.md), [mechanism-server-spec.md](mechanism-server-spec.md) and the integrated contracts they name. The starting full-chain decomposition is in [theory-design.md](theory-design.md).

## 1. Separate a smooth approximation from the actual numeric pipeline

Fix one source, cell and seed, its conditioning and its entire explicitly replayed noise bundle. Let u be the clean injection state and h=a_t*d the exact paired injection displacement, with native scaling and input conversions included in d. Scheduler-history coordinates, if present, belong to the state; their initial displacement is zero. The main law uses this finite d, not an encoder Jacobian applied to the pixel residual. There is consequently no input-encoder Taylor remainder in this decomposition.

Let G map the injection state to 320 chips through the declared real-valued downstream surrogate: every reverse step, decoder, output processing and F5 reader encoder, followed by the fixed linear chip operator. Write

`g0=G(u), g1=G(u+h), v*=J_G(u)h`.

Let b and p be the native C0 and C1 chips, and define endpoint discrepancies

`eta0=b-g0, eta1=p-g1`.

These include whatever the declared surrogate does not reproduce: integer rounding, finite-precision/kernel effects, and any remaining native/surrogate endpoint mismatch. They are definitions, not assumed random noise. If the surrogate does not actually receive injection states separated by h, that input inconsistency also enters these discrepancies; it cannot be silently attributed to downstream curvature. An unsupported adapter stays unsupported under the existing contract.

For an implemented tangent v, define `eJ=v-v*`. This term distinguishes mathematical derivative accuracy from primal agreement. Agreement of cached primal states alone does not establish a correct derivative. With `r_curv=G(u+h)-G(u)-J_G(u)h`, the exact algebra is

`p-(b+kappa*v) = r_curv + (eta1-eta0) + (1-kappa)*v* - kappa*eJ`.

The native C0 anchor matters: the discrepancy entering the paired prediction is **eta1-eta0**, not eta1 alone. A constant chip offset common to both endpoints cancels. Large individual offsets can therefore cancel, while a small C0 discrepancy does not bound the unobserved C1 discrepancy. Without additional structure the safe triangle bound is `||eta1-eta0|| <= ||eta1||+||eta0||`. The forecast information barrier forbids using the marked endpoint to repair its own prediction; this decomposition explains later diagnostics only.

## 2. A conditional remainder bound, with its actual assumptions

Use Euclidean vector norms and their induced operator norms in the declared native coordinates. Suppose G is continuously differentiable on a neighborhood of the complete segment `{u+t*h:0<=t<=1}`. The fundamental theorem of calculus gives

`G(u+h)-G(u) = integral_0^1 J_G(u+t*h)h dt`,

`r_curv = integral_0^1 [J_G(u+t*h)-J_G(u)]h dt`.

If, additionally, `||J_G(u+t*h)-J_G(u)||op <= L*t*||h||` for every t, then

`||r_curv|| <= (L/2)*||h||^2`.

Thus, conditional on bounds N for `||eta1-eta0||` and E for `||eJ||`,

`||p-p_hat|| <= (L/2)||h||^2 + N + |1-kappa|*||v*|| + |kappa|*E`.

This is a sufficient bound, often loose because it ignores cancellation. It is not an F5 guarantee: no such L, N or E has been measured or certified here. L concerns the complete downstream map along a finite latent segment, not merely the attack encoder, the clean endpoint or the pixel-space PSNR. Small pixel distortion alone need not imply small h, small L, or small relative chip error. A change of latent coordinates changes numerical constants; their units must remain consistent.

Differentiability at u alone is insufficient for the integral formula as stated or its quadratic bound. A weaker formulation is possible if `t -> G(u+t*h)` is absolutely continuous: integrate its almost-everywhere path derivative, subtracting the chosen initial tangent. But absolute continuity alone supplies no quadratic remainder. Clipping boundaries and piecewise-smooth operations may require this weaker treatment. Integer rounding is discontinuous and is deliberately outside G; its literal derivative cannot provide the desired transport. None of these observations authorizes a straight-through replacement.

Analytic examples expose the missing assumptions. For `G(t)=(t,M*t^2)` at u=0, the tangent is `(h,0)` and the exact remainder is `(0,M*h^2)`. This is perfectly smooth, but an unspecified M allows arbitrarily large error at a fixed nonzero h. For `G(t)=max(0,t-a)`, u=0 and h=2a with a>0, the initial derivative is zero while the endpoint change is a. The path crosses a kink; the uniform quadratic conclusion does not follow from the initial flat region. Finally, rounding a scalar with step Delta can map endpoints separated by arbitrarily small h on opposite sides of a rounding boundary to outputs separated by Delta. A smooth identity surrogate has zero curvature here, yet the native/surrogate discrepancy difference remains large relative to h. These are mathematical constructions, not assertions about realized images or executions.

## 3. Exactly what the best global scalar repairs

Index admissible fit vectors by j, let `Delta_j=p_j-b_j`, and retain the frozen original weights `w_j=1/18` and all-or-none vector masks. This is precisely the observed-data objective in [training-missingness-design.md](training-missingness-design.md), with its unchanged coverage qualifications:

`L(k)=sum_j w_j ||Delta_j-k*v_j||^2`.

Define `V=sum_j w_j ||v_j||^2`. For finite V>0,

`k* = [sum_j w_j <v_j,Delta_j>]/V`.

Completing the square yields

`L(k)=L(k*)+V*(k-k*)^2`,

`sum_j w_j <v_j,Delta_j-k* v_j>=0`.

The residual is orthogonal to the single tangent column in the weighted, stacked observation space. It need not be orthogonal separately within every trajectory. Relative to the unfitted coefficient one,

`L(1)-L(k*)=V*(k*-1)^2`.

Therefore a fitted scalar can improve training squared error whenever it corrects a pooled scale discrepancy. That elementary improvement establishes neither prospective accuracy nor a physical gain. If `Delta_j=v_j+r_j`, then

`k*=1+[sum_j w_j <v_j,r_j>]/V`.

The fitted correction can absorb the projection of curvature, numeric discrepancy, derivative error and other residual structure. It does not identify which generated that projection. A negative coefficient is mathematically allowed by the frozen unconstrained fit, and is not by itself evidence for a named physical reversal mechanism. V=0 leaves the coefficient unidentified; no replacement scalar follows from this derivation.

For each nonzero v_j, decompose `Delta_j=alpha_j*v_j+z_j`, where `<v_j,z_j>=0`. Then

`k*=sum_j w_j ||v_j||^2 alpha_j / V`,

`L(k*)=sum_(v_j!=0) w_j[||z_j||^2+||v_j||^2(alpha_j-k*)^2] + sum_(v_j=0) w_j||Delta_j||^2`.

This exposes two irreducible costs of one scalar: missing direction within a trajectory, and incompatible gains across trajectories. The alpha_j are algebraic explanatory quantities, not authorized per-cell coefficients or additional fitted predictors. A small set of high-energy v_j can dominate the pooled scalar despite equal trajectory weights. Fixed coverage floors do not remove that geometry or selection from missing vectors.

In the smooth example above with h nonzero, the best scalar is one and the perpendicular component `(0,M*h^2)` survives unchanged. No scalar can manufacture that second direction. More generally, in weighted stacked space with nonzero Delta and v, the minimum squared residual is `||Delta||_w^2*(1-cos(theta)^2)`, where theta is their angle. Parallel or antiparallel changes can be matched by an unrestricted scalar; an orthogonal change cannot. This is a projection identity, not a new study statistic. The full-chain Jacobian already includes first-order rotation: the argument does not claim that an exact full-chain derivative inherently omits rotations. Finite curvature or a surrogate mismatch can create directions absent from that local tangent.

## 4. Consequences for the frozen interpretation

These identities explain why the already specified vector residual, direction, margin and proxy-disagreement diagnostics answer different questions. Aggregate scalar improvement cannot identify an encoder-only mechanism: the predictor includes the reverse sampler, decoder, reader, native C0 background and privileged target information. Neither a fitted gain nor a successful forecast separates their causal contributions or proves transfer to a new family.

A conditional vector-error bound can be passed to the existing [reader-stability boundary](reader-stability-boundary.md) only with its nonzero-energy and decision-margin assumptions. That note explains why D-score accuracy does not establish decoded-word stability, semantic binding or compound C. The q90 score radius is not any of L, N, E or a chip-error bound. Conversely, small native C0 mismatch or a plausible smoothness argument does not certify q90 coverage or H4.

The unchanged experiment tests the frozen forecast and compound source-majority C criteria. This supplement adds no allocation, computation, measurement requirement, fit, threshold or rescue rule. Its result is a precise conditional explanation of what existing diagnostics could mean; actual smoothness conditions and future predictive success remain unestablished.

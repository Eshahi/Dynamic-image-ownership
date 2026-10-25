# Forgery theory: source-assumption boundary

Author analysis by Codex agent, 2026-10-25. This is a bounded mathematical contribution, not another milestone review, a published refutation, an experiment, or an F5 result. No accepted predictor, statistics, protocol, or decision rule changes.

## Inspected source and extraction boundary

Primary source: [Lee et al., arXiv:2606.29807v1](https://arxiv.org/html/2606.29807v1), accessed 2026-10-25 through the browser reader; access-log clock check: 16:58:20 UTC. No file download. Inspected §§4.1–4.3, Appendix B.1–B.3 and C.4; additionally Table 2, A.4 and D.5. Reader line locators: 138–217, 234–253, 509–633, 657–659, 699–712.

Source synopsis (under 200 words; subsequent derivations are original analysis): Theorem 4.2 claims a KL-based additive distortion floor and effective-rate penalty under shared Gaussian posteriors and normalized MSE. Appendix B.2 calls the penalty a surrogate but does not derive its operational information constraint. Appendix B.3 argues angular and covariance separation, then concentration. Section 4.1 discourages per-image feature storage; §4.3.1 and C.4 compare a recovered latent with a reference latent. Table 2 reports empirical anti-forgery AUCs. D.5 checks residual Gaussianity and variance similarity. These observations do not establish the missing rate constraint, angular scaling, or dimension-uniform concentration assumptions.

## 1. KL is not an MSE floor: exact calculation and counterexample

Use exact, rather than approximate, conditional Gaussians. Write

\[
P(X\mid Y)=N(m(Y),s^2I_d),\qquad Q(X\mid Y)=N(a(Y),s^2I_d).
\]

For natural-log KL, direct Gaussian integration gives

\[
K=E\,\mathrm{KL}(P\|Q)=\frac{E\|m(Y)-a(Y)\|^2}{2s^2}.
\]

If the estimator is specifically the proxy posterior mean, conditioning on Y and expanding the square gives the exact identity

\[
E\|X-a(Y)\|^2/d=s^2+B,
\qquad B=E\|m-a\|^2/d=(2s^2/d)K.
\]

The cross term vanishes because E[X−m(Y)|Y]=0. This proves a relation between KL and **this estimator's excess risk**, not irreducibility over every permitted estimator. KL in bits introduces an additional ln(2) factor. K is dimensionless and scales with dimension; normalized MSE has squared-coordinate units and averages dimensions. Rescaling all latent coordinates by c preserves K but multiplies MSE by c². Thus adding unconverted K to MSE cannot be invariant under an innocuous coordinate change. Unit-variance coordinates do not fix the missing factor d.

Explicit counterexample to inference from the two advertised assumptions alone: let d=4, Y carry no information, X~N(0,I₄), and let the proxy posterior be N(a,I₄), where a=(4,0,0,0). The constant proxy-mean estimator outputs a. Its normalized MSE is 1+16/4=5, whereas K=16/2=8. Hence its actual distortion is already below the proposed KL floor. Both posteriors are exactly Gaussian with identical covariance. Even independently sampling the proxy posterior has MSE 2+16/4=6<8.

For the proposed expression, the penalty is (1/2)log₂9. A rate budget R=2 bits per coordinate exceeds that penalty, and the constant estimator is feasible within that budget. The alleged lower bound is 8+9/16=8.5625, again above 5. This avoids relying on a negative effective rate. If R instead means exact attained mutual information, that must be stated; here it is zero, and substituting zero would make the alleged inequality still stronger. Posterior assumptions alone do not impose any minimum achieved information rate.

This counterexample tests the sufficiency of the mathematical assumptions. It does not construct an operational diffusion forgery. An intended restriction excluding it must become an explicit theorem assumption.

## 2. What extra assumptions a valid rate claim would require

Nonzero posterior KL does not imply information loss. For example, let X=Y+E with independent Gaussian E. A proxy mean Y+b is a bijective translation of Y, so I(X;Y+b)=I(X;Y), although the shifted proxy posterior has positive KL. A deterministic mismatch can preserve all information while biasing a particular estimator. Whether an attacker knows how to correct the bias is a separate knowledge/model-class restriction.

A defensible operational bound must define the observation channel, allowable reconstructions, nominal rate and its per-vector/per-coordinate units, side information, and the joint law. It must then derive any effective-rate restriction and any error decomposition; neither follows from shared covariance alone. An additive quantization term also needs control of its cross term with proxy bias. Further, conditional posterior variance is not generally marginal source variance: in X=Y+E these are s² and Var(Y)+s² respectively. The variance used in a Gaussian rate-distortion function must match the source actually encoded.

For orientation, when the encoder observes Y, the decoder approximates m(Y), and m(Y) is an isotropic Gaussian with per-coordinate variance v, ordinary indirect Gaussian coding yields s²+v·2^(−2R) under the usual asymptotic rate model. The s² term is observation uncertainty. It is not posterior mismatch KL. This example illustrates the missing operational specification; it is not a replacement theorem for diffusion or for our protocol.

## 3. Positive orthogonal energy does not imply a persistent angle

Let z~N(0,I_N), r=||z||, and choose a measurable unit vector u(z) orthogonal to z (normalize the projection of e₁ onto z's orthogonal complement; the exceptional collinear event has probability zero). Fix a>0 and set δ=a·u(z). Then ||δ_perp||²=a² is strictly positive for every N, while

\[
\theta=\arctan(a/r)\longrightarrow0
\]

in probability because r/√N→1. Since 0≤θ≤π/2, Eθ→0 as well. The small-relative-perturbation condition holds with probability approaching one. This directly defeats the inference from merely positive orthogonal energy to a dimension-independent angular gap.

More generally, writing δ=αz+δ_perp gives, for 1+α>0,

\[
\tan\theta=\frac{\|\delta_\perp\|}{(1+\alpha)\|z\|}.
\]

A sufficient expectation-gap assumption is that this ratio exceeds a fixed c>0 with probability at least p>0, uniformly in dimension; then Eθ≥p·arctan(c). Orthogonal energy of order N, with suitable probability and radial control, can meet this condition. Nonzero energy alone cannot. Pure positive radial scaling produces zero angle despite nonzero MSE, so a distortion floor by itself cannot establish angular detection.

## 4. SPD geometry: valid invariance, insufficient separation

For arbitrary SPD P,Q, choose G=Q^(1/2)P^(−1/2); then GPGᵀ=Q. Consequently, no pair of SPD matrices is globally outside the other's invertible congruence orbit. Exclusion from a specified neighborhood of identity is a quantitative extra assumption, requiring conditioning and dimension-uniform constants.

Simultaneous congruence preserves AIRM distance: transforming both arguments by the same G changes neither their distance nor generalized eigenvalues. It does not make d(P,GPGᵀ) zero. For P=I_N and G=2I_N, that distance is √N·log(4). Conversely, distinct matrices need not have a fixed gap: P=I_N and Q=(1+1/N)I_N give distance √N·log(1+1/N)→0.

A log-eigenvalue gap ≥η on an event of probability ≥p does imply expected AIRM distance ≥ηp. That final inequality is sound. The gap and event probability must be established rather than inferred from generic mismatch. Also, adding a fixed εI to both empirical covariances breaks general affine equivariance of that preprocessing: G(S+εI)Gᵀ=GSGᵀ+εGGᵀ, which differs from GSGᵀ+εI unless GGᵀ=I.

An additional concentration step needs scale-aware assumptions. A generic 1-Lipschitz function of N standard Gaussian coordinates does not gain exp(−cN) tails: f(z)=z₁ has variance one for every N. Lipschitz constants, normalization, the perturbation map, eigenvalue bounds and class-specific mean gaps need control. Positive expectations alone cannot certify nearly perfect discrimination.

## 5. Empirical and detector-side-information boundary

The algebra above does not erase measured anti-forgery separation. Empirical performance can be useful even when a universal theoretical explanation needs stronger assumptions. Our admissible use is motivation to measure geometric discrepancies under explicit conditions, not evidence that independently trained encoders universally remove marks or force detectable forgery. Large latent reconstruction error also need not change a watermark statistic: an error can lie in dimensions that statistic ignores.

A detector comparing suspect inversion with a reference needs access to that reference and a way to associate it with the suspect. Storage is one implementation; deterministic regeneration from a key/seed or inversion of an available original is another, with different costs and side information. Therefore the source's storage rhetoric does not justify calling the illustrated detector reference-free. The inspected passages do not resolve a general reference-retrieval mechanism. Our writeup must name available reference/registry information explicitly and must not transfer the source's claims to F5.

Disposition: retain this source as empirical anti-forgery motivation with explicit reference dependence. Do not inherit its advertised universal distortion floor, encoder-independence claim, removal guarantee, or asymptotic separability claim from Gaussian posteriors plus MSE alone. No new experiment or protocol amendment is proposed here.

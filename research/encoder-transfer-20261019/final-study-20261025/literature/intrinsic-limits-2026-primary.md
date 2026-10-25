# Intrinsic limits of latent watermarking: primary-source boundary

Author: Codex research subagent. Date: 2026-10-25. Status: bounded primary-source analysis, not an independent milestone review. No experiment, model pass, scientific interpreter, download or protocol change.

**Decision:** retain this paper as component-level robustness analysis and empirical prior art. Do not import its universal amplification, impossibility or maximum-tolerable-attack language as a proved constraint on the proposed signed full-chain predictor. The useful parts and unsupported steps are separated below; this is not a rejection of all its mathematics or experiments.

## Source, retrieval and locators

Cheng-Han Yeh, Kuan-chun Yu, Cheng-Chang Tsai and Chun-Shien Lu, *On the Intrinsic Limited Robustness of Latent-Based Watermarking*, arXiv:2610.08178v1, submitted 2026-10-06 11:29:50 UTC. Primary [record](https://arxiv.org/abs/2610.08178v1), [full HTML](https://arxiv.org/html/2610.08178v1), [DOI](https://doi.org/10.48550/arXiv.2610.08178). Only v1 appears in the inspected submission history. This is an arXiv manuscript; no acceptance claim is made.

Read directly on 2026-10-25: Sections 3.1–3.5 and 4.1–4.4; Appendix B and C proofs; Appendices D–H; Appendix I text and Table 2; Appendix J; Appendix K text and tables. Browser HTML line locators below refer to the 1,385-line extraction and supplement the stable section/equation identifiers. Plot captions and surrounding analysis were inspected; histogram pixels were not digitized and no plot-derived detection rate is asserted here.

Search receipt, approximately 17:13 UTC: exact query `"2610.08178" "On the Intrinsic Limited Robustness"`. The primary URL had already been directly opened and analyzed. Search surfaced mirrors and an AI-written Pith review; none was opened or used as evidence. The MMSE counterexample and bound-direction objections were derived and communicated before that search. No claim of originality over other critiques is made.

## Source digest — under 200 words

The framework combines watermark injection, decoding, image transformation, encoding, inversion, Fourier processing and masking (Eqs. 3–4). Theory starts with Gaussian noise and an ideal MMSE denoiser; Proposition B.1 invokes log-concavity. Theorem 3.5 gives an upper extraction-error bound, conditional on bounded image displacement and ideal recovery in its proof. Experiments use SD2.1, 50-step generation/inversion, guidance 7.5/1.0, and 1,000 calibration pairs for nominal 1% FPR. Appendix G tests 100 marked images per method, including VAE regeneration and SD1.4 DiffPure at 10–50 steps. Threshold distances include 77.12 for Tree-Ring and 68.52 for HSQR. Table 2 reports nonzero clean extraction deviations. Appendix H separately uses PRCW decoding keys and decoding/detection criteria. Section 3.5 motivates a noncentral-chi null. Section 5 acknowledges MMSE and invertibility assumptions. The scope therefore exceeds RST, but does not isolate independent-encoder causality. Detector-side requirements include the original inversion model and reference watermark or decoding key; no original-image registry is specified in Eqs. 3–4.

## Original mathematical analysis and transfer assessment

Everything below is this session's analysis, counterexamples or project comparison. Locators identify which premise to check; they do not endorse the manuscript's wider conclusion.

### 1. Preserve the exact-MMSE identity; do not grant universal contraction

At Proposition B.1 and Lemma B.2 (HTML lines 398–461), distinguish two questions: positive semidefiniteness and an upper spectral bound. For an exact posterior mean under additive Gaussian noise, direct differentiation gives

`D'(u) = Cov(X | U=u) / sigma²`.

The covariance is positive semidefinite. It need not be bounded above by `sigma² I` pointwise. A self-contained scalar counterexample is `P(X=a)=P(X=-a)=1/2`, with `U=X+N`, `N~N(0,sigma²)`. Bayes' rule gives

`D(u)=a tanh(a u/sigma²)`, and `D'(0)=a²/sigma²`.

Choose `a>sigma`. The exact MMSE derivative exceeds one. This is not a neural approximation, numerical error or empirical claim about image priors. It disproves a universal contractivity assertion from Gaussian observation noise alone. The marginal is a two-Gaussian mixture; Gaussian convolution does not automatically make it log-concave. A sufficient additional condition such as log-concavity of the noisy marginal can restore this particular upper bound. Whether an actual learned denoiser satisfies it must be established separately.

The correction does **not** remove every invertibility argument. For the ideal update `F(z)=mu z+gamma D(z/sqrt(alpha))`, with `mu>0`, `gamma>0` and exact-MMSE smoothness, the PSD derivative gives

`(F(x)-F(y)) dot (x-y) >= mu ||x-y||²`.

Integrate the Jacobian along the segment to obtain this inequality. Uniform strong monotonicity provides injectivity and, with the usual continuity/coercivity conditions on all of Euclidean space, global solvability. Its validity does not require the disputed upper contraction bound. A zero-noise endpoint where `mu=0` needs separate treatment. An approximate network, clipping, classifier-free guidance and a numerical inversion algorithm do not inherit exact-MMSE symmetry, strong monotonicity or the mathematical inverse merely by naming them DDIM. This is the boundary to retain at Theorem 3.1 and its Appendix C proof (lines 480–490).

### 2. Upper operator bounds do not guarantee directional amplification

For any linear map `A`, `||A d|| <= ||A||op ||d||`. Even knowing its *exact* operator norm exceeds one does not ensure expansion for each `d`: `A=diag(2,1/2)` contracts `e2` and expands `e1`. Knowing only an upper bound greater than one proves less. This directly limits the inference made after Theorem 3.4 and in the design guideline (Section 3.4; Appendix C lines 542–549).

There is also a sharper problem with the high-dimensional orthogonality step in the proof of Theorem 3.3 (Eq. 26 onward; lines 524–539). Consider a Gaussian prior with an exact MMSE denoiser `D(u)=c u`, where `0<c<1`; choose prior variance `tau²` so `c=tau²/(tau²+sigma²)`. In any dimension its Jacobian is `c I`. For the displayed one-step map `J=eta I-kappa D'`,

`J d=(eta-kappa c)d`, with `0<eta-kappa c<eta`.

The residual term is antiparallel to `d`, not perpendicular. This holds for **every** direction, including an independent uniform direction in arbitrarily high dimension. Hence the stated high-probability lower amplification by `eta` cannot follow from dimension and `0 <= D' <= I`. The map is linear, so there is no remainder to blame. The manuscript's Eq. 26 is a displayed inversion update; equating it with the exact inverse of its reverse step is a further issue, not a repair of this algebra.

A local derivative prediction also cannot be promoted to a global finite-perturbation statement without controlling the remainder along the connecting segment. None of these observations implies that real attacks always contract, or that practical inversion is robust.

### 3. Keep the direction of the certificate and its clean error

Let `Q` be an extractor, let `w` be the reference, and let `e0=||Q(x)-w||`. If `Q` is Lipschitz with bound `LQ`, then a direct triangle inequality yields

`||Q(x+h)-w|| <= e0 + LQ ||h||`.

For an acceptance threshold `R`, `e0+LQ||h|| <= R` is a **sufficient** condition for acceptance. Failure of this inequality does not establish rejection. A loose bound can exceed the threshold while every actual output remains accepted. Thus a bound-based certified radius is a lower guarantee on a robust region, not an upper limit on all possible robustness.

This is the right interpretation of the structure around Theorem 3.5/Finding 3.7 and Lemma C.2 (Eqs. 30–40). The ideal special case `e0=0` must remain visibly separate from a practical system with clean mismatch. A scalar radius used to cover mismatch does not make an exact inverse identity true. For a supremum clean error `r`, `R<r` means at least some clean cases may be excluded if that supremum is realized or approached above `R`; it does not imply every clean sample fails. At inclusive equality, an error equal to the threshold is accepted.

Likewise, `G(B_r(w))` lying inside an image-space ball does not imply that entire ball lies in `G(B_r(w))`. For example, `G(u)=(u,0)` maps an interval into a two-dimensional ball, while off-axis points in that ball have no preimage. Generator-side upper displacement bounds cannot be reversed into a universal image-neighborhood recovery guarantee. This is the quantifier to check in Lemma C.1, Eq. 27, and its interpretation in Section 3.5.

An attack's Lipschitz constant alone also fails to measure its displacement: `T_b(x)=x+b` has constant one for every `b`, however large. Its displacement term is indispensable. Different upper bounds cannot rank the realized errors of different attacks.

### 4. Invariance, normalization and null calibration are separate obligations

An injective representation preserves inequality between two different inputs. A noninjective readout can nevertheless preserve its detection decision. For instance `q(x)=||x||` is invariant to orthogonal rotations although the identity representation is injective. Even when a full representation changes, a fixed acceptance ball can contain both values. Therefore injectivity, failure of exact representational invariance and failure of thresholded watermark detection are three distinct claims. This limits Theorems 3.2–3.3 as an operational detector argument, without denying the observed sensitivity of particular implementations.

Normalization must be fixed before comparing constants. In Euclidean norm, a nonzero coordinate mask has exact operator norm one: choose a vector supported on a retained coordinate. A unitary Fourier transform also has norm one; an unnormalized transform changes both distances and constants. For fixed background and a same-coordinate injected vector, `W_y(w')-W_y(w)=w'-w`, so the exact watermark-variable Lipschitz constant is one under the same norm. A larger value can be a valid loose bound, but needs a specified parameterization; it cannot be treated as necessary physical gain. Inspect Section 3.1, Eq. 3, and the masking discussion after Eq. 5 for this distinction. Spectral calculations naturally control Euclidean norms; extending to arbitrary `l_p` requires the corresponding induced norm or explicit equivalence factors.

A noncentral-chi distance law requires an isotropic Gaussian vector, Euclidean distance and fixed center, with the appropriate scale/dimension. More samples do not force an arbitrary inverse-latent distribution to become Gaussian. Correlation, non-isotropic variance, channel selection, Fourier conventions, absolute-distance aggregation and maximization over candidate words change the null. The statement in Section 3.5 is therefore not a transferable calibration theorem. One thousand negatives provide only order-statistic resolution near 1/1000; a nominal 1% threshold is not an independently certified operational FPR. A native analytic PRC criterion and an empirical pattern-distance threshold should not be conflated.

### 5. What this establishes for the planned study

The experiment scope must not be described as RST-only: the primary digest records full regeneration in its benchmark. Equally, a model/version change does not by itself isolate independently trained encoders, and the inspected experiment specification does not establish that causal isolation. The universal perturbation symbol can formally contain a fixed-randomness regeneration map, but applying a deterministic Lipschitz argument to it still needs a domain, a bound, a coupling of random inputs and a finite-displacement assumption. Averaging over fresh noise additionally needs a stated probability distribution. The mere availability of a generic transformation symbol does not supply these ingredients or a cellwise detection forecast.

Our [mechanism dossier](../04-mechanism.md) and [rank/direction note](../analysis/rank-direction-limit.md) propose a different bounded object: exact native-encoder displacement, transported through the target reverse path and decoder into the original reader along a common-noise **C0** trajectory. It predicts chips using `p_hat=p_C0+kappa v`, then applies the unchanged reader and declared content proxy. It preserves signed directional alignment and background rather than replacing them by a product of worst-case component norms. For its fixed-word score `s(p)=w dot p/||p||`, the derivative is

`grad s(p)=w/||p|| - (w dot p) p/||p||³`, for `p != 0`.

Consequently a radial chip change has zero first-order score effect, while a transverse change can matter strongly. Equal output norm does not mean equal signed score. This elementary calculation supports measuring the relevant direction; it does not prove that the proposed surrogate will forecast decoding or binding.

The candidate has more privileged information: original source, stored marked input, target model internals, common random tensors, C0 output and target derivatives. It is neither a lightweight extractor nor a predictor from encoder labels alone. Its local remainder, branch changes, quantization, proxy error and new-family calibration can all invalidate the forecast. It must retain its frozen falsifiers and external evaluation. A successful case study would test utility under those resources; it would not refute every empirical finding here or create a universal transfer law.

The defensible positioning is **a bounded, direction-sensitive full-chain forecast case study beyond component norm bounds**, with the earlier component formulation acknowledged. No first-ever formulation claim is warranted. No threshold, hypothesis, experiment allocation, protocol, article or milestone verdict changes as a result of this note.

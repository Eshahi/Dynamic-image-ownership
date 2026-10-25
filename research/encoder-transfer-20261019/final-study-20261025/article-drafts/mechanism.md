# Mechanism: a proposed predictor of signed readable transport

**Draft status.** Author: Codex agent, 2026-10-25. This section distinguishes retained development observations, mathematical derivation and a prospective scientific predictor. The predictor has not been measured or validated. No experiment was executed for this draft. The final prospective protocol, [FS07](../07-final-experiment.md), takes precedence over provisional criteria in earlier theory notes; the independent [FS08 review](../08-review.md) accepts the research design with corrections, not the mechanism itself.

## The observation requiring explanation

Frozen F5 r2 preserves semantic-bound detection, C, on 60/60, 57/60 and 39/60 development sources under SD1.5 regeneration at strengths .1, .2 and .4, respectively. Under SDXL the corresponding counts are all zero; native Kandinsky 3 at .2 retains 5/60. Nevertheless, SDXL and MoVQ autoencoder round trips each retain 55/60. Thus foreign-codec survival and full-regeneration survival are distinct observations. These comparisons motivate a full-chain account, but do not isolate encoder training independence: preprocessing, precision, posterior convention, decoder, denoiser and scheduler also differ. Kandinsky's MoVQ independence is qualified, and equal numeric strength does not equal matched corruption. The retained verdict remains FAILS, ROUTE C. [E1]

Recorded distortion also fails to order these outcomes monotonically. Across all 58 complete F5 sources, SDXL .1 is milder than SD1.5 .2 and .4 on LPIPS, PSNR and SSIM, yet loses C. This narrows specified quality-only explanations within the observed grid; it is not a matched-distortion causal comparison, whose frozen calipers yield only two F5 sources. Posterior smoothing reduces F5 any-carrier A from 32/60 to 16/60 against its matched mode control. A is the union of semantic and instance carrier presence, **not the instance tier alone**; F5 C is already zero in both cells. Increased smoothing distortion also prevents a matched-distortion attack claim. [E1–E2]

## What must be transported

The operational endpoint is `C = semantic.read AND semantic.content_match`. Carrier presence, readable decoding, exact original-code recovery and content compatibility are different quantities. F5's robust reader forms 320 chip projections from the scaled SD1.5 posterior-mode latent through a weighted DCT operator A. For a fixed 320-sign pattern w,

\[
T_w(p)=\frac{w^\top p}{\|p\|}=\sqrt{320}\cos\angle(w,p).
\]

Positive global amplitude scaling cancels. Large latent displacement can therefore coexist with weak readable alignment or a denominator enlarged by off-pattern background. The native decoded score D(p) maximizes segmentwise over candidate bits; the recomputed branch instead tests the suspect's current content-derived code. Neither is necessarily the original-word score. The writer's signed hinge objective improves deficient chip margins through the SD1.5 encoder. It does not compute a leading singular vector or establish that the final residual lies in a top singular subspace. Quantization, fragile-tier insertion and refinement change that residual further. [E3–E4]

Saved-score contrasts illustrate loss without identifying transported signal. The paired median across complete source seed-medians of F5 decoded C1-minus-C0 score falls from 12.068 clean to 1.989, .919 and .342 under SDXL .1/.2/.4. These are differences of native search scores: their maximizing words and output-derived codes can change between C0 and C1. They are **not** fixed-codeword transport measurements. Residual separation does not establish successful detection, and approaching background does not establish complete signal erasure. The prospective measurement instead retains chip vectors and fixes w to the original input code when measuring signed transport. [E5]

## A full-chain local decomposition

Let x be the clean source and x+δ the final stored RGB8 mark, represented in [0,1]. For channel c, U_c includes actual preprocessing and input numeric conversion. Represent a sampled encoder with its native scaling as

\[
z_c(x;\eta)=m_c(U_cx)+\sigma_c(U_cx)\odot\eta.
\]

For an explicitly shared posterior tensor η, the exact paired displacement is

\[
d_c=m_c(U_c(x+\delta))-m_c(U_cx)
 +[\sigma_c(U_c(x+\delta))-\sigma_c(U_cx)]\odot\eta.
\]

Omitting the scale-difference term would incorrectly treat an input-dependent posterior as additive input-independent noise. Mode paths omit posterior sampling; the actual deterministic MoVQ path receives no invented Gaussian posterior or hard quantization. For the variance-preserving DDIM/DDPM paths, a_t=√ᾱ_t and b_t=√(1−ᾱ_t), so forward corruption is u_t=a_tz_c+b_tε. A conditional flow-model path instead uses its exact native interpolation coefficients; the alpha-bar notation is not a universal dose conversion. Shared ε cancels in the paired injection difference, a_td_c, but still controls the background trajectory and its nonlinear response. Identical seed integers alone do not certify identical tensors. [E4]

Let F_c denote the complete reverse sampler, including its state history and fixed reverse innovations; D_c its decoder; V_c output resizing and numeric transformations; and E_0 the pinned reader encoder. The complete chip map is

\[
p_c(x)=A E_0\{V_cD_cF_c(u_t(x))\}.
\]

Along the **unmarked** trajectory, a floating-path expansion gives

\[
p_c(x+\delta)=b_c+v_c+r_c,\qquad
b_c=p_c(x),\quad v_c=H_ca_td_c,
\]
\[
H_c=A J_{E_0}J_{V_cD_c}J_{F_c}.
\]

All derivatives are evaluated at their corresponding C0 intermediate states. The remainder includes finite-displacement curvature and discrepancy between the surrogate and frozen numeric pipeline. Literal RGB8 rounding has zero derivative almost everywhere; an informative tangent must explicitly omit integer rounding, retain the declared floating operations and compare float/RGB8 readout discrepancies. A straight-through approximation is not the derivative of the discrete program. Large remainder is a falsifier, not a licence to silently change the surrogate. [E4]

For e=w/√320, nonzero denominators permit the factorization

\[
e^\top v_c=a_t\|\delta\|\,
\underbrace{\frac{\|d_c\|}{\|\delta\|}}_{g_c}
\underbrace{\frac{\|H_cd_c\|}{\|d_c\|}}_{h_c}
\underbrace{\frac{e^\top H_cd_c}{\|H_cd_c\|}}_{\cos\theta_c}.
\]

Zero products are recorded directly and undefined component ratios labelled. Encoder gain, downstream gain and signed orientation are factors of one response, not independently identified causal mediators. Equal norm gain can produce positive, zero or negative signed increments. Background b_c and nonlinear decoding/binding remain necessary even after that increment is known. Native scaling matters: a_t‖d_c‖/b_t is an idealized isotropic input separation, whereas division of its squared value by latent dimension gives a different energy statistic. Neither determines C. [E4]

Rank alone supplies no missing direction. For a rank-r orthogonal projector P and an independent spherical unit direction U, E‖PU‖²=r/n. An optimized direction in range(P) retains all its energy, while one in its kernel retains none. Independently trained networks do not automatically furnish independent Haar subspaces or isotropic F5 residuals. For a general J, even spherical expected energy depends on ‖J‖²_F/n, not rank alone. These bounded algebraic examples explain the directional controls; they establish no empirical geometry for F5. [E6]

## A forecast that can fail

The proposed chip forecast is

\[
\widehat p=b_{C0}+\kappa v.
\]

One global unconstrained κ is fitted on 30 fixed development sources using R0/R1 chip changes; 30 separate sources calibrate one q90 radius. The radius is the 28th order statistic of sourcewise maximum absolute decoded-margin errors over the prescribed grid. Incomplete source maxima receive positive infinity. It is a descriptive margin radius, not a standard deviation, C probability or family-shift coverage guarantee. Negative κ is retained; a zero fitting denominator leaves the law unidentifiable. One coefficient plus a radius does **not** imply low total capacity or lightweight computation: the predictor embeds pretrained target models, the reader, C0 trajectories and their derivatives. [E7]

Predicted chips pass through the unchanged native word search and soft-binding calculation. The C0 output's seven-view semantic descriptor is an explicit proxy for the unknown marked-output descriptor. This assumption can fail even when chip transport is accurate. Its predicted per-seed C bits receive the fixed three-seed majority; the resulting deterministic source bit has 0/1 Brier loss. q90 supplies no majority probability. After outcome release, comparison with `C(p_actual, descriptor_C0)` separates carrier-model error from descriptor-proxy error descriptively, retaining their joint error table because errors can cancel. [E7]

All Phase-B forecasts and availability records must freeze before **any** marked target output is generated or released. Permitted information includes the original source, marked input, target internals, explicit noise, C0 pixels, descriptors and C0 derivatives. Marked **target** pixels, chips, descriptors, words, scores, derivatives, finite differences and realized qualities are prohibited forecast inputs. Thus the design extrapolates along C0 rather than evaluating the result it claims to predict. Computational feasibility remains unmeasured. [E7–E8]

H4 retains exactly two predictive targets: absolute predicted-versus-observed source-majority C-rate error ≤.10 **in every cell**, and aggregate law Brier loss ≤.8 times the frozen quality comparator's Brier loss, with positive comparator loss. The primary comparator uses six pre-output features: C0-to-original seed-median LPIPS/PSNR/SSIM and marked-input-to-original LPIPS/PSNR/SSIM. It is an unconstrained, fixed-penalty logistic fit with training-only scaling, no family or strength label, and no realized marked-target quality. Family-balanced validation weights are frozen. Better performance would establish usefulness relative to this comparator under unequal information and computation, not superiority over every quality function. [E8]

Statistical support additionally requires the protocol's conservative completion bounds, cellwise mismatch certificate and 13-slot Holm procedure. The sole primary Brier mean test is the fixed **uniform mixture** of bets λ∈{1/16,1/8,1/4,1/2,3/4,1}, not selected betting weights or the secondary empirical-Bernstein test. Structural missing paths make H4 unevaluated; sporadic unavailable forecasts/outcomes retain conservative numerical-completion bounds. Point success can remain inferentially inconclusive. Continuous-margin accuracy cannot rescue failed C prediction. [E8]

## Discriminating measurements and theoretical limits

The server design pairs preprocessing, mode codec, sampled codec, sampled-posterior-plus-noise direct decoding and the same sampled latent/noise with native reverse processing. A separate mode-full control examines posterior convention. Direct noisy decoding may be out of distribution and is a diagnostic, not a fair attack. Fixed norm-matched and Fourier-phase differential directions test directional advantage without creating alternate watermarks; their few draws establish neither singular spectra nor extreme percentiles. Historical round trips are not silently added to the future native-cell inventory. [E8]

A conditional Gaussian bottleneck supplies a ceiling, not the missing mechanism. If payload M and host latent Z are conditionally independent given all external information C_s, X=a(Z+Δ)+σε has fresh Gaussian noise, and downstream Y uses only (X,C_s) through a common kernel, then

\[
I(M;Y\mid C_s)\le \frac{a^2\mathbb E\|\Delta\|^2}{2\sigma^2}.
\]

Host dependence adds I(M;Z|C_s); undeclared side information invalidates the restricted channel. If M=h(C_s), conditional entropy is already zero and this bound is vacuous about payload recovery: preserved content may reproduce a content-derived code after carrier loss. A separate marked/unmarked bound concerns carrier-detection advantage under equal host/condition laws. Neither ranks these native pipelines, derives latent energy from a pixel budget, handles unequal posterior covariances automatically, or proves finite-strength erasure. [E9]

The proposed explanation therefore earns support only by sealed, fresh-source prediction. Excessive remainder, poor signed transport, descriptor-proxy failure or failure against the frozen comparator are informative negative results. Until those measurements exist, the evidence establishes a pipeline-specific development failure and a falsifiable full-chain predictor, not a validated cause.

## Compact claim and evidence ledger

All paths are relative to this draft. Author ID for every entry: **Codex agent**. Retained run ID: `20261025-0128-encoder-transfer-stage2b`, whose `stage2b-full/rows.jsonl` includes the inherited stage-2a units; no new run belongs to this draft.

| ID | Claim scope | Type | Evidence path / identity |
|---|---|---|---|
| E1 | R0/R1/K3 and D1/D3 development C counts; compound contrasts | measured; limitation | [results-2b](../../results-2b.md); [FS04](../04-mechanism.md) |
| E2 | Quality dominance, sparse matching, A union and smoothing | measured; limitation | [FS04](../04-mechanism.md); [reader contract](../analysis/reader-contract.md) |
| E3 | Native reader, distinct endpoints, writer geometry | derivation from inspected source-text contract | [reader contract](../analysis/reader-contract.md), naming `f5_latent_codec.py` / `revised_watermark_v5.py` |
| E4 | Coupled full-chain expansion and signed factors | derivation; hypothesis; limitation | [theory design](../analysis/theory-design.md), §§1–6 |
| E5 | Saved decoded-score contrasts are not common-word transport | measured; limitation | [negative-background analysis](../analysis/negative-background-analysis.md) / companion JSON, retained union run |
| E6 | Rank requires a directional model | derivation; limitation | [rank/direction note](../analysis/rank-direction-limit.md) |
| E7 | κ law, q90, proxy, information barrier | hypothesis; limitation | [prediction contract](../analysis/prediction-contract.md); [FS07](../07-final-experiment.md), §§4–5 |
| E8 | Frozen six-feature comparator, exact H4 targets, controls/inference | proposed method; limitation | [quality baseline](../analysis/quality-baseline-contract.md); [statistics](../analysis/confirmatory-statistics.md); [FS07](../07-final-experiment.md); [FS08](../08-review.md) |
| E9 | Conditional-information ceiling and content-payload limits | derivation; limitation | [conditional bound](../analysis/conditional-information-bound.md), §§2–5; [FS08](../08-review.md), §4 |

No external bibliography key is introduced in this bounded draft. Its mathematical claims cite the opened local derivations; primary-paper attribution and bibliography integration require the manuscript's separately inspected source ledger. This is an article-section draft, not human chapter approval, confirmation or publication authorization.

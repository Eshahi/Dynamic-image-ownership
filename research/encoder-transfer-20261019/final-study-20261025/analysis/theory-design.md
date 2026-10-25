# WP2 contributor: a falsifiable readable-transport model for F5

WP5 integration note: the equations and derivation remain the theoretical support. The provisional continuous-margin acceptance suggestions in section 5 are diagnostics, not the primary H4 decision. [07-final-experiment.md](../07-final-experiment.md), [prediction-contract.md](prediction-contract.md), [quality-baseline-contract.md](quality-baseline-contract.md) and [confirmatory-statistics.md](confirmatory-statistics.md) fix compound C prediction, the stronger quality comparator and the original .10/20% criteria. q90 is measured in native decoded-score units, without threshold normalization.

Status: research-only design, 2026-10-25. No model, image, detector, metric, timing or experiment was run. No raw result journal was opened or aggregated. The authoritative MAIN STATE was read once. This note uses the already reported development aggregates and inspected code; its equations and predictions precede this contributor's access to any new measurements. It does not claim that any mechanism below has been established.

## 1. What the writer actually optimizes

Code authority: `scripts/f5_latent_codec.py`, `Layout.projections`, `Reader.encode`, `robust_pgd`, `embed_rgb` and `detect_rgb`; `scripts/revised_watermark_v5.py`, `_key_test` and `_channel_result`; frozen endpoint definition in `research/encoder-transfer-20261019/protocol.md`.

Let `x` be the clean RGB8 source represented in [0,1], `x+δ` the FINAL stored F5 image, and `E0` the pinned, scaled SD1.5 posterior-mode encoder. Let `A` be the complete linear DCT/selected-band/radial-weight/sign/chip-sum operator. There are K=320 chip coordinates. Its rows use disjoint DCT slots, normalized by their squared radial weights; with nonempty chip assignments, `A Aᵀ=I`. This is an algebraic normalization of carrier rows, not empirical covariance whitening of natural-image backgrounds. Let `w(q)` be the ±1 chip pattern of the original 32-bit semantic code.

The robust writer minimizes

`L(δ)=K⁻¹ Σ_j [m* − w_j (A E0(x+δ))_j]_+²`

under a pixel L2 budget and the [0,1] box. If `r=[m*−w⊙A E0(x+δ)]_+`, its unconstrained ascent direction for improving margins is proportional to

`J_E0(x+δ)ᵀ Aᵀ (w⊙r)`.

Consequently the writer favors directions with gain **toward currently deficient signed carrier margins**. It does not maximize `||J_E0 δ||`, compute a singular vector, or prove that its final residual occupies a top singular subspace. Directions that amplify orthogonal latent coordinates can be useless. The active chip set changes during PGD. Pixel clipping, RGB8 rounding, the fragile luminance tier and robust refinement further alter the final δ. Use the final clean/marked pair, never the robust-stage target PSNR, to measure residual energy. The frozen mask power is zero; a nonzero texture mask would change the optimization geometry.

Encoder-targeted pixel optimization is established prior methodology in [PhotoGuard, §3 Eq.4–5](https://proceedings.mlr.press/v202/salman23a/salman23a.pdf). Its objective is edit disruption, not F5 carrier readability. First-order transfer analyses motivate the signed alignment term, but supply no F5 transfer coefficients ([Demontis et al., §4 Eq.13–18](https://www.usenix.org/system/files/sec19-demontis.pdf)).

## 2. The complete channel, and what a paired difference removes

Index a cell by c=(family, scheduler, strength, preprocessing, pass count). `U_c` includes its actual resize, normalization and input numeric conversion. Write its attack encoder as a reparameterization

`z_c(x;η)=m_c(U_c x)+s_c(U_c x)⊙η`.

The official latent scaling is included here. Mode paths set the posterior-noise term to zero; the actual MoVQ path must be represented by its deterministic encoder, without inventing a Gaussian posterior or hard codebook quantization. The existing code audit says its decoding uses `force_not_quantize=True`.

Let `a_t=√ᾱ_t`, `b_t=√(1−ᾱ_t)`. The noisy latent is

`u_t(x;η,ε)=a_t z_c(x;η)+b_t ε`.

`F_c,t` is the ENTIRE reverse sampler, including all denoising steps, fixed conditioning and any reverse-step random draws ξ. `D_c` is its own decoder and `V_c` its output resizing/clipping/rounding map. The observed image and F5 chips are

`y_c(x;ω)=V_c D_c F_c,t(u_t(x;η,ε);ξ)`,
`p_c(x;ω)=A E0(y_c(x;ω))`, with `ω=(η,ε,ξ)`.

No encoder is swapped into an incompatible denoiser. Conditioning that depends on the input must enter this chain; the frozen empty-prompt core avoids a separately generated caption changing between arms.

Within a family, replay the SAME explicit random tensors for a clean/marked pair. Equal seed integers alone are insufficient because RNG consumption can differ. The exact attack-encoder paired displacement is

`d_c(η)=m_c(U_c(x+δ))−m_c(U_c x) + [s_c(U_c(x+δ))−s_c(U_c x)]⊙η`.

At injection, its paired displacement is exactly `a_t d_c`. The injected ε cancels in this paired subtraction. It has NOT disappeared from the detector's problem: ε changes the clean trajectory, its local response, the output background and the variability between realizations. A coupled difference is a diagnostic counterfactual, not the detector's side information and not an estimate of independent-draw noise variance.

For a smooth floating-point approximation to the downstream path, linearization at the UNMARKED trajectory gives

`p_c(x+δ;ω) = b_c(ω) + v_c(ω) + r_c(ω)`,
`b_c(ω)=p_c(x;ω)`,
`v_c(ω)=A J_E0 J_VD J_F(c,t) a_t d_c(η)`.

The Jacobians are evaluated at the corresponding clean intermediate states, not at a globally common latent. `r_c` includes finite-displacement curvature, numeric discontinuities and mismatch between the smooth approximation and the frozen pipeline. This decomposition explicitly separates input gain, reverse transport, decoder/readout orientation, and background drift. There is no identity that turns large `||d_c||` into large positive `wᵀv_c`.

**Numeric caveat.** A literal Jacobian through RGB8 rounding is zero almost everywhere and is not the intended measurement. Declare the floating-path surrogate: preserve model weights, continuous normalization, resize kernels and clipping wherever differentiable, but omit output integer rounding and treat input casts exactly when forming `d_c`. Evaluate the reader derivative around the corresponding unmarked output; record its float-versus-RGB8 discrepancy. Do not call a straight-through estimator the derivative of the exact frozen image pipeline. Confirmatory failure of this surrogate is a legitimate failure of the law.

## 3. Noise and direction have different roles

For a fixed deterministic encoder and isotropic Gaussian corruption, latent separation is

`μ_enc = a_t ||d_c|| / b_t`.

Its energy-per-coordinate version is `μ_enc²/d_latent`; the distinction matters when comparing dimensions. An arbitrary latent rescaling changes `||d_c||`, but not a consistently transformed Mahalanobis separation. Report native scaling, shape and units. A norm ratio from unscaled SDXL latents and scaled SD1.5 latents is meaningless.

For an equal-covariance Gaussian channel with downstream processing common to both inputs, let `μ²=ΔmᵀΣ⁻¹Δm`. At a specified false-positive rate α, every downstream detector obeys the equal-Gaussian tradeoff `FNR ≥ Φ(Φ⁻¹(1−α)−μ)`. This is an impossibility constraint when μ is small, not a survival guarantee when μ is large. [Zhao et al., Theorem 4.3 and Appendix C.1](https://arxiv.org/html/2306.01953v3) explicitly condition their bound on embedding gain and warn about input-dependent VAE variance. Native sampled posteriors give `Σ(x)=a_t² diag(s_c(x)²)+b_t²I`, generally unequal between clean and marked inputs. Therefore a single scalar pooled σ is not an exact application of that theorem.

To expose readable transport, let `e=w/√K`, `H=A J_E0 J_VD J_F` and define

`g=||d_c||/||δ||`, `h=||H d_c||/||d_c||`,
`cosθ=eᵀH d_c/||H d_c||`,
`s_read=eᵀv_c=a_t ||δ|| g h cosθ`.

Set products directly to zero when a denominator vanishes, and label the corresponding individual ratio undefined. The signed angle can be negative. `g` is encoder amplification, `h` is downstream/readout gain, and `cosθ` is readable orientation. These are measured factors of one operator, not independent causal mediators. Two channels can have identical g and μ_enc while one sends signal parallel to e and the other orthogonal to e. They then have identical norm-only SNR and different readable signal. This is a constructive nonidentifiability example.

A local one-coordinate noise approximation is

`ν_read² ≈ eᵀH[a_t²Σ_post+b_t²I]Hᵀe + reverse-innovation terms`.

It must include the full chain sensitivity to each stochastic innovation. Host variation across images, stochastic trajectory variation and semantic-feature drift are additional uncertainties, not automatically Gaussian white noise. `s_read/ν_read` is useful only with its conditioning and approximation stated. A high value does not suffice for native C: the decoder uses all chip coordinates and a content gate.

**Background drift:** `b_c−A E0(x)` may be large even with a stable positive v_c. The frozen decoder divides by `||p||`, so added orthogonal energy can reduce its normalized score without eliminating the signed numerator. Conversely a host component already aligned with the semantic pattern can inflate score. The pattern is source-dependent; assuming a mean-zero independent host is unjustified for a fixed public owner and consulted source distribution.

## 4. Why the scheduler matters without determining survival

For scaled-linear betas, `β_k=[√0.00085 + k(√0.012−√0.00085)/999]²` and `ᾱ_t=∏_{k=0}^t(1−β_k)`. The frozen DDIM20 leading sequence with offset1 is 951,901,…,51,1. Strengths .1/.2/.4 retain 2/4/8 reverse updates and start at 51/151/351. These conventions are documented in the frozen protocol and the pinned [diffusers 0.35.1 scheduler source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py). For a fixed d, `a_t/b_t` strictly decreases over these starts. This orders input distinguishability under the simplified noising channel, not full-output C.

For a deterministic DDIM jump from t to s, with unclipped epsilon prediction,

`z_s=(a_s/a_t) z_t + [b_s−a_s b_t/a_t] εθ(z_t,t)`,
`J_step=(a_s/a_t)I + [b_s−a_s b_t/a_t]J_εθ(z_t,t)`.

The full reverse derivative is the ordered product of these step derivatives along the clean trajectory. Equal `a_t/b_t`, step count or scheduler names do not imply equal products. A direction can contract, amplify or rotate. DDIM's η=0 removes reverse random innovations but not initial corruption or VAE posterior sampling. These equations follow [Song et al., DDIM §4.1 Eq.12](https://arxiv.org/html/2010.02502v4); no universal monotonicity of a particular detector follows from them.

R3 uses its native cosine DDPM schedule and reverse randomness. Its `ᾱ(151)` differs from the SD-family schedule, and its encoder/decoder units and reverse map also differ. Thus a shared nominal .2 is neither a matched SNR nor matched perceptual intervention. [DiffPure §3.1 and §5.5](https://arxiv.org/html/2205.07460v1) motivates the noising/utility tradeoff, but its distributional purification result does not establish monotonic F5 retention in a nonlinear latent sampler.

## 5. A two-quantity predictive law, not a family lookup table

The primary prediction is the continuous decoded carrier margin. The additional scalar signed-pattern margin and vector error are diagnostics. The model has **one fitted global response coefficient κ plus one global calibration radius q90**; no intercept, family term, per-strength coefficient, feature selection or learned detector threshold is allowed.

For every forecast cell/source/seed, compute before reading its target marked-output detector:

1. `b=A E0(y_clean)` from the target channel's C0 image.
2. Exact `d_c` from the clean and final marked INPUT encodings under explicitly paired posterior draws.
3. `v=H a_t d_c` by a tangent-vector pass of the declared smooth downstream path around C0. Full Jacobian matrices are unnecessary. An automatic-differentiation JVP is acceptable; finite differences that regenerate/read a perturbed target image are not allowed in this confirmatory forecast stage.
4. `p_hat=b+κv`.

Define the exact frozen native decoded score as

`D(p)= [Σ_{j=1}^{32} max_{b∈{0,1}} w_{j,b}ᵀ p_j] / ||p||`.

Use the implementation's zero-energy convention. Let `τ_dec` be the already frozen searched-pattern threshold. The predicted continuous read margin is

`M_hat=D(p_hat)−τ_dec`.

The observed target is `M=D(p_marked)−τ_dec`; this equals the native read boundary, unlike the record's generic selected `score−threshold`, whose candidate/threshold can switch between recomputation and decoding. For original-word orientation also report `T_w(p)=w(q_original)ᵀp/||p||`. Large predicted T_w and small observed D would expose model failure; D can be large with an incorrect decoded word.

**Fit:** before any Phase A measurement, assign the 60 already-consulted development sources by an ID-only fixed rule to 30 fit and 30 calibration sources. Fit κ by least squares through the origin on paired chip changes `p_marked−b` versus v from R0 and R1 only, with equal total weight per source and cell. κ is unconstrained: a negative estimate is scientifically adverse evidence, not silently truncated. Report κ=1 as the zero-fit tangent reference. If `Σ||v||²=0` or required fields are missing, the law is not estimable; do not add a family intercept to rescue it.

On the 30 separate calibration sources compute one residual per source: the maximum absolute `|M−M_hat|` over the complete predeclared R0/R1 forecast grid and seeds. Let q90 be the 28th order statistic (`ceil((30+1)×.90)=28`), fixed before measurements. Forecast intervals are `[M_hat−q90, M_hat+q90]`. This is sourcewise calibration of a finite grid. An exchangeability argument would apply only to the same source/channel distribution; it does NOT certify coverage on a new family. Keep missingness visible, and do not select the set of complete sources after seeing errors. If the required calibration set is incomplete, no calibrated interval claim is made.

**Test:** freeze κ, q90, all numerical paths and the source split before Phase B. On fresh held-out sources, predict all planned seeds before opening any marked-output detector result. Test R0/R1 on new sources and a third family with no target-family marked examples used to fit or calibrate. The fact that R3's historical aggregate is known must be disclosed; call this family-held-out prediction relative to the fit, not discovery of an unknown family.

**Candidate acceptance criterion for WP5 to lock:** at least 20% lower source-averaged absolute read-margin error than the background-only prediction `D(b)−τ_dec`, AND at least 85% of fresh sources have every planned predicted margin covered by the frozen q90 interval, with q90≤1 native score unit. Apply these requirements separately to R0/R1 and the withheld family; failure or non-estimability on either is failure of the claimed cross-family law. One score unit and the 20%/85% targets are proposed design tolerances, not derived statistical guarantees. WP5 must fix them before server data; if power/cost makes this untenable, weaken the claim before execution, not after failure. Report signed bias and error by cell so a pooled average cannot conceal one failed family.

This predictor has privileged research side information: the clean source, the final residual, target-model internals, C0 outputs, explicit noise draws and the fixed reader. The deployed F5 detector still receives none of the clean reference or target-model tangent. The contribution would be predictive mechanism measurement, not a new blind detector or a cheap black-box attack. The cost of tangent passes belongs in Phase A/B budgeting. If the platform cannot supply the JVP, leave the law untested rather than substitute outcome-adjacent marked-output finite differences.

## 6. What the law predicts about C, and what it cannot identify

Historical `C = semantic.read AND semantic.content_match`. It is not recomputed-pattern presence, exact original-code recovery, or the fragile tier. F5 soft binding compares the decoded code with seven-view CLIP-derived features of the suspect; its likelihood also uses an inferred decoding error rate. Neither `||d||` nor one signed margin identifies the decoded bits, these features, or C.

The vector law predicts D and a decoded word. Predicting its input to soft binding requires a separate justified approximation to the suspect's semantic features. Using actual marked-output CLIP features or content status to predict C would leak the target endpoint. The following explicit **C0 semantic-proxy extension** has no further fitted parameters and can be declared jointly with the chip law. It is a falsifiable approximation, not an identified consequence of the norm or transport equations.

For the target channel's unmarked output, obtain `f0` with the unchanged seven-view semantic-feature extractor. Treat `(p_hat,f0)` as a synthetic detector input: derive the recomputed semantic code `q0` from f0 using the frozen profile; run the existing `_key_test(p_hat, semantic_table, q0)` and `_channel_result`; derive its decoding-error-rate estimate; call the unchanged soft-binding status calculation with its predicted decoded word and f0; finally set `C_hat=predicted_read AND predicted_content_match`. All thresholds, radii, tie rules and angle-grid settings remain frozen. The instance tier is unnecessary for C and must not be used to rescue it. This procedure uses the **unmarked target-output** descriptor, never the marked target-output descriptor. Its substantive assumption is that the true marked output's descriptor crosses the same binding boundaries as f0, even though its latent chip vector changes.

After the forecast has been frozen and actual outputs are released, compute an explicit diagnostic `C_proxy_oracle=C(p_actual,f0)` using the actual chips but still f0. Compare it with `C_actual=C(p_actual,f_marked)` to measure semantic-proxy errors; compare `C_hat` with `C_proxy_oracle` to measure carrier-model errors under a common descriptor. Keep their joint 2×2 error table because errors can cancel; they are not additive causal fractions. Also report the paired descriptor angle and the soft-binding distance difference. This diagnostic MUST NOT be used to revise predictions, fit κ or change the proxy on held-out data.

If WP5 calls H4 a **C-survival law**, it must predeclare both continuous-margin and compound-C criteria. A proposed companion criterion is at least 85% correct source-majority C predictions AND absolute predicted-versus-observed source-majority C-rate error at most 0.10, separately in R0, R1 and the withheld family, with every planned source retained and missing predictions counted as unsuccessful. Evaluate all fixed seeds and apply the same majority rule to predicted and observed C. Floor/ceiling cells can trivially meet C agreement, so C agreement alone is insufficient: the continuous-margin improvement and coverage requirements above must also pass. If this proxy is omitted, unavailable or fails, mark H4 C prediction failed/not estimable as appropriate; a good read-margin fit cannot silently replace the promised C endpoint. These are proposed engineering tolerances for WP5 to freeze, not guarantees supplied by theory.

Without the explicit proxy extension, the honest theoretical implication is one-sided: predicted unreadability implies predicted C failure, while predicted readability leaves C unresolved. If a forecast interval is entirely below zero, forecast `read=false, C=false`; otherwise report the continuous prediction and `C not identified`. With the extension, publish its point C prediction even where the interval crosses zero, with uncertainty flagged; do not selectively abstain to improve accuracy. Report observed readable-but-content-failed, readable-and-content-matched, found-but-not-read and absent separately. Even a correct read forecast is not a causal explanation of semantic-binding failure.

## 7. The fifteen cells: fixed conditional predictions and explicit silence

All numeric C counts here were already disclosed development aggregates, not fresh forecasts. They motivate challenges to the model. The model form is fixed now; per-source numeric predictions require the approved server measurements and must be frozen before their marked outputs are examined.

| Cell | Consequence of the proposed model before measurements | What is not identified / falsifier |
|---|---|---|
| clean | No attack channel: observed clean F5 chips can be a code/reader consistency control. High clean original-word margin is the writer's intended effect. | Not an out-of-sample test of transfer; final quantization and fragile-stage changes can prevent perfect margins. |
| R0 .1 | Highest input `a/b` of the three R0 strengths for fixed d; use its full tangent/background for M. Existing C=60/60 is descriptive. | No numerical C forecast from scheduler alone; κv must predict the measured margin. |
| R0 .2 | Lower input `a/b` than .1; retain F5 only if directional downstream gain and background permit. Existing C=57/60. | Monotone read/C decline is an additional hypothesis, not a theorem. |
| R0 .4 | Lowest R0 input `a/b`; stronger initial loss of distinguishability. Existing C=39/60. | A changed reverse derivative can break margin ordering; a blanket monotonic law is falsified by persistent reversals. |
| R1 .1 | Same scalar schedule as R0 .1, different d,H,b; therefore no equal-survival prediction. Existing C=0/60 challenges encoder-norm-only accounts. | Small d, rotated H, background energy and content failure remain alternatives until measured. |
| R1 .2 | Same qualification; existing C=0/60. | Floor C cannot discriminate these mechanisms; inspect continuous D and binding separately. |
| R1 .4 | Smaller input `a/b` than R1 .1/.2; existing C=0/60. | The floor supplies no ranking of true readable transport or attack superiority. |
| R1 rinse | Local displacement transports by `J_T2(T1(x)) J_T1(x)δ`, plus both quantization remainders. Evaluate second background at first clean output. | Neither squared survival probability nor equivalence of .1+.1 to .2 follows. Second pass can rotate/recover a coordinate. |
| R1-smooth | Different encoder map: average of eight perturbed modes. Its derivative is the average of local derivatives, including clipping effects. | Jensen gives `||mean(J_j d)||≤mean||J_j d||`, not ≤`||J_at_center d||`. No guaranteed improvement over mode. |
| R1-mode | Removes posterior sampling and its input-dependent covariance term; gives the correctly matched control for smooth. | Removing noise can either increase or decrease an individual margin because trajectory/background change; do not assume a C gain. |
| R3 .2 | Use native MoVQ displacement, cosine schedule and full stochastic DDPM response. Existing C=5/60 despite D3=55/60 motivates downstream transport measurements. | Neither latent dimension nor ᾱ alone ranks it against SDXL. No hard-quantization explanation without a matching runtime. |
| D1 | `a=1,b=0,F=identity`; predictor reduces to SDXL decoder→F5-reader transport plus baseline. Existing C=55/60 rejects universal destruction by the independent autoencoder round trip. | Infinite norm-SNR is uninformative. D1/R1 differ in posterior, precision path and diffusion; not a denoiser-only intervention. |
| D3 | Same no-diffusion law with the actual MoVQ path; existing C=55/60. | Not proof that the encoded carrier is semantically retained or that full R3 will preserve it. |
| X1 | Transport only through one resize cycle and the reader; no latent diffusion noise. Existing resize survival is high. | Pixel fidelity or low-pass intuition alone gives no native C guarantee. |
| X2 | Compose two resize operators before the reader; possible extra attenuation is testable. | Native normalized score need not fall monotonically even for contractive pixel maps. |

The already reported round-trip/full-pipeline contrasts rule out the strong statement that encoder independence alone must annihilate F5. They do not by themselves locate the extra loss. Their numerical sources are the frozen results documents and STATE, as summarized in `01-literature-synthesis.md`; this contributor did not recompute them.

## 8. Minimal server measurements and discriminating interventions

These are specifications for later approved compute. No new infrastructure or runnable experiment code is supplied here.

**Required paired records:** final x and x+δ; original semantic chip pattern; the clean and marked attack-encoder mode and posterior scale (where applicable); explicit shared random tensors; continuous chip vectors before and after each measured path; native recomputed/decoded scores and thresholds separately; decoded code, `read`, soft distance and content status; output quality referenced to both published mark and original. Store the original clean/marked residual norm in [0,1] and each model's native latent units. No bit independence is assumed.

**Minimum controlled paths within one compatible family:** (i) exact same-preprocessing mode AE round trip; (ii) same-preprocessing sampled AE round trip; (iii) mode-plus-forward-noise-and-direct-decode; (iv) mode-plus-identical-forward-noise-and-native-reverse-sampler; (v) native sampled full path. For (iii), decoding `u_t/a_t` is a fixed diagnostic that keeps signal scale and exposes additive corruption; record that noisy latents may be outside the decoder's training support and do not treat its fidelity as a legitimate attack. Pair (iii)/(iv) by the SAME mode and injected ε, while acknowledging direct-decode versus reverse-sampler is the intervention. Paired mode versus sampled full paths isolate that runtime choice more closely than historical D1/R1. No transplantation of an encoder across incompatible denoisers is an isolation experiment.

**Directional comparison:** for each final δ compare attack-encoder gain with fixed-seed random residuals matched in pixel norm and, in a second diagnostic, matched per-channel spatial power spectrum. Enforce the same input box/quantization handling and report any norm change. These are separate diagnostic perturbations, never new watermark variants. Randomizing a residual's direction tests whether the writer exploits special sensitivity; spectrum-matching reduces a trivial frequency-content explanation. Neither null distribution establishes a universal top singular space.

### Computation interfaces for budgeting, without a runtime claim

Per source/family, the exact encoder-input displacement requires two attack-encoder primal evaluations (clean and final mark), cached across strengths and seeds where their input precision/path matches. A sampled encoder reuses those posterior parameters and the declared η; changing η does not require re-encoding. Each source/cell/seed forecast then requires one C0 trajectory, one directional tangent through its entire reverse sampler, one decoder/output-transform tangent, one pinned-reader tangent, and the C0 seven-view CLIP evaluation if the C extension is used. One JVP yields all 320 predicted chip displacements; it is not 320 full sampler passes. Cache the C0 primal/output/descriptor shared with the ordinary C0 evaluation when permissible.

For N reverse updates, define `T_c0 = T_encode + N*T_unet_primal + T_decode + T_read + T_clip7`. The additional law cost is `T_tangent = N*T_unet_jvp + T_decode_jvp + T_read_jvp + T_resize_jvp`; input encoder-pair work is amortized separately. These are interfaces to be timed only on the later approved server, not measured values. N is 2,4,8 for R0/R1 .1/.2/.4. Rinse has two 2-step paths, with the second tangent receiving the first pass's output displacement; its input encoding/resize and intermediate RGB8 approximation also need a tangent. R3 .2 has four native reverse updates plus its fixed innovation tensors. Smooth adds eight mode encodings per input (16 for a clean/marked pair), cached across diffusion seeds; mode adds two. D1/D3 use zero denoiser steps. X1/X2 use zero attack-model calls.

Do not budget `T_unet_jvp` as zero or assume it equals one primal call: architecture, forward-mode support, dtype and checkpointing determine its cost. Use a separately reserved multiplier range and replace it with server preflight measurements before committing a fixed full-grid count. If only reverse-mode differentiation is available, specify the chosen JVP construction and memory cost explicitly; repeated scalar-output backpropagation is not the same cost. A scalar signed-noise-variance diagnostic can use a VJP to accumulate `eᵀH` and its sensitivity to each stochastic innovation, but that is **additional** backward work and is not required to compute v. No empirical ν is claimed from only three seed values.

This is not a one-forward-pass tautology: the only target output examined before prediction is C0, and the target marked trajectory is never evaluated to construct v. The model extrapolates a finite displacement through a local surrogate and then nonlinear chip decoding and optional semantic proxy. The eventual marked forward pass is separate scored ground truth. Computationally expensive privileged prediction is still privileged prediction; if it is too costly to be practically useful, report that limitation rather than claim a cheap transfer rule.

**Primary falsifiers:**

1. **Encoder-amplification story:** F5 has no gain advantage over the prespecified random residuals in its own encoder, or target failure persists despite comparable g. The second result rejects encoder gain as a sufficient explanation, not the existence of optimized signed gain.
2. **Directional-transport story:** v is well aligned and large, and the model predicts positive read margins, yet held-out actual D is near null. This rejects the local law or reveals large unmodeled quantization/curvature; it cannot be repaired using a family intercept.
3. **Noise-only story:** controlled noising with comparable Mahalanobis separation yields markedly different D under compatible downstream samplers. Initial μ is then insufficient. Equal raw strength is not the required comparison.
4. **Content-only story:** native read already fails while content descriptors remain close. Conversely reliable read with failed binding implicates the compound gate rather than carrier removal. Describe conditional tables, not an identified causal mediation percentage.
5. **Smoothing cancellation story:** smoothing leaves directional g and downstream v unchanged or increases them relative to matched mode, while C remains at floor. A floor endpoint cannot rescue the claimed mechanism.
6. **Universal law:** source-held-out or family-held-out error/coverage criteria fail. Publish that failure and the per-cell residuals; do not fit parameters on the failed confirmation set.

## 9. Source access and handoff record

The existing V2 literature cards and their limitations were read: PhotoGuard, Zhao, DiffPure, Demontis; also the WP1 synthesis and pre-outcome T4 mechanism synthesis. This contributor directly reopened primary sources on 2026-10-25 via the web tool (direct URL retrieval, not a new search):

| Source | Sections inspected in this contribution | Role |
|---|---|---|
| [PhotoGuard, PMLR final PDF](https://proceedings.mlr.press/v202/salman23a/salman23a.pdf) | §3 Eq.4–5; §4.2, Table1 context | Encoder-targeted optimization precedent; no watermark survival theorem. |
| [Zhao et al., arXiv v3](https://arxiv.org/html/2306.01953v3) | §3.3 Algorithm1; §4.1–4.2; §5 setup; Appendix C warning | Conditional Gaussian impossibility and utility assumptions. |
| [DiffPure, arXiv v1](https://arxiv.org/html/2205.07460v1) | §3.1; §5.2; existing V2 card includes §5.5 | Noising/reverse-processing distinction; not an F5 guarantee. |
| [Demontis et al., USENIX final PDF](https://www.usenix.org/system/files/sec19-demontis.pdf) | §4 Eq.13–18; §5.1.1 setup and Figure5–6 text | Directional first-order transfer motivation. |
| [DDIM, arXiv v4](https://arxiv.org/html/2010.02502v4) | §4.1 Eq.12; §4.3; §5 introductory experimental setup | Reverse-step derivative; no imported F5 empirical result. |
| [diffusers v0.35.1 DDIM source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py) | scheduler source read as text; frozen thesis protocol supplies selected settings | Pinned schedule convention, not executed code. |

No verbatim paper quotation is used. The mathematical transport expansion, counterexample, law and measurement proposal are this contributor's derivations. Root should add these retrievals to its consolidated log if it uses this note, reconcile the proposed fitting/calibration split and accuracy thresholds with WP5, and preserve the no-raw-journal-before-hypothesis-freeze order.

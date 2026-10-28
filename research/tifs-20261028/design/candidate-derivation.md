# Three candidate derivations and a bounded development screen

Author: Codex design agent, 2026-10-28. Authoring escalation, not an independent review. No scientific code was executed. This is a design recommendation; the parent protocol must freeze exact identifiers, seeds and implementation parameters before server outputs exist.

## Recommendation and claim boundary

Select **A, conditionally**, because it can produce a new intervention with a matched ablation and a security-relevant endpoint. Select **C only as a separately preregistered backup**, with no automatic switch after inspecting A's outcomes. B is a useful engineering baseline, but the generic combination of a robust carrier and content verification is already occupied; its decoding and security assumptions are also less straightforward than its name suggests.

A's defensible claim is narrow: *post-hoc constrained pixel optimization through finite native noisy-codec surrogates can improve full-regeneration retention of an unchanged content-bound reader across design families and an optimization-excluded family, at controlled clean distortion*. This is neither the first regeneration-robust watermark nor the first latent/noise-aware watermark. It remains a pixel-domain writer, not the proposal's latent-generation method.

The existing SDXL stagewise values (.66 codec, .08 noise-only, .08 native) motivate an intervention, not a causal conclusion. Encoder amplification already transfers while detection fails. K3 is **optimization-excluded**, not discovery-unseen: its 61/200 held-out retention and mechanism results already influenced this proposal. A truly unseen family requires a subsequent frozen confirmation, without consulting its outcomes for method design.

## A. Finite noisy-codec EOT with the frozen F5 reader

Let x be RGB pixels in [0,1], w the fixed F5 semantic chip signs derived from the original image and OwnerID, and P the unchanged F5 latent chip reader. Let R_f resize to the native family resolution, E_f and D_f be the pinned encoder and decoder, and S_f return decoded pixels to the reader resolution. Define

    T_f,t,e(x) = S_f D_f(a_f,t E_f(R_f x) + b_f,t e).

The latent scaling, posterior convention, actual inference timestep, a and b must come from the native attack implementation. A nominal strength is not an interchangeable noise standard deviation across families. Do not renormalize away a, undo b, or divide the latent by a before decoding. Noise-only decoding is a surrogate outside the decoder's ordinary input distribution, not a diffusion output. Its value is tested by full native regeneration.

For signed margins m_i(y)=w_i P_i(y), use

    L(y) = mean_i max(0, tau - m_i(y))^2
    min_delta  L(x+delta) + mean_(f,t) E_e L(T_f,t,e(x+delta))
    subject to ||delta||_2 <= sqrt(3HW) 10^(-B/20), 0<=x+delta<=1.

Use frozen F5 tau=4 and B=52 dB for the initial robust residual, with equal clean and surrogate terms. This is a concrete conservative starting point, not an optimized setting. The final image must also satisfy the final clean quality gates after fragile-tier writing and RGB8 quantization. Keep F5's existing owner, semantic projections, seven-view features, fragile instance stage, thresholds and decision table unchanged. A differentiable robust-chip surrogate does not guarantee semantic binding; report carrier failure and binding failure separately.

For a bounded implementation, fix 150 updates, alternate SD1.5 and SDXL, and cycle their native .1 and .2 timestep settings. Draw one independent Gaussian noise realization per update from a recorded stream; hold a separate fixed eight-noise set only for diagnostics. Backpropagate one family graph at a time and accumulate its clean-plus-surrogate gradient. Use normalized projected updates, inherited F5 step-size schedule, and no early selection by native outcomes. The codec-only ablation sets b=0 and a=1, with the same families, resolutions, number of backward calls, clean term, budget and fragile processing. Match gradient evaluations, not merely iteration labels. Repeated deterministic codec calls deliberately preserve this accounting.

Do not load full diffusion models during writing. Frozen VAE weights still require differentiable input paths; `no_grad` around the encoders would silently invalidate optimization. SDXL encoding must respect its fp32 requirement. Keep only the two VAEs and one active autograd graph, or offload the inactive VAE; delete each graph immediately. A 24 GB fit is plausible but unmeasured. Rehearsal must record peak allocated and reserved memory and stop on an unsatisfied cap. Never infer feasibility from the previous machine's anomalous 49 GB report.

**Nontrivial test.** Improvement over F5 alone is insufficient: codec exposure or extra compute could explain it. Improvement over the compute-matched codec ablation on native SDXL, combined with retained SD1.5 performance and K3 gain, is the contribution. The ablation is an intervention on the writer objective, not proof that noise injection is the unique physical removal cause.

**Counterexample.** A denoiser can project every optimized residual onto a watermark-free manifold even when noisy-codec margins are high. Conversely, a semantic carrier may be unreadable in directly decoded noisy latents but recover after denoising. Optimizing average chip margins can also sacrifice a few essential chips or the source semantic code. Therefore no implication of the form “proxy passes, native must pass” is valid. Native endpoints decide.

### Cheapest useful screen for A

Use the first 24 sources under a committed ordering of the 60 development identifiers; two other development sources rehearse execution separately. No outcome-based replacements. Arms: F6-noise, F6-codec, unchanged F5 r2, v5 r3, WAM, VINE-R, and C0. Native cells: SD1.5 .2, SDXL .1 and .2, K3 .2. Three fixed seeds yield 2,016 outputs including C0. Reader calls and quality evaluation are additional, explicitly budgeted work. All arms receive the same attacks; interpret each detector's distinct endpoint honestly.

Proposed necessary development GO conditions, all required: F6-noise clean both-match >=23/24; every clean source PSNR>35, SSIM>.9, LPIPS<.1; paired clean LPIPS median increase versus F5 <=.005 and PSNR median decrease <=1 dB; native source-majority semantic attribution >=18/24 in SDXL .1 and .2 and K3 .2; at least six additional successes versus F5 in each SDXL cell, at least four in K3; at least four additional successes versus F6-codec in each SDXL cell; SD1.5 .2 no more than two successes below F5. These are screening thresholds, not significance tests or publishable guarantees. F6 superiority over VINE-R presence is not required or implied.

Freeze 24 ordered donor-recipient T4 pairs, two residual-transfer scales, and 24 T5 pairs chosen by a documented content rule before new outcomes. Count successful false attribution separately from delivery of the donor carrier. Zero events is necessary, but not sufficient for strong security: with 24 independent negative units, zero gives a one-sided 95% upper bound about 11.7%; the historical 0/20 and 0/66 bounds are about 13.9% and 4.4%. Pair dependence further limits interpretation. T5 must include real distinct near-duplicates in confirmation; semantic similarity alone is not an adversarial collision test.

Safety blocks remain missing and also enter a conservative failure count for positive GO; never retry with a new seed to rescue a majority. Unresolved negative calls prevent a clean specificity GO. Distinguish scientific kill, incomplete screen and resource stop. Do not call a timed-out partial subset a successful screen.

Historical anchors are 119 seconds/source for F5 marking and Phase B's 17,800 outcomes in roughly 7.3 hours, with detector and quality stages overlapping; these are not measurements of F6. Reserve 1.5 hours setup/rehearsal, 7 hours all marking, 2 hours native outputs, 1.5 hours reading/quality, .5 hours T4/T5, .5 hours secondary distortions and 2 hours contingency/retrieval: 15 total. The native estimate has margin over linear historical scaling; F6 writing remains the dominant unknown. During the two-source rehearsal, extrapolate each required stage with 1.5 times measured per-unit time and stop if projected total exceeds 15 hours. Do not silently shrink n or iterations. A smaller design requires a new pre-output freeze.

## B. Content binding in VINE-R's fixed 100-bit carrier

The technically meaningful question is whether content verification reduces false attribution **conditional on the same delivered carrier**, with a measured retention cost. Test the same marked images with binding on and off. Comparing a new VINE payload against F5 confounds carrier and binding.

A direct payload might allocate 32 semantic bits, 32 instance-hash bits and 36 owner-conditioned check bits. This totals 100 with no error-correction overhead. It is not equivalent to F5's 320-chip semantic channel plus separate fragile channel. VINE's known-message 69/100 decision is not a guarantee that arbitrary 100-bit messages can be decoded. Even an illustrative independent bit accuracy .98 yields probability .98^100 approximately .133 of an entirely correct payload; exact verification of 36 check bits alone gives .483 before descriptor errors. These illustrative calculations are not measured VINE error models. Accepting check-bit errors instead requires a new null model and calibration.

A registry-assisted construction avoids that decoding problem: store the expected 100-bit owner-and-record message and published-image descriptor, then require both known-message presence and descriptor consistency. Its mathematical event is A(y,r)=M(y,m_r) AND d(F(y),F(x_r))<=c. This is straightforward, but changes detector side information to a registry and is not a new provenance primitive. A public OwnerID-derived tag is not a MAC; anyone able to invoke the public writer can re-embed or spoof an owner label. Neither construction proves legal ownership or cryptographic unforgeability.

The cheapest screen reuses the VINE-R arm above and performs binding-on/off reads on identical T3/T4/T5 images, with fingerprint-only as a third comparator. It can fit below two incremental hours if existing descriptors are reused, but only after exact payload and decision rules are independently frozen. Kill the research-contribution claim if the only novelty is replacing an existing carrier, if no negatives deliver the carrier (making binding reduction unidentifiable), or if successful T3 attribution loses more than 10 percentage points. A positive result supports a bounded system comparison, not yet a TIFS method contribution.

## C. Finite reader-response survival predictor

Abandon the full-chain tangent law explicitly. The new target is a finite, empirical predictor of each method's own reader decision after native regeneration. For each arm a, define a normalized score margin u_a(y) relative to its frozen detection threshold. Features can be the clean margin, mean noisy-codec margin, its variance, and codec-only margin; estimate noisy features with four common-random-number draws on clean/marked pairs. Common noise reduces variance of a contrast but does not create causality. Fixed feature definitions must work for all four readers; do not use ground-truth native detections as features.

Fit a small ridge logistic model p=logistic(beta_0+beta^T features) on source-disjoint training data. Compare against a prespecified quality-only logistic model with the same fitting split and penalty; include the base-rate constant predictor. No family IDs, method IDs, fitted per-family coefficients, or post-failure feature expansion. Use Brier score as primary and calibration plus log loss as secondary. Bootstrap whole sources, preserving all arm/cell/seed dependence.

For development, divide 60 identifiers into 30 fit, 10 calibration and 20 locked evaluation sources; seal forecasts before releasing new native outputs. These sources and families already have historical results, so “prospective” describes prediction sealing, not pristine discovery independence. A new seed is not a new source. Confirmation needs fresh sources and a family excluded from predictor fitting. Report leave-one-method-out stress tests without selecting the best fold.

Necessary screen success: Brier improvement >=.05 over quality-only on the locked sources, positive improvement in at least three of four methods, and positive improvement on optimization-excluded K3; additionally reject an intercept-only explanation. This is a preregisterable practical bar, not a universal law. Counterexample: two regenerators can share exactly E, D and injection noise, yet use denoisers with opposite watermark behavior. Any predictor seeing only the noisy codec gives identical forecasts. Therefore no model-agnostic guarantee is possible without assumptions about denoising.

Four arms, three families and three seeds at 60 sources need 2,160 marked native outputs plus C0 and finite proxies. A 10-15 hour standalone screen is plausible using retained development clean marks, with server rehearsal determining feasibility. Do not run both A and C under one 15-hour promise. C is strongest as a falsifiable empirical calibration study; a second failure table alone will not meet the positive-contribution requirement.

## Prior art and secondary reporting

[VINE, ICLR 2025](https://arxiv.org/abs/2410.18775) already supplies regeneration robustness using blur surrogates and a generative prior. [OptMark, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/download/38094/42056), sections 2-3, already supplies inference-time latent optimization and gradients through diffusion. DrawMark (ICASSP 2026, DOI 10.1109/ICASSP55912.2026.11464504), inspected by the parent research agent, adds predicted-noise steering with frozen diffusion and trained adapters. This agent's PDF fetch failed; its detailed comparison remains delegated evidence. Thus A's possible distinction is the precise post-hoc/frozen-reader/finite-surrogate transfer intervention, pending hostile review, not “noise-aware watermarking.” Shallow Diffuse and MarkNull also require the parent's prior-art check before any novelty statement.

[DREW](https://arxiv.org/html/2406.02836v2), section 3, combines watermark-assisted retrieval and error-controlled identifiers. [Kazempourradi et al.](https://arxiv.org/html/2610.04151v1), sections 3.3 and 6-7, explicitly examines watermark/fingerprint complementarity, second-stage verification and near-copy false matches. They pre-empt B's generic registry claim. No absent search hit establishes novelty for C.

All three designs include the user's small, frozen article-only distortion grid on every clean marked arm, with no diffusion and separate reporting. It cannot choose the primary contribution. Exact strengths belong in the common protocol. Quality comparisons must retain separate PSNR, SSIM and LPIPS: F5's historical PSNR advantage and VINE's LPIPS advantage do not establish equal quality. Human quality assessments for these new images remain missing. Final verdict: **conditional feasibility for A's screen; no present basis to promise a TIFS paper**.

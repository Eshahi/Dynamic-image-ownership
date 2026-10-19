# T4: mechanism, falsifiable predictions and adaptive threat

2026-10-19. Pre-outcome design research. No GPU, model loading, mark scoring, new image outcomes, held-out access or code/weight download. The only new cached artifacts are primary paper HTML. This topic supplements the frozen protocol; it does not change its decision rule or authorize an extra experiment.

## Decision for the core

Keep SDXL .2 as primary, the SD1.5 anchor, SDXL posterior-mode VAE-only reconstruction and a resize-only 512→1024→512 control. Keep the SD1.5 reader fixed in every cell. Report raw carrier evidence separately from content binding. An independent encoder can attenuate F5's specially amplified directions, but independence alone predicts neither certain erasure nor certain survival. A positive result demonstrates transfer to the tested complete SDXL pipeline; a negative result is operational failure under that pipeline, not proof that encoder weights alone caused it.

The core cannot certify robustness to an adaptive adversary. Recommend the bounded, encoder-aware ensemble proposal below only as a separately approved extension. A trained robustified encoder is scientifically interesting but adds a research project with uncertain optimization and quality costs; do not silently include it in the USD15/15-hour core.

## Three encoders and the exact carrier

Let x be the original RGB image, x_w=x+δ the final saved mark, and U,V the declared up/downsampling operators. E_w is the writer's SD1.5 posterior-mode encoder with its input normalization and latent scaling. E_a is the attacker's encoder, which may be independently trained. E_r is the reader's pinned SD1.5 encoder; here E_r=E_w, even when E_a is SDXL. These roles must never be collapsed into a single E.

The code fixes F5 r2 at robust-stage PSNR 52 dB, 150 gradient steps, chip target margin 4, radial DCT index band [4,32), whitening exponent 1, one refinement, soft semantic binding and seven-view CLIP. The actual final image also includes a fragile luminance tier, refinement, clipping and RGB8 quantization. Therefore 52 dB is **not** a bound on final-image δ; use measured final clean quality. The writer targets signed chip margins in E_w(x_w); it does not maximize an attacker's encoder norm, denoiser robustness or an end-to-end SDXL score.

Let P denote the frozen weighted DCT-to-chip linear map and b the signed chip pattern determined by owner/profile and semantic code. A schematic clean margin vector is diag(b)P E_w(x_w). The codec's nonlinear key tests, correction, recomputed-pattern path and binding rule remain authoritative; this linear notation is diagnostic, not a replacement detector. Low frequency in this latent coordinate system is not automatically low frequency in RGB or in another VAE's latent coordinates.

For deterministic mode encoding, write a complete attacked image as

    y_a(δ, ε) = V D_a H_a,t( a_t E_a(U(x+δ)) + b_t ε ),
    a_t = sqrt(alpha_bar_t), b_t = sqrt(1-alpha_bar_t).

D_a includes inverse latent scaling; H includes denoising and fixed prompt conditioning. For native pipelines that sample the VAE posterior, replace E_a by the sampled, input-dependent encoder. That adds a separate source of randomness. Diagnostic VAE-mode output is V D_a E_a(U(x+δ)) with matching scale conventions, **not** an img2img call at a nominal zero strength.

## Noise scale and the removal bound

Zhao et al., Theorem 4.3, gives a conditional Gaussian-channel testing bound. In equal-covariance coordinates, if d=||φ(x_w)-φ(x)||/σ, then FNR ≥ Φ(Φ⁻¹(1−FPR)−d). Large d only weakens that restriction; it does not give a lower bound on recovery. Input-dependent VAE variance requires additional assumptions (Remark C.6). Their evaluation covers 500 COCO and 500 generated images, not F5. [Primary source](https://arxiv.org/html/2306.01953v3).

Our derivation: dividing the displayed noising equation by a_t gives effective σ_eff=b_t/a_t and

    d_a,t = (a_t/b_t) ||E_a(U(x_w)) − E_a(U(x))||₂.

This is a norm in the attacker's **scaled** latent coordinates. It is not RMS displacement divided by per-coordinate σ: an RMS summary must be multiplied by sqrt(latent dimension) to recover d. It is not comparable across encoders before accounting for actual scaling, resizing, dimensions, posterior sampling and noise law. A general equal-covariance Gaussian channel uses sqrt(ΔzᵀΣ⁻¹Δz). A flow-matching channel has a different interpolation/noise equation; DDIM alpha formulas must not be pasted onto FLUX.

At fixed per-image FPR f and desired per-image TPR q, this idealized bound makes d ≥ Φ⁻¹(1−f)−Φ⁻¹(1−q) necessary, never sufficient. For f=10⁻⁴ and q=.75 this is about 4.39. This illustration is neither the F5 decision threshold nor a guarantee for the study's source-majority statistic. Three dependent seeds and a mixed population do not inherit this single-pair Gaussian number. Do not estimate a uniform Lipschitz bound from a few observed pairs.

The corresponding local sensitivity L_a=||ΔE_a||/||δ|| can be small or large independently of L_w. An independent encoder need not be statistically independent of E_w's gradients: both models learn related natural-image structures. Conversely, even equal architecture and equal latent width do not imply corresponding channels or DCT axes. Merely measuring a large latent displacement can include irrelevant directions; it cannot establish decodable watermark information.

The original F5 design's statement that an invisible mark is safe only when L is small has an ambiguous referent. Small L helps **removal** under the specified noise model. It does not help watermark survival. Preserve the historical design record but use the explicit inequality above in new reporting.

## Transfer Jacobians: what must survive

For small δ and fixed noise/prompt, the first-order difference in the reader's chips is

    Δp ≈ P J_Er(y0) V J_Da J_Ha (a_t J_Ea(Ux) U δ),

where y0 is the attacked unmarked image and all derivatives are evaluated along the corresponding clean trajectory. Resizing is locally linear before clipping/rounding. This linearization is a hypothesis aid, not an error-controlled certificate: the network is nonlinear and the actual quantized δ need not remain in one locally linear region.

If one approximates a writer step by δ∝J_Ew(x)ᵀPᵀb, then the relevant signed transfer includes

    bᵀ P J_Er V J_Da J_Ha J_Ea U J_Ewᵀ Pᵀ b.

F5 actually optimizes hinge losses with adaptive chip weights and projections, so this is illustrative rather than an exact algorithm identity. It shows why a large ||J_Ew δ|| alone misses attacker gradient alignment, denoiser retention, decoder reconstruction and reader alignment. A direction can remain large in E_a while becoming nearly orthogonal to the reader's pattern. A tiny ||ΔE_a|| relative to equal-covariance noise limits any image-only reader's discrimination; a large one merely leaves discrimination possible.

The unmarked host term P E_r(y0) remains in each score. Scores can fall through host interference or semantic-code drift even if some signed perturbation remains. Conversely, a raw score can remain high because of an accidental host projection. Paired unmarked channels and wrong-owner calls are therefore required. Same-seed paired residuals are useful descriptive sensitivity diagnostics if already retained, but they are not samples from independent experimental units or theorem certificates.

Content preservation, carrier presence and semantic binding are separate. Preserve the implementation's exact S/C/Q/J definitions and report at least semantic key-found, corrected/decoded code evidence, soft content distance and C. With the fixed reader, count key-not-found versus key-found-but-C-failed separately, including missing/safety-blocked outputs as a third status. Continuous CLIP similarity to the source can contextualize content drift, but must not gate the primary denominator. The registry's content descriptors, when reported, are additional side information; reference-free carrier detection and record matching are different endpoints.

## Pre-outcome predictions and falsifiers

These directional predictions are registered before the new outputs. They cannot be used to tune the writer, choose sources, thresholds, prompts or cells. Use source-level paired differences and the intervals specified by T6; a direction with an interval crossing zero is inconclusive rather than confirmed. Deterministic controls use per-source outcomes; stochastic cells use the frozen ≥2/3 seed majority.

| ID | Prediction | Operational falsifier / interpretation |
|---|---|---|
| P1 | At strength .2, F5 C source-majority rate is lower in SDXL than SD1.5. This is the specific-gain working hypothesis, not a theorem. | A nonnegative paired SDXL-minus-SD1.5 difference contradicts the point prediction. A convincingly positive difference refutes the proposed directional ranking; neither establishes universal transfer. |
| P2 | F5 SDXL VAE-mode C rate is at least as high as its SDXL .2 full-regeneration C majority rate. | Full regeneration exceeding VAE-only contradicts the direction and suggests reconstruction/denoising can repair a detector input. A VAE-only pass never substitutes for full transfer. |
| P3 | Resize-only C loss is smaller than complete SDXL .2 C loss. | Equal or greater resize loss means resizing is sufficient to explain much of the failure and encoder attribution is unsupported. Resize-only success does not prove resizing has no interaction with SDXL. |
| P4 | F5 raw carrier key-found and C rates are non-increasing from .1 to .2 to .4 within each regenerator, at the group level. | An adjacent reversal contradicts monotonicity for that endpoint. Sampling noise and nonlinear restoration are possible explanations; no cell may be discarded to restore the curve. |
| P5 | If SDXL chiefly destroys encoder-specific carrier gain, its excess C failures versus the SD1.5 anchor will include an increased key-not-found component. | Excess failures entirely concentrated in key-found/content-failed outputs contradict carrier erasure as the main explanation and favor binding/content drift. Mixed outcomes leave both mechanisms plausible. |
| P6 | If the optional .1+.1 SDXL rinse is adopted, C rate is no greater than a single .1 pass. | A higher rinse rate contradicts the accumulation prediction. The rinse is not mathematically equivalent to .2: two encode/decode steps and independent diffusion noise matter. |

Predeclare the hypotheses without inventing numeric success rates. The brief's SDXL .2 thresholds remain the sole decision label: at least .75n plus its negative-control/comparator conditions for TRANSFERS; below .5n for FAILS; the intermediate and comparative cases follow the frozen rule. Do not reinterpret a carrier-only positive as primary C success. SD1.5 anchor weakness does not authorize re-tuning; report it as a reproduction/context limitation. An independent family such as FLUX or Kandinsky tests breadth only if actually authorized and feasible; its absence narrows the result.

## Encoder-aware adaptive proposal A: bounded purification ensemble

Threat: the adversary knows F5's published writer/reader model family and architecture, but has only the suspect image, no clean original, no owner secret, no registry access and no detection queries. The detector remains the pinned honest E_r. Adaptation targets the unusually sensitive encoder, rather than replacing the reader. This is an explicitly designed proposal, not a claimed reproduction of a published robustified model.

For the approved extension, define a deterministic eight-sample antithetic ensemble around the 1024-pixel input u: ν_j are four fixed public Gaussian arrays and their negatives, coordinate standard deviation 2/255. Set

    E_smooth(u) = (1/8) Σ_j E_SDXL(clip(u+ν_j,0,1)).

Then use the ordinary frozen SDXL .2 DDIM20 pipeline with the resulting scaled mode latent, decoder, prompt and seeds 12–14 unchanged. Apply the same channel to every arm and C0; read all outputs with the original detectors. The perturbation arrays are fixed by a pre-outcome seed, independent of source, arm and outcome. Name this **encoder smoothing**, not a certified robust encoder. Nonlinearity and clipping make the average biased; it may erase host details or preserve the very direction it seeks to suppress. The 2/255 input jitter is an attack-composition parameter, not an extra watermark budget. Test final image quality jointly with detection, without retuning this radius.

This is a method-aware T3 composition. The base study still does not explore standalone T1/T2 attacks. The setting is fixed for a costed proposal only; approval must precede outputs, and any later radius/ensemble sweep would be a new preregistered study. Do not select the best attack after looking at the core result and describe it as prespecified.

Workload at n=60, four marked arms plus C0: 60×5×3=900 extra regenerated outputs. Encoder ensembles can be cached once per source/arm before the three diffusion seeds: 300×8=2,400 VAE encodes, rather than 7,200. No new watermark embedding is required. With explicitly assumed planning throughput 4–12 seconds/output plus 0.2–1.0 seconds/extra encoder pass, encoding adds approximately 0.12–0.58 GPU-hours and generation 1–3 GPU-hours. Allow 0.5–1 hour for detection, setup and transfer: **1.6–4.6 extra instance-hours** (round authorization to **5 hours maximum**). At a hypothetical $0.50–$1.00/hour, **$0.80–$4.60**, cap **$5** plus explicitly budgeted storage/network. These are estimates, not measured hardware speeds or a live price quote; multiply by actual quoted hourly rate and include them in the parent budget. n=120 approximately doubles workload. The existing absolute core cap does not automatically expand. Recommendation: optional, useful after independent transfer, but reserve it at stage 1 if a single planned extension is desired.

## Encoder-aware adaptive proposal B: train a robustified attacker encoder

A more direct mechanism test would train E_a^rob to preserve clean SDXL latents/reconstruction while reducing sensitivity to an adversarial neighborhood, then freeze it before attacking evaluation marks. A schematic objective is clean latent matching plus reconstruction fidelity plus max_{||η||≤r}||E_a^rob(u+η)−E_a^rob(u)||². Keep the decoder fixed to maintain coordinate compatibility. Evaluate on independently reserved development sources never used to select r, optimizer, stopping rule or checkpoint; no held-out/test pool may be used.

This may suppress F5 gain, but contraction can destroy useful detail and mismatch denoiser training. Average stability is not a uniform certificate. PRC's discussion of a robust/private **reader** VAE concerns resisting embedding attacks; that is not evidence that a robust **attacker** encoder has been trained or defeats F5. GhostVAE compromises the reader's supply chain, which is a different capability and is excluded from this study.

Provisional feasibility envelope only: 8–24 additional GPU-hours for a bounded training pilot, plus 2–5 for the same 900-output evaluation, totaling **10–29 hours** and **$5–$29 at hypothetical $0.50–$1/hour**. Storage/data licensing and a separate development calibration pool also need to be fixed. These are budget ceilings to discuss, not a credible accuracy/performance forecast. Recommendation: **do not approve into this one-experiment core**; first require an exact training protocol, data split and compatibility plan. No publicly inspected drop-in robustified SDXL attack encoder was found that would remove this work.

## Coverage and remaining uncertainty

Primary Zhao theorem/method/evaluation and PhotoGuard were refreshed from their V2 dossier cards; PRC 2025 method/evaluation and Figure 8 distinguish reader robustness from attack robustness. Recent 2026 GhostVAE and BiSLW were read at method/evaluation depth and cached. BiSLW supplies a close VAE-DCT-carrier precedent but uses learned latent residuals and decoding rather than F5's pixel-gradient writer. SERUM, MarkNull, RAVEN and Watermarks Attack Watermarks remain covered by the dossier/T1/T3; their V2 cards were used as routing evidence, not new performance evidence here. Search-log records recent leads and limits. No exhaustive universal novelty or security claim is made. No source proves F5 survival under an independent encoder, no suitable robustified attack checkpoint was verified, and no stage-1 output fills that empirical gap.

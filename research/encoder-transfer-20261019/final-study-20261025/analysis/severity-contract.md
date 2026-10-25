# Comparing regeneration severity without equating strength

WP4 analytical design note, 2026-10-25. No model or image computation occurred. The equations describe observables for the approved server phase, not measured latent responses.

## Three distinct comparisons

1. **Native operating point:** use the released pipeline and a frozen schedule. Report the actual noising coefficient, number of updates, precision, resolution, posterior convention, prompt and guidance. This measures a concrete attack's external validity.
2. **Source-paired image fidelity:** compare the resulting images to the same declared reference, within source. A comparison against each arm's published image measures incremental attack damage; a comparison against the original unmarked source measures total damage. Keep the two references separate.
3. **Mechanistic latent severity:** measure the attack-encoder displacement and its signed downstream transport. This can explain a result but requires privileged residual and model access. It does not replace the native attack or an observable image-fidelity comparison.

Equal values in one column do not make the other columns equal. In particular, the same number of updates does not imply equal forward-noise energy, and equal nominal forward-noise coefficients do not imply equal signal-to-noise ratios under differently scaled encoders.

## Affine corruption and readable transport

Write a source-conditional initial state as `z_t = a z_0 + b epsilon`. The exact paired marked/unmarked displacement under shared explicit epsilon is `a d`, where d is the scaled encoder displacement (including the paired posterior convention). For DDIM/variance-preserving diffusion, `a=sqrt(alpha_bar)` and `b=sqrt(1-alpha_bar)`. For native flow-matching interpolation, `a=1-sigma`, `b=sigma`.

Report both `a^2 ||d||^2 / b^2` and `a^2 ||d||^2 / (b^2 d_latent)`, with their different meanings and a separate b=0/no-noise case. The second divides by expected total standard-Gaussian noise energy; the first is a directional location-shift quantity. Neither is the reader's operational SNR. A source-image latent RMS diagnostic may also be reported, but it describes the host, not specifically the watermark.

The relevant fixed signed read increment is approximately `a r^T J_decoder J_reverse d`. Under an Euler flow step, `z_next = z + (sigma_next-sigma) v_theta(z,sigma)`, the local Jacobian is `I + (sigma_next-sigma) J_v`; the complete reverse Jacobian is its ordered product. Its rotations and singular gains are not determined by a/b. This is why matching nominal sigma cannot isolate an encoder effect.

An autoencoder affine scaling must be applied before these quantities are compared. A change of latent coordinate scale accompanied by its correctly transformed denoiser can leave the image channel unchanged while changing an unnormalized encoder gain. Report native scaling, shift and latent dimensions explicitly.

## Discrete operating points are the actual grid

The pinned [FluxImg2ImgPipeline v0.35.1](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/flux/pipeline_flux_img2img.py) computes `t_start=int(max(N-N*strength,0))`. Away from floating-point boundary artifacts, effective updates are `ceil(N*strength)`, not `floor(N*strength)`. Thus at N=4, strengths .1 and .2 select the same one-update suffix. They must not be counted as independent severity levels or used as evidence that a strength curve is flat. Strength exactly zero is rejected after producing no effective updates.

The [FlowMatchEulerDiscreteScheduler v0.35.1](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_flow_match_euler_discrete.py) may shift the supplied sigma grid. The released model's configuration decides whether a fixed or resolution-dependent shift is used. The public pipeline's defaults are not evidence of the gated checkpoint's exact configuration. Derive its grid only after that configuration is available; archive it and the actual emitted arrays before outcomes are released. Do not override it to produce a desired severity match.

For this study, a candidate's native grid must be reduced to unique `(actual start coefficient, update sequence)` pairs before development. The deduplication uses schedule metadata only. No new image outcomes, detector outputs or tuned custom sigma schedule may define those pairs.

## Prospective quality selection and confirmation

For a new family's native operating point, use the shared WP3 automated quality region and all four marked arms in development. Freeze one global setting by a quality-only rule before detector outcomes. It remains a family challenge even if its achieved fidelity differs from R0/R1; report that mismatch. A quality-ineligible family may still yield labelled descriptive outputs, but it cannot be advertised as quality-constrained successful removal.

Keep the main H3 comparison fixed to SDXL .1 versus SD1.5 .2, with all three fidelity metrics evaluated against each source's same F5 marked image. A future third-family result does not replace that hypothesis after its outcomes are known. Within-source dominance and predeclared caliper overlap are stronger comparisons than pooled median quality, but still cannot isolate encoder training from all other pipeline differences.

When a model is excluded from law fitting and calibration, its challenge predictions are out of those training families. If its historical aggregate retention is already known (Kandinsky 3), describe it as a held-out model family relative to fitting, not a previously unknown model or a blind discovery.

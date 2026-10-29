# R3 denoiser-aware writer: implementation and primary-source audit

2026-10-29. Pre-output design amendment, not scientific evidence or permission to execute. The implementation is `scripts/tifs_writer.py` plus `scripts/tifs_denoiser.py`. Every model operation is server-only. No model, image, gradient, metric or timing operation was executed locally.

## Operator and scope

`f6-x0` retains the fixed F5 reader, semantic payload, robust update schedule, fragile writes and clean refinement. At each robust update it adds a surrogate chip loss to the clean chip loss. Family/strength cycles R0 .2, R1 .1, R1 .2. The family VAE encodes the posterior mode. For a timestep drawn from that cell's native executed window,

\[
z_t=\sqrt{\bar\alpha_t}z+\sqrt{1-\bar\alpha_t}\epsilon,\qquad
\widehat z_0=\frac{z_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta(z_t,t,c)}{\sqrt{\bar\alpha_t}}.
\]

The family VAE decodes the estimated clean latent, and the same F5 semantic reader supplies the surrogate loss. Both terms differentiate to the image. In particular epsilon is **not detached**. The estimate is a one-evaluation denoiser surrogate; it is not the final latent of the complete native attack. No k-step option is included: it would multiply an unmeasured backward cost and introduce an additional search dimension before the first server rehearsal. K3 is excluded from optimization; a K3-in design requires an additional implementation and new pre-output authorization/configuration, not this helper's fallback.

The baseline `f6-noise` remains the earlier decoded noisy latent at the first native timestep. `f6-codec` and `f6-generic` remain controls. Their old formulas and update schedules are unchanged. The new sampling applies only to `f6-x0`. Consequently x0-versus-noise changes both denoiser inclusion and the timestep distribution; it cannot isolate the denoiser's causal contribution. No extra schedule-matched arm is added to the bounded search. Report that comparison as a comparison of the complete surrogate designs.

## Native schedule and randomness

`native_window` initializes the pinned local DDIM scheduler with the retained overrides and 20 steps, then invokes the actual pipeline class's `get_timesteps`. It requires order one, epsilon prediction, no clipping and no thresholding. Thus the implementation never approximates a strength by a continuous noise level or assumes a timestep table from another family. The expected retained windows are [151,101,51,1] at strength .2 and [51,1] at .1; actual values and their alpha-bars come from the loaded scheduler and are recorded.

`sample_window` hashes the canonical tuple `(f6-x0-timestep-v1, stream, source, family, strength, update)` and selects a window index by modulus. This is an effectively uniform discrete draw (the negligible 64-bit modulo imbalance is below one part in 2^62 for these window sizes; all current lengths divide 2^64 exactly). Its stream is separate from the epsilon generator and diagnostics are separate from optimization. Epsilon retains `tifs_writer.draw_seed` with the `f6-x0` variant domain. Every full x0 embedding reports all 150 selected timesteps, coefficients, indices and both seeds. There is no global reseeding or outcome-dependent draw.

## Native conditioning, attention and precision

The retained R0 and R1 configurations have `prompt=""`, `negative_prompt=""`, `guidance_scale=1.0`, 20 DDIM steps and eta zero. Therefore the **exact native computation is one branch**, not an approximation to classifier-free guidance. `assemble_conditioning` also implements the exact negative-first two-branch CFG ordering for a future scale greater than one, and mocks verify it; current writer validation rejects changing the frozen native prompt/guidance. Distilled timestep-conditioned UNets and nonzero guidance-rescale variants are outside this contract.

R1 passes `prompt_2=""`, `negative_prompt_2=None`, `clip_skip=None`, original and target size (1024,1024), crop origin (0,0). The native `encode_prompt` supplies both concatenated token embeddings and the second encoder's pooled embeddings. The native `_get_add_time_ids` supplies the time ids using projection dimension from text_encoder_2 (or its native pooled fallback). Positive and negative time/pooled tensors are concatenated only if CFG is actually enabled. No zero-vector shortcut replaces the empty prompt. The pinned SDXL base does not use aesthetics conditioning; native 6.0/2.5 defaults are nevertheless supplied to its native helper.

The writer loads the same local fp16 UNet weights and text encoders. Text encoders are frozen/eval, moved to CUDA just long enough to compute cached conditioning under no-grad, then released; the pipeline forward is never called by this loader. The writer uses the same retained `ClassicAttention` and explicit LayerNorm implementation as Stage S native evaluation. This is relevant because the stage's native wrapper, unlike the upstream default, deliberately installs that scope. Each writer UNet is moved to CPU after its differentiated graph has been freed. Cached CPU weights avoid repeated disk loads; only one active writer UNet is on CUDA. The shared reader and active codec retain fp32 VAEs.

Autocast is explicitly disabled. The UNet input is explicitly cast to its fp16 weight dtype, and epsilon is promoted to fp32 for the x0 subtraction/division and fp32 VAE decode. The cast participates in autograd; fp16 arithmetic can still overflow, underflow or lose gradient accuracy, so finite/nonzero checks are mandatory and no precision fallback is automatic. Posterior mode, fp32 noise arithmetic and differentiable float Lanczos remain deliberate approximations to sampled native RGB8 regeneration. R1 still normalizes, casts through fp16 and returns to fp32 before encoding. These statements do not claim whole-pipeline primal equality.

## Checkpointing source audit (diffusers 0.35.1, read online)

The pinned [UNet blocks](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/unets/unet_2d_blocks.py) test gradient-enabled mode plus their checkpoint flag, including cross-attention down/up and mid blocks. They do not require training mode. The pinned [Transformer2DModel](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/transformers/transformer_2d.py) uses the same condition around transformer blocks. Thus frozen eval UNets can checkpoint activations while retaining input gradients.

The pinned [ModelMixin](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/modeling_utils.py) enables the model's checkpointable modules and supplies PyTorch `use_reentrant=False` on the supported PyTorch runtime. This is compatible with `autograd.grad`; the implementation calls the native enabling method and checks every advertised checkpoint flag. It never enables train mode or parameter gradients.

UNets are registered in the same writer-gradient lifetime as VAEs. Flags remain active through backward and recomputation, and are disabled on success and exceptions using local references even if writer closure clears model fields. Native inference and clean verification run after scope exit. The attention override is private to the writer's separately loaded UNets and is restored when they close.

The pinned [SDXL img2img pipeline](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py) supplies the conditioning contract above: native prompt encoding, `_get_add_time_ids`, negative-first CFG ordering, and `guidance_scale > 1` with no time-conditioning projection as the CFG condition. The [SD1.5 img2img pipeline](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py) supplies the equivalent single/text branch and scheduler-scaled UNet call. The pinned [DDIM scheduler](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py) computes `pred_original_sample` from epsilon using the formula above. The source audit establishes the intended API behavior, not successful execution of our adapter.

## Server rehearsal contract

1. On both prespecified rehearsal sources, the writer checks finite nonzero input gradients for clean loss and every surrogate/cell. For x0 it additionally differentiates the epsilon prediction's squared mean with respect to its noisy input. This additional check catches a detached denoiser even if the direct x0 identity term still yields an image gradient. All model parameters must remain frozen with no accumulated parameter gradients. Existing reader-projection parity remains mandatory.
2. In the existing native C0 generation on each R0/R1 cell and source (first rehearsal seed), invoke `native_first_step_parity(pipe, family, spec, run_native)` inside Stage S's existing `ClassicAttention` scope. It returns the original native output plus a receipt and consumes no additional native trajectory. Its temporary hooks capture the actual first UNet call and the scheduler's sample, guided epsilon and predicted original sample, then always restore.
3. The helper independently reassembles conditioning and demands exact token, pooled and time-id equality. It repeats the same native epsilon operator on the captured noisy latent, with atol/rtol 1e-3. It compares fp32 x0 arithmetic with native fp16 DDIM x0 using an operand-based rounding envelope: `16 * 2^-11 * (abs(z_t)+sqrt(1-alpha)*abs(epsilon))/sqrt(alpha) + 1e-5`. This conservatively covers arithmetic/casting error without dividing by a nearly cancelled x0. The receipt records observed errors and the bound. This is first-step operator parity conditional on the actual native input; it does not validate posterior-mode or float-resize equivalence.
4. Native C0 capture/replay, final saved-PNG reads, strict quality, all source counts and every existing integrity gate remain required. No tolerance failure authorizes changing a model, precision, strength or gate. Failure is an implementation stop. The native epsilon rerun and the extra diagnostic backward probes must enter rehearsal timing/cost accounting.

## Budget control and capacity

The registered robust PSNR choices are 52, 46, 42 and 38 dB. Refinement stays fixed at 58 dB and 50 updates in every new arm; the robust stage stays at 150 updates. These are per-stage L2 budgets and do not imply final strict quality. `f5-budget` disables every surrogate and delegates each optimization stage to the unchanged F5 `robust_pgd` callable. At 52 dB, its calls are exactly (52 dB,150 updates,margin4,mask0) and (58 dB,50 updates,margin4,mask0), with the inherited fragile body unchanged. Pure mocks verify callable, arguments and returned-object identity. No numerical F5 output equality is claimed to have been measured locally. At lower budgets fixed refinement58 deliberately keeps the F6 refinement budget, rather than adopting F5's usual `max(psnr+6,50)` policy.

This is a **matched declared budget** control. Final achieved PSNR/LPIPS must be reported; matching the input radius alone does not establish equal achieved perceptual quality. Each F6 writer uses 350 reader-gradient evaluations and 150 surrogate evaluations; x0 adds 150 native UNet forward/backward graphs. `f5-budget` uses 200 reader gradients and no surrogate. Rehearsal x0 adds three epsilon-gradient probes per source, plus native first-step epsilon replays.

The [scalar budget derivation](r3-distortion-budget-bounds.md) follows both
fragile writes, all four RGB8 roundings and the refinement's intermediate
center. Even ideal-arithmetic worst-case bounds do not certify final PSNR35;
this is a limitation of what nominal budgets prove, not a prediction of poor
quality. SSIM/LPIPS and final strict quality remain measured server outcomes.

Checkpointing recomputes activations and cannot establish fit. The existing measured-total-minus-1.5-GiB capacity rule applies to **the new x0 rehearsal peaks**, not a previous codec-only peak. No 24-GB fit guarantee is made. Native classic attention, saved UNet checkpoint inputs, the active fp32 VAE and the reader all contribute to peak memory. The server forecast must include model/CPU-to-GPU transfer time; moving fp16 UNets each update can materially increase wall time. Do not start Stage P/S if x0 rehearsal lacks positive capacity, complete receipts, finite gradients or enough budget.

## Local validation and limits

The stdlib-only test suites cover native-window delegation, seeded draws, epsilon/x0 algebra, native prompt arguments, SDXL added conditioning, exact CFG arithmetic/order, eval/frozen checkpoint preconditions, scope and hook cleanup, variant dispatch, registered budgets and unchanged F5 callable delegation. They are not tensor simulations or scientific outputs. Only the permitted MAIN stdlib interpreter with `-I` was used. Server-only code was syntax-compiled. GPU backward feasibility, numeric gradient accuracy, practical transfer cost, retention gain, visual acceptability and TIFS contribution remain unmeasured.

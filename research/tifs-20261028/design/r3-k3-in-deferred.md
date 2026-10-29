# Prospective K3-in branch: precise design, deferred implementation

2026-10-29. **NOT IMPLEMENTED. NOT EXECUTABLE. NOT PART OF THE CURRENT EIGHT-CONFIGURATION SEARCH.** This document supplies the K3-in alternative requested in the round-3 brief. It neither changes an effective configuration nor authorizes execution. Choosing it requires a new pre-output amendment, implementation, validation and measured resource forecast. K3-out remains the recommendation and the current executable design. No model operation, timing experiment or scientific simulation was performed for this document.

## Decision and scientific purpose

**K3-out:** optimize against R0 .2 and R1 .1/.2, then evaluate native K3 .2. K3 is excluded from writer gradients but is selection-seen because its Stage P counts rank candidates. This supports a claim about transfer beyond the optimized regenerator families after development selection, not a claim about a prospectively unseen family.

**K3-in:** replace the writer's three-cell optimization cycle with the four-cell cycle below, using K3's own MoVQ and denoiser. This asks whether direct exposure to the third family improves robustness under the same total number of updates. K3 becomes gradient-seen as well as selection-seen. A positive K3 result would demonstrate robustness to an optimized family; it would not establish transfer to an unseen family. Native evaluation remains the full K3 attack in either branch.

The prospective SD3.5 Stage C family remains gradient-unseen and selection-unseen only while its outputs, diagnostics and performance are withheld from all writer/configuration selection. Model availability knowledge is distinct from performance exposure. Neither branch may use SD3.5 to choose this amendment. Development source separation alone does not make a family unseen.

User choices, to record before any Stage P scientific output:

- **Recommended: K3-out.** Keep the current eight configurations and disclose K3 as selection-seen, gradient-excluded.
- **Deferred: K3-in.** Commission and freeze this replacement branch before execution; accept direct K3 exposure, redistributed updates and an unknown additional resource requirement.

This is a choice of one search design. It does not silently add a ninth candidate, a second eight-candidate search or post-outcome switching. Running both branches would create a sixteen-configuration search and require its own allocation, selection rule and cost amendment.

## Inspected native contract

The retained [stage-2b configuration](../../encoder-transfer-20261019/stage2b-config.json), [runtime](../../../scripts/encoder_transfer_runtime.py), [pilot](../../../scripts/et_final_pilot.py) and [phase-A native wrapper](../../../scripts/et_final_phase_a.py) establish the reference: Kandinsky revision `bf79e6c219da8a94abb50235fdc4567eb8fb4632`, diffusers 0.35.1, `Kandinsky3Img2ImgPipeline`, fp16 weights, native `DDPMScheduler`, 20 scheduled steps, strength .2, empty prompt and guidance 1. The scheduler is recorded as squared-cosine, epsilon prediction, clipping enabled, leading spacing and offset 1. Native input is saved RGB8 resized by Lanczos from 512 to 1024; output is quantized to RGB8 then resized to 512. Future Stage P/S uses its frozen seeds 0, 1, 2; the historical 12, 13, 14 are not inherited.

The inspected [0.35.1 K3 img2img pipeline](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/pipelines/kandinsky3/pipeline_kandinsky3_img2img.py) directly encodes the preprocessed image into MoVQ latents before `prepare_latents`; its four-channel path adds noise without posterior sampling or scaling. `get_timesteps` takes the final four entries at 20 steps and strength .2. Guidance 1 disables classifier-free guidance. The UNet receives `encoder_hidden_states` and `encoder_attention_mask`; native decoding uses `force_not_quantize=True`. Its public pipeline call is decorated with no-grad, so a differentiable writer must call constituent modules instead.

The retained runtime computes the actual empty-prompt embeddings and mask once with `encode_prompt(..., do_classifier_free_guidance=False, _cut_context=True)`, then releases the text encoder before loading the denoiser and MoVQ onto GPU. An all-zero embedding is not equivalent. K3 has neither SDXL pooled/time-ID conditioning nor an SD posterior-mode substitution.

The inspected [DDPM implementation](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/schedulers/scheduling_ddpm.py) uses epsilon prediction to estimate the clean sample, applies configured thresholding or clipping, then forms a posterior mean and adds stochastic variance noise in the native step. Model-input scaling is the identity. Leading spacing with 1,000 training steps and offset 1 implies the window `[151,101,51,1]`; obtain and record the actual window and alpha-bars from the loaded native scheduler. The direct pinned model scheduler JSON was inaccessible through the web tool, so this design does not claim independently verified values for every serialized field. Read the exact local pinned JSON before implementation freeze; reject disagreement instead of imposing SD scheduler overrides. In particular verify `num_train_timesteps`, `prediction_type`, `thresholding`, `clip_sample`, `clip_sample_range`, spacing and offset. The library default clip range is 1, but the loaded value is authoritative.

## Proposed differentiated operator

Let `x` be the candidate float image, `U` and `V` the declared differentiable float Lanczos resize operators to 1024 and back to 512, `E_K`/`D_K` the native MoVQ encoder/decoder, and `R` the unchanged F5 semantic reader. Use the same normalization as native image preprocessing. Define

\[
z=E_K(2U(x)-1).\mathrm{latents},\qquad
z_t=a_tz+b_t\epsilon,\quad
a_t=\sqrt{\bar\alpha_t},\quad b_t=\sqrt{1-\bar\alpha_t},
\]
\[
e_t=\epsilon_{\theta,K}(z_t,t,c_K,m_K),\qquad
u_t=(z_t-b_te_t)/a_t,\qquad
\widehat z_0=\operatorname{clip}(u_t,-c,c),
\]
\[
S_K(x;t,\epsilon)=V\!\left(\operatorname{clip}_{[0,1]}
\left[\tfrac12D_K(\widehat z_0,\mathrm{force\_not\_quantize=True}).\mathrm{sample}+\tfrac12\right]\right).
\]

Here `c` is the native scheduler's loaded clip range; this proposed branch requires epsilon prediction, clipping enabled and thresholding disabled. An incompatible scheduler fails configuration validation. Use the inherited clean chip loss plus the inherited weighted semantic chip loss on `R(S_K(x))`, with identical payload, target margin, views, projection and reader parameters. This is a complete proposed operator, not an instruction to call the current SD-only helper with a different family name.

Differentiate through both the direct `z_t` path and the denoiser. In the unsaturated region the latent derivative is

\[
\frac{\partial\widehat z_0}{\partial z}
=I-b_tJ_{\epsilon_{\theta,K}}(z_t),
\]

and clipping left-multiplies this by its coordinatewise derivative. Thus detaching the denoiser removes the very term the design intends to optimize. Do not use a straight-through derivative for x0 clipping or RGB8 rounding. Saturation can suppress the useful gradient and must be reported, not repaired by silently disabling clipping. The unchanged reader adds its own encoder/Jacobian after the MoVQ decode.

The [0.35.1 VQModel implementation](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/autoencoders/vq_model.py) returns continuous encoder latents. Its decode bypasses vector quantization when `force_not_quantize=True` and codebook lookup is disabled, then applies the post-quant convolution and decoder; spatial normalization can additionally condition on the latent. Require `lookup_from_codebook=False` in the frozen adapter. Preserve this decoder behavior and do not replace it with a nearest-codebook approximation or multiply by SD's latent scaling constant.

This is a **single-denoiser clean-latent surrogate**, not a four-step differentiable native attack. It omits the DDPM posterior transition and subsequent random draws. At a sampled later timestep, the noised encoded image is not the actual state of a preceding native DDPM trajectory. Its fidelity is therefore to native components, conditioning and timestep support; it is not equality to the complete attack distribution. Native evaluation still uses the full stochastic chain and paired C0 tape replay.

## Frozen hypothetical allocation and random streams

Use exactly 150 robust updates and 50 unchanged clean refinements, refinement PSNR 58 dB, one EOT realization per robust update and the existing two fragile writes. Repeat the ordered cycle

`[R1 .2, K3 .2, R0 .2, R1 .1]`

37 times and append `[R1 .2, K3 .2]`. This fixes the allocation before outcomes:

| Cell | Robust surrogate updates | Change from current three-cell allocation |
|---|---:|---:|
| R0 .2 | 37 | -13 |
| R1 .1 | 37 | -13 |
| R1 .2 | 38 | -12 |
| K3 .2 | 38 | +38 |
| Total | 150 | 0 |

This assigns the two unavoidable extra updates to the harder-strength foreign cells by design choice, not measured superiority. It is not 150 updates per family, and K3 inclusion does not increase the robust update count to 200. For the x0 branch, each cell samples uniformly from its loaded executed timestep window, with a fixed source/cell/update-derived hash stream and a separate epsilon stream. Use new versioned K3-in domains, shared across the four PSNR-budget configurations; configuration IDs must not introduce a new random-seed search axis. Record all draws and actual coefficients. Diagnostic streams remain separate.

At the logical operation level this retains 350 reader-gradient evaluations (150 clean +150 surrogate +50 refinement), 150 family-codec paths and 150 denoiser graphs, now distributed 37/75/38 over R0/R1/K3. Checkpoint recomputation, parity/gradient diagnostics, model transfers and setup are additional physical work. Equal operation counts do not imply equal wall time or memory.

## Precision, memory and validation contract to implement

The prospective writer should retain the current SD branches and use a dedicated K3 adapter: frozen eval fp16 K3 UNet weights; MoVQ in fp32 compute from the retained fp16 weights; explicit autocast-disabled regions; native-normalized encoder input cast through fp16 then promoted to fp32; fp32 noising and x0 arithmetic; explicit differentiable cast to fp16 for the UNet and promotion back to fp32 before clipping/decode. This is a declared precision approximation to native fp16 K3. It matches the existing writer's preference for fp32 codec differentiation, not bit-exact native primal arithmetic. No automatic precision, resolution, attention or clipping fallback is permitted.

The inspected [Kandinsky3 UNet source](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/unets/unet_kandinsky3.py) has no gradient-checkpointing flag or execution branch. [ModelMixin](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/modeling_utils.py) defaults support to false and rejects its generic enabling call for unsupported models. Therefore reusing the SD helper's `enable_gradient_checkpointing()` is not a valid implementation. Importing the checkpoint module in the K3 file does not prove checkpointing occurs.

Proposed adapter policy: explicit non-reentrant checkpoint closures around the K3 UNet call and MoVQ encode/decode, returning tensors and preserving input gradients. Hold model placement, dtype, conditioning and the retained attention context fixed until backward/recomputation finishes. Only then release the graph and offload the active denoiser. Do not move a module inside a checkpointed closure or enable inference-mode offload hooks as an unvalidated substitute. The pinned [PyTorch 2.7.1 checkpoint implementation](https://github.com/pytorch/pytorch/blob/v2.7.1/torch/utils/checkpoint.py) supports the non-reentrant route needed for `autograd.grad`; recomputation must agree with forward execution. Whole-call checkpointing may still exceed memory. Finer checkpoint segmentation would require an explicit adapter revision and renewed validation, not an outcome-dependent runtime fallback.

Cache native prompt conditioning once and remove the text encoder from GPU before derivative work. Keep only the active writer denoiser on GPU; account for the F5 reader, active codec, retained activations, checkpoint recomputation, attention workspace, allocator reserve, CPU copies and transfer time. Previously successful native inference or JVP diagnostics do not establish that this full reverse-mode graph fits. No minimum GPU size or runtime is asserted here.

Before this branch can enter Stage P, its new pre-output contract must specify and pass server-only checks on the first two authorized Stage P tuning sources: loaded scheduler/window/conditioning parity; native-precision component forward parity; separately reported mixed-precision surrogate discrepancy; checkpointed versus uncheckpointed gradient agreement where feasible; finite nonzero image gradients in three fixed directions; explicit dependence on denoiser gradients; x0-clipping saturation; and actual peak memory/complete per-update time including transfers. Numeric tolerances must be frozen with the implementation before these diagnostics, using the existing R3 validation discipline. This document supplies no passing verdict. A nonfinite derivative, missing comparison or resource failure blocks K3-in; it never permits a silent return to K3-out after observing outcomes.

## Controls, selection and claims

For a replacement eight-configuration search, retain the two surrogate types times four robust PSNR targets, with the current fixed refinement budget. Both types use the four-cell allocation. On K3 updates, the noise branch uses the same MoVQ encode/decode but decodes the noisy latent at the first native timestep, without a denoiser; the x0 branch uses the clipped estimate above with window sampling. This comparison changes both denoiser inclusion and timestep distribution, just as in the present SD design. It compares complete surrogate designs and cannot isolate the causal effect of a denoiser.

The Stage S codec control must use the same four-cell allocation, including the K3 continuous MoVQ round trip without diffusion/noising. The generic control remains the declared generic perturbation at the same update count; a K3 label must not falsely imply it uses K3 components. Retained F5 is unchanged. `f5-budget` remains the separately labelled no-surrogate comparator with matched optimization budget/refinement and its measured-quality comparison; it receives no K3 gradients. Matching a PSNR target still does not establish matching achieved quality. Freeze all changed arm identities and disclose training exposure for each arm.

Comparing a K3-in result with K3-out at fixed 150 updates changes exposure **and** reallocates 38 updates away from SD. It cannot isolate the benefit of adding K3 while holding SD training constant. The current plan does not contain a randomized comparison of these branches; cross-run differences would be exploratory and potentially confounded by selection. Do not manufacture an ablation claim from the user choosing one branch.

Preserve the chosen profile's strict clean quality/F, native C/J thresholds, paired gains, negatives, T4/T5, inventory and article requirements. K3-in is not a reason to lower 12/16, drop K3 evaluation or alter the VINE-B article ceiling. Its direct K3 exposure also does not certify success on SD3.5. A new implementation and amendment must update the cost inventory, calibration and two-stage resource decision: Stage P measurements qualify Stage P only; Stage S's all-arm rehearsal still qualifies Stage S on the same paid clock. The existing 126-hour planning scenario does not price K3-in gradients and must not be reused as its forecast.

## Judgment

K3-in is scientifically coherent if the intended claim is robustness across three explicitly optimized families. It might repair a K3 weakness, but no evidence here estimates that benefit or its runtime. K3-out is the better present recommendation because it preserves an interpretable gradient-excluded family, avoids diluting each existing cell's 50 updates, and has a more mature implementation within an already uncertain resource budget. These are design and feasibility judgments, not measured advantages. The user can select K3-in prospectively; the honest consequence is additional work and a new frozen design before any output, not an immediately executable toggle.

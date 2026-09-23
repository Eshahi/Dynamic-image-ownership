# A5 candidate: explicit existing-image initial-noise path

2026-09-23, author `/root`, issue #6. **PARTIAL CANDIDATE SPECIFICATION; not A5 completion, model selection, empirical feasibility or compute approval.** Applies [scope-guard.md](scope-guard.md), [research-contract.md](research-contract.md), [io-spec.md](io-spec.md) and [bridge-design-options.md](bridge-design-options.md). Does not change the proposal, four RQs, final dataset commitments or detector knowledge.

## 1. Inspected identities, not acquired weights

Code candidate: Diffusers `v0.35.1`, commit `0f252be0ed42006c125ef4429156cb13ae6c1d60`. [DDIM scheduler](https://github.com/huggingface/diffusers/blob/0f252be0ed42006c125ef4429156cb13ae6c1d60/src/diffusers/schedulers/scheduling_ddim.py), inspected lines 180-270 and 290-521. SHA-256 `6bb3c830a7937a96acd9bfc3bbab6d75404ceda0189c423899d03c9d34da8599`, 24,919 bytes.

Configuration candidate: `stable-diffusion-v1-5/stable-diffusion-v1-5`, revision `451f4fe16113bff5a5d2269ed5ad43b0592e9a14`, obtained from its public model API. **This repository describes itself as an unaffiliated mirror**, not the original publisher. Inspection authenticates these repository contents, not equality of its weights to an original release. No weight bytes/hash were obtained. Acquisition requires provenance and license review of the exact selected components first.

| Inspected file at that revision | SHA-256 | Relevant observation |
| --- | --- | --- |
| `vae/config.json` | `786a7d21647ddea6a04b9675c03d3cb45e90a2f3c6da5fbda2c54ade040036de` | 3 image channels, 4 latent channels; scaling factor absent. |
| `unet/config.json` | `78f474de6bab3d893868f37be97b636ae65c0df3073ed3256ca458ff599b5f96` | 4 input/output channels, sample_size 64, cross-attention dimension 768. |
| `scheduler/scheduler_config.json` | `699cce92eb7c122e2eb7dfdea78e6187fda76a5ed4a8e42319b85610e620e091` | PNDM, not DDIM; 1,000 training steps, scaled-linear beta endpoints 0.00085/0.012, offset 1, final-alpha flag false, clipping false. |
| `README.md` | `2079161f9df7524bd9eca5e53ff5911271b8551e0f868b7b5a92b84776df28a3` | Mirror warning, lossy VAE, 8x spatial downsampling, model-license reference and safety-module expectation. |

File links share this [pinned repository root](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/tree/451f4fe16113bff5a5d2269ed5ad43b0592e9a14). Read-only reproduction: `scripts/inspect_noise_sources.py`; it fetches only five fixed text URLs, prints hashes/excerpts, writes no files, and executes no upstream code. First attempt hit sandbox socket denial; explicit network approval allowed the successful retry. Web retrieval of several raw URLs also failed; those failures were not treated as missing source evidence after successful direct inspection.

The card names CreativeML OpenRAIL-M, distinct from Diffusers' Apache-2.0 code license. The [linked license text](https://huggingface.co/spaces/CompVis/stable-diffusion-license/raw/main/license.txt) was inspected: use restrictions and redistribution obligations apply; training data is not licensed by that text. No license acceptance, redistribution or legal clearance is inferred. Preserve safety handling; a component-level implementation must not silently drop it. A flagged output must be logged as such, not counted as successful preservation. This license page is an inspected mutable reference, not yet a frozen model-acquisition license artifact.

## 2. Declare the optimized variable precisely

For an eventual existing-image candidate, define `Iwork` as the explicitly preprocessed input and `v = s_vae * E_vae(Iwork)`, shape `[1,4,H/8,W/8]`. A 512x512 working image therefore has `[1,4,64,64]` latents. This is a development working-resolution example, not a decision to resize every final dataset or a native-2K claim. Final preprocessing/alignment remains unresolved.

Select the VAE posterior mode for this candidate to avoid an extra posterior draw; this is an author design choice, not the inspected pipeline's default sampling behavior. The scale `s_vae` must be materialized and checked from the selected class/configuration before execution: the mirror config does not itself specify it. The inspected [AutoencoderKL v0.35.1 source](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/autoencoders/autoencoder_kl.py) documents a default of 0.18215, but a production loader must verify its resolved value instead of silently relying on an omitted config field.

Let epsilon0 be one recorded Gaussian-noise tensor, and delta the **only** variable optimized by L1. With cumulative alpha `a_t` at the initial reverse-process time `t_star`:

```text
epsilon_w = epsilon0 + delta
z_start(delta) = sqrt(a_t_star)*v + sqrt(1-a_t_star)*epsilon_w
I_float(delta) = VAEdecode(DDIM_suffix(z_start(delta), fixed_condition)/s_vae)
```

Hold v, epsilon0, source signatures/templates, model weights, conditioning and time schedule fixed for every optimization step. The perturbation is in the additive noise used **before the first reverse step**, not a post-decoding image residual, a replacement final latent, or new noise injected at every step. Bound delta in noise units; a bound in noisy-latent units differs by `sqrt(1-a_t_star)`. Record both norms. After optimization, perturbed noise need not retain an exact standard Gaussian distribution; do not claim it does.

This is initial noise **for an image-conditioned reverse suffix**, not unconditional pure-Gaussian generation from the terminal training time. It is an explicit interpretation of A3's unresolved existing-image route, permitted for candidate investigation only. If the source requirement is interpreted to mandate terminal pure-noise generation, this route would need a material amendment; do not claim equivalence. Native prompt-only signing remains unsupported.

## 3. Deterministic DDIM candidate and parameter ownership

The following is an explicit proposed scheduler adaptation, **not the checkpoint's native PNDM configuration**. Rationale: an eta-zero, first-order update makes the perturbation path and matched-noise comparison explicit. It is not selected for demonstrated speed, quality or watermark robustness.

Set the candidate to DDIM with 1,000 training steps, scaled-linear betas spanning 0.00085 to 0.012, epsilon prediction, leading spacing, offset 1, `set_alpha_to_one=false`, no zero-SNR rescaling, no clipping/dynamic thresholding, and `eta=0`. Materialize all these values rather than inheriting unrelated defaults. The candidate beta schedule uses linearly spaced square roots squared; `a_t = product_{k=0}^t (1-beta_k)`.

Keep N (inference steps) and strength u as mandatory unresolved design inputs, not fabricated defaults. Require integer `1<=N<=1000`, finite `0<u<=1`, and at least one retained step. Leading times are reversed `j*floor(1000/N)+1`, j=0..N-1. Retain the suffix after `N-floor(N*u)` entries. Reject any selected index outside 0..999; the offset makes N=1000 invalid in this particular candidate. Record the exact time list, not merely N and u. This is also why u cannot be called a continuous noise level independent of N.

For each retained t, define `t_prev=t-floor(1000/N)` and `a_prev=a[t_prev]` if nonnegative, otherwise `a[0]`. For fixed-condition UNet epsilon prediction e:

```text
z0_hat = (z_t - sqrt(1-a_t)*e) / sqrt(a_t)
z_prev = sqrt(a_prev)*z0_hat + sqrt(1-a_prev)*e
```

No fresh variance noise is added with eta zero. The final-alpha convention is not silently replaced with 1; this matters at the final step. Changing the scheduler, prediction type, clipping, conditioning or time list changes the candidate and must change its configuration identity. Exact numerical equivalence to installed Diffusers remains a future component test; the current standard-library tests check the equations and index guards only.

## 4. Gradient and control contract

The public img2img pipeline's no-grad entry point is not the proposed optimizer. Use an explicit component path only after implementation review: fixed VAE encoding and fixed text conditioning may be cached without gradients; UNet, DDIM updates and VAE decoding must retain derivatives to delta while model weights remain frozen. Evaluation mode and frozen parameters do not themselves prove the input graph is retained. Do not detach intermediate states or substitute PIL/NumPy inside that graph. Memory-efficient attention, offload, mixed precision and checkpointing each require tested gradient compatibility; ordinary inference VRAM fit is insufficient evidence.

Do not select a captioner here. A fixed empty text-conditioning candidate would avoid source-caption leakage but can affect reconstruction quality; conditioning policy remains an explicit final-design choice. No prompt, seed, diffusion state or decoder is introduced into the core verification API.

Matched unmarked reference uses identical v, epsilon0, conditioning, time list, encoding and safety policy with delta zero. Report quality against original I **and** the matched reconstruction separately. Include VAE reconstruction distortion; never report only watermark-incremental quality. Final range conversion and encoded image must be rechecked with the true discrete signature computation. An invalid/unstable key, nonfinite gradient, resource failure or safety flag remains a recorded failure, not an omitted image or unlimited retry.

No optimization rate/iterations, noise radius, quality weight, mark-loss target, score threshold or stability margin is frozen here. These remain required for the full method/design package; the document must not be loaded as an executable configuration. Core detection is still CLIP/pHash recomputation plus DCT, never the differentiable embedding model. No benefit under regeneration is inferred from this path.

## 5. Verification and handoff

`scripts/noise_path_reference.py` is a standard-library scalar/index reference, not an image generator, model adapter or scientific runner. `scripts/test_noise_path_reference.py` checks valid/invalid schedules, noise-domain scaling, eta-zero algebra and final-alpha semantics using hand-specified numbers. It loads no dataset, model or external package. Passing it does not demonstrate differentiability of a real pipeline or compatibility/fit on the RTX 5070 Ti.

Next: resolve exact feature/key/template/DCT construction and parameter rationale alongside model-component provenance; then assemble the two A5 outputs and review the whole method. A4 must freeze calibration/power/stopping; A6 must lock and measure the real environment. Scientific model trials require manifest-specific user approval. Issue #6 and plan-acceptance remain open. No change to scope, data, paid budget or publication authority has been made.

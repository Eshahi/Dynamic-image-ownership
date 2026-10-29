# Round 3 pre-output amendment

Date: 2026-10-29. Base: `01bf24f` (Claude's Round 3 brief), following reviewed Round 2 `2c41d5f`. No Stage P or Stage S scientific outputs exist. This amendment changes preparation only. No user approval, experiment result, human judgment or publication readiness is created here. The retained F5 r2, v5 r3, profiles, thresholds, artifacts and held-out sources remain unchanged.

## R3-1: native denoiser-aware alternative

Add `f6-x0`: posterior-mode encoding, a deterministic timestep draw within each native 20-step img2img window, native epsilon prediction, float32 x0 reconstruction and decoding into the unchanged F5 reader. It optimizes R0 .2, R1 .1 and R1 .2; K3 remains optimization-excluded. Keep `f6-noise`, `f6-codec` and `f6-generic`. Default candidate and effective numerical gates remain the Round 1 F6-noise design until the pre-output user choice and, if selected, Stage P freeze. An additional arm cannot silently rewrite the original ablation thresholds.

The pinned native R0/R1 settings use empty prompts and guidance 1, so their exact native denoiser has one branch. SDXL pooled embeddings and time IDs are assembled by the native pipeline helpers. UNet weights/input are fp16 with autocast disabled; x0 arithmetic and VAE paths remain fp32. Frozen eval UNet/VAE checkpoint flags are enabled only during writer gradients and restored before native operations. The one-step estimate is a surrogate, not full denoising; posterior-mode and differentiable resizing remain explicit approximations. Optional k-step is omitted to keep the search and memory cost bounded.

Require finite nonzero clean, surrogate and epsilon-input gradients during server rehearsal. Wrap the native first step on both rehearsal donors in all three optimized cells; independently rebuild conditioning, compare epsilon, and bound x0 differences caused by native fp16 arithmetic. The existing exact C0 capture/replay check remains. Measured peak memory must stay below device total minus 1.5 GiB; no numerical/GPU fit claim follows from local mocks. See `design/r3-denoiser.md` and `stage-s/writer-implementation.md` for inspected diffusers 0.35.1 sources, precision and parity scope.

The original Stage S protocol and Round 2 amendment remain historical freezes; the cumulative Round 3 config/inventory and sections below specify prospective additions. Intermediate commits remain preparation-INCOMPLETE pending integration and the fresh independent review.

## Decisions for the user

Decisions and the recommended package will be finalized after R3-2 through R3-5. All alternatives remain proposals. Claude must record the actual gate/profile and compute choice in a commit **before any server scientific output**, including Stage P; the later post-P freeze records the selected configuration under that already chosen profile. No outcome-dependent profile choice is permitted.

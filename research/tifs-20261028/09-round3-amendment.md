# Round 3 pre-output amendment

Date: 2026-10-29. Base: `01bf24f` (Claude's Round 3 brief), following reviewed Round 2 `2c41d5f`. No Stage P or Stage S scientific outputs exist. This amendment changes preparation only. No user approval, experiment result, human judgment or publication readiness is created here. The retained F5 r2, v5 r3, profiles, thresholds, artifacts and held-out sources remain unchanged.

## R3-1: native denoiser-aware alternative

Add `f6-x0`: posterior-mode encoding, a deterministic timestep draw within each native 20-step img2img window, native epsilon prediction, float32 x0 reconstruction and decoding into the unchanged F5 reader. It optimizes R0 .2, R1 .1 and R1 .2; K3 remains optimization-excluded. Keep `f6-noise`, `f6-codec` and `f6-generic`. Default candidate and effective numerical gates remain the Round 1 F6-noise design until the pre-output user choice and, if selected, Stage P freeze. An additional arm cannot silently rewrite the original ablation thresholds.

The pinned native R0/R1 settings use empty prompts and guidance 1, so their exact native denoiser has one branch. SDXL pooled embeddings and time IDs are assembled by the native pipeline helpers. UNet weights/input are fp16 with autocast disabled; x0 arithmetic and VAE paths remain fp32. Frozen eval UNet/VAE checkpoint flags are enabled only during writer gradients and restored before native operations. The one-step estimate is a surrogate, not full denoising; posterior-mode and differentiable resizing remain explicit approximations. Optional k-step is omitted to keep the search and memory cost bounded.

Require finite nonzero clean, surrogate and epsilon-input gradients during server rehearsal. Wrap the native first step on both rehearsal donors in all three optimized cells; independently rebuild conditioning, compare epsilon, and bound x0 differences caused by native fp16 arithmetic. The existing exact C0 capture/replay check remains. Measured peak memory must stay below device total minus 1.5 GiB; no numerical/GPU fit claim follows from local mocks. See `design/r3-denoiser.md` and `stage-s/writer-implementation.md` for inspected diffusers 0.35.1 sources, precision and parity scope.

The original Stage S protocol and Round 2 amendment remain historical freezes; the cumulative Round 3 config/inventory and sections below specify prospective additions. Intermediate commits remain preparation-INCOMPLETE pending integration and the fresh independent review.

## Decisions for the user

Decisions and the recommended package will be finalized after R3-2 through R3-5. All alternatives remain proposals. Claude must record the actual gate/profile and compute choice in a commit **before any server scientific output**, including Stage P; the later post-P freeze records the selected configuration under that already chosen profile. No outcome-dependent profile choice is permitted.

## R3-2: bounded writer selection and budget control

Stage P uses exactly the24 metadata-verified development sources outside Stage S:16 tuning and8 veto-only check. Eight alternatives combine noise/x0 with robust PSNR budgets52/46/42/38dB; refinement remains58dB. Successive halving evaluates cumulative4/8/16 tuning prefixes, allocating8/4/2 entrants and nominating one. Shared retained F5 and finalist F5 budget controls keep the worst-case allocation at136 marked source-units and3264 native saved-image attempts. The check cannot nominate a runner-up. Missing contenders block progression; observed scientific failures and resource stops remain distinct. See stage-p/PROTOCOL.md for exact ranking, futility, quality and negative-call predicates.

The chosen Stage P profile is recorded before its first scientific output. Successful selection is hash-bound to that choice, the base config, complete tuning/check evidence and exact parameters. Stage S consumes it automatically or by explicit path. If the user chooses P, a missing/failed selection cannot fall back to the original candidate. The original noise52 writer remains available only when P was declined beforehand. K3 is excluded from gradients but seen by selection, so it is not an unseen-family selection test; future SD3.5 is the proposed unseen Stage C family.

Stage S adds f5-budget beside retained F5r2. It uses the original robust writer with the selected robust budget,150+50 reader updates and unchanged fragile writes; retained F5r2 remains unchanged. All four F6 variants share the selected robust budget. Nominal budget equality is not achieved-distortion equality: paired measured quality against the budget control remains required in the proposed profile. The complete11-arm screen has176 clean,2112 native,1232 threat and1408 secondary images,8960 detector rows and4928 quality rows.

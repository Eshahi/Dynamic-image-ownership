# C4 pinned inversion/reconstruction path bridge

Issue #18 / draft PR #67. Ordinary implementation under the actual reconstruction
amendment in c4-reconstruction-path-amendment-20260927.md. Apply research-contract.md
and scope-guard.md. Original proposal, controls, quality targets, failed runs and
blind image-domain detector remain unchanged. No learned-model execution here.

## Composition and exact semantics

`src/embedding/inversion_path.py` connects the reviewed pair solver to already
loaded `DiffusersComponents`. It never loads checkpoints, encodes/decodes an image,
generates new noise, optimizes a watermark or chooses a development source.
Only Diffusers 0.35.1 concrete DDIM/epsilon profile is allowed: scaled-linear
1000 training steps, beta .00085–.012, leading spacing and offset1, eta0,
no clipping/thresholding/rescaled betas, final alpha **not set to one**.
All scheduler coefficients, complete inference timesteps and chosen suffix are
compared with a separately constructed software reference before prediction.
The initial component profile remains SD1.5 fp32, fixed detached finite
`[1,77,768]` condition and frozen eval UNet with compatible input/output widths.
Parameter/buffer device/dtype/gradient/eval state, backend/schedule identity and
condition values are rechecked before and after each prediction. No weight-content
authenticity or adversarial-module isolation follows: the future exact loader
must still bind actual asset hashes and prove conditioning/model provenance.
Eval/frozen state alone does not certify bitwise CUDA determinism.

Following an actual independent blocking finding, named child/parameter/buffer
identities, shapes/strides and Torch mutation versions are also bound at constructor
and checked before/after every prediction. Original object references are retained
to prevent identity-id recycling; removed/replaced or ordinary in-place updated
tensors cannot silently become a different predictor. Pinned eager tensors must
expose Torch's `_version`; untracked inference-mode tensors are refused. This is
an intentionally pinned-runtime guard, not a public-portable mutation API or a
content hash. Deliberate `.data`/raw-storage edits bypassing Torch versioning and
hostile Python method monkeypatches are outside this accidental-drift guarantee;
manifest source/asset checks and trusted worker ownership remain mandatory.

Inversion visits pairs in reverse denoising order; reconstruction replay visits
the same pairs in forward order with the same bound timestep/condition. Pair alpha
continuity is checked. For the existing10-step/.2suffix this is inversion `[1,101]`
and replay `[101,1]`. The final prior scheduler alpha is alpha[0], not1; the desired
encoded source is explicitly the **post-final-step decoder latent target**. Treating
it as this solver's boundary does not claim that an exact generative-distribution
transition at alpha[0] or all possible encoders/VAEs was reproduced. No VAE scale,
padding/crop/native PNG semantics are altered by this latent-only component.

Every pair must report actual forward-residual convergence. The complete replay
then measures maximum absolute latent error against the immutable terminal target,
with a separately declared tolerance. Individually converged pairs can still fail
the roundtrip. A failed inverse pair stops immediately, with its failed state
offered for persistence; no skip, fallback or regeneration search is performed.
This roundtrip criterion is not image PSNR/SSIM/LPIPS or blind watermark evidence.

## Bounded cost and honest partial results

Whole-path forward cap is an explicit integer up to16384; each inverse call's
pair policy is additionally capped by remaining budget. All replay calls are
reserved before inversion so a budget cannot silently omit the verification.
Prediction/evaluation and backward counts are distinct. Rejected line-search
trials, gradient-bearing re-evaluations and replay calls count; a started failed
prediction is retained in the journal count, not retrospectively erased.
No learned backward timing or GPU fit is claimed by this accounting.

The cooperative monotonic wall limit is at most1200seconds, checked around
operations. It cannot terminate a stuck synchronous UNet/CUDA operation: a future
official runner must enforce an independent external timeout and memory guards.
Already-measured numeric outcomes are journaled before an overdue refusal.
Malformed payloads, model errors or persistence/callback failures propagate rather
than becoming success. Termination status distinguishes failed pair, global budget,
failed roundtrip and completed latent roundtrip. Exceptions require the outer
worker to persist actual failure/partial evidence; no success status is invented.

Caller-owned callbacks must durably journal metadata and save detached copies of
every completed/failed pair state and replay state **before** that state is marked
saved. The library does not write files or claim an in-memory list is crash-safe.
Returned pair summaries do not retain all GPU latent graphs/states; only metadata
is accumulated internally. Optional caller-declared guided priors are in denoising
order, fully validated before prediction and detached within a16MiB fp32 snapshot
cap. Their correct mathematical distribution is not chosen or accepted here.
The tensor cap of the pair component remains; these caps are not a full RAM/VRAM
ceiling and do not replace resource approval. No new software installation is used.

## Ordinary evidence versus next scientific package

Owned CPU fake-UNet tests use the actual pinned scheduler class without any model
weights or study images. They cover inverse/replay order, nonunit final alpha,
full roundtrip error, NFE/backward counts, partial/budget/timeouts, shape/profile
drift, callbacks, persistence isolation and declared priors. This is software
evidence only. The original random-noise backend remains the historical control;
it has not been relabeled as this inversion implementation.

Before image comparison, complete an exact versioned configuration, manifest-bound
integration into a separately reviewed worker, source/model/metric/safety custody,
whole-run resources and durable file inventories, then obtain actual runner-bound
user approval. Compare native source preservation and incremental distortion and
key drift, retain all failures, and eventually test the real blind DCT detector.
No current method winner, C4 closure, RunPod need or new model download is established.
The older exact localization question stays pending on its historical clean commit;
this bridge does not modify, approve or consume that package.

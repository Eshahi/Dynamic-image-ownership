# Frozen-decoder source-latent refinement: bounded software candidate

Issue #18 / draft PR #67. Apply research-contract.md, scope-guard.md and the
actual user's reconstruction-path amendment. This is ordinary implementation and
supported prospective design, not a complete experiment/runner package or approval.
No claim of REED-VAE/GNRI author-code reproduction, new weights or decoder training.

## Why this next candidate is justified

Reviewed exploratory c4-reconstruction-dev-001 reports one native source's VAE-only
PSNR22.482789/SSIM0.742910/LPIPS0.058493, failing the combined unchanged targets.
The original fixed-base route is worse in PSNR/SSIM and exactly replays prior bytes.
That does not prove a universal VAE compression ceiling or identify a unique cause.
It does justify investigating different latents through the same frozen decoder,
instead of assuming inversion back to the unrefined encoded latent repairs loss.
Original failed outputs and all OOM records remain immutable negative evidence.

## Explicit candidate objective and algorithm

src/embedding/latent_refinement.py takes already-verified loaded components, a
fixed source RGB float32[0,1] native grid and a supplied scaled latent. It performs
no encoding/model load/DDIM/semantic extraction/carrier generation/watermarking.
Native crop follows the unchanged replicate-pad64 profile. Decoder input is latent
divided by the existing VAE scale; output normalization/clamp is unchanged.

Objective: native continuous RGB MSE against source plus explicit nonnegative
weight times mean-square latent displacement from the immutable initial latent.
The source is available only on the embedding/reconstruction side, not to the
blind image-DCT detector. Model weights stay frozen; only the scaled latent changes.
No SSIM/LPIPS/safety/PNG quality target is asserted from continuous MSE alone.

Fixed normalized-gradient projected descent updates within an explicit global L2
ball around the initial latent. Each declared trial halves the step on rejection;
it must strictly decrease both the last accepted objective and the fresh gradient
evaluation objective. Rejected trials count and are durably persisted too. This is
a declared numerical algorithm, not unreported hyperparameter/outcome search.
There are no selected scientific defaults: the typed policy requires iteration,
NFE, backtrack, learning-rate, L2-radius, prior-weight, MSE tolerance and duration
values. Owned fixture values are not selections or evidence on study images.

## Custody, accounting and failure contract

Accept only exact base DiffusersComponents or reviewed CheckpointedComponents;
the bound backend decode and VAE decode methods must retain the exact owners and
functions. Named VAE/UNet identities, tensor versions, shapes/device/dtype/eval,
conditioning/scheduler/config/scale remain guarded through the existing bridge.
Original objects stay retained; `.data`/hostile-code/content-authentication limits
of the private mutation-version guard are unchanged. Manifest asset custody is
still mandatory. Decode delegates through the checkpoint-preserving backend.

One forward-evaluation budget includes initial state, gradient reevaluations and
all accepted/rejected line trials. Backward calls and actual root decoder forward
starts/recomputations are separate; a temporary decoder pre-hook refuses before
exceeding twice NFE and is removed on every exit. These counts are not complete VAE
FLOPs, measured memory or completed-forward evidence. State copies/metadata go to
mandatory caller persistence before evaluated/terminal records; callback failure
aborts, not silently continues. Exceptions preserve earlier callbacks and never
return a terminal success. Budget/zero-gradient/line-search stops are explicit
diagnostic results, not removed failed seeds or a fallback method.

MSE-tolerance termination is only a continuous optimization diagnostic. It does
not report combined source PNG targets, safety or watermark survival. No encoder,
DDIM or detector is called, and no model parameter gradient is accumulated.
Cooperative time checks cannot kill a stuck call; external runner timeout and
actual resource/allocation headroom are required for any learned-model execution.

## Supported next full experiment, still incomplete

A coherent future comparison should retain all historical reconstruction arms
and add this separately labeled fixed-decoder candidate after justified fixed
policy rationale. Test decoder-only refinement and refined-latent inverse/replay
without erasing an inversion failure. Preserve fixed source/config/assets,
native PNG source PSNR/SSIM/LPIPS, safety, original control replay, q/h diagnostics
if declared, durable partial states and actual resource/time counts. One source
remains exploratory; dependent arms are not independent samples or CI evidence.

The complete worker/config/schema/strict input closure/helper/manifest binding and
independent package review do not yet exist for this candidate. Do not make a
compute question or execute a pretrained module until they do. The localization
approval is consumed; no new data, model download/training, paid compute, threshold
change, source-assisted detector or reduced dataset is authorized. C4 stays open,
C5 dependent; no quality repair, broader efficacy or lifecycle verdict is claimed.

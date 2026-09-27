# C4 retained-pair quality and key-drift design

Status: complete package code/design reviewed under #18 / draft PR #67. NOT RUN on study
images; no new model load, inference, scientific approval or C4 acceptance.
Applies [research contract](research-contract.md), [scope guard](scope-guard.md)
and [A5](method-spec.md). This is a post-hoc exploratory follow-up to run003,
not retroactive preregistration of that completed embedding trial.

## Frozen observation frame

Exactly the retained source snapshot and two saved outputs from
`c4-embedding-dev-003`, executed commit
`0ac89f587554c27b4fd6b143f270a65770c6d11f`, manifest
`6681e972a7fb249e66d6cb31f0e0b09f4bc6e6e6890e45ce4df0cc4816d3156e`.
Source UID `ms-coco:coco-2017:val2017:109798`, native RGB8 500x333.
The existing [reviewed result](../reports/dev/c4-embedding-dev-003/result.md)
and retained-artifact analyzer are the custody basis; a new execution worker
must reverify their source/output/config digests before loading a model.
No raw dataset scan, new image, seed, generator, latent optimizer, attack,
calibration, detector threshold or inference-time method modification.

Three dependent comparisons, in fixed order: control versus original source;
candidate versus original source; candidate versus control. The second is the
proposal quality reference; the third is incremental distortion only and must
not conceal reconstruction loss. No geometric alignment, resizing or cropping
for quality metrics. Report every comparison, failure and missing value.
No averaging into a success claim, population CI or independent N=3 claim.

## Metric profile and diagnostic targets

`src/embedding/quality.py` implements RGB float64 MSE over all native pixels
and channels in [0,1], PSNR with fixed data range 1 (zero MSE encoded as JSON
null plus explicit positive-infinity flag), and channel-averaged RGB SSIM:
scikit-image 0.26.0, Gaussian sigma 1.5, 11-pixel extent, population covariance,
K1 .01/K2 .03 and data_range=1. No outcome-dependent luminance profile choice.
The [official metric documentation](https://scikit-image.org/docs/stable/api/skimage.metrics.html)
supports explicit floating-point data range and the Gaussian/population
covariance profile; RGB averaging is this project's declared choice, not a
claim of exact grayscale Wang-paper reproduction.

LPIPS 0.1.4 / learned metric version 0.1 / AlexNet, native grid, batch one,
RGB float32 [-1,1], normalize=False, spatial=False, eval/no-grad, no dropout
activity, CUDA fp32/no autocast/no TF32/deterministic algorithms. Both the
verified 244,408,911-byte AlexNet trunk and exact five learned linear tensors
are required. The constructor disables pretrained download and random trunk
features are wholly replaced by verified weights; failure aborts, not random
fallback. Package source/learned bytes are checked before package import.
The loader rejects an already-imported LPIPS package, binds imported module
origins to checked distribution files, and returns a frozen receipt. Before
every forward call it rechecks configuration, every child eval flag, module
identities and a digest of all floating parameter/buffer tensors (including
scaling buffers), requiring CUDA fp32 and no gradients. This is conservative
profile custody, not cryptographic protection from hostile Python code.
[Pinned upstream](https://github.com/richzhang/PerceptualSimilarity/tree/082bb24f84c091ea94de2867d34c4544f68e0963)
and [official usage](https://github.com/richzhang/PerceptualSimilarity)
document RGB NCHW [-1,1] and version 0.1. Software tests alone do not establish
numeric LPIPS parity or validate rights to redistribute weights.

Report strict PSNR>35, SSIM>0.9, LPIPS<0.1 separately and their conjunction
for each pair. These are per-image proposal-target diagnostics, not a final
task/thesis acceptance gate. A failed target is retained without tuning or
retry. No neural metric is computed by importing this module.

## Key drift, not blind detection

Future authorized worker must use the existing C2 `PinnedClipEncoder` CUDA
fp32 profile, all-zero 32-byte projection seed and C3b native pHash profile.
Re-extract source/control/candidate, with no cache reuse. Source q=`5f0f`,
h=`40a9a967` must exactly replay prior enrollment or record profile/replay
failure; never silently replace enrollment. Record all 12 projection margins
and pHash margins, code bytes, source/output Hamming distances and whether the
source q/h lie within radius-one neighborhoods centered on each output.
Source-code containment is a necessary search-coverage diagnostic, not proof
of C5 fused-score detection, watermark recovery, authenticity or ownership.
The module always labels blind detection NOT_RUN and scientific acceptance
false. Do not supply original codes to claim blind detector success.

## Execution boundary and remaining binding

One future exact scientific package should cover all three quality comparisons
and three feature extractions together, using existing local assets, USD0,
no new downloads, external 20-minute ceiling and a proposed Torch 4GiB limit.
This is a planning estimate, NOT measured capacity or approved authority.
Dedicated fail-closed worker/launcher, exact retained-byte/environment/recipe
inventory, exploratory spec and official helper/preview are now implemented.
Independent exact-package review and repairs are recorded in
[package audit](../audits/c4-saved-pair-package-review-20260927/review.md).
Before asking the user, independently rebind the final documentation-only
clean commit and regenerated manifest; review-candidate hashes are not the
final execution authorization. No actual scientific run has been approved.
Do not reuse the consumed run003 approval or execute this library standalone.
Preserve restricted local-research custody: no source/output redistribution,
public figures or expanded rights certification.

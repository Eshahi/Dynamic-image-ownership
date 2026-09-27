# C4 reconstruction-path amendment and next implementation

Status: authorized alternative research/design and ordinary implementation;
no new scientific execution or measured improvement. Issue #18 / PR #67.

## Actual user direction and authority

On 2026-09-27 the user explicitly stated that the proposal's path is not final
and asked to find and use better reconstruction routes from newer related papers.
This records the actual direction, not supervisor/university acceptance or an
invented exact compute verdict. Under research/approval-policy.md, routine
reconstruction candidate implementation may now diverge from A5 candidate v1,
with versioned rationale, independent review and disclosed experimental changes.
Original proposal, failed runs, questions, datasets and quality targets remain.

The narrower reconstruction authorization does not silently replace public
OwnerID/signature semantics, latent/noise embedding, or blind image-DCT detection.
Embedding-side inversion is different from adding inversion to verification.
Changing those core claims or adopting source-assisted/neural verification must
be separately described and reviewed. Apply research/research-contract.md and
research/scope-guard.md, with this recorded reconstruction amendment.

## Selected direction, not a selected winner

The present random-noise img2img suffix is not inversion: a newly generated noise
sample is added to the encoded source, rather than solving for a state that
reconstructs it. Nearly identical poor marked/control source quality suggests
a shared reconstruction problem in the one measured case, not a causal diagnosis.

Promote **source-conditioned deterministic inversion and reconstruction** to the
next C4 implementation candidate. Keep the current SD1.5 assets initially to
separate algorithm improvement from model replacement; retain the empty prompt
as a controlled primary profile. Build exact scheduler-pair residual tests, a
bounded iterative inversion reference and a guided residual solver informed by
GNRI. No copied unlicensed upstream implementation: independently implement the
published equations with attribution and synthetic numerical/parity review.
GNRI is a candidate, not presumed superior to ReNoise or stochastic alternatives.
TRDI is a later, explicitly paired scheduler ablation, not an automatic add-on.

The source screen has concrete contrary evidence: captioned SD1.5 inversion
benchmarks in TRDI still miss our >35 dB target. Captions, A100 timings, model
identities, 50-step trajectories and editing-background metrics do not transfer
directly to our empty-conditioned native-size source metrics. See the inspected
version ledger at literature/reconstruction-screen-20260927/inspection.md.

If the VAE-only control fails, better inversion alone is not presumed sufficient.
Its encode/decode benchmark is a measured reference, not a theorem bounding all
decoder latents or all future VAEs. A second candidate is bounded source-latent
reconstruction optimization with the existing frozen decoder; this is an agent
design proposal, not an attributed REED-VAE reproduction. Decoder adaptation or
an alternative compatible VAE needs actual published weights/rights/shape/scaling
and safety review before adoption; REED's inspected repository is not ready.
No model download, fine-tuning or training has been authorized by this screen.

## Coherent next package and selection criteria

1. Complete the prospective three-arm localization control once specifically
   approved; preserve all failures and original matched reconstruction.
2. Implement synthetic-testable scheduler/inversion components, with explicit
   target residual, maximum function evaluations, finite/zero-gradient handling,
   latent-shape/scaling checks, deterministic termination and partial journals.
3. Prepare one reviewed comparison package: current method control, VAE-only,
   ordinary inversion, guided inversion, and (only if justified by VAE results)
   bounded frozen-decoder source-latent refinement. Preregister arms/IDs/limits
   before outcome inspection, not best-of-many unrecorded prompt/step tuning.
4. Evaluate decoded native PNG PSNR/SSIM/LPIPS against the source and paired
   incremental distortion, q/h drift, actual blind-DCT evidence, runtime/VRAM
   and coverage. Reconstruction improvement alone cannot establish watermark
   survival, owner authentication, regeneration resistance or full method success.
5. Select a versioned embedding reconstruction route only after measured paired
   development evidence and independent review; lock it before held-out evaluation.

No extra paid GPU is justified from literature alone. Local fit and total backward
cost remain empirical. New package resources/downloads/remote costs receive their
own exact approval. Do not execute author's upstream launch commands, install their
requirements, or upgrade the scientific environment by inference.

## Existing pending compute package

The earlier question concerns only `c4-reconstruction-dev-001`, local20min/USD0,
manifest `065979dd13b7a6665c149d96baf8c9eceb7c06882321b99b15cf6445412337da`,
clean commit `36b4fa85942d744b7c1749947b675da784215d3a`. This new research direction
is not its affirmative reply and does not extend it to inversion experiments.
Preserve this historical exact package and question; do not duplicate the prompt.
If approved later, execute only from that exact clean commit through the official
runner, or present a genuinely revised package for its separate exact decision.
The evolving author checkout is no longer that execution binding. Prior run003
and saved-pair001 approvals remain consumed; C4 open, C5 dependent, no gate verdict.

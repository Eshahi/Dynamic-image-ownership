# Refined-target reconstruction comparison: ordinary software composition

Issue #18 / draft PR #67. Applies research-contract.md and scope-guard.md and the
actual user request for reconstruction repair. Implements the priority from the
independent Astra audit, not a claim that source quality has been repaired.
No learned model, study image, metric, GPU, installation or download was run.

## Fixed six-arm composition

`src/embedding/refinement_comparison.py` accepts already verified, loaded concrete
base or checkpointed components. One posterior-mode encode supplies an immutable
scaled terminal latent. Exactly these arms run in order, with no outcome-selected
solver or undeclared retry:

1. VAE-only from the original encoded terminal latent.
2. Unchanged zero-noise DDIM from that encoded latent.
3. Unchanged fixed-base-noise DDIM from that encoded latent.
4. Direct frozen-decoder source-latent refinement.
5. Fixed-point inverse/replay targeting the original encoded terminal latent.
6. The same fixed-point policy targeting the **refined** terminal latent.

The three historical controls are retained for parity/source-loss localization;
the unrefined inverse is an endpoint/path control. The last two new fidelity
questions are separate: whether the fixed decoder can represent a better source,
and whether the diffusion path can reproduce that refined latent. Inversion does
not target the original encoded latent while pretending to preserve refinement.
This component excludes GNRI-inspired extra arms, watermark optimization, source
output blending, decoder training, a neural detector and blind-detection claims.

All policy values are supplied by a typed explicit policy; owned synthetic fixture
values are not selected scientific defaults. Native continuous source MSE plus
optional latent penalty is the reviewed refinement objective; historical
`configs/c4-development.json` and its poor-control regularizer are unchanged.
Revisiting that regularizer belongs to a later versioned watermark design, after
an actual good reconstruction anchor exists. No source-side optimization is
provided to the core suspect-only detector as privileged side information.

## Outcomes, persistence and failure

Native crop and normalization follow the existing pipeline. Direct refinement
returns its already evaluated native tensor without an unreported final decode.
Every arm image requires durable caller persistence; all returned images still
require native saved-PNG PSNR/SSIM/LPIPS, safety and public q/h checks in the future
worker. Continuous MSE or a completed component is not scientific acceptance.

The shared encoded target and refined target are separately persisted. All
refinement evaluated/rejected states and inverse/replay pair states flow through
mandatory caller-owned saves. Returned inverse initial and successful terminal
states are also retained. Tensor/metadata callback payloads are isolated copies.
Storage/journal failures abort rather than emitting a false completed composition.

Normally stopped refinement (budget, zero gradient, line-search failure or MSE
tolerance) returns a labeled diagnostic target. Its status is retained in the
refined inverse arm, never relabeled as quality success. This prospectively fixed
composition attempts inverse/replay even for a normally budget-stopped refinement;
it does not condition execution on observed quality. A refinement exception,
including strict rounded-radius refusal, aborts the package with earlier controls
and partial states retained; there is no encoded-target fallback.

An inverse that fails pair convergence, global NFE or whole-path residual has a
durably journaled failed arm and **no image/decoder fallback**. Its failure does
not erase the other fixed arm. Exceptions stop all later arms. A terminal result
may say completed-with-nonconverged-arms, not completed scientific success.

## Binding and resource accounting

One outer cooperative wall deadline bounds all arms and persistence; inner
refinement/path deadlines use the remaining duration. Time/profile checks occur
before and after callbacks, including the last image save and terminal journal.
A stuck model call still requires the official runner's external timeout.

Guard exact backend/VAE method owners and functions, frozen VAE identities/tensor
versions/dtype/device/evaluation/scaling, and the existing pinned UNet/condition/
DDIM profile. No CPU fixture or mutation-version check authenticates weight bytes
or protects against hostile in-process code. Future manifest/loader custody remains
mandatory. Keep checkpoint delegation for decoder and UNet operations.

Per-arm refinement decoder NFE/backward/root-start/recomputation counts and inverse
scheduler NFE/backward/root-UNet/recomputation/residual counts remain distinct.
Legacy denoising metadata reports its fixed scheduler count, not a full measured
FLOP or decoder-call inventory. The six-arm policy is not a learned-model VRAM,
RAM, disk or time estimate. No resource cap increase or RunPod permission follows.

## Checks and limits

Owned CPU tests use analytic fake decoder/UNet modules and actual pinned scheduler
software. They check shared encode, native outputs, refined versus original inverse
targets, unchanged historical control parity, checkpoint fixture parity, normal
budget status propagation, inverse/residual failure without fallback, isolated
payloads, storage/rounded-radius failures, owner/profile mutation and slow final
persistence. No learned-model or population inference follows from these fixtures.
The initial suite had one author test error: per-arm budget2 is a structurally
valid policy value but insufficient for this fixture's two-step replay; refusal
belongs to composition preflight, not policy construction. The test now checks
the correct layer; the original failure is preserved in this description/Git.

This is not the full executable package. A versioned real policy/config, actual
worker/launcher, asset/environment/input closure, durable disk quota/journal/PNG/
safety/metric/key outputs, reviewed exact clean manifest and actual runner-bound
user decision are still required. No compute question should be issued from this
component alone. All prior scientific approvals are consumed. C4 remains open;
C5 remains dependent; targets, failures, source counts and native2K obligations
are unchanged. Independent review must bind the exact committed artifacts.

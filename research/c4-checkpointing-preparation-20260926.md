# C4 activation-checkpoint candidate: software preparation only

Issue #18 / draft PR #67. Applies the unchanged research contract, scope guard
and method specification. Failed approved runs 001 and 002 remain immutable and
their authorizations consumed. No model, study pixel, GPU or scientific run is
used by this preparation; no new execution manifest is approved or generated.

## Source rationale and exact candidate

[Official PyTorch 2.12 checkpoint documentation](https://docs.pytorch.org/docs/2.12/checkpoint.html),
inspected 2026-09-26, describes exchanging activation retention for backward
recomputation, recommends explicit non-reentrant mode, and warns that changed
forward/recompute behavior can silently invalidate gradients. Its default
determinism check compares tensor shape/dtype/device, not numerical equality.

`src/embedding/checkpointing.py` introduces a separate opt-in class requiring
installed Torch 2.12.1. Each UNet call and VAE decoder is independently checkpointed
with `use_reentrant=False`, RNG preservation and the default determinism check.
Timesteps are bound per invocation. Source encode, matched-control/no-grad and
final/no-grad renders remain direct. No resolution, source, fp32 precision, empty
condition, scheduler arithmetic, gain, loss, optimizer, projection or cap changes.
The original class has only two equivalent dispatch hooks extracted from its
existing calls; its default arithmetic remains unchanged. No worker imports or
constructs the candidate, and consumed run001/run002 recipes are not repackaged.

The candidate checks module/parameter/buffer identities, ordinary tensor version
counters, device/dtype/shape/gradient flags, module training states, condition,
scheduler tensor identities/versions/config/step count and frozen settings before
forward/replay. This is not a proof of arbitrary Python state or unsafe `.data`
mutation immutability. Future concrete SD integration must review side effects,
attention processors/hooks and replay compatibility. Current operation journals
mark original forward operations; replay occurs within backward, not a second
logical denoising iteration. Do not interpret forward journal counts as total
kernel/recompute work. Replay failure propagates; no fallback or auto retry.

## Owned CPU evidence and limits

Six tests cover exact toy output/input-gradient parity across both suffix
timesteps, unchanged projected optimizer/control trajectories, no-grad bypass,
condition/weight/training/identity/schedule drift rejection, replay failure, and
lower autograd-saved payload in an owned nonlinear decoder fixture with equal
outputs and gradients. These analytic pixels/parameters are not dataset images
or model weights. Saved-payload hooks count requested tensor bytes, not unique
live storage, RSS, CUDA peak or physical VRAM. No numeric GPU saving is claimed.

Initial test discovery accidentally re-exported the original fixture TestCase
and ran its 12 tests in addition to five new tests; that import was corrected to
a module reference. Final focused discovery finds 27 tests: WSL 26 pass/one
expected JSON Schema environment skip; Windows controller nine pass/18 expected
Torch-dependent skips. The Windows controller has no Torch, so its skips are not
cross-runtime tensor parity evidence. Existing WSL Torch/Diffusers are used;
there is no installation or tiny CUDA probe repetition.

Actual SD forward/gradient parity, recomputation peak/time, CUDA allocator fit,
PNG/quality/safety/blind verification remain NOT_RUN. Whole-component checkpointing
can still need large replay workspace and fail during backward; CPU tests cannot
promise a fix for the observed 8GiB OOM or prove a GPU minimum. Next is independent
code review, then explicit new integration/design/package review before any new
scientific approval request. C4 stays OPEN; official lifecycle remains paused.

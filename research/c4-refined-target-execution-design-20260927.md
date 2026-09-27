# Prospective source-refinement and target-replay execution design

Issue #18 / PR #67. Apply research-contract.md and scope-guard.md. Follow the
actual user's reconstruction-repair request and independent Astra feasibility
audit. This is exploratory development after negative results on this same
source, not retrospective confirmatory preregistration or scientific approval.
All earlier scientific approvals are consumed and cannot execute this package.

## Exact question and boundaries

The six-arm composition is specified in c4-refined-target-comparison-component-
20260927.md. Use only the retained run003 source109798 native500x333 and existing
verified SD1.5,CLIP and LPIPS/AlexNet assets. No new image/model/software download,
source replacement, training, watermark optimization, blind detector or paid
service. Original failed outputs/config/targets remain unchanged.

The two new questions are decoder representability under this finite budget and
faithful diffusion replay of the refined target. The three historical controls
and unrefined inverse keep their own outcomes. Preserve all failed arms, residuals,
direct versus replayed target identities and resource measures. There is no
quality-based branch: normally budget/line-search/zero-gradient-stopped refinement
still supplies its explicitly labeled target to the fixed inverse. Exceptions
abort and never use an encoded fallback. Nonconverged inverse arms have no PNG;
the worker may measure other rendered arms but finishes failed/incomplete.

## Parameter rationale, not a performance prediction

Hash-bound configs/c4-refinement-comparison.json selects a first prospectively
fixed source-only optimization profile. These values have not been tested on the
retained source and are not inferred to be sufficient to meet35dB.

- 64 normalized descent updates, step L2=1, at most two halvings per update.
  This permits finite incremental movement without unnormalized-gradient scale
  dependence. NFE257 is exactly initial1 +64*(gradient1 +maximum3trials).
  The global trust radius80 exceeds the arithmetic sum64 of nominal unit steps,
  retaining an explicit outer displacement ceiling without intentionally testing
  its rounding boundary. Strict measured fp32 refusal remains authoritative.
- Latent prior weight0 isolates source reconstruction from the old poor-control
  anchor; this is a new labeled reconstruction-only arm, not an unreported change
  to watermark loss. Native continuous RGB MSE diagnostic tolerance0.0003 is below
  10^-3.5; it does not guarantee native PNG PSNR,SSIM or LPIPS after quantization.
- Refinement720s within comparison1000s leaves a bounded cooperative allowance for
  controls and both inverse arms. The pair fixed-point reference retains its
  existing32-NFE,1e-5 absolute residual policy. Per inverse128 NFE permits the two
  active suffix pairs plus replay without assuming convergence. Whole-path
  residual1e-5 remains separate from per-pair convergence and image quality.
- No GNRI-inspired arm, new prompt, source bypass or trained decoder is included.
  These parameter choices are engineering budget selections, not optimized
  scientific defaults or literature-reproduced hyperparameters.

## Measurements and outcome integrity

Save native ties-even PNGs before safety/metrics. Classical source-reference
RGBfloat64 MSE/PSNR and existing SSIM, pinned LPIPS AlexNetv0.1, and all unchanged
target indicators are primary. Report direct-refined versus VAE source MSE and
replay versus direct-refined source metrics/residual explicitly; no population
confidence interval on one source or six dependent arms.

Sequential existing CLIP extracts q and pHash h from source and each saved PNG;
source enrollment must replay exactly before drift is interpreted. These are
recovery/stability diagnostics, not watermark presence, calibrated detection,
regeneration classification or legal ownership. No source keys go to a detector.
Geometric synchronization and latent-to-DCT feasibility remain separate blockers.

25 fixed cells cover render/safety/LPIPS/codes for six arms plus source codes.
Pending and failed cells remain distinct; absent arms are never zero metrics.
The entire result requires normal composition return, all required cells/output
hashes and official runner success. A terminal-named journal row followed by an
exception/timeout is overridden by failure, not a completed experiment.

Generated latent states use exclusive bounded safetensors files, not untrusted
pickle loading. Each state digest,size,row and path is journaled after fsync.
State quota64MiB/1024files, single-state4MiB and journal8MiB cap runaway storage;
quota failures retain existing bytes, never delete or restart. Final reports,
partial PNGs and earlier trajectory states survive normal caught failures.

## Execution custody and resource estimate

Prospective ID c4-refined-target-reconstruction-development-v1, run
c4-refined-target-dev-001, local only, one seed0. Exact source/config/environment,
policy, transitive code/spec/design and installed helper/clean Git checks must
pass bounded independent package and final-binding review before one actual
user approval question. No approval artifact is supplied here.

The existing Windows C1 validator produces a per-run exact receipt; the existing
WSL CPython3.14.4/62-distribution worker consumes it. The bridge adds only this
named experiment to its allowlist; it neither bypasses the official runner nor
changes full configuration/schema validation. The new package checks its fixed
run,target,outputs,budget,resources,policy and exact input inventory separately.

Outer1200s, parent1190s, Linux timeout1140s with TERM and10s KILL escalation.
Torch allocator ceiling9216MiB is not total VRAM; require measured freeVRAM
>=10240MiB. RAM estimate12288MiB requires available>=13GiB. Disk ceiling4096MiB
requires >=4GiB free: existing SD asset snapshot is about3GiB, latent quota64MiB,
six native PNGs/journal/result far smaller. Existing metrics models load sequentially
after diffusion models are deleted. Local costUSD0, no remote reservation/API.
The previous localization's observed allocated5.16GiB/reserved7.62GiB and59.82s
are contextual measurements, not evidence that64decoder backwards or inversion
fit this budget. Actual fit/time are unknown and failure remains informative.

No package execution has occurred. Full final clean manifest/hash/helper preview
and independent binding disposition must be recorded externally before approval.
C4 stays open,C5 dependent, native2K/all6900-source obligations unchanged; this
native500x333 diagnostic is not a coverage substitute or method success claim.

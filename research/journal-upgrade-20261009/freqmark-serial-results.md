# FreqMark serial scheduling: numerical gate unavailable

2026-10-13. The single [serial-backprop amendment](freqmark-memory-amendment.md) stopped after **7.277 seconds**, before optimizing either photograph. The actual-model numerical comparison could not complete because the installed PyTorch CUDA antialiased bicubic resize backward has no deterministic implementation. This is an unsupported execution path, not a measured gradient disagreement, watermark failure, strict-quality result or competitive loss.

Code/config commit: `636eb8c`. Retained run: MAIN `.thesis-build/dev-runs/20261013-1843-freqmark-serial/run.json`, outcome `numeric_gate_failed`, process exit 3. [Compact evidence](freqmark-serial-summary.json) preserves the exact implementation identity, flags, error, resources and source statuses. The earlier allocation-limited attempt at `878a736` remains unchanged and separate.

## Observations

- Both pinned models and all configuration/card files passed cached-file checks against the acquisition ledger. No downloads occurred. Cached verification took .234 seconds; recorded model loading took .782 seconds.
- Deterministic algorithms were enabled with errors rather than warnings, TF32 was disabled, and fp32 precision was retained. The frozen 128-square fixture was saved before model calls.
- The first comparison, zero perturbations with fresh Adam state, reached the joint-reference backward operation. `upsample_bicubic2d_aa_backward_out_cuda` raised an unsupported-determinism error. No one of the four comparisons completed; the serial gradient, update residuals and tolerances were therefore not evaluated.
- Sources 30 and 72 both remain `not_started`: zero real-source updates and no final marked PNGs. No recovery, quality, embedding-time or attack score exists for this attempt.
- The monitor recorded 901,803,520 bytes of peak CUDA allocation and 1,521,111,040 bytes of process RSS. These are recorded monitor values, not evidence that full-resolution optimization fits the allowance. No resource-limit failure occurred.
- Fixture, partial validation JSON/NPZ, traceback and execution flags are retained. The process exited and no science child remained. Additional rental/API cost was USD 0; electricity was not metered.

## Decision and article consequence

Close this amendment under its prospective stop rule. Do not disable determinism, relax tolerances, replace interpolation, change precision or launch a second attempt under the same protocol. Serial accumulation is algebraically motivated, but this implementation has not passed the required numerical validation. A larger GPU alone would not address the reported missing deterministic operation; this run supplies no evidence that paid compute is needed.

FreqMark remains a named independent reconstruction of uncertain native fidelity, with no usable performance result. Its absence cannot become an E3 win. WAM's existing exploratory results address a different comparison and do not replace the missing closest-method evidence. The two reconstruction attempts are closed; they do not prove that FreqMark is infeasible in general or exhaust other implementation approaches.

The next local preparation targets a different outstanding validity question: a blinded human development panel from the already retained H1 attack images. It can distinguish observed content-predicate rejection from independently judged content change. It cannot establish external competitiveness, novel mechanism, population validity or Q1 readiness. Actual ratings must come from independent humans; no ratings or approval are supplied by this report.

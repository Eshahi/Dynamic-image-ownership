# Native CUDA reconstruction: bounded warning-amendment result

2026-10-13, Codex agent. The separately named `FM-R48-Eq10-SD2community-serial-AAwarn` attempt is closed. Its [prospective protocol](no-human-next-study.md) was committed with the implementation at `4213674169c5d305115a50ddf90da81dc6c1e95f` before execution. No E3, held-out output or previous attempt was changed.

## Outcome

The run stopped after **12.744495 inclusive seconds** in the first actual-model joint-reference backward. The full-resolution interpolation probe passed, but memory-efficient attention emitted nondeterminism warnings outside the sole permitted antialiased-bicubic operation. The policy rejected them before an optimizer update. The actual-model gate completed **zero of its 20 required comparisons**; neither photograph was started. This is an execution-policy failure, not measured gradient disagreement or watermark performance.

Evidence: MAIN `.thesis-build/dev-runs/20261013-150109-freqmark-serial-aawarn/run.json`, `interpolation-validation.json`, `numerical-validation.json` and saved fixtures/arrays. The run receipt contains exact commands, committed identity, asset receipts, installed versions and captured warnings. Torch was `2.12.1+cu130` on the RTX 5070 Ti Laptop GPU. All assets were cached; zero bytes were downloaded and additional rental/API cost was USD 0.

| Fixed prerequisite or endpoint | Observed result |
|---|---|
| Native 512-to-256 interpolation repeats | Three completed, finite and nonzero gradients; both reference comparisons passed |
| Maximum forward residual | 0 |
| Maximum gradient relative L2 residual | 3.216368903327017e-8, below 1e-4 |
| Maximum absolute gradient residual | 8.940696716308594e-8, below the fixed 0.0001601075695285797 limit |
| Expected interpolation warning | Observed and retained |
| Actual-model replicated comparisons | 0 completed; stopped at zero-fresh / J1 |
| Source 30 | Not started, zero updates, final PNG absent |
| Source 72 | Not started, zero updates, final PNG absent |
| Useful feasibility and strict-budget readiness | Neither conjunction achieved; clean recovery and quality are unobserved |
| Peak allocated GPU / process RSS | 1,417,047,040 / 1,682,989,056 bytes; not evidence that 512-square optimization fits |

The rejected warning states that memory-efficient attention defaults to a nondeterministic algorithm and requests strict deterministic mode. Temporarily enabling warning mode for backward therefore exposed another operation, even though the interpolation operator itself was locally stable. The whitelist was not broadened and no attention backend, precision, recipe, fixture or tolerance was changed after seeing this result. Strict deterministic mode was restored by the backward policy's `finally` block. The science process exited; no background experiment remains.

## Decision and interpretation

Close this FreqMark implementation route for the current local round, as frozen before execution. No fourth amendment, resumed terminal run, paid escape or artificial baseline score follows. This does not establish that native FreqMark is infeasible on this GPU, that its gradients fail the tolerances, that its quality is 0/2, or that E3 wins. Author-code/checkpoint equivalence was unresolved before the attempt and remains so.

Historical inclusive recorded effort is reported separately: the allocation-limited attempt used 580.234 seconds (including acquisition), the strict serial attempt 7.277 seconds, and this attempt 12.744 seconds, approximately 600.255 seconds in total. These are engineering-attempt times, not watermark construction-time comparisons.

The next scientific allocation is the prospectively specified valid-positive binding/component control study. Human ratings remain optional; constructed controls may establish behavior on their exact interventions but cannot declare regenerated images human-equivalent. The frozen M2 findings and their limitations remain unchanged.

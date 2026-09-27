# Independent decoder-continuation component review

Reviewer: `/root/astra_inverse_route_review`, independent of author `/root`.
Date: 2026-09-27. Issue #18 / PR #67. Final reviewed code commit:
`868d27a69415f2c4a479ee81cab4591e7d0a56b5`.

## Bounded verdict

No unresolved numerical/composition blocker found for this exact ordinary
implementation checkpoint. This is not execution approval, learned-model parity
evidence, image-quality acceptance, inverse convergence evidence, or C4 closure.
The real worker/custody/lifecycle review is a separate independent assignment.
All scientific approvals remain outside this verdict; no real retained tensor,
study image, learned model, GPU, image metric, download, or install was executed
for this review.

Read scope: `decoder_continuation.py`, the optional `constraint_anchor` and final
guard changes in `latent_refinement.py`, unchanged `adaptive_refinement.py`,
checkpoint/path binding dependencies, fixed config, experiment spec, design,
package policy/custody declarations, and related owned CPU fixtures. Initial
candidate was `8e4bea1c6e99f551e833e44180a896483dc29d47`; the config-typing repair
was `96d541bb3f6b1018084f0c587298c2a079ef3a03`.

## Evidence and numerical interpretation

- Both optimization arms receive independent clones of the same retained start.
  The separate original encoded anchor remains the radius-80 centre; neither
  continuation recentres it. `constraint_anchor=None` preserves historical
  refinement semantics. The strict recipe pins the two retained-state hashes,
  parent metadata and start-pixel replay; this review did not load those states.
- Both optimize native cropped, clamped RGB source MSE through the same frozen
  decoder scale/profile. Zero prior is enforced. The composition does not encode,
  predict with UNet, invert DDIM, train weights, or insert a watermark. Constructing
  the existing path guard checks bindings; it does not call its predictor.
- Control retains reset-step normalized descent, two halvings and strict
  objective decrease, including its existing rounded-projection refusal.
  Adaptive retains its separately reviewed projected Armijo test using
  `gradient dot (trial-current)`, deeper backtracking, warm starts and bounded
  step growth. The config's gradient threshold is the control's `1e-12`.
  These policies differ as a bundle, not a one-factor ablation or paper optimum.
- Each arm has 128 optimizer iterations/backwards and 513 optimizer decoder-NFE
  ceilings. Its actual returned state then receives one separately counted
  gradient-enabled image evaluation and backward: at most 514 decoder-NFE and
  129 backwards. The final loss must replay within `1e-8`; the gradient norm is
  measured there, not inherited from the preceding accepted state's gradient.
  Root decoder starts and checkpoint recomputations are counted separately.
- Callback payloads/state/image tensors are copies. Persistence failures,
  frozen-profile drift and time overruns propagate; hooks are removed in
  `finally`. Final callback guards prevent a terminal-named event from being
  mistaken for normal return. Numeric stops explicitly remain diagnostics,
  with saved-PNG quality and safety obligations outside the numeric component.
- The normal state-count bound is consistent with the declared inventory:
  2 shared states + 2 arm starts + 1026 optimizer evaluated states + 2 optimizer
  final states + 2 final-measurement states = 1034, below the 1040 reserve.
  Equal ceilings do not imply equal actual work or equal final NFE.

## Resolved review observation

At `96d541bb`, `900 > 2*430` alone did not reserve both full arm windows because
retained replay/persistence also consumed the global deadline. The author repaired
this at final commit `868d27a`: before either optimized arm starts, its full
430-second allowance must fit the remaining global window; otherwise the package
refuses. The arm deadline is its own start plus its complete allowance, including
final measurement/persistence. This prevents silently shortened arm allowances.
The design records that refusal as incomplete package evidence, not optimizer
failure. It does not promise that all work fits the prospective runtime cap.

The earlier integer-versus-float canonical recipe mismatch was repaired in
`96d541bb`; the tracked-config regression now passes. The original refusal must
remain recorded by the author rather than be represented as a successful preflight.

## Reproduced ordinary checks

Existing pinned WSL CPU interpreter only, with `-B`, no installations:

```text
python -B -m unittest scripts.test_c4_decoder_continuation \
  scripts.test_c4_latent_refinement scripts.test_c4_adaptive_refinement \
  scripts.test_c4_continuation_package
```

At `96d541bb`: 46 tests, 45 passed, one expected Windows-only launcher skip.
At final `868d27a`: 47 tests, 46 passed, the same expected skip. The new test
rejects insufficient second-arm time before adaptive continuation begins.

Additionally, 12 reviewer-owned, in-memory CPU scenarios passed on `96d541bb`:
caps 2/3/8/32 across plain and checkpointed synthetic decoders checked exact
saved-evaluation counts, final loss and an independent analytic gradient reference,
original-anchor bounds, recomputation accounting, no UNet calls and hook cleanup;
four further scenarios checked image/metadata sink mutation isolation, terminal
model mutation, final-state persistence failure and final image-save deadline
overrun. On final `868d27a`, an independent slow-retained-replay probe also passed:
the first optimized arm was refused before any arm-start event when its full
window no longer fit. No source/test files were changed by these probes.

## Limits on the next experiment

The frozen same-start comparison is an informative next decoder-endpoint test:
it separates additional old-policy optimization from the adaptive-policy bundle,
without confusing that question with inverse accuracy. It cannot establish a
decoder-capacity bound, population advantage, native-2K feasibility or full-method
success. A small measured gradient is local to this clamped objective and may
also reflect saturation; active trust-radius constraints require separate
interpretation. Saved-PNG PSNR/SSIM/LPIPS of all arms, failures and actual/common-NFE
progress remain required. Improved continuous MSE alone is not joint quality
acceptance, and a timeout must not be interpreted as numerical stagnation.

Final reviewed artifact SHA-256 values:

| Artifact | SHA-256 |
| --- | --- |
| `src/embedding/decoder_continuation.py` | `3f6ffb7ebc492d30bd22c89abba89c788aafb866adfe9df000ba07a92a2a9c23` |
| `src/embedding/latent_refinement.py` | `4cc53312496d022f9a14eb7b6221a81fc7c72a44722dbacfdda0c7da25c14a26` |
| `src/embedding/adaptive_refinement.py` | `4a1f9f00cf6424b52d10e6161ddc9f26556de9aff69bd145a8813f6b2ac4cbfd` |
| `configs/c4-decoder-continuation.json` | `3b3cefb90982c7b3b75b6a0fe8465b65cbc0fac1a100aa6eb0f242584b059d9e` |

## LONG delta review — 2026-09-27

Exact revised code: `31a87c157f907ac1d539ca271239c7bb99b0006a`, reviewed against
`868d27a69415f2c4a479ee81cab4591e7d0a56b5`. This addendum is the current narrow
component verdict; the earlier numerical counts/hashes describe the preserved
short-budget checkpoint, not the revised execution package.

No unresolved blocker found in this bounded delta. The algorithm arithmetic,
original anchor/start, source objective, step policies, stopping logic, callback
guards, full-arm-window reservation, final-gradient measurement and scientific
nonacceptance semantics are unchanged. The revised policy is still a prospective
finite-budget experiment, not an instruction to run until an optimum. The user's
conditional request for longer time does not authorize the prior 20-minute
manifest, this new manifest, indefinite execution, or restarts after early stops.

The typed component hard maxima are now 512 iterations, 4096 evaluations and
1800 seconds per optimizer; composition duration remains bounded at 3300 seconds.
Type/finite/range validation remains in place. The *fixed concrete recipe* is
narrower: each arm receives 512 iterations/backwards and 2049 optimizer decoder
evaluations, plus one actual final-state image/gradient evaluation and backward.
Thus the declared maxima are 2050 decoder-NFE and 513 backwards per arm; the
existing conservative root-decoder start ceiling becomes 4100. The 2049 control
ceiling equals `1 + 512*(1 gradient + 3 trials)`. Arm windows are 1500 seconds,
global composition 3060 seconds, including persistence/final diagnostics as
before. No unused time or evaluation allowance is transferred between arms.

Storage accounting is consistent: normal bound 4106 states = 2 shared + 2 starts
plus 4098 optimizer evaluations + 2 optimizer final states + 2 final-measurement
states. The 4112-state reserve is 202,441,984 bytes at the retained grid's 49,232
bytes per file, below the 256-MiB quota. Journal quota rises to 32 MiB while its
failure reserve and exclusive persistence behavior remain. Torch VRAM stays at
9216 MiB. The launcher declarations consistently become Linux 3540 seconds plus
10-second TERM grace, parent 3590 seconds and official 3600 seconds. Exact
manifest/isolated-checkout validation and resource approval remain with the
separate package review; this component review does not confer them.

Reproduced the same four-module owned CPU suite on `31a87c1`: 48 tests, 47 passed,
one expected Windows-only launcher skip. Independently checked 19 invalid typed
boundary cases, including above-cap integers, Boolean values, nonfinite duration
and excessive composition duration: all refused. An additional in-memory owned
synthetic decoder test used small fixed steps solely to exercise the enlarged
loop bounds: both arms completed exactly 512 updates, stopped with
`iteration_budget`, and reported 1025 optimizer evaluations, 1026 total decoder
evaluations and 513 backwards including final measurement. Adaptive reported
512 accepted updates. No UNet call or leaked decoder hook occurred. These
deliberately synthetic step settings are not the frozen scientific recipe and
provide no learned-model result. No author source/test files were edited.

More time does not bypass the unchanged MSE `0.0003`, gradient `1e-12`, radius or
line-search stops, and does not establish global optimality or joint saved-PNG
quality. New runtime/memory fit remains unproved. Preserve every early stop and
failed/incomplete comparison; report both arms and common-NFE/actual work without
winner selection. All prior scientific scope limitations continue to apply.

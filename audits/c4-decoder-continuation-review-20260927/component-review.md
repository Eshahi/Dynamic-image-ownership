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

# C4 inverse stability: diagnosis and versioned numerical candidate

Issue #18 / draft PR #67. Author /root, 2026-09-27. Apply
[research contract](research-contract.md), [scope guard](scope-guard.md) and
[approval policy](approval-policy.md). Original proposal, configurations, targets,
negative evidence, native2K and all6900-source obligations remain unchanged.
This document and ordinary component tests authorize no scientific execution.

## Separate two problems

The retained run `c4-refined-target-dev-001` failed with two missing inverse PNGs;
its approval is consumed. Four rendered arms and every partial/failure cell remain
in [the report](../reports/dev/c4-refined-target-dev-001/result.md).
Direct refinement improved PSNR22.482789 to25.567447dB and SSIM.742910 to.807923,
but worsened LPIPS.058493 to.075412. The direct endpoint still fails PSNR>35 and
SSIM>.9; LPIPS<.1 alone is not acceptance. More than8.775-fold further MSE reduction
is required to reach35dB. Exact inversion of this frozen target cannot repair that
endpoint. This is not a ceiling over all decoder latents or alternative methods.

The two inverse paths failed later, before complete replay. Read-only scalar
diagnosis uses the actual retained journal, worker report and runner record,
bound to canonical manifest
`78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683`.
`scripts/analyze_c4_inverse_trace.py` neither loads tensors/images/models nor
recomputes metrics. It rejects malformed/stale/unfinished metadata and records
input byte hashes; it does not replace the earlier full custody review.

| Target / pair | NFE | First / minimum / last max residual | Minimum evaluation |
| --- | ---: | --- | ---: |
| Encoded / t1 | 7 | .02239698 / .0000071004 / .0000071004 | 7 |
| Refined / t1 | 7 | .03030276 / .0000058413 / .0000058413 | 7 |
| Encoded / t101 | 32 | .82401097 / .20169759 / .29868770 | 4 |
| Refined / t101 | 32 | .78606713 / .10542405 / .15412617 | 14 |

Encoded/refined t101 max residual increased21/12 times; the L1 objective increased
9/9 times. Last/best residual ratios1.480869/1.461964 describe these traces, not
an accepted best-state substitution. No signed residual vectors were retained
at every evaluation; oscillation, Jacobian spectrum and root existence are not
established. A larger GPU or arbitrary larger iteration budget is not a demonstrated
repair. The last run had no OOM; full method/native2K fit remains unmeasured.

## Equation and literature-guided choice

For the unchanged eta0 epsilon-prediction/no-clipping DDIM pair,

    D(x)=a*x+b*epsilon(x), a=sqrt(alpha_previous/alpha)
    b=sqrt(1-alpha_previous)-a*sqrt(1-alpha)
    G(x)=(target-b*epsilon(x))/a
    R(x)=D(x)-target=a*(x-G(x)).

No algebraic defect was identified by the independent Astra reviewer. The
unit-damped historical Picard iteration may be unstable, but no learned Jacobian
was measured. Underrelaxation changes eigenvalues to1-lambda+lambda*mu: it can
stabilize some negative slopes, not a positive real mu>1. Averages cannot be
treated as nonlinear roots without evaluating the true residual.

Primary evidence is recorded in
[inspection notes](literature/inverse-stability-20260927/inspection.md) and the
validated literature response/synthesis. AIDI motivates Anderson acceleration
for DDIM roots; ReNoise supplies an averaging comparator but no unconditional
divergence cure. PreciseInv's inspected NeurIPS2025 abstract motivates a secondary
test-time optimization route, not a ready reproduced implementation.

The independent **gpt-6-astra / xhigh** route review ranked safeguarded Anderson
first, pure residual trust-region optimization second, same-final-equation
coefficient continuation as a contingency. This is an actual separate reviewer,
not a claimed switch of the parent conversation. See
[review](../audits/astra-inverse-route-review-20260927/review.md).

EDICT's paired sampler, trained decoder/skip replacement, detector changes and
image bypass are different interventions. A denser schedule also changes the
forward composition unless used only as a warm start polished against the original
map. These must not silently replace the historical method or experiment.

## Implemented ordinary candidate, not a scientific package

`src/embedding/inverse_acceleration.py` independently implements the same pair
equation with short-history, constrained, regularized Anderson mixing. Call it
**AIDI-inspired safeguarded Anderson**, not AIDI reproduction. It leaves historical
`inversion.py`, the runner, execution checkout and all old configs untouched.

Candidate engineering defaults:32 evaluations,1e-5 max-residual tolerance,
history4, scale-normalized Gram ridge1e-8, condition limit1e10, coefficient-L1
limit20, RMS displacement limit2, fallback damping(1,.5,.25). These are transparent
ordinary API defaults, not paper-derived optimums or an approved scientific policy.
The short history limits tensor storage; only its <=8-square float64 system is
on CPU. There is no learned backward pass or dense latent Jacobian.

Every trial is evaluated against the real current nonlinear equation. Acceptance
requires convergence or strict RMS-residual decrease with nonincreasing max
residual. A rejected mixed or Picard point may enter the measured mixing history
but cannot become accepted output implicitly. This permits two-point information
even when positive-slope Picard fails. Rejected mixes force bounded fallback;
bad conditioning/coefficients/displacement are refused. Explicit budget or
safeguard-stagnation failure is valid; there is no convergence guarantee.

Every actual callback consumes NFE, including rejected trials. Returned states
are measured accepted states, with current residual/counters, never unmeasured
proposals or hidden best-of-history outputs. Failures in journal/observer callbacks
abort. An optional observer receives isolated state/residual clones for future
durable diagnostics. Target and callback inputs are isolated. The ordinary tests
use owned CPU equations only: no study pixels, weights, model/GPU or metrics.

## Next coherent package and falsifiable conclusion

Prepare two new inverse/replay attempts: exact retained encoded and refined
targets from run001, one identical frozen acceleration policy, original forward
path[101,1], reversed inverse[1,101], same model/config/source hashes. Do not refit
the latent, select a better source, alter endpoints or reuse old approval. Keep
historical Picard failures as nonconcurrent references, not fresh comparator runs.

The actual worker/helper/config/input closure, final clean manifest and full
independent review remain to be implemented. Freeze all engineering policy values
and account total pair/path/replay calls before asking one exact user question.
Proposed first budgets remain32 per pair/128 path; final replay reserve, timeout,
Torch allocator ceiling and persistence bytes must fit the concrete manifest.
Neither this design nor component success substitutes for that package.

Persist true max/RMS residuals, accepted/rejected decisions, actual call counts,
mixing weights/condition, step norms, successive residual cosine and lag2/lag4
differences, enough state/residual bytes for audit, and all failures. Directional
secant ratios are not global Lipschitz estimates. Null/missing dependent cells
remain missing rather than imputed.

Only after both pairs converge may the identical complete path replay be checked
against1e-5 and the native output decoded/saved under existing safety/quality
controls. Measure PNG PSNR/SSIM/LPIPS against source and its own frozen endpoint,
plus q/h drift, not blind detection. A success supports this solver on two
dependent targets of one source only; it does not establish35dB, quality repair,
population success, full native2K fit, watermark efficacy or C4/C5 completion.

If either target fails, record that this bounded acceleration did not resolve the
bottleneck; do not expand its budget or switch methods inside the package. The
next route is explicitly pure residual least-squares/trust-region, without the
GNRI-inspired distribution prior. Decoder/source-quality repair remains a separate
feasibility gate whether or not the numerical inverse succeeds. No paid GPU need,
new downloads, package installation or lifecycle decision is inferred.

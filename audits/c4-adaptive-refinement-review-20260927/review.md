# Independent adaptive-refinement component review

Reviewer `/root/astra_inverse_route_review` (gpt-6-astra/xhigh), independent of
author `/root`. Exact author commit
`e5bd48b7a967f3968b3e23a22fd0d2243bef1df5`, 2026-09-27, issue #18 / draft PR #67.
This bounded review concerns only the current reconstruction/inversion problem.
Apply AGENTS.md, the approval policy, research contract, scope guard and evidence
audit skill. Only this audit file is written. No model, study image, GPU, learned
metric, scientific execution, installation, download, approval or lifecycle action.

## Initial disposition

**One limited cooperative-deadline blocker; no projected-descent, anchor,
accepted-state, evaluation-count or gradient-provenance blocker identified.**
The objective-only engine explicitly does not claim model binding or a scientific
package. Existing frozen-decoder guards, complete worker and concrete resource
manifest are future composition work, not requirements to close this component
review. No new scientific defaults or image-quality acceptance are inferred.

## Blocking finding: final progress callback can bypass the deadline

In `src/embedding/adaptive_refinement.py:91-103`, `finish` checks the deadline
after final `save_state`, then calls `emit(row)` and returns without another
check. A slow final progress/persistence callback therefore permits a normal
return after the declared cooperative duration.

Independent deterministic reproduction: replace monotonic time by a controlled
clock initially0; set maximum_seconds=1; advance the clock to2 inside the
`adaptive_terminated` progress callback. With an initial objective within its
declared numeric tolerance, the function returns status `objective_tolerance`
normally at time2. No sleep, real scientific operation or machine-clock change
is needed. This contradicts the otherwise checked callback/deadline boundary.

Required narrow repair: check the deadline after the terminal progress callback
and before normal return, with an owned regression for this exact case. A final
record may already exist when a callback or subsequent deadline check fails;
the future caller must require normal return and its outer terminal report,
rather than treating the component's terminal journal event alone as success.
Do not weaken the timeout or fabricate a successful package.

## Independently verified numerical behavior

All10 existing owned CPU tests passed in the existing WSL interpreter
`/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python -B`.
This reviewer encountered no access denial and used no escalation, installation
or security change. The author's earlier E_ACCESSDENIED remains documented in
its plan; it is not recast as a successful test.

An additional16 owned weighted-quadratic cases independently checked four
anchor/start/target/radius configurations at evaluation caps2/3/7/30. They include
an active projection boundary and nonzero anchors. All passed:

- Every evaluated trial stayed within the original anchor ball; neither caller
  anchor nor current tensor changed, and the returned state matched the last
  accepted measured state.
- The independently calculated gradient dot(actual trial minus current) matched
  the recorded Armijo slope. Accepted values satisfied strict decrease and the
  actual projected-displacement sufficient-decrease condition.
- Objective callback count matched NFE and persisted evaluated-state count;
  backward/update counts matched their events, and all caps were respected.
- The returned objective agreed with the known analytic objective at the actual
  returned state, including budget and iteration terminations.

Reading confirms that the separate original anchor is cloned once and retained;
resuming from a refined state does not recenter its constraint. Trial projection
uses an inward rounding margin and rechecks the rounded radius. Step size starts
from the last accepted step, can shrink through the explicit halving depth and
minimum, and grows only after the declared pair of first-attempt acceptances.
Every evaluated trial, including a rejection, reaches the state sink before its
evaluated journal row; callback errors propagate. These checks do not establish
the efficacy of any future parameter choices on the actual decoder.

The gradient is measured at the current state. An accepted update clears
`gradient_at_returned_state_l2`, correctly preventing the old gradient from being
presented as stationarity at the new state. A zero/high-threshold gradient is
reported only as `gradient_tolerance`, and all terminal rows explicitly retain
scientific_acceptance=false. Objective-tolerance and budget stops are likewise
numeric outcomes, not native PNG quality, global optimality or decoder capacity.

At an active constraint boundary, a nonzero ordinary gradient and rejected
projected steps may end in `line_search_failed`. This is not a false stationary
claim; no projected-gradient/KKT certificate is promised. Reserving one trial
before a gradient can leave one unused evaluation at a small cap, which is an
explicit conservative accounting choice rather than an overrun.

## Scope and handoff

The design accurately keeps continuous source MSE distinct from saved-PNG
PSNR/SSIM/LPIPS and states that the25.57dB endpoint still fails the combined goals.
The fixed same-start control/candidate comparison and separate original anchor
are appropriate prospective distinctions. Real numerical improvement, image
quality, learned-decoder binding and resource fit remain untested here.

Resolve the single callback-deadline defect and review the exact repair; then this
ordinary numerical checkpoint can proceed to the separately bounded worker and
execution-package composition. Do not require a finished worker to accept this
component, or treat component acceptance as scientific execution authorization.

## Final narrow re-review: exact6daeb0b

Independently reviewed repair commit
`6daeb0b3377bbd9bed5c28d80637417843a534d7`. **The callback-deadline blocker is
resolved; no remaining blocker was found for this ordinary adaptive numerical
component.** This supersedes the initial disposition for the repaired version,
while retaining the original failure evidence above.

The exact code change adds a guard immediately after final progress emission.
All11 owned CPU tests pass independently in the existing WSL runtime, including
the new controlled-clock regression. Independently reran the original reviewer
probe with the nonzero starting state, objective_tolerance=1 and maximum_seconds=1:
advancing the clock to2 in the final progress callback now raises the expected
cooperative-time-limit exception instead of returning an AdaptiveResult. The
already emitted terminal row remains evidence of the attempted finish, correctly
not evidence of normal return. The prospective caller requirement is now explicit
in the repair plan.

The repaired component SHA-256 is
`4a1f9f00cf6424b52d10e6161ddc9f26556de9aff69bd145a8813f6b2ac4cbfd`.
The descent/projection logic is unchanged, so the16 independently checked
weighted-quadratic Armijo, anchor and accounting cases remain applicable. This
bounded disposition permits the ordinary component checkpoint to proceed; it
does not certify future model binding, decoded image quality, stationarity of
the retained image, resource fit, a full worker, scientific compute or C4 closure.
Only this audit was written, with no permission workaround or scientific action.

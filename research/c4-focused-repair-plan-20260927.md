# Exclusive C4 reconstruction repair focus

Actual user direction, 2026-09-27: stop every other task and focus on solving the
current problem before returning to the rest. This changes priority, not original
claims, targets, data obligations or consumed scientific execution approvals.
Author /root. Issue #18 / draft PR #67. Apply the research contract, scope guard
and approval policy. Existing heartbeat was updated with this instruction and
the saved prompt was verified. No unrelated writer is active in this agent tree.

## Evidence that changes the next decision

Independent `/root/astra_method_feasibility` read the actual retained journal
SHA256 `11fba38f0263db064fef5e9be6d711307496717fc83a695bdeaf44ee9193a8aa`,
code and config after run `c4-refined-target-dev-001`. It returned these observations
in the authenticated task; it wrote no author files and ran no model or image metric:

- All64 iterations accepted an improvement. The stop was the iteration cap.
- Displacement14.44 was below the original radius80;150/257 evaluations and
  approximately114/720 seconds were used in the refinement stage.
- Iterations1--51 accepted normalized step1. Iterations52--56 rejected1 and
  accepted.5. Iterations57--64 rejected1 and.5, accepting.25 every time.
- The implementation restarts at1 each iteration and permits only two halvings.
  It never tries a step below.25 with this configuration.
- The final pre-update gradient norm was approximately8.10e-5, far above the
  1e-12 zero-gradient cutoff. The gradient at the final updated point is unmeasured.
- Progress slowed: last16 updates reduced MSE about3.79%, last8 about1.17%.

These are trace observations, not a decoder-capacity bound. A coarse, repeatedly
restarted search is a plausible contributor. Scalar logs cannot establish gradient
oscillation, final stationarity, root existence or a globally optimal latent.
Native PNG25.567447dB/.807923/.075412 still fails combined source targets, and the
remaining MSE gap to35dB is about8.775-fold. No extrapolation to35dB is justified.

## Next scientific question: optimizer limitation versus inadequate local route

Prioritize one bounded decoder-fidelity comparison before enlarging the inverse
experiment. Start BOTH arms from the exact retained final refined latent and
keep the same frozen decoder, source, preprocessing and source-MSE objective.

1. Same-start continuation with the original normalized-step policy is the control
   for additional optimization effort.
2. Same-start continuation with a warm-started step and deeper sufficient-decrease
   backtracking is the candidate. It must be able to try steps below.25.

The **constraint centre remains the original encoded latent E(I)**, radius80.
Passing the refined latent as the existing API's `initial_latent` would silently
recenter the constraint and is not an acceptable implementation of this comparison.
Keep current state and constraint anchor separate in the new versioned API.

The new ordinary `src/embedding/adaptive_refinement.py` implements that numerical
API: separate current/anchor tensors, normalized descent, warm-started step,
Armijo sufficient decrease using the actual projected displacement, deeper
halving, and bounded cautious step growth after two first-attempt acceptances.
Every parameter is explicit; no new scientific default is selected by this API.
All trials, rejections, backward counts and measured states are exposed to caller
persistence. The final-gradient field is null after an accepted update until a
gradient is actually measured at that new state. The fixed radius is checked
after rounded float32 projection. Model binding and the concrete worker remain
to be composed and reviewed; this callable is not an execution package.

Ten owned CPU unit tests passed in the existing WSL environment: small-step
recovery on a quadratic, original-anchor retention, no false stationary-gradient
claim, budget/persistence behavior and invalid objective/profile refusal. The
first restricted-shell WSL attempt failed with E_ACCESSDENIED before tests; the
authorized tool escalation ran those CPU tests successfully. No scientific run,
GPU, model, installation or security change occurred. Exact new component review
is pending; these tests do not establish a quality gain on the retained image.

Freeze iteration/NFE/backward/recomputation/time/allocator/storage budgets,
line-search constants, trial persistence, exact start/anchor hashes and stopping
rules in the complete worker/package before one execution decision. Do not choose
them from a new learned-model run. Record any final gradient evaluation explicitly;
do not mislabel the preceding gradient as stationarity at the returned state.
Quality is native saved-PNG PSNR/SSIM/LPIPS versus the same source, with diagnostic
q/h drift. MSE improvement alone is insufficient; LPIPS already worsened once.

Interpretation is prospective and falsifiable: renewed substantial descent would
support an optimizer limitation; a reproducible local plateau with a small measured
gradient and no active resource/radius boundary would motivate a concrete
source-detail-preserving reconstruction amendment. Another artificial budget stop
is inconclusive about decoder capacity. Even a stationary high-loss point is a
local-route failure, not proof that all decoder latents are inadequate.

## Numerical inverse work remains within this same problem

Independent `/root/astra_inverse_route_review`, confirmed gpt-6-astra/xhigh,
inspected the same-equation safeguarded-Anderson candidate at931b2ec. Its existing
24 tests and33 additional owned CPU checks found no solver correctness/accounting
blocker. A known-root nonnormal affine fixture still stalls under the defaults;
safeguards can refuse a solvable problem. This is a software limitation, not
learned-model evidence. See its exact artifact review for reproduction details.

The retained-trace reader did have a blocking identity/event/status validation
defect. Repair binds the actual executed commit, CLI input byte hashes, observed
pair inventory/order and terminal tolerance/accounting;16 fixture tests and a
read-only replay of the real metadata pass. The initial defective reader and its
v1 output remain in history; no raw scientific result is rewritten.

Finish this independent re-review and keep the inverse component available.
Its full worker/clean execution manifest is not ready. Exact inverse of the frozen
25.57dB endpoint would only reproduce that endpoint, so inverse convergence must
not displace the source-fidelity question. No new model/data download, installation,
science execution, paid GPU, task closure or lifecycle transition occurred here.

All other thesis tasks are paused by the user's priority instruction. This includes
unrelated data, detector, evaluation/reporting and university-template work.

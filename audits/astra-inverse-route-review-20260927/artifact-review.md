# Independent inverse-acceleration artifact review

Reviewer: `/root/astra_inverse_route_review` (gpt-6-astra/xhigh), distinct from
author `/root`. Exact reviewed author commit:
`931b2ecbb36991b29a4dd455a2a722b74d730fe2`, 2026-09-27, issue #18 / draft PR #67.
Scope is solely reconstruction/inversion under the user's latest priority.
Apply AGENTS.md, research/approval-policy.md, research/research-contract.md,
research/scope-guard.md and the independent evidence-audit skill. Only this
review file is written; no model, study image, GPU, learned metric, scientific
execution, installation, download, runner action or lifecycle transition occurs.

## Disposition at the reviewed commit

**One blocking metadata-validation finding remains. No numerical-solver
correctness or accepted-state/NFE blocker was found in the inspected component.**
The literature and design correctly label engineering defaults, selected-section
inspection, dependent targets, missing replay and unresolved decoder quality.
This is not acceptance of learned-model behavior or permission to execute.

The worker, path adapter, exact config/manifest, resource guards and full durable
diagnostics are deliberately not implemented in this commit. They are outstanding
package work, not defects in a component that explicitly does not claim them.

## Blocking finding: retained-trace validation overclaims its binding

`scripts/analyze_c4_inverse_trace.py:27-95` names a single exact historic run and
manifest, but `diagnose` checks only equality of the two `git_commit` fields.
Both missing fields compare equal; two unrelated matching commits also pass.
Separately filtering start/evaluated/terminated rows fails to establish causal
event order or reject extra evaluations at another timestep. Finally, `converged`
and `evaluation_budget` are copied without checking the actual fixed policy's
residual criterion and evaluation ceiling.

Five independent owned-fixture probes were accepted at this exact commit:

| Invalid specimen | Observed result |
| --- | --- |
| Remove git_commit from both worker and runner metadata | Accepted. |
| Set both commits to an unrelated forty-character hash | Accepted. |
| Put evaluated before its evaluation_started, preserving monotonic timestamps | Accepted. |
| Insert an evaluated row at t202 under a known inverse arm | Silently omitted; accepted. |
| t1 status converged with final max residual .01 | Reported converged despite the fixed1e-5 criterion. |

The current synthetic fixture additionally uses2/3 evaluations while the exact
retained run has7/32. A generic descriptive core can support flexible fixture
lengths, but then a distinct exact-run validator must bind that core before the
CLI labels its output as this execution. The output's scientific_acceptance=false
does not repair a misleading provenance or convergence assertion.

Repair before accepting this metadata artifact: require the actual executed
commit `dd347afb861774f7a86138e7170dba96d4f47044`, required header types, exact
applicable policy/inventory, ordered pair/evaluation/termination/path events and
status-to-residual/count consistency. Reject unexpected inverse timesteps,
duplicate/missing/crossed events and mismatched actual-call/path totals. Add the
five refusal regressions above, plus explicit policy/count mismatches. Byte hashes
record identity of supplied inputs; preserve the distinction between that and the
earlier full custody audit. Do not modify the historical run or invent outputs.

This finding does not assert that the authentic retained journal is corrupt.
Its transcribed numeric trajectory agrees with the independent previous review;
the flaw is that the new validator also accepts materially different specimens.

## Numerical/component verification

Independently ran all24 existing tests (13 acceleration,11 trace) with the existing
WSL interpreter `/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python -B`;
all passed with no skipped tests. No package installation or CUDA operation.

An additional33 owned CPU cases covered constant/duplicate, nonlinear,
positive-unstable, no-root and nonnormal vector maps across evaluation caps
1/2/3/7/16/32, plus conditioning/coefficient/displacement refusals. Independently
checked callback count equals reported NFE, decisions equal NFE minus the initial
evaluation, accepted+rejected counts agree, returned state is exactly the latest
accepted measured state, reported max/RMS match its observed residual, and success
occurs only at the max-residual tolerance. All checks passed.

The code solves the original DDIM pair equation. Its regularized constrained
mixing weights are applied to G(x_i); every candidate's actual nonlinear residual
is measured. Rejected states may inform history without becoming accepted state,
which is explicitly documented and tested. Finite checks, coefficient-L1 bound,
step bound and a finite fallback grid limit proposals. Observer clones isolate
mutations, and observer/journal exceptions propagate. No backward call or hidden
best-of-history success appears in this component.

Nonblocking limitation demonstrated independently: for

    G(x) = r + [[0.7, 4.0], [0.0, 0.7]] (x-r), r=(0.1,-0.2),

replicated into the supported tensor shape, the default safeguards honestly stop
after7 evaluations at max residual .347645998 with safeguard_stagnation. This map
has a known unique root and stable eigenvalues. Thus the combined RMS/max
monotonicity, displacement and fallback choices can stall on a solvable system.
Keep this example as a regression/limitation; do not interpret a future refused
learned-model trajectory as root nonexistence or universal AA failure. No tuning
of scientific parameters was performed from this synthetic outcome.

The regularized Gram condition number is not a certificate of nonlinear
contraction or independent history. Regularization intentionally permits rank
deficiency. Default constants are engineering choices, as the design correctly
states; they must be prospectively frozen with rationale before a scientific
package, and should not be described as literature-optimal values.

## Evidence and literature assessment

Independently hash-checked the inspection notes and both retained primary HTML
snapshots; all agree with their declared identities. The response, three cards,
ledger, matrix, synthesis, gaps and bibliography preserve the same bounded claims.
The parent's official helper validate/synthesize success was not represented as
an independently rerun entailment proof.

Now independently inspected AIDI v1 sections3.1--3.2/Algorithm1: residual-history
mixing is directly relevant, but the implemented safeguards and default history
are modifications. ReNoise's averaging argument assumes a convergent underlying
sequence. PreciseInv's official abstract verifies metadata/DOI and motivates a
separate recursive test-time optimization approach; its proofs, parameters and
implementation remain uninspected. No local fidelity guarantee follows.
[AIDI v1](https://arxiv.org/html/2309.04907v1),
[ReNoise v1](https://arxiv.org/html/2403.14602v1),
[PreciseInv proceedings abstract](https://proceedings.neurips.cc/paper_files/paper/2025/hash/2e4bc9f6e31aa27861299940aa5242ad-Abstract-Conference.html).

Reviewed component SHA-256:
`b6b294c9006c41615ec461a86f3d6d74ae2897693e297982240f528036910d90`.
Analyzer SHA-256:
`aeaa99b9e0e070f3f667a25bb4f3c8e198faf70369524bae1cef14e25b0f1555`.
Design SHA-256:
`764ce234cfdc54f341d4bbb9f452cd34d845eb5658634fc37e42474e6533faab`.

## Is the proposed pilot informative?

Yes, as a bounded numerical mechanism test: the same solver and original path
applied to both already frozen targets isolates a solver change without selecting
a favorable source or repeating/refitting the decoder. Historical Picard traces
must stay explicitly nonconcurrent references. A failure remains informative only
with complete accepted/rejected trajectories and reason-specific termination;
the nonnormal example explains why safeguard failure alone is inconclusive.

It is not a complete reconstruction repair. Even perfect replay preserves the
refined endpoint's25.57dB/.808 SSIM, which still fails source quality and has worse
LPIPS than the VAE anchor. Keep source-quality objective/decoder feasibility as a
separate reconstruction workstream within the user's current focus. The pilot
does not justify buying a GPU, lowering targets, closing C4/C5, or replacing the
detector. A subsequent pure-residual trust-region method or same-equation
continuation is a contingent design, not an undeclared fallback in this package.

After the metadata blocker is repaired, a new exact review can accept this
ordinary component/documentary checkpoint. The complete scientific package still
requires its own exact review and actual runner-bound user execution decision.

## Additive repair review: exact37260b9

Independently re-reviewed author commit
`37260b909ace601f97fda408f927825e7f59242c` on2026-09-27. **The narrow metadata
blocker above is resolved; no remaining blocker to this ordinary component and
documentary checkpoint was found.** This supersedes the initial disposition only
for the repaired version. It grants no scientific/learned-model acceptance,
execution approval, C4 closure or lifecycle verdict.

The CLI now requires the three exact historical raw byte digests before diagnosis
or output creation. Independently rehashed the actual retained journal, worker
report and runner record; all match RAW_HASHES and the previously reviewed
custody identities. The validator separately pins executed commitdd347afb, the
observed7/32 evaluation inventory, ordered pair starts/evaluations/terminations,
only timesteps1/101, path39-call/zero-backward accounting and1e-5 terminal semantics.
Direct `diagnose` is a structured validation/description core; the CLI's byte
binding is the stronger exact-input boundary. It is not a general authenticity
validator for new arbitrary executions.

All16 owned trace tests independently pass in the existing WSL interpreter with
`-B`. Nine additional independent refusal probes pass: each of the three changed
raw digests is rejected before `diagnose` is reached, and missing/unrelated
commits, false convergence, an extra timestep, reversed start/evaluated order and
changed observed counts are rejected. The mocked CLI probes performed no file
writes. No actual learned-model or metric computation was repeated.

Repaired analyzer SHA-256:
`f9f72e25f6b0fc2aedb1f7bca6375c8d87a2b487623615026c2b60f3d22dc9dd`.
The acceleration solver is unchanged: its Git diff is empty and its byte digest
still equals `b6b294c9006c41615ec461a86f3d6d74ae2897693e297982240f528036910d90`.
The earlier numerical verification and nonnormal-map limitation therefore remain
the relevant bounded component findings; they were not erased by metadata repair.

Read the new focused repair plan. Prioritizing a same-start decoder-fidelity
comparison is appropriate to the remaining source-quality question; the existing
two-target inverse diagnostic remains a useful numerical experiment when needed.
Keeping the original encoded-latent constraint centre separate from the continued
refined starting state avoids silently enlarging/recentering the feasible set.
The plan labels the other independent reviewer's trajectory observations as such;
this narrow re-review did not independently rederive those decoder-gradient
observations or accept a new optimizer implementation. Its control/candidate,
unchanged quality criteria and no-decoder-capacity-proof caveats are appropriate.

The unfinished worker/path integration and future exact scientific package remain
explicit prospective work. They are not prerequisites for accepting this repaired
ordinary checkpoint. No filesystem permission limitation was encountered, and
only this additive audit section was written by the reviewer.

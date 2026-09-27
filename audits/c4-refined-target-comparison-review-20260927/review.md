# Independent refined-target composition review

Reviewer: `/root/b3_intake_review`; author: `/root`.
Reviewed exact author commit: `43331bca48396c0117a67cb1ce84e16432e346fa`.
Authority: AGENTS.md and research/approval-policy.md technical-review delegation.
This is bounded software/design acceptance, not scientific results acceptance,
compute authorization, lifecycle advancement or issue #18 closure.

## Artifacts and actual checks

Read src/embedding/refinement_comparison.py, its owned test suite and
research/c4-refined-target-comparison-component-20260927.md, with the previously
reviewed refinement/path/checkpoint dependencies. Applied the evidence-audit
skill's claim/scope separation; no full-thesis audit verdict is implied.

Ran existing WSL clean science Python at
`/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python` with
`-m unittest scripts.test_c4_refinement_comparison scripts.test_c4_latent_refinement -v`:
35 owned CPU tests passed, zero skips/failures. No learned weights, real study
pixels, model inference, GPU, network, downloads or installation were involved.

The checks cover one encode, all six fixed arms, native output shape, separate
original/refined inverse targets, historical-control exact owned-fixture parity,
checkpoint trajectory and recomputation accounting, inverse nonconvergence and
roundtrip failure without rendering/fallback, labeled budget-stopped refinement,
rounded-radius refusal, persistence failures, profile/method-owner drift,
callback mutation isolation and slow last-save timeout refusal.

Additional independent in-memory owned probes verified that save_arm mutation
of its image and metadata cannot modify returned outcomes or the distinct refined
target. A slow terminal journal callback was also tested: advancing a mocked
clock beyond the outer deadline caused an exception and a final time-limit row;
no completed return was produced, and both temporary model hooks were removed.

## Blocking findings

None within the declared component scope at this exact commit.

The refined inverse selects the persisted refined terminal latent, not the
original encoding (lines 171 onward). Failed inverses retain state/status and
do not decode or substitute another target (lines 187–195). Callback arguments
are isolated copies; method owners/functions and frozen profiles are checked;
inner budgets are limited by the outer remaining time. Last image persistence
is checked before an arm is marked saved.

## Nonblocking warning and required future interpretation

`event` checks the deadline after the caller's journal callback (lines 109–113).
Consequently a slow terminal callback can persist
`refinement_comparison_terminated`, followed by
`refinement_comparison_time_limit`, before the component raises. This correctly
refuses a completed return, but a future persisted-artifact reader must not
infer completion merely from a terminal-named journal row. Require normal return
and the final consistent worker report; a later timeout/error must override an
earlier terminal-named event. No such future worker/reader is accepted here.

Hard rounded-radius refusal remains an explicit numerical failure policy, not
evidence that refinement is feasible for the real profile. Root decoder/UNet
starts and backward/recomputation counts do not establish full FLOPs, resource
fit or learned-model parity. Caller persistence is a contract; this in-memory
composition does not itself establish disk durability or asset authenticity.

## Preserved failures and limits

The author-reported initial test incorrectly expected per-inverse budget 2 to
fail policy construction; it is structurally valid but fails this fixture's
two-step replay preflight. The corrected test passed independently. Preserve
that original test failure rather than treating it as a skip. Previous refinement
projection/deadline and detached-decoder findings remain historical evidence.

No scientific policy/config, complete worker, asset/environment closure, saved
PNG metrics/safety/key study, exact execution manifest or new actual approval was
reviewed or created. All earlier scientific approvals remain consumed. Synthetic
descent/parity is not source-quality repair, GNRI/REED reproduction, watermark
efficacy, ownership certification or population evidence. C4 remains open and
C5 dependent.

Disposition: no narrow software/design blocker; component acceptance supported
with the preceding explicit limitations and future-consumer warning.

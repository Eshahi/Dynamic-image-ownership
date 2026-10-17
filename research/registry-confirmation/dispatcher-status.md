# Registry development rehearsal dispatcher

Implemented in the existing dispatcher source and its compute-runner runtime bundle. No launcher, approval file, or schema was added.

The `dispatch --development-rehearsal` flag admits only local USD-0 manifests whose nonempty dataset list is entirely `development`, reviewed entry is exactly `scripts/m1b_coco512_worker.py`, and sole hash-bound `*.m1b-plan.json` declares `registry-two-factor-v1` with `data_split=development`. The plan's source index and the registry runtime validator must also be hash-bound manifest inputs. The dispatcher loads that checkout's validator and calls `validate_plan(plan, repo)` before launching. The runtime's independent locked-cohort membership checks remain authoritative for individual sources.

The exception preserves the existing script hash, input hash, exact clean commit, tracked entry, resource and artifact checks. The current Python interpreter still launches the worker, so invoke the official runner through the science virtual environment for real rehearsals. Without this flag, execution still requires exact matching human approval; test and rehearsal split manifests cannot use this exception. A human approval argument cannot be combined with the flag.

Run evidence has `approval_reference: null`. A separate `rehearsal-context.json` records the development scope, plan and index hashes, USD-0 limit and the brief's clarification as the authorization source. It contains no approval decision. The unchanged run schema remains valid.

Local execution also accepts `--resume-incomplete`. This reopens only the exact artifact directory with an identical stored execution manifest and an incomplete prior run. A held OS file lock prevents concurrent dispatchers; persisted child PID state prevents resuming while an orphaned worker still runs. Unknown child launch state fails closed. Windows liveness uses process-query APIs rather than signals. Before replacement, prior run manifests, dispatcher state, process logs and summaries are copied into numbered `attempts/attempt-NNN` directories. Existing contracts, execution manifest, scientific outputs and journal are preserved. The worker resumes its own journal. Missing endpoints keep the resumed run failed; they are never fabricated. Approval checks remain unchanged for normal/test execution and are rechecked on every resume.

Verification (2026-10-17):

- `test_registry_dispatch.py`: 21 tests passed, including real local CPU subprocesses, successful journal-preserving continuation, numbered failed continuations, active child/concurrent dispatcher rejection and exact-manifest binding. No image was read or created.
- `test_forward_compute.py`: all 14 existing tests passed, preserving approval, provider and recovery behavior.
- `test_contracts.py`: all 15 existing contract tests passed, including bundle validation and a default approved local fixture.
- Source and compute-runner bundle are byte-identical; `git diff --check` passed.

The focused tests use a synthetic metadata validator to exercise dispatcher boundaries and delegation to source membership validation. Full scientific-worker validation and GPU rehearsal belong to the package integration tests; these dispatcher tests do not claim pipeline rehearsal success.

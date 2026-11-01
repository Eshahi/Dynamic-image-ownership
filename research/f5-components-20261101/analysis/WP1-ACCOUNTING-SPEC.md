# WP1 saved-development accounting specification

JUDGMENT: This is exploratory accounting of previously observed results, not a preregistered new experiment or a search for a favorable reader. Written before the root's data aggregation. Governing source: ../BRIEF.md section 4 WP1.

## Inputs and boundaries

SOURCE: Read only declared JSON/JSONL development artifacts from MAIN .thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a, 20261025-0128-encoder-transfer-stage2b, 20261026-0705-et-final-pilot, 20261026-0855-et-final-phase-a and 20261030-regen-channel, plus earlier development reports as needed. Never glob their parent dev-runs directory. Phase B journals/xfer and every held-out folder are excluded. Committed reports are SOURCE evidence, not newly measured data.

## Accounting rules

JUDGMENT: Inspect each journal schema before specifying its adapter. Inventory statuses, duplicate attempts, detector availability, channel, strength, seed and source identities. Retain unsuccessful attempts in coverage statistics. Use the study's declared terminal/union policy with disagreement checks; do not silently pool duplicate runs or independent studies.

DERIVED: Each expected marked self-owner detection occupies exactly one operational bucket: frozen C; decoded but content failed (B); recomputed-only detection (U); neither threshold passed (L); unavailable (M). L means neither frozen test passed, not zero physical information. A=found, B_read=read, C=read-and-content; J must be reported from the saved endpoint if available, without substituting a new endpoint.

DERIVED: Source majority is at least two successes in a fixed three-seed cell. Incomplete calls count unsuccessful in the primary lower count; separately give best-case missingness bounds. Clean one-image cells use one success. Other seed counts use their declared endpoint rule and are kept distinct. Never divide by observed-only sources to hide missing cases.

DERIVED: Fixed-reader content-only oracle = number of sources with a majority of decoded calls (C+B). Frozen-found oracle = majority of (C+B+U). The latter assumes any found call could be converted to the desired endpoint and is not an unrestricted upper bound for recoding, threshold changes, carrier changes or learned readers. Component effects overlap; do not sum their ceilings. Unobserved writer interventions have UNKNOWN nontrivial ceilings, with only the trivial remaining-source bound available.

JUDGMENT: Reproduce judge tables against judge/loss-budget.json and reader-ball.json read-only. Any content-ball counts remain new, exploratory endpoints; no selection among radii. Verify exact relation to frozen C and missingness. Extend to available negatives where saved scores permit a descriptive check, without claiming T4/T5 safety from unrelated C0/wrong-owner calls.

JUDGMENT: No bootstrap, p-values, performance forecast, or tuning on frozen reports. Time every local invocation, use stdlib interpreter -I and one process, save command/code commit/input provenance/output summaries below RD. Abort on schema failures, contradictory terminal rows or elapsed budget approaching 600 seconds.

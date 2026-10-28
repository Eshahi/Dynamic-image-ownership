# Stage S handoff — INCOMPLETE, DO NOT RUN

2026-10-28 partial-session snapshot. This is a completion checklist, not the server-ready runbook required by WP4. No setup or launch command is certified. `READINESS.json` blocks both scientific entrypoints before any torch import.

## Required work before renting or launching

1. Write `05-stage-s-protocol.md` and reconcile it with `frozen-config.json`, `source-manifest.json`, the selected rule and every producer/reader endpoint. Write `06-stage-c-design.md`; keep Stage C execution separately gated.
2. Implement a read-only Journal path compatible with producer/reader calls. Preserve latest-row semantics; a concurrent reader must not truncate or repair an active producer's journal. Verify crash, torn-row, resume and missingness behavior with pure-logic tests.
3. Complete pinned server setup and `scripts/tifs_stage_s_driver.sh`. Audit all retained adapter signatures, payload fields, hashing, canonical source paths, C0 replay and shard inventory. Release GPU objects between families; do not presume GPU concurrency fits 24 GB.
4. Implement rehearsal timing aggregation and the frozen full-inventory forecast/launch seal, including paid setup/rehearsal/idle time and the one-hour retrieval reserve. Exit 3 denotes resource stop; exit 4 currently denotes incomplete scientific inventory. The driver must preserve missing/safety/error outcomes without calling them negatives or silently skipping them.
5. Implement analysis applying every frozen C/J, clean quality, relative distortion, C0/wrong-owner and T4/T5 condition. Produce tables/JSON with denominators and lower/upper missing-outcome bounds. Keep the eight standard distortions in their separate secondary family.
6. Compile every new Python file and finish all meaningful pure-logic tests. Prior syntax checks do not validate runtime behavior. The common-helper filesystem tests were not fully verified in this session.
7. Obtain the fresh WP5 independent review of the complete protocol/code diff; record real findings and dispositions in `07-review.md`. No such review has occurred. Commit corrections before changing READINESS to COMPLETE.

## First later server action

After completion and a later authorized server session, run only the specified two-source rehearsal first. Verify gradient/projection parity, codec/native timestep and scaling agreement, saved-PNG reads, all arms and all native families, safety bookkeeping, output hashes, T4/T5, secondary distortions, 24 GB memory and complete-inventory runtime. A failed implementation check stops launch. Do not alter scientific thresholds to pass rehearsal.

The future full screen has 16 development donors, three seeds, four native cells and eight arms, plus clean, threats and secondary inventories. Rehearsal and full screen use different output folders but share the actual instance-start timestamp and the 15-hour paid ceiling. The required output collection includes code/config/source identities, every journal and shard, incomplete/resource-stop records, hashed producer inventory, forecasts, analysis tables/JSON and all outputs needed for provenance. Retrieval and stopping the rented instance must fit the reserved time; never destroy the instance on the user's behalf.

See `../FINAL-REPORT.md` for the proposed gates, budget arithmetic, scientific limitations and missing Stage C manifest. No metadata selection, scientific run, model download, package installation or rental was performed during this session.

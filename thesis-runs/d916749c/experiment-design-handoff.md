# Experiment-design handoff

Date: 2026-09-23 UTC. Run: `d916749c`. Stage: experiment design / A4 readiness. No external mutation or spending occurred.

## Outcome

The available evidence supports a bounded prospective design for `a5-latent-dct-feasibility`, but not a completed preregistration or executable compute manifest. The package is under `experiments/a5-latent-dct-feasibility/` and intentionally records `BLOCKED_PREREGISTRATION` / `BLOCKED_NOT_EXECUTABLE`.

The block is substantive: A5 `research/method-spec.md` and `configs/method.schema.json` are absent; no scientific Python entrypoint, dataset release/split/license manifests, seed inventory, frozen primary endpoint, target FPR, practical margin or independent sample-size calculation exists. Repository inspection found no scientific image/model/data/code artifacts. The existing evidence approval accepts literature for planning only and explicitly excludes feasibility, datasets, architecture, compute and scientific claims.

## Resource and budget boundary (partially measured)

GPU inspection observed an RTX 5070 Ti Laptop GPU with 12,227 MiB total and 11,499 MiB free; the safe planning cap remains 10,240 MiB. Disk inspection observed about 246,243 MiB free; the provisional reservation ceiling is 51,200 MiB. RAM inspection was denied, so availability is unknown and must be rechecked. Runtime cannot be estimated honestly before the workload exists. Approved remote/API spend is USD 0.00; no live quote was obtained. Local execution is only a conditional candidate after measurement. Live RunPod creation is currently blocked by the runner's reviewed deadline-enforcement limitation.

## Required next inputs

1. Complete and independently review A5's proposal-faithful method specification and final configuration schema, explicitly applying `research/scope-guard.md`.
2. Complete A4 acceptance criteria, sample-size analysis and stop rules against that fixed method.
3. Record immutable dataset identities, licenses, IDs, splits and deduplication, plus reviewed comparator revisions.
4. Implement and review a version-controlled Python entrypoint accepting exactly `--manifest` and `--output-dir`; create a clean commit and hashes.
5. Replace the blocked manifest and preliminary capacity envelope, run the design helper successfully, obtain independent manifest review, and only then request a concrete compute decision from the user.

The modified root `THESIS_GUIDE_OFFLINE.html` was treated as an existing user edit and was not changed.

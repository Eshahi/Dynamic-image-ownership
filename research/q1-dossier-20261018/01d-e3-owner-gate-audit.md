# Post-hoc E3 owner-gate count

18 October 2026, WP9 response analysis. This is a count of already saved Boolean detection results, using only the authorized stdlib interpreter. It is not a new detector call, descriptor score, threshold, experiment, ablation or confirmatory endpoint. No pixels or descriptor arrays were read. Machine-readable results: [01d-e3-owner-gate-counts.json](01d-e3-owner-gate-counts.json).

## Finding

Every completed beta native call in all eight E3 cells has `semantic.found=false` and `semantic.read=false`. Completed-call counts, in the ledger's EV-59–66 order, are **294, 294, 294, 293, 297, 297, 297, 297**. Each cell has 300 saved rows; the remaining calls are unavailable. No completed call lacks its semantic object. These completed-call counts coincide with the reviewed complete-case counts, but this audit selects completed beta calls directly rather than rerunning descriptor eligibility.

The frozen `native_q` function returns a decoded code only if both flags are true. Consequently, beta has no candidate in these observed queries before the code-distance and record-descriptor checks are reached. This is a deterministic implication of saved outputs and the source predicate, **not a newly evaluated owner-only arm**. It establishes that the measured E3 zero-beta result does not isolate any added wrong-owner rejection from q matching or D1+B1. The record check may still matter for alpha record correctness and distinct-content rejection; neither contribution is estimated by this Boolean count. No missing query is assigned a result, and no claim is made about active beta re-marking.

The E3 comparison remains a valid observation of two frozen pipelines under passive enrollment, subject to its approved complete-case and incomplete-bank qualifications. It is insufficient evidence of a synergistic pointer-plus-content defense or a causal contribution of all its components. A future component study must distinguish owner detection, q candidate gating and content verification, while reporting record correctness, owner correctness and abstention separately.

## Source and reproducible counting specification

Source: MAIN `.thesis-build/registry-package/artifacts/M1b-test/registry-div2k300-confirm-01/outputs/journal.jsonl`. Predicate source: this worktree `scripts/m1b_registry_analysis.py`, functions `native_q` and `attribution`, read as text only.

Parse each JSONL row and key it by `id`, retaining the last row if repeated, consistent with the analysis loader. For each model `sd15` / `sd21`, strength `0.2` / `0.4`, and scenario:

- Exact-copy beta rows begin `native:t3:<model>:` and end `:<strength>:15:C1:qim-pilot-owner-beta`.
- Further-regeneration beta rows begin `native:scenario:<model>:` and end `:<strength>:qim-pilot-owner-beta`.
- Count all matching rows, then rows with `outcome == completed`.
- Within completed rows, count the saved `detection.semantic.found`, `read`, and their conjunction. Check separately that no semantic object is missing.

All three Boolean counts are zero in each cell. Do not sum the eight completed counts into an independent sample size; they repeat source photographs. The JSON records unavailable source IDs for audit only. This finding is added as **EV-77, post-hoc retained-output count**, after the WP9 review snapshot.

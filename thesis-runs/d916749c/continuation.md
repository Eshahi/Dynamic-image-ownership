# Current continuation record

Updated 2026-09-23. Authority: `research/approval-policy.md`.

## Verified state

- A1 and A2a artifacts are merged in PRs #39 and #40; issues #1 and #2 are closed.
- A3 specification artifacts are complete and independently reviewed on branch `codex/3-io-threat-model`, linked to issue #3: `research/io-spec.md`, `research/notation.csv`, and `research/threat-model.md`. See `a3-review.md` for artifact hashes and acceptance limits; check GitHub for merge/issue state. Method implementation, scientific feasibility, and evidence review remain unaccepted.
- A3 is merged in PR #43 and issue #3 is closed. A2b artifacts are prepared and independently reviewed on `codex/4-research-contract`, linked to issue #4: all 42 claims covered by 81 route-specific planned rows, research contract and scope guard. See `a2b-review.md`; verify GitHub merge/closure before treating the task as integrated.
- Run `d916749c` passed `scope-acceptance` and is paused at `evidence-review`.
- The original `research-request` and `literature-synthesis` prompt invocations returned with `BLOCKED_INPUT`. Subsequent source checkpoints now exist (below), but do not interpret the CLI's completed prompt status as scientific task completion.
- The existing B1 request `d916749c-B1-001` was manually authored in a nested runtime; its task text contains encoding corruption and the helper was not executed there. Retain it as historical output, not as the current request.
- The main Windows task has a working Python virtual environment. The nested runtime's missing-Python observation does not describe this host. Use the explicit path in `AGENTS.md`.

## Next authorized work

Latest new source: `response-regeneration.json` and incremental `research/literature/regeneration/` add Zhao v3 with three source-specific evidence entries. Current corpus is eight distinct DOI cards / thirteen entries across method-checkpoint plus regeneration; earlier cumulative snapshots are historical subsets. Validator/synthesis pass without warnings for the new package; the earlier Kumari limitation remains. Regeneration threat and conditional bounds are now inspected, including qualifying defense results; no general impossibility or thesis advantage inferred. PROB-02/RQ-02/HYP-02/METRIC-05 relevance is recorded in the incremental README, pending namespace consolidation.

Next: finish SEAL revision/code preflight and inspect remaining qualifying-source lead as needed; then consolidate current evidence into root B1 outputs and whole-package review. Do not re-open source identities already audited. A5 may proceed independently with its exact method/feasibility specification under the scope guard. No compute or evidence-gate acceptance occurred.

## Historical checkpoints — superseded counts and next-step notes

The following checkpoint descriptions preserve earlier observations, not current corpus counts or competing execution instructions. Use the latest new-source paragraph above for current state.

Latest reconciliation: `research/claim-evidence-map.csv` covers all 42 original IDs/kinds with validated references to the existing ten B1 evidence IDs, or explicit no-admitted-mapping entries. `research/evidence-gap-assessment.md` prioritizes the DCT bridge, stable key recomputation, distinct comparator roles, and attack-access limits. No new source or experimental result was added in this checkpoint. Original claims and proposal unchanged. This closes an initial traceability gap, not B1 or the evidence gate.

Immediate next task is primary regeneration/contrary-source inspection and SEAL revision/code checks, then bounded evidence consolidation; avoid another mapping-only checkpoint. A5 remains a ready independent architecture branch requiring the scope guard and actual executable mechanism, not a placeholder. Current B1 corpus remains seven cards and ten evidence entries from response-methods.json.

Newest method checkpoint: `response-methods.json` and `research/literature/method-checkpoint/` contain seven cards (three targeted full-text, three abstract, one metadata-only). InvisMark v2 now has method/attack inspection and read-only upstream preflight at a pinned commit; see `research/baseline-readiness.md`. Its neural comparator role is separate from SEAL's inversion role. Checkpoint 100-bit/no-ECC versus paper 256-bit settings must not be conflated. A proxy-forgery paper is admitted at v1 only; no universal attack conclusion. Validation/synthesis pass with expected Kumari warning. B1 and evidence gate remain pending.

Next bounded work: reconcile source-to-original-claim support, qualify proposal literature narrative, inspect regeneration source and later forgery version, and finish SEAL revision/code preflight. Do not spend another checkpoint merely re-auditing the same citation identities. Consolidate the accumulated snapshots into required B1 outputs once coverage is sufficient, without duplicating versions or claiming completion from file presence. Only then request independent whole-package evidence review. Scientific compute still requires a concrete approved manifest; no such execution has occurred.

Latest B1 checkpoint: `response-citations.json` and `research/literature/proposal-citations/` now contain six cards (four abstract, one targeted full-text, one metadata-only). Validation and synthesis pass with the expected Kumari unverified warning; bibliography correctly omits that card. `research/citation-audit.csv` covers all six original references without modifying the proposal. Reference 1 incorrectly includes the academic editor as an author. Dasgupta's conference identity is matched via Crossref, but only its separate preprint abstract is inspected; no version equivalence is asserted. B1 remains incomplete and gate remains paused. Prior one-source checkpoint below is historical, not the current count.

Next: full-method inspection of candidate baselines and primary regeneration/forgery evidence, source claim mapping, Kumari abstract access, and SEAL proposal-era comparison. Root consolidated matrix/BibTeX remain absent intentionally until the expanded coverage is reconciled; citation audit existence is not task completion. No compute approval or execution.

B1 partial checkpoint: A2b is merged in PR #44 and issue #4 is closed. Issue #8 remains open. `research/literature-protocol.md` and `research/search-results.csv` establish a partial executed search. Corrected request B1-002 now has `response-seed.json`; the installed helper validates and synthesizes it successfully to `research/literature/seal-seed/`. Only one source is admitted. The initial validator rejected an unmarked inference assumption; the assumption was made explicit and both commands then passed. This is not B1 completion or evidence-gate acceptance. Official status remains paused at evidence-review.

Historical next-step note from the one-source checkpoint (superseded by the latest checkpoint above): six-reference cards and citation audit were then outstanding. Those initial records now exist; fuller source inspection and consolidated B1 matrix/BibTeX remain outstanding. The SEAL record pins v4 (2026-05-18), not the proposal-era version. Its inspected detector does not supply the missing image-domain DCT bridge. Resolve this scientifically without silently changing the method. No scientific compute has been run or approved. Pending search leads must not be cited as inspected evidence.

1. Corrected request `d916749c-B1-002` has been generated successfully with the installed helper and UTF-8 source task; `context.md` supplies scope/policy context. Its task payload matches the source plan exactly. Public-source research may be performed directly with available tools, with inspected artifacts and honest access labels. Perplexity is optional and no private upload is authorized by this policy.
2. After confirming A2b integration/issue #4 closure, prioritize B1 primary-source inspection to resolve architecture/baseline uncertainty, alongside ready A5 architecture work. Carry forward IO-01 through IO-07, attack budgets and SC-01 through SC-04. RQ-03 needs a neural-decoder comparator; HYP-03/METRIC-07 also need an inversion comparator. Evidence must justify any single method used to satisfy both. A5 must apply the scope guard in its method specification; no placeholder is an executable method.
3. Complete the real B1 search/source inspection and synthesis. Submit exact evidence to an independent reviewer; only then consider delegated `evidence-review` acceptance. Do not advance just to clear the UI gate.
4. Continue the task dependency graph and the scoped calendar. Ordinary review/implementation work proceeds under delegation; scientific execution still needs its manifest-specific compute approval.

## Historical records

An hourly heartbeat named `Continue thesis research` (ID `continue-thesis-research`) is active in the current Codex task. It advances ready work under the approval policy and reports meaningful milestones/decisions only. Its saved prompt includes the 2026-10-13 target and completion/deadline stop boundary. It is a wake-up mechanism, not another workflow state store.

`handoff.md`, `research-request-handoff.md`, `literature-synthesis-handoff.md`, and the initial artifact inventory retain their stage-time observations. This file records current continuation without rewriting those historical observations. Keep the immutable source plan and user-modified offline HTML intact.

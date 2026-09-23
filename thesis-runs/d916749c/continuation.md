# Current continuation record

Updated 2026-09-23. Authority: `research/approval-policy.md`.

## Verified state

- A1 and A2a artifacts are merged in PRs #39 and #40; issues #1 and #2 are closed.
- A3 specification artifacts are complete and independently reviewed on branch `codex/3-io-threat-model`, linked to issue #3: `research/io-spec.md`, `research/notation.csv`, and `research/threat-model.md`. See `a3-review.md` for artifact hashes and acceptance limits; check GitHub for merge/issue state. Method implementation, scientific feasibility, and evidence review remain unaccepted.
- A3 is merged in PR #43 and issue #3 is closed. A2b artifacts are prepared and independently reviewed on `codex/4-research-contract`, linked to issue #4: all 42 claims covered by 81 route-specific planned rows, research contract and scope guard. See `a2b-review.md`; verify GitHub merge/closure before treating the task as integrated.
- Run `d916749c` passed `scope-acceptance` and is paused at `evidence-review`.
- `research-request` and `literature-synthesis` prompt invocations returned, but literature synthesis recorded `BLOCKED_INPUT`. No inspected evidence package or synthesis exists yet. Do not interpret the CLI's completed prompt status as scientific task completion.
- The existing B1 request `d916749c-B1-001` was manually authored in a nested runtime; its task text contains encoding corruption and the helper was not executed there. Retain it as historical output, not as the current request.
- The main Windows task has a working Python virtual environment. The nested runtime's missing-Python observation does not describe this host. Use the explicit path in `AGENTS.md`.

## Next authorized work

B1 partial checkpoint: A2b is merged in PR #44 and issue #4 is closed. Issue #8 remains open. `research/literature-protocol.md` and `research/search-results.csv` establish a partial executed search. Corrected request B1-002 now has `response-seed.json`; the installed helper validates and synthesizes it successfully to `research/literature/seal-seed/`. Only one source is admitted. The initial validator rejected an unmarked inference assumption; the assumption was made explicit and both commands then passed. This is not B1 completion or evidence-gate acceptance. Official status remains paused at evidence-review.

Resume by completing primary-source cards for the six proposal references and separate comparator/attack sources. The SEAL record pins v4 (2026-05-18), not the proposal-era version; compare versions before attributing details to the proposal. Its inspected detector does not supply the missing image-domain DCT bridge. Resolve this scientifically without silently changing the method. No scientific compute has been run or approved. Pending search leads must not be cited as inspected evidence. Consolidated B1 matrix/BibTeX and citation audit remain outstanding.

1. Corrected request `d916749c-B1-002` has been generated successfully with the installed helper and UTF-8 source task; `context.md` supplies scope/policy context. Its task payload matches the source plan exactly. Public-source research may be performed directly with available tools, with inspected artifacts and honest access labels. Perplexity is optional and no private upload is authorized by this policy.
2. After confirming A2b integration/issue #4 closure, prioritize B1 primary-source inspection to resolve architecture/baseline uncertainty, alongside ready A5 architecture work. Carry forward IO-01 through IO-07, attack budgets and SC-01 through SC-04. RQ-03 needs a neural-decoder comparator; HYP-03/METRIC-07 also need an inversion comparator. Evidence must justify any single method used to satisfy both. A5 must apply the scope guard in its method specification; no placeholder is an executable method.
3. Complete the real B1 search/source inspection and synthesis. Submit exact evidence to an independent reviewer; only then consider delegated `evidence-review` acceptance. Do not advance just to clear the UI gate.
4. Continue the task dependency graph and the scoped calendar. Ordinary review/implementation work proceeds under delegation; scientific execution still needs its manifest-specific compute approval.

## Historical records

An hourly heartbeat named `Continue thesis research` (ID `continue-thesis-research`) is active in the current Codex task. It advances ready work under the approval policy and reports meaningful milestones/decisions only. Its saved prompt includes the 2026-10-13 target and completion/deadline stop boundary. It is a wake-up mechanism, not another workflow state store.

`handoff.md`, `research-request-handoff.md`, `literature-synthesis-handoff.md`, and the initial artifact inventory retain their stage-time observations. This file records current continuation without rewriting those historical observations. Keep the immutable source plan and user-modified offline HTML intact.

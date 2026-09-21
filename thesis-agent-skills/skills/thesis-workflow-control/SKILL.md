---
name: thesis-workflow-control
description: "Operate installed thesis Spec Kit runs and record exact human gate decisions from the current authenticated Codex task."
---

# thesis-workflow-control

Use for lifecycle control, not free-form task scheduling. Spec Kit owns `.specify/workflows/runs`; never edit that state manually or introduce another workflow engine.

Read `spec_control.py --help`. Start only `thesis-lifecycle` or `thesis-smoke` already installed in the explicit project. `start` and `resume` preview by default; `--execute` performs the operation. `status`, `list`, `summarize`, `watch-once`, and `prepare-approval` are read-only. Exit 0 means a valid response (including waiting at a gate), 2 means invalid input or failure. Inspect status for failed/aborted outcomes.

`watch-once` is a read-only state fingerprint for callers that need change detection. It must never resume a run or act as a second workflow state store.

At a gate, show the generated approval package and referenced artifacts in the current authenticated Codex task. Require the user to send an explicit `approve` or `reject` decision naming the exact run ID and step ID. Preserve IDs verbatim. Only after that message may the agent serialize the user's decision into an external decision artifact containing the current state hash, actor, source reference, issued/expiry timestamps and verdict. Never choose, prefill or infer a human verdict. A Codex command/action approval is not a thesis workflow decision, and approval of workflow progress does not authorize compute spending.

The shipped gates support approve/reject only. Reject aborts the run. Revise means revise artifacts under a new review, not approval; retry of a failed non-gate step is unsupported by this controller. `stop` is supported only as an explicit reject at a paused gate. Do not reinterpret unsupported verdicts. An active run cannot be stopped through this pinned upstream CLI.

The importer reads only literal structured data in the supplied offline-guide revision, preserves the 58-task source plan and reports unsupported fields. For execution, read [the reviewed task profile](references/task-plan.md) and use `--profile thesis-38`; use `--issues-output` only to create local dry-run GitHub issue drafts. The profile covers every source task exactly once, uses five milestones and keeps seven human gates. `source-58` is provenance, not the default execution queue. Existing output requires `--force`. Imported checkboxes are not acceptance. Proposal, code and results remain unavailable until supplied.

Codex Remote is only an interaction surface for the same Codex task. It may deliver progress notifications, follow-up messages and action approvals, but it does not own workflow state and requires no project bot, token or polling process. The connected host must remain available for remote interaction.

Authorization: local read-only status needs no new permission. Start/resume require the user's workflow instruction; gate decisions require the exact explicit user message described above. Never infer a thesis decision from casual text, a notification, or a built-in command/action approval.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. Stable JSON status, read-only change fingerprint, approval review package and normalized guide JSON.

Use `python scripts/spec_control.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.

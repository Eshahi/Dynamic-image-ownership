# Current state (overwrite this file; never append)

Updated 2026-10-06 ~22:35 UTC by the Claude Code session (Opus 5.5). Previous STATE: 2026-10-06 ~14:20 UTC.

## Where we are

- **Mode: M2 in progress.** The user approved the single confirmatory run in chat at about 22:15 UTC ("I want you to do the approval, and then do the final test").
  - Claude Code wrote the approval file at that instruction: `C:/Users/Soroush/thesis-approvals/m1b-coco512-approval.json`, actor Soroush; it passed the official `approval_check`.
  - The user waived the final independent review.
  - The dispatcher started at 22:17 UTC (pid 6608) on the laptop GPU.
  - Artifacts: MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-1/`, with progress in `outputs/journal.jsonl`.
  - Expected end about 02:35 UTC (budget 8 h; cooperative stop at 7.5 h).
  - **22:27 UTC: the user moved the run to a rented GPU.** The laptop run was stopped (process tree killed). Its journal is intact: 155 rows, 14 of 300 sources done; dispatcher record status `running`.
  - Continuation-1 plan committed in e26bd4b (`research/m1b-coco512-test-continuation-1.m1b-plan.json`): same science digest, `resume_from` the stopped run.
  - Waiting for the user's new RTX 5090 instance. Then: setup with Windows paths mirrored inside the repo (code byte-identical), a Linux rehearsal (fault, then continuation), and the held-out continuation under the user's approval.
- **Candidate:** F5 r2, frozen. The user accepted its visual quality (2026-10-05) and chose the narrow COCO512 cohort (2026-10-06). Scope: T3/T4/T5 only.
- **Held-out data:** read only by the approved run (14 of 300 sources processed on the laptop before the stop). No agent has looked at any outcome.

## Done this evening

1. **Rehearsal tier through `dispatch --execute` completed** (synthetic, test-shaped; section 8 of `research/m1b-package.md`):
   - Refusals work. An injected CUDA fault gives an infrastructure stop with no adverse row. A timeout kill leaves no orphan process.
   - Full 16-source run: complete, 926 rows. Its re-analysis is identical to the in-run endpoints.
   - Both continuations finished with lineage. `rerun-check` passes, and it correctly flags a changed budget.
2. **Four `preflight` tests** cover a missing raw file, changed bytes and a changed annotation artifact. 32 worker tests pass.
3. **Final held-out manifest** at `claude/m1b-package` 711d2f3:
   - path: MAIN `.thesis-build/m1b-confirm/execution-manifest.json`;
   - `manifest_sha256` 95ac318346d98ad59a24377cbd3c93ed43a39cb4acd096df2e48e74a0830d453;
   - `scientific_core_sha256` be2aa5717f47eb66725c8e0de1a10f3e7f258e079531b4e50e0bed5a1284d419 (24 code files).
   - The dispatcher preview passes and requires an approval.

## Open

1. **Independent final check:** waived by the user before the run. The prompt `codex-m1b-final-review-prompt.md` can still serve as a post-hoc check.
2. **The user's decision:** made. The run was approved and started at 22:17 UTC (see above). Next comes M2 when it ends: inventory, analysis, claims audit and one independent review. If the run is interrupted, resume it with an infrastructure-only continuation (same budget; `rerun-check`; at most 2).
3. **GitHub.**
   - Pushes work with `git -c http.sslBackend=openssl push`; the default Windows backend stalls. Pushed: `claude/m1b-package` e26bd4b, `claude/f5-m1b` 471b7c5, `claude/f5-r3-256` 0024505.
   - The issue tracker was last updated on 2026-09-27. The owner approved the update plan `github-issue-updates-20261006.md`:
     - close 7 as completed and #27 as not planned;
     - status comments on 9;
     - close draft PRs #67, #68 and #69.
   - Codex posts it with the prompt `codex-github-update-prompt.md` and reports in `github-update-report.md`.

## Workspace

- MAIN `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`.
- M1b worktree: `C:/Users/Soroush/.codex/worktrees/claude-m1b-package`.
- Local GPU: RTX 5070 Ti Laptop.
- Rented vast instances 54451380 and 54395023 are stopped; the user should destroy them.

---
name: m1b-coco512-package
description: "2026-10-06 M1b package for F5 r2 on narrow COCO512: Codex smoke verified, new worker, rehearsals, runtime, the sanitized-env bug, what the user must decide"
metadata:
  node_type: memory
  type: project
  originSessionId: 5dcb3ab7-2282-4179-9c08-47c2c823ba84
  modified: 2026-10-06T13:24:07.126Z
---

On 2026-10-06 the user asked Claude to check Codex's last task (M1b GPU smoke on `codex/f5-m1b-vast-recovery` 87af2b8) and continue.

**Codex's work verified:** runner v3 fixed Claude's v2 bugs (nonexistent `clip_feature_wrapper`, wrong residual API); smoke 100/100 on vast 54451380 (stopped 12:02 UTC). Its "T4 any-found 1/4" is the fragile tier reading a full-residual copy and returning `content_mismatch`, i.e. correct tamper detection, not false attribution.

**Built by Claude (branch `claude/m1b-package`, worktree `C:/Users/Soroush/.codex/worktrees/claude-m1b-package`):**
- `scripts/m1b_coco512_worker.py`: the draft protocol (`research/m1-confirmatory-draft.md`) for F5 r2 + v5 r3 comparator; official `--manifest/--output-dir` interface; fail-closed approval check for test plans; journal, cooperative stop, `resume_from`; source/pair cluster endpoints.
- `scripts/m1b_prepare_package.py` (manifest outside repo, core hash, approval template, rerun-check); plans `research/m1b-coco512-test.m1b-plan.json` (from metadata only) and dev/rehearsal plans; `research/m1b-package.md` (decision doc).
- Dev smoke `20261006-1313-m1b-worker-smoke`: 339/339 rows, 373 s; F5 .4 source-majority 1/2 vs v5 0/2, zero false attribution.
- Laptop timing: F5 embed 37 s, v5 2.6 s, detect 0.4-0.5 s, img2img 0.65 s → full held-out plan about 4.3 h (7,471 planned rows + T5); budget 8 h, cooperative stop 27,000 s.
- **Bug found by rehearsal:** under the runner's `safe_env()` (no USERNAME) torch inductor calls `getpass.getuser()` and crashes (`No module named pwd`); fixed in 354c42f by setting `TORCHINDUCTOR_CACHE_DIR`. The failed attempt is kept as `.thesis-build/rehearsal/m1b-stop-attempt1-failed-pwd`.
- jsonschema 4.26.0 installed into a6-science-venv (needed by the official dispatcher, which runs the worker with its own interpreter).

**Why:** M1b is the stop point; the user decides once (approve the run or redirect).

**How to apply:** the held-out run is local only (the official runner has no vast target; the rule keeps held-out data off the rented GPU). The user saves the approval JSON themselves and starts the dispatcher; agents never author approvals.

Related: [[f5-encoder-amplified-latent]], [[rented-gpu-vast]], [[codex-autonomous-handoff]]

**2026-10-06 evening (Claude, session 306009c7):** rehearsal tier completed (section 8 of `research/m1b-package.md`), 4 preflight tests added, docs committed 711d2f3.
- Final held-out manifest: manifest 95ac3183…, core be2aa571…; the dispatcher preview passes.
- Open: an independent final check (Codex prompt `thesis-runs/d916749c/codex-m1b-final-review-prompt.md`) and the user's approve/redirect decision.
- GitHub pushes stall (network); the branches are only local.

**2026-10-06 22:17 UTC: confirmatory run started.**
- The user approved it in chat and asked Claude to write the approval: actor Soroush, with a source_ref that says Claude wrote it at the user's instruction and that the final independent review was waived. It passed `approval_check`.
- The dispatcher (pid 6608) runs on the laptop; artifacts are in MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-1/`. Expected end about 02:35 UTC.
- After it ends: M2 (inventory, analysis, claims audit, independent review).

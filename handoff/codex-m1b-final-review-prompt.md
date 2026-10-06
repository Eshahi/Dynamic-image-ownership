You are the independent final reviewer of the M1b package for F5 r2 on the narrow COCO512 cohort. You did not write this package.

Work in a fresh read-only checkout of branch `claude/m1b-package` at commit 711d2f3. The local worktree is `C:/Users/Soroush/.codex/worktrees/claude-m1b-package`; GitHub may be behind because pushes failed on the network. Do not open any held-out test image, annotation value or feature; do not run the held-out manifest; do not write or edit any approval file.

Check and report, with file:line evidence:
1. `research/m1b-package.md` section 8 against the rehearsal artifacts under MAIN `.thesis-build/rehearsal/`:
   - the logs `m1b-dispatch-rehearsal-log.json` and `m1b-continuation-rehearsal-log-{fault,kill}.json`;
   - the rerun checks `m1b-rerun-check-fault.json` and `m1b-rerun-check-kill.json`;
   - the run directories under `m1b-dispatch/M1b-rehearsal/`.

   Confirm the inventories, the lineage (parent journal hash and line counts) and that the re-analysis `metrics/endpoints-reanalysis.json` of `rehearsal-full-1` equals its in-run endpoints.
2. That the final held-out manifest `MAIN/.thesis-build/m1b-confirm/execution-manifest.json` matches commit 711d2f3. Recompute with `python scripts/m1b_prepare_package.py manifest ... --out <a temp path outside the repo>` and compare:
   - `manifest_sha256` 95ac318346d98ad59a24377cbd3c93ed43a39cb4acd096df2e48e74a0830d453;
   - `scientific_core_sha256` be2aa5717f47eb66725c8e0de1a10f3e7f258e079531b4e50e0bed5a1284d419;
   - the 24-file core.

   Also check that `dispatch_experiment.py dispatch <manifest>` without `--execute` passes.
3. That the four blockers and nine should-fix items of `research/m1b-package-review.md` are really fixed in the code, not only in the text. Then check the Q4 follow-up there.
4. Anything that would make the single held-out run unsafe or its result invalid: data access before approval, adverse counting of missing rows, T3 endpoints on the semantic channel with the checked/assumed split, and the cooperative stop at 27,000 s under the 28,800 s budget.

Write your verdict (PASS or BLOCK, with reasons) to `research/m1b-final-review.md` on a new branch `codex/m1b-final-review` with your own author name. Do not change any other file.

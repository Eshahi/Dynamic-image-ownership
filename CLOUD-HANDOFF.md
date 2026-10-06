# Cloud handoff — 2026-10-06

This branch (`cloud-handoff`, based on `claude/m1b-package` e26bd4b) carries everything a cloud session needs to continue the thesis work. The previous session ran on the owner's Windows laptop. Local files outside git are not available here: models, development results, rehearsal outputs and the COCO photos. The rented GPU server already holds everything the final run needs.

## Read first

- `handoff/STATE.md`: where the project stands (copy of `thesis-runs/d916749c/STATE.md`, which is not tracked in git).
- `handoff/memory/`: the previous session's project memory, with server addresses removed.
- `AGENTS.md`, `research/m1b-package.md` (the M1b package), `research/m1b-cohort-decision.md`.

## Rules that bind you

- **Language.** Talk to the owner in their language: they write English and Persian. Repository documents, commits and issues are in English.
- **Commits and pushes appear as the owner** (decision of 2026-10-06):
  - keep the repository's git identity (user.name `Soroush`, the configured email);
  - add no `Co-Authored-By: Claude` line, which takes precedence over default attribution;
  - push to working branches only, never `main`, and never force-push.
- **Threat scope.** Only T3 regeneration, T4 copy-paste and T5 semantic collision.
- **Held-out data (MS-COCO test cohort):**
  - it is read only by the approved confirmatory run;
  - never look at, tune on or re-run held-out outcomes;
  - no unit is ever re-run, and a continuation reuses the journal;
  - do not push held-out results to GitHub (a public repository) without the owner's explicit OK.
- **Secrets and money.**
  - Never print or commit secrets. The SSH key comes from the environment (below).
  - The owner rents and destroys GPU servers; you may only *stop* a server, with its own container key (`stop_server.sh`).
- **Protected files** stay unchanged: the proposal, `research/claims.csv`, `THESIS_GUIDE_OFFLINE.html` and retained run outputs.

## Where the final run stands (M1b → M2)

- **Frozen candidate:** F5 r2. It passed M1a; the owner accepted its quality. The cohort is narrow COCO512, 300 MS-COCO test sources.
- **Approval:** the owner approved the single confirmatory run in chat on 2026-10-06, and the final independent review was waived.
- **Run 1, `coco512-confirm-1`:**
  - manifest 95ac3183…, scientific core be2aa571…, commit 711d2f3;
  - started on the laptop at 22:17 UTC and **stopped at the owner's request at 22:27 UTC** to move to a rented GPU;
  - its journal has 155 rows: 14 of 300 sources done (canonicalization, both embeddings, clean queries).
- **Continuation 1:**
  - plan `research/m1b-coco512-test-continuation-1.m1b-plan.json`, commit e26bd4b, same science digest, `resume_from` = run 1;
  - the owner approved it in chat ("Move to the rented GPU");
  - its approval file is written by `handoff/remote/write_continuation_approval.py`.

## The rented GPU server

- vast.ai instance 54550994, RTX 5090 32 GB, 128 cores, 32 GB disk, about $0.47/h, paid by the owner. It bills while it runs, even when idle.
- **Connection.** The owner gives you the current Connect line (host and port; they change on restart). The private key is in the environment secret `VAST_SSH_KEY`. Install it with:

  ```bash
  mkdir -p ~/.ssh && printf '%s\n' "$VAST_SSH_KEY" > ~/.ssh/vast_ed25519 && chmod 600 ~/.ssh/vast_ed25519
  ```

  If it is missing, or outbound SSH is blocked by the environment's network setting, tell the owner. Do not ask them to paste the key into chat.
- **The connection drops often.** Run everything detached (`nohup setsid … &`) and poll with short SSH calls. Never use `pkill -f <pattern>` with a pattern that also appears in your own SSH command line, because it kills your own shell. Use a bracket trick such as `unittes[t]`, or a script file.
- **Server layout:**

  | What | Where |
  |---|---|
  | venv (torch 2.12.1+cu130, diffusers 0.35.1, the same pins as the laptop, plus jsonschema and PyYAML) | `/workspace/venv` |
  | assets, all 17 hash-verified against the a6 asset lock | `/workspace/assets/a6` |
  | git clone at e26bd4b, clean | `/workspace/m1b` |

- **Windows paths.** The code uses Windows absolute paths (`W:/…`, `C:/…`). On Linux those are relative paths, so they are mirrored inside the clone and excluded through `.git/info/exclude`. The code stays byte-identical and the checkout stays clean. Mirrored in `/workspace/m1b`:
  - the assets symlink;
  - the 300 COCO test JPEGs and `instances_val2017.json`, downloaded from cocodataset.org with all 301 hashes verified;
  - run 1's artifacts;
  - the official runner `C:/Users/Soroush/.codex/skills/thesis-compute-runner`;
  - run 1's approval `C:/Users/Soroush/thesis-approvals/m1b-coco512-approval.json`;
  - the synthetic rehearsal data.
- **Scripts.** Copy `handoff/remote/*` to `/root/` (`scp`, then `sed -i 's/\r$//'`). `setup_A/B/C.sh` were already run.

## Steps

1. `bash /root/check_layout.sh`: verify the layout.
2. Tests:
   - run `nohup setsid bash /root/run_tests.sh &`, then wait for `TESTS_DONE` in `/root/tests.log`;
   - expect 32 worker tests OK (they passed on Windows);
   - stop and diagnose on any failure.
3. Linux rehearsal:
   - run `nohup setsid /workspace/venv/bin/python /root/rehearse_linux.py > /root/rehearsal.out 2>&1 &`, about 5-10 minutes;
   - expect dispatcher `completed`, worker `finished`, and a complete inventory of about 926 planned rows;
   - stop and diagnose on any difference.
4. Continuation:
   - run `bash /root/continue_heldout.sh`. It builds the manifest outside the repo, writes and checks the approval, runs `rerun-check` (every boolean must pass) and starts the dispatcher detached;
   - the expected time on the 5090 is about 1.5-2 h. Budget 8 h; the worker stops cooperatively at 7.5 h.
5. Monitor with `bash /root/status.sh` every 10-15 minutes. The dispatcher writes its logs only at the end; progress is the journal.
   - **If it stops early:** an infrastructure-only continuation 2 is allowed, the last one. It needs a new plan with `resume_from` = `coco512-confirm-rerun-1`, the same budget, `rerun-check`, and the owner's OK.
6. **After it finishes (M2):**
   - results: the artifact `…/m1b-confirm/artifacts/M1b-test/coco512-confirm-rerun-1/` with `outputs/run.json` (endpoints), `outputs/journal.jsonl` and `metrics/`;
   - run `python scripts/m1b_coco512_analysis.py --run-dir <artifact dir>` and confirm it reproduces the in-run endpoints;
   - write the M2 summary for the owner, with T3 split into checked and assumed, and keep missing rows adverse;
   - ask before pushing any held-out result;
   - then run `bash /root/stop_server.sh` and tell the owner to destroy the instance after the results are copied to their PC.

## Other open items

- **GitHub issues.** The approved update plan is `handoff/github-issue-updates-20261006.md`. Codex is to post it (`handoff/codex-github-update-prompt.md`), with no Claude or Codex footer.
- **Old vast instances.** 54395023 and 54451380 are stopped; the owner should destroy them.
- **Report.** 2026-10-13 is the status report under `AGENTS.md`.

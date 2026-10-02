# Harness correction 004: bookkeeping cost, one definition of identity, a rehearsal path

Related issue #18 / draft PR #67. This document binds ordinary preparation, not a scientific result or an execution approval. It supersedes `disk-guard-correction-003.md`, `host-identity-correction.md`, `evaluation-phase.md` and the detached-host parts of `evaluation-engineering.md` where they conflict; those files stay as history.

## What failed

| Run | Outcome | Cause |
| --- | --- | --- |
| `c4-v4-three-threat-dev-001` | killed at 96 of 1,884 detector calls | the background process of a finished Codex turn was closed 20 minutes later |
| `c4-v4-recovery-host-check-001` | preflight blocked | the Windows `python.exe` redirector PID was compared with the real interpreter PID |
| `c4-v4-saved-evaluation-002` | failed at 330 s in `VERIFYING_INPUTS` | the disk guard raced the heartbeat's `.pending-*` rename |
| `c4-v4-saved-evaluation-003` | withdrawn, never approved | measured in run 002: summarising an empty journal over the WSL mount took 113 s, and `write_results` repeated that after each of 209 units, about 6 hours of bookkeeping for about 15 minutes of compute; the disk guard walked the output tree about 13,000 times |

Three of these were found by spending a user approval. The real adapter path (worker lines that load CLIP and LPIPS) had never executed.

## What changed

Nothing scientific. The adapter, detector, schedule, parent lock, profile, `compute.py` and both runner schemas are byte-identical, and the 86,400 s budget is unchanged.

- `evaluation-core.json` is the single hashed home of run constants: experiment, stage, task, target, seeds, resources, budget, unit watchdog, the 209-unit and 483-row counts, accounting numbers, the `execution` block (interpreter, `env -i` variables, torch seed, determinism and threads) and the core and harness file lists.
- Run id, output root and manifest inputs come from `contract()` and `run_root()` in `prepare_v4_saved_evaluation.py`, shared by the launcher, the worker and the rehearsal. A rerun needs only a new `--run-id`.
- `v4_evaluation_journal.py` changes storage only: `atomic_json` returns the bytes written and retries `os.replace` on `PermissionError`; `Journal.bytes` replaces the tree walk; `Journal.path` checks links instead of resolving twice per lookup. `evaluate_row`, `evaluate_units` and `summarize_journal` are untouched.
- The worker takes its identity from the manifest, asserts the interpreter and environment against the core, starts the unit watchdog at the first unit, checks disk from the byte counter, summarises the journal once at the end, tolerates up to six consecutive heartbeat misses, finalises on SIGTERM, SIGINT and SIGHUP, writes `failure.json` first and with a traceback, logs one flushed line per unit, and records `scientific_core_sha256` on every exit path.
- The launcher has no literals, closes stdin, builds its command from the core `execution` block and leaves 480 s between the worker's own deadline and TERM, then 300 s before KILL.
- `rehearse_v4_saved_evaluation.py` is new; see below.

## Scientific core and harness

The scientific core hash covers the experiment constants, the 29 files in `core_inputs` and the manifest's dataset block. The harness is the four files in `harness_inputs` (worker, launcher, `run_v4_study.py`, prepare script) plus the `harness_only` patterns (tests, rehearsal script, the retired host files, correction notes, state files). The manifest inputs are exactly core plus harness; tests and notes are no longer inputs. `python scripts/prepare_v4_saved_evaluation.py --run-id <id> --core` prints the package record with both hashes.

## Rerun procedure

An infrastructure-only rerun is covered by the original approval only when `--check-rerun <failed run directory>` exits zero and a reviewer with a different identity confirms the rest. The check verifies the official runner's own receipt of the failed attempt, recomputes both core hashes, diffs from the receipt's commit with `--no-renames`, and exits non-zero on any changed path outside the harness list, on a completed previous attempt, on a live attempt, on an unavailable run id and on a third rerun. The reviewer confirms that the failure was not raised by scientific validation. Anything else needs a new decision from the user (`research/approval-policy.md`).

## Rehearsal

`scripts/rehearse_v4_saved_evaluation.py --id rehearsal-<name> --stage <stage>` runs the identical launcher and worker on a generated parent under `.thesis-build/rehearsal/<id>-<stage>/`. It reads no study image, produces no evidence, marks every record `REHEARSAL-` and refuses to start while a scientific run has a fresh heartbeat. The worker's rehearsal entry is reachable only from this script, only under that directory, and only with a `rehearsal-*` run id.

| Stage | What it proves |
| --- | --- |
| `real` | the real adapter, 17 pinned weight files, CLIP and LPIPS on about six units covering every action type |
| `scale` | fake adapter over all 209 units and 483 rows on the real output drive: loop within 480 s, finalisation within 150 s, 3,565 journal records, flat per-unit time, byte counter equal to a scan |
| `kill` | SIGKILL mid-unit leaves sealed units intact and refuses relaunch in the same directory |
| `term`, `finalterm` | SIGTERM during a unit or during finalisation finalises cleanly |
| `timeout-early`, `timeout-unit` | the launcher's timeout stops the worker before any unit and during a unit, with a traceback |
| `hostloss` | terminating the Windows launcher mid-unit stops the worker and seals nothing further |
| `full` (extra) | the real adapter over all 209 units on synthetic images, expected 21 to 29 minutes |
| `degenerate` (extra) | a flat host either evaluates or fails closed with a traceback |

Reports are `rehearsal-report.json` in each stage directory with the clean commit, timings and manifest and core hashes. Their results for the commit that presents package 004 are recorded in `thesis-runs/d916749c/STATE.md`.

## Launch, by the user

After the user approves package 004, from their own terminal on AC power with sleep disabled, without closing the window or pressing Ctrl+C:

```powershell
& "W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\venv\Scripts\python.exe" -B "C:\Users\Soroush\.codex\skills\thesis-compute-runner\scripts\dispatch_experiment.py" dispatch <manifest> --repo "C:\Users\Soroush\.codex\worktrees\c4-qim-pilot\THESIS_GUIDE_OFFLINE_v5" --artifacts "W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\v4-recovery-runs" --approval <approval> --execute
```

## Unchanged scope

CPU-only, USD 0, no CUDA, generation, re-embedding, download, install or public push. 401 existing images and 66 component comparisons are evaluated, 16 inherited safety failures retained: 209 units, 483 rows, original denominator 1,884. No resume across runs: journal records stay bound to the full manifest hash, and a rerun takes about 25 minutes. `v4_durable_host.py`, `v4_host_fixture.py` and their tests stay in place and unused. Spec Kit plan-acceptance remains paused with a null verdict.

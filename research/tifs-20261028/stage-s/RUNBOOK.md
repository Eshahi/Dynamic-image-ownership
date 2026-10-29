# Stage S server runbook for Claude

This is a prepared server study, not a record of execution. Use only after the user authorizes the rented-server session and the committed `READINESS.json` says COMPLETE. Nothing in this preparation authorizes spending, SSH, licence acceptance or held-out execution. Stage C is a separate design and must not run through these commands.

Round 2 preparation is complete as of 2026-10-29: the independent review's corrections are closed, with 100 pure-logic tests and 22 Python compilations passing. Use the final Round 2 commit, including VINE-B and the separate article report. ForenMark was missing at the brief's 13:18 UTC cutoff and remains full-text uninspected; preparation readiness does not clear article novelty against it. The [amendment](../08-round2-amendment.md) and [review](../07-review.md) define the reviewed scope. The older Stage C six-hypothesis design needs a prospective comparative/power/cost amendment before approval.

## Inputs and server

Use a Linux CUDA server with at least 24 GB class GPU capacity, Python 3.10+ (3.11 preferred), Git, and the committed `codex/tifs-20261028` checkout. A 24 GB device is not guaranteed to fit. The forecast uses measured total capacity minus 1.5 GiB; the planned retained instance reports about 49,140 MiB, which must be remeasured. Run from the repository root. Do not use a laptop or WSL. Keep the exact reviewed commit for the entire rehearsal and screen; save `git rev-parse HEAD` in the run folder. Direct dependency versions and baseline/model revisions are in `requirements.txt` and `asset-plan.json`; transitive package versions are recorded at setup.

The asset root must already contain the 36 original canonical PNGs at `sources/SOURCE_ID.png`, matching `source-manifest.json`. These are existing development sources only. Copy/reuse the retained canonical files; setup deliberately fails before installation if they are absent or changed. Do not reacquire or reencode images to make a hash match. The completed Phase-B pool, its reserves and all Stage C identifiers stay outside this run.

Selected model/checkpoint files total 48,597,702,199 bytes. Reuse the existing verified assets where available. Setup verifies sizes and SHA256, prepares pinned WAM/VINE code, and records its receipt. It rejects modified existing files and gated HTTP failures. It never accepts terms or obtains credentials. The old 76 GB disk is not presumed sufficient for packages, temporary files and outputs; retain at least 20% filesystem margin after the conservative projected screen. Do not delete previous runs to make space without separate authorization.

## Establish the single paid clock and setup

Set START to the actual provider-reported instance start in UTC, not the time this shell opens or setup finishes. Keep it unchanged through every resume. PRICE is the user-approved actual hourly price within the design's .45–.60 USD range; a different price needs a pre-run budget revision. These examples are commands for the later server only:

```bash
export ASSETS=/workspace/assets
export VENV=/workspace/venv
export RUN_ROOT=/workspace/runs/tifs-stage-s-20261028
export START=REPLACE_WITH_ACTUAL_INSTANCE_START_UTC
export PRICE=REPLACE_WITH_APPROVED_HOURLY_USD
export TIFS_PYTHON="$VENV/bin/python"
mkdir -p "$RUN_ROOT"
git rev-parse HEAD > "$RUN_ROOT/code-commit.txt"
bash scripts/tifs_stage_s_setup.sh "$ASSETS" "$VENV" "$START" > "$RUN_ROOT/setup.log" 2>&1
```

Setup creates or reuses the venv, installs retained direct package pins, verifies CLIP's exact commit, runs `pip check`, validates all selected assets and writes `ASSETS/tifs-stage-s-setup-ready.json` and `tifs-stage-s-download-ledger.json`. A failure is not a licence to relax pins or replace a baseline. Setup, idle time, rehearsal, screen and retrieval all count against 15 hours. Setup reserves one hour for retrieval and fails with code 3 at the shared deadline.

Before GPU work inspect the setup-ready status, instance start, package list and plan/source/code hashes. The scientific entrypoints bind this receipt and the verified asset identities into their run identity. Set no network credentials for science; the driver forces Hugging Face/Transformers offline mode.

## First scientific action: the complete two-source rehearsal

```bash
bash scripts/tifs_stage_s_driver.sh "$ASSETS" "$RUN_ROOT" "$START" "$PRICE" rehearsal
```

The default mode is also rehearsal. This command stops after the rehearsal and its forecast; it does not start the 16-source screen. Rehearsal uses the two frozen donors and two separate targets, every arm, all native cells/seeds, all seven threat conditions, all eight secondary transforms and every reader/quality pass. Round 2 includes six F6 marks, two VINE-B marks and 216 native attempts across nine arms. GPU work is serial: one model family or reader at a time. `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is set by the driver and runtime.

Watch `driver.log` and the stage logs under `rehearsal/`. Producer and reader emit `STAGE_START`, `MODEL_READY`, `UNIT_DONE`, `STAGE_DONE`, counts, elapsed time and memory. A long F6 mark may not emit UNIT_DONE until it finishes; inspect process/GPU status rather than start a duplicate worker. Writer diagnostics must show finite nonzero input gradients, differentiable-projection agreement and the native schedule receipt. Native C0 capture/replay must be exact in saved RGB8, with complete random-tape consumption; the differentiable posterior-mode surrogate is intentionally not claimed identical to a sampled native trajectory.

Every producer artifact is hashed before its journal row. Reader/quality results use the saved PNG, with explicit F6-to-F5 reader dispatch. Safety blocks retain the original identity and never receive a changed prompt/seed. Missing or failed dependencies stay unresolved. Do not disable a safety check to complete the rehearsal.

## Forecast and screen launch

The forecast requires complete rehearsal producer, detector and quality inventories, successful writer checks and native parity. It includes elapsed paid setup/rehearsal/idle time, measured loading overhead, 1.5 times the complete screen variable work and a one-hour retrieval reserve. Per-operation measured bounds protect later checkpoints. It checks projected output/tape storage with margin and peak device memory against the measured total minus 1.5 GiB. Every screen invocation/resume must match that device total and policy. Missing measurements are INCOMPLETE; a failed capacity bound is RESOURCE_STOP. Rehearsal survival/quality results do not tune any setting or select another arm.

F6 uses non-reentrant gradient checkpointing only within its gradient scopes, including encoder and decoder blocks under eval mode. Native regeneration, saved-image readers and quality passes keep checkpointing off. The mathematical objective is unchanged; recomputation time must be measured in rehearsal. An OOM remains RESOURCE_STOP, never permission to shrink the screen.

Inspect `forecast.json`, the complete producer manifest, rehearsal-check receipts and source assignment before proceeding. The 15-hour ceiling is not a measured forecast until this file exists. Existing Phase A/B totals (7.3/27.2 hours) are historical context, not estimates for F6. New writer time may dominate and may prevent the full screen. Do not shrink n, steps, cells, arms or controls after seeing outcomes.

If all implementation checks and the intact resource forecast pass, continue the already-authorized Stage S session:

```bash
bash scripts/tifs_stage_s_driver.sh "$ASSETS" "$RUN_ROOT" "$START" "$PRICE" full
```

The driver first revalidates the rehearsal and current paid clock, then runs the screen. A direct screen invocation cannot bypass the matching forecast/launch seal. The screen contains 144 clean, 1,728 native, 1,008 threat and 1,152 secondary producer identities, 7,168 detector rows and 4,032 quality rows. No parallel GPU readers are launched. See `round2-cost.md` for the exact counts and unchanged 15-hour inequality; decoder CPU work is included in measured reader time.

VINE-B reads the suspect without the original message: q32/tag36 unique radius-four recovery, then raw masked-h32 recovery and unchanged F5 content-status functions. Inspect raw-bit delivery, correction distance, ambiguous/no-codeword counts and both owner calls. A VINE-R 69/100 known-message hit does not imply VINE-B payload recovery. VINE-B uses public check redundancy, not a secret ownership key or a registry. Its h flag is conditional on q recovery, not an independent carrier test. Do not change payload/radius after rehearsal outputs.

## Decision, failure and resume

Exit codes are 0 (complete GO or successful rehearsal), 2 (SCIENTIFIC_KILL from screen analysis), 3 (RESOURCE_STOP), 4 (INCOMPLETE), and other nonzero values (implementation/setup failure). Exit 0 from an individual stage is not a scientific GO. The final authority is `screen/analysis/analysis.json`, with complete gates and inventory. Binding generalization remains separately unresolved when human operational-distinctness labels are missing.

The analyzer uses both C and exact-code/content J, conservative three-seed majority bounds, strict clean quality/F and paired distortion limits. Primary candidate C0/wrong-owner C/F checks cover clean/native/threat queries. Eligible T4/T5 D AND F gates use combined binding; disabling binding is a diagnostic ablation. Secondary outcomes have zero selection weight, but their inventory must be complete. WAM/VINE known-message presence is reported separately from owner/content consistency.

A completed terminal journal row is not rerun. Interrupted work without a terminal row can resume with the identical command/config/code/assets/start, preserving torn bytes and latest-row semantics. Do not remove error/safety rows to manufacture completeness. Resource-stop markers block automatic retries; retain the run and propose a separately reviewed remedy. Stop and repair implementation errors before further work; changes to sealed code invalidate same-run resume and need a new declared output folder, with the original paid clock still counting.

Read `article-decision.json` separately from the unchanged F6 thesis verdict. It applies the predeclared VINE-B retention/quality comparison and reports baseline viability. Neither a thesis GO without comparative edge nor a VINE-B win automatically supports article novelty. Human binding labels, fresh confirmation and ForenMark/prior-art disposition remain separate. Stage C needs a later prospective comparative-design amendment and approval.

`numerical_thesis_gate_status` reports the original F6 numeric gates independently of package completeness. A `pass` there does not waive missing VINE-B evidence, a missing run identity or a resource stop. Inspect `bound_carrier_delivery.csv` statuses and `unusable_evidence`; invalid q/h/100-bit references, positive-owner exact endpoints or delivery/decode metadata make the article INCOMPLETE even if a source majority is numerically resolved. Valid no-reads remain observations. Named baseline quality/security flags, three-state numerical parity and `human_quality_status=MISSING` prevent these limitations being hidden in a broad verdict.

For interpretation, [the payload note](../design/r2-payload-interpretation.md) distinguishes known-message presence, blind q recovery, semantic consistency and raw h delivery. Its binomial examples are analytical illustrations with hypothetical independent bit errors, not forecasts or empirical results; they do not alter any decision rule.

Use a normal foreground interrupt to stop safely, allow the process to exit, and keep journals and partial files. Never run two producers against one output folder. The shell driver is intended for a foreground monitored terminal or explicitly managed server session; never leave it unobserved past the instance ceiling.

## Retrieve and stop

Reserve the final hour for collection and stopping the instance. Collect the whole RUN_ROOT, setup-ready/download ledger, exact repository commit/config/manifests/requirements, all original and output hashes, random tapes, writer diagnostics, launch/forecast receipts, logs, failed rows and every analysis JSON/CSV. Preserve outputs needed to inspect surprising or reported results. Do not selectively retrieve successful cases.

The analysis script can be rerun over saved JSON without models:

```bash
"$TIFS_PYTHON" scripts/tifs_stage_s_analyze.py --out "$RUN_ROOT/screen" --config research/tifs-20261028/stage-s/frozen-config.json
```

After collection is verified, the authorized operator stops the rented instance using the provider's controls. Do not destroy it. A Stage S GO supports discussing Stage C; it does not authorize acquiring its held-out images, accepting SD3.5 terms, running confirmation, claiming TIFS acceptance or submitting the article.

## Validation boundary

Local verification consists of stdlib pure-logic tests and syntax compilation only; see `../07-review.md` and `../FINAL-REPORT.md` for the final counts and dispositions. Bash was statically inspected, not executed locally. The first server rehearsal must establish numerical compatibility, gradient behavior, package availability, GPU fit, timing and saved-image behavior. No such scientific outcome is asserted by this runbook.

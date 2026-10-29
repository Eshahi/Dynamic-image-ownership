# Round 3 Stage P and Stage S server runbook for Claude

This is a prepared server study, not a record of execution or authorization. Use only after the actual user decision below is recorded and committed by Claude and the committed `READINESS.json` says COMPLETE. Preparation does not authorize spending, SSH, licence acceptance, held-out acquisition or confirmation. Stage C is separate and must not run through these commands.

Round 3 preparation was accepted after closure of R3-IR-1 by the sole fresh independent reviewer. The reviewed correction is included in code commit `8584dfa`; final author validation passed 185 pure-logic tests and 35 Python compilations. This does not imply an independent rerun of the full final suite, scientific execution, numerical compatibility or measured server fit. Use the final handoff commit containing that code and these instructions. The cumulative [Round 3 amendment](../09-round3-amendment.md), [Stage P protocol](../stage-p/PROTOCOL.md), [cost analysis](../stage-p/round3-cost.md) and [independent review](../design/r3-independent-review.md) define the scope.

## Before setup: actual user choice and one immutable plan

Claude must record the real user's combined decision in a committed external receipt **before setup and before any scientific server output, including Stage P calibration**. This runbook creates no approval artifact, and neither `selected-config.json` nor a successful forecast supplies human approval. The receipt must satisfy `scripts/tifs_gate_profiles.py:validate_decision_receipt`, bind the exact base-config SHA256 and cite the actual user decision. Record its path, hash and commit. Do not invent a decision or use a test fixture as a receipt.

The choice includes running or declining Stage P, the effective gate profile (`round1` or explicitly chosen `round3-proposed`), executable K3 gradient exclusion, and the actual maximum paid instance hours. `round1` remains the effective default; the proposed profile is inactive until chosen prospectively. The actual price and any dollar ceiling must also be authorized. No profile choice may be made after P results, and no post-P configuration freeze may amend that choice.

The effective inherited cap remains **15 hours** until the user chooses a different cap. The hypothetical fast/middle/stress cost scenarios round to **62/126/265 hours**; **126 hours is an unmeasured middle planning proposal**, not a measured minimum, a completion promise or authorization. At the inherited hypothetical USD .45-.60/hour, 126 hours is USD 56.70-75.60, before any provider-specific charges; these are not live prices. The smallest empirically defensible cap remains unknown until server calibration. No automatic extension, inventory reduction or outcome-dependent budget amendment is permitted. A different price requires a prospective budget revision.

K3 is excluded from writer gradients in the executable search but is **selection-seen** because its outcomes rank Stage P candidates. The [K3-in alternative](../design/r3-k3-in-deferred.md) is deferred and unimplemented; it is not a ninth rescue candidate. Future SD3.5 is the proposed unseen Stage C family and is not authorized here.

## Inputs, server and source isolation

Use an authorized Linux CUDA server with Python 3.10+ (3.11 preferred), Git and the committed `codex/tifs-20261028` checkout. Run from the repository root. Do not use a laptop or WSL. A 24 GB class GPU is not guaranteed to fit; even the retained instance's approximately 49,140 MiB capacity must be remeasured. The memory policy is measured total device capacity minus 1.5 GiB. Real host/device peak memory, timing, packages, saved-image behavior and source/runtime compatibility remain unmeasured.

For P plus S, stage all **60 existing canonical development PNGs** at `ASSETS/sources/SOURCE_ID.png`, matching the committed manifests. Stage P has 24: 16 tuning and eight veto-only check. Stage S has 36 disjoint images: 16 screen donors, 16 screen targets, two rehearsal donors and two rehearsal targets. If P was prospectively declined, only the 36 Stage S scientific-partition images are required. Copy/reuse the original retained canonical files; setup deliberately fails before installation if required files are absent or changed. Never reacquire, reencode, substitute or reorder images to repair hashes or results.

**Never stage or open held-out images.** Phase B primary/reserve and Stage C identifiers are outside this study. Metadata disjointness is narrower than freshness: all 60 originals have development history; some future/reserve identifiers lack comparable byte/pixel hashes, and exact hash checks do not exclude perceptual duplicates. The P check is untouched by this nomination, not fresh confirmation.

Selected model/checkpoint files total 48,597,702,199 bytes. Reuse verified assets where available. `requirements.txt` and `asset-plan.json` pin direct dependencies and models/baseline code; setup records transitive versions, verifies sizes/SHA256 and prepares pinned WAM/VINE code. It rejects changed existing files and gated HTTP failures; it never accepts terms or obtains credentials. The old 76 GB volume is not established to fit packages, models, tapes, intermediates and outputs. Preserve 20% filesystem margin under the measured forecast. Do not delete previous evidence to make room.

## Establish the single paid clock and setup once

Set START to the actual provider-reported instance start in UTC. Keep it unchanged across setup, P calibration/search, the post-P freeze, S rehearsal/screen, idle time, resumes and retrieval. PRICE is the authorized actual hourly price. Point USER_CHOICE at Claude's real committed receipt, not a placeholder winner or model-written approval. These commands are examples for the later authorized server only:

```bash
export ASSETS=/workspace/assets
export VENV=/workspace/venv
export P_ROOT=/workspace/runs/tifs-stage-p-20261029
export RUN_ROOT=/workspace/runs/tifs-stage-s-20261029
export START=REPLACE_WITH_ACTUAL_INSTANCE_START_UTC
export PRICE=REPLACE_WITH_APPROVED_HOURLY_USD
export USER_CHOICE=/workspace/REPLACE_WITH_REAL_COMMITTED_USER_CHOICE.json
export TIFS_PYTHON="$VENV/bin/python"
mkdir -p "$RUN_ROOT"
git rev-parse HEAD > "$RUN_ROOT/pre-p-code-commit.txt"
bash scripts/tifs_stage_s_setup.sh "$ASSETS" "$VENV" "$START" \
  --user-choice "$USER_CHOICE" > "$RUN_ROOT/setup.log" 2>&1
```

Run setup once for this shared session, before P. It creates/reuses the venv, installs pinned packages, verifies CLIP's exact commit, runs `pip check`, validates the chosen source inventory/assets, and writes `ASSETS/tifs-stage-s-setup-ready.json` and `tifs-stage-s-download-ledger.json`. It requires the choice but does not require a P selection that does not yet exist. A setup failure does not permit relaxed pins or a replacement baseline. The actual chosen ceiling applies already during setup, with one hour reserved for retrieval.

Before science, inspect setup-ready status, paid start/cap, package list, source/config/code/choice hashes and available disk. Scientific entrypoints bind the setup receipt and verified asset identities into run identity. Preserve these identities throughout P and S. Drivers force Hugging Face/Transformers offline mode; scientific work must not acquire missing assets or credentials.

## Stage P: calibration, measured P forecast, selection and veto

Run this section only when the pre-output choice says `stage_p=run`. Its first scientific actions use exactly the first two P tuning sources (544 and 1355), with retained F5, noise52 and x052 in immutable trial directories. These outputs are reused by rung one. No S source may be used for P timing, tuning or substitution.

```bash
bash scripts/tifs_stage_p_driver.sh "$ASSETS" "$P_ROOT" "$START" "$PRICE" "$USER_CHOICE"
```

The actual driver accepts exactly those five positional arguments. It invokes the stdlib selector's `plan`, `calibration`, `entrants`, `finalist-controls`, `advance`, `plan-check` and `finish` commands; no separate hand-written selection or manual winner is needed. Watch `P_ROOT/driver.log`, `selection.log`, `forecast.log` and per-trial prepare/clean/native/detect/quality logs. GPU processes run serially.

After the two-source calibration, `tifs_stage_s_forecast.py --stage-p-root` writes `P_ROOT/forecast.json`. It qualifies **P only**, using actual measured timings, loads, peaks, replay/gradient diagnostics and paid elapsed time. The conservative runtime reserves the **full P allocation again after calibration**, with slower-writer/control proxies and a 1.5 allowance; it does not subtract completed calibration work or automatically refresh the forecast at each rung. It can stop under a 126-hour cap even when the analytical middle scenario fits. The full P+S scenario remains unqualified until the independent S rehearsal measures all final paths.

After P resource qualification, the driver evaluates eight fixed noise/x0 by 52/46/42/38 dB robust-budget candidates on cumulative **4/8/16** tuning prefixes, with at most **8/4/2** entrants. Refinement remains 58 dB. Retained F5 is shared only under matching identities; finalist budget controls are required as specified by the frozen protocol. Maximum P work is 136 marked source-units, 136 repeated C0 source-directory units and 3,264 saved native attempts; these repeated units are not independent sources. No T4/T5, external-baseline or secondary-transform search is added to P.

Complete finite saved-RGB8 quality, required owner/C0 calls, all seeds, control comparisons and manifest/tape identities are mandatory. Fixed lexicographic ranking nominates exactly one winner before the eight veto-check sources are marked/read. A failed check cannot nominate a runner-up, change profile, retune, replace sources or select seeds. P cannot itself establish the S binding/security or article gate.

For allocated P evidence the status precedence is **RESOURCE_STOP, then INCOMPLETE, then observed scientific rejection**, including required retained/budget controls even when candidates already failed scientifically. Keep every failure reason. A missing, failed or resource-stopped P selection blocks S; the original default is not a fallback after choosing P.

Successful `finish` writes the default destination `research/tifs-20261028/stage-p/selected-config.json` and the selection evidence under `P_ROOT/selection/`, including `final-result.json`, `check-inventory.json`, rung decisions/inventories and nomination evidence. The successful selection must say SELECTED/PASS and ELIGIBLE_FOR_PROPOSAL, match the prechosen profile/receipt and preserve all config/source/evidence hashes. Its `execution_authorized=false` is intentional: analysis is not approval.

The post-P technical freeze commits **only the selected configuration under the already chosen profile**. Preserve the original code, base configuration, requirements, source/asset and setup identities; no code changes between P and S. A selection-only commit may create a new HEAD: record both the original science-code commit and this freeze commit so the same source code is traceable. The freeze consumes paid time and cannot become unbounded waiting on a running instance. Set the explicit selection path for the next commands:

```bash
export SELECTION=research/tifs-20261028/stage-p/selected-config.json
git rev-parse HEAD > "$RUN_ROOT/post-p-freeze-commit.txt"
```

If P was actually declined beforehand, skip the entire P section and use the original noise52 candidate under that real decline receipt. Do not pass a stale selection. The S driver automatically notices the committed default selection file if it exists: verify the fresh authorized checkout contains no old selection rather than deleting failed P evidence to obtain a fallback. P-declined S commands below use only `--user-choice "$USER_CHOICE"` and omit `--selection "$SELECTION"`.

## Stage S: complete two-source rehearsal before screen

After successful P and its freeze, run the full disjoint two-source S rehearsal with the same clock and choice:

```bash
bash scripts/tifs_stage_s_driver.sh "$ASSETS" "$RUN_ROOT" "$START" "$PRICE" rehearsal \
  --user-choice "$USER_CHOICE" --selection "$SELECTION"
```

This stops after rehearsal and forecasting; it does not start the screen. Default mode is also rehearsal. If P was prospectively declined, omit the selection flag as described above. Every S invocation, forecast and analyzer must resolve the same effective choice and selection paths/hashes.

Rehearsal includes all eleven arms: f6-noise, f6-x0, f6-codec, f6-generic, f5-budget, retained F5 r2, v5 r3, WAM, VINE-R, VINE-B and C0. All four F6 variants share the selected robust budget. `f5-budget` uses the selected robust budget with retained F5 objective and 150+50 updates; retained F5 r2 is unchanged. Budget F5 has 200 reader-gradient evaluations versus F6's 350 plus the x0 arm's 150 UNet differentiated graphs. Equal declared budgets do not establish equal achieved quality or equal compute, and a pass does not isolate denoiser causality.

The complete rehearsal has **22 clean, 264 native, 154 threat and 176 secondary** producer identities, **1,120 detector rows and 616 quality rows**. Its two donors and two separate targets are outside both P and S-screen sources. It measures all seven threat conditions, eight secondary transforms, readers and quality paths. Watch `driver.log` and logs under `rehearsal/`; `STAGE_START`, `MODEL_READY`, `UNIT_DONE` and `STAGE_DONE` include counts/time/memory. A long writer may not emit UNIT_DONE until it finishes; inspect process/GPU state without starting a duplicate worker.

Require finite nonzero clean/surrogate **and epsilon-input gradients**; an identity-only x0 gradient is insufficient. Require differentiable-projection agreement, the native schedule receipt, and native first-step epsilon/x0 parity on both rehearsal donors in every optimized R0/R1 cell, with independently rebuilt conditioning. UNet fp16, fp32 x0/VAE arithmetic, native guidance/conditioning and checkpoint behavior must work on the real pinned runtime. Separately require exact saved-RGB8 native C0 capture/replay and complete random-tape consumption. First-step forward parity does not validate the full attack gradient, and the posterior-mode one-step surrogate is not claimed identical to full sampled native denoising. P calibration requires these checks on its two sources too.

Checkpointing is non-reentrant and limited to writer gradient scopes; eval/frozen parameters do not by themselves disable its intended gradient path. Native generation, readers and metrics run without writer checkpointing. Measure recomputation, transfers, diagnostics and actual peak capacity. OOM or failed diagnostics cannot authorize a smaller surrogate, fewer cells or a changed precision policy.

Every producer artifact is hashed before journaling. Readers/quality consume saved PNGs, with explicit F6-to-F5 dispatch. Safety blocks keep their identity and original prompt/seed; do not disable checks or remove rows. Missing/failed dependencies remain unresolved.

## Stage S measured forecast and intact screen

The S forecast requires complete rehearsal inventories, writer checks, native parity, real timing/storage/memory evidence and the same selected execution identity. It includes **all elapsed setup/P/freeze/rehearsal/idle time**, loading overhead, 1.5 times intact screen variable work and one-hour retrieval reserve. Check peak memory against **measured device total minus 1.5 GiB**, projected remaining image/tape/log storage plus temporary peaks and 20% filesystem margin. Missing measurements mean INCOMPLETE; a failed capacity/time/storage bound is RESOURCE_STOP. The P forecast cannot certify these S-only paths. Every invocation/resume revalidates the current paid clock and matching device policy.

Inspect `RUN_ROOT/forecast.json`, full rehearsal manifests/check receipts, source assignment and selection/choice binding before continuing. Historical Phase A/B times and analytical 62/126/265-hour scenarios do not replace this measurement. If the intact screen does not fit the actual chosen cap, collect P plus rehearsal evidence and stop. No automatic extension or reduction of sources, steps, seeds, arms, controls or cells is permitted.

Only if this measured qualification passes, continue the already-authorized session:

```bash
bash scripts/tifs_stage_s_driver.sh "$ASSETS" "$RUN_ROOT" "$START" "$PRICE" full \
  --user-choice "$USER_CHOICE" --selection "$SELECTION"
```

For a P-declined session again omit `--selection`. The driver revalidates the rehearsal and forecast before the screen; completed terminal units are reused. Direct screen invocation cannot bypass the forecast/launch seal. The complete 16-donor, eleven-arm screen has **176 clean, 2,112 native, 1,232 threat and 1,408 secondary** producer identities, **8,960 detector rows and 4,928 quality rows**. One process owns the GPU at a time; reader/quality costs include decoder and CPU work.

VINE-B reads without the original message: q32/tag36 unique radius-four recovery, then raw masked-h32 recovery and unchanged F5 content-status functions. Inspect raw delivery, correction distance, ambiguous/no-codeword outcomes and both owner calls. VINE-R known-message 69/100 presence does not imply VINE-B payload recovery. VINE-B uses public redundancy, no secret ownership key or registry; h is conditional on q recovery. Do not alter payload/radius after outputs. The [payload interpretation note](../design/r2-payload-interpretation.md) distinguishes these endpoints; its hypothetical bit-error calculations are not empirical forecasts.

## Analysis, failures and resume

Exit codes are 0 (complete GO or successful rehearsal), 2 (observed scientific rejection/SCIENTIFIC_KILL), 3 (RESOURCE_STOP), 4 (INCOMPLETE), and other nonzero values (implementation/setup error). A stage's exit 0 is not a scientific GO. The S authority is `screen/analysis/analysis.json`, its gates, inventory and effective prechosen profile. **S retains its existing observed decisive-scientific-failure precedence**; do not replace it with P's required-allocation precedence or conceal accompanying resource/missing evidence.

The analyzer emits **both round1 and round3-proposed reports**. Only the pre-output selected profile determines the effective verdict. The proposed profile preserves absolute C/J 12/16, retained-F5 gains 4/4/3, R0 loss at most one, candidate clean F 15/16, strict candidate quality and primary negatives. It adds F5-budget quality/F eligibility and gains/paired quality against that control, while treating mechanism-ablation superiority/quality/F as secondary. It loses mandatory retained-F5 quality parity and superiority to every mechanism control; report those limits. Do not promote an inactive favorable profile after seeing outcomes.

Both profiles retain the fixed C/J definitions, conservative three-seed majority treatment and full inventories. Primary negative C/F calls and eligible T4/T5 D AND F binding gates remain required. Secondary outcomes have no selection weight but must be complete. Human operational-distinctness/visual judgments remain MISSING until a human supplies them; their absence cannot be fabricated into a positive binding/generalization claim.

Read `article-decision.json` separately: **VINE-B article numerical margins are unchanged**. Neither thesis GO nor a VINE-B win alone establishes novelty, publication readiness or TIFS acceptance. Inspect `numerical_thesis_gate_status`, `bound_carrier_delivery.csv` and `unusable_evidence`; a numerical pass cannot waive missing references, delivery/decode metadata, identity, quality or resources. Valid no-reads remain observations. Known-message presence and owner/content consistency stay separately labelled.

ForenMark was skipped at the earlier cutoff and remains full-text **UNINSPECTED**. Generic binding and surrogate ingredients have close prior art; the exact combination has not received priority clearance. Preserve the [Round 3 surrogate prior-art limits](../design/r3-surrogate-prior-art.md) and [result interpretation](../design/r3-result-interpretation.md). No article novelty claim follows from preparation acceptance.

A terminal journal row is not rerun. Interrupted units without terminal rows may resume only with identical commands/config/code/assets/choice/selection/start, retaining torn bytes and latest-row semantics. Never remove safety/error rows to manufacture completeness. Resource-stop markers block automatic retries. A code repair invalidates the same-run resume: preserve the failed run, declare a new output folder and remedy, and keep the original paid clock; no code change between P and S is part of this frozen plan. Any new design/spending decision remains prospective.

Use a foreground interrupt, let the process exit and retain partial evidence. Never run duplicate producers on one folder or leave an unobserved session past the cap. Per-unit deadline/next-unit checks and collection reserve remain necessary after forecasts; calibration cannot guarantee future latency.

## Retrieve the entire session and stop, never destroy

Reserve the last hour for collection and stopping. Retrieve the **entire P_ROOT and RUN_ROOT**, including failures, eliminated candidates, incomplete/resource-stopped trials, calibration, tuning, veto, nomination/rung/check evidence, S rehearsal and screen. Also collect the external **USER_CHOICE receipt and selected configuration even if either lies outside RUN_ROOT**, both code/freeze commits, setup log/ready/download ledger, requirements/environment versions, base/effective configs, source/asset manifests and hashes, originals/output hashes, tapes, writer/parity/gradient diagnostics, storage/capacity/timing measurements, forecast/launch receipts, logs and every analysis JSON/CSV. Do not retrieve successes selectively or omit P because only S was planned for delivery.

Saved-JSON S analysis may be rerun without models using the same paths:

```bash
"$TIFS_PYTHON" scripts/tifs_stage_s_analyze.py --out "$RUN_ROOT/screen" \
  --config research/tifs-20261028/stage-s/frozen-config.json \
  --user-choice "$USER_CHOICE" --selection "$SELECTION"
```

For P declined, omit `--selection`. Keep P selection evidence rather than recomputing a different choice. After collection is verified, Claude stops the instance using the provider controls. **Never destroy it**; destruction is the user's action.

Stage C still contains **120 primary plus 40 reserve NOT_DOWNLOADED identifiers**. It requires a separate prospective comparative/power/cost amendment and actual user approval. A P pass, S GO or this runbook authorizes neither acquiring those images, accepting SD3.5 terms, confirmation, publication nor submission.

## Validation boundary

Local validation is stdlib pure logic and syntax only: final author totals are 185 tests and 35 compilations. Bash/source compatibility was inspected, not scientifically exercised locally. Real package/model loading, fp16 backward support, nonzero epsilon gradients, native conditioning/parity, saved-RGB8 replay, source/runtime compatibility, achieved quality, host/device memory, timing and storage remain for the authorized server calibration/rehearsal. No scientific result or measured completion forecast is asserted here.

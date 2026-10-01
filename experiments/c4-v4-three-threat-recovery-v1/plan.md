# Recoverable v4 evaluation of the three proposal threats

This design replaces the all-generation-before-evaluation execution order, not the watermark algorithm or scientific criteria. It first evaluates the 401 retained images from the interrupted run, then allows 53 downstream regeneration candidates. One additional pending cell is quarantined because it may have been in flight at interruption. Every small unit must finish detection, quality measurement and durable evidence recording before another unit starts. A shutdown cannot be prevented by this protocol; durable recording limits lost progress to the current unit, and saved images remain usable without generating them again.

Related work is issue #18 and draft PR #67. The original proposal, research contract, scope guard, 38-task plan, native-2K and 6,900-source obligations remain unchanged. This is an exploratory image-domain v4 comparator, not acceptance of the original latent method. This request authorizes redesign only: no scientific execution or human approval is created here.

## Scientific settings remain unchanged

Use the original twelve-source clean and semantic cohort, original ten-source regeneration and copy-paste cohort, frozen 66 pair labels, four owner claims, public-derived external CLIP profile, 42 dB embedding setting, both 32-bit radii of 6, alpha 1e-6, all four binding modes, and original native clipping and RGB8 quantization. Regeneration retains VAE posterior mode separately from diffusion; diffusion strengths are .05, .1, .2 and .4 with seeds 0, 1 and 2 and the same pinned SD1.5/DDIM settings. No new model, data, threshold, key regime, seed or attack is selected from observed outcomes.

The original scientific acceptance file remains authoritative at SHA256 `6ab5bd251aa126cf59f894b2eefea1118e6739092caf3c87a8e7734a9306b5e6`. PSNR >35 dB, SSIM >.9 and LPIPS <.1, sufficient delivered marks, matched C0 controls, source-group analysis, semantic coverage and independent content review are not relaxed. Existing clean results and safety failures are already known; this is recovery of exploratory evidence, not fresh confirmatory preregistration.

## Preserve and classify the interrupted evidence

The parent run is `c4-v4-three-threat-dev-001`, approved source commit `0e91bd2ff4f7a17dc35868f734257c85ee855d01` and canonical execution-manifest hash `ce4eca20933618d96c5930abebf503f2e9e2aa353fe9e7c4d768c89c0e6e4f73`. Its results snapshot has SHA256 `490078f55aff806f93f187dd843ecad73d3bb646fdd238b709e9592363471ce6`. Never edit that run, its stale official receipt, original outputs or authorization.

The interruption cause is undetermined. The receipt still saying running is not proof of a live worker. No fault-recovery claim below assumes that the 16 safety rejections caused the interruption.

| Original evidence | Recovery action |
| --- | --- |
| 24 clean images and 96 completed calls | Verify exact files, call receipts and same-suspect features; inherit those calls and measure missing RGB quality |
| 190 saved regeneration images | Reopen, freshly encode each suspect, detect all four owners and measure source and immediate-input quality |
| 180 saved copy-paste and control images | Reopen, detect all four binding modes on identical pixels and measure recipient quality |
| 7 saved same-semantic transfers | Reopen, detect all four modes and measure recipient quality |
| 66 unperformed component comparisons | Compute the frozen q/H diagnostics from the original clean and marked inputs and their own verified feature records |
| 16 safety-blocked regeneration cells | Preserve terminal failures and their 64 missing detector calls; never regenerate or replace them |
| 53 downstream, unreached regeneration cells | Candidate generation only after existing-image evaluation; at most two matched cells per unit |
| 1 ambiguous pending regeneration cell | Quarantine `t3-190676-0.4-1-C1`; no generation or terminal receipt without a concrete reviewed disposition |

The parent worker executed T3 in the frozen inventory order and checkpointed each terminal image or failure, but never durably recorded attempt-start before the model call. The first pending cell, `t3-190676-0.4-1-C1`, immediately follows saved `t3-190676-0.4-0-C1`; its `NOT_RUN` status cannot establish whether it was attempted. Only the following 53 cells are classified unreached under that verified sequential path and checkpoint prefix. A nonsequential checkpoint invalidates this inference and blocks automatic scheduling. The ambiguous cell retains four unresolved calls; do not call them safety failures or definitively unattempted.

All 401 existing PNG hashes must match before adoption. Reuse a cached CLIP vector only with the exact saved suspect pixel hash, feature hash, checkpoint hash, normalization, transform/runtime and dimension; never borrow source features for an attacked suspect. New execution receipts link the original run and row, preserving inherited versus newly computed evidence. The stale running receipt is an input observation, not something this design rewrites.

The 537 original rows and 1,884 planned calls remain the denominator: 96 inherited + up to 1,720 new + 64 known missing + 4 unresolved. Of the new calls, 1,508 concern saved attacked images and up to 212 concern the 53 downstream candidates. Additional safety failures or incomplete metrics increase missing evidence. The unresolved cell remains unresolved until a separate concrete disposition; it is never silently excluded. With the existing missing controls, this recovery cannot satisfy the original complete-evidence joint acceptance rule; its value is actual threat measurements and an honest negative or inconclusive conclusion, not a forced pass.

## Small evaluation units

The metadata-only schedule in `schedule.json` assigns every original row exactly once across 237 units. The first 12 units each cover one clean C0/C1 pair. Next, a fixed round-robin order interleaves 20 copy-paste edge units, 66 semantic component units, 7 semantic-transfer units and 104 recovered regeneration groups. Then 27 generation units cover the 53 downstream candidates; some are single missing members of a partially generated pair. The last unit is the quarantined ambiguous cell, not an executable generation unit. Unit order uses frozen identifiers, never scores. The whole schedule cannot be called operationally complete while that disposition is missing.

A copy-paste edge unit contains at most nine image/control rows, or 36 detector calls. A regeneration unit contains at most the two C0/C1 members of one fixed source, dose and seed, or eight calls. Component comparisons use the same pair labels. A split pair keeps references to its already evaluated partner; neither member is invented, repeated or removed. Scientific source-group conclusions wait for all their planned controls even when an individual unit is operationally complete.

The invariant for each image is:

1. Verify an existing input. For a listed downstream generation candidate, atomically record `ATTEMPT_STARTED` with unique attempt ID, row ID, recipe and input hashes before any model call, then use the unchanged safety checker. No such record means the attempt is ambiguous on recovery, not available for automatic retry.
2. Atomically save RGB8 pixels, their hash and a generation receipt before unloading the diffusion model.
3. Reopen those exact pixels and compute or verify that suspect's own CLIP vector.
4. Run the declared owner claims or binding ablations; atomically record every successful call and every failure.
5. Measure RGB PSNR, SSIM and LPIPS against the declared reference roles. Identical-image PSNR uses an explicit identical status, not non-finite JSON.
6. Atomically seal the unit with hashes of its row results. Only then may the next unit start.

Release GPU generation components before loading evaluator components when memory requires it. Do not accumulate a new collection of unevaluated generated images. An algorithmic negative result or recorded safety rejection is evidence, not an infrastructure error; it does not silently disappear. A broken hash, model/runtime mismatch, missing required metric or evaluator failure stops the dependent execution queue and preserves its partial receipts.

A new safety rejection has a separate `NEW_SAFETY_BLOCKED` terminal receipt: row and attempt identity must match the durable attempt-start receipt, and failure evidence must bind its hash plus the same recipe and input hashes. Preserve the exact `safety_checker_blocked_output` reason, zero saved output, zero detector calls, four missing calls and `scientific_success=false`. This can seal operational failure evidence and allow the next independent unit; it is not an evaluated image, scientific success, exclusion or permission to retry. The reference checks receipt shape and cross-binding only; production must verify the actual durable bytes and hashes.

## Durable recording and recovery

Future reviewed adapters must use temporary files, flush and fsync, then atomic rename. Distinguish reserved, durably attempt-started, image-saved, detected, quality-complete, safety-blocked and sealed states. A sealed unit records its recipe hash, execution attempt, input-image hashes, output-result hashes and row inventory. An image-only or detector-only unit cannot be called complete. Distinct row and call IDs reject duplicates. Partial row receipts may be reported as partial evidence, never as a sealed unit or full study result.

If a process disappears after image saving but before evaluation, a separately reviewed recovery package evaluates those exact bytes; it does not call the generator again. If a unit already has a verified seal, later recovery reuses it. If a result is written but not sealed, verify that result and finish only its missing evidence. Inherited safety failures remain terminal. Ambiguous unrecorded attempts are not retried automatically; isolate them for a concrete recovery decision. Corrupt artifacts block their dependent unit and preserve the corruption evidence.

Exact runtime, profile, transform and input hashes must remain equal before combining inherited and new results. If they differ, do not silently pool results or recanonicalize images; stop for explicit compatibility review. No recovery claims that an interrupted execution completed, invents a final exit code, or changes Spec Kit state ownership.

## Process ownership and monitoring

Before any future launch, the reviewed Windows execution host must demonstrate that an official-runner invocation survives loss of its initiating chat/tool session. A single user-account local process may be started with a hidden window through the existing Windows facilities, but no service, daemon, new scheduler, installation or security change is authorized. This process-host adaptation is a required future implementation and test, not a capability established by the current design.

The approved entrypoint writes a heartbeat every five seconds, including execution identity, PID plus process-start identity, phase, current unit and last sealed unit. A PID alone is insufficient because it can be reused. During an active turn, the agent checks process identity and heartbeat at most once per 30–60 seconds. Between turns, only the existing task heartbeat checks; no new automation is added, and immediate notification while the host is unavailable is not promised.

A running receipt with no matching process is reported separately as interrupted observed, cause unknown. A live process with a heartbeat older than 120 seconds is stalled and needs a check; age alone never authorizes a kill, restart or claim of cause. Re-read the latest artifacts before a status report. At launch, report evaluated and sealed counts, not saved-image count as experiment completion.

## Required tests before execution

The new standard-library reference and its tests validate the proposed inventory, ordering, completion fields and liveness labels using fakes. They are not production fault recovery or evidence that background process ownership works. Future actual adapters must pass model-free failure injection after image rename, feature writing, each detector call, metric writing and seal rename; corrupted inputs, duplicate IDs, non-finite metrics, process loss and partial paired controls must be covered.

Acceptance requires that the evaluated prefix survives each injected failure, saved images are never regenerated, blocked cells stay blocked, no new unit begins before a valid seal and no absent worker is called running. Test a harmless official-runner fixture launched through the intended durable host, terminate its initiating session, and verify survival plus timeout/exit recording. If this fails, do not launch scientific work in that mode. WSL/host failure cannot be prevented; recovery after it requires exact approved evidence and no silent repeat.

## Execution contract and remaining work

Local-only planning retains RAM 6 GiB, VRAM 8 GiB and at most 2 GiB of new outputs, USD 0. Old images are read in place, not duplicated. Model reloads trade throughput for a small failure boundary; a provisional 2–8 hour envelope for the complete recovery is not measured. Recheck actual RAM, VRAM, disk and absence of competing workers at launch. Resource guards are polled rather than OS allocation limits. No paid compute, model/data/software download, public push or publication is authorized.

The future exact execution bundle must list every official-runner unit manifest, reviewed entrypoint SHA, clean code commit, inherited inputs, runtime/assets, seeds, expected outputs, per-unit safety timeout and total budget. Planning timeouts are 1,800 seconds per unit and an 86,400-second total safety budget, not research deadlines or evidence of guaranteed durations. A concrete batch decision may cover its explicitly listed exact manifests once; it cannot approve unknown future artifact hashes. Recovery of an interrupted unit needs a newly reviewed concrete evaluation manifest and actual decision unless it was already exactly listed and unused. Never reuse the consumed parent-run approval.

No production evaluator, durable host, exact new execution manifests or scientific execution are delivered by this design. Their implementation, fault-injection tests and bounded independent exact-package review remain before a new execution decision. The official design helper cannot validate a complete execution package until those entrypoints and manifests exist; validating the experiment schema alone does not imply readiness.

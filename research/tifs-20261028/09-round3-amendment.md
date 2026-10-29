# Round 3 pre-output amendment

Date: 2026-10-29. Base: `01bf24f` (Claude's Round 3 brief), following reviewed Round 2 `2c41d5f`. No Stage P or Stage S scientific outputs exist. This amendment changes preparation only. No user approval, experiment result, human judgment or publication readiness is created here. The retained F5 r2, v5 r3, profiles, thresholds, artifacts and held-out sources remain unchanged.

## R3-1: native denoiser-aware alternative

Add `f6-x0`: posterior-mode encoding, a deterministic timestep draw within each native 20-step img2img window, native epsilon prediction, float32 x0 reconstruction and decoding into the unchanged F5 reader. It optimizes R0 .2, R1 .1 and R1 .2; K3 remains optimization-excluded. Keep `f6-noise`, `f6-codec` and `f6-generic`. Default candidate and effective numerical gates remain the Round 1 F6-noise design until the pre-output user choice and, if selected, Stage P freeze. An additional arm cannot silently rewrite the original ablation thresholds.

The pinned native R0/R1 settings use empty prompts and guidance 1, so their exact native denoiser has one branch. SDXL pooled embeddings and time IDs are assembled by the native pipeline helpers. UNet weights/input are fp16 with autocast disabled; x0 arithmetic and VAE paths remain fp32. Frozen eval UNet/VAE checkpoint flags are enabled only during writer gradients and restored before native operations. The one-step estimate is a surrogate, not full denoising; posterior-mode and differentiable resizing remain explicit approximations. Optional k-step is omitted to keep the search and memory cost bounded.

Require finite nonzero clean, surrogate and epsilon-input gradients during server rehearsal. Wrap the native first step on both rehearsal donors in all three optimized cells; independently rebuild conditioning, compare epsilon, and bound x0 differences caused by native fp16 arithmetic. The existing exact C0 capture/replay check remains. Measured peak memory must stay below device total minus 1.5 GiB; no numerical/GPU fit claim follows from local mocks. See `design/r3-denoiser.md` and `stage-s/writer-implementation.md` for inspected diffusers 0.35.1 sources, precision and parity scope.

The original Stage S protocol and Round 2 amendment remain historical freezes; the cumulative Round 3 config/inventory and sections below specify prospective additions. Intermediate commits remain preparation-INCOMPLETE pending integration and the fresh independent review.

## Pre-output choice policy

All alternatives remain proposals. Claude must record the actual gate/profile and compute choice in a commit **before any server scientific output**, including Stage P; the later post-P freeze records the selected configuration under that already chosen profile. No outcome-dependent profile choice is permitted.

## R3-2: bounded writer selection and budget control

Stage P uses exactly the 24 metadata-verified development sources outside Stage S: 16 tuning and 8 veto-only check. Eight alternatives combine noise/x0 with robust PSNR budgets 52/46/42/38 dB; refinement remains 58 dB. Successive halving evaluates cumulative 4/8/16 tuning prefixes, allocating 8/4/2 entrants and nominating one. Shared retained F5 and finalist F5 budget controls keep the worst-case allocation at 136 marked source-units and 3264 native saved-image attempts. The check cannot nominate a runner-up. Missing contenders block progression; observed scientific failures and resource stops remain distinct. See stage-p/PROTOCOL.md for exact ranking, futility, quality and negative-call predicates.

The chosen Stage P profile is recorded before its first scientific output. Successful selection is hash-bound to that choice, the base config, complete tuning/check evidence and exact parameters. Stage S consumes it automatically or by explicit path. If the user chooses P, a missing/failed selection cannot fall back to the original candidate. The original noise52 writer remains available only when P was declined beforehand. K3 is excluded from gradients but seen by selection, so it is not an unseen-family selection test; future SD3.5 is the proposed unseen Stage C family.

Stage S adds f5-budget beside retained F5 r2. It uses the original robust writer with the selected robust budget, 150+50 reader updates and unchanged fragile writes; retained F5 r2 remains unchanged. All four F6 variants share the selected robust budget. Nominal budget equality is not achieved-distortion equality: paired measured quality against the budget control remains required in the proposed profile. The complete 11-arm screen has 176 clean,2112 native,1232 threat and1408 secondary images,8960 detector rows and4928 quality rows.

## R3-3: proposed gates and analytical sensitivity

The committed registry exposes round1 (effective default) and round3-proposed (inactive proposal). The analyzer emits both; the main verdict is only the profile selected before outputs. The proposed profile preserves C/J 12-of-16 absolute foreign retention, retained-F5 gains 4/4/3, R0 loss at most 1, clean F 15-of-16, strict quality on every candidate/control source and all primary negative gates. It adds 4/4/3 gains against F5-budget and paired LPIPS<=+.005/PSNR>=-1dB quality relative to that control. Ablation gains and their clean-quality/F outcomes become fully measured secondary diagnostics. VINE-B article margins remain numerically unchanged.

This loses the automatic claim of near-quality parity to retained F5 and of superiority over every mechanism control. The budget control is not computation-matched (200 versus350 F6 reader gradients plus surrogate paths); a pass cannot attribute improvement uniquely to the denoiser or claim compute efficiency. Source-majority and paired-gain probability grids in design/r3-gate-analysis.md are exact sums under explicit hypothetical assumptions, not scientific outputs or calibrated pass probabilities. Rough subjective complete-execution thesis GO estimates are 15% current and 35% recommended (broad 5-30% and 15-55% judgment ranges); article conditional-GO estimates are 5% and 10%, not publication-acceptance probabilities.

## Decisions for the user: recommended package

- **Stage P:** run the eight fixed noise/x0 by 52/46/42/38 configurations, 16 tuning plus8 veto-only check; recommendation run, accepting up to 136 marked source-units and no fallback after failed selection.
- **Gate profile:** retain round1 or choose round3-proposed before any server output; recommendation proposed, preserving absolute/security bars while losing mandatory mechanism superiority and retained-F5 quality parity.
- **Budget-control interpretation:** use unchanged F5 objective at the selected robust budget with measured quality noninferiority; recommendation yes, calling it optimization-budget-matched rather than exact perceptual-quality- or computation-matched.
- **Ablations:** keep all observations but make their superiority/quality/F gates secondary under the proposed profile; recommendation yes, so a strong mechanism control is reported honestly rather than automatically killing the empirical construction.
- **K3:** keep it gradient-optimization-excluded in the executable search, or defer for the separately designed [K3-in amendment](design/r3-k3-in-deferred.md); recommendation excluded, explicitly selection-seen after P. SD3.5 remains reserved for an approved future unseen-family Stage C.
- **Absolute/article bars:** retain 12/16 and all Round 2 VINE-B numerical margins; recommendation retain, with no retrospective lowering.
- **Paid-session cap:** keep 15 h effective until an explicit expanded cap is chosen; the R3-4 scenario arithmetic and measured qualification determine whether any larger proposal is defensible.

Claude records the actual combined choice and its evidence reference in a committed receipt before setup/server outputs. This session creates no approval receipt. A post-P freeze records selection under that existing choice; it cannot choose a more favorable gate after seeing outcomes.

## R3-4: one paid clock and explicit cost uncertainty

The [cost inventory](stage-p/round3-cost.md) prices the complete 136-mark Stage P allocation and 180 marks across Stage S rehearsal/screen, including native replay, diagnostics, UNet backward/checkpoint recomputation, transfers, readers and metrics. Fast/middle/stress assumptions yield 61.9951/125.8175/264.9849 hours after allowances, rounded to 62/126/265 hours. These are hypothetical timing scenarios, not measured GPU performance. The middle 126-hour planning proposal is USD 56.70-75.60 at the inherited USD .45-.60/hour assumptions; no live offer or spending authorization is asserted. The smallest empirically defensible cap remains unknown until server calibration.

Recommend considering 126 hours only as a prospective maximum under the declared middle assumptions, with a separately committed actual user ceiling and mandatory measured Stage P and Stage S qualification. The runtime forecast is deliberately more conservative than the nonduplicating scenario: it charges full P after calibration and slower measured writer proxies. It may stop even under the proposed cap. No automatic extension, smaller inventory or reinterpretation as scientific failure is permitted. Setup, P, freeze, S rehearsal/screen and retrieval share the actual instance start. The profile choice is committed before any P output; post-P freeze records only the selected configuration under that choice.

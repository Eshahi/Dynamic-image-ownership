# C: one final fixed public-carrier margin amendment

Version **`m1-progressive-q5m5-design-v1`**, 2026-10-04; method escalation **gpt-6-astra/high**. Prospective design only: implementation waits for parent review; no scientific model execution, download, commit, held-out access or retained-output edit occurred in this task.

**Freeze one candidate, C-Q5M5: retain the same nearest-five-vote objective, eta100 and final-five-step window, and increase only the signed coefficient margin from.3 to.5.** Do not run a six-vote branch or a margin grid. The competing nearest-six/margin.3 possibility was inspected only through the two bounded coefficient-space probes below. C-Q5M5 gets one complete clean/VAE screen and, only if all gates pass, the already defined conditional T3 extension. This is the last scalar/repetition adjustment of the current public-carrier branch on these four prompt/seed blocks.

## Why this amendment rather than a sixth vote

The [completed Q5/EQ5 result](m1-progressive-vote-margin-results.md) establishes that the Q5/.3 operator's quality passes8/8, clean presence passes8/8, but extra-VAE presence passes6/8. All eight terminal latent words are exact. The two failed original-word outputs lose majority votes after decoding/re-encoding, despite zero intended corrected-clean loss at each guided update. Several clean decision margins have already fallen to.008–.024; seed1002 bit15 goes from terminal.32364 to extra-VAE-.18518. More scalar optimization of the same.3 inequality cannot cure a channel not represented by that loss.

Candidate fixes have distinct costs: requiring six votes adds potentially expensive naturally opposite-sign coefficients; increasing the margin strengthens the existing cheapest five. Actual Q5 clean quality leaves at least2.846346dB PSNR headroom, with seed1001 complement the tightest case. This motivates checking the cost of the two preselected alternatives before running either, without extrapolating a global decoder noise model.

The read-only algebra script [m1_progressive_redundancy_algebra.py](../scripts/m1_progressive_redundancy_algebra.py) consumes the pinned stage-diagnosis JSON and preserves its receipt. Its output [m1-progressive-redundancy-algebra.json](m1-progressive-redundancy-algebra.json), SHA-256 `e7b8f33e2bb027106c978a31c7c7412658bf9722e6397411b31f0379e5572a10`, contains all per-block numbers and script/input hashes. No model, image pixels or held-out sample is used.

First, exact nearest-halfspace projection costs on the **old C0 terminal coefficient vectors** are:

|Seed / word|Five/.3 squared cost|Six/.3 squared cost|Five/.5 squared cost|Observed Q5/.3 PSNR|
|---|---:|---:|---:|---:|
|1000 / original|8.696|17.606|17.757|39.588|
|1000 / complement|3.191|8.926|8.138|44.154|
|1001 / original|5.145|15.347|10.567|40.267|
|1001 / complement|9.664|20.942|17.527|37.846|
|1002 / original|10.552|25.469|18.393|41.281|
|1002 / complement|5.897|14.809|11.493|43.613|
|1003 / original|7.914|18.201|15.876|44.106|
|1003 / complement|3.283|9.420|7.654|47.531|

Five/.5 is cheaper than six/.3 on7/8 coefficient vectors and gives cost ratios1.743–2.550 relative to five/.3, versus2.025–2.983 for six/.3. In the tightest observed quality case its ratio is1.814, versus2.167 for six/.3. The actual pixel-MSE growth factor that would reach35dB there is1.926. **These quantities inhabit different spaces:** the juxtaposition favors a lower-cost candidate but does not establish that either candidate preserves PSNR, or that pixel MSE is proportional to this coefficient cost. SSIM and LPIPS still require actual measurements.

Second, a deliberately limited frozen-residual stress probe projects the recorded Q5 terminal coefficients onto either new inequality, then adds the **old measured terminal-to-extra-VAE coefficient difference unchanged**. Five/.5 yields match counts `16,16,16,16,15,15,15,16` in seed1000–1003/original-then-complement order; six/.3 yields `16,16,16,16,16,16,14,16`. Both clear14/16 in this artificial calculation, so it does not uniquely validate either. Five/.5 has a lower projection cost in the difficult-quality block and a less marginal minimum count in this probe, providing a bounded reason to choose it first and exclusively. The remaining five/.5 stress errors are seed1002 original bit15, seed1002 complement bit14 and seed1003 original bit10.

This stress probe is **not a VAE simulation or a scientific image result**. The VAE is nonlinear; changing the mark changes the whole denoising trajectory, decoded image and channel residual. It also projects the endpoint directly, whereas actual guidance acts on predicted-clean states before DDIM transport. Do not count these eight vectors as new trials, assert actual15/16 recovery from them, or reuse their numbers as T3 evidence.

## Exact operator and controls

Retain the accepted Q5 implementation's frozen selection rule and normalization. For each group of eight current ordinary predicted-clean coefficients c_j and payload sign y, set `v_j=max(0,.5-y*c_j)`, select the five smallest `v_j^2` using the original within-group index to break ties, and use `L=sum(selected v_j^2)/128`. Gradient is `-2*y*v_j/128` on the selected five, zero elsewhere; use the same orthonormal DCT adjoint and eta100. Selection is frozen during that gradient calculation and recomputed at the next guided step. No sixth vote, active-mask leakage, decoder gradient, source residual, new threshold, altered payload or CFG-order change is allowed.

Guide only indices45–49 (timesteps81,61,41,21,1) of the existing SD1.5 fp16 DDIM50 schedule, sampler eta0, CFG7.5, post-CFG clean prediction, channel0, original ordered128 DCT positions/band16..48, eight repetitions and same four prompts/seeds1000–1003. Other steps are the exact old unguided path. Original/complement words remain `1011010001101001` and `0100101110010110`. Detector remains the identical blind VAE-mode/DCT/strict-positive majority reader, tie to0, presence>=14/16. Neither prompt, seed, C0 nor selected-five indices are available to it.

For each seed run exactly five arms, in this order:

1. C0 replay.
2. C-Q5/.3 original-word replay.
3. C-Q5/.3 complement-word replay.
4. C-Q5M5/.5 original word.
5. C-Q5M5/.5 complement word.

This is **20 generations,1000 batched-CFG U-Net calls,40 primary clean/VAE image conditions**,80 endpoint stages and4000 step-stage records under the current four-state trace schema. Candidate denominators are eight clean images and eight additional-VAE images; replay controls add12 clean and12 VAE images. There are only four reused development clusters. Retain the fixed64-query panel separately for each primary readout:2560 dependent native queries and, if retained,2560 image-DCT diagnostic queries. It is not an all-negative gate or calibrated FPR estimate.

Source replay reference is completed MAIN `.thesis-build/dev-runs/20261004-0937-progressive-vote-margin`, `run.json` SHA-256 `38241d538c242bd5181f3d2cbc3d750488a97d0f4103445be5d9c73741886530`, commit `7be2a6c`. Verify source schema/config/completion, all40 newly planned units and all **24 old replay PNG** receipts (four seeds x three replay arms x clean/VAE). New replay PNGs must match their old hashes exactly; no claim of old endpoint-latent parity without an actual comparison. Same-seed initialization hashes must match across all five arms. Preserve a mismatch as an attribution failure; do not repair it by choosing another source output.

Carry forward the existing full coefficient/objective/precision/selected-index traces and latent/decoder arrays. Each arm's target-MSE/margin labels must use its actual.3 or.5 setting. Endpoint stages remain terminal predecode and clipped float as oracle diagnostics, clean RGB8 and additional-VAE RGB8 as eligible image detections. Record raw extracted bits, all reference matches, per-group votes and signed margins to enable direct comparison with the old failures. No best-word selection, per-seed margin, failed-cell replacement or corpus-dependent detector branch is permitted.

## Gates, conditional T3 and finite stopping rule

The new candidate qualifies only with complete/hash-verified inventory, exact control replay, C0 absent against both words on clean and VAE for all four seeds, **all eight** candidate clean images satisfying PSNR>35, SSIM>.9, LPIPS<.1 versus new same-seed C0, and **all eight** candidate images reaching>=14/16 both clean and after the additional VAE cycle. Recompute quality and matches from numerical metrics/raw bits; a rounded display or stale success boolean cannot override a strict boundary. Do not average away a failure. Human visual assessment stays absent.

If it passes, freeze its source run hash and run the already accepted conditional T3 extension on all eight candidate clean PNGs plus all four C0 PNGs: strengths.1 and.4; fresh DDIM scheduler per image/strength;20 inference steps; empty positive/negative prompts; CFG1.0; sampler eta0; attack seed0 shared in every block. This produces **24 new attacked images**, nominal120 U-Net calls (12 x(2+8)), with actual step/call traces checked. Preserve the hashes of all12 reused clean inputs, all24 outputs and all raw readout words. No hand-selected source image, regenerated source or arm override is allowed.

The fixed T3 gate remains all eight marked images>=14/16 and all four C0 images below14/16 against both words at **each** strength. A.1 success and.4 failure is a graded measured outcome, not a joint pass. This screen still tests public carrier feasibility, not dual binding, T4/T5, authentication or a new independent validation set.

**Finite stopping rule:** after this one complete scientific clean/VAE attempt (and its one conditional T3 extension if eligible), close the current *fixed public DCT carrier with scalar five/six-vote redundancy tuning* branch if any required gate fails. Do not try.4/.6 margins, six/seven votes, alternate window lengths, thresholds, bit subsets, favorable seeds, or another payload on these blocks. Retries are allowed only for a documented execution/provenance defect and must use unchanged scientific settings in a fresh retained run directory; a genuine low bit count or quality failure is not such a defect. Repeated environmental failure must be preserved, not converted into a scientific ceiling.

Closing this bounded branch is **not family-C exhaustion or a global theoretical ceiling**. The report should list the measured best quality/clean/VAE/T3 tradeoffs and the finite tested operator set. Further C work would require a separately versioned *mechanism* amendment that models the observed codec channel during embedding—for example an explicitly decoder-aware objective with a fixed computation budget—and an a priori reason it can fix the localized failure within measured quality constraints. That would usually remain a family-C amendment if the mark still lives in guided DDIM predicted-clean latents; naming a new loss does not create another substantially different family for M1's three-family exit. A changed signal location/reader/embedding architecture requires explicit taxonomy and comparison with the already explored decoder-aware A branch. Do not count administrative renaming as research breadth.

If all gates pass, freeze C-Q5M5 as the public carrier candidate and move to a separate dual CLIP+pHash+OwnerID binding/three-state design; do not keep tuning its carrier on the same four blocks to improve reported means. Both stopping outcomes yield a concrete next research decision without claiming these development trials complete M1.

## Execution limits and necessary tests

USD0, pinned local assets only, no new model/download/training. Clean/VAE run cap300 seconds,10 GiB allocated GPU or free memory minus512 MiB,16 GiB process working set,350 MiB artifacts; require at least1 GiB free after headroom. The measured24-generation Q5 run took142.703 seconds/120.4 MB artifacts, so these caps have headroom but are not guarantees. Conditional T3 cap180 seconds, same memory limits,150 MiB artifacts. Queue GPU work sequentially and retain planned/started/failed/missing rows; never overwrite old runs or orphan a child process.

Before GPU execution, commit exact runner/config/spec and test: the margin is the only candidate operator change; stable five-member ties and zero gradients on satisfied/unselected coordinates; unchanged eta100 scaling and DCT adjoint; exact old Q5 original/complement and C0 arithmetic on synthetic fixtures; paired initialization;20/40 inventory;24 replay receipts/mismatch handling; unaltered blind reader and14/16 boundary; strict quality limits and all-eight gate; source hash checking and old-output immutability. Conditional T3 requires its separate exact manifest and completed-source gate before GPU loading. This document author has not implemented or executed either stage.

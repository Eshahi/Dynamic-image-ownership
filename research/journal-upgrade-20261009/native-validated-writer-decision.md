# D2: native-forward-validated proposal writer

2026-10-10. Codex method-design agent, gpt-6-astra, high effort. Prospective USD 0 development decision; no implementation or experiment performed by this agent.

## Decision and scope

Proceed with one bounded **D2** screen. Use native autograd only to propose directions; accept an update only when its actual saved-RGB8 nine-branch loss decreases and its hard clean constraints pass. This is scientifically legitimate because acceptance does not rely on the direction being an accurate derivative. It changes the optimization algorithm, not merely the wording of the failed derivative requirement.

D1 and D1N remain failed, with no candidate produced and no native utility result. D2 makes no accurate-gradient, local-convergence or general-optimization guarantee. It is another algorithm in the same image-domain refinement family, not a third independent family or a proposal-native latent watermark. Its engineering novelty does not establish publication novelty. The hypothesis is only that this particular heuristic can propose useful feasible RGB8 moves on the fixed development set.

Evidence inspected: `ddim-writer-amendment.md`, `ddim-numerical-decision.md`, the channel/feasibility code, and MAIN `.thesis-build/dev-runs/20261010-1202-ddim-convergence/run.json` at df24e733f96403efd11eeebe8a13a14666c0063e. The TF32-disabled run completed in 89.984 s. At .1, AD was -2771.804 and the four FDs were -424.272, -763.162, -1238.078, -1755.059; at .2, AD was -2411.553 and FDs were -472.975, -852.452, -1300.469, -1711.657. Neither strength passes the required two-smallest-scale gate. This is negative diagnostic evidence, even though all secants point downward. Peak allocated memory reached 18.028 GB under Windows oversubscription; it does not demonstrate fitting fp32 work inside 12 GB VRAM.

No more epsilon trials, fp32/TF32 diagnostics, source replacement, loss-scale search or relaxed convergence gate belongs to D2. The old three-proposal native utility stage was never observed, so it remains a genuinely unobserved, cheap way to kill the new heuristic. Its selection is nevertheless informed by prior development failures and must be labelled exploratory.

## Fixed objective and observations

Retain RC3 final RGB8 as the start for every source, F5-RC1 as the detector, the same intended q and frozen operational h, and all D1 keys, tables, whitening, thresholds and semantic/content rules. Preserve the twelve-source order and exact nine branches from D1: clean; SD1.5 VAE; SDXL VAE; DDIM .1 and .2, seeds 0-2. Use the pinned native half DDIM channel with exact RGB8 input/output conversion, actual posterior sampling, empty prompt, guidance 1, eta 0 and 20 nominal steps.

For each branch retain `L_b = relu(9-score_b)^2 + mean(relu(1-gap_bj)^2)`, and `L(x)=max_b L_b(x)`. This is a forward-measured training proxy, not the detector's full semantic acceptance predicate. Exact q or lower loss still need not improve T3 semantic acceptance. Optimizing these six DDIM identities reuses development evaluation identities and proves no independent generalization.

Use the full existing native autograd graph and unit backward scale solely as a proposal generator. Its RGB8 straight-through and half-precision backward remain unvalidated surrogates. Do not detach the denoiser, substitute a mode posterior or use an identity backward for diffusion. Internal pre-checker tensors may supply losses only; every reported attack outcome must use the unchanged official pipeline, safety checker and validation path.

## Cheapest decisive screen

Commit this protocol and implementation before execution. In a fresh native process, confirm exact RNG/timestep/RGB8 parity at source 1675, seed 0, both strengths; record peak allocated/reserved memory and runtime without inferring residency from successful completion. No fp32 promotion is involved.

Before outcomes, implementation coverage also includes the six native DDIM identities on utility source 468505. These additional parity observations check the exact operator used for its loss; they do not add candidate configurations or count as independent attack-success observations. Their cost stays inside the 300-second screen cap.

Use only fixed utility source 468505, chosen before this screen because its prior RC3 .1/seed-1 exact-q loss was recorded. Evaluate the complete nine-branch baseline, with finite values and all branch details. Require a positive worst-branch loss and finite nonzero native input gradient of that actual loss, choosing the first worst branch in declared order. All-inactive loss despite the retained wrong-q identity is an unresolved consistency failure; do not choose another source or use the linear diagnostic as a utility substitute.

Let x0 be its RC3 pixels, u its clean source, n the RGB component count, B=sqrt(n)*10^(-52/20), and T=sqrt(n)*10^(-35.1/20). Test all three proposals `x0 - a*B*g/norm(g)` with a=.10,.50,1.00. Apply the existing two-ball/box projection, save RGB8, and re-read the saved pixels. Evaluate every branch of every proposal; report infeasible proposals as such without substituting a different step. Discard all screen outputs afterward.

A proposal is eligible only if both its projected continuous pixels AND authoritative saved pixels lie inside both balls and [0,1], clean exact operational q/h and both_match hold, PSNR >35, SSIM >.9 and LPIPS <.1 hold, and `L(start)-L(proposal) >= max(1e-6, 1e-4*L(start))`. All strict inequalities retain their original meaning. This fixed positive decrease margin avoids counting an arbitrarily tiny numerical fluctuation as progress. Do not tune it after outcomes.

At least one eligible proposal is required. Report all three losses, clean metrics, rounded distances, changed-pixel counts and rejection reasons. If none qualifies, stop D2 before twelve-source writing: the fixed proposal heuristic failed its cheapest utility test. Do not switch objective, gradient scale, source, step lengths or precision. A failure is local evidence, not proof that any DDIM-aware method is impossible.

## Fixed global writer after screen success

Use exactly **20 logical iterations** on each source, in the original order. This is D2's new bounded algorithm, not D1's unchanged 40-step schedule. Initialize the state to RC3 RGB8 and require all screen clean/feasibility constraints. Every retained state is authoritative RGB8; there is no hidden continuous accumulator or later h restoration.

At each iteration, use the current complete nine-loss vector, choose its first maximum and calculate one unit-scale native gradient there. For iterations 0-9 use a=.10; for 10-19 use a=.025. Propose the same three globally fixed lengths aB, 5aB and 10aB along that direction, always measured from the current state but projected into the original x0/u balls. Evaluate all three saved-RGB8 proposals with the same full eligibility rule as the screen. No extra backtracking or extrapolation is allowed.

Choose the eligible proposal with smallest nine-branch maximum, ties resolved by proposal order. Otherwise retain the current state. This is a fixed per-iteration acceptance policy applied identically to every source; it is not a source-specific writer or a choice of best final checkpoint. Log all three proposals, including rejected quality and loss outcomes. Cache the complete loss vector belonging to the selected saved state; never mix losses from different states or seeds.

If all nine losses and hinges are exactly inactive and full clean/feasibility checks pass, remaining iterations are declared no-ops. If no proposal is eligible at an unchanged state, identical iterations in the SAME schedule phase are exact no-ops: advance directly to the next phase, which must still be tested. A zero/nonfinite heuristic gradient with positive loss terminates that source's updates as stalled/invalid, retaining its current pixels and recording the reason; do not manufacture a stationary optimum. Final qualification still applies to every source. No extra direction is drawn.

Each accepted state strictly decreases the measured nonnegative objective by at least the fixed margin; that is the limited monotonicity claim supported by the acceptance rule. It neither proves convergence to a useful solution nor preserves individual branch losses. Conflicting branches, rounding, distortion and fragile-read constraints may leave the method stuck. Final outputs are the last states after this fixed policy, not smoke images or per-source best checkpoints.

## Scientific qualification and downstream work

All twelve final saved images must pass PSNR >35, SSIM >.9, LPIPS <.1, exact operational q/h and both_match. Require deterministic SD1.5 VAE joint readable/exact-q and semantic acceptance on 12/12, SDXL at least 11/12; report SDXL 12/12 preservation separately. Round-trip feasibility and clean checks are additional D2 constraints, not replacements for these prerequisites. Failed or missing images make the candidate ineligible.

If prerequisites pass, run the complete unchanged official matched T3 .1/.2 seeds 0-2 grid and the existing assessors. Require fixed-I semantic 29/29 at .1 and 28/28 at .2, exceeding retained v5 27/29 and 18/28; preserve every available frozen exact-q and J-positive identity separately using `frozen_sets()`; require zero observed C0/wrong-owner detections. Frozen J totals remain 27 and 20 among 35 available C1 slots per strength. Gains cannot compensate for obligated identity losses. Keep blocked/missing/observed denominators explicit and shared controls labelled; never replace seeds or drop failures.

Only a T3 survivor advances to the unchanged scoped T4/T5 and delivered-binding work, with performance at least retained v5 where endpoints are identifiable. The inherited all-alpha T5 panel cannot certify distinct-owner attribution. Preserve public-recipient synthesis as an authorization counterexample, absent fresh calibration as a limitation on population FPR, and all historical M1/M2 numbers. A proxy-loss improvement is neither a journal milestone nor a revised historical gate.

## Finite cost and exit

Authorize one new USD 0 development study on the basis of this new acceptance algorithm, not leftover D1 budget: total <=5400 seconds, comprising screen <=300, twelve-source writing and qualification <=3300, and official T3/summaries <=1800. Include loads, evaluations and failed attempts in each cap. No complete screen retry is allowed. A coding, parity or numerical failure is recorded and stops this fixed study; a further study needs a new method decision, not an automatic retry.

Before twelve-source writing, use measured screen throughput to conservatively bound all 240 logical iterations: at most 240 full native gradient computations, 720 complete nine-branch proposal evaluations and clean/quality checks, plus twelve baseline and final qualifications and load time. Use the slowest measured relevant gradient/proposal/qualification time; include every branch. Require the projection to fit 3300 s. Do not shorten the declared schedule or omit a branch to fit after seeing outcomes. Stop as budget-infeasible if it does not fit. Shortcuts may save time but are not assumed when qualifying throughput.

The hard finite search has one direction and three proposals per logical iteration, twenty iterations per source, twelve sources, and one predeclared smoke source. No source-specific tuning, mixed final writer, extra seeds, extra epsilon trials or held-out access is permitted. Ordinary committed code, run.json, per-source records and retained failed outputs suffice; build no new execution infrastructure. A cap interruption leaves an incomplete, ineligible candidate.

Report one of: native parity/implementation failure; no useful fixed proposal; budget infeasible/incomplete; clean/VAE prerequisite failure; T3 continuity failure with lost identities; or T3 survivor eligible for the existing downstream work. Preserve D1/D1N failures next to the D2 record. If the screen fails, derive a different proposal mechanism or representation from the observed obstruction in a separate bounded design; do not keep renaming this heuristic until it succeeds.

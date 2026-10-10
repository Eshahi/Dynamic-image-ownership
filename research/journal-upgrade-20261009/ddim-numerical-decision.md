# D1 failure and prospective D1N numerical continuation

2026-10-10. Codex design-escalation agent, gpt-6-astra, high effort. Decision written before the four-scale convergence diagnostic outcomes. This file authorizes no additional method, source search, threshold tuning or paid computation. It changes no historical gate.

## Decision

Close original D1 as **smoke infeasible under its declared derivative criterion; complete retry exhausted; no candidate written**. Its failed records remain authoritative. Permit exactly one separately named continuation, D1N, only if the bounded diagnostic below passes. D1N retains D1's mathematical writer, RC3 initialization, objective, decoder, targets, 40-step schedule and all scientific qualification gates. It changes the numerical diagnostic, and retains the already disclosed native unit loss scale. This is a prospective continuation after failure, not a retroactive D1 pass, a second independent experiment, or a substantially different design family.

It is defensible to retain the unchanged writer when its preliminary diagnostic tested too large a perturbation to approximate a local derivative: correcting a graph test need not change the algorithm it tests. That explanation is conditional, however. Finite-difference convergence would support local consistency in the explicitly diagnostic operator; it would not show that native-half gradients are accurate derivatives of RGB8 or useful at the actual update scale. The separate rounded utility gate remains indispensable.

## Evidence and mechanism

Inspected internal sources: `ddim-writer-amendment.md`, `scripts/journal_ddim_channel.py`, `scripts/journal_ddim_feasibility.py`, the retained retry `results.json`, and authoritative MAIN STATE.md. No external claim or GPU run was made by this decision agent.

The first smoke at f6260a0 established .1 native RNG/timestep/RGB8 parity but returned zero input gradient with the fixed 1/1024 backward multiplier. At 10ccbd5, the fixed three-scale diagnostic returned rescaled norms 0, 2.643683 and 2.924345 for multipliers 1/1024, 1 and 1024. That supports destructive numerical underflow from downscaling. It does not establish numerical scale invariance. Unit scaling was committed at 0d36752 before the complete retry.

MAIN `.thesis-build/dev-runs/20261010-1157-ddim-feasibility-retry` passed exact native parity and finite nonzero diagnostic gradients at both strengths. Its .1 fp32 continuous check then failed: gradient norm 2.9670479; AD -2631.2080; centered FD -46.2973 at .003 and -95.8122 at .001; relative discrepancies .98240 and .96359. Both native hinges were inactive, so these are fixed linear-scalar diagnostics. The .2 continuous check and source-468505 utility stage remain unmeasured. Peak allocated/reserved memory was 8.629/10.198 GB. Computation consumed 25.719 + 12.391 + 18.000 = 56.110 seconds before the new diagnostic.

For n = 3*512*512, g = gradient f and d = -g/RMS(g), the exact directional identity is g dot d = -sqrt(n)*norm(g). Thus the observed AD magnitude follows the declared direction normalization. At epsilon .003 its linear prediction changes the scalar by about 7.89, and at .001 by 2.63, from a baseline scalar 1.0498. This does not prove excessive curvature, but it shows that these perturbations need not be local for this scalar. Their RGB RMS amplitudes are .765 and .255 pixel levels, respectively.

Code inspection finds no obvious detached diffusion stage or late-bound UNet timestep: timestep defaults are bound inside the loop, posterior/noise draws occur outside checkpointed blocks, and the fp32 projection omits rounding. This limited inspection is not a proof that the graph is correct. The diagnostic still clamps RGB inputs and decoded outputs. At exact input 0/1, framework clamp backward and a central difference can disagree at a kink. Record exact-boundary counts and, if already available, the fraction of directional squared norm on those pixels; otherwise mark the latter unmeasured without another gradient pass. Do not silently mask or perturb them to obtain a pass. Output clamp crossings and fp32 cancellation are further possible limitations.

The parent has also identified that fp32 tensors can use reduced-precision TF32 kernels. The new diagnostic disables TF32 for CUDA matmul and cuDNN, recording original flags and restoring them afterward. Smaller differences and diagnostic kernel precision change together; a pass cannot attribute the previous discrepancy to either cause separately. Native fp16 attack settings remain unchanged.

## Fixed prospective numerical gate

Use source 1675, RC3 starting RGB8, seed 0, strengths .1 then .2, and precisely the same continuous promoted-half-weight chain and fixed scalar mean(w*p). Remove RGB8 operations only as previously declared; retain input/output clamps. Use fixed common posterior/noise per precision and a newly computed negative unit-RGB-RMS gradient for that same diagnostic operator. No source, direction or scalar replacement is allowed.

Evaluate every centered difference at epsilon 1e-4, 3e-5, 1e-5 and 3e-6. Record both scalar values, AD, FD, relative discrepancy and precision flags for every scale at both strengths. These are diagnostic inputs, not writer step choices. Define R(a,b) = abs(a-b)/max(abs(a),abs(b),1e-8).

The convergence gate passes only if **both strengths** satisfy all of the following:

- Finite scalar, finite nonzero input gradient and finite negative AD.
- At **each of the two smallest fixed scales**, 1e-5 and 3e-6, FD is finite, strictly negative, and R(AD,FD) <= .35.
- The two smallest-scale FD estimates satisfy R(FD_1e-5,FD_3e-6) <= .20.

The two larger scales are descriptive and cannot substitute for either required scale. The .35 tolerance preserves the original agreement tolerance; the second-scale and .20 stability condition prevent an isolated matching secant from being called convergence. These finite tolerances are an engineering gate, not a theorem of differentiability. Freeze this file and the diagnostic implementation before observing results. No extra epsilon, precision, direction or tolerance may be selected after failure under D1N.

If the gate fails, stop D1N before candidate writing and record whether the evidence is consistent with clamp kinks, precision limits, nonlocality or an unresolved graph defect. Do not infer universal impossibility of DDIM-aware writing. Any later materially different study requires a separate design decision; unused budget is not permission for more numerical retries.

## Native and rounded gates remain mandatory

On diagnostic success, D1N receives one native continuation, with no retry. Restore the original native precision and kernel flags, move unchanged modules back as needed, and recheck exact native RNG/timestep/RGB8 parity at .1/.2 seed 0. Reusing the successful pre-diagnostic parity alone is insufficient. This also verifies that precision promotion/reversal did not alter the operator.

Run the originally declared utility stage on source 468505. Recompute all nine branches in order: clean, deterministic SD1.5 VAE, deterministic SDXL VAE, and all .1/.2 DDIM seeds 0-2. Require finite losses, a positive initial worst-branch loss, and a finite nonzero unit-scale native gradient of that actual loss. An unexpected all-inactive objective despite the retained wrong-q identity is a contradiction to diagnose, not a successful utility test or reason to change source.

Evaluate all three fixed proposals at .10B, .50B and 1.00B, using the original two-ball/box projection. Re-read their saved RGB8 pixels and evaluate **all nine rounded branch losses**, not just the branch supplying the gradient. At least one proposal must strictly lower the rounded nine-branch maximum and preserve feasible projection, exact clean operational q/h, clean both_match and saved-image PSNR >35. Report every plateau/increase and discard every trial. The successful proposal is not selected as the final mark or as a new optimizer step. This retains the original utility gate without post-outcome relaxation.

Only after all smoke requirements and the conservative throughput bound pass may D1N run the unchanged global 40-step writer over all twelve sources. Preserve clean exact q/h/both_match and PSNR checks on every proposed update; final saved outputs must each pass PSNR >35, SSIM >.9, LPIPS <.1, exact q/h and both_match. Preserve deterministic SD1.5 joint readable/exact-q and semantic acceptance on 12/12, SDXL at least 11/12, and report SDXL 12/12 preservation separately. No h restoration, best-checkpoint choice, source-dependent configuration or relaxed final rounding constraint is allowed.

After qualification, use the unchanged official checked T3 grid and original D1 identity gates: fixed-I semantic 29/29 and 28/28, preservation of each available frozen exact-q and J-positive identity, zero observed C0/wrong-owner detections, unchanged blocked-slot treatment and all clean/VAE prerequisites. A positive T3 result only advances to the previously scoped T4/T5 and binding work. Diagnostic or training losses never count as an attack result.

## Cost and reporting

D1N receives **no fresh budget**. All D1 failures, three-scale diagnosis, four-scale diagnosis, loading, native restoration and rounded utility share the original aggregate 900-second smoke cap. Starting recorded expenditure is 56.110 seconds, leaving at most 843.890 seconds before this diagnostic. The parent additionally fixed a 120-second cap for the convergence diagnostic before its outcomes; account for any unavoidable single-operation overrun and stop at the next safe check. If that cap prevents completion, numerical feasibility remains unresolved and D1N cannot advance. Optimization/qualification remains <=8100 seconds; official T3/summaries <=1800; total <=10800. Unused allowance cannot buy another candidate or more iterations. Measure throughput with the same complete nine-forward, worst-backward and clean-check accounting before writing twelve outputs. A cap interruption is incomplete and ineligible.

Keep original D1 run.json and outputs unchanged. The new ordinary development run record must identify D1N, link all prior failed/diagnostic runs, record shared elapsed cost, the exact committed code and this decision, and distinguish pending/failed/passed numerical, native, utility, quality and T3 gates. No new launcher, receipt system, approval JSON or confirmatory infrastructure is needed. A final report must say that D1 failed its original screen and that any D1N result follows an outcome-informed but prospectively fixed numerical continuation on reused development data.

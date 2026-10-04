# A-C: terminal-latent optimization with the blind continuous reader

Version `m1-terminal-continuous-v1`, frozen2026-10-04 before implementation or model execution. Method escalation gpt-6-astra/xhigh. This prospective local development amendment follows `m1-blind-noise-results-decision.md`. It is **within family A**, using a new VAE-based reader and continuous full-CLIP templates; it is neither an initial-noise method nor a fifth independently tried family. Parent owns implementation, commit, execution and shared-state records. No held-out use or human verdict.

## Scientific question and what stays fixed

Can a terminal-latent embedder use gradients through the actual VAE readout to produce two public, content-dependent correlations within the photo quality budget, while retaining semantic alignment after a VAE cycle? B3-C's failed full denoising transport is removed; its frozen feature geometry, maps, owner roster, score definition, thresholds and operational states are retained exactly. This isolates an embedding-route amendment rather than changing reader and threshold after observing results.

Import `m1_blind_noise_core.py` unchanged. Full normalized512-dimensional CLIP E,32-bit image-DCT pHash H, owner-dependent disjoint8192-coordinate templates and SRHT instance projection remain version`m1-blind-noise-template-v1`. Both primary score thresholds remain inclusive4. States remain `both_match`, `semantic_only`, `neither_supported`, with `ambiguous_instance_only` and `invalid_measurement` retained as abstentions. No causal regeneration/copy-paste or cryptographic ownership label is adopted. Low alignment cannot distinguish a missing carrier from a mismatched-content carrier.

The production interface remains `detect(suspect_rgb8, candidate_owner, pinned_public_models_and_profile)`. It has **no source image, source features/hash, reconstruction latent, source noise, enrollment record, target message, nonce or inversion**. Use the original B3 reader's fp16 SD1.5 VAE posterior mode times.18215, CPU pinned CLIP, identical pHash and float64 core scoring. An embedder's source-template score is an oracle surrogate and never substitutes for this reader. All four public owners are queried; only alpha embeds. No map or threshold selection.

## Frozen latent variable, source bypass and quality cap

Use the same reserved sources1675 and4795, their canonical512x512 RGB8 arrays and original hashes. Initialize from their **unmarked** reconstruction step200 checkpoints in MAIN's retained reconstruction run; resolve and receipt those checkpoints exactly as A did. Do not initialize from a previously watermarked A/B/D output or select the best past checkpoint. Preserve source manifests and feature/profile/model receipts.

Let I be source RGB float in[0,1], and u0 the unscaled posterior-coordinate checkpoint. The only optimized variable is unscaled terminal latent u, initialized u0. Load the frozen SD1.5 VAE weights in fp32 for differentiable embedding, disable TF32, and use checkpointed sequential graphs if needed. Define `D(u)=clip((VAE.decode(u)+1)/2,0,1)`, `R(u)=D(u)-D(u0)`. D(u0) is fixed. This is a genuine latent decision variable, with no optimized pixel array or post-hoc pixel watermark codec.

For differentiable optimization use `epsilon=10^(-35.2/20)`, `rho=RMS(R(u))`, `beta=1` if rho<=epsilon and otherwise epsilon/rho, and

`J_float(u)=clip(I + beta*R(u),0,1)`.

Differentiate through beta when its cap is active. At rho0 use the beta1 branch, without a zero division. This radial cap bounds the **unclipped** float displacement norm; component clipping cannot increase distance from I. It constrains distortion while allowing the optimizer to change the useful residual direction. It does not guarantee SSIM/LPIPS or exact RGB8 PSNR.

At the fixed final step retain the raw residual R(u100), then choose **one deterministic scalar lambda in[0,1] from image quality only**, using the existing D diagnostic's exact36-iteration bisection convention: emit lambda1 if saved RGB8 at1 has PSNR>=35.2dB; otherwise use the largest feasible lower endpoint after36 bisection iterations. The candidate is `RGB8(clip(I+lambda*R(u100),0,1))`, with CPU float64 composition and `RGB8=uint8(rint(255*clip(...)))`. At lambda0 it must reproduce the exact source. PSNR uses the saved/redecoded RGB8 array. This scalar search queries **no watermark score, CLIP feature, hash or owner**. Preserve lambda, beta_final, the unscaled residual, float/source/PNG hashes and capped-vs-surrogate image RMSE. It may correct a small surrogate/quantization discrepancy; it must not select an earlier latent, sign, channel or stronger mark.

The final image explicitly contains original pixels through a source bypass. It is not pure VAE decoding. Retain D(u0) and D(u100) as diagnostic float arrays and source-referenced pure-decoder quality, but neither counts as a second primary arm or family. C0 is exactly I; its VAE-cycle control is formed from its saved RGB8.

## Fixed differentiable objective and schedule

Freeze E(I),H(I) once inside the embedder and construct both alpha-owner templates from the unchanged core. Convert their arrays to fp32 torch constants. Let `Q(X)=.18215*mode(VAE.encode(2X-1))` and `C(X)=D(mode(VAE.encode(2X-1)))`, with the same clipping convention and no posterior sampling. Q is in scaled units while u and the decoder's input are in unscaled units. Positive global scaling cancels from the normalized scores, but receipt it to prevent unit errors.

Let `S_s(X), S_i(X)` be the exact core score formulas applied to Q(X) with the **fixed source** templates. Keep their denominator differentiable. If a denominator is zero or nonfinite, retain failure; do not silently add a data-fitted stabilizer. A tiny numerical guard can only raise an explicit invalid measurement, not change the formula.

Define `h_m(x)=[max(0,m-x)/m]^2`. For all100 updates, use

`L_clean = h_6(S_s(J_float)) + h_8(S_i(J_float)) + .01*mean((J_float-I)^2)/epsilon^2`.

On update indices0,2,...98 also accumulate

`L_cycle = h_6(S_s(C(J_float)))`.

The cycle branch is evaluated/backpropagated separately to avoid retaining two full VAE graphs. The same gradient buffer receives both contributions before the single Adam update. Clean instance receives a target; cycle instance is measured but not penalized toward either presence or absence. Do not weaken a carrier artificially to manufacture a regeneration state.

Margins6/8 are prospective engineering margins above threshold4, not estimated false-positive quantiles. Full CLIP tends to preserve the semantic template under small source distortion; instance geometry additionally loses a factor`1-2HD/32`. For illustration, CLIPcos.95 and6 pHash flips give an exact uncompressed kernel.59375, so a margin8 leaves more room than6 in an ideal coherent-signal model. This is not a score guarantee: native background, projection, denominators and the actual channel matter. No descriptor-radius theorem is assumed.

The larger instance margin also has a binding cost: with CLIP similarity near1 and pHash distance8, the ideal uncompressed kernel is.5, so a hypothetical coherent score8 becomes4, exactly the inclusive threshold. Thus increased tolerance to pHash drift is not automatically stronger instance discrimination. Future T4/T5 assessment must retain actual source/recipient geometry and score distributions; distance>=8 alone does not guarantee rejection. The pilot margin stays8.

Use Adam lr.01 in **unscaled latent units**, betas(.9,.999), eps1e-8, no weight decay, no stochastic augmentation, no learning-rate schedule and no gradient clipping. Seed0; all frozen model parameters have gradients disabled. Exactly100 updates per source; take the last step even if a score peaked earlier. Do not early-stop on success, extend failed cases, or change margin/lr after inspecting one source. Journal before-update losses, all clean/cycle source-template scores when computed, residual RMS/beta, gradient norm and finite checks. Save u, optimizer state and RNG state every10 steps plus step0/final, atomically to new files; resume only the identical committed configuration and source/checkpoint receipts. Nonfinite state, absent gradient or budget cap retains the source as failed/incomplete.

No source CLIP or hash gradient is required: the source descriptors are constants inside this bounded objective. Blind recomputation is an independent endpoint check. This is deliberate, not an assertion that fixed-source optimization ensures self-consistency. Do not add pHash margins, recomputed-feature feedback, learned offsets or a CLIP adversarial objective during the pilot.

## Evaluation, bottleneck attribution and promotion

For each source assess C0/C1 saved RGB8, clean and after the pinned **fp16 production** VAE roundtrip. This is8 primary image conditions and32 owner queries, with two independent source clusters. Include all conditions even if optimization fails; unavailable results are missing, not negative or discarded. Source-to-suspect CLIP cosine, pHash distance and actual instance-kernel/projection errors are evaluator diagnostics only. Report quality for all cells but apply clean source quality gate to C1 clean: PSNR>35,SSIM>.9,LPIPS<.1. Human assessment remains missing.

Retain primary terminal reader latents from each of the eight saved images, so diagnostic source-template scores can be recomputed without another model run. For both marked sources also retain these clearly separated stages:

1. Final fp32 float surrogate clean and cycle source-template scores.
2. Final capped RGB8 re-encoded in fp32 with fixed source templates.
3. The identical RGB8 re-encoded by the primary fp16 reader with fixed source templates (oracle).
4. The primary fp16 readout with suspect-recomputed features (blind).

This distinguishes failed carrier optimization, composition/quantization, precision, and content drift. Keep all raw values; no diagnostic receives promotion credit. The production cycle includes the saved-image quantization at its declared boundary, whereas the optimization cycle is a float surrogate. Report that gap explicitly.

Promote the frozen candidate only if **both sources** pass clean quality and blind clean`both_match`, both pass blind after-VAE semantic threshold, and every C0/marked-wrong-owner query stays below **both** thresholds, with no missing/invalid/instance-only case discarded. Instance survival after VAE is descriptive. This gate is intentionally the same logical screen as B3, not relaxed after its failure. If it passes, expand the unchanged rule to the remaining ten reserved development sources, then run the common full T3/T4/T5 assessment. Do not claim T3 diffusion robustness, T4 rejection or T5 semantic separation from this pilot.

If source-template surrogate targets remain unmet at the fixed budget, report the measured quality/score tradeoff and stop this configuration; do not immediately tune another margin/lr grid. If surrogate targets are met but saved oracle scores fail, localize the recorded rendering/precision gap. If saved oracle scores pass while blind scores fail, diagnose actual feature/hash drift before any further method amendment. The full old-A threat assessment may inform a later decision but cannot retroactively change this pilot's criterion. All outcomes remain exploratory.

## Resources, tests and provenance

Use a new runner/config; do not edit the live A runner, frozen B3 core or retained runs. Commit scientific code/config/spec before execution. Freeze the complete dependency hashes, source/checkpoint receipts, dtype/scaling, exact cap convention and command in a unique MAIN development run. Estimate two100-step VAE optimizations, no U-Net or inversion calls. Cap1800 seconds overall,10GiB GPU allocation or lower available headroom,16GiB RAM,500MiB new artifacts andUSD0. Flush checkpoints and case journals; preserve failed attempts and all8 planned rows. The cap is an operational limit, not a measured performance estimate. No extra downloads.

CPU tests must compare torch source-template scores to the independent float64 core on fixed nonzero fixtures, verify norm-cap derivative and zero-residual branch, check exact RGB8 identity/cap monotonicity and36-step endpoint rule, validate scaled/unscaled conventions, prove no source argument crosses the primary reader boundary, and check the8-row/four-owner inventory. A small finite-difference check on the mathematical score/cap suffices; no GPU smoke run or actual image result is fabricated as a test. During the real run, retain actual gradient norms/finite checks and implementation-versus-core endpoint parity.

The reader's ideal random-owner fixed-image tail discussion remains as in the B3 specification. The same public maps can be used by an attacker to optimize a forged mark; this objective demonstrates that possibility rather than creating a cryptographic authenticator. Fixed four-owner empirical controls, content-dependent templates and a successful quality budget do not imply adaptive-forgery resistance, a secure ownership proof or causal three-way attack identification.

## Implementation handoff

`scripts/m1_terminal_continuous.py` and `research/m1-terminal-continuous-dev.json` implement the frozen two-source pilot. The primary function delegates to the unchanged B3 `detect` boundary. The embedding-only `FixedSourceScores` never crosses that boundary. A separate fp32 VAE supports optimization; a separate fp16 VAE and the same `VaeImageProcessor(vae_scale_factor=8)` preprocessing support production readout/cycling. No U-Net is loaded. The pinned safety checker is retained for saved outputs and the production cycle. Final eight-row conditions,32 owner queries and28 dependent negative queries have an explicit strict gate in `run.json`.

Run only after committing all dependencies, using science Python with `scripts/m1_terminal_continuous.py --run --manifest research/m1-terminal-continuous-dev.json --output-dir <fresh MAIN dev-runs directory>`. `--resume-from <incomplete prior directory>` reads hash-verified latent/Adam/RNG state into a new directory; it never modifies the prior attempt, changes code/config or resets the cumulative1800-second budget. The starting resumed snapshot is also saved in the new directory so a second interruption remains recoverable. Completed attempts cannot be used as resume inputs. The fixed reconstruction inputs are1675/4795 step200 from`20261003-1455-latent-reconstruction`; that run's overall interruption does not invalidate its separately completed, hash-verified cases.

CPU tests cover independent score algebra/gradient/scaling, zero and active norm-cap derivatives, exact RGB8 cap arithmetic, reference-free detection, inventory/gate handling of missing/invalid queries, checkpoint identity/replacement guards, and uninterrupted-versus-resumed optimization equality on an analytic toy codec. They do not load a model or constitute scientific evidence. The four fixture owners remain unchanged; any future16-owner confirmatory interface requires a separately versioned generalization and development parity before the final method freeze.

Operational memory clarification before the first run: immediately before loading models, read CUDA free/total bytes and set `effective_allocation_bytes=min(10GiB, free_bytes-512MiB)`. Reject a nonpositive result. Record the free/total snapshot, configured cap, fixed512MiB reserve, effective cap and allocator fraction in `run.json` before loading weights. Both PyTorch's allocator fraction and subsequent allocation checks use this same effective cap. A changing external GPU workload can still cause OOM; it is retained as a failure rather than silently changing any scientific parameter. This clarification changes no source, objective, score, threshold or optimization schedule.

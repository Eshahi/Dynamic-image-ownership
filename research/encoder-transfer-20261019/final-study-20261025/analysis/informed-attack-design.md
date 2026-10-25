# WP3: two informed attacks without detector feedback

Prospective server-only design, 2026-10-25. No image, attack, metric, model, timing or training was run. MAIN STATE was read once. Historical development results motivated this design; it is not blind discovery and does not change **FAILS, ROUTE C**. This file does not authorize execution.

## Information and quality contract

The attacker sees only published marked RGB8 image u and public proxy/quality-model weights. It never sees original x, residual u−x, owner, key, payload, reader, detector output, target gradient or registry. One callable and one globally selected setting apply to F5/v5/WAM/VINE-R. Arm labels are absent from the callable; the development selector can use anonymized arm labels solely to enforce quality in every arm. Originals and quality relative to originals are forbidden to selection. Historical detection knowledge motivated these prospective choices but no newly generated detection can tune them.

Retain R0/R1, the existing R1 rinse and foreign-codec controls D1/D3. No new watermark baseline, trained attack network, writer, captioner or prompt search is introduced.

The joint output-quality target against u is **LPIPS≤.15, PSNR≥25 dB, SSIM≥.75**. This is an automated fidelity region, not imperceptibility or human approval. Use existing pinned RGB8 quality helpers (`m1_latent_reconstruction.py::quality`, `three_threat_models.py::load_lpips/lpips_score`), with code and weight hashes in the server contract. Never change LPIPS backbone or SSIM convention. All A quality is final output versus u, not versus its intermediate image.

Develop on all 60 existing development sources and all four marked arms. A has seeds12/13/14; B is deterministic. A source quality-pass requires at least two of three scheduled outputs to jointly meet all three criteria. A candidate needs BOTH ≥48/60 passing sources AND ≥144/180 passing outputs in EACH arm. B needs ≥48/60 passing outputs/sources in EACH arm. Failed, blocked, nonfinite and missing outputs are quality failures; no identity fallback or dropped denominator.

For eligible candidates, compute each arm's mean `min(LPIPS/.15,1)` over all scheduled outputs, assigning zero to missing/nonfinite outputs. Score the candidate by the minimum of four arm means. Select the largest score rounded to six decimals; ties choose lower declared model-call cost, then ascending parameter tuple. This quality-only rule spends distortion budgets; it does not estimate removal strength. Preserve every candidate's quality summary. No detector tie-break is allowed.

If no setting passes, freeze the attack as **quality-ineligible**, not a successful identity attack. Do not enlarge its grid or relax quality. Freeze both attacks before any new detector release. Phase B never recalibrates; quality failure there is reported with all frozen outputs retained. Quality versus x may be evaluated later but never enters attack tuning. Construction failure is not evidence of removal: separate missing output, quality failure, detection and completed non-detection, with missing-outcome bounds.

```text
for attack in [A,B]:
    for theta in attack.finite_grid:
        for source in fixed_60_development_sources:
            for arm in [F5,v5,WAM,VINE_R]:
                u = published_mark(source,arm)        # original forbidden
                for seed in attack.seeds:
                    y,status = attack(u,theta,seed)   # no arm argument
                    save(y,status,metrics_against_u)
        eligible(theta) = every_arm_meets_locked_quality_rules
        score(theta) = min_arm(mean_scheduled(clipped_lpips_or_zero))
    if no eligible theta: freeze(INACTIVE_QUALITY_INELIGIBLE)
    else: freeze(argmin_eligible(-round(score,6),cost,parameter_tuple))
# Only after both freezes release any new detector outputs.
```

## A: mixed-family chained reconstruction

**Hypothesis:** two native reconstructions can rotate readable response and background twice. The second may also preserve or restore a readable direction; independent-pass retention products are unjustified. SDXL-first F5 collapse alone adds little; the useful question is additional cross-arm effect at stated quality/cost.

Use exactly the pinned native R1 then R0 pipelines in `research/encoder-transfer-20261019/protocol.md`: compatible encoder/denoiser/decoder within each family, sampled posterior, native scaling, DDIM20, scaled-linear schedule, CFG1, eta0, empty prompts, existing precision, resize and safety rules. SDXL runs at 1024 and returns saved RGB8 at 512; SD1.5 receives those exact pixels. No incompatible encoder/denoiser swap. Order is fixed SDXL→SD1.5.

Grid: same strength s on both passes, **s∈{.05,.10,.15,.20}**. Pinned DDIM20 yields m=1/2/3/4 updates per pass, starting timestep1/51/101/151. Verify actual arrays on server preflight; mismatches are implementation errors, not new tuning opportunities.

```text
ATTACK_A(u,s,seed):
    assert s in {.05,.10,.15,.20}; assert seed in {12,13,14}
    v = pinned_R1(u,strength=s,seed=seed,steps=20,CFG=1,eta=0,empty_prompts)
    if v blocked/failed: return FAILED_WITH_FIRST_PASS_RECORD
    y = pinned_R0(saved_RGB8_512(v),strength=s,seed=seed+100,
                  steps=20,CFG=1,eta=0,empty_prompt)
    return y,status
```

Each call gets its fresh native generator. Equal seed integers are not claimed equal noise tensors across families. Serial family batching is allowed with identical saved intermediate pixels. First-pass records remain detector-sealed until selection freezes.

**Controls:** preserve R1 .1 and R1 rinse .1→.1. At selected s retain A's first-pass output as a paired control. At .1, existing rinse has equal pass count but a different second family and potentially different distortion. No efficiency superiority follows from greater removal at greater damage. Fixed quality-caliper comparisons must report sparse/non-estimable matching. Development candidates do not become multiple confirmatory winners.

**Expected effects:** F5 C may be at floor after first SDXL near.1; report semantic margins and found/read/binding, not just another zero. Historical rinse suggests possible additional v5/WAM loss; a different second family could change that. VINE-R is the resistant comparator and biggest uncertainty. These are hypotheses, not rankings.

**Cost per image/seed:** two VAE encodes, two decodes, 2m denoiser forwards/reverse updates, no backwards, plus cacheable text encoding and quality assessment. SDXL/SD1.5 forwards have different costs. **Straw-man risk:** one order and equal strengths are narrow; failure cannot establish robustness to all chains.

## B: proxy latent decorrelation reconstruction

[MarkNull §5.3, Eq.8–11/Algorithm1](https://arxiv.org/html/2608.10166v1) encodes an image, inverts once, then optimizes its data latent against the fixed inverse latent with angular/fidelity losses. Final output uses decoding, not another reverse diffusion trajectory. B is **MarkNull-inspired**, with a different squared-cosine objective, optimizer and grid; it is not an official reproduction. Orthogonality does not imply independence; the paper's transfer assumption requires compatible coordinates/inversion. See [the root assumption check](marknull-assumption-check.md).

**Inference:** proxy reconstruction features might change without knowing the residual. Reduced proxy cosine need not reduce a watermark statistic. We do not identify removable high-gain directions from encoder norm, assume smoothing contracts them, or claim that adjusting cosine proves signal erasure.

Use pinned public unmodified SD1.5 weights already used by R0, identically across arms. E is its512 posterior-mode encoder plus official latent scale; D undoes that scale and decodes. E/D, optimizer latents and scheduler arithmetic are fp32; UNet/text use R0 fp16 precision. Cast latent only at UNet input and return predictions to fp32. Empty prompt, CFG1, frozen eval mode, no posterior samples or restarts.

Use **diffusers0.35.1 DDIMInverseScheduler**:1000 train steps, beta_start=.00085, beta_end=.012, scaled_linear, epsilon prediction, clip_sample=false, set_alpha_to_one=true, steps_offset=1, leading spacing, rescale_betas_zero_snr=false. Native20 timesteps are1,51,…951. UNet receives native t; inverse arithmetic uses alpha index t−50 (initial alpha1 if negative), destination index t. These [source-verified conventions](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddim_inverse.py) approximate inversion; they are not an exact inverse of R0.

```text
INVERT_PROXY(z0):
    inverse = DDIMInverseScheduler(explicit_config_above)
    inverse.set_timesteps(20)
    z = fp32(z0)
    for t in inverse.timesteps:
        e = fp32(UNet(fp16(inverse.scale_model_input(z,t)),t,empty_text))
        z = inverse.step(e,t,z).prev_sample
    return stop_gradient(z)
```

This is20 denoiser forwards once per image, cached across candidates. Output n is an approximate terminal proxy latent, not original generating noise or guaranteed Gaussian. No gradient through inversion.

Let z0=E(u), n=INVERT_PROXY(z0). Reject zero/nonfinite reference norms. Define `c(z,n)=clamp(dot(z,n)/(max(||z||,1e-12)*max(||n||,1e-12)),-1,1)`. Loss is

`L(z)=.5*[LPIPS_float(D(z),u)/.15 + MSE(D(z),u)/10^(-2.5)] + lambda*c(z,n)^2`.

MSE means all RGB coordinates in[0,1]; its denominator is the25dB PSNR equivalent. LPIPS_float uses the pinned metric's exact weights/normalization in eval mode on floating pixels, with gradients to z. SSIM is a selection constraint, not a gradient surrogate. Clipping remains in the differentiable path; final RGB8 rounding does not.

Grid: **epsilon∈{.025,.075,.225} officially scaled SD1.5 latent-coordinate units**, **lambda∈{.1,1,10}**, **20 steps fixed**: nine candidates. The coordinate box is centered on z0. All have equal call cost; tie tuple is(epsilon,lambda). No adaptive radius, early stopping, selected intermediate iterate or restarts.

```text
ATTACK_B(u_rgb8,(epsilon,lambda),unused_seed=None):
    u = fp32(u_rgb8)/255
    z0 = stop_gradient(E_mode(u)); n = INVERT_PROXY(z0)
    reject_zero_or_nonfinite_reference_norms(z0,n)
    z = z0.clone(); step = epsilon/10
    for k in 1..20:
        v = clip01(D(z))
        L = .5*(LPIPS_float(v,u)/.15 + mean((v-u)^2)/10^(-2.5))
            + lambda*c(z,n)^2
        g = gradient(L,z)
        if nonfinite(L,g): return FAILED_WITH_TRACE
        z = z - step*g/(sqrt(mean(g*g))+1e-12)
        z = z0 + clip(z-z0,-epsilon,epsilon)
    return uint8(floor(255*clip01(D(z))+.5)),status
```

Every candidate starts at z0; zero gradient gives zero update. Log initial/final cosine, each loss component, each projected step norm and the fraction of coordinates on the box bound. The cosine-squared gradient vanishes at cosine 0 and ±1; an unchanged objective can therefore be a genuine optimizer limitation. Diagnostics never select iterations/settings or authorize post-detection tuning. Frozen deterministic math settings apply; cross-GPU bit identity is not claimed. B has one output/source; do not manufacture three identical independent trials.

**Controls:** B-codec=`quantize(D(E(u)))` with B's exact mode/fp32/rounding; B-fidelity is the same20 steps at selected epsilon but lambda=0, skipping inversion. Neither enters selection; evaluate only after freeze. These are B ablations, not new watermark baselines. B versus B-fidelity tests adding this objective to this optimizer; differing distortion prevents claiming a quality-matched causal mechanism. Report quality and fixed-caliper coverage as well as achieved cosine.

**Expected effects/risks:** F5 uses the public encoder coordinates but reads signed chips and binding, not cosine with n; B could leave it intact or improve its score. v5/WAM might respond mainly to the codec; VINE-R may retain its signal through both. Initial cosine near zero, inaccurate inversion, fidelity preserving the mark, or a restrictive box can make B weak. It may alter host content instead. These measured failure modes reject this bounded candidate, not all MarkNull/informed attacks. Never repair it with residuals, reader projections, detector queries or post-detection proxy selection.

**Cost per image:** one encoder forward;20 denoiser forwards/inverse updates;21 decoder forwards;20 decoder backwards and20 LPIPS loss forwards/backwards; no UNet backward or final reverse-diffusion trajectory. Cache fixed LPIPS reference features and release each step's graph. B-codec adds one cached-latent decode; B-fidelity adds21 decodes and20 decoder/LPIPS backwards, no inversion. Memory/time require server preflight. Neither attack needs JVPs; separate mechanism-law JVP feasibility remains unknown.

## Budget and release order

Counts below are model calls, not seconds or equal-work estimates; exclude embedding, metric-only assessment, detection, loading and failures. Distinguish SDXL from SD1.5 timings.

| Task |60 development sources ×4 marks|200 fresh sources ×4 marks|
|---|---:|---:|
|A full grid,3 seeds|14,400 denoiser;5,760 encoder and5,760 decoder forwards|Never repeat grid|
|A selected s,3 seeds|Already in grid|4,800m denoiser;4,800 encoder and4,800 decoder forwards, m=1..4|
|B cached inversion|4,800 denoiser;240 encoder forwards|16,000 denoiser;800 encoder forwards|
|B full9-setting optimizer grid|45,360 decoder forwards;43,200 decoder/LPIPS backwards|Never repeat grid|
|B selected optimization|Already in grid|16,800 decoder forwards;16,000 decoder/LPIPS backwards|
|B-fidelity selected radius|5,040 decoder forwards;4,800 decoder/LPIPS backwards|16,800 decoder forwards;16,000 decoder/LPIPS backwards|
|B-codec cached z0|240 decoder forwards|800 decoder forwards|

Apply the selected attack, identical settings, to C0 as well as marked inputs for negative gates. Generate one C0 output per source/attack/seed, shared among detectors; adding C0 increases a selected-setting generation schedule by5/4. Development selection uses marked arms only, so C0 does not need the full tuning grid. Wrong-owner calls need no additional images. The60/200 counts are sizing examples; WP5 sets final n.

Only server preflight can establish time/memory, particularly fp32 decoder backward. If B cannot fit the approved envelope, record resource non-execution; preserve A and core native cells. Do not omit controls or reduce iterations after detection release. Any feasibility amendment must precede full Phase A measurements.

Order: freeze design/code → authorized server preflight without detector inspection → marked development quality grid → freeze both settings/inactivity → selected controls/C0 → development detection release → complete Phase B protocol freeze → required user confirmation decision. All Phase B images remain outside attack development.

These tests establish bounded empirical evasion at an automated quality operating region, not universal removal, signal erasure, forgery, ownership or a transfer law. Report F5/v5 C and carrier/read/binding separately from native WAM/VINE known-message presence, with side information and negative coverage. Unequal native embedding quality remains a limitation.

Primary-source access:2026-10-25, direct web opens of MarkNull §§4–6 (Eq.8–11,Algorithm1,Assumption2) and diffusers0.35.1 inverse scheduler source. No search query, code/model download or execution occurred. Project sources: mechanism/theory/attack cards, frozen protocol and quality-helper call sites. Proposed grids, controls, selection rules and costs are this contributor's design.

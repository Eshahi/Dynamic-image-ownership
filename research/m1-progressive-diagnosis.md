# C: mechanism diagnosis and a schedule-only amendment

Version **`m1-progressive-phase-diagnostic-v1`**, 2026-10-04; method escalation **gpt-6-astra/xhigh**. This document follows the completed exploratory screen; it is not retrospective preregistration. Only existing source, primary-source text, retained metadata and synthetic CPU arithmetic were inspected. No scientific image/model inference, GPU run, held-out access, original-output edit or commit was performed by this author. The proposed run below remains prospective.

**Decision: do not stop the progressive-guidance family after the present screen. Freeze one controlled late-half amendment, C-L100, with instrumentation that separates guidance, subsequent denoising and decoder/encoder loss. Change only the guidance interval.** Keep alpha .5, eta100, the actual orthonormal DCT, channel0, 128 coefficients, post-CFG order, fp16 models, mask, payload and threshold unchanged. A target-complement arm tests whether alignment follows the chosen word rather than generic coefficient signs. Do not add a simultaneous transform, precision, CFG-order or strength sweep.

## What the negative screen actually establishes

The [retained report](m1-progressive-results.md) identifies MAIN `.thesis-build/dev-runs/20261004-0031-progressive`, commit `eca1a533a852d988b213ca47ab24f94dcda5b1f0`, run SHA-256 `c3436690fd0ae549d0a2a3ac71c00e43105d753697f0b26ce61984ccee62ff94`. Its actual entrypoint is `scripts/m1_progressive_latent.py`, SHA-256 `1ab50ebf7d94883c80af623b1f14f1a7c6412c1ea4b8a83b8e06b80be0e52914`. The screen completed all28 generations and112 image conditions. Neither readout reached 14/16 on any of the96 marked conditions; those conditions share only four prompt/seed clusters and six variants.

For alpha.5/eta100, native clean matches in seed1000–1003 order are **10,13,9,11**, versus C0 **5,8,6,3**; after one VAE cycle they are **10,13,9,10**. Thus a consistent increase exists without a qualifying message. The same C0 words rise to **7,11,10,9** after strength.4 regeneration. A regeneration-driven increase therefore cannot by itself demonstrate watermark survival. Only alpha.1/eta25 passed the generated-pair quality conjunction on all four clusters, with no clean carrier success. This is measured failure of the six declared configurations, not a numerical upper bound for the family.

The original artifacts do not retain predicted-clean coefficients, final predecode latent or its hash. They cannot determine whether the guided state ever carried the target, whether the remaining25 unguided steps erased it, or whether decode/re-encode lost it. Original PNG hashes are available for exact replay comparison; original latent-hash parity is **unavailable**, not inferred from the PNG receipt.

## Cheap CPU diagnosis: no reversed gradient or divergent eta100

The source and earlier [preflight](m1-progressive-preflight.md) agree on the declared operator. For selected coefficient c and target s, the loss is the masked squared residual averaged over128 positions. Its orthonormal-DCT gradient gives

`c_guided - s = (1 - 2*eta/128)*(c_before - s)`.

At eta25 the residual factor is .609375 and isolated loss ratio .371337890625. At eta100 they are **-.5625 and .31640625**. Eta100 crosses the target but still contracts this fixed quadratic; calling that isolated step divergent would be wrong. Eta64 would exactly project selected predicted-clean coefficients to their targets in exact arithmetic, but it is **not adopted** in this schedule-only experiment. The sign and /128 normalization are internally correct for our specification. No proposed fix is justified merely by seeing the overshoot.

The noise rearrangement also has the correct sign. With `a=a_t`, `a_prev=a_(t-20)` and sampler eta0, ignoring numerical rounding and with clipping/thresholding disabled, a predicted-clean correction `delta_x0` induces

`delta_epsilon = -sqrt(a/(1-a))*delta_x0`,

`delta_z_prev = q_t*delta_x0`,

`q_t = sqrt(a_prev) - sqrt(a*(1-a_prev)/(1-a))`.

The scheduler therefore does **not** replace the next state by the corrected clean prediction. In particular, early corrections have small immediate coefficients. Using the installed real scheduler's declared50-step schedule:

| Index | Timestep | q_t | Epsilon conversion gain sqrt(a/(1-a)) |
| ---: | ---: | ---: | ---: |
| 0 | 981 | .009393912 | .076217098 |
| 10 | 781 | .019038536 | .213143572 |
| 24 | 501 | .035377406 | .615879976 |
| 25 | 481 | .036744273 | .658233564 |
| 35 | 281 | .056390309 | 1.283822767 |
| 48 | 21 | .707346467 | 7.068953209 |
| 49 | 1 | .293886832 | 24.204590059 |

The first25 q values sum to .5394983 and the last25 to2.9067369. These sums are explanatory local coefficients, **not cumulative watermark gain or a retention bound**: U-Net predictions and coefficient errors change after every step. Large late epsilon gains also warrant explicit fp16 diagnostics. The final step uses `final_alpha_cumprod=a_0`, because `set_alpha_to_one=False`; silently replacing it with one would be another method change.

An isolated reproducible CPU script, [m1_progressive_cpu_diagnosis.py](../scripts/m1_progressive_cpu_diagnosis.py), verifies the source receipt, computes this schedule and compares the real DDIM transition with the formula on synthetic tensors. It uses seed670, alpha.5, timesteps981/501/481/21/1, and eta25/64/100 solely as arithmetic fixtures. It loads no pretrained weights or image pixels. Across15 fixtures, maximum fp32 transition relative error is .000175559; fp16 epsilon changes92.33–99.83% of channel0 coordinates and **zero coordinates in the other three channels**. For eta100, measured post-cast loss ratios span .3163880–.3169617, close to the analytic .31640625. This fails to support wholesale quantization-erasure or a wrong-sign explanation in these fixtures; it does not certify precision behavior on real model trajectories.

The retained CPU report is `research/m1-progressive-cpu-diagnosis.json`, SHA-256 `3c6c9dd04b19f3f8b208be8eb652e57f8eb0af6330fc2ca4f3587a0a0cf22f4d`; script SHA-256 `8e1b993e9007cc330f9e882be43caf773c38a675573023020a9f0b206eaa400e`. Run it with the science Python and `--source-run <original run.json>`; stdout is an algebra/metadata report, not a scientific development run. Synthetic arrays are not additional image trials.

## Newly inspected primary implementation changes the schedule diagnosis

The [GROW primary paper](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html), Sections4.2.1–4.2.3, Algorithm1 and5.2, was read from the retained full text. Its time-index notation motivated our previously declared first-half interpretation. The author's repository has real source under a nested `GROW/` directory, although some root README links return404. Inspecting the implementation resolves what that version actually does; it does not retroactively change the earlier declaration.

Pinned repository revision: **`6aa69a9c5d4a9e75df457fcca8dfc71b64a6b870`**, commit dated2026-05-12. Only `watermark.py`, `utils.py`, `config.py` and `LICENSE` were downloaded as text, **22,827 bytes total**; none was imported or executed. Their receipt is `research/literature/m1-primary-extension/grow-code-6aa69a9c/download-records.json`; license is MIT. Parent owns the shared downloads/bibliographic ledger.

| Inspected implementation | Consequence for comparing with C |
| --- | --- |
| [watermark.py, lines243–258](https://github.com/luopengchen/GROW/blob/6aa69a9c5d4a9e75df457fcca8dfc71b64a6b870/GROW/grow/watermark.py#L243) starts when loop index >=25 | It guides the **last** half, unlike our first-half screen. |
| watermark.py263–287 computes conditional clean prediction, selected-mask mean loss, then CFG | /selected-count is consistent in kind; conditional-before-CFG remains different from our post-CFG operator. |
| [utils.py43](https://github.com/luopengchen/GROW/blob/6aa69a9c5d4a9e75df457fcca8dfc71b64a6b870/GROW/grow/utils.py#L43) implements `fft2(...,norm="ortho").real` in its DCT-named helper | This is a real Fourier transform component, not our orthonormal DCT. |
| config.py17/33/42 defaults fp32, eta200 and all4 channels; mask is a rectangular frequency band | It is neither our fp16/channel0/eta100 screen nor a complete specification match to the paper's stated defaults. |

Source SHA-256: watermark `46cdbe79506a1b0d8b1601313817accd4f2de269dec83013079fcfe17b90dbd5`; utils `8536f3b1c3fc7b51982ae52a70f2777936a80c318029cd5ca593a380f694f229`; config `5d849ea1c1766f1008cf31b6c19e6be71161dde583b2f22fffa6bb0a476b9c71`; license `958a57f511ae7176c2eaf3ed81fc16e4b4dde44efe1f89191bfb44d091bb0c37`.

The real-FFT helper also discards the imaginary component. Applying its real-IFFT helper returns `(x + circular_reflection(x))/2`, generally not x. Independent NumPy algebra verifies that identity to8.88e-16 on a fixed array, with relative reconstruction error .70965. This does **not** prove the upstream watermark fails: its guidance differentiates the operative real-FFT loss and need not use that inverse helper. It does mean that importing its helper while retaining our orthonormal-DCT gradient formula would be incorrect. Do not relabel either method a faithful reproduction or infer that published tables are invalid from these implementation differences.

Together, the actual late schedule and the missing late-stage traces make a controlled phase test substantially better justified than increasing eta, changing the detector threshold or declaring the family exhausted.

## Frozen C-L100 experiment for mechanical implementation

Create a new isolated runner/manifest; do not modify the original script/config or its retained outputs. Keep all four original prompt/seed cases1000–1003, existing assets and scheduler, CFG7.5, DDIM50, eta_sampler0, true orthonormal DCT, channel0, band/positions, eight repetitions and threshold14/16. The only primary algorithm change is early versus late guidance. Freeze alpha.5/eta100 because they are the existing paper-motivated screen values; their observed strongest mean does not turn this follow-up into independent confirmation.

For **each** seed, execute exactly these four generation arms:

1. `C0-replay`: alpha0, no guidance; evaluate against both reference words.
2. `C-E100-replay`: alpha.5/eta100, indices0–24, original word `1011010001101001`.
3. `C-L100`: alpha.5/eta100, indices25–49, the same original word.
4. `C-L100-complement`: identical late operator with target word **`0100101110010110`**. Positions, grouping, noise seed, prompt and alpha remain unchanged.

This is **16 generations**, each50 batched CFG U-Net calls, total **800 calls**. Save clean RGB8 and the unchanged additional VAE-cycle RGB8 for every generation: **32 primary image conditions**, with native and image-DCT diagnostic readouts kept separate. The original-word and complement-word cases have distinct intended-payload fields. Every extracted word reports integer matches against **both intended and original** words, plus the other member of the pair. The original64 SHAKE hypotheses contain neither the original target nor its complement (checked before this run), so keep all64 fixed hypothesis queries unchanged. No payload-conditioned extraction branch or word-dependent mask change is permitted; only the target coefficient signs change.

Compare C0 and early replay PNG byte hashes with their original0031 counterparts. Record mismatches as replay-attribution failures, preserve outputs and diagnose them before treating this as an exact matched replay. Do not invent an original latent hash: none was retained. In the new run, save initial and final latent tensor bytes/hashes for every arm, demonstrate identical initial noise across all four same-seed arms, and retain scheduler timesteps/guided indices. A new-run final latent hash enables future replay checking only.

### Required traces; do not infer the missing stage

At **every** step, retain the128 selected coefficients, word, coefficient-sign matches and MSE to that arm's intended target for: ordinary post-CFG predicted clean latent; corrected predicted clean latent (equal to ordinary on unguided steps); and the effective clean latent recovered from the exact fp16 epsilon supplied to the scheduler. Also retain the128 coefficients of the actual scheduler output state. Name predicted-clean and noisy-state quantities distinctly; their magnitudes and sign stability need not be identical.

Record gradient L2 norm, intended clean correction L2, epsilon correction L2 before/after cast, fraction of changed channel0 fp16 epsilon entries, changed-entry count in the other channels, nonfinite/zero counts, q_t and observed local scheduler displacement. The local unmarked displacement comparator must use the **same current state and original epsilon**, without an extra U-Net evaluation; it is a one-step algebraic counterfactual, not the independent C0 trajectory. DDIM's formula can supply it without mutating scheduler state. Log its discrepancy from q_t times the clean correction, with fp16 rounding explicit.

At the generation endpoint, retain four readout stages:

- `terminal_predecode`: actual final scaled latent, before VAE decoding.
- `clipped_float_cycle`: posterior mode from the clipped float decoded image, before RGB8 rounding, scaled back by.18215. Preserve this as a diagnostic model input distinct from the primary PNG.
- `clean_rgb8`: posterior mode from the saved PNG; this is the primary native clean detector.
- `additional_vae_rgb8`: the existing VAE-cycle channel followed by the same PNG detector.

Save float decoder arrays or their deterministic binary representation/hash, actual latent arrays,128 coefficients for all stages, RGB8 hashes and clipping fraction. Avoid retaining full tensors at all50 steps when the specified coefficient and norm traces suffice. Extraction from the actual final latent is an oracle carrier diagnostic, **not an eligible image-only detector result**. It must not enter the clean image denominator as another success.

For the complementary arm, log accuracy to both words at every stage; never substitute its intended accuracy for original accuracy without labeling it. If outputs merely favor generic signs, changing the target will not produce the predicted opposite response. C0 remains a no-mark null, and complement generation is an intervention on the target, not an independent sample or an ordinary wrong-key test.

## Frozen interpretation, gates and next decisions

Keep generated-pair quality strictly PSNR>35 dB, SSIM>.9, LPIPS<.1 versus the same-seed **new C0** PNG, after successful C0 replay attribution. Report old-C0 comparison too if replay differs, with the difference explicit. This remains preservation of a generated counterfactual, not an existing photograph. Human visual judgment remains absent.

The late carrier passes the bounded necessary-condition gate only if **all eight late outputs** (four seeds x original/complement) reach14/16 against their intended word clean and after the additional VAE cycle, while all four C0 images stay below14/16 against both words on both channels. The complement of a qualifying intended word is automatically a strong mismatch, but still retain its count. The joint quality gate separately requires all eight late clean outputs to meet the three strict metrics. Do not discard complement or difficult seed cases, lower14/16, choose the preferred payload or average away a failure. Report the64-query false findings descriptively; they do not define a population FPR.

- If late guidance changes the intended predicted-clean coefficients as specified, but they decay before the final state, the bottleneck is trajectory transport/scheduler coupling. A later decoder-aware or alternative-transform guidance amendment remains possible; this run does not try it.
- If the final latent qualifies and the clipped-float cycle loses it, the codec channel is the immediate bottleneck. If the float cycle qualifies but RGB8 does not, rounding/clipping is implicated. If clean qualifies but the additional cycle fails, that further autoencoder channel is measured separately. These are stage-local observations, not global impossibility claims.
- If both words qualify clean/VAE and quality passes, freeze the late operator and expand to the existing T3 strengths/seeds before attempting dual content binding. T4/T5 and fixed-photograph preservation remain untested.
- If carrier passes but quality fails, retain the measured quality/bit tradeoff and request the next documented design decision; do not secretly normalize or blend the output. A lower preexisting alpha or an explicit source-preserving route could be reasonable follow-ups, but neither was tested by C-L100.
- If the recorded local equations or replay attribution fail, repair the implementation in a new version before a scientific mechanism conclusion. Do not classify a plumbing failure as evidence against the family.

No population confidence interval is justified by16 dependent generations. The public16-bit word has at most16 bits of nominal payload and no CLIP/OwnerID binding. Even an ideal fair16-bit null would give a14/16-or-better tail of137/65536 per tested word; real majority ties, natural coefficient bias and repeated hypotheses do not satisfy that simple model automatically. Public target re-embedding is forgeable. This experiment is a carrier diagnosis, not a three-state ownership classifier or M1 completion.

Commit the new runner/manifest before model execution and record their actual hashes. Budget **300 seconds,10 GiB GPU allocation or lower available memory minus headroom,16 GiB system RAM,250 MiB new artifacts,USD0**; estimates use the previous172-second28-generation screen and are not guarantees. There is no paid service, new model or large download. Retain started/failed/missing entries for all16 arms and32 image conditions; flush each generation and preserve failed attempts. If a resource limit stops the run, the declared denominator remains unchanged. The parent queues it after current GPU work; this author has not launched it.

Before execution, CPU tests must verify exact old/new phase index sets, paired initialization, target-complement coefficients, identical reference-free extraction bits when only evaluation references change,14/16 boundaries, timestep-dependent q_t, trace stage naming/row completeness, replay hash failure handling and original-output immutability. The existing preflight already validates the original formula; new trace fields and the changed interval still require their own integration checks. The parent-authorized mechanical implementation belongs to the literature/runtime agent, not an unreviewed import of upstream source.

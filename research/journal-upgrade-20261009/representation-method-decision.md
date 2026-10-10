# L1: decoder-tangent carrier with native image-DCT observation

2026-10-10. Prospective development decision by Codex method-design agent, gpt-6-astra, high. No execution, institutional acceptance, or lifecycle transition.

## Decision and hypothesis

Close D3: its immutable estimate 4352.734 exceeds 3300 seconds despite useful proposals. Test a different readout hypothesis: a decoder-tangent perturbation aimed directly at the existing image-DCT semantic carrier can remain readable after regeneration without a VAE watermark reader.

This is a **source-bypass decoder residual**, not pure decoder output or initial-noise writing. A–C and IPS already tested decoder residuals; IPS achieved clean/VAE presence 9/12 each, joint 8/12. The new element is image-DCT-directed latent tangent selection and image-DCT extraction, not residual composition. It is not automatically another independent design family. F5's measured encoder advantage makes failure plausible.

## Fixed construction

Use canonical C0 sources **1675 then 468505**: lowest development ID and a previously observed continuity failure. This is development-adaptive selection, not validation. Retain existing source identities/licenses and 512-square RGB8 preprocessing; access no held-out data.

Let x be source RGB in [0,1], z its unscaled pinned SD1.5 fp32 posterior mode, and D the corresponding decoder converted to RGB [0,1] without clipping. Let P_x be the existing v5 robust image-DCT 320-chip projection, with its normalization and activity weights frozen at x **only for direction construction**. Use the recorded intended source q and public correct-owner semantic table to form its 320-chip W_s.

Compute pixel direction a = gradient_x[W_s dot P_x(x)]. Compute latent direction g = gradient_z[W_s dot P_x(x + D(z)-D(z).detach())]. Project g onto per-channel latent DCT radii **4 <= radius <= 32**, then normalize its Euclidean norm. Stop on zero/nonfinite directions. These derivatives choose a direction; actual saved-image measurements decide success.

Set e = .001 max(||z||,1), r = D(z+e g)-D(z), B=10^(-36/20), and t=e B/RMS(r). Stop if RMS(r)=0 or nonfinite. For fractions **.25,.50,.75,1.00**, render latent arm L as x+D(z+f t g)-D(z), and pixel control P as x+f B a/RMS(a). Clip, round to RGB8, save/reload. No rescaling, direction update, extra fraction, or retry. This compares nominal budgets, not perfectly matched realized distortion.

## Detector and screen

Use v5 native robust image-DCT projections recomputed from every suspect. Retain RC1's semantic/channel logic, public tables, seven-view suspect CLIP, soft binding, radii, roster=1 and thresholds 8.259326826136963/4.982033056390042. Replace only its robust projection provider; no latent tensor or VAE is available to detection. No source, target q, reference residual, amplitude, or search over owners enters the detector. CLIP remains a semantic feature network, so the whole detector is not network-free.

For every fraction/arm/source measure strict source quality and actual semantic calls on clean, deterministic SD1.5 VAE and deterministic SDXL VAE saved RGB8 outputs. Qualification requires clean PSNR>35, SSIM>.9, LPIPS<.1 and **read, exact intended q, found, content_match** in all three conditions. Select the smallest qualifying fraction per arm/source; do not inspect T3 before selection. No qualifying fraction is a screen failure.

For selected images run official SD1.5 DDIM, 20 steps, CFG1, eta0, strengths .1/.2, seeds0–2, preserving safety checks. Run corresponding C0 controls; wrong-owner calls reuse selected pixels. Blocks/missing outputs count unsuccessful, never disappear. Record complete calls, quality, fractions, signed chip displacement, fixed-q score, all32 bit gaps, timings and failures.

Primary success: L qualifies on both sources and recovers exact checked q on all12 planned T3 identities, with zero C0/wrong-owner detections. Pixel-arm results are descriptive; they neither rescue failed L nor require L superiority. Any failure closes this fixed one-direction construction, not all latent methods.

## Capacity, limits and next step

Thirty-two semantic bits use320 chips; h is absent. In the ideal orthogonal-host model, score is sqrt(320) times carrier norm divided by total norm; reaching threshold tau requires carrier/host energy >=tau²/(320-tau²). Individual bit interference adds stricter constraints. This is a necessary model calculation, not measured32-bit channel capacity. Public templates provide no authorization security. Existing searched-pattern bounds assume suitable random-sign null behavior; reused sources, public adaptive attacks and routed decisions do not establish population FPR.

Commit implementation first; retain run.json and one dev-log line. **600seconds inclusive**, USD0, existing local models, <=10GiB allocated VRAM; timeout/OOM closes this screen without cap extension. No new execution infrastructure. Only a survivor permits a separately preregistered twelve-source dual-tier writer and unchanged M1a/T3/T4/T5 assessment. No M1 passage or full32+32-bit method follows here.

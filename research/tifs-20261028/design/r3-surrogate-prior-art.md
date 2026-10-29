# R3 predicted-clean surrogate: bounded prior-art assessment

2026-10-29. Author research assistance, not an independent review or novelty clearance. This file changes no R3 design, arm, threshold, code, baseline or execution permission. No scientific outputs exist. Only three substantive primary papers were newly opened for this check; no files, code, models, weights or images were downloaded. The authoritative MAIN STATE was read once. Local context: `r3-denoiser.md`, `../09-round3-amendment.md`, `../02-prior-art-delta.md` and `../literature/r2-prior-art-check.md`.

## Answer

**The inspected literature already occupies the central ingredients: watermark losses on a one-evaluation predicted clean latent, differentiating watermark recovery through frozen denoising components, and training-free guidance from an unchanged reader. The exact combined F6-x0 post-hoc RGB optimization construction was not established in these three methods. Its novelty remains unverified.** A difference in optimization variable, reader and sampled native window is a concrete implementation distinction; it does not by itself establish a publishable scientific contribution. An absence in a bounded inspection is not evidence of absence across the literature.

## Three inspected primary sources

### 1. DrawMark: the closest predicted-clean training analogue

[Author-hosted ICASSP 2026 manuscript](https://msf-hnu.github.io/resource/DrawMark_Defeating_Regeneration_Attacks_by_Embedding_Watermark_into_Predicted_Noise_of_Diffusion_Models%20%281%29.pdf), DOI 10.1109/ICASSP55912.2026.11464504. Opened through the PDF link on the authors' publications page after direct URL opening failed. Inspected sections 2.1-2.4 and 3.1-3.3, printed pages 13458-13460.

**Direct evidence:** equation 3 is the same epsilon-to-clean-latent reconstruction algebra used in F6-x0. Training encodes covers, samples a timestep/noisy latent, predicts noise, obtains a single-step estimated clean latent, decodes it and applies watermark/fidelity losses. The diffusion backbone is frozen, but trainable noise-steering adapters alter its features and a watermark decoder is learned. Evaluation uses SD2.1-generated images and includes a 40-step diffusion-regeneration attack; Table 1 reports 0.975 bit accuracy for the 48-bit arm.

**Inference:** predicted-clean reconstruction, sampled noisy-cover training and a decoded watermark objective cannot be claimed as new. This is not the same fixed-reader per-image RGB PGD: its optimized objects are adapters/decoder and its inference embeds during generation. Its recovery result does not establish our content acceptance or strict source-preservation endpoint. The paper does not establish the input-Jacobian behavior of our unmodified native UNet. **Classification: ingredient preemption; very close operator analogue, not demonstrated exact-construction preemption.**

### 2. Robust-Wide: frozen-denoiser gradients for a post-hoc image embedder

[arXiv 2402.12688v3](https://arxiv.org/html/2402.12688v3), dated 17 July 2024. Inspected sections 3.1-3.5 and 4.1-4.5, equations 4-8 and Tables 1-2.

**Direct evidence:** an image embedder and watermark extractor are jointly trained. PIDSG freezes the editor's VAE, UNet and CLIP, truncates the first T-k sampling steps, then allows gradients through the final k steps. The source-image latent conditions the editor. Clean and edited watermark recovery losses both appear in the total objective. The default editor is InstructPix2Pix; Table 2 reports edited BER 2.6579% with PIDSG versus 50.1558% without it, with materially different achieved PSNR. Section 4.3 also evaluates null-prompt SDEdit at strength .2.

**Inference:** backpropagating watermark-recovery loss through a frozen denoiser to improve the robustness of marks in pre-existing images, combining clean/edited losses and limiting differentiated denoising for memory are occupied ideas. The method uses learned embedder/extractor and a partially differentiated full editor, rather than F6-x0's fixed reader and one-evaluation native predicted-clean surrogate. Its ablation is evidence under its protocol, not a transportable effect size or proof that our surrogate approximates regeneration. **Classification: broad denoiser-gradient preemption; close task analogue, not demonstrated exact-construction preemption.**

### 3. Guidance Watermarking: unchanged-reader guidance and its gradient approximation

[arXiv 2509.22126v2](https://arxiv.org/html/2509.22126v2), dated 7 May 2026; venue identity was checked in the earlier R2 card. Inspected sections 4.1-4.5, 5.1-5.4 and Appendix B.2.

**Direct evidence:** equations 5-8 guide diffusion with an off-the-shelf reader and transformation losses. Section 4.5 approximates the remaining diffusion derivative by an identity and activates guidance later. Appendix B.2 qualitatively reports instability and reduced detectability with full backpropagation. Its prose, Table 6 row and caption inconsistently name Simplification 1/2, so this inspection does **not** extract an isolated numerical backpropagation effect. The main augmentation set is not our empty-prompt native regeneration-window objective.

**Inference:** training-free fixed-reader guidance and augmentation exposure are occupied. The identity-gradient approximation differs from F6-x0's native-denoiser derivative; in-generation steering differs from source-constrained post-hoc RGB optimization. **Classification: fixed-reader machinery preemption, not demonstrated exact-construction preemption.** More derivative is not automatically better; the source ambiguity prevents a precise causal effect claim here.

## What is distinctive in the current construction, without asserting novelty

The registered F6-x0 operator begins with a fixed source photograph and posterior-mode latent z=E(x); forms z_t=a_t z+b_t epsilon; evaluates the unmodified frozen native epsilon UNet once; reconstructs z0hat=(z_t-b_t epsilon_theta)/a_t; decodes; and applies the unchanged F5 semantic reader. It retains differentiation through epsilon_theta. R0/R1 use their native empty-prompt conditioning at guidance 1, with a sampled executed-window timestep. The current writer uses serial clean and surrogate gradients over 150 robust updates followed by 50 clean refinement updates. None of those statements is a measured gain.

An elementary chain-rule observation helps specify the claimed distinction. Holding t, epsilon and conditioning fixed, with f(z_t)=epsilon_theta(z_t,t,c), the ideal real-arithmetic latent derivative is

\[
\frac{\partial\widehat z_0}{\partial z}=I-b_t J_f(z_t).
\]

Thus the surrogate includes the native denoiser's input Jacobian; detaching its prediction would remove that term and leave the identity. This is algebra about the chosen operator, not a new robustness theorem, a numerical gradient validation or an assertion that its derivative matches the full attack. Native preprocessing, casts, encoding and decoding still surround it. A finite nonzero input gradient alone cannot demonstrate a useful gradient direction or final diffusion survival.

## Scientific claims constrained by the present design

1. **Package contrast only:** F6-x0 samples the native executed window while F6-noise uses the first native timestep. Their comparison changes both denoiser inclusion and timestep exposure. Even an eventual gain cannot isolate the denoiser's causal contribution. No new arm is proposed here.
2. **Budget and compute:** nominal robust-radius matching does not imply equal final perceptual distortion. F6 additionally uses surrogate reader/UNet gradients; F5-budget is not computation matched. A pass supports the declared empirical comparison only, not denoiser-specific attribution or computational superiority.
3. **Surrogate fidelity:** one predicted clean state is neither the complete native denoising trajectory nor a proven approximation to its watermark-reader response. First-step operator parity validates a conditional implementation check; it does not validate posterior-mode versus sampled encoding, all later steps, or the final PNG channel.
4. **Transfer scope:** K3 is excluded from gradients but is visible during Stage P selection. Report gradient-excluded, selection-seen transfer; do not call it an untouched unseen-family test. R0/R1 survival would concern exposed families.
5. **Reader/task scope:** arbitrary-message bit recovery, presence detection and original semantic-code/content acceptance are different endpoints. Prior performance numbers cannot be inserted into F5's compound acceptance rule or used as evidence for T4/T5 security, rare-event rates, lawful ownership or unique-instance binding.
6. **Selection and evidence:** no scientific run, gain, human quality judgment, server feasibility or TIFS readiness is established. The proposed profile can pass without mandatory superiority over every mechanism control; such a pass does not automatically establish a new mechanism. Retain all negative controls and failed configurations under the existing protocol.

Suggested prospective wording: *We evaluate whether a one-evaluation, native predicted-clean denoiser surrogate improves a fixed-reader, source-constrained post-hoc watermark writer under the registered regeneration and quality protocol.* If results later support it, describe the measured package improvement and its uncertainty; avoid first predicted-clean watermark, first denoiser-gradient robustness, first training-free fixed-reader writer, denoiser-isolated causal gain or certified regeneration robustness.

## Search and unresolved boundaries

Queries included `watermark regeneration surrogate denoising predicted clean`, `watermark robustness diffusion one-step surrogate`, `watermark predicted clean gradient diffusion`, `Robust-Wide partial denoising gradient`, and `image watermark denoiser surrogate gradient regeneration`. Search results were discovery leads only. The three substantive full methods above were the bounded inspection set. Their sections, versions and links identify the evidence; qualitative preemption classifications are author inference, not legal or bibliometric priority judgments. No source-code behavior was independently verified.

ForenMark remains skipped/full-text unavailable under the session instruction. The earlier R2 and wider prior-art/access qualifications remain in force, including the already recorded ONRW post-hoc fixed-reader precedent. This report neither clears overlap with uninspected work nor replaces the sole official R3 independent review. It recommends no change to R3 items; it sharpens their final novelty limitation.

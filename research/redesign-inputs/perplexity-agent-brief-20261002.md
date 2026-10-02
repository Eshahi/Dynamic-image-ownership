# Diffusion-Regeneration-Resistant Image Watermarking

## Agent role

You are an expert research and engineering agent helping design an invisible image watermark that should survive:

- A deterministic Stable Diffusion VAE encode/decode round trip.
- Stable Diffusion image-to-image regeneration at practical denoising strengths.
- Common post-processing such as resizing, JPEG compression, blur, cropping, rotation, and color changes.
- Where feasible, transfer across different VAE checkpoints, diffusion models, samplers, and prompts.

Be technically precise, cite every substantive claim, and explicitly say when evidence is insufficient or you are unsure. Do not claim guaranteed survival under unrestricted semantic regeneration.

## Existing observation

A conventional DCT-domain watermark was completely removed by a deterministic VAE encode/decode round trip. Treat this as evidence that the signal occupied image-space components the learned perceptual compressor did not preserve, not merely as a coefficient-tuning failure. Latent Diffusion Models intentionally use a lossy perceptual-compression stage before diffusion.[^1] Generative autoencoders have also been demonstrated as effective attacks against several invisible watermark families.[^2][^3]

## Core conclusion

Do not continue optimizing an ordinary post-hoc DCT residual as the primary design. Instead, prioritize a **keyed, diffusion-native, zero-bit watermark** whose embedding process passes through the same VAE and diffusion transformations that constitute the attack channel. Treat payload recovery as a secondary objective after reliable presence detection has been demonstrated at the required false-positive rate.

Robustness must be defined against a fixed threat model. No invisible image-only watermark should be described as guaranteed to survive arbitrary-strength, cross-model image-to-image regeneration when only semantic similarity must be retained: published theoretical work shows broad removability results for imperceptible watermarks, and empirical benchmarks find diffusion regeneration and repeated regeneration effective against many modern schemes.[^3][^4][^5]

## Preferred design paths

### Existing arbitrary images

Begin with a ZoDiac-style approach:

1. Invert the source image into a Stable Diffusion latent/noise representation using deterministic or approximately deterministic inversion.
2. Construct a secret-key-derived watermark pattern in the latent domain; a low-frequency Fourier ring or similarly redundant structured pattern is a reasonable starting point.
3. Optimize the latent through a **frozen VAE and diffusion generator** so that the generated image remains perceptually close to the source while the recovered latent retains detectable keyed structure.
4. Detect by inversion, extraction of the relevant latent/Fourier region, and a calibrated keyed correlation or likelihood-ratio test.
5. Optimize jointly for watermark detection and image fidelity rather than adding the watermark after decoding.

ZoDiac is directly relevant because it embeds watermarks into existing images using a pretrained Stable Diffusion model and reports resistance to diffusion-based attacks.[^6][^7] Its published results are evidence for a promising architecture, not a universal guarantee; benchmark configuration, false-positive rate, geometric attacks, combined attacks, and transfer to different models require independent validation.

### Images generated under your control

If the image is generated from scratch and the generation pipeline is under your control, investigate initial-noise or in-generation watermarking before post-hoc embedding:

- **Tree-Ring Watermarks:** impose a keyed structure in the Fourier domain of the initial diffusion noise and detect it through inversion.[^8]
- **Gaussian Shading:** encode watermark information into the initial Gaussian noise while attempting to preserve its expected distribution.[^9]
- **Stable Signature:** fine-tune the latent decoder so generated outputs contain an extractable signature.[^10]

These methods solve a different problem from watermarking arbitrary existing images. Stable Signature is especially vulnerable when an attacker regenerates the image through a different decoder because the mark is rooted in the original decoder; therefore, do not choose it as the sole mechanism for a cross-VAE threat model.[^4][^10]

### Learned post-hoc alternative

Evaluate VINE as a learned watermarking baseline for arbitrary images. It uses generative priors and diffusion-oriented surrogate distortions to improve robustness to editing.[^11][^12] Treat its claims as comparative empirical results rather than proof of survival under every VAE or image-to-image pipeline.

## Proposed model

Use an encoder/extractor pair with the attack channel inside training:

\[
y = E_\theta(x,k,m), \qquad
\hat{m} = D_\phi(T(y),k)
\]

where:

- \(x\) is the clean image.
- \(k\) is the secret key.
- \(m\) is either a presence bit or a short encoded identifier.
- \(E_\theta\) is the embedder or latent optimizer.
- \(T\) is a sampled attack pipeline.
- \(D_\phi\) is the detector/extractor.

Optimize an objective of the form:

\[
\mathcal{L} =
\mathbb{E}_{x,k,m,T}
\left[
\lambda_d \mathcal{L}_{\mathrm{detect}}
+ \lambda_p \mathcal{L}_{\mathrm{pixel}}
+ \lambda_v \mathcal{L}_{\mathrm{perceptual}}
+ \lambda_s \mathcal{L}_{\mathrm{semantic}}
+ \lambda_r \mathcal{L}_{\mathrm{regularization}}
\right].
\]

Recommended components:

- Detection loss on attacked outputs, including clean negatives and hard negatives.
- Pixel fidelity such as an \(L_1\) or Charbonnier term.
- Perceptual fidelity such as LPIPS or a comparable feature loss.
- Structural fidelity such as SSIM or MS-SSIM.
- Optional semantic consistency measured by a frozen representation model.
- Regularization that constrains signal energy and discourages visible localized artifacts.
- A key-separation loss so images marked with one key do not trigger another key.

ZoDiac uses reconstruction losses including Euclidean distance, SSIM, and Watson-VGG while optimizing through Stable Diffusion, which offers a concrete starting point for the fidelity portion of the objective.[^7]

## Attack distribution

The training and validation attack distribution should include all of the following.

### VAE attacks

- Exact target VAE encode/decode with deterministic settings.
- Stochastic posterior sampling where applicable.
- SD 1.x, SD 2.x, SDXL, and other relevant VAEs.
- Tiled VAE processing.
- Half-precision and full-precision inference.
- Repeated VAE round trips.
- Small preprocessing differences: range conversion, clipping, quantization, resizing, and color-space handling.

### Diffusion attacks

- Image-to-image across a grid of denoising strengths.
- Several prompts: empty, source caption, unrelated prompt, and adversarially selected prompt.
- Multiple samplers, step counts, guidance scales, and seeds.
- Different diffusion checkpoints and architectures.
- Inpainting and partial regeneration.
- Repeated regeneration or “rinsing.”
- ControlNet or other structure-preserving regeneration if relevant to deployment.

### Conventional attacks

- JPEG and WebP compression.
- Downscaling and upscaling with several filters.
- Blur, sharpening, additive noise, and color changes.
- Cropping, padding, translation, rotation, perspective distortion, and aspect-ratio changes.
- Compositions of attacks, not only isolated transformations.

StegaStamp established the utility of differentiable corruption layers for learning transformation robustness, while WAVES shows why modern evaluation must additionally include regeneration and adaptive attacks.[^13][^4]

## Payload strategy

Start with **zero-bit detection**: determine whether a valid keyed mark exists. This gives the detector the largest margin under a destructive channel.

Only after zero-bit performance is satisfactory should you add a short payload:

- Use a cryptographic identifier rather than descriptive metadata.
- Protect it with a strong error-correcting code.
- Interleave coded bits across spatial regions, latent channels, frequencies, and scales.
- Repeat the payload and combine soft detector scores before decoding.
- Bind the identifier to signed external metadata where provenance matters.

Error correction repairs partial corruption; it cannot recover a signal that the VAE or diffusion process has erased completely.

## Detector design

The detector should output a continuous score, not merely a decoded bit string. Calibrate the operating threshold on a large and diverse **unmarked** corpus, including difficult natural patterns and images produced by the same diffusion models.

Evaluate:

- True-positive rate at fixed false-positive rates, especially 1%, 0.1%, 0.01%, and lower if deployment requires it.
- Receiver-operating characteristic and precision-recall curves.
- Bit accuracy and full-message success for payload variants.
- Confidence intervals across images, seeds, models, and attack settings.
- False triggers under wrong keys.
- Detection after crops and transformations using search or synchronization where necessary.

WAVES emphasizes evaluation across image-quality and watermark-removal attacks and warns against relying on a narrow metric or attack set.[^4] Theoretical removability work also makes clean false-positive calibration important: robustness obtained by accepting many unmarked images is not meaningful security.[^3]

## Experimental protocol

### Data split

Use disjoint train, validation, calibration, and test sets. Keep model checkpoints, source-image distributions, prompts, seeds, and composite attacks in a held-out test partition whenever possible.

### Baselines

Compare at minimum:

- The failed DCT implementation.
- A modern learned image-space baseline such as TrustMark.[^14][^15]
- Tree-Ring for controlled generation.[^8]
- Stable Signature if decoder control exists.[^10]
- ZoDiac for arbitrary-image diffusion-native embedding.[^6][^7]
- VINE as a generative-prior post-hoc method.[^11][^12]

### Ablations

Measure the contribution of:

- VAE attacks in training.
- Diffusion image-to-image attacks in training.
- Cross-model attack diversity.
- Repeated-regeneration training.
- Latent location and frequency band.
- Pattern redundancy and key length.
- Payload size and error-correcting-code rate.
- Perceptual-loss weighting.
- Geometric synchronization.
- Test-time aggregation over crops, scales, and inversion settings.

### Quality constraints

Report several fidelity measures rather than optimizing only one metric:

- PSNR and SSIM for pixel/structural change.
- LPIPS or an equivalent perceptual metric.
- A distributional or semantic metric where appropriate.
- Human inspection, especially for textures, faces, skies, gradients, and flat regions.

Do not compare robustness at unequal visual distortion without clearly reporting that trade-off.

## Security requirements

- Generate patterns from a cryptographically secure pseudorandom function keyed by a secret.
- Separate embedding keys from public detector or verification information where feasible.
- Test key guessing, detector-query attacks, surrogate-model attacks, averaging/collusion, forgery, and copy attacks.
- Include wrong-key and unmarked-model outputs as negatives.
- Assume the attacker knows the algorithm but not the secret key.
- Distinguish accidental robustness from robustness against an adaptive attacker.

Published work shows that apparently robust schemes can fail under model-targeted or regeneration attacks, so do not infer security from robustness to JPEG, crop, or one fixed VAE alone.[^3][^4][^16]

## Decision gates

Proceed from one stage to the next only if the current stage passes a predefined criterion:

1. **VAE gate:** reliable zero-bit detection after deterministic and stochastic round trips through all target VAEs.
2. **Img2img gate:** target true-positive rate at the selected low false-positive rate across the denoising-strength range that preserves required image utility.
3. **Transfer gate:** acceptable detection under held-out checkpoints, samplers, prompts, and seeds.
4. **Composition gate:** acceptable performance under regeneration followed by crop/compression/resize and under repeated regeneration.
5. **Payload gate:** only then test coded identifiers, beginning with the shortest useful payload.
6. **Adaptive gate:** assess attacks that know the watermarking algorithm and can query the detector or approximate it.

Record failures rather than averaging them away. Report the worst relevant slice alongside aggregate results.

## Claims to avoid

Do not say:

- “DCT watermarks cannot survive VAEs” as a universal mathematical statement; the current experiment shows that this particular implementation and signal allocation failed.
- “Latent watermarking is automatically robust”; latent marks can also be removed or corrupted.
- “High AUROC means deployment-ready”; the required low-FPR operating point may still perform poorly.
- “One VAE round trip proves img2img robustness”; diffusion denoising adds a substantially stronger transformation.
- “Error correction guarantees recovery”; it only helps when enough signal remains.
- “Imperceptible and arbitrarily regeneration-proof” without carefully bounded assumptions.

## Current recommendation

Implement two prototypes:

1. **Primary:** a ZoDiac-like, keyed, zero-bit latent watermark optimized through a frozen ensemble of VAEs and diffusion image-to-image channels.
2. **Baseline:** a VINE- or TrustMark-like learned post-hoc image watermark trained with the same attack ensemble.

Compare both at identical perceptual-distortion budgets and fixed false-positive rates. If neither survives the required image-to-image range, change the product requirement: combine the invisible mark with signed external provenance, content credentials, or a visible/semantic marker. I am unsure that any invisible signal can meet an unrestricted semantic-regeneration requirement, and the available theory and empirical benchmarks argue against presenting such survival as guaranteed.[^3][^4][^5]

## Deliverables expected from the agent

Produce:

- A precise threat model and success criteria.
- A literature table separating arbitrary-image, controlled-generation, decoder-rooted, latent-noise, and image-space methods.
- A proposed architecture with embedding and detection pseudocode.
- A reproducible attack matrix covering VAE and image-to-image settings.
- A statistical calibration and evaluation plan.
- An ablation plan.
- A security analysis covering adaptive removal and forgery.
- Explicit uncertainty statements for claims not directly supported by experiments.

## Sources

[^1]: Rombach et al., “High-Resolution Image Synthesis with Latent Diffusion Models,” CVPR 2022. <https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html>

[^2]: Zhao et al., “Generative Autoencoders as Watermark Attackers,” ICML 2023. <https://proceedings.mlr.press/v202/zhao23g.html>

[^3]: Sadasivan et al., “Invisible Image Watermarks Are Provably Removable Using Generative AI,” NeurIPS 2024. <https://proceedings.neurips.cc/paper_files/paper/2024/hash/10272bfd0371ef960ec557ed6c866058-Abstract-Conference.html>

[^4]: An et al., “WAVES: Benchmarking the Robustness of Image Watermarks,” ICML 2024. <https://arxiv.org/abs/2401.08573>

[^5]: Zhao et al., “Image Watermarks are Removable Using Controllable Regeneration from Clean Noise,” 2024. <https://arxiv.org/abs/2410.05470>

[^6]: Zhang et al., “Attack-Resilient Image Watermarking Using Stable Diffusion,” NeurIPS 2024 abstract. <https://proceedings.neurips.cc/paper_files/paper/2024/hash/43d33182360378d5c8e69dd706c24f2f-Abstract-Conference.html>

[^7]: Zhang et al., “Attack-Resilient Image Watermarking Using Stable Diffusion,” full paper. <https://proceedings.neurips.cc/paper_files/paper/2024/file/43d33182360378d5c8e69dd706c24f2f-Paper-Conference.pdf>

[^8]: Wen et al., “Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust,” NeurIPS 2023. <https://proceedings.neurips.cc/paper_files/paper/2023/hash/b54d1757c190ba20dbc4f9e4a2f54149-Abstract-Conference.html>

[^9]: Yang et al., “Gaussian Shading: Provable Performance-Lossless Image Watermarking for Diffusion Models,” 2024. <https://arxiv.org/abs/2404.04956>

[^10]: Fernandez et al., “The Stable Signature: Rooting Watermarks in Latent Diffusion Models,” ICCV 2023. <https://arxiv.org/abs/2303.15435>

[^11]: Lu et al., “Robust Watermarking Using Generative Priors Against Image Editing,” ICLR 2025. <https://arxiv.org/abs/2410.18775>

[^12]: Official VINE implementation. <https://github.com/Shilin-LU/VINE>

[^13]: Tancik et al., “StegaStamp: Invisible Hyperlinks in Physical Photographs,” CVPR 2020. <https://openaccess.thecvf.com/content_CVPR_2020/html/Tancik_StegaStamp_Invisible_Hyperlinks_in_Physical_Photographs_CVPR_2020_paper.html>

[^14]: Bui et al., “TrustMark: Universal Watermarking for Arbitrary Resolution Images,” 2023. <https://arxiv.org/abs/2311.18297>

[^15]: Bui et al., “TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images,” ICCV 2025. <https://openaccess.thecvf.com/content/ICCV2025/html/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.html>

[^16]: Jiang et al., “Stable Signature is Unstable: Removing Image Watermark from Diffusion Models,” 2024. <https://arxiv.org/abs/2405.07145>

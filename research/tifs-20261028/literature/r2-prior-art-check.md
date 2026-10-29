# Round 2 primary-method check: F6 and the bound-carrier control

Date: 2026-10-29. Author: Codex research agent. Scope: seven requested papers; ForenMark is handled separately by the session lead. This is a bounded priority check, not an exhaustive novelty certificate. Only paper/official venue pages were read; no scientific execution, package installation, model/image/code download or server access occurred. Section/equation locators below are stable within the named versions; browser line numbers are secondary locators.

## Decision for the pre-output amendment

**Generic semantic/content binding is pre-empted. Training-free optimization through a fixed reader, diffusion-aware insertion, augmentation losses and robust learned carriers are also pre-empted.** The inspected methods do not establish an identical construction to F6's constrained post-hoc pixel optimization through finite native-noise codec surrogates with the unchanged F5 semantic consistency reader. That narrow distinction remains an untested empirical hypothesis, not a claim of firstness.

VINE-B is necessary as a strong control for whether the F6 writer adds value beyond transporting the same content code with a published carrier. A VINE-B win cannot by itself move the article novelty to a generic content-bound robust-carrier protocol: that protocol-level idea is already occupied. Such a move would require an independently defensible property and evidence beyond the carrier substitution. Conversely, F6 beating VINE-B is evidence about the declared task/quality/reader envelope, not proof that no prior method could do the task.

Suggested selection wording: “We test whether finite native-noise codec exposure adds original semantic-code retention beyond matched codec/augmentation writers and a content-bound published robust carrier, under a fixed reader and source-preserving quality constraints.” Avoid “first semantic binding,” “first robust bound carrier,” “first optimization watermark,” or a claimed cryptographic ownership guarantee.

## Inspected method cards

### SemBind, arXiv 2601.20310v1

[Full method](https://arxiv.org/html/2601.20310v1), sections 2.3, 3.1–3.3; HTML lines 129–173 and 200–212. A private learned semantic masker converts an image to bits. A same-prompt auxiliary clean generation supplies the embedding code; secret permutation and tiling turn it into a sign mask that modulates an existing initial-noise watermark. Verification recomputes the code from the suspect, inverts diffusion, removes the modulation and invokes the base decoder. Required artifacts include the private masker, permutation/base keys and inversion model; this is not a lightweight pixel-only reader.

**Pre-empts:** binding a published watermark to a recomputed semantic code to resist transfer; compatibility with multiple carriers. **Difference:** generation-time latent modulation and a trained private semantic representation, rather than a fixed public F5 rule in a post-hoc photograph writer. A public descriptor gives an attacker different knowledge; do not borrow its anti-forgery guarantee. No identical F6 finite-codec pixel objective was found in these sections.

### MetaSeal, arXiv 2509.10766v2

[Full method](https://arxiv.org/html/2509.10766v2), sections 5.1–5.3, Definition 1 and equations 6–15; HTML lines 210–295. It signs a semantic image caption, packages the caption/signature in a QR pattern and embeds via an invertible network with DWT. The reader recovers both message and signature and verifies with a public key. Importantly, section 5.1 says suspect-to-caption similarity is supplementary: exact cryptographic verification checks recovered message/signature. No per-image registry is intrinsic to that definition. Appendix C/Figure 11 explicitly reports failed verification after diffusion regeneration.

**Pre-empts:** self-contained content-dependent signed image attribution and a learned robust carrier. **Difference:** a 100-bit keyed VINE-B payload is not its large signed caption/QR construction; public label conditioning is not a public-key signature. **Caution:** signature validity proves authorization of the recovered message, not uniqueness of the suspect's visual instance. Regeneration survival remains a distinct carrier requirement; no F6-style finite native-noise objective was found.

### Dual-Guard, arXiv 2604.19090v1

[Full method](https://arxiv.org/html/2604.19090v1), sections 3.1–3.5; HTML lines 139–183. It puts a registered fingerprint into Gaussian Shading initial noise and a trained final-latent residual codec. Full verification assumes a candidate record already resolved, retrieves a per-image key/fingerprint/reference latent and combines provenance with latent integrity/localization evidence. Section 3.1 explicitly distinguishes claimed-record verification from open-set search and excludes stronger adaptive white-box joint attacks.

**Pre-empts:** two complementary robust/content channels and reference-assisted verification as generic novelty. **Difference:** its main content anchor is stored latent reference comparison plus learned codec, not VINE-B's recomputed F5 semantic rule without a per-image reference registry. It does not justify claiming that a short semantic code uniquely binds an operational instance. Its regeneration provenance result must not be equated with joint content authentication after regeneration. The inspected method is not an F6 pixel writer.

### Guidance Watermarking, arXiv 2509.22126v2

[Full method](https://arxiv.org/html/2509.22126v2), sections 4.1–4.5, equations 5–9; HTML lines 146–184. It guides diffusion using gradients from an off-the-shelf fixed decoder, with message/cosine loss. Transformation-specific losses are combined using PCGrad. The practical approximation replaces backward diffusion gradient propagation with an identity and activates guidance only after a chosen step. Detection uses the existing decoder/reference message; the procedure does not supply a semantic-content consistency rule.

**Pre-empts:** training-free fixed-reader guidance, differentiated image augmentations, improving decoder robustness without reader retraining, and approximate gradients through diffusion. **Difference:** in-generation guidance modifies the denoising trajectory; F6 optimizes a constrained pre-existing RGB image using codec/noise surrogates without that trajectory. A new native-noise term must beat matched augmentation exposure; the use of gradients, multiple models or differentiable surrogates alone cannot carry novelty. No same construction was found in the inspected method.

### DrawMark, author-hosted five-page IEEE manuscript

[Full text](https://msf-hnu.github.io/resource/DrawMark_Defeating_Regeneration_Attacks_by_Embedding_Watermark_into_Predicted_Noise_of_Diffusion_Models%20%281%29.pdf), sections 2.2–2.4, equations 3–7, printed pages 13458–13459 (PDF pages 2–3). It trains noise-steering adapters in U-Net decoder features and a watermark reader while freezing the diffusion backbone. Training encodes cover images, samples noisy latents, predicts watermark-bearing noise, estimates the clean latent and decodes to RGB. Losses combine cover distortion, LPIPS, message recovery and timestep-weighted noise prediction. Inference activates embedding according to a convergence/SNR criterion. Section 3.1.3 evaluates VAE compression and diffusion regeneration.

**Pre-empts:** training on noisy encoded covers, noise-aware generative insertion, timestep-aware optimization and regeneration robustness claims. **Difference:** learned U-Net adapters and a trained reader, not per-image constrained RGB optimization with unchanged F5 readout. Consequently “noise-aware watermarking” is too broad a novelty claim; the actual finite-surrogate/fixed-reader control comparison remains the candidate distinction. Its arbitrary-message recovery does not establish semantic binding or F5's instance acceptance property.

### OptMark, arXiv 2508.21727v1

[Full method](https://arxiv.org/html/2508.21727v1), sections 3.2–3.5, equations 5–13; HTML lines 111–168. It optimizes structural and detail watermark vectors inserted at initial and intermediate denoising timesteps. A pretrained self-supervised image extractor and fixed carrier vectors recover the message; the message hinge loss is coupled with latent-distribution regularizers. An adjoint method reduces gradient memory. This is an inference-time optimization method, with a fixed feature reader, rather than a newly trained reader.

**Pre-empts:** optimized latent multi-bit insertion, two insertion points, fixed-feature decoding and gradient-memory engineering as novelty. **Difference:** generated-image latent vectors/trajectory versus a source-constrained post-hoc RGB writer exposed to finite codecs/native noise. The method sections do not define owner/content-bound payload acceptance from a suspect-recomputed F5 code. It is therefore a machinery precedent, not evidence that arbitrary message decoding equals original semantic-code consistency.

### ONRW, arXiv 2601.17388v1

[Full method](https://arxiv.org/html/2601.17388v1), section 3.2 equations 2–10, section 4.1 and Appendix A.1–A.2; HTML lines 123–165 and 342–373. It null-text-inverts a pre-existing image, optimizes inversion noise and denoises to a watermarked image. Objectives combine message recovery after simulated image attacks, self-attention preservation and masked reconstruction; foreground masks come from cross-attention. Section 4.1 explicitly says no additional training or reader retraining; Appendix A.1 specifies the pretrained whitened HiDDeN extractor. Wording about “training” in section 3.2 should not be mistaken for a new trained reader.

**Pre-empts:** training-free source-image watermark optimization in noise with a fixed pretrained extractor and semantic preservation constraints. **Difference:** full inversion/denoising optimization rather than finite codec/noise surrogate optimization of RGB. Its random 48-bit messages are not a recomputed owner/content-binding rule. Do not describe F6 as first post-hoc fixed-reader optimization, or treat source preservation alone as its distinguishing contribution.

## Venue verification and access receipt

| Work | Official identity evidence opened on 2026-10-29 | Allowed wording |
|---|---|---|
| SemBind | [ICML 2026 official downloads](https://icml.cc/Downloads/2026), title at listing line 5495, points to poster 63877; poster fetch restricted | ICML 2026 listing verified; method comparison uses arXiv v1, not an assumed final proceedings version |
| Guidance Watermarking | [Official ICLR proceedings record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/b9501301a7a0f99e57406cc901f4e3ce-Abstract-Conference.html), explicitly ICLR 2026 Conference; also [official downloads](https://iclr.cc/Downloads/2026) | ICLR 2026 verified; method comparison uses arXiv v2 |
| DrawMark | [Official ICASSP paper 2721](https://cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=2721), IFS-L5.4, May 7 presentation | ICASSP 2026 verified; method inspected in author-hosted IEEE manuscript |
| OptMark | [Official AAAI record](https://ojs.aaai.org/index.php/AAAI/article/view/38094), March 14 2026, volume 40(13), pages 11150–11158, DOI 10.1609/aaai.v40i13.38094 | AAAI 2026 verified; method comparison uses arXiv v1 |
| MetaSeal | [Author arXiv record](https://arxiv.org/abs/2509.10766) says “To appear at TMLR 2026”; linked [OpenReview record](https://openreview.net/forum?id=8i3ErmCfdJ) blocked by browser verification. Search-indexed older OpenReview PDFs say under review | Use arXiv v2, author-reported to appear TMLR 2026; drop the unsupported precise “TMLR 02/2026” publication label |
| Dual-Guard; ONRW | Versioned arXiv full texts above; no accepted venue was independently established in this bounded check | arXiv preprint |

All seven relevant primary methods were inspected, rather than relying on abstracts. DrawMark direct URL initially failed in the browser tool; following PDF link 47 from the [authors' publications page](https://msf-hnu.github.io/publications/) succeeded and yielded five pages/492 text lines. OpenReview challenge pages were not bypassed. No quantitative performance claim here is independently reproduced. No evidence in this check clears ForenMark or establishes a complete prior-art search.

## ForenMark access receipt

Lead-agent checks, 2026-10-29: the exact expected file was `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-tifs/papers/forenmark.pdf`. It was absent at the start, each item boundary, subsequent manual checks, and the final 13:18:10 UTC check. The 13:17:58 UTC Downloads scan also found no PDF. No file was supplied for inspection during this window.

The [publisher page](https://www.sciencedirect.com/science/article/pii/S0950705126018101), DOI 10.1016/j.knosys.2026.117084, was the only primary paper route returned by public title, DOI and author searches. Direct full-text opening returned HTTP 403; indexed results provided a preview and section snippets only. Searches included `ForenMark pdf`, the exact title plus `pdf`, the DOI plus `full text`, and the title with the listed authors. No complete method/results or accessible author manuscript was located. No access restriction was bypassed, no abstract performance number is treated as inspected evidence, and no full-text claim is made.

**Disposition: FULL-TEXT UNINSPECTED.** BRIEF-R2 directs this disposition if the file is still absent with forty minutes remaining. The seven-paper inspection is complete; the ForenMark overlap remains an explicit unresolved novelty limitation. This access disposition permits finishing the requested preparation package, not asserting publication novelty or submission readiness.

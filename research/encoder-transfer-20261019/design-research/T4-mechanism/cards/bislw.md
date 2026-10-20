# T4-05: BiSLW: Bi-Spectral Latent Watermarking for Generative Diffusion Models

- **Primary source:** [2607.02643v1](https://arxiv.org/html/2607.02643v1); authors: Aryan Pandit.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. Prior T4 source explicitly rechecked for this mechanism topic; the body records the new assumption/endpoint checks.
- **Method locators:** cached `bislw.txt` lines 100-202. **Evaluation locators:** 203-241; 595-611. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/bislw.html`. **HTML SHA-256:** `23980345f87dc46515dd8408eefd7a8e4837209c342775d8dc6fbdaa2069b5ab`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

BiSLW embeds complementary learned residuals into low- and high-frequency VAE latents using channel-wise DCT, reconstructs an image and re-encodes the suspect. Two learned band decoders estimate the watermark; their outputs are averaged before sign recovery. Training combines image-quality, watermark and robustness objectives. Latent DCT watermarking and multi-band robustness are therefore prior mechanisms.

F5 differs narrowly: it optimizes an image-domain perturbation through a fixed SD1.5 encoder to satisfy signed DCT chip targets, with a fixed reader and content binding. It is not the first watermark exploiting latent frequency structure. Calling its carrier semantic because it is in a VAE would skip the question: does preserved scene information carry the message, or does the writer exploit encoder-specific sensitive directions?

## Evaluation actually inspected

The method/setup uses a learned framework with MIRFLICKR training and 256-pixel crops. The regeneration appendix reports bit accuracy across noise levels t=50 to 500, above 0.96 through t=250 and around 0.92 at t=500 for its configuration. Those are bit-accuracy results, not native detection counts at the study's common presence threshold. The source does not establish F5 C, F5's quality budget, SDXL/DDIM20 behavior or a cross-encoder attribution guarantee.

## Limits and topic-specific use

The low-band/semantics and high-band/texture interpretation is a design argument, not a theorem that a random payload becomes semantic or survives independent regeneration. Recent preprint status and unresolved release/venue details constrain use as an executable baseline. T4 uses the inspected paper as a mechanism source only. Conditional P3 PhaseMark is not silently replaced by BiSLW.

If F5 retains C after R1 while v5 loses presence, that supports a channel distinction but does not establish novelty over all learned latent spectral watermarking. If D1 destroys F5 while X1 survives, it challenges a universal claim that latent frequency evidence survives arbitrary autoencoder reconstruction. This experiment cannot validate BiSLW's performance or train its decoders.

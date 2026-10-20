# TrustMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **TrustMark: Universal Watermarking for Arbitrary Resolution Images**. Version/date: arXiv:2311.18297v1 [cs.CV] 30 Nov 2023. Venue: Final ICCV 2025 paper, pp. 18629–18639, also inspected. Its exact title is TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images. The final version takes precedence where stated.

Authors: Tu Bui; Shruti Agarwal; John Collomosse. Year: 2023. DOI: not established for this inspected version.

Stable ID: `arxiv:2311.18297v1`. Citekey: `T3TrustMark2311`. Canonical URL: https://arxiv.org/abs/2311.18297v1

Primary full text: https://arxiv.org/html/2311.18297v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/trustmark-reused.txt`
SHA-256: `7610cc8f76c61f1314ff8b481a4ab79a29089af718419708cad3113cec8eed9a`

Actually inspected: arXiv v1 §§3.1–3.3,4.1–4.4; final ICCV PDF pp. 3–7 (method, Algorithm 1, experimental setup, Table 3); Table 3 visually verified from rendered page 7; pinned official Q loader/config/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

The image encoder uses MUNIT components, additional 1×1 layers and spectral/quality losses; a ResNet50 sigmoid decoder recovers the message. ReMark is a separate learned removal and re-watermarking module. A recovered public identifier is a provenance pointer, not owner authentication.

## Native operating point and detector side information

The paper network resolution is 256. The pinned Python Q release resizes the encoder input to 256×256 and the decoder input to 245×245 using PIL bilinear (trustmark.py:119–122,451–458). It normalizes to [-1,1], interpolates the encoder residual onto the original image, uses lambda=1 by default, and clamps. Native Q with use_ECC=True and BCH_5 carries 61 payload bits, 35 BCH parity bits and 4 header bits. With use_ECC=False, the release sets detected=True unconditionally; this is not a presence detector. P1 must preserve the native BCH configuration and report native detected/schema, recovery of the expected 61-bit payload, and raw 100-bit agreement descriptively. A further common-query cutoff needs a null model for structured codewords and headers; Binomial(100,.5) cannot simply be assumed. Neither BCH success nor an analytic payload rule establishes empirical image FPR. The final paper's alpha_max=27.5 quality setting and alpha_max=20 removal setting differ.

## Code, weights, pinned release and licenses

adobe/trustmark@6df5a0a29b51cbec832695fdf02051a1937e37bd. Final paper footnote and official LICENSE explicitly release code/models under MIT. Q encoder/decoder at https://cai-watermark.adobe.net/watermarking/trustmark-models/encoder_Q.ckpt and decoder_Q.ckpt; official loader MD5 values 700328b8754db934b2f6cb5e5185d81f and 4ced90e9cfe13e3295ad082887fe9187. These are integrity metadata, not a new SHA256 or immutable release revision; weight SHA256 remains unresolved without downloading.

## Published evaluation and regeneration conditions

Final ICCV Table 3 uses alpha_max=20 and lambda=1: no removal gives PSNR 40.20 and bit accuracy .970; Zhao et al. denoising with sigma=.3 gives PSNR 9.23 and bit accuracy .660. Table 3 was visually checked on rendered page 7. Section 4.1's default evaluation has 900 DIV2K images; a distinct table-specific count is not stated. Exact denoiser revision, sampler, steps and prompt are unspecified. VINE Table 1's third-party raw-100-bit variant instead gives stochastic/deterministic TPR 9.22/34.20% at .1% FPR and quality 41.27/.9910/.0026, under the VINE card's attack conditions and count conflict. WAM Appendix G.3 uses a different 40-bit configuration: DiffPure bit accuracy 100/98.3/74.9/54.3% and VAE 100/100/99.9/98.1%. These are different attacks and operating points, not necessarily contradictory results.

## Cost and uncertainty

Final ICCV Section 4.1 reports encoding 125 ms and decoding 25 ms on RTX3090; the stated 48-hour training time is not inference. VINE Table 7 reports .0705 seconds and 648 MB on Quadro RTX6000, averaged over 1,000 images. Hardware and timing scopes differ; neither is a measurement on the future rented server.

## Limitation and design implication

P1 remains the first additional baseline proposal because the official Q release is practical and independently published. Its native ECC payload, 245-pixel decoder resize and quality must stay visible. Final ICCV paper access is now closed through PDF rendering/OCR and visual checking of Table 3.

Disposition: **P1 TrustMark Q retained; proposed, excluded from core.**

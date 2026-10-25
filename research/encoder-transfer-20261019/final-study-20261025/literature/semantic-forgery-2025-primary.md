# Semantic-watermark forgery: inspected primary evidence

Accessed 2026-10-25 by Codex. **V2:** methods §§3.1–3.3, experiments §§4.1–4.6, Appendix F inspected in [arXiv:2412.03283v3](https://arxiv.org/html/2412.03283v3). Title: *Black-Box Forgery Attacks on Semantic Watermarks for Diffusion Models*. Authors: Andreas Müller, Denis Lukovnikov, Jonas Thietke, Asja Fischer, Erwin Quiring. [Metadata](https://arxiv.org/abs/2412.03283) identifies CVPR 2025, 20937–20946; v3 is 7 June 2025. Publisher full text was inaccessible; publisher-version equivalence is not asserted.

## Bounded source extraction

Imprinting minimizes proxy-inverted latent distance to one watermarked reference; reprompting regenerates its inverted latent with another prompt. Removal targets the negated proxy latent (§3). The SD2.1 proxy attacks Tree-Ring and Gaussian Shading. Table 1's 150-step SDXL forgery gives Gaussian-Shading detection/attribution 1.00, PSNR 19.77, LPIPS .253; Tree-Ring detection .99. Their declared FPRs differ: 10^-6 versus .01 (§4.1). Table 3's single-candidate SDXL reprompt detection is .995/.968. Imprinting is evaluated every tenth step; §3.1 mentions stopping at desired detection accuracy, so this text does not establish an operational query-free stopping rule. Appendix F finds Common Canvas and SD2.1 VAE weights matching to 10^-3, despite independently trained generator descriptions; Mitsua's encoder behaves differently. Encoder similarity correlates with transfer but does not fully explain it. V3 corrects earlier PSNR processing (§4.2).

## Consequence for this study — author interpretation

This is relevant prior art for the distinction between carrier detection and content/provenance binding. It neither measures F5 nor establishes a failure of its content-compatible C endpoint. In particular, a watermark transplanted onto another image can satisfy a presence test while failing a content-binding test; zero unmarked/wrong-owner calls are not an adaptive-forgery certificate. The closed T3 protocol is unchanged and no forgery experiment is added.

The Appendix F qualification is a concrete reason to audit autoencoder lineage separately from generator architecture or training labels. It also argues against a universal claim that independently trained models necessarily erase all watermark signals. Our retained codec/full-regeneration contrast stays a bounded empirical case. The paper's quality, payloads, thresholds and attack endpoints preclude a numerical ranking against our four arms.

## Access and search log

- Exact query: `"Black-Box Forgery Attacks on Semantic Watermarks" arxiv`, domain `arxiv.org`.
- Both `https://www.openaccess.thecvf.com/content/CVPR2025/html/Muller_Black-Box_Forgery_Attacks_on_Semantic_Watermarks_for_Diffusion_Models_CVPR_2025_paper.html` and its non-www equivalent returned 403. No bypass attempted.
- Directly opened arXiv v2 HTML initially, then abstract metadata and v3 HTML. All numerical extraction above uses v3 only. In-page `query`, `without` and section/line searches were used. No local download, experiment or execution occurred.
- Search also exposed arXiv:2606.29807, a separate 2026 theory/anti-forgery preprint; it is not evidence for the 2025 paper and requires its own assumption check.

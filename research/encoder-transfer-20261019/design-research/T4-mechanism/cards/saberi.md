# T4-07: Robustness of AI-Image Detectors: Fundamental Limits and Practical Attacks

- **Primary source:** [2310.00076v2](https://arxiv.org/html/2310.00076v2); authors: Mehrdad Saberi; Vinu Sankar Sadasivan; Keivan Rezaei; Aounon Kumar; Atoosa Chegini; Wenxiao Wang; Soheil Feizi.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `saberi.txt` lines 100-125. **Evaluation locators:** 126-140. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** CC BY 4.0, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/saberi.html`. **HTML SHA-256:** `62263e94c500f1efeb29d9c9a63bf5b6508a52bb923b082ca270892faf18ed83`. Text hash and byte counts are in `source-manifest.json`.

## Claim and theorem

Theorem 1 considers clean and marked distributions passed through pixel Gaussian noising and a common diffusion purifier. It bounds FNR+FPR below by 1-erf(sqrt(alpha_bar) W/(2 sqrt(2(1-alpha_bar)))), where W is Wasserstein distance based on expected L2 distance. It is not W squared. Coupling each image with its marked counterpart upper-bounds W by expected pixel perturbation norm; after a learned encoder the coupling instead involves encoded displacement.

As noise increases, the noised distributions become harder to distinguish under these assumptions. The theorem does not promise every purifier preserves useful content or that an actual detector's TPR is monotone in a strength label. The paper's purifier and larger-perturbation spoofing attack are distinct mechanisms.

## Evaluation actually inspected

Section 3 evaluates removal on 100 ImageNet images with 64-bit payloads, using an unconditional ImageNet256 guided-diffusion model and purification time 0.2, reporting watermark-detector AUROC. Its domain, resolution and endpoint differ from the development pool, SDXL512-to-1024 channel and source-majority C. It establishes a pixel-purification precedent, not a ready native 1024 image-to-image API.

## T4 use and disconfirmation

Alongside Zhao, the source explains why pixel diffusion can attack the pixel perturbation directly, without the VAE amplification step. P7 still needs legitimate image conditioning/noise semantics and useful output quality. HiDream-O1's pixel representation does not make its editing API equivalent to noising at SDXL strength 0.2; PRX also lacks a qualified drop-in protocol. Losing scene content cannot support useful removal just because detection is negative.

P7's conditional hypothesis is lower F5 readable-carrier retention at comparable utility than R1, consistent with removal of the amplification route. Equal/higher retention with usable output weakens that explanation; unacceptable utility is inconclusive about a practical attack. No pixel-regenerator run or held-out inspection occurred here.

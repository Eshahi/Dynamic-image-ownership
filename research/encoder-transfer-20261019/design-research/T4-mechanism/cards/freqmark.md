# T4-06: FreqMark: Invisible Image Watermarking via Frequency Based Optimization in Latent Space

- **Primary source:** [2410.20824v1](https://arxiv.org/html/2410.20824v1); authors: Yiyang Guo; Ruizhe Li; Mude Hui; Hanzhong Guo; Chen Zhang; Chuangjian Cai; Le Wan; Shangfei Wang.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `freqmark.txt` lines 123-170; 862-868. **Evaluation locators:** 172-195; 407-432; 508-530; 869-875. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/freqmark.html`. **HTML SHA-256:** `856524b2eef7dc07efb9f1be26d7e24df834f81bdeca880369a1966f01e1d70e`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

FreqMark encodes an image with a frozen VAE, optimizes an additive perturbation in latent FFT space and decodes it. A frozen DINOv2-small image encoder reads bits as signs along predefined feature directions. Its objective mixes hinge-message, PSNR and LPIPS losses plus latent/pixel Gaussian noise augmentation. Only the perturbation is optimized. It differs from F5's pixel optimization and SD1.5 latent-DCT reader, while establishing prior art for fixed-network latent frequency optimization.

## Evaluation actually inspected

The setup evaluates 500 ImageNet images plus 500 Stable-Diffusion images using DiffusionDB prompts. Appendix A.1 specifies an SD2.1 KL autoencoder, 512-pixel processing, 400 Adam steps and 48 coordinate directions of DINOv2-small features. Table 3 reports bit accuracy falling from 0.945 at 60 diffusion steps to 0.637 at 200. Image quality and TPR/FPR are also examined; bit accuracy is not a method-independent presence probability. Roughly 31 dB reconstruction/marking figures do not equal F5's strict quality constraints.

Section 5.2 checks pairwise bit correlations on 2000 clean images. Near-zero pairwise correlations do not prove joint independence, equiprobability conditional on a public key, or security against adaptive image selection. Binomial-tail calculations require their assumptions and cannot be copied into F5's claims.

## T4 implications and falsification

Frequency optimization alone is not a novel mechanism. Successful R1 transfer would support this particular post-hoc construction under the named channel, not all frequency marks. Failure after X1 reveals resampling weakness before an encoder interpretation. Failure after D1 but not X1 points at combined autoencoder/reconstruction effects, not exclusively the encoder.

Native message lengths, thresholds and side information remain visible. Neither this paper's bit accuracy nor PRC's security theorem substitutes for C or common external presence. FreqMark is a closed execution line: this recheck authorizes no retry, installation or new baseline arm.

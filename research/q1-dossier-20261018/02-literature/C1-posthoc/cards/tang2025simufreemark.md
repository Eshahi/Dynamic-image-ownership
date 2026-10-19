# tang2025simufreemark — V2

Yichao Tang, Mingyang Li, Di Miao, Sheng Li, Zhenxing Qian and Xinpeng Zhang. *SimuFreeMark: A Noise-Simulation-Free Robust Watermarking Against Image Editing*. arXiv2511.11295v1, 14 November 2025; venue unverified. Accessed 18 October 2026. [Primary text](https://arxiv.org/html/2511.11295v1). Inspected §§3–4, Tables 1–5.

Existing photos: split low/high frequencies; encode the low-frequency image with frozen SD-VAE; learn a residual payload in latent space; decode and restore original high frequencies. A learned image decoder extracts 64 bits without diffusion inversion. No per-image registry; trained model is side information.

Training: 20,000 COCO images at512². Evaluation:1,000 UltraEdit images with supplied instructions/masks. Table2 reports PSNR39.19/SSIM.990 and mean bit accuracy97.64/94.05/92.25% for SDIP+ strengths.1/.3/.5; P2P90.42%. These are bit averages, not fixed-FPR attribution. Exact regenerator revision and independent-encoder transfer are not established by the inspected protocol.

This directly pre-empts broad claims that VAE latent insertion, frequency-aware reconstruction, or avoiding diffusion inversion are new for existing images. Its latent-residual writer differs from F5's pixel optimization through a frozen encoder. No measured same-shot specificity or competing-enrollment result supports a claim that it resolves E2/E3.

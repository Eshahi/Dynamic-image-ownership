# Li2026RAIN

Zilai Li. *RAIN: Region-Aware Inversion Network for Semantic Watermark Extraction*. arXiv:2609.14856v2, 22 September 2026, preprint. [Primary text](https://arxiv.org/html/2609.14856v2). V2; accessed 2026-10-18, §§3–4, Tables 1–2; submission history checked. Supersedes the project's v1 inspection.

Generation-time Gaussian Shading uses a learned prompt-free anchor/residual estimator to recover the watermark's noise decision region from a VAE-encoded image. Side information includes the trained NAFNet components, VAE and GS key/decoding convention; no diffusion U-Net is used in extraction. Capacity follows the GS repetition configuration rather than a new message code.

Training uses 89,600 image/noise pairs and 15,000 iterations. The SD1.5 ablation evaluates 1,000 COCO-caption samples under ten ordinary image-distortion conditions. Table 1 reports 100% clean detection with a nominal GS false-positive target of 10⁻⁶, not empirical million-negative calibration. Table 2's 2.993–3.085 ms/image uses two RTX Pro 6000 GPUs and batch ten, excluding VAE encoding, input transfer and GS decoding.

Relevance: inexpensive learned extraction already has recent prior art. This is not an image-DCT detector, an existing-photo carrier, or evidence for T3 regeneration, T4 transfer and T5 instance discrimination together.

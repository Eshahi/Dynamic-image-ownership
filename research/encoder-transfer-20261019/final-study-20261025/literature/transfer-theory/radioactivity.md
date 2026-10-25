# Are Watermarks for Diffusion Models Radioactive?

**V2.** Jan Dubinski, Michel Meintz, Franziska Boenisch and Adam Dziedzic; 2025 Workshop on GenAI Watermarking, collocated with ICLR. Author-hosted manuscript inspected 2026-10-25: [primary PDF](https://adam-dziedzic.com/static/assets/papers/RadioactiveDiffusion.pdf). DOI not verified. Read §3, §4 experimental setup, §§4.1.1–4.1.2, Tables 1–2 and Figures 2–3.

The attack trains another generator on marked outputs. It is **not** img2img regeneration. The LDM experiments use SD2.1 and COCO2014; EDM experiments use CIFAR10, with 50,000 generated training images. Table 1 reports LDM-to-LDM Stable Signature bit accuracy changing from 100% to 49.9%, PRC from 100% to 50%, and Tree-Ring TPR at 1% FPR from 100% to 1%. Autoencoder filtering explains the decoder-trained signature result, but not every other scheme's loss during subsequent training.

Relevance: a signal surviving an autoencoder need not survive a later generative operation. This is an analogy supporting decomposition, not evidence about F5, SDXL img2img or repeated rinsing. These results do not estimate the proposed study's effect sizes.

Cache: MAIN `.thesis-build/cache-et-final/papers/root/dubinski2025-radioactive.pdf`; SHA-256 `2fbca083864bfbb1c4339abf4a3ea59bea70fee801b43cbc792c71a2c3f5c325`.

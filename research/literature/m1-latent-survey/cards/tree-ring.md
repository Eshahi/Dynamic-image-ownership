# Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust

Primary source: https://arxiv.org/html/2305.20030v3

Inspected: Sec.3.2-3.4; Sec.4.1-4.2/Table1. Full-text artifact/checksum in paper JSON and inventory.

Overwrites circular low-frequency Fourier coefficients of initial noise with zero, random, or constant-per-ring keys. DDIM inversion with empty prompt recovers approximate noise; masked L1 matching or noncentral chi-square test detects it. Main SD2 experiments use radius10, CFG7.5, generation/detection50 steps. Detector needs model, watermark key/mask and inversion; original prompt unnecessary. Table1 Tree-RingZeros clean AUC/TPR@1%FPR .999/.999, averaged manipulation .963/.715; FID26.56 versus unmarked25.29. Main benchmark covers ordinary transformations, not a general img2img regeneration guarantee.

Limitations: Fourier invariance is heuristic through nonlinear model. Distribution changes and multi-key limitations. No lightweight DCT detector demonstrated.

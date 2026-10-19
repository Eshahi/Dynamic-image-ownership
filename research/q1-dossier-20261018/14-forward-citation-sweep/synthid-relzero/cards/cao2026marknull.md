# cao2026marknull — V2

Jie Cao et al. MarkNull: Model-Agnostic Watermark Removal in AI-Generated Images via On-Manifold Latent Manipulation. arXiv:2608.10166v1 (2026-08-10), inspected 2026-10-19. [Primary text](https://arxiv.org/html/2608.10166v1); cache/hash in `../source-artifacts.json`. ArXiv metadata reports USENIX Security 2026 acceptance; proceedings version not inspected.

**Citation edge:** Reference 7 identifies SynthID-Image, arXiv:2510.09263.

**Direct evidence:** Section 5 optimizes latent noise-alignment and quality objectives using a proxy diffusion model; an amortized restoration network supplies MarkNull-A. Section 7.1 evaluates 100 images per scheme across nine schemes. Section 7.3/Table 4 uses 20 Imagen 3 images and Gemini fast-mode verification because official detector code is unavailable; both variants report 100% attack success in this setting. Table 2's overall bit accuracy 53.14% is a different metric; Tree-Ring retains TPR 43% for MarkNull and 63% for MarkNull-A at 1% FPR.

**Author interpretation:** Broad model-agnostic watermark removal.

**Our inference/limits:** The small service-specific SynthID test is not a universal removal guarantee or direct audit of Google's internal detector. No trusted-registry attribution experiment appears in these inspected evaluations. This supports carefully scoped future active-removal questions, not claims about failure of the thesis cascade.

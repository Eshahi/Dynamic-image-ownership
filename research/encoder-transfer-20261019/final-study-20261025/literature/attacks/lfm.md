# V2 card: Aistov et al. (2026)

- **ID / key:** `aistov2026lfm`; **title:** *Exploring Weaknesses of Generative Image Watermarks against Latent Frequency Masking*.
- **Authors:** Kirill Aistov, Khaled Abud, Irina Serzhenko, Egor Kovalev, Aleksey Yakushev, Aleksandr Akimenkov, Dmitry Obydenkov, Yury Markin, Sergey Lavrushkin, Dmitriy Vatolin, Anastasia Antsiferova. **Year / venue / version:** 2026, arXiv:2610.02010v1 (1 October 2026); IEEE notice on HTML, final venue unverified. **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2610.02010v1. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `lfm`.
- **Inspected:** §§III-A–III-C, IV, V-A/Table I, V-D. **Verification:** V2.

**Threat and method — direct evidence (§III):** The attack encodes an image in a VAE, Fourier transforms the latent and replaces selected frequency coefficients with Gaussian or diffusion-generated values before decoding. It targets zero- and multi-bit diffusion watermarks with a separate quality objective. It does not need target-key access; settings such as channel and mask radius are selected per watermark method in the reported benchmark.

**Checked experiment (§§IV–V/Table I):** 1,000 prompts each from DiffusionDB and MS-COCO; six watermark methods based on SD2.1, with FLUX used for regeneration/replacement attacks. On DiffusionDB, Table I averages TPR@1%FPR of 0.36, PSNR 21.6 dB, LPIPS 0.119 for LFM Gaussian; LFM Diffusion gives TPR 0.44, PSNR 28.4 dB, LPIPS 0.043. §V says Gaussian Shading resists partial masking because its signal is distributed; this is an explicit negative result.

**Limit / inference:** Method-specific mask selection and very different average quality make this unsuitable as a plug-in F5 comparator without development-only tuning and matched quality. These are latent-noise generation marks, not an image-domain SD1.5 encoder-directed writer. **Agent inference:** spatial concentration of F5 energy should be measured before deciding if frequency masking is an informed attack.

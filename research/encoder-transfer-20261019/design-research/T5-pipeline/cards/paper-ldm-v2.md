# High-Resolution Image Synthesis with Latent Diffusion Models

[Primary source](https://arxiv.org/html/2112.10752v2). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** methods §3.1–3.3; evaluation §4.1–4.2 and Figure7. Cached full HTML and independently extracted text were read, not only the abstract.

**Mechanism:** perceptual and patch-adversarial autoencoding removes fine pixel detail before latent diffusion. The paper considers KL and VQ regularization and several spatial compression factors. This motivates separating AE-only reconstruction from AE-plus-diffusion; it does not establish survival of any particular watermark.

**Evaluation reread:** compression variants f=1,2,4,8,16,32 are compared under matched A100 training budgets; sampling-quality plots use5,000 samples and10/20/50/100/200 DDIM steps. Text-to-image evaluation includes COCO256 and250 DDIM steps. These are generation/compression experiments, not the frozen SD1.5 img2img strength grid.

**Audit use / limits:** source for representation/compression mechanism only. Actual SD1.5 release tensor/config/scheduler behavior is established by pinned official code/configs. No claim that the paper itself pins SD1.5 weights, proves independent encoders or reports our regeneration false-positive rates.

**Read locations:** `ldm-paper.read.txt:758–928,1552–1720,2155–2247`.

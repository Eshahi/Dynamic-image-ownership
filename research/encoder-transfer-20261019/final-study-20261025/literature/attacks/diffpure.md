# V2 card: Nie et al. (2022)

- **ID / key:** `nie2022diffpure`; **title:** *Diffusion Models for Adversarial Purification*.
- **Authors:** Weili Nie, Brandon Guo, Yujia Huang, Chaowei Xiao, Arash Vahdat, Anima Anandkumar. **Year / venue / version:** 2022, ICML; arXiv:2205.07460v1 (16 May 2022). **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2205.07460v1. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `diffpure`.
- **Inspected:** §§3.1–3.2/Theorems 3.1–3.2, 5.1–5.5/Tables 5–6 and timestep ablation. **Verification:** V2.

**Threat and method — direct evidence (§3):** This is a *defense* against classifier adversarial examples, not a watermark attack. DiffPure adds forward SDE noise to an input and reverses with a diffusion model before classification. It evaluates adaptive attackers via adjoint gradients and EOT. Theorem 3.1 says KL divergence of clean and adversarially perturbed distributions decreases during forward diffusion; Theorem 3.2 bounds reconstruction error, which grows with diffusion time.

**Checked experiment (§5):** CIFAR-10, ImageNet and CelebA-HQ; EOT=20 and usually 512 sampled test images for expensive adaptive evaluations. Table 5(b) reports CIFAR-10 BPDA+EOT robust accuracy 81.40% at `t*=0.1` versus 70.01% for the DSM+LD comparator. Table 6 reports 70.64% VP-SDE versus 39.86% VP-ODE robust accuracy under its specified AutoAttack setup. §5.5 says larger `t*` initially helps robust accuracy, then damages semantics.

**Limit / inference:** Classifier robustness is not watermark removal. Dataset, pixel-space SDE and adaptive-attacker objective differ from F5's latent img2img setting. **Agent inference:** noising and denoising should be separated experimentally because both the noise level and reverse sampler can change retention; these results cannot predict F5 counts.

# liu2025ctrlregen — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Yepeng Liu, Yiren Song, Hai Ci, Yu Zhang, Haofan Wang, Mike Zheng Shou and Yuheng Bu. *Image Watermarks are Removable Using Controllable Regeneration from Clean Noise*. ICLR 2025; arXiv 2410.05470v2, 2025-03-02. [Full text](https://arxiv.org/html/2410.05470v2); [official repository](https://github.com/yepengliu/CtrlRegen). Inspection: §3, §4 Table 1 and Appendix A. Conference final PDF not independently version-compared.

**Mechanism and access.** CtrlRegen regenerates from fresh noise, conditioned on DINOv2 semantic features and Canny edges through trained conditioning networks; CtrlRegen+ also uses a noised image latent. Removal does not require detector queries at attack time. This is a trained attack, not a cost-free generic diffusion call.

**Evaluation.** 1,000 MIRFLICKR images for post-hoc marks and 1,000 DiffusionDB prompts for generated-image methods. Training uses large LAION/COYO samples and COCO edge pairs. Table 1 reports StegaStamp TPR .01 at 1% FPR with PSNR 19.10 dB, and Tree-Ring .12 with 19.32 dB.

**Limits.** Comparators in the same table have different quality; those rates do not establish dominance at matched distortion. Semantic similarity and instance identity can disagree.

**Thesis implication.** A serious future T3 assessment needs a controllable fresh-noise attacker. It must predefine whether its output remains the same instance under the thesis relation. Its output cannot be relabeled after seeing the detector result.


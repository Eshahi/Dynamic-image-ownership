# Sadasivan2025IConMark

**Source:** Vinu Sankar Sadasivan, Mehrdad Saberi, Soheil Feizi. *IConMark: Robust Interpretable Concept-Based Watermark For AI Images*. [arXiv:2507.13407v1](https://arxiv.org/html/2507.13407v1), 17 July 2025. Metadata states ICLR 2025 WMARK workshop acceptance; inspected version is the arXiv v1. Accessed 2026-10-19. **V2:** methods §§3–4, evaluation §5, limitations §6, references inspected.

**Verified edges:** reference [19] cites DREW, arXiv:2406.02836; reference [4] cites TrustMark's 2023 preprint, not its final ICCV2025 publication. The DREW reference does not specify v2.

**Direct evidence:** §§3.1–3.3 select nine prompt-related objects from a private 100-concept collection, modify the generation prompt, and detect concepts with IDEFICS3. §4 combines concept and conventional watermark detections. §5.1 uses COCO/OIP captions and FLUX.1-dev; hybrid ROC curves select Pareto-optimal threshold pairs. Table 3 regeneration TPR at 1% FPR is 59.26%/13.64% for IConMark on COCO/OIP. §6 acknowledges prompt specificity.

**Interpretation:** authors argue complementary signals improve detection. My inference: concept insertion changes image semantics and targets generated-image detection, so these results neither establish strict-fidelity instance attribution nor identify the thesis's owner/q/content contributions. No lawful-ownership or cryptographic-binding result follows.

**Artifact:** MAIN `.thesis-build/q1-research-20261018/cache/iconmark-2507.13407v1.html`; SHA256 `6D672B3E553CF6A18540D71BDD05A05FBFE0C474C7335EE01A26A810C5DF4760`.

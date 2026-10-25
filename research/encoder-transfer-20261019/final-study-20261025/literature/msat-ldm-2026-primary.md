# MSAT-LDM: adaptation is a different transfer task

Late author source note, outside WP6/E3 review. Inspected 2026-10-25: official nine-page paper, methods §4 and experiments §5, pp. 36050–36054. The separately mentioned appendix was not available in that PDF.

Zhang and Zeng, AAAI 40(42), 36048–36056, published 2026-03-14. [Official record](https://ojs.aaai.org/index.php/AAAI/article/view/40921), [paper](https://ojs.aaai.org/index.php/AAAI/article/download/40921/44882), DOI `10.1609/aaai.v40i42.40921`.

The method trains a modular message injector using empty-prompt generated latents while preserving original decoder parameters; extraction adds a spatial transformer. SD1.5 uses 100-bit messages, 1,000 evaluation images and three runs. Table 1 reports PSNR 40.6, SSIM .98, FID 2.35 and .99 aggregate attacked bit accuracy. These are bit-recovery results, not compound owner/content verification.

Table 2 transfers the module to SD1.5 derivatives and LoRA variants **after adaptation on 400 internally generated images**. It does not demonstrate unchanged-watermark survival through an independently trained regenerator. The listed attacks are conventional distortions; regeneration lineage and operational FPR are not established by the inspected main experiments. Empty-prompt/mixed-prompt distribution equality is acknowledged as approximate. Theorem 1's simultaneous generalization wording needs a separate [scope qualification](../analysis/uniform-bound-scope.md).

Decision: useful adaptation prior art, no new baseline or protocol change. No code downloaded or executed.

Version receipt: the [author repository](https://github.com/LukeZane118/MSAT-LDM) links to [SAT-LDM v2](https://arxiv.org/abs/2501.00463v2), dated 2025-02-17, with a different title. Its Appendix A.2 was separately inspected for the scope note; it is not the final MSAT supplement. The repository showed a README and a forthcoming-code notice at access time.

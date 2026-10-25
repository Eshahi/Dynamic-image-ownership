# AR regeneration and mimicry: bounded primary-source closure

Inspected 2026-10-25 by Codex agent. Late author addition, outside the WP6/E3 review scope. No experiment, download, code execution or new baseline. Authoritative MAIN STATE read once before work.

## Source and reading record

Andreas Müller, Denis Lukovnikov, Shingo Kodama, Minh Pham, Anubhav Jain, Jonathan Petit, Niv Cohen and Asja Fischer, *On the Robustness of Watermarking for Autoregressive Image Generation*, arXiv:2604.11720v1, submitted 13 April 2026, 16:56:48 UTC. The abstract page lists only v1. Primary records: [version metadata](https://arxiv.org/abs/2604.11720v1), [full primary HTML](https://arxiv.org/html/2604.11720v1), [PDF](https://arxiv.org/pdf/2604.11720v1). Read the actual methods (§§2.2–3.3), evaluation (§§4.1–4.3, Tables 1–2), Appendix A.1–A.2, Algorithms 1–3, and the relevant Appendix B breakdowns including Table 13. This is not an abstract-only classification; no PDF was saved.

## Compact evidence record

VQ-Regen substitutes second-nearest codebook entries. LatentOpt shifts proxy-encoder latents; forgery uses one marked reference. BitOpt additionally knows green lists/scales. Frequency injection needs no model/reference. Attack sets contain 100 targets/covers per setup; metrics are TPR@1% FPR, median p, PSNR/LPIPS. SD2.1 Regen uses 60 steps; Rinse uses three rounds; CtrlRegen+ uses guidance 2, strength .3. Black-box VQ-Regen TPR: IndexMark/WMAR/ClusterMark .03/.12/.39; PSNR 20.32/21.59/20.49, LPIPS .15/.12/.15. BitMark retains 1.00 under Regen/Rinse/VQ-Regen. BitOpt: TPR .00, PSNR 46.17, LPIPS .01. BitMark black-box LatentOpt forgery: .59 aggregate, .88 LlamaGen; frequency setting A: .73, 37.53 dB, .06 LPIPS. LatentOpt checks target verification every ten steps and selects per-image best within 300 steps, budget 8/255. [Methods, tables and appendix](https://arxiv.org/html/2604.11720v1).

## Interpretation for this dossier

The access axis must distinguish generator secrets, encoder parameters, and detector feedback. Calling an attack black-box because its proxy encoder differs from the verifier does not make the complete reported procedure detector-free. Per-image selection against verification can favor successful checkpoints. For our proposed detector-free attacks, an endpoint fixed independently of target scores is therefore an essential design distinction. This is a critique of comparability, not an allegation that the paper concealed its procedure: Appendix A states it explicitly.

Likewise, model names do not establish independent training histories. The named diffusion checkpoint family is SD2.1; the inspected passages do not supply an exact model revision, VAE hash, or an independence audit against every targeted tokenizer. Their black-box category means an entirely different encoder. It supports a proxy/verifier mismatch interpretation; it should not be promoted to a controlled causal estimate of encoder-training independence. Grey-box token experiments use the corresponding unfine-tuned tokenizer, so architectural similarity and weight ancestry remain entangled. Bitwise grey-box comparisons change vocabulary/channel configurations within Infinity. Those are useful access categories, but they answer a different question from a documented independent-AE transfer test.

The VQ operation is a reconstruction with altered discrete quantization, rather than diffusion denoising of a noisy latent trajectory. Its relevance is that a detector can depend on precise assignments to token regions. Replacing tokens can disrupt that assignment while leaving a recognizable picture. This motivates separating reconstruction survival from downstream detection in our narrative. It does not identify which stage causes F5's SDXL failure, and it does not measure the proposed signed-transport predictor. The frozen future stage contrasts also do not guarantee unique component attribution; the [stage-attribution note](../analysis/stage-attribution-boundary.md) states that boundary.

Three meanings of transfer must remain separate: perturbations computed through one encoder affecting another verifier; a marked reference inducing acceptance of a different cover; and signal inheritance by a newly trained generator. None is automatically watermark survival through an unrelated image-to-image regeneration pipeline. In particular, reference-based acceptance on an unrelated image is evidence about detector specificity under attack, not evidence that a valid owner/content binding survived.

The numerical contrast also prevents a blanket claim that AR watermarks are removed by regeneration. A family can resist the tested reconstruction attacks yet admit forgery or a stronger privileged attack. Conversely, low aggregate TPR must be read alongside substantial pixel distortion and the weaker perceptual metric. Our strict clean-image quality gate cannot be substituted for attack-output quality, and averages cannot certify per-source admissibility. The nominal 1% FPR operating point is not an independent empirical certificate at our intended rare-event scale; no such certificate should be imported from this paper.

F5 r2 is an image-domain encoder-directed comparator with compound outcome C. The paper's token/bit green-count detection statistic is not C, owner attribution, cryptographic authenticity, registry matching or lawful ownership. Consequently no cross-paper ranking, numerical F5 prediction, new baseline or protocol change follows. The defensible contribution to the final report is narrower: encoder access, reconstruction geometry, checkpoint selection and forgery must be reported separately, and robustness claims should identify the exact endpoint tested. Keep this source as contextual counterevidence to universal survival/removal language, with no expansion of the frozen study.

## BibTeX for root integration

```bibtex
@misc{muller2026robustnessarwatermarking,
  title = {On the Robustness of Watermarking for Autoregressive Image Generation},
  author = {M{\"u}ller, Andreas and Lukovnikov, Denis and Kodama, Shingo and Pham, Minh and Jain, Anubhav and Petit, Jonathan and Cohen, Niv and Fischer, Asja},
  year = {2026},
  eprint = {2604.11720},
  archivePrefix = {arXiv},
  primaryClass = {cs.CV},
  doi = {10.48550/arXiv.2604.11720},
  url = {https://arxiv.org/abs/2604.11720v1},
  note = {Version 1, 13 April 2026; primary methods and experiments inspected 25 October 2026}
}
```

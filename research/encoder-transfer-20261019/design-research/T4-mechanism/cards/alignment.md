# T4-13: Improving Adversarial Transferability via Model Alignment

- **Primary source:** [Ma et al., arXiv 2311.18495v2](https://arxiv.org/html/2311.18495v2), 2024. Authors: Avery Ma; Amir-massoud Farahmand; Yangchen Pan; Philip Torr; Jindong Gu.
- **Inspected:** 2026-10-20; V2 method and evaluation, no reproduction. Added after the floor to address cross-model alignment directly.
- **Method locators:** cached `alignment.txt` lines 108-161. **Evaluation:** 162-181, 575-595, 1119-1124. These are HTML-to-text line numbers.
- **License:** CC BY 4.0 as displayed in the inspected arXiv HTML. Code/model rights are separate.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/alignment.html`. **SHA-256:** `b3212ef7732a6b02ecb288fdaab49e5a8e8dcb681e9a67293feaef67475d3a6f`.

## Mechanism and evaluation inspected

The source classifier is fine-tuned toward an independently trained witness using prediction divergence. ImageNet evaluation uses 1000 selected examples, 20-step PGD at Linf 4/255 and results averaged over three runs. The examples must satisfy clean correctness and successful originating-model attack criteria. The study reports improved transfer across CNN/ViT architectures and lower input-loss gradient norms after alignment. It also observes changes in perturbation DCT energy and interprets them as greater use of shared features. That frequency-based interpretation is not a universal definition of semantics.

## T4 implication and limits

Independent training does not force adversarial directions to be orthogonal, and smoothing a writer's landscape can coexist with greater transfer. This directly cautions against treating SDXL independence as a predicted eraser or treating all smoothing as attenuation. The classifier study does not prove an alignment between SD1.5 and SDXL autoencoders, nor F5 survival. Its attacks and conditional evaluation population differ from a fixed 60-source watermark study.

Our cross-Jacobian derivation is a local mathematical approximation, not this paper's measured quantity. High R1 C would weaken a strict encoder-specific explanation but would remain compatible with shared nonsemantic features; low R1 C would not identify which Jacobian or decoder caused the loss. P5 operates on the attack encoder, while this paper aligns a source used to generate perturbations: their direction of intervention differs. No model alignment, retraining or F5 amendment is proposed for core.

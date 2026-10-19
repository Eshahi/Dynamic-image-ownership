# salamon2026beyondgeneration — V2, focused reading

Olivia Salamon, Virginia N. L. Franqueira, Shujun Li. Beyond Generation: Using Multimodal LLMs as Detectors of LLM-Generated Deepfake Facial Images. **arXiv:2610.21760v2 (2026-10-16)**, focused method/evaluation refresh on 2026-10-19. [Primary text](https://arxiv.org/html/2610.21760v2). The earlier v1 cache/hash in `../source-artifacts.json` remains a historical artifact; it does not authenticate v2, which was read through the web reader without a local copy. Count this work once.

**Citation edge:** References, Gowal entry, exact SynthID-Image title and arXiv:2510.09263.

**Direct evidence:** Sections 3.1–3.4 describe 400 portraits (50 real, 350 generated) and six MLLM detectors. Section 3.2.3 compares Imagen/API and Gemini-web images, logo cropping, and RealisticVision V5.1 reconstruction at strength .15. Section 4.4/Table 5 compares cropped D3 with cropped-and-reconstructed D5: accuracy 90% versus 100%, reported p=.002. Section 4.4.6 acknowledges possible reconstruction-induced artifacts; §5.4 limits the study to high-quality studio portraits and a small sample. These inspected values and the SynthID citation edge are unchanged from the earlier card; no whole-document equivalence is asserted.

**Author interpretation:** SynthID may mask cues used for self-detection.

**Our inference/limits:** Reconstruction changes more than the watermark. The inspected ablation does not independently verify watermark removal with a SynthID detector, so it does not isolate a causal SynthID effect. It studies synthetic-image classification, not payload decoding, lawful ownership, or registered-image matching. Its relevance is the need for compatible controls, not proof of a universal watermark penalty.

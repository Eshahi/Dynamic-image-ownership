# salamon2026beyondgeneration — V2, focused reading

Olivia Salamon, Virginia N. L. Franqueira, Shujun Li. Beyond Generation: Using Multimodal LLMs as Detectors of LLM-Generated Deepfake Facial Images. arXiv:2610.21760v1 (2026-10-15), inspected 2026-10-19. [Primary text](https://arxiv.org/html/2610.21760v1); cache/hash in `../source-artifacts.json`. Metadata reveals v2 dated October 16; its full text was not inspected.

**Citation edge:** References, Gowal entry, exact SynthID-Image title and arXiv:2510.09263.

**Direct evidence:** Section 3 describes 400 portraits, 50 real and 350 generated, and six MLLM detectors. Focused method Section 3.2.3 compares Imagen/API and Gemini-web images, logo cropping, and RealisticVision reconstruction at strength .15. Section 4.4/Table 5 compares cropped D3 with cropped-and-reconstructed D5: detection accuracy 90% versus 100%, reported p=.002.

**Author interpretation:** SynthID may mask cues used for self-detection.

**Our inference/limits:** Reconstruction changes more than the watermark. The inspected ablation does not independently verify watermark removal with a SynthID detector, so it does not isolate a causal SynthID effect. It studies synthetic-image classification, not payload decoding, lawful ownership, or registered-image matching. Its relevance is the need for compatible controls, not proof of a universal watermark penalty.

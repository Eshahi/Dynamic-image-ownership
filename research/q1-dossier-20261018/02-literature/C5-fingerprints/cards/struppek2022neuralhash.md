# struppek2022neuralhash — V2

Lukas Struppek, Dominik Hintersdorf, Daniel Neider, Kristian Kersting. *Learning to Break Deep Perceptual Hashing: The Use Case NeuralHash*. FAccT 2022. DOI: [10.1145/3531146.3533073](https://doi.org/10.1145/3531146.3533073). Inspected arXiv 2111.06628v5 (2024-07-16), a later revision than the venue year. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2111.06628v5).

**Mechanism / access.** White-box optimization attacks the differentiable pre-binarization output of public 96-bit NeuralHash using hash agreement and image-similarity losses. Target hashes/encoder are available; this is a targeted collision attack, with no watermark payload.

**Evidence.** Read §§2–5, especially §3/Table 1 and §4/Table 2. With a 20,580-image Stanford Dogs target registry, 10,000 ImageNet inputs and up to 10,000 optimization iterations, closest-target collision success is 90.81%, mean SSIM 0.9647. Changing one bit for evasion is a different, easier criterion than defeating a tolerant matcher.

**Boundary / relevance.** Public perceptual fingerprints do not inherit cryptographic collision resistance. This does not break a secret mark plus trusted-record verifier, nor establish natural same-shot false binding or diffusion robustness.

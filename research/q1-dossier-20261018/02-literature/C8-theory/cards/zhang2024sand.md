# zhang2024sand — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Hanlin Zhang, Benjamin L. Edelman, Danilo Francati, Daniele Venturi, Giuseppe Ateniese and Boaz Barak. *Watermarks in the Sand: Impossibility of Strong Watermarking for Generative Models*. ICML 2024; inspected expanded arXiv 2311.04378v5, 2025-05-27. [Metadata](https://arxiv.org/abs/2311.04378), [full text](https://arxiv.org/html/2311.04378). Locators: §4 Theorem 2, Appendix C Theorem 6, §§5.1–5.3 and Table 2. Conference-version equivalence is not asserted.

**Mechanism/assumptions.** A quality oracle and quality-preserving perturbation oracle generate a mixing random walk. Irreducibility, aperiodicity and mixing time are essential assumptions; detector-key access is unnecessary.

**Evaluation.** Three language watermark schemes and two image schemes. Image tests start with 200 selected prompts, filter weak initial marks, and use 100 accepted perturbation steps. Invisible Watermark has 141 retained examples; Stable Signature retains all. Mean p-values and quality judgments are not a calibrated population forgery rate.

**Limit/relevance.** The result concerns erasing a model-output signal under its oracle assumptions. It is not an unconditional theorem about preserved photographic instance identity or trusted-record authentication. It motivates adaptive T3 analysis without proving the present E2 failure unavoidable.


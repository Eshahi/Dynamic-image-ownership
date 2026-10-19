# an2024waves — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Bang An, Mucong Ding, Tahseen Rabbani, Aakriti Agrawal, Yuancheng Xu, Chenghao Deng, Sicheng Zhu, Abdirisak Mohamed, Yuxin Wen, Tom Goldstein and Furong Huang. *WAVES: Benchmarking the Robustness of Image Watermarks*. ICML 2024; arXiv 2401.08573v3, 2024-06-07. [Full text](https://arxiv.org/html/2401.08573); [project](https://wavesbench.github.io/). Inspection: §§3–4, Appendices D.1, E, F.2–F.3 and G.1. DOI not verified.

**Setting and mechanism.** A benchmark of 26 attacks in three categories, three watermark methods, and eight image-quality measures. Includes repeated diffusion regeneration and embedding-space attacks. Public matched encoder access is distinguished from a different encoder.

**Evaluation.** 5,000 images each from COCO, DiffusionDB and DALL-E 3, with filtering. Main detection metric is TPR at 0.1% FPR. User identification with a large candidate bank is a separate task. Two- and four-pass rinsing tests expose accumulated removal and accumulated quality loss.

**Limits.** Aggregated performance-quality summaries are not a single matched-quality operating point. Dataset filtering and method-specific setup prevent simple comparison to 300 DIV2K photographs. A nominal FPR threshold does not establish a bank-wide owner-attribution error rate.

**Thesis implication.** Future T3 work should include multi-pass regeneration, matched quality, access declarations and encoder lineage. Conventional transformations in WAVES do not enlarge this thesis's fixed T3/T4/T5 scope automatically.


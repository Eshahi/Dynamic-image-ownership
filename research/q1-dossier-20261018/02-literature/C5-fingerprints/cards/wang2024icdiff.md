# wang2024icdiff — V2

Wenhao Wang, Yifan Sun, Zhentao Tan, Yi Yang. *Image Copy Detection for Diffusion Models*. NeurIPS 2024, vol. 37. DOI: [10.52202/079017-0460](https://doi.org/10.52202/079017-0460). Inspected arXiv 2409.19952v2 (2024-10-02); [venue record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/1a000ee0f122d0bbd3edb9bf55170ea3-Abstract-Conference.html). Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2409.19952v2).

**Mechanism / access.** A ViT-B/16 PDF embedding learns graded replication levels with representative vectors and smoothed distribution targets. Query/reference images and trained weights are required; no embedded payload.

**Evidence.** Read §§3–5.3, Tables 1–3. D-Rep comprises 40,000 prompt/reference examples, six replication levels and ten annotators, split 90/10. PCC/relative-distance pairs are CLIP 36.8/35.8, DINOv2 39.0/32.9, SSCD 29.1/62.3; exponential PDF embedding reports 56.3/25.6 (Tables 1–2).

**Boundary / relevance.** These are graded agreement metrics, not false-acceptance-controlled verification. Table 3's selected high-replication pairs do not supply negative specificity. This directly relevant prior art undermines a generic diffusion-copy-descriptor novelty claim, while leaving exact-shot/regeneration discrimination unresolved.

# Attack-literature search log

All searches and reads below occurred on 2026-10-25 UTC. Paper text is cached outside Git; see `source-manifest.json`. Search hits alone are not evidence. The legacy arXiv full-text extracts were moved, with matching pre/post SHA-256, into `legacy-cli/attacks/` under the paper cache.

| Engine | Query or direct retrieval | Useful primary source / action |
|---|---|---|
| Web search | `arxiv provable removability of image watermarks diffusion regeneration paper` | Zhao et al., arXiv:2306.01953v3; opened §§2–5 and Appendix E. |
| Web search | `DiffPure Diffusion Models for Adversarial Purification experiments arxiv` | Nie et al., arXiv:2205.07460v1; opened §§3,5 and ablations. |
| Web search | `W-Bench benchmark watermark attacks VINE paper` | Lu et al., arXiv:2410.18775v2 / ICLR 2025; inspected cached §§3–4. |
| Web search | `multi pass rinsing watermark diffusion removal paper` | An et al., arXiv:2401.08573v3 / ICML 2024; inspected cached §§3–4. |
| Direct arXiv HTML | `2306.01953`, `2205.07460`, `2608.10166` | Saved official HTML for Zhao, DiffPure and MarkNull; inspected methods and experiments. |
| Direct cached primary full text | `2410.05470v2`, `2405.08363v2`, `2610.02010v1`, `2601.16473v1`, `2609.08213v1`, `2504.20111v1` | Inspected CtrlRegen, UnMarker, LFM, DeMark, DRIFT and single-image attack sections; the first three receive V2 cards in this package. |

Search scope is bounded to the queries above and the cached papers. No absence-of-prior-work claim follows from it.

# C2 search and inspection log

Date: 2026-10-18. Primary-source web search and full-text reading only. No code or data downloaded, and no experiment performed. Inventory was read before this search. Counts below indicate useful distinct primary leads, not exhaustive search-engine result counts.

| Query or direct-open route | Useful leads and disposition |
|---|---|
| `UnMarker universal watermark removal 2025 paper` | arXiv and DBLP; method/evaluation read, final publication metadata checked |
| `CtrlRegen controllable regeneration watermark removal 2410.05470` | arXiv and author repository; V2 paper read |
| `W-Bench VINE watermark regeneration benchmark` | official repository, OpenReview and dataset card; handed to C1, no duplicate card |
| `"WAVES" "watermark" benchmark arxiv` | arXiv, official project and repository; V2 read |
| `site:arxiv.org "regeneration" "robustified encoder" watermark` | No decisive exact-match primary source |
| `watermark removal robustified encoder adversarial perturbation VAE 2025 2026` | GhostVAE, challenge solution and SpecGuard supplement; challenge V2, others leads only |
| `"watermark" "robust encoder" regeneration` | No direct evidence of the requested robustified-regenerator experiment |
| `"Watermarks in the Sand" arxiv` | arXiv 2311.04378 and author discussion; full text opened, C8 inspection pending |
| `"watermark" "robustified" encoder` | No exact source supporting a measured robustifier |
| `"watermark removal" "adversarially robust" encoder` | PRC ICLR 2025 Appendix Figure 8 discusses a robust/private VAE as a possible mitigation; not a completed robustifier experiment |
| `"watermark" "robust VAE"` | SERUM author blog and GhostVAE; not evidence for the hypothesized robustified removal encoder |
| Zhao 2306.01953 direct open | v3 metadata, theory, method and experiments read |
| 2609.16832 supplied by C1 | Local-watermark benchmark, V2 read |
| 2605.09203 direct primary open | Forensic-stealth paper, V2 read |

Version recovery: attempted UnMarker v4 and CtrlRegen v3 URLs did not resolve; authoritative metadata identified v2 for both. No inference is made from a nonexistent version. OpenReview/browser challenges and unavailable publisher pages were not bypassed; accessible author/arXiv versions are identified explicitly.

## Remaining leads: V1/V0, excluded from V2 count

- GhostVAE, arXiv 2608.00543, [official repository](https://github.com/CryptoAILab/GhostVAE/): abstract/project lead only (V1). Supply-chain encoder compromise is distinct from ordinary robustified regeneration.
- SpecGuard, ICCV 2025 [official supplement](https://www.openaccess.thecvf.com/content/ICCV2025/supplemental/Alam_SpecGuard_Spectral_Projection-based_ICCV_2025_supplemental.pdf): V0 until substantive main-paper reading; forwarded to C1 as optional refresh.
- *Diffusion-based image editing for breaking robust watermarks*, arXiv 2510.05978: V0 citation lead from the local-watermark benchmark.
- SERUM, [author discussion](https://sprintml.com/blog/2026-04-25-serum/): V1, needs primary paper; C7 boundary candidate.
- *Watermarks in the Sand*, arXiv 2311.04378: pending C8; not counted here.

## Search answer: robustified encoders

This targeted search did not establish a published, measured robustified-encoder removal result applicable to F5. PRC's discussion motivates a hypothesis, not a result. Future experiments may test an independently trained or robustified encoder, but the dossier must label the latter as a proposed adversary and explain its training/access cost. See ../Q-VAE.md for the separate, stronger conclusion that SD1.x and SD2.x do not establish independent encoder families.

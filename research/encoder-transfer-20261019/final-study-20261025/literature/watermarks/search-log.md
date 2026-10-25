# WP1 watermark search and inspection log

Date: 2026-10-25 UTC. Search service: live web search; primary full texts: arXiv HTML. Search requests were grouped for efficiency; exact per-query wall-clock timestamps were not preserved. All listed queries were executed during this subtask. Cached papers are outside the repository under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/watermarks/`. HTML-to-reading-text copies are conveniences; HTML hashes identify sources.

## Executed queries

| Order | Exact query | Disposition |
|---|---|---|
| 1 | `Tree Ring Gaussian Shading ZoDiac Stable Signature watermark arxiv` | Located primary initial-noise, decoder-training and latent-optimization papers. |
| 2 | `ROBIN WIND RingID diffusion watermark arxiv` | Primary IDs 2411.03862, 2412.04653, 2404.14055. |
| 3 | `ZoDiac watermark diffusion arxiv 2024` | Confirmed 2401.04247; full-text title differs from earlier shorthand title. |
| 4 | `Hidden in the Noise Two Stage Robust Watermarking Images WIND 2412.04653` | Confirmed WIND primary full text/proceedings. |
| 5 | `latent diffusion watermark encoder transfer VAE SDXL 2025 2026` | Located WMAdapter and newer leads; separated deployment transfer from attack transfer. |
| 6 | `"WMAdapter" watermark VAE zero-shot transfer arxiv` | Inspected Appendix A.4; only stated zero-shot pair is SD2.1→SD1.5. |
| 7 | `"Guidance Watermarking for Diffusion Models" arxiv` | Inspected 2509.22126v2, methods/experiments/Appendix C. |
| 8 | `"watermark" "encoder" "transfer" "SDXL" arxiv` | Additional coverage; no absence or first-ever conclusion. |

## Full-text inspections

`source-manifest.json` records exact versions, dates, URLs, artifacts, SHA-256 and section/table locators for twelve V2 primary sources. All numbered cards derive from opened method and experiment passages, not snippets. Stable Signature's guessed v4 URL returned 404; v2 is the verified artifact. OpenReview's WMAdapter PDF `https://openreview.net/pdf?id=HAD6iZxKuh` encountered an access challenge; primary arXiv v1 was used instead. Unversioned arXiv download requests were resolved using the version/date printed within each cached HTML; canonical manifest URLs pin those versions.

The earlier interrupted worker's ten complete `.txt` full texts were moved with native PowerShell from this owned folder into the authorized external `papers/legacy-cli/watermarks/` cache. `legacy-cache-manifest.json` preserves original→cache paths and SHA-256. They did not count as V2 by mere existence. The newer inspected primary HTML is the principal V2 artifact. FreqMark's legacy text was preserved but not elevated to V2 or used for claims in this dossier.

## Lower-verification recent leads — excluded from V2 evidence

| Lead | Located record | Status and limit |
|---|---|---|
| GhostVAE | https://www.usenix.org/conference/usenixsecurity26/presentation/liu-jinyuan | V1 metadata lead; encoder-backdoor relevance; no method/experiment inspection here. |
| GROW | https://github.com/luopengchen/GROW | V1 primary project/README lead; CVPR2026 association observed; paper not inspected. |
| Latent Seal | DOI 10.1007/s11633-025-1620-y | Lower-verification press/metadata lead dated June 2026; no primary full-text inspection. |
| TraceMark-LDM | ScienceDirect search result dated June 2026 | V1 abstract/metadata only; excluded from claims and bibliography. |
| Semantic-aware attention-guided digital watermarking | https://www.sciencedirect.com/science/article/pii/S0923596526001955 ; DOI 10.1016/j.image.2026.117672 | V1 abstract/metadata only; not inspected. |
| DiffMark / “Transferable Multi-Bit Watermarking Across Frozen Diffusion Models via Latent Consistency Bridges” | Parent-supplied aggregator lead | V0; no verified primary source in this subtask. |
| BiSLW / “Bi-Spectral Latent Watermarking for Generative Diffusion Models” | Parent-supplied aggregator lead | V0; no verified primary source in this subtask. |

Only permitted paper HTML was downloaded; no code repositories, model weights, images or datasets were downloaded. No claims are made from the lower-verification leads. DOI/publication metadata not independently checked is null or explicitly unnormalized in the manifest.


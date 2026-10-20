# T7 stage 1b search and coverage

2026-10-20. Resumed documentary work only. Eight preserved API/repository query receipts plus four new live web queries = 12 distinct durable queries across four categories. Prior interrupted work referred to 38 queries, but the missing first 30 are not counted without individual receipts. No query snippet counts as method/evaluation evidence.

| ID | Category | Exact query | Receipt / screening |
|---|---|---|---|
| Q31 | openalex | image watermark benchmark robustness quality | `Q31.json`; Metadata discovery only; overlapping leads link to full-text cards; no metadata-only item counts as V2. |
| Q32 | openalex | image watermark false positive matched distortion | `Q32.json`; Metadata discovery only; overlapping leads link to full-text cards; no metadata-only item counts as V2. |
| Q33 | openalex | visual paraphrasing image watermark 2026 | `Q33.json`; Metadata discovery only; overlapping leads link to full-text cards; no metadata-only item counts as V2. |
| Q34 | official_repository | VINE official evaluation/quality threshold | `Q34.json`; Official README read as discovery/release context only; frozen pinned implementation remains T5 authority. |
| Q35 | official_repository | WAM official native FPR/mask detection | `Q35.json`; Official README read as discovery/release context only; frozen pinned implementation remains T5 authority. |
| Q36 | official_repository | WAVES official reporting benchmark | `Q36.json`; Official README read as discovery/release context only; frozen pinned implementation remains T5 authority. |
| Q37 | arxiv_api | all image watermark benchmark 2025-2026 | `Q37.xml`; Metadata discovery only; not proof of venue or evaluation practice. |
| Q38 | arxiv_api | watermark false positive quality | `Q38.xml`; Metadata discovery only; not proof of venue or evaluation practice. |
| Q39 | web_search | site:openaccess.thecvf.com CVPR 2026 image watermark evaluation false positive quality PECCVAI | `Q39-Q42-web.json`; Official CVF/NeurIPS/ICLR/ECVA identities corroborated. Certifiably Robust Image Watermark and Structured-Key candidates are screened leads only, not V2 cards; LLM watermark results are excluded as a different modality. |
| Q40 | web_search | site:proceedings.neurips.cc 2024 ZoDiac watermark false positive image quality | `Q39-Q42-web.json`; Official CVF/NeurIPS/ICLR/ECVA identities corroborated. Certifiably Robust Image Watermark and Structured-Key candidates are screened leads only, not V2 cards; LLM watermark results are excluded as a different modality. |
| Q41 | web_search | site:proceedings.iclr.cc 2025 image watermark benchmark matched quality false positive VINE WAM | `Q39-Q42-web.json`; Official CVF/NeurIPS/ICLR/ECVA identities corroborated. Certifiably Robust Image Watermark and Structured-Key candidates are screened leads only, not V2 cards; LLM watermark results are excluded as a different modality. |
| Q42 | web_search | site:ecva.net 2024 watermarking bit accuracy image quality LaWa RingID Robust-Wide | `Q39-Q42-web.json`; Official CVF/NeurIPS/ICLR/ECVA identities corroborated. Certifiably Robust Image Watermark and Structured-Key candidates are screened leads only, not V2 cards; LLM watermark results are excluded as a different modality. |

## Coverage statement

Fifteen distinct top-venue papers: ICML 2024 (1), ICLR 2025 (3), ECCV 2024 (3), CVPR 2024 (2), CVPR 2025 (1), ICCV 2025 (3), NeurIPS 2024 (1), CVPR 2026 (1). All have official venue evidence and their own V2 method/evaluation card. Thirteen are final PDFs; WAVES and VINE use explicitly identified arXiv versions after failed official PDF transport. They count once each. Historical grouped cards and policy pages do not increase the floor. The table covers image counts, metrics, FPR operating points, quality practice, baselines and exact locators. It deliberately keeps incomplete counts/thresholds as NR and preserves VINE/WIND internal contradictions.

OpenAlex/arXiv metadata is used for discovery; official repositories supply release context. The floor relies on inspected primary papers, not index ranking or claimed journal quartiles. No Q1 journal ranking is needed because all counted papers meet the top-venue alternative.

## what we might still have missed

The search is bounded rather than exhaustive: queries emphasize image watermark evaluation, editing, low-FPR reporting and the chosen external methods. It may miss Q1 journals indexed under steganography/authentication, non-English work, 2026 late camera-ready changes and benchmark supplements with counts omitted in the main paper. The newest evidence is one CVPR 2026 evaluation; this is not a census of 2026 research. Certifiably Robust Image Watermark and Structured-Key ECCV leads were not read to V2 here and therefore do not count. WAVES/VINE official PDFs remained transport-inaccessible; the inspected arXiv versions may differ from final proceedings. Some supplements were not read in full; missing detail means absent in the inspected windows, not nowhere documented. Human perceptual judgments, low-FPR calibration on a fresh population, and actual matched-quality overlap remain future evidence, not literature substitutes.

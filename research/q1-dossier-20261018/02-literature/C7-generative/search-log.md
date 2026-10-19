# C7 search and inspection log

Date: 2026-10-18. Research only; no experiments, images, code acquisition, packages or model/data downloads. Inventory was read before search. Authoritative MAIN STATE was read once. Sources used for scientific claims are primary papers/venue pages. HTML was read through the web tool; no local caches were created.

## Queries and direct retrievals

| Query/direct lead | Result and disposition |
|---|---|
| `Tree Ring Watermarks NeurIPS 2023 Wen Kirchenbauer Geiping Goldstein` | arXiv v3 and official NeurIPS 2023 page; published title differs from preprint title. Method and evaluation refreshed. |
| `Gaussian Shading watermark CVPR 2024 Yang` | official CVF paper page and arXiv; current v3 replaces inherited v1. §§3–5 refreshed. |
| `Pseudorandom Codes image Watermarks ICLR 2025 2410.07369` | arXiv v4, ICLR 2025 metadata; inherited v2 stale. Formal assumptions/method/evaluation refreshed. |
| `AquaLoRA WOUAF watermark ICML 2024 CVPR 2024` | primary conference/arXiv leads; both inspected fully at required method/evaluation locators. |
| `WOUAF Weight Modulation User Attribution Fingerprinting CVPR 2024` | official CVF page, arXiv v3. Distinguished per-bit metric from million-entry database test. |
| `AquaLoRA ICML 2024 Feng proceedings` and `site:proceedings.mlr.press/v235 "AquaLoRA"` | PMLR volume index resolves feng24k. An initially guessed feng24c URL was unrelated and rejected; no scientific claims taken from it. |
| `WIND watermark 2412.04653 publication` | arXiv v5; official ICLR proceedings PDF subsequently found. Natural-photo and database passages inspected. |
| `ROBIN 2411.03862 RingID 2404.14055 publication` | arXiv v2/v3 refreshed. |
| `site:openaccess.thecvf.com "Stable Signature" Fernandez ICCV 2023` | official CVF PDF/program; current arXiv v2 method/evaluation refreshed. |
| `"Hidden in the Noise" "NeurIPS" 2025` | no primary venue support; did not assign NeurIPS. |
| `"Hidden in the Noise: Two-Stage Robust Watermarking for Images" site:openreview.net` | official ICLR 2025 proceedings PDF surfaced; arXiv primary full text used. |
| `"RingID" "2024" "ECCV"` and `"RingID" site:ecva.net` | initial queries found secondary leads only; no venue claim was imported from them. |
| `"RingID" "ECCV" site:link.springer.com` and `"RingID" "ECCV" site:ecva.net/papers/eccv_2024` | official ECVA final PDF 04104.pdf located and opened; first-page title/authors verified. ECCV 2024 status now primary-supported; substantive method/evaluation remains pinned to arXiv v3. |
| `"ROBIN: Robust and Invisible" site:proceedings.neurips.cc` | official NeurIPS 2024 PDF. |
| `"Tree-Rings Watermarks" site:papers.neurips.cc` | official NeurIPS 2023 final-title page. |
| Direct author-blog lead `https://sprintml.com/blog/2026-04-25-serum/` | resolved primary arXiv 2603.13396v1. Method, experiments and relevant appendices read; blog is discovery only. |

## Freshness and access notes

Current arXiv records were opened for the ten counted works. Version identifiers are pinned in `matrix.csv`; author metadata supports SERUM's ICLR 2026 Poster status, but the OpenReview page returned a challenge and was not independently inspected. CVF PDF retrieval for Stable Signature/WOUAF sometimes failed internally; official venue HTML/program and arXiv full text supplied metadata/method/evaluation. No abstract-only source received V2. Some source-specific experiment counts not needed for the boundary were not re-extracted; cards mark these missing rather than invent them.

Seven inherited cards were read from `research/literature/m1-latent-survey/cards/` and `research/literature/m1-primary-extension/cards-additional.md`; their explicit section/table trails are named in each refresh. Ten counted cards additionally received live primary method/evaluation inspection. SEAL and GROW/DiffMark are routed to C3/C1 and are not counted again.

## Not-yet-refreshed leads (not additional V2 counts)

| Lead | Current C7 status | Existing evidence / next bounded read |
|---|---|---|
| Gaussian Shannon, arXiv 2603.26167v1 | V0 freshness; retained project V2 is not silently promoted | `research/literature/m1-latent-survey/cards/gaussian-shannon.md`; refresh primary metadata then inspect coding/decoding assumptions and evaluation. |
| Latent Watermark, arXiv 2404.00230v3 | V0 freshness | Existing inventory names `research/literature/journal-upgrade-20261009/sources/latent-watermark-v3.html`; inspect terminal-latent insertion and learned decoder evaluation. |
| RAIN, arXiv 2609.14856v1 | V0 freshness | Existing `research/literature/journal-upgrade-20261009/rain-v1-card.md` V2 locators §§3–4/Tables 1–4; fresh 2026 primary/version check remains pending. |
| GaussMarker | V0 paper inspection | Primary SERUM cites it as a comparator; do not infer mechanism/guarantees from SERUM's characterization. Locate original primary paper before upgrading. |

No V1-only papers were used for scientific synthesis. These leads are explicitly retained so ten refreshed works do not imply exhaustive coverage of 2026 literature.

Parent refresh 2026-10-18: RAIN abstract history identifies v2 dated September 22, superseding retained v1. Opened v2 Sections 3-4 and Tables 1-2; added Li2026RAIN. Extractor-only two-GPU latency is not end-to-end DCT cost.

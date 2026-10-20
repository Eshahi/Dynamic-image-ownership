# T4 Stage1b search log

Date/cutoff: 2026-10-20. This is an actual-query log, not a proposed search plan. Eighteen distinct discovery queries were issued across four categories. The first two web batches were pooled by the search tool; exact queries are preserved, while relevant leads below describe batch-level outcomes rather than claimed per-query rankings. Nine API responses are cached in full. Web event summaries are cached, not represented as full raw search exports.

## Successful discovery queries

| ID | Category | Exact query | Outcome |
|---|---|---|---|
| W01 | web | `watermark regeneration removal Gaussian bound encoder Lipschitz Zhao invisible watermarks` | Found Zhao removal-bound source and related watermark-removal leads. |
| W02 | web | `adversarial perturbation transfer encoder Jacobian alignment diffusion VAE watermark` | Found encoder-attack/backdoor and adversarial-watermark leads; primary mechanisms rechecked via PhotoGuard/GhostVAE. |
| W03 | web | `2025 2026 watermark encoder robustness smoothing regeneration PRC` | Found FreqMark, LFM, CtrlRegen and other recent leads; unsupported secondary/publisher-only results not promoted. |
| W04 | web | `site.arxiv.org "Certified Adversarial Robustness via Randomized Smoothing"` | Located Cohen smoothing primary source; actual version resolved by arXiv metadata after failed version guesses. |
| W05 | web | `site.arxiv.org "Diffusion Models for Adversarial Purification"` | Located DiffPure primary source and related purification work; version1 subsequently inspected. |
| W06 | web | `site.arxiv.org watermark "Robustness of AI-Image Detectors" Saberi` | Located Saberi detector-limit/purification primary source. |
| W07 | web | `site.arxiv.org "Latent Frequency Masking"` | Located LFM paper, selected for fresh method/evaluation reading. |
| W08 | web | `"Improving Adversarial Transferability via Model Alignment" ECCV 2024 paper` | Located ECVA paper, arXiv version history and author repository; arXiv v2 method/evaluation read as T4-13. |
| W09 | web | `"An adversarial transferability metric based on SVD of Jacobians" paper` | Located open-access publisher article; discovery only, not floor evidence. Model-alignment paper selected for deep reading. |
| A01 | arxiv_api | `all:"watermark" AND all:"encoder" AND all:"regeneration"` | New Limits and BiSLW mechanism leads; FeatMark, SpreadMark, WaterVIB and other leads preserved as discovery-only. |
| A02 | arxiv_api | `all:"watermark" AND all:"Gaussian" AND all:"bound"` | New LFM and Limits leads qualified; SemField full text screened as text watermarking and excluded; 3D/VR/LLM leads excluded. |
| A03 | arxiv_api | `all:"adversarial" AND all:"autoencoder" AND all:"robust"` | Broad robustness search returned mainly malware/VLA/medical/security-domain items; no qualified replacement SDXL attack encoder. |
| O01 | openalex | `watermark regeneration encoder robustness` | Returned Decoupling Defense, SpreadMark and image-watermark survey leads plus out-of-modality records; no absence claim. |
| O02 | openalex | `adversarial transferability Jacobian alignment` | Located Jacobian-SVD and model-alignment papers; model alignment subsequently read as T4-13. |
| O03 | openalex | `latent frequency watermark removal` | Located LFM and newer adaptive attack leads; LFM qualified, LiBRA/RAVEN/ProxyEraseAgent remain discovery-only. |
| G01 | official_repository_platform | `watermark robust encoder` | Nine total repositories, six returned; no verified drop-in robust SDXL attack encoder. Platform search does not establish author ownership or code rights. |
| G02 | official_repository_platform | `latent frequency masking watermark` | Successful search with zero results; official LFM repository was separately located through paper/web. Empty search is not an absence proof. |
| G03 | official_repository_platform | `diffusion randomized smoothing purification` | Successful search with zero results; does not establish absence of purification implementations. |

## Failed discovery queries

None. G02/G03 returned zero results with successful HTTP responses; they are successful empty queries, not access failures. Direct retrieval failures below do not inflate the query count.

## Failed direct retrievals and resolution

| URL actually requested | Outcome | Resolution |
|---|---|---|
| https://arxiv.org/html/2205.07460v3 | HTTP Error 404: Not Found | Correct arXiv version then located and read: 2205.07460v1. |
| https://arxiv.org/html/1902.02918v4 | HTTP Error 404: Not Found | Correct arXiv version then located and read: 1902.02918v2. |
| https://arxiv.org/html/2410.18775v3 | HTTP Error 404: Not Found | VINE version guess failed. No T4 V2 card counted; baseline evidence belongs to T3. |
| https://arxiv.org/html/1902.02918v6 | HTTP Error 404: Not Found | Correct arXiv version then located and read: 1902.02918v2. |
| https://arxiv.org/html/2205.07460v5 | HTTP Error 404: Not Found | Correct arXiv version then located and read: 2205.07460v1. |

## Source screening and coverage

Thirteen distinct full-text primary theory/mechanism sources are in `source-manifest.json`, each with an individual card, exact version, cached HTML SHA-256, derived-text SHA-256, document license, and method/evaluation locators. Five Stage1a sources were explicitly rechecked; eight are new T4 cards. Limits is formal theory with numerical Gaussian evaluation, clearly distinguished from an empirical image benchmark. SemField 2610.11848v1 was fetched and screened but excluded because it addresses text/sentence watermarking. No secondary summary, abstract-only result or duplicate version counts toward V2.

Search selection prioritized (1) the actual Gaussian removal assumptions, (2) encoder sensitivity and independent-model alignment, (3) carrier/payload/security distinctions, (4) repeated and adaptive regeneration, and (5) the proposed smoothing/pixel/robust-encoder interventions. New October LFM and September Limits papers were read. A targeted late query added direct model-alignment evidence after the numerical floor was already met.

ArXiv and OpenAlex queries returned up to 8 records; GitHub up to 6. All source dates were screened against 2026-10-20 using metadata. GitHub is an official repository platform, but returned repositories are not automatically official author implementations. No claim of a global absence of a robust replacement encoder is made.

## what we might still have missed

Discovery-only leads include Jacobian-SVD metrics, FeatMark, SpreadMark, WaterVIB, LiBRA, RAVEN and ProxyEraseAgent. They remain leads rather than inspected evidence. Search truncation, indexing lag, alternative terminology and changing releases may hide other mechanisms. The core does not identify local Jacobians, input-dependent covariance, human visual utility, adaptive forgery security or a valid native pixel-space strength protocol. See the synthesis for the consequences.

## Audit files

`search-events.json` is the machine-readable query record. `retrieval-events.json` separates direct paper successes/failures. `download-receipts.json` records all successful documentary network downloads. Full API responses, source HTML and derived text live only under the authoritative main-checkout cache. `floor-audit.json` lists qualifying IDs. These files report readings and algebraic deductions, not reproductions or experiment outcomes.

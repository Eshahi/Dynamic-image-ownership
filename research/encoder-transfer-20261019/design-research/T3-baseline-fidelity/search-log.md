# T3 search and inspection log

Updated 2026-10-20 by Codex agent. This log extends the 2026-10-19 topic work rather than resetting it. The authoritative MAIN STATE, BRIEF sections 1a/1b, prior topic evidence and the literature-synthesis skill were inspected. No executable upstream code, model, weight, image or scientific runtime was loaded. Only research-source acquisition, text extraction, JSON/hash inspection and topic-document generation occurred.

## Counted discovery

There are **22 distinct successful substantive discovery queries across three categories**: 18 web searches, one OpenAlex search and three official GitHub repository searches. This conservative count excludes metadata/file fetches, release retries and the older narrative query list. The arXiv API route was attempted three times but failed; those requests are recorded and not counted as successful coverage. Different channels searching a related topic are reported separately, while a retry is not another query.

The 18 web searches below were executed in this resumed research session. Their result pages are not archived full text and have no invented checksum. They are discovery receipts only. Primary result URLs and follow-up cache receipts are in [search-events.jsonl](search-events.jsonl). The full-text method/evaluation inspections and their exact versions are independently recorded in [deepening-manifest.json](deepening-manifest.json). Secondary search hits were leads, never the authority for numerical claims.

| ID | Exact web discovery query | Finding and follow-up |
|---|---|---|
| W01 | `post hoc image watermark regeneration benchmark 2025 2026 TrustMark VINE Pixel Seal` | Broad discovery led to final TrustMark, VINE and EditGuard primary sources; comparisons require payload and quality qualification. |
| W02 | `post-hoc robust watermarking diffusion regeneration image editing 2026 method code` | Newer-method search surfaced generation-time methods as well as eligible post-hoc leads; generation-time leads were not counted. |
| W03 | `"OmniGuard" "watermark" "github"` | Official OmniGuard repository found; primary paper and partial demo release inspected separately. |
| W04 | `"EditGuard" "copyright" watermark regeneration` | EditGuard arXiv and CVF found; local inpainting evidence must be separated from global regeneration. |
| W05 | `"post-hoc" watermark "2026" "code" regeneration latent` | Release-oriented search led to the official VideoSeal model zoo, including ChunkySeal; no new core arm. |
| W06 | `"SimuFreeMark" code github checkpoint` | No official SimuFreeMark implementation or weights established by this targeted search; paper remains V2. |
| W07 | `"SpecGuard" "weights" watermark` | Official SpecGuard release evidence inspected; checkpoint and dependency limits remain in its card. |
| W08 | `"Pixel Seal" watermark "github"` | Official VideoSeal release/card establishes PixelSeal model availability; checkpoint bytes were not downloaded. |
| W09 | `"TrustMark" "Q" "BCH_5" encoder decoder 245` | Official TrustMark configuration/source confirms BCH schema and distinct encoder/decoder resizing. |
| W10 | `"RoSteALS" "ZoDiac" "InvisMark" regeneration benchmark` | Cross-baseline search reinforced differences in attack, payload, quality and detector definitions; primary cards carry the numbers. |
| W11 | `"Robust-Wide" watermark code license pretrained` | Official Robust-Wide repository located; license, model and attack conditions are separated. |
| W12 | `"GenPTW" "OmniGuard" "LaWa" image watermark` | GenPTW final AAAI entry and latent post-hoc paths found; method-specific quality retained. |
| W13 | `"Optimizing and Securing the Modern Watermarking Channel for Images"` | SNW full primary text acquired and read, including method and Table 6 regeneration capacity evaluation. |
| W14 | `"Semantic-aware attention-guided digital watermarking for diffusion models"` | Publisher lead found, but full-text acquisition returned 403; not counted as a V2 method. |
| W15 | `"SNW" "watermarking" "2026" images code` | SNW primary paper identified; no verified official code/weights established. |
| W16 | `"LatentShield" watermark "code"` | LatentShield publisher lead found, but full-text acquisition returned 403; eligibility and results remain unverified. |
| W17 | `"SNW" "Gesny" watermark github` | No verified official SNW release found; negative search is scoped, not a universal absence claim. |
| W18 | `"Optimizing and Securing" "github" watermark` | No verified official SNW release found; unrelated or secondary results were not treated as release evidence. |

| Category / ID | Exact query or route | Durable result |
|---|---|---|
| OpenAlex / O1 | `post-hoc watermarking regeneration`, per-page 20 | Successful OpenAlex works search, `openalex-baselines.json`; SHA-256 and 333,575-byte response in the event/manifest. Results were screened as leads, not V2 evidence. |
| Official repository / G1 | GitHub repository search `SimuFreeMark` | Successful API response; no official release established. `simufree-github-search.json`. |
| Official repository / G2 | GitHub repository search `SpreadMark watermark` | Successful discovery response, `spread-repos.json`; method and release assertions are separately sourced. |
| Official repository / G3 | GitHub repository search `NAWE watermark` | Successful discovery response, `nawe-repos.json`; no unverified repository is promoted to an official implementation. |

## Inspection routes, separately from discovery counts

The raw ledger contains 115 events: 18 web searches, one OpenAlex search, three arXiv API attempts, 23 primary-paper acquisition events and 70 official-repository events. The latter include file inspection, metadata, source-tree lookup, unsuccessful direct fetches and fallback routes; they are not 70 substantive discovery queries. The three counted official searches are part of those 70 events, not an extra set. Nine reused primary-cache conversions are recorded separately in `reused-source-manifest.json`; reuse does not add another method.

The method/evaluation texts read are WAM, VINE, TrustMark preprint plus final ICCV PDF, StegaStamp, InvisMark, RoSteALS, ZoDiac, PhaseMark, MBRS, SSL, SimuFreeMark, SpecGuard, Pixel Seal, JigMark, Robust-Wide, SpreadMark v2 (with v1 differences inspected), NAWE, LaWa, Chunky-Seal, GenPTW v2, DistSeal, EditGuard, OmniGuard v2 and SNW. The 24 method cards state the actually read sections, native operating points, side information, code/weights/licenses, conditional regeneration evidence and cost uncertainty. Each card has a current cached-text SHA-256; the final TrustMark PDF has its separate provenance/checksum. A listing or abstract alone is not V2.

Official GitHub, Hugging Face and model-card text established WAM/VINE pins and native implementation details; alternative repository README/LICENSE/configuration and source text were inspected without importing or running them. Remote LFS identifiers, byte counts and checkpoint URLs are metadata, not evidence that weights were locally downloaded. The legacy `manifest.json` retains detailed WAM/VINE dependency URLs and sizes. The new manifest consolidates deeper paper/code text and current cache inventory.

Important adaptive discoveries were the partial OmniGuard demo, GenPTW/LaWa/DistSeal existing-image paths, official ChunkySeal release inside VideoSeal, and SNW's primary Table 6. These changed the coverage or qualification rather than adding a speculative execution arm. SNW gives third-party PixelSeal capacity evidence at a rescaled/whitened operating point; it does not establish native P9 SDXL performance.

## Access failures and version handling

All three export.arxiv.org API requests failed (rate limiting or timeout). Direct raw GitHub URLs frequently returned errors; successful GitHub contents API or HTML fallbacks were used where recorded. API rate limits also required repository HTML fallback for DistSeal and LaWa. Two earlier HTML snapshots of those pages were overwritten by later fetches of the same URL: the old hashes remain historical acquisition receipts, the later hashes match current files, and both extracted-text hashes stayed identical. This is explicitly marked in the manifest rather than presented as an intact archive of every HTML response.

Guessed StegaStamp/ZoDiac main-branch paths returned 404 in the original work, followed by successful master-branch inspection. An absent LICENSE or API `license=null` means no license was established; it is not permission to use or a proof that permission is impossible. Missing checkpoint hashes, mutable URLs, dependency restrictions and incomplete demo paths stay unresolved. A paper license does not license its implementation.

The TrustMark final ICCV PDF was already successfully cached in `cache/access-refresh/` (6,840,136 bytes; SHA-256 `94be2a50e08356b321c4f64a56579eeb63ea4676634ac9c019e3c76f6c5726f5`). Its method, setup and Table 3 were inspected and page 7 visually checked by the preceding topic agent. A later direct T3b refresh returned 403; these are separate events. The final title and DOI are in their own bibliography record, and final results supersede old preprint claims only where stated. No false claim of a newly successful refresh is made.

The two new ScienceDirect leads below returned HTTP 403 to full-text acquisition. Search-result abstracts/snippets were not used to fill missing method or evaluation fields. Neither is in the V2 count or bibliography. No abstract-only negative/positive result is asserted.

## what we might still have missed

*Semantic-aware attention-guided digital watermarking for diffusion models*, DOI 10.1016/j.image.2026.117672, and *LatentShield: A robust latent watermarking framework for diffusion-generated images with multi-objective optimization*, DOI 10.1016/j.iswa.2026.200719, remain inaccessible primary-text leads. Post-hoc eligibility, complete methods, evaluation and releases are unverified. They may change the survey after primary access.

Image-to-video-specific WaTeRFlow, generation-only methods, and text/code watermark systems are outside this post-hoc image baseline count. This boundary is not a verdict on their merit. Unindexed papers, alternate method names, private or newly updated releases and supplements not exposed in the inspected version remain possible omissions. Failed arXiv API access weakens coverage of that route; the successful three-category search satisfies the minimum without pretending to be exhaustive. Release and license searches establish what was found as of 2026-10-20, not universal absence.

# C3 search and inspection log

Date: **2026-10-18**. Research-only; no experiment, image inspection, model loading, package install or code/data/model download. Paper PDFs/HTML alone were cached. Main authoritative STATE was read once at start, followed by BRIEF and existing-inventory; BRIEF WP2 range was checked again after a mistaken range selected WP3. The thesis-literature-synthesis skill was read. Repository validation scripts were not executed under the research-only interpreter restriction; CSV/card/bibliography consistency was checked with PowerShell text processing.

All searches below used the available **web search (web.run)** engine. “Useful hits” counts distinct useful leads, not the engine's total result count; metadata leads are not treated as verified evidence.

| Query | Useful hits / disposition |
|---|---|
| Craver Memon Yeo Yeung resolving rightful ownerships invertible watermarking 1998 pdf | 2: UCLA primary PDF and metadata lead; full PDF inspected |
| Kutter Voloshynovskiy Herrigel watermark copy attack 2000 pdf | 2: UNIGE repository and mirror lead; repository PDF inspected |
| Müller 2025 forgery diffusion watermark single image CVPR | 2: CVPR and arXiv; refreshed to v3 |
| SemBind 2601.20310 geometric forgery 2606.29807 SEAL 2503.12172 | 0 usable direct matches in combined results; exact primary URLs opened separately |
| "Forging" "Single Image" "latent" watermark Jain 2025 | 1: arXiv 2504.20111, full text inspected |
| "watermark" "timestamp" "Qiao" "Nahrstedt" noninvertible | 1 metadata lead; not used as paper evidence |
| "watermark" "ownership" "regenerate" "enroll" 2026 | 0 exact-attack matches established; no novelty-by-absence inference |
| "Watermark copy attack" pdf Kutter | 1: UNIGE PDF |
| watermark ownership protocol timestamp noninvertible Qiao Nahrstedt pdf | 2: Illinois metadata and Fraunhofer PDF lead; V1/V0 below |
| "semantic watermark" forgery 2026 "2026" defense registry | 0 decisive new match beyond already identified works |
| "One-Shot Forging" watermark NeurIPS 2025 | 2 same-work primary records: official proceedings/arXiv; official method and experiments inspected |
| "Watermark copy attack" "10.1117" | DOI only in secondary records; omitted from verified BibTeX |
| "Resolving rightful ownerships" "10.1109/49.668979" | 1 author-institution repository verifies DOI |
| "Watermark copy attack" "10.1117/12.384991" | Secondary DOI leads only |
| "Black-Box Forgery Attacks" "20937" CVPR 2025 | Official CVPR metadata verifies author/title/pages; official PDF text remained inaccessible |

## Exact-source access and version audit

- Ten primary papers are listed in `matrix.csv`, with specific method/evaluation locators and corresponding cards. Nine use method-plus-experiment inspection; Thietke uses the formal-security-analysis route.
- Craver: UCLA-hosted published PDF; metadata cross-check [SUNY repository](https://researchconnect.suny.edu/en/publications/resolving-rightful-ownerships-with-invisible-watermarking-techniq/).
- Kutter: [UNIGE published PDF](https://access.archive-ouverte.unige.ch/access/metadata/e3e4f2aa-53ab-4eb3-9b1d-d804da974042/download). Author spelling follows the paper rather than inconsistent catalog transliteration.
- Müller: [CVPR metadata](https://www.openaccess.thecvf.com/content/CVPR2025/html/Muller_Black-Box_Forgery_Attacks_on_Semantic_Watermarks_for_Diffusion_Models_CVPR_2025_paper.html) confirmed venue/pages. PDF downloaded, but multiple web parser attempts (standard/www/http/query variants) failed or returned 403. **Substantive V2 evidence is current arXiv v3**, including its explicit PSNR correction. The venue PDF is not falsely claimed read.
- ArXiv abstract version histories and current versioned HTML were opened for Müller, Jain, SemBind, geometric defense, SEAL, WMCopier and Thietke. Current SEAL v4 is dated 2026 although the conference year is 2025; WMCopier v3 has a different title from older search results.
- Souček: [official proceedings abstract/DOI](https://proceedings.nips.cc/paper_files/paper/2025/hash/47fee9cd8a252161dec7cb48ec0ca2f2-Abstract-Conference.html) and official 24-page PDF; method pp.4–6 and experiments pp.6–9 read.
- Selected HTML sections were also read from cached text with tags/equations removed for readability; exact original HTML remains available for formulas/tables. No local paper figures or images were processed.
- [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161.html) opened directly for §§1–2.4.1 as timestamp context. Not counted as a V2 research paper and not used to assert present-day algorithm recommendations.

## Screened leads not promoted to substantive evidence

| Source | Status and reason |
|---|---|
| Qiao / Nahrstedt, Watermarking methods for MPEG encoded video: towards resolving rightful ownership, 1998; DOI lead 10.1109/MMCS.1998.693656 | V1 metadata via Illinois institutional record; method not inspected, not cited for novelty |
| Nahrstedt / Qiao, Non-Invertible Watermarking Methods for MPEG Video and Audio, 1998 workshop | V0 full-text PDF lead at Fraunhofer not opened; not evidence |
| A Watermark Forgery Attack Against Stable Diffusion Model Watermarking, IEEE document 11152559, 2025 | V1 search metadata only; potential adjacent counterfeit-extractor attack; not used for a security or novelty claim |
| arXiv 2604.11720, autoregressive watermark forgery | V1 search abstract only; different generation family, no full-text claim made |
| SemField / LLM watermark result, 2610.11848 | Excluded by modality; not evidence |

This is a targeted cluster search, not a systematic exhaustive review. No absence-of-prior-art claim is licensed by it.

## Cache and artifact accounting

Cache root: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C3/`.

`cache-manifest.csv` records each downloaded paper file's byte length, SHA-256 and absolute path. Includes the unread CVPR PDF explicitly distinguished above. Cached paper total is approximately 22 MB, below the session cap. Source URLs are in cards or access notes; no copyrighted paper text is copied into the dossier beyond titles and short source descriptions.

No thesis quantitative result was imported without ledger IDs. The cluster keeps descriptor-only versus whole-pipeline decisions, any-attacker-record acceptance, ambiguity and unique wrong attribution distinct.


Parent refresh 2026-10-18: reopened MetaSeal arXiv history and v2 Sections 4-6, Appendix C; current version remains v2. Added Zhou2026MetaSeal; gray-box model secrecy and single regeneration failure constrain comparisons.

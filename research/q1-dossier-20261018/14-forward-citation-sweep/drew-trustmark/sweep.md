# DREW and TrustMark forward-citation sweep

Research-only bounded search, 2026-10-19. Prepared by Codex child agent citation_drew_trustmark. No experiments, image inspection, model/code/dataset downloads or shared-file edits. Primary paper text only. Main STATE and existing 87-row literature matrix / 88-entry bibliography informed scope. Outputs are additions, not replacements for the master.

## Outcome and version boundary

One newly read paper directly references DREW: **IConMark**, reference [19]. Two newly read papers directly reference **final TrustMark: NRGMark and Signpost**. Four new usable V2 cards and matrix rows are supplied; a fifth inspected source is quarantined separately. These are bounded verified findings, not a complete count of citations.

Correct the task's venue label: final TrustMark is **ICCV2025**, not CVPR2025. Its title is *TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images*, DOI [10.1109/ICCV51701.2025.01731](https://doi.org/10.1109/ICCV51701.2025.01731), pp.18629–18639. Its older 2023 preprint is *TrustMark: Universal Watermarking for Arbitrary Resolution Images*, arXiv:2311.18297. A citation to that preprint is not evidence of reading/citing the final version. DREW's target reading remains [arXiv:2406.02836v2](https://arxiv.org/html/2406.02836v2); IConMark's bibliography cites the work without a version suffix, so its edge cannot be assigned specifically to v2.

| Newly inspected candidate | Primary reference-list edge | Reading / disposition |
|---|---|---|
| [IConMark](https://arxiv.org/html/2507.13407v1) | DREW [19]; older TrustMark [4] | V2; [card](cards/Sadasivan2025IConMark.md) |
| [Coexistence and Ensembling](https://arxiv.org/html/2501.17356v1) | Older TrustMark, Bui et al. 2023a | V2; [card](cards/Petrov2025Coexistence.md) |
| [NRGMark](https://collomosse.com/pubs/Agarwal-WACV-2026.pdf) | Final TrustMark [15]; older version [13], PDF p.9 | V2 author PDF; [card](cards/Agarwal2026NRGMark.md) |
| [Signpost](https://arxiv.org/html/2608.10091v1) | Final TrustMark [7] | V2; [card](cards/Agarwal2026Signpost.md) |
| [Ni et al., Breaking Robust Watermarks](https://arxiv.org/html/2510.05978v1) | Older TrustMark, Bui et al. 2023 | Inspected V2, conclusions quarantined; [card](cards/Ni2025BreakingWatermarks.md) |

The [candidate register](candidates.csv) retains verified edges, partial reference extracts, metadata-only candidates and keyword neighbors as different statuses. Parent-owned Nemecek arXiv:2603.02378v2 ref.[5] and existing Soft Bindings arXiv:2610.04151 ref.[4] are cross-referenced from the parent's primary verification, not independently promoted here. Existing InvisMark is not recarded. Parent also owns RAVEN and Watermarks Attack Watermarks reading.

## Search record and coverage

Every query below was issued/read on **2026-10-19**. General web search was used for discovery; only primary paper text supports paper conclusions. Index metadata alone never validates an edge.

| Source / exact query or endpoint | Observed result and limitation |
|---|---|
| Semantic Scholar `graph/v1/paper/ARXIV:2406.02836?fields=title,citationCount,citations.title,citations.year,citations.externalIds` | HTTP429; no coverage inference. |
| [OpenAlex DREW DOI lookup](https://api.openalex.org/works/https://doi.org/10.48550/arXiv.2406.02836), [cites W4399444533](https://api.openalex.org/works?filter=cites:W4399444533&per-page=100) | 0 indexed citing works and 0 referenced works. IConMark's primary reference disproves any inference of no citations. |
| [OpenAlex final TrustMark DOI lookup](https://api.openalex.org/works/https://doi.org/10.1109/ICCV51701.2025.01731), [cites W7160035753](https://api.openalex.org/works?filter=cites:W7160035753&per-page=100) | 9 indexed works; full JSON retained in `openalex-final-trustmark.json`. NRGMark primary edge verified. Eight others remain metadata-only. Signpost found outside this index result demonstrates incompleteness. |
| [OpenAlex older TrustMark cites W4389261001](https://api.openalex.org/works?filter=cites:W4389261001&per-page=100) | 7 indexed works, including three 2024 works outside the requested years. 2025/26 candidates retained separately. |
| Pith TrustMark citation view | Older-version SEAL lead; already in master. Discovery only, no authority for an edge. |
| Web exact-title variants: `"DREW: Towards Robust Data Provenance" citations 2025`; `"DREW" "Error-Controlled Watermarking" "2025"` and `"2026"`; `"2406.02836" "2025"` and `"2026"`; `"DREW" watermarking "References"` | IConMark primary reference; broad queries also produce unrelated uses of Drew. |
| `"DREW" "TrustMark" watermark 2025 2026`; `"TrustMark: Universal Watermarking" citations 2026`; `"TrustMark: Robust Watermarking and Watermark Removal" "2026"` | Older/final identity separation; NRGMark, Signpost and unresolved OpenReview leads. |
| `"On the Coexistence and Ensembling of Watermarks" arxiv`; `"Signpost Watermarking: Joint Optimization"` | Primary versioned HTML and arXiv identity pages opened; method and evaluation inspected. |
| Candidate exact-title searches: DDRW, SLIM, ZOETROPE | Bibliographic corroboration only. Closed/missing primary fulltext leaves reference edges unverified. ZOETROPE institutional/PubMed authorship metadata differ; no forced identity merge. |

This is not an exhaustive forward-citation census. Index coverage is partial, new records can lack references, preprint/final identities split, search ranking can miss works, and two OpenReview PDFs were blocked by browser challenges. CVF retrieval for NRGMark was intermittent; its author-hosted PDF was read instead. No failed API or unavailable fulltext is evidence of absence. The search date is the coverage boundary, not a claim that all 2026 publications have been indexed.

## Consequence for the thesis

The inference from these reads is narrower than a method recommendation. NRGMark strengthens the already-established objection to broad watermark-plus-registry novelty. Signpost concerns routing to watermark technologies, while the thesis stores original-image descriptors; these registries must not be conflated. IConMark and Coexistence strengthen prior art for complementary or layered signals, with different image-generation assumptions and operating points. Their results cannot be transferred numerically to F5.

None of these newly read evaluations identifies the thesis's incremental q/content-verifier benefit under its owner gate. MAIN STATE/EV77 says every completed E3 beta query fails owner detection before q/content checks. The causal ambiguity therefore remains. There is no basis here to reopen closed baseline work or run an experiment. The defensible contribution remains an empirical distinction between payload recovery and registered-image attribution, with additional compatible controls only a proposal for later authorization.

## Integration and integrity

Merge the four rows in `matrix-additions.csv` and four entries in `new.bib` after the parent's audit. `metadata.json` supplies bibliographic identity sources; each card supplies exact version, locators, cached primary artifact and SHA256. MAIN cache root is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/`. Do not merge Ni2025BreakingWatermarks as reliable results: its separate `quarantine.bib` and card preserve the verified citation and explicit internal concerns. V2 describes inspection depth, not truth certification. Unknown-title OpenReview and similar-title arXiv leads have no new bibliography entries.

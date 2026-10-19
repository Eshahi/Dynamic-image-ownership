# Forward-citation search: October 2026 soft-binding benchmark

Target: `kazempourradi2026softbindings`, arXiv2610.04151v1, 2 October 2026. Searched 19 October 2026. This target had existed for only about seventeen days at the session date. The search window is 2025 through the retrieval date, with temporal plausibility checked against the target's release. No new citing paper was verified for this target in this bounded search. This is an access-and-index result, not evidence that no citing work exists or that novelty is secure.

## Search record

| Route | Query or exact URL | Observed result and interpretation |
|---|---|---|
| Web search | `"Soft Bindings" "Kazempourradi" watermark 2026 citations` | Target and mirrors; no independently verified citing paper |
| Web search | `"2610.04151" -site:arxiv.org` | Target mirrors and automated summaries, not independent research citations |
| Web search | `"2610.04151" citations watermark` | Same limitation |
| Web search | `"Watermarks and Fingerprints as Soft Bindings" -site:arxiv.org -site:alphaxiv.org` | Mirrors/aggregators; no primary reference-list edge found |
| Web search | `"Kazempourradi" "Mojtahedi" "Mohseni" watermark provenance 2026` | Target and author-name mirrors, not forward citations |
| OpenAlex identity | https://api.openalex.org/works/https://doi.org/10.48550/arXiv.2610.04151 | Direct shell retrieval succeeded; W7220650979; cited_by_count0; record updated11October |
| OpenAlex forward query | https://api.openalex.org/works?filter=cites:W7220650979,from_publication_date:2025-01-01,to_publication_date:2026-10-19&per-page=100 | meta.count0; empty results; compact JSON saved in `index-check.json` |
| Semantic Scholar | https://api.semanticscholar.org/graph/v1/paper/ARXIV:2610.04151?fields=title,year,citationCount,citations.title,citations.year,citations.externalIds | HTTP429; unavailable, not zero |
| Primary version check | https://arxiv.org/abs/2610.04151 and https://arxiv.org/html/2610.04151v1 | Submission history still lists only v1; inspected content agrees with the existing card |

OpenAlex also returns referenced_works_count0 although the primary paper has an extensive bibliography. This is an explicit sign of incomplete reference ingestion, so neither its incoming nor outgoing zero should be treated as a complete graph. Initial PowerShell parsing encountered case-distinct abstract-index keys; the final saved selected-field JSON was produced with a case-preserving hashtable parser. Tool-level web opens of the APIs failed, while the shell OpenAlex requests succeeded; those outcomes are distinguished.

## Cross-target edge and scope consequence

The target itself directly cites final TrustMark, ICCV2025, as reference[4], with DOI10.1109/ICCV51701.2025.01731. This is a confirmed incoming edge for the TrustMark target, not a forward citation of the October paper. It was already V2 in WP2 and is not counted as a newly read work.

The primary paper's §6/Table19 gives a .69 union for its specified image pairing; this is complementarity on shared queries, not the accuracy of a deployed decision cascade. Sections5.2/7 show why near-copy identity definitions and complete decision rules matter. Those existing observations already limit broad hybrid and specificity novelty. No extra numerical comparison with the thesis is justified by a citation sweep, and no code or media were retrieved.

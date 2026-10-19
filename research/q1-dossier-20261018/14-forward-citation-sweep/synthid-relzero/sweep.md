# E4: SynthID-Image and Rel-Zero forward-citation sweep

Research-only; accessed 2026-10-19. Canonical seeds: `gowal2025synthidimage`, arXiv:2510.09263v1, and `chen2026relzero`, arXiv:2603.17531v2. Scope: bounded 2025–2026 discovery, primary reference-list verification, and focused method/evaluation reading. This is not an exhaustive bibliography.

## Result and contribution consequence

This lane verified six distinct SynthID-Image citation edges and one Rel-Zero edge. Four SynthID citing papers received new V2 cards; Pixel Seal already has a V2 dossier card. Two publisher-preview sources have verified reference entries but remain V1 for scientific claims. A citation edge does not imply endorsement, replication, or methodological dependence. Anonymous OpenReview search hits remain unresolved leads.

These readings do not restore a broad watermark-plus-registry novelty claim. They also do not identify the added q/content contribution in EV77: the frozen E3 complete-call beta owner gate already fails before those checks. Their defensible contribution is to sharpen distinctions between watermark presence, payload recovery, registered-image attribution, and causally identified robustness. Applying these distinctions to the thesis is our inference, not a result reported by the citing papers.

| Candidate | Cited seed and primary locator | Reading disposition |
|---|---|---|
| Luminark | SynthID; [v1 References, Gowal et al. (2025)](https://arxiv.org/html/2601.01085v1) | New V2; method/evaluation card |
| AWPD | SynthID; [v3 reference 10](https://arxiv.org/html/2603.06723v3) | New V2; inspected v3, not just earlier v2 |
| MarkNull | SynthID; [v1 reference 7](https://arxiv.org/html/2608.10166v1) | New V2; service-specific removal evidence |
| Beyond Generation | SynthID; [v1 References, Gowal entry](https://arxiv.org/html/2610.21760v1) | New V2 for focused ablation; later v2 metadata seen, not read |
| Pixel Seal | SynthID; [v1 References, Gowal entry](https://arxiv.org/html/2512.16874v1) | Existing V2 `Soucek2025PixelSeal`; no duplicate card/bib |
| Multimodale Deepfake-Erkennung in der Praxis | SynthID; [publisher References, Gowal entry](https://link.springer.com/article/10.1365/s40702-026-01314-8) | New V1 reference/method excerpt only |
| Trading off payload and robustness… | Rel-Zero; [publisher References (48), Chen et al. 2026](https://www.sciencedirect.com/science/article/pii/S1077314226003115) | New V1 publisher preview; recognizable title/authors but entry truncated |
| Two anonymous TMLR PDF hits | Search snippets name SynthID; primary PDFs blocked | Unresolved identity; not counted as verified citations |

Parent owns Nemecek's Authenticated Contradictions (arXiv:2603.02378v2, SynthID reference 20), the October soft-binding benchmark, RAVEN and Watermarks Attack Watermarks. Another lane owns IConMark, Coexistence/Ensembling and NRGMark. Their evidence is deliberately not duplicated in this lane's count.

## Search and index coverage

Exact queries are in `search-log.md`; all ran on 2026-10-19 through web search plus primary-page opening. Queries combined seed arXiv IDs, exact titles, title fragments, references/citations terms, and arXiv/CVF restrictions. Follow-up searches resolved candidate identity and version. Citation indexes were used as discovery aids, not scientific evidence.

OpenAlex DOI lookup returned SynthID `W4417128155` with cited_by_count=1 and Rel-Zero `W7139065171` with cited_by_count=0. `cites:` queries returned the German paper and zero records, respectively. The four raw responses are retained alongside this report. The primary references found outside OpenAlex demonstrate that these returned counts are incomplete for this search date; neither zero nor one is a literature-absence finding. Initial PowerShell JSON parsing encountered case-sensitive keys, resolved using `ConvertFrom-Json -AsHashtable`; that was not an index failure.

Semantic Scholar public Graph API returned HTTP 429 for both seeds, including a bounded retry. Web opening of index endpoints also failed. No claim about citation coverage follows from those failures. No authenticated Scholar/Scopus/Web of Science search was performed. Search ranking, crawling delays, inaccessible publisher full text, anonymous submissions, and unpublished citations limit recall. No citation-network closure or saturation claim is made.

ScienceDirect's primary search-rendered preview exposed its References (48) section and the Chen et al. Rel-Zero entry. Direct full/abstract page opens failed (including 403). This verifies an identifiable citation at the preview level, not the complete bibliography string, cited arXiv version, or the paper's method/evaluation. Its issue is November–December 2026; online-first date was not established. The Springer article was accessible for references and a prototype-method excerpt, but was not promoted to V2. OpenReview PDFs presented an access challenge; their anonymous records may overlap other candidates and are not independent paper counts.

## Evidence handling

Existing matrix and bibliography were searched before adding cards. Only four newly read V2 sources enter `new.bib`; V1 and unresolved records remain in `candidates.csv`. Fulltext HTML was cached under the authorized MAIN cache, without fetching image assets; paths and SHA-256 are in `source-artifacts.json`. Beyond Generation is pinned to v1 despite awareness of v2. AWPD is pinned to inspected v3; v2 is retained only as an earlier reading artifact. Cards separate direct results, author interpretation and our inference.

No experiment, image inspection, scoring, package installation, code/model/data download, threshold change, or retained-output edit occurred. No shared dossier matrix or bibliography was edited. CSV/JSON structure and file presence were checked with ordinary PowerShell; no thesis experiment or science-interpreter scripts were invoked.

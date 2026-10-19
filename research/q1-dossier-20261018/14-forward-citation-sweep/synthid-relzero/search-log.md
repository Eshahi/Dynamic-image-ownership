# Search log

Access date for every entry: 2026-10-19. Discovery queries used web search; primary pages and cached HTML supplied claim evidence. Empty/failed retrievals are coverage limitations.

| Query | Purpose/outcome |
|---|---|
| `"2510.09263" -site:arxiv.org -site:huggingface.co` | Seed identifier discovery |
| `"2603.17531" -site:arxiv.org -site:huggingface.co` | Seed identifier discovery; many self/secondary records |
| `"SynthID-Image" references watermark` | Citing bibliography discovery |
| `"Rel-Zero" watermark references` | Citing bibliography discovery |
| `"SynthID-Image: Image Watermarking at Internet Scale" -site:reddit.com -site:github.com -site:huggingface.co` | Exact-title search |
| `"Rel-Zero" "2026" watermark -site:reddit.com` | Date/name search |
| `site:arxiv.org/html "2510.09263"` | Primary fulltext edges |
| `site:arxiv.org/html "2603.17531"` | Primary fulltext edges |
| `"Luminark" watermarking arxiv` | Resolve candidate |
| `"Rel-Zero" -"Rel-Zero: Harnessing" -site:github.com -site:reddit.com` | Reduce seed/secondary duplicates |
| `"AWPD" "arxiv"` | Resolve candidate |
| `"Synthid-image" "2026" site:arxiv.org/html` | Recent primary edges |
| `"Rel-Zero" citations -site:reddit.com -site:github.com` | Forward-discovery probe |
| `"Rel-Zero" site:openaccess.thecvf.com` | CVF discovery probe |
| `"Rel-Zero" "References" watermark -site:reddit.com -site:alphaxiv.org -site:bytez.com -site:papernotes.org -site:aimodels.fyi -site:github.com` | Publisher references discovery |
| `"Harnessing Patch-Pair Invariance" -site:arxiv.org -site:alphaxiv.org -site:papernotes.org -site:github.com -site:papers.cool -site:sciencestack.ai` | Exact subtitle discovery |
| `"Trading off payload and robustness in image watermarking"` | Primary publisher preview |
| `"Trading off payload and robustness in image watermarking" "Rel-Zero"` | Recovered primary References (48) section |
| `"S1077314226003115" "Available online"` | Online-first date unresolved |

## Citation APIs

For each seed ID (2510.09263; 2603.17531):

`https://api.semanticscholar.org/graph/v1/paper/ARXIV:ID?fields=title,citationCount,citations.title,citations.externalIds,citations.year`

Outcome: HTTP 429, including retry; no citation data obtained.

`https://api.openalex.org/works?filter=doi:https://doi.org/10.48550/arXiv.ID&select=id,title,cited_by_count`

Outcome: seed records resolved, saved `openalex-ID.json`.

`https://api.openalex.org/works?filter=cites:W4417128155&per-page=100&select=id,doi,title,publication_year,primary_location`

`https://api.openalex.org/works?filter=cites:W7139065171&per-page=100&select=id,doi,title,publication_year,primary_location`

Outcome: one and zero records, saved `citing-W*.json`; no further pages indicated. Independent primary-reference evidence contradicts interpreting these as comprehensive counts.

## Unresolved access leads

- https://openreview.net/pdf/589ff913f373d72e07f4a60389463f8549ff2961.pdf — anonymous TMLR search hit; access challenge; no identity or independent-edge count.
- https://openreview.net/pdf/97a4f7366f53cddd2a3023ac9c5c58ed10417ec3.pdf — same status; possible overlap unresolved.
- https://openaccess.thecvf.com/content/CVPR2026W/SAFE/papers/Ao_AWPD_Frequency_Shield_Network_for_Agnostic_Watermark_Presence_Detection_CVPRW_2026_paper.pdf — venue PDF failed to open; arXiv v3 is the inspected version.

Rel-Zero name collisions about relational language-model learning, author/project pages and secondary summaries were not treated as forward citations. No complete negative list is claimed.

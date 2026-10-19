# Search and retrieval log

Date: 2026-10-19. Engine: `web.run` except API/PowerShell routes explicitly identified below. Useful manuscript hits means a retained lawful complete original method-and-evaluation text for either target. Every query below returned **zero useful manuscript hits**. Documentary leads are identified separately; counts are not paper counts. Prior search history was read first in `02-literature/access-refresh/`.

| Exact query | Useful manuscript hits | Retained documentary lead / outcome |
|---|---:|---|
| `"Robust Reversible Watermarking" "Guo" manuscript` | 0 | No manuscript |
| `"RI-Mark" "Li Li" watermarking` | 0 | Publisher preview |
| `"Bobiao Guo" watermarking publications` | 0 | DBLP bibliography |
| `"RI-Mark" watermarking "Shanghai"` | 0 | Publisher preview |
| `"Bobiao Guo" "Ping" Hohai` | 0 | No new manuscript route |
| `"Chengming Zhao" "watermarking" author` | 0 | No new manuscript route |
| `"Robust Reversible Watermarking" "Invisible" site:edu.cn` | 0 | No new manuscript route |
| `"Ping Ping" Hohai homepage publications watermarking` | 0 | perfectpicture.top author homepage |
| `"Fan Liu" Hohai "Robust Reversible"` | 0 | No new manuscript route |
| `"Li Li" "Guorui Feng" homepage publications` | 0 | Bibliographic listings only |
| `"Chengming Zhao" "RI-Mark" -site:researchgate.net -site:sciencedirect.com` | 0 | No new manuscript route |
| `"RI-Mark" site:shu.edu.cn` | 0 | No target manuscript |
| `"Chengming Zhao" watermark diffusion github` | 0 | No target manuscript |
| `"李莉" "冯国瑞" "主页"` | 0 | No retained target manuscript |
| `"平萍" "Robust Reversible"` | 0 | Unauthenticated off-domain mirror excluded; author route pursued independently |
| `"Guorui Feng" site:shu.edu.cn` | 0 | No target manuscript |
| `"Li Li" "watermarking" "homepage"` | 0 | Homonymous authors; not accepted as target identity |
| `"RI-Mark" "pdf"` | 0 | Unrelated vinyl products; none retained |
| `"Robust Reversible Watermarking With Invisible Distortion" manuscript OR filetype:pdf` | 0 | Bibliographic/abstract records only |
| `"Li Li" "llichn" publications` | 0 | Same-institution author evidence, no target manuscript |
| `"RI-Mark" "watermarking" manuscript` | 0 | Publisher preview |
| `"Robust Reversible Watermarking" "Invisible Distortion" pdf Guo Ping -site:researchgate.net -site:openalex.org -site:pubmed.ncbi.nlm.nih.gov` | 0 | DBLP and abstract mirrors; no manuscript |
| `"llichn" homepage` | 0 | Shanghai University Li Li faculty page |
| `"Guorui Feng" "homepage"` | 0 | Homonyms and other publications; none used as paper evidence |
| `"Chengming Zhao" "132903"` | 0 | Publisher/DBLP identity only |
| `"Robust Reversible Watermarking" site:arxiv.org` | 0 | Other RRW papers, not the target |
| `"RI-Mark" "watermarking" site:arxiv.org` | 0 | No target preprint |
| `"RI-Mark" "watermarking" site:github.com` | 0 | No target manuscript |
| `"Robust Reversible Watermarking" site:github.com/Hohai-PingPing` | 0 | Other RRW repositories, no target manuscript |

## Direct primary and bibliographic routes

- Crossref exact records `https://api.crossref.org/works/10.1109/TIP.2025.3613958` and `https://api.crossref.org/works/10.1016/j.eswa.2026.132903`: PowerShell `Invoke-RestMethod`, both successful; identity fields inspected. TIP's similarity-checking staging link was not used as a public access route. RI-Mark's text-mining link was inspected once at `https://api.elsevier.com/content/article/PII:S0957417426018154?httpAccept=text/xml`; HTTP 429, no full text.
- IEEE `https://ieeexplore.ieee.org/document/11185321/`: web produced near-empty content; ordinary PowerShell request returned HTTP 202 and zero-length content. IEEE stamp `https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11185321`: first ordinary request returned HTTP 200 HTML; one follow-up timed out; subsequent request supplied article metadata/abstract, which was extracted without executing page JavaScript. `isOpenAccess` is false; the PDF link points back to stamp. No PDF was received. Repeated requests were limited to diagnosing the initially ambiguous HTML response, not defeating access controls.
- PubMed `https://pubmed.ncbi.nlm.nih.gov/41032569/` and its `?format=pubmed` variant: near-empty response/error in this pass; prior abstract access remains documented in access-refresh. Primary IEEE abstract was subsequently inspected directly.
- ScienceDirect full and `/abs/` PII URLs: direct web open returned 403; indexed publisher content showed abstract, highlights and introduction/preview. No full method/evaluation was read. Preview retrieval is not a V2 upgrade.
- Personal `https://perfectpicture.top/`: opened with web and PowerShell; exact title listed, all anchor destinations inspected, no paper download. Followed `https://jszy.hhu.edu.cn/pp100/` (institutional profile) and `https://github.com/Hohai-PingPing` (public account). No linked images were fetched.
- GitHub API `https://api.github.com/users/Hohai-PingPing/repos?per_page=100`: eight public repository names/descriptions read. `https://api.github.com/repos/Hohai-PingPing/Hohai-PingPing.github.io/git/trees/main?recursive=1`: nontruncated path listing, no PDF path; README paths only among PDF/README/watermark/VAE/reversible search terms. `https://api.github.com/repos/Hohai-PingPing/C/git/trees/main?recursive=1`: HTTP 409. No code files or repository archives acquired.
- DBLP `https://dblp.org/pid/367/8994.html`, `https://dblp.org/pid/149/5851.html`, `https://dblp.org/pid/53/2189-103.html`, and `https://dblp.org/pid/438/6010.html`: bibliographies inspected for exact target entries and author routes. Direct Guo record open initially failed; the bibliography displayed the exact identity. DBLP's RI-Mark Unpaywall link `https://unpaywall.org/10.1016%2FJ.ESWA.2026.132903` redirected to inaccessible oadoi.org; no OA location obtained.
- Semantic Scholar exact DOI API, fields `title,authors,openAccessPdf,url,externalIds`: TIP HTTP 429; RI-Mark successful with empty PDF URL, status/license null. No inference of absence from TIP's rate limit.
- `https://scie-ie.shu.edu.cn/info/1078/1185.htm`: Shanghai University Li Li faculty biography/publication list read; no RI-Mark manuscript route. Unrelated Li Li and Guorui Feng homonyms were excluded.

No credentials, private access, paid route, author contact, shadow library, or paywall bypass was used. No full-text artifact was retained. The bibliographic and access statements in this folder are paraphrases/selected factual fields, not a copy of either paper.

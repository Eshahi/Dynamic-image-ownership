# Bounded access search log

Date: 2026-10-19. Engine: web.run; ordinary unauthenticated PowerShell HTTP requests for metadata and public article routes. Searches are not a systematic review. Zero readable target manuscripts were retained. Earlier access-refresh and C4 gap/search logs were read first. Primary routes were prioritized; unsupported third-party delivery services were not used.

## Queries issued

| Exact query | Useful route or outcome |
|---|---|
| `"ConZWNet" "Hongxin" university` | Author repository; no new manuscript |
| `"Rad-Mark" "Dakai" university` | Publisher author biographies suggest Tsinghua institutional search |
| `"Pseudo Zero-watermarking" "Thanh" pdf` | Distinct EAI 2021 chapter; author publication listing |
| `"ConZWNet" "pdf" -site:sciencedirect.com -site:researchgate.net` | Author repository; no paper PDF |
| `"ConZWNet" site:edu.cn` | No retained original manuscript |
| `"Deyu Tong" watermarking university` | Institutional affiliation and ORCID; no target manuscript |
| `"Rad-Mark" site:tsinghua.edu.cn` | No retained original manuscript |
| `"Dakai Zhai" watermarking github` | Author index; no manuscript |
| `"ConZWNet" site:nufe.edu.cn` | No retained original manuscript |
| `"Rad-Mark" "清华"` | No retained lawful primary manuscript route |
| `"Rad-Mark" "Hu" manuscript repository` | Publisher preview and author index; no manuscript |
| `"Pseudo Zero-watermarking Technique" site:lqdtu.edu.vn` | No retained original manuscript |
| `"ConZWNet" "佟"` | No retained original manuscript |
| `"Reliable adversarial zero-watermarking" manuscript` | Publisher snippets, not a complete manuscript |
| `"12079-9" "pdf" -site:researchgate.net -site:link.springer.com` | Mostly unrelated results; no manuscript |
| `"ConZWNet" "accepted" manuscript` | No retained original manuscript |
| `"Rad-Mark" site:arxiv.org` | No retained original manuscript |
| `"Pseudo Zero-watermarking Technique" manuscript` | ResearchGate publication preview |
| `"ConZWNet" site:alchemylab.cn` | No retained original manuscript |
| `"Ta Minh Thanh" "website"` | No authenticated manuscript homepage located |
| `"ConZWNet" "S2214212625001760" pdf` | Author repository, no manuscript |
| `"Rad-Mark" site:github.io` | Unrelated noise; no manuscript |
| `"ConZWNet" "full text"` | Publisher/ResearchGate request-copy page |
| `"Pseudo Zero-watermarking" "s11042-022-12079-9.pdf"` | No retained original manuscript |
| `"Rad-Mark" "129970" repository` | Publisher and bibliographic indexes only |
| `"Ta Minh Thanh" watermarking homepage` | Author ResearchGate profile, inspected for target link |
| `"ConZWNet" site:zenodo.org` | No retained original manuscript |
| `"Rad-Mark" site:tsinghua.edu.cn filetype:pdf` | No retained original manuscript |
| `"s11042-022-12079-9" site:edu.vn` | No target institutional manuscript; unrelated institution result discarded |
| `"ConZWNet" site:osf.io` | No retained original manuscript |

## Direct retrievals and decision points

- ConZWNet: `https://www.sciencedirect.com/science/article/pii/S2214212625001760`, `/science/article/abs/pii/S2214212625001760`, and `/science/article/pii/S2214212625001760/pdfft` returned 403 through web; ordinary HTTP PDF-route request also returned 403.
- Rad-Mark: `https://www.sciencedirect.com/science/article/pii/S0925231225006423` and `/science/article/abs/pii/S0925231225006423` returned 403 through web. Indexed publisher section snippets are not complete methods/evaluation.
- `https://github.com/hanhongxin1028` opened. Its linked `https://www.alchemylab.cn` did not load. ORCID `0000-0002-1009-750X` supplied no manuscript; `0009-0001-7231-0417` failed to load. No code or repository archive downloaded.
- Crossref REST `https://api.crossref.org/works/{doi}` successfully supplied both Elsevier paper identities and public text-mining links. The Pseudo DOI lookup timed out; publisher page already verified its identity.
- Crossref-provided `https://api.elsevier.com/content/article/PII:S2214212625001760?httpAccept=text/plain` and corresponding Rad-Mark PII were unavailable in web; ordinary HTTP gave 400. These are failed metadata-provided routes, not evidence of closed access.
- Canonical API route `https://api.elsevier.com/content/article/pii/S2214212625001760` with `Accept: text/xml` returned HTTP 200 but only 1,881 characters of core metadata, no full paper. Corresponding Rad-Mark route returned 429; no repeated rate-limit probing.
- Semantic Scholar `/graph/v1/paper/DOI:{doi}?fields=title,authors,year,externalIds,openAccessPdf,url`: ConZWNet returned DOI-only OA record; Pseudo returned empty OA URL; Rad-Mark timed out. These are locator records, not manuscripts.
- OpenAlex `https://api.openalex.org/works/https://doi.org/10.1016/j.jisa.2025.104139?select=id,doi,title,open_access,best_oa_location,locations` succeeded after a first unfiltered response hit a local JSON case-key parsing error. It returned only the DOI location and no PDF URL. The retry changed requested fields to resolve a local parser issue; it was not an access-control workaround.
- Springer `https://link.springer.com/article/10.1007/s11042-022-12079-9` opened: title/authors/volume/pages/date, abstract, subscription notice; SharedIt link unavailable. No linked figures opened.
- EUDL `https://eudl.eu/doi/10.1007/978-3-030-77424-0_36` opened: different title/authors/DOI and account-required download. No account or download action taken.
- `https://www.researchgate.net/profile/Ta-Thanh` opened; target listed as full-text available. Clicking its target publication `https://www.researchgate.net/publication/358020398_Pseudo_Zero-watermarking_Technique_based_on_Non-blind_Watermarking_and_VSS` eventually opened only publisher preview: first page, abstract, opening introduction, then citations/references. Earlier direct opening failed, and ordinary HTTP returned 403. No request-copy action taken, no figures opened.
- Direct DBLP `https://dblp.org/rec/journals/mta/ThanhD22` failed in web. No reliance placed on the search engine's generic unpaywalled-version UI label.
- Incidental 2026 publisher route `https://www.sciencedirect.com/science/article/abs/pii/S0925231226026834` failed; kept only as unverified lead.

## Stop rationale

The bounded search traversed publisher, public metadata API, author profile, institutional-domain and repository-domain routes without finding a complete target manuscript. The three papers remain V1. No assertion of globally unavailable full text or absent prior art follows from this result.

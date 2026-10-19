# Access-refresh search log

Date: 2026-10-18. Engine: `web.run`, unless specified. Useful hits below count retained relevant access/metadata routes, not independent papers or newly discovered manuscripts. Queries without a retained accessible primary route count zero, even when secondary search results appeared. This was a bounded access refresh, not a comprehensive systematic search.

| Query | Useful retained hits | Outcome |
|---|---:|---|
| `"Robust Reversible Watermarking With Invisible Distortion Against VAE Watermark Removal"` | 1 | PubMed abstract |
| `"ConZWNet"` | 2 | Publisher and author validation repository |
| `"RI-Mark" watermarking` | 1 | Publisher preview |
| `"Rad-Mark" watermarking` | 1 | Publisher preview |
| `"Robust Reversible Watermarking" "Guo" "2025" pdf` | 1 | Abstract route; no manuscript |
| `"ZWNet" "435" pdf` | 1 | Publisher identity; access errors |
| `"RI-Mark" "Zhao" watermarking github arxiv` | 0 | No accessible manuscript |
| `"FaceSigns" "3640466" pdf` | 1 | ACM identity; final access denied |
| `"ZWNet" "Li" watermarking` | 1 | Full publisher-formatted PDF mirror found |
| `"Rad-Mark" "github"` | 0 | No usable author manuscript |
| `"TrustMark" "ICCV 2025" pdf` | 2 | CVF final and Surrey accepted-manuscript record |
| `"FaceSigns" "Media Authentication" pdf Neekhara` | 2 | Author page and old arXiv preprint |
| `"Robust Reversible" "Bobiao" github` | 0 | No accessible manuscript |
| `"3613958" pdf` | 0 | Unrelated noise; no usable manuscript |
| `"ConZWNet" arxiv` | 0 | No original manuscript located |
| `"Rad-Mark" arxiv` | 0 | No original manuscript located |
| `"TrustMark" "Bui-ICCV-2025" pdf` | 1 | Surrey record |
| `"FaceSigns" "3640466" site:ucsd.edu` | 0 | No accessible final paper |
| `"Guo" "VAE Watermark Removal" arxiv` | 0 | No manuscript located |
| `"Rad-Mark" "Kun Hu" pdf` | 0 | No accessible manuscript |
| `"FaceSigns" "pdf" "2024"` | 1 | Author/preprint route only |
| `"TrustMark: Robust" filetype:pdf` | 0 | No additional useful route |
| `"ConZWNet" "Tong" manuscript` | 1 | New author implementation repository |
| `"Robust Reversible Watermarking With Invisible Distortion" -site:researchgate.net -site:openalex.org -site:eurekamag.com` | 1 | PubMed; no manuscript |
| `"RI-Mark" "Chengming Zhao" pdf arxiv github` | 0 | No accessible manuscript |
| `"ConZWNet" filetype:pdf` | 0 | Secondary Rel-Zero citation is not the original paper |
| `"Rad-Mark" "Zhai" filetype:pdf` | 0 | No accessible manuscript |
| `"TrustMark" "2025" site:openaccess.thecvf.com` | 1 | Final CVF metadata |

## Direct retrievals and inspection

- ZWNet: publisher HTML/PDF failed with 403/429. [Semantic Scholar PDF mirror](https://pdfs.semanticscholar.org/1b6b/7141ad46619282533aba62cfdfbd7de7d583.pdf) supplied the journal-formatted paper. Read Sections 3–4, pp.6–15, including method, split/stopping protocol and Tables 2–4. A local paper copy and SHA-256 are recorded in its card.
- TrustMark: web access to CVF returned 403; an ordinary `curl.exe` request to the same public CVF PDF succeeded. Surrey's record verified title, authors, venue and DOI; its PDF route was unreliable. Read the cached CVF paper's methods/evaluation through installed Node/pdfjs text extraction, pp.18629–18637, including Tables 1–4 and practical limitations. No package was installed and no source code was acquired. The paper identifies its CVF copy as the accepted version, differing from the final published version only in the watermark.
- FaceSigns: final DOI/full/PDF retrieval failed (403), including ordinary curl. The author's publication link resolves to arXiv2204.01960; its history identifies only v1 (2022). The final 2024 evaluation was not read. Indexed final excerpts are not counted as inspection.
- ConZWNet: opened author repository READMEs at `github.com/hanhongxin1028/ConZWNet` and `github.com/hanhongxin1028/ConZWNetwork_Valid`. The newer README links the publisher article; no accessible manuscript was found. Repository results are not used to upgrade original paper verification.
- Guo TIP: PubMed opened; an apparent lab-site hit could not be authenticated or read. No author manuscript was retained.
- Publisher previews for ConZWNet, Rad-Mark and RI-Mark were opened; no full paper was obtained.
- Crossref REST `/works/{doi}`: Guo TIP, ConZWNet, Rad-Mark, RI-Mark and FaceSigns records opened successfully; useful metadata records = 5. These are direct DOI lookups, not additional discovery queries. Four journal DOI records were checked twice while preparing bibliography metadata.
- OpenAlex direct DOI lookups: Guo TIP, ConZWNet, Rad-Mark, RI-Mark. Rad-Mark and RI-Mark explicitly reported closed access/no repository full text. The other responses did not establish a usable manuscript route; no absence conclusion was inferred from them.

No public communication, paid access, credentials, shadow library, or paywall bypass was used. Only two paper PDFs were retained in the dedicated cache, below 100 MB. Cards and matrix state the precise version inspected; cached full texts are not part of the dossier commit surface.

WP9 parent retry, 2026-10-18: exact searches `"ConZWNet" filetype:pdf`, `"Rad-Mark" "watermarking" filetype:pdf`, `"Robust Reversible" "Guo" "2025" "autoencoder" watermarking`, and `"10.1109/TIP.2025.3613958" pdf` produced no new accessible original full text (zero useful manuscript hits). Rad-Mark's publisher preview exposes short method/experiment excerpts but not the complete methods and evaluation; it remains V1. Rel-Zero's supplemental citation to ConZWNet is not the original source. No access level was upgraded and no paper was downloaded in this retry.

# Search and access log

Date: 2026-10-18 PDT / 2026-10-19 UTC. Engine: `web.run` live search. Counts below are **useful retained leads in this bounded pass**, not search-engine result totals. Repeated hits count as leads for the query but are not new papers. Secondary hits were used for discovery only; paper claims and journal metadata rely on primary pages. No assertion of exhaustive coverage is made.

| Query | Useful hits | Disposition |
|---|---:|---|
| `"Robust-Wide" watermarking multimedia` | 1 | Primary author/project source identifies ECCV2024: exclude from journal set. |
| `"3543079" watermarking` | 1 | TMM2025 feature-fusion journal lead; no accessible primary full method/evaluation. |
| `image watermarking "2025" "Transactions on Multimedia" arxiv` | 1 | MarkPlugger lead. |
| `watermarking "Transactions on Multimedia" "arxiv.org" "2025" -"video" -wide -survey` | 1 | MarkPlugger. |
| `watermarking "Transactions on Information Forensics" "2024" "arxiv.org" -DualDefense -FaceSigns` | 0 | No retained additional source. |
| `"Robust Watermarking Based on Multi-layer Watermark Feature Fusion" pdf` | 1 | Publisher metadata; secondary full-text mirrors not used. |
| `watermarking "Pattern Recognition" "2025" arxiv` | 0 | No retained source. |
| `watermarking "2024" "TIFS" "arxiv"` | 0 | No additional retained source. |
| `watermarking "2025" "TMM" "arxiv"` | 1 | MarkPlugger. |
| `"De-END" watermarking journal` | 0 | No retained recent journal source. |
| `"SepMark" journal` | 0 | No retained recent journal source. |
| `"watermarking" "2025" "TIFS" "image" arxiv -language -point -model` | 1 | MantleMark lead. |
| `"watermarking" "2024" "TMM" image arxiv -video -survey -federated` | 1 | Two-stage removal lead. |
| `"watermarking" "2025" "TCSVT" arxiv -video -neuralnetwork` | 1 | Reversible Unlearnable Examples lead. |
| `"MantleMark" arxiv` | 1 | University manuscript and journal record. |
| `"MarkPlugger" "TMM"` | 1 | Journal-linked author manuscript and metadata. |
| `"Two-Stage Watermark Removal" "BSD"` | 0 | No accessible evaluation retained. |
| `"Two-Stage Watermark Removal" "512"` | 0 | No accessible evaluation retained. |
| `"Two-Stage Watermark Removal" pdf -scispace -researchgate -eurekamag` | 1 | Author-university final PDF link; fetch failed. |
| `site:fst.um.edu.mo/personal/wp-content/uploads/2024/04/TwoStageWatermarkRemoval.pdf "training"` | 0 | No full evaluation accessible. |
| `site:fst.um.edu.mo/personal/wp-content/uploads/2024/04/TwoStageWatermarkRemoval.pdf "1000"` | 0 | Same. |
| `site:fst.um.edu.mo/personal/wp-content/uploads/2024/04/TwoStageWatermarkRemoval.pdf "datasets"` | 0 | Same. |
| `site:fst.um.edu.mo/personal/wp-content/uploads/2024/04/TwoStageWatermarkRemoval.pdf "seconds"` | 0 | Same. |
| `"watermarking" "arxiv" "Computers & Security" "2025"` | 0 | No retained source. |
| `"watermarking" "arxiv" "Signal Processing" "2024" journal` | 0 | No retained source. |
| `"watermarking" "arxiv" "TIFS" "ZoDiac"` | 0 | No retained recent journal source. |
| `"watermarking" "arxiv" "TIP" "2025" -language -model` | 0 | No additional retained source. |
| `"image watermarking" "2024" "Pattern Recognition" pdf` | 0 | No retained V2 source. |
| `"image watermarking" "2025" "Computers" "Security" pdf arxiv` | 0 | No retained V2 source. |
| `"image watermarking" "2024" "Signal Processing" "pdf" -symposium -icassp -circuits -conference -reviews -survey` | 0 | No retained V2 source. |
| `"Reversible Unlearnable Examples" arxiv` | 1 | Author-uploaded August2026 full HTML. |
| `"screen-shooting" "Grayscale Deviation" arxiv` | 0 | Journal lead not pursued after three full reads were available. |
| `"Two-Stage Watermark Removal Framework" "experiments"` | 1 | Primary search extract includes method only; not promoted to V2. |
| `"Reversible Unlearnable Examples" "3619199"` | 2 | IEEE and author-institution metadata; same work. |
| `"Reversible Unlearnable Examples" "3975"` | 2 | Confirms journal volume/pages via IEEE/institution, no new paper. |
| `"MarkPlugger" "6211" "IEEE"` | 1 | DBLP/JST corroborate volume27/pages6211–6220; no publisher full text obtained. |
| `"MantleMark" "234126" accepted` | 0 | Repository version designation remains unverified. |

## Primary access record

- [MarkPlugger arXiv metadata](https://arxiv.org/abs/2404.05607) and [v2 HTML](https://arxiv.org/html/2404.05607v2): accessible. Read IV and V, particularly V-A/B/C/E/H and Tables I–III. [DOI](https://doi.org/10.1109/TMM.2025.3565960) resolves to IEEE document 10980457, but publisher full text was not accessible in this pass. Author page [Lanjun Wang](https://wanglanjun-academic.github.io/) also lists TMM2025. Journal DOI relation explicit on arXiv. Bibliographic indexing supplements [DBLP's TMM27 record](https://dblp.org/db/journals/tmm/tmm27.html) and [JST](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202502220982053405) corroborate volume/pages; these are metadata corroboration, not sources for methodological claims.
- [MantleMark university-hosted PDF](https://eprints.lancs.ac.uk/id/eprint/234126/1/111.pdf): intermittently accessible through web; method IV and evaluation V actually read. [CityU author-affiliated record](https://scholars.cityu.edu.hk/en/publications/mantlemark-migrating-watermarks-from-multi-view-images-to-radianc/) verifies journal DOI, authors, year, pages and first-online date. Lancaster landing page failed to fetch; consequently exact repository version designation is unverified. PDF header alone is not a final-version certification.
- [Reversible author manuscript](https://arxiv.org/html/2608.06211v1) and [metadata](https://arxiv.org/abs/2608.06211): accessible. Read III and IV including robustness, ablations and repeated-classifier evaluations. [IEEE journal metadata](https://doi.org/10.1109/tcsvt.2025.3619199) was returned by primary publisher search; direct open was intermittent. [Macao Polytechnic University record](https://research.mpu.edu.mo/en/publications/reversible-unlearnable-examples-toward-the-copyright-protection-i/) independently verifies the same authors/title, TCSVT36(3), pages3975–3988 and DOI. Manuscript relation supported by all authors/abstract/mechanism, but arXiv does not explicitly assert the journal DOI. Keep that caveat when citing evaluation numbers.
- [Two-stage removal author publication list](https://www.fst.um.edu.mo/personal/yicongzhou/publication/) identifies TMM26, 7687–7699(2024), DOI10.1109/TMM.2024.3370380. [Author-hosted PDF](https://www.fst.um.edu.mo/personal/wp-content/uploads/2024/04/TwoStageWatermarkRemoval.pdf) repeatedly timed out; a curl request returned a 311-byte error HTML document, not a paper. That failed file was removed. Search extracts exposed known-message attacker assumptions and part of the method, but no full evaluation read: **excluded from V2 synthesis**, no card/bib entry.
- [Feature-fusion publisher page](https://ieeexplore.ieee.org/document/10891427/): DOI10.1109/TMM.2025.3543079 verified as a discovery lead. No primary full method/evaluation inspected: **excluded**, no guessed author list or claims.

## Execution boundary

Only paper reading and dossier text/CSV/Bib writing occurred. No experiments, package installs, scientific interpreter, model/code/data/image downloads or repository execution. No retained paper cache download was needed. No commits or shared-state edits were made by this child agent.

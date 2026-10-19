# C1 search and inspection log

Researcher: Codex C1 child agent. Date: 2026-10-18 (America/Los_Angeles; environment offset -08:00). Scope: post-hoc existing-photo watermarking, VAE/encoder-gradient novelty, and explicit generation-time boundaries. All searches used `web.run`; primary arXiv, CVF, OpenReview, official repositories and institutional manuscripts were preferred. No code, model, dataset or image was downloaded or executed.

## Inventory first

Read `02-literature/existing-inventory.md` before new searching. Used retained inspection records to identify refresh targets; did not count those records as new papers. Read authoritative MAIN STATE once at start and once after context compaction, and BRIEF sections 1, 2 and WP2. Applied thesis-literature-synthesis provenance conventions. No experiment workflow was invoked.

## Search queries

“Useful hits” counts distinct useful primary records returned for that query, not search-engine result totals or additional unique papers. A paper page and its official repository can both be useful records. Counts are conservative triage observations; they do not constitute V2 verification.

| Date | Engine | Exact query | Useful hits | Result / use |
|---|---|---|---:|---|
| 2026-10-18 | web.run | VINE W-Bench watermark diffusion image editing paper | 2 | arXiv and official VINE repository |
| 2026-10-18 | web.run | TrustMark watermark arxiv | 2 | arXiv and official Adobe repository |
| 2026-10-18 | web.run | RoSteALS watermark paper | 1 | arXiv seed |
| 2026-10-18 | web.run | PhaseMark GROW image watermark | 2 | PhaseMark and GROW primary leads |
| 2026-10-18 | web.run | "TrustMark: Robust" ICCV 2025 pdf | 2 | CVF and Surrey accepted-manuscript record |
| 2026-10-18 | web.run | "RoSteALS" paper arxiv | 1 | arXiv primary |
| 2026-10-18 | web.run | "GROW" "CVPR 2026" watermark | 2 | CVF and official project/repository |
| 2026-10-18 | web.run | "Robust Watermarking Using Generative" 2410.18775 | 1 | VINE primary/version |
| 2026-10-18 | web.run | PixelSeal watermark paper arxiv | 2 | Official Video Seal repository and author paper |
| 2026-10-18 | web.run | "PhotoGuard" "2302.06588" paper | 1 | Primary arXiv lead; secondary summaries not evidence |
| 2026-10-18 | web.run | "post-hoc" watermark "encoder" "2026" VAE | 3 | 2610.04151, 2609.16832, 2609.25972 leads; no V2 credit |
| 2026-10-18 | web.run | "RoSteALS" CVPR 2023 pdf | 2 | CVF and author PDF |
| 2026-10-18 | web.run | "TrustMark" "ICCV 2025" "4.1" "bit" | 0 | No additional useful primary record |
| 2026-10-18 | web.run | "Watermark Anything" "ICLR 2025" | 1 | Official ICLR paper |
| 2026-10-18 | web.run | "InvisMark" "CVPR" 2025 | 0 | Final venue not verified; retain preprint |
| 2026-10-18 | web.run | "FreqMark" "NeurIPS" 2024 | 2 | Official proceedings metadata and PDF |

## Direct retrieval and version checks

Direct URL opens are retrievals, not unlogged search queries. All 14 primary URLs and inspected locators are recorded in `matrix.csv`; cards include the retained source SHA-256. arXiv abstract-page submission histories were checked for VINE v2, TrustMark v1, RoSteALS v1, InvisMark v2, ZoDiac v2, FreqMark v1, WAM v2, APT v1, PhaseMark v1, PhotoGuard v1, DiffMark v2 and Pixel Seal v1. WAM, DiffMark and FreqMark histories were checked again before writing.

- Initial VINE v3 retrieval failed; latest identified version is v2. PhotoGuard v2/v3 and TrustMark v2 guesses failed; v1 histories were used. Failed guessed URLs are not evidence.
- DiffMark v1 was read first; latest v2 (2026-06-02) was then downloaded and method/experiments read again. Current arXiv comment says TAIGR workshop at ICML 2026, not main ICML. Its four-author list agrees with the HTML title block; the generated “and 2 other authors” sentence is inconsistent.
- GROW's retained CVPR 2026 final PDF/text was read at Sections 3–5.5 and Tables 1–3; official CVF metadata refreshed. No associated code was opened or executed.
- StegaStamp retains the 2026-10-03 primary inspection in `research/literature/m1-primary-extension/cards-additional.md`, PDF pp. 3–7, Sections 3–5, Tables 1–2. Hash checked now; no current full reading claimed.
- TrustMark CVF final PDF returned access errors. Surrey's accepted-manuscript PDF opened once, exposing introduction and method; subsequent requests for experimental pages timed out. Full arXiv v1 method/experiments were read. The final DOI/title/venue are verified by [Surrey](https://openresearch.surrey.ac.uk/esploro/outputs/conferencePaper/TrustMark-Robust-Watermarking-and-Watermark-Removal/991164459902346); final experimental results are not silently imported.
- FreqMark venue/DOI verified using [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/cbc4912b67d57e3932f56f3fa99faab3-Abstract.html). RoSteALS CVPRW DOI cross-checked against bibliographic/CVF metadata; other unknown publication DOI fields omitted.

## Cache and access

Only paper HTML was newly downloaded, into MAIN `.thesis-build/q1-research-20261018/cache/C1/`. Files: vine, trustmark, rosteals, invis, zodiac, freqmark, wam, apt, phase, photoguard, diffmark (superseded v1), diffmark-v2, pixelseal. Each current source file is hashed in its card. Existing GROW/StegaStamp PDFs were reused in place. Cached source text was inspected using PowerShell text extraction; no Python/science interpreter, PDF rasterization, image inspection, model loading or experiments occurred. Copyright/licensing remains source-specific; no redistribution permission is inferred.

## Leads and limits

- [Watermarks and Fingerprints as Soft Bindings for Content Provenance, 2610.04151](https://arxiv.org/abs/2610.04151): October 2026 primary abstract lead routed to C5/C6; not C1 V2.
- [What Breaks Local Watermarks?, 2609.16832](https://arxiv.org/abs/2609.16832): routed to attacks/localization cluster; not C1 V2.
- arXiv 2609.25972 (NAWE lead): not method/experiment inspected; excluded from V2 synthesis.
- A search result advertising a 2026 IEEE Access “rank-ratio bound” with a placeholder-looking DOI was not trusted or used.
- RAIN/MetaSeal remain cross-cluster boundary leads; no C1 full-card count.
- No quantitative ranking across papers. No evidence here changes the thesis's E2 failure or establishes cryptographic ownership.


Parent continuation,2026-10-18: discovered SpecGuard2510.07302v1 and SimuFreeMark2511.11295v1 through journal-oriented searches; read full methods and evaluation. Added separate cards and metadata rows. SimuFreeMark directly performs VAE latent insertion for existing photographs with a learned image extractor; bit recovery is not fixed-FPR attribution. SpecGuard supplies spectral post-hoc regeneration comparisons with unclear main test denominators. Both are V2, with version qualifications in cards.

Parent resolved lead 2026-10-18: NAWE2609.25972v1 opened at abstract/history and full Sections 3-4. Added Chaban2026NAWE V2; no diffusion-regeneration or active-forgery evaluation established. MetaSeal and RAIN refreshed to current v2 in C3 and C7, respectively; older unresolved-lead notes above are historical.

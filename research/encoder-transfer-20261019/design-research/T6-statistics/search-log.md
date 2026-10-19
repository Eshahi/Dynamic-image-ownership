# T6 search and inspection log

2026-10-19. All searches used the live web search tool. No model/code/data downloads; cached statistical papers and documentation only. Source files and SHA-256 hashes are recorded in `source-manifest.json` under MAIN `.thesis-build/q1-research-20261018/cache/T6/`, outside git.

| Action | Exact query or URL | Outcome and inspected depth |
|---|---|---|
| Search | `site.itl.nist.gov binomial proportion confidence interval Clopper Pearson` | NIST exact-binomial tail inversion retained. |
| Search | `site.jstor.org Holm 1979 simple sequentially rejective multiple test procedure` | Original located, full text unavailable. Official implementation documentation used instead. |
| Search | `beta binomial intracluster correlation cluster sample binary data exact binomial source clustering paper` | Ahmed–Shoukri (2010) primary PDF located. |
| Search | `2025 2026 binomial confidence interval clustered binary exact source repeated measures sample size` | 2025 randomized-experiment and differential-privacy leads screened; no applicable verified 2026 replacement. |
| Open | https://jds-online.org/journal/JDS/article/912/file/pdf | Read model section 2 and simulation section 4, PDF pp.2–7. Formula/ICC relation retained, estimator not used. Actual PDF cached. |
| Open | https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm | Full Description and syntax/examples inspected. Actual HTML cached. |
| Open | https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html | Details, references and example inspected. Primary software documentation retained and cached. |
| Open | https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf | Existing dossier V2 card reused; PDF opened, introductory clustering motivation inspected; later line-specific web request timed out. Actual author PDF downloaded successfully to cache. |
| Open | https://web.pdx.edu/~ihd/stat563.S17/brown.pdf | Browser fetch failed. Existing dossier V2 Brown–Cai–DasGupta card reused, no new full-text inspection claimed. |
| Open | https://www.jstor.org/stable/4615733 | No usable original full text; not promoted to V2. |
| Open | https://pmc.ncbi.nlm.nih.gov/articles/PMC3040008/ | Captcha; clustered sign sample-size paper not relied on. |
| Open | https://www.sciencedirect.com/science/article/pii/S0304407625001101 | 2025 Aronow/Chang/Lopatto lead, 403 on full open. Search-rendered section snippets not promoted to V2; randomized treatment setting unlike this design. |
| Screen | https://arxiv.org/abs/2511.02227 | Search result only, differential privacy outside scope; not cited as evidence. |

Local sources: authoritative MAIN STATE read once; worktree BRIEF read; existing C8-theory cards `brown2001binomial.md` and `cameron2015cluster.md`, and `25-statistical-design/search-log.md` inspected. No AGENTS re-read. Existing runner read only. Mathematical arithmetic used only Python stdlib; no synthetic outcome simulation. The single calculator command is documented in `tools/plan.py`; its output is `planning-table.json`.

# T6 Stage1b search and inspection log

Completed 2026-10-20. Sixteen successful discovery query strings across three categories (5 arXiv API, 8 OpenAlex, 3 web), conservatively ten substantive intents after merging overlaps; direct source retrievals and repeated searches are not added to this count. Exact API response bytes, URLs and SHA-256 receipts are in the manifests. The three web queries share a single cached service response, clearly identified rather than presented as separate receipts.

| # | Category | Exact query |
|---|---|---|
| 1 | arxivAPI | `all:"beta binomial" AND all:"correlation"` |
| 2 | arxivAPI | `all:"missing" AND all:"cluster" AND submittedDate:[202501010000 TO 202610202359]` |
| 3 | arxivAPI | `all:"binomial" AND all:"confidence" AND all:"exact"` |
| 4 | OpenAlex | `clustered binary outcomes missing data sensitivity analysis` |
| 5 | OpenAlex | `beta binomial intraclass correlation validation` |
| 6 | OpenAlex | `exact binomial confidence interval sample size` |
| 7 | OpenAlex | `benchmark machine learning correlated evaluation 2025 2026` |
| 8 | arxivAPI | `cat:stat.ME AND all:"missing" AND all:"binary" AND submittedDate:[202501010000 TO 202610202359]` |
| 9 | arxivAPI | `all:"majority" AND all:"correlation" AND cat:stat.ML` |
| 10 | web | `exact binomial confidence interval clustered data beta binomial missing data evaluation` |
| 11 | web | `Holm multiple testing exact McNemar official R binom.test` |
| 12 | web | `2025 2026 machine learning benchmark correlated evaluations missing data statistical uncertainty` |
| 13 | OpenAlex | `correlated paired binary outcomes joint probability superiority margin` |
| 14 | OpenAlex | `co primary efficacy safety endpoints joint probability dependence` |
| 15 | OpenAlex | `matching post treatment variable collider bias common support caliper` |
| 16 | OpenAlex | `computational experiments time budget informative censoring runtime algorithm benchmarking` |

Intent counts and 24 metadata-only lead screenings: `query-gap-audit.md` and `intent-gap-screening.json`. The four additional searches do not add scientific source credit. Historical 12-query records/bytes are preserved in MAIN cache.

## Selection and reading

Queries cover dependence/clustered binary outcomes, exact intervals, informative missingness, aggregate benchmark comparisons and multiple testing. Search results were discovery leads, not evidence by themselves. Eight papers received topic-specific method-and-evaluation reading and individual V2 cards. Five official references received method/examples/tests reading and are counted separately. See the source manifest for exact cached assets, hashes, licenses and original/final URLs. The dated card paragraphs identify the inspected sections and evaluations.

| Paper | Read and applied |
|---|---|
| Ahmed/Shoukri 2010 | Sections 2,4 and Table 1; beta mixture and invalid-fit simulation limits; rechecked, counted once. |
| Cameron/Miller 2015 | II,IV,VIII.A-B and Table 2; independent clusters and state-resampling evaluation; rechecked, counted once. |
| Thulin 2013/2014 | 2.1-2.3,3.1-3.3,4 and Figures 1-3; tail inversion and exact-versus-approximation numerical evaluation. |
| Hossain et al. 2016 | 3-4,5.1-5.3 and Table 2; missingness assumptions and four-scenario simulation. |
| Wang et al. 2026 | 2,3,5,6.1-6.2, Tables 1-3 and Figure 2; selection/missingness and finite-sample evaluation. |
| Elmore 2020 | 2.1-2.2 equations 1-3,3,4; higher moments and model comparison simulations/examples. |
| Longjohn et al. v2 2026 | 2.1-2.3,3.1-3.2 Tables 2-4; aggregate uncertainty and simulated VTAB illustration. |
| Singh 2026 | 2-5 and Appendices B-C; finite-rollout identification and calibration/certificate evaluation. |

Official references: NIST exact-tail inversion worked outputs; R binom.test Details and inheritance example; R p.adjust Details/n/NA examples; SciPy beta-binomial PMF and moment/frozen-distribution examples; statsmodels McNemar Notes plus pinned v0.14.4 test_mcnemar regression tests. Downloaded test text never executes. Raw GitHub fetches failed SSL; the rendered official test file was successfully cached/read instead.

## Exclusions and reuse boundaries

Other fetched leads (kim2017.html, matched2026.html, llm2025.html) are preserved in receipts but do not have V2 cards, do not count toward the paper floor, and support no synthesis claim. Search snippets, abstracts, OpenAlex metadata and arXiv feed abstracts do not support claims. Original Holm (1979) was not inspected in full and gets no paper-level credit; the official R implementation documentation is identified explicitly. Brown et al. is not silently reused as current V2 evidence. Ahmed and Cameron are retained only after topic-specific full-text rechecks. API metadata licenses do not imply a full-text license. Local caches with unclear permissions are not redistributable research artifacts.

## what we might still have missed

A search floor is not an exhaustive review. We may have missed late-2026 work not indexed by these services, dependence involving creator/content groups, partial exchangeability with negative pairwise correlations, arbitrary three-way cross-method dependence, or a missingness process triggered by a shared software/model failure. The grids do not estimate those processes. The current finite-exchangeable bounds cover feasible third moments for the specified nonnegative-ICC grid; route examples cover named laws, not all joint laws. No new source discovered through a snippet can remove these limits without full reading. The fixed development roster and one primary endpoint prevent a claim of representative population reliability even with exact arithmetic.

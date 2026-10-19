# Statistical-design source log

19 October 2026. Supplementary mathematical support for the future design, not additions to the 98-work image-watermark literature matrix or its V2 count. No package, data, image, code, or model was downloaded. Web-rendered paper text was inspected; no local paper cache addition was needed. The design author records its own exact searches in design-core.md; the table here records the parent searches and direct opens.

| Engine / action | Exact query or URL | Useful outcome / inspected depth |
|---|---|---|
| web search | `site.stat.ethz.ch R binom.test exact confidence interval Clopper Pearson` | One official R reference retained; primary documentation for the binomial contrast only. |
| web search | `site.stat.ethz.ch R Hypergeometric distribution phyper sampling without replacement` | One official R reference retained; finite-population distribution and CDF conventions. |
| web search | `site.itl.nist.gov binomial confidence interval one sided exact sample size` | One NIST exact-binomial reference retained; another handbook result was not needed. No secondary search result is evidence. |
| Direct open | https://stat.ethz.ch/R-manual/R-patched/library/stats/html/Hypergeometric.html | R stats 4.5.0 page as displayed: Details, probability mass, moments and lower/upper-tail definitions. Primary support for HG(N,D,n), not a claim that R was run. |
| Direct open | https://www.stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html | R stats 4.6.0 page as displayed: exact Bernoulli test and Clopper–Pearson coverage. This model is not selected for dependent image pairs. |
| Direct open | https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm | NIST Dataplot exact-binomial interval page, updated 2015-11-16: CDF inversion equations. Its example generation code was not executed. The prospective design uses probability-tail allocation, not a normal critical-value substitution. |
| Direct open | https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf | Refreshed introduction and start of Section II in the existing inspected Cameron–Miller source. Used only to motivate grouping; not a ready-made rare-event interval. Existing full card remains the literature record. |
| Direct open | https://arxiv.org/pdf/1507.08298v3 | Greene–Wellner, arXiv v3, 7 March 2016. Read Section 1, equation (1.2), and Section 2 opening (PDF pp. 1–3), including the stated convex-order/Chernoff transfer from sampling with replacement to without replacement. This bounded inspection supports the conservative planning argument, not a claim to have audited every proof. |

The hypergeometric interval is derived in the design from inversion of its exact finite-population tails. The numeric appendix evaluates a displayed KL expression on fixed planning constants; it generates no observations or random draws and makes no empirical power claim. Confidence coverage follows the sampling design, not evidence that creators discovered on these websites represent all Internet images.

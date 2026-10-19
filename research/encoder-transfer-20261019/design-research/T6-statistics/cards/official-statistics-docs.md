# Official statistical documentation — inspected primary guidance

## NIST exact-binomial reference

[NIST Dataplot EXACT BINOMIAL](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm). Accessed 2026-10-19. Read Description, tail equations and examples; cached HTML hash in manifest. The documentation describes upper/lower confidence limits through inversion of binomial CDF equations. We use the two-sided .025 tails and independently derive the one-sided zero-count bound 1-alpha^(1/n). This guidance assumes a binomial model and does not validate exchangeability or independence of image sources. This is primary implementation guidance, not a research paper with experimental sections.

## R stats p.adjust reference

[Official R p.adjust documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html), displayed stats 4.6.0. Accessed 2026-10-19. Read Details, references and examples; cached HTML hash in manifest. It documents Holm family-wise error control under arbitrary dependence among valid input p-values and handling of a family size larger than observed tests. Use here: Holm adjustment of three prespecified exploratory primary comparisons. It does not make non-random development selection or dependent source pairs valid. Original Holm full text was unavailable; no original-paper V2 assertion is made.

## Reused dossier evidence

Brown–Cai–DasGupta and Cameron–Miller retain their existing V2 cards in `research/q1-dossier-20261018/02-literature/C8-theory/cards/`; no duplicate cards or new V2-paper count. The Cameron author PDF is cached here for local provenance. Brown's mirror fetch failed during this refresh; its earlier card supports only the already documented binomial-coverage caveat, also independently supported by NIST's equations.

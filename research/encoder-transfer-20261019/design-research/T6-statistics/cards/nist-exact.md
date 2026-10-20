# NIST Dataplot exact-binomial documentation — V2 software reference

[Official method documentation](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm). Cache ID `nist-exact.html`; inspected 2026-10-20. Source is government-hosted documentation; specific redistribution terms were not established, so cache is local only.

Read Description, one-/two-sided syntax and sample program/output. The method inverts binomial CDF equations at the appropriate tail probability. Its examples illustrate application to binary data and grouped/subset inputs; they are worked documentation examples, not independent empirical validation or a research-paper evaluation.

Use: formula-level cross-check for our pure-stdlib inversion and zero-count endpoint identities. The local planning script checks every k at n=60/90/120 plus reflection and boundary identities. We do not run Dataplot. Documentation does not license treating 180 correlated seeds or 1,080 repeated negative calls as independent samples. The interval remains a model-based exploratory display for this deterministic cohort. Counted separately from research-paper V2 cards in the floor audit.

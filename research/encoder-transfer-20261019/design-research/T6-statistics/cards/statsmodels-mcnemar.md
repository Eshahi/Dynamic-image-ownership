# statsmodels McNemar — V2 software reference

[Official reference](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html) and [v0.14.4 official regression tests](https://github.com/statsmodels/statsmodels/blob/v0.14.4/statsmodels/stats/tests/test_contingency_tables.py). Cache ID `statsmodels-mcnemar.html`; exact test page inspected through GitHub, raw fetch failed and is logged. Documentation reuse license not verified; local cache only.

Read parameters/results/Notes and test_mcnemar in the pinned repository (GitHub rendered lines 1721-1743; cached as `statsmodels-tests-page.html`). The exact option uses binomial discordance counts; the repository checks the exact result against an R reference and separately checks corrected/uncorrected chi-square variants. These are software regression tests, not a new empirical watermark evaluation.

Use: source-paired wins/losses with ties excluded from the conditional test, retained in denominators and effect sizes. Our planning script checks six versus zero discordances and all ties. No statsmodels library runs and no downloaded tests execute. This reference does not justify ignoring cross-source dependence, rescue missing comparisons, or turn a routing margin into a noninferiority test.

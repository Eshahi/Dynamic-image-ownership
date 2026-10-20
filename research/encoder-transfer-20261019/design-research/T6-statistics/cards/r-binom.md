# R stats binom.test — V2 software reference

[Official R documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html). Cache ID `r-binom.html`; inspected 2026-10-20, rendered package version 4.6.0. Documentation reuse terms not separately verified; local cache only.

Read arguments, Details, returned values and the complete inheritance worked example (682 successes, 243 failures, null .75). Confidence limits follow Clopper-Pearson and need not be shortest. The page is primary implementation documentation; the example is not a simulation study or proof of validity under clustered sampling.

Use: verify exact-binomial terminology, the distinction between null test probability and confidence level, and explicit denominator reporting. No R process ran. For paired comparisons the null is .5 among discordances, not .5 across all sources. For this symmetric null, the doubled smaller tail agrees with the conditional exact sign calculation; this should not be generalized to all two-sided binomial tests with arbitrary null p. Paper-level evidence and exploratory-coverage limits are supplied separately.

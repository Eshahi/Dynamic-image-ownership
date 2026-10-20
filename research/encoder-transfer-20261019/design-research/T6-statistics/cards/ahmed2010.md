# Ahmed and Shoukri (2010) — V2

Marwa Ahmed and Mohamed Shoukri. *A Bayesian Estimator of the Intracluster Correlation Coefficient from Correlated Binary Responses*. Journal of Data Science 8, 127–137 (2010). [Primary PDF](https://jds-online.org/journal/JDS/article/912/file/pdf). Accessed 2026-10-19; cache hash in `../source-manifest.json`.

Inspected section 2 (beta-binomial model and ICC relation), section 4 and Table 1 (simulation evaluation), PDF pp.2–7. Conditional Bernoulli probabilities vary across clusters as Beta(a,b), producing beta-binomial counts and ICC 1/(1+a+b). The paper evaluates a Bayesian ICC estimator using 96 parameter combinations and 2,000 valid samples each. It reports degraded coverage at high ICC, and discards invalid fitted samples; this limits direct generalization of its favorable coverage claims.

Use here: only the probability model for explicitly hypothetical dependence sensitivity. We do not fit the estimator, adopt its prior, transfer its clinical sampling assumptions, or claim its evaluation establishes image-source ICCs. No watermark threat/payload is applicable.

Stage1b recheck, 2026-10-20: actually reopened PDF sections 2 and 4, pp.128-133, including all Table 1 rows and the invalid-sample replacement procedure. The simulation uses cluster size two; it does not validate three image seeds. Cache ID `ahmed2010.pdf`; license not established from inspected PDF, retained for local research only. This source counts once.

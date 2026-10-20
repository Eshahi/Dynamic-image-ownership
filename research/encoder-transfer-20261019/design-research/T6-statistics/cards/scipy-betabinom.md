# SciPy beta-binomial — V2 software reference

[Official SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.betabinom.html). Cache ID `scipy-beta.html`; inspected 2026-10-20. Documentation copyright is SciPy community; precise reuse terms not established from this page, local cache only.

Read Notes, support/shape conditions, PMF and full examples for moments, probability mass and frozen distributions. The distribution mixes a binomial success probability with Beta(a,b). Its examples demonstrate method use; they do not establish a beta-mixture law for our selected image sources or seeds.

Use: cross-check the closed PMF evaluated with stdlib lgamma in plan_v2.py. No SciPy code or random sampling runs. The rho=0 and rho=1 cases require explicit limiting distributions, rather than invalid a/b parameters. Numerical mass sums, seed-majority limits, and exhaustive retention-mask identities are checked locally. This card supplies implementation provenance; Ahmed and Elmore supply paper-level model/identification context. We do not interpret a beta-binomial predictive interval as a confidence interval for p.

# Analytic justification and sensitivity of n = 1,200

This appendix is prospective mathematical planning, not an experiment, simulation, synthetic dataset or analysis of new outcomes. The parent evaluated only displayed expressions on fixed constants using JavaScript Math in the orchestration tool. No Python, scientific runtime, random draw, model, image or statistical package was used. Full numeric inputs/results are in [analytic-planning-values.json](analytic-planning-values.json).

## Why the finite-population law is appropriate

Conditional on a frozen finite frame of N blocks, a fixed endpoint vector with K positive blocks and a genuine size-n uniform sample without replacement gives `X ~ Hypergeometric(N,K,n)`. This remains true if creator outcomes are heterogeneous or correlated as attributes of the fixed frame. What must hold is fixed block potential outcomes and the specified probability sample; interference or outcome-selected sampling defeats that argument. The exact mass and finite-population variance are documented in the [official R reference](https://stat.ethz.ch/R-manual/R-patched/library/stats/html/Hypergeometric.html). No R function was executed.

For each endpoint, `Var(X/n) = (K/N)(1-K/N)(N-n)/(n(N-1))`. This explains why sampling fraction matters and why the eventual realized N belongs in exact inference. It does not supply a normal approximation for rare events. The design inverts integer K tail tests with probability `a=1/240`; an upper-tail probability for `X>=x` includes x (with an upper-tail CDF API it would use x-1). Zero/all-success and census cases follow the same degenerate finite-population law. K=0 and K=N belong to the candidate grid but are not forced into every confidence set.

H and L are paired block predicates before any distribution is used. Under nesting, H lower-bounds both any-wrong and same-owner incidence differences, and L upper-bounds per-seed mean loss. These deterministic inequalities justify the chosen utility scale. No independence between Q and F, owners, seeds, arms or checkpoints is assumed. Union bounding 12 directional errors at a gives family error at most .05.

## Sufficient count region and assurance

Let `D(t||p)=t ln(t/p)+(1-t) ln((1-t)/(1-p))`. Markov's inequality applied to the exponential moment and minimization over its tilt give the Bernoulli Chernoff exponent. The without-replacement convex ordering permits the same conservative exponential bound for the hypergeometric tail; see Greene–Wellner v3, [Section 2 opening](https://arxiv.org/pdf/1507.08298v3). This ignores any favorable finite-population correction and is intentionally conservative.

| Sufficient observed condition in each checkpoint | Boundary-null tail upper bound at n=1,200 |
|---|---:|
| H count >=90 | exp[-1200 D(.075||.05)] = 0.00101780649 |
| L count <=8 | exp[-1200 D(8/1200||.02)] = 0.00066252323 |
| G count >=1080 | exp[-1200 D(.90||.85)] = 0.00000209643 |

All are below a=0.00416666667, so this sufficient region clears the relevant exact limits for every N>=1,200. These counts are not replacements for exact hypergeometric critical values; the exact rule can be less demanding. Under the fully observed planning region H>=.10, L<=.002 and G>=.95 in both checkpoints, failure of these sufficient conditions is bounded by the sum of six tails. For H and G use enlarged failure events X<=90 and X<=1080; for L use X>=9. The respective per-checkpoint bounds are 0.01087297607, 0.00492208807 and 0.0000000000172181. Thus

`joint assurance >= 1 - 2(.01087297607 + .00492208807 + .0000000000172181) = .96840987169`.

This exceeds the selected 95% planning-assurance target while retaining 95% simultaneous confidence coverage. Assurance is conditional on an assumed true effect region and full observability; confidence coverage is the repeated-sampling property of the interval procedure. Neither is a posterior probability that F5 works. No existing pilot is claimed to justify the assumed H=.10 or L=.002. The alternative is deliberately strong so the study can reliably recognize a clearly useful component, rather than promise decisive results arbitrarily close to a boundary.

For scale comparison, n=1,000 with sufficient counts H>=75, L<=6 and G>=900 gives only a 0.90824 lower assurance bound by the same argument and strong alternative. This does not prove n=1,000 inadequate under exact tails, nor prove 1,200 minimal. The selected 1,200 is a round, conservative design with an auditable guarantee independent of unknown N. Exact-tail optimization could reduce cost in a different pre-outcome plan; it is not silently substituted here.

## Sensitivity: what the guarantee does not say

The following are algebraic lower bounds using the same sufficient region, with the same assumed parameters in both checkpoints. A zero means the bound is uninformative, not that actual power is zero. No row is an empirical result.

| Assumed H | Assumed L | Assumed G | Conservative joint assurance lower bound |
|---:|---:|---:|---:|
| .100 | .002 | .95 | .96841 |
| .125 | .002 | .95 | .99016 |
| .090 | .002 | .95 | .63862 |
| .075 | .002 | .95 | 0, uninformative |
| .100 | .005 | .95 | 0, uninformative |
| .100 | .010 | .95 | 0, uninformative |
| .100 | .002 | .92 | .87274 |
| .100 | .002 | .90 | 0, uninformative |

Missing outcomes widen the H/L completion bounds, and failed delivery reduces operational G. No fixed dropout inflation is imposed because there is no evidence for a missingness rate and adding replacement successes would change the target. If these stronger conditions do not hold, the exact intervals and unresolved/refuted categories still apply; the 96.84% assurance claim does not. Precision near the margins depends on N and the actual counts. The design makes no universal fixed-width or million-comparison rare-risk guarantee.

The references support distributional facts, not the chosen practical margins or actual feasibility. Those are researcher decisions and future factual requirements, respectively.

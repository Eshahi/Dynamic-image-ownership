# T6: statistical design and sample size (superseded v1 history)

This historical document is superseded in full by `synthesis.md`, `planning-table-v2.json` and the v2 tables. It exposes earlier assumptions and corrections and is not current protocol guidance.

2026-10-19. Stage-1 planning only. No observations, images, models, GPU work or random simulations were used. Arithmetic is reproducible with `tools/plan.py`; all precision beyond the printed tables is in `planning-table.json`.

## Recommendation and estimand

Retain **n = 60**, the three fixed seeds and the source-majority rule. Freeze the deterministic source roster before outcomes. The primary estimand actually measured is the fraction of this consulted development roster whose F5 C endpoint succeeds on at least two of seeds 12, 13, 14 in R1 SDXL at strength .2, counting missing positives as failures. It is a finite-roster descriptive endpoint. Source order is purposive/deterministic, not a probability sample of Internet images. Neither a confidence interval nor more seeds makes this a confirmation or gives design-based population coverage.

The count rule stays unchanged: K >= ceil(.75n) plus a complete zero-negative gate gives TRANSFERS; 2K < n gives FAILS; everything else gives PARTIAL. At n=60 these are >=45 and <=29; margin m=3. At n=90 they are >=68 and <=44, m=5; at n=120 >=90 and <=59, m=6. A strict comparison with .5 matters at the boundary. The margin is a routing convention, not a statistically established noninferiority margin. ROUTE A/B depends on paired baseline results and cannot have a unique operating characteristic specified from F5's success rate alone.

## Exact count-rule operating characteristics

For planning only, suppose the **source-majority indicators**, not the seed calls, are independent exchangeable Bernoulli(p). Then K is Binomial(n,p). Each row below gives percentages in the order FAILS / PARTIAL / TRANSFERS. The negative gate is assumed to hold with certainty in this table; this is an upper-envelope transfer probability, not unconditional whole-rule assurance.

| Source p | n=60: F / P / T (%) | n=90: F / P / T (%) | n=120: F / P / T (%) |
|---|---:|---:|---:|
| .50 | 44.8711 / 55.1222 / .0067 | 45.8064 / 54.1935 / .0000625 | 46.3658 / 53.6342 / .00000189 |
| .60 | 4.4480 / 94.4571 / 1.0948 | 2.1292 / 97.7291 / .1417 | 1.0460 / 98.9137 / .0404 |
| .70 | .0364 / 75.5852 / 24.3784 | .0023 / 85.0023 / 14.9954 | .000146 / 86.4076 / 13.5923 |
| .75 | .000838 / 43.1194 / 56.8797 | .00000941 / 49.1853 / 50.8147 | .000000111 / 45.1147 / 54.8853 |
| .80 | .00000489 / 13.0621 / 86.9379 | <.000001 / 11.9508 / 88.0492 | <.000001 / 7.2122 / 92.7878 |
| .85 | <.000001 / 1.3599 / 98.6401 | <.000001 / .6247 / 99.3753 | <.000001 / .1409 / 99.8591 |
| .90 | <.000001 / .0201 / 99.9799 | <.000001 / .0019 / 99.9981 | <.000001 / .000060 / 99.99994 |

Thus n=60 distinguishes strong transfer (p=.85) cheaply. Doubling to 120 raises the conditional TRANSFERS probability at p=.8 by only 5.85 percentage points, while doubling image work. Near p=.75 the label remains uncertain at every allowed n; integer thresholds also make assurance nonmonotone in n. At p=.6, PARTIAL is the intended likely outcome, not an error to tune away. At p=.5, FAILS happens under half the time because the threshold is strict; this design is not a high-power test against p=.5. A label of TRANSFERS is not a 95% lower confidence statement that p >= .75.

If G is the event of complete, all-zero F5 R1 negatives, the actual transfer probability is P(K>=cut, G). Given only g=P(G) and t=P(K>=cut), its bounds are max(0,t+g-1) to min(t,g). Under the additional illustrative independence assumption it is gt; FAILS is unchanged and the lost transfer mass moves to PARTIAL. At n=60,p=.8,g=.9, this gives 78.2441% TRANSFERS, versus 86.9379% with g=1. Positive and negative outcomes share sources and can be dependent, so multiplication is not an empirical prediction. The JSON includes g=.8,.9,.95,1 sensitivity.

## Dependence: two different levels

The source-majority endpoint already respects clustering of three seed calls within a source. Using Binomial(180,p) on the pooled seeds would change the estimand and falsely treat seed repetitions as new images. Pair all methods on the same source and preserve all seeds together in summaries.

For an illustrative seed-dependence calculation, let a source-specific seed probability Q have Beta(a,b), with conditional independent seed calls. With seed mean q and within-source ICC rho, use a=q(1/rho-1), b=(1-q)(1/rho-1). The source-majority probability is 3 E[Q^2] - 2 E[Q^3], with the rho=0 limit 3q^2-2q^3. This is an analyst-specified sensitivity model, not a fitted model or measured ICC. The beta-binomial construction is supported by Ahmed and Shoukri, section 2; their estimator is not adopted.

| q=.8, seed ICC | source-majority p | n=60 conditional TRANSFERS |
|---|---:|---:|
| 0 | .8960 | .999685 |
| .1 | .870691 | .996727 |
| .3 | .836185 | .970669 |
| .5 | .8160 | .926818 |
| .9 | .800505 | .871526 |

The table at the start already parameterizes **p after majority**, so no extra design-effect multiplier should be applied to that p. Different sources may also be correlated through shared creator, near-duplicate content or dataset provenance. A separate sensitivity treats K as beta-binomial with source ICC .01 or .05. At p=.8,n=60, transfer probabilities then become .817327 and .736340; at n=120 they become .841619 and .734545. This all-sources exchangeable mixture is deliberately illustrative and does not assert that these ICC values describe the roster. It demonstrates that more images cannot remove systematic cohort dependence. Record known group structure and counts; do not report nominal CP coverage as valid under that dependence. The existing Cameron–Miller V2 card is reused only for the general clustering warning.

## Intervals, comparisons and multiplicity

Report two-sided equal-tailed **95% Clopper–Pearson** intervals for each source-level proportion, with the caption: "Model-based exploratory interval assuming independent exchangeable source indicators; consulted deterministic development cohort." Invert binomial tails at .025, as in NIST's exact-binomial documentation; the existing Brown–Cai–DasGupta V2 card documents conservatism. The interval is marginal per cell, not simultaneous across cells. No interval changes the fixed rule. Illustrations: 45/60 -> [.6214,.8528]; 68/90 -> [.6536,.8400]; 90/120 -> [.6627,.8245]. Even the transfer cutoff is compatible with substantially lower model p.

For the primary cell, compare F5 against v5, WAM and VINE using source-majority binary pairs. Report the full paired table, wins w, losses l and ties; difference=(w-l)/n. The two-sided exact sign/McNemar conditional p-value is min(1,2 P[Binomial(w+l,.5)<=min(w,l)]); no discordances gives p=1. Its validity requires independent source pairs with symmetric discordance under the null. Shared fixed seed labels do not create randomized treatment assignment. Tests compare operational endpoints with different payloads/side information; they do not establish equivalent tasks or fair quality by themselves.

Use **one prespecified Holm family of three primary comparisons**, reporting raw and adjusted p-values. Sorted adjusted values are max over j<=i of min(1,(3-j+1)p_(j)). Unavailable comparisons retain a family slot, use p=1 internally and display "not estimable". Official R documentation confirms Holm's arbitrary-dependence family control; this does not repair invalid individual p-values or selection of sources. Other channels, strengths, diagnostics and secondary endpoints are descriptive: counts, marginal intervals, distortion and paired deltas, with no extra inferential stars. If the author later adds exploratory secondary tests, place all added tests in one declared secondary family, retain the complete family and apply Holm there; never let that change routing. Prefer not to add them.

## Negatives and missing observations

The integrator has frozen the conservative historical **A endpoint** (any found semantic or instance) for the F5 negative gate, and will report every negative endpoint separately. Primary positives remain C. Gate inventory includes every F5 C0 and wrong-owner call on R1 outputs over the retained .1/.2/.4 strengths: 540 C0 + 540 wrong-owner calls at n=60, unless a prespecified budget drop removes .1 before the full run. Any observed false call or unresolved planned negative blocks TRANSFERS; no majority vote is applied to negatives. R0, D1 and resize negatives are reported but do not silently expand this gate.

Zero observed negatives is not an empirical FPR <=1e-4 claim. Even with 1,080 independent trials, the one-sided 95% zero-count upper bound is .002770; at 540 it is .005532. Treating 1,080 correlated calls as independent would itself be unjustified. Define source-level "any observed negative acceptance" for description; with 60 fully observed independent hypothetical source groups, 0/60 has one-sided upper .048703 (two-sided CP upper .059629). No bound proves a population FPR for this selected cohort. Under genuine independent Bernoulli sampling, 29,956 zero trials are needed just for a one-sided 95% upper bound <=1e-4.

The common presence thresholds are k=27/32 for WAM (random-message tail .0000565371) and k=69/100 for VINE (tail .0000915716). The previous k values exceed 1e-4. These are arithmetic properties of independent fair random matching bits, not validation of empirical false detections, correlated decoder bits or source-majority FPR.

Keep n fixed. A missing/safety-blocked positive seed contributes false; two observed successful seeds still yield source success if the third is missing. Do not remove or replace difficult sources, lower n, select successful seeds or treat absent journal rows as completed negative calls. Show attempted, observed, missing and safety-blocked denominators. For transparency add non-decision optimistic bounds: count a source successful if its observed successes plus missing seeds could reach two; bound the count between the fixed failure-imputed K and this optimistic count. This is missingness sensitivity, not a rescued verdict. If K<.5n, FAILS remains the operational rule even with missingness, but explicitly distinguish execution failures from observed detector failures. Missing negatives stay unresolved, never zero. Complete-case summaries may be secondary only. Preserve paired alignment in sign tests and show imputation counts per arm; differential failures can drive the operational comparison.

## Budget and why not n=90 or 120

Four marked arms plus one shared unmarked stream, two channels, three strengths and three seeds produce **90n regeneration calls**. Wrong-owner calls decode existing outputs and add no regeneration. D1 adds 5n deterministic VAE round trips; a resize-only control adds 5n image transformations. A second .1 rinse pass on the saved first-pass R1 .1 outputs adds **15n** calls, assuming three seed trajectories and no independent repeated first pass. FLUX is absent from this planning core; D2 is therefore absent.

| n | Core calls | Extra rinse calls | D1 / resize units | Average core-call ceiling with 3h nonregeneration reserve | Ceiling with rinse |
|---|---:|---:|---:|---:|---:|
| 60 | 5,400 | 900 | 300 / 300 | 8.00 s | 6.86 s |
| 90 | 8,100 | 1,350 | 450 / 450 | 5.33 s | 4.57 s |
| 120 | 10,800 | 1,800 | 600 / 600 | 4.00 s | 3.43 s |

These are break-even arithmetic, **not measured runtime promises**. They include a hypothetical three-hour reserve for setup, embedding, detection, metrics, diagnostics, smoke and transfer; the integrator must reconcile that reserve with its hardware plan. More precisely total hours = H_other + [45n*t_R0 + 45n*t_R1 + 15n*t_rinse]/3600, using amortized seconds and omitting rinse if absent. The hard limit is min(15,15/hourly_USD_rate). The displayed ceilings assume hourly rate <=$1; at $1.50/hour the allowed time is 10h and the n=60 core ceiling with the same reserve falls to 4.67s. Include download/setup billing and result-transfer time. Freeze n before any output; smoke timing may trigger only the brief's declared channel drops, not outcome-based resizing or stopping. A budget truncation retains fixed-n missing-data accounting.

At .8, n90 buys just 1.11 percentage points of conditional transfer probability for 50% more work; n120 buys 5.85 points for 100% more work. At .85, n60 already has 98.64% conditional transfer probability. The purpose is a cheapest decisive development screen, so n60 gives the best defensible balance. A larger n could improve precision in a later fresh confirmation, but this study must not be represented as powered to resolve small baseline margins or broad FPR claims.

## Draft-code review and provenance

Read-only review of `scripts/encoder_transfer_test.py` found the integer ceilings, strict fail threshold, negative/unresolved blocking, CP inversion and sign-tail formulas correct for the specified integer count domain. `tools/plan.py` extracts only five pure functions with AST, never imports the runner, and checks all decisions for n60..120, CP bounds/reflection for every k at n60/90/120, zero/all-success closed forms and simple exact sign cases. It records the inspected draft hash. No GPU/model/image code executes. Input-validation hardening is advisable: reject noninteger n/k and alpha outside (0,1), and require actual Boolean paired vectors. These are API defenses, not found errors for the frozen valid inputs. Add Holm output and explicit negative-A documentation during integration; the reviewer did not edit shared code.

Coverage: primary statistical references and official implementation documentation were searched; existing Brown and Cameron cards were reused. Ahmed–Shoukri's model and evaluation were inspected. A 2025 exact randomized-experiment paper was screened but full text was inaccessible here and its randomized-assignment estimand does not replace this study's deterministic source design. A 2025 differential-privacy interval lead is outside scope. No specific relevant 2026 methodological improvement was verified; no claim of exhaustive statistical literature coverage is made. Holm's 1979 original full text was inaccessible; the adopted implementation guidance is the inspected official R documentation, not an invented full-paper reading. See `search-log.md`, cards and `source-manifest.json` for exact accesses and cached-file hashes.

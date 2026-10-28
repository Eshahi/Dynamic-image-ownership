# Stage C exact power and resource design (conditional author recommendation)

2026-10-28. This document does not select the WP2 writer and authorizes no execution. It applies only if WP2 selects the F6-noise writer and Stage S passes its frozen screen. Recommend **one frozen n=120 fresh source pool**, not optional stopping at 80/120/160. The root Stage C protocol must adopt its n before outputs. A failed 50-hour resource check means resource NO-GO, not an automatic reduction of n. All calculations here use pure stdlib analytical probability sums, not model runs, timing runs or Monte Carlo.

## Endpoint and six hypotheses

For each source, arm and model cell, let J be exact recovery of the original semantic payload q **and** the frozen content-match gate recomputed on the current suspect. J is neither original-instance uniqueness nor cryptographic authentication nor legal ownership. It is stricter than a merely readable semantic payload, but does not require the original h value. Freeze every threshold and the reader before new held-out observations.

The binary source endpoint is at least two J-positive seeds of the same three fixed seeds. Seeds are repeated measurements inside the source; they do not increase n. The parameter p is a probability of this source-majority endpoint, not a single-seed success probability. Without a conditional independence assumption, one cannot transform single-seed accuracy r into 3r^2-2r^3; no such transformation is used here.

| Slot | One-sided alternative (all at strength .2) |
|---|---|
| H1 | Paired J(F6-noise) > J(F5), SDXL |
| H2 | Paired J(F6-noise) > J(F6-codec), SDXL |
| H3 | Paired J(F6-noise) > J(F6-generic), SDXL |
| H4 | Paired J(F6-noise) > J(F5), new SD3.5 |
| H5 | Pr[J(F6-noise)] > .70, new SD3.5 |
| H6 | Pr[J(F6-noise)] > .70, SD1.5 |

Use six Holm slots at familywise .05. Sort raw p values ascending (fixed slot order breaks ties), compare successive values to .05/(7-rank), and stop at the first failure. Unavailable hypotheses retain p=1; the family is not reduced. SD3.5 must remain excluded from writer design, fitting and Stage S outcomes. New sources alone do not make an already explored generator a new family. Licence/access or memory failure is unavailability, never a reason to replace its family after outputs.

## Exact tests and unconditional power

Absolute test: for X source successes among n, the exact inclusive-tail p value is

    p_abs = sum[k=X..n] choose(n,k) .70^k .30^(n-k).

This tests the composite null p<=.70, whose least favorable boundary is .70. Define c_n as the smallest integer with this tail <= a, where a=.05/6. Power at alternative p is the Bin(n,p) tail from c_n. Nonrandomized exact tests are conservative due to discrete counts; no mid-p adjustment is permitted.

Paired test: let B count candidate-positive/comparator-negative sources and C count candidate-negative/comparator-positive sources. Given D=B+C discordances, under the least favorable null p10=p01,

    p_pair = sum[k=B..D] choose(D,k) 2^(-D), with p_pair=1 if D=0.

The null p10<=p01 is equivalent to no positive paired marginal difference. An exact conditional McNemar test is valid here. Its **unconditional power**, integrating over the random discordant count, is

    q = p10+p01, theta = p10/q,
    power(n;p10,p01) = sum[d=0..n] BinPMF(d;n,q)
                      * Pr[Bin(d,theta) >= c_d(.5,a)].

For q=0 power is zero. This is a finite exact probability calculation (evaluated with floating point), not the normal approximation, not power conditional on expected D, and not a Monte Carlo estimate. The non-discordant split between (0,0) and (1,1) does not affect this test's power. The marginal difference alone is insufficient: total discordance controls information.

Using a=.0083333333 in every table gives a sufficient rejection event for every Holm slot. Consequently these are per-hypothesis lower bounds on Holm rejection probability under any dependence among the six tests. They are **not** joint all-six power. Holm may have higher marginal power after earlier rejections; claiming that gain requires a joint outcome model.

### Absolute superiority over .70

| Fresh n | Required successes at a | Power p=.80 | Power p=.85 | Power p=.90 |
|---:|---:|---:|---:|---:|
| 80 | 66 | .346281 | .787391 | .987654 |
| 120 | 97 | .463624 | .916527 | .999250 |
| 160 | 127 | .623371 | .978802 | .999981 |
| 200 | 156 | .788738 | .996879 | 1.000000* |

*The final rounded value is .9999998238, not exactly one.*

### Paired superiority

The scenarios below have marginal advantages .20, .10 and .30 respectively.

| Fresh n | p10=.25, p01=.05 | p10=.20, p01=.10 | p10=.35, p01=.05 |
|---:|---:|---:|---:|
| 80 | .803694 | .163132 | .984119 |
| 120 | .958865 | .292283 | .999511 |
| 160 | .993063 | .421416 | .999989 |
| 200 | .998932 | .534627 | 1.000000* |

*The final rounded value is .9999997773.*

n=120 is defensible as a large-effect confirmation: over 91% marginal power for .85 versus .70 and over 95% for a paired .20 gain with the stated discordance. It is weak for .80 absolute survival (46%) or a .10 paired gain (29%). n=160 costs 33.3% more source-dependent work, raising these to 62% and 42%, still insufficient for a modest-effect guarantee. Even n=200 is below 80% for .80 absolute survival and below 54% for the paired .10 scenario. Inconclusive slots must remain inconclusive; no post-hoc weakening of .70 or switching to an unadjusted test.

If all four paired alternatives have (.25,.05) and both absolute rates are .85, the dependence-free union bound on all-six rejection is only max(0,1-4*(1-.958865)-2*(1-.916527))=.6685 at n=120, versus .9299 at n=160. This is a conservative joint lower bound under those specific simultaneous alternatives, not a prediction of actual joint power. Quality, specificity, completeness and Stage S gates may further reduce the probability of an overall GO; these tables cover only the six primary efficacy tests.

## Missing observations and complete reporting

Keep the original frozen denominator n. A missing/error/blocked candidate seed is J=false. A missing comparator seed is treated as success in that paired comparison, never as failure. Then compute the three-seed majority from all three positions. Equivalently, any source outcome whose majority cannot be determined conservatively receives candidate=false or comparator=true on its missing side. An optional stricter source rule may map every incomplete pair to (candidate=false, comparator=true), but must be frozen consistently before outputs. Do not complete-case drop pairs, replace sources, reinterpret safety blocks as negatives for specificity, or rerun with altered content to avoid blocks.

Publish conservative positive tests with a full missingness inventory and a separate complete-case sensitivity table. Missing negative calls never count as demonstrated specificity. If required C0, wrong-owner, T4 or T5 coverage is incomplete, the joint primary security status is **INCOMPLETE**, even if all six efficacy p values pass. Do not count an efficacy rejection as a complete positive security claim. Under the iid source assumption, pessimistic completion cannot increase the rejection event relative to the true unobserved outcomes.

## Specificity: zero observations do not certify tiny error rates

For n independent Bernoulli units with zero events, the exact one-sided 95% upper confidence bound is u=1-.05^(1/n). This is an individual bound for a specified negative endpoint, not simultaneous coverage over negative families. For simultaneous coverage over K declared families, use alpha=.05/K in the same formula or a prespecified valid joint procedure.

| Independent zero-event units | Upper 95% event probability |
|---:|---:|
| 80 | .0367542 |
| 120 | .0246554 |
| 160 | .0185491 |
| 200 | .0148670 |

To obtain u<=target with zero events requires ceil(log(.05)/log(1-target)) independent units:

| Target | Required independent zero-event units |
|---:|---:|
| .01 | 299 |
| .001 | 2,995 |
| .0001 | 29,956 |

Repeated seed, arm, threshold, patch or claim queries on the same source do not form independent units. For a source-cluster endpoint, declare an event if **any** frozen negative query in that cluster accepts; its binomial bound concerns that finite query bundle. T4/T5 pairs sharing donors or recipients are dependent as well. A complete graph of 120 images cannot be reported as 14,280 independent pairs. With disjoint donor/recipient pairs from 120 images there are at most 60 pair units (zero-event upper bound about .0487). Larger overlapping-pair studies need a valid clustered analysis and do not inherit the simple binomial n. Human distinctness judgements stay missing until actually provided; no tiny error-rate, authentication or unique-instance claim follows from this design.

## 50-hour envelope: freeze inventory, then measure before outcomes

There is no measured F6 timing yet. Historical F5/native figures do not establish the cost of robust F6 optimization or SD3.5. For a full eight-arm inventory (including C0), three primary family cells and three seeds, native output counts alone are 72n: 5,760 / 8,640 / 11,520 / 14,400 for n=80/120/160/200. Every additional strength adds its full inventory. These counts exclude writer creation, all metrics/readers, mechanism diagnostics, controls, attacks and standard distortions. They are inventory arithmetic, not runtime forecasts. If the protocol uses fewer arm-cell combinations, enumerate those combinations explicitly; do not use an eight-arm budget to hide omitted comparisons.

Recommend n=120 fixed before outputs, conditional on the following resource gate. Time only later on the authorized server, using development sources, before new held-out generation. Extrapolate **each operation class** (new marks by writer; native trajectories by family/resolution; readers; metrics; T4/T5; secondary distortions), allowing any shared marks only once. Include model loading, asset staging/licences, output hashing, collection and retrieval. Use a 1.5-times observed per-unit multiplier plus a fixed explicit retrieval/failure reserve. Require

    H_fixed + 1.5 * sum_j(count_j(120) * measured_seconds_j / 3600)
       + H_retrieval_reserve <= 50 hours.

H_fixed must include unmeasured setup allowances. If a necessary operation has not been measured or conservatively bounded, the gate is unqualified. Full observed rehearsal counts and the extrapolation must be written before held-out outputs, not estimated from a partially completed run. Keep the secondary standard-distortion section within its separately allocated approximately 1-2 hours; it cannot displace primary T3/T4/T5 coverage. Failure gives resource NO-GO and a documented later redesign requiring a new pre-output protocol; it never silently switches to n=80 or drops a comparator. Nothing in this document asserts that either 120 or 160 fits 50 hours.

## Freshness, reproducibility and tests

Use a committed identifier-only **fresh** held-out pool, disjoint from all prior development, the consumed 200 Phase-B sources and its untouched 40 reserves. Freeze a source-order rule before outcomes. Server-side hash deduplication must precede scientific use; identifier disjointness alone does not establish content disjointness. Neither freshness nor public release dates prove exclusion from model pretraining. No old 200-source result is an independent Stage C replicate.

Reproduction (approved stdlib interpreter, each invocation under 15 minutes):

    W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe -I scripts/tifs_design_power.py
    W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe -I scripts/tifs_test_design_power.py

Six unit tests passed on 2026-10-28: mass normalization/endpoints; exact inclusive cutoffs and null size; an independently enumerated small McNemar case; expected effect/scenario ordering and increasing power on this four-n grid; minimal specificity sample sizes; invalid probability rejection. Exact nonrandomized power can have small local sawteeth as n changes, so no test asserts monotonicity at every successive integer. No model library was imported and no image, model, experiment or timing workload was run.

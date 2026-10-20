# T6 Stage1b: statistical operating characteristics and limits

Completed 2026-10-20. This is hypothetical analytic design research, not an experiment result. No real images, outcomes, weights, GPU or server were used. Retain the frozen n=60 core, fixed three-seed majority, denominator, negative safety gate and routing rule. Increasing to n=90/120 offers conditional precision but is not justified under current time/cost assumptions. The revision is to reporting: show conditional operating characteristics, dependence and missingness sensitivity instead of calling a binomial calculation an unconditional probability of success.

Eight primary papers have individual method-and-evaluation V2 cards; five official implementation/reference cards are separate. Twelve substantive discovery queries span arXiv API, OpenAlex and web. See `search-log.md`, `query-manifest.json`, `source-manifest.json`, `references.bib` and `floor-audit.json`. Exact cache hashes/URLs and licenses are recorded; caches are outside Git. Software worked examples do not count as paper evaluations.

## Fixed endpoint and estimand

The primary cell is F5 r2 under R1 SDXL strength .2. A source succeeds if at least two of fixed seeds 12,13,14 recover C; K counts successful sources among fixed n. G means complete R1 F5 C0 and wrong-A negative calls with zero positives across all retained R1 strengths. TRANSFERS requires K>=ceil(.75n) and G; FAILS requires 2K<n; otherwise PARTIAL, including safety failure blocking TRANSFERS. Missing positive calls are false. Missing negative calls are unresolved, never silently zero. The denominator is the preregistered roster, not completed sources.

| n | Transfer threshold | Largest failing count | External margin ceil(.05n) |
|---|---:|---:|---:|
| 60 | 45 | 29 | 3 |
| 90 | 68 | 44 | 5 |
| 120 | 90 | 59 | 6 |

This selected development cohort is not a probability sample of images, owners, prompts or regenerators. Counts on it describe that finite cohort. Repeated-sampling probabilities and intervals below require hypothetical source laws; exact arithmetic does not supply representativeness. Cameron/Miller's cluster warning and Longjohn et al.'s aggregate-comparison work support separating counts from inferential assumptions, not population generalization.

## Conditional source-count operating characteristics

If source outcomes were iid Bernoulli(p), K would be Binomial(n,p). Direct finite sums give this probability of reaching the positive threshold **with the safety gate treated as satisfied (G=1)**. Full FAILS/PARTIAL/TRANSFERS partitions for p=.50,.51,...,.90 and all three n are in `tables/source_oc.csv` (123 rows).

| Hypothetical p | n=60 | n=90 | n=120 |
|---|---:|---:|---:|
| .50 | .0000673 | .000000625 | .0000000189 |
| .60 | .010948 | .001417 | .000404 |
| .70 | .243784 | .149954 | .135923 |
| .75 | .568797 | .508147 | .548853 |
| .80 | .869379 | .880492 | .927878 |
| .85 | .986401 | .993753 | .998591 |
| .90 | .999799 | .999981 | .999999 |

At p=.50 and n=60, FAILS probability is .448711 and PARTIAL .551222: half successes do not satisfy the strict failure rule. At p=.75, integer rounding means the threshold probability need not increase monotonically with n. At p=.80 the gain from 60 to 90 is small relative to the workload increase. These numbers do not predict F5's unknown success probability.

## Seed dependence and identification

The transparent sensitivity model assumes a source's conditionally iid Bernoulli seeds have Q~Beta(a,b), mean q and nonnegative pairwise ICC rho=1/(a+b+1). For 0<rho<1, a=q(1/rho-1), b=(1-q)(1/rho-1). Sum beta-binomial probabilities of two and three successes for the majority probability. At rho=0 use iid seeds, p=3q^2-2q^3; at rho=1 use identical outcomes, p=q. Ahmed/Shoukri supports this model, but its cluster-size-two estimator simulation does not validate three image seeds. SciPy's reference cross-checks the PMF; no library or estimator ran.

At q=.80 and n=60, with independent sources and G:

| Seed ICC | Majority p | Positive threshold probability |
|---|---:|---:|
| 0 | .896000 | .999685 |
| .1 | .870691 | .996727 |
| .3 | .836185 | .970669 |
| .5 | .816000 | .926818 |
| .9 | .800505 | .871526 |
| 1 | .800000 | .869379 |

`within_source` covers q=.50 to .90 by .05 and rho=0,.1,.3,.5,.9,1 for each n (162 rows). These are assumptions, not estimated ICCs.

Mean and pairwise correlation do not identify a three-seed majority. Define s=q^2+rho*q*(1-q), t=P(all three succeed). Under finite exchangeability, probabilities for counts 3,2,1,0 are t,3(s-t),3q-6s+3t,1-3q+3s-t. Nonnegativity implies max(0,2s-q)<=t<=min(s,1-3q+3s); majority probability is 3s-2t. Both endpoint distributions are feasible, checked locally. `exchangeable_bounds` gives these sharp bounds beside the beta assumption. Elmore emphasizes higher-order joint probabilities; Singh separates pooled random-task mixture assumptions from fixed labeled likelihoods. These finite-three-variable bounds are a local derivation, not attributed as an image-seed theorem in either paper. Negative ICC and nonexchangeable seed laws are outside this grid.

Cross-source dependence is separate. `cross_source` uses hypothetical beta-binomial K with source ICC .01/.05 and variance inflation 1+(n-1)rho (1.59/3.95 at n=60). Creator/content groups may violate source independence. Do not multiply a seed design effect into K after already mapping seed calls to a majority, or treat this second beta mixture as an estimated image population model. More sources need not deliver iid precision when shared dependence persists.

## Missing units and fixed denominators

False-imputation is retained; complete-case analysis or imputation does not replace it. Hossain et al. and Wang et al. motivate explicit missingness/estimand assumptions, not transferring their clinical estimators or rates.

* Independent seed loss d: conditional on k latent successful calls, retained successes follow Binomial(k,1-d); sum the chance of retaining at least two over the beta-binomial count law.
* Whole-source loss d: majority success probability is (1-d)p. All calls within a lost source are absent, unlike independent call loss.
* Outcome-dependent loss: for latent success probability u and loss risk ratio r=d_success/d_failure, set d_failure=d/(u*r+1-u), d_success=r*d_failure. Use u=q for seed loss and u=p for source loss. Tables use r=.5/2 with feasible probabilities checked. Seed retention masks are conditionally independent here; this is not arbitrary informative missingness.
* Fixed h lost sources: K~Binomial(n-h,p) under homogeneous independent surviving-source assumptions, keeping original cutoff/denominator. At n=60, h=15 requires all 45 remaining sources to succeed; h>=16 makes transfer impossible. Other tipping points are h>22 at n=90 and h>30 at n=120.

`missing_positive` has 1,620 rows, `informative_missing_positive` has 2,592, and `fixed_missing_sources` has 189. Loss rates 0,.01,.05,.10,.20 are hypothetical. All 27 three-seed observed/missing patterns and all 64 latent-outcome/retention patterns are checked. Reports should disclose missing counts/reasons by arm/strength/source. An optimistic completion count (whether successes+missing could reach two) may describe unresolved potential; it cannot replace the pessimistic endpoint or negative safety gate. Shared outage/process-triggered missingness may satisfy none of these models.

## Negative safety and FPR resolution

Full R1 safety requirements are 18n calls: two control types x three seeds x three retained strengths (.1,.2,.4). The predefined reduction dropping .1 leaves 12n, not 9n. At n=60 these are 1,080 or 720 correlated calls, not independent sources.

If t is the positive-threshold probability and g=P(G), unrestricted intersection bounds are max(0,t+g-1)<=P(TRANSFERS)<=min(t,g). Multiplication t*g requires independence. `joint_negative_gate` supplies 135 examples; the principal OC hides no assumption of independence between positive and negative results.

For missing negatives with marginal rate d and M required calls, completeness is (1-d)^M under independent call loss, (1-d)^n under independent whole-source loss, or 1-d if all calls share one loss event. Arbitrary dependence bounds are max(0,1-Md) and 1-d. At n=60, M=1080, d=.001 these named laws give .339412,.941736,.999; unrestricted bounds are [0,.999]. `negative_missing_gate` retains all 30 scenarios. Missing negatives can block transfer without any false positive and must not be reported as an FPR. `negative_false_gate` separately varies source-level any-negative probability. Combining call errors with missingness requires another dependence model.

With zero events among 60 independent source-level any-negative trials, a hypothetical one-sided 95% upper bound is still .048703 (two-sided .059629). Counterfactually independent 1,080 calls would yield .002770; 720 calls .004152. The latter are resolution illustrations, not valid bounds for these correlated repeated controls. A one-sided zero-event upper bound<=1e-4 requires 29,956 independent trials. Thus finite development controls cannot certify global FPR<=1e-4.

Ideal fair-independent-bit null calibration is distinct: 27/32 has upper tail .0000565371 versus .000267526 for 26/32; 69/100 has .0000915716 versus .000204389 for 68/100. Real bit/owner dependence or selected thresholds can invalidate that null. Keep bit-model calibration distinct from measured zero-control counts.

## External comparison and route dependence

The external reference is max(K_WAM,K_VINE) among eligible available arms. With F5 TRANSFERS, Route A requires F5 count>=external maximum-ceil(.05n); Route B applies when the external maximum exceeds F5 by more than that margin. Remaining outcomes keep frozen Route C/UNDECIDED logic. Eligibility/availability and safety are runner responsibilities; these examples assume eligible available arms and G=1. The arithmetic margin is a development decision rule, not a statistical noninferiority test.

Marginals do not identify routes. `paired_route_examples` uses exact source-paired DP for three feasible F5/baseline p11 laws with WAM=VINE. At n=60 and all three p=.8, Route A is .739199/.748825/.869379 at minimum/independent/maximum feasible F5/shared-baseline joint success; Route B is .130180/.120554/0. `independent_route_examples` separately sums the maximum of two independent external binomial counts and an independent F5 count: same marginals yield A .662007 and B .207372. These named joint laws are not bounds across arbitrary three-arm dependence. Source difficulty can couple every method; retain the observed paired table.

## Intervals, paired tests and multiplicity

Retain source-level two-sided 95% Clopper-Pearson displays using exact tail inversion. Thulin evaluates their length cost; NIST and R cross-check formulas and terminology. For 45/60 the interval is [.621404,.852814], not evidence of population success above .75. Label intervals exploratory and conditional on source-binomial assumptions for this selected cohort. Every k at n=60/90/120 is checked for endpoint bounds/reflection. Seed calls never replace source denominators. Secondary channels, strengths, distortion-matched comparisons and quality metrics are descriptive, not opportunities to rescue the primary route.

For the three prespecified primary paired F5 comparisons report source 2x2 tables, wins/losses/ties and count difference divided by fixed n. Under the conditional sign/McNemar null, wins among discordances are Binomial(d,.5). Ties remain in effect denominators but contribute no discordance. Six wins/zero losses gives two-sided p=.03125; all ties gives p=1 but does not establish precise equivalence. Valid independent-source null assumptions remain necessary. The official statsmodels pinned tests compare the exact branch with an R reference; downloaded tests never execute.

Holm uses one fixed family of three comparisons: sorted p-values multiplied by 3,2,1 with monotonic truncation. It tolerates dependence among valid component p-values (official R guidance), not invalid component tests. An unavailable comparator keeps an internal p=1 slot but displays not estimable; no manufactured comparison is reported. Missing calls keep frozen false-imputation operationally and must be disclosed when interpreting comparisons. Adjusted exploratory tests never override counts, margin or safety.

## Budget and reproducibility

Full abstract work is core 90n+rinse 15n+clean 5n+D1 5n+both X1/X2 controls 10n=125n plus 250 smoke units. Units are heterogeneous planning counts, not measured throughput.

| n | Full units | With smoke | Illustrative hours scaled from n=60 10-14h |
|---|---:|---:|---:|
| 60 | 7,500 | 7,750 | 10-14 |
| 90 | 11,250 | 11,500 | 14.84-20.77 |
| 120 | 15,000 | 15,250 | 19.68-27.55 |

The cap is min(15h,$15/hourly price), not authorization to buy compute. An illustrative three-hour combined non-unit allowance (not the frozen 30-minute retrieval/stop reserve) gives arithmetic average ceilings 5.57/3.76/2.83 seconds per unit under the 15h case, but unit costs differ and no timing was measured. Keep n=60; no resizing after outcomes. Larger n remains proposed only, with no hardware feasibility inferred.

`tools/plan_v2.py` uses stdlib finite sums, lgamma beta masses, root inversion, exact DP and assertions; no Monte Carlo or observations. It extracts only allowlisted pure rule functions from runner AST without importing execution machinery. Rerun with MAIN's bundled stdlib Python after current reporting config: 15 JSON/CSV tables, 5,154 rows, all 9 check groups passed. `planning-table-v2.json` records script/runner/config hashes. A later metadata-only refreeze can change the raw config hash; that is not an outcome-driven statistical amendment. Historical `synthesis-v1.md`, `planning-table.json` and `tools/plan.py` are superseded history, retained transparently.

Changed decisions: no endpoint, n, seeds, threshold, gate, route or margin changed. Reporting now separates positive OCs from negative-gated transfer, includes finite-exchangeable bounds, informative/grouped missingness, explicit cross-method route laws, fixed multiplicity and honest cohort/FPR limits. These strengthen design interpretation without running or tuning an experiment.

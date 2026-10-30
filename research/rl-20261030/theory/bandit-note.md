# Short-horizon bandits: the relevant objective, information and budget

2026-10-30. WP4 bounded theory contribution. **No candidate score or selection is made.** PHASE_B_JOURNALS=off. Read-only inputs were this session's BRIEF, decision map, logged analysis, C7 literature note, the frozen Stage P protocol, and the authoritative STATE once. No F6 outcome, image, Phase B journal, reserve identity, Stage C identity, later TIFS commit or model was accessed. Arithmetic below used only MAIN's stdlib interpreter with `-I`; no simulation or science ran. This file is the sole deliverable of this subtask.

**JUDGMENT.** A short one-off search is usually a best-arm or constrained optimization problem. A bandit can improve information allocation, but its long-horizon cumulative-regret guarantee is often irrelevant or numerically vacuous here. The strongest conditional case for learning is amortization across many fresh sources, with predictable action-dependent gains and stable deployment conditions. Neither condition is established by the existing logs. The existing Stage P already spends adaptively through successive halving; renaming it RL contributes nothing.

## 1. What is a round, and what is being optimized?

Let `x` be a source, `f` a regeneration cell/family, `a` one of K feasible actions and `z` a fresh regeneration seed. Write `Y(x,f,a,z)` for a prospectively defined reward in [0,1]. C and J are different rewards. External message presence is another task, not interchangeable with either. All statements below optimize within a declared feasible action set: strict clean PSNR>35, SSIM>.9, LPIPS<.1 and separately required T4/T5 and negative controls remain constraints, not costs that extra reward can cancel. A clipped/scaled continuous margin would need its range and transformation frozen; these [0,1] bounds cannot be applied directly to the unscaled correlation margin.

| Decision and information | Correct objective/class | Relevant comparator |
|---|---|---|
| Select one configuration, test it repeatedly, then keep one final writer | Pure exploration; simple regret or best-arm identification | Uniform allocation, fixed grid, racing, successive halving |
| Choose a writer for every arriving image and every choice has operational value; observe only that writer's result | Contextual bandit, if feedback really arrives | Best fixed feasible arm, supervised reward predictor when training labels permit, greedy/contextual bandit |
| All K action outcomes are already recorded for each source/cell | Full-information prediction/selection | Source-disjoint supervised or cost-sensitive selection; direct policy scoring |
| Query regeneration choices on one published carrier, then return the best attack | Budgeted best-action search; typically simple regret or probability of finding a successful attack | Finite grid/random search, Bayesian optimization or racing |
| Repeatedly attack, and each successful/failed attack itself has value | Cumulative reward may be appropriate | Cost-aware bandit, with declared query access |
| Change a residual or image through sequential actions | Potential MDP: actions change later states and reward laws | Fixed/greedy schedules, differentiable optimization, then a stateful learner if needed |
| Spend source/compute budget to select an experiment configuration | Pure exploration/resource allocation | Existing Stage P; no learned policy is automatically required |

**SOURCE.** Simple regret evaluates the recommended final arm; cumulative regret evaluates the arms actually played during collection. Their allocation objectives differ. Recommending a uniformly sampled past action gives expected simple regret equal to expected cumulative regret divided by the number of plays; this is a particular recommendation rule, not a guarantee for whichever empirical winner an implementation returns. [Bubeck, Munos and Stoltz, inspected arXiv v6 (9 June 2010), §§2–3, pp.3–6](https://arxiv.org/pdf/0802.2655).

**DERIVED/project interpretation.** A deployed per-image choice has an episode horizon of one even if the training set has thousands of images. Three regeneration seeds are repeated measurements, not three state transitions. The writer's 200 updates are not 200 affordable native-feedback bandit pulls. Their state changes, and their per-update/gradient latency has not been measured. For a fixed source and unchanged action, repeated seeds can estimate `mu_a(x,f)`; for fresh sources from a fixed distribution, an action can instead have a marginal `mu_a`. These are different estimands and their sample counts must not be substituted for each other.

## 2. Cumulative regret: an explicit bound, and why short horizons matter

For a fixed stationary stochastic K-arm problem, let `mu_* = max_a mu_a`, `Delta_a = mu_* - mu_a`, and

`R_T = sum_(t=1)^T (mu_* - mu_(A_t))`.

**SOURCE.** For UCB1 on fixed [0,1] stochastic arms, Auer et al.'s Theorem 1 gives

`E R_T <= 8 ln(T) sum_(Delta_a>0) 1/Delta_a + (1 + pi^2/3) sum_a Delta_a`.

The policy initializes each arm and uses an empirical mean plus an exploration bonus. Its distributional setup is stationary; the proof uses the displayed Chernoff–Hoeffding inequality (Fact 1). This is an upper guarantee, not a predicted regret or a lower bound on other algorithms. [Auer, Cesa-Bianchi and Fischer, Machine Learning 47 (2002), §2 Theorem 1 and §3 Fact 1/proof, pp.237, 242–243](https://people.eecs.berkeley.edu/~russell/classes/cs294/s11/readings/Auer%2Bal:2002.pdf).

**DERIVED.** A transparent gap-free corollary splits arms at a gap `epsilon`: all small-gap pulls together cost at most `epsilon*T`; large-gap arms contribute at most `8K ln(T)/epsilon + cK`, where `c=1+pi^2/3`. Optimizing the split, and retaining the trivial [0,1] bound, yields

`E R_T <= min{T, 2 sqrt(8 K T ln T) + cK}`.

When the optimizing epsilon exceeds one, use the trivial bound directly. This loose corollary is deliberately not claimed to be the best available minimax rate. It exposes constants that an unqualified `O(sqrt(KT))` would hide.

For K=8, T=24 gives an untruncated corollary of 174.1 against the trivial maximum 24: **vacuous**. At T=573 it is 999.5 against 573: still vacuous. Even the gap-dependent formula with seven suboptimal arms all 0.1 below the best gives 3,559.5 at T=573, again vacuous. This does not prove UCB fails; it means this theorem cannot certify useful performance on that budget. At T=19,834, K=8 the gap-free corollary is 7,122.5, or average regret at most .3591: nonvacuous but weak. K=64 at the same T gives 20,323.0 and truncates to T; K=1024 also truncates.

The contrast matters because 20 hours buy approximately 19,834 high-cost endpoint-only calls, but only 573 calls if every action rewrites an F5-style mark (§4). If those 573 calls are divided among 60 sources and a controller restarts on each, there are about 9.6 calls per source. They do not provide a 573-round stationary per-source problem. K=8 barely permits one pass; K=64/1024 do not. Pooling source histories requires a justified common reward model or contextual generalization, not just a change of T in the formula. If actions depend on the current context, each arm's observed contexts may have a different distribution; ordinary UCB on those pooled arm averages does not automatically estimate the same marginal source-population objective.

**DERIVED no-structure obstruction.** Suppose one unknown arm gives deterministic reward one and all others zero, with the rewarding identity uniform among K arms. With at most T<K distinct queries and no informative features, the greatest probability of recommending the good arm is `(T+1)/K`: a successful query identifies it; otherwise one can only guess among unqueried arms. Thus Bayesian expected simple regret is at least `1-(T+1)/K`, and some fixed arm identity attains at least that much regret. For T=24 this is .6094 at K=64 and .9756 at K=1024. This constructed worst case is not a model of watermark data; it shows why a broad action inventory needs structure, useful priors or sufficient coverage. Repeated queries do not help in that construction.

## 3. Simple regret: a usable elementary bound and its assumptions

Assume n independent fresh reward draws per arm, fixed means, fixed sample counts, and [0,1] rewards. Cross-arm pairing is permitted; independence across the n observations for each arm suffices for the following union bound. Let the recommendation maximize the empirical mean.

**DERIVED using the concentration inequality cited in §2.** For each arm,

`P(|mean_a - mu_a| > e) <= 2 exp(-2 n e^2)`.

Union over K arms gives simultaneous error at most `e = sqrt(ln(2K/delta)/(2n))` with probability at least `1-delta`. On that event, empirical maximization loses at most twice that error:

`r = mu_* - mu_recommended <= min{1, sqrt(2 ln(2K/delta)/n)}`.

Consequently `E r <= min{1, sqrt(2 ln(2K/delta)/n) + delta}`. For a unique best arm and known minimum positive gap Delta, the separate elementary tail bound `P(error) <= min{1, 2(K-1) exp(-n Delta^2/2)}` follows by considering an upward or downward error of Delta/2. Near-ties can make exact identification hard while the cost of a wrong choice remains small; simple regret and best-arm success probability should both be specified when relevant.

At delta=.05, the n required by the first sufficient bound for simple regret no greater than .1 is:

| K | Sufficient n per arm | Total arm-reward observations K*n |
|---:|---:|---:|
| 8 | 1,154 | 9,232 |
| 64 | 1,570 | 100,480 |
| 1,024 | 2,125 | 2,176,000 |

These are conservative sufficient counts, not lower bounds or empirical forecasts. At K=8 and n=4/8/16/24 independent observations per arm, the untruncated bound is 1.698/1.201/.849/.693. At n=60 it is .438. In particular, adding seeds to 16 existing sources does not turn this into hundreds of independent sources for a population claim. The gain from more seeds and the gain from more source diversity address different uncertainty.

**DERIVED explore-then-commit comparison.** If each of K arms is sampled n times and the remaining `T-Kn` plays exploit the selected arm, then

`E R_T = n sum_a Delta_a + (T-Kn) E r`.

This exposes the short-horizon tradeoff without assuming UCB: exploration pays for K*n trials before any repeated exploitation. If the eventual deliverable is only one image or configuration, the corresponding objective is r and collection cost, not this sum of operational rewards. If T is approximately K*n, there is little exploitation horizon to amortize exploration. With only three observations per arm at K=8, the distribution-free .05-confidence bound on r is vacuous.

## 4. Twenty-hour cost envelopes: inventory, caching and rewrites

**MEASURED-AS-SUPPLIED/SOURCE.** BRIEF §2 and [WP1's evidence key](../01-decision-map.md) supply measured native regeneration medians, approximately 1.4 s for a detector row and .25 s for a quality row. Their additive feedback estimate is `c=2.19–3.63 s`, a DERIVED serial planning sum, not measured end-to-end throughput. F5's 732 s shard latency divided by six gives approximately `w=122` whole-device-equivalent seconds under even sharing; the independent Phase A anchor is 119 s. F6's `w=361–723 s` is **UNMEASURED**, only a planning range. Price `.551 USD/hour` is the retained instance price, not a new quote. Twenty hours would be $11.02 at that price.

Define S sources, K actions, n independent feedback seeds per source/action and F native cells. The cost before controls, overhead, feature extraction and training is

`cached candidate cost = S*K*w + S*K*n*sum_(f=1)^F c_f`;

`rewrite-every-rollout cost = N*(w+c)` for N action/seed rollouts with one feedback cell.

An attack that acts on an already published carrier may pay no writer cost. An F5-style writer action pays once per distinct cached candidate and source. A continuous action that changes the mark each time cannot reuse the previous candidate's write. Nothing in the method name makes the cheaper regime applicable.

**DERIVED optimistic capacity ceilings** for a single source, one cell and 72,000 device-equivalent seconds are:

| Regime | Total endpoint calls, c=3.63 to 2.19 s | What this omits |
|---|---:|---|
| Already available carrier/options, w=0 | 19,834–32,876 | Acquisition, features, extra owner calls and attack-specific costs |
| New F5-style mark on every call, w=122 | 573–579 | Controls, overhead, policy optimization and failures |
| New F6-style mark on every call, w=361 | 197–198 | All above; writer cost itself unmeasured |
| New F6-style mark on every call, w=723 | 99 | Same caveat |

For fixed F5-style candidate options, caching changes the inventory substantially:

| K | Cost to write each once and get one feedback, high c | n per arm fitting 20 h, high to low c | .05-confidence simple-regret bound using high-c n |
|---:|---:|---:|---:|
| 8 | .279 h | 2,445–4,053 | .0687 |
| 64 | 2.233 h | 276–457 | .2385 |
| 1,024 | 35.735 h | Infeasible to cover all arms | Unavailable |

The nonvacuous K=8 bound concerns **one fixed source/cell with thousands of genuinely fresh independent seed rewards**. It does not certify a 6.9-point population effect, learn an unseen family, evaluate T4/T5, or describe an efficient practical allocation. If all 1,024 options already exist without writer cost, high-c n=19 yields a bound above one and is vacuous. If every draw rewrites, high-c n=71/8/0 for K=8/64/1024: the K=8 bound is .4031, the K=64 bound is vacuous and full K=1024 coverage is impossible. F6-style write-once plus one feedback for K=8/64/1024 costs .810–1.615 / 6.482–12.918 / 103.717–206.686 h, respectively, under its unmeasured planning range.

**DERIVED 20-hour source-inventory example.** A prospective one-cell screen on 24 fresh sources, K=8 and n=3 uses 192 cached F5-style marks and 576 endpoint calls:

`24*(8*122 + 8*3*3.63)/3600 = 7.0875 h` (about $3.91).

Rewriting for every one of the 576 calls instead costs `576*(122+3.63)/3600 = 20.1008 h`: already beyond 20 h before any controls. At 60 sources the corresponding cached and rewritten totals are 17.7187 and 50.2520 h. These are inventories, not proposed experiments or promises of sufficient evidence. The 24/60 sizes are hypothetical fresh samples; all existing 60 sources are already assigned and cannot be reassigned by this note. Multiple cells, source-disjoint evaluation, T4/T5 and negative controls add cost. No source acquisition is authorized here.

An existing-carrier attacker instead needs only `24*8*3*3.63/3600 = .5808 h` for that same query grid. Even adding one initial F5-style mark per source gives 1.3941 h. This is a structural cost advantage for attacker search, not evidence that useful attack headroom or allowed feedback exists. The original threat may allow no detector queries; a queried attack is a separately declared stronger-access experiment.

## 5. Hindsight headroom, full information and deployment amortization

**MEASURED/DERIVED from [WP3 §§3–4](../03-logged-analysis.md).** Over the seven logged native cells and 60 sources, the C best fixed arm gives 196/420, a cell-known fixed selector 275/420 and a source-and-cell hindsight selector 276/420. Thus within-cell source personalization adds only `1/420=.00238`, or .238 percentage points, over the cell-known selector. For J the corresponding known-cell gap is `2/420=.00476`. Without knowing the future cell, the hindsight per-source C improvement over one global fixed arm is `13/420=.03095`. Most of the larger apparent improvement is regenerator information: `79/420=.18810` from global fixed to cell-known fixed selection.

These are descriptive maxima on a finite measured table, not population limits. The per-source hindsight arm uses outcomes unavailable at decision time. The source-and-cell oracle has more information than a writer selected before an unknown future attack; a policy cannot claim the oracle's value without receiving and paying for that information. These ceilings apply only to the observed F5/v5 action menu and endpoint/quality conditions. They say nothing decisive about novel configurations. WP3's source-dominated variance and survival predictability do not identify differential action benefit, and the clean features may require paying for several candidate marks first.

For the logged T3 attack menu, WP3 reports no unconstrained removal improvement beyond the strongest fixed cell for F5/v5/WAM; VINE-R has five additional oracle removals in 60 sources (8.3 points), before enforcing attack-output fidelity or a query budget. This bounds only that observed menu's realized opportunity, not the expected value of a learned attacker or its security claim.

**DERIVED.** If there is a prospectively fixed finite class Pi of deployable policies and every action outcome is observed on S iid fresh sources, a union bound over policies gives excess expected regret at most `sqrt(2 ln(2*|Pi|/delta)/S)` for empirical policy selection with probability at least `1-delta`. Each source contributes one bounded score per policy, possibly an average over its correlated cells/seeds. The proof is the same simultaneous mean argument in §3. This needs fresh iid source sampling from the intended target distribution and a class fixed before scoring. An unrestricted neural class is not Pi=K, and using the same table to invent and evaluate the class breaks that simple calculation. For the existing development sweep, use direct full-information evaluation and source-disjoint fitting; do not fabricate historical propensities or claim IPS/DR evidence. [C7's inspected literature synthesis](../literature/c7-contextual-bandits.md#existing-data-full-information-selection-not-retrospective-bandit-logs) explains this distinction.

**DERIVED amortization accounting.** Let training/selection cost be B_train, extra deployment cost relative to a strong comparator be d seconds per fresh source and N future sources. Incremental compute is `B_train+N*d`. Accuracy improvement alone does not convert into seconds without a declared utility tradeoff. For a pure speed claim with savings s>0 seconds/source, break-even is `N > B_train/s`. A hypothetical 20-hour training cost requires at least 591 future sources if it saves one whole 122 s write, or 5,902 if it saves 10% of that writing cost. Neither saving is measured. Neural training, tuning, repeated algorithm seeds and failed trials belong in B_train.

For an explicit throughput objective, baseline success probability p0 and per-source cost c0 yield approximately `B_total*p0/c0` expected successful sources. A policy with gain g, cost c_pi and upfront B_train yields `(B_total-B_train)*(p0+g)/c_pi`. With equal deployment cost, it wins only if `g > p0*B_train/(B_total-B_train)`. A fixed-cohort efficacy study uses a different objective and should report extra cost instead of silently substituting throughput. This makes clear why a tiny observed finite-menu headroom cannot automatically repay a training budget.

**JUDGMENT.** Cross-image amortization is plausible only if future sources resemble the training distribution in the aspects that predict action advantage, and the evaluator permits the same decision-time information. Thousands of seeds on one source do not establish that condition. Thousands of images within the same three families do not establish an unseen-family reward law. If family identity is unavailable at writing time, one must preregister a deployment mixture or a worst-family objective. If it changes adversarially, stationary UCB's theorem does not apply. An adversarial regret guarantee against the best fixed action would still not provide an oracle for a genuinely unseen family or an unobserved feasible action.

## 6. Existing Stage P: allocation benefit already has a strong baseline

**SOURCE/project fact.** The frozen [Stage P protocol](../../tifs-20261028/stage-p/PROTOCOL.md), allocation/ranking/check sections, uses eight candidates, three elimination rungs with cumulative 4/8/16 tuning sources, and eight separate veto-check sources for one nominated winner. Earlier rows are reused. Candidate tuning writes are `8*4+4*4+2*8=64`; the veto check adds eight, giving 72 candidate writes. The protocol's complete maxima are 136 marked images, 136 C0 source-directory units and 3,264 native attempts, including required controls. Its ranking is lexicographic across C/J/cells and quality, with hard eligibility and incomplete-result rules. No result was read and no change is proposed.

**DERIVED.** A full fixed grid on 16 tuning sources would use `8*16=128` candidate writes. The existing elimination schedule halves that candidate tuning inventory to 64, before shared controls and veto evaluation. That economy is already part of the non-RL comparator. There are 16 tuning source units, not 768 independent tuning sources merely because 64 candidate writes each produce 12 native calls. The rungs offer only three adaptive allocation decisions. Training a sophisticated meta-controller for this single search must repay its additional information, optimization and verification costs relative to the existing rule.

**SOURCE.** In the idealized stationary scalar-reward model, Sequential Halving's Theorem 4.1 bounds error by `3 log2(K) exp[-T/(8 H2 log2(K))]`, where arms are mean-ordered, the best is unique and `H2=max_(i>=2) i/Delta_i^2`. Its algorithm allocates an equal pull budget to each elimination round. [Karnin, Koren and Somekh, ICML 2013, §2 and §4 Algorithm 2/Theorem 4.1, pp.1240, 1242–1243](https://proceedings.mlr.press/v28/karnin13.pdf).

**DERIVED applicability check.** For K=8 and a hypothetical gap .25 to each inferior arm, H2=128. Even T=64 yields an untruncated error bound 8.8144, so the meaningful bound is just one. The formula requires about 15,953 total pulls to reach a .05 upper bound under those hypothetical gaps. This is conservative theorem arithmetic, not a lower bound, estimated Stage P gap or reason to expand its budget. Stage P does not instantiate that exact scalar iid algorithm: it reuses cumulative source panels, has a different budget-per-rung pattern, lexicographic rankings, hard gates, dependent endpoints and source sampling constrained by the project. Therefore **the theorem must not be attached as a confidence guarantee to Stage P at all**. The numerical illustration only shows that even the simpler textbook abstraction would not offer a useful certificate at such tiny counts.

**JUDGMENT.** A future allocation method would need a prospectively frozen, repeated selection task distribution and evidence that it saves total cost or finds better feasible configurations at fixed cost. It must beat the existing halving schedule, uniform/fixed allocation and a simple cost-aware racing rule. Changing the frozen F6 run is outside this session. GO, failure and RESOURCE_STOP would change later empirical motivation, but none retroactively supplies the stationarity, horizon, action coverage or source-disjoint generalization assumptions used above.

## 7. Reproduction and conclusion for integration

All tabulated costs and bound substitutions are DERIVED planning quantities. The following stdlib fragment reproduces the central 20-hour table without accessing data; `math` and arithmetic suffice. Run only with the permitted interpreter and `-I` if rechecking is needed.

```python
import math
B, w, c, delta = 20*3600, 122, 3.63, .05
for K in (8, 64, 1024):
    n = math.floor((B-K*w)/(K*c)) if B >= K*w else 0
    regret = min(1, math.sqrt(2*math.log(2*K/delta)/n)) if n else None
    n10 = math.ceil(2*math.log(2*K/delta)/(.1**2))
    print(K, K*(w+c)/3600, n, regret, n10, K*n10)
for w_call in (0, 122, 361, 723):
    print(w_call, [math.floor(B/(w_call+cf)) for cf in (3.63, 2.19)])
```

**JUDGMENT for WP4.** Bandits deserve consideration for partial-feedback allocation or inexpensive attack queries; a truly state-changing writer controller requires a different sequential model. Existing complete-arm logs favor supervised/full-information comparisons. For one-off K=8 selection, the exploit horizon is small and halving already captures a major allocation benefit. At K=64/1024, action structure and caching become decisive. Cross-source learning could change this assessment, but only with fresh sources, equal total budgets, decision-time features, an independently evaluated reward gap and a stated deployment distribution. The bounds above establish neither RL superiority nor impossibility; they identify exactly which finite budgets, assumptions and kinds of evidence could make a meaningful claim.

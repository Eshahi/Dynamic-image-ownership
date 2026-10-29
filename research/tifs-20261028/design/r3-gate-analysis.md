# Round 3 gate analysis and proposed decision profile

Status: PRE-OUTPUT ANALYTICAL DESIGN; no scientific output, simulation, model pass, timing or approval. Author: Codex design agent, 2026-10-29. The effective profile remains `round1`. The user must choose a proposed profile before server outputs, with the choice recorded by Claude. The accompanying [probability artifact](r3-gate-probabilities.json) contains hypothetical finite-sum calculations, not experiment results.

## Recommendation

Recommend bounded Stage P selection of the writer and budget, then the `round3-proposed` thesis profile below. Preserve the 12/16 foreign-cell absolute bars and every primary negative rule. Move the ablation-superiority requirement to a secondary mechanism analysis. Replace parity to the retained, very small F5 distortion budget with an explicit F5-objective control at the selected candidate's optimization budget, retaining paired measured-quality noninferiority to that control. Keep K3 excluded from gradient optimization in the executable package. The [K3-in alternative](r3-k3-in-deferred.md) is a separately deferred design option until its native surrogate is implemented and rehearsed. Keep the Round 2 VINE-B article comparison numerically unchanged.

The proposed gate asks whether a quality-controlled F6 construction delivers a useful cross-family improvement, while the original gate additionally demands that two specific mechanisms lose by large margins. A strong ablation can invalidate the latter mechanism claim without invalidating the former empirical finding. This is a change in claim, not free statistical power. Adding the budget control can also make the proposed profile harder than the original in some outcomes; a more permissive label is not guaranteed.

## What probability is being calculated

For one endpoint, arm and native cell, let `s` be the probability of a positive **seed**, and `p` the probability that a randomly sampled **source has at least two positive seeds out of three**. These are different parameters. Under independent, identically distributed seeds,

`p = 3 s^2 (1-s) + s^3 = 3 s^2 - 2 s^3`.

If the brief's `p` already means per-source retention, do not apply this transformation again. The analysis defaults to source-majority `p`. Under independent, identically distributed sources, the number of positive source majorities is `X ~ Binomial(16,p)`, and

`B_k(p) = P(X >= k) = sum[x=k..16] choose(16,x) p^x (1-p)^(16-x)`.

These are exact finite sums, evaluated in floating point. No random simulation is used. A fixed development cohort does not literally resample itself: the probability refers to a hypothetical population of comparable development sources and seed draws. The observed gate will be a deterministic count. Neither a source population nor its rates has been estimated by this analysis.

There is **no identified unconditional whole-gate probability** from one retention rate per arm. Quality failures, clean F, negative events, R0 retention, missingness, arm pairing, endpoint nesting and cross-cell dependence are also required. Precisely,

`P(GO) = P(foreign efficacy) * P(all remaining required conditions | foreign efficacy)`.

The second factor is unknown, bounded by zero and one; setting it to one gives the efficacy-only scenarios below. In these hypothetical models the omitted gates pass identically. This is not an estimate of efficacy conditional on an actually observed quality/security pass, which could change the source-count distribution. The unknown factor must not be replaced by an unlabelled guess or by multiplying marginal gate probabilities without a joint model. In particular, the numeric grids are not calibrated predictions of Stage S success. The separate subjective estimates at the end are research judgments, not values inferred from these grids.

## Absolute gate grid and endpoint dependence

| Source-majority p | One cell >=12/16 | Three independent cells >=12/16 | One cell >=11/16 | One cell >=10/16 |
|---:|---:|---:|---:|---:|
| .50 | .0384 | .000057 | .1051 | .2272 |
| .60 | .1666 | .0046 | .3288 | .5272 |
| .65 | .2892 | .0242 | .4900 | .6881 |
| .70 | .4499 | .0911 | .6598 | .8247 |
| .75 | .6302 | .2503 | .8103 | .9204 |
| .80 | .7982 | .5086 | .9183 | .9733 |
| .85 | .9209 | .7811 | .9765 | .9944 |
| .90 | .9830 | .9499 | .9967 | .9995 |
| .95 | .9991 | .9974 | .9999 | 1.0000 |

The full JSON includes .30/.40 and the >=13 alternative too. At p=.75, meeting an observed 75% bar is not a 75% probability event, and three difficult cells reduce the independent-cell probability to .25 before comparative or quality gates. A method probably needs appreciably more than .75 true source retention in every cell to pass this small conjunctive screen reliably.

The table is for one endpoint. **J implies C seed by seed and therefore source majority by source majority.** With complete valid references, the absolute C gate is redundant given the absolute J gate. Squaring the table to model independent C and J would violate that nesting. However, J gains do not imply C gains: a comparator can have many content-consistent but wrong-original-code C positives. All C and J comparative gates remain necessary.

For three cell-pass marginals `r1,r2,r3`, arbitrary dependence gives the Frechet bounds

`max(0,r1+r2+r3-2) <= P(all three) <= min(r1,r2,r3)`.

At p=.80 these are [.3947,.7982], with .5086 only under independent cells. Shared images, frozen reader and shared model families make dependence plausible. The profile JSON reports these bounds alongside the independent-cell illustration. It neither claims independence nor interprets the upper bound as expected performance.

Passing 12/16 is a practical screen, not proof that population retention is at least 75%. For example, the one-sided exact 95% binomial lower bound after 12/16 is approximately .5156. No repeated-seed denominator makes this n=48 evidence. Dropping to 11/16 changes the observed practical floor to 68.75%, and 10/16 to 62.5%. Such alternatives can support a weaker partial-retention claim, but cannot preserve the present broad 75%-of-sources screen claim. **Do not recommend lowering 12/16.**

## Seeds, sources and correlation sensitivity

A beta-binomial seed model makes the dependence assumption explicit. Draw each source's latent seed success probability independently from `Beta(a,b)`, with mean `s` and seed intraclass correlation `rho=1/(a+b+1)`. Compute the three-seed majority probability by the exact beta-binomial probabilities for counts two and three. This is a sensitivity family, not a fitted description.

| Per-seed s | Seed ICC | Per-source majority p | One-cell >=12 | Three independent cells |
|---:|---:|---:|---:|---:|
| .70 | 0 | .7840 | .7480 | .4185 |
| .70 | .20 | .7448 | .6114 | .2285 |
| .70 | .50 | .7140 | .4996 | .1247 |
| .70 | 1 | .7000 | .4499 | .0911 |
| .80 | 0 | .8960 | .9801 | .9415 |
| .80 | .20 | .8512 | .9232 | .7867 |
| .80 | .50 | .8160 | .8437 | .6006 |
| .80 | 1 | .8000 | .7982 | .5086 |

Perfectly correlated seeds buy no majority amplification. This explains why an impressive per-seed intuition can substantially overstate the source-majority gate's reliability. Correlation between only three seeds is not itself estimable robustly from a tiny screen.

Separately, the JSON uses a beta-binomial **source-count** model to illustrate a shared cohort difficulty effect. At source mean p=.90, one-cell success falls from .9830 under independent sources to .9422/.8945/.8697 at source ICC .05/.15/.30. At p=.60 it instead rises from .1666 to .2446/.3321/.4076: overdispersion can help a low-mean arm cross a threshold by chance while hurting a high-mean arm's consistency. Correlation does not uniformly lower pass probability. Independent fixed source-specific rates would give a Poisson-binomial count; independent source-specific latent draws with a common marginal p still give a binomial marginal. Neither is the shared cohort beta-binomial model. Source, seed and cross-cell dependence must not be conflated.

## Exact paired-gain calculation and dominant conjuncts

For candidate source-majority indicator `A` and comparator indicator `B`, define `P(A=1)=p`, `P(B=1)=b`, `P(A=B=1)=r`, with `max(0,p+b-1)<=r<=min(p,b)`. Across iid source pairs, conditional on candidate count `X=x`,

`Y | X=x = Binomial(x,r/p) + Binomial(16-x,(b-r)/(1-p))`,

where the two binomials are independent. Empty groups handle p=0 or p=1 without division by zero. Therefore an absolute bar a and net gain g have exact joint probability

`sum[x=a..16] P(X=x) P(Y<=x-g | X=x)`.

For several controls, multiply their conditional CDFs inside this sum **only under conditional independence of their source indicators given the candidate's indicator**. The script states and uses this assumption. It does not falsely multiply unconditional gain probabilities that share the same candidate. A source pairing matters even though the frozen gate uses net counts instead of discordant-pair significance tests.

The grid interpolates `r=p*b + lambda*(min(p,b)-p*b)` between independent arms and maximal positive overlap. `lambda` is an overlap parameter, not Pearson correlation. Two controls remain conditionally independent given candidate source state in this particular construction; it is not a model of all real control dependencies. For C/J the profile scenarios assume **C=J for every source and arm**. That special case respects nesting, but excludes wrong-original-code C-only recovery; it is not a full model of the actual endpoints. The formula can be applied separately to either endpoint for marginal sensitivity, with the joint pass bounded by the smaller marginal.

The current threshold arithmetic is revealing without any probabilities. In an SDXL cell with candidate count 12, retained F5 must be <=8 and **each** ablation <=9. Even a perfect 16/16 candidate cannot gain four over an F5 count above 12, or three over an ablation above 13. In K3, a 12-count candidate requires F5<=9 and both ablations<=11. A good codec-only control can therefore kill a successful empirical method. Such failure is meaningful for attributing improvement specifically to noisy-codec writing, but is not evidence that native regeneration retention is absent.

For illustration only, take candidate source rate .80, retained F5 .30, each of two ablations .70, budget F5 .50, all equal across the three foreign cells. Set every other gate to pass identically in this toy model and use C=J. These rates are hypothetical, not historical estimates:

| Foreign efficacy profile | Independent arms and cells | Maximal candidate/control overlap; independent cells |
|---|---:|---:|
| Current: F5 gains 4/4/3 and ablation gains 3/3/1 | .0173 | .0010 |
| Only make ablation gains secondary; retain F5 gains | .4983 | .5037 |
| Proposed: gains 4/4/3 against retained and budget F5 | .2845 | .2951 |

At candidate p=.90 with these same hypothetical control rates, the corresponding independent-arm probabilities are .1568, .9437 and .7364. These differences show *which conjunct* binds in that scenario. They do not show that the recommended method will attain p=.90, or that the true controls have those rates. If matched-budget F5 improves as much as F6, the new attribution comparison properly prevents GO. For other grid rows the relative ordering can differ.

Auxiliary conjuncts can also dominate. If a source has .99 probability of strict clean quality, all 16 pass with probability .8515; all 48 source/writer pairs pass with .6173 **only under their independence**. A .99 clean F probability gives P(>=15/16)=.9891. If each independent source cluster has .01 probability of *any* qualifying negative event, zero events in 16 occurs with probability .8515; at .05 it is .4401. Multiple queries on one image do not create thousands of independent specificity trials. Relative paired median quality also needs its own joint metric distribution; no retention p can supply it. Inventory and resource failures are separate from these scientific probabilities.

## Proposed profile and its claim changes

| Item | `round1`, unchanged effective default | `round3-proposed`, user-selectable only | Consequence |
|---|---|---|---|
| Absolute foreign retention | Both C/J >=12/16 in R1 .1, R1 .2, K3 .2 | Same | Preserves practical cross-family retention bar |
| Retained F5 gains | Both C/J >=4,4,3 | Same | Historical construction comparison remains explicit |
| Same-budget F5 gains | Not present | Both C/J >=4,4,3 against `f5-budget` | Controls for giving the writer more distortion budget |
| R0 retention | Both C/J net loss vs retained F5 <=1 | Same | Retains original-family performance protection |
| Candidate clean quality/F | Strict quality all16, F>=15 | Same | Never trades away the strict clean bar |
| Budget control clean quality/F | Not present | Strict quality all16, F>=15 | Failed control cannot support clean attribution |
| Retained F5 paired quality | LPIPS delta<=.005, PSNR delta>=-1 dB | Report, no primary conjunct | Loses claim of near-parity to retained F5's tiny distortion |
| Budget F5 paired quality | Not present | LPIPS delta<=.005, PSNR delta>=-1 dB | Adds measured practical noninferiority to budget control |
| Ablation gains and ablation clean quality/F | All primary conjuncts | Secondary mechanism outcomes, fully measured | Loses automatic claim that every tested mechanism control is worse |
| Primary negative events/inventory | Zero qualifying events; complete required evidence | Same | No missing-negative or partial-inventory escape |
| K3 gradient optimization | Excluded | Excluded in implemented recommendation | K3 is optimization-excluded; Stage P K3 selection makes it selection-seen |
| VINE-B article comparison | Round 2 rule | Same numerical comparison | Easier thesis gate cannot manufacture an article edge |

Strict clean quality always means PSNR>35 dB, SSIM>.9, LPIPS<.1; numerical equality at a strict boundary fails. The entire profile is a prospective development screen, not a formal statistical noninferiority or superiority test. Candidate and control clean F/quality limitations should also be reported even if one gate fails. A control that ties F6 in a secondary ablation has not been shown equivalent; it simply does not establish F6's mechanism advantage.

### Budget matching is not measured quality matching

Use the retained F5 objective with surrogate disabled, keeping semantic views, payload, reader, clean/refinement schedule, fragile writes and projection convention fixed except for the declared robust-stage budget. Preserve retained F5 r2 untouched as a separate arm. At the original 52 dB budget the implementation must exercise the same F5 robust optimization primitive and arguments; pure control-flow tests can verify that dispatch, and actual numerical equivalence remains a server rehearsal check. An adapter label alone proves nothing.

Match the selected F6 robust-stage target and the fixed 58 dB refinement target in `f5-budget`. The proposed 52/46/42/38 dB robust targets permit approximately 1, 4, 10 and 25.1 times the 52 dB squared-error budget, respectively, before the rest of the writing pipeline. A target is a constraint, not the final measured PSNR; quantization, fragile writing and refinement can alter the final image and different objectives can leave different fractions of the budget unused. Call this **matched optimization budget**, not matched quality.

Requiring paired measured clean LPIPS/PSNR noninferiority to this budget control prevents a candidate's success being credited solely to a visibly worse measured quality within a loose absolute threshold. It still does not imply equal perceptual quality, equal spatial distortion, equal SSIM or human equivalence. Preserve all distributions and missing human quality status. If measured noninferiority fails, report a retention-quality tradeoff; do not adjust the control's budget after observing Stage S. A truly equal-measured-quality frontier would need a new prospectively specified calibration study on tuning sources and more writes; it is outside this bounded package.

This control is not computation-matched. It preserves F5's 200 reader-gradient evaluations, whereas F6 uses 350 plus up to 150 codec/UNet paths. The requirement that 52 dB delegates to the unchanged F5 primitive prevents silently extending the control's optimization schedule. A gain over this control controls the declared perturbation budget and measured quality, but cannot distinguish the surrogate mechanism from extra optimization effort. The existing F6-codec/generic controls share the 350-reader schedule and remain informative; making their superiority secondary explicitly forfeits a mandatory mechanism-attribution claim. Report these counts beside retention and time, with no claim of compute efficiency.

### K3: optimization, selection and unseen claims

Adding K3 to optimization can plausibly increase its retention, but the probability analysis cannot quantify that effect. An unchanged p means an unchanged numerical gate probability; a claim of increased p requires server evidence. K3 has already been historically inspected, so it is never discovery-unseen. Under Stage P selection using K3 .2 outcomes, even K3-out is **selection-seen but gradient-optimization-excluded**. Calling it simply unseen would be incorrect.

A faithful K3-in writer requires its actual codec, transformer/denoiser, conditioning, scheduler/noise parameterization, differentiation and memory policy. An SDXL UNet x0 implementation or a K3 codec-only pass is not a native K3 denoiser-aware surrogate. Do not enable a boolean option that silently ignores K3, reuses another family's denoiser or relabels a codec surrogate. Defer this branch explicitly with `not implemented / not executable` status until native equivalence and resource rehearsal are implemented. Stage P's eight executable configurations can therefore remain two surrogates by four budgets, K3-out only. Stage C's prospective SD3.5 family must stay outside optimization, selection and rehearsal if it is to carry the fresh-family generalization claim.

### Article bar and alternatives not recommended

Changing quality parity from retained F5 to its budget control does not force any change to the VINE-B numerical article rule: the selected F6 must still lose at most one source on both C/J in every cell, satisfy paired LPIPS/PSNR noninferiority to VINE-B, and have either a same-foreign-cell gain of three for both endpoints or the specified joint clean-quality advantage. The active thesis gate remains a prerequisite. Candidate identity and approved thesis profile should be disclosed, but numerical VINE-B margins should not move.

A larger F6 distortion budget may improve retention while making VINE-B quality noninferiority harder. This is precisely the tradeoff that the article comparator should expose. There are no VINE-B Stage S outcomes; VINE-R's known-message presence is not blind q/tag/h recovery. It is unjustified to lower 12/16 using what VINE-B is "likely" to reach. If both methods fail that threshold, report that practical limitation rather than declare a new winning dimension after outputs.

The JSON also evaluates the article comparison block under a C=J independent-cell toy model, with all its quality conditions fixed to pass. For candidate and VINE source rates both .90, independent paired arms give .1011 probability of a retention edge plus noninferiority (and foreign absolute bars); perfectly overlapping pairs give zero retention-edge probability. A separately satisfied quality edge changes these to .4489 and .9499. These are comparison-block probabilities, **not conditional probabilities given thesis GO**, since conditioning on the thesis gate would change the candidate count distribution. They illustrate why the unchanged article hurdle can dominate even after a promising thesis screen.

## Subjective research judgment, separate from the calculations

Conditional on an authorized, complete server execution without resource or infrastructure failure, my current judgment is approximately **15%** for a complete thesis numerical GO with the original untuned writer/current conjunction, with a broad **5-30%** plausible judgment range. For the recommended bounded tuning, denoiser-aware option, budget control and proposed gate, I judge approximately **35%**, with a **15-55%** range. These are deliberately rough personal estimates before GPU feedback, not confidence/credible intervals, a posterior, power calculations or a fitted extrapolation. The earlier 25% design estimate was also subjective; the lower present current-profile estimate reflects closer inspection of the full conjunction, not new scientific evidence.

The direction of improvement is credible: tune on separate development sources, expose the denoiser Jacobian rather than decode only noisy latents, and allow a controlled larger perturbation budget. The size is uncertain: one-step x0 is still not multi-step regeneration, gradients can be unstable, final quantization can erase tiny margins, the fragile channel can fail clean F, a stronger F5-budget can erase attribution, and optimization-excluded K3 can remain the bottleneck. No monotonic guarantee follows from more distortion or additional surrogate computation.

For the **separate article conditional-GO label**, including a thesis GO and the preserved VINE-B comparative edge, rough current/recommended estimates are only **5% / 10%**, with broad **1-15% / 2-25%** judgment ranges. These are unconditional with respect to thesis scientific success but conditional on complete execution, as above. They are not probabilities of paper acceptance or even a complete publishable result. Novelty clearance, human assessments, a valid binding evaluation and approved fresh Stage C confirmation remain outside that label. A thesis GO without an article edge is a legitimate and informative result.

## Decisions for the user: text for the amendment

1. **Gate:** keep `round1` effective, or select `round3-proposed` before outputs; recommended proposed profile preserves absolute/negative bars but replaces automatic mechanism superiority with controlled empirical improvement.
2. **Budget:** permit Stage P to select among robust targets 52/46/42/38 dB, with refinement fixed at 58 and an F5-objective control at the selected budget; recommendation yes, accepting loss of quality parity to retained F5 while requiring measured noninferiority to the budget control.
3. **Ablations:** make gains and their clean-quality/F eligibility secondary while retaining all measurements; recommendation yes, accepting that a successful screen may not isolate a unique denoiser/noise mechanism.
4. **K3:** use optimization-excluded K3 now, or defer execution for a separately implemented native K3-in option; recommendation K3-out, disclosed as selection-seen under Stage P, with fresh-family claims reserved for SD3.5 Stage C.
5. **Absolute bar/article:** retain 12/16 and the unchanged VINE-B comparative rule; recommendation retain both, with no claim-preserving lowering available.

## Reproduction and verification

The approved stdlib invocation is:

```text
W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe -I scripts/tifs_gate_probability.py --self-test --output research/tifs-20261028/design/r3-gate-probabilities.json
```

Identity checks passed: binomial/beta-binomial normalization and endpoints, the three-seed majority polynomial, independent double-binomial gain sums, and a separate small paired-outcome dynamic program against the conditional-sum formula. No retained outputs or images are read. All probabilities in the artifact are analytic assumptions, explicitly marked as such. The script reads no current gate configuration, so its illustrative profile names do not select or authorize a production profile. The analyzer/config remain owned by the session lead; this document specifies the proposed scientific meaning.

# WP4: estimator variance and the equal-compute question

**Status:** research-only derivation, 2026-10-30. `PHASE_B_JOURNALS=off`; F6 outcomes unseen. No candidate is scored here. Labels distinguish MEASURED saved-development summaries, SOURCE inspected literature/code semantics, DERIVED mathematics under stated assumptions, and JUDGMENT implications. Only tiny stdlib arithmetic ran; no model, image or timing experiment ran.

## 1. Specify the objective before comparing estimators

**SOURCE:** [reader semantics](../context/wp1-reader-semantics.md) and [WP3](../03-logged-analysis.md) distinguish decoded normalized-correlation margin from generic branch-selected margin, content-compatible C, and original-code J. C needs both decoding and content consistency; J also needs the original q. Improving decoded margin alone need not improve either endpoint. The retained reader includes hard bits, threshold decisions, angle-grid selection and RGB8 rounding; its deployed implementation exposes no end-to-end autograd path. F5's existing differentiable chip-loss PGD is already gradient optimization.

**DERIVED setup:** condition on one development source x and one regenerator cell. Let action a control a specified writer/loop setting and let omega denote regeneration randomness. Write reward R=f(a,omega); the same derivation applies separately to a soft reward or an exact binary endpoint. A Gaussian policy has a=theta+sigma*z, z~N(0,I_d), fixed sigma>0, with omega independent of policy sampling. Define J_sigma(theta)=E[f(theta+sigma*z,omega)]. This is the stochastic-policy/smoothed objective; deploying the mean action targets a different quantity and needs its own evaluation. Action scaling and physical constraints must be fixed before choosing d or sigma.

**SOURCE:** score-function estimation needs differentiable policy probabilities and valid interchange of derivative/integral, but no reward derivative. Ordinary pathwise differentiation additionally needs an appropriate differentiable sampling/reward path and justified interchange. There is no universal variance ordering. [Mohamed et al., JMLR 2020, §§4.2–4.3, 5.2–5.3](https://www.jmlr.org/papers/volume21/19-346/19-346.pdf).

**DERIVED:** with s=grad_theta log pi(a)=z/sigma and action-independent baseline b,

`g_SF=(R-b)z/sigma`, `E[g_SF]=grad J_sigma`, since `E[s]=0`.

When valid, `g_PW=grad_a f(theta+sigma*z,omega)` has the same expectation. If f explicitly depends on theta outside a, include its direct derivative in both estimators. Neither a score-function identity nor a Gaussian action alone makes an algorithm RL: the same estimator underlies non-RL Gaussian smoothing/NES. The decision problem and training procedure determine the classification.

## 2. Exact local-linear Gaussian toy, including the optimal baseline

**DERIVED toy, not a fitted reward model:** around theta0 let

`f(a,epsilon)=m+h^T(a-theta0)+epsilon`, `E[epsilon]=0`, `Var(epsilon)=v`, `epsilon independent of z`.

Here h is the unknown action gradient, not the observed standard deviation of rewards. Evaluate estimators at theta=theta0. The policy score is z/sigma, and grad J_sigma=h. Minimize trace covariance over one scalar constant b by minimizing `E[(R-b)^2 ||s||^2]`. Differentiation gives

`b*=E[R||s||^2]/E[||s||^2]=m`.

The last equality uses symmetry `E[(h^T z)||z||^2]=0` and independent zero-mean epsilon. Outside this toy, the weighted optimum need not equal mean reward. This weighted-baseline principle agrees with [Greensmith et al., JMLR 2004, Theorem 13, pp.1489–1490](https://jmlr.csail.mit.edu/papers/volume5/greensmith04a/greensmith04a.pdf); the vector trace calculation here is explicit rather than an invocation of that paper's POMDP assumptions.

At b=m, `g_SF=(h^T z)z + epsilon*z/sigma`. Gaussian fourth moments give

`E[(h^T z)^2 zz^T]=||h||^2 I + 2hh^T`, so

`Cov(g_SF)=(||h||^2+v/sigma^2)I + hh^T`.

Thus for n independent samples,

`E||mean(g_SF)-h||^2 = [(d+1)||h||^2 + d*v/sigma^2]/n`. **(1)**

For arbitrary deterministic b, add `d*(m-b)^2/(n*sigma^2)`; all cross terms vanish by symmetry/independence. A negative intercept therefore wastes variance if left uncentered, but gives no evidence of gradient direction. A baseline learned from independent or prior data stays unbiased; a naive same-batch sample-mean baseline produces expectation `(1-1/n)h` in this iid setting. Leave-one-out centering removes that particular shrinkage; baseline learning still costs data and computation.

Pathwise differentiation in this exact toy yields `g_PW=h`, so its variance is zero. This is an illustrative consequence of action-independent additive noise, **not** a claim that native diffusion gradients are noiseless. The `(d+1)||h||^2` term in (1) is directional sampling variance even when v=0; the WP3 noise-only expression omits it deliberately. For h!=0, relative trace RMS at most eta requires

`n >= [(d+1)+d*v/(sigma^2*||h||^2)]/eta^2`. **(2)**

This is a gradient-estimation error criterion, not a learning-curve or success-probability guarantee. If h=0, relative error is undefined and no local improvement follows from lower variance.

**DERIVED dimension caveat:** at fixed per-coordinate sigma, both the directional term and independent-noise term scale with d, but expected exploration energy is `E||a-theta||^2=d*sigma^2`. Holding that energy at rho^2 instead gives `sigma^2=rho^2/d` and noise term `d^2*v/rho^2`. This describes isotropic unstructured search in the chosen coordinates, not an impossibility bound on structured policies. A low-dimensional basis changes the reachable actions and must be compared at the same physical distortion/quality constraint.

For a network mean mu_theta with local Jacobian A=d(mu)/d(theta), parameter-gradient covariance is `A^T Cov(g_SF) A`. Its trace at the optimal toy baseline is `(||h||^2+v/sigma^2)||A||_F^2+||A^T h||^2`; use this rather than substituting the network's parameter count for d. More generally the independent additive-noise contribution is `v*trace(Fisher)/n`. Rescaling policy coordinates changes these numbers.

## 3. What the measured magnitudes do and do not identify

**MEASURED:** [variance note](../analysis/variance-note.md), Stage2 union, F5 R1 .2: mean decoded margin -3.9109; pooled within-source variance v=0.15674 correlation-units squared; 60 complete sources, three prescribed seeds. [WP3](../03-logged-analysis.md) reports 0/180 observed C successes there. Source SS dominates, but neither source variation nor seed variation identifies action sensitivity.

**DERIVED conditional substitution:** treating v as homogeneous independent additive noise for a *new* local policy gives seed SD 0.39590. Substituting pooled m as a representative intercept gives `m^2/v=97.58`: without centering, the intercept term alone is 97.58 times the additive-noise term. This is not a measured gradient-variance ratio; source-specific intercepts differ, action dependence is unknown, and the gradient term remains. The margin deficit is about 9.88 within-source SDs, only a descriptive scale comparison: three fixed seeds and heterogeneous sources do not justify a Gaussian tail probability or a bound on achievable margin change.

For illustration only, fix sigma=1 in explicitly chosen action units and target **noise-component** trace RMS tau=.1 correlation-gradient units. Equation (1)'s noise component requires `n>=ceil(d*v/(sigma^2*tau^2))`:

| d | n, noise component only | Existing-carrier feedback, device-hours | Rewrite F5 each rollout, device-hours |
|---:|---:|---:|---:|
| 8 | 126 | .077–.127 | 4.347–4.397 |
| 64 | 1,004 | .611–1.012 | 34.635–35.037 |
| 1,024 | 16,051 | 9.764–16.185 | 553.715–560.135 |

**SOURCE/DERIVED cost:** times use [WP3's accounting](../analysis/variance-note.md): 2.19–3.63 seconds feedback, approximately 122 additional device-equivalent seconds to rewrite an F5 mark, and $0.551/device-hour. Multiply hours by .551 for the corresponding illustrative USD. These are **one source, one gradient estimate**, not a training budget, and omit policy updates, tuning, baseline fitting and final evaluation. The 732-second F5 observation is six-shard latency; 122 is an approximate device-equivalent amortization, not serial latency. Additive timer scopes are planning approximations. A policy that directly changes pixels need not pay an entire F5 rewrite; a policy selecting F5 settings does. Cost follows the actual action semantics.

At sigma=.1 the unrounded noise-only n is 100 times larger (ceilings: 12,540; 100,314; 1,605,018). Increasing sigma to avoid this is not free: it can violate fidelity, change the smoothed objective or leave the local-linear region. These arbitrary scales are sensitivity examples, not recommended hyperparameters or lower bounds for every estimator. Caching K fixed candidate marks costs `K*w + K*n*feedback`, whereas changing/rebuilding a mark every rollout costs `N*(w+feedback)`; neither regime should be silently substituted for the other. No F6 cost or output is inferred.

**DERIVED non-identification witness:** replace the toy with random slopes,

`f(a,omega)=m+(h+u)^T(a-theta0)+epsilon`, `E[u]=0`, `Cov(u)=S`,

with u, epsilon, z mutually independent. At the logged fixed action theta0, every h and S gives the same reward distribution m+epsilon and the same v. Yet `g_PW=h+u` has trace variance `trace(S)`, while the optimal-baseline score estimator has

`trace Cov(g_SF)=(d+1)||h||^2+(d+2)trace(S)+d*v/sigma^2`. **(3)**

Therefore fixed-action reward variance cannot identify either gradient signal or pathwise variance. Real action-dependent diffusion noise can be still more complex; even the assumption that retained v transfers to changed actions is untested. The recorded C floor does not establish a zero gradient of success probability under a new policy.

## 4. Discontinuities, surrogate bias and a possible hybrid

**DERIVED counterexample:** take `f(a)=1[a>=0]`, `a~N(theta,sigma^2)`. Then `J_sigma=Phi(theta/sigma)` and `dJ_sigma/dtheta=phi(theta/sigma)/sigma`, but differentiating the indicator samplewise gives zero almost everywhere. The missing boundary contribution invalidates naive pathwise differentiation. Score-function estimation remains unbiased under its regularity conditions. This is why hard C/J decisions, quantization and binding gates cannot be treated as a free exact pathwise reward.

**JUDGMENT for this reader:** a continuous decoded-margin loss can supply dense feedback while C is at its observed floor, but it changes the objective and omits binding unless binding is represented separately. A zero binary batch with zero baseline supplies no observed direction; subtracting a nonzero baseline only creates sampling noise in that batch. It does not prove that all reachable actions fail. Keep C, J, strict quality, C0/wrong-owner and T4/T5 as frozen assessment endpoints.

**DERIVED:** differentiating a smooth reward surrogate optimizes its own expectation, with target-gradient bias `beta=E[g_surrogate]-grad J_target`. A straight-through derivative, truncated backpropagation, substituted regenerator or frozen intermediate state introduces a further approximation unless an exact identity is proved. Small surrogate-value error does not imply small derivative error. Training against a surrogate family also leaves a family-transfer error which more rollout averaging cannot remove.

**SOURCE:** [DRaFT §4/Algorithm 1](https://arxiv.org/html/2309.17400v2) backpropagates differentiable image rewards and explicitly uses stop-gradient truncation for DRaFT-K; checkpointing trades memory for recomputation. [DDPO §4.3](https://arxiv.org/html/2305.13301v4) uses trajectory score functions with terminal rewards. Neither paper tests this retained reader or proves its equal-compute ordering. The [C8 cards](../literature/c8-diffusion-rl.md) also preserve AlignProp's historical/subsumed status; its timing advantage must not be imported as a watermark speed multiplier.

**DERIVED rescue worth retaining, without a novelty claim:** for a fixed differentiable control variate q(a), Gaussian integration by parts gives the unbiased hybrid

`g_hybrid = grad_a q(a) + (f(a,omega)-q(a))*z/sigma`. **(4)**

Its expectation is grad J_sigma even when f is discontinuous, provided q and its derivative satisfy the boundary/integrability conditions. Unlike blindly using grad q, the score residual corrects surrogate bias. If q(a)=m+h^T(a-theta0) were exact for the toy mean, (4) has trace variance only `d*v/sigma^2`, eliminating the directional term. Learning such q is not free, its fit must be fixed/independent of the evaluation sample to justify this simple identity, and a poor q can increase variance. This is a control-variate comparator, not a new RL contribution.

**DERIVED pairing:** an antithetic difference `[f(theta+sigma*z,omega+)-f(theta-sigma*z,omega-)]z/(2*sigma)` uses two evaluations. Under the linear toy, shared identical additive epsilon cancels; independent epsilons leave noise trace `d*v/(2*sigma^2)` per pair, with the same directional term. Shared seed labels need not imply this additive cancellation: [WP3](../analysis/variance-note.md) observed paired F5-minus-v5 margin variance ratios .812 at R0 .2 and 1.054 at R1 .2. Match total evaluations and test covariance on fresh development actions before claiming a variance reduction.

## 5. Equal total compute gives a conditional crossover, not a categorical verdict

**DERIVED local comparison:** let method j have preparatory/tuning cost A_j, all-in per-estimate cost c_j, independent-estimate trace variance V_j, and bias vector beta_j relative to the **same** target gradient. For available budget B>A_j,

`n_j=floor((B-A_j)/c_j)`, `MSE_j=||beta_j||^2+V_j/n_j`. **(5)**

Independence and stationary parameters apply only within that local comparison; correlated reuse changes effective sample size. Score-function residuals, critic fitting, rejected trials, backward/checkpointing passes, memory-driven batching, reward readers and writing all belong in the cost. Neither pathwise c_j nor h/S/beta is measured in the saved logs, so a numerical crossover is currently unidentified.

After subtracting a common preparation cost (or when it is negligible), call the remaining budget B. With unbiased SF and pathwise-surrogate bias norm beta, approximate costs give `MSE_SF=V_SF*c_SF/B` and `MSE_PW=beta^2+V_PW*c_PW/B`. Put `D=V_SF*c_SF-V_PW*c_PW`. If D>0 and beta>0, pathwise has smaller local MSE for `B<D/beta^2`, while unbiased SF wins beyond that crossover. If D<=0, the biased pathwise route has no MSE advantage in this comparison. If beta=0, compare variance-times-cost directly. Exact pathwise in the additive-linear toy needs one valid derivative evaluation and has zero MSE, but that toy grants information unavailable from scalar rewards. Real pipelines may reverse the ordering through large backward cost, high derivative variance or derivative unavailability.

These are gradient-error statements, not sufficient conditions for final C/J superiority: optimizer stability, useful step alignment, constraints, nonconvexity, generalization and endpoint mismatch still matter. For differentiable feasible objectives compare tuned projected gradients, non-RL smoothing/search and an appropriate learned non-RL optimizer. For black-box/discrete endpoints compare SF against random search, finite-menu allocation and appropriate zeroth-order methods at equal full cost, not only against an unavailable exact derivative.

**SOURCE:** [Li and Malik §§3–4](https://arxiv.org/pdf/1606.01885) learn optimizer updates by policy search; [Andrychowicz et al., arXiv v2, §§2–3](https://arxiv.org/html/1606.04474v2) learn recurrent updates through an optimization objective and backpropagation. Learned adaptation itself therefore does not isolate an RL benefit; see [C6](../literature/c6-learned-optimization.md) for inspected evaluation limits.

**DERIVED amortization:** if a reusable policy has extra training/tuning cost DeltaT and saves DeltaD>0 per deployed source at matched assessment performance, cost recovery requires `N>DeltaT/DeltaD`. If DeltaD<=0 and DeltaT>0 there is no compute-saving crossover, although a measured performance gain could still justify it. Count fresh deployments, not training sources reused as evaluation. No N or positive saving is established here.

## 6. Short sequential control: credit and cost

**DERIVED:** with H policy decisions, known conditional policy scores `s_t=grad log pi(a_t|history_t)`, policy-independent environment dynamics, and terminal reward R, an unbiased score estimator is `sum_t (R-b_t(history_t))*s_t`. For an independent zero-mean additive terminal noise epsilon of variance v, its variance contribution is

`v*E||sum_t s_t||^2 = v*sum_t E||s_t||^2`,

because policy scores are martingale differences. Under direct Gaussian mean coordinates this becomes `v*sum_t d_t/sigma_t^2` (and divide by n independent trajectories). Real action-dependent returns introduce weighted cross-time covariances and require actual credit assignment; no universal H^2 penalty or H-fold learning benefit follows. Critics can reduce variance, but fitted value/advantage errors and any bootstrapping bias must enter (5).

**JUDGMENT:** for H=1, input-conditioned configuration choice is a contextual bandit/search problem. Repeating noisy evaluations of a fixed choice does not create sequential environmental information. A short H>1 policy has a reason to exist only if earlier actions change later state and the resulting observations change the useful next decision, compared with the best input-conditioned open-loop schedule. A writer's 150 gradient steps are not automatically 150 costly native-regeneration feedback queries. Charge native reward only where it is actually requested; charge all intervening writer/gradient computation. Differentiable unrolling is a comparator when those transitions and the target reward support it. Controls on a cooperative regenerator do not establish robustness to an attacker who does not use that control policy.

## 7. What can be concluded now

**JUDGMENT:** unstructured high-dimensional score-function updates have an explicit variance burden in the local model; the measured seed-scale makes that burden costly when each action rebuilds F5. This favors testing a valid dense-gradient or low-dimensional structured comparator, but is not a rejection theorem for RL. RL can remain competitive where the true endpoint is discrete, exact derivatives are unavailable or too costly, surrogate bias is substantial, useful state-dependent control exists, or training amortizes over enough fresh tasks. Each condition needs prospective evidence.

**Unidentified quantities:** action-to-reward slope/curvature, conditional derivative variance, feasible exploration scale, baseline/control-variate accuracy, actual backward cost, learning iterations, family-transfer error, and deployment count. Existing fixed-arm outcomes identify none of these. Later measurement must use fresh disjoint development sources; the frozen F6 study and consumed confirmation are not amended. The conclusions above apply conditionally whether F6 later has GO, fail or RESOURCE_STOP.

**Inspection and arithmetic record:** primary full-text method passages were opened on 2026-10-30: Mohamed §§4.2–4.3/5.3; Greensmith Theorem 13/proof; DRaFT §4/Algorithm 1; DDPO §4.3; Li/Malik §§3–4; Andrychowicz §§2–3. Local C6/C8 cards and WP1/WP3 notes were read. Constants/table use only `math.sqrt`, `math.ceil` and scalar arithmetic through MAIN `.thesis-build/venv/Scripts/python.exe -I`; no Monte Carlo run or scientific-library dependency was needed. Equations (1)–(5), random-slope witness and crossover are explicitly derived analysis, not reported empirical paper effects.

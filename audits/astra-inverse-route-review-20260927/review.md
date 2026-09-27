# Independent inverse-route review

Reviewer: `/root/astra_inverse_route_review` (gpt-6-astra, xhigh), independent of
author `/root`. Reviewed HEAD `d63f09e239e97eac791fb9aec0a6fc9744474436` on
2026-09-27; issue #18 / draft PR #67. Authority: AGENTS.md,
research/approval-policy.md, research/research-contract.md and research/scope-guard.md.
The evidence-audit skill was applied to this bounded, separate report. No model,
image decoding, learned metric, GPU, scientific run, installation, download,
approval creation or lifecycle transition was performed. Only this file is written.

## Disposition

**Proceed with ordinary implementation/design of a safeguarded Anderson solver
for the existing DDIM equation, then prepare one frozen two-target diagnostic.**
Keep a pure residual-minimization trust-region method as the next numerical route,
and coefficient continuation as a separate same-equation contingency. No measured
convergence, quality repair, root existence or unique cause is established here.
Do not spend the next scientific package on an arbitrary larger iteration count,
or presume that a paper's named algorithm solves this particular failure.

There is no identified algebraic bug in the inspected DDIM pair or its inverse
rearrangement. The observed trajectories contradict a simple description of slow,
monotone convergence. They support investigating noncontractive/oscillatory
behavior, but cannot identify a Jacobian spectrum, periodic orbit or basin failure.
The numerical bottleneck and the source-quality bottleneck remain separate.

## Inspected evidence and limits

Read the actual refined-target report and its independent custody review, prior
Astra feasibility audit, inversion.py, inversion_path.py, the original/refined
comparison configuration, relevant backend/schedule code, and existing
GNRI/REED/TRDI cards and inspection notes. Read-only JSON inspection used all
recorded inverse `evaluated` rows in the retained worker journal. No prior
custody review or learned metric was represented as independently reproduced here.

| Target and pair | Recorded behavior | Supported conclusion |
| --- | --- | --- |
| Encoded target, t1 | 7 evaluations; max residual .02239698 to .0000071004 | This pair met its 1e-5 criterion. |
| Refined target, t1 | 7 evaluations; .03030276 to .0000058413 | This pair also met its criterion. |
| Encoded target, t101 | .82401097 initially, .20169759 at evaluation4, .29720509 at14, .29868770 at32 | Initial progress followed by a substantial plateau/reversal. |
| Refined target, t101 | .78606713 initially, .10542405 at14, .15412617 at32 | A nonmonotone trajectory; last iterate is worse than its observed minimum. |

The encoded L1 objective settles near83--86 after evaluation14; the refined
objective repeatedly revisits roughly73--76. Scalar norm/objective histories
cannot reveal residual signs, vector directions or an exact cycle. Internal
inverse iterates/residual vectors were not durably saved at every evaluation;
final pair states cannot reconstruct those missing directions without a new run.
Both whole-path replays are absent, with null roundtrip residuals. Neither a
better intermediate residual nor the smaller refined terminal residual is an
observed successful inversion or image-quality result.

The direct refined PNG is 25.567447dB/.80792258/.07541168 versus VAE-only
22.482789/.74290992/.05849318. PSNR and SSIM still fail, and LPIPS worsens despite
passing .1. Exact inversion of either frozen target preserves its corresponding
decoder endpoint; it does not supply the missing source-quality improvement.
No inference about all decoder latents, other sources or universal impossibility
follows. All scientific approvals are consumed.

Relevant reviewed byte identities (SHA-256):

- inversion.py: `4888bb95ebc806da6751375591d7b5c4249d15ed7dc2416dbc90e9becc86f81a`.
- inversion_path.py: `0fc8e5da67179d1a535c3e2b73d49d7c2febaa9b547dbd6a717e7237d65307da`.
- configs/c4-refinement-comparison.json: `e4aa8c0b1979c75676fce22c3fb94e3112c1f08d5eda49b5ec9ff260c7f67df0`.
- Retained journal identity, independently verified by the prior custody review:
  `11fba38f0263db064fef5e9be6d711307496717fc83a695bdeaf44ee9193a8aa`;
  location: stable project's `.thesis-build/c4-runs/C4-refined-target-development/c4-refined-target-dev-001/logs/refinement-progress.jsonl`.

## Equation, stability and endpoint distinction

For alpha_t <= alpha_s, fixed epsilon predictor e_t(x), and target y, the inspected
eta-zero/no-clipping pair is

    D_t(x) = a*x + b*e_t(x)
    a = sqrt(alpha_s/alpha_t)
    b = sqrt(1-alpha_s) - a*sqrt(1-alpha_t)
    R(x) = D_t(x)-y
    G(x) = (y-b*e_t(x))/a
    R(x) = a*(x-G(x)).

These expressions agree algebraically with DDIM. The current convergence test is
the actual forward max residual, not the sum-L1 optimization objective. The
schedule inversion order [1,101], forward order [101,1] and terminal alpha[0]
(not1) are explicit. Real fp32 scheduler/backend equality still needs the pinned
ordinary parity tests; algebra alone does not certify arbitrary future adapters.

At a root, J_G=-(b/a)J_e. Local fixed-point stability depends on its spectrum;
an operator-norm bound <1 on an invariant neighborhood is a sufficient contraction
condition. Neither condition is measured for this UNet. With unit damping,
x_(k+1)-x_k=-R(x_k)/a, so substantial residual increases are inconsistent with a
uniform strict max-norm contraction along the complete visited trajectory
(apart from insignificant numerical noise). This does not exclude another norm,
a locally stable root, transient nonnormal growth or a better starting basin.

For relaxation x+ = (1-lambda)x + lambda G(x), each linearized eigenvalue mu becomes
1-lambda+lambda*mu. A negative real mu below -1 can be stabilized by sufficiently
small positive lambda; a positive real mu>1 cannot. Thus damping is a testable
candidate, not a universal cure. Persistent finite-precision/determinism noise is
also not established; the observed .1--.3 residuals are far above the achieved
t1 residuals, so merely loosening tolerance would change the success definition.

The 101->1 edge is much wider than the 1->0 terminal edge. Its coefficient
|b/a| multiplies the predictor sensitivity. That motivates a coarse-step
hypothesis, but no learned Jacobian bound or controlled schedule comparison
establishes that cause. The t1 success also does not prove t101 has a root.

Finally, starting the current solver at G(y) is just starting at its already
computed first fixed-point iterate; it shifts the same orbit and costs a predictor
call. It is not an independent initialization repair unless it changes the actual
warm-start construction. VAE encoding versus decoder refinement changes the
terminal equation target, not merely the initial guess of the same equation.

## Ranked alternatives

1. **Safeguarded Anderson on the unchanged pair equation.** Form a short history
   of g_i=G(x_i)-x_i; solve a regularized constrained least-squares mixing problem
   with coefficients summing to one, then evaluate the proposed mixed state with
   the real predictor. The residual of a linear combination is not the nonlinear
   residual at that combination. Require actual residual acceptance, finite
   coefficients, a displacement safeguard, rank/conditioning checks and a
   declared restart/fallback. Every rejected trial consumes NFE. Bounded damped
   Picard fallback can still fail and must report failure; it provides no global
   guarantee. AIDI establishes direct relevance of Anderson to DDIM inversion,
   not success for these targets. A new safeguarded implementation must be called
   AIDI-inspired unless its source parity is actually shown.
   [AIDI, ICCV 2023](https://openaccess.thecvf.com/content/ICCV2023/html/Pan_Effective_Real_Image_Editing_with_Accelerated_Iterative_Diffusion_Inversion_ICCV_2023_paper.html).

   Published safeguarded-AA convergence results require assumptions such as a
   nonexpansive map and a nonempty fixed-point set. Those assumptions are not
   verified here, and generic residual rejection does not automatically implement
   that theorem. [Zhang, O'Donoghue and Boyd, 2020](https://stanford.edu/~boyd/papers/nonexp_global_aa1.html).

2. **Pure residual least squares with a trust region.** Minimize
   phi(x)=||R(x)||_2^2/(2n), using gradient J_R^T R/n. A matrix-free Gauss--Newton
   model minimizes ||R+J_R p||_2 within a bounded step; actual/predicted decrease
   determines acceptance and radius updates. A simpler gradient/Cauchy step is
   legitimate but must be named accurately. JVP/VJP and checkpoint recomputation
   require separate accounting and memory evidence. No full dense latent
   Jacobian is necessary. A small gradient, falling mean loss or exhausted radius
   does not establish R=0; keep the unchanged max-residual and replay checks.
   Nonzero stationary minima remain possible. This is mathematically better
   aligned with the current reconstruction question than a distribution prior.

3. **Continuation, with two different meanings kept distinct.** A same-equation
   continuation can track H(x,lambda)=a*x+lambda*b*e_t(x)-y=0 from lambda0=0,
   x0=y/a, to lambda=1. This offers easier intermediate equations without changing
   the final DDIM map. Continuation is locally justified only while the relevant
   Jacobian remains nonsingular; folds, multiple branches and missed roots remain
   possible. Freeze the continuation grid, corrector and total budget prospectively.
   This is a reviewer-proposed numerical contingency, not a literature result or
   proven repair.

   A denser timestep schedule instead changes the forward composition itself.
   D_(101->1) is generally not D_(51->1) composed with D_(101->51), because the
   predictor inputs/timesteps differ. Dense inversion must use the identical
   dense replay, or supply only a warm start subsequently polished and tested
   against the original map. Keeping strength=.2 while increasing inference_steps
   can also change the first retained timestep; explicitly fix endpoint noise
   levels before calling it a step-density comparison. TRDI motivates schedule
   investigation, but its existing card supports no local guarantee.

**ReNoise** supplies a useful averaging/renoising comparator. Its Appendix A
averaging argument assumes convergence of the original sequence; it does not
prove that averaging an arbitrary divergent/nonlinear cycle finds a root.
Averaged epsilon or latent candidates require fresh true residual evaluation.
Its editability regularization and stochastic noise correction are separate
mechanisms; noise correction requiring a nonzero stochastic coefficient does
not apply to this eta0 path. [ReNoise v1, sections3--4 and Appendix A](https://arxiv.org/html/2403.14602v1).

**GNRI** is secondary here. The inspected implementation is explicitly modified:
sum-L1 residual plus an L2 transition prior and reciprocal-coordinate gradient
updates. It is neither vector Newton nor a pure residual trust-region method.
The prior can trade residual against distribution preference, and reciprocal
gradient denominators add their own failure modes. Author-reported speed and
captioned reconstruction do not transfer to this empty-conditioned SD1.5 pair.
[GNRI v5, sections4--5](https://arxiv.org/html/2312.12540v5).

**EDICT** changes the sampler to two coupled latent sequences with invertible
mixing. Its exactness pertains to that new paired map, subject to numerical
precision; its paper explicitly discusses inverse dilation instability. It does
not invert the existing one-latent DDIM map, and cannot repair a frozen VAE
endpoint by exactness alone. Adopting it requires an explicit reconstruction
architecture amendment, defining both watermark carriers/output semantics and
costs; its detector need not become inversion-based. [EDICT v2, sections4--5](https://arxiv.org/html/2211.12446v2).
REED-VAE concerns decoder training, a different intervention and resource/package
boundary; the inspected local card supplies no ready approved replacement.

## Ordinary synthetic regressions to require before the pilot

Use owned scalar/small-vector fixtures with analytically known roots, embedded in
the supported tensor shape. These are software checks, not learned-model evidence.

- Recover constant and affine epsilon roots; compare DDIMPair with the pinned
  scheduler, including alpha equality, final alpha[0], reversal and full replay.
- Negative unstable slope (e.g. G(x)=-1.2x+c) distinguishes oscillation from root
  absence; positive slope G(x)=1.2x+c proves that positive underrelaxation alone
  cannot universally fix instability. Include a nonnormal affine matrix with a
  stable spectrum and transient norm growth so diagnostics do not overclaim.
- Test repeated/dependent history, nearly singular mixing, huge coefficients,
  nonfinite trials, nonlinear residual-of-average mismatch, stagnation and a
  nonzero-residual stationary point. No gradient/step-norm success substitute.
- Check accepted/rejected/fallback evaluations, fresh residual at every returned
  state, exact source-target immutability, paired replay reserve, durable partial
  writes, cancellation/deadlines and cleanup. Preserve failures and no fallback PNG.
- If continuation/schedule work is later implemented, test the identity lambda0
  root and exact lambda1 residual; for dense schedules, test same-endpoint order
  and demonstrate that a dense inverse is not automatically a sparse inverse.

## One coherent prospective first pilot

Prepare **two new inverse/replay attempts**, one for each already retained target
(encoded and refined), using one identical, versioned safeguarded-Anderson policy
and the unchanged [101,1] forward path. Reuse exact stored target hashes; do not
rerun/refit the decoder, pick a new source or choose the better target afterward.
Keep both historical fixed-point failures and their whole trajectories as archived
references, explicitly nonconcurrent rather than new runs. This isolates a solver
intervention from decoder or schedule changes.

Before requesting execution, the author must provide a concrete policy for history
depth, mixing regularization/conditioning, acceptance norm/rule, coefficient/step
bounds, restart/fallback, stopping and all counters, supported by cited source
choices or declared engineering rationale plus the synthetic cases above. Freeze
those choices before study-model evaluation. This report intentionally supplies
no guessed magic constants and is not a ready compute manifest. Retaining the
existing 32-evaluation pair and128-evaluation path ceilings is an interpretable
first comparison; any changed ceiling must be explicit, justified and approved.
Keep the existing1e-5 pair and whole-replay criteria. Trial/restart/fallback work
and final replay must fit the predeclared budget; no unreported best-of-history
selection, retries or post-failure extension.

Record true max and RMS residual, all accepted/rejected status, step norm,
successive-residual cosine and lag2/lag4 differences, mixing conditioning and
actual root-model calls. Persist enough state/residual information to check these
diagnostics without another learned-model run. A local secant ratio is a directional
observation, not a global Lipschitz estimate. Distinguish numerical refusal,
stagnation, evaluation budget, time/memory failure and true convergence.

Only if both pairs converge, replay the identical original path and evaluate
the whole terminal residual; only then decode/save the native PNG under the
existing safety/quality policy. Compare each with its own frozen direct endpoint
and the source. Exact endpoint-image hashes may change under finite latent error;
report discrepancies rather than require accidental bit identity. Preserve every
missing dependent cell. Improvement in one target is a conditional N1 result;
convergence in both supports this solver on two dependent targets of one source,
not an accuracy rate or35dB. Neither outcome completes C4/C5 or blind detection.

If both still fail, the predeclared conclusion is that this bounded acceleration
did not resolve the observed bottleneck. Prepare the pure residual trust-region
route using the recorded directions, then a continuation or same-endpoint denser
path comparison if justified. Do not choose a new method during this pilot. The
decoder's remaining8.775-fold source-MSE gap remains an independent research
problem even if this pilot succeeds.

## Boundaries and next exact review

No blocker prevents scoped ordinary solver implementation, synthetic tests and
prospective design. Scientific execution is blocked until that exact complete
package is independently reviewed and actually authorized through the existing
runner. A material architecture change (coupled EDICT state, trained/replaced
decoder, image bypass, altered detector knowledge or core detector) needs a
concrete scope decision; do not silently include it as a numerical parameter.
Keep source claims, original targets/data commitments, old negative results,
existing issue links and official state ownership intact.

This is a preliminary route review, not acceptance of a new author artifact.
Re-review must name the exact new design/code versions and resolve their concrete
blocking findings before a delegated technical decision. Access limits: AIDI's
proceedings abstract/search-indexed method text was available but direct PDF and
the guessed arXiv-v2 HTML retrieval failed; no unseen algorithm parameters were
inferred. ReNoise/GNRI/EDICT primary HTML sections cited above were inspected.

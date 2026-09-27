# C4 deterministic pair inversion component

Issue #18 / draft PR #67. Ordinary software component, not a learned-model run,
complete trajectory, selected production method or measured quality improvement.
Apply research-contract.md, scope-guard.md and the actual reconstruction-path
amendment recorded in c4-reconstruction-path-amendment-20260927.md.

## Equation and attribution

Independently implemented in `src/embedding/inversion.py`; no upstream code copied.
The inspected [GNRI v5 paper](https://arxiv.org/html/2312.12540v5), sections 3–4,
motivates the implicit fixed-point residual and scalar coordinate update. Its
upstream implementation/license and runtime parity are not accepted here.

One eta-zero epsilon-prediction DDIM denoising pair is `y=A*x+B*epsilon(x)`:
`A=sqrt(alpha_previous/alpha)` and
`B=sqrt(1-alpha_previous)-A*sqrt(1-alpha)`.
The inversion reference solves `x=(target-B*epsilon(x))/A` iteratively, starting
at the retained target. Residual objective is the **sum** of coordinate absolute
errors in this fixed-point equation; convergence instead requires the maximum
forward reconstruction error to meet the declared tolerance.

The experimental `guided_coordinate` profile adds
`prior_weight * L2(x-prior_mean) / prior_beta` and uses the paper-inspired scalar
coordinate update `objective/(D*(gradient+eta))`. The fixed mean and positive beta
are caller-supplied; no default claim that they constitute the correct diffusion
transition distribution. L2 is an explicit profile choice, not proof of source
implementation parity. Unlike a faithful GNRI reproduction, this profile clips
each proposed coordinate delta and performs bounded objective-decreasing halving
backtracking. These safeguards, explicit stopping and full rejected-trial reporting
are experimental modifications; label this **GNRI-inspired**, never GNRI results.
Zero-weight fixed-point mode has no prior. No full Jacobian is formed, but guided
mode differentiates through the predictor and can be expensive with a real UNet.

## Limits and failure evidence

Exactly one fixed fp32 `[1,4,h,w]` target with at most 1,048,576 values, CPU/CUDA
device only. No scheduler clipping, thresholding, stochastic variance or v-prediction
support is inferred. The shape cap is not a VRAM/RAM guarantee. Alpha floor is
1e-12, finite positive previous alpha cannot be below current alpha. Equal alphas
are an identity pair. No VAE scaling or timestep selection occurs in this kernel.

Policy validation precedes prediction. Explicit per-pair forward evaluation cap
(1–256) counts initial and gradient re-evaluations plus every rejected line-search
trial. Backward calls are counted separately, not included in NFE or hidden as a
free operation. No global trajectory/resource/time budget is implemented here.
Each proposed state must actually be evaluated before being returned. Nonconverged
budget, zero gradient, unsafe denominator and failed line search remain failures;
a small guided objective cannot replace actual forward-residual convergence.
Nonfinite tensors, malformed predictions and predictor/autograd errors propagate
after an evaluation-start event; no retry, fallback, success record or dropped case.
The caller must durably persist progress and failure details; in-memory trace alone
is not crash-safe. Journal callback exceptions abort immediately. Predictors receive
isolated tensor copies; target/prior and returned state are detached snapshots.

## What ordinary tests do and do not establish

Owned CPU tensors test analytic affine roots, budget exhaustion, noncontraction,
prior-biased nonconvergence, zero derivative, invalid payloads and journal failure.
Pinned Diffusers scheduler comparisons cover all ten existing schedule pairs,
including final alpha with `set_alpha_to_one=False`, using synthetic epsilon only.
No model import/load, study-image read, GPU kernel, model gradient, reconstruction
metric or watermark execution is requested by these tests. No native image target,
source preservation, blindness, ownership authority or scientific acceptance follows.

Before a scientific package: integrate and review a pinned scheduler/model adapter,
reverse pair ordering and terminal-alpha source semantics, conditioning, whole-path
limits, durable partial states, model/asset/code provenance and exact runner approval.
The existing three-arm localization question remains pending and bound to its old
clean commit; this component neither changes nor consumes that authorization.

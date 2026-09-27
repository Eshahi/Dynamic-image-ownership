"""Bounded objective-only latent continuation with a separate fixed anchor.

Ordinary numerical component. Learned decoder binding, image quality, durable
storage quotas and exact compute approval belong to the future reviewed worker.
No models, images, weights, network or Torch are loaded at import.
"""
from dataclasses import dataclass
import time
from .inversion import _latent, _same, _real
from .proposed import EmbeddingError, _torch


@dataclass(frozen=True)
class AdaptivePolicy:
    iterations: int
    maximum_evaluations: int
    maximum_backtracks: int
    initial_step: float
    minimum_step: float
    maximum_step: float
    armijo: float
    radius_l2: float
    gradient_tolerance: float
    objective_tolerance: float
    maximum_seconds: float

    def __post_init__(self):
        for name,lo,hi in (("iterations",1,256),("maximum_evaluations",2,2048),
                           ("maximum_backtracks",0,20)):
            if type(getattr(self,name)) is not int or not lo<=getattr(self,name)<=hi:
                raise EmbeddingError("invalid adaptive "+name)
        for name,lo,hi in (("minimum_step",1e-12,100),("initial_step",1e-12,100),
                ("maximum_step",1e-12,100),("armijo",1e-12,.5),("radius_l2",1e-8,1000),
                ("gradient_tolerance",0,1),("objective_tolerance",0,1),
                ("maximum_seconds",1e-6,1100)):
            _real(getattr(self,name),"adaptive "+name,lo,hi)
        if not self.minimum_step<=self.initial_step<=self.maximum_step:
            raise EmbeddingError("ordered adaptive step limits required")


@dataclass(frozen=True)
class AdaptiveResult:
    state: object
    status: str
    objective: float
    evaluations: int
    backward_evaluations: int
    accepted_updates: int
    displacement_l2: float
    gradient_at_returned_state_l2: object


def continue_latent(objective, current, anchor, policy, *, progress, save_state):
    """Minimize a deterministic scalar using actual projected Armijo displacement.

    Anchor is independent of current: resuming must retain the original trust
    ball. Every evaluated input, including rejected candidates, is sent to the
    caller's durable state sink. Failures propagate. A small gradient or exhausted
    budget is a numeric termination reason, never image-quality acceptance.
    """
    torch=_torch()
    if type(policy) is not AdaptivePolicy or any(not callable(c) for c in (objective,progress,save_state)):
        raise EmbeddingError("typed policy and objective/persistence callbacks required")
    _latent(anchor,"fixed continuation anchor");_same(current,anchor,"continuation start")
    anchor=anchor.detach().clone();current=current.detach().clone()
    def norm(value):return float(torch.linalg.vector_norm(value.double()))
    if norm(current-anchor)>policy.radius_l2:
        raise EmbeddingError("start outside original anchor radius")
    deadline=time.monotonic()+policy.maximum_seconds
    evaluations=backward=updates=0
    gradient_here=None
    def emit(row):progress(dict(row))
    def guard():
        if time.monotonic()>=deadline:
            raise EmbeddingError("adaptive continuation cooperative time limit")
    def evaluate(state,gradient,role,iteration):
        nonlocal evaluations
        guard();_same(state,anchor,"evaluated continuation state",allow_grad=gradient)
        if evaluations>=policy.maximum_evaluations:
            raise EmbeddingError("internal continuation evaluation ceiling")
        evaluations+=1
        row={"evaluation":evaluations,"iteration":iteration,"role":role,"gradient_enabled":gradient}
        emit(dict(row,phase="adaptive_evaluation_started"));guard()
        with torch.set_grad_enabled(gradient):
            value=objective(state.clone())
        if (not isinstance(value,torch.Tensor) or value.numel()!=1 or value.ndim!=0
                or value.device!=state.device or not bool(torch.isfinite(value)) or float(value.detach())<0
                or (gradient and not value.requires_grad)):
            raise EmbeddingError("finite differentiable nonnegative scalar objective required")
        observed=float(value.detach())
        save_state(dict(row,phase="adaptive_evaluated_state",objective=observed),state.detach().clone())
        emit(dict(row,phase="adaptive_evaluated",objective=observed));guard()
        return value,observed
    def finish(status,observed):
        guard()
        displacement=norm(current-anchor)
        row={"phase":"adaptive_terminated","status":status,"objective":observed,
             "evaluations":evaluations,"backward_evaluations":backward,"accepted_updates":updates,
             "displacement_l2":displacement,"gradient_at_returned_state_l2":gradient_here,
             "scientific_acceptance":False}
        save_state(dict(row),current.clone());guard();emit(row)
        return AdaptiveResult(current.clone(),status,observed,evaluations,backward,updates,
                              displacement,gradient_here)
    _,observed=evaluate(current,False,"initial",0)
    step=policy.initial_step;first_try_streak=0
    for iteration in range(1,policy.iterations+1):
        if observed<=policy.objective_tolerance:return finish("objective_tolerance",observed)
        # Reserve a candidate measurement before spending on a gradient.
        if evaluations+2>policy.maximum_evaluations:return finish("evaluation_budget",observed)
        state=current.clone().requires_grad_(True)
        value,at_current=evaluate(state,True,"gradient",iteration)
        backward+=1;emit({"phase":"adaptive_backward_started","iteration":iteration,"backward_evaluations":backward});guard()
        gradient,=torch.autograd.grad(value,state,create_graph=False)
        gradient=gradient.detach();_same(gradient,anchor,"adaptive gradient")
        gradient_here=norm(gradient)
        emit({"phase":"adaptive_gradient","iteration":iteration,"gradient_l2":gradient_here});guard()
        del value,state
        if gradient_here<=policy.gradient_tolerance:return finish("gradient_tolerance",observed)
        baseline=min(observed,at_current)
        accepted=False
        for attempt in range(policy.maximum_backtracks+1):
            if evaluations>=policy.maximum_evaluations:return finish("evaluation_budget",observed)
            trial_step=step*(.5**attempt)
            if trial_step<policy.minimum_step:break
            trial=current-trial_step*gradient/gradient_here
            delta=trial-anchor;length=norm(delta)
            if length>policy.radius_l2:
                # A conservative inward factor handles float32 rounding;
                # validate the rounded result against the original radius.
                trial=anchor+delta*(policy.radius_l2/length)*(1-8*torch.finfo(torch.float32).eps)
            _same(trial,anchor,"adaptive trial")
            if norm(trial-anchor)>policy.radius_l2:
                emit({"phase":"adaptive_trial_refused","reason":"rounded_radius","iteration":iteration})
                continue
            displacement=trial-current
            slope=float((gradient.double()*displacement.double()).sum())
            if slope>=0:
                emit({"phase":"adaptive_trial_refused","reason":"non_descent","iteration":iteration})
                continue
            _,trial_value=evaluate(trial,False,"trial",iteration)
            accepted=trial_value<baseline and trial_value<=baseline+policy.armijo*slope
            emit({"phase":"adaptive_trial","iteration":iteration,"evaluation":evaluations,
                  "step":trial_step,"attempt":attempt,"slope":slope,"accepted":accepted,
                  "objective":trial_value})
            if accepted:
                current=trial.detach().clone();observed=trial_value;updates+=1
                gradient_here=None  # last gradient belongs to the preceding state
                first_try_streak=first_try_streak+1 if attempt==0 else 0
                step=min(policy.maximum_step,trial_step*(2 if first_try_streak>=2 else 1))
                if first_try_streak>=2:first_try_streak=0
                break
        if not accepted:return finish("line_search_failed",observed)
    return finish("objective_tolerance" if observed<=policy.objective_tolerance else "iteration_budget",observed)

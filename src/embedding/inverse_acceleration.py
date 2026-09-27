"""Ordinary safeguarded Anderson component for the unchanged eta-zero DDIM root.

No model adapter, trajectory, execution authority or import-time Torch. This is
an independently implemented AIDI-inspired candidate, not a paper reproduction.
Every proposed state is measured with the actual callback; rejected evaluations
may inform the small mixing history but never become accepted output implicitly.
"""
from dataclasses import dataclass
import math

from .inversion import DDIMPair, _latent, _same, _real
from .proposed import EmbeddingError, _torch


@dataclass(frozen=True)
class AccelerationPolicy:
    max_evaluations: int = 32
    residual_tolerance: float = 1e-5
    history: int = 4
    regularization: float = 1e-8
    condition_limit: float = 1e10
    coefficient_l1_limit: float = 20.
    maximum_step_rms: float = 2.
    fallback_damping: tuple = (1., .5, .25)

    def __post_init__(self):
        for name, low, high in (("max_evaluations", 1, 256), ("history", 2, 8)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise EmbeddingError(f"invalid {name}")
        for name, low, high in (("residual_tolerance", 0, 1),
                ("regularization", 1e-12, 1), ("condition_limit", 1, 1e12),
                ("coefficient_l1_limit", 1, 100), ("maximum_step_rms", 1e-8, 100)):
            _real(getattr(self, name), name, low, high)
        if type(self.fallback_damping) is not tuple or not 1 <= len(self.fallback_damping) <= 8:
            raise EmbeddingError("bounded immutable fallback grid required")
        for value in self.fallback_damping:
            _real(value, "fallback damping", 1e-8, 1)
        if any(a <= b for a,b in zip(self.fallback_damping, self.fallback_damping[1:])):
            raise EmbeddingError("strictly decreasing fallback grid required")


@dataclass(frozen=True)
class AccelerationResult:
    state: object
    status: str
    evaluations: int
    residual_max: float
    residual_rms: float
    accepted_updates: int
    rejected_trials: int
    trace: tuple


def invert_pair_accelerated(pair, target, predictor, policy, *, progress=None, state_observer=None):
    """Root of D(x)-target, with true-residual acceptance and bounded NFE.

    The callback must be deterministic with frozen conditioning/weights. Observer
    receives detached clones of each evaluated state and true residual for durable
    prospective diagnostics; observer/journal failures abort. There is no backward
    pass. Component success requires max residual, not mixing-model fit or RMS.
    """
    torch = _torch()
    if not isinstance(pair, DDIMPair) or not isinstance(policy, AccelerationPolicy):
        raise EmbeddingError("typed pair/acceleration policy required")
    _latent(target, "target")
    for callback in (predictor, progress, state_observer):
        if callback is not None and not callable(callback):
            raise EmbeddingError("callable callbacks required")
    if predictor is None:
        raise EmbeddingError("predictor required")
    y = target.detach().clone()
    a,b = pair.coefficients
    trace=[]; history=[]
    calls=accepted=rejected=0

    def emit(row):
        trace.append(dict(row))
        if progress is not None:
            progress(dict(row))

    def rms(tensor):
        return float(tensor.double().square().mean().sqrt())

    def measure(state, proposal):
        nonlocal calls
        _same(state, y, "candidate")
        if calls >= policy.max_evaluations:
            raise EmbeddingError("internal evaluation cap violation")
        calls += 1
        emit({"phase":"evaluation_started", "evaluation":calls, "proposal":proposal})
        epsilon = predictor(state.clone())
        _same(epsilon, y, "prediction")
        residual = pair.denoise(state, epsilon)-y
        g = (y-b*epsilon)/a-state
        _same(residual, y, "true residual")
        _same(g, y, "fixed-point displacement")
        maximum=float(residual.abs().max()); norm=rms(residual)
        emit({"phase":"evaluated", "evaluation":calls, "proposal":proposal,
              "residual_max":maximum, "residual_rms":norm})
        if state_observer is not None:
            state_observer(calls, state.detach().clone(), residual.detach().clone())
        item=(state.detach().clone(), g.detach().clone(), maximum, norm)
        history.append(item)
        del history[:-policy.history]
        return item

    def mixed(current):
        if len(history) < 2:
            return None
        # Only the <=8 x <=8 Gram system lives on CPU in float64. No dense
        # latent Jacobian, autograd graph or synthetic residual-of-average test.
        gram=torch.empty((len(history),len(history)), dtype=torch.float64, device="cpu")
        for i,(_,gi,_,_) in enumerate(history):
            for j,(_,gj,_,_) in enumerate(history[:i+1]):
                value=float((gi.double()*gj.double()).mean())
                gram[i,j]=gram[j,i]=value
        scale=float(gram.diag().max())
        if not math.isfinite(scale) or scale <= 0:
            emit({"phase":"mix_refused", "reason":"zero_or_nonfinite_history"})
            return None
        matrix=gram/scale+policy.regularization*torch.eye(len(history),dtype=torch.float64)
        eigen=torch.linalg.eigvalsh(matrix)
        condition=float(eigen[-1]/eigen[0]) if float(eigen[0]) > 0 else math.inf
        if not math.isfinite(condition) or condition > policy.condition_limit:
            emit({"phase":"mix_refused", "reason":"conditioning"})
            return None
        try:
            weights=torch.linalg.solve(matrix,torch.ones(len(history),dtype=torch.float64))
        except RuntimeError:
            emit({"phase":"mix_refused", "reason":"linear_solve"})
            return None
        denominator=float(weights.sum())
        if not math.isfinite(denominator) or denominator <= 0:
            emit({"phase":"mix_refused", "reason":"normalization"})
            return None
        weights=weights/denominator
        if not bool(torch.isfinite(weights).all()) or float(weights.abs().sum()) > policy.coefficient_l1_limit:
            emit({"phase":"mix_refused", "reason":"coefficients"})
            return None
        candidate=torch.zeros_like(y)
        for weight,(state,g,_,_) in zip(weights.tolist(),history):
            candidate.add_(state+g,alpha=weight)
        if not bool(torch.isfinite(candidate).all()) or rms(candidate-current[0]) > policy.maximum_step_rms:
            emit({"phase":"mix_refused", "reason":"displacement"})
            return None
        emit({"phase":"mix_proposed", "condition":condition,"weights":weights.tolist()})
        return candidate

    def finish(current, status):
        emit({"phase":"terminated", "status":status,"evaluations":calls,
              "accepted_updates":accepted,"rejected_trials":rejected,
              "residual_max":current[2],"residual_rms":current[3]})
        return AccelerationResult(current[0].clone(), status,calls,current[2],current[3],
                                  accepted,rejected,tuple(trace))

    with torch.no_grad():
        current=measure(y.clone(),"initial")
        fallback=0
        while True:
            if current[2] <= policy.residual_tolerance:
                return finish(current,"converged")
            if calls >= policy.max_evaluations:
                return finish(current,"evaluation_budget")
            candidate=mixed(current)
            proposal="anderson"
            if candidate is None:
                if fallback >= len(policy.fallback_damping):
                    return finish(current,"safeguard_stagnation")
                damping=policy.fallback_damping[fallback]; fallback+=1
                candidate=current[0]+damping*current[1]
                proposal=f"picard:{damping}"
                if rms(candidate-current[0]) > policy.maximum_step_rms:
                    emit({"phase":"fallback_refused","reason":"displacement","damping":damping})
                    continue
            trial=measure(candidate,proposal)
            improved=(trial[2] <= policy.residual_tolerance or
                      (trial[3] < current[3] and trial[2] <= current[2]))
            emit({"phase":"trial_decision", "evaluation":calls,"proposal":proposal,"accepted":improved})
            if improved:
                current=trial; accepted+=1; fallback=0
            else:
                rejected+=1
                # A rejected nonlinear mix is not accepted from its predicted
                # residual. Force one declared fallback; retain the measured
                # off-iterate point for the next small Anderson history.
                if proposal=="anderson":
                    if fallback >= len(policy.fallback_damping):
                        return finish(current,"safeguard_stagnation")
                    if calls >= policy.max_evaluations:
                        return finish(current,"evaluation_budget")
                    damping=policy.fallback_damping[fallback]; fallback+=1
                    candidate=current[0]+damping*current[1]
                    if rms(candidate-current[0]) > policy.maximum_step_rms:
                        emit({"phase":"fallback_refused","reason":"displacement","damping":damping})
                        continue
                    trial=measure(candidate,f"picard:{damping}")
                    improved=(trial[2] <= policy.residual_tolerance or
                              (trial[3] < current[3] and trial[2] <= current[2]))
                    emit({"phase":"trial_decision","evaluation":calls,"proposal":f"picard:{damping}","accepted":improved})
                    if improved:
                        current=trial; accepted+=1; fallback=0
                    else:
                        rejected+=1

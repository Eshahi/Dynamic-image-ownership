"""Bounded eta-zero DDIM pair inversion; no model/runner or import-time Torch.

Independent equation implementation, not copied upstream GNRI code. The guided
profile deliberately differs from the paper: explicit L2 prior, coordinate trust
cap and monotone-objective backtracking. See the component design for limits.
"""
from dataclasses import dataclass
import math

from .proposed import EmbeddingError, _torch


def _real(value, name, low, high):
    if (type(value) not in (int, float) or not low <= value <= high
            or not math.isfinite(value)):
        raise EmbeddingError(f"invalid {name}")


@dataclass(frozen=True)
class DDIMPair:
    """One epsilon-prediction denoising pair, no clipping/thresholding/variance."""
    alpha: float
    previous_alpha: float

    def __post_init__(self):
        _real(self.alpha, "alpha", 1e-12, 1)
        _real(self.previous_alpha, "previous_alpha", self.alpha, 1)

    @property
    def coefficients(self):
        a = math.sqrt(self.previous_alpha / self.alpha)
        b = math.sqrt(1-self.previous_alpha) - a*math.sqrt(1-self.alpha)
        return a, b

    def denoise(self, state, epsilon):
        _latent(state, "state", allow_grad=True)
        _same(epsilon, state, "epsilon", allow_grad=True)
        a, b = self.coefficients
        result = a*state + b*epsilon
        _same(result, state, "denoised", allow_grad=True)
        return result


@dataclass(frozen=True)
class InversionPolicy:
    method: str = "fixed_point"
    max_evaluations: int = 32
    residual_tolerance: float = 1e-5
    damping: float = 1.
    denominator_eta: float = 1e-6
    maximum_coordinate_step: float = 1.
    max_backtracks: int = 8
    prior_weight: float = 0.
    prior_beta: float = 1.

    def __post_init__(self):
        if type(self.method) is not str or self.method not in ("fixed_point", "guided_coordinate"):
            raise EmbeddingError("unsupported inversion method")
        for name, low, high in (("max_evaluations", 1, 256), ("max_backtracks", 0, 16)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise EmbeddingError(f"invalid {name}")
        for name, low, high in (("residual_tolerance", 0, 1), ("damping", 1e-8, 1),
                ("denominator_eta", 1e-12, 1), ("maximum_coordinate_step", 1e-8, 100),
                ("prior_weight", 0, 1e3), ("prior_beta", 1e-12, 1)):
            _real(getattr(self, name), name, low, high)
        if self.method == "fixed_point" and self.prior_weight != 0:
            raise EmbeddingError("fixed-point reference has no prior")


@dataclass(frozen=True)
class InversionResult:
    state: object
    status: str
    evaluations: int
    backward_evaluations: int
    residual_max: float
    objective: float
    # Includes rejected trials; caller must persist progress for crash recovery.
    trace: tuple


def _latent(value, name, *, allow_grad=False):
    torch = _torch()
    if (not isinstance(value, torch.Tensor) or value.dtype != torch.float32
            or value.ndim != 4 or tuple(value.shape[:2]) != (1, 4)
            or not 1 <= value.numel() <= 1_048_576
            or value.device.type not in ("cpu", "cuda")
            or (value.requires_grad and not allow_grad)
            or not bool(torch.isfinite(value).all())):
        raise EmbeddingError(f"invalid {name} latent")


def _same(value, reference, name, *, allow_grad=False):
    _latent(value, name, allow_grad=allow_grad)
    if value.shape != reference.shape or value.device != reference.device:
        raise EmbeddingError(f"{name} shape/device mismatch")


def invert_pair(pair, target, predictor, policy, *, prior_mean=None, progress=None):
    """Solve pair.denoise(x, predictor(x)) == target, starting at target.

    Predictor must be deterministic, differentiable for guided mode and use
    frozen weights. Timesteps/conditioning belong to its immutable closure.
    This is a component API, NOT a scientific execution authorization. No model
    adapter, trajectory, VAE, watermark or detector is invoked here.
    """
    torch = _torch()
    if not isinstance(pair, DDIMPair) or not isinstance(policy, InversionPolicy):
        raise EmbeddingError("typed pair/policy required")
    _latent(target, "target")
    if not callable(predictor) or (progress is not None and not callable(progress)):
        raise EmbeddingError("callable predictor/progress required")
    if prior_mean is not None:
        _same(prior_mean, target, "prior mean")
    if (policy.prior_weight > 0) != (prior_mean is not None):
        raise EmbeddingError("positive prior weight requires exactly one fixed mean")
    target = target.detach().clone()
    mean = None if prior_mean is None else prior_mean.detach().clone()
    a, b = pair.coefficients
    trace = []
    evaluations = backward = 0

    def emit(row):
        trace.append(dict(row))
        if progress is not None:
            progress(dict(row))  # failure aborts; never silently lose journal

    def evaluate(state, gradients):
        nonlocal evaluations
        evaluations += 1
        emit({"phase": "evaluation_started", "evaluation": evaluations,
              "gradient_enabled": gradients})
        # Callback may mutate its input; isolate it from the current iterate.
        epsilon = predictor(state.clone())
        _same(epsilon, state, "prediction", allow_grad=True)
        reconstructed = pair.denoise(state, epsilon)
        residual = state - (target-b*epsilon)/a
        objective = residual.abs().sum()
        if mean is not None:
            objective = objective + policy.prior_weight*torch.linalg.vector_norm(state-mean)/policy.prior_beta
        if not bool(torch.isfinite(objective)):
            raise EmbeddingError("nonfinite inversion objective")
        error = float((reconstructed-target).abs().max().detach())
        return epsilon, objective, error

    def finish(state, status, obj, error):
        emit({"phase": "terminated", "status": status,
              "evaluations": evaluations, "backward_evaluations": backward,
              "residual_max": error, "objective": float(obj.detach())})
        return InversionResult(state.detach().clone(), status, evaluations, backward,
                               error, float(obj.detach()), tuple(trace))

    x = target.clone()
    # Every accepted iterate is evaluated before return. NFE includes line-search
    # rejects, initial evaluation, and gradient-bearing re-evaluations.
    while True:
        gradient_mode = policy.method == "guided_coordinate"
        x = x.detach().requires_grad_(gradient_mode)
        with torch.enable_grad() if gradient_mode else torch.no_grad():
            epsilon, obj, error = evaluate(x, gradient_mode)
            emit({"phase": "evaluated", "evaluation": evaluations,
                  "residual_max": error, "objective": float(obj.detach())})
            if error <= policy.residual_tolerance:
                return finish(x, "converged", obj, error)
            if evaluations >= policy.max_evaluations:
                return finish(x, "evaluation_budget", obj, error)
            if not gradient_mode:
                x = ((1-policy.damping)*x + policy.damping*(target-b*epsilon)/a).detach()
                _latent(x, "fixed-point iterate")
                continue
            backward += 1
            emit({"phase": "backward_started", "backward_evaluation": backward})
            gradient, = torch.autograd.grad(obj, x, create_graph=False)
            _same(gradient, x, "objective gradient")
            if float(gradient.abs().max()) == 0:
                return finish(x, "zero_gradient", obj, error)
            denominator = gradient + policy.denominator_eta
            if bool((denominator.abs() < policy.denominator_eta).any()):
                return finish(x, "unsafe_denominator", obj, error)
            delta = (obj.detach() / (x.numel()*denominator)).clamp(
                -policy.maximum_coordinate_step, policy.maximum_coordinate_step)
            _same(delta, x, "coordinate update")
        accepted = False
        for attempt in range(policy.max_backtracks+1):
            if evaluations >= policy.max_evaluations:
                return finish(x, "evaluation_budget", obj, error)
            candidate = (x.detach()-policy.damping*(.5**attempt)*delta.detach()).detach()
            with torch.no_grad():
                _, trial_obj, trial_error = evaluate(candidate, False)
            accepted = float(trial_obj) < float(obj.detach())
            emit({"phase": "backtrack", "evaluation": evaluations, "attempt": attempt,
                  "accepted": accepted, "objective": float(trial_obj),
                  "residual_max": trial_error})
            if accepted:
                x = candidate
                if trial_error <= policy.residual_tolerance:
                    return finish(x, "converged", trial_obj, trial_error)
                if evaluations >= policy.max_evaluations:
                    return finish(x, "evaluation_budget", trial_obj, trial_error)
                break
        if not accepted:
            return finish(x, "line_search_failed", obj, error)

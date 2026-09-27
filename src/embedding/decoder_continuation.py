"""Same-start frozen-decoder comparison; no loads or execution authorization."""
from copy import deepcopy
from dataclasses import dataclass, replace
import time
from .proposed import DiffusersComponents, EmbeddingError, _torch, padded_source
from .checkpointing import CheckpointedComponents
from .inversion import _latent, _same, _real
from .inversion_path import PinnedDDIMPath, module_fingerprint
from .latent_refinement import RefinementPolicy, refine
from .adaptive_refinement import AdaptivePolicy, continue_latent

ARMS = ("retained_start", "fixed_continuation", "adaptive_continuation")


@dataclass(frozen=True)
class ContinuationPolicy:
    control: RefinementPolicy
    adaptive: AdaptivePolicy
    maximum_seconds: float

    def __post_init__(self):
        if type(self.control) is not RefinementPolicy or type(self.adaptive) is not AdaptivePolicy:
            raise EmbeddingError("typed continuation policies required")
        c, a = self.control, self.adaptive
        if (c.latent_penalty != 0 or c.iterations != a.iterations
                or c.maximum_evaluations != a.maximum_evaluations
                or c.maximum_displacement_l2 != a.radius_l2
                or c.mse_tolerance != a.objective_tolerance
                or c.maximum_seconds != a.maximum_seconds):
            raise EmbeddingError("same objective, anchor radius and equal ceilings required")
        _real(self.maximum_seconds, "continuation duration", 1e-6, 1100)


def compare(backend, source, start, anchor, policy, *, progress, save_arm, save_state):
    """Decode retained start, then two independent continuations; no encode/DDIM.

    Each optimized arm reserves ONE extra decoder evaluation/backward for its
    actual final-state gradient and image. No final-gradient inference from a
    preceding state. Every learned computation still needs exact runner approval.
    """
    torch = _torch()
    if type(backend) not in (DiffusersComponents, CheckpointedComponents) or type(policy) is not ContinuationPolicy:
        raise EmbeddingError("typed decoder continuation components/policy required")
    if any(not callable(c) for c in (progress, save_arm, save_state)):
        raise EmbeddingError("all continuation persistence callbacks required")
    padded = padded_source(source, backend.settings.maximum_side)
    _latent(anchor, "original continuation anchor"); _same(start, anchor, "retained start")
    shape = (1, 4, padded.shape[-2]//8, padded.shape[-1]//8)
    if tuple(start.shape) != shape or start.device != source.device or source.device != backend.condition.device:
        raise EmbeddingError("continuation grid/device mismatch")
    target, initial, centre = source.detach().clone(), start.detach().clone(), anchor.detach().clone()
    if float(torch.linalg.vector_norm((initial-centre).double())) > policy.control.maximum_displacement_l2:
        raise EmbeddingError("continuation start outside original anchor radius")
    path = PinnedDDIMPath(backend)
    vae = backend.vae
    if not isinstance(vae, torch.nn.Module) or not isinstance(getattr(vae, "decoder", None), torch.nn.Module):
        raise EmbeddingError("frozen explicit decoder required")
    binding = module_fingerprint(vae)
    retained = tuple(vae.modules())+tuple(vae.parameters())+tuple(vae.buffers())
    methods = []
    for owner, name in ((backend, "_decode"), (vae, "decode")):
        method = getattr(owner, name)
        if getattr(method, "__self__", None) is not owner or getattr(method, "__func__", None) is None:
            raise EmbeddingError("decoder method owner binding required")
        methods.append((owner, name, method.__func__))
    deadline = time.monotonic()+policy.maximum_seconds
    arm_deadline = deadline
    arm = ARMS[0]; mode = "forward"; evaluations = backwards = starts = recomputations = 0
    outcomes = {}

    def guard():
        if time.monotonic() >= min(deadline, arm_deadline):
            raise EmbeddingError("continuation cooperative time limit")
        path._validate()
        if (backend.vae is not vae or module_fingerprint(vae) != binding
                or any(m.training for m in vae.modules())
                or float(vae.config.scaling_factor) != backend.settings.vae_scale):
            raise EmbeddingError("continuation frozen decoder identity/profile drift")
        for owner, name, function in methods:
            method = getattr(owner, name)
            if getattr(method, "__self__", None) is not owner or getattr(method, "__func__", None) is not function:
                raise EmbeddingError("continuation bound method drift")
        for value in tuple(vae.parameters())+tuple(vae.buffers()):
            if (value.device != target.device or value.requires_grad
                    or (value.is_floating_point() and value.dtype != torch.float32)):
                raise EmbeddingError("continuation frozen tensor profile drift")

    def emit(row):
        guard(); progress(deepcopy(dict(row, arm=arm))); guard()

    def persist(row, state):
        guard(); save_state(arm, deepcopy(row), state.detach().clone()); guard()

    def inner_event(row):
        nonlocal mode, evaluations, backwards
        phase = row["phase"]
        if phase in ("refinement_evaluation_started", "adaptive_evaluation_started"):
            mode = "forward"; evaluations += 1
            if evaluations > policy.control.maximum_evaluations:
                raise EmbeddingError("continuation optimizer evaluation ceiling")
        if phase in ("refinement_backward_started", "adaptive_backward_started"):
            mode = "backward"; backwards += 1
            if backwards > policy.control.iterations:
                raise EmbeddingError("continuation optimizer backward ceiling")
        emit(row)

    def started(module, args):
        nonlocal starts, recomputations
        guard()
        if starts >= 2*(policy.control.maximum_evaluations+1):
            raise EmbeddingError("continuation actual decoder forward ceiling")
        starts += 1
        if mode == "backward": recomputations += 1
        emit({"phase": "continuation_decoder_started", "context": mode,
              "actual_decoder_forward_starts": starts, "checkpoint_recomputations": recomputations})

    def decoded(state):
        guard()
        image = backend._decode(state.clone()/backend.settings.vae_scale)
        guard()
        if (not isinstance(image, torch.Tensor) or tuple(image.shape) != tuple(padded.shape)
                or image.dtype != torch.float32 or image.device != target.device
                or not bool(torch.isfinite(image).all())):
            raise EmbeddingError("invalid continuation decoder image")
        native = ((image+1)/2).clamp(0, 1)[:, :, :target.shape[-2], :target.shape[-1]]
        mse = (native-target).square().mean()
        return native, mse

    def objective(state):
        return decoded(state)[1]

    def save_image(image, metadata):
        guard(); save_arm(arm, image.detach().clone(), deepcopy(metadata)); guard()
        emit({"phase": "continuation_arm_saved", "outcome": metadata})
        outcomes[arm] = deepcopy(metadata)

    guard()
    handle = vae.decoder.register_forward_pre_hook(started)
    try:
        # Both original states are persisted before any forward. The worker
        # verifies retained-start canonical pixel replay in save_arm.
        persist({"phase": "fixed_original_anchor"}, centre)
        persist({"phase": "common_continuation_start"}, initial)
        emit({"phase": "continuation_arm_started"})
        with torch.no_grad(): image, mse = decoded(initial)
        evaluations = 1
        save_image(image, {"continuous_mse_rgb01": float(mse), "decoder_evaluations": 1,
                          "backward_evaluations": 0, "status": "retained_start_replay"})
        del image, mse
        for arm in ARMS[1:]:
            evaluations = backwards = starts = recomputations = 0
            mode = "forward"
            arm_deadline = min(deadline, time.monotonic()+policy.control.maximum_seconds)
            emit({"phase": "continuation_arm_started"})
            persist({"phase": "arm_identical_start"}, initial)
            remaining = min(deadline, arm_deadline)-time.monotonic()
            if arm == "fixed_continuation":
                result = refine(backend, target.clone(), initial.clone(),
                    replace(policy.control, maximum_seconds=remaining),
                    constraint_anchor=centre.clone(), progress=inner_event, save_state=persist)
                state = result.latent.detach().clone()
                numeric = {"status": result.status, "objective": result.objective,
                           "optimizer_evaluations": result.evaluations}
            else:
                result = continue_latent(objective, initial.clone(), centre.clone(),
                    replace(policy.adaptive, maximum_seconds=remaining),
                    progress=inner_event, save_state=persist)
                state = result.state.detach().clone()
                numeric = {"status": result.status, "objective": result.objective,
                           "optimizer_evaluations": result.evaluations, "accepted_updates": result.accepted_updates}
            del result
            guard()
            # This is an additional measured evaluation, not free evidence.
            evaluations += 1; mode = "forward"
            emit({"phase": "final_gradient_evaluation_started", "evaluation": evaluations})
            variable = state.clone().requires_grad_(True)
            with torch.enable_grad(): image, mse = decoded(variable)
            if not image.requires_grad or not mse.requires_grad:
                raise EmbeddingError("detached final decoder gradient")
            persist({"phase": "final_gradient_evaluated_state", "objective": float(mse.detach())}, state)
            mode = "backward"; backwards += 1
            emit({"phase": "final_backward_started", "backward_evaluations": backwards})
            gradient, = torch.autograd.grad(mse, variable)
            guard(); _same(gradient.detach(), centre, "final measured gradient")
            final_mse = float(mse.detach())
            if abs(final_mse-numeric["objective"]) > 1e-8:
                raise EmbeddingError("final decoded objective replay mismatch")
            numeric.update(continuous_mse_rgb01=final_mse,
                final_gradient_l2=float(torch.linalg.vector_norm(gradient.detach().double())),
                displacement_l2=float(torch.linalg.vector_norm((state-centre).double())),
                decoder_evaluations=evaluations, backward_evaluations=backwards,
                actual_decoder_forward_starts=starts, checkpoint_recomputations=recomputations,
                scientific_acceptance=False)
            save_image(image, numeric)
            del variable, image, mse, gradient, state
        emit({"phase": "continuation_terminated", "scientific_acceptance": False})
        guard()
        return {"arms": outcomes, "status": "completed_requires_png_safety_quality", "scientific_acceptance": False}
    finally:
        handle.remove()
        del retained

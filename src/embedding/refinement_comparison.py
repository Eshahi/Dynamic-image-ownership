"""Six-arm reconstruction composition; no worker, loading or compute approval.

One source encode, historical controls, direct frozen-decoder refinement and
fixed-point inverse/replay of both the encoded and refined terminal latents.
Ordinary tests use owned CPU modules only. No watermark or decoder training.
"""
from copy import deepcopy
from dataclasses import dataclass, replace
import time

from .proposed import DiffusersComponents, EmbeddingError, _torch, padded_source
from .checkpointing import CheckpointedComponents
from .inversion import InversionPolicy, _latent, _real
from .inversion_path import PinnedDDIMPath, invert_roundtrip, module_fingerprint
from .latent_refinement import RefinementPolicy, refine


ARMS = ("vae_only", "ddim_zero_noise", "ddim_fixed_base_noise",
        "decoder_refinement", "fixed_point_encoded_inverse", "fixed_point_refined_inverse")


@dataclass(frozen=True)
class RefinementComparisonPolicy:
    refinement: RefinementPolicy
    inverse: InversionPolicy
    maximum_evaluations_per_inverse_arm: int
    maximum_seconds: float
    roundtrip_tolerance: float

    def __post_init__(self):
        if type(self.refinement) is not RefinementPolicy:
            raise EmbeddingError("explicit typed refinement policy required")
        if (type(self.inverse) is not InversionPolicy or self.inverse.method != "fixed_point"
                or self.inverse.prior_weight != 0):
            raise EmbeddingError("unmodified fixed-point inverse policy required")
        if (type(self.maximum_evaluations_per_inverse_arm) is not int
                or not 2 <= self.maximum_evaluations_per_inverse_arm <= 16384):
            raise EmbeddingError("invalid per-inverse evaluation ceiling")
        _real(self.maximum_seconds, "refinement comparison duration", 1e-6, 1100)
        _real(self.roundtrip_tolerance, "refinement comparison roundtrip tolerance", 0, 1)


def comparison(backend, source, base_noise, policy, *, progress, save_arm, save_state):
    """Compose fixed arms with durable caller saves, no selected scientific defaults.

    A normally terminated refinement (including budget/zero-gradient/line-search
    stops) remains an explicitly labeled diagnostic target, never quality success.
    Inverse nonconvergence records a failed arm without image or decoder fallback.
    Exceptions abort the entire composition with prior caller-owned saves intact.
    Final PNG metrics/safety/keys, exact approval and external kill belong to the
    separately reviewed future worker, not this cooperative software component.
    """
    torch = _torch()
    if (type(backend) not in (DiffusersComponents, CheckpointedComponents)
            or type(policy) is not RefinementComparisonPolicy):
        raise EmbeddingError("typed concrete components/comparison policy required")
    if any(not callable(callback) for callback in (progress, save_arm, save_state)):
        raise EmbeddingError("comparison journal and both persistence callbacks required")
    padded = padded_source(source, backend.settings.maximum_side)
    _latent(base_noise, "fixed comparison noise")
    shape = (1, 4, padded.shape[-2]//8, padded.shape[-1]//8)
    if (tuple(base_noise.shape) != shape or base_noise.device != source.device
            or source.device != backend.condition.device):
        raise EmbeddingError("comparison noise/source/conditioning grid or device mismatch")
    target = source.detach().clone()
    noise = base_noise.detach().clone()
    path = PinnedDDIMPath(backend)
    if policy.maximum_evaluations_per_inverse_arm < len(path.steps)+1:
        raise EmbeddingError("insufficient per-arm replay reservation")
    vae = backend.vae
    if (not isinstance(vae, torch.nn.Module)
            or not isinstance(getattr(vae, "decoder", None), torch.nn.Module)):
        raise EmbeddingError("explicit frozen VAE/decoder required")
    binding = module_fingerprint(vae)
    retained = tuple(vae.modules())+tuple(vae.parameters())+tuple(vae.buffers())
    methods = ((backend, "encode"), (backend, "reconstruct"), (backend, "decode_encoded"),
               (backend, "_decode"), (vae, "encode"), (vae, "decode"))
    method_bindings = []
    for owner, name in methods:
        method = getattr(owner, name)
        if getattr(method, "__self__", None) is not owner or getattr(method, "__func__", None) is None:
            raise EmbeddingError("comparison method must bind exact owner")
        method_bindings.append((owner, name, method.__func__))

    def guard():
        path._validate()
        if (backend.vae is not vae or module_fingerprint(vae) != binding
                or any(module.training for module in vae.modules())
                or float(vae.config.scaling_factor) != backend.settings.vae_scale):
            raise EmbeddingError("comparison frozen VAE identity/profile drift")
        for owner, name, function in method_bindings:
            method = getattr(owner, name)
            if (getattr(method, "__self__", None) is not owner
                    or getattr(method, "__func__", None) is not function):
                raise EmbeddingError("comparison bound method owner/function drift")
        for value in tuple(vae.parameters())+tuple(vae.buffers()):
            if (value.device != target.device or value.requires_grad
                    or (value.is_floating_point() and value.dtype != torch.float32)):
                raise EmbeddingError("comparison frozen VAE tensor profile drift")
    guard()
    deadline = time.monotonic()+policy.maximum_seconds
    outcomes = {}

    def check_time():
        if time.monotonic() >= deadline:
            progress({"phase": "refinement_comparison_time_limit", "completed_arms": tuple(outcomes)})
            raise EmbeddingError("refinement comparison cooperative time limit")

    def event(row):
        check_time(); guard()
        progress(deepcopy(row))
        guard(); check_time()

    def persist(arm, row, state):
        check_time(); guard()
        save_state(arm, deepcopy(row), state.detach().clone())
        guard(); check_time()

    event({"phase": "refinement_comparison_started", "arms": ARMS})
    event({"phase": "shared_encode_started"})
    with torch.no_grad():
        encoded = backend.encode(padded.clone())
    _latent(encoded, "shared encoded source")
    if tuple(encoded.shape) != shape or encoded.device != target.device:
        raise EmbeddingError("shared encoder latent profile mismatch")
    encoded = encoded.detach().clone()
    persist("shared_encoded", {"phase": "shared_encoded_target", "native_hw": tuple(target.shape[-2:])}, encoded)
    event({"phase": "shared_encode_completed"})
    refined = None
    refinement_status = None

    for arm in ARMS:
        event({"phase": "refinement_comparison_arm_started", "arm": arm})
        details = {"arm": arm, "native_hw": tuple(target.shape[-2:]),
                   "image_quality": "NOT_RUN", "safety": "NOT_RUN", "blind_detection": "NOT_RUN"}
        if arm in ARMS[:3]:
            with torch.no_grad():
                if arm == "vae_only":
                    image = backend.decode_encoded(encoded.clone())
                    calls = 0
                else:
                    arm_noise = torch.zeros_like(noise) if arm == "ddim_zero_noise" else noise.clone()
                    image = backend.reconstruct(encoded.clone(), arm_noise)
                    calls = len(path.steps)
            details.update(scheduler_evaluations=calls, target_identity="shared_encoded")
        elif arm == "decoder_refinement":
            remaining = deadline-time.monotonic()
            check_time()
            # Every inner stage is bounded by the remaining global deadline;
            # callback time is checked before/after every persistence operation.
            refinement_policy = replace(policy.refinement,
                maximum_seconds=min(policy.refinement.maximum_seconds, remaining))
            result = refine(backend, target.clone(), encoded.clone(), refinement_policy,
                progress=lambda row: event(dict(row, arm=arm)),
                save_state=lambda row, state: persist(arm, row, state))
            refined = result.latent.detach().clone()
            _latent(refined, "refined terminal target")
            if tuple(refined.shape) != shape or refined.device != target.device:
                raise EmbeddingError("refined terminal target profile mismatch")
            refinement_status = result.status
            image = result.native_image.detach().clone()
            details.update(refinement_status=result.status, continuous_mse_rgb01=result.mse_rgb01,
                penalized_objective=result.objective, displacement_l2=result.displacement_l2,
                decoder_evaluations=result.evaluations, backward_evaluations=result.backward_evaluations,
                actual_decoder_forward_starts=result.actual_decoder_forward_starts,
                checkpoint_recomputations=result.checkpoint_recomputations,
                target_identity="refined_terminal")
            persist(arm, {"phase": "refined_terminal_target", "refinement_status": result.status}, refined)
            del result
        else:
            terminal = encoded if arm == "fixed_point_encoded_inverse" else refined
            if terminal is None:
                raise EmbeddingError("missing refined target; no encoded fallback")
            details.update(target_identity="shared_encoded" if arm == "fixed_point_encoded_inverse"
                           else "refined_terminal", refinement_status=refinement_status if terminal is refined else None)
            remaining = deadline-time.monotonic()
            check_time()
            result = invert_roundtrip(path, terminal.detach().clone(), policy.inverse,
                maximum_evaluations=policy.maximum_evaluations_per_inverse_arm,
                maximum_seconds=remaining, roundtrip_tolerance=policy.roundtrip_tolerance,
                progress=lambda row: event(dict(row, arm=arm)),
                save_state=lambda row, state: persist(arm, row, state))
            details.update(path_status=result.status, scheduler_evaluations=result.evaluations,
                backward_evaluations=result.backward_evaluations,
                actual_unet_forward_calls=result.actual_unet_forward_calls,
                checkpoint_recomputation_calls=result.checkpoint_recomputation_calls,
                roundtrip_residual_max=result.roundtrip_residual_max)
            persist(arm, {"phase": "inverse_returned_state", "path_status": result.status}, result.state)
            if result.status != "completed":
                details["status"] = "not_rendered_nonconverged"
                event({"phase": "refinement_comparison_arm_failed", "arm": arm, "outcome": details})
                outcomes[arm] = deepcopy(details)
                del result
                continue
            persist(arm, {"phase": "replayed_terminal_state", "path_status": result.status}, result.reconstructed)
            with torch.no_grad():
                image = backend.decode_encoded(result.reconstructed.detach().clone())
            del result
        guard(); check_time()
        expected_shape = tuple(target.shape) if arm == "decoder_refinement" else tuple(padded.shape)
        if (not isinstance(image, torch.Tensor) or tuple(image.shape) != expected_shape
                or image.dtype != torch.float32 or image.device != target.device or image.requires_grad
                or not bool(torch.isfinite(image).all()) or float(image.min()) < 0 or float(image.max()) > 1):
            raise EmbeddingError("comparison native decoded image profile mismatch")
        native = image[:, :, :target.shape[-2], :target.shape[-1]].detach().clone()
        details["status"] = "rendered_requires_png_safety_quality"
        save_arm(arm, native.clone(), deepcopy(details))
        guard(); check_time()
        event({"phase": "refinement_comparison_arm_saved", "arm": arm, "outcome": details})
        outcomes[arm] = deepcopy(details)
        del image, native
    failed = tuple(arm for arm in ARMS if outcomes[arm]["status"] == "not_rendered_nonconverged")
    status = "completed_with_nonconverged_arms" if failed else "completed_requires_png_safety_quality"
    event({"phase": "refinement_comparison_terminated", "status": status, "failed_arms": failed,
           "scientific_acceptance": False})
    del retained
    return {"status": status, "arms": outcomes, "failed_arms": failed,
            "scientific_acceptance": False, "blind_detection": "NOT_RUN"}

"""Fixed five-arm native reconstruction comparison, no scientific CLI/approval.

One encode, unchanged legacy controls, fixed-point inversion and a safeguarded
GNRI-inspired L2 transition-prior candidate. No watermark or outcome selection.
Ordinary tests use only owned fake CPU components, never pretrained assets.
"""
from dataclasses import dataclass
import time

from .proposed import EmbeddingError, _torch, padded_source, DiffusersComponents
from .inversion import InversionPolicy, _latent, _real
from .inversion_path import PinnedDDIMPath, invert_roundtrip, module_fingerprint


ARMS = ("vae_only", "ddim_zero_noise", "ddim_fixed_base_noise",
        "fixed_point_inversion", "transition_prior_inversion")


@dataclass(frozen=True)
class ComparisonPolicy:
    fixed_point: InversionPolicy
    transition_prior: InversionPolicy
    maximum_evaluations_per_inverse_arm: int
    maximum_seconds: float
    roundtrip_tolerance: float

    def __post_init__(self):
        if (type(self.fixed_point) is not InversionPolicy
                or self.fixed_point.method != "fixed_point" or self.fixed_point.prior_weight != 0):
            raise EmbeddingError("unmodified fixed-point reference policy required")
        if (type(self.transition_prior) is not InversionPolicy
                or self.transition_prior.method != "guided_coordinate"
                or self.transition_prior.prior_weight <= 0 or self.transition_prior.prior_beta != 1):
            raise EmbeddingError("explicit positive transition-prior policy required")
        if (type(self.maximum_evaluations_per_inverse_arm) is not int
                or not 2 <= self.maximum_evaluations_per_inverse_arm <= 16384):
            raise EmbeddingError("invalid comparison inverse evaluation ceiling")
        _real(self.maximum_seconds,"comparison cooperative duration",1e-6,1100)
        _real(self.roundtrip_tolerance,"comparison roundtrip tolerance",0,1)


def comparison(backend, source, base_noise, policy, *, progress, save_arm, save_state):
    """Persist outputs as produced; return metadata only, no GPU image retention.

    save_arm(arm, native_image, metadata) and save_state(arm,row,latent) must be
    durable caller-owned callbacks. A nonconverged candidate gets a failed arm
    record and NO decoded image; continue only the next explicitly listed arm.
    Exceptions stop the whole package, preserve prior callbacks, no retries.
    """
    torch = _torch()
    if type(backend) is not DiffusersComponents or type(policy) is not ComparisonPolicy:
        raise EmbeddingError("typed concrete backend/comparison policy required")
    if any(not callable(callback) for callback in (progress,save_arm,save_state)):
        raise EmbeddingError("all comparison persistence callbacks required")
    padded = padded_source(source,backend.settings.maximum_side)
    if source.requires_grad:
        raise EmbeddingError("source must be fixed")
    shape = (1,4,padded.shape[-2]//8,padded.shape[-1]//8)
    _latent(base_noise,"fixed comparison noise")
    if tuple(base_noise.shape) != shape or base_noise.device != source.device:
        raise EmbeddingError("comparison noise grid/device mismatch")
    path = PinnedDDIMPath(backend)
    if policy.maximum_evaluations_per_inverse_arm < len(path.steps)+1:
        raise EmbeddingError("insufficient per-arm replay reservation")
    if source.device != path.condition.device:
        raise EmbeddingError("source and conditioning device mismatch")
    vae = backend.vae
    if not isinstance(vae,torch.nn.Module):
        raise EmbeddingError("explicit frozen VAE required")
    vae_binding = module_fingerprint(vae)
    retained = tuple(vae.modules())+tuple(vae.parameters())+tuple(vae.buffers())
    def guard():
        path._validate()
        if backend.vae is not vae or module_fingerprint(vae) != vae_binding:
            raise EmbeddingError("fixed comparison VAE identity or mutation drift")
        if (any(module.training for module in vae.modules())
                or float(vae.config.scaling_factor) != backend.settings.vae_scale):
            raise EmbeddingError("VAE evaluation/scaling drift")
        for value in tuple(vae.parameters())+tuple(vae.buffers()):
            if (value.device != source.device or value.requires_grad
                    or (value.is_floating_point() and value.dtype != torch.float32)):
                raise EmbeddingError("VAE dtype/device/gradient profile drift")
    guard()
    deadline = time.monotonic()+policy.maximum_seconds
    outcomes = {}
    def event(row):
        progress(dict(row))
        if time.monotonic() >= deadline:
            progress({"phase":"comparison_time_limit","completed_arms":tuple(outcomes)})
            raise EmbeddingError("comparison cooperative time limit exceeded")
    event({"phase":"comparison_started","arms":ARMS})
    with torch.no_grad():
        event({"phase":"comparison_encode_started"})
        latent = backend.encode(padded.clone())
        _latent(latent,"shared encoded source")
        if tuple(latent.shape) != shape or latent.device != source.device:
            raise EmbeddingError("shared encoder latent profile mismatch")
        latent = latent.detach().clone()
    guard()
    event({"phase":"comparison_encode_completed"})

    for arm in ARMS:
        guard()
        event({"phase":"comparison_arm_started","arm":arm})
        details = {"arm":arm,"native_hw":tuple(source.shape[-2:]),
                   "image_quality":"NOT_RUN","safety":"NOT_RUN","blind_detection":"NOT_RUN"}
        if arm in ARMS[:3]:
            with torch.no_grad():
                if arm == "vae_only":
                    image = backend.decode_encoded(latent.clone())
                    calls = 0
                else:
                    noise = torch.zeros_like(base_noise) if arm == "ddim_zero_noise" else base_noise.clone()
                    image = backend.reconstruct(latent.clone(),noise)
                    calls = len(path.steps)
            details.update(status="rendered_requires_png_safety_quality",scheduler_evaluations=calls)
        else:
            inverse_policy = policy.fixed_point if arm==ARMS[3] else policy.transition_prior
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                event({"phase":"comparison_time_limit_before_inverse","arm":arm})
                raise EmbeddingError("comparison time limit")
            result = invert_roundtrip(path,latent.clone(),inverse_policy,
                maximum_evaluations=policy.maximum_evaluations_per_inverse_arm,
                maximum_seconds=remaining,roundtrip_tolerance=policy.roundtrip_tolerance,
                transition_prior=(arm==ARMS[4]),
                progress=lambda row:event(dict(row,arm=arm)),
                save_state=lambda row,state:save_state(arm,dict(row),state.detach().clone()))
            details.update(path_status=result.status,scheduler_evaluations=result.evaluations,
                backward_evaluations=result.backward_evaluations,
                roundtrip_residual_max=result.roundtrip_residual_max)
            if result.status != "completed":
                details["status"]="not_rendered_nonconverged"
                outcomes[arm] = dict(details)
                event({"phase":"comparison_arm_failed","arm":arm,"outcome":dict(details)})
                del result
                continue
            with torch.no_grad():
                image = backend.decode_encoded(result.reconstructed.detach().clone())
            del result
            details["status"]="rendered_requires_png_safety_quality"
        guard()
        if (not isinstance(image,torch.Tensor) or tuple(image.shape) != tuple(padded.shape)
                or image.dtype != torch.float32 or image.device != source.device
                or image.requires_grad or not bool(torch.isfinite(image).all())
                or float(image.min()) < 0 or float(image.max()) > 1):
            raise EmbeddingError("comparison decoded image profile mismatch")
        native = image[:,:,:source.shape[-2],:source.shape[-1]].detach().clone()
        # Do not silently mark saved/completed when the caller could not persist.
        save_arm(arm,native.clone(),dict(details))
        guard()
        outcomes[arm] = dict(details)
        event({"phase":"comparison_arm_saved","arm":arm,"outcome":dict(details)})
        del image,native
    failed = tuple(arm for arm in ARMS if outcomes[arm]["status"]=="not_rendered_nonconverged")
    status = "completed_with_nonconverged_arms" if failed else "completed_requires_png_safety_quality"
    event({"phase":"comparison_terminated","status":status,"failed_arms":failed})
    # Retained object references keep guard bindings alive through all callbacks.
    del retained
    return {"status":status,"arms":outcomes,"failed_arms":failed,
            "scientific_acceptance":False,"blind_detection":"NOT_RUN"}

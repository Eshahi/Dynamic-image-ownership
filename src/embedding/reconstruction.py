"""Prospective fixed reconstruction localization component; no execution CLI.

Only owned fake CPU tensors may be used in ordinary tests. Actual components,
source pixels, saves/safety/metrics require a separately approved exact worker.
No model loading, data discovery, downloads, retries or optimizer here.
"""
from .proposed import EmbeddingError, _torch, _finite_tensor, padded_source, operation_phase

ARMS = ("vae_only", "ddim_zero_noise", "ddim_fixed_base_noise")


def localization(backend, source, base_noise, *, maximum_side, progress=None):
    """Hold encoded source/grid/schedule fixed; return every declared native arm.

    Zero initial noise is a diagnostic ablation, not the main method or an
    identity route: scheduler.add_noise still scales the latent. Never select
    its output as a replacement candidate after seeing metric results.
    """
    torch = _torch()
    if (type(maximum_side) is not int or not 256 <= maximum_side <= 8192
            or maximum_side % 64):
        raise EmbeddingError("maximum_side must be exact int256..8192, multiple64")
    padded = padded_source(source, maximum_side)
    shape = (1, 4, padded.shape[-2]//8, padded.shape[-1]//8)
    _finite_tensor(base_noise, "fixed base noise")
    if (tuple(base_noise.shape) != shape or base_noise.dtype != torch.float32 or
            base_noise.device != source.device or base_noise.requires_grad):
        raise EmbeddingError("fixed noise shape/dtype/device/profile mismatch")
    if any(not callable(getattr(backend, name, None)) for name in
           ("encode", "decode_encoded", "reconstruct")):
        raise EmbeddingError("explicit diagnostic backend required")
    outputs = {}
    # Clone each supplied tensor and each per-arm latent/noise: one callback
    # cannot silently change the input to a later comparison or caller source.
    with torch.no_grad():
        with operation_phase(progress, "localization_source_encode"):
            latent = backend.encode(padded.clone())
        _finite_tensor(latent, "fixed encoded source")
        if (tuple(latent.shape) != shape or latent.dtype != torch.float32 or
                latent.device != source.device or latent.requires_grad):
            raise EmbeddingError("encoded source contract mismatch")
        latent = latent.detach().clone()
        for arm in ARMS:
            with operation_phase(progress, arm):
                encoded = latent.clone()
                if arm == "vae_only":
                    image = backend.decode_encoded(encoded)
                else:
                    noise = torch.zeros_like(base_noise) if arm == "ddim_zero_noise" else base_noise.clone()
                    image = backend.reconstruct(encoded, noise)
                _finite_tensor(image, arm)
                if (tuple(image.shape) != tuple(padded.shape) or image.dtype != torch.float32
                        or image.device != source.device or image.requires_grad
                        or image.min().item() < 0 or image.max().item() > 1):
                    raise EmbeddingError("localization output profile mismatch: " + arm)
                outputs[arm] = image[:, :, :source.shape[-2], :source.shape[-1]].clone()
    return outputs

"""Prospective explicit phase residency, NOT enabled by the scientific worker.

No model imports or execution on import. Call only in a future exact-approved
worker. Preserve fp32 GPU conditioning/UNet/VAE arithmetic, and return safety
to the SAME GPU profile before saved-pixel checks. No inference offload hooks,
precision/model/source changes or allocator changes. Fit/parity are unproven.
"""
from .proposed import EmbeddingError, operation_phase


def _profile(module):
    values = tuple(module.parameters()) + tuple(module.buffers())
    return tuple((str(v.device), str(v.dtype), bool(v.requires_grad)) for v in values)


class PhaseResidency:
    """Single-use transition guard; failure is terminal, never a retry/fallback.

    RAM rises when idle components are parked. CPU transfer is not CPU forward:
    text conditioning must already have been computed on CUDA; safety forwards
    still happen on CUDA after UNet/VAE have been moved out of its way.
    """
    def __init__(self, models, *, progress=None):
        self.models, self.progress, self.state = models, progress, "new"
        pipeline, components = models.pipeline, models.components
        if components.vae is not pipeline.vae or components.unet is not pipeline.unet:
            raise EmbeddingError("pipeline/component module identity differs")
        condition = components.condition
        if str(condition.device) != "cuda:0" or str(condition.dtype) != "torch.float32" or condition.requires_grad:
            raise EmbeddingError("detached CUDA0 fp32 condition required")
        self.condition = condition
        self.modules = {name:getattr(pipeline,name) for name in ("vae","unet","text_encoder","safety_checker")}
        self.profiles = {}
        for name,module in self.modules.items():
            profile = _profile(module)
            if module.training or not profile or any(device != "cuda:0" or
                    dtype not in ("torch.float32", "torch.int64", "torch.int32", "torch.int16",
                                  "torch.int8", "torch.uint8", "torch.bool") or grad
                    for device,dtype,grad in profile):
                raise EmbeddingError("frozen CUDA0 fp32 module profile required")
            self.profiles[name] = profile

    def _check(self, devices):
        pipeline, components = self.models.pipeline, self.models.components
        if (components.condition is not self.condition or str(self.condition.device) != "cuda:0" or
                str(self.condition.dtype) != "torch.float32" or self.condition.requires_grad or
                components.vae is not self.modules["vae"] or components.unet is not self.modules["unet"]):
            raise EmbeddingError("active identity or detached conditioning profile changed")
        for name,module in self.modules.items():
            if (getattr(pipeline,name) is not module or module.training or
                    _profile(module) != tuple((devices[name],dtype,grad) for _,dtype,grad in self.profiles[name])):
                raise EmbeddingError("original module identity/eval/precision/freeze profile changed")

    def park_idle(self):
        if self.state != "new": raise EmbeddingError("one idle parking transition required")
        self.state = "failed_transition"  # remains terminal on any exception
        pipeline = self.models.pipeline
        with operation_phase(self.progress, "idle_components_to_cpu"):
            self._check({name:"cuda:0" for name in self.modules})
            for module in (pipeline.text_encoder, pipeline.safety_checker):
                before = _profile(module)
                module.to(device="cpu")
                after = _profile(module)
                if after != tuple(("cpu", dtype, grad) for _,dtype,grad in before):
                    raise EmbeddingError("idle transfer altered precision/freeze or failed")
            self._check({"vae":"cuda:0","unet":"cuda:0","text_encoder":"cpu","safety_checker":"cpu"})
        self.state = "optimization"

    def prepare_safety(self):
        if self.state != "optimization": raise EmbeddingError("safety transition requires parked optimization phase")
        self.state = "failed_transition"
        pipeline = self.models.pipeline
        with operation_phase(self.progress, "active_components_to_cpu_and_safety_to_cuda"):
            self._check({"vae":"cuda:0","unet":"cuda:0","text_encoder":"cpu","safety_checker":"cpu"})
            for module in (pipeline.vae, pipeline.unet):
                before = _profile(module)
                module.to(device="cpu")
                if _profile(module) != tuple(("cpu", dtype, grad) for _,dtype,grad in before):
                    raise EmbeddingError("active transfer altered precision/freeze or failed")
            before = _profile(pipeline.safety_checker)
            pipeline.safety_checker.to(device="cuda:0")
            if _profile(pipeline.safety_checker) != tuple(("cuda:0", dtype, grad) for _,dtype,grad in before):
                raise EmbeddingError("safety original GPU profile not restored")
            self._check({"vae":"cpu","unet":"cpu","text_encoder":"cpu","safety_checker":"cuda:0"})
        self.state = "safety"

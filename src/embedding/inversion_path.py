"""Pinned scheduler/UNet bridge and bounded source-conditioned latent roundtrip.

No loading, image decoding, scientific authorization or watermark replacement.
Call only from a separately approved exact-manifest worker for learned models.
"""
from dataclasses import dataclass, replace
import time
from types import MappingProxyType

from .proposed import DiffusersComponents, EmbeddingError, Settings, _torch, leading_suffix
from .inversion import DDIMPair, InversionPolicy, _latent, _same, _real, invert_pair


SCHEDULER_PROFILE = MappingProxyType({
    "num_train_timesteps": 1000, "beta_start": .00085, "beta_end": .012,
    "beta_schedule": "scaled_linear", "prediction_type": "epsilon",
    "timestep_spacing": "leading", "steps_offset": 1, "set_alpha_to_one": False,
    "clip_sample": False, "thresholding": False, "rescale_betas_zero_snr": False,
    "trained_betas": None,
})


@dataclass(frozen=True)
class PathStep:
    timestep: int
    pair: DDIMPair


class PinnedDDIMPath:
    """Bridge to already-loaded, frozen fp32 SD1.5 components; no model loads.

    Profile checks are accidental-drift guards, not weight authenticity or a
    sandbox for hostile models. Asset hashes remain the manifest loader's job.
    """
    def __init__(self, backend):
        import diffusers
        from diffusers import DDIMScheduler
        torch = _torch()
        if diffusers.__version__ != "0.35.1" or type(backend) is not DiffusersComponents:
            raise EmbeddingError("requires pinned concrete Diffusers components")
        if type(backend.settings) is not Settings or type(backend.scheduler) is not DDIMScheduler:
            raise EmbeddingError("invalid bound settings/scheduler type")
        self.backend = backend
        self.settings = backend.settings
        self.model = backend.unet
        self.scheduler = backend.scheduler
        self.condition = backend.condition.detach().clone()
        self.reference = DDIMScheduler(**SCHEDULER_PROFILE)
        self.reference.set_timesteps(self.settings.inference_steps)
        self.times = tuple(leading_suffix(self.settings.inference_steps, self.settings.strength))
        stride = 1000 // self.settings.inference_steps
        self.steps = tuple(PathStep(t, DDIMPair(
            float(self.reference.alphas_cumprod[t]),
            float(self.reference.alphas_cumprod[t-stride] if t-stride >= 0
                  else self.reference.final_alpha_cumprod))) for t in self.times)
        if any(left.pair.previous_alpha != right.pair.alpha
               for left,right in zip(self.steps,self.steps[1:])):
            raise EmbeddingError("noncontiguous pinned DDIM pairs")
        # Desired encoded source is the actual post-final-step decoder latent,
        # not an assertion that final_alpha==1 (this pinned profile uses alpha[0]).
        self.terminal_alpha = self.steps[-1].pair.previous_alpha
        self._bound_steps = self.steps
        self._validate()
        self._module_binding, self._tensor_binding = self._fingerprint_model()
        # Retain original objects, so a removed object's numeric id cannot be
        # recycled into a false identity match during the path's lifetime.
        self._bound_modules = tuple(module for _,module in self.model.named_modules(remove_duplicate=False))
        self._bound_tensors = tuple(tensor for _,tensor in self.model.named_parameters(remove_duplicate=False)) + tuple(
            tensor for _,tensor in self.model.named_buffers(remove_duplicate=False))

    def _fingerprint_model(self):
        modules = tuple((name,id(module),type(module),module.training)
                        for name,module in self.model.named_modules(remove_duplicate=False))
        tensors = []
        for kind,iterator in (("parameter",self.model.named_parameters(remove_duplicate=False)),
                              ("buffer",self.model.named_buffers(remove_duplicate=False))):
            for name,tensor in iterator:
                try:
                    version = tensor._version
                except RuntimeError as error:
                    raise EmbeddingError("untracked inference tensor cannot bind fixed predictor") from error
                tensors.append((kind,name,id(tensor),version,tuple(tensor.shape),tuple(tensor.stride()),
                                tensor.dtype,tensor.device,tensor.requires_grad))
        return modules,tuple(tensors)

    def _validate(self):
        torch = _torch()
        b = self.backend
        if (b.settings != self.settings or b.unet is not self.model
                or b.scheduler is not self.scheduler or tuple(b.times) != self.times
                or self.steps != self._bound_steps
                or self.terminal_alpha != self._bound_steps[-1].pair.previous_alpha):
            raise EmbeddingError("bound backend identity/schedule drift")
        if any(self.scheduler.config.get(k) != v for k,v in SCHEDULER_PROFILE.items()):
            raise EmbeddingError("scheduler configuration drift")
        if (self.scheduler.num_inference_steps != self.settings.inference_steps
                or self.scheduler.timesteps.tolist() != self.reference.timesteps.tolist()
                or not torch.equal(self.scheduler.alphas_cumprod.cpu(),self.reference.alphas_cumprod)
                or not torch.equal(self.scheduler.final_alpha_cumprod.cpu(),self.reference.final_alpha_cumprod)):
            raise EmbeddingError("scheduler coefficient/timestep drift")
        condition = b.condition
        if (not isinstance(condition,torch.Tensor) or condition.dtype != torch.float32
                or tuple(condition.shape) != (1,77,768) or condition.requires_grad
                or condition.device != self.condition.device
                or not bool(torch.isfinite(condition).all())
                or not torch.equal(condition,self.condition)):
            raise EmbeddingError("fixed conditioning drift")
        if (not isinstance(self.model,torch.nn.Module)
                or any(module.training for module in self.model.modules())
                or self.model.config.in_channels != 4 or self.model.config.out_channels != 4
                or self.model.config.cross_attention_dim != 768):
            raise EmbeddingError("UNet evaluation/shape profile drift")
        for parameter in self.model.parameters():
            if (parameter.requires_grad or parameter.dtype != torch.float32
                    or parameter.device != condition.device):
                raise EmbeddingError("UNet parameter profile drift")
        for buffer in self.model.buffers():
            if (buffer.device != condition.device or buffer.requires_grad
                    or (buffer.is_floating_point() and buffer.dtype != torch.float32)):
                raise EmbeddingError("UNet buffer profile drift")
        if hasattr(self,"_module_binding"):
            if self._fingerprint_model() != (self._module_binding,self._tensor_binding):
                raise EmbeddingError("bound UNet module/tensor identity or mutation drift")

    def predict(self, state, step):
        self._validate()
        if type(step) is not PathStep or step not in self.steps:
            raise EmbeddingError("unbound inversion timestep")
        _latent(state,"predictor input",allow_grad=True)
        if state.device != self.condition.device:
            raise EmbeddingError("predictor device mismatch")
        prediction = self.model(state.clone(),step.timestep,
                                encoder_hidden_states=self.condition.clone()).sample
        self._validate()  # a forward-side profile mutation is not an accepted call
        _same(prediction,state,"UNet epsilon",allow_grad=True)
        return prediction


@dataclass(frozen=True)
class PairSummary:
    timestep: int
    status: str
    evaluations: int
    backward_evaluations: int
    residual_max: float
    objective: float


@dataclass(frozen=True)
class PathResult:
    status: str
    state: object
    reconstructed: object
    evaluations: int
    backward_evaluations: int
    pair_results: tuple
    roundtrip_residual_max: object


def invert_roundtrip(path, terminal, policy, *, maximum_evaluations,
                     maximum_seconds, roundtrip_tolerance, progress, save_state,
                     prior_means=None):
    """Invert reverse order, replay forward order, stop on any failed pair.

    Requires caller-owned progress and persistence callbacks. No filesystem is
    written here. Cooperative deadline does not kill a stuck model operation;
    official runner must independently enforce external time/memory boundaries.
    """
    torch = _torch()
    if type(path) is not PinnedDDIMPath or type(policy) is not InversionPolicy:
        raise EmbeddingError("typed pinned path/policy required")
    _latent(terminal,"terminal")
    if not callable(progress) or not callable(save_state):
        raise EmbeddingError("progress and partial-state persistence required")
    if type(maximum_evaluations) is not int or not len(path.steps)+1 <= maximum_evaluations <= 16384:
        raise EmbeddingError("invalid whole-path evaluation ceiling")
    _real(maximum_seconds,"path time limit",1e-6,1200)
    _real(roundtrip_tolerance,"roundtrip tolerance",0,1)
    path._validate()
    if terminal.device != path.condition.device:
        raise EmbeddingError("terminal device mismatch")
    if policy.prior_weight > 0:
        if type(prior_means) is not tuple or len(prior_means) != len(path.steps):
            raise EmbeddingError("one declared prior per denoising-order step required")
        for mean in prior_means:
            _same(mean,terminal,"path prior mean")
        if terminal.numel()*len(prior_means) > 4_194_304:
            raise EmbeddingError("declared prior snapshot exceeds 16 MiB fp32 cap")
        prior_means = tuple(mean.detach().clone() for mean in prior_means)
    elif prior_means is not None:
        raise EmbeddingError("unused prior means forbidden")
    terminal = terminal.detach().clone()
    x = terminal.clone()
    results = []
    nfe = backward = 0
    deadline = time.monotonic()+maximum_seconds

    def check_time():
        if time.monotonic() >= deadline:
            progress({"phase":"path_time_limit", "evaluations":nfe,
                      "backward_evaluations":backward})
            raise EmbeddingError("cooperative path time limit exceeded")

    def finish(status, reconstructed=None, error=None):
        progress({"phase":"path_terminated","status":status,"evaluations":nfe,
                  "backward_evaluations":backward,"roundtrip_residual_max":error})
        return PathResult(status,x.detach().clone(),
            None if reconstructed is None else reconstructed.detach().clone(),
            nfe,backward,tuple(results),error)

    for index in reversed(range(len(path.steps))):
        step = path.steps[index]
        check_time()
        # Reserve every replay call, rather than succeeding with no roundtrip budget.
        available = maximum_evaluations-nfe-len(path.steps)
        if available < 1:
            return finish("evaluation_budget")
        pair_policy = replace(policy,max_evaluations=min(policy.max_evaluations,available))
        progress({"phase":"pair_started","timestep":step.timestep,
                  "denoising_index":index,"available_pair_evaluations":pair_policy.max_evaluations})

        def pair_progress(row):
            nonlocal nfe,backward
            if row["phase"] == "evaluation_started":
                check_time()
                nfe += 1
            elif row["phase"] == "backward_started":
                check_time()
                backward += 1
            progress(dict(row,timestep=step.timestep,denoising_index=index,
                          path_evaluations=nfe,path_backward_evaluations=backward))
            # Publish already-measured outcomes before a cooperative refusal.
            if row["phase"] not in ("evaluation_started","backward_started"):
                check_time()

        result = invert_pair(step.pair,x,lambda state:path.predict(state,step),pair_policy,
            prior_mean=None if prior_means is None else prior_means[index],progress=pair_progress)
        results.append(PairSummary(step.timestep,result.status,result.evaluations,
            result.backward_evaluations,result.residual_max,result.objective))
        row = {"phase":"pair_state","timestep":step.timestep,"denoising_index":index,
               "status":result.status,"evaluations":nfe,"backward_evaluations":backward,
               "residual_max":result.residual_max}
        save_state(dict(row),result.state.detach().clone())
        progress(row)
        x = result.state.detach().clone()
        check_time()
        if result.status != "converged":
            return finish("pair_not_converged")
    replay = x.clone()
    for index,step in enumerate(path.steps):
        check_time()
        if nfe >= maximum_evaluations:
            return finish("evaluation_budget")
        nfe += 1
        row = {"phase":"replay_started","timestep":step.timestep,
               "denoising_index":index,"evaluations":nfe}
        progress(dict(row))
        with torch.no_grad():
            replay = step.pair.denoise(replay,path.predict(replay,step)).detach()
        row.update(phase="replay_state")
        save_state(dict(row),replay.clone())
        progress(row)
        check_time()
    error = float((replay-terminal).abs().max())
    return finish("completed" if error <= roundtrip_tolerance else "roundtrip_residual_failed",
                  replay,error)

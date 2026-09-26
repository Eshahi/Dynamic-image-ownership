"""Opt-in software candidate; not wired into a worker or approved manifest.

Checkpoint each UNet call and VAE decoder separately. No model loading, dtype,
resolution, scheduler, objective, cap, or source substitution. CPU owned fixtures
do not establish SD numerical parity or CUDA fit. Requires new reviewed execution.
"""
from src.embedding.proposed import DiffusersComponents, EmbeddingError, _torch


class CheckpointedComponents(DiffusersComponents):
    profile_id = "unet-each-vae-decode-nonreentrant-rng-preserved-v1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if _torch().__version__.split("+")[0] != "2.12.1":
            raise EmbeddingError("checkpoint candidate requires Torch 2.12.1")
        self._frozen_profile = self._profile()

    def _profile(self):
        def tensor(value):
            return (id(value), value._version, str(value.device), str(value.dtype),
                    tuple(value.shape), value.requires_grad)
        models = tuple((id(model), tuple((id(m), m.training) for m in model.modules()),
                        tuple((name, tensor(v)) for name, v in model.named_parameters()),
                        tuple((name, tensor(v)) for name, v in model.named_buffers()))
                       for model in (self.vae, self.unet))
        schedule = tuple((name, tensor(getattr(self.scheduler, name))) for name in
                         ("alphas_cumprod", "final_alpha_cumprod", "timesteps"))
        return (models, tensor(self.condition), id(self.scheduler), schedule,
                tuple(sorted(dict(self.scheduler.config).items())),
                self.scheduler.num_inference_steps, self.times, self.settings)

    def _checked(self, function, state):
        torch = _torch()
        if self._profile() != self._frozen_profile:
            raise EmbeddingError("checkpoint component profile changed before forward/replay")
        def guarded(value):
            if self._profile() != self._frozen_profile:
                raise EmbeddingError("checkpoint component profile changed before forward/replay")
            return function(value)
        if not torch.is_grad_enabled() or not state.requires_grad:
            return guarded(state)
        from torch.utils.checkpoint import checkpoint
        return checkpoint(guarded, state, use_reentrant=False,
                          preserve_rng_state=True, determinism_check="default")

    def _predict(self, state, timestep):
        # Default argument binds this call's timestep; no loop-variable closure.
        def prediction(value, fixed_timestep=timestep):
            return self.unet(value, fixed_timestep,
                             encoder_hidden_states=self.condition).sample
        return self._checked(prediction, state)

    def _decode(self, state):
        return self._checked(lambda value: self.vae.decode(value).sample, state)

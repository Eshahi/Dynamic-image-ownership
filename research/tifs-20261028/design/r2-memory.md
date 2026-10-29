# R2-3 memory correction (pre-output, 2026-10-29)

No scientific operation was run locally. The writer memory intervention is activation checkpointing only; fp32, image sizes, objectives, updates, seeds and frozen parameters remain unchanged.

## Primary source inspected online

Diffusers tag **v0.35.1**, read 2026-10-29:

- [vae.py Encoder.forward, lines 143-159; Decoder.forward, lines 260-283](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/autoencoders/vae.py#L143): encoder down/middle blocks and decoder middle/up blocks use the checkpoint path when autograd is enabled and their checkpoint flag is true. Eval mode does not suppress that path.
- [AutoencoderKL, line 67](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/autoencoders/autoencoder_kl.py#L67): advertises checkpoint support.
- [ModelMixin.enable_gradient_checkpointing, lines 258-283](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/models/modeling_utils.py#L258), and `_set_gradient_checkpointing`, lines 1640-1653: sets the function and flags on supporting submodules; default PyTorch checkpoint is non-reentrant on the pinned modern torch runtime, allowing the writer's `autograd.grad` calls. A bespoke wrapper is unnecessary.

Implementation: `writer_gradient_scope` wraps writer optimization and its diagnostic gradients. It enables SD1.5 and already-loaded SDXL; a lazy SDXL registers on first use. Registration checks frozen eval state and both encoder/decoder flags. Flags persist until backward finishes and are disabled in `finally`, retaining local references when close clears model fields. Ordinary readers, final native verification, quality and native regeneration do not enable checkpointing. Non-gradient calls inside the rehearsal scope bypass checkpointing through the upstream gradient-mode condition.

## Capacity rule

`capacity` takes measured GPU total as a separate argument from filesystem total. Minimum hardware is 24 GB class (24,000,000,000 bytes). The tested-fit limit is measured GPU total less 1536 MiB. Forecast receipts export `device_total_bytes`, `gpu_margin_bytes`, `gpu_limit_bytes`, `gpu_ok`, `minimum_gpu_bytes` and policy `measured-total-minus-1.5GiB-v1`. All rehearsal totals must exist and agree. A 48 GiB GPU can pass with a 35 GiB peak; a 24 GiB GPU fails at 23 GiB peak because its reserved margin is unavailable. Device telemetry already contains the total; launch must compare current total with the forecast total, including resumed invocation paths.

Disk policy remains 1.5 times scaled artifacts plus 20% filesystem free. Peak accounting retains max-reserved allocator high-water plus endpoint non-allocator usage, including model loads; this is a conservative estimator from available telemetry, not continuously sampled external-device high-water proof. Full rehearsal with native families, readers, quality and all arms is still decisive. Any OOM is RESOURCE_STOP, and a 24 GB class minimum is never evidence of successful SDXL backward fit.

## Validation and integration

21 pure-logic tests passed (7 writer, 14 forecast) under the permitted stdlib interpreter with `-I`; no scientific modules imported and no constructor executed. Tests exercise lifecycle cleanup, lazy SDXL, invalid VAE flags, device margin boundaries, larger cards, telemetry omissions/device changes and previous timing guards. Compilation is checked separately. GPU behavior and time savings/cost remain unmeasured until the authorized server rehearsal.

Integration requested from main agent: update RUNBOOK and frozen config descriptions to writer-only checkpointing and measured-total reserve; add current-device comparison in `screen_launch` and matching launch tests. No RUNBOOK, config or runtime file was edited by this subtask.

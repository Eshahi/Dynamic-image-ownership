# Round 2 pre-output amendment

Date: 2026-10-29. Base reviewed implementation: `665b4dd`; Round 2 begins at `071c8ec` after Claude's two brief commits. No Stage S scientific output exists. This file records prospective changes before the later server rehearsal. All retained methods, thresholds and outputs stay unchanged. Paid execution and held-out confirmation are not authorized by this amendment.

## R2-3: activation memory and measured capacity

Enable native diffusers 0.35.1 non-reentrant gradient checkpointing only for the F6 writer's gradient scopes, on the SD1.5 reader VAE and lazily loaded SDXL VAE, both frozen and in eval mode. Primary-source inspection confirms encoder and decoder gate on gradient mode rather than `.training`. The objective, steps, precision and native generation settings do not change. Flags are restored after normal/exceptional exit before final native verification. See `design/r2-memory.md` and `stage-s/writer-implementation.md`.

Replace the hard 24 GiB peak ceiling with the measured device total minus **1.5 GiB**. Minimum hardware is 24 GB class; fit remains unproven until rehearsal. Forecast receipts require identical device totals. Initial screen launch and every resume validate the measured total and reserve policy. Larger cards may qualify when the measured peak exceeds 24 GiB. Disk margin, 15-hour cap, complete-inventory forecast and OOM RESOURCE_STOP remain unchanged. Checkpoint recomputation cost is included in the later measured forecast.

## Pending items

R2-1 prior-art conclusion (including ForenMark if delivered), R2-2 bound-carrier protocol and article comparison, R2-4 inventory/cost, and R2-5 independent review will be recorded here before readiness is restored. The Round 1 numerical F6 thesis gates are not amended.

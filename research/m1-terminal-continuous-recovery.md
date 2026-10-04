# A-C execution-memory recovery

Version `inference-model-offload-v1`, 2026-10-04. Execution-only recovery of the unchanged `m1-terminal-continuous-v1` scientific pilot. No GPU run was performed for this diagnosis or patch. This is neither a scientific negative for source4795 nor a claim that a GPU tensor leak has been proved.

## Retained failure and diagnosis

MAIN `20261004-0940-terminal-continuous` used commit `7be2a6c1cf73ea16138b04b407773af5fc24218b`. Its immutable run receipt SHA256 is `63d122b0d355bd6747641e6ddee9db51f417e6432a3346dc9e83b264331d4463`. Source1675 completed100 updates and all four saved-image conditions: clean quality/dual detection and VAE semantic gates pass; all14 applicable negative queries pass. Source4795 saved step000, then failed in its first cycle-loss backward. Overall outcome remains failed/incomplete; the two-source gate is not passed. The formal failed-attempt analysis at `69e7b95`, MAIN `20261004-0950-terminal-continuous-analysis`, retains those missing rows.

The error reports9.67GiB PyTorch allocated,332.85MiB reserved but unallocated, a failed128MiB request and the configured10GiB allocator limit. This is an instantaneous **backward-pass** allocation, not measured idle retention between sources. No boundary allocation snapshots existed in the original run, so attribution to a reader leak, fragmentation or another process would be unsupported.

Code inspection found: both VAE models and the safety model were loaded before the first source; the public reader cache contains CPU NumPy arrays; CLIP and LPIPS run on CPU; saved fp32 diagnostics are NumPy; final embedding tensors are no-grad and explicitly deleted after each source. A CPU analytic20-update checkpoint-lifetime probe retained zero tracked decoder/encoder tensors after returning and deleting the result, with garbage collection both enabled and disabled. CUDA stayed uninitialized. This probe does not prove real-VAE graph lifetime, but did not reproduce the suspected persistent-tensor explanation.

An exact safetensors-header count identifies **739.358MiB** of avoidably resident inference weights: fp16 VAE167,307,726bytes (159.557MiB) and safety checker607,965,232bytes (579.801MiB). Neither participates in the differentiable optimizer, which uses its separate fp32 VAE. Moving them out during fitting provides concrete headroom; it does not explain all9.67GiB or guarantee recovery success.

## Minimal patch and unchanged science

Immediately before each `optimize()` call, move only the frozen fp16 reader VAE and safety checker to CPU; collect Python garbage and empty the unused CUDA cache. Restore both models to CUDA immediately after optimization, before every saved-image safety/readout/quality assessment. Dtypes, tensor values, frozen status and reader implementation stay unchanged. The fp32 embedding VAE remains on CUDA throughout. No slicing, tiling, mixed precision, changed autograd checkpointing, allocator-limit increase, objective, loss weight, steps, learning rate, source, initialization, threshold, cap or owner was introduced.

Record synchronized allocated/reserved/peak/free/total CUDA bytes before and after both transfers, the actual model parameter/buffer byte counts and the placement stage in the journal and case record. These prospective measurements distinguish reclaimed live model storage from cached storage. They must be inspected after recovery; successful execution alone cannot retrospectively prove the original cause.

## Fresh replay, not a cross-commit resume exception

The existing identical-commit checkpoint-resume rule is unchanged. After committing this patch, run both sources afresh from their original **unmarked reconstruction step200** inputs, using the identical frozen manifest and seed. Retain the original watermark checkpoints as evidence; neither original step100 nor step000 initializes the fresh optimization. The fresh run has its own1800s cap and unique directory; aggregate original and recovery durations must be disclosed rather than treating the original expenditure as zero.

Pass `--replay-reference <MAIN/20261004-0940-terminal-continuous>` along with the existing `--run --manifest research/m1-terminal-continuous-dev.json --output-dir <fresh MAIN directory>`. This optional recovery control is incompatible with `--resume-from`. It requires an identical scientific configuration and exactly one completed first source in the reference. It hashes/records that reference and performs no optimization from its watermark state.

After fresh source1675 assessment and **before** starting4795, verify exact source/initialization receipts; all four clean/VAE C0/C1 PNG hashes; all eight fp16/fp32 terminal-reader NumPy artifact hashes; every owner decision; and the step100 latent, Adam state, RNG state and step. Check old and fresh artifacts against their own receipts. Checkpoint-file bytes and embedded commit identity are expected to differ, so scientific tensor/state equality is checked directly with CPU `torch.equal`, not pickle-file equality. A parity failure stops the run and retains the discrepancy; it never selects the favorable old result. Replayed1675 is still one development source, not an extra independent trial.

## Verification and remaining uncertainty

All15 existing and recovery CPU tests pass in1.337s with `CUDA_VISIBLE_DEVICES=-1`; CUDA remains uninitialized. Tests cover frozen model-placement value/dtype preservation, rejection of trainable models, acceptance of identical scientific endpoints with different provenance, and rejection of changed latent/Adam/RNG/step, image bytes, missing rows, decisions or initialization. AST comparison against the original commit confirms14 scientific/reader/checkpoint/RNG function or class definitions are unchanged, including `optimize`, `configuration` and both checkpoint functions. CLI help and diff whitespace checks pass. CPU synthetic tests do not certify real GPU memory savings or scientific parity; the fresh run must supply those observations. No old output, public core, scientific manifest, protected file or lifecycle state is changed.

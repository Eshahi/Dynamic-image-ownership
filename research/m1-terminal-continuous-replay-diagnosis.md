# A-C replay divergence and deterministic execution amendment

Version `ac-deterministic-execution-v1`, prospective2026-10-04 after the retained offload replay failure. Method/execution escalation gpt-6-astra/xhigh. CPU diagnosis only; no GPU computation was performed by this document's author. The original scientific thresholds, objective,100-update budget, optimizer, source initialization and production reader remain unchanged. The previous exact replay **failed** and is not reclassified as passed.

## Retained evidence and localization

The original MAIN `20261004-0940-terminal-continuous` run.json SHA-256 is `63d122b0d355bd6747641e6ddee9db51f417e6432a3346dc9e83b264331d4463`. The fresh offload recovery `20261004-0955-terminal-continuous-recovery`, at3f464ab, failed after source1675 because its exact endpoint replay differed; run.json SHA-256 `98b7df2bec9d8d344b880c13b04363f5582bf2d885de2bd7580ed09b96510f12`. Source4795 was not attempted. Preserve both incomplete attempts, their checkpoints and time costs. The recovery's four first-source conditions are exploratory observations, not a passed two-source gate.

CPU comparison with CUDA hidden found exact equality of source RGB8, source CLIP vector, pHash, reconstruction receipt, step000 latent, `reference.npy=D(u0)`, both C0 PNGs, and all four C0 fp16/fp32 terminal latent arrays. The Python/Torch/NumPy/diffusers versions and effective10GiB allocation caps agree. The step1 before-update clean semantic/instance values and cycle values are exactly equal. The first recorded difference is the gradient norm: `2.4118926525115967` versus `2.411892890930176`, a difference of approximately2.38e-7. The full first-step gradients were not retained, so their exact difference and which backward kernel produced it cannot be recovered retrospectively.

By step2 the before-update semantic scores differ by6.56e-6. Drift then accumulates rather than appearing as a new source, feature or endpoint-only change:

| Saved update | Max absolute unscaled-latent difference | Latent RMS difference | Relative L2 difference |
|---:|---:|---:|---:|
|0|0|0|0|
|10|.0058145523|.0001769995|.0000346757|
|20|.0109689236|.0006395644|.0001252971|
|50|.1767241955|.0066092506|.0012950046|
|100|.2848367691|.0080755573|.0015826024|

The final latent differs at16382/16384 coordinates; its difference L2 is1.03367133 against original latent L2 norm653.1465563. Source1675 clean C1 old-versus-new RGB8 RMSE is.335356 byte units, PSNR57.620683dB, with30419/786432 channels changed and maximum difference33. After the VAE cycle the corresponding RMSE is1.127778, PSNR47.086334dB and maximum71. These are actual changes, not just differently serialized checkpoints.

The recovery source1675 clean quality is36.352119dB/.980146/.010342 LPIPS, clean scores5.875762/7.347244, and VAE scores5.695704/6.320359. Its operational outcomes happen to match the original, but matching labels cannot certify numerical equivalence or excuse the failed replay. No tolerance was tuned to include these endpoints.

The measured placement reduced live allocation from1,159,884,288 to373,480,960bytes, reclaiming786,403,328bytes (750MiB including allocator/storage effects). The reported inference tensor bytes remain775,272,958 (739.358MiB). Optimization reached peak9,731,623,936bytes under the cap. The concrete memory benefit is measured. There is still no evidence that offload alone caused the drift: no same-placement repeat was run. A nondeterministic backward kernel or a changed allowed numerical execution path is consistent with the first observed difference. A memory leak, particular cuDNN algorithm, incorrect gradient or causal offload effect is not proved.

The code sets seeds, disables TF32 and disables cuDNN benchmarking, but did not enable deterministic algorithms. The inspected, version-matched [PyTorch2.12.1 reproducibility guidance](https://github.com/pytorch/pytorch/blob/v2.12.1/docs/source/notes/randomness.rst) distinguishes deterministic algorithm selection from an algorithm's own nondeterministic execution. Its [deterministic API](https://github.com/pytorch/pytorch/blob/v2.12.1/torch/__init__.py) supports deterministic alternatives or an error where an operation lacks one. These primary sources justify a deterministic-execution diagnostic; they do not identify the kernel responsible for this run.

## Prospective remedy: strict independent-process prefix

Use the same scientific method under a separately recorded execution variant `ac-deterministic-execution-v1`. Before any CUDA initialization, set `torch.use_deterministic_algorithms(True,warn_only=False)`, `torch.backends.cudnn.deterministic=True`, preserve `benchmark=False` and both TF32 flagsFalse, and set fixed `CUBLAS_WORKSPACE_CONFIG=:4096:8`. Reject a conflicting preexisting workspace value rather than silently overriding it. This workspace value is an explicit execution choice, not a claim that every operation in this installed release requires it. Record all settings, actual device/CUDA/cuDNN identity and package versions. Do not switch attention implementation, slice/tiling behavior, dtype, loss or optimizer preemptively. An unsupported nondeterministic operation must fail closed, with its traceback retained.

First run exactly two fresh **independent processes**, source1675 only, from its original unmarked step200 checkpoint, using the original pilot manifest. Each executes only the first10 of the fixed100 Adam updates through the unchanged `optimize()` implementation. No marked checkpoint initializes either process. Each begins from the same seed/config/source and mirrors the full runner's model loading, safety source check and inference-model offload. It retains all10 full fp32 gradient tensors, before/after-update trajectory values, step0/10 latent/Adam/RNG state, source descriptors, and baseline/final/surrogate arrays. Gradients are copied after each update while the pre-update gradient is still present, before the next `zero_grad`; this timing does not recompute a different gradient.

These records use `run_kind=ac-gradient-prefix-v1`, outcome `probe_completed`, an empty scientific condition inventory, and `gate=null`. They are not ten-step candidate enrollments, shorter alternatives, two independent images or valid inputs to the scientific analyzer. The model/parameter manifest still declares100 scientific updates; `repeatability_prefix_updates=10` explicitly records the diagnostic truncation. The original1800s/10GiB-or-lower/16GiB/500MiB guards apply to each fresh prefix process. No default-nondeterministic extra probe is required unless this bounded check fails and new evidence warrants it.

CPU comparison requires exact equality of all10 full nonzero finite gradient arrays; all before/after-update measurements; source/features/initialization; step0/10 latent, Adam, RNG and step; and all three retained forward arrays. Gradient-norm agreement alone is insufficient. Metadata must identify distinct process IDs, exact executed-code/config/model bytes, device identity and numerical settings. Different artifact paths, process IDs and execution commits are provenance, not tensor values. Comparison outputs preserve both input run hashes and all array/checkpoint receipts. Any discrepancy fails; no `allclose` relaxation, winning prefix selection or replacement of the first failed probe is permitted.

Passing this probe establishes a repeatable **ten-step prefix** on this pinned stack, not proof that all100 updates or another platform must be bitwise identical. The completion receipt states this limit. It is adequate to proceed with the unchanged full pilot under the now explicit deterministic contract; any later exact-continuation divergence still fails its own check. Do not demand that deterministic execution reproduce the old, unvalidated nondeterministic Adam trajectory. That old comparison remains descriptive and failed, not erased. The old source1675 output is never selected in place of the new variant's output.

## Commands and execution boundaries

Commit the worker, prefix helper, documentation and tests first. With science Python, run these sequentially in separate processes and fresh MAIN development directories:

```text
scripts/m1_terminal_repeatability.py --probe --manifest research/m1-terminal-continuous-dev.json --output-dir <fresh-prefix-a>
scripts/m1_terminal_repeatability.py --probe --manifest research/m1-terminal-continuous-dev.json --output-dir <fresh-prefix-b>
scripts/m1_terminal_repeatability.py --compare <fresh-prefix-a> <fresh-prefix-b> --output-dir <fresh-comparison>
```

Only if the CPU comparison passes, run the full1675/4795 pilot afresh:

```text
scripts/m1_terminal_continuous.py --run --manifest research/m1-terminal-continuous-dev.json --repeatability-receipt <fresh-comparison>/run.json --output-dir <fresh-deterministic-pilot>
```

No old `--replay-reference` is supplied. The worker rejects an old execution variant as a deterministic replay target, rejects a prefix as a resume source, revalidates the comparison's input/gradient/checkpoint hashes before fitting, and checks current scientific dependency bytes/config against the probes. A report-only commit can differ, but changed script/config/model bytes cannot use the old receipt. Current deterministic settings, package/device identity must match the checked receipt. Ordinary optimizer checkpoint resume remains the existing stricter exact-commit/receipt mechanism in this pilot; expansion's proposed scalable wrapper is separate and not implemented by this fix.

The full pilot still requires both clean source-quality conjunctions, both blind clean `both_match`, both VAE semantic passes, all28 C0/wrong-owner queries below both thresholds, valid complete32-query evidence, and successful repeatability receipt validation. Do not lower a score threshold, replace a source or exempt a changed state. A failed deterministic prefix or pilot remains failed/incomplete. Expansion is prohibited until this amended prospective execution gate and all original scientific gates pass.

The scientific analyzer must recognize the new helper/doc dependencies and execution variant, revalidate the repeatability receipt, and explicitly reject `probe_completed`/`ac-gradient-prefix-v1` as scientific enrollment. Its adaptation is a separate parent-owned task; until it exists, raw completion is not a formally analyzed passed pilot. Retained old attempts keep their original analyzer/commit receipts.

## CPU verification

Twenty existing and new CPU tests pass in1.650s with CUDA hidden. New tests verify strict deterministic configuration without CUDA initialization, reject conflicting/late settings, compare exact fresh gradient/state arrays, reject equal-norm but different gradients, changed Adam/environment/source/trajectory and missing/nonfinite evidence, and rehash receipt inputs rather than trusting a success flag. Scientific score/cap/optimizer tests continue to pass. These are implementation checks; the actual two-process GPU prefix is still unrun at this document's completion.

# Bounded reconstruction diagnosis after the M1 step-200 endpoints

Version `m1-reconstruction-diagnosis-v1`, 2026-10-03. Development implementation of the parent-adopted diagnosis in [the family-A design](m1-dual-latent-design.md). No watermark, CLIP code, attack or new model is involved. No GPU run has been performed by this implementation's author. The purpose is to test whether a finite reconstruction endpoint materially improves with additional lower-rate optimization; no outcome certifies the global decoder manifold floor or exhausts latent watermark designs.

## Selection is fixed before the diagnostic outcomes

The input manifest is [m1-reconstruction-diagnosis-dev.json](m1-reconstruction-diagnosis-dev.json). It names the original interrupted reconstruction directory and its separate recovery directory. The original retained artifacts are never modified. A run whose overall outcome still says `started` may contribute a case already marked `completed`, with intact step-200 PNG and latent hashes. Incomplete source cases are inventoried but ignored as candidate endpoints.

Exactly one completed step-200 endpoint is required for **each of the 12 reserved development IDs** in `research/m1-reconstruction-dev.json`. Every input must identify the same pinned original reconstruction configuration, development split and unscaled latent units. Missing cases stop preflight. Two completed records for an ID stop preflight even if one scores better; resolve the intended input provenance explicitly instead of choosing a favorable retry. An input run's repeated ID, different raw source hash, absent endpoint hash, invalid PSNR or unauthorized ID also stops preflight.

Use saved RGB8 PSNR at step 200 to select:

1. The largest-PSNR source, with ties broken by the smallest numeric ID (`best`).
2. The smallest-PSNR source, with ties broken by the smallest numeric ID (`worst`).

Execute best then worst. If both roles resolve to one image, execute it once and retain both roles. An infinite PSNR must be represented explicitly as null `psnr_db`, true `psnr_infinite` and zero MSE; it ranks above finite values without emitting nonstandard JSON Infinity. NaN and malformed scores are invalid. This is **adaptive extremum selection on development evidence**, not random sampling, new independent evidence or a replacement for the original 12-image inventory.

The complete 12-source selection inventory, ignored incomplete records and selected roles are copied into the new run. Exact raw source `run.json` bytes are preserved in `input-snapshots/`, with hashes. Selection uses each JSON snapshot read once; later completion-status edits in the source run cannot rewrite what was selected. Before execution, all 24 step-200 PNG/latent artifacts are hash-verified, including unselected cases. This verifies the selection evidence without decoding unselected source images.

## Fixed scientific schedule

Load each selected source's step-200 latent, verifying SHA-256, shape `1x4x64x64`, finite float32 values, step and units. Reject other tensor types/precisions instead of silently casting the scientific start. Recreate the canonical RGB8 source with the same EXIF orientation, optional ICC-to-sRGB conversion and bicubic 512x512 resize as the original diagnostic. Its canonical pixel hash must match the source receipt. Keep the pinned SD1.5 VAE frozen in float32, and optimize only its **unscaled** latent `z`.

Start a **new Adam optimizer** at the step-200 latent: lr .005, betas (.9,.999), epsilon 1e-8. No original Adam moments are imported. Run exactly 400 further updates. The labels 300/400/600 count the original 200 updates plus this new optimization; they do not imply uninterrupted Adam state from update zero. The optimizer rule, image resolution, model and source objective otherwise stay fixed.

The decoder objective is the original **unclamped** RGB MSE:

`mean((((VAE.decode(z)+1)/2) - source_RGB01)^2)`.

Clipping inside this objective would change the experiment by hiding saturated decoder errors; the code does not do so. Saved-image measurement clamps decoder RGB to [0,1], rounds to RGB8 using the existing NumPy policy, writes PNG and reopens it. Evaluate at total steps **200, 300, 400 and 600**, including a new baseline measurement before the first diagnostic update. Save each measured latent and image. Re-decoding the starting latent must reproduce the previous step-200 PNG pixels exactly; compressed PNG bytes are recorded separately and may differ between writers. Any pixel discrepancy is retained as a failure to resolve before interpreting optimization results.

The final step 600 is the reported endpoint. Intermediate improvement does not authorize selecting an earlier best checkpoint. Measure PSNR, Gaussian-window RGB SSIM and pinned AlexNet LPIPS relative to the canonical source. Quality admissibility is the conjunction PSNR >35 dB, SSIM >.9 and LPIPS <.1. LPIPS load/verification failures abort the new run rather than silently treating missing quality as passing. Source-only VAE reconstruction has no human safety or visual-quality verdict attached.

Use batch one, seed 0, TF32 off, decoder activation checkpointing and the existing verified local VAE assets. GPU allocation cap is 10 GiB and total run wall-time cap is 3600 seconds. The two images run sequentially. There are no downloads, remote services or paid calls; the process blocks network before model loading. The parent schedules this after other GPU work.

## Output and recovery

`scripts/m1_reconstruction_diagnosis.py` requires a new output directory under the authoritative `.thesis-build/dev-runs` root. Existing directories are refused. All declared scientific scripts, manifest, cohort and asset lock must match HEAD before a run, with Git CRLF clean-filter handling and actual working SHA-256 receipts. The implementation writes only its new run; it never repairs or updates the source runs.

An initial run.json is written before inventory/hash/commit preflight. A preflight or setup failure returns a nonzero exit and retains its failure phase, manifest hash, error, traceback and duration in that new directory, with a journal receipt. Missing source inputs do not silently disappear. Existing output directories are still refused before any write. Source reconstruction receipts must identify an exact Git commit; malformed infinity flags or nonfinite/invalid MSE receipts are rejected before extrema selection.

The root `run.json` records the source inventories/snapshots, selection roles, commit, command, full config/hash, model receipts, environment, seeds, duration and outcome. `cases[]` retains each selected image's source/init receipts, all fixed checkpoints, recovery snapshots, final optimizer statistics, peak memory and comparison. The checkpoint records include image and latent paths/hashes, unclamped float loss, source-relative PSNR/SSIM/LPIPS and the quality conjunction. `journal.jsonl` records every update's **pre-update** loss, gradient norm, cumulative update number, elapsed time, measurement events and recovery snapshot receipts.

Every ten additional updates, write a separate atomic `restart` snapshot containing latent, full Adam state, CPU/CUDA Torch RNG state, source hash, initial latent hash, config hash, units and update counters. These snapshots preserve the state needed for a later explicit continuation. This version intentionally has no implicit same-directory resume or favorable-checkpoint loader. Any later continuation must use a new run directory and verify/hash its chosen snapshot; the existing run is retained. Completed-image recovery is immediately available using a new committed manifest with `case_roles=["best"]` or `["worst"]`, keeping the same 12-source selection inventory and reporting the prior missing/failed attempt. A restarted role uses the original step-200 start and reset Adam unless a separate, documented snapshot-continuation implementation is adopted.

Nonfinite values, bad assets, changed inputs, CUDA absence, memory cap and wall-time cap are failures. A Python-handled Ctrl-C is recorded as `interrupted`; remaining selected images become `not_attempted_after_stop`. Hard process termination may prevent finalization, so the journal and atomic snapshots support an external interruption receipt. A failure never becomes a reconstruction-quality conclusion.

## Descriptive decision and limits

Report step-200 to step-600 PSNR gain, step-400 to step-600 gain, all quality metrics and the final conjunction for both selected roles. The predeclared **slow-improvement flag** is late PSNR gain <.25 dB. The JSON field is called `plateau` but is strictly this finite-interval rule. A negative gain also satisfies it and should be described as deterioration. Infinite/nonfinite gain differences are null and produce no flag. A flagged result is relevant to the proposed quality ceiling only when the final quality conjunction still fails.

An improving endpoint supports the explanation that the earlier optimizer budget was insufficient. A slow or poor endpoint supports de-prioritizing these precise model/optimizer/budget settings. Neither result proves a best possible decoder reconstruction, performance on held-out data or watermark robustness. Both selected images belong to the already observed development cohort, so their adaptive gains do not estimate population reconstruction accuracy. The original 12-case results remain the complete denominator.

A separately versioned L-BFGS experiment may follow if the parent finds it useful; it is not implemented or executed by this file. Changing the VAE, objective, latent units, image size or adding a source bypass is a different amendment and must not be concealed as further fitting of this arm.

## Commands and validation

Metadata-only readiness/selection preview (works with the stdlib interpreter; no images, tensors, model imports or GPU):

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_reconstruction_diagnosis.py --manifest research/m1-reconstruction-diagnosis-dev.json --preview
```

The preview returns status 2 with an explicit missing/duplicate inventory when source reconstruction is incomplete. It does not write an output directory or wait on the GPU. Commit the implementation/config before the parent starts a scientific run:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/m1_reconstruction_diagnosis.py --manifest research/m1-reconstruction-diagnosis-dev.json --output-dir 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/NEW-RECONSTRUCTION-DIAGNOSIS'
```

The test module uses synthetic metadata, temporary mock artifacts and a CPU mock VAE. It covers complete-inventory enforcement, deterministic extrema/ties, duplicate/incomplete source-run handling, explicit infinity, development/config guards, artifact and latent-unit verification, unclamped loss, frozen model weights, fixed measurement/final selection and saved Adam-state counters. It never opens real development images or loads actual model weights. Passing these tests establishes implementation behavior; GPU/runtime and reconstruction evidence remain unmeasured until the parent's run.

Validation on 2026-10-03: all nine CPU tests passed in .724 seconds using the pinned science interpreter with `CUDA_VISIBLE_DEVICES=-1`; stdlib CLI help and syntax checks passed. One metadata-only preview correctly refused the still-incomplete twelve-case inventory. No new scientific run or commit was performed by this author.

Routine implementation check added three CPU fixtures for malformed score/commit receipts, rejected latent dtype coercions and retained preflight failure receipts. All twelve tests pass with CUDA hidden. This check found no source bypass or change to fixed endpoint selection, objective, optimizer reset, final-step reporting or configuration. It is not the independent milestone review. No real source image, scientific score or model was evaluated by these added fixtures.

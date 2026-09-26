# C4 existing-image embedding component: implementation checkpoint

2026-09-26, author `/root`, issue #18. **Partial C4 implementation; not task closure, a scientific run, final configuration or method acceptance.** Applies [method-spec.md](method-spec.md), [initial-noise-path.md](initial-noise-path.md), [research-contract.md](research-contract.md), [scope-guard.md](scope-guard.md) and [approval-policy.md](approval-policy.md). C3b/#17 is actually closed and PR #66 merged at `19c704a10d9d88f5d249eea0a57f98d0df00c19b`; A5/#6 and B4/#11 are closed prerequisites. Old B3 download heartbeat text is not the current task state.

## Concrete implemented path

`src/embedding/proposed.py` is a component kernel, not a public pipeline call. `DiffusersComponents` uses installed Diffusers 0.35.1 `DDIMScheduler.add_noise/step`, an explicit suffix, one conditional UNet call per time, scaled VAE posterior **mode**, and a differentiable decoder divided by the same checked scale. Models are eval/frozen float32; only initial-noise `u` has an optimizer. No CFG, replacement-image/prompt generation, intermediate detach, hidden resize, inference-mode pipeline, autocast, offload or checkpointing is introduced. The constructor takes already-loaded components and a fixed condition; it cannot authenticate their bytes or prove that the supplied embeddings came from the empty tokenizer. That remains a fail-closed loader/manifest responsibility before real execution.

For each native source `[1,3,H,W]`, edge pad bottom/right to 64; VAE latent `[1,4,Hpad/8,Wpad/8]`; all-one masks; existing A6 SHAKE byte/numeric reference supplies base Gaussian noise and the two domain-separated unit-norm carriers. This reuses `scripts/base_noise_reference.py`; its one-million-element cap is retained, not silently lifted. A configured maximum dimension therefore does not itself establish every native resolution's eligibility or resource fit. Source digest belongs only to enrollment/noise provenance, not detection.

Continuous objective uses native cropped luminance blocks edge-padded to 8, float64 orthonormal DCT and per-frequency centering, with the fixed A5 frequency lists and SHAKE templates. Shape/range/nonfinite guards, zero-variance diagnostics, four explicit loss terms, Adam (.9/.999, eps 1e-8, bias correction), finite-gradient checks, L2 projection, fixed iteration cap and post-last-update evaluation are implemented. The scalar DDIM reference and DCT oracle are independent arithmetic checks, not evidence about learned model quality. Model computations remain float32; no universal cross-runtime bit equality is asserted.

Matching C0 uses **both carrier gains zero and u=0**, even if settings specify nonzero marked gains. Diffusion scheduler `strength` remains strictly positive per A5; the plan's zero-mark-strength control is not a fabricated zero-length diffusion suffix. The reference uses exactly the same encoded latent, base noise, schedule, decoder and native crop. Loss/gradient trajectories distinguish pre-update loss from post-projection norm and include final objective. A caller-supplied journal callback is never ignored on failure; a future worker must write case-start/failure records before entering this kernel so errors and interruptions remain visible.

## Ordinary test evidence, not scientific results

`tests/test_embedding.py` uses analytically constructed owned 37x43 pixel tensors and tiny author-defined VAE/UNet arithmetic modules on **CPU only**. No model checkpoint, source study image, CLIP inference, CUDA execution, new download, package installation, dataset mutation or scientific runner invocation occurs. Tests cover padding/crop, streams/domain/shape/norms, DCT edge blocks versus a float64 scalar oracle, centered-score finite differences and zero variance, installed DDIM versus eta-zero equations, input gradients and frozen module parameters, one-pass/no-CFG calls, matched C0 identity, deterministic repeat, perturbation projection, final iteration, detached/nonfinite/wrong-shape failures, settings mismatch and failed journal writes.

Commands (existing environments; no installation):

```text
wsl -d Ubuntu --cd /mnt/c/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5 -- /home/soroush/.cache/thesis-a6-science-clean-py314/bin/python -m unittest tests.test_embedding -v
W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe -m unittest tests.test_embedding tests.test_instance tests.test_owner tests.test_runtime -v
```

The immutable plan names pytest; neither existing environment has pytest. Standard-library unittest is an explicitly recorded command substitution, **not a claim that pytest was run**. Initial ten WSL tests passed; the initial Windows combined 35 tests had 26 pass / 9 expected skips (eight tensor tests lack Torch in that small Windows interpreter, one symlink permission skip). Final counts and actual independent review are recorded in the review audit after changes, not inferred here. A diagnostic source-read attempt found `rg` unavailable inside Ubuntu; native shell `sed` was used. An earlier plan-print diagnostic hit Windows cp1252 encoding, repaired only by `-X utf8`; neither was a model/experiment failure or basis for altered evidence.

## CLI and remaining C4 evidence

`scripts/embed.py --config ... --preview` reuses C1 full A5 schema/cross-field validation over exact configuration bytes, then validates component settings, emits configuration hash and explicitly says no compute is authorized. Tests use a temporary **synthetic configuration specimen**, not a real selected scientific config or valid artifact provenance. Invalid config returns 2. Calling without `--preview` returns 4 (`execution_adapter_not_ready`) and loads no model; there is deliberately no direct CLI route around the runner. Passing this preview is not the successful development-image CLI required for C4 closure.

`reports/dev/embedding-manifest.csv` currently has **header only, zero executions**. No output image/path/hash, Control/Watermarked pair, quality metric or final detector score has been invented. A `ContinuousCandidate` is explicitly pending safety, saved-PNG roundtrip, quality and blind verification; continuous target-template scores never count as a detector result.

Still required before #18 acceptance:

- reviewed hash-bound local component/tokenizer/safety loader, source C2/C3b extraction and output persistence using B5 without modifying the original;
- a concrete preregistered development config/exact-manifest runner worker, approval and measured actual input-conditioned UNet/decoder gradient, runtime and VRAM fit; current float32 path is not a feasibility claim;
- actual matched control/marked RGB8 PNGs with source/seed/config/output hashes and preserved failure ledger;
- final saved-PNG q/h code drift, full blind bounded-candidate verification (C5 dependency), and aligned PSNR/SSIM/LPIPS for source and control, with actual safety-check result;
- independent evidence review of the exact resulting artifacts. No calibration threshold/version or optimization value is selected from these toy outcomes.

The original one-shot C2 execution authorization is consumed. No new scientific approval is requested at this checkpoint because the real loader/output/worker package is not yet ready. Official controller read still reports `d916749c` paused at plan-acceptance, null choice, workflow SHA-256 `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`. No lifecycle state write or human verdict was fabricated.

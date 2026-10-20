# Runtime and optional alternatives: Stage1b superseding audit

This replaces the preliminary Stage1 recommendation. Core pins are now frozen, not proposed: Linux/Python3.11, torch2.7.1+cu128, torchvision0.22.1, diffusers0.35.1. The authoritative file for all package pins is `research/encoder-transfer-20261019/frozen-config.json`. No v0.36/current source is used to establish frozen execution semantics. Six `*-implementation-v2.md` cards give the official pinned source paths and lines.

## Actual runtime trace

| Behavior | Local file and lines inspected |
|---|---|
| FP32/full VAE and finite guards | `scripts/encoder_transfer_runtime.py:78–99,265–278` |
| External Lanczos and saved RGB contract | `scripts/encoder_transfer_runtime.py:101–116,419–432` |
| SD1.5 required safety components and explicit DDIM | `scripts/three_threat_models.py:94–112` |
| SDXL base and full VAE upcast override | `scripts/encoder_transfer_runtime.py:265–278` |
| D1 direct unscaled mode, fp32 | `scripts/encoder_transfer_runtime.py:280–294` |
| Fresh per-call CUDA generator and microconditioning | `scripts/encoder_transfer_runtime.py:296–314` |
| WAM native load/strict safe state dict | `scripts/journal_wam_probe.py:40–83` |
| WAM release-specific quantization and native presence | `scripts/encoder_transfer_runtime.py:183–207` |
| VINE native fp32 residual/decode | `scripts/encoder_transfer_runtime.py:210–252` |
| Incidental global RNGs | `scripts/encoder_transfer_runtime.py:323–330,373,419` |
| Rinse saved512 intermediate and offset seeds | `scripts/encoder_transfer_runtime.py:412–432` |
| Deterministic controls and runtime version capture | `scripts/encoder_transfer_runtime.py:563–577` |

Exact inspected local snapshots and SHA-256 are in the source manifest/cache. The floor matrix carries this trace per implementation. Kandinsky3 and TrustMark have no local runtime branch: they remain proposals, so absence is labelled rather than replaced by an invented implementation reference.

## Determinism and memory boundaries

Official PyTorch2.7.1 `docs/source/notes/randomness.rst:5–19,29–44,71–140` distinguishes seeded random draws, deterministic algorithms and cross-platform reproducibility. Runtime sets CUBLAS workspace before CUDA initialization, disables TF32 and cudnn benchmarking, requests deterministic algorithms, seeds global generators, and creates a per-regeneration CUDA generator. It does not separately set `cudnn.deterministic`; the broader deterministic-algorithm flag supplies the documented guarantee where available. It does not freeze a specific SDPA kernel. Record effective hardware/backend and failures; do not claim cross-device bit identity or silently switch to warn-only.

Official diffusers0.35.1 `pipeline_utils.py:1154–1239,1270–1336` implements model/sequential CPU offload. Neither is called by this runtime. The current policy is serial one-image models with explicit missingness on failure; previous wording suggesting an automatic offload fallback was only a preliminary suggestion and is superseded. GPU memory and elapsed time are unmeasured. Full fp32 SDXL VAE at1024 matters; disk bytes do not prove VRAM sufficiency. Tiling, precision reduction or alternative AE weights would alter scientific outputs and need a pre-outcome amendment.

Version compatibility remains unverified by this documentary phase: native constructors, safe checkpoint loading, nested offline VINE dependency paths, CUDA determinism and full-VAE guards need authorized Stage2 synthetic smoke. PyTorch2.7.1 `torch/serialization.py:88–91,1427–1431` defaults to the restricted weights loader in the ordinary case. TrustMark's source uses `torch.load` without an explicit argument; this is a compatibility item, not permission to turn safe loading off. WAM already explicitly uses `weights_only=True` and strict tensor-state validation.

## Alternatives and budget

Kandinsky3 and TrustMark are fully audited proposals, not appended core arms. FLUX.1-schnell remains gated/excluded; neither a newer FLUX variant nor KD3 automatically replaces it. T2 is authoritative for alternative asset accounting and the rejected non-strength Klein interface. Core remains n60dev with F5r2/v5r3/WAM32/VINE-R100+C0, R0/R1/D1/X1/X2/rinse.

Current work downloads only documentary text under the existing30GB research cap. The separate future Stage2 allowance is80GB and total experiment budget15hours/$15. No weight/package/server/GPU operation occurred here. The rented server is to be stopped, never destroyed, after results come home. This audit does not start paid execution.

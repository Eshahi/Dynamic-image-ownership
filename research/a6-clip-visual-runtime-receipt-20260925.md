# A6 image-only CLIP compatibility receipt

Status 2026-09-25: **the pinned CLIP ViT-B/32 visual encoder loaded and returned finite 512-dimensional CPU/CUDA features for one fixed synthetic image. Full official package import, tokenizer availability, method parity and scientific acceptance remain open.** Issue #7 / draft PR #58 stays open.

The user asked us to investigate CLIP access after affirming the bounded local synthetic model-load preflight. Windows Code Integrity had blocked the unsigned native `regex` module when the official `clip` package initializer imported its text tokenizer, before the earlier visual check could start; see [the prior failure receipt](a6-metric-runtime-receipt-20260925.md). Read-only host checks found `VerifiedAndReputablePolicyState=1` and `CiTool --list-policies --json` returned access denied. No code-integrity policy, Smart App Control setting, registry value, native module, trust rule or system permission was changed.

The official method needs image encoding, not CLIP text tokenization. Commit `81f35fc2080d8afaa51679ae7adda6c2ca37a897` makes `scripts/check_a6_metric_parity.py` load the **same installed official `clip/model.py` visual builder** as a verified source file, without importing the unused package initializer. It checks the exact installed `clip/model.py` SHA-256 `dc4981bbd17867430890cfe711bb813466232f3b19c5753e26de0b7b047b0926` and `clip/clip.py` SHA-256 `3891eee0ad659a781ec3fd0240f9d69b7f3845837f671ff6670accf0d4bad0a2` before source execution, then applies the official `_transform` operations/constants recorded in the latter. The earlier [installed-source audit](a6-clip-install-byte-audit-20260924.md) matched these files against the locally cached source wheel and pinned VCS-origin metadata. The checkpoint remains the separately verified official JIT archive in the 17-file candidate lock; the loader rejects arbitrary pickle fallback. This is an image-only compatibility path, **not** a claim that the blocked tokenizer or full `clip` package works. It did not execute the blocked native binary or weaken host protections.

One bounded offline `--load-metrics --metric clip` invocation used the already verified local 17-file asset inventory and four LPIPS package files, fixed synthetic RGB8 224×224 pixels, the predeclared launch-time deterministic settings, network-disabled process and an external 1,200-second timeout. It exited 0 after about six seconds wall-clock (1.625 seconds measured inside the metric section), with empty stderr. The ignored stdout SHA-256 is `74a4112ce6a75dde30afc30f5b02df56465002bcad9dc406d543c679b7e11ce1`; empty stderr SHA-256 is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

| Observation | Value |
| --- | --- |
| Asset-lock SHA-256 | `b8c2595857853ea5b7835bb71f12a34dde07b78623c5e638f692dc7eb220b27e` |
| Preprocessed float32 tensor SHA-256 | `9465569501fdd08c5fc6d057f0263763eb703ad0547cda10c049e109401f2db3` |
| CPU feature float32 SHA-256 | `739ffb20e62d7ae75289b6609c0cfbbb863fc1903b583443796876492e500842` |
| CUDA feature float32 SHA-256 | `c823765d2bcfe8590c010ec32b4c4b8ea89ec6bf5a6c3105271e1d1602117730` |
| Normalized CPU/CUDA maximum absolute component difference | `1.8790364265441895e-05` |
| Reported cosine similarity | `1.000000238418579` (float32 rounding above 1; not a literal correlation above 1) |
| Peak Torch CUDA allocation | `644345344` bytes |

The image-only path requires independent exact-code review and a nontrivial numerical acceptance criterion. One synthetic image does not prove library parity across images, canonical color handling, a full image-conditioned gradient, RTX memory fit, remote reproduction, dataset rights, or scientific results. Text APIs remain blocked on this host. The full official package may need a sanctioned signed dependency or administrative policy route **only if a later reviewed task truly requires its tokenizer**; disabling Smart App Control or evading a code-integrity policy is not an approved remedy. No dataset acquisition, diffusion inference, method experiment, paid compute, Spec Kit transition or A6 closure occurred.

The model-free repository suite discovered 83 tests: 81 passed and two expected skips; `git diff --check` passed. A new negative test confirms changed installed visual-source bytes fail before source execution.

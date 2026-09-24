# B2 bounded search for an executable existing-image inversion comparator

2026-09-24 UTC; [issue #9](https://github.com/Eshahi/Dynamic-image-ownership/issues/9).
Status: **targeted public-source preflight, not comparator substitution, code
acquisition, license clearance or scientific reproduction**. The relevant
contract is HYP-03/METRIC-07: compare the *full* inversion-based detector to
the proposed inversion-free verifier on the same existing-image source IDs,
quality/attack profile and declared access. See `baseline-selection.md`,
`research-contract.md`, `scope-guard.md` and the separate neural-decoder role.
No package, weight, dataset or upstream source tree was downloaded or run; only
public text/API responses were inspected. URL/commit observations are bounded
to the revisions below and do not imply terms for third-party dependencies.

| Candidate | Pinned evidence inspected | Exact I/O and rights observation | Decision for the required role |
| --- | --- | --- | --- |
| [Shallow Diffuse](https://github.com/liwd190019/Shallow-Diffuse/tree/c80c553fdf66fda8db735d77a9d56538b7a0ade8) | Official README and [`run_shallow_diffuse_i2i.py`](https://github.com/liwd190019/Shallow-Diffuse/blob/c80c553fdf66fda8db735d77a9d56538b7a0ade8/run_shallow_diffuse_i2i.py), pinned tree `c80c553fdf66fda8db735d77a9d56538b7a0ade8`. Inspected HTTP UTF-8 script response: 9,677 bytes, SHA-256 `12614b27936ac677b52b224b7651e7e6b9bb4a107d9bc48c1314a6c6a6d1d90b`. | The i2i script opens a caller-provided source image, VAE-encodes/inverts it, injects a latent-frequency watermark, regenerates and later inverts the marked image for detection. Thus it is a **closer route match** than a generated-only method. GitHub repository license metadata was null and the inspected recursive tree had no root/nested LICENSE or COPYING file. Its README names PyTorch 1.13, Transformers 4.23.1 and Diffusers 0.11.1, not this project's Stage-1 Torch 2.12.1 lock. No exact model/weight receipt or paper-to-code parity was established. | `PAPER/CODE_ROUTE_RELEVANT; BLOCKED_CODE_RIGHTS_AND_ENVIRONMENT`. Do not copy/execute as a licensed comparator merely because it is public. This is a read-only code observation, not legal advice or a claim that all research use is forbidden. |
| [FARI](https://github.com/0xD009/FARI/tree/c08064222366842bf962998506c4815b0a2cbe63) | Official README, MIT LICENSE metadata and [`val_tr.py`](https://github.com/0xD009/FARI/blob/c08064222366842bf962998506c4815b0a2cbe63/val_tr.py), pinned tree `c08064222366842bf962998506c4815b0a2cbe63`. Inspected HTTP UTF-8 script response: 7,520 bytes, SHA-256 `964695078e0221e3682682eaa73b1b508f5c3162b8ffb4a61bf9f997fa92d9b7`. Tree lists `results/fari_default/fari_weights.pth` as a 10,299,221-byte blob; no model bytes or SHA-256 were acquired. | FARI is a one-step **inversion/verification** accelerator with released LoRA weights, but the pinned Tree-Ring validation script selects prompts from a dataset, generates an unmarked image and a marked image from the pipeline, then inverts them. Its published evaluation command is not an existing-image embedding route. Model/checkpoint, underlying SD 2.1 and upstream Tree-Ring rights/parity remain separately unverified. | `LICENSED_CODE / GENERATED_ONLY_REFERENCE`. Potential limited timing sensitivity, **not** a direct HYP-03 existing-image comparator. Adapting its inverter to an existing-image embedder would be a new method combination and cannot be called official FARI reproduction. |
| [MarkDiffusion SEAL adapter](https://github.com/THU-BPM/MarkDiffusion/tree/9d81656d1a5f9e5194fc2f727bb795ef29e53809) | Official Apache-2.0 toolkit at tree `9d81656d1a5f9e5194fc2f727bb795ef29e53809`; [`seal.py`](https://github.com/THU-BPM/MarkDiffusion/blob/9d81656d1a5f9e5194fc2f727bb795ef29e53809/markdiffusion/watermark/seal/seal.py) HTTP UTF-8 response 15,717 bytes/SHA-256 `394e34f4ff7d6d223464797b53979d4144aba07d262f20319042b7e8728f6070`; [`seal_detection.py`](https://github.com/THU-BPM/MarkDiffusion/blob/9d81656d1a5f9e5194fc2f727bb795ef29e53809/markdiffusion/detection/seal/seal_detection.py) 3,983 bytes/SHA-256 `5158423afc2cd27d7158a4b84eff193fd4442a350ee55160c2a0e64df78743cb`; pinned `pyproject.toml`. | Its encoder first calls `pipe(prompt, ...)` to **generate** an image and later calls the pipeline again with caption-derived noise. Detection inverts an image and compares patches, but the shown encoder does not accept an existing source image to sign. Constructor loads BLIP-2 and sentence-transformer models via `from_pretrained` (implicit downloads). Toolkit pins Torch `<2.11` and TorchVision `<0.26`, conflicting with A6's installed Stage-1 pair, so a separate reviewed environment would be needed even for a valid route. The Apache header covers these toolkit files; it does not establish rights/parity of the SEAL paper's original source, pretrained models or downstream artifacts. | `LICENSED_TOOLKIT / GENERATED_ONLY_SEAL_ADAPTER`; not a drop-in existing-image replacement for the provisional ZoDiac role. Do not conflate this implementation with the original SEAL repository or claim that toolkit availability resolves the model/weight rights gap. |

**Disposition before test outcomes:** keep ZoDiac as the provisional closest
existing-image inversion candidate and SEAL as semantic related work; their
previously recorded code/weight rights and parity blockers remain. Shallow
Diffuse provides a *new relevant existing-image prior-work lead* but no
inspectable code permission at this revision. FARI and MarkDiffusion show that
an open license or packaged inverter alone does not satisfy the input route.
None is promoted to `RUN_READY`, and no absent comparator is silently removed
from HYP-03/METRIC-07. Before any substitution, inspect a candidate's exact
embedding/detection I/O, code and weight terms, model hashes, common score,
quality and timing profile, and freeze it **before** held-out outcomes. If the
direct comparison stays unavailable, report `BLOCKED_COMPARATOR` and seek a
claim-level decision rather than asserting speed/quality superiority.

This was a bounded search of three plausible public codebases, not a
comprehensive literature or repository census. GitHub license detection and
absence of a license file are observations, not legal conclusions. No
performance numbers, independent source-image results, or test-set data were
used to rank candidates. The official Spec Kit gate and compute authorization
are unchanged.

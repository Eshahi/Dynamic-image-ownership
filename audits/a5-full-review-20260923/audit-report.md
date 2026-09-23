# Independent A5 architecture review

Review time: 2026-09-23 10:13 UTC. Reviewer: `/root/a5_full_review`. Author: `/root`. Scope: source task `repair-4`, reduced task A5 / issue #6, documentary architecture only. This is an independent read-focused review, not an experiment, implementation acceptance, or a Spec Kit gate decision.

## Verdict

**Accept A5 as a documentary architecture and configuration contract, with no blocking findings for that limited task.** The existing-image embedding and blind verification algorithms can be followed from canonical RGB input to two DCT scores. The feature, signature, latent, output and block shapes are compatible after the author's correction that `I_pad` is used only for the model while `I`, cropped `I_float`, and cropped `I_ref` share `[3,H,W]`. The key-derived image template is constructed from only the suspect dimensions, candidate codes, public OwnerID and frozen detector configuration. The latent-to-image-DCT link is an explicit differentiable objective and a falsifiable candidate, not an established transfer result.

This verdict permits closing the A5 **document** task after integration and ordinary checks. It does not accept `plan-acceptance`, authorize scientific compute, certify weight provenance, establish empirical feasibility, or support any ownership/security/quality hypothesis. No final config, model weights, dataset, run ID, result table or scientific analysis was supplied; those are correctly absent from this review.

## Examined artifact identities

| Artifact | SHA-256 |
| --- | --- |
| `research/method-spec.md` | `fd22aba99b2643ff33b088e65077ba08562cc97b0779e051ca37314b20588ce9` |
| `configs/method.schema.json` | `7df9e064b3b6321bbd3cccc3dd950a6154e5a6401bfba89fbbd90e00b06ab5e0` |
| `scripts/validate_method_config.py` | `890b40caebc6f294d8f57b7e86629086a6602d37bc88c7125c3f1570adaf8b64` |
| `scripts/test_validate_method_config.py` | `13354a0565ca6eec17aa55865a7de2de2487d39c432b5e3243ab3a0fefb2bf6a` |
| `research/initial-noise-path.md` | `d57b9c76b50facdcc86d8a3ffcd0fd7d7122ddb0a23241ed8f5369fda7933251` |
| `research/bridge-design-options.md` | `91d647f76121f4b8b2fe8054a8f6689794d75b22a94aefc608cbfd55452855` |
| `research/io-spec.md` | `9c257f7bd5101c51f7bdd15859ca21b969be9c3e3028df4b93c3746abd4eb27a` |
| `research/scope-guard.md` | `c8c6af9d5349cd9a194d7594fe84c02679e79592f581d14392447cd4b6fea833` |
| `research/research-contract.md` | `4ff8f58a808d5b50a7f1ce4ab90dba6416930d25be6715b0a261bf7790b28679` |

The original proposal extraction, Table 8, was read for the dual signatures, initial-noise embedding and image-block DCT detector. The unconverted Office Math equations in that extraction were not treated as transcribed formulas; the design equations here are author-selected and subject to empirical testing. The immutable A5 source task in `thesis-runs/d916749c/guide-plan-38.json` requires separate algorithms, shapes, stable-key handling, a testable bridge, and a strict config schema. The method applies the research contract and scope guard explicitly. Earlier source preflight reports pin Diffusers code and a model-mirror revision, but this review did not reacquire weights or assert original-release equivalence.

## Technical assessment

- The CLIP 512-vector, 12-bit projection code, 32-bit DCT pHash, byte packing, domain-separated SHA-256 `Ws`/`Wi`, and Hamming-one candidate search are explicit. Whole-code hash avalanche is acknowledged. The maximum single-owner candidate counts are 13 semantic and 429 instance signatures; measured drift and any-of-candidates false attribution remain required.
- The image detector specifies sRGB luminance, right/bottom replication, 8×8 orthonormal DCT, disjoint mid-band positions, keyed Rademacher templates, centered cosine score, zero-variance failure, and a common-q rule for `both_match`. Detector inputs exclude source image, original signatures, seed and diffusion model; CLIP remains part of full verification cost.
- The embedding route keeps the original image grid, uses a padded VAE/UNet working grid, adds two carriers and projected `u` to the initial noise of an image-conditioned DDIM suffix, and optimizes continuous image-domain DCT scores through that suffix. Empty-string conditioning with guidance scale 1 and RGB8 PNG post-encoding verification are fixed. C0 sets both carrier strengths and `u` to zero. The objective's quality terms compare same-grid images.
- The 2020-12 schema requires all core objects, image I/O, model pins, scheduler, optimizer, calibration fields and thresholds. The companion validator checks its own static detector ID, nonempty valid schedule, nonzero combined carriers, finite parsed JSON, placeholders and zero-digest sentinels. This establishes a structural contract only; a plausible digest string does not verify actual bytes.
- `semantic_only`, `instance_only` and `neither_match` remain observed states, not causal regeneration/transfer diagnoses. Public OwnerID is not authenticated ownership. The prompt-only signing branch and transfer protocol remain outside the executable profile under the current scope guard.

## Reproduction and preserved limits

The verified Windows Python ran eight `test_validate_method_config.py` tests and six `test_noise_path_reference.py` tests successfully. These tests use synthetic/scalar values, load no model or dataset, and do not establish image quality, gradient continuity, GPU memory fit, signature stability, robustness, thresholds or security. `scripts/audit_evidence.py --help` could not run because that helper is not installed at the repository path; this manually reviewed documentary audit uses the prescribed five-file audit shape without claiming automated evidence-helper validation.

`THESIS_GUIDE_OFFLINE.html` was already modified in the working tree and was not edited by this reviewer. Its observed SHA-256 remained `fdba83a7d1aec198a0e7654fb3ce04f26b101292005f614e784e919f7d8e460e`.

See `findings.json` for non-blocking issues, `claim-matrix.csv` for claim classifications, `reproducibility-checklist.md` for checked and pending items, and `unresolved-items.md` for downstream work. If any of the four reviewed A5 files changes, this verdict must be rebound to new hashes before it is used for issue closure.

# DCT-QIM RGB development pilot: retained results

## Outcome

The supplied v2 DCT-QIM profile passed the narrow native saved-PNG engineering criterion on all ten previously reserved COCO development sources. It did **not** demonstrate broad attack robustness: JPEG quality 80 and a one-pixel horizontal shift each destroyed accepted detection on all ten marked images. No parameter was changed after observing results and no retry was performed.

| Frozen condition | Intended owner detected / planned | Unmarked positives / planned |
| --- | ---: | ---: |
| Native saved RGB8 PNG | 10/10 | 0/10 |
| Gaussian RGB noise, sigma 1 byte | 10/10 | 0/10 |
| Bicubic 0.75 resize then native-size restoration | 9/10 | 0/10 |
| JPEG quality 80, subsampling 2 | 0/10 | 0/10 |
| One-pixel left shift, repeated final column | 0/10 | 0/10 |

All 10 sources completed; all 130 planned detection calls are retained, with no missing calls. Three fixed wrong public OwnerIDs on each native marked image produced 0/30 positive detections. This is not a calibrated population false-positive rate or cryptographic ownership proof. Independent component review had already exhibited a selected different wrong OwnerID accepted by the supplied approximate owner threshold; that negative evidence remains valid.

Native RGB quality: PSNR mean **50.346377 dB**, range **50.080506–50.537584 dB**; SSIM mean **0.996239**, range **0.993550–0.997872**. Every marked image changed nonzero RGB channels. The reference is the canonical decoded source RGB8, not raw JPEG bytes. Detection uses reopened saved PNG luminance, not the floating embedding output.

The sole resized marked-image failure was source 499768: decoded owner accuracy 1.0, CRC true, binding distance 0, but confidence 0.626505 below the frozen 0.65 threshold. The threshold was not lowered. JPEG and shift failures retain their full decoded diagnostics in results.json.

## Scope and limitations

This is an exploratory, nonrandom development census, one batch run, not ten independent seeds or a confirmatory evaluation. The batch analysis record faithfully transcribes native_joint_pass_fraction = 10/10 = 1.0; no confidence interval, significance or superiority claim is made. LPIPS was **NOT_RUN** because no learned quality weights were loaded, so the original PSNR/SSIM/LPIPS conjunction is **NOT_EVALUABLE**. Native 2K, the 6900-source obligation, latent-only embedding compatibility, method acceptance, authentication and final thesis acceptance are not established. C4 remains open and C5 dependent. Previous latent experiment failures are neither replaced nor retrospectively repaired by this amended method pilot.

The experiment used ten native development images (IDs 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768), unchanged supplied profile with QIM step 4.0, and the preregistered controls and transforms. See experiments/c4-qim-rgb-development-v1/plan.md, acceptance-criteria.md, cohort.json and experiment-spec.yaml for exact definitions and item-level source restrictions. No public image redistribution is authorized.

## Execution provenance

- Run: c4-qim-rgb-dev-001, stage C4-QIM-RGB-development, official runner status completed, exit 0.
- Exact clean executed commit: 2e05d926ec9eb889116a60be19fe5345211b512b.
- Canonical execution-manifest SHA256: 5532fe6fc5f7c88de4535a3d097fdda566e409dee1a8baf483c90c59b3f98b42.
- Results SHA256: 11132dc4363d4a2ec22f1754cd1291a96b4c83e85ea07d5a6bda686438b6945a.
- Runtime SHA256: 6a498b7550e3a3746d60dfdf07d36ef670cfefc3e2edd58f0539e791f081f735.
- Official start/end UTC: 2026-09-30T09:02:58.159304Z / 2026-09-30T09:04:02.814537Z (64.655 seconds outer elapsed; worker 60.198 seconds).
- Local WSL CPU only, CUDA unused, cost USD 0; no downloads, installs, paid services or GPU kernels.
- Retained private root: W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/qim-pilot-runs/C4-QIM-RGB-development/c4-qim-rgb-dev-001.
- Frozen manifest and reviewed package receipt: W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/qim-pilot-20260930/v2-final/execution-manifest.json and adjacent package-review.md in the parent directory.

The user's authenticated direct instruction was to design an experiment from their updated algorithm and then execute it. The authorization record honestly preserves that instruction and bounds this one reviewed local CPU run (1200 seconds, USD 0). It does not claim the user manually reviewed or typed the final hash. The official runner validated that serialized decision before dispatch. That one execution is now consumed: no rerun, extension or new scientific execution is implied. No official Spec Kit lifecycle state was advanced and nothing was publicly pushed.

## Review status

Independent exact-package review resolved checkpoint atomicity and missing-control accounting blockers before execution. A retained-output audit is recorded separately under audits/c4-qim-rgb-review-20260930/review.md; its verdict must be read at its actual scope, never as method or lifecycle acceptance.

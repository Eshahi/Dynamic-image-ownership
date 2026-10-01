# Engineering verification before the execution decision

Date: 2026-10-01. Related work: issue #18 and draft PR #67. Author: authenticated Codex task; independent reviewer: `/root/v4_execution_readiness_review`, actual `gpt-6-astra` with high reasoning effort. A stronger independent model was selected for scientific protocol and execution-boundary review under the recorded model-selection delegation. Reviewer and author differ.

## Ordinary checks

Verified Windows Python ran the 26 supplied v4 codec tests and 15 study-specific model-free tests together: 41 passed in 10.580 seconds, exit 0. The independent reviewer reproduced all 15 study-specific tests in 0.967 seconds and had reproduced the supplied 26 codec tests during the earlier review. These are synthetic engineering tests, not this scientific experiment or empirical attack success.

The reviewer found no remaining blocker in the settled code/design draft. Repairs cover failed-returned-image retention; saved/reopened suspect-only CLIP; corrected four-owner roster; VAE posterior mode rather than sampling; intact checker and malformed/unsafe-verdict rejection before postprocessing; finite atomic JSON checkpoints; attack timing; and transitive manifest inputs including the legacy module imported by the RGB helper. Complete clean-commit/canonical-manifest matching is a separate final check.

Read-only runtime verification checked all 23,021 bound installed files: zero hash mismatches, 7.387 seconds, no model imports or scientific kernels. Resources at the final preparation check: host free RAM 8,508,984 KiB; WSL MemAvailable 15,175,560 KiB; GPU total/free 12,227/10,892 MiB; W: free 143,404,781,568 bytes. Availability is transient and must be checked again immediately before dispatch. Selected envelopes remain RAM 6 GiB, VRAM 8 GiB, disk 2 GiB and USD 0. Guards are polled, not hard allocation limits.

## Independently reviewed core hashes

| Artifact | SHA-256 |
| --- | --- |
| `scripts/revised_watermark_v4.py` | `5c5dd3e2976da52d5983af273da5c5059c85a50f26d5abd12b5532387ded57fa` |
| `scripts/v4_study_worker.py` | `b7d4de75fa6a30b63d074dfbea73fb19b1b7cd679d8ece89c388ab8cbd22e270` |
| `scripts/run_v4_study.py` | `e28af79e465c2ec8ae96342ce8c49cd4e77fe7ed653c623061f2c555ab8407c6` |
| `scripts/prepare_v4_study.py` | `737191d4dc7eed2d9addc9d77bf580e5cb0e928d8ea70a02096d2f39840b3fd8` |
| `scripts/v4_study_boundary.py` | `38073ccceb5faa1ee9fb33675b5185a785cd807cbbdab4c31814bf9045884be3` |

## Boundaries preserved

No scientific run, human approval, controller verdict, public push, download, installation or paid compute is claimed by this document. The supplied algorithm remains unchanged. This is an image-domain development comparator, not the original latent architecture, native-2K/full-6,900 validation, legal ownership proof, or method acceptance. The public-profile statistical bound remains conditional and unvalidated; failures and incomplete controls must remain in denominators. Independent visual assessments and analysis require actual future outputs.

The new fixed batch has 537 rows and 1,884 authoritative detector calls across Copy-Paste, Regeneration and Semantic Collision. The prior v2 three-threat run and its consumed approval are distinct and must never be rerun or reused for this package. Spec Kit remains paused at plan-acceptance with no fabricated decision; unrelated tasks remain paused.

# Bounded independent redesign review, 2026-10-01

Related issue #18 / draft PR #67. Author: `/root`. Independent read-focused reviewer: `/root/v4_execution_readiness_review`, actual `gpt-6-astra` / high. This is a documentary and metadata-reference review, not production execution readiness, scientific acceptance, rights clearance, human approval or lifecycle transition.

The reviewer initially found two blockers: the first pending parent cell could have been in flight despite NOT_RUN, and new safety-rejected generation had no terminal completion contract. Both were corrected and independently re-reviewed. The settled verdict reports no remaining blocking documentary/reference finding. The parent snapshot remains immutable.

The metadata-only schedule replay exactly equals saved JSON: 237 units, 401 saved rows, 16 inherited safety failures, 66 component comparisons, 53 downstream-unreached generation candidates and one quarantined ambiguous cell (`t3-190676-0.4-1-C1`). Call accounting is 96 inherited + up to 1720 new + 64 known missing + 4 unresolved = 1884 planned. No automatic ambiguous retry or silent denominator exclusion is allowed. Parent sequential execution/checkpoint evidence, not NOT_RUN alone, supports the downstream classification.

Author reference tests: 12 passed in 0.015 seconds. Reviewer independently reproduced 12 passes in 0.019 seconds. Author validated the official experiment JSON schema and parsed every design JSON. These are ordinary model-free conformance checks; no image decoding, watermark calculations, model loading, study kernels or generation was performed for this redesign. No full official design-helper/runner validation was claimed because real entrypoints and execution manifests are absent.

## Exact core artifacts

| Artifact | SHA256 |
| --- | --- |
| `scripts/v4_recovery_design.py` | `c71215293889ee7403a5e92fd530f5b44eaaee5640621df74487114179b3e0c7` |
| `scripts/test_v4_recovery_design.py` | `a65ba5a7f6e0137cb094086662be1d789d6b3f3f6e577ff1a1edb48248e9d09c` |
| `plan.md` | `b2511c48883141df3df703ce828c0d84cde0e1f8b9557f3eade4bf0c3452f07c` |
| `schedule.json` | `62ddd044f94240069f73049f25c9e0acf78ec7d094cd39057b5401a8633bc364` |
| `experiment-spec.yaml` | `442e9f79d4dc1d5e1877d9f5fad21dbe7f2b48a30e2235df46e9d5e3da52dcc4` |
| `acceptance-criteria.md` | `bfc18174d65c1b7e6341ae988b48755f2782fc8cf3d3e45bc8ee6e4ebd33d98b` |
| `compute-estimate.json` | `4d7df16e1d240d00de413468c3781f6f76da4f789a36af5f14457d33920fefcd` |
| `execution-contract-status.json` | `8f6242b262d95a7d505165b844deaf3f6874f221b601cb9712c0cc81d7f43600` |

## Production boundary and warning

Still required: actual per-unit evaluator/adapter, atomic durable receipts and real fault-injection tests, durable official-runner process host and parent-session-loss test, exact clean manifests/input/runtime/resource bindings, bounded independent whole-package review and an actual exact execution decision. The consumed parent approval is not reusable. This design cannot guarantee survival of OS/WSL failure or power loss.

The existing VAE wrapper conflates affirmative unsafe and malformed flags as `safety_checker_blocked_or_malformed_vae_output`. The future adapter must distinguish affirmative safety rejection from malformed infrastructure failure. Only verified affirmative rejection may become `NEW_SAFETY_BLOCKED` with exact `safety_checker_blocked_output` evidence; malformed flags stop the dependent queue. This is a future implementation check, not grounds to relabel historical failures, loosen scientific criteria or retry them.

No public push, download/install, paid compute, additional automation, workflow acceptance or scientific dispatch occurred.

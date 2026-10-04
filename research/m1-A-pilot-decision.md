# Family A decision after the pure and source-bypass pilots

Version **`m1-A-pilot-decision-v1`**, 2026-10-04; design escalation at **xhigh**. This decision follows the observed development pilots and is therefore an exploratory amendment, not a retrospective preregistration. It freezes the next expansion before its outcomes. No GPU experiment is executed by this document and no held-out data or human verdict is introduced.

**Proceed with the unchanged hybrid recipe on the remaining ten reserved sources, then one complete frozen T3/T4/T5 assessment. Do not expand the current pure recipe or change its semantic code/thresholds yet.** The hybrid passes both clean quality and clean dual-signature recovery on its two preselected pilot sources, providing a sufficient engineering reason to test generality. Its remaining threat evidence is missing. The pure recipe misses both clean requirements and needs the separately specified reconstruction diagnosis before another expensive expansion.

## Evidence actually inspected

Both retained runs report `completed`, with two completed cases and routes. The ten source/output PNG hash receipts in each run were checked against retained bytes; no pixels were selected or outputs modified.

| Route/run under the main `.thesis-build/dev-runs/` | Commit | `run.json` SHA-256 | Duration |
| --- | --- | --- | ---: |
| `20261003-2337-A-pure-pilot-retry2` | `92705c288b8bfb54def37016bae541a181e6b0fc` | `854a23ebc4eac433d6cfe213837ae24789deba82e4047445704962cc4eafcc2d` | 467.485 s |
| `20261003-2347-A-hybrid-pilot` | `421787d14cfaceaa41c94141f517e1730da0390a` | `0e56178cbdf483ac790bef3c2b575ca9e072b3a4ca0f65a93a4a20f93848a677` | 466.016 s |

The successful pure execution follows retained engineering retries; this receipt does not erase those attempts. Source IDs 1675 and 4795 were fixed before outcomes. Quality below is relative to their canonical source RGB8 images, using saved/reopened outputs and the existing strict conjunction PSNR >35 dB, SSIM >.9, LPIPS <.1.

| Route | ID | Clean PSNR | Clean SSIM | Clean LPIPS | Clean detector | After one VAE cycle |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Pure decoder | 1675 | 31.21379 | .891491 | .071756 | `semantic_only` | `semantic_only` |
| Pure decoder | 4795 | 28.23120 | .716639 | .178808 | `semantic_only` | `semantic_only` |
| Source bypass | 1675 | 38.62899 | .985181 | .007618 | `both_match` | `both_match` |
| Source bypass | 4795 | 38.25546 | .982948 | .009204 | `both_match` | `semantic_only` |

Thus pure clean quality is **0/2**, clean dual match **0/2**, and semantic presence **2/2** both clean and after VAE. Hybrid clean quality and dual match are each **2/2**; after VAE its semantic presence is **2/2**, but dual match is only **1/2**. Do not report hybrid VAE joint recovery as 2/2.

The hybrid's selected semantic/instance scores are `(9.07194,8.64994)` and `(8.71570,9.99095)` clean; after VAE they are `(8.70966,5.14472)` and `(8.69107,4.71403)`. For the VAE instance scores, the relevant recomputed-code threshold is **4.9820330564**, while decoded-code search uses **8.2593268261**. The first image's instance evidence crosses the former by only .16269, while the second misses it by .26801. This is reason to measure the fixed attack grid, not to move the threshold between the two images. Retain detector candidate type and per-component thresholds, because a single displayed score does not identify which test was used.

Every source C0, matched C0 and cycled C0 returns `neither_match` for alpha and beta in these records. Both marked outputs, clean and cycled, return `neither_match` under beta. These are per-condition two-image controls, with duplicate/paired sources, not independent trials proving a population FPR. Gamma/delta will be included by the frozen threat assessor.

Hybrid VAE-cycle source-relative PSNR/SSIM/LPIPS are **26.60579/.811287/.057096** and **25.06666/.586150/.090499**. Their paired unmarked VAE controls are **26.69187/.818284/.056885** and **25.20381/.595006/.088430**. The cycle's quality loss is therefore already substantial on matched unmarked sources. Neither clean quality success nor cycle signature survival establishes visually harmless regeneration; report attack quality against both the source and same-arm clean image, with human judgments still missing.

## Explicit method amendment and limits

Let `D01(z)=clip((VAE.decode(z)+1)/2,0,1)`. Pure output is `D01(z*)`. Hybrid output is

`clip(source + D01(z*) - D01(z_ref), 0, 1)`, followed by the fixed RGB8 serialization.

Only the unscaled VAE latent is optimized, so the perturbation is generated through a frozen decoder. But the original source bypasses the VAE reconstruction path. The hybrid output is not constrained to the decoder manifold and is not a pure latent-decoded image or initial-noise watermark. Adopt the name **latent-generated residual with source bypass**, preserving the route tag `hybrid-source-bypass`. Its matched C0 is the source itself; the pure route's matched C0 is `D01(z_ref)`. The improvement in source quality is consistent with this structural difference and is not proof that latent optimization solved photographic VAE reconstruction.

The extractor remains genuinely inversion-free image DCT plus CLIP: suspect RGB8, public OwnerID, fixed profile and pinned CLIP weights only. It receives no original source, reference latent or enrollment feature. Its operational outputs must stay distinct from causal history. Untouched pure C1 already produces `regeneration-consistent`, while one deliberately VAE-cycled hybrid C1 produces `authentic-consistent`. These observations directly preclude treating the qualified labels as reliable causal classifications. Keep raw `both_match`, `semantic_only`, mismatch and abstention evidence; do not silently rename either case to match the known attack label.

The hybrid is an explicit amendment within family A, not an additional independent design family. Public feature-derived keys still allow adaptive re-embedding. The 32-bit semantic sketch's known collision/geometry problem is unresolved. No capacity increase, projection-seed search, new cryptographic claim or T5 success follows from these carrier results.

## Expansion frozen now

Keep the exact config from `research/m1-dual-latent-hybrid-dev.json`: source CLIP/pHash signing before watermark, owner alpha/beta, source-fixed surrogate weights, unscaled latent lr .01, 60 robust plus 40 joint updates, unchanged loss weights/margins and every-fourth-step VAE semantic term. Keep last-fixed-step selection, pinned SD1.5/CLIP/LPIPS, seed 0, float32, source preprocessing, RGB8 policy and all v5 detection parameters. The quality budget remains 35.2 dB in the optimizer and the external strict quality targets remain unchanged. Do not raise power, add instance cycle protection, change h signing order or select a better intermediate checkpoint.

Reuse the existing two hybrid enrollments without rerunning them. The new manifests are disjoint and differ from the pilot only in experiment ID and requested source IDs:

| Manifest | IDs, in order | Required `--reconstruction-run` |
| --- | --- | --- |
| [old2](m1-dual-latent-hybrid-expand-old2.json) | 6012, 25394 | main `.thesis-build/dev-runs/20261003-1455-latent-reconstruction` |
| [recovery4a](m1-dual-latent-hybrid-expand-recovery4a.json) | 80932, 109798, 134882, 147498 | main `.thesis-build/dev-runs/20261003-2255-latent-reconstruction-recovery` |
| [recovery4b](m1-dual-latent-hybrid-expand-recovery4b.json) | 177015, 190676, 468505, 499768 | same recovery directory |

Every initialization is the already completed, hash-verified step-200 endpoint. The old run's overall status remains `started`, but its first four cases are completed and valid inputs; its incomplete 80932 must not be used. The recovery run is completed with the other eight cases. No source is reassigned to a favorable reconstruction attempt or later step-600 result. Preserve both initialization provenances.

Run each manifest with the existing `scripts/m1_dual_latent.py --manifest ... --output-dir <new-main-dev-runs-directory> --reconstruction-run ...` after parent commit, GPU availability and ordinary provenance preflight. The two-image timing suggests roughly 8/16/16 minutes for the new shards; this is an estimate, not a promise. Each shard retains the existing one-hour cap, 10 GiB GPU cap and checkpoint/journal policy. Run sequentially, USD 0, with no downloads or held-out access. Failures remain explicit; a repair requires a separate recorded attempt and must not replace completed successful sources. No best-attempt selection is permitted.

Before execution, compare all scripts/asset-lock receipts with the hybrid pilot; the current assessor requires them to match exactly across enrollment shards. New manifest commits can differ, but do not edit an enrollment dependency mid-expansion. If a scientific bug forces a change, separate versions and amend the aggregation explicitly; do not bypass the receipt check. The union of pilot plus three shards is exactly the twelve reserved IDs, with no duplicate or absent source.

## Frozen threat assessment and next decision

After all three enrollment shards stop, prepare one new manifest using the existing [dual-threat assessor](m1-dual-threat-assessment.md), ordered pilot, old2, recovery4a, recovery4b, route `hybrid-source-bypass`. Preserve 489 planned conditions: 24 clean, 312 T3, 80 T4, 66 T5 component pairs, and seven T5 transfers. The 423 image conditions use the unchanged blind verifier for alpha and beta/gamma/delta, giving 1,692 planned detector calls. No new pairing, source eligibility, threshold or owner search is introduced. Incomplete enrollment remains missing in the fixed twelve-source inventory rather than shrinking the study.

Full expansion is justified before a separate two-image threat gate: the clean bridge passes, the additional enrollment costs about forty minutes, and T4/T5 need the fixed donor/recipient coverage. A two-image T3 result would add little confidence while leaving most pairs unavailable. Finish the full predefined grid even if an expanded source fails quality or clean detection; report intention-to-process coverage and valid-only diagnostics separately. A failed quality case is still attacked and reported. Do not stop at the most favorable strength.

Compare with retained v5 only on matched source/attack subsets, noting v5's originally smaller T3 source set and the hybrid's different output operator. This version is not PSNR matched to v5, so differing quality or robustness is descriptive and cannot establish a controlled superiority claim. Report semantic presence, instance presence, raw/qualified-state distributions, source and same-arm attack quality, transfer acceptance and all wrong-owner controls. T5 agent labels are fixed development labels, not human verdicts. For T3, report survival and attack-state agreement separately; a surviving dual mark is not automatically a correct regeneration classification.

After this inventory, make a fresh xhigh decision using the worst unresolved requirement. If the channel survives but T5 fails, assess capacity-aware semantic coding within the measured carrier budget; do not select a winning projection seed from the prior diagnostics. If T3 destroys even semantic evidence, investigate transport/objective support before adding payload bits. If T4 transfers the dual mark, report the content-binding failure and public-forgery limit rather than treating clean detection as authenticated ownership.

The pure route remains a retained **two-image negative recipe result**. Execute the already implemented [best/worst reconstruction diagnosis](m1-reconstruction-diagnosis.md) when scheduled; it may justify another pure attempt, but must not overwrite these outcomes or be described as a certified decoder floor. Hybrid success, failure, and the A/B/C/D alternatives remain separate from the final M1 exit decision. No milestone is complete on these two-image pilots alone.

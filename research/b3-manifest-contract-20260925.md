# B3 image-manifest contract, before acquisition

Status 2026-09-25, issue #10 / draft PR #60: this is a **schema and synthetic validator**, not `data/manifest.csv`, `data/dev-ids.json`, `data/datasheet.md`, dataset acquisition, split freeze or B3 acceptance. A6/#7 remains open. The user-authorized COCO choice is the official **2017 image release** for the existing 1,000-image commitment, recorded in [the decision](b3-coco-release-decision-20260925.md); it must never be relabeled as a 2020 image release. The other preserved commitments remain DIV2K 800 source-train plus 100 source-validation images and DiffusionDB 5,000 images. The planned study allocations remain prospective in [sample-size.md](sample-size.md).

`scripts/validate_data_manifest.py` defines one row per source image with the exact columns below. Its future invocation requires a concrete CSV and local asset root; it checks listed file sizes and SHA-256 values, rejects traversal/links, duplicate image IDs and paths, malformed fields, and identical bytes assigned to different content groups. It reports counts and rights-status labels. It makes **no** image-decoding, license-clearance, legal ownership, source-authenticity, count-completeness, deduplication beyond identical bytes, split-lock or scientific-use claim. Empty/header-only manifests fail.

| Field | Meaning |
| --- | --- |
| `domain` | One of `ms-coco`, `div2k`, `diffusiondb`. |
| `release_id`, `source_split`, `source_id` | Explicit upstream release/split/image identity, not an inferred study split. Their tuple must be unique. |
| `relative_path`, `raw_sha256`, `raw_size_bytes` | Local raw-byte identity under an explicit asset root. No absolute path or credential-bearing source URL. |
| `width`, `height` | Declared native pixel dimensions; later pinned decoder must verify these separately. |
| `group_id` | Provisional content-dependence group. Exact duplicate bytes must share one group; perceptual/prompt/seed grouping remains B4 work. |
| `source_url`, `license_reference` | Public HTTPS acquisition/terms references without query strings; these are citations, not rights clearance. |
| `rights_status`, `use_limitations` | `pending-image-rights` or `reviewed-restrictions`, plus explicit limitations. Neither label means copyright ownership or approval to publish/redistribute. |

Before creating the declared B3 outputs, pin source releases and archive digests, document per-image rights/terms and exclusions, acquire only the bounded selected bytes, decode them with the reviewed A6 image stack, verify native dimensions, review content groups, and meet or explicitly amend all source counts. B4 then freezes development/validation/test IDs without viewing method outcomes. No synthetic test can substitute for those steps.

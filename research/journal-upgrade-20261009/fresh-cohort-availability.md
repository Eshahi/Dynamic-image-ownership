# Fresh cohort availability: metadata-only planning

Prepared 2026-10-10 by Codex agent. No images, annotations, feature values, individual labels, outcome tables or metric files were opened. No download, manifest, execution infrastructure, protected edit or commit was made. This is a source-availability memo, not scientific authorization or a source-plan amendment.

## Decision

New downloads are not necessary for a narrow fresh COCO confirmation: the existing admitted partition has 600 COCO test groups, of which the historical 300-source schedule consumes exactly 300. The remaining **300 sources / 300 primary groups** have existing local raw paths and zero raw-digest overlap with that historical cohort. They are a technically available reserved pool, conditional on no other exposure and the future user's confirmatory approval. The historical 300 cannot be fresh confirmation after their M2 results informed method planning.

There is no already legally/scientifically cleared new confirmation. Existing source metadata retains pending image rights and restricted local academic use; approval of the historical run does not authorize the revised method on remaining holdouts. Published examples or redistribution remain separate decisions. Do not inspect remaining test pixels or calibration data during E3 development.

## Current partition and raw availability

Authoritative metadata inspected at `C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5/`:

- `data/splits.csv`, recorded SHA-256 `60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f`.
- `data/b4-admission-20260926/source-manifest.csv`, recorded SHA-256 `40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4`.
- `data/b4-admission-20260926/development-reservation.json`, recorded SHA-256 `0bfd4178a1929e26d12401000c1eda0c549034c348458844e72f0c5b0a8f79ae`.
- `data/datasheet.md`, `data/holdout.json`, `configs/splits-admitted-v2.json` and `research/b3-coco-source-candidates-20260926.md` for selection, restrictions and grouping rules.

Pins above are recorded documentary identities, not a new full-file rehash audit. Counts were recomputed from IDs, split/group fields and primary-representative flags. Local availability was checked with path existence only against the admitted receipt join under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/`; raw bytes were neither opened nor rehashed.

| Domain | Development images/groups | Calibration (`validation`) images/groups | Test images/groups | Remaining test after historical COCO300 | Existing remaining-test raw paths |
| --- | ---: | ---: | ---: | ---: | ---: |
| MS-COCO | 200/200 | 200/200 | 600/600 | 300/300 | 300/300 |
| DIV2K | 300/300 | 300/300 | 300/300 | 300/300 | 300/300 |
| DiffusionDB | 1000/259 | 1000/251 | 3000/757 | 3000/757 | 3000/3000 |
| Total | 1500/759 | 1500/751 | 3900/1657 | 3600/1357 | 3600/3600 |

All listed development and calibration raw paths also exist: 1500/1500 each. Existing directories are `val2017`, `DIV2K_train_HR`, `DIV2K_valid_HR` and `diffusiondb-2m`. This is actual local availability, rather than a promise to acquire sources. DiffusionDB's 3000 images supply only 757 operational groups; do not count seeds, same-group members or owner calls as independent sample units. Finite grouping is an operational leakage screen, not certified population independence.

The separate original 100 DIV2K native-validation IDs 0801–0900 and linked components are test-only under `data/holdout.json`; they cannot be borrowed for calibration. Original32 development reservations cover 10 COCO, 10 DIV2K and 12 DiffusionDB and preserve linked components in development.

## Exposure and overlap evidence

In the journal worktree, `research/m1-confirmatory-schedule-draft.json` contains 300 clean source UIDs. Its join to the admitted split has **300/300 in COCO test**, zero in development/calibration, leaving 300 COCO test groups. `research/m1-confirmatory-external-index.json` binds that same historical narrow schedule to raw receipts. MAIN `thesis-runs/d916749c/STATE.md` records historical M2 as the 300-source COCO run. This memo treats all of that schedule as exposed, including members without a particular attack outcome.

The fixed twelve development IDs from `research/m1-terminal-e2e-threat-schedule.json` are 1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505 and 499768. Their overlap with historical COCO300 is **0/12**. Ten match the admitted index, all ten in development; two are outside the admitted 1000-image COCO partition. Therefore the twelve are not identical to the original ten COCO reservation and must remain development-reserved when any expanded cohort is considered. `research/development-sources.md` was absent in both MAIN and this journal checkout at inspection; do not claim a complete modern reservation ledger exists.

Across all remaining test rows, overlap of recorded raw SHA-256 with the historical COCO300 is **zero**. No test pixels, canonical features or annotation values were used to establish this. Source UIDs/group IDs provide the membership exclusion; existing metadata hashes supplement duplicate exclusion.

“Fresh” here means not in the known M2 source schedule or twelve-source development schedule. I did not inspect every run's outcomes or private history, so I cannot certify that no other actor has viewed these sources. Existing metadata says native integrity, canonical preprocessing and leakage grouping occurred before the original lock; such engineering reads are disclosed and do not mean pristine never-decoded bytes. The relevant condition is no method-dependent scientific exposure or selection. Confirm historical run inventory IDs and any additional development reservation IDs before the future milestone freeze, without opening outcomes or images.

## Deterministic route preserving the existing plan

Keep the protected source plan and existing split assignments untouched. After M1a passes and during M1b planning, use the complement of the historical300 within admitted `domain=ms-coco`, `study_split=test`, `primary_group_representative=true`. Exclude any additional known scientifically exposed UID, raw digest or full linked group using metadata only. With the currently known exposure ledger this selects exactly all remaining300, so there is no outcome-based sampling choice. Do not replace members following safety blocks, decode failures or poor quality; retain failures under frozen analysis rules. Freeze revised method and thresholds before their pixels are unlocked by the user's milestone decision.

Use the existing 200-group COCO calibration partition for new calibration only if that scientific access is explicitly included in the future approval. Calibration is not development and cannot be consumed under the development-only authority. Keep it disjoint from the fresh300. Expanded development can use untouched members of the existing development partition after a prospective deterministic metadata selection, preserving all original reservations; it must not borrow validation/test sources.

DIV2K300 and DiffusionDB757 test representatives offer additional reserved domains with existing local bytes, subject to the same exposure/rights/approval checks. They do not provide an independent diffusion-model experiment automatically: acquisition domain, source generation provenance, regeneration model and detector model are different factors. An all-domain revised protocol must be presented as its own prospective amendment; this memo does not adopt it.

If more than the remaining300 COCO confirmation sources are needed, obtain a new source-cohort decision at the milestone rather than silently enlarging the protected plan. One precise metadata-only candidate extension is the preserved B3 COCO ordered-reserve frame: 1274 license-label-screened val2017 identities originally comprised 1000 candidates plus274 reserves; three prospective admission replacements used reserves, so an upper bound of271 reserves remains outside admitted membership, before group/exposure exclusions. Preserve the recorded rank `SHA256(UTF8("b3-coco-source-candidate-v1\\0") || annotation_digest_bytes || uint64be(image_id))`, exclude every admitted or development UID/hash/full group, and take successive eligible entries without viewing images or labels. Do not treat the upper bound as verified eligible fresh N, and do not open its per-image annotation fields now. A supplement could reserve disjoint successive groups for development/calibration/confirmation in a fixed order before outcomes, subject to user approval for any new held-out source contract. Existing local COCO val2017 bytes make an initial download unnecessary; availability outside the admitted receipt join was not checked here.

For a truly new free licensed dataset, predeclare the primary-source release, licensing rule, UID hash-ranking tag, full-group exclusions and separate development/calibration/test allocations before acquisition or outcomes. Current authority allows free development acquisition, not unilateral creation/use of a new confirmatory source contract or protected-plan editing. Record URLs, licences, revisions, bytes and SHA-256 in `research/downloads.md` and reserve development additions; no paid/gated source. The repository's 30 GB overall download cap applies across prior acquisitions. Historical datasource documentation records 8,493,745,129 bytes of fourteen DiffusionDB archives and 3,070,774,949 selected raw bytes (selected copies are not additional downloaded archives), plus models/papers elsewhere. This memo did not establish remaining download headroom, so no new large acquisition budget is claimed. No acquisition is required for the current fresh300 route.

M1a remains the immediate task. This document deliberately creates no fresh manifest, schedule, launcher, rehearsal or approval record.

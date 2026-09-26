# B3 bounded DiffusionDB acquisition decision, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60).

## Actual user authority

The pending question proposed increasing only the original hash-ranked candidate prefix from eight to fourteen, preserving 5,000 images, 1,000 reserves, the 0.10 NSFW exclusion threshold and source ranking. In this authenticated Codex task on 2026-09-26 the user directly replied **«دانلود کن»** (download it). In this concrete context, that authorizes the fourteen-part resource amendment **and agent acquisition of exactly this batch**, superseding the prior personal-download preference for these archives only. It is not a fabricated Spec Kit gate decision, blanket dataset-download permission, scientific-compute approval or paid budget. See [machine-readable scope record](../data/intake/20260926-diffusiondb-download-authorization.json).

## Production, not diagnostic, evidence

The production cap is now fourteen. Strict `b3_read_diffusiondb_metadata.py` re-hashed and parsed the same 194,548,652-byte immutable Parquet snapshot with separately installed PyArrow 21.0.0. Checked all 2,000,000 rows / 2,000 x 1,000 parts, including full validation/cardinality of **all fourteen** candidate parts before accepting any prefix. Malformed prompt types block even otherwise score-excluded rows; empty text remains an explicit exclusion. Ranking, target count and cutoff are unchanged.

[Production receipt](../data/intake/20260926-approved-fourteen-part-production-selection.json), SHA-256 `094fa4cebc4481a337b1761af01f9887265da6c0e6531112fc749085988bd002`:

- 14,000 candidate rows examined; 7,206 score/size exclusions and three additional empty-text exclusions.
- **6,219 distinct normalized exact-prompt groups**; shortest eligible prefix is all fourteen parts.
- Parts: `948, 1232, 1790, 420, 1929, 1168, 1467, 558, 943, 1034, 836, 268, 1854, 1359`.
- No prompt/user identifiers exported and no final source IDs/splits frozen.

The historical proposal and diagnostic outputs remain unchanged for provenance. Their pending status is superseded by this decision and the strict production receipt, not silently rewritten. Archive source revision is `fb620fbe49fa4420e0734bd9c0df11f51176b61f`; pinned paths/sizes/LFS SHA-256 values remain in [the original proposal inventory](../data/intake/20260926-proposed-diffusiondb-parts.json), itself hash-bound by the authorization record.

## Download behavior and limits

`scripts/acquire_b3_diffusiondb_parts.ps1` consumes hash-checked authorization, proposal and production snapshots. It admits only those exact fourteen source paths/order and **8,493,745,129 bytes** of final archives (~8.49 GB / 7.91 GiB), over HTTPS at the pinned curator revision. Actual retransmission overhead may exceed final archive bytes if a connection fails; at most three resumable attempts per file, each with a two-hour curl timeout. This ceiling describes the approved archive inventory, not a false measurement of network billing. No paid service is used.

Archives remain ignored under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/diffusiondb-2m/archives/`. One exclusive FileShare.None lock serializes writers; a persistent lock filename alone does not imply a live writer. Partial bytes remain under `.zip.partial`, final names are assigned only after exact size/full SHA-256 match, verified existing archives are reused, and wrong/oversized files are preserved and block rather than overwritten/deleted. Linked paths, contract mismatches and insufficient storage block. Initial W: free space exceeded 226 GB. No extraction or arbitrary dataset code runs in this helper. Do not interpret a completed archive as rights/content/duplicate acceptance.

Before network execution, PowerShell parser and `-ListOnly` contract preview passed. Full workflow-interpreter suite: **152 tests, 146 pass and six expected dependency skips**. Ten focused production-selection tests passed, including a favorable early prefix with a later missing/incomplete part and malformed text in an excluded later row. Independent narrow technical review is required before launch; record its actor and exact commit separately. The official controller read-only status still reports `d916749c` paused at `plan-acceptance`; this resource decision does not advance it.

B3 remains open for archive receipt, safe image inspection, item-level rights/content/grouping, final source manifest and development IDs. Scientific execution still needs the runner's exact-manifest user approval.

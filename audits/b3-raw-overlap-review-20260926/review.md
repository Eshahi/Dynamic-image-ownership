# Independent B3 raw-overlap and additional archive review

Date: 2026-09-26. Author: `/root`. Actual independent reviewer: `/root/b3_intake_review`, requested under `AGENTS.md` and `research/approval-policy.md`. Exact reviewed commit: `c376564b6fe5ace678e0a7ea7382141ec0a2a32f`. The reviewer returned a read-focused report and made no tracked changes; this record transcribes that report, not a human verdict.

## Findings and independent evidence

No blocking finding for the narrow raw-inventory overlap and completed-archive integrity evidence. Five focused model-free tests passed independently. All four local CSV snapshot digests matched the recorded input hashes. In-memory helper replay equaled the existing ignored overlap receipt and its serialized output digest `c8f1c4a385758270e5a206c4d79455acdbaaf9972c8dc3c03d2431c87a040146`.

The reviewer separately constructed raw-digest buckets, reproducing 8,900 records and seven duplicate groups/fourteen images, with two/two/three groups within parts 948/1232/1790. No cross-inventory-domain overlap occurred, and complete fourteen-part coverage was correctly false. The reviewer also fully replayed completed parts 1232 and 1790: exact upstream sizes/SHA-256, every member CRC, all 1,000 native PNG verify/decode/dimension checks, aggregate fields and reconstructed per-image CSV digests matched.

The report confirmed strict inventory schemas/cardinalities, duplicate-qualified-ID rejection, inconsistent byte-count/dimension rejection for identical digests, stable domain-separated raw group identity, distinct cross-part versus cross-source labeling, hash-before-parse snapshots and exclusive new output creation. No partial archive was accessed or download process modified.

## Non-blocking limitations and acceptance boundary

- Supplied CSV digests do not authenticate arbitrary inventories; this review accepts only the inspected previously verified local snapshots.
- Raw-byte equality is not canonical decoded-pixel, near-duplicate, prompt/user dependence or eligibility analysis; documentation retains these limits.
- Eleven other candidate parts are outside this checkpoint. No dependence conclusion extends to them.

The root's full workflow suite passed **162 tests, 154 pass/eight expected dependency skips**, and `git diff --check` passed. The accepted scope is these bound inventories' raw-byte overlap and the two additional completed archive integrity receipts only. No final source/study IDs, content/rights, B3 closure, split/gate transition or scientific acceptance was granted. The official run remains paused at plan-acceptance.

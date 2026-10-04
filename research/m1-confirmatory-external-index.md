# Confirmatory external-input metadata index

Prepared2026-10-04, metadata only. Candidate UNRESOLVED; source contract/scientific split acceptance, scientific unlock and scientific compute all remain false. This is a contained index for the alreadyversioned fixed300COCO512 schedule, not source-plan adoption, an approval/gate file, a raw-data inspection or a scientific run.

`research/m1-confirmatory-external-index.json` has300/300 existing raw input receipts,300distinct frozen operational groups and300distinct recorded raw SHA256 values, with no input errors. Final index byte SHA256 is `8521b783324b62c9394081f0f7f0d8e5162b6592b9bf3256dddf0d400e28b88a` (488,938bytes); the300recorded raw sizes total52,398,675bytes, without rereading them. It preserves the exact schedule order/public OwnerID/next wrong owner/uint64 decimal+hex seeds and the fixedT3/T4/T5 schedule through the pinned schedule receipt. Group independence is not certified. The acquisition manifest raw-byte group and the later split component group are separate fields; their difference is expected, not a silent group replacement.

## Exact preparation inputs

The builder `scripts/m1_confirmatory_external_index.py` reads only its enumerated, pinned existing metadata files from `C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5` and the versioned schedule in this worktree. It does not read private canonical/feature bridge files or follow any metadata image/annotation path.

| Metadata receipt | SHA256 |
| --- | --- |
| admitted data/b4-admission-20260926/source-manifest.csv | 40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4 |
| data/splits.csv | 60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f |
| configs/splits-admitted-v2.json | 02cab97279eb657dfe52c34a5fa987c375fac40b137b098b646754f7cfeb0bc3 |
| data/intake/20260926-extracted-source-receipt.json | 3fac7726917fcb2ebe41e2c264d12dca73d4d5af23d3ec2e9424dc1741639224 |
| versioned research/m1-confirmatory-schedule-draft.json | 83c023bc3e0acb2a38142e8ef6e6a27f9216b7dacb5d885ab778b8799469f35d |
| scripts/b3_local_data_receipt.py path-binding code | d21debb5aaa669912d96f9f3ed96a67ff06668dcf838d4074d4a9c0f84b4a68b |

Existing datasheet/local-intake/handoff documentation byte receipts are also pinned in the index, supplying recorded licenses, source-page revision and original archive limitation. No source metadata was rewritten. The earlier data/manifest.csv is not substituted for the admitted manifest.

Each entry has scheduledUID/source-group/study_split=test and release=coco-2017/source_split=val2017; recorded relative path, raw SHA256 and byte size; original source URL, per-image license reference, pending rights status and use limitations. External paths are lexical strings under MAINdata/raw; the builder does **not** call resolve, exists, stat, hash or decode on them. Recorded per-image licenses in this300 are198CC-BY2.0 and102CC-BY-SA2.0; their counts are metadata coverage, not rights clearance. Exact current raw bytes will only be verified after legitimate scientific unlock. No dimension, source quality, feature, annotation category or detector score was used to construct the index.

The builder recomputes the existing metadata-only deterministic schedule and requires exact equality of all300clean entries, T3UIDs, T4pairs, T5policy and metadata candidate count. Source/split UID, raw SHA, release and primary test representative/group are joined exactly. Missing/malformed planned source receipts remain explicit300denominator entries with errors and raw_index_ready=false; duplicates or altered authority/schedule are rejected. Paths must be canonical relative POSIX paths and match the recorded COCO extracted-wrapper/member naming rule. No replacement occurs.

## Annotation artifact, archive limitation and authorization

The acquisition receipt authenticates the existing extracted **instances_val2017.json** artifact:19,987,840bytes, SHA256`e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`. Its lexical external path is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/annotations_trainval2017/annotations/instances_val2017.json`, derived from the pinned intake code's `intake` directory binding and documented raw root. That path was never followed. Values/content were never opened, hashed or parsed now. Exact fields are `annotation.receipt_kind=extracted-file-only`, `annotation.sha256`, `annotation.size_bytes`, `annotation.external_path`, and `annotation.byte_exact_artifact_receipt_ready=true`; `annotation.raw_bytes_verified_now=false`, `annotation.archive_sha256=null`, `annotation.archive_revision=null`.

The index identifies COCO2017/val2017 and the alreadyrecorded official annotation archive sourceURL, with annotations/website CC-BY4.0 per existing datasheet. The maintained download/terms page revision `5e1c4da72464b1c6f068df0c02c91e3000ea62c4` is a **web-source revision**, not an archive-byte revision. Original annotations_trainval2017.zip SHA256 and archive revision are null: the intake explicitly says original ZIPs absent/archive_hashes_available=false. Do not describe the extracted-file hash as an archive hash, fabricate a revision or download/hash annotations to repair this preparation.

Missing original archive identity alone need not prevent prospective use of the exact authenticated extracted artifact if that artifact choice/release/source/license is explicitly frozen for M1review. Therefore byte-exact extracted annotation receipt readiness and raw-index readiness are true, archive identity readiness remains false, archive identity is not required for this extracted-artifact contract, and scientific unlock remains false. This document proposes no source-plan acceptance or milestone verdict. A future authorized worker verifies the **file** receipt before parsing only the frozen300source observations and recording deterministic T5candidate/rejection ledger; annotation shortages stay missing and do not trigger a rule change.

## Reproduction and tests

```powershell
# New output only; existing index is never overwritten.
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_confirmatory_external_index.py --output research/m1-confirmatory-external-index-rebuilt.json
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m unittest discover -s tests -p test_m1_confirmatory_external_index.py -v
```

Nine synthetic CPU tests passed: fixed300deterministic exact joins/no filesystem access; missing receipt denominator retention; raw hash mismatch/malformed size retention; altered subset/group/seed/unlock/candidate refusal; duplicate/wrong authority refusal; traversal/absolute/Windows separator path guards without following them; annotation artifact/archive distinction; missing/bad/duplicate/changed annotation receipt refusal; unknown metadata input rejected before read. Pure assembly is tested with Pathread/stat/resolve patched to fail; no actual source paths are used in fixtures. Actual builder execution only read the enumerated metadata and wrote this new contained index. File/payload hashes are distinct; metadata_payload_sha256 hashes canonical JSON before adding that field, and the official input receipt must hash final index bytes.

Remaining execution work: real official scientific envelope/unlock, path/link containment and byte verification inside the authorized worker, adopted candidate/core, original200-step initialization, resource/recovery/rehearsal receipts, and real source/scope/milestone decisions. Metadata readiness never implies pixels valid now or permission to inspect them.

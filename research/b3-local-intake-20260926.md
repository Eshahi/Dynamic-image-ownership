# B3 local first-batch intake (2026-09-26)

Issue #10 / draft PR #60. The user supplied **extracted** files under ignored `data/raw/` and asked work to resume. Agents did not download datasets. Original COCO/DIV2K ZIPs are absent: their archive SHA-256 and upstream archive-byte identity remain unavailable. Source files were not relocated, rewritten or committed.

## Checked local evidence

- All 5,000 COCO val2017 JPEGs and 800+100 DIV2K HR PNGs passed exact expected filenames, per-file SHA-256/size, single-frame native dimensions/mode/format, Pillow `verify()` and full pixel decode. COCO dimensions match supplied `instances_val2017.json`; its license references resolve. No identical raw-byte groups occurred across 5,900 images. This is not a decoded-pixel/near-duplicate/content audit or study selection.
- [Aggregate receipt](../data/intake/20260926-extracted-source-receipt.json) records six annotation-file hashes and the ignored inventory location. The 5,900-row CSV SHA-256 is `bd849697919a1bba5101319ded0401f14be8e8ea150629187fd692389698fe18`. Its canonical ordered record-stream digest is separately `8893b095fc96ad63f480f2da72d797a1dc604d5689f4212802161a59bffeecaf`; these are different encodings.
- COCO license IDs 1/2/3/4/5/6/7 have 1,431/630/1,414/857/417/246/5 images. References are not certified ownership. NoDerivs/NonCommercial/ShareAlike restrictions remain relevant to later selection/publication; no blanket clearance follows.
- `metadata.parquet` is 194,548,652 bytes, SHA-256 `eecd341187bc91c07f5994ad0660d40228ea025616fd57a509bef8323677c68f`, matching pinned curator LFS claims. The reader parses the same checked in-memory snapshot, reads seven required columns, never reads `user_name`, exports no prompts, and checks 2,000,000 rows with exactly 1,000 per part.

The user separately approved the 26,203,175-byte official PyArrow 21.0.0 CPython 3.12 Windows wheel, hash-locked in `requirements-b3-metadata-win312.txt`. Isolated installation in ignored `.thesis-build/b3-metadata-venv` and `pip check` passed. No scientific environment change. Reader reference: [Apache Arrow Parquet documentation](https://arrow.apache.org/docs/python/parquet.html).

## Preserved failures, repairs and shortfall

Initial intake failed because each extracted image folder has a single same-named wrapper directory. The helper now explicitly handles that shape without moving data; ignored `.thesis-build/b3-intake-20260926/failure.json` preserves the failure. The second complete intake passed.

Prior independent-review blockers in `e1a15a7` were repaired: all part IDs are validated before filtering; used parts require exactly 1,000 rows; overfull parts block. Regression tests cover malformed IDs, incomplete parts and an impossible 6,000-record single part.

Real Parquet attempts then blocked on empty prompts and `image_nsfw=2.0`; failed ignored selection receipts are retained. The pinned [curator README](https://huggingface.co/datasets/poloclub/diffusiondb/blob/fb620fbe49fa4420e0734bd9c0df11f51176b61f/README.md) documents 2.0 as an already-flagged/blurred NSFW sentinel. It is now excluded by the unchanged 0.10 ceiling, while other invalid/nonfinite scores block. Empty text prompts are explicit exclusions, never invented groups; null/nontext prompts block. Safety criteria were not relaxed.

The corrected first-eight-part rule returns `blocked_insufficient_metadata_eligible_groups`: 8,000 rows, 4,112 score/size exclusions, three additional empty-prompt exclusions, **3,541 distinct eligible groups**. No download list is accepted under this rule.

An unchanged-ranking metadata diagnostic yielded 4,033/4,503/4,917/5,393/5,823/**6,219** groups at prefixes 9/10/11/12/13/14. This is not an authorized amendment or method outcome. A pending proposal preserves 5,000 images plus 1,000 reserves and the same content ceiling by expanding only to the shortest 14-part prefix. [Proposed path/size/LFS inventory](../data/intake/20260926-proposed-diffusiondb-parts.json) totals **8,493,745,129 bytes** (8.49 GB / 7.91 GiB), read from the pinned curator paths-info API. No image bytes were fetched. User resource authorization and independent review are pending; do not expand the cap or request ZIPs before both.

B3/#10 remains open for DiffusionDB images, rights/content checks, final 6,900-source manifest and development IDs. B4 study grouping/splits remain pending. No inference, watermarking, scientific experiment or gate transition occurred; official `d916749c` remains paused at `plan-acceptance`.

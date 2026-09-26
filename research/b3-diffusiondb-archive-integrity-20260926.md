# B3 streaming acquisition and first completed archive integrity, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60). The separately [user-authorized fourteen-part acquisition](b3-diffusiondb-acquisition-decision-20260926.md) continues under one hidden PowerShell writer PID 38904. No duplicate writer or new download was started. The first archive finished and passed upstream full size/SHA-256 while the second part began; do not extrapolate this to all fourteen.

## Local inspection, not scientific compute

Read-only central-directory inspection of the completed `part-000948.zip` found **1,000 root PNG members plus `part-000948.json`**, not just 1,000 entries. No directory wrappers are present in this observed part. The metadata JSON may contain prompts or user-linked content; the inspector checks its CRC and full byte digest **without parsing/exporting its content**. No ZIP is extracted and no dataset Python code, model, metric or scientific experiment is executed.

The [index helper](../scripts/b3_diffusiondb_part_index.py) checks the pinned 194,548,652-byte Parquet snapshot and full 2M-row / 2,000 x 1,000 cardinalities, reading only part ID, image name and native dimensions. It emits an **ignored local integrity frame** for all 14,000 candidate-part images, not only eligible images and not a frozen 5,000-image source selection. No prompt/user columns are read/exported. Its local SHA-256 is `c987a60ce1c21335b6a6ef5887530e7be8b1013b86d0272d3c2441978c20f829`.

The [archive inspector](../scripts/b3_diffusiondb_archive_receipt.py) binds its archive to the pinned size/SHA-256 inventory, checks a regular/unlinked same verified in-memory snapshot, and validates the entire ZIP directory before any decompression. Require exact metadata-bound canonical UUIDv4 PNG names plus one exact part-JSON name, 1,001 entries, no duplicates, directories, encrypted/link/nonregular entries, traversal/extra members or unsupported compression. Resource ceilings: 64 MiB per PNG member, 8 MiB metadata JSON, 2 GiB total member bytes and 64 Mi-pixels per image; a ceiling failure blocks instead of silently excluding/reducing the dataset. The raw ZIP size is checked before snapshot allocation; private index is capped at 16 MiB. CRC checks occur on full member reads; each PNG then passes format, single-frame, mode, exact Parquet native dimensions, Pillow verify and full decode. Per-image byte hashes/dimensions/mode are recorded in an ignored CSV. No image data or raw prompt/user content enters Git.

## Actual part 948 evidence

[Aggregate receipt](../data/intake/20260926-diffusiondb-part-000948-integrity.json):

- Archive: **559,791,366 bytes**, full upstream SHA-256 `e5c9c9cbf0e13f2b388d95bf50ecc579ce1897c16ef23465f7cb2360383203aa`.
- **1,000 PNGs fully decoded/hashed**, all names and native dimensions equal the pinned metadata part frame; all 1,001 members passed ZIP CRC.
- Total uncompressed member bytes **559,958,716**; metadata JSON hash `c2e524a1a3236d74ff8a6d73c983106c67b6e53afd89642b250e44ef5c9801d4` (not a claim that its private content was inspected).
- Ignored per-image CSV SHA-256 `95faffa4267a925846ca22f4ebf80b60c9e84ed0f6e48470465fd248a4c02b44`; Pillow **12.3.0** from the already-installed Windows science venv, used only for image decoding. No installation or science-environment change occurred.

The receipt remains `archive_crc_and_png_decode_only`, `content_reviewed=false`, `rights_cleared=false`, `study_ids_frozen=false`, `scientific_compute=false`. It does not assert eligibility, near-duplicate independence, final 5,000 source IDs or B3 completion. Later complete parts must undergo the same checks without opening in-flight `.partial` bytes. Final rights/content/grouping and dev IDs remain pending.

## Reproduction and verification

Ignored private index and receipts are under the stable project `.thesis-build/b3-diffusiondb-integrity-20260926/`. Use existing metadata-only interpreter for the index and existing Pillow science interpreter only for decoding:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/b3-metadata-venv/Scripts/python.exe' `
  scripts/b3_diffusiondb_part_index.py --metadata 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/metadata.parquet' `
  --output '<new ignored private index path>'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' `
  scripts/b3_diffusiondb_archive_receipt.py --archive '<completed approved ZIP path>' `
  --inventory data/intake/20260926-proposed-diffusiondb-parts.json `
  --index 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/b3-diffusiondb-integrity-20260926/private-image-index.json' `
  --index-sha256 c987a60ce1c21335b6a6ef5887530e7be8b1013b86d0272d3c2441978c20f829 `
  --output-prefix '<new ignored receipt prefix>'
```

Five adversarial/synthetic ZIP tests pass in the existing Pillow interpreter, including traversal, duplicate/member mismatches, symlinks, encryption, unsupported compression, byte/dimension ceilings, wrong PNG dimensions and corrupt ZIP CRC. Workflow-only interpreter: three pass/two expected Pillow skips; full suite: **157 tests, 149 pass/eight expected dependency skips**. `git diff --check` passed. Independent actor `/root/b3_intake_review` replayed exact `2bb9cf75986c16cd588721535ba66acd23dd09ae` with no narrow blocker: full in-memory index reconstruction, exact ZIP size/hash, all 1,000 CRC/PNG decode records and CSV digest matched, and all five focused tests passed independently. See [review record](../audits/b3-archive-integrity-review-20260926/review.md). No gate or issue is advanced by this narrow review.

Acquisition failure provenance: part 1232's first transfer ended with curl code **18**, preserving **228,863,859 bytes** and reporting 322,493,169 missing bytes. The same parent automatically began resumable attempt two; no duplicate/replacement writer was created and neither the failure nor partial file was discarded. The raw ignored acquisition logs remain authoritative for ongoing progress. It is not a completed second archive until exact size/full digest pass.

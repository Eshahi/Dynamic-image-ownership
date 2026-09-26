# B3 COCO source-candidate frame, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60). This advances deterministic source eligibility while the separate DiffusionDB fourteen-part resource decision is pending. It does not change that eight-part production cap, acquire data, approve scientific compute, certify rights, allocate study splits or complete B3.

## Selection rule and applicability limits

The original commitment remains **1,000 COCO source images**, with the user-authorized 2017 release-year amendment. The research contract leaves subset IDs and licenses to the data specification; no method outcomes have been evaluated. We conservatively construct a candidate frame from annotation license IDs **4 (CC BY 2.0)** and **5 (CC BY-SA 2.0)**, both with recorded native width/height at least 64 pixels. This is a derivative-compatible *license-label screen*, not a finding that other labels are unlawful for research. Exclude NC/ND and ambiguous labels from this candidate frame to avoid carrying their extra reuse ambiguity into watermark/derivative publication planning. Do not silently generalize findings to all COCO: the licensing screen restricts the sampling population and may alter its content distribution.

Primary evidence: [COCO-maintained terms at pinned commit](https://github.com/cocodataset/cocodataset.github.io/blob/5e1c4da72464b1c6f068df0c02c91e3000ea62c4/dataset/termsofuse.htm) distinguish annotation rights from image rights and disclaim consortium ownership of images. The official [BY 2.0 deed](https://creativecommons.org/licenses/by/2.0/) permits adaptation with attribution; [BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) additionally imposes ShareAlike for distributed adaptations. These deeds do not guarantee the licensor's authority or all privacy/publicity/moral rights. Preserve the actual 2.0 labels; neither is converted into the annotation license's 4.0 version. Per-item copyright/attribution, Flickr terms and any publication remain pending, not accepted by this screen.

Validate **all 5,000** annotation/image-inventory identities before eligibility: canonical integer source IDs, twelve-digit filenames, exact dimensions/license agreement, defined license IDs, recorded JPEG/RGB-or-L metadata, unique raw hashes, positive bytes, safe relative paths and Flickr URL hooks. Bind ranking to the intake annotation SHA-256:

```text
rank = SHA256("b3-coco-source-candidate-v1\0" UTF-8 bytes
              || annotation_digest_bytes || uint64be(integer_image_id))
order = ascending (rank_hex, canonical_decimal_source_id)
```

The first 1,000 eligible records are **candidates**, and every remaining eligible record is an ordered reserve. After item-level content/rights/dependence checks, any replacement must retain its exclusion reason and advance this order, never choose by method performance. If fewer than 1,000 acceptable source records remain, stop and report the shortfall; do not relax eligibility or reduce the commitment implicitly. This is not a development/test split or a permission to expose holdouts. Near-duplicate/group exclusions remain to be implemented and reviewed before final source/study freezing.

## Bound local evidence

Inputs were already user-provided and checked at intake. The candidate builder reads the same verified in-memory snapshots it hashes; it does not re-decode images or claim new verification of raw files since intake.

- Annotation: `data/raw/annotations_trainval2017/annotations/instances_val2017.json`, SHA-256 `e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`.
- Ignored local inventory: `.thesis-build/b3-intake-20260926-r2/images.csv`, SHA-256 `bd849697919a1bba5101319ded0401f14be8e8ea150629187fd692389698fe18` (CSV encoding digest, not the separate canonical row-stream digest).
- Output: [source candidates JSON](../data/intake/20260926-coco-source-candidates.json), SHA-256 `37dbd65045497b54a02d14b965824c2155606a0a39d194eced4bc5bdfceff270`.
- Result: **1,274 eligible**, **3,726 license-label exclusions**, **zero additional native-dimension exclusions**; **1,000 candidates** (677 BY, 323 BY-SA) and **274 ordered reserves**. Every output record explicitly remains `pending-image-rights`.

Flickr static-image URLs are retained as annotation attribution hooks, not asserted to be a current creator/title/license page. No creator/title is fabricated. Original source ZIP identity remains unavailable. Current/source rights, content checks, decoded/near-duplicate grouping and real DiffusionDB images remain required before `data/manifest.csv` or `data/dev-ids.json` is final. The candidate JSON deliberately is neither of those artifacts.

## Reproduction and tests

From the B3 checkout, using the existing workflow interpreter:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' `
  scripts/b3_coco_candidates.py `
  --annotation 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/annotations_trainval2017/annotations/instances_val2017.json' `
  --inventory 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/b3-intake-20260926-r2/images.csv' `
  --output '<new nonexisting local receipt path>'
```

The CLI fixes the production 5,000/1,000 counts, rejects input digest changes and refuses to overwrite an earlier output. Eight focused synthetic tests passed; the full workflow-interpreter suite ran **151 tests: 145 passed, six expected dependency skips**. These are selection/provenance tests, not science. `git diff --check` passed. Initial real-input invocation failed before writing because the draft parser incorrectly assumed twelve-digit *inventory IDs*: intake stores canonical integer IDs and only pads filenames. That failure is recorded here; the parser and fixtures were repaired, then actual input and both test suites passed. No source/intake byte or prior failure was overwritten.

Independent review of the exact implementation/artifacts is required for narrow technical acceptance. Until recorded, this remains authored evidence only. No Spec Kit lifecycle state is advanced.

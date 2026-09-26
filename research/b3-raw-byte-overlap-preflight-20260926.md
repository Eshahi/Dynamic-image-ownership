# B3 raw-byte dependence preflight, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60). This bounded CPU inventory audit proceeds while the already-authorized single download writer continues. It does not run a model, canonicalize source pixels, select final images, freeze splits or authorize science.

## Verified additional bytes

The existing fail-closed archive inspector fully verified two more final ZIPs against pinned upstream sizes/SHA-256 and the existing private metadata index. Each contains exactly 1,000 metadata-bound PNGs plus one part JSON; all CRC/full native PNG decodes/dimensions passed. No extraction, arbitrary dataset code or prompt/user-content parsing occurred. Aggregate receipts: [1232](../data/intake/20260926-diffusiondb-part-001232-integrity.json), [1790](../data/intake/20260926-diffusiondb-part-001790-integrity.json). They retain all content/rights/study/science acceptance flags as false.

Part 1232 recovered within the same original writer: attempt one curl18 after 228,863,859 bytes, attempt two curl56 after 421,183,731 bytes, attempt three successfully resumed to 551,357,028 bytes and matched upstream SHA-256. Prior errors and transfer logs are preserved; no second writer or new batch was launched. Part 1790 completed at 564,341,623 bytes; subsequent in-flight parts are outside this receipt.

## Actual overlap evidence and limit

The [raw grouping helper](../scripts/b3_raw_duplicate_groups.py) checks the exact digest of each already-verified ignored CSV snapshot, validates schema/source-frame cardinalities and source-qualified identities, and groups equal **raw image byte hashes**. Identical-byte records with inconsistent byte count or native dimensions block. A group ID is SHA-256 over a fixed domain separator and the raw digest, so input order or later-added members cannot change its identity. Cross-part inventory overlap is distinguished from cross-dataset overlap. Input CSV digests bind inventory evidence; this step does not re-read every original image byte or establish the provenance of an arbitrary caller-supplied CSV.

The complete available frame at this checkpoint has **8,900 records**: COCO 5,000, DIV2K 800+100, and three complete DiffusionDB parts (948, 1232, 1790). It contains **seven exact raw-byte duplicate groups involving fourteen images**, all within individual DiffusionDB parts (two, two and three groups respectively). No raw-byte overlap was found between these inventory domains. This does **not** imply no decoded-equivalent, near-duplicate, prompt/user or other content dependence. It does not imply any of these fourteen images survives the independent metadata eligibility rule. Do not drop or replace images on this preliminary result alone; preserve groups for later reviewed selection/dependence handling.

The ignored local output is `.thesis-build/b3-diffusiondb-integrity-20260926/raw-overlap-three-parts.json`, SHA-256 `c8f1c4a385758270e5a206c4d79455acdbaaf9972c8dc3c03d2431c87a040146`. It contains source image IDs but no raw prompts/user identifiers; only aggregate counts/digests are recorded here. The earlier two-part diagnostic is preserved separately, not overwritten. No final study IDs or manifest is created. Eleven candidate parts remain unaudited at this checkpoint.

## Reproduction

Use the verified workflow interpreter and pair each `--inventory` with its exact `--sha256`, plus a new ignored `--output` path. All input files are under the stable W: project, not this checkout:

| Inventory path beneath stable project | SHA-256 |
| --- | --- |
| `.thesis-build/b3-intake-20260926-r2/images.csv` | `bd849697919a1bba5101319ded0401f14be8e8ea150629187fd692389698fe18` |
| `.thesis-build/b3-diffusiondb-integrity-20260926/part-000948.csv` | `95faffa4267a925846ca22f4ebf80b60c9e84ed0f6e48470465fd248a4c02b44` |
| `.thesis-build/b3-diffusiondb-integrity-20260926/part-001232.csv` | `b2437d764fd6274ec281ad18aaf3d773ec9ccfd048c52dc5e53d1c8e34d7c3ca` |
| `.thesis-build/b3-diffusiondb-integrity-20260926/part-001790.csv` | `f0917e7d823843e57e0dc0f620e2b13dd683e234bdbd525ad31df0cd55abf3d5` |

Five focused model-free tests cover stable groups/input permutation, duplicate IDs and conflicting digest metadata, complete/partial ZIP frames, unknown headers/digests and cross-part versus cross-source labeling. Full workflow suite: **162 tests, 154 pass/eight expected dependency skips**; `git diff --check` passed. Independent actor `/root/b3_intake_review` replayed exact `c376564b6fe5ace678e0a7ea7382141ec0a2a32f` with no narrow blocker: all input/receipt hashes, separate digest buckets, five tests and full additional ZIP/CRC/PNG/CSV checks matched. See [the exact-artifact review](../audits/b3-raw-overlap-review-20260926/review.md). A5 canonical RGB8/EXIF/ICC handling and B4/B5 dependence decisions remain separate; neither raw grouping nor PNG integrity acceptance substitutes for them. B3 and all dependent gates remain open.

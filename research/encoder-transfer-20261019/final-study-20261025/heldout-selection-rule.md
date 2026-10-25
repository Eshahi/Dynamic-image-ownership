# Fresh confirmation identifiers: rule frozen before drawing

Written 2026-10-25 during WP5, before any candidate image identifier was requested or selected. This rule will be committed before the metadata draw. It permits metadata only; no image, thumbnail, dataset archive, pixel decoding, model pass or outcome may be fetched or inspected in this session.

## Population, fixed seed and order

Use Wikimedia Commons Picture of the Day (POTD) entries dated **2018-01-01 through 2025-12-31 inclusive** as a fresh, separately named source frame. This is a curated public-image population, not a representative sample of all natural images. It is distinct from the project's COCO/DIV2K split namespaces; that does not prove absence of mirrored or visually similar content.

Generate those calendar dates without looking at image entries. For each date compute SHA256 of the UTF-8 string `et-final-holdout-v1/20261025/YYYY-MM-DD`. Sort ascending by the lowercase hexadecimal digest, breaking ties by date. This is the fixed seeded order. No category, visual quality, semantic class, watermark result or model outcome changes it.

Read the official Commons `Template:Potd/YYYY-MM-DD` metadata to identify its file. Follow template indirection if needed using text only. Retrieve official file metadata (imageinfo/extmetadata), never the URL's pixel content. Record exact API queries, timestamps and page/revision identifiers when exposed. Use a descriptive user agent and at most approximately one request per second; bounded batched title queries are allowed. A parsing ambiguity is a recorded ineligible candidate, not permission to choose its image by viewing it.

## Eligibility, uniqueness and attribution

Accept only candidates whose official metadata establishes all of the following:

- A JPEG image with both sides at least 512 pixels, no more than 40 million pixels, aspect ratio in [0.5, 2], and file size at most 20,000,000 bytes. These are metadata/resource constraints, not pixel judgments. No claim that every eligible JPEG is a photograph is made.
- An explicit reusable licence: CC BY or CC BY-SA version 2.0/2.5/3.0/4.0, CC0, or an explicitly labelled public-domain dedication/status. Record the exact label and licence URL. Missing, conflicting, NC/ND-only or unclear metadata is ineligible. No licence is inferred from mere hosting on Commons.
- A nonempty recorded artist/creator attribution. HTML is retained as attribution evidence and a plain-text form is produced without rendering linked images. For grouping, HTML-decode and strip tags, normalize whitespace, and lowercase the complete plain-text creator string. Exclude empty or solely unknown/anonymous creator labels. Keep at most one selected image per exact normalized creator string; this is a conservative clustering precaution, not proof that differently spelled creators are independent.
- The canonical Commons file title, page ID, original file URL and provided file SHA1 have not already appeared in accepted candidates. Different POTD dates pointing to the same file or SHA1 do not create new sources.
- No exact identifier, canonical file URL/title, upstream source-image identifier exposed in the metadata, or available recorded hash overlaps the project's documented development sources, downloads and held-out manifests. Read these ledgers as text/metadata only. Record the files checked and their digests. URL/title normalization must be documented; do not compare a Commons page ID to a COCO integer as though they shared a namespace.

The identity audit checks metadata equality. It cannot establish absence of mirrored images with different URLs, near duplicates or shared depicted scenes. All such limits must remain in the manifest/report. Future authorized acquisition must perform exact raw/canonical hash exclusion against existing recorded hashes before scientific use; it must not open old held-out pixels. No new descriptor or visual-similarity screening is authorized now.

## Fixed selection, reserves and future failures

Traverse the fixed date order and accept eligible, nonduplicate candidates until **240** are selected: first **200 primary sources**, then **40 ordered reserves**. Stop at that point and retain the rejected-candidate reasons and enough metadata provenance to reproduce the traversal. Do not view pixels. If the date frame is exhausted, report the achieved count and a partial pool; do not expand dates or weaken rules after seeing metadata without a separately labelled prospective amendment.

Reserves may replace unavailable/licence-invalid/identity-overlapping files only during a logged acquisition-and-identity stage completed **before any marking or detector outcome on this new pool**. Use the next eligible reserve in its frozen order. Keep the failed primary's receipt and reason. Once any scientific outcome is released, no replacement is allowed: missing attempts remain in the prescribed denominator and no new source may be selected on the basis of quality or retention. If fewer than 200 eligible acquired sources remain, confirmation is incomplete; do not silently advertise n=200 completed sources.

The manifest must contain identifiers, original/description URLs, licence/attribution, metadata dimensions/size/SHA1, date/hash rank, primary/reserve assignment, acquisition status `NOT_DOWNLOADED`, selection-rule commit and exclusion-audit references. This file is an identifier-only preregistration aid; it is not execution approval, a licence warranty, a claim of unseen pixels everywhere, or an independently random population sample beyond the stated deterministic selection design.

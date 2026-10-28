# Stage C fresh full-frame identifier selection rule

Status: PROSPECTIVE RULE; NO IDENTIFIERS SELECTED. Written 2026-10-28 after metadata-only feasibility counts and before applying the new seeded ordering. Commit this rule before any selection. No pixels, thumbnails or URLs were dereferenced. This document is not execution approval.

## Frame and order

Use ALL 2,922 calendar dates from 2018-01-01 through 2025-12-31 inclusive, fixed before new metadata requests. This is a curated public-image population, not representative of all natural images. For each date compute lowercase SHA256 of UTF-8 `tifs-stage-c-v1/20261028/YYYY-MM-DD`; sort ascending digest, then ascending date. Traverse this committed full-frame order without prioritizing cached dates. The new order has not been applied during feasibility counting.

Reuse matching old official cached template/file responses and their original timestamps/query receipts exactly. These include 1,000 earlier shuffled template dates and 820 projected file rows; they do not constitute the entire frame. Cached availability and prior metadata inspection do not imply scientific image exposure. Old primary/reserve identities remain excluded. For missing records, query only `https://commons.wikimedia.org/w/api.php` with bounded batches of at most 50 POTD template/file titles and only revisions/imageinfo/extmetadata metadata properties. No media or thumbnail URL is ever opened. Retain response bytes, request URL, actual timestamp, status and SHA256. No fresh timestamp is attached to an old response. Use a six-second request-start interval, at most one request per second; reject redirects and stop on API errors/rate limits rather than retrying around restrictions. A metadata error is not permission to reorder dates or silently skip a candidate.

## Eligibility

Require official JPEG MIME, minimum side >=512 pixels, total pixels <=40,000,000, aspect ratio 0.5–2 inclusive and original size <=20,000,000 bytes. Require complete file title, namespaced Commons page ID, URL, provided SHA1 and unambiguous template/file mapping. After an official metadata query, a missing file or ambiguous template is ineligible with retained evidence. A transient request failure stops the draw and can be resumed without changing order.

Require exact CC BY or CC BY-SA labels at version 2.0/2.5/3.0/4.0 with agreeing code and creativecommons.org versioned URL; CC0 with its official zero/1.0 URL; or explicit Public domain label, `pd` code and `Copyrighted=False`. Do not add ported variants, FAL, GFDL, NC/ND or unclear labels. A public-domain status lacking LicenseUrl is recorded as null. Preserve full attribution HTML and exact licence evidence.

Creator grouping: HTML-decode, strip tags without rendering, collapse whitespace, lowercase the complete resulting attribution string. Require nonempty attribution not solely unknown/anonymous/author/artist labels or punctuation. Accept at most ONE exact normalized creator string within the entire NEW primary-plus-reserve pool. Previous pool creators need not be globally excluded; exact prior images must be. This string rule does not prove creator independence or prevent aliases.

## Prior identities and exclusions

Reuse the historical frozen exclusion inventory and its 79 file receipts exactly as evidence, without recreating or changing the protected source plan: `analysis/heldout-metadata/exclusion-identifiers.json`, `exclusion-files.json`, and `analysis/heldout-metadata-audit.md` relative to the final-study directory. Union that inventory with ALL 240 rows (200 primary AND 40 reserves, whether downloaded or not) of `heldout-manifest.json`, the Phase-B acquired-source receipts, current `research/development-sources.md`, and any subsequent documented pool identifiers in worktree/MAIN text-only records. Record current paths/hashes and additions in the eventual manifest audit; historical receipts do not certify absence of additions after their date.

Compare namespaced Commons page IDs, normalized canonical file title, description and original URL, SHA1 and recoverable image-specific upstream URLs/IDs from credit/source/description metadata. Preserve COCO/DIV2K namespace prefixes: a bare Commons page integer is never equated to a COCO/DIV2K integer. Exclude any same-namespace identity or available hash match, including all old reserves. Hash equality across algorithms is not meaningful.

URL normalization: HTML/percent-decode, lowercase, remove trailing slash/semicolon/backtick; remove only the Commons API `utm_source`, `utm_campaign`, `utm_content` tracking parameters, retaining other query identity. Title normalization additionally maps underscores to spaces and collapses whitespace. Record conservative normalization collisions; do not silently bypass them. Generic licence, help and creator-page links are not image-specific identities. Within the new pool deduplicate page IDs, normalized titles/URLs, provided SHA1 and exposed upstream image identifiers as well as creators.

## Size, reserves and failure handling

Target 120 primary plus 40 ordered reserves; first 120 eligible acceptances are primary, next 40 reserves. Select only after this rule and `scripts/tifs_stage_c_identifiers.py` have been committed; record the exact commit. If all 2,922 dates are exhausted before 160 acceptances, write an INSUFFICIENT partial pool and report achieved counts. Never expand dates, relax creator grouping or lower n after metadata inspection. The cache alone has at most 62 eligible unused creator groups and is insufficient; this full-frame rule is a prospective expansion fixed before any new requests. Do not select cached acceptances first and append fresh metadata afterward.

After this full-frame rule is committed, final rows must carry rule commit/hash, date/order digest and rank, assignment/order, all official identifiers, licence/attribution/dimensions, receipt filename/hash/revision IDs, `acquisition_status: NOT_DOWNLOADED`, null raw/canonical SHA256 and `execution_approval: false`. No pixel acquisition is permitted here. Later user-authorized server acquisition must compare raw and canonical hashes with recorded old pools before any scientific use; no old held-out pixels are opened. Exact metadata equality cannot detect mirrors/near duplicates or establish pretraining exclusion.

Reserves may replace only acquisition/licence/identity failures, in frozen reserve order, before ANY new-pool scientific outcome is available. Preserve failed-source receipts. Once outcomes exist, no substitutions; missingness remains in the protocol denominator. Fewer than 120 acquired eligible primaries is incomplete confirmation.

## Frozen input file receipts

Paths are repository-relative; original historical absolute receipts remain in their existing file. SHA256 applies to the currently read bytes. This list fixes the cache version, not permission to render URLs.

| Input | SHA256 |
|---|---|
| research/development-sources.md | 263a06a5df969f6c001096cbfd4a403fef0e3e3582c83c5a48f497df07aed9ee |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/candidate-template-map.json | 5804394b75b24bae0ac888b2f9b915b7b19075cb519c928eab0df4a0d9a312b3 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/exclusion-files.json | 82f1d77122c71100982102020e81d94c6d1c83d9364f18afc17d09bc752639f0 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/exclusion-identifiers.json | 2ca50d584666ee3595ff293581bd29f330510b0ea221cb5df292eadaf47aa9fd |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0000.json | 3fe256f03176f14e607d0ad8f85f0df55bb97edcbcffe384556ee7fbbcd7c937 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0020.json | 5114f529d7e14cc04204985b89a42664740ff1f39321014dd344fb23a18ef228 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0040.json | 30b3402989058344b7bd45fce94a9f5e6bc880e7ac1fafa86a32db5c1d7bee35 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0060.json | 9a0db96947db10ea9c115b58a5221ea29efa53ea54650c61f3009751ea620d63 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0080.json | a4257b3635c3bb0f1a8900c46fb561e085d1d05e761e6fc8d2862f3d4abe5b86 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0100.json | 9de0ace5f58a23ac84d7a1920f500cfc4aa453c7a59951d27d62605b433958a5 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0120.json | d94392b223a533629050cc187c12f3d5c53ad67fac18ae55c3aa21f62cb83102 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0140.json | d3cc9cf815db053f4bb4f67482857eb4cc0bcc65de4d5132596965c67e045ae9 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-0160.json | 0fee7b19797f2c341236f39c8e682551c0419712994f44472b058addbf1b9929 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0000.json | 73b8ef8d7d5abac49b05f627bef6270cdb8af0c32462897d0ef66e5702db8cbf |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0020.json | a63bd6120e301f822cae7e7fc7c6511f5d3e69bbca4f1ca2452706f0d30cc6f0 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0040.json | c84b611024e813a06c9fdc65bcc9b9f5b9e913a62b51b1acaf12f1fc76f20ad2 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0060.json | 89fe8e29840d2cdda1cc630e2e60bea3f94b565da50b6a9075016d7e2ab74021 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0080.json | 6095dc6f604570cb9decaae844857110368773ca787b6db6d78c432d10fbc6d5 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0100.json | 06c3446d727b02df9265c924c038b81f4e3cf9e37c9a540847f60614f419cf94 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0120.json | bd7613f36a535e612ffdb633697accf0da6c98019c0a6b0f3efe7effb204da24 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0140.json | d3192dd11c0e04cc48a01bcd0cc9d86267e57791176d54a3ce39a13c88652c45 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0160.json | 6b11ba3f8d8074b79c7d00f498f70fdf43ea6283686c146577530d7d8f8b9e93 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0180.json | 20fcf8a2063c77f521b631bf6e521a1b6233ac49ecf171fd6f657985393f5d18 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0200.json | a56ca01f46fa53a31ed6b29396c343ca9c679f16681ed743933ad266b3eea00c |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0220.json | 6799645dcad20dc64a47eb88b071483aef0e0a6108c063af9a7d787e421fa92a |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0240.json | 9ed9b9c712870e6cba40ad58b8b52a27bf20f58ab3ee41fe615519757ca75022 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0260.json | 6335b49b4580b2051e20536045e3c3e7d3deae3e7643cb932072f0e0fd77ac9a |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0280.json | b088e5427b6bc5e160d0cff15755ec7f0f03aedc437dbe4c0ecbd06df5b700eb |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0300.json | 98d2b4fada95d79063cb20a8ee2210bc392643c0340b6e503dd4099611faeecd |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0320.json | e331e6222e81029c9e03db3f5cab8d3ae9909aee83f52ff702fe888176b927dc |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0340.json | 2d591cb17aa922b16262a13cf0219e7562ce725580f43e62e7dfc00afb8f13ba |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-corrected-0360.json | 936d90c1c35024fec779668416af2330532727762deea7808465ec7327948237 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0500.json | ff3aad4ea5a4ef0494bb270f51f648e275f800f12540b1543a7886018ce8d780 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0520.json | 0687752d6d04dd952c0ccd19ea18d38e67848dbedf688e667cd85ee94845d7a2 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0540.json | 4cb0a4490192f1a57400c8d5937c63f752b214e56acf6c6bc837a02518643944 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0560.json | 0c7be6401ac5589ffcc90574056bcf8ccd5c8ee9b2053a0f2f389d7612522e47 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0580.json | 28a276e4fb551a54f681fd73c090fe87c54756cb966e2e7c060a4c97eda34156 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0600.json | fee65669b5b59892c2eec313a532ad8df81552011fc91b464b056b9d5aa31318 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0620.json | 0a9615fa5791b828fd29e9522e09a58fc7ab4c017f2913eae83c379607b5cf5a |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0640.json | 903b03f9ec877f1c4518cc57dac08d459c3c6bdfad68a203af05c5f096b42fc9 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0660.json | 58cacef5c8f2b01fd9bdda8d3e35a0cb098e012a9afc0a5f4aa01844802db433 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0680.json | c2365b979257f2e52cef16ad9a62124766f0f0a3f181f8243e3c5414a4711718 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0700.json | 402ad2b2b26a27721adbb48b0982c59f690038e39049c055d820d2f3b6e0b753 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0720.json | a93354a79c7af5307e543118820f58ed052da402394b5c8b3e803dfdaba84ee1 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0740.json | 167f4a2c7336031a194ec022a075b11ee2d37712cf99f417754663c17520a2de |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0760.json | c9936dc692aad89bae03fda176af4f7d5bfeef94b8a59a33e0ca213fbf37bbf6 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0780.json | e3cb1cf07b42f99c5260d29410ac9396ab67b56b8a767d983141cf1e58078ef5 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-next-0800.json | 9813ebda7d103c66c9b972e7464be3519834f6eaf038a424b10981b978fa815f |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/files-plain-template-0283.json | 4dff73a195970091668a9cbd96662840dd80389703b899c81cf07b02453bea32 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/flat-file-metadata.json | 5928ef902f726368f1da5be9116775e83d917bf98cb4617cf34df3138f9d0250 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0000.json | 7b5c88a35caf5ec46425a4bac95ed6a77d3bbb423bdc1f0e3d6087d5f91bbc2f |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0050.json | 2d48479f6f63e583d41aed02a0fa903de4a56afd0bc0d1ad04d335d8e5a9b9d0 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0100.json | 4c0d345f3d541d81a0bb08d8031fa4ddc0a921ba5965e2fbd93c3cd0a77c8923 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0150.json | 269cde9650c2c4158ffb0d9621106a6ab8a6ebf9c24a4bc3c39a8e8bdaddae1b |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0200.json | 9efa0dba023c99db6425bfabba61d626ceafdc9af121c01bf0d8723322cb7fbe |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0250.json | def21d5e99dd5570d037a94b3eb378bb5462f75b8e64230a4ada7277a0f08d18 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0300.json | 01ff1bc532c79e781313b1de60618616b98b3cdcb6bba8aba50f09b8df08e63f |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0350.json | 65c828f4a86debbe3de438b3cb5e38bb76a1e73ce28762ba96626c3ab82cd7ef |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0400.json | ef78d7b3ee1799e3075549c1850811d6a7469cc25f6a73a15fc0018067bf0177 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0450.json | f7f6c367737577a17cee2b900c28f38a9db7ccfa3b58d9aac557e59db4db333e |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0500.json | 9f053e5166cbda4f8b4d534660c1656d3352f0ef7a383bc13367fd47c88abd17 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0550.json | 93544074033d8aaf2ffae0695865b8b2b524972d67405b0d854d984f997fc2ce |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0600.json | dcf6e63f88f372387d3951d84508982e1594f28eb7fe9352b706d4c5829a7a91 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0650.json | 993cb37bd8637ad0d236b9c01ad62801a51c0b4f94ee95a96ca84473dbf32151 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0700.json | 6778fd6300306de4477bc9de590eab3392a164231b918ab85e67ac9a3a124681 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0750.json | 2e20eb6b0d426515271b2c20bff29f819b4b0b9360be1f1f60c359afa953733a |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0800.json | acd75a3a7c9c46c263a85893c7ae0fc355bc8dfc40521dce5e04f0b7c840a130 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0850.json | ceac389497197439ce788152e9d106711c28d4e4b135f3c9ca6ceda365d7b4d9 |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0900.json | f975b62060fb5f42dd15ad2cc50ddcdf36b8c9d14e81b98295ae64e84412b45e |
| research/encoder-transfer-20261019/final-study-20261025/analysis/heldout-metadata/templates-0950.json | d1996cad1194afca115383f523b016505cbb1c2f948ce78d1f185da7c0f0d7ef |
| research/encoder-transfer-20261019/final-study-20261025/heldout-manifest.json | 323790d531b75f136bf5603c8f69a3b704886253d518212011e8c49ded90fae1 |
| research/encoder-transfer-20261019/final-study-20261025/phase-b/phase-b-sources.json | 1ebd184c4a0bc5de92ee2f5fabc0c0100018969d1b1a9328b54f9da799978b8b |

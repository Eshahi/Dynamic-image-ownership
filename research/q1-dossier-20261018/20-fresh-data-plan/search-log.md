# Fresh-data metadata documentation search log

Date: 19 October 2026. Tool: `web.run` (through `functions.exec`). Official text pages only. This log distinguishes search results from direct document access. Useful-hit counts mean primary documents retained for this plan, not all engine matches. A zero means no search hit was retained as evidence, not that no relevant source exists. No literature novelty/absence claim is made.

Local start clock, obtained with PowerShell `Get-Date -Format o`: `2026-10-19T04:09:55.4604753-08:00`. Original session deadline `2026-10-19T04:04:04.3769833-08:00` had expired; this bounded parent-assigned continuation did not start a new timed session.

## Exact search queries

The first four queries were issued in one batch. Their combined output was broad and partly truncated. No search-hit factual claim from that batch was retained; the known official URLs from the existing gap-closure plan were opened directly and verified below. Thus these four rows deliberately count zero retained useful search hits; they do not estimate the engine's number of relevant results.

| Date | Engine/tool operation | Exact query | Useful hits retained | Disposition |
|---|---|---|---:|---|
| 2026-10-19 | web.run search_query | `site.storage.googleapis.com/openimages/web V7 image metadata author license original url` | 0 | Official URLs verified by direct opens D1–D2. |
| 2026-10-19 | web.run search_query | `site.commons.wikimedia.org Commons licensing reuse individual file metadata author` | 0 | Official URLs verified by direct opens D3–D4. |
| 2026-10-19 | web.run search_query | `site-nlpir.nist.gov V3C2 dataset usage agreement` | 0 | Official catalog/form verified by D5 and D8; no agreement submitted. |
| 2026-10-19 | web.run search_query | `site.ultravideo.fi UVG dataset creative commons noncommercial` | 0 | Provider page and its license link verified by D6–D7. |
| 2026-10-19 | web.run search_query | `site.mediawiki.org API Imageinfo extmetadata sha1 commonmetadata` | 1 | Retained canonical API:Imageinfo documentation; language duplicates and source-code hits not separately counted. Opened D9. |

## Direct official documents inspected

These are metadata/policy inspections, not V2 paper readings and not individual asset checks. Access times below are date-level; no precise web-request time is invented. The renderer sometimes displayed surrounding lines beyond the requested locator. No media links, image examples, thumbnail links, bulk metadata files, dataset/code downloads or API asset queries were followed.

| ID | Date | Tool/access | Exact URL | Relevant locator and result |
|---|---|---|---|---|
| D1 | 2026-10-19 | web.run open; find `Licenses` | https://storage.googleapis.com/openimages/web/factsfigures_v7.html | Lines 277–280: listed image/annotation licenses and per-image verification caveat. Useful official document: 1. |
| D2 | 2026-10-19 | web.run open; find `OriginalMD5`; find `Author` | https://storage.googleapis.com/openimages/web/download_v7.html | Lines 571–589: fields; base64 MD5; byte size; changing thumbnail caveat; rotation. Useful official document: 1. |
| D3 | 2026-10-19 | web.run open; find `individual`; open at line 220 | https://commons.wikimedia.org/wiki/Commons:Licensing | Lines 337–381 inspected in returned text: license information and reuse responsibility; no file/license certification. Useful official document: 1. |
| D4 | 2026-10-19 | web.run open; find `responsibility` (no match); open at line 75 | https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia | Lines 133–168: individual terms, author/uploader distinction and warranty caveat. Useful official document: 1. |
| D5 | 2026-10-19 | web.run open; find `agreement` | https://catalog.data.gov/dataset/vimeo-creative-commons-collection-v3c2 | Lines 68–81 and 136: catalog description, form link and agreement requirement. Catalog license not applied to every video. Useful official document: 1. |
| D6 | 2026-10-19 | web.run open; find `NonCommercial` (no match); find `16` | https://ultravideo.fi/dataset.html | Lines 23–29: 16-sequence provider statement and noncommercial license link. Individual per-sequence license/copyright fields appear empty in extracted text. Useful official document: 1. |
| D7 | 2026-10-19 | web.run click D6 link 20; open resolved document at line 40 | https://creativecommons.org/licenses/by-nc/3.0/deed.en_US | Redirected to https://creativecommons.org/licenses/by-nc/3.0/deed.en ; lines 36–64 identify CC BY-NC 3.0 Unported and limitations. Useful official document: 1. |
| D8 | 2026-10-19 | web.run click D5 link 10; open at line 0 | https://www-nlpir.nist.gov/projects/tv2019/pastdata/ad.hoc.search/V3C_Org.Form.txt | Lines 28–58 and 61–74: scope, per-video JSON license, withdrawal and organizational signature. Read as text only; no contact/signature. Useful official document: 1. |
| D9 | 2026-10-19 | web.run open | https://www.mediawiki.org/wiki/API:Imageinfo | Lines 155–193: uploader/version/title/size/SHA-1/extmetadata fields. API documentation read; no asset metadata requested. Useful official document: 1. |

## Local text inspected and authoring checks

- Authoritative MAIN `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/thesis-runs/d916749c/STATE.md` read once at task start.
- This worktree's `research/q1-dossier-20261018/BRIEF.md` and `07-gap-closure-plan.md` read; targeted `rg` around source/licensing/creator/F2 terms retained the relevant planning text. The initial combined shell output was truncated; source-specific/F2 text was then read with `rg`.
- A directory-name listing checked the existing dossier layout. No retained scientific outputs or pixels were opened for this follow-up.
- New files are documentation/schema only within `20-fresh-data-plan/`; no real asset rows, new IDs or split assignments exist. No Python, science interpreter or experiment command was used. No shared-state file or git operation was performed by this child task.

## What remains unverified

No candidate assets have been inventoried. Individual license scope, attribution details, creator identity, cross-dataset overlap, group diversity, source availability, annotation reliability, precision feasibility and actual-use/release compatibility remain unresolved. Opened policy pages do not certify those facts. The fresh-data plan records a prospective process; it supplies no evidence of new empirical performance.

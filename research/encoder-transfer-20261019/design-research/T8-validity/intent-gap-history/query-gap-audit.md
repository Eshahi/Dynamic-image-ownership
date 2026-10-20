# T8 strict discovery query-gap audit

Fresh gap-agent correction, 2026-10-20. Parent acceptance and the required independent package review remain pending.

## What was wrong

The historical author package reported 11 successful substantive queries in four categories. Q13/Q14 retrieve metadata for named model IDs; Q15/Q16 retrieve trees from named repositories at known commits. These are useful official-content inspections, but they cannot count as discovery searches. Excluding them leaves **seven** substantive discovery queries in **three** categories: web, OpenAlex and arXiv API. Q13-Q16 and every original receipt are retained. The original author query manifest, floor audit, search log, synthesis and progress file are copied byte-for-byte into `query-gap-history/`; current documents explicitly mark the correction.

## Fresh searches and screening

Six genuinely new discovery searches were made to real OpenAlex/arXiv search endpoints. Each returned eight results with HTTP 200. Exact GET URLs, query strings, User-Agent, request and completion timestamps, response status/headers, raw request/response paths and SHA-256 values are in [the manifest](query-manifest.json). Raw bytes are stored only in MAIN `.thesis-build/q1-research-20261018/cache/T8-1b-query-gap/`, outside Git.

| Query | Distinct search job | Count | Screened leads and relevance |
|---|---|---|---|
| Q18, OpenAlex | Training-use and watermark overlap/memorization | no | ROBIN, MSAT-LDM, memorization/generalization theory and DIAGNOSIS are adjacent image-model leads. Tabular/LLM hits are excluded. No title establishes actual training overlap. |
| Q19, OpenAlex | Safety-filter false positives and content bias | yes | DiffGuard, Stable Diffusion safety-filter red-teaming and recent image-classifier safety work directly identify candidates for V30. Broad surveys and unrelated adaptation work are not relied on. |
| Q20, OpenAlex | Resizing/interpolation and LPIPS sensitivity | no | Eight results are mostly peripheral super-resolution, video, medical or general quality work. Excluded conservatively; Q22 supplies direct leads. |
| Q21, OpenAlex | Forgery, false attribution and null calibration | yes | Randomized-key forgery mitigation, Forging Tree-Ring and Residual Transferability are direct candidate threats for V39/V65. Soft Bindings is already read and adds no source credit. |
| Q22, arXiv API | Perceptual-metric shift/resampling/robustness | yes | R-LPIPS, Shift-tolerant Perceptual Similarity and E-LPIPS directly address the metric-sensitivity search job. Segmentation, lunar mapping and classifier hits are excluded. |
| Q23, OpenAlex | Dataset duplication and diffusion memorization | yes | Extracting Training Data, Local Coverage Governs Memorization and other memorization papers identify direct candidates for V02/V25. The repeated theory hit is not another source. |

All **48 returned leads** have individual rank/title/screening decisions in the machine manifest. Q18 addresses mostly watermark/training-use task boundaries and is conservatively excluded. Q23 directly searches dataset duplication and memorization and supplies the countable training-dependence query. Q20 and Q22 are separate backend searches, and only the direct Q22 response counts. Search snippets, titles, abstracts and OpenAlex metadata have **no V2 credit** and support no new empirical claim. A lead would need a primary-text method/evaluation read before being used to revise the science. This bounded gap correction does not introduce another baseline or attack.

## Corrected floor

There are now **23 logged requests: 19 distinct discovery searches plus four known-content inspections**. Eleven successful substantive discovery queries count: Q01, Q03, Q04, Q05, Q09, Q11, Q17, Q19, Q21, Q22 and Q23. They cover **three categories: web, OpenAlex and arXiv API**. Thus the minimum of ten queries/three categories is met without counting any official-content inspection or the peripheral/adjacent Q18/Q20. Four new queries count, meeting the requested four-query gap fill.

The **68 distinct threats and 14 own primary V2 papers are unchanged**. Existing V02/V25, V30, V39/V65 and V56 already retain the training-dependence, missingness, attribution and metric limits. These searches make discovery coverage broader; metadata alone cannot resolve hidden training overlap, calibrate an FPR, prove a filter bias or quantify metric instability. No consequential new scientific finding was adopted, and no protocol, code, shared state, source images, outputs or decisions were changed.

[The machine checks](query-gap-checks.json) verify current counts, six complete responses, 48 per-lead decisions, raw response and request hashes, and retained historical author artifacts. Historical `checksum-checks.json` and skill checks remain historical and were not rewritten as though they originally tested this correction.

## What may still be missed

Eight-result relevance ranking remains a cutoff. English search terminology, indexing lag, unindexed corrections and undisclosed model training sets still limit coverage. The 2025-2026 candidate metadata from Q18/Q19/Q21/Q23 remain unverified scientific leads, not newly read papers. Direct metric-method leads are older, relevant to the pipeline validity question and do not replace recent benchmark coverage already in the fourteen-paper set. This gap audit establishes the search floor and preserves honest limits; it is not an exhaustive-literature or independent-review verdict.


## New method leads screened for T1 scope

Metadata-only triage requested by the parent; no V2 status or experimental result is inferred. MSAT-LDM's abstract concerns watermark training and adaptation across fine-tuned/LoRA backbones, while Residual Transferability concerns residual-transfer forgery and a defense. Neither abstract identifies the work as a regeneration/removal benchmark. A fresh T1 agent should confirm the full evaluation sections before making a final scope exclusion under the every-found rule.

| Exact title | Primary source | Abstract-level scope |
|---|---|---|
| MSAT-LDM: Toward Transferable High-Fidelity Watermarking for Latent Diffusion Model via Modular Self-Augmented Training | https://ojs.aaai.org/index.php/AAAI/article/view/40921 ; DOI https://doi.org/10.1609/aaai.v40i42.40921 ; PDF https://ojs.aaai.org/index.php/AAAI/article/download/40921/44882 | Training-based generative watermarking, internal augmentation, prompt generalization and adaptation. No exact attack-panel claim. |
| Residual Transferability in Neural Image Watermarking | https://arxiv.org/abs/2609.32241 ; PDF https://arxiv.org/pdf/2609.32241 | Residual-transfer forgery/T4, architectural cover dependence, RT metric and CoverLock defense. Full robustness evaluation remains uninspected. |

The source of this triage is the exact OpenAlex Q18/Q21 raw search responses, including their abstract inverted indices and primary-location metadata. This does not add a discovery request, V2 paper, threat or protocol amendment.

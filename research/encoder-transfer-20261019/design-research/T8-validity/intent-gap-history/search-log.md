# T8 Stage1b discovery log

The original author claimed 11 successful substantive queries in four categories. A fresh strict audit found that Q13-Q16 retrieve already named model metadata and repository trees. They are inspections, not discovery searches, and are now excluded. The original records and receipts remain in [query-gap-history](query-gap-history/search-log.md.txt); the correction is not retroactively presented as the original check.

Current total: **23 logged requests: 19 distinct discovery searches and four known-content inspections. Eleven successful substantive discovery queries across three categories (web, OpenAlex and arXiv API) count toward the floor.** Six searches were added for the gap; four count. Q18/Q20 remain conservatively peripheral or adjacent. Q10/Q12 and four ambiguous pooled historical web queries remain excluded.

[Machine query manifest](query-manifest.json), [gap audit](query-gap-audit.md) and [gap receipts/checks](query-gap-checks.json) preserve exact requests, raw response locations and SHA-256 values. Search results are discovery-only; no new V2 paper credit follows from a title, abstract or snippet.

| ID | Category | Exact query / inspection | Counts | Screening outcome |
|---|---|---|---|---|
| T8-Q01 | web | watermark evaluation validity regeneration false positive image public message WAVES benchmark | yes | WAVES primary paper/project |
| T8-Q02 | web | SDXL independent autoencoder original autoencoder architecture trained scratch | no | Lineage lead; primary independently reread, pooled batch not uniquely attributed |
| T8-Q03 | web | VINE watermark W-Bench image quality regeneration evaluation 2025 | yes | VINE primary paper |
| T8-Q04 | web | Watermark Anything native detection threshold mask 0.07 SA1B | yes | Official WAM repository |
| T8-Q05 | web | site.arxiv.org 2025 2026 image watermark UnMarker RAVEN MarkNull removal adaptive | yes | MarkNull/RAVEN/UnMarker primary leads |
| T8-Q06 | web | site.arxiv.org DREW robust watermarking image embedding 2406.02836 | no | No uniquely attributed substantive DREW result in pooled batch; OpenAlex Q11 supplies it |
| T8-Q07 | web | site.github.com diffusers 0.35.1 stable diffusion xl img2img upcast_vae retrieve_timesteps | no | Pooled official latest-source lead, exact pin independently rechecked; not discovery floor |
| T8-Q08 | web | site.pytorch.org reproducibility random seed CUDA determinism independent releases | no | Official reproducibility lead; excluded conservatively from floor |
| T8-Q09 | OpenAlex | watermark regeneration evaluation false positive quality | yes | success |
| T8-Q10 | OpenAlex | SDXL autoencoder trained from scratch | no | success |
| T8-Q11 | OpenAlex | DREW error controlled watermarking provenance | yes | success |
| T8-Q12 | OpenAlex | MarkNull RAVEN watermark removal | no | successful HTTP200, empty result; excluded from floor |
| T8-Q13 | official-model-hub | official SDXL model availability and ancestry | no | Known-content inspection; excluded by fresh correction. |
| T8-Q14 | official-model-hub | official FLUX.1 schnell gate and license | no | Known-content inspection; excluded by fresh correction. |
| T8-Q15 | official-repository | WAM released evaluation and native mask rule file discovery | no | Known-content inspection; excluded by fresh correction. |
| T8-Q16 | official-repository | VINE native inference and model lineage file discovery | no | Known-content inspection; excluded by fresh correction. |
| T8-Q17 | arXiv API | all:watermark AND all:regeneration | yes | success |
| T8-Q18 | OpenAlex | diffusion image watermark training data overlap memorization | no | Memorization/training-use and adjacent watermark leads; discovery only. |
| T8-Q19 | OpenAlex | stable diffusion safety checker false positive bias image | yes | DiffGuard, safety-filter red-teaming and recent image-safety leads. |
| T8-Q20 | OpenAlex | image quality evaluation resizing interpolation LPIPS sensitivity | no | Mostly peripheral; excluded; Q22 supplies direct metric leads. |
| T8-Q21 | OpenAlex | image watermark forgery false attribution detection calibration | yes | Forgery/key selection, residual transferability and one already read source. |
| T8-Q22 | arXiv API | all:LPIPS AND (all:shift OR all:resizing OR all:resampling OR all:robustness) | yes | R-LPIPS, Shift-tolerant metric, E-LPIPS; direct metric-validity leads. |
| T8-Q23 | OpenAlex | diffusion training data memorization duplication dataset overlap | yes | Training-data extraction and recent memorization/dependence leads. |

## Coverage and limits

Historical Q17 surfaced BrushOff, video Erase the Mark, taxonomy 2610.09755v1, LFM and FeatMark. BrushOff has an own V2 card; the others retain the qualifications recorded in the historical log. Fresh Q18-Q23 screen 48 ranked leads covering training dependence, filter selection, perceptual-metric sensitivity and adversarial attribution. Every returned lead has a screening decision in query-manifest.json. None establishes that this cohort overlaps any training set or that any particular safety checker or metric fails here.

Query limits are eight results for new searches and five for the historical APIs. Ranking, indexing, ambiguous terminology and unavailable training histories remain limitations. No new method, baseline, metric, channel or scoring is added from discovery metadata. Existing V02/V25, V30, V39/V65 and V56 already retain the corresponding validity boundaries. The fourteen V2 papers and 68 threats are unchanged.

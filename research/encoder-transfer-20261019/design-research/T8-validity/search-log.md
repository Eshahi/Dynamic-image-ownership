# T8 Stage1b discovery log

Seventeen distinct searches/official discovery requests were attempted. **11 successful substantive queries across four categories** count toward the floor. Q10 is peripheral and Q12 empty despite HTTP200. Four ambiguous/peripheral pooled web queries are conservatively excluded. Errors in an initial shell cache-write attempt and a missing JavaScript base64 helper were storage errors, not successful searches; corrected cache writes are hashed. No API failure is counted as evidence.

[Machine query manifest](query-manifest.json) preserves queries, URLs, result summaries and cache receipts. Primary papers require own method/evaluation cards and do not inherit V2 from discovery.

| Query | Category | Exact query | Counted substantive | Discovery / qualification |
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
| T8-Q13 | official-model-hub | official SDXL model availability and ancestry | yes | success |
| T8-Q14 | official-model-hub | official FLUX.1 schnell gate and license | yes | success |
| T8-Q15 | official-repository | WAM released evaluation and native mask rule file discovery | yes | success |
| T8-Q16 | official-repository | VINE native inference and model lineage file discovery | yes | success |
| T8-Q17 | arXiv API | recent regeneration watermark validity sources | yes | success |

ArXiv Q17 returned BrushOff2610.26682v1 (19October2026), Erase the Mark2610.22457v1 (video/out of image scope), taxonomy2610.09755v1, latent-frequency masking2610.02010v1 and FeatMark2609.30980v1. BrushOff has an own V2 validity card; parent has separately flagged a T1 settings-row gap. The video lead, taxonomy and FeatMark remain discovery-only here. LFM was already read in accepted T1/T4; this T8 package does not count it as an own paper. OpenAlex surfaced Distilling Latent Manifolds2603.14536 as a peripheral Q10 lead, not verified lineage evidence. Primary-only reliance: no search snippet, survey summary or third-party tutorial is cited as a scientific finding.

Coverage remains bounded by top5 API results, web ranking, terminology, indexing delays, access and date. A successful query discovers evidence; it does not establish exhaustive coverage or paper reproducibility. The source manifest records actual inspected versions and checksums.

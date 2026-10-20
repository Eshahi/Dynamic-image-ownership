# T2 §1b search and inspection log

Executed 2026-10-20 UTC. The previous search log is superseded by this expanded log and machine-readable `search-events.jsonl`.

There are 19 query events: 11 unique substantive web queries, 2 OpenAlex queries, 4 official hub/repository queries and 2 failed arXiv API requests. H02/H03 are one corrected owner-discovery intent, so the conservative intent count is 18 overall and 16 successful. This exceeds ten without counting individual file downloads as new searches. Three successful categories are web search, OpenAlex and official repositories/model hubs; arXiv API was executed but failed and is not counted as a successful category.

The eleven web queries were repeated once to preserve raw response artifacts. Re-execution does not increase the unique count. Batched engine responses combine results across queries; event records retain the whole response group instead of inventing a per-result query assignment. Result snippets and abstracts are discovery only. Scientific claims come from the method/evaluation sections in individual cards.

| ID/category | Exact query or endpoint | Outcome and inspection |
|---|---|---|
| W01 / web_search | SDXL autoencoder trained from scratch SD3 16 channel VAE independent — web.run search_query | success; Original SDXL and SD3 method/evaluation cards, not forum speculation. cards/sdxl.md, cards/sd3.md |
| W02 / web_search | Kandinsky 3 MoVQ 270M 1024 inference VRAM paper — web.run search_query | success; Kandinsky primary reports; official model resource/config inspection. cards/kandinsky.md, cards/kandinsky3.md |
| W03 / web_search | SANA DC AE 32 compression 1024 latency 4090 — web.run search_query | success; SANA/DC-AE/Sprint primary methods, benchmarks and native source. cards/sana.md, cards/dcae.md, cards/sprint.md |
| W04 / web_search | site.arxiv.org "Qwen-Image" "Wan" "VAE" — web.run search_query | success; Qwen frozen encoder/decoder-only training, Wan causal AE and successor caveat. cards/qwen.md, cards/wan.md, cards/qwen-vae2.md |
| W05 / web_search | site.github.com black-forest-labs FLUX.2 autoencoder 32 latent channels — web.run search_query | success; Official FLUX2 autoencoder code/config; Lens explicit reuse. cards/flux.md, cards/lens.md |
| W06 / web_search | site.huggingface.co "PRX Pixel" — web.run search_query | success; Official modelcard and pinned Diffusers source; quantitative evaluation missing. cards/prxpixel.md |
| W07 / web_search | site.arxiv.org pixel diffusion 2026 "LENS" "Kandinsky" — web.run search_query | success; Primary reports inspected directly; broad web result noisy, not an absence proof. cards/lens.md, cards/kandinsky5.md |
| W08 / web_search | site.huggingface.co "AuraFlow-v0.3" "VAE" — web.run search_query | success; Official card/config/hash; no sufficient quantitative evaluation. cards/auraflow.md |
| W09 / web_search | site.github.com "Lumina-Image-2.0" "vae" — web.run search_query | success; Primary paper and official README/config; FLUX reuse. cards/lumina.md |
| W10 / web_search | site.arxiv.org "pixel" "diffusion" "2026" "image generation" — web.run search_query | success; Primary methods/evaluations; PixARG remains uninspected lead. cards/pixelgen.md, cards/pixsgr.md, cards/hidream-o1.md |
| W11 / web_search | site.huggingface.co "HiDream-I1-Full" "VRAM" — web.run search_query | success; Primary papers and official source; third-party VRAM reports excluded. cards/hidream.md, cards/hidream-o1.md |
| A01 / arxiv_api | all:autoencoder AND all:diffusion, latest submitted, top10 — https://export.arxiv.org/api/query?search_query=all%3Aautoencoder%20AND%20all%3Adiffusion&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending | failed; 429 response; switched to arXiv HTML found through web/official papers. Failure is not successful search coverage.  |
| A02 / arxiv_api | ti:Qwen-Image OR ti:Lumina OR ti:HiDream, top15 — https://export.arxiv.org/api/query?search_query=ti%3A%22Qwen-Image%22%20OR%20ti%3A%22Lumina%22%20OR%20ti%3A%22HiDream%22&start=0&max_results=15 | failed; Timed out; switched to primary paper HTML and official repositories.  |
| O01 / openalex | pixel space diffusion image generation — https://api.openalex.org/works?search=pixel%20space%20diffusion%20image%20generation&per-page=10 | success; Metadata discovery only. Returned Edify, Latent Forcing, WiT, PixelDiT, Pixel-Space Diffusion Transformers, HiDiT and related work. No abstract-only evidence promoted to V2.  |
| O02 / openalex | deep compression autoencoder image generation — https://api.openalex.org/works?search=deep%20compression%20autoencoder%20image%20generation&per-page=10 | success; Broad results included generic compression/TC-AE; inspected primary DC-AE through official trail. No negative completeness inference. cards/dcae.md |
| H01 / official_repository_model_hub | HuggingFace models search PixelGen, limit20 — https://huggingface.co/api/models?search=PixelGen&limit=20 | success; Seven results; only paper-author zehongma/PixelGen used as official. Community mirrors excluded from support claim. cards/pixelgen.md |
| H02 / official_repository_model_hub | HuggingFace models search Lens author LensAI, limit20 — https://huggingface.co/api/models?search=Lens&author=LensAI&limit=20 | success; Empty wrong-owner query; corrected to Microsoft using primary-paper/repository links. cards/lens.md |
| H03 / official_repository_model_hub | HuggingFace models author microsoft search Lens, limit30 — https://huggingface.co/api/models?author=microsoft&search=Lens&limit=30 | success; Corrected owner search empty; direct advertised model API401. Do not infer model nonexistent. cards/lens.md |
| H04 / official_repository_model_hub | GitHub repository search PixSGR — https://api.github.com/search/repositories?q=PixSGR | success; Two repositories; paper links identify CVL-UESTC/PixSGR. Its HF release is empty, not gated. cards/pixsgr.md |


## Retrieval failures and alternatives

Raw GitHub downloads repeatedly failed with TLS EOF; GitHub contents API later returned403. Pinned GitHub blob pages exposed embedded rawLines, decoded as text without executing code. Each successful fallback has URL, original-response SHA and derived-text SHA in the receipt manifest. arXiv API429/timeout did not block primary full-text HTML inspection. Lens model401, empty PixSGR weights, gated FLUX/SD3 and a missing paper benchmark are different availability classes and are not conflated.

Official model API snapshots were used for exact revision, actual `gated` state, declared license, component sizes and advertised LFS SHA. They are model-release audits, not extra substantive discovery queries. Unknown initialization stays unknown even where config and weights are available.

## Search stopping rationale

All named brief families and newer pixel/high-compression directions are represented. Eighteen conservative families have their own inspected paper card. Additional models with only metadata or a short card remain nonqualifying. Search was stopped after method/evaluation and operational distinctions were resolved for the major requested families, not on reaching fifteen names. This is a bounded landscape, not a claim to enumerate every October2026 model.

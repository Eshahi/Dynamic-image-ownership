# Final-study search register

Date: 2026-10-25 UTC. Engine: web.run unless specified. Queries discover sources; only personally opened methods and experiments can support substantive claims. Cluster logs contain the delegated searches and are part of this register: [attacks](attacks/search-log.md), [watermarks](watermarks/search-log.md), [encoders](encoders/search-log.md), [transfer theory](transfer-theory/search-log.md).

## Root searches during desktop continuation

| ID | Exact query | Useful hits and handling |
|---|---|---|
| R01 | `"watermark" "autoencoder" "transfer" diffusion regeneration` | Candidate rank-ratio paper and existing watermark papers; primary verification required. |
| R02 | `"encoder" "watermark" "regeneration" 2026` | Recent latent watermark and removal candidates; no snippet-based comparison. |
| R03 | `"latent" "watermark removal" "alignment"` | MarkNull arXiv:2608.10166, delegated for primary inspection. |
| R04 | `"diffusion" "watermark" "transferability" encoder` | Jeon et al. arXiv:2609.24377; OpenReview workshop PDF; aggregator-only DiffMark/BiSLW leads delegated, not accepted as evidence. |
| R05 | `"A Rank-Ratio Bound for Pixel-Space Signal Fragility" arxiv` | ResearchGate record; primary-publisher/author verification needed. |
| R06 | `"INSIGHTS INTO LATENT DIFFUSION MODELS" watermark transferability` | OpenReview workshop manuscript; browser verification wall. |
| R07 | `"watermark" "cross-autoencoder" 2025 2026` | No result used to assert absence; search coverage only. |
| R08 | `"A Rank-Ratio Bound for Pixel-Space Signal Fragility" site:ieeexplore.ieee.org` | No accessible publisher result; follow DOI and author repository. |
| R09 | `"10.1109/ACCESS.2026.3717412"` | ResearchGate author-version excerpt; DOI not yet verified. |
| R10 | `"watermark transferability" "ICLR 2025" latent` | Author-hosted RadioactiveDiffusion PDF and ICLR transfer-attack paper. |
| R11 | `"vae-watermark-fragility" "rank"` | Author repository; submission metadata differs from ResearchGate publication display. |
| R12 | `"3717412" IEEE Access` | No accessible primary publisher confirmation; irrelevant number matches discarded. |
| R13 | `"Rank-Ratio Bound" watermark` | Same manuscript and repository; identity remains unresolved. |

Direct opens: four retained transfer-theory primary PDFs; Jeon v1 HTML and abstract; OpenReview hashed workshop PDF (verification wall), then author-hosted RadioactiveDiffusion. Direct source and cache locators are in cards/manifests. Negative or incomplete searches do not establish novelty.

## Retained work verification

Desktop root re-opened PhotoGuard §3 and Table 1, Demontis §4 and §5.1.1, Tramèr §§3.1–3.2/Table 3, Ilyas §3 and Table 1. The four paper-cache SHA256 values exactly match the earlier CLI manifest. Those cards are preserved, with prior full-section inspection attributed to the earlier CLI root; this continuation does not pretend they were newly discovered.

## Consolidated delegated/retained log: attacks

# Attack-literature search log

All searches and reads below occurred on 2026-10-25 UTC. Paper text is cached outside Git; see `source-manifest.json`. Search hits alone are not evidence. The legacy arXiv full-text extracts were moved, with matching pre/post SHA-256, into `legacy-cli/attacks/` under the paper cache.

| Engine | Query or direct retrieval | Useful primary source / action |
|---|---|---|
| Web search | `arxiv provable removability of image watermarks diffusion regeneration paper` | Zhao et al., arXiv:2306.01953v3; opened §§2–5 and Appendix E. |
| Web search | `DiffPure Diffusion Models for Adversarial Purification experiments arxiv` | Nie et al., arXiv:2205.07460v1; opened §§3,5 and ablations. |
| Web search | `W-Bench benchmark watermark attacks VINE paper` | Lu et al., arXiv:2410.18775v2 / ICLR 2025; inspected cached §§3–4. |
| Web search | `multi pass rinsing watermark diffusion removal paper` | An et al., arXiv:2401.08573v3 / ICML 2024; inspected cached §§3–4. |
| Direct arXiv HTML | `2306.01953`, `2205.07460`, `2608.10166` | Saved official HTML for Zhao, DiffPure and MarkNull; inspected methods and experiments. |
| Direct cached primary full text | `2410.05470v2`, `2405.08363v2`, `2610.02010v1`, `2601.16473v1`, `2609.08213v1`, `2504.20111v1` | Inspected CtrlRegen, UnMarker, LFM, DeMark, DRIFT and single-image attack sections; the first three receive V2 cards in this package. |

Search scope is bounded to the queries above and the cached papers. No absence-of-prior-work claim follows from it.

## Consolidated delegated/retained log: watermarks

# WP1 watermark search and inspection log

Date: 2026-10-25 UTC. Search service: live web search; primary full texts: arXiv HTML. Search requests were grouped for efficiency; exact per-query wall-clock timestamps were not preserved. All listed queries were executed during this subtask. Cached papers are outside the repository under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/watermarks/`. HTML-to-reading-text copies are conveniences; HTML hashes identify sources.

## Executed queries

| Order | Exact query | Disposition |
|---|---|---|
| 1 | `Tree Ring Gaussian Shading ZoDiac Stable Signature watermark arxiv` | Located primary initial-noise, decoder-training and latent-optimization papers. |
| 2 | `ROBIN WIND RingID diffusion watermark arxiv` | Primary IDs 2411.03862, 2412.04653, 2404.14055. |
| 3 | `ZoDiac watermark diffusion arxiv 2024` | Confirmed 2401.04247; full-text title differs from earlier shorthand title. |
| 4 | `Hidden in the Noise Two Stage Robust Watermarking Images WIND 2412.04653` | Confirmed WIND primary full text/proceedings. |
| 5 | `latent diffusion watermark encoder transfer VAE SDXL 2025 2026` | Located WMAdapter and newer leads; separated deployment transfer from attack transfer. |
| 6 | `"WMAdapter" watermark VAE zero-shot transfer arxiv` | Inspected Appendix A.4; only stated zero-shot pair is SD2.1→SD1.5. |
| 7 | `"Guidance Watermarking for Diffusion Models" arxiv` | Inspected 2509.22126v2, methods/experiments/Appendix C. |
| 8 | `"watermark" "encoder" "transfer" "SDXL" arxiv` | Additional coverage; no absence or first-ever conclusion. |

## Full-text inspections

`source-manifest.json` records exact versions, dates, URLs, artifacts, SHA-256 and section/table locators for twelve V2 primary sources. All numbered cards derive from opened method and experiment passages, not snippets. Stable Signature's guessed v4 URL returned 404; v2 is the verified artifact. OpenReview's WMAdapter PDF `https://openreview.net/pdf?id=HAD6iZxKuh` encountered an access challenge; primary arXiv v1 was used instead. Unversioned arXiv download requests were resolved using the version/date printed within each cached HTML; canonical manifest URLs pin those versions.

The earlier interrupted worker's ten complete `.txt` full texts were moved with native PowerShell from this owned folder into the authorized external `papers/legacy-cli/watermarks/` cache. `legacy-cache-manifest.json` preserves original→cache paths and SHA-256. They did not count as V2 by mere existence. The newer inspected primary HTML is the principal V2 artifact. FreqMark's legacy text was preserved but not elevated to V2 or used for claims in this dossier.

## Lower-verification recent leads — excluded from V2 evidence

| Lead | Located record | Status and limit |
|---|---|---|
| GhostVAE | https://www.usenix.org/conference/usenixsecurity26/presentation/liu-jinyuan | V1 metadata lead; encoder-backdoor relevance; no method/experiment inspection here. |
| GROW | https://github.com/luopengchen/GROW | V1 primary project/README lead; CVPR2026 association observed; paper not inspected. |
| Latent Seal | DOI 10.1007/s11633-025-1620-y | Lower-verification press/metadata lead dated June 2026; no primary full-text inspection. |
| TraceMark-LDM | ScienceDirect search result dated June 2026 | V1 abstract/metadata only; excluded from claims and bibliography. |
| Semantic-aware attention-guided digital watermarking | https://www.sciencedirect.com/science/article/pii/S0923596526001955 ; DOI 10.1016/j.image.2026.117672 | V1 abstract/metadata only; not inspected. |
| DiffMark / “Transferable Multi-Bit Watermarking Across Frozen Diffusion Models via Latent Consistency Bridges” | Parent-supplied aggregator lead | V0; no verified primary source in this subtask. |
| BiSLW / “Bi-Spectral Latent Watermarking for Generative Diffusion Models” | Parent-supplied aggregator lead | V0; no verified primary source in this subtask. |

Only permitted paper HTML was downloaded; no code repositories, model weights, images or datasets were downloaded. No claims are made from the lower-verification leads. DOI/publication metadata not independently checked is null or explicitly unnormalized in the manifest.


## Consolidated delegated/retained log: encoders

# Encoder work-package search log

Date: 2026-10-25 UTC. Engine: web search/open on primary arXiv, official Hugging Face model cards and Diffusers documentation/source. Queries and inspected hits:

| Query / action | Useful primary hits |
|---|---|
| Open arXiv HTML 2112.10752v2, 2307.01952v1, 2403.03206v1; find `3.1 Perceptual Image Compression`, `Table 8`, `2.4 Improved Autoencoder`, `Table 3`, `5.2.1 Improved Autoencoders` | LDM first-stage method/zoo; SDXL fresh AE and SD2 decoder lineage; SD3 16-channel ablation. |
| Open arXiv HTML 2410.10629v1, 2410.10733v1, 2306.00637v2, 2410.21061v1, 2209.09002v1; find method/experiment sections | Sana and DC-AE; Würstchen; Kandinsky 3 and original MoVQ (not same checkpoint). |
| `site:huggingface.co/stabilityai/stable-cascade model card license img2img stage a effnet`; `site:huggingface.co/black-forest-labs/FLUX.1-schnell license gated access model card autoencoder`; `site:huggingface.co/stabilityai/stable-diffusion-3.5-medium license gated img2img`; `site:huggingface.co/Efficient-Large-Model/Sana_600M_1024px license pipeline img2img` | Official checkpoint cards and repo trees. FLUX page explicitly gated. |
| `site:huggingface.co/docs/diffusers StableDiffusion3Img2ImgPipeline strength FlowMatchEulerDiscreteScheduler`; `... FluxImg2ImgPipeline strength ...`; `... SanaImg2ImgPipeline strength`; `... StableCascade img2img pipeline strength` | Diffusers docs; initial search insufficient for SD3/Sana/Cascade contracts. |
| Open arXiv 2312.03511v1 and v3; find `3.4 Sber-MoVQGAN`, `6 Human evaluation` | Kandinsky 3 technical report v3, separately trained Sber codec, Table 2. |
| Find `pretrain`, `initializ` in DC-AE; `pre-trained` in Sana; `scratch` in SD3; `pretrained` in Würstchen | No explicit final SD3/DC-AE/Sana checkpoint weight-initialization proof found in these paper sections. This is not a proof of independence or dependence. |
| `site:huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 license openrail++ model card`; `site:huggingface.co/kandinsky-community/kandinsky-3 license model card`; `site:huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main gated files size`; `site:huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/stable_diffusion_3 StableDiffusion3Img2ImgPipeline` | SDXL/Kandinsky license cards and repo sizes. |
| `site:huggingface.co/docs/diffusers "StableDiffusion3Img2ImgPipeline" "strength"`; same for `SanaImg2ImgPipeline`, `Kandinsky3Img2ImgPipeline`, `StableCascadeImg2Img` | Kandinsky confirmed; no standard Sana/Cascade strength pipeline found. |
| `"StableDiffusion3Img2ImgPipeline" diffusers Hugging Face`; `"SanaImg2ImgPipeline" diffusers GitHub`; `"StableCascade" "img2img" "strength" diffusers` | Official Diffusers SD3 img2img source and auto-pipeline map; Sana/Cascade no comparable contract found in these searches. |
| `site:github.com/black-forest-labs/flux ae.py autoencoder FLUX trained from scratch VAE`; `FLUX.1 autoencoder trained from scratch provenance paper model card`; `site:arxiv.org FLUX.1 schnell autoencoder training paper` | Found BFL's 2025 FLUX.1 Kontext paper. Opened arXiv HTML 2506.15742v2, §2/Table 1 and Appendix B. Explicit from-scratch FLUX.1 AE statement; 4096-image reconstruction evaluation. Same released schnell AE file identity still unverified. |
| Open BFL official `flux/src/flux/util.py`; find `flux-schnell`, `ae.safetensors`, `z_channels` | Official inference mapping gives schnell AE file name, 16 channels, scale 0.3611, shift 0.1159. This is config evidence, not a checkpoint hash or training ledger. |
| `site:huggingface.co/stabilityai/stable-diffusion-3.5-medium vae config latent_channels 16 scaling_factor`; `stable diffusion 3.5 medium VAE pretrained from scratch official source`; `site:github.com/Stability-AI/sd3.5 VAE model architecture training` | Official SD3.5 card and Stability AI inference repository found; no explicit AE weight-initialization proof in inspected hits. Third-party mirrors were excluded as evidence. WP4 to audit exact official checkpoint/config/access. |

Absence statements are limited to these searches and the pages inspected on this date. All cited model access/size facts should be rechecked when WP4 freezes the server plan.

## Consolidated delegated/retained log: transfer-theory

# Transfer theory and evaluation searches

All times/dates UTC. Engine: `web.run` unless specified. Queries are discovery; only opened primary texts support claims. Existing project cards are locators only.

| ID | Date | Exact query | Useful hits / disposition |
|---|---|---|---|
| TT01 | 2026-10-25 | adversarial example transferability gradient alignment Demontis Why Do Adversarial Attacks Transfer 2019 | USENIX Security 2019 primary landing page and paper |
| TT02 | 2026-10-25 | Tramer Space of Transferable Adversarial Examples dimensionality 2017 | arXiv:1704.03453; v2 PDF opened |
| TT03 | 2026-10-25 | Ilyas adversarial examples are not bugs they are features 2019 paper | NeurIPS 2019 proceedings PDF; author discussion and counterexample discovered |
| TT04 | 2026-10-25 | PhotoGuard raising the cost malicious AI powered image editing encoder attack diffusion 2023 | ICML 2023 PMLR 202 PDF opened; arXiv:2302.06588 |

Direct opens: USENIX Demontis page then PDF link; arXiv:1704.03453 PDF; NeurIPS final Ilyas paper; PMLR final PhotoGuard paper. No conclusions inferred from search-result snippets.

## WP2 source-text retrievals and analytical use (2026-10-25 13:57–14:09 UTC)

- Direct-opened the pinned diffusers v0.35.1 DDIM scheduler, DDPM scheduler and Stable Diffusion img2img pipeline as web text; inspected beta construction, leading timestep spacing/offset and strength slicing. URLs: https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py ; https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddpm.py ; https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py . No code downloaded or executed. Local frozen source selects scaled_linear for R0/R1 and squaredcos_cap_v2 for R3.
- Theory contributor personally inspected DDIM https://arxiv.org/html/2010.02502v4, DiffPure https://arxiv.org/html/2205.07460v1, and the previously carded Zhao, PhotoGuard and Demontis sources; exact section/equation locators are in analysis/theory-design.md. These supply conditional mathematical structure, not observed F5 derivatives.
- No new paper result was substituted for a missing mechanistic measurement. Current journals support continuous-score and source-cluster analysis, not encoder gains or full-chain transport fitting.

## WP3–WP4 source checks (2026-10-25 14:12–14:39 UTC)

- WP3 direct opens: MarkNull v1 §§5–6 and Appendix B.1, and diffusers v0.35.1 DDIMInverseScheduler. No search query. Exact source links and analytical counterexamples are in 05-informed-attacks.md and analysis/marknull-assumption-check.md.
- WP4 search, web tool: `site.stability.ai stable diffusion 3.5 medium 2.5 billion 9.9 GB`. Used the opened official Stability announcement to correct the model size and the qualification that 9.9 GB excludes text encoders; no secondary result was relied on.
- WP4 direct opens: official HF cards, revision metadata and component listings; pinned v0.35.1 Flux, SD3, Kandinsky3, Sana-Sprint and Cascade source; FlowMatchEuler and SCM scheduler source; BFL Kontext, DC-AE and Sana-Sprint method/experiment sections. Full successful/failed-access logs are in analysis/flux-feasibility.md and analysis/third-family-alternatives.md. Root independently inspected Flux step slicing and FlowMatchEuler interpolation/shifting. These were text reads, not downloaded or executed code.
- New bounded V2 mini-card: Sana-Sprint arXiv:2503.09641v1, in analysis/third-family-alternatives.md. Native Sprint img2img is verified; ordinary Sana support and exact released AE initialization are not inferred from it. FLUX's gated scheduler remains inaccessible, so all numerical shifted-grid examples are explicitly conditional.

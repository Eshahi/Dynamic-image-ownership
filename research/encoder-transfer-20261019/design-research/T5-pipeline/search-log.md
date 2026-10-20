# T5 Stage1b search log

Executed2026-10-20. **16 distinct substantive discovery queries across3 successful categories**: web8, OpenAlex4, official model Hub search4. Direct pinned-file retrievals, retries and repeated web queries are not new discovery queries. Raw web responses were preserved by reissuing the same8 queries; counts remain16. All API/tool receipts are under the authorized MAIN cache/T5-1b, never a secondary worktree cache.

| ID | Category | Exact discovery query | Screening and coverage | Raw receipt |
|---|---|---|---|---|
| T5-Q01 | web | diffusers 0.35.1 SDXL img2img force_upcast prepare_latents | Upcast and img2img API discovery; floating docs/community examples resolved to official v0.35.1 code. | `web-search-batch-0.json` |
| T5-Q02 | web | Kandinsky 3 img2img movq force_not_quantize strength | Official docs/report led to actual MoVQ call-chain inspection; generic posterior helper rejected as executed path. | `web-search-batch-0.json` |
| T5-Q03 | web | VINE watermark official SD Turbo residual inference | Author release located; paper/release model-family disagreement retained. | `web-search-batch-0.json` |
| T5-Q04 | web | TrustMark Q BCH 5 decode watermark payload | Official Adobe CONFIG/JS/Python leads; pin Python and inspect ECC code, not snippets. | `web-search-batch-0.json` |
| T5-Q05 | web | site:openaccess.thecvf.com ICCV 2025 TrustMark Robust Watermarking Watermark Removal Arbitrary Resolution | Final ICCV2025 paper located and methods/evaluation reread. | `web-search-batch-1.json` |
| T5-Q06 | web | site:github.com facebookresearch watermark-anything interpolation antialias inference | Official WAM implementation/related release leads; exact selected commit governs. | `web-search-batch-1.json` |
| T5-Q07 | web | site:huggingface.co Shilin-LU VINE-R-Enc | Targeted author Hub query resolves noisy broad VINE-R Hub results. | `web-search-batch-1.json` |
| T5-Q08 | web | diffusers 0.35.1 deterministic algorithms DDPM step noise t greater zero | Noise/scheduler leads mostly broad or off-version; actual pinned DDPM code decides. | `web-search-batch-1.json` |
| T5-Q09 | OpenAlex | SDXL latent diffusion autoencoder | Retrieved autoencoder/compression literature including DC-AE leads; selected LDM/SDXL primary methods remain audited basis. | `openalex-0.json` |
| T5-Q10 | OpenAlex | VINE robust image watermark regeneration | Retrieved newer regeneration/removal leads including Diffusion-Based Image Editing for Breaking Robust Watermarks and Vanishing Watermarks; leads only, not performance evidence here. | `openalex-1.json` |
| T5-Q11 | OpenAlex | Watermark Anything localized message decoding | Retrieved localized-message/related-watermark leads; no uninspected secondary metrics imported. | `openalex-2.json` |
| T5-Q12 | OpenAlex | TrustMark robust image watermarking | Retrieved final ICCV2025 TrustMark and arxiv predecessor; final paper independently reread. | `openalex-3.json` |
| T5-Q13 | official model hub search | stable-diffusion-xl-base-1.0 | Official SDXL alongside fp16-fix/other mirrors; only pinned official base adopted. | `hub-search-4.json` |
| T5-Q14 | official model hub search | kandinsky-3 | Official community KD3 and ai-forever variants; no silent3.1/5 replacement. | `hub-search-5.json` |
| T5-Q15 | official model hub search | VINE-R | Fuzzy unrelated VINE-R hits; low-precision search acknowledged, targeted author web query resolves. | `hub-search-6.json` |
| T5-Q16 | official model hub search | trustmark | Unofficial TrustMark mirrors only; retain official Adobe code/CDN, not mirror availability as provenance. | `hub-search-7.json` |

## Retrieval and evidence rules

`search-events.jsonl` preserves successful query receipts and every recorded retrieval attempt, including raw.githubusercontent TLS failures, transient API failures, nonexistent paths and successful official GitHub contents-API retries. Failed requests do not count as successful categories. GitHub API responses were decoded as text only; no third-party source was imported or executed. Reused source bytes were independently inspected with their original pinned URL and SHA-256 preserved.

Search snippets, search-result ranks, secondary tutorials, floating current docs and Hub model names are leads only. Exact frozen implementation claims use diffusers0.35.1, torchvision0.22.1, PyTorch2.7.1 and official repository commits/config revisions. Final papers are separately reread to V2; claims about evaluation do not come from implementation files or abstracts.

## Coverage

| Domain | Discovery coverage | Decisive inspected evidence |
|---|---|---|
| SD1.5/SDXL / schedules / VAE precision | Web runtime queries, OpenAlex AE search, official SDXL Hub search | Pipeline/scheduler/AE/image-processor source, immutable model configs; LDM/SDXL V2 cards |
| Kandinsky3 / MoVQ | Web MoVQ/strength and official KD3 Hub search | Actual call chain plus VQModel, scheduler/config; report method/evaluation |
| WAM localized messages | Web official-code query and scholarly localized-message search | Native config, transforms, JND, raw-logit aggregation, checkpoint identity; paper§3/§5 |
| VINE released residual pipeline | Web release and targeted author Hub, OpenAlex regeneration, broad Hub | Author code/pinned models/SD-Turbo dependency; paper method/evaluation discrepancy |
| TrustMark Q / ECC / revision differences | Web ECC/final-paper, OpenAlex and Hub | Pinned Python245 decode, BCH61 schema, Adobe CDN config; final ICCV paper |

## what we might still have missed

Breadth is not exhaustive: source compatibility and model tensor metadata still need authorized setup validation; public CDN bytes may change; unknown training-data overlap is not excluded by independent AE training. Fuzzy Hub search missed VINE's author handle and supplied unofficial TrustMark mirrors, corrected by targeted primary-source resolution. Newer OpenAlex regeneration papers are leads for attack-literature review, not silently treated as evidence for this frozen pipeline. No actual server memory/timing, model smoke, watermark scores or held-out pixels are in this research package.

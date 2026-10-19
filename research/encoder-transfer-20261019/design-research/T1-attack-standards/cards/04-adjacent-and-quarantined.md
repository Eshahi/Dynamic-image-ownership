# Adjacent 2025 work and evidence exclusions

## Competition winner

Extends [existing card](../../../../q1-dossier-20261018/02-literature/C2-removal/cards/shamshad2025challenge.md). [2508.21072v1](https://arxiv.org/html/2508.21072v1), §§3.1–3.3, Tables 1–4, Figure 6. Beige-box attack trains/optimizes VAEs using opposite-payload pairs; black-box attack uses img2img and per-cluster settings. Figure 6 specifies ChatGPT-generated caption conditioning, guidance 1 and T=500 steps. Training set: 1,000 prompts, SD2.1 images 512² resized to 400² for StegaStamp. Test-time VAE optimization and color transfer also change the attack. The headline 95.7% removal is a competition endpoint, not fixed-FPR SDXL transfer. It supports analyzing encoder adaptation as a separate costed threat. Commercial caption generation is not authorized here.

## SemanticRegen

New focused V2 card: [2505.08234v1](https://arxiv.org/html/2505.08234v1), §§3.1–3.4 and §4/Tables 1–3. VQA captions plus segmentation preserve selected foreground and repaint background using SD-v2 inpainting, 50 steps; MiniChat-MA summarizes captions. Table 3 describes 1,000 prompts. §4.1 reports mean Tree-Ring p-value .10 and mSSIM .95. A mean p-value is not an evasion fraction; masked SSIM excludes altered regions and is not whole-image SSIM. Reported table references/quality summaries are inconsistent in prose. No aggregate superiority claim is adopted. This is semantic editing with partial reconstruction, beyond the same-content regeneration core.

## Ni et al.: retain quarantine

[2510.05978v1](https://arxiv.org/html/2510.05978v1) was re-opened (method §4 and evaluation §6) and checked against the [existing quarantine](../../../../q1-dossier-20261018/14-forward-citation-sweep/drew-trustmark/cards/Ni2025BreakingWatermarks.md). The guided optimization direction and reported summary/table numbers conflict. Do not use its numbers to choose settings, rank attacks or support impossibility. It counts as inspected coverage, not trustworthy positive evidence.

## Coverage boundary

The official NeurIPS 2025 competition-report landing page was found, but its final fulltext was not independently inspected in T1. The winner's V2 paper and prior dossier cover the attack mechanism; no aggregate competition statistic from an abstract is used. NFPA/Imprint/NoisePrints remain primary leads, not new V2 entries. Generic visible-watermark removal, audio/LLM watermarking, benign JPEG/crop sweeps and image-to-video are outside this T3 study's execution scope. Their exclusion is explicit, not evidence of robustness.

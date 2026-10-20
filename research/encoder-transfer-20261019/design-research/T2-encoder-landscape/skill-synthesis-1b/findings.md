# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- ldm-method: KL-regularized convolutional perceptual autoencoder with adversarial/perceptual reconstruction; latent C=4, spatial f=8 in SD1.5 (1024→128²×4). Cross-attention U-Net diffusion. LDM also studies VQ and other compression factors; these are not all SD1.5 configurations. [ldm; supporting; direct-evidence; confidence high]. Limitations: Generation/reconstruction metrics do not evaluate watermark survival. Official SD2 metadata endpoint was inaccessible; no new SD2 revision or gate status is invented.

- ldm-evaluation: Fig.7 compares f=1,2,4,8,16,32, 5K samples,500K CelebA-HQ or2M ImageNet updates, A100 and DDIM step sweeps; f4/8 balances speed and quality. Official decoder-ft card: COCO2017-val5K at256, original PSNR23.4±3.8dB/SSIM.69/rFID4.99 versus ft-MSE24.5±3.7/.71/4.70. Its PSIM column is not our LPIPS assessor. [ldm; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sdxl-method: KL AutoencoderKL,C=4,f=8; same architecture class as SD1, separately trained. SDXL U-Net≈2.6B, dual CLIP conditioning; native1024. Optional refiner excluded from core. [sdxl; supporting; direct-evidence; confidence high]. Limitations: Reconstruction at256 does not predict1024 survival. From-scratch training is an author statement, not independent initialization forensics.

- sdxl-evaluation: Table3 COCO2017-val256: SDXL PSNR24.7/SSIM.73/LPIPS.88/rFID4.4; SD1 23.4/.69/.96/5.0; SD2 24.5/.71/.92/4.7. Preserve paper metric convention rather than treating these LPIPS values as the thesis assessor. Generation preferences can include refiner and cannot be assigned to base-only img2img. [sdxl; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sd3-method: MMDiT rectified flow, KL VAE C=16/f=8 with latent scale/shift. SD3.5 grouped withSD3; model size/version is not a fresh AE family. [sd3; supporting; direct-evidence; confidence high]. Limitations: SD3Medium noncommercial research terms; SD3.5 Community terms differ. Both API snapshots auto-gated. Public text does not authorize gated weights.

- sd3-evaluation: Table3 C16 VAE PSNR28.62/SSIM.86/FID1.06 versus C4 25.12/.75/2.41; dataset/resolution not clear in inspected caption, so do not assign COCO/1024. Generator-quality gains do not establish encoder-transfer survival. [sd3; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky-method: Image-embedding prior, diffusion decoder and MoVQ,C=4/f=8. Kandinsky3 enlarges MoVQ; Kandinsky5 images use FLUX.1-dev VAE, so the brand is not a persistent encoder lineage. [kandinsky; supporting; direct-evidence; confidence high]. Limitations: KD2.2 native resolution lower than1024; KD3 better1024 proposal. Fix quantization mode explicitly. Independence conclusion does not extend toKandinsky5.

- kandinsky-evaluation: §5 COCO30K256: linear-prior FID8.03; diffusion-prior quantized9.86 versus unquantized9.87. Human DrawBench5,000 votes. These are generation, not native1024 regeneration/watermark metrics. [kandinsky; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sana-method: DC-AE continuous nonvariational C32/f32 (1024→32²×32), residual shortcuts and linear-attention DiT, Gemma2-2B. Sprint is distilled, not another family. [sana; supporting; direct-evidence; confidence high]. Limitations: Apache ungated packages; upstreamGemma terms/access remain separate. Packaged weights do not erase upstream terms. Optimized headlines do not establish frozen-stack24GB throughput.

- sana-evaluation: GenEval533 prompts as paper states, DPG1,065,MJHQ30K. Table5 quantization CLIP28.5→28.3 and ImageReward1.03→.96 on statedMJHQ/first1K subsets. DC-AE supplies reconstruction evidence; Sprint few-step gains do not validate equal corruption. [sana; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixartsigma-method: 0.6B DiT/T5, KL VAE C4/f8. α uses pretrained LDM VAE; Σ explicitly replaces with SDXL VAE and adapts denoiser2K updates. α paper does not establish exactSD1.5 versusSD2 checkpoint. [pixartsigma; supporting; direct-evidence; confidence high]. Limitations: Ungated OpenRAIL++ packages, not Apache/MIT permissiveness. Private evaluation/evaluator differences prevent direct score ranking.

- pixartsigma-evaluation: Σ evaluates30K curated high-quality examples and300-caption human/GPT4V preference subset. α COCO30K FID7.32. α753 A100GPU-days partly converts V100 by2.2×; training estimate, not inference cost. [pixartsigma; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- playground-method: SDXL-like U-Net with EDM and balanced resolution buckets; C4/f8 SDXL VAE. [playground; supporting; direct-evidence; confidence high]. Limitations: Custom Playground Community license, ungated. AdvertisedVAE hash is metadata evidence, not locally verified weights.

- playground-evaluation: MJHQ30K1024 FID4.48 versusSDXL+refiner9.55; private1K-prompt aesthetic preference4.8×ratio. Settings mix model/sampler/training differences, not AE isolation. [playground; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hunyuan-method: ≈1.5B transformer with bilingualCLIP/T5; C4/f8 VAE explicitly fromSDXL. [hunyuan; supporting; direct-evidence; confidence high]. Limitations: Tencent custom terms, ungated hub; availability is not permissiveness. Native strength wrapper not verified.

- hunyuan-evaluation: §4 >3,000 prompts,>50 professional raters,four dimensions,30–50 prompts/subcategory. Smaller.7B ablations COCO30K256. Do not assign those conditions to1024 full-model reconstruction/survival. [hunyuan; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- qwen-method: 20B MMDiT/Qwen2.5VL, Wan2.1 VAE C16/spatial8/temporal4. Image encoder frozen, decoder fine-tuned. Qwen2.1 instead RGBA4 input/output,z64,spatial16/temporal8; no inheritedWan assumption. [qwen; supporting; direct-evidence; confidence high]. Limitations: Qwen-Image/2512 are Apache and ungated. Qwen2.1 uses ungated Qwen Research terms, not Apache. The original paper cannot establish successor initialization.

- qwen-evaluation: Table2 ImageNet-val256FP32 PSNR33.42/SSIM.9159 versusWan31.29/.887; in-house text-rich25636.63/.9839 versus26.77/.9386. Effective image encoder19M/decoder25M. Decoder improvement does not prove new encoder. [qwen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- zimage-method: 6B single-stream S3-DiT with Qwen3-4B conditioning; frozen FLUX1 VAE, C=16/f=8. Turbo uses 8 NFE. [zimage; supporting; direct-evidence; confidence high]. Limitations: Apache2 and ungated model package. Published object hashes are metadata evidence; no weights or outcomes were generated.

- zimage-evaluation: Table9 reports GenEval .84 for base and .82 for Turbo. Speed depends on NFE and specialized optimization; quality scores do not isolate the encoder. Prompt rewriting and distillation can affect outcomes. [zimage; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- lumina-method: 2.6B UnifiedNextDiT with Gemma2-2B and FLUX VAE, C=16/f=8. Progressive multiresolution training, RoPE and CFG normalization improve the denoiser. [lumina; supporting; direct-evidence; confidence high]. Limitations: Apache ungated package; upstream Gemma license/access remain separate dependencies. No native strength interface is assumed.

- lumina-evaluation: Table8: low-resolution DPG84.5/GenEval.63 → high-resolution85.7/.67 → high-quality5K updates87.2/.73 →11K updates87.6/.72. Nonmonotonic GenEval requires retaining training-stage context. FDPM/TeaCache speed choices trade stability or blur. [lumina; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hidream-method: I1 uses a 17B sparse-MoE DiT, four text encoders and FLUX1 VAE, C=16/f=8. O1 is native RGB3/f1 unified pixel diffusion; its separate card is conservatively grouped under this one family. [hidream; supporting; direct-evidence; confidence high]. Limitations: MIT ungated model packages. I1 external Llama3.1 is gated. O1 optional Gemma prompt refiner is gated; plain inference loads the local bundled model/processor, not a required external text encoder. No runtime validation.

- hidream-evaluation: I1 reports GenEval .83, DPG85.89 and HPSv2.1 mean33.82. Paper 50/28/14-step variants differ from the native Fast16 example; preserve revisions. Sample count/resolution are incomplete in the table. O1 GenEval .90 and DPG89.83 support pixel generation potential, not corruption equivalence. [hidream; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- omnigen-method: 3.8B Phi3-initialized multimodal rectified flow with frozen SDXL VAE, C=4/f=8. Input images are instruction/context tokens, not necessarily source latents initialized with partial noise. [omnigen; supporting; direct-evidence; confidence high]. Limitations: MIT ungated model. Resource table uses official custom code; current Diffusers may differ, so reported seconds cannot be transferred blindly.

- omnigen-evaluation: Table2 GenEval overall .70 versus SD3 .68; task tests include EmuEdit and DreamBench. Editing capability does not validate matched-strength regeneration. Resource measurements show an offload latency tradeoff. [omnigen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- cascade-method: Stage A VQ reconstruction uses spatial f=4; Stage B reconstructs its latent; Stage C uses a semantic EfficientNetV2-S compressor with16 channels and about24×24 tokens for1024, effective f≈42.7. This is not a single f8 VAE. Stable Cascade successor sizes differ from the paper. [cascade; supporting; direct-evidence; confidence high]. Limitations: Ungated custom noncommercial model license. Successor weights and stages prevent direct reuse of paper timing or scores.

- cascade-evaluation: COCO30K generated at1024, downsampled to256 for FID. Table2 Würstchen FID23.6/IS40.9; Stage C60 steps, Stage B12 steps, CFG4. PickScore also uses LocalNarratives5K and PartiPrompts. These are not measurements of the Stable Cascade3.6B release. [cascade; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- ddpm-method: RGB C=3/f=1, no AE. U-Net predicts noise with group normalization and attention at16². Training uses1000 steps and beta1e-4→.02. [ddpm; supporting; direct-evidence; confidence high]. Limitations: Apache2 model and permissive diffusion code. An adapter would be new scientific work;256 feasibility does not establish1024 feasibility.

- ddpm-evaluation: Table1 CIFAR train-reference FID3.17 (test-reference5.24), IS9.46. LSUNChurch256 FID7.89 and Bedroom4.90. These unconditional domain metrics do not validate general-photo regeneration. [ddpm; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- lens-method: 3.8B48-block MMDiT with frozen FLUX2 VAE, C=32/f=8;2×2 packing gives128 channels/f16 token grid. GPT-OSS20B total/about3B active text encoder. [lens; supporting; direct-evidence; confidence high]. Limitations: Code MIT. Actual model revision/license unverified at inaccessible endpoint. GPU-specific quantization undermines a blanket small-VRAM claim.

- lens-evaluation: Table2: Lens20-step GenEval.930 and Turbo4-step.914; OneIG EN/ZH are separate columns (.557/.525 for Lens), not two GenEval settings. Protocols include OneIG1,120 prompts, GenEval553 as this paper states and LongText160. Default inference refines prompts with a reasoner, uses20 steps/CFG5, while Turbo4-step uses no CFG. Prompt rewriting and system-prompt search therefore limit comparison with frozen unrewritten prompts. The H100 .84s/3.15s speed reports are primary author measurements, not our replication. [lens; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixelgen-method: RGB C=3/f=1 with affine identity PixelAE: encode x/scale+shift, inverse decode. Clean-image prediction converts to flow. LPIPS, perceptual DINO and REPA losses train the model; no compression AE. [pixelgen; supporting; direct-evidence; confidence high]. Limitations: Official HF weights Apache2 and ungated. Repository tree lacks LICENSE; do not infer code permission from weight terms. Community Diffusers mirror is not official support.

- pixelgen-evaluation: ImageNet256,80 epochs without CFG: FID5.11;160 epochs with CFG and50 Heun steps: FID1.83. T2I5121.1B GenEval.79. Paper title “Pixel Diffusion Beats Latent Diffusion with Perceptual Loss” differs from repository “Improving Pixel Diffusion with Perceptual Loss”; retain version distinction. [pixelgen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixsgr-method: Pixel diffusion with learned low-channel bottleneck and sparse global refinement inside the denoiser. RGB3/f1 output, no external pretrained AE. [pixsgr; supporting; direct-evidence; confidence high]. Limitations: Ungated but empty HF repository; license/code/weights unavailable rather than gated.

- pixsgr-evaluation: ImageNet256,50K samples,320 epochs,875M model: FID1.51, IS311, precision.78, recall.65. CFG3 over[.2,.98], interval guidance.04 over[.2,.7]. These are evaluation settings, not .2 img2img strength. No general T2I1024 result established. [pixsgr; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- dcae-method: Continuous nonvariational deep-compression AE; SANA uses C32/f32. Paper studies f64/c128 and f128/c512 too; denoiser patch size is separate from AE compression. [dcae; supporting; direct-evidence; confidence high]. Limitations: No full diffusion result can be inferred from encoder-only reconstruction quality.

- dcae-evaluation: Table2 ImageNet512 reconstruction: f64/c128 rFID16.84→.22 and f128/c512100.74→.23 with the proposed training/shortcuts. Reconstruction tradeoffs do not imply better preservation of a watermark. [dcae; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sprint-method: Same DC-AE C32/f32; SANA denoiser distilled to1–4 steps. Conversion rescales time, SNR and model output between flow matching and TrigFlow. [sprint; supporting; direct-evidence; confidence high]. Limitations: Distilled speed claims do not justify assuming strength labels have the same meaning as DDIM.

- sprint-evaluation: MJHQ30K FID/CLIP and GenEval comparisons: headline one-step FID7.59/GenEval.74; four-step table FID6.48/GenEval.76. Faster sampling is not evidence of matched source corruption. [sprint; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- wan-method: 127M causal3D VAE, C16/spatial8/temporal4; first image frame only undergoes spatial compression. Train2D image AE then inflate to3D with L1/KL/LPIPS followed by adversarial learning. [wan; supporting; direct-evidence; confidence high]. Limitations: Counted under Qwen family for the conservative floor, not as an extra family just for AE reuse.

- wan-evaluation: WanBench1,035 cases/model and VBench14B86.22%; video evaluation is not image regeneration. Fig7 numerical image values were not reliably extracted, so no fabricated PSNR/latency is listed. [wan; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky3-method: C4/f8 MoVQ; compares67M,102M,270M and selects270M. Updated model combines roughly3B U-Net and8.6B FLAN-UL2 text encoder. [kandinsky3; supporting; direct-evidence; confidence high]. Limitations: A larger MoVQ model is not automatically independent of earlier MoVQ training; count the family once.

- kandinsky3-evaluation: Table2 ImageNet reconstruction270M FID.686/SSIM.741/PSNR27.04, latent32². Do not invent an image resolution absent from the inspected table caption. Updated report uses human comparisons; these are not watermark outcomes. [kandinsky3; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky5-method: Image Lite6B CrossDiT flow matching; explicitly FLUX.1-dev VAE C16/f8. Video uses HunyuanVideo VAE. The image branch is not MoVQ. [kandinsky5; supporting; direct-evidence; confidence high]. Limitations: Paper inspected V2, but exact image checkpoint revision/license/gate not resolved in this sweep. Treat those model-release fields unavailable, not inferred from old Apache Kandinsky.

- kandinsky5-evaluation: §8.2.8 uses internal SBS prompts expanded from PartiPrompts with GigaMax; expert judges rate prompt following/visual quality against FLUX-dev/Qwen and editing counterparts. Figure win percentages and exact sample count were not extracted; remain unknown. Video2.7× speedup is not image timing. [kandinsky5; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- qwen-vae2-method: Global space-to-channel shortcut plus semantic DINO alignment; studies f16/c64 and f16/c128 image AEs. These are not automatically the released Qwen2.1 RGBA z64/f16 checkpoint. [qwen_vae2; supporting; direct-evidence; confidence high]. Limitations: Supplement only, not an additional model family in the floor.

- qwen-vae2-evaluation: ImageNet256 and FFHQ1024 reconstruction; OmniDoc roughly3K images at256, f16/c128 PSNR30.45/SSIM.9706/NED.9617 versus FLUX1 NED.9546. SiT80-epoch no-CFG comparisons change patch rates. NED convention and OCR quality matter; not our mark detector. [qwen_vae2; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hidream-o1-method: Raw RGB C3/f1, no external VAE or disjoint text encoder; single shared text/image token system. Pixel patches32×32 are tokenization, not a learned AE compression. Qwen3-VL-8B initialization, clean-image prediction, LPIPS/perceptualDINO and flow conversion; distillation uses distribution matching/adversarial training. [hidream_o1; supporting; direct-evidence; confidence high]. Limitations: MIT code/models, HF ungated. Plain inference uses bundled local weights/tokenizer/processor; optional Gemma4-31B prompt agent requires gate acceptance, optional API can cost money. Neither optional reasoner is required for plain generation or authorized here. PyTorch≥2.10/Transformers4.57.1 and optional FlashAttention differ from frozen stack.

- hidream-o1-evaluation: §5/table1 8B GenEval.90, Pro.92; DPG8B89.83. Full50/Dev28-step protocols and multiple text/editing benchmarks provide substantive evaluation. Sampling resolution/sample counts are not fully specified for every table; leaderboard images are not independent measurements. [hidream_o1; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

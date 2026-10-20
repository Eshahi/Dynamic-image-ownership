# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- ldm-method: The paper trains perceptual autoencoders with KL or VQ regularization, then trains cross-attention diffusion in their compressed latent spaces. It studies multiple compression factors rather than one later Stable Diffusion release configuration. [ldm; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- ldm-evaluation: Figure 7 compares compression factors 1, 2, 4, 8, 16 and 32 using 5K samples, 500K CelebA-HQ or 2M ImageNet training updates and A100/DDIM sampling sweeps. Moderate compression balances image quality and sampling cost. [ldm; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sdxl-method: KL AutoencoderKL,C=4,f=8; same architecture class as SD1, separately trained. SDXL U-Net≈2.6B, dual CLIP conditioning; native1024. Optional refiner excluded from core. [sdxl; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- sdxl-evaluation: Table3 COCO2017-val256: SDXL PSNR24.7/SSIM.73/LPIPS.88/rFID4.4; SD1 23.4/.69/.96/5.0; SD2 24.5/.71/.92/4.7. Preserve paper metric convention rather than treating these LPIPS values as the thesis assessor. Generation preferences can include refiner and cannot be assigned to base-only img2img. [sdxl; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sd3-method: The paper uses MMDiT with rectified-flow training and evaluates a 16-channel latent autoencoder against smaller bottlenecks. [sd3; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- sd3-evaluation: Table3 C16 VAE PSNR28.62/SSIM.86/FID1.06 versus C4 25.12/.75/2.41; dataset/resolution not clear in inspected caption, so do not assign COCO/1024. Generator-quality gains do not establish encoder-transfer survival. [sd3; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky-method: Kandinsky combines an image-embedding prior, a diffusion decoder and MoVQ reconstruction; the paper compares linear and diffusion priors and quantized versus unquantized decoding. [kandinsky; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- kandinsky-evaluation: §5 COCO30K256: linear-prior FID8.03; diffusion-prior quantized9.86 versus unquantized9.87. Human DrawBench5,000 votes. These are generation, not native1024 regeneration/watermark metrics. [kandinsky; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sana-method: SANA combines a deeply compressed DC-AE latent representation, linear-attention diffusion transformer and Gemma text conditioning. Its spatial compression factor is 32; this differs from the transformer patch size. [sana; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- sana-evaluation: The paper reports GenEval with 533 prompts as stated, DPG with 1,065 prompts and MJHQ30K. Table 5 reports CLIP 28.5 to 28.3 and ImageReward 1.03 to .96 under quantization on the stated evaluation subsets. These are generation and optimization results, not matched source-corruption measurements. [sana; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixartsigma-method: PixArt-Sigma replaces the earlier autoencoder with the SDXL VAE and adapts the denoiser for 2K updates; it also applies key/value compression to support higher-resolution generation. [pixartsigma; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- pixartsigma-evaluation: The Sigma report evaluates 30K curated high-quality examples and a 300-caption human/GPT4V preference subset. The curated prompts and evaluator protocol limit comparisons with other papers. [pixartsigma; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- playground-method: Playground v2.5 uses an SDXL-like diffusion architecture with EDM formulation, noise-schedule changes and balanced resolution-bucket training. [playground; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- playground-evaluation: MJHQ30K1024 FID4.48 versusSDXL+refiner9.55; private1K-prompt aesthetic preference4.8×ratio. Settings mix model/sampler/training differences, not AE isolation. [playground; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hunyuan-method: ≈1.5B transformer with bilingualCLIP/T5; C4/f8 VAE explicitly fromSDXL. [hunyuan; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- hunyuan-evaluation: §4 >3,000 prompts,>50 professional raters,four dimensions,30–50 prompts/subcategory. Smaller.7B ablations COCO30K256. Do not assign those conditions to1024 full-model reconstruction/survival. [hunyuan; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- qwen-method: Qwen-Image uses an MMDiT architecture and adopts the Wan VAE. Section 2.3 freezes its image encoder and fine-tunes the decoder; decoder reconstruction gains therefore do not establish a separately trained image encoder. [qwen; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- qwen-evaluation: Table2 ImageNet-val256FP32 PSNR33.42/SSIM.9159 versusWan31.29/.887; in-house text-rich25636.63/.9839 versus26.77/.9386. Effective image encoder19M/decoder25M. Decoder improvement does not prove new encoder. [qwen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- zimage-method: 6B single-stream S3-DiT with Qwen3-4B conditioning; frozen FLUX1 VAE, C=16/f=8. Turbo uses 8 NFE. [zimage; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- zimage-evaluation: Table9 reports GenEval .84 for base and .82 for Turbo. Speed depends on NFE and specialized optimization; quality scores do not isolate the encoder. Prompt rewriting and distillation can affect outcomes. [zimage; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- lumina-method: 2.6B UnifiedNextDiT with Gemma2-2B and FLUX VAE, C=16/f=8. Progressive multiresolution training, RoPE and CFG normalization improve the denoiser. [lumina; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- lumina-evaluation: Table8: low-resolution DPG84.5/GenEval.63 → high-resolution85.7/.67 → high-quality5K updates87.2/.73 →11K updates87.6/.72. Nonmonotonic GenEval requires retaining training-stage context. FDPM/TeaCache speed choices trade stability or blur. [lumina; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hidream-method: HiDream-I1 uses a 17B sparse-mixture-of-experts diffusion transformer, four text encoders and a pretrained autoencoder. The official repository identifies the autoencoder family separately; that identification is not attributed to this paper. [hidream; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- hidream-evaluation: The I1 paper reports GenEval .83, DPG 85.89 and HPSv2.1 mean 33.82. Its 50/28/14-step variants are distinct settings, and some evaluation tables do not fully specify image resolution or sample counts. [hidream; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- omnigen-method: OmniGen initializes its unified transformer from Phi-3 and uses a pretrained SDXL VAE. Input images supply multimodal instruction/context tokens; this interface alone does not define a partial-noise source regeneration attack. [omnigen; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- omnigen-evaluation: Table 2 reports GenEval .70 versus SD3 .68. The paper also evaluates editing and subject-driven generation using EmuEdit and DreamBench. These results do not establish matched-strength regeneration. [omnigen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- cascade-method: Wuerstchen uses a three-stage system: Stage A VQ reconstruction at spatial factor 4, Stage B latent reconstruction and Stage C diffusion over a highly compressed semantic representation produced with an EfficientNetV2-S-based compressor. The effective semantic compression is about 42 rather than an ordinary factor-8 VAE. [cascade; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- cascade-evaluation: COCO30K generated at1024, downsampled to256 for FID. Table2 Würstchen FID23.6/IS40.9; Stage C60 steps, Stage B12 steps, CFG4. PickScore also uses LocalNarratives5K and PartiPrompts. These are not measurements of the Stable Cascade3.6B release. [cascade; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- ddpm-method: RGB C=3/f=1, no AE. U-Net predicts noise with group normalization and attention at16². Training uses1000 steps and beta1e-4→.02. [ddpm; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- ddpm-evaluation: Table1 CIFAR train-reference FID3.17 (test-reference5.24), IS9.46. LSUNChurch256 FID7.89 and Bedroom4.90. These unconditional domain metrics do not validate general-photo regeneration. [ddpm; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- lens-method: 3.8B48-block MMDiT with frozen FLUX2 VAE, C=32/f=8;2×2 packing gives128 channels/f16 token grid. GPT-OSS20B total/about3B active text encoder. [lens; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- lens-evaluation: Table2: Lens20-step GenEval.930 and Turbo4-step.914; OneIG EN/ZH are separate columns (.557/.525 for Lens), not two GenEval settings. Protocols include OneIG1,120 prompts, GenEval553 as this paper states and LongText160. Default inference refines prompts with a reasoner, uses20 steps/CFG5, while Turbo4-step uses no CFG. Prompt rewriting and system-prompt search therefore limit comparison with frozen unrewritten prompts. The H100 .84s/3.15s speed reports are primary author measurements, not our replication. [lens; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixelgen-method: The method performs clean-image prediction in RGB pixel space and converts it to a flow field, using LPIPS, perceptual DINO and REPA training losses without an external compression autoencoder. [pixelgen; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- pixelgen-evaluation: ImageNet 256 evaluation reports FID 5.11 at 80 epochs without CFG, and FID 1.83 at 160 epochs with CFG and 50 Heun steps. The 1.1B text-to-image model at 512 reports GenEval .79. [pixelgen; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- pixsgr-method: Pixel diffusion with learned low-channel bottleneck and sparse global refinement inside the denoiser. RGB3/f1 output, no external pretrained AE. [pixsgr; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- pixsgr-evaluation: ImageNet256,50K samples,320 epochs,875M model: FID1.51, IS311, precision.78, recall.65. CFG3 over[.2,.98], interval guidance.04 over[.2,.7]. These are evaluation settings, not .2 img2img strength. No general T2I1024 result established. [pixsgr; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- dcae-method: Continuous nonvariational deep-compression AE; SANA uses C32/f32. Paper studies f64/c128 and f128/c512 too; denoiser patch size is separate from AE compression. [dcae; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- dcae-evaluation: Table2 ImageNet512 reconstruction: f64/c128 rFID16.84→.22 and f128/c512100.74→.23 with the proposed training/shortcuts. Reconstruction tradeoffs do not imply better preservation of a watermark. [dcae; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- sprint-method: Same DC-AE C32/f32; SANA denoiser distilled to1–4 steps. Conversion rescales time, SNR and model output between flow matching and TrigFlow. [sprint; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- sprint-evaluation: MJHQ30K FID/CLIP and GenEval comparisons: headline one-step FID7.59/GenEval.74; four-step table FID6.48/GenEval.76. Faster sampling is not evidence of matched source corruption. [sprint; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- wan-method: 127M causal3D VAE, C16/spatial8/temporal4; first image frame only undergoes spatial compression. Train2D image AE then inflate to3D with L1/KL/LPIPS followed by adversarial learning. [wan; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- wan-evaluation: WanBench1,035 cases/model and VBench14B86.22%; video evaluation is not image regeneration. Fig7 numerical image values were not reliably extracted, so no fabricated PSNR/latency is listed. [wan; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky3-method: C4/f8 MoVQ; compares67M,102M,270M and selects270M. Updated model combines roughly3B U-Net and8.6B FLAN-UL2 text encoder. [kandinsky3; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- kandinsky3-evaluation: Table2 ImageNet reconstruction270M FID.686/SSIM.741/PSNR27.04, latent32². Do not invent an image resolution absent from the inspected table caption. Updated report uses human comparisons; these are not watermark outcomes. [kandinsky3; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- kandinsky5-method: Image Lite6B CrossDiT flow matching; explicitly FLUX.1-dev VAE C16/f8. Video uses HunyuanVideo VAE. The image branch is not MoVQ. [kandinsky5; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- kandinsky5-evaluation: §8.2.8 uses internal SBS prompts expanded from PartiPrompts with GigaMax; expert judges rate prompt following/visual quality against FLUX-dev/Qwen and editing counterparts. Figure win percentages and exact sample count were not extracted; remain unknown. Video2.7× speedup is not image timing. [kandinsky5; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- qwen-vae2-method: Qwen-VAE2 introduces global space-to-channel shortcuts and semantic DINO alignment, including image autoencoder experiments with spatial factor 16 and 64 or 128 latent channels. These experiments do not by themselves identify the ancestry of a separately released Qwen-Image checkpoint. [qwen_vae2; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- qwen-vae2-evaluation: ImageNet256 and FFHQ1024 reconstruction; OmniDoc roughly3K images at256, f16/c128 PSNR30.45/SSIM.9706/NED.9617 versus FLUX1 NED.9546. SiT80-epoch no-CFG comparisons change patch rates. NED convention and OCR quality matter; not our mark detector. [qwen_vae2; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

- hidream-o1-method: HiDream-O1 uses a shared text/image token model initialized from Qwen3-VL-8B, with raw-pixel clean-image prediction, perceptual losses and flow conversion. It does not require an external VAE or a disjoint text encoder; distribution-matching and adversarial distillation produce faster variants. [hidream_o1; supporting; direct-evidence; confidence high]. Limitations: Paper evidence only. Official code/config and successor claims are separately sourced in the human Markdown card.

- hidream-o1-evaluation: §5/table1 8B GenEval.90, Pro.92; DPG8B89.83. Full50/Dev28-step protocols and multiple text/editing benchmarks provide substantive evaluation. Sampling resolution/sample counts are not fully specified for every table; leaderboard images are not independent measurements. [hidream_o1; supporting; direct-evidence; confidence medium]. Limitations: Author-reported metrics under stated protocol; not thesis outcomes.

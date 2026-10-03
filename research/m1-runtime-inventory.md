# M1 runtime and development inventory (2026-10-03)

Code worktree: `C:/Users/Soroush/.codex/worktrees/v5-study/THESIS_GUIDE_OFFLINE_v5`. MAIN: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. Worktree `.thesis-build` is absent (no link). Assets/interpreters/retained runs are in MAIN. No image bytes, held-out images or held-out scores were opened during this inventory. No experiment/download/install ran.

## Pinned runtime

Windows science interpreter: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe`. Read-only metadata check: Python 3.12.14, torch 2.12.1+cu130, torchvision 0.27.1+cu130, numpy 2.5.2, scipy 1.16.2, Pillow 12.3.0, diffusers 0.35.1, transformers 4.57.6, lpips 0.1.4, safetensors 0.6.2. Official retained v5 launcher uses WSL `/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python`; its current availability/version was not reverified.

SD provenance candidate: `stable-diffusion-v1-5/stable-diffusion-v1-5` mirror, revision `451f4fe16113bff5a5d2269ed5ad43b0592e9a14`, CreativeML OpenRAIL-M. Existing `research/initial-noise-path.md` identifies the mirror and warns that original-publisher equivalence is unproved. Asset lock provides exact bytes; configuration revision is not independently established as every weight download revision by this inventory. CLIP source install receipt: https://github.com/openai/CLIP.git commit `d05afc436d78f1c48dc0dbf8e5980a9d471f35f6`; MIT. CLIP weights are ViT-B/32 official archive identity below. LPIPS 0.1.4 learned alex weights live inside science venv `Lib/site-packages/lpips/weights/v0.1/alex.pth`, 6009 bytes, SHA256 `df73285e35b22355a2df87cdb6b70b343713b667eddbda73e1977e0c860835c0`; package/source preflight in `scripts/check_a6_lpips_assets.py`. AlexNet trunk identity is in table.

All following paths are relative to `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6`. Values copied from `research/a6-candidate-model-assets.json` (lock SHA256 `b8c2595857853ea5b7835bb71f12a34dde07b78623c5e638f692dc7eb220b27e`); file existence/size checked, bulk hashes not recomputed here.

| Asset | Bytes | SHA256 |
| --- | ---: | --- |
| `clip/ViT-B-32.pt` | 353976522 | `40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af` |
| `alexnet/alexnet-owt-7be5be79.pth` | 244408911 | `7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02` |
| `sd15-fp16/feature_extractor/preprocessor_config.json` | 342 | `2a1da83b5e1032aaeef397552ddb408dca0d8cd1dc58f61bf6abf38d6f33a0a2` |
| `sd15-fp16/model_index.json` | 541 | `e2f6f22e274374010aec30c79eb2d6e53fff4a36ac0225523a92cb2d41a83347` |
| `sd15-fp16/safety_checker/config.json` | 4723 | `5dd77a06cbd9b155060bd58deb81ffd1aafc1c6d7970acac674c1128bd4edfe2` |
| `sd15-fp16/safety_checker/model.fp16.safetensors` | 608018440 | `08902f19b1cfebd7c989f152fc0507bef6898c706a91d666509383122324b511` |
| `sd15-fp16/scheduler/scheduler_config.json` | 308 | `699cce92eb7c122e2eb7dfdea78e6187fda76a5ed4a8e42319b85610e620e091` |
| `sd15-fp16/text_encoder/config.json` | 617 | `845df614cb9327ae7bbea027316246fae917827407da6df13572e41b5f93b4cc` |
| `sd15-fp16/text_encoder/model.fp16.safetensors` | 246144864 | `77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e` |
| `sd15-fp16/tokenizer/merges.txt` | 524619 | `9fd691f7c8039210e0fced15865466c65820d09b63988b0174bfe25de299051a` |
| `sd15-fp16/tokenizer/special_tokens_map.json` | 472 | `c4864a9376a8401918425bed71fc14fc0e81f9b59ec45c1cf96cccb2df508eac` |
| `sd15-fp16/tokenizer/tokenizer_config.json` | 806 | `00439066fcba73de57644cf41e4e3b9f2dbb09d7f3fc2005898ba52399045882` |
| `sd15-fp16/tokenizer/vocab.json` | 1059962 | `e089ad92ba36837a0d31433e555c8f45fe601ab5c221d4f607ded32d9f7a4349` |
| `sd15-fp16/unet/config.json` | 743 | `78f474de6bab3d893868f37be97b636ae65c0df3073ed3256ca458ff599b5f96` |
| `sd15-fp16/unet/diffusion_pytorch_model.fp16.safetensors` | 1719125304 | `c83908253f9a64d08c25fc90874c9c8aef9a329ce1ca5fb909d73b0c83d1ea21` |
| `sd15-fp16/vae/config.json` | 547 | `786a7d21647ddea6a04b9675c03d3cb45e90a2f3c6da5fbda2c54ade040036de` |
| `sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors` | 167335342 | `4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c` |

## Development sources

Exact photograph manifests: `experiments/c4-qim-rgb-development-v1/cohort.json` (original ten) and `experiments/c4-three-threat-small-v1/development-expansion.json` (1675,4795). These are exploratory development, selection not random; item rights remain pending and local academic restrictions retained. v5 r3 uses all twelve clean/T5, original ten T3/T4. Exact reusable manifest: `research/m1-reconstruction-dev.json`.

| ID | Absolute raw path | SHA256 |
| ---: | --- | --- |
| 1675 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000001675.jpg` | `6ba641627c08ef424b7dc3e6cee069aa0dd49615a31c54ae0de1ecd1fabd9dea` |
| 4795 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000004795.jpg` | `6f8994bac6aef0602d4aa4397ecd4b7d579f5b18f66058a2df021352dd22bdc6` |
| 6012 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000006012.jpg` | `7cd0d627b15c09f373aa613d013fb2d8ae6bd20bcce0d98aa31b963e6bcca495` |
| 25394 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000025394.jpg` | `f13f54a3cbe28140004425b1b010c51bd5be0e4c4da1d4b1e382e3e0b426e316` |
| 80932 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000080932.jpg` | `c5bdb620680ad74c2bb788cabbf3374d68285bec3a2023fadf0ffc7eb257ba72` |
| 109798 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000109798.jpg` | `8fafbfb6d1c320f9efc59291748c0b9a730726db311364c03280b2de39fe656f` |
| 134882 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000134882.jpg` | `d2a42fe606563d125e105246e6cd473f098338364b51f085da8a97d5943876c5` |
| 147498 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000147498.jpg` | `70c27d6d67cafe8d0d5a91a6913bc26ce1ba68f7cb69cdec60e96894ac1ec5d6` |
| 177015 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000177015.jpg` | `13bc4db7ed2ac2612fd03cbb25a597712f99cf1e44784d4abde5aca47f6999c7` |
| 190676 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000190676.jpg` | `d2302cb8d9e0d37a4a150d79ffbb4ba9b1adfd2bcfd477b7b64581ba40e00b7b` |
| 468505 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000468505.jpg` | `a3327665e199c84b0ad0e69c8e3f3f6df13902eb3b8580a0708c2c6cade370b6` |
| 499768 | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/val2017/val2017/000000499768.jpg` | `8570324bcf64969f77f938941778a8fc69ec5a8943f0945511ce4ab09bce5a3a` |

Synthetic host directory: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/rehearsal/v5-channel-dev/hosts`; existing `generated-00.png` through `generated-11.png` and `procedural-0.png` through `procedural-3.png`. Procedural generator is `dev_v5_channel_probe.procedural(100+i)`, size512. Generated hosts derive from fixed PROMPTS, seeds1000+i, SD1.5 DDIM25steps CFG7.5. Existing files were enumerated, not opened/scored. Never use adjacent `holdout`/`holdout2` directories for tuning.

## Reuse APIs and transformations

- `three_threat_models.verify_assets(asset_root, lock_path)` verifies all17 assets plus LPIPS package bytes; `load_regenerator(asset_root)` loads explicit local fp16 SD1.5 including safety and substitutes explicit DDIM. `regeneration_kwargs(strength,seed,image,torch.Generator)` uses empty prompt/negative,20 steps,eta0,CFG1,fresh matched CUDA generator; frozen study supports strength0.2/0.4,seeds0/1/2. `validate_generated` rejects incomplete/flagged safety or geometry mismatch.
- `dev_v5_channel_probe.load(device)` returns text/image pipelines; `vae_round_trip(pipe,rgb)` uses posterior mode unscaled VAE decode, not inversion; `regenerate(pipe,rgb,strength,seed)` runs the same attack with a broader development strength grid. These dev helpers need explicit MAIN `ASSETS`/`OUTPUT` override because worktree build directory is absent.
- `a6_clip_visual.load_visual_encoder(clip_path,device="cpu")` hashes official model source/JIT archive and returns encoder/transform. Transform bicubic shorter-edge224 then center crop224, RGB, tensor, official normalization. `three_threat_models.clip_feature` returns finite unit-normalized512-D feature. `load_lpips(asset_root,package_root)` + `lpips_score(metric,left,right)` use CPU AlexNet/two weight sets, RGB[-1,1].
- `qim_rgb_pilot.canonical_rgb` requires RGB JPEG/PNG, EXIF transpose, embedded ICC-to-sRGB if present. v5 worker then bicubic resizes native canonical image directly512x512. Saved marked PNG is reopened before detector/attack. `revised_watermark_v5.embed_rgb` and `detect_rgb` accept RGB list plus owner, profile, external semantic feature; v5 is an image-domain comparator. `v4_study_boundary.prepare_marked` implements saved source-feature embedding/refinement contract.
- `three_threat_protocol.center_patch` copies central128/256 patch donor->unmarked recipient; `residual_transfer` adds donor mark residual at scale0.5/1 with clipping/rounding (stronger access arm). `v5_study_protocol.transfer` contains v5-specific arms. Benign `dev_v5_regeneration_check.ordinary`: JPEG75/50, Gaussian blur1.5, down384 Lanczos, down384 then original geometry Bicubic. v5 protocol ordinary settings should be used for exact comparator parity.

## Retained latent route (distinct from v5)

Code not present in this v5 worktree; retained source exists in `C:/Users/Soroush/.codex/worktrees/c4-localization-exec/THESIS_GUIDE_OFFLINE_v5/src/embedding/`. Relevant files: `worker.py`, `proposed.py`, `source_preserving.py`, `latent_refinement.py` where available, `refinement_package.py`, `validation_bridge.py`, `output.py`. Find exact retained revisions from MAIN `.thesis-build/c4-runs/*/*/execution-manifest.json`, rather than silently importing mutable worktree code.

MAIN `.thesis-build/c4-package-20260926/final-design-package/experiment-spec.yaml`: c4-embedding-dev-001, native COCO109798500x333 padded512x384, fixed image-conditioned initial-noise delta,10DDIMsteps strength0.2(two suffixsteps),seed0,fp32,Adam lr0.005,two updates,rho0.01. Primary endpoint engineering finite gradients/custody; enrollment-informed continuous DCT template scores, no blind detection; saved q/h drift/quality NOT_RUN in that first spec. It is a gradient feasibility antecedent, not regeneration/lightweight-extractor proof.

MAIN `.thesis-build/c4-refinement-package-20260927/v1-design/experiment-spec.yaml`: one-source decoder refinement and fixed-point inverse/replay localization, six fixed arms,64decoder iterations max and257decoderNFE; no watermark. Retained source-composition/ten-source-composition artifacts explicitly mix reconstruction/source and must not be relabelled pure latent outputs. Existing initial-noise reference is scalar/index-only; does not itself generate images.

New diagnostic `scripts/m1_latent_reconstruction.py`: posterior-mode initialization, then optimize unscaled latent RGB MSE through frozen fp32 VAE decoder only, checkpoints0/50/100/200,Adam0.02,batch1,10GiB allocator ceiling; saved RGB8 PSNR/SSIM/optional LPIPS and partial provenance. This measures one optimization route, not a universal decoder ceiling or watermark result. Parent must commit before scientific execution.

"""Build the topic-local, research-only evidence package from inspected text.

No upstream code is executed. No model, image, dataset, or result is loaded.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
from curated_prose import polish
from final_overrides import enrich


TOPIC = Path(__file__).resolve().parents[1]
CACHE = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache")
DATE = "2026-10-20"
METHODS = []


def add(name, file, arxiv, venue, sections, mechanism, native, release, regen, cost, implication, rank="Literature coverage; excluded"):
    text = (CACHE / "T3b" / file).read_text(encoding="utf-8")
    lines = text.splitlines()
    version_line = next(x for x in lines if x.startswith("arXiv:"))
    i = lines.index(version_line)
    # Titles are supplied explicitly below where line breaking matters.
    title = lines[i+1]
    METHODS.append(dict(name=name, source_file=file, arxiv=arxiv, title=title,
                        version_date=version_line, venue=venue, sections=sections,
                        mechanism=mechanism, native=native, release=release,
                        regeneration=regen, cost=cost, implication=implication,
                        ranking=rank))


add("WAM", "wam-reused.txt", "2411.07231v2", "ICLR 2025; inspected arXiv v2 is the evidence version.",
    "Method §§3–4, Eqs.1–2; evaluation §§5.1–5.3; Appendix G.1–G.3, Table 9; pinned README, params.json, embed/detect and metrics.py.",
    "A message-conditioned autoencoder writes a residual; a ViT-based extractor predicts one mask logit and 32 message logits per pixel. Full-image single-message embedding is the relevant post-hoc use. Localization and several messages are additional capabilities, not owner authentication.",
    "Native released MIT SA-1B model: 32 raw bits, 256 processing size, scaling_w=2.0, scaling_i=1.0, JND jnd_1_3_blue. RGB512 is ImageNet-normalized; internal bilinear resize to256 and antialiased residual upsampling preserve the original image. Paper training is COCO, with alpha=.3 and high-resolution JND scaling; it is not the same checkpoint. Pixel mask sigmoid>0.5; paper image presence is mask-positive area fraction>0.07, calibrated on COCO to about 2.6e-4 FPR. Released README passes RAW message logits to semihard aggregation: select mask>0.5, average logits, compare average>0.5. This differs from averaging probabilities in paper Eq.2; retain released behavior. Empty mask is an abstention, not a recovered message. Official save_image rounds via multiply255/add0.5/clamp/uint8. Our common known-message presence is >=27/32 matches (analytic fair-query tail 5.6537101045e-5); it is NOT the native image detector and must not be conjoined with it. COCO calibration does not transfer automatically to the SA-1B release.",
    "Official facebookresearch/watermark-anything@2c08af04d037d5667c02f6ddebbda9ff04581c3e; MIT code and chosen SA-1B checkpoint. https://dl.fbaipublicfiles.com/watermark_anything/wam_mit.pth is 377825938 bytes; inherited metadata SHA256 90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2. Source archive SHA256 7baaa18c6774d1397207b262cd077f588150e846fada9c7c7b5ce7d0239ef0b6. No new binary download. COCO-weight licensing is distinct and those weights are not substituted.",
    "Primary Table 9, Appendix G.3: DiffPure attack PSNR 30.1/28.4/27.0/24.9 dB -> bit accuracy 100/99.4/71.3/49.1%; VAE attack PSNR 32.9/32.4/28.6/25.5 -> 100/99.8/98.6/53.7%. These are bit accuracies, not TPR at our threshold. This appendix does not specify enough to reproduce model revision, diffusion strength/noise schedule, sampler, prompt, exact evaluation count or every attack resolution; do not infer them from the main 10k COCO/DIV2K evaluation. The published curves are COCO-weight evidence. VINE and SpreadMark comparisons use other payload/quality and attack conditions; they cannot establish this release's R1 outcome.",
    "Paper: approximately 1.1M embedder and 96M extractor parameters. Weight size above is storage, not peak VRAM. Future inference is one small embedder and one ViT forward; target-server time/VRAM are unmeasured. Existing core cost remains the parent budget; no new timing claim.",
    "Maintain separate native mask-presence, common queried-message presence, exact recovery and clean quality columns. Do not silently fix the paper/code threshold discrepancy. Preserve native quality; no outcome-based residual scaling.",
    "Core: already user-approved; no new arm.")

add("VINE", "vine-reused.txt", "2410.18775v2", "ICLR 2025; official repository and paper version inspected.",
    "Method §§3.1–3.3; evaluation §§4.1–4.3, Table 1; Appendix C/G.2/H, Table 7; native encoder/decoder and stochastic/deterministic regeneration scripts at the pinned commit.",
    "Low-frequency surrogate corruption trains a one-step generative-prior residual encoder and ConvNeXt-B message decoder. VINE-R is the chosen robust post-hoc checkpoint. VINE-Base is a separate quality/robustness point, not an interchangeable baseline.",
    "100 raw bits; native encoder RGB256 in [-1,1], decoder RGB256 in [0,1], sigmoid outputs and NumPy rounding. PIL bicubic resize input; posterior MODE; tensor bicubic residual upsample onto original512; clamp then native ToPILImage truncation and reopenPNG. No ImageNet normalization. Text CLI uses 96 text bits plus 4 zeros, unlike arbitrary100-bit API use. Paper/README says SDXL-Turbo, but constructor actually uses stabilityai/sd-turbo. Native benchmark reports ROC TPR at FPR<.001 or<.01; no universal numerical message-match threshold is published. Our >=69/100 is a separate fair-query tail rule (9.1571612441e-5), not native TPR@.1%. Report C0 and wrong-owner behavior without outcome-based recalibration.",
    "Shilin-LU/VINE@d72f11a93f8de9bc45ef61202b9c8dda2a70cc77. Repository NTUITIVE noncommercial license; HF cards separately say MIT; sd-turbo dependency has Stability AI Community License. Do not label the stack MIT. Encoder Shilin-LU/VINE-R-Enc@0c255688e032e4318c700c485c0625367b70908c: 4019166704 bytes, LFS SHA256 16bf5f2acf5f7d5f00570431f5dc9dd61a8e95f828a2f68483ffe06448293dd6. Decoder VINE-R-Dec@0f094b300be71a358f7c1769221f50318f1b4d74: 354802864 bytes, SHA256 9aded1fc22efe47bdafc8f436f81953cd06bde1d6c7242f86bf101c020d7eea0. sd-turbo@b261bac6fd2cf515557d5d0707481eafa0485ec2; combined needed fp32 stack 9533935644 bytes. Immutable URLs are in retained manifest.json. No weights downloaded.",
    "Table1 VINE-R: PSNR37.34, SSIM.9934, LPIPS.0063; stochastic/deterministic regeneration TPR@.1% FPR 99.66/99.98%, averaged across severities. VINE-Base:40.51/.9954/.0029 and91.03/99.25%. Official stochastic code: stabilityai/stable-diffusion-2-1 fp16 revision fp16, DDIM, noise indices60..240 step20, requested50 inference steps with head-start logic 50-max(noise//20,1), CFG7.5, empty prompt unless captions supplied; latent posterior sampled. Deterministic code: SD2.1-base fp32, DPM multistep inverse/forward scheduler order2, 15/25/35/45 steps, CFG1, empty prompt/negative prompt, posterior mean*.18215. Native benchmark512. COUNT CONFLICT: Table1 caption says5000 images per editing method; §4.2 says1000 stochastic and1000 deterministic sources; §4.3 describes m×1000 over severities. Preserve all statements; no silent reconciliation or claim of5000 independent sources. Quality uses10k UltraEdit images. Native ROC calibration is empirical against unmarked images; no .0001 calibration is claimed.",
    "Table7: NVIDIA Quadro RTX6000, mean over1000 images, reported running time .0795s and memory4982MB. Phase/batch scope is not sufficiently explicit to turn this into whole-grid time. Storage~9.53GB is not peakVRAM. Budget target-server smoke remains unmeasured.",
    "Independent SDXL regeneration is absent from these SD2.1 attack scripts. The generative prior's name does not prove independent-encoder transfer. Freeze actual released sd-turbo and preprocessing, and label both operating points.",
    "Core: user-approved VINE-R; VINE-Base remains excluded.")

add("TrustMark", "trustmark-reused.txt", "2311.18297v1", "Final ICCV2025 open-access paper also inspected, pp18629–18639; final version takes precedence where stated.",
    "arXiv v1 §§3.1–3.3,4.1–4.4; final ICCV PDF pp3–7 (method, Algorithm1, experimental setup, Table3); Table3 visually verified from rendered p7; pinned official Q loader/config/LICENSE.",
    "MUNIT-based image encoder with postprocessing1x1 layers, spectral/quality loss, ResNet50 sigmoid decoder. ReMark is a separate learned removal/re-watermarking module. Public decoding is a provenance-pointer function; a decoded identifier does not authenticate an owner.",
    "256 network resolution; normalize[-1,1], obtain residual at256, interpolate residual to originalH×W, scale lambda=1 by default, clamp. Paper raw100-bit setting is distinct from released Q default:61 useful bits +35 BCH parity +4 header=100 physical bits. Raw100 mode bypasses BCH. BCH validity is not the same endpoint as100-bit match detection. Paper final alpha_max27.5 quality variant and alpha_max20 removal experiment must not be conflated. No published universal presence threshold at1e-4. P1 must state raw100 presence and native BCH success separately; do not force equal useful payload by silently changing native code.",
    "adobe/trustmark@6df5a0a29b51cbec832695fdf02051a1937e37bd. Final paper footnote and official LICENSE explicitly release code/models under MIT. Q encoder/decoder at https://cai-watermark.adobe.net/watermarking/trustmark-models/encoder_Q.ckpt and decoder_Q.ckpt; official loader MD5 values 700328b8754db934b2f6cb5e5185d81f and 4ced90e9cfe13e3295ad082887fe9187. These are integrity metadata, not a new SHA256 or immutable release revision; weight SHA256 remains unresolved without downloading.",
    "Final primary Table3: TrustMark alpha_max20/lambda1, no removal PSNR40.20 and BA.970; Zhao et al. denoising sigma=.3 gives PSNR9.23 and BA.660. Visually checked p7. Default evaluation is DIV2K900 train+validation images (§4.1); table-specific count is not separately stated. Exact denoiser/model revision, sampler, steps and prompts are unspecified; do not call this matched SDXL. Third-party VINE Table1 raw100 variant gives stochastic9.22%, deterministic34.20% TPR@.1%, PSNR41.27/.9910/.0026 under VINE card conditions/count conflict. WAM G.3 uses a different40-bit configuration: DiffPureBA100/98.3/74.9/54.3%; VAE100/100/99.9/98.1%. These results disagree in attack and native configuration, not necessarily scientifically.",
    "Final ICCV§4.1 reports125ms encoding and25ms decoding on RTX3090; training48h is not inference. VINE third-party Table7 reports .0705s/648MB on QuadroRTX6000,1000-image mean. Different hardware/protocol; neither is a rented-server measurement.",
    "P1 is the strongest conventional published-release comparator proposal, but bit payload, ECC and visual quality must be visible. Final-paper access gap is now closed via Windows PDF rendering/OCR and visual Table3 check.",
    "P1 TrustMark Q retained; proposed, excluded from core.")

add("StegaStamp", "stegastamp.txt", "1904.05343v2", "CVPR2020.",
    "§§4.1–4.4 encoder/decoder/BCH and print-camera pipeline; §§5.1–5.5 and Table2; official README/LICENSE.",
    "U-Net residual encoder and spatial-transformer CNN decoder learn physical-world robustness. Detection of a rectangular stamp in photographs can use segmentation; that localization stage is not a calibrated arbitrary-image watermark detector.",
    "Native400×400 RGB,100 physical bits; message linear map to50×50×3 then upsample. BCH supports56 useful bits (seven characters), so100 raw is not100 useful native payload. Decoder sigmoid/bit rounding; original BCH decode success is native application success. The paper does not define a universal queried-message presence threshold at1e-4. A512 study needs documented official residual adaptation or a native400 arm; do not resize final image and call it equivalent.",
    "tancik/StegaStamp@c984446048b826587ca1875027b0a1dc1885fb30, MIT code. README references saved_models/stegastamp_pretrained; exact stable checkpoint artifact/hash not verified. TensorFlow1.13-era execution dependency; no install attempted and no port is counted as faithful release.",
    "Original evaluation is physical print-camera, not diffusion:1890 photos (105 samples×18 camera/printer conditions), meanBA98.7%;500-image synthetic quality Table2 givesPSNR28.50,SSIM.905,LPIPS.101 at100bits. Third-party VINE Table1:91.09/92.13% stochastic/deterministic TPR@.1%; PSNR29.65/.9107/.0645 with VINE512 residual pipeline and its count conflict. ZoDiac Table15 uses a96-bit readout and threshold61/96 at observedFPR.056: Zhao23 40/60/80/100/120/140/160/180/200 steps ->WDR.588/.286/.098/.032/.010/.002/.002/0/0. This is not native100-bit+BCH nor an equal-FPR comparison. Exact attack sampler/prompt/revision unresolved.",
    "VINE Table7 .0672s,1984MB on QuadroRTX6000,mean1000. No current hardware estimate established; legacy environment and artifact resolution dominate integration risk.",
    "P2 remains useful as the historically strong regeneration baseline, conditional on a verified official checkpoint. Its much lower native quality and56-bit useful payload must not be concealed.",
    "P2 retained, deferred until artifact and faithful runtime preflight; excluded.")

add("InvisMark", "invis-reused.txt", "2411.07795v2", "WACV2025, pp909–918; inspected arXiv v2.",
    "§§2.1–2.4; §§3.1–3.5,Tables2–3,Figure4 and UUID extension.",
    "MUNIT residual encoder with convolutional postprocessing and ConvNeXt-Base sigmoid decoder; resolution scaling and worst-case augmentation training target high-resolution AI images.",
    "Low-resolution encoder residual is upsampled and added to original high-resolution image (paper experiments1024/native encoder256).100-bit primary setting; a separate256-bit BCH extension carries a128-bit UUID. No native FPR-calibrated presence threshold reported. Pixel Seal paper states its tested InvisMark100-bit checkpoint has6 fixed trained bits and94 effective bits; this is a third-party implementation observation requiring checkpoint verification, not an independently proven fact about every InvisMark model.",
    "microsoft/InvisMark@8d5ce55705ada1c2daf642c97f7ff3ae6dbd1825, MIT repository. Official README OneDrive checkpoint folder available as a pointer; immutable revision/hash and durable direct artifact access not verified. Private100k DALL-E3 training images unavailable; do not replace weights with retraining and call it native.",
    "Primary§3.3/Fig4: SD2.1 regeneration noise settings1,3,5,10,20,60,100 on10 images; BA approaches chance around attackedPSNR25dB. Exact per-setting numeric BA is graphical and was not digitized; no invented scalar or confidence interval. Sampler, prompt, seed replication and exact count per condition are not fully reported. Table2 clean quality on900DIV2K and900DALL-E3 isPSNR51.4 andSSIM.998; this favorable quality is not a regeneration detection guarantee.",
    "No inspected inference time/peakVRAM number. Qualified architecture estimate: one256 MUNIT encoder and ConvNeXt-B decoder plus high-resolution interpolation; no diffusion sampling at inference. Actual costs remain unmeasured.",
    "Published10-image regeneration evidence is small and weak under noise; unavailable immutable weights lower priority. Residual copy attack described in§3.5 also prevents an ownership-authentication interpretation.")

add("RoSteALS", "rosteals-reused.txt", "2304.03400v1", "CVPR2023 Workshops (CVPRW); official release.",
    "§§3.1–3.2;§§4.1–4.3 and evaluation definitions; official README/license/checkpoint metadata.",
    "A small secret encoder injects message-conditioned offsets into frozen autoencoder latent features; a ResNet50 recovers the message from the decoded image. Existing images can be encoded, so this is a post-hoc latent method rather than initial-noise-only generation.",
    "256 RGB,100 physical bits; frozen VQ-f4 plus~300k secret encoder. Word accuracy in paper accepts<20% bit error; it is not exact recovery or an empirical1e-4 presence test. BCH application settings must be distinguished from raw bit accuracy. Decoder observes image and trained model; known-message testing adds queried-message side information.",
    "TuBui/RoSteALS@8c09b022a362ffdf977a86f355e5af339793d9c9, CC BY-NC-SA4.0. Official520MB watermark checkpoint https://kahlan.cvssp.org/data/Flickr25K/tubui/cvpr23_wmf/epoch=000017-step=000449999.ckpt; frozenVQ dependency https://ommer-lab.com/files/latent-diffusion/vq-f4.zip. Neither downloaded; immutable hash and dependency license/version remain unresolved.",
    "Original evaluation:100kMIRFlickr training,1k validation; CLIC530,MetFace1336,Stock1K1000,14 ImageNet-C noise families. No quantitative diffusion-regeneration experiment in the inspected original evaluation. Thus no native model/strength/sampler/prompt/count/TPR tuple exists to report; standard-noise word accuracy cannot fill that gap.",
    "README training batch4 fits12GB; this is a training fit statement, not inference peak. Qualified estimate: oneVQ encoder/decoder plus small secret network andResNet50; no iterative denoising. Actual timing/VRAM unavailable.",
    "Relevant to latent post-hoc taxonomy and encoder bottleneck, but older generic-noise training and missing directT3 evidence make it lower priority than released robust baselines.")

add("ZoDiac", "zodiac-reused.txt", "2401.04247v2", "NeurIPS 2024 main track; official proceedings verified; numerical evidence is inspected arXiv v2.",
    "§§3.2–3.3,4.1; Appendix B.6/Table15,B.7/Table16 andD timing/memory.",
    "Per-image latent optimization through Stable Diffusion writes a Fourier-ring pattern in an inverted image latent, then adaptive blending meets an SSIM target. Detector inverts image and performs a noncentral-chi-square-based test against the watermark ring.",
    "Zero-bit detection, not a32/100-bit message baseline. SD2.1-base,512,DDIM inversion, ring radius10 in last latent channel,100Adam iterations and50 denoising steps by default, SSIM target.92. Native accepts when1-p>p*=.90 by default; p*=.95/.99 alternatives changeFPR. Ring key and inversion model are detector side information. Do not set .0001 and imply published performance.",
    "zhanglijun95/ZoDiac@89f864d2e4f6f33663dc69b4d99bee49073e194c. Code inspected; no repository license verified (public accessibility is not a license). Requires SD2.1-base; weight/dependency permissions and full reproducible pin not resolved for a proposed run. No checkpoint download or inference performed.",
    "500 images each fromMS-COCO,DiffusionDB,WikiArt; default learned attacks bmshj/cheng quality3 and Zhao23 regeneration60steps. AppendixTable15 (MS-COCO attack-strength study): atp*=.95 and observedFPR.032, WDR at40/60/80/100/120/140/160/180/200steps=.980/.974/.950/.940/.924/.912/.894/.866/.818. Atp*=.90,FPR.062,WDR=.988/.988/.964/.970/.952/.946/.938/.926/.898. AttackPSNR27.15 down22.44. Prose says .998 to.898; table first value is.988, so preserve the inconsistency. Exact attackmodelrevision,sampler,prompt not fully specified. These percent-level false positives cannot support a1e-4 claim.",
    "AppendixD RTX8000 fp32: peak15552MiB, modelweights5308MiB; per-image embedding255.94s at50denoise steps,159.47s30,65.35s10,45.41s1. Changing steps changes the method point; do not adopt the fastest variant merely to fit budget.",
    "Strong published detection at permissiveFPR and lowerquality (Table16PSNR29.41,SSIM.92,LPIPS.09) is not an equivalent-quality competitor. Its inversion and iterative embedding are a poor fit for this cheapest decisive core.")

add("PhaseMark", "phase.txt", "2601.13128v1", "ICASSP2026; official README DOI10.1109/ICASSP55912.2026.11463051.",
    "§§2.1–2.3,3.1–3.3,Tables1–2; official code README/LICENSE.",
    "Training-free phase modulation in a VAE latent Fourier annulus. APM,PCQ,IPS,SPS are distinct modulation variants; the detector re-encodes the image and decodes phase/correlation.",
    "512 image; SD2.1 VAE; central44×44×4 latent spectrum, annulus radii10–18,32bits/channel=128,2×2blocks and Hermitian constraints. APM uses±pi/2; PCQ constellation distances; IPS/SPS relative-cosine tests, SPSgamma.8. Presence uses binomialalpha=.01; identificationN=1e6 uses Bonferroni. Text says BA 'exceeds' a threshold while minimumk tail definition uses>=; exact integer boundary must be verified in code before any implementation. Native128bits andVAE side information are not the common32/100bit points.",
    "SungJuLee/PhaseMark@dfe42ad0449459e26fe1579957c6d05ccdee9b92 (official provenance is retained in manifest). CC BY-NC4.0. No learned watermark weights; pretrained SD2.1VAE dependency is still required. README uses a Manojb mirror; immutable dependency version/license resolution remains open.",
    "PrimaryTable1 APM TPR@1%FPR:VAE-B.996,VAE-C.997,diffusion1.000 on1000SD2.1-generated512images. Attacks cite bmshj/cheng quality3 and Zhao-style diffusion60steps; actual attackmodelrevision,sampler,prompt not fully specified. CFG7.5/DDIM50 in setup describes source generation, not proof of attacksettings. PCQ cleanPSNR34.156 versus VAE ceiling36.4193; neither establishes strictPSNR>35 for every source. No independentSDXL source/attack pairing is demonstrated.",
    "Table2 reports .142s embed and .050s detection; hardware not sufficiently specified in inspected timing table. Estimate consists ofVAE encoder/decoder+FFT, not a heavy iterative generator. Server timing remains unmeasured.",
    "P3 tests a distinct phase-based latent hypothesis, but requires dependency/variant/boundary fidelity and quality reporting. Literature numbers use1%FPR and cannot justify our1e-4 operating point.",
    "P3 preserved; proposed/deferred behind P1 and P9; excluded.")

add("MBRS", "mbrs.txt", "2108.08211v1", "ACM Multimedia2021 oral, official README.",
    "§§3.1–3.3,4.1–4.2; official README, repository tree and release metadata.",
    "Encoder/decoder learning mixes realJPEG, simulatedJPEG andidentity mini-batches. Its 'diffusion block' spreads message features; it is not training against diffusion-model regeneration.",
    "Paper settings64bits128×128 and625bits400×400; strength1. Official release also has30bits128(FC256) and256bits256 variants. Their native payloads and quality must not be interchanged. Decoder binary message/BER, no universal native image-presence threshold or ECC guarantee. RGB resizing, checkpoint-specific normalization and output rounding require configuration-level verification before use.",
    "jzyustc/MBRS@2bab0df66480f66cfdef534d38c851354ee2c6aa. Official code and GoogleDrive weights folder https://drive.google.com/drive/folders/1A_SAqvU2vMsHxki0s9m9rKa-g8B6aghe?usp=sharing. No LICENSE file in inspected tree/API license null; license unverified, not MIT by assumption. Checkpoint hashes/immutable revisions unresolved.",
    "Original5kCOCO test after10kImageNet training:JPEGQ50 BER<.01% atPSNR>36; no original diffusion-regeneration result. VINE30-bit Table1 gives99.53/99.35% stochastic/deterministicTPR@.1%, butPSNR27.37,SSIM.894,LPIPS.1877, under VINE conditions/count conflict. WAMTable9's256-bit repeated-message configuration givesDiffPureBA100/99.5/85.1/64.8 andVAE100/100/100/97.7. Differentpayload/quality/noiser settings forbid a single pooled 'MBRSrobustness' number.",
    "VINETable7 .0053s,938MB onQuadroRTX6000 mean1000; originalRTX2080Ti100epoch training is not inference. No target-server measurement.",
    "A legitimate historical post-hoc baseline and cautionary example of payload/quality confounding. No new proposal because license and exact variant are unresolved and P1/P2 cover the conventional family.")

add("SSL", "ssl.txt", "2112.09581v1", "ICASSP2022, official README citation.",
    "§§3.1–3.4,4.1–4.3; official README/LICENSE and DINO/normalization asset listing.",
    "Optimizes image pixels so whitened self-supervised DINO features align with a secret direction or multiple orthogonal message carriers; differentiable augmentations improve stability.",
    "DINOResNet50 2048-d features withPCA whitening;100Adam steps atLR.01,SSIM mask andPSNR constraint. Zero-bit cone threshold has analyticFPR1e-6; multibit signs on orthogonal carriers (30bits inVINE) are a different endpoint. Native image resolution and whitening bank are experiment-specific; COCO128 comparison atPSNR33 differs from highresolutionnatural-image banks. Detector requires secretcarrier and whitening statistics, not an enrollment registry.",
    "facebookresearch/ssl_watermarking@3e65334bd28ecbc66756f0179def9dc4c88a6acc, CC BY-NC4.0 (actualLICENSE inspected). Official dino_r50_plus.pth and out2048_yfcc_orig.pth under https://dl.fbaipublicfiles.com/ssl_watermarking/; README distinguishes resizedYFCC andCOCO whitening. Immutableweight hashes unresolved; no download.",
    "Original1000YFCC,118CLIC and1000COCO128 evaluations concern conventional distortions, not diffusion regeneration. Zero-bit FPR check0/100kYFCC and1/1281167ImageNet, not a guarantee after model/domain change. Third-partyVINE30-bit Table1 stochastic1.76%,deterministic9.70%TPR@.1%;PSNR41.77/.9796/.035 underVINEconditions/count conflict. WAMTable9DiffPureBA99.2/63/54.2/52,VAE98.4/97.6/66.8/51.6, different benchmarkconfiguration.",
    "VINETable7 2.1938s/1072MB,QuadroRTX6000,1000mean; iterativepixeloptimization is slower than feedforward comparators. No currentservermeasurement.",
    "Useful optimization-family coverage but weak third-party regeneration and additional secretcarrier/normalization state lower priority.")

add("SimuFreeMark", "simufreemark.txt", "2511.11295v1", "arXiv preprint2025; venue not verified.",
    "§§3.2–3.3,4.1–4.2,Tables1–2.",
    "Splits low/high spatial frequencies; a learned residual in a frozenSDVAE low-frequency latent carries the message, while original high-frequency content is restored. Decoder reads low-frequency image features without a generative editor in training.",
    "512images,64rawbits,central20%FFT low-pass,latentresidualalpha=.2,pixelrange[-.5,.5],CNNsigmoid roundedbits. No native FPR-calibrated presence threshold orECC specified. Exact clamp/resize/quantization in executable release cannot be verified because no official release was found.",
    "No official code/weights discovered by exact-title web and GitHubrepository search (zero results). Version/license/checkpoint are unavailable; paper accessibility does not license an implementation. No training attempted.",
    "20kCOCO training,1000UltraEdit test withinstructions/masks. Table2 SDIP+ full-image inpaint/regeneration strengths.1/.3/.5 ->BA97.64/94.05/92.25%;InstructP2P90.42%. QualityPSNR39.19/SSIM.990. These are bit accuracies, notTPR; native negative calibration absent. Exact modelrevision,sampler,steps,prompttext andper-strength seedcounts not fully specified. Same-family surrogate evidence does not establish SDXLtransfer.",
    "TrainingRTX3090 reported; no inference time/peakmemory. Qualified estimate:VAE forward+smallCNN+FFT with no iterative denoising at embedding, but runnable costs remain unknown.",
    "Strong mechanism match to encoder-transfer question; high literature priority, low executable priority until official checkpoint release. Not added as a numbered proposal.")

add("SpecGuard", "specguard.txt", "2510.07302v1", "ICCV2025, official repository title.",
    "§§3.1–3.3 includingEqs13–17/Algorithm1;§§4.1–4.6;Appendix12.2/Table9 attack settings.",
    "WaveletHH decomposition and spectral projection embed messages with a learnedconvolutional encoder and spectral threshold decoder. High-frequency model rhetoric must be distinguished from its reported regeneration metric.",
    "Radius100,32convchannels,watermarkstrength20,theta initialized.001 and learned;payload48/64/128/256 (Table1 also30-bit comparisons across256/512/1024). Algorithm1 thresholds extracted spectralvalues by learnedtheta; this is bit extraction, not presence calibration. Exact checkpoint preprocessing and theta unavailable. Main128-bit qualityPSNR42.89/SSIM.99/BRA.99; cannot assume everypayload uses samequality.",
    "inzamamulDU/SpecGuard_ICCV_2025@eebe26e12c0647f7aebb060e7fabf90d4931783e, MIT LICENSE verified. Inspected repository contains README/assets/license; baseline/fullcode/modelweights checklist remains TODO and README says codebase not fully updated. Thus no runnable official model release verified despite the repository being public.",
    "Table3 AvgP:RegenDiff.982,DiffP.982,VAE.995,KLVAE.990,Rinse2x.993,Rinse4x.992. These are WAVES-style performance/quality summary metrics (Q@.95/.7,AvgP/AvgQ), not unconditionalTPR@1e-4. AttackTable9:diffusion40–200steps;promptedvariant40–200;VAEquality1–7;KLVAEbottleneck4/8/16/32;Rinse2SD1.4 twice20–100steps,Rinse4 fourtimes10–50. DatasetsCOCO/DiffusionDB/DALL-E3; exactmaincount,modelrevisions,sampler,prompttexts,negativecalibration not fully reported. The200 count in social-media experiment must not be transplanted here.",
    "25kCOCO training300epochs,multipleRTX2080,batch32; no verified inferencebenchmark. Qualified estimate spectraltransforms+CNN may be inexpensive, but absent model prevents reliableVRAM/time.",
    "Recent robust-method coverage is satisfied by fulltext inspection, not by trusting abstract performance. Do not recommend execution until actual model and metric definition can be reproduced.")

add("Pixel-Seal", "pixelseal.txt", "2512.16874v1", "arXiv2025; a later venue is not verified here.",
    "§§4.1–4.4,5.1–5.3,Tables1–2; officialVideoSeal README/LICENSE and pinnedpixelseal.yaml.",
    "Adversarial-only image watermark training, three-stage schedule, high-resolution JND/residual adaptation. Distinct43.8M U-Net and33.4M ConvNeXt-v2Tiny form a post-hoc image model; video temporalpooling is outside this proposal.",
    "Native256rawbits; processing256,training resolutions256–768,scaling_w=.2,scaling_i=1,additiveblending,JND jnd_1_1,boostbeta1. ReleasedYAML args.nbits=256; nested16-bit template entries require loaderoverride verification before futureexecution, not reducingnativepayload. Full-image residualupsampling preservesoriginalresolution. Native metricsBA andbinomiallog10p; no fixed empiricalpresence threshold. An optional common1e-4 queried-message comparison would require deriving the256-bit threshold beforeoutputs and retaining nativep/BA; it is not thepaper'sdefault.",
    "facebookresearch/videoseal@870ca7fb33578b90f14c602016b6c2788096226e, officialREADME explicitly MIT code AND models; actualLICENSE inspected. Modelcard videoseal/cards/pixelseal.yaml points to https://dl.fbaipublicfiles.com/videoseal/pixelseal/checkpoint.pth. Code/card pinned; checkpointURL is mutable and itsSHA256/size notverified withoutweightdownload. No runnableinstall or weights fetched.",
    "No diffusion-regeneration result in inspectedpaper. Imageevaluation1000MetaAI1280×1280 and100SA-1b highresolution photos; conventional/geometric/compression+brightness compound attacks. Table2 onMetaAI qualityPSNR48.9,SSIM.9905,LPIPS.0013,JND.34. Compound imageattackBA remains>90% whilepayload256 versusInvisMark94effective, but this cannot predictSDXLregen. Native logp uses binomialchance, not empiricalC0calibration. No model/strength/sampler/prompt regeneration tuple exists.",
    "No inspected inference time/peakVRAM. Parameter-only fp32 storage lowerbound77.2M×4≈308.8MB excludesactivations/framework. P9 limited workload:60clean+180R1.2markedregenerations, shared180C0 decoderqueries andwrong-ownerreadout reuse; estimate180×(8–20s)/3600 +.15h=.55–1.15h, round planning allowance .55–1.25h. This is a conservative scenario assumption, not measured cost; at$1/h equals$.55–1.25, not authorized spending.",
    "P9 adds a modern strongquality/largepayload releasedbaseline, not known regeneration superiority. Fixedall60sources atR1.2seeds12/13/14 only; no extra strengths,rinse orothergenerators. Requiresuserapproval and aggregatebudgetrevision beforeexecution.",
    "P9 proposed, excluded from core; practical rank2 afterP1.")

add("JigMark", "jigmark.txt", "2406.03720v1", "arXiv2024; venue not independently verified.",
    "§§4.1–4.2,5.1–5.4,Table3;AppendixD.3–D.4,F.1,Tables7–9; officialREADME/LICENSE.",
    "Key-conditioned jigsawshuffle plus neuralresidual encoder andbinarycontrastive detector; learns fromblack-box editedimages andhuman-aligned variation scores.",
    "Zero-bit model with4×4shuffle key:16! permutations≈44bits keyentropy, NOT44-bit recoverablepayload. Detector needskey; nativeTPR@1%FPR usesROCcalibration, no universalnumericthreshold. Exact image normalization/quantization/nativeinference resolution insufficiently specified in inspectedrelease; do not inferresolution frombatchsize256.",
    "pmzzs/JigMark@4e51cd1ebcf6b95ca01e286d086f9e8883df4621, MIT LICENSE. README HAV/JigMark checkpoint entries are literal '[Download Link]' placeholders; usableweights notverified. Earlier milesfun/jigmark query404 was a falselead, not officialprovenance.",
    "Table3TPR@1%:SDEdit.945,InstructP2P.953,Zero123.876,InPaint.873,DALL-E2.721;mean.874.2000ImageNet1kval images plusLLaVAcaptions; evaluated edits filteredHAV.3–.5, thereforeconditionalonacceptededitseverity. AppendixtrainingSDEdit50–80steps,strength.1–.2 ramp.2–.8,CFG5–20 andshuffledinstructions; these are not an exactfixedtestpipeline. Attackmodelrevision,sampler,permodelcount andnegativecalibrationsplit incomplete. DALL-E2 adaptation raisesTPR.824 after600updates costing$96, not zero-shottransfer. CleanqualityTable7PSNR30.1354,SSIM.89372,LPIPS.06572.",
    "Section6 about1000A100h training;Table8 fullkeyretrain40h on8A100 is a differentscope. No reliable perimageinference figure extracted. Qualifiedestimate feedforwardencoder/decoder butkeytraining andunreleasedweights dominatecost.",
    "Publishedrobustness is conditionedonHAVselection andpermissiveFPR withmuchlowerquality. Distinctdetectorsideinformation andblackboxadaptation are material; no additionalproposal.")

add("Robust-Wide", "robustwide.txt", "2402.12688v1", "ECCV2024 (official proceedings citation2025,pp20–37).",
    "§§3.1–3.5,4.1–4.4,Tables1/4; officialREADME/LICENSE.",
    "U-Net residualencoder andresidualblockdecoder train through a frozenInstructPix2Pix editor, allowinggradients only throughlastk samplingsteps(PIDSG); qualityloss also constrainsVAElatents.",
    "Native512×512,64rawbits,noECC/nativeFPRpresence thresholdspecified. Encoderobservescoverandmessage; decoderimageonly plusknownqueryforpresence. Exactserializedcheckpointpreprocessing/rounding remainsunverified; no substitute interpolationpolicy is authorized.",
    "hurunyi/Robust-Wide@6a2ee6c991b27f36f2980a7de5c6d7b064c9fa11,MITLICENSE. OfficialweightsGoogleDrivefolder https://drive.google.com/drive/folders/1Y67UuFQiWqX5mA_1TBUs9FB4OUvazrZe?usp=drive_link; immutableartifacthash unresolved.",
    "20ktrainingpairs;1200nonoverlaptest;realstudy30images×6instructions×8samples=1440edits. InstructP2P Euler20steps,textCFG10,imageCFG1.5;Table1BER2.6579%,quality41.9142/.9910;realBER2.6062%,quality41.4038/.9922. Table4 SDEditDiffusersstrength.2,promptNull,otherdefaults: Noise+DenoiseI(beforeediting)BER8.6401%,II(onmark)3.9071%,III(afteredit)9.3654%. ExactSDrevision,sampler/defaultsteps notspecified inthatattackparagraph. BER is notTPR; unmarkedbiterror near50%is not calibratedlowFPR.",
    "A6000 training,batch2,20kimages reported; no inference time/VRAMbenchmark. Qualifiedestimate onefeedforwardencoder/decoder; diffusiontrainingcost not paidinferencecost whenofficialweightsavailable.",
    "A strong editing-awareposthocmethod and plausiblefutureQ1baseline; releasedartifactpin gap and same-familytrainededitor must be stated. RankafterP1/P9/P2 forfuturefollowup, no newnumberedproposal.")

add("SpreadMark", "spreadmark-v2.txt", "2608.03165v2", "arXiv2026 preprint; v2 inspected and differs numerically fromv1.",
    "Method 'Spread-Spectrum Embedding', 'Receiver',SA-AT;ExperimentSetup,Tables1–2,Ablations andDiscussion; v1-to-v2 diff inspected.",
    "LearnedCNN residual plusfixedsecretGaussian densecodewords; matchedfilter oncover-suppressedchip fused withCNNhead; sparsification-awareadversarialtraining.",
    "30rawbits,128×128,RGB[-1,1],bilinearresize. AnalyticDA=TPRusing smallestk withBinomial(K,.5)upper-tail<=.01; consumes nocalibrationimages but doesnot proveempirical1%FPR. Fixedcodebooksecretandneverestimated isexplicitthreatassumption; no keyrotation/collusion/chosenmessage study.",
    "No officialrepository/weights discovered by exactweb/GitHubsearch. Code/weightlicense,pin,downloadability unverified. v2 source is authoritative for thiscard; do notcopyv1numbers.",
    "SD1.4WAVESimg2imgstrength.25,512attackresolutionthenbilinearbacktonative128. v2Table1/prose:COCOBA.78/DA.77;DIV2KBA.73/DA.60. Sampler,steps,prompttext/modelrevision notreported. Training4500COCO;test500COCO and claimed500'DIV2Kvalidation' images: the latter count/splitdescription needsclarification because standardDIV2Kvalidationis100; do not silentlyfix. Singletrainingrun,novariance. NativequalityCOCOPSNR30.1,SSIM.874,LPIPS.014;DIV29.4/.891/.012. At256resolution regenerationDA collapsesnearzero; do notextrapolate128resultto512. Thev1BA.85 figure must notreplacev2Table1; v2ablationstillshows.85 fordecoderpath, a differentsetting.",
    "RTX6000Ada evaluationhardware; no timing/peakmemory number. Qualifiedestimate CNN+correlationscheaprelative todiffusion, butnotexecutablewithoutmodel. Per-image costunknown.",
    "RecentT3mechanismcoverage, butunreleasedmodel,lowresolution,lowerquality,analyticFPR andcodebooksecrecy prevent a readybaselineproposal. Avoidcausalclaimthatspreadingalonecausesrobustness.")

add("NAWE", "nawe.txt", "2609.25972v1", "arXiv2026 preprint; venue unverified.",
    "§§3.1–3.3,4.1–4.4,robustnessgrid andOFAT evaluation.",
    "Analyticperiodiccarrier withCRC/Polar coding andnonce-derivedlayout; frozenGS-DRUNet suppresseshostcontent; autocorrelation/RANSAC synchronizegeometry; CRC-aidedlistdecoder recoversframe.",
    "Reference512,48payloadbits+16CRC=64frame,PolarN256rate1/4,68syncbits,separateredundancy,s2,GS-DRUNetsigma18,PSNRtarget40. Payloadrange16–256 changescode. Sharedkey,nonce/layout,synchronizationsearchandCRC are detectorsideinformation; CRCvalidity is notcryptographicauthentication or calibratedpresence. Multiplecandidate trials affectfalsepositives.",
    "No verifiedofficialimplementation/weights/release found byexactweb/GitHubquery. Publicdenoiserdependencies do notconstitute aNAWErelease. License,pin,preprocessquantization andartifacthash remainunknown.",
    "100COCOrobustnessimages+100OFAT;156arms in34families covergeometry,photometric,compression,noise andcompounddistortions. No diffusionregeneration ininspectedtestgrid. OFATmeanBER.07 isreturned-messageconditional;WER counts failures acrossalltrials. No regenerationmodel/strength/sampler/prompt/count/TPR tuple; absentC0calibration mustnotbe inferredfromCRC16.",
    "Nohardwaretiming/peakmemory benchmark. Qualifiedestimate onedenoiserplusFFT/RANSAC/Polarlists; searchfan-out makeslatencyuncertain.",
    "Usefulstructuredpayloadanddetectorsideinformationcontrast, weakdirectT3priority. Recentpreprintincluded forcoverage, notasproof ofregenerationresilience.")

add("LaWa", "lawa.txt", "2408.05868v1", "ECCV2024; officialREADME confirms.",
    "§§3.1–3.4,4.1–4.2,4.6–4.7 andFigure7; officialREADME/download.sh.",
    "Messageembeddingmodules insertedbeforelatentdecoderupsampling; frozenoriginalautoencoder. Explicitposthoc§3.3 writes x+D_watermarked(E(x))-D_original(E(x)); therefore arbitraryexistingimage support qualifies despite'in-generation'in title.",
    "48nativebits,KL-f8autoencoder,training256randomcrops;paper512evaluation with32and48 variants. ResNet50extractor. Knownmessage softmatch; Eq6 uses>=n butEq7tail uses>n, a boundaryambiguity. ExampleattributionN1e5,FPR1e-6,n45for48bits mustpreserve strict-tailcondition. It is not equivalentto1e-4singlequeryatourpayload.",
    "vbdi/LaWa@251ac11aa223e6ff12553364a65a75add5b1aecf. OfficialREADME anddownload.sh point to https://vbdai-notebooks.obs.cn-north-4.myhuaweicloud.com/lawa/pretrained-checkpoints/last.ckpt andfirst_stage_KL-f8.ckpt. No weightdownloads/hash; code/modellicense notverified (noLICENSEshown). READMEalsoasksSD1.4generationweights;posthocpathstillneedsautoencoder.",
    "Table1postgen eval1000generated512images×10messages plusnatural-imagecomparison; Figure7autoencoderattacks bmshj2018/cheng2020/KLVAE/VQVAE. §4.7 statesKLVAEf8 attackBA85%versusStableSignature55%; bmshjq8/chengq6/KL/VQf4 comparativelyrobust. Exactfigureperconditioncount/quality/scalarsnot fullytabulated; this85%is notisolatedposthoc-only evidence and mustnotbeassignedtoourarbitrary-imagearm. No diffusiondenoisingregeneration tuple. Generationtaskediting in§4.5 isnot a post-embeddingremovalattack.",
    "README trainingbatch8fits32GB; notinferencememory. Posthocrequiresoneencoderandtwo decoderpassesplusmessageextractor; qualifiedestimate heavierthanpixelCNN butwithoutdiffusionsampling. No measuredtimeavailable.",
    "Closesimportanttaxonomyomission: some'generative'papers have anactualposthocresidualpath. ItsVAEdependence andnativequality/attributionthreshold mustbe explicit; artifactlicensegaps deferproposal.")

add("Chunky-Seal", "chunkyseal.txt", "2510.12812v1", "arXiv2025 preprint; venue notverified.",
    "§5 modelarchitecture/training/Table3;§6discussion andAppendixI.1 contextualevaluation.",
    "A separatelytrainedscaledVideoSeal model:~90×largerembedder and23×largerextractor,RGBembedding ratherthanluma-only. It is a distinct1024-bitmethod instance fromPixelSeal, not anextra count foranotherreleaseofthesamepaper.",
    "1024rawbits,256processing;embedder1022.7M/extractor773.7Mparameters;gradientclipping.01 intraining. Testoriginal-resolutionSA-1b imagesusingresidualrescaling. Bitaccuracyreported; no empiricalpresence threshold. Capacityboundtheoryisnotapracticalguarantee at1e-4FPR.",
    "No standaloneofficialChunkySealcheckpoint/repository verified byexactnamesearch; baseVideoSealavailable doesnot proveChunkySealweightsavailable. PaperCC BY-NC-ND4.0 is a documentlicense, not a code/modellicense. Implementation/version/license/weights unresolved.",
    "Table3SA-1boriginalresolution:PSNR45.32±2.16,SSIM.995±.006,LPIPS.0085±.0067;identityBA99.74±.28%,overallconventionaldistortionBA99.15±.63%. Attacksrotation<=10deg,resize71–95%,crop77–95%,brightness/contrast.5–1.5,JPEG50–80,blurkernel<=9. ExactimagecountnotestablishedfrominspectedTable3. No diffusionregenerationresults; no model/strength/sampler/prompt/calibratedTPR tuple.",
    "Parameter-only fp32 storage lowerbound1.7964B×4≈7.19GB, excludingactivations; this is aderivation, notpeakVRAM. No measuredinference timing. Largearchitecture makes itcostlyrelative toPixelSeal.",
    "Addressesrecenthighcapacityomissionwithoutclaimingallbitsareequalquality. Excludedfromexecutiondueunreleasedartifact,largecostandnodirectT3evidence.")

add("GenPTW", "genptw-latest.txt", "2504.19567v2", "AAAI2026,40(5):4085–4093,DOI10.1609/aaai.v40i5.37412 (publisher discovery); evidence is arXivv2.",
    "Method:OverallFramework,MultiscaleLatentEmbedding,CAF/SF,Tamper-AwareExtractor;ExperimentalSetup,Tables1–3,ComparisonwithDeepWatermarking.",
    "Multi-scaleVAEdecoder messageinjection throughcross-attention/spatialfusion; sharedextractor recoversmessageandlocalizestamperingusinghigh-frequencyfeatures. Posthocpipeline explicitlyencodesexistingimage; tablemarksGenPTW*separately.",
    "Posthoc64rawbits512;pretrainedautoencoderwithinsertedtrainedmodules,ConvNeXt-basedmultiscaleextractor. No nativeFPRpresencethreshold orECCspecified. TamperlocalizationF1/AUC isdistinctfromwatermarkpresence. Exactpreprocessing/quantization/modelartifact unavailable.",
    "No officialGenPTWcode/weightsfound byexact-titlewebquery; sourcepin/license/checkpointhashunverified. AAAIandv2paper establishmethod/evalbutnotrunnableavailability.",
    "Table2POSTHOC GenPTW*(64):PSNR35.56,SSIM.864,LPIPS.077,SIFID.002;bitaccuracyP2P.963,SDIP+regeneration.975,SDIP.998,Lama.997. In-generationGenPTWquality39.56/.892 isNOTtheposthocnumber. Setup5000naturalCOCOtest+1000SDv2generated,all512;editingprompts/masksUltraEdit;tableposthocCOCOrow. Sampler,SDIP+strength,steps,modelrevision/per-editcountnotfullyspecified; trainingprompt'None'isnot atestpromptguarantee. NoTPR/negativecalibration.",
    "TrainingA100,batch2withgradaccum8; no reportedinference time/peakmemory. Qualifiedestimate VAEwithattentionmodulesplusmultitaskdecoder,unmeasured.",
    "Important2026posthocomission; mainin-generationqualityclaimwouldoverstateposthocquality. Below.9SSIMatnativeposthocpoint andnoofficialrelease deferproposal.")

add("DistSeal", "distseal.txt", "2601.16140v1", "arXiv2026 preprint; officialREADMEcitationyear2025 differs fromJan2026arXivdate.",
    "§§4.1–4.2,5.1–5.2,Tables1–3; officialREADME posthocimage-notebookdescription/LICENSE.",
    "Learnsalatentembedder thenoptionallydistillsintoagenerator/decoder. CountONLYposthoclatentwatermarker: officialnotebooksloadanexistingimage,encode,modifylatents,decodeandextract. Distilledin-modelvariants do notincreasecount.",
    "64rawbits; DCAE512 latent8×8×128,epsilon.5; RAR256 latent16×16×256 afterquantizationepsilon.5 orbeforeepsilon1.5. ModifiedUNetwithoutupsampling/downsampling,ConvNeXtTinyextractor. NoJNDmask inmatchedpixelbaseline;BAendpointwithoutnativepresenceFPRthreshold. DCAE/RARcodecandcodebookaredependencies,notreferenceimageenrollment.",
    "facebookresearch/distseal@d0a71cd272bb29e3b49cdc965bbaf4d24f2684ac. ActualMITLICENSE andREADMEexplicitMITcode/models inspected. Officialloader/modelcardsandposthocnotebooksavailable; checkpointtripletsreleased,butselectedposthoccheckpointSHA256/dependencylicenseandpins notfullyresolved. Paper/READMEauthor/yearmetadata differ; bibliographyusesinspectedpaperidentity.",
    "50kgeneratedimagespergeneratortestevaluation. DCAEposthoclatent:PSNR31.06,FID11.42,IS98.11,averageBA95.18%,combined84.28%;matchedpixelPSNR43.48,avg97.78%,combined97.29%. RARpostquantlatentavg93.96% versuspixel97.27%. Attacksvaluemetric/geometric/compression/combined,notdiffusionregeneration. Thus noT3model/strength/sampler/prompt/calibrationtuple. Nativequalitylowerthanstrictthesisgate.",
    "§5.2reportedCPUembedding3mslatentvs63mspixel(DCAE),17msvs41ms(RAR). These arewatermarkmodulecostsinlatentrepresentation; do notincludea freshimagecodecroundtrip/fullgenerators orclaimend-to-endCPUtime. NopeakVRAMreported.",
    "Closesa2026latentposthocreleaseomission; efficientembeddingdoesnotguaranteeend-to-endqualityorT3. Strongfuturetaxonomycomparison,butnotaddedtothischeapcore.")


# Preserve the detailed, already frozen WAM/VINE implementation notes and append
# new paper/version evidence rather than discarding earlier fidelity work.
add("EditGuard", "editguard-latest.txt", "2312.08883v1",
    "CVPR 2024, pp. 11964–11974; numerics below refer to inspected arXiv v1, not an assumed identical final PDF.",
    "Sections 3.1–3.3, 4.1–4.5, 5.1–5.4; Equation 7; Tables 2–4; Appendix A and network details; official repository README and license metadata.",
    "An invertible image-hiding/revealing network and bit embedding/recovery network jointly insert a localization image and a robust message. Wavelet coupling blocks and degradation-conditioned posterior estimation support image recovery. It marks an existing image without retraining its generator.",
    "Native 512×512 evaluation embeds 64 bits plus an RGB localization watermark, commonly a pure blue image. A separate comparison retrains at 128 pixels and 30 bits. The localization reference must be shared between encoder and decoder; this is additional detector side information. Equation 7 uses maximum channel difference >=.2 for the pixel tamper mask. README clean/degraded pipelines use mask thresholds .2/.4 respectively; neither is an image watermark-presence cutoff. No calibrated bit-presence FPR or ECC is established. Exact release normalization, resize and quantization remain unverified.",
    "xuanyuzhang21/EditGuard@174778fb371640bb31b32fcb9f7bfd440c88766b. README provides clean.pth and degrade.pth checkpoint links and test/train scripts. The inspected root has no LICENSE and official API license is null, so code/model permission is unverified. Artifact SHA-256 and immutable checkpoint versions are unresolved. README explicitly limits trained copyright robustness to Gaussian noise, JPEG and Poisson noise.",
    "Original Table 2 uses 1,000 COCO test images with SD inpainting: native 512/64-bit PSNR 37.77, SSIM .949, NIQE 4.257 and bit accuracy 99.95%; the 128/30-bit variant is 36.93/.944/5.567 and 99.89%. These are local edits, not fully specified global regeneration. Appendix AGE-Set-C construction uses over 30,000 512-pixel COCO/CelebA images with several editing tools; it is not a 30,000-image calibrated detection trial. Third-party OmniGuard Table 3 evaluates 1,000 512-pixel UltraEdit images: EditGuard bit-only SD Inpaint* regeneration BA .623 (quality 42.15/.986), dual-watermark BA .617 (37.53/.936). Exact attack model revision, strength, sampler, steps and prompt strings are not supplied; paired dataset prompts are used. No TPR/FPR calibration is established.",
    "Original training is 250,000 Adam iterations at batch size 4. No sufficiently conditioned inference timing or peak VRAM was found. A full dual-watermark inference path includes extra invertible/localization modules beyond the bit decoder; training cost is not inference cost.",
    "A legitimate post-hoc comparator previously missed, but its primary scope is local tamper localization. Side information, weaker global regeneration evidence and unresolved licensing keep it outside the current proposal set.")

add("OmniGuard", "omniguard.txt", "2412.01615v2",
    "CVPR 2025, pp. 3008–3018; inspected arXiv v2.",
    "Sections 3.1–3.6 and 4.1–4.4; Tables 2–5; Appendix A.1–A.4 and B–C; official README, API metadata and app.py.",
    "A proactive dual-watermark network combines an adaptive localization watermark with a robust bit encoder; a passive degradation-aware transformer extracts tamper masks without the original localization reference. Training simulates global editing with frozen SD1.5 VAE reconstruction and local removal, each with probability .5. Only the robust-bit path is relevant to this T3 study.",
    "The paper evaluates 100 raw bits at 512×512, both alone and jointly with a localization image. A MUNIT-based U-Net encoder and ResNet50 sigmoid extractor use resolution scaling; the mask network pads to 1024 and uses window size 14. No numerical calibrated image-presence threshold or ECC is specified. Exact encoder/decoder internal size, quantization and normalization need a faithful release adapter. Unlike EditGuard, mask extraction is blind to the original localization image, but localization accuracy is still a separate endpoint.",
    "xuanyuzhang21/OmniGuard@2e3c86b3650cb904d2a8a112c640a78895aa93eb. README offers checkpoint.zip through PKU Disk and Google Drive https://drive.google.com/file/d/1khdBDUDIRIhPIKlV0ictcbTdWLh-WFY_/view?usp=sharing and says full training/testing will be released later. No LICENSE in inspected root; official API license is null. The inspected app.py loads a WAM model from a hard-coded local path as well as OmniGuard modules; this demo is not evidence of a self-contained faithful 100-bit adapter. Checkpoint identities/hashes and code/model licenses remain unresolved.",
    "Table 3 uses 1,000 512×512 UltraEdit images with paired prompts. Bit-only quality is PSNR 42.33/SSIM .992 and BA .981 for InstructPix2Pix, .989 for SD Inpaint* regeneration, .996 for local SD Inpaint. Dual watermark quality is 41.78/.989 with BA .979/.988/.995 respectively. SD Inpaint* regenerates conditioned on a mask, whereas local SD Inpaint preserves untouched pixels. Exact attack strength, sampler, steps and model revisions are not supplied; this is not an empty-prompt SDXL img2img test or a calibrated TPR. Separate localization testing uses 1,000 COCO examples, so those counts/endpoints must not be merged.",
    "The paper reports training iteration time .16 seconds per sample versus Robust-Wide 3.675 seconds, and says training can fit an 11 GB GTX1080Ti. General experiments used a 3090Ti server. These are training statements, not inference time or peak VRAM. No target-server measurement exists.",
    "This is a strong relevant omission to close: it shows VAE-surrogate training and global regeneration results in a post-hoc dual-watermark method. A later expanded benchmark should resolve its partial release, WAM demo dependency and licensing first; no new proposal or core arm is added.")

add("SNW", "snw.txt", "2609.34744v1", "arXiv September 2026 preprint; no verified final venue.",
    "Sections 2 through 4, 5, 6.1 through 6.2; Appendix C.1, F, G and H.2; Table 6. Method, evaluation and security scope were read, not only the abstract.",
    "The authors adapt PixelSeal's U-Net embedder and ConvNeXt extractor to a 768-dimensional continuous unit-vector channel. A keyed semi-orthogonal matrix rotates a codeword into a secret subspace, with an orthogonal Gaussian component. Alignment, isotropy and quality losses train the channel; a separate anti-spoof loss targets residual transfer. It explicitly marks existing images. Continuous messages are allowed by the formulation, but the reported evaluation uses binary codewords.",
    "The channel dimension L is 768. Evaluation uses M'=L and alpha=1, so the tested physical codeword has 768 bits. Abstract maximum capacity 656 and table-specific capacities are different quantities. All compared methods are rescaled to 48 dB PSNR, and decoder features are whitened using statistics from one million unmarked MFlickr images. This is a modified operating point and extra calibration side information. The key, codebook and expected codeword support attribution. No universal numerical image-presence cutoff, empirical FPR or implemented practical ECC recovery is established. Reported Shannon capacity is derived from empirical bit accuracy under an independent-bit assumption; it is not recovered useful payload or TPR.",
    "No official implementation, checkpoint or corresponding code/model license was established from the inspected paper and exact-name release searches. The arXiv document license is not a code license. A faithful implementation would be new work, not a runnable native release. PixelSeal's official release does not release SNW-specific learned weights or whitening statistics.",
    "General evaluation uses 1,000 MFlickr images at 1,024 pixels and COCO training; at 48 dB, reported LPIPS is .0047 for SNW versus .0034 for PixelSeal, .0025 for VideoSeal and .0010 for TrustMark. Appendix H.2/Table 6 instead uses 200 MFlickr images. Its entries are rate/capacity bits, NOT bit accuracy: SNW identity .892/684.7, VAE .495/380.3, Sana 2 steps .479/368.1, 4 steps .388/298.3, 8 steps .145/111.5, 10 steps .068/52.2 and 20 steps .001/.8. PixelSeal gives identity .939/240.5, VAE .555/142.0, Sana 2 .519/132.8, 4 .357/91.3, 8 .076/19.4, 10 .025/6.4 and 20 .003/.8. The text describes a frozen-VAE roundtrip and DiffPure inversion of the last t steps followed by regeneration. Exact checkpoint/VAE, strength, sampler, prompts and seed replication are not established; Sana step labels must not be mapped to our SDXL strengths. These capacity estimates are neither calibrated detections nor a native PixelSeal result. Appendix G's 200-image residual-transfer experiment reports spoofed capacity 86.5 bits for vanilla SNW and .2 for anti-spoof training, versus identity 678/682.2. This is a specific attack, not a general forgery guarantee.",
    "No adequately conditioned end-to-end inference time or peak VRAM was established. The PixelSeal-family backbone plus key transforms and whitening suggests feed-forward inference, but this is an architectural inference, not measured target-server cost. Training cost and parameter storage cannot replace that measurement.",
    "A recent distinct post-hoc method closes a search gap and supplies qualified third-party PixelSeal regeneration evidence. The covariance/PCA security statement is conditional on its statistical model; Section 2.3 explicitly separates adversarial robustness from its security scope. Capacity, whitening and attack settings limit transfer to our study. No extra proposal or core arm is added.")

TITLE_OVERRIDES = {
    "ZoDiac": "Attack-Resilient Image Watermarking Using Stable Diffusion",
    "Chunky-Seal": "We Can Hide More Bits: The Unused Watermarking Capacity in Theory and in Practice",
    "NAWE": "NAWE: Digital Watermarking with Neural-Assisted Watermark Extraction",
}
for m in METHODS:
    m["title"] = TITLE_OVERRIDES.get(m["name"], m["title"])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cards = TOPIC / "cards"
    cards.mkdir(exist_ok=True)
    polish(METHODS)
    enrich(METHODS)
    for m in METHODS:
        path = cards / (m["name"] + ".md")
        source = CACHE / "T3b" / m["source_file"]
        body = f"""# {m['name']}: inspected method and evaluation

Evidence level **V2**. Inspected {DATE}; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **{m['title']}**. Version/date: {m['version_date']}. Venue: {m['venue']}

Authors: {'; '.join(m['authors'])}. Year: {m['year']}. DOI: {m['doi'] or 'not established for this inspected version'}.

Stable ID: `{m['stable_id']}`. Citekey: `{m['citekey']}`. Canonical URL: {m['canonical_url']}

Primary full text: https://arxiv.org/html/{m['arxiv']}

Cached text: `{source.as_posix()}`
SHA-256: `{sha(source)}`

Actually inspected: {m['sections']}

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

{m['mechanism']}

## Native operating point and detector side information

{m['native']}

## Code, weights, pinned release and licenses

{m['release']}

## Published evaluation and regeneration conditions

{m['regeneration']}

## Cost and uncertainty

{m['cost']}

## Limitation and design implication

{m['implication']}

Disposition: **{m['ranking']}**
"""
        if m["name"] in ("WAM", "VINE") and path.exists():
            old = path.read_text(encoding="utf-8").split("\n<!-- STAGE1B DEEPENING -->")[0]
            body = old + "\n\n<!-- STAGE1B DEEPENING -->\n\n" + body
        path.write_text("\n".join(line.rstrip() for line in body.splitlines()) + "\n", encoding="utf-8")
        m["card_path"] = path.relative_to(TOPIC).as_posix()
        m["primary_text_sha256"] = sha(source)
    (TOPIC / "methods.json").write_text(json.dumps(METHODS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (TOPIC / "method-comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(METHODS[0]))
        writer.writeheader()
        writer.writerows(METHODS)
    print(json.dumps({"cards": len(METHODS), "paths": [m["card_path"] for m in METHODS]}, indent=2))


if __name__ == "__main__":
    main()

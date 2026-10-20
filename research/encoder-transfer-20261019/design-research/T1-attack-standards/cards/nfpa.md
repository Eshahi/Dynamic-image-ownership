# The Future Unmarked: Watermark Removal in AI-Generated Images via Next-Frame Prediction

ID: `nfpa`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Huming Qiu; Zhaoxiang Wang; Mi Zhang; Xiaohan Zhang; Xiaoyu You; Min Yang
Version/date: Official NeurIPS2025 proceedings PDF; exact publication day/version not stated. Venue: NeurIPS2025, final proceedings PDF.
Primary: [https://proceedings.neurips.cc/paper_files/paper/2025/file/b48405307576689bea14d221ccba73ae-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2025/file/b48405307576689bea14d221ccba73ae-Paper-Conference.pdf); [inspected full text](https://proceedings.neurips.cc/paper_files/paper/2025/file/b48405307576689bea14d221ccba73ae-Paper-Conference.pdf). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-nfpa.pdf`. SHA-256: `fb07425e8f44b564920b8455ec48e8819d28a8671d0dc03f09167eda161e2eea` (48691983 bytes).
Inspected: Section3 pp4-6; Section4 pp6-8,10; AppendixB p22, limitations p26; Table1/Figure5 visually checked PNG pp8/10.

## Mechanism and attacker access

Training-free next-frame prediction: invert the input, optimize bounded optical flow to change latent features, then use frame attention conditioned on the first frame to preserve semantics. No target watermark/detector knowledge.

## Models

SD2.1-base; ablationsSD1.4/1.5/2.0/2.1

## Strength / noise

Motion bound delta40 pixels eachaxis; x/y/xy; baselineDA noising100

## Sampler / steps / optimizer

DDIM inversion10 and denoising10 default; original generation50

## Prompt / guidance

Empty inversion prompt; reconstruction prompt not separately specified

## Resolution

Exact resolution not found in inspected setup; do not infer512 from model name

## Image counts and units

1,000watermarked images/method x8;FID/CLIP against1,000correspondingCOCO2017 realimage/text pairs

## Metrics

TPR@1%FPR;FID,CLIP;PSNR/SSIM explicitly excluded

## Conditioned numerical results

Table1 NFPA-xy meanTPR.04 vsDA.46,CtrlRegen+.39,IRA.05; Tree-Ring.07 vsDA.92;StegaStamp.02 vsDA.72;N1,000/method. Figure5 SD2.1Tree-RingFID69.18/CLIP.33

## Limits and unresolved conflicts

Semantic-level quality omits paired pixel fidelity; FID compares to realCOCO distributions, not identical source reconstruction. SD1.x/2.x backbone ablation does not establish independently trained encoder ancestry.

## Consequence for this design

Same-view regeneration and next-frame prediction answer different identity questions; retain strict paired quality reports and no new core attack.

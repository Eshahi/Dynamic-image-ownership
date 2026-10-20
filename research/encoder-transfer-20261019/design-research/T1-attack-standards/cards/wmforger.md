# Transferable Black-Box One-Shot Forging of Watermarks via Image Preference Models

ID: `wmforger`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Tomáš Souček; Sylvestre-Alvise Rebuffi; Pierre Fernandez; Nikola Jovanović; Hady Elsahar; Valeriu Lacatusu; Tuan Tran; Alexandre Mourachko
Version/date: 2510.20468v1; 23 Oct 2025. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2510.20468v1](https://arxiv.org/abs/2510.20468v1); [inspected full text](https://arxiv.org/html/2510.20468v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-wmforger.html`. SHA-256: `4f02d93a26bbe904ae93d23e1bf2aa447c670cf4fe2f90466eec1a0cd0b8c001` (296720 bytes).
Inspected: Sections3-4.1; Table6; AppendicesB-C web298-318.

## Mechanism and attacker access

A clean-image preference model guides pixel optimization without target decoder; synthetic Fourier perturbations train preference. Forgery additionally uses a marked reference.

## Models

ConvNeXtV2-Tiny; CIN/MBRS/TrustMark/VideoSeal

## Strength / noise

Training synthetic amplitude.05, not attack budget; attack k50-500

## Sampler / steps / optimizer

SGD lr.05,50-500 steps; preference training AdamW1e-5,120k steps

## Prompt / guidance

N/A pixel preference optimization

## Resolution

768x768

## Image counts and units

100 SA1b validation images per watermark; shared message

## Metrics

BA; PSNR relative to clean original

## Conditioned numerical results

Table6 k500 BA.82/.64/.60/.49 for CIN/MBRS/TrustMark/VideoSeal; meanPSNR31.2dB. k50 BA1/.83/.95/.85,PSNR38.8.

## Limits and unresolved conflicts

BA alone does not give FPR-calibrated removal. Downstream FLUX-dev last3-step baseline called DiffPure is not original pixel DiffPure.

## Consequence for this design

Keep optimizer/model-based threat distinct from fixed SDXL transfer.

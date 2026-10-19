# zhang2024dualdefense — V2 preprint; final journal evaluation V1

Yunming Zhang et al. *Dual Defense: Adversarial, Traceable, and Invisible Robust Watermarking Against Face Swapping*. IEEE TIFS19,4628–4641,2024; DOI[10.1109/TIFS.2024.3383648](https://doi.org/10.1109/TIFS.2024.3383648). [Author publication record](https://github.com/Xming-zzz/DualDefense). Inspected [arXiv2310.16540v1](https://arxiv.org/html/2310.16540v1), §§III–V, TablesII–VIII,18 October2026. Preprint has seven authors; final author list differs and must not be silently conflated.

Existing faces: train a watermark encoder against a white-box FaceSwap model, coupling adversarial feature impersonation with recovery before/after swapping. Learned extractor needs no content registry. Thirty-bit payload; VGGFace2/CASIA-WebFace160²; per-character60/20/20 split, absolute test counts unreported in inspected setup.

TableII VGGFace2 in-domain clean PSNR31.782/SSIM.917, watermark accuracy.996 before and.923 after swapping. These are recovery metrics, not calibrated wrong-owner rates. TableVII's no-adversarial-loss ablation reaches42.112dB but loses the disruption objective. JPEG/noise/resize, task and dataset transfer, and ablations are reported; diffusion regeneration is absent.

Norm: report competing objectives and ablations rather than combine best quality from one configuration with robustness from another. Final TIFS evaluation remains an access/version gap.

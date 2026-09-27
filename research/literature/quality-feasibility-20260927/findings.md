# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- C4-FREQMARK-QUALITY: FreqMark reports DiffusionDB-source quality PSNR31.20/SSIM0.854; its VAE reference31.22/0.879 misses our targets too. [freqmark-image-v1; contradicting; direct-evidence; confidence high]. Limitations: Author results, different pipeline; not our reproduction.

- C4-FREQMARK-NOT-DROPIN: The inspected method uses a DINOv2 decoder and500 freshly generated images from DiffusionDB prompts, not our existing-image blind-DCT profile. [freqmark-image-v1; inconclusive; direct-evidence; confidence high]. Limitations: Cannot transfer numerical fidelity or detection to our native datasets.

- C4-VINE-ATTAINABILITY: VINE-B reports40.51dB/0.9954/0.0029 and VINE-R37.34dB/0.9934/0.0063, contradicting blanket impossibility of the three quality values. [vine-v1; contradicting; agent-inference; confidence high]. Limitations: Author-reported means over10000 paired images, not every-image guarantees or our results.

- C4-VINE-NOT-DROPIN: VINE adds trained encoder-decoder skips, fine-tunes generative components, uses a ConvNeXt neural detector and resolution scaling; it does not validate our fixed SD1.5/blind-DCT route. [vine-v1; inconclusive; direct-evidence; confidence high]. Limitations: Replacement/training/resource/scope review is required before adoption.

# Gaussian Shading: Provable Performance-Lossless Image Watermarking for Diffusion Models

Primary source: https://arxiv.org/html/2404.04956v1

Inspected: Sec.3.2-3.4; Sec.4.1/Table1; Sec.4.5-5. Full-text artifact/checksum in paper JSON and inventory.

Repeats a 256-bit payload 64 times (fc1,fhw8,l1), stream-encrypts, samples Gaussian quantile intervals (one bit means sign), then standard denoising. Detector needs model, secret cipher key/nonce, payload reference and 50-step DDIM inversion with empty prompt/CFG1. Table1 SD1.4/2.0/2.1 clean TPR1; averaged nine transformations TPR .997/.998/.996 and bit accuracy .9753/.9749/.9724. Inversion attack flips latent signs; Fig7c reports reliable extraction below flip rate .4, which is not img2img strength .4. Sec4.5 explicitly admits prompt-change forgery can frame the prior owner.

Limitations: Assumes private diffusion model; stream key management required. Repeated-key or nonce misuse invalidates security reasoning. Reported .4 is sign flip rate, not regeneration strength.

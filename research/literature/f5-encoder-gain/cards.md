# Family 5 literature cards (opened 2026-10-05 by Claude)

## Zhao et al., Invisible image watermarks are provably removable using generative AI (arXiv 2306.01953, HTML v3)
- Claim: regeneration x' = A(phi(x_w) + N(0, sigma^2 I)) is certified watermark-free with trade-off f(e1) = Phi(Phi^-1(1 - e1) - L Delta / sigma) (Theorem 4.3).
- Mechanism: Gaussian mechanism in the embedding space; assumes a local watermark-specific Lipschitz bound ||phi(x_w) - phi(x)|| <= L ||x_w - x||.
- Use here: the bound weakens as L grows; family 5 maximizes L along a keyed latent direction of the SD1.5 VAE encoder.
- Limit: an upper bound on detectability, not a survival guarantee; survival was measured.

## Salman et al., Raising the cost of malicious AI-powered image editing (PhotoGuard, arXiv 2302.06588, HTML)
- Encoder attack: delta = argmin over ||delta||_inf <= eps of ||E(x + delta) - z_targ||^2, eps = 16/255, 200 PGD steps, step 2/255; disrupts Stable Diffusion edits.
- Use here: evidence that small pixel changes move the SD VAE latent far and that this survives img2img. Family 5 uses the same sensitivity constructively, with a keyed target and a far smaller L2 budget (52 dB PSNR).

## Guo et al., FreqMark (arXiv 2410.20824, NeurIPS 2024, HTML)
- Mechanism: optimizes a perturbation of the FFT of the SD VAE latent; the watermarked image is the decoder output D(FFT^-1(F_z + delta_m)); extraction by DINOv2-small features against fixed directions.
- Reported: about .93-.97 bit accuracy (48 bits) under VAE and diffusion regeneration.
- Difference from family 5: writes through the decoder and reads with another network; family 5 writes through the encoder's gradient and reads with the attacker's own encoder.

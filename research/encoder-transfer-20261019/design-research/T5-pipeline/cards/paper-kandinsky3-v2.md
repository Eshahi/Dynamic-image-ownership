# Kandinsky 3.0 Technical Report

[Primary source](https://arxiv.org/html/2312.03511v1). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** §3.4 image autoencoder and training passages; Table2 reconstruction evaluation, independently of the cached T2 card.

**Mechanism:** Sber-MoVQGAN is a270M-parameter image autoencoder using spatial normalization, modified VQGAN objectives and EMA. The report attributes its training to LAION-HighRes. This provides a different autoencoder lineage from SD1.5; it does not assert disjoint training images.

**Evaluation reread:** Table2 compares reconstruction on ImageNet, including the270M16,384-codebook model (latent32×32), FID.686, SSIM.741, PSNR27.04. These author-reported reconstruction numbers are not the effective fp16 inference precision, measured VRAM or output quality of our proposed1024 path.

**Audit use / limits:** motivates the optional MoVQ comparison. Actual diffusers0.35.1 img2img bypasses codebook quantization at decode and uses continuous encoder latents. Thus even an author VQ reconstruction table cannot be imported as a benchmark of this exact continuous pipeline. No P4 model was loaded or scored.

**Read locations:** `kandinsky3-paper.read.txt:448–646` (mechanism and Table2), training passage beginning647.

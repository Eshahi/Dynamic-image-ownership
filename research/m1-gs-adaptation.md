# Gaussian Shading native baseline adaptation

Implementation: `scripts/m1_gaussian_shading.py`. Manifest: `research/m1-gs-synthetic.json`. Primary inspected method and pinned MIT official code are in `research/literature/m1-latent-survey/`.

This is an exploratory synthetic prompt-generation comparator, separate from the proposal and v5 image-domain watermark. It has no existing-photo preservation or content-bound ownership claim. It requires SD1.5 U-Net, VAE encoder, text encoder, payload reference, whitening key and per-generation nonce; extraction performs 50 U-Net calls and VAE encoding. The extractor is not lightweight image-DCT. The deterministic payload and public development keys are test fixtures, with no secrecy claim.

The payload has shape4x8x8 and is spatially tiled8x8 into4x64x64. Its 64 repetitions match official Gaussian Shading `fc=1, fhw=8, l=1`. Whitening XORs expanded bits with a domain-separated SHAKE256 stream; ChaCha20 and cryptography packages are absent in the existing science environment. This engineering adaptation does not reproduce the paper's cipher implementation and carries no cryptographic indistinguishability claim. There is no payload permutation. Latent magnitudes are independent absolute standard-normal samples and signs follow whitened bits. C0 and C1 share magnitudes, providing a reproducible generation counterfactual; semantic changes between these generated images cannot be interpreted as watermark distortion of a fixed existing photograph.

Diffusion adapts published SD1.4/2.0/2.1 experiments to the pinned local SD1.5 mirror. Sampling uses explicit existing DDIM epsilon/unclipped scheduler configuration,50 steps,CFG7.5,eta0. Detection uses current diffusers0.35.1 DDIMInverseScheduler constructed from those scheduler fields, empty prompt, no classifier-free guidance,50 inverse steps and posterior-mode VAE encoding scaled by the model scaling factor. Record both effective scheduler configs. This inverse is approximate and differs from the official legacy inversion code; clean recovery must be demonstrated before judging attacks.

Four fixed prompts and seeds1000-1003 each produce C0 and C1. Clean and deterministic VAE mode round-trip are tested. T3 uses SD1.5 img2img empty prompt/CFG1/DDIM20/eta0,strengths0.05,0.1,0.2,0.4 and matched seeds0,1,2. This yields112 image rows; each row records native bit accuracy, exact-message indicator, predeclared threshold0.7 detection, wrong-key query, image hash, detector runtime/NFE and PSNR/SSIM/LPIPS against its same-arm preattack image. C1 versus paired C0 clean quality is an explicitly different generation comparison. Safety checker remains attached for text generation, img2img and the VAE round-trip; a blocked output stops and preserves error provenance.

Threshold0.7 is fixed before execution; C0 and wrong-key frequencies have four cases per channel and cannot substantiate population FPR. No claimed binomial false-positive bound is applied to correlated repeated payload bits or public development secrets. T4/T5 content binding remains outside this native comparator.

Run provenance records commit, script/manifest SHA256, all configuration/seeds, asset lock verification, runtime versions, duration and started/completed/error state. Image and row journals support resume with identical commit/script/manifest only. Resume never silently treats error as success. Parent commits source before scientific execution; no GPU experiment was run by the implementation agent. Finite codec tests cover exact recovery,31-versus33 corrupted repeated tiles, nonce/key separation and invalid shape, and passed3/3. Those tests are implementation checks rather than scientific evidence.

Example (after parent commit):

```
W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe scripts/m1_gaussian_shading.py --manifest research/m1-gs-synthetic.json --output-dir W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261003-HHMM-gs-synthetic
```

In PowerShell quote the interpreter and output path containing spaces and invoke the interpreter with `&`.

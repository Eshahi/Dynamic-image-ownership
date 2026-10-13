# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- APT-mechanism: Latent perturbations use DINOv3 cosine hinge, worst-10% mining, noisy latent branches and uniform anchors; decoded pixels are clipped. [apt-v1; supporting; direct-evidence; confidence high]. Limitations: 

- APT-results: Table 1: APT PSNR 32.80 dB, AUC .97, IoU .90; APT* IoU .92 versus WAM .84. [apt-v1; supporting; direct-evidence; confidence high]. Limitations: Localization, not payload recovery; PSNR below 35 dB.

- APT-security: Verifier anchors are server secrets; same-image copy-move may evade localization. [apt-v1; supporting; direct-evidence; confidence high]. Limitations: 

- APT-novelty-boundary: Uniform feature alignment surviving regeneration is prior art; H1 chip-versus-symbol needs a narrower empirical claim. [apt-v1; contradicting; agent-inference; confidence medium]. Limitations: Not equivalent to E3 pixel optimization, fixed latent-DCT payload, exact 32-bit Q or public-owner verification.

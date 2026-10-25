# RingID — V2 primary-source card

Source: Hai Ci, Pei Yang, Yiren Song and Mike Zheng Shou, *RingID: Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification*, arXiv:2404.14055v2, 23 April 2024. [Inspected version](https://arxiv.org/html/2404.14055v2). Inspected 25 October 2026. Artifact/hash: manifest key `ringid`.

**Direct evidence — mechanism (§§4–5).** The analysis separates watermark-presence detection from key identification: distribution shift may help the former without discriminating keys. RingID combines heterogeneous Fourier-channel patterns, spatial shifting, conjugacy-aware drawing and discretization of initial noise. Detection still uses generator inversion and a reference keybook.

**Direct evidence — experiments (§6, Tables 1–2).** With SDv2 and 50 steps, verification uses 1,000 positive/negative images. Average verification AUC is .995 versus Tree-Ring's .975. In the 2,048-key identification setting, average accuracy is .819 versus .066 for Tree-Ring; RingID's rotation and crop-scale identification accuracies are .860 and .080 respectively. Thus strong aggregate verification is compatible with weak identification under crop-scale.

**Limits / transfer.** Appendix D's additional diffusion-model experiments reinstantiate watermark generation. They do not establish transfer of one frozen writer through independently trained autoencoders, nor separate encoder, decoder and denoiser effects.

**Agent inference for F5.** Presence, owner identification and image-record matching require separate metrics and negatives. The keybook is detector side information and should not be hidden by the phrase reference-free.

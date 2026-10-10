# MetaSeal

Zhou et al., arXiv:2509.10766v2, 13 February 2026. [Primary full text](https://arxiv.org/html/2509.10766v2). Inspected 2026-10-10: Sections 4–6 and Appendix C; citation `Zhou2026MetaSeal`.

Mechanism: sign an image caption using ECDSA P-256; encode caption plus 512-bit signature as a QR pattern and embed through a wavelet/invertible network. Verification recovers the signed message; comparison with freshly extracted suspect semantics is supplementary in Section 5.1.

Threat/numbers: the stated gray-box attacker lacks encoder/decoder parameters. Training uses DIV2K; evaluation includes natural/generated 512-pixel images. Appendix C's illustrated diffusion regeneration defeats verification: reported PSNR changes from 35.58 dB for the mark to 23.23 dB after regeneration, against the unmarked image.

Limit/use: that example is not a success-rate grid. A valid signature authenticates its recovered message, not automatically the suspect's instance identity; replay requires a defined content check. Useful attribution/capacity comparator, not a ready T3 replacement or evidence of our superiority. No files or models downloaded.

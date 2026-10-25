# WIND — V2 primary-source card

Source: Kasra Arabi, Benjamin Feuer, R. Teal Witter, Chinmay Hegde and Niv Cohen, *Hidden in the Noise: Two-Stage Robust Watermarking for Images*, arXiv:2412.04653v5, 27 April 2025. [Inspected version](https://arxiv.org/html/2412.04653v5). Inspected 25 October 2026. Artifact/hash: manifest key `wind`.

**Direct evidence — mechanism (§§3–4, Algorithms 1–2).** The complete initial noise serves as a watermark. A secret-salted hash of an index reproduces candidate noises; a Fourier group identifier accelerates search. WIND-fast searches a selected group, whereas WIND-full can fall back to exhaustive search. Detection needs model inversion, secret salt and the indexed candidate-noise construction. It does not need the original image, but does use substantial keyed reference information.

**Direct evidence — experiments (§5, Tables 1–2,4).** For 100,000 keys/2,048 groups, WIND-full averages .969 correct-watermark detection accuracy (the reported endpoint) and .930 under crop-scale; WIND-fast gives .814/.060. Recovered-noise cosine similarity averages .888 clean, .824 after regeneration and .000 for unrelated noise. Cross private/public SDv2 checkpoint inversion gives .166 versus .888 for matched private inversion.

**Limits / transfer.** A different SDv2 checkpoint is not evidence of independently trained encoder transfer. The security discussion acknowledges replay of a recovered noise (§4.2/Appendix E); cryptographic unpredictability does not itself bind noise to image semantics.

**Agent inference for F5.** Count key search and model secrecy as detector resources. Do not equate reference-free pixels with absence of references.


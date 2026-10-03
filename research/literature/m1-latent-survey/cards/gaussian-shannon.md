# Gaussian Shannon: High-Precision Diffusion Model Watermarking Based on Communication

Primary source: https://arxiv.org/html/2603.26167v1

Inspected: Sec.3.1-3.4; Sec.4.1/Table1; Fig5/Table3. Full-text artifact/checksum in paper JSON and inventory.

LDPC encodes payload, repeats codeword, pseudorandomly modulates Gaussian signs; empty-prompt DDIM inversion50/CFG1 recovers copies. Attempts individual LDPC decode, then majority plus LDPC, else verification only. SD1.4/2.0/2.1 default256 bits, redundancy16, rate .25, DDIM50/CFG7.5. Table1 average ordinary-noise exact-message recovery .968/.966/.965 versus GS .399/.387/.381. Table3 DDIM exact recovery under noise .965 versus DPM-Solver .895. Fig5 includes VAE/diffusion/embedding attacks, but does not specify an img2img-strength-compatible regeneration setting there.

Limitations: Preprint; ordinary-noise averages are not T3 guarantee. LDPC parity success alone is not cryptographic authentication. Dependent errors challenge iid communication bounds.

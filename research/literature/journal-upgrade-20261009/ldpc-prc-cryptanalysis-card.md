# LDPC-PRC cryptanalysis

Wang et al., arXiv:2512.17310v2, 15 June 2026. [Primary full text](https://arxiv.org/html/2512.17310v2). Inspected 2026-10-10: Sections 3.1, 4, 6.3 and 7; citation `Wang2026LDPCCryptanalysis`.

Claim/mechanism: concrete LDPC-PRC parameters admit partial parity-check recovery, weak-key distinguishers and noise-overlay attacks. Their soundness definition is not the attacked property; undetectability and robustness are distinct.

Threat/numbers: the image attack uses recovered code structure and differentiable image-to-codeword extraction. On 100 images, 100 PGD steps at learning rate .01 remove 67%, 89%, and 96% at L-infinity budgets 8/255, 12/255, and 16/255. These are paper results, not our experiments or a matched T3 comparison.

Limit/use: this analyzes an LDPC-based cryptographic construction, not our shortened BCH carrier. It prevents borrowing a generic PRC security label without checking actual parameters and attacker access. No additional out-of-scope attack is scheduled. No files or models downloaded.

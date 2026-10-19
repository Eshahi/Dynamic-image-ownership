# Zhou2026MetaSeal

Tong Zhou, Ruyi Ding, Gaowen Liu, Charles Fleming, Ramana Rao Kompella, Yunsi Fei, Xiaolin Xu, Shaolei Ren. *MetaSeal: Defending Against Image Attribution Forgery Through Content-Dependent Cryptographic Watermarks*. arXiv:2509.10766v2, 13 February 2026; arXiv says to appear at TMLR 2026. [Primary text](https://arxiv.org/html/2509.10766v2). V2; accessed 2026-10-18, §§4–6 and Appendix C; current version history checked.

Existing-photo protection signs an extracted caption with ECDSA P-256, encodes caption and 512-bit signature in a 53×53-module QR pattern, and embeds it through a wavelet invertible network. Detector requires that trained network and the public verification key, without a registry. The gray-box adversary knows algorithms but lacks network parameters.

DIV2K training has 800 images; validation has 100. Evaluation additionally uses COCO and generated images at 512²; those evaluation counts are unclear. Table 2 reports DIV2K PSNR 34.40 dB, SSIM .965 and perfect pattern recovery, which is not a fixed-FPR attribution estimate. Appendix C illustrates failed verification after regeneration, with PSNR 23.23 dB: one example, not an attack-success rate.

Relevance: content-bound cryptographic attribution is prior art. Our registry changes side information and regeneration tolerance; neither signatures nor caption agreement alone resolve same-instance identity or lawful authorship.

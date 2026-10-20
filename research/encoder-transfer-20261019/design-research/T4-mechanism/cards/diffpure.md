# T4-10: Diffusion Models for Adversarial Purification

- **Primary source:** [2205.07460v1](https://arxiv.org/html/2205.07460v1); authors: Weili Nie; Brandon Guo; Yujia Huang; Chaowei Xiao; Arash Vahdat; Anima Anandkumar.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `diffpure.txt` lines 153-204. **Evaluation locators:** 241-261; 546-579. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/diffpure.html`. **HTML SHA-256:** `17ab7e23ca7f120a85150c9f929b50882cc324f4d2fa753da05741bec0ba75b7`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

DiffPure adds forward diffusion noise to an adversarial input and solves a reverse stochastic differential equation before classification. Forward noising contracts distribution discrepancy under stated assumptions; purification trades perturbation removal against useful information. The method differentiates through purification with an adjoint method and tests attacks aware of randomness. An oblivious attack against a stochastic defense would be insufficient evidence.

For P5/P8, success against one frozen F5 writer is a bounded attacker result, not adaptive security. Randomness can impede a naive optimizer without removing signal. A classifier-robust encoder need not remain compatible with the SDXL decoder/UNet or preserve scene detail.

## Evaluation actually inspected

Setup covers CIFAR-10, CelebA-HQ and ImageNet and adaptive attack families including EOT, BPDA and the paper's gradient method; 512-image fixed subsets are used in evaluations. Appendix ablations vary purification time, show clean-accuracy loss and nonmonotone robust accuracy, and compare SDE/ODE variants. Twenty EOT samples are specified. These are classification results, not watermark presence or arbitrary-message experiments.

## T4 implications and falsification

DDIM eta0 is not DiffPure's reverse SDE, although posterior sampling and initial corruption still make the frozen channel stochastic. More strength is a noise/utility tradeoff, not proof that every source's C must fall. A strength 0.1-to0.2 reversal can reflect nonlinear dynamics or a read threshold; retain it honestly.

P8 requires a separate objective that suppresses F5-induced displacement while preserving reconstruction and SDXL compatibility, separate calibration data and whole-channel evaluation. If a replacement reduces C only by destroying content, the useful attack fails. If useful content is preserved and C falls relative to the matched honest encoder, it supports the mechanism against the frozen writer; adaptation remains untested. No training, timing or benchmark estimate was imported into P8.

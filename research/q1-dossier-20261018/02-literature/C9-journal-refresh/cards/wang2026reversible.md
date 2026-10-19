# Wang et al. (2026): Reversible Unlearnable Examples

**Verification: V2, version caveat.** Read III and IV of [arXiv:2608.06211v1](https://arxiv.org/html/2608.06211v1), submitted 6 August 2026. [IEEE metadata](https://doi.org/10.1109/tcsvt.2025.3619199) and the [author institution](https://research.mpu.edu.mo/en/publications/reversible-unlearnable-examples-toward-the-copyright-protection-i/) verify TCSVT 36(3), 3975–3988 (2026), online 8 October 2025, DOI 10.1109/TCSVT.2025.3619199. All authors, abstract and mechanism match; arXiv says “Towards,” publisher “Toward.” The author-uploaded text lacks an explicit journal DOI: relation is strongly supported, exact final-version equivalence unverified. Numerical statements below refer to this manuscript.

An MBRS-based encoder embeds random messages before class-wise unlearnable perturbations are added. Two extractors handle perturbed and recovered images; either matching the known message suffices. Authorized recovery additionally requires class labels and perturbations through a secure channel.

IV tests ImageNet-100, CIFAR10 and Pets; it mentions 130,000 ImageNet attack images and a 5,000-image ImageNet validation ablation. Exact watermark train/test counts and duplicate exclusion are not established. Watermark evaluation uses BER and PSNR, with 64-bit messages at 256×256 and 32-bit CIFAR messages. JPEG75, noise/filter/resize and augmentation tests appear; no fixed-FPR negative attribution study is reported. GEAA is rerun from public code with matched capacity; Adv-watermark's size prevents CIFAR comparison. Six-repeat means/standard deviations describe classifier experiments, not calibrated watermark false accepts. Hardware and a ten-day baseline cost are disclosed; end-to-end verification latency is not established. Code is linked.

**Assessment.** Low BER and classifier transfer do not establish sound owner attribution. An either-extractor decision needs joint false-positive calibration. Do not import the paper's language of “cryptographic” perturbations as a security guarantee. Its detailed mismatch disclosures are valuable reporting examples.

**Locators:** III-A/B/D/E; IV-A/B/D/E/F; Tables II, IV–IX.

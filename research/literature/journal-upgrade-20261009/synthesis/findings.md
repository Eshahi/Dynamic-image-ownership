# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- journal-waves-direct-evidence: WAVES evaluates detection at 0.1% FPR and performance across attack-quality tradeoffs; detection and identification are distinct endpoints. [waves; supporting; direct-evidence; confidence high]. Limitations: Benchmark conventions do not establish universal acceptance thresholds for a thesis; its full attack suite is outside the three-threat scope.

- journal-waves-agent-inference: Use fixed-FPR and quality-conditioned evaluation, restricted to T3/T4/T5. [waves; inconclusive; agent-inference; confidence medium]. Limitations: Benchmark conventions do not establish universal acceptance thresholds for a thesis; its full attack suite is outside the three-threat scope.

- journal-zodiac-direct-evidence: ZoDiac optimizes a Fourier ring in an inverted diffusion latent and blends the decoded image with the original; detection uses diffusion inversion. Table 3 reports Zhao23 detection 0.988 at FPR 0.062, or 0.938 at FPR 0.004. [zodiac; supporting; direct-evidence; confidence high]. Limitations: Different detector thresholds, distortion and attack settings prevent comparison of those rates with F5 source-majority counts.

- journal-zodiac-agent-inference: Include as an inversion-based post-hoc baseline, recalibrated on development/calibration data. [zodiac; inconclusive; agent-inference; confidence medium]. Limitations: Different detector thresholds, distortion and attack settings prevent comparison of those rates with F5 source-majority counts.

- journal-seal-direct-evidence: SEAL binds initial noise to caption-derived semantic codes using secret-salted projections; detection requires semantic extraction and inversion. Table 1 cat-insertion AUC is 0.551 for the basic method and 0.982 with spatial verification. [seal; supporting; direct-evidence; confidence high]. Limitations: AUC for that semantic edit is neither TPR at a fixed FPR nor the thesis copy-paste endpoint; this is a generation-time method.

- journal-seal-agent-inference: Semantic binding is prior art; use as a mechanism reference or in a separately defined generative comparison. [seal; inconclusive; agent-inference; confidence medium]. Limitations: AUC for that semantic edit is neither TPR at a fixed FPR nor the thesis copy-paste endpoint; this is a generation-time method.

- journal-grow-direct-evidence: GROW guides generation toward a terminal-latent frequency message and extracts through a VAE encoder without inversion. Its 16-bit COCO results report PSNR 27.54, SSIM 0.85, LPIPS 0.05, DiffPure message accuracy 0.95; extraction is 0.24 seconds on T4. [grow; supporting; direct-evidence; confidence high]. Limitations: Generated-image message accuracy and paper-specific hardware are not existing-photo checked detection or a local latency benchmark.

- journal-grow-agent-inference: Inversion-free latent extraction alone is not novel; measure total local detector cost. [grow; inconclusive; agent-inference; confidence medium]. Limitations: Generated-image message accuracy and paper-specific hardware are not existing-photo checked detection or a local latency benchmark.

- journal-ctrlregen-direct-evidence: CtrlRegen regenerates from clean noise using DINOv2 semantic and ControlNet spatial guidance. Table 1 Tree-Ring TPR at 1% FPR is 0.12 under CtrlRegen versus 0.87 under Regen; CtrlRegen PSNR is 19.32. [ctrlregen; supporting; direct-evidence; confidence high]. Limitations: These attack results are not F5 measurements; learned adapters and substantial distortion require a separate admissibility and resource check.

- journal-ctrlregen-agent-inference: Test a stronger controlled T3 attack only after the cheap independent-VAE test; do not infer general robustness from DDIM alone. [ctrlregen; inconclusive; agent-inference; confidence medium]. Limitations: These attack results are not F5 measurements; learned adapters and substantial distortion require a separate admissibility and resource check.

- journal-wam-direct-evidence: Watermark Anything learns localized watermark presence and message decoding. Table 8 gives PSNR 38.3, SSIM 0.99, LPIPS 0.04 and splicing bit accuracy 95.30%; Table 9 shows regeneration bit accuracy falling from 100% to 49.1% over increasing distortion. [wam; supporting; direct-evidence; confidence high]. Limitations: Localization and bit accuracy are not whole-image forgery rejection, TPR or content-binding efficacy; pretrained assets are not locally reproduced here.

- journal-wam-agent-inference: Use as a neural post-hoc comparator and a donor-delivery diagnostic, separating its localization goal from authentication. [wam; inconclusive; agent-inference; confidence medium]. Limitations: Localization and bit accuracy are not whole-image forgery rejection, TPR or content-binding efficacy; pretrained assets are not locally reproduced here.

- journal-diffmark-direct-evidence: DiffMark trains latent consistency bridges and a VAE-based 64-bit extractor without diffusion inversion. Table 2 reports TPR at 0.1% FPR of 0.81 for VAE and 1.00 for diffusion regeneration; Section 4.6 reports 16.4 ms extraction on L40S. [diffmark; supporting; direct-evidence; confidence high]. Limitations: Preprint; training and generation setting differ, exact Table 2 severity is unclear, and latency is not hardware-normalized against F5.

- journal-diffmark-agent-inference: Use as recent context for learned extraction and transfer, not a numeric claim that F5 loses or wins. [diffmark; inconclusive; agent-inference; confidence medium]. Limitations: Preprint; training and generation setting differ, exact Table 2 severity is unclear, and latency is not hardware-normalized against F5.

- journal-freqmark-direct-evidence: FreqMark optimizes latent-frequency perturbations through a frozen VAE and reads bits with fixed pretrained image features. For 48 bits and 400 optimization steps, Table 1 ImageNet reports PSNR 31.27, SSIM 0.857 and diffusion-regeneration bit accuracy 0.969. [freqmark; supporting; direct-evidence; confidence high]. Limitations: Bit accuracy is not TPR; its 60-step attack and lower fidelity are not matched to F5. Published numbers do not establish performance under our strict quality constraints.

- journal-freqmark-agent-inference: Closest prioritized post-hoc latent-frequency comparator; compare quality frontiers and separately calibrated FPR. [freqmark; inconclusive; agent-inference; confidence medium]. Limitations: Bit accuracy is not TPR; its 60-step attack and lower fidelity are not matched to F5. Published numbers do not establish performance under our strict quality constraints.

- journal-latent-watermark-direct-evidence: Latent Watermark injects a message into the terminal latent and detects with a VAE encoder and trained decoupler. It trains on 50,000 LAION images. Table 2, 48-bit COCO SD2.1 reconstruction gives 99.09% bit accuracy and 100% TPR at 1% FPR. [latent-watermark; supporting; direct-evidence; confidence high]. Limitations: Generation-time evaluation, a different operating point, and learned modules preclude direct comparison with existing-photo F5; no instance-binding proof follows.

- journal-latent-watermark-agent-inference: Further prior art against novelty claims based solely on terminal-latent or inversion-free extraction. [latent-watermark; inconclusive; agent-inference; confidence medium]. Limitations: Generation-time evaluation, a different operating point, and learned modules preclude direct comparison with existing-photo F5; no instance-binding proof follows.

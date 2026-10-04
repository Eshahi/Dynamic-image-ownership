# D: PhaseMark terminal-phase pilot results

Exploratory development pilot on sources1675/4795. Both APM and IPS completed all8 conditions per arm (C0/C1 ×clean/VAE cycle ×two sources), with four public owner hypotheses per condition. Sixteen conditions and64 queries share only two source clusters. This is a terminal-VAE phase-carrier adaptation, not an initial-noise method or a three-state/content-bound ownership detector. No images were opened for this report.

At the fixed presence cutoff82/128, correct-owner C1 detection is2/2 clean and2/2 after one VAE cycle for each arm. Exact recovery is APM2/2 clean and1/2 cycle; IPS0/2 clean and0/2 cycle. All unmarked and wrong-owner queries remain below82. The derived and source-recorded carrier gates pass for both arms, while their clean source-quality gates fail.

| Source /arm | Clean correct matches /128 | VAE-cycle correct matches /128 | Clean source PSNR /SSIM /LPIPS | Clean paired C1/C0 PSNR /SSIM /LPIPS |
| --- | --- | --- | --- | --- |
|1675 /APM|128|126|23.687 /0.7404 /0.1323|25.517 /0.8547 /0.1041|
|4795 /APM|128|128|23.480 /0.5340 /0.1741|26.594 /0.7766 /0.1275|
|1675 /IPS|126|121|24.794 /0.7652 /0.0993|27.790 /0.8912 /0.0641|
|4795 /IPS|127|125|24.182 /0.5575 /0.1434|28.677 /0.8264 /0.0925|

Clean C1 source-quality conjunction PSNR>35, SSIM>0.9, LPIPS<0.1 is0/2 in both arms. Mean source metrics are APM23.584dB/0.6372/0.1532 and IPS24.488dB/0.6614/0.1214. Paired decoder-counterfactual quality is better than source fidelity but also fails the conjunction0/2 in each arm; mean paired metrics are APM26.055dB/0.8157/0.1158 and IPS28.234dB/0.8588/0.0783. These references cannot be interchanged. C0 pure-decoder source PSNR is26.692/25.204dB and SSIM0.8183/0.5950 before any mark, so the base source-fidelity loss is already substantial; phase embedding adds measurable distortion.

For each arm, C0 positives are0/16 queries over4 unmarked conditions andfour owners; correct-owner C0 positives are0/4. Wrong-owner C1 positives are0/12 across4 marked conditions andthree wrong owners. APM's largest C0 score is79 (1675/VAE-cycle/beta); IPS's is77 (4795/VAE-cycle/delta). All marked wrong-owner scores are≤69. These repeated public hypotheses are descriptive controls, not independent population FPR evidence. APM per-condition VAE+phase extraction times are0.171–0.188s; IPS0.187–0.219s. No selected coefficient had zero magnitude in the16 condition readouts. Human visual verdict remains missing.

The observations establish clean and single-VAE-cycle carrier readout on these two images while this fixed pure-decoder configuration fails existing-photo source-quality criteria. They do not show diffusion-regeneration T3, transfer T4 or semantic-collision T5 resilience, secure content/OwnerID binding, native-resolution performance or exhaustion of PhaseMark/latent designs. Broader quality-preserving amendments remain untested.

## Provenance

MAIN `.thesis-build/dev-runs/20261003-2355-phasemark-pilot` completed at commit `c4f722e5ae0512e872ebaef0bd4b71228ea95f29` in24.453s; terminal `run.json` SHA256 `0fd2f7f8a1cdb34e6a129f753eb1f090e279cd8c1018a774a262a84bb7a123c8`. Manifest `research/m1-phasemark-dev.json` SHA256 `d6375e2f61e5c8101f7ec1df4933de770f056a25e589e4bb0c01a5263dbf3b8b`. Run records retain upstream code revision/hashes, asset receipts, image/source hashes, conditions and missing human assessments.

MAIN `.thesis-build/dev-runs/20261003-2357-phasemark-analysis` is completed descriptive analysis at the same commit; `run.json` SHA256 `5ae0fc6c0c121a80cb77180259976cf1c69d26ab18a67299d922e5563267efe0`, `analysis.json` SHA256 `50d0fa7a88489b1303a864011cd65b99b2a1e7a3b7bba3b8ab2c11144d64ccca`. All values above were checked against its condition/query inventories and the retained terminal pilot record; no scientific output was modified.

# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- TC01: Tang compares five external RRW methods using separate 1000-image BOWS2 comparison data and 256/512-bit payloads. [tang2024rrw; supporting; direct-evidence; confidence high]. Limitations: Image selection random seeds not established; not a diffusion test.

- TC02: Tang reports mean RRW-PCET PSNR40.25dB before reversible embedding and39.09dB final. [tang2024rrw; supporting; direct-evidence; confidence high]. Limitations: Mean image quality is not an all-source quality guarantee.

- TC03: Chen evaluates four external named methods and an adapted FPSMark variant on real screen captures, COCO groups and LVIS transfer. [chen2026instance; supporting; direct-evidence; confidence high]. Limitations: 100 images per COCO group,50 per LVIS instance-count subset; unique aggregate and subset overlaps unknown.; Image-level methods are mask-adapted; capture images manually perspective corrected.

- TC04: Chen reports five-instance quality36.00dB PSNR and.964 SSIM and explicitly acknowledges failures on fragments and absence of object instances. [chen2026instance; supporting; direct-evidence; confidence high]. Limitations: Bit extraction ACC does not establish false-attribution probability.

- TC05: These TIFS precedents support task-specific operating conditions, meaningful component ablations and quality/payload-matched comparisons as useful design targets. [tang2024rrw; supporting; agent-inference; confidence medium]. Limitations: Observed precedents cannot establish necessary or sufficient journal acceptance criteria.

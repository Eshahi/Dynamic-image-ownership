# Watermark copy attack

- Citation key: `kutter2000copy`
- Authors: Martin Kutter; Sviatoslav Voloshynovskiy; Alexander Herrigel.
- Year / venue: 2000; Security and Watermarking of Multimedia Contents II, Proceedings of SPIE 3971.
- Version: Published repository PDF; paper heading: The Watermark Copy Attack.
- Primary source: [full text / repository](https://archive-ouverte.unige.ch/unige:47812).
- DOI: Not primary-verified; omitted.
- arXiv / identifier note: Not applicable; DOI 10.1117/12.384991 surfaced in secondary metadata only and is omitted from verified bibliography.
- Access date: 2026-10-18.
- Verification: **V2**. Primary repository full PDF: method and experimental sections inspected.
- Inspection locators: Sections 2–7, especially attack construction §§3–5 and experiments §6 (internal pp. 2–8).
- Cached artifact: `kutter2000.pdf`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Post-hoc existing-image watermarking.
- Mechanism: Estimate watermark residual using denoising and adapt its strength to the target image through local perceptual/noise models.
- Threat and attacker access: Copying a victim's watermark to unrelated content. Victim detector retains its original verification information; attacker has a marked image, neither secret key nor embedding algorithm.
- Detector side information: Victim detector retains its original verification information; attacker has a marked image, neither secret key nor embedding algorithm.
- Payload / capacity: Both tested commercial spread-spectrum systems carried 64-bit messages.
- Datasets and counts: Lena-to-Cameraman demonstration, 256×256, two anonymized commercial systems; other trials mentioned without a complete sample count.
- Attacks / regenerators: Residual estimation and additive copy; no diffusion regenerator.
- Conditional results: Section 6 reports successful detection after copying for both commercial systems, using a 5×5 adaptive Wiener filter; not a population ASR.
- Limits: Small demonstrations, unspecified broader denominators, older spatial marks. Content dependence is not automatically secure binding.

## Thesis relevance and inference

Direct predecessor of active watermark-copy forgery. Different from enrolling an unchanged regenerated image under an attacker's own record.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.


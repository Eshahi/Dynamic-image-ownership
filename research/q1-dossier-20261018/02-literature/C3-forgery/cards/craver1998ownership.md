# Resolving Rightful Ownerships with Invisible Watermarking Techniques: Limitations, Attacks, and Implications

- Citation key: `craver1998ownership`
- Authors: Scott Craver; Nasir Memon; Boon-Lock Yeo; Minerva M. Yeung.
- Year / venue: 1998; IEEE Journal on Selected Areas in Communications 16(4), 573–586.
- Version: Published May 1998.
- Primary source: [full text / repository](https://web.cs.ucla.edu/~miodrag/cs259-security/craver98resolving.pdf).
- DOI: 10.1109/49.668979.
- arXiv / identifier note: Not applicable.
- Access date: 2026-10-18.
- Verification: **V2**. Primary full-text formal definitions, counterexamples, security discussion and illustrative trials; DOI/issue metadata checked against SUNY author repository.
- Inspection locators: Sections IV–VIII, pp. 578–585; Example 3/Table III; Definitions 1–2 and Example 5.
- Cached artifact: `craver1998.pdf`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Existing digital images; ownership disputes.
- Mechanism: Constructs competing ownership evidence. One-way hashing of original-plus-identifier constrains admissible marks; noninvertibility alone does not eliminate quasi-invertibility.
- Threat and attacker access: Counterfeit originals and watermark claims; invertibility and quasi-invertibility. Claimed originals, candidate marks/identities and a fixed admissible watermark protocol; central registration discussed.
- Detector side information: Claimed originals, candidate marks/identities and a fixed admissible watermark protocol; central registration discussed.
- Payload / capacity: Example 3 uses 1,000 AC coefficients; this is not a 1,000-bit authenticated payload.
- Datasets and counts: Illustrations use Baboon/Peppers; Table III reports 100 random trials. No modern dataset or diffusion model.
- Attacks / regenerators: Inverse embedding, mix-and-match counterfeit evidence; no regeneration.
- Conditional results: No performance number transferred to the thesis. Counterexamples demonstrate ambiguity rather than calibrated false-positive rates.
- Limits: Scheme-dependent formal notions; suggested nonquasi-invertible construction is not a universal proof. Historical legal observations are not current legal guidance.

## Thesis relevance and inference

Closest earlier ownership-ambiguity framework. Inference: passive regenerate-and-enroll belongs to this protocol-level family, but is not literally the same inverse-watermark algorithm.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.


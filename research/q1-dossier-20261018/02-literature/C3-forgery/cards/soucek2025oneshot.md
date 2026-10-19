# Transferable Black-Box One-Shot Forging of Watermarks via Image Preference Models

- Citation key: `soucek2025oneshot`
- Authors: Tomáš Souček; Sylvestre-Alvise Rebuffi; Pierre Fernandez; Nikola Jovanović; Hady Elsahar; Valeriu Lacatusu; Tuan Tran; Alexandre Mourachko.
- Year / venue: 2025; NeurIPS 2025.
- Version: Official proceedings PDF.
- Primary source: [full text / repository](https://proceedings.neurips.cc/paper_files/paper/2025/file/47fee9cd8a252161dec7cb48ec0ca2f2-Paper-Conference.pdf).
- DOI: 10.52202/085713-1675.
- arXiv / identifier note: 2510.20468; evidence taken from proceedings PDF.
- Access date: 2026-10-18.
- Verification: **V2**. Official primary full-text method and experiment sections inspected; DOI from proceedings abstract page.
- Inspection locators: Threat model p.3; §§3.1–3.2 pp.4–6; §§4.1–4.3 pp.6–9; Table 1.
- Cached artifact: `soucek-neurips2025.pdf`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Post-hoc image watermark forgery.
- Mechanism: Train preference model using procedural corruptions, optimize marked image toward a clean estimate, transfer estimated residual.
- Threat and attacker access: Single-image victim-watermark copying. Victim extractor; attacker needs one marked image, no key/API, plus a trained preference model.
- Detector side information: Victim extractor; attacker needs one marked image, no key/API, plus a trained preference model.
- Payload / capacity: CIN 32 bits and MBRS 256 bits; other method capacities not extracted.
- Datasets and counts: SA-1b training; 100 marked validation images and 100 new covers; same message used for baseline comparability.
- Attacks / regenerators: Gradient residual extraction; comparisons include FLUX DiffPure and CtrlRegen, not registry enrollment.
- Conditional results: Table 1: CIN/MBRS/TrustMark/Video Seal bit accuracies 1.00/.83/.61/.83; average PSNR 31.3. These are not calibrated forgery ASRs.
- Limits: One-shot refers to target samples, not training-free operation. Content-aware embedding alone does not ensure decoder binding.

## Thesis relevance and inference

Closest modern post-hoc extension of Kutter; essential future active-copy evaluation for F5, with no present F5 failure implied.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.


# Diffusion-Generated Image Watermarking: A Two-Axis Taxonomy and Three Protocol-Bounded Case Studies

ID: `taxonomy`. Verification: **V2, own T1 method and evaluation recheck**. Conservative direct floor: **supplemental only**.

Authors: Sung Ju Lee; Nam Ik Cho. Version/date: 2610.09755v1; 07 Oct 2026. Venue: arXiv preprint; final venue not independently verified. DOI: not independently verified. Citation key: `T1_taxonomy`. Accessed 2026-10-20.

Primary: [https://arxiv.org/abs/2610.09755v1](https://arxiv.org/abs/2610.09755v1); [inspected full text](https://arxiv.org/html/2610.09755v1).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-taxonomy.html` (241377 bytes). SHA-256: `1cecf056723788113e305811b50cee7deb2efd95738797f888438496767d0609`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-taxonomy.read.txt`; SHA-256 `184ec0904a22a3c808ea0b3d5bd1aec29a534a5aa6b2d20e2d3cc2e16927d3ba`.

Inspected: Own T1 recheck: translation footnote; Sections 3--6, Tables 2--6, Section 7 threat boundary; cached lines 143--443.

## Mechanism and attacker access

Taxonomy distinguishes insertion mechanism from carrier representation; combines source-native verification/identification, editing and VAE-phase case studies. This is a translation/reorganization of a July 2026 Korean article, not another independent replication.

## Models

Table 4 sources use SD2.1; P2P and InfEdit use SD1.5. Table 5 covers VAE-B, VAE-C and diffusion regeneration; exact attack checkpoints NR here.

## Strength / noise

Editing strengths and regeneration noise levels NR in this inspected article; do not import them from its citations.

## Sampler / steps

DDIM inversion is described; exact step counts and samplers for case-study attacks NR here.

## Prompt / guidance

Prompt policies for tabulated attacks NR here.

## Resolution

Case-study image resolution NR here.

## Image counts and units

Per-attack image denominators NR here. DeltaFID-1k labels 1,000 quality samples, not a regeneration denominator. Enrolled 2,048/8,192 IDs are keys, not images.

## Metrics

TPR at 1% FPR; source-native identification; DeltaFID-1k, PSNR, LPIPS; latency.

## Conditioned numerical results

Table 2 harmonized subset: HSTR verification .993, identification .946, DeltaFID-1k -.099 (new matched-condition quality measurement); most other entries follow PhaseMark. Table 4: Tree-Ring P2P .25 / InfEdit .32, versus HSQR .99 / 1.00. Table 5: PhaseMark APM regeneration mean .998 across VAE-B, VAE-C and diffusion.

## Limits and conflicts

Adjunct only: reused data dominate; no complete attack configuration or image denominator is supplied here. Table 2 harmonization and new HSTR quality do not make Tables 4/5 fresh experiments. The translated original is not counted again. A semantic carrier remains a hypothesis; editing conditions and native readouts differ across tables.

## Consequence for this study

Keep conditional retention and native metrics distinct. Do not infer a semantic carrier or encoder-independent F5 robustness from this taxonomy.

The settings and numbers above are direct evidence from the named locators; the consequence is agent inference. Native claims of semantic preservation, distribution preservation or general robustness retain the stated assumptions and were not reproduced. No outcome from our study exists.

# Bibliography integration audit

Author: Codex agent; 2026-10-25. Mechanical integration of citation keys in `related-work.md`, using retained bibliographies only. No new web search, download, experiment, or publisher-version verification occurred in this pass.

## Version and identity qualifications

- `behera2026rankratio`: IEEE Access volume 14, pages 114877–114892, year 2026 and DOI 10.1109/ACCESS.2026.3717412 describe the Crossref-resolved publication identity. Substantive inspection was of the author manuscript linked in the prose and `literature/transfer-theory/rank-ratio-unverified.md`. Final publisher text was inaccessible and its equivalence to that manuscript is unverified. The DOI URL is an identity locator, not a full-text inspection receipt. The manuscript's provisional header is not silently replaced as evidence.
- `lee2026phasemark`: arXiv 2601.13128v1 methods/experiments were inspected. The retained note reports that arXiv states ICASSP 2026 acceptance; no publisher-text access or final-version equivalence is claimed. The alternate `T3PhaseMark2601` key is excluded because it is not cited, and is not a duplicate definition of the cited key.
- `lee2026taxonomy`: the inspected arXiv 2610.09755v1 restatement is not inspection of the original Semantic Imprinting paper. `lee2026imprinting` occurs only as an explicitly excluded key in explanatory prose, without citation syntax, and is intentionally omitted.
- `podell2023sdxl`: the draft evidence ledger pins inspection to arXiv 2307.01952v1, section 2.4/Table 3. The inherited BibTeX URL is unversioned and has no note field; it is copied unchanged. The draft ledger and `literature/encoders/podell-sdxl.md` supply the inspected-version locator, rather than the current contents of that unversioned URL.
- `zhao2024invisible`, `an2024waves`, `lu2025vine`, `cao2026marknull`: versioned URLs specify arXiv v3, v3, v2 and v1 respectively. Retained venue/year metadata does not change which text was inspected.
- `lu2025vine`: retained ICLR publication year 2025 is distinct from preprint year 2024 in the uncited `T3VINE2410` entry. The paper SDXL-Turbo versus released SD-Turbo constructor discrepancy remains in the prose/cards. Neither citation entry certifies checkpoint provenance.
- `rezaei2024lawa`: cited v3 is preserved. The uncited `T3LaWa2408` entry refers to v1 and is not substituted.

## Verification scope

Citation-key resolution and selected-entry counts were checked with PowerShell text parsing. The output retains full title/author/year/URL/DOI fields, original notes, Unicode author names and TeX accents. No DOI or other metadata was invented. Entries with unversioned `eprint` identifiers retain their original versioned URLs and notes. Shared bibliographies and manuscript prose were not edited. This is a mechanical integration check, not an independent scientific review or publication-readiness certification.

The draft contains **12 unique citation keys**, all resolved exactly once across source bibliographies. Missing keys: **0**. Duplicate definitions of cited keys: **0**. Repeated in-text citations are intentional. Output `references.bib` contains exactly 12 entries in first-citation order, copied without substantive metadata normalization; the inherited malformed SDXL author accent is corrected to Unicode Müller. Citation count differs from the 14 evidence-ledger rows.

## Exact source paths

- S1: `C:\Users\Soroush\.codex\worktrees\codex-et-final\research\encoder-transfer-20261019\final-study-20261025\literature\watermarks\references.bib`
- S2: `C:\Users\Soroush\.codex\worktrees\codex-et-final\research\encoder-transfer-20261019\design-research\T3-baseline-fidelity\references.bib`
- S3: `C:\Users\Soroush\.codex\worktrees\codex-et-final\research\encoder-transfer-20261019\final-study-20261025\literature\attacks\references.bib`
- S4: `C:\Users\Soroush\.codex\worktrees\codex-et-final\research\encoder-transfer-20261019\final-study-20261025\literature\encoders\references.bib`
- S5: `C:\Users\Soroush\.codex\worktrees\codex-et-final\research\encoder-transfer-20261019\final-study-20261025\literature\transfer-theory\references.bib`

## Resolved metadata

Fields reproduce the selected retained entries. Absent means no DOI field exists in that entry; it does not mean that no DOI exists. DOI discovery was outside this mechanical integration.

| Key / source | Title | Authors | Year | URL | DOI status |
|---|---|---|---|---|---|
| `wen2023treering` / S1 | Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust | Yuxin Wen and John Kirchenbauer and Jonas Geiping and Tom Goldstein | 2023 | [Retained URL](https://arxiv.org/abs/2305.20030v2) | Absent in retained entry; not searched |
| `fernandez2023signature` / S1 | The Stable Signature: Rooting Watermarks in Latent Diffusion Models | Pierre Fernandez and Guillaume Couairon and Hervé Jégou and Matthijs Douze and Teddy Furon | 2023 | [Retained URL](https://arxiv.org/abs/2303.15435v2) | Absent in retained entry; not searched |
| `rezaei2024lawa` / S1 | LaWa: Using Latent Space for In-Generation Image Watermarking | Ahmad Rezaei and Mohammad Akbari and Saeed Ranjbar Alvar and Arezou Fatemi and Yong Zhang | 2024 | [Retained URL](https://arxiv.org/abs/2408.05868v3) | Absent in retained entry; not searched |
| `T3WAM2411` / S2 | {Watermark Anything with Localized Messages} | Tom Sander and Pierre Fernandez and Alain Durmus and Teddy Furon and Matthijs Douze | 2024 | [Retained URL](https://arxiv.org/abs/2411.07231v2) | Absent in retained entry; not searched |
| `zhao2024invisible` / S3 | Invisible Image Watermarks Are Provably Removable Using Generative AI | Zhao, Xuandong and Zhang, Kexun and Su, Zihao and Vasan, Saastha and Grishchenko, Ilya and Kruegel, Christopher and Vigna, Giovanni and Wang, Yu-Xiang and Li, Lei | 2024 | [Retained URL](https://arxiv.org/html/2306.01953v3) | Absent in retained entry; not searched |
| `an2024waves` / S3 | WAVES: Benchmarking the Robustness of Image Watermarks | An, Bang and Ding, Mucong and Rabbani, Tahseen and Agrawal, Aakriti and Xu, Yuancheng and Deng, Chenghao and Zhu, Sicheng and Mohamed, Abdirisak and Wen, Yuxin and Goldstein, Tom and Huang, Furong | 2024 | [Retained URL](https://arxiv.org/html/2401.08573v3) | Absent in retained entry; not searched |
| `lu2025vine` / S3 | Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances | Lu, Shilin and Zhou, Zihan and Lu, Jiayou and Zhu, Yuanzhi and Kong, Adams Wai-Kin | 2025 | [Retained URL](https://arxiv.org/html/2410.18775v2) | Absent in retained entry; not searched |
| `cao2026marknull` / S3 | MarkNull: Model-Agnostic Watermark Removal in AI-Generated Images via On-Manifold Latent Manipulation | Cao, Jie and Li, Qi and Zhang, Zelin and Wu, Xiaodong and Liu, Lingshuang and Li, Xiangman and Ni, Jianbing | 2026 | [Retained URL](https://arxiv.org/html/2608.10166v1) | Absent in retained entry; not searched |
| `podell2023sdxl` / S4 | SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis | Podell, Dustin and English, Zion and Lacey, Kyle and Blattmann, Andreas and Dockhorn, Tim and Müller, Jonas and Penna, Joe and Rombach, Robin | 2023 | [Retained URL](https://arxiv.org/abs/2307.01952) | Absent in retained entry; not searched |
| `behera2026rankratio` / S5 | A Rank-Ratio Bound for Pixel-Space Signal Fragility in Latent-Diffusion Autoencoders | Behera, Mohini Mohan | 2026 | [Retained URL](https://doi.org/10.1109/ACCESS.2026.3717412) | Retained: 10.1109/ACCESS.2026.3717412 |
| `lee2026phasemark` / S1 | PhaseMark: A Post-hoc, Optimization-Free Watermarking of AI-generated Images in the Latent Frequency Domain | Lee, Sung Ju and Cho, Nam Ik | 2026 | [Retained URL](https://arxiv.org/abs/2601.13128v1) | Absent in retained entry; not searched |
| `lee2026taxonomy` / S1 | Diffusion-Generated Image Watermarking: A Two-Axis Taxonomy and Three Protocol-Bounded Case Studies | Lee, Sung Ju and Cho, Nam Ik | 2026 | [Retained URL](https://arxiv.org/abs/2610.09755v1) | Absent in retained entry; not searched |

## Retained version notes

- `wen2023treering`: Inspected version 2305.20030v2 dated 2023-06-01; accessed 2026-10-25 URL: https://arxiv.org/abs/2305.20030v2
- `fernandez2023signature`: Inspected version 2303.15435v2 dated 2023-07-26; accessed 2026-10-25 URL: https://arxiv.org/abs/2303.15435v2
- `rezaei2024lawa`: Inspected version 2408.05868v3 dated 2025-05-30; accessed 2026-10-25 URL: https://arxiv.org/abs/2408.05868v3
- `T3WAM2411`: Inspected version 2411.07231v2; accessed 2026-10-20.  URL: https://arxiv.org/abs/2411.07231v2
- `zhao2024invisible`: No note field; see versioned URL where supplied and qualifications below. URL: https://arxiv.org/html/2306.01953v3
- `an2024waves`: No note field; see versioned URL where supplied and qualifications below. URL: https://arxiv.org/html/2401.08573v3
- `lu2025vine`: No note field; see versioned URL where supplied and qualifications below. URL: https://arxiv.org/html/2410.18775v2
- `cao2026marknull`: No note field; see versioned URL where supplied and qualifications below. URL: https://arxiv.org/html/2608.10166v1
- `podell2023sdxl`: No note field; see versioned URL where supplied and qualifications below. URL: https://arxiv.org/abs/2307.01952
- `behera2026rankratio`: Bibliography verified through Crossref; author-manuscript text inspected, final publisher text identity unverified URL: https://doi.org/10.1109/ACCESS.2026.3717412
- `lee2026phasemark`: Version 1 methods and experiments inspected; arXiv states accepted at ICASSP 2026; publisher version not accessed URL: https://arxiv.org/abs/2601.13128v1
- `lee2026taxonomy`: Version 1 inspected; its restatement is not inspection of the original Semantic Imprinting paper URL: https://arxiv.org/abs/2610.09755v1

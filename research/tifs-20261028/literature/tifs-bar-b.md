# TIFS bar, literature assistant B

Access date: 2026-10-28. Four primary full texts were inspected through method and experiment sections and cached with SHA-256 provenance. These correspond to four published TIFS works, but **not four final-journal manuscripts**: WFM and StyleMark were inspected in earlier author-preprint versions. StyleMark final full text was inaccessible. LVMark is adjacent video evidence and MantleMark adjacent 3D evidence; neither establishes a diffusion-image evaluation norm.

Detailed observations occur once in the [generated findings](tifs-b/synthesis/findings.md); metadata, exact inspected artifact/checksum, version restrictions and locators are in [paper cards](tifs-b/synthesis/papers/). The [response contract](tifs-b/response.json) and [ledger](tifs-b/synthesis/evidence-ledger.jsonl) distinguish observations from inference. Validation and synthesis both returned `valid: true`, no warnings. This is structural/source-identity validation, not independent scientific review.

| Work | Journal verification / exact inspected version | Relevance / limitation |
|---|---|---|
| LVMark | [IEEE](https://xplorestaging.ieee.org/document/11495243), TIFS21:4908-4923, 2026, DOI10.1109/TIFS.2026.3688194; [arXiv v4](https://arxiv.org/html/2412.09122v4) | VIDEO; eight named baselines despite prose saying seven. Preprint author order retained; repository citation reverses first two names. |
| MantleMark | [CityU institutional publication record](https://scholars.cityu.edu.hk/en/publications/mantlemark-migrating-watermarks-from-multi-view-images-to-radianc/), TIFS21:256-271, 2026 (online2025), DOI10.1109/TIFS.2025.3636020; [16-page institutional manuscript](https://eprints.lancs.ac.uk/id/eprint/234126/1/111.pdf) | 3D reconstruction; nine image baselines plus three 3D comparators. Strength sweeps directly inspected; other component-ablation details remain UNKNOWN. |
| WFM | [Author-group publication list](https://clem.dii.unisi.it/~vipp/journals.html), TIFS19:8322-8337, 2024, DOI10.1109/TIFS.2024.3443650; [13-page arXiv v1](https://arxiv.org/pdf/2310.16919v1) | Generative-image model ownership; final article is three pages longer, differences UNKNOWN. |
| StyleMark | [DBLP journal metadata](https://dblp.org/rec/journals/tifs/ZhangYSWX25.html) corroborates TIFS20:7867-7880, 2025, DOI10.1109/TIFS.2025.3592521; [author preprint v1](https://arxiv.org/html/2412.07129v1) | IMAGE/style-transfer; final IEEE page returned robot gate. Preprint title differs and omits final coauthor Caiyun Xie; cannot attribute its experiment details to the final version without reconciliation. |

## Agent inference, not a journal requirement

A credible contribution can be supported by mechanism-targeted embedding and tests across architectures excluded from training. The present thesis needs a prospective claim that survives such exclusion, with comparators matched to that claim. Bitwise accuracy alone does not establish content-bound ownership. Claims at rare false-positive rates require stated assumptions and calibration, rather than treating a zero-event sample as proof.

These works support diverse evidence packages; they do not demonstrate a universal minimum number of datasets, baselines, users or pages. A user study is one observed way to support imperceptibility. Its absence elsewhere is UNKNOWN here, not evidence that reviewers waive it. Existing standard-distortion experiments in these papers imply reviewer risk; they do not authorize expanding this thesis beyond T3/T4/T5.

## Access and interpretation caveats

- No abstract-only work is counted as method/experiment inspection. Two final-version gaps remain explicit; if WP1 requires eight *final journal versions*, substitute or acquire author-accepted WFM/StyleMark manuscripts before declaring that stricter criterion satisfied.
- All cached full texts reside only under MAIN `.thesis-build/cache-tifs/papers/`; no code, images, datasets, models, packages or experiment processing was downloaded/run.
- No quotations were used. UNKNOWN means not established from the inspected version/sections, not an assertion of absence.
- MantleMark prose says four baselines before enumerating nine; use enumerated methods. Its TableIII includes three 3D methods, making twelve unique comparator names across the inspected experimental sections.

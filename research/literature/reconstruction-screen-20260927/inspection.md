# Inspected reconstruction alternatives, 2026-09-27

Observer: `/root`. Targeted primary-source screen, not systematic coverage.
No scientific reproduction. Sections below were inspected in downloaded HTML
using the existing interpreter's standard-library HTMLParser, after excluding
table-of-contents matches. An initial extraction found only contents entries;
a second failed with Windows cp1252 UnicodeEncodeError; UTF-8 body extraction
succeeded. Neither failed extraction supplies evidence.

## gnri-v5

Lightning-Fast Image Inversion and Editing for Text-to-Image Diffusion Models,
Dvir Samuel, Barak Meiri, Haggai Maron, Yoad Tewel, Nir Darshan, Shai Avidan,
Gal Chechik, Rami Ben-Ari. ICLR 2025; inspected arXiv v5, 2025-02-06,
https://arxiv.org/html/2312.12540v5 . DOI not checked.
Inspected sections 4, 5.1-5.3, Appendix H and failure discussion through browser.
Scalar residual root finding with a noise-distribution guidance term is proposed.
Reconstruction uses captions and models SD2.1, SDXL-Turbo and Flux, not our
empty-conditioned SD1.5 profile. Appendix H2 reports GNRI PSNR 23.9 versus
EditFriendly 26.1: faster does not mean universally most faithful.
Raw HTML: stable project's ignored `.thesis-build/reconstruction-literature-20260927/gnri-v5.html`,
277716 bytes, SHA-256 `20bafdba7fa043091fc5fc1285a2fca56cb09ebe93bd0e06296507005a4a6207`.

## trdi-v1

Timestep Rescheduling in Diffusion Inversion, Shangquan Sun, Ting Gong,
Zhirui Liu, Jiamin Wu, Runkai Zhao, Mianxin Liu, Wenqi Ren, Xiaochun Cao.
arXiv:2606.15389v1, 2026-06-13; conference status not established here.
https://arxiv.org/html/2606.15389v1 . DOI not checked.
Inspected sections 3-4/Table 1 and Appendix G. Nonuniform timesteps augment
existing inversion; its local surrogate does not guarantee global accuracy.
Table 1 uses captioned COCO/SD1.5/50 steps: ReNoise+TRDI PSNR 22.67,
GNRI+TRDI 22.32. Neither meets our source-quality target. Failures are shown.
Raw HTML: ignored `.thesis-build/reconstruction-literature-20260927/trdi-v1.html`,
531365 bytes, SHA-256 `bbffce9a4104801a4ba36e2c5ad2f3b4730ecb74118db9d7986fca7489ffe049`.

## reed-vae-v1

REED-VAE: RE-Encode Decode Training for Iterative Image Editing with Diffusion
Models, Gal Almog, Ariel Shamir, Ohad Fried. Inspected arXiv:2504.18989v1,
2025-04-26, https://arxiv.org/html/2504.18989v1 . Publication DOI
10.1111/cgf.70020 verified separately on publisher; inspected version is preprint.
Inspected sections 3-4 and limitations. Decoder-only fine-tuning keeps encoder
fixed to address repeated encode/decode degradation; reconstruction remains
imperfect. Iterative editing evidence does not guarantee our single-pass targets.
Raw HTML: ignored `.thesis-build/reconstruction-literature-20260927/reed-vae-v1.html`,
595375 bytes, SHA-256 `3bbce90fc841e42be41e4f0657f37fe4dec8cdc2bcbd49053f7cfdaae443ebb4`.

## Read-only official implementation inventories

GitHub API tree/README inspections, 2026-09-27:

- `dvirsamuel/NewtonRaphsonInversion`, commit
  `fe4d850f06d001f9c244c68d53bc39eb398054f3`: SDXL inversion/Euler and
  fixed-point SD pipeline code exists; no LICENSE file found in this tree.
  No code copied, installed or executed; licensing is unresolved, not denied.
- `sunshangquan/TRDI`, commit
  `65c4a8de3f356b2e7a5ec8150f1822bc7f63ac7f`: SD15 examples and LICENSE
  exist; README declares Apache-2.0. Full dependencies/runtime/source parity
  not audited; no library adopted or installed.
- `galmog/REED-VAE`, commit
  `1ea918c799c3149b36cc898cc5749752a98a37c9`: README and teaser only;
  README says code/models will be released. No ready checkpoint demonstrated.

## Additional primary-source leads, weaker access depth

- ReNoise, ECCV 2024: inspected Google Research abstract only; iterative
  noising/refinement is an accuracy/speed comparator, not reproduced here.
  https://research.google/pubs/renoise-real-image-inversion-through-iterative-noising/
- Exact DPM inversion, CVPR 2024: inspected CVF abstract/intro excerpt; implicit
  inversion is relevant, not a turnkey image-preservation guarantee.
  https://openaccess.thecvf.com/content/CVPR2024/html/Hong_On_Exact_Inversion_of_DPM-Solvers_CVPR_2024_paper.html
- FireFlow, ICML 2025: inspected PMLR abstract; rectified-flow/Flux method needs
  a different model profile, not a drop-in SD1.5 change.
  https://proceedings.mlr.press/v267/deng25c.html
- FARI, ICLR 2026: inspected official abstract only; watermark-extraction
  inversion/LoRA is not existing-source reconstruction nor the current DCT
  detector. No claimed paper-level fidelity transfer.
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/dad66bb085bab14fbca07cfa4271f00b-Abstract-Conference.html
- ROAR, ICCV 2025: inspected CVF search-exposed abstract/method excerpt; direct
  PDF fetch returned 403. Restoration/inversion-based extraction is a comparator,
  not evidence of source preservation or a proposed blind-DCT implementation.
  https://openaccess.thecvf.com/content/ICCV2025/papers/Wang_ROAR_Reducing_Inversion_Error_in_Generative_Image_Watermarking_ICCV_2025_paper.pdf

Browser GNRI proceedings PDF exceeded the browser size limit; OpenReview returned
a challenge. REED v2 HTML failed. Accessible pinned arXiv HTML versions above
were used openly, without access circumvention. Only public paper text acquired;
no model/dataset bytes, GPU work, installation, private upload or paid service.

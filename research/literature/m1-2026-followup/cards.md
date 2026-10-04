# Bounded 2026 primary-source follow-up

Access date: 2026-10-03. Both version-one full texts were opened and archived from official arXiv HTML. Inspected methods and experiments are identified below. “Verified” means the inspected source and bytes exist, not that its experiments were independently reproduced or peer reviewed. No paper code, models or thesis data were executed/inspected. Download receipts include artifact licenses and SHA256. Root bibliography already contains `Gao2026SLICEv1`; only DiffMark is supplied as a new BibTeX entry.

## SLICE — Gao et al., arXiv:2603.12749v1, 2026

Source: [versioned primary full text](https://arxiv.org/html/2603.12749v1). Local artifact: `slice-v1.html`. Venue: preprint; DOI metadata already recorded in root bibliography, not independently resolved here. Authors: Zheng Gao, Yifan Yang, Xiaoyu Li, Xiaoyan Feng, Haoran Fan, Yang Song, Jiaojiao Jiang.

**Direct evidence, mechanism:** §§3.1–3.3 generate an unmarked reference from a prompt, extract subject/environment/action/detail with a VLM, synthesize keyed semantic noise in four disjoint latent partitions, then generate again. Verification requires DDIM inversion, the VLM/meta-prompt, text encoder, partition geometry, secret synthesis key and thresholds. It produces global/partition-based three states; it is neither image-DCT extraction nor pixel-region copy-paste localization. §6 uses SD2/Qwen3-VL; §5 evaluates descriptor stability with BLIP and chooses Chinese prompts.

**Direct evidence, experiments:** §6.1/Table1 defines attack success as edited content still triggering watermark presence: LFA/RPM/CSI success 0/5/19%, versus SEAL 0/7/81%. These are forgery rejection rates, not regeneration-survival rates. §6.2/Table2 reports clean accuracy1.000/JPEG0.990; §6.3/Table3 COCO CLIP31.342→31.240 compares generated alternatives, not preserved photographs. §6.5/Table4 crop/scale active AUC0.054.

**Limits/inference:** inversion steps/runtime, sample counts, regeneration strengths and exact keyed synthesis are unspecified in inspected experimental sections. §6.4 uses count threshold35 whereas §3.3 defines ratios. Theorem4.4 assumes independent matches; no measured unconditional FPR follows. Semantic binding omits DCT/OwnerID signatures. Public synthesis secrets would permit authorized-pattern generation; actual public-key security is unestablished. Local reproduction needs additional pinned SD2/VLM components.

## DiffMark — Nguyen-Le et al., arXiv:2603.20304v1, 2026

Source: [versioned primary full text](https://arxiv.org/html/2603.20304v1). Local artifact: `diffmark-v1.html`. Venue: preprint. Authors: Hong-Hanh Nguyen-Le, Van-Tuan Tran, Thuc D. Nguyen, Nhien-An Le-Khac. DOI: not independently resolved.

**Direct evidence, mechanism:** §§3.1–3.3 train secret-to-perturbation encoder and latent decoder, inject persistent delta before frozen denoiser evaluations, and use differentiable four-step LCM plus detached50-step DDIM supervision. AppendixB/Table3 encoder295,265/decoder2,339,704 parameters. AppendixG.4 detection requires VAE encoding/scaling, learned decoder and registered secret/threshold; no inversion/prompt/U-Net at detection. §4.6 reports16.4ms including VAE overhead, L40S/100 images, not local GPU timing.

**Direct evidence, experiments:** AppendixE evaluates1,000 generated prompts/dataset, not original-photo marking. Table1 COCO bitaccuracy0.9407/PSNR8.91dB/LPIPS0.7343 are stated generated-counterfactual metrics. Table2 DiffusionDB TPR@0.1%FPR: VAE0.81/diffusion1.00/twice-diffusion1.00, crop/rotation/blur0.00. AppendixF specifies surrogate SD1.4 noising40–200 steps/rinsing20–100; exact Table2 severity is unclear, not equivalent to local img2img0.4.

**Limits/inference:** no CLIP+pHash content binding or digital signature; public runtime payload plus available encoder can imprint arbitrary identities. §4.1 requires up to50k pretraining+10k diffusion-training steps, SD1.5 and LCM_Dreamshaper_v7. Local feasibility needs vetted trained weights or bounded training, neither obtained here. Eq14 trains DDIM with delta/N, but Eq5/Algorithm3 inject delta; resolve before reproduction. No evidence closes photographic fidelity, T4 or T5.

## Interpretation boundary

These preprints justify further method consideration, not a scientific success claim or an executable local baseline. The applicable gap remains a detector with measured cost and a content-authentication mechanism whose development quality and threat results can be evaluated under one frozen protocol. Source numbers above retain their authors' definitions; they must not be inserted as local measurements, universal false-positive guarantees, or our existing-photo acceptance results.

# GROW primary-source card — partial inspection, explicit access limits

Inspected 2026-10-25 by Codex agent. Research only; no paper/code/model/image downloads, installations, execution or new baseline.

## Identity and source versions

- **Title:** GROW: Watermark Generation with Progressive Guidance for Diffusion Models.
- **Authors:** Pengcheng Luo, Zexi Jia, Yijia Zhong, Jinchao Zhang, Jie Zhou.
- **Venue/version:** CVPR 2026, June, proceedings pp. 35978–35987; CVF open-access accepted-paper version. No arXiv version or immutable repository revision was established.
- [Official landing page](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html).
- [Official paper PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.pdf).
- [Author repository README](https://github.com/luopengchen/GROW), live main branch; inspected directly, not cloned.

## Main-paper evidence (compact paraphrase)

The inspected method (§4.2, p.35980; Algorithm 1, p.35982) guides predicted clean latents toward keyed, repeated message targets in mid-frequency DCT coefficients during denoising. Extraction uses the VAE encoder, DCT and coefficient signs. Implementation (§5.2) uses 16 bits in the first VAE channel, 50 steps, alpha=.5, eta=100, start ratio=.5.

M-ACC (§5.1, p.35982) is exact whole-message recovery per image. Quality uses PSNR/SSIM/FID/LPIPS. Figure 3 lists rotation 75°, JPEG25, crop25%, blur radius4, noise sigma=.05, brightness6, and Diff-Pure s=.5. The Diff-Pure attack model and independently trained-encoder status were not established. Table 1 (p.35983), MS-COCO: GROW PSNR27.54, SSIM.85, FID12.32, LPIPS.05; clean M-ACC1.00, adversarial .95, average .978. Table 2/§5.4 (p.35984) evaluates generation using SD1.5 and SDXL, with average .965/.981; it does not identify a cross-regenerator transfer matrix. Watermarked/unmarked verification is deferred to the supplement; its FPR definition/results remain uninspected.

**Answer:** independent-autoencoder full-regeneration transfer is **not established by the inspected evidence**. Diff-Pure prevents characterizing the suite as merely codecs/distortions. Multi-generator portability does not establish survival of regeneration by another generator.

## Separately inspected author README

The README's Method section describes direct VAE encoding, DCT sign extraction and majority voting; inference requires a compatible encoder and the secret key/mask, rather than DDIM inversion. Its Results section identifies 1,000 MS-COCO generated images, 16-bit payloads, and Tesla T4 timings: .24 seconds extraction, 21.16 seconds generation with .17 seconds watermark overhead, at 512x512 and 50 steps. These are author-reported conditions, not reproduced measurements. Training-free concerns model retraining; inversion-free concerns extraction. Neither phrase removes encoder dependence or proves cross-regeneration robustness. README defaults eta=200 and channels=[0,1,2,3] differ from paper §5.2's eta=100 and first-channel experiment; do not silently combine them into a single protocol. README labels its adversarial condition purification but supplies no independently trained regeneration matrix in the inspected text. Repository code, attack implementations, dependencies, licence file, commits and output artifacts were not inspected or run.

## Relevance to the retained F5 result (local evidence and inference)

Authoritative STATE.md was read once from the main checkout. It records F5 source-majority C=60/60,57/60,39/60 on SD1.5 strengths .1/.2/.4, SDXL C=0/60 throughout, and SDXL-VAE/MoVQ round trips C=55/60. These are local development results, not GROW measurements. They distinguish codec survival from full regeneration survival; they do not identify encoder replacement as the sole cause.

GROW is relevant to generation-time insertion with inexpensive extraction. Its endpoints, generation setting, quality envelope and payload differ from F5's image-domain procedure and source-majority semantic detection. No numerical ranking, causal refutation of F5, novelty priority, new baseline or protocol amendment follows from this card. A defensible article sentence is: “GROW demonstrates progressive generation-time guidance and direct latent-frequency extraction; the inspected evidence does not settle independently trained cross-regenerator survival.”

## What was actually inspected

- Search-indexed **primary PDF text**, rather than abstract-only summaries: p.35980 §4.1–4.2.2; p.35982 Algorithm 1/§5.1–5.3/Figure 3; p.35983 Table 1; p.35984 Table 2/§5.4/Table 3/§5.5; p.35985 Table 4/§5.6/§6–7. Only selected facts above are retained within the source paraphrase budget.
- Official landing-page metadata was exposed in search results; direct opening failed. Author README was directly opened and read.
- **Not inspected:** full continuous PDF, rendered pages/figures, complete references, supplementary document, FPR/ROC verification, full Diff-Pure specification or source code. Consequently no categorical claim that the entire paper/supplement lacks transfer tests is warranted.
- CVF search result advertises a supplement, but its actual linked target could not be retrieved. The conventional candidate `https://openaccess.thecvf.com/content/CVPR2026/supplemental/Luo_GROW_Watermark_Generation_CVPR_2026_supplemental.pdf` was attempted and returned 403; it is **not a verified supplement URL**.
- Third-party results appeared automatically but were not used as evidence. OpenReview candidate `https://openreview.net/forum?id=ZhDTUQiXHN` and `/pdf?id=ZhDTUQiXHN` returned browser-verification pages; neither identity nor paper content was established there.

## Exact discovery and direct-open log

All queries below were submitted on 2026-10-25. Repeated queries are omitted only when their text was identical; there were no useful supplementary search hits.

```text
"GROW" "Watermark Generation with Progressive Guidance"
site:openaccess.thecvf.com/content/CVPR2026 "GROW"
site:openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW "4.1" "attack"
site:openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW "adversarial" "M-ACC"
site:openaccess.thecvf.com/content/CVPR2026/supplemental/Luo_GROW
"GROW" "Progressive Guidance" "Adversarial" "purification"
"GROW" "Progressive Guidance" "M-ACC" "false"
"GROW" "Progressive Guidance" "4.1."
site:openaccess.thecvf.com "Luo_GROW" "5.1"
site:openaccess.thecvf.com "Luo_GROW" "False"
site:openaccess.thecvf.com "Luo_GROW" "Regeneration"
"GROW: Watermark" "Evaluation Metrics"
"GROW: Watermark" "Attack" "0.1"
"GROW: Watermark" "M-ACC" "defined"
"GROW: Watermark" "supplementary" "SDXL"
"GROW" "Progressive" "Message Accuracy"
"Luo_GROW_Watermark" "Experiments"
"Luo_GROW_Watermark" "Adversarial" "attack"
"Luo_GROW" "5.1. Experimental"
"GROW" "Progressive Guidance" "Diff-Pure"
"GROW" "Progressive Guidance" "single bit"
"GROW" "Watermark" "supplemental" "verification"
"GROW" "Watermark" "non-watermarked" "ROC"
site:openaccess.thecvf.com/content/CVPR2026/supplemental/ "GROW"
"Luo_GROW_Watermark" "Diff-Pure" "30"
```

Direct-open sequence: official landing page (403); official PDF (403); unverified conventional supplement candidate (403); author GitHub repository (success); landing page with `?x=1` (inaccessible); PDF using `http://` (redirected to HTTPS, 403); PDF using `www.openaccess.thecvf.com` (inaccessible); OpenReview forum and PDF candidates (verification pages); CVF daily listing `https://openaccess.thecvf.com/CVPR2026?day=2026-06-07` (403). Search-indexed primary excerpts supplied the method/experiment evidence despite those failures. No local document was downloaded to evade access failures.

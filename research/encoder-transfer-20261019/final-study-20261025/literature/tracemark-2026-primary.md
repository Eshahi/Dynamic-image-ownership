# TraceMark-LDM: encoder and regeneration boundaries

Inspected 2026-10-25. V2 means primary methods and experiments were read; it does not mean reproduced or independently validated. No experiment or download.

## Identity and inspected version

Wenhao Luo, Zhangyi Shen, Ye Yao, Feng Ding, Guopu Zhu and Weizhi Meng, *TraceMark-LDM: Authenticatable Watermarking for Latent Diffusion Models via Binary-Guided Rearrangement*. [arXiv metadata](https://arxiv.org/abs/2503.23332) records v1 on 2025-03-30 and v2 on 2026-06-22 and states acceptance at Expert Systems with Applications. The publisher version was not inspected. Technical evidence below uses [v2 full text](https://arxiv.org/html/2503.23332v2), not the initially opened v1.

## Compact source evidence (under 200 words)

Sections IV-B–D rearrange Gaussian values using repeated message bits, group small-magnitude values, interleave and key-shuffle. Extraction uses a **fine-tuned encoder**, DDIM inversion, the key and voting. The decoder is frozen. Section V-A uses SD2.1, 512-pixel images, 50 sampling/inversion steps, and encoder training on 200 images for 100 epochs.

The comparison payload is 256 bits. Section V-B assumes iid Bernoulli(.5) null matches and uses a strict score >167 for theoretical FPR below 10^-6. This is an assumed-null tail, not an observed million-negative experiment. Table III reports diffusion noise-step 300/400/500/600/700 TPRs 1/1/.999/.995/.954 and bit accuracies .9702/.9376/.8860/.8193/.7416; §V-C uses 1,000 generated images. Its inspected attack description cites Zhao but does not identify an independent regenerator checkpoint. Regen-VAE-A/B are CompressAI Bmshj2018/Cheng2020 (§V-C.2), not named diffusion encoders. Section IV-A proves invariance for a permutation independent of the Gaussian input. Section V-C.4 uses non-rejection of FID/CLIP equality tests to argue negligible quality impact.

## Local inference and admissible use

The detector's trained encoder and iterative inversion are material resources. They prevent describing this result as a fixed vanilla-encoder or lightweight image-extractor result. Its corruption suite supplies regeneration evidence under its own setup; the inspected text does not establish SDXL/FLUX independent-autoencoder transfer. This is a limitation of what was verified, not proof that no further implementation evidence exists.

Do not confuse the reported average bit accuracy with exact message recovery, owner attribution among many candidates, or cryptographic authentication. The word “authenticatable” is not a substitute for an adaptive unforgeability experiment or proof. A null match probability assumed for one message does not itself cover a large search over records or adversarially chosen images.

Non-rejection of equality is not an equivalence conclusion. A quality-equivalence claim needs a declared tolerance and an interval contained within it. Neither FID nor CLIP significance certifies the strict per-image quality envelope used for F5. Thus these results cannot be numerically ranked against F5's source-majority endpoint.

The permutation premise also deserves careful scope: a fixed index permutation preserves an iid input distribution, but a value-dependent rearrangement followed by a fixed permutation is a different map. For example, sorting two independent standard Gaussians yields an ordered pair whose first coordinate never exceeds its second. Preserving the multiset and its empirical histogram has not preserved the joint distribution. A fresh independent uniform permutation can restore exchangeability after sorting, but a fixed secret permutation must be analysed with its actual key/message randomness. This elementary counterexample does not prove that the full TraceMark construction is distinguishable; it shows why its preliminary lemma alone is insufficient to certify every later rearrangement. No new cryptanalysis or method modification is claimed.

## Inspection receipt

- Discovery query: `"TraceMark-LDM" watermark`, domains arxiv.org, openreview.net, openaccess.thecvf.com.
- Opened arXiv metadata, v1 HTML, then v2 HTML; v2 governs technical values. No publisher equivalence or DOI beyond arXiv was inferred.
- Read v2 §§IV-A–D, algorithms 1–2, §§V-A–C, Tables II–IV and equations 1–4, 12–16. Reference 32 identifies Zhao et al. arXiv:2306.01953; it does not fill in an unstated attack checkpoint.
- In-page searches included `VAE-Based`, `AUC` (no match), `False`, `Regen-Diff` (no exact match), and `Zhao`. Browser text, not rendered figure inspection, supports this card.
- No code, supplement, model weights, images or experiment outputs were acquired. No baseline or prospective protocol criterion changes.

# AEON (WACV 2026): primary-source card and detector-contract boundary

Status: **V2: main methods/experiments and full supplement inspected.** Initial indexed-only access was superseded by root's official-PDF reading at 17:38–17:46 UTC, 2026-10-25. No execution, replication, baseline amendment, or protocol change. This author addendum is outside completed WP6/E3 reviews.

## Source digest (under 200 words)

Muhammad Shahid Muneer and Simon S. Woo, WACV 2026, pp. 5406–5415 [L]. AEON trains a latent-conditioned hash network using a linear projection, tanh and straight-through sign; insertion blends it in Fourier space during generation. Objectives include cosine alignment and masked reconstruction, with the printed final loss `Lret+Lcons+Delta−Lrecon` (§3.2, Eq.8) [P].

Main Fig.3 stores a generation hash; supplement Algorithm1/§7 recomputes reference bits from the recovered latent. Verification uses inverse diffusion, model/hash weights, injection step, mask and threshold [P,S].

Experiments use SD2.1-base and guided ImageNet diffusion, 1,000 images and a 1% FPR operating point; Table2 reports Zhao23 AUC .999 and cumulative AUC .991. These are AUCs, not retention at a fixed threshold. Section4.2 selects best quality results across four experiments. Exact ordered cumulative attacks, checkpoint revisions and null-calibration procedure remain unresolved. Supplement Fig.6's different SD versions do not establish independently trained encoders [P,S].

## Author implications (interpretation, not an empirical result)

- Latent cosine alignment supplies a mechanism hypothesis; it does not identify which semantic features carry a mark or establish their transport across independently trained encoders. A mechanism label alone cannot support the thesis's transfer claim.
- Treat stored-reference and recomputed-reference detection as separate unresolved contracts. Do not silently select one, infer original-image-free verification, or compare with a lightweight extractor without stating inversion and model side information.
- AUC or combined-attack language cannot substitute for an operating false-positive rate or a reproducible ordered attack pipeline. Do not translate the paper's robustness language into the final study's native-cell outcomes.
- Both reference modes require their own null experiment. If the supplement constructs the candidate and reference from the same recovered latent, independent random-bit calibration is not automatic. This is a conditional dependence issue, not a measured false-positive result or proof that the reported ROC is invalid.
- The final loss's printed signs are retained without silently correcting an implementation that was not inspected. Best-of-four quality reporting is not interchangeable with the final study's all-source strict quality gate. No source result becomes an F5 prediction.

## Precise locators and unresolved fields

| Field | Inspected locator | Access-qualified disposition |
|---|---|---|
| Publication provenance | [L], title, authors, CVF BibTeX | Official indexed venue record; no arXiv identity inferred. |
| Learned architecture/embedding | [P], §3.1–3.3, Eqs.1–10, Algorithm1, pp.5408–5410; §4.1 | Full printed objective and training recipe read; actual implementation and revisions not verified. |
| Semantic-alignment support | [P], Eq.2, Fig.3; §4.2/Fig.5, p.5412 | Loss description and qualitative interpretation read; no causal semantic-transport test verified. |
| Detector main contract | [P], Fig.3 caption, p.5409; §3.4, p.5410 | Stored generation hash in caption; thresholded inverse-diffusion matching in method. |
| Detector supplement contract | [S], Algorithm 1; §7(i)–(vi) | Recomputed hash and private inverse model explicitly described; relationship to main contract unresolved. |
| Attack identity/order | [P], Table 2 caption and §4.2, p. 5412; [S], §4/Fig. 5 | Attack family names and all-attacks combination visible. Exact checkpoint revisions, severities, order and seeds not verified. |
| Encoder independence | [S], §5/Fig. 6 caption | Different model-version wording is insufficient to establish independent encoder training. |
| FPR/threshold | [P], §3.4 and §4.1; [S], Algorithm1 | Example <1% false-positive target and TPR at1% FPR stated. Exact threshold, null pool and calibration split remain unspecified in inspected material. |

## Access receipt and source URLs

Initial receipt, 2026-10-25: direct web-reader requests returned403; official indexed excerpts supplied partial access. At that stage no full-text promotion was justified. Root subsequently retrieved both public official PDFs with an ordinary HTTP request into the brief's authorized paper cache, without authentication. Bundled Node PDF.js extracted text in memory. Main PDF pages3–8 (printed5408–5413), covering §§3–4 and methods/experiments/limitations, and every supplement page1–4 were read. Page pixels were not rendered; no claim of visual figure inspection is made. This supersedes the initial access limitation, while the substantive unresolved fields above remain.

Cache root: MAIN `.thesis-build/cache-et-final/papers/`. `aeon-wacv2026.pdf`: 1,539,814 bytes; SHA-256 `8AC611762F92CE3DE06F199B46E304F7E5882B497AA439500EA8FE535021A06F`. `aeon-wacv2026-supp.pdf`: 8,538,138 bytes; SHA-256 `C4D20F8C731FDE141029EC6DBDFFE3F0E83103E0EFAA8FCFBF87F930D4723593`. No model, image, dataset, code, package or science interpreter was used; PDFs/full text are not committed.

- [L: Official CVF landing page](https://openaccess.thecvf.com/content/WACV2026/html/Muneer_AEON_Adaptive_Embedding_Optimized_Noise_for_Robust_Watermarking_in_Diffusion_WACV_2026_paper.html)
- [P: Official main paper](https://openaccess.thecvf.com/content/WACV2026/papers/Muneer_AEON_Adaptive_Embedding_Optimized_Noise_for_Robust_Watermarking_in_Diffusion_WACV_2026_paper.pdf)
- [S: Official supplement](https://openaccess.thecvf.com/content/WACV2026/supplemental/Muneer_AEON_Adaptive_Embedding_WACV_2026_supplemental.pdf)

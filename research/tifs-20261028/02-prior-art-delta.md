# Prior-art delta and claim exclusions

Research snapshot: 2026-10-28. This updates the [October 25 map](../encoder-transfer-20261019/final-study-20261025/article-drafts/close-prior-art-map.md); it does not erase that dossier or convert its proposed law into a supported result. New means newly found in this search unless a publication date is explicitly given. A three-day search window is too short to assume that every relevant older paper was already covered.

## Newly inspected close work

The [versioned response](literature/delta/response.json), [cards and bibliography](literature/delta/synthesis/), and cached artifact SHA-256 values identify the inspected material. Validation and synthesis passed with no schema warnings. That checks evidence packaging, not scientific truth or novelty. All comparisons below are agent inference from the stated versions; none is an exhaustive priority proof.

| Work and inspected primary source | Relationship to the October 25 dossier | What it pre-empts; remaining question |
|---|---|---|
| [OptMark, arXiv v1](https://arxiv.org/html/2508.21727v1), later AAAI2026 | Newly emphasized older work; method and experiments inspected | Generic optimized latent insertion with a fixed image reader is occupied. A pixel-space, fixed-content-reader intervention across independently trained codecs would require its own controlled ablation and transfer evidence. |
| [ONRW, arXiv v1](https://arxiv.org/html/2601.17388v1) | January2026; newly emphasized | Inversion-noise optimization, a pretrained extractor and semantic-preservation constraints are prior art. Calling such a pipeline RQ-02 does not create novelty; source-relative reconstruction quality remains a material constraint. |
| [DrawMark, ICASSP2026](https://msf-hnu.github.io/resource/DrawMark_Defeating_Regeneration_Attacks_by_Embedding_Watermark_into_Predicted_Noise_of_Diffusion_Models%20(1).pdf) | Newly found, not newly published this week | Noise-aware generative watermark embedding is already reported. Distinguish its learned in-generation adapters from an untrained post-hoc writer, and distinguish bit recovery from content-bound acceptance. |
| [Soft-binding benchmark, 2610.04151v1](https://arxiv.org/html/2610.04151v1) | Published2October; re-inspected relevant method/security sections | Generic watermark pointer plus descriptor registry, source-level evaluation and near-copy negatives are occupied. Any new protocol needs a new security property, not merely a new carrier. |
| [VINE/W-Bench, ICLR2025, v2](https://arxiv.org/html/2410.18775v2) | Retained comparator; methods re-inspected | A surrogate for generative editing and a generative embedding prior are occupied. VINE-R remains a required strong positive control, not a baseline that may be omitted because it wins. |
| [IAP, TIFS2023](https://arxiv.org/html/2303.11625), inspected author version | Newly explicit ownership precedent from WP1 | Embedded database pointers and source-image comparison predate the registry direction. [Version restrictions and locators](literature/tifs-bar-a.md) apply. |

The strongest new boundary is about **what is observed**: post-hoc source-preserving marking, generated-image provenance, known-message verification, arbitrary message decoding, registry retrieval and content attribution are different tasks. They cannot be pooled as a single detection score. A baseline may supply a useful carrier without establishing the proposed binding property.

## Publication-window and access gaps

[ForenMark: Semantic keyed watermarking with evidence recovery for latent diffusion images](https://www.sciencedirect.com/science/article/pii/S0950705126018101), DOI10.1016/j.knosys.2026.117084, has a publisher listing dated25October2026. Its semantic-key and evidence-recovery framing is close to content binding. The publisher returned403 on full-text opening; only the publisher preview was available. **Do not count it as full-text inspected or claim novelty cleared against it.** Its quantitative results are deliberately not used here. This is a potentially important overlap to resolve before manuscript submission, not evidence that our method is novel.

Searches restricted to 26–28 October did not yield a verified new full-text academic paper that changes the comparison. This is a search outcome, not proof of absence. [RI-Mark](https://www.sciencedirect.com/science/article/pii/S0957417426018154) and [LatentShield](https://www.sciencedirect.com/science/article/pii/S2667305326000931) also remain access-limited leads; their abstracts are not a basis for mechanism claims. The September 2026 preprint [What Limits Robustness in Deep Image Watermarking](https://arxiv.org/pdf/2609.01050) is now inspected in §§III–V: its measured mechanisms concern spatial-grid payloads and a frozen embedder with separately trained extraction. It is submitted to IEEE Access, not a TIFS publication, and does not validate an injection-SNR predictor for arbitrary published readers.

## Additional close neighbors found in the audit

These older papers materially narrow WP2 despite not being publications since October 25. Full-text sections and access qualifications are recorded in [the audit receipt](literature/wp1-delta-audit.md). This audit adds no experiments and reproduces no published result.

| Work / inspected version | What it occupies | Remaining empirical distinction, not a novelty assertion |
|---|---|---|
| [SemBind](https://arxiv.org/html/2601.20310v1), ICML 2026 identity; §§3–4, Appendices D/E | Content-derived modulation of existing latent watermark carriers; private learned semantic masker; imprinting/reprompting resistance and adaptive tests | Arbitrary pre-existing photographs, post-hoc source preservation, lightweight readout, and robust rejection of operationally distinct near-copies remain different requirements. Merely adding a semantic hash to VINE is insufficient. |
| [MetaSeal](https://arxiv.org/html/2509.10766v2), TMLR 02/2026; §§4–7, Appendix C | Self-contained content-dependent cryptographic attribution with a semantic description, signature and invertible image carrier | Appendix C explicitly reports signature verification failure after diffusion regeneration. A new carrier must preserve binding under regeneration, not merely reproduce signed semantic attribution. Signature unforgeability does not prove that two visually different images cannot share a description. |
| [SLICE](https://arxiv.org/html/2603.12749v1), preprint; §§3, 6 | Four semantic factors anchored to distinct initial-noise regions, query-side re-extraction and factor-specific tamper diagnosis | Local semantic binding is occupied too. Its VLM/auxiliary-generation/inversion setting differs from a fixed photograph plus a small post-hoc payload. Its conditional theory cannot certify our descriptor separation. |
| [Dual-Guard](https://arxiv.org/html/2604.19090v1), preprint; §§3.1, 4.1–4.3 | Initial-noise provenance channel plus final-latent content channel; owner-side reference-assisted verification | Its Full mode resolves a claimed record and stores a reference latent; closed-set authentication is distinct from open-set ownership. Two complementary channels plus a registry are not a new contribution by themselves. |
| [Guidance Watermarking](https://arxiv.org/html/2509.22126v2), ICLR 2026 identity; §§4–5, Appendix C | Training-free insertion through off-the-shelf reader gradients; augmentation gradients aggregated with PCGrad; multiple generators/readers and false-alarm analysis | An ensemble or expectation-over-transformations objective is routine prior machinery. A possible new claim must concern native injection-aware optimization, controlled source preservation and transfer to a family excluded from writer design. |
| [WARP](https://arxiv.org/html/2609.40031v1), MM 2026 proceedings identity; §§3–5, Appendix C | Unified attack/quality study of 32 methods and 34 adversarial scenarios, including regeneration and re-embedding | A larger failure table, new implementation framework, or family ranking reversal alone is insufficient. Incremental prospective prediction or a validated security improvement is needed. |
| [Latent Frequency Masking](https://arxiv.org/html/2610.02010v1), §§III–V | VAE-latent frequency replacement using Gaussian or regenerated coefficients; public-verifier-query attack setting | A new latent proxy or noise replacement attack cannot be called first. Keep its query/model access assumptions separate from the present native-regeneration threat. |

[IRIS v1](https://arxiv.org/html/2608.03539v1), §§4–5, describes endpoint-derived keyed semantic rings and late-trajectory insertion. However, the [current arXiv record](https://arxiv.org/abs/2608.03539) marks v2 **withdrawn** on August 26 for substantial revisions. Its accessible v1 is a priority-warning lead, not established performance or a usable accepted baseline. Do not silently cite it as current validated evidence.

## Retained close-work boundaries

These are bounded checks against opened primary sections and the earlier provenance cards, not a replacement survey.

| Work | Inspected object | Consequence for a new contribution |
|---|---|---|
| [Shallow Diffuse v5](https://arxiv.org/html/2410.21088v5), §§3–5 | Shallow-timestep insertion, inversion detection and conditional Jacobian arguments | No first latent, first shallow, first Jacobian, or first post-generation claim. Its local assumptions do not prove arbitrary foreign-encoder survival. |
| [MarkNull v1](https://arxiv.org/html/2608.10166v1), §§5–7 | Proxy inversion/latent removal and cross-backbone tests | No first cross-model removal claim. Orthogonality is not general independence; its conditional analysis is not a theorem for our unrelated encoders. |
| [DREW v2](https://arxiv.org/html/2406.02836v2), §§3.3–4.2 | ECC cluster pointer, conditional database retrieval, fallback search | No first hybrid watermark/fingerprint or first registry retrieval under regeneration claim. The database is detector side information. |
| [WAVES v3](https://arxiv.org/html/2401.08573v3), §§3–4 and AppendixF.1 | Detection/identification under multiple attack strengths and quality trade-offs | Another attack table alone is weak novelty. Explicit score/quality and source-level analysis are still necessary. |
| [October25 transfer map](../encoder-transfer-20261019/final-study-20261025/article-drafts/close-prior-art-map.md) | Drift Kernel, rank-ratio analysis, Early Semantic Commitment and version/access qualifications | Total drift, local rank or aggregate quality cannot be substituted for the signed response of a fixed nonlinear reader. The failed F5 tangent law stays failed. |

## Secondary distortion grid: source basis

WAVES AppendixF.1 specifies five levels spanning JPEG quality90–10, Gaussian noise standard deviation.02–.1 on [0,1], brightness/contrast increase20–100%, resized cropping removing10–50% area, and blur kernels4–20. We will use a small declared subset, state the exact interpolation, crop geometry, random seed, clipping and blur convention, and label any implementation deviation. This will be a separate descriptive article family. It does not expand thesis gates. The user's28October amendment explicitly authorizes it.

## Search receipt

Primary-source routes: arXiv full text/version records, official IEEE/SPS guidance, author-hosted manuscripts, CVF/OpenReview where accessible, publisher pages and author code pages for identity. No code, models, image data or packages were downloaded. Paper-only cache is under MAIN `.thesis-build/cache-tifs/papers/`.

Queries included: `IEEE Transactions on Information Forensics and Security watermarking 2025 diffusion`; corresponding2024 and2023 image queries; `watermark regeneration robust cross model diffusion 2026 October`; `watermark content binding robust Kazempourradi`; `watermark 2026 noise injection`; `watermark 2026 multi-encoder`; `site:arxiv.org watermark diffusion after:2026-10-24 before:2026-10-29`; `site:arxiv.org watermark 2610 regeneration`; `ForenMark pdf`; `multi VAE watermark robust 2025 2026`; and date-specific26/27October queries. Access date for this receipt is28October2026. Access failures and final-version mismatches are retained in the paper cards, rather than silently replaced with abstract summaries.

## Implication for WP2

The credible opportunity is a narrow, falsifiable improvement or a generalizable measurement result, with a clear counterfactual control. The following constraints apply before selection in `03-ideas.md`:

1. **Ensemble/noisy writer:** compare the same optimization budget and clean-quality envelope against single-encoder F5, encoder-only ensemble, blur/noise augmentation, and the proposed native-injection term. A family excluded from optimization is essential. Otherwise improvements can be explained by augmentation or model exposure already used in prior art.
2. **Content-bound robust carrier:** SemBind, MetaSeal, SLICE, Dual-Guard, DREW and soft-binding work collectively exclude generic semantic binding, cryptographic payloads, two channels and registry verification as stand-alone novelty. Declare known-record versus blind lookup; state secret versus public descriptors; test same-scene near-copies and transplant attacks with an attacker who knows the public descriptor. VINE bit presence remains a carrier control, not a content-binding baseline.
3. **Cheap survival predictor:** native latent scaling, actual scheduler timestep and noise level must enter the definition. Total latent energy can erase reader-sign information, and equal nominal strength does not imply equal channel noise. Validate incrementally over family/strength-only, clean reader margin, encoder gain and quality predictors on new outcomes. An injection ratio alone cannot be called a causal law or a lower bound on final compound acceptance.

No inspected source establishes that these narrowly stated opportunities are new. They define killable hypotheses. The strongest feasible result must still earn its distinction through an ablation or prospective validation, preserve T4/T5 binding, and explain the failed F5 tangent law without rewriting its negative outcome.

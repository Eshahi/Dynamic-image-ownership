# Thesis alignment: article evidence versus original obligations

WP8, 18 October 2026. Author: Codex agent. Read-only sources: `inputs/proposal-text.md`, the twelve OBJ/RQ/HYP rows of `research/claims.csv`, `research/scope.md`, `research/research-contract.md`, `research/acceptance.md`, and the dossier ledger. The original proposal is identified in the contract by SHA-256 `15a02877be74f5118cc7b3d3ded9ab447cc07551773486264ac4755119adfeff`. No proposal, claim ledger, source plan or institutional record was edited.

**Conclusion:** the proposed article can report a useful, bounded empirical study of regeneration recovery and registered-image attribution. It does **not** fulfill all original thesis objectives. The original latent-insertion, lightweight DCT extraction and CLIP-plus-pHash hypothesis remain open. Registry side information was authorized for development, but that authorization does not certify that a different architecture satisfies the original hypotheses or that an institutional amendment has occurred.

## Authority and wording

The approved titles remain, verbatim:

> سامانۀ پویای تملک تصویر با بهره‌گیری از نشانه‌گذاری عصبی مقاوم

> Dynamic Image Ownership With Robust Neural Watermarking

The supervisor's scope ruling, relayed by the user on 14 October, places ownership transfer, ledgers and rights management outside the thesis. The registry amendment supplies verification side information; it is not a rights-management service. Preserve both facts. A narrower article title does not automatically rename the thesis, and “dynamic” in the existing title does not authorize implementing a transfer platform.

The current session's permission is research and writing only. All proposed later experiments in WP6 remain NOT RUN. The original contract contains older planned-status text; this note uses completed-run evidence for current results while preserving unamended commitments. It does not advance a Spec Kit gate or fabricate supervisor acceptance.

## Twelve-obligation map

Source locators below refer to the mechanical proposal extraction, not newly created requirements. Status describes evidence for the **original** obligation; a related experiment is not automatically a direct test.

| ID | Original obligation and source locator | Current evidence and status | What the article covers; what remains |
|---|---|---|---|
| **OBJ-01** | Combined semantic/perceptual signature with uniqueness and tolerance to permitted changes. Proposal §4-2, Table 6, line 141. | **Partial related evidence; original completion unestablished.** Earlier combined-code behavior and T5 panels exist (EV-10–15/18–31), but registry D1+B1 accepts 3/45 eligible real pairs (EV-55/71). D1+B1 is not the specified CLIP/pHash signature. | Covers measured specificity and recovery trade-offs for the actual representation. Leaves original feature combination, uniqueness unit and permitted-edit guarantees open. |
| **OBJ-02** | Implement watermark insertion in diffusion latent space and test denoising/regeneration survival. §4-2, Table 6, line 142. | **Open.** F5 optimizes RGB pixels through an encoder-space objective; E3 is also an image-domain comparator. E1 277/300 and 280/300 measures the amended registry pipeline, not latent insertion (EV-50/51). | Covers an encoder-directed image-domain carrier under fixed channels. Does not call it the proposal's latent method or evidence that relocating insertion caused improvement. |
| **OBJ-03** | Lightweight extraction without heavy models using DCT coefficient analysis. §4-2, Table 6, line 143. | **Open.** Native extraction depends on the pinned neural encoder/profile. Historical runtime and cached registry lookup measurements do not remove those dependencies (EV-07–09/34/41). | Reports actual costs with extraction, caching and hardware qualifications. A model-free 8×8 image-DCT detector and matched quality/cost comparisons remain unestablished. |
| **OBJ-04** | Validate watermark–content binding to reject copy-paste transfer. §4-2, Table 6, line 144. | **Partially addressed under amended side information.** Retained copy-transfer tests show zero available donor-record accepts, with incomplete observations and finite access/scales (EV-14/30/54). | Covers clean-donor-assisted residual transfer and separate specificity. Does not generalize to arbitrary transplant attacks or claim original reference-free binding achieved the same result. |
| **RQ-01** | Combine semantic vectors and perceptual hashes to preserve uniqueness and allowed-edit stability. §4-2, Table 6, line 146. | **Not fully answered.** Existing semantic/exact-code and registry results concern particular representations/thresholds; look-alike rejection fails for the frozen descriptor endpoint (EV-55/72). | Offers a negative lesson on one robustness/specificity operating point, without treating descriptor failure as a proof against every CLIP+pHash construction. |
| **RQ-02** | Does moving insertion from pixels to diffusion latents significantly improve regeneration survival? §4-2, Table 6, line 147. | **Untested as stated.** F5/E3 versus v5 comparisons do not isolate latent versus pixel insertion. Post-hoc removal of the exact-H gate changes interpretation of earlier gains (EV-20–25); SD2.1 is not independent-encoder evidence (Q-VAE). | Covers observed carrier and registry outcomes, not the proposed causal location comparison. An amendment or a separate direct study would be needed. |
| **RQ-03** | Can mid-frequency statistical detection match neural decoder accuracy with higher speed? §4-2, Table 6, line 148. | **Open.** No matched, full-pipeline neural-decoder accuracy/noninferiority and latency comparison establishes this result. EV-41 is cached lookup and cannot answer it. | Honest timing taxonomy only. Neural-decoder comparator obligation remains distinct from HYP-03's inversion comparator, as the research contract states. |
| **RQ-04** | Distinguish an original from different content carrying a copied watermark. §4-2, Table 6, line 149. | **Partially answered for tested access and rule.** Available T4 counts are favorable but finite; descriptor-only E2 is a separate negative relation and E3 is passive enrollment (EV-54/55/58–66). | Reports false donor-record acceptance separately from delivery and abstention. Does not combine distinct threats into one “forgery accuracy.” |
| **HYP-01** | CLIP-derived semantic plus pHash-derived perceptual features reduce semantic collisions. §4-5, Table 9, line 232. | **Not established by this article.** D1 is a native fine-detail vector and B1 a gray-layout vector; they are not CLIP/pHash. Neither E1 success nor D1+B1 failure is a direct test of the exact hypothesis. | Cite the hypothesis as original motivation, then state the actual method change. No substitution of feature names. A later direct combination-versus-component comparison needs its own evidence. |
| **HYP-02** | Latent insertion increases regeneration survival relative to pixel insertion. §4-5, Table 9, line 233. | **Untested as stated.** Encoder-space objectives applied to RGB do not move the insertion variable to a latent. v5, E3 and F5 differences do not provide the isolated contrast. | Preserve as open; no inference from strong E1 or literature results to local hypothesis acceptance. |
| **HYP-03** | DCT-statistical extraction reduces cost versus diffusion-inversion decoders without important accuracy loss. §4-5, Table 9, line 234. | **Open.** No prespecified quality noninferiority margin and matched end-to-end inversion baseline support it. Model-dependent extraction plus cached descriptor comparison does not satisfy the premise. | Cost observations only; SEAL or any other comparator must be verified for the actual inversion role before selection. No “inversion-free therefore lightweight” shortcut. |
| **HYP-04** | Mathematical content dependency exposes copied watermarks via signature mismatch. §4-5, Table 9, line 235. | **Bounded supportive observations, no universal proof.** Copy-transfer outcomes support tested rejection; broad binding is limited by same-shot descriptor failures and unevaluated active access. E2 failure is not itself a measured T4 full-system forgery. | Explains exact acceptance logic and uncertainty. Reject “any attempt necessarily fails”; registry conjunction is an empirical condition, not cryptographic content authentication. |

## Preserve the research questions verbatim

For a later thesis chapter or amendment comparison, these are the existing questions from `research/scope.md` and the proposal extraction; the English table above is an operational summary, not a replacement.

1. چگونه می‌توان با تلفیق بردارهای معنایی و کدهای هش ادراکی، امضایی برای تصویر تولید کرد که همزمان با حفظ یکتایی، در برابر ویرایش‌های مجاز پایدار باقی بماند؟
2. آیا انتقال محل جاسازی واترمارک از فضای پیکسل به فضای پنهان در مدل‌های انتشار، تأثیر معناداری بر افزایش نرخ بقای واترمارک در برابر حملات بازتولید خواهد داشت؟
3. چگونه می‌توان با تحلیل آماری ضرایب فرکانسی میانی، وجود و صحت واترمارک را با دقتی قابل رقابت با دیکودرهای عصبی اما با سرعت بیشتر تشخیص داد؟
4. آیا معماری پیشنهادی توانایی تفکیک میان تصویر اصلی و تصویر جعلی که دارای واترمارک کپی‌شده است را دارا می‌باشد؟

## Method vocabulary the thesis must keep separate

| Phrase | Accurate use in this project | Prohibited substitution |
|---|---|---|
| Image-domain writer | F5's optimized variable is RGB; the known encoder defines an objective. | Calling gradient flow through a VAE “latent insertion.” |
| Encoder-space carrier objective | Explains where a margin/feature constraint is measured, as an implementation property. | Claiming a proved causal amplification mechanism or all-encoder survival. |
| Native detector | Uses its pinned neural model/profile and owner-conditioned code construction. | Calling an internal DCT transform a model-free lightweight extractor. |
| Registry verification | Uses trusted associations and stored descriptors of the published marked reference; includes an explicit D1-abstention fallback. | Describing the detector as reference-free, CLIP+pHash, or always requiring two descriptors. |
| Registered-image attribution | Acceptance of records/owners under specified access and matching rules. | Creator authentication, legal ownership, rights transfer, or cryptographic unforgeability. |
| Unseen checkpoint | SD2.1-base was outside the writer's evaluated development channel; encoder ancestry remains shared. | Independent-autoencoder transfer based on unequal serialized full-VAE hashes. |

Suggested thesis wording: “The implemented and evaluated system is an image-domain comparator with an encoder-space objective and an explicitly authorized registry-verification amendment. It supplies empirical evidence about regeneration recovery and record attribution under specified conditions. It does not establish the original latent-insertion or lightweight DCT-extraction hypotheses.”

## Other proposal obligations not discharged by a journal article

- **Data/domain coverage:** original commitments include 1,000 COCO images, DIV2K 800 training plus 100 validation images, and 5,000 DiffusionDB images. The reviewed 300-image panels do not silently replace those commitments. Dataset-native split labels are not study split definitions, canonical 512 images are not a native-2K evaluation, and camera-originated results do not establish existing-generated-image generalization.
- **Quality:** retain PSNR >35 dB, SSIM >.9 and LPIPS <.1 as stated targets. In the registry run, 291/297 available marks and 291/300 attempted sources met all three; no human ratings exist (EV-67/73). Do not call every mark imperceptible.
- **Threat scope:** current work prioritizes T3/T4/T5. Older proposal text mentioning benign transformations does not authorize spending this session on T1/T2. Whether those remaining narrative commitments need a formal amendment belongs to the supervisor.
- **Scientific conclusion:** a hypothesis may remain unsupported or receive negative evidence. Reporting that honestly is a thesis outcome; converting an amended method into a purported test of the original hypothesis is not.
- **Administrative acceptance:** a well-supported article and a Q1 venue do not by themselves certify degree requirements, chapter finalization, authorship or submission approval.

## Decisions for the user and supervisor

No answer is requested during this autonomous session. Defaults preserve the original documents and the bounded article framing.

1. **Thesis versus article scope:** retain the original proposal and present this as an empirical chapter/comparator, or pursue an explicit institutional amendment toward registry-assisted attribution? Default: retain original obligations and label gaps.
2. **Original latent/DCT/CLIP+pHash obligations:** must they be directly tested later, accepted as unresolved negative scope, or formally revised? Default: unresolved; this dossier does not reopen closed method families or authorize new experiments.
3. **Identity criterion:** accept the frozen PSNR-based operational relation for reporting, and decide whether future work needs blinded human/source-provenance labels. Default: preserve old labels and call them operational. A user's relayed provisional professor agreement is not an independently documented institutional amendment.
4. **Title and ownership language:** decide whether the approved thesis title needs a formal change given the exclusion of transfer/ledgers. Default: retain it verbatim in protected records, use the narrower article title, and avoid legal ownership conclusions.
5. **Remaining data/quality/domain commitments:** agree on any formal reduction or substitution, including DiffusionDB/native-resolution obligations and human visual evaluation. Default: no silent substitution.
6. **Future evidence authorization:** consider F1/F2 and, for broader TIFS claims, F3; expressly decide whether closed external-baseline work is reopened. Active claims additionally require F4. Default: all NOT RUN.
7. **Journal eligibility and publication:** specify JCR/SCImago edition and category, confirm institution rules, authorship, funding and later submission authority. Default: TIFS is conditional; TMM/TOMM are backups; no external action.

This note resolves reporting language now while preserving every scientific and institutional decision that the dossier cannot make on behalf of the user.

# JigMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **JigMark: A Black-Box Approach for Enhancing Image Watermarks against Diffusion Model Edits**. Version/date: arXiv:2406.03720v1 [cs.CV] 06 Jun 2024. Venue: arXiv2024; venue not independently verified.

Authors: Minzhou Pan; Yi Zeng; Ning Yu; Cho-Jui Hsieh; Peter Henderson; Ruoxi Jia; Xue Lin. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2406.03720v1`. Citekey: `T3JigMark2406`. Canonical URL: https://arxiv.org/abs/2406.03720v1

Primary full text: https://arxiv.org/html/2406.03720v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/jigmark.txt`
SHA-256: `4dab1981ae4f549cf3ec66d3ae125c814220273fc903f6224f5774769e951fee`

Actually inspected: §§4.1–4.2,5.1–5.4,Table 3; Appendix D.3–D.4,F.1, Tables 7–9; official README/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A black-box training approach embeds a key-dependent watermark using jigsaw permutations and a human-aligned variation discriminator to distinguish useful edits from destructive changes.

## Native operating point and detector side information

The 4×4 shuffle provides 16! permutations, approximately 44 bits of key entropy, not a recoverable 44-bit payload. This is a zero-bit detector requiring the key. Native TPR at 1% FPR uses ROC calibration; no universal numerical threshold is published. The exact released normalization, quantization and inference resolution are unverified; batch size 256 is not image resolution.

## Code, weights, pinned release and licenses

pmzzs/JigMark@4e51cd1ebcf6b95ca01e286d086f9e8883df4621 has an inspected MIT LICENSE. The README's HAV and JigMark checkpoint links are literal '[Download Link]' placeholders, so usable weights remain unverified. An earlier milesfun/jigmark 404 was a failed lead, not official provenance.

## Published evaluation and regeneration conditions

The evaluation uses 2,000 ImageNet images and LLaVA instructions, retaining edits with HAV in [.3,.5]. Table 3 TPR at 1% FPR is .945 for SDEdit, .953 for Prompt-to-Prompt, .876 for Zero123, .873 for inpainting and .721 for DALL-E 2 (mean .874). DALL-E fine-tuning improves .721 to .824 after 600 updates costing $96; that is not zero-shot transfer. Quality is 30.1354/.89372/.06572. Training uses 50–80 SDEdit steps, strengths ramped from .1–.2 to .2–.8, CFG 5–20 and random instructions; those training ranges are not a complete exact evaluation attack specification.

## Cost and uncertainty

The paper describes 1,000 A100 GPU-hours and a separate 40-hour, eight-A100 key-retraining setting. Neither is inference time. Usable checkpoints and target memory remain unresolved; no retraining expenditure is proposed.

## Limitation and design implication

Valuable black-box edit evidence, but HAV filtering, 1% FPR, poor native quality and missing checkpoints make it a lower-priority comparison.

Disposition: **Literature coverage; excluded**

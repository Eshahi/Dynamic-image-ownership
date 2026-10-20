# DC-AE supporting encoder evidence

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §3 residual shortcuts/three-phase training; reconstruction tables; high-resolution efficiency comparisons.

Primary paper: [2410.10733v1](https://arxiv.org/html/2410.10733v1). Cached original SHA-256 `379cb7cff3040afea41fb34d8fb7d0785b1d5d3e84d867e0ef6c684f783ee993` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-dcae-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Continuous nonvariational deep-compression AE; SANA uses C32/f32. Paper studies f64/c128 and f128/c512 too; denoiser patch size is separate from AE compression.

**Quantitative evaluation and conditions (direct source account):** Table2 ImageNet512 reconstruction: f64/c128 rFID16.84→.22 and f128/c512100.74→.23 with the proposed training/shortcuts. Reconstruction tradeoffs do not imply better preservation of a watermark.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: qualified distinct training lineage. Three phases train on ImageNet/SAM/Mapillary/FFHQ; no SD initialization is stated. Architectural resemblance alone is not independence evidence.

**Official code and img2img:** DC-AE encode/decode is used by Sana and Sprint classes. Standalone reconstruction is possible conceptually, but no execution/adapter was built.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Efficient-Large-Model/Sana_600M_1024px_diffusers](https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/tree/28f3af7689de15f3883d5863059a2fca0aa9b829) | 28f3af7689de15f3883d5863059a2fca0aa9b829 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Primary19.1× H100 speedup concerns UViT-H512, not1024 batch-one AE or full-generation latency. AE-only memory/seconds unknown; dense weights and activations must be measured later.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Supports the SANA family independence rationale; does not add another family to the floor.

**Limits/open assumptions:** No full diffusion result can be inferred from encoder-only reconstruction quality.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Efficient-Large-Model/Sana_600M_1024px_diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-api.json | 2b939300a75454a6353dc0ae6541f639aba9db79a64c0f8d2ea1d2518a460b8e |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-README.md | 956e2d4cc2706eae2a1408349325b0a9786aac24dbaae4d0c9f6c3ada25e229c |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-vae--config.json | 4e5669aa03caa77615b73b21c9347c384cb11124a9590683e32a510df0176eb4 |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-model_index.json | 5692423f50e7908bec51264ad39e5a9b7566970600f6089a0a40759524f5569b |
| https://arxiv.org/html/2410.10733v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-dcae-paper.txt | 379cb7cff3040afea41fb34d8fb7d0785b1d5d3e84d867e0ef6c684f783ee993 |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--README.md.txt | 956e2d4cc2706eae2a1408349325b0a9786aac24dbaae4d0c9f6c3ada25e229c |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--vae--config.json.txt | 4e5669aa03caa77615b73b21c9347c384cb11124a9590683e32a510df0176eb4 |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--model_index.json.txt | 5692423f50e7908bec51264ad39e5a9b7566970600f6089a0a40759524f5569b |
| https://arxiv.org/html/2410.10733v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-dcae-paper.read.txt | cc72c1aa6f6db11a14c3bf69abcab0a4e67dc45b7b492e4475221e787fb87b4e |

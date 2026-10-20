# Stable Diffusion 3 / 3.5

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3 rectified flow; §5.2.1/Table3 VAE channels; AppendixE.1/Table7 component memory/throughput.

Primary paper: [2403.03206v1](https://arxiv.org/html/2403.03206v1). Cached original SHA-256 `f82ef37115732eb873f96dbc7bb0baad3fd95b1e711aac2868b2ed43801a6c91` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sd3-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** MMDiT rectified flow, KL VAE C=16/f=8 with latent scale/shift. SD3.5 grouped withSD3; model size/version is not a fresh AE family.

**Quantitative evaluation and conditions (direct source account):** Table3 C16 VAE PSNR28.62/SSIM.86/FID1.06 versus C4 25.12/.75/2.41; dataset/resolution not clear in inspected caption, so do not assign COCO/1024. Generator-quality gains do not establish encoder-transfer survival.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1: UNKNOWN initialization. vs SDXL: UNKNOWN initialization. Table3 proves a wider bottleneck and improved reconstruction, but does not explicitly establish random initialization or absence of SD weights.

**Official code and img2img:** stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py: native image+strength; get_timesteps/encode with shift+scale and flow scheduler. Equal numeric DDIM/flow strength is not equal corruption.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [stabilityai/stable-diffusion-3-medium-diffusers](https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers/tree/ea42f8cef0f178587cf766dc8129abd379c90671) | ea42f8cef0f178587cf766dc8129abd379c90671 | other | auto gated |
| [stabilityai/stable-diffusion-3.5-medium](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/b940f670f0eda2d07fbb75229e779da1ad11eb80) | b940f670f0eda2d07fbb75229e779da1ad11eb80 | other | auto gated |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

2B denoiser≥4GB BF16 weights. AppendixE.1: VAE encoder weights.14GB and2.45ms forward at batch32; T5 weights19.05GB. Component reports are not1024 batch-one peak/runtime. Complete residentT5 pipeline needs offload/more memory; candidate runtime unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Potential larger-panel architecture contrast if access and ancestry gaps resolved; exclude gated models now.

**Limits/open assumptions:** SD3Medium noncommercial research terms; SD3.5 Community terms differ. Both API snapshots auto-gated. Public text does not authorize gated weights.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/stabilityai/stable-diffusion-3-medium-diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-3-medium-diffusers-api.json | fb0a542c88ee1ea608cc186c3d848cd7ef43de5aea277246c0eb5692c80fa9f1 |
| https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers/resolve/ea42f8cef0f178587cf766dc8129abd379c90671/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-3-medium-diffusers-README.md | f493f3746d6794edaa046dbbe41f94e73c406d378e933373eae556f45fc94faf |
| https://huggingface.co/api/models/stabilityai/stable-diffusion-3.5-medium?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-3.5-medium-api.json | 4270aa57ce84ec129efdfdf423d08cfd0d33514a0fc06012df611d153fd29858 |
| https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/resolve/b940f670f0eda2d07fbb75229e779da1ad11eb80/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-3.5-medium-README.md | 076c5b3ce1cb9bd33751656cac2b094b6ab93212a82624dab5405f4596737f7a |
| https://arxiv.org/html/2403.03206v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sd3-paper.txt | f82ef37115732eb873f96dbc7bb0baad3fd95b1e711aac2868b2ed43801a6c91 |
| https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers/resolve/ea42f8cef0f178587cf766dc8129abd379c90671/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-diffusion-3-medium-diffusers--README.md.txt | f493f3746d6794edaa046dbbe41f94e73c406d378e933373eae556f45fc94faf |
| https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/resolve/b940f670f0eda2d07fbb75229e779da1ad11eb80/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-diffusion-3.5-medium--README.md.txt | 076c5b3ce1cb9bd33751656cac2b094b6ab93212a82624dab5405f4596737f7a |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_3--pipeline_stable_diffusion_3_img2img.py-api.txt | b1c1339460d12909c397fa86415d16ee323964ebd6c60e27f68cf1743510565e |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_3--pipeline_stable_diffusion_3_img2img.py-api.decoded.txt | e9a733a53c0cb6ca618f251298605e4888f8cde37719098ba9239dc046d8bb28 |
| https://arxiv.org/html/2403.03206v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-sd3-paper.read.txt | ccb84f6f2f93cc08f25a48ebb0a2fdbceaa64de5420de0c6fa8e8cc6f0cbd8ae |

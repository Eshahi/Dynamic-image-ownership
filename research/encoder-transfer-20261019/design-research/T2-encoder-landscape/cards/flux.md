# FLUX1, FLUX2 and FLUX3 native model evidence

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **NATIVE PRIMARY MODEL/CODE — explicitly not paper V2**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: Official modelcards Architecture/Usage/Limitations; official autoencoder code; current model API gates; FLUX2 Klein pipeline signature.

**Method evidence (direct source account):** FLUX1 C16/f8,12B flow transformer. FLUX2 C32/f8 with2×2 packing gives128 channels/f16 token grid; code ch_mult=[1,2,4,4]. FLUX3 is a newer flow-map release, not proof of newly initialized AE.

**Quantitative evaluation and conditions (direct source account):** Native cards/code substantiate architectures and reported operational numbers, but no opened full FLUX training/evaluation paper establishes AE initialization or watermark behavior. Distinguish primary model evidence from paper V2; excluded from conservative18-paper floor.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: UNKNOWN initialization for all inspected FLUX generations. Different channels or names do not prove independent training. FLUX2 adoption by Lens is reuse.

**Official code and img2img:** v0.36.0 flux/pipeline_flux_img2img.py supports image+strength for FLUX1. Current flux2/pipeline_flux2_klein.py accepts image conditioning but no strength, despite being an editing pipeline.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9) | 741f7c3ce8b383c54771c7003378a50191e9efe9 | apache-2.0 | auto gated |
| [black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev/tree/3de623fc3c33e44ffbe2bad470d0f45bccf2eb21) | 3de623fc3c33e44ffbe2bad470d0f45bccf2eb21 | other | auto gated |
| [black-forest-labs/FLUX.2-dev](https://huggingface.co/black-forest-labs/FLUX.2-dev/tree/26afe3a78bb242c0a8bb181dcc8937bb16e5c66c) | 26afe3a78bb242c0a8bb181dcc8937bb16e5c66c | other | auto gated |
| [black-forest-labs/FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/tree/e7b7dc27f91deacad38e78976d1f2b499d76a294) | e7b7dc27f91deacad38e78976d1f2b499d76a294 | apache-2.0 | ungated API snapshot |
| [black-forest-labs/FLUX.2-klein-9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/tree/92196c8e11f7b6cf2b7493e037d8c5345c559216) | 92196c8e11f7b6cf2b7493e037d8c5345c559216 | other | auto gated |
| [black-forest-labs/flux-3-image-klein](https://huggingface.co/black-forest-labs/flux-3-image-klein/tree/337337621b8526e120f2275d250242f4a6bedd75) | 337337621b8526e120f2275d250242f4a6bedd75 | other | auto gated |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

FLUX1 denoiser12B≥24GB BF16 before T5/VAE. FLUX2 Klein4B card claims~13GB/subsecond without matched conditions;9B~29GB. FLUX3 card reports B2001024 with prompt upsampler off: BF16 peak31GB,FP8 26GB,NVFP4 25GB; upsampler adds28GB on80GB devices. None measures our target1024 img2img.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Retain gated FLUX1 exclusion. Ungated Klein4B is available under Apache but is not an equivalent strength-controlled replacement and not proven independently initialized.

**Limits/open assumptions:** API auto-gated: FLUX1-schnell despite Apache, FLUX1-dev customNC, FLUX2-dev/custom, Klein9B/custom, FLUX3/KommUnity. Klein4B ungated Apache. Public README availability is not ungated weight access.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/black-forest-labs/FLUX.1-schnell?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.1-schnell-api.json | bf8cdd32fd989f82c7cbd1f5eee55b9deb4301ed1e31a5978c2ba47b50426785 |
| https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/741f7c3ce8b383c54771c7003378a50191e9efe9/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.1-schnell-README.md | 66f915ff73552215a78f83852312eda079af1f5a08a258b6b6733350101c58aa |
| https://huggingface.co/api/models/black-forest-labs/FLUX.1-dev?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.1-dev-api.json | ad065fb3e15b7b45d5de7957e9e60571dd77af48812be3087bd6c6777623457f |
| https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/3de623fc3c33e44ffbe2bad470d0f45bccf2eb21/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.1-dev-README.md | efaf627d78af42f5ff92ec6c05551237c6939dbc1a8ee83910b9b5c7340d34cf |
| https://huggingface.co/api/models/black-forest-labs/FLUX.2-dev?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-dev-api.json | 1e9101c07f33c92888d6a384ae4466621b2478c430464b4ef94826f1967d501c |
| https://huggingface.co/black-forest-labs/FLUX.2-dev/resolve/26afe3a78bb242c0a8bb181dcc8937bb16e5c66c/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-dev-README.md | f161ac5822374c29c1df2ba13ea8567a7a5318d3b0ec6ac0b1b9f00c596f300b |
| https://huggingface.co/api/models/black-forest-labs/FLUX.2-klein-4B?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-4B-api.json | 938f962aa6d2690d753556037e4cdd4d7cec08820de308b3c94fd5e51c0e1352 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-4B-README.md | bd447051cf2db4bf67b992e563d89c35ebf1123f009c063361a222ab14e1c4f7 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-4B-vae--config.json | 0d6dfb69ae95a5e2ac9836284bbb63d8b38ce67b25ba2dff380752b2a10ab948 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-4B-model_index.json | 51a76cb1cf3ed37423a1128c79c22faee8e6fbe7f5aaeb737f0a258930dbaac0 |
| https://huggingface.co/api/models/black-forest-labs/FLUX.2-klein-9B?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-9B-api.json | b4342170edbe9b3eefc3d76a876a5d867078f620abdd0b36bd281603d03b2cf9 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/resolve/92196c8e11f7b6cf2b7493e037d8c5345c559216/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--FLUX.2-klein-9B-README.md | 1328d32010b8e372df5d4c572d1a7cf3535ec0063578dcb7d60bc2f5b7d0f3f0 |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/pipelines/flux/pipeline_flux_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-flux-pipeline-v036.txt | 57dfd7fb482e7028659626deb89c35b60f8b292fc4720db363739f051083f033 |
| https://huggingface.co/api/models/black-forest-labs/flux-3-image-klein?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-black-forest-labs--flux-3-image-klein-api.txt | 7668f6b03deaeabf1708c98b0c75914ad79e3a1563773df3b38da5d88eea7209 |
| https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/741f7c3ce8b383c54771c7003378a50191e9efe9/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.1-schnell--README.md.txt | 66f915ff73552215a78f83852312eda079af1f5a08a258b6b6733350101c58aa |
| https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/3de623fc3c33e44ffbe2bad470d0f45bccf2eb21/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.1-dev--README.md.txt | efaf627d78af42f5ff92ec6c05551237c6939dbc1a8ee83910b9b5c7340d34cf |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.2-klein-4B--README.md.txt | bd447051cf2db4bf67b992e563d89c35ebf1123f009c063361a222ab14e1c4f7 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.2-klein-4B--vae--config.json.txt | 0d6dfb69ae95a5e2ac9836284bbb63d8b38ce67b25ba2dff380752b2a10ab948 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/resolve/e7b7dc27f91deacad38e78976d1f2b499d76a294/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.2-klein-4B--model_index.json.txt | 51a76cb1cf3ed37423a1128c79c22faee8e6fbe7f5aaeb737f0a258930dbaac0 |
| https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/resolve/92196c8e11f7b6cf2b7493e037d8c5345c559216/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--FLUX.2-klein-9B--README.md.txt | 1328d32010b8e372df5d4c572d1a7cf3535ec0063578dcb7d60bc2f5b7d0f3f0 |
| https://huggingface.co/black-forest-labs/flux-3-image-klein/resolve/337337621b8526e120f2275d250242f4a6bedd75/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\black-forest-labs--flux-3-image-klein--README.md.txt | cca5f3490d05e506c4d10e2443405372303a0f59d3e249b7413e6588290d5d12 |
| https://api.github.com/repos/black-forest-labs/flux/contents/src/flux/modules/autoencoder.py?ref=802fb4713906133fcbd0d8dc5351620ca4773036 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\flux-ae-code.decoded.txt | cc022bc661b6df332ba542487584a4b53b6bbf80f3dd0e40b6cf9bc6b571b86e |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/flux2/pipeline_flux2_klein.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-flux2--pipeline_flux2_klein.py-html.txt | 48e5489baa8bf1beedb7bcbc5bdf9d846b7bf40bc77fc092be65260fc10409bf |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/flux2/pipeline_flux2_klein.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-flux2--pipeline_flux2_klein.py-html.decoded.txt | 9f825080f37fa94494bf218f10375cd83f29bf23c4e4653e4735a061e1631455 |
| https://github.com/black-forest-labs/flux2/blob/50fe5162777813d869182b139e83b10743caef15/src/flux2/autoencoder.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\flux2-ae-html.decoded.txt | 28c0f82faeced3b160922ce00262ccc4dba85901a2bb66f877acc85a52e5e62f |

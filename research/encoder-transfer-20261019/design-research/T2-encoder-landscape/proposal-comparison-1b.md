# Bounded proposal comparisons: P4, P7 and possible P10

No protocol, asset plan, fixed decision rule or execution authorization changes here. Core R2 FLUX1-schnell stays disabled. Core uses60 development sources, four marked arms plus C0, three strengths and three seeds. A full added regenerator costs60×5×3×3=2700 outputs, one strength900 outputs, deterministic AE-only300 outputs. Earlier estimates omitting C0 undercounted by25%.

## P4: Kandinsky3 / MoVQ

Prefer P4 over a new FLUX2 Klein proposal when the question is encoder-training transfer: documented separate MoVQ training, native1024 and native image+strength interface are stronger than a different latent channel count. This is qualified documentary independence, weaker than SDXL's explicit from-scratch statement. Its large text encoder means28.391GB advertised components and phased offload; speed is unmeasured. A full added2700-output grid at an assumed8s/output plus.7h setup adds6.7h. One strength adds2.7h. Those are planning scenarios, not primary timings, and cannot be promised inside core10–14h/15h cap.

An AE-only300-output diagnostic at an assumed1s/output plus.5h setup adds.583h. It can fit after a14h core only if this time is actually reserved and the later timing-only check supports it. It tests compression survival, not full regeneration. Selecting the roughly.541GB MoVQ component alone would bring core model assets to about20.747GB; selecting full KD3 instead would bring them to about48.597GB, exceeding the current40GB asset/retry reservation. No such addition is approved here.

## P7: pixel-space regeneration

HiDream-O1 replaces DDPM as the strongest **high-resolution pixel-method research lead**, with a primary methods/evaluation report and MIT ungated package. It does not replace PRX as the direct1024-interface lead: official O1 code snaps square requests to2048, while PRX has native1024 examples. O1 reference editing starts target RGB Gaussian noise and uses reference context; there is no strength. PRX is also T2I-only, so source-noise regeneration requires new code/scientific calibration. DDPM256 faces remains a small mechanism control, not a general-photo1024 attack.

O1 official model index contains8,804,887,792 parameters, implying17.609775584GB BF16 parameter storage before activations/KV. Its eight published files total35.219643552GB. Added to20.206GB frozen core gives55.425643552GB before packages, images and extra dependencies: below the future80GB absolute cap, but above the current40GB asset/retry reservation and therefore requiring an explicit revised download allocation if proposed. No downloads occurred. Plain inference loads bundled local processor/model; optional Gemma prompt refiner is gated and optional API rewriting can cost money. Neither is part of this proposal.

Native2048 has four times as many pixel patches as1024 and potentially much larger attention workspace; no1024 or2048 target-device peak/runtime has been measured. A900-output pilot at hypothetical10/30/60s each would add2.5/7.5/15h plus setup. These sensitivity scenarios make no throughput claim. P7 is research-only, outside the frozen15h plan.

## Possible P10: ungated FLUX2 Klein4B

**Do not recommend a separate P10 for this encoder-transfer study.** It is Apache2 and genuinely ungated at revision `e7b7dc27f91deacad38e78976d1f2b499d76a294`, but encoder initialization versusSD1/SDXL remains unknown. Its C32/f8 AE is not proved independent merely because it differs from FLUX1's C16/f8. P4 has clearer separate-training evidence.

Current pinned Diffusers `flux2/pipeline_flux2_klein.py` accepts image conditioning, not strength. This provides native high-resolution editing but not the frozen partial-noise regeneration interface; it also differs from frozen Diffusers0.35.1. Card~13GB/subsecond claims lack matched target hardware/settings; target1024 peak/runtime unknown. Consequently neither scientific equivalence nor guaranteed budget fit is established.

Selected Diffusers-format weights total **15964212614 bytes (15.964212614GB)**; do not also select the duplicate top-level single-file checkpoint. Core+these weights ≈36.170212614GB before metadata/packages/images, leaving little room in the40GB asset/retry reservation. The package includes Qwen text weights; the inspected direct path does not require downloading gated FLUX1. That does not prove unrestricted rights for every future dependency.

| Selected official file | Bytes | Advertised LFS SHA |
|---|---|---|
| text_encoder/model-00001-of-00002.safetensors | 4967215360 | 8c0506e7f4936fa7e26183a4fd8da4e2bdbc5990ba64ae441f965d51228f36ea |
| text_encoder/model-00002-of-00002.safetensors | 3077766632 | 82f2bd839378541b0557bfabaf37c7d3d637071fdcb73302dedd7cf61162ce07 |
| transformer/diffusion_pytorch_model.safetensors | 7751109744 | 9f29f9edcfdae452a653ffb51a534ca4decd389952c225724ff3b94042612a6e |
| vae/diffusion_pytorch_model.safetensors | 168120878 | ca70d2202afe6415bdbcb8793ba8cd99fd159cfe6192381504d6c4d3036e0f04 |


If a user later wants a distinct editing experiment, a2700-output Klein grid at hypothetical2/5/10s/output adds1.5/3.75/7.5h plus.5h setup. Even its lowest scenario is not guaranteed inside a14h core. A900-output instruction-editing pilot would be a different corruption scenario and must not be labelled fixed strength. No P10 is inserted and no disabled R2 is reactivated.

## Highest diversity within budget and larger-panel cost

The guaranteed design recommendation is the unchanged core: SD1 anchor plus independently trained SDXL. With at most1h slack after a14h core, one preapproved AE-only MoVQ diagnostic is the most defensible extra training-lineage contrast under the illustrative.583h assumption. Three extra AE-only diagnostics (MoVQ, DC-AE, Wan) would cover five documentary encoder lineages includingSD1/SDXL, adding900 outputs and1.75h under that same assumption; only the lower part of the10–14h core estimate could fit15h. This is not guaranteed and not an approved expansion.

For a larger full-regenerator panel, add KD3, a separately calibrated DC-AE/SANA schedule and Qwen/Wan,2700 outputs each (8100 extra). Planning examples8/2/20s per output yield6+1.5+15=22.5h generation, plus3h total setup:25.5h extra,35.5–39.5h total with the core. At a scenario rateUSD1/h this isUSD35.5–39.5, before additional contingency. Rates and throughputs are assumptions, not live rental quotes. SANA's few-step schedule must first be redesigned/calibrated; until then this is a cost envelope, not an executable equal-strength panel.

The larger full-model panel also needs a revised download allocation. Even parameter storage at BF16 for Qwen's20B denoiser plus7B text encoder is at least54GB, before VAE or serialized-file overhead. Adding core20.206GB and full KD3≈28.391GB already gives more than102.597GB before SANA, packages or images, beyond the present80GB total-download cap. Streaming/offload reduces accelerator residency, not the cumulative downloaded bytes. AE-only selection has a materially different resource profile and scientific question.

Adding a pixel900-output scenario would add2.5–15h plus setup under the hypothetical rates above. The larger panel therefore requires a new budget/design decision; it cannot be disguised as a small within-cap substitution.

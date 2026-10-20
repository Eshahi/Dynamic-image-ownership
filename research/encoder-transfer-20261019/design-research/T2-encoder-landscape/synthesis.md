# T2 encoder landscape: expanded §1b synthesis

The unchanged SD1.5 anchor plus SDXL remains the cheapest decisive experiment with the clearest primary-source encoder independence. The deeper sweep contains18 distinct qualifying paper families,30 individual Markdown cards and25 inspected-paper records. It covers the named families, contemporary FLUX/Qwen/Kandinsky changes, new pixel models and released-model constraints. Model-family count is not encoder-lineage count.

## Evidence standard and scope

Each qualifying card records method and evaluation inspection, exact arXiv revision, source URL/cache SHA, architecture/channels/compression, lineage versusSD1 andSDXL, official release pins/licenses/actual gates, native source interface and1024 resource limits. V2 denotes inspection of methods and evaluation, not “arXivv2.” Native modelcards are explicitly distinguished and are not used to pad the18-paper floor. Metadata-only or unevaluated leads are nonqualifying. All16 old JSON cards now have individually rechecked Markdown counterparts; the old JSON/dossier files are historical leads, and this §1b package controls updated claims.

`lineage-settings-matrix.md` gives the readable comparison; `.csv` retains all exact fields. `manifest-receipts-1b.json` retains original and derived text receipts, failures and alternatives. `references-1b.bib` is topic-local for later parent merge:26 entries, including the paired PixArt-Alpha source beyond the25 structured paper records. `skill-synthesis-1b-final/` is the validated final paper-only export; `skill-synthesis-1b/` is a superseded intermediate directory and must not be merged. No shared bibliography or protocol was edited.

## What changed after primary inspection

1. SDXL §2.4 explicitly trains its AE from scratch with the same4-channel/f8 architecture. It remains the strongest independence anchor. Core VAE precision means full fp32 execution of the pinned official fp16 checkpoint values, not substitution of the separate fp32 file. Frozen selected SDXL assets are6.941187536GB.
2. SD2 decoder fine-tuning does not establish a new encoder. SD3/3.5 C16/f8 establishes a wider representation but leaves initialization versusSD1/SDXL unresolved in inspected text.
3. PixArt-Σ, Playground, Hunyuan-DiT, OmniGen and AuraFlow reuse SDXL-class encoder assets; multiple new generator names do not multiply encoder diversity. Hunyuan's SDXL-from-SD1.5 description conflicts with SDXL's original from-scratch account; retain the original creator source.
4. MoVQ and DC-AE have separate documented training procedures and are useful qualified independent-lineage candidates. MoVQ code may bypass codebook quantization; paper VQ ablations cannot silently define Diffusers runtime. DC-AE compression is f32/c32, not merely another f8 VAE.
5. Qwen-Image freezes the Wan encoder and fine-tunes its decoder (§2.3); improved reconstructions do not establish a new Qwen encoder. New Qwen2.1 is RGBA/z64/spatial16/temporal8. Its initialization and mapping to Qwen-VAE2 paper variants remain unresolved.
6. Lumina2, HiDream-I1, Z-Image and Chroma reuse FLUX1. HiDream README says schnell while config path says flux-dev; family reuse is supported, exact object identity is not inferred. Kandinsky5 images also adopt FLUX1-dev, unlike Kandinsky2/3 MoVQ.
7. Lens explicitly adopts FLUX2 VAE. FLUX2 is32-channel/f8, packed to128/f16 tokens; this does not prove fresh initialization. Ungated Apache Klein4B is real, but its native editing API lacks strength and does not replace disabledFLUX1.
8. Native pixel-space methods are no longer limited to small DDPM face models. PixelGen, PixSGR and HiDream-O1 have inspected methods/evaluations. Availability and protocol fit differ sharply: PixelGen native512 with code-license gap; PixSGR no released weights; O1 MIT/ungated but current square-resolution interface snaps to2048. PRX offers native1024 code but lacks a sufficiently specified quantitative evaluation in its card.

## Resource and interface conclusions

Published resource reports were actively sought. OmniGen documents1024 A800/3090 memory/time and large offload penalties. SANA/Sprint and Lens report specific optimized1024 speeds; FLUX3 reports B200 peak memory under multiple precisions. SD3 reports component batch32 metrics. These are preserved with hardware, precision, steps, resolution and missing conditions rather than pooled into a misleading ranking. Most do not measure this frozen img2img path.

Parameter-memory lower bounds are not peak memory, disk bytes are not VRAM, activeMoE parameters are not resident weights, and a fast transformer forward is not whole-pipeline generation. No GPU timings were taken. Absence of a matched primary1024 measurement remains explicit, not replaced with a fabricated estimate.

Native `image` input can mean reference conditioning or instruction editing. It is not equivalent to forward-noising the source and truncating a denoising schedule. Current source confirms this difference for FLUX2 Klein, Qwen2.1, Kandinsky5, OmniGen, StableCascade and HiDream-O1. Different scheduler strength numbers also do not imply matched noise/SNR. Sprint tiny step counts can produce empty or coarse strength schedules.

## Recommendations and fixed constraints

Keep the frozen core and fixed primary R1 SDXL .2 decision rule, n60, .75n/.5n/.05n thresholds, four marked arms plus C0,7500 outputs,15h/USD15 cap. R2FLUX1 remains excluded by actual gate. No proposal is inserted automatically.

P4 MoVQ is the strongest optional additional encoder training-lineage contrast. AE-only300-output diagnostic is cheaper than full2700-output regeneration but answers a narrower compression question. DC-AE and Wan AE-only add architectural/training diversity in a larger diagnostic panel.

P7 now distinguishes a high-resolution pixel-method lead (HiDream-O1), a direct1024-interface lead (PRX) and a small256 mechanism control (DDPM). None is yet a frozen strength-controlled regenerator. O1's exact file sizes, optional gated reasoner, source-noise initialization, resolution snapping and dependency version differences are documented in its card.

Do not recommend a separate P10 FLUX2 Klein experiment for this encoder-transfer question: weaker initialization evidence thanMoVQ, no native strength API and unmeasured target throughput outweigh its ungated Apache availability. A future instruction-editing study would be a separate proposal.

`proposal-comparison-1b.md` provides selected-file arithmetic and costed scenarios. Core20.206GB plus O1 files35.219643552GB gives55.425643552GB before additions: below future80GB absolute cap, but requiring reconsideration of the40GB asset/retry reservation. A full extra regenerator is2700 outputs, not2160, becauseC0 must be included. No server, model weight, installer, inference, mark scoring, paid API or held-out pixels were used.

## Coverage statement

Qualifying families: LDM/SD1–2, SDXL, SD3/3.5, Kandinsky, SANA/DC-AE/Sprint, PixArtα/Σ, Playground, Hunyuan-DiT, Qwen, Z-Image, Lumina, HiDream, OmniGen, Würstchen/StableCascade, pixelDDPM, Lens, PixelGen and PixSGR. Variants/encoders are grouped conservatively even where a successor architecture changes. FLUX/IF native primary evidence and AuraFlow/Chroma/PRX leads are separately labelled; not needed to reach the floor.

Search log has19 actual events across four attempted categories, three successful categories and at least16 distinct successful intents after collapsing the corrected Lens-owner query. Eleven web queries were re-executed only to preserve raw receipts; repetition does not inflate breadth. Full-text primary evidence, not abstracts, supports qualifying cards.

## what we might still have missed

The sweep is not exhaustive. PixARG2610.14713, PixelDiT, HiDiT, Edify, TC-AE, LongCat, Kandinsky6 and other newer generators remain leads rather than evaluated cards here. HunyuanImage3 encoder initialization, FLUX/SD3 scratch lineage, Qwen2.1 checkpoint-to-paper mapping, current Lens release access, and some dependency license details remain unresolved. A newer model may use a genuinely distinct encoder, but neither its name nor latent shape would establish that.

No source establishes watermark survival for this experiment, nor native GPU compatibility, detector behavior or target-device runtime. Paper rankings often use different prompts, private curation, rewriting, CFG and metric implementations. The recommendation may change after a separately authorized timing/design decision; it does not change from unobserved outcomes.

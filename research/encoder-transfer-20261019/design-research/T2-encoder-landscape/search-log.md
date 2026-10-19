# T2 search and inspection log

Date: 2026-10-19. Researcher: Codex T2 agent. Scope: independent image encoder ancestry, native regeneration support, access/license and budget feasibility. The requested deliverable is Markdown and supporting cards; no shared literature ledger or existing bibliography was edited.

1. Read authoritative MAIN STATE and current BRIEF; reused existing Q-VAE dossier. Did not inspect source images, held-out pools or new outcomes.
2. Primary-source searches covered SDXL from-scratch VAE; SD3 autoencoder latent dimensions; FLUX1/2/3 VAE configs, licenses and access; Kandinsky MoVQ training and official img2img; DC-AE/SANA/Sprint methods and deployment; PixArt, Playground and Hunyuan VAE reuse; Qwen/Wan encoder training; newer Z-Image, Lumina, Chroma, AuraFlow and HunyuanImage releases; pixel-space DDPM, IF, Chroma Radiance and PRX Pixel.
3. Opened papers through arXiv HTML. Method and evaluation locators for each V2 item are recorded in cards. Abstract-only or partially screened new papers are not V2. Existing Q-VAE was reused rather than silently reclassified as newly inspected evidence.
4. Queried official Hugging Face API with `blobs=true` to obtain repository revisions, gate flags, filenames, LFS sizes and SHA-256. Read available pinned config JSON, README and licenses. These were metadata/text requests only; no weight or model executable was acquired. Code sources were read as plain cached text for API inspection, not installed or run.
5. Read official diffusers documentation and repository tree. Inspected exact v0.36.0 Kandinsky2.2, Kandinsky3, SanaSprint, Flux img2img implementations and VQModel. Identified floor-vs-ceil truncation, native scheduler, quantization bypass, and image preprocessing. Current main-tree snapshot: e04f0c5f24392fcd34b32d18d0ce03668f9bcd50. Stable v0.36.0 APIs are distinguished from newer main-only integrations.
6. Compared metadata hashes where identical released VAE files establish reuse. Did not claim unequal hashes prove different encoders. SD3/FLUX initialization remains unknown where explicit evidence was absent.
7. Initial FLUX3 uppercase guessed ID failed; corrected official lower-case ID was resolved successfully. Only the corrected API gate flag supports its gating classification. Some guessed LICENSE paths returned404; these failures do not imply absent licensing. Anonymous FLUX/SD3 pinned config requests401 are preserved. Browser access to Gemma terms succeeded while cache-client access failed; exact terms text is not represented as a locally verified paper.
8. Derived planning-only timings and cost arithmetic; no rental price or GPU measurement was fabricated. Corrected initial rough KD3 download estimate using all five text-encoder shards:28.390829958GB, not14.2GB. No download or execution proposal was enacted.

## Artifacts and verification

- `synthesis.md`: self-contained decision, comprehensive requested-family map, optional native API and costed panels.
- `model-metadata.json`:30 official model metadata records, including failed config-access fields where applicable.
- `download-plan.json`: exact selected SDXL/KD3/KD2.2 filenames, pinned revisions, sizes and published hashes. Config/tokenizer/index companion lists are metadata, not downloaded assets.
- `source-cache-manifest.json`: original URLs, successful cached paths, bytes, SHA-256 and access failures. Cache resides only in MAIN `.thesis-build/q1-research-20261018/cache/`, with unique T2 prefixes, outside git.
- `cards/*.json`, `literature-matrix.csv`, `evidence-ledger.jsonl`, `references.bib`: bounded local literature records. Unextracted authors and DOI remain null/missing instead of invented. The BibTeX is an inspection index, not publication-ready author metadata.

The literature skill's standard validator command was attempted, but `scripts/validate_literature.py` does not exist in this checkout. The requested bespoke topic structure was retained; no claim of schema-validator success is made. Local JSON/CSV parsing and cached-file checksum verification were used. This is a documentary deliverable, not a tested runtime environment.

## Remaining uncertainty

No exhaustive absence claim: newer releases, private models and all fine-tunes are outside this bounded search. Full from-scratch initialization remains unresolved for FLUX and SD3. New reference-image editing APIs do not establish classic regeneration equivalence. Runtime1024 memory, actual rental price, host-RAM peak and complete baseline download total must be verified at the authorized execution stage before admitting an optional arm. None of these open items changes the fixed SDXL .2 decision rule.

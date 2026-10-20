# T5 Stage1b: pinned pipeline fidelity audit

The six required implementations have been inspected at actual frozen source versions. The61-setting matrix links exact official files and line ranges; six independent paper V2 cards record methods **and** evaluation rereads. No core scientific-definition bug was established by this static audit. Documentary completeness does not imply package, checkpoint, CUDA or model runtime validation.

## Findings that matter

1. **R0/R1 strength semantics:** frozen DDIM20 leading/offset1 retains2/4/8 updates at.1/.2/.4, beginning51/151/351. `schedule-and-tail-arithmetic.json` gives the whole schedule. Equal indices do not equate severity across encoders. R0/R1 sample posterior; D1 uses unscaled posterior mode.
2. **SDXL precision is a deliberate policy:** native diffusers0.35.1 upcast partly returns decoder blocks to fp16; the existing local override correctly retains the entire official VAE in fp32. This preserves fp16 checkpoint values promoted to fp32, not a replacement fp32 file. Native R1 preprocess casts image values to pipeline fp16 before float32 VAE encoding, whereas D1 preprocesses directly to fp32; describe D1 as a reconstruction control, not an exact subtraction of R1's encoder arithmetic.
3. **Spatial arithmetic is method-specific:** WAM tensor bilinear resizing uses torchvision0.22.1 antialias=True and image output floor(255x+.5); VINE uses PIL bicubic256 plus tensor bicubic residual scaling and ToPIL uint8 truncation; diffusers rounds to nearest/ties-even. Rinse uses the saved512 PNG between attacks. Harmonizing these details would silently change the released methods.
4. **Native detectors differ:** WAM mask sigmoid>.5/fraction>.07 is a transferred published presence rule; message aggregation thresholds mean raw logits>.5. Empty masks abstain. VINE has a100bit decoder with np.round and no universal fixed presence cutoff. Common27/32 and69/100 are random-message tail rules, never image-FPR bounds.
5. **VINE RNG:** posterior.mode is deterministic, but its one-step DDPM999→−1 still draws a tiny global Gaussian term because variance clamps at1e−20. Existing per-mark global seed42 covers it. Do not silently replace the native step to remove that draw. Released dependency SD-Turbo differs from paper SDXL-Turbo prose.
6. **Optional Kandinsky3:** actual img2img encodes continuous4-channel MoVQ latents then bypasses the helper's stale `.latent_dist.sample` branch; decode uses `force_not_quantize=True` and no latent scaling. DDPM cosine/noisy reverse semantics differ from R1. Source precision and runtime memory remain unmeasured proposal choices.
7. **Optional TrustMark-Q:** Python decoder245, encoder256; default BCH_5 neural100bits contain61payload+35parity+4header. Native logits>0 feed ECC; valid ECC and exact expected-payload equality are separate. Raw mode's unconditional detected=True is not presence. Official CDN Q YAML matches pinned MD5; no weights retrieved. Do not use JS256, P224, arbitrary100bit-binomial calibration or an unofficial mirror.

## Classification: fixes, amendments and missing evidence

| Class | Finding | Required action |
|---|---|---|
| Required core bug fix established | None from this documentary audit | No shared code edit made; parent retains responsibility for final integration and runtime smoke |
| Textual clarification | R1 input half-rounding versus D1, VINE tiny global RNG, WAM release calibration transfer, TrustMark245/ECC, KD3 bypass | Carry these limits into consolidated protocol/report |
| Version compatibility | Safe-load/native imports, VINE offline nested paths, full-fp32 VAE guards, selected CUDA backend | Authorized Stage2 synthetic smoke before real development-image execution; retain errors explicitly |
| Pre-outcome amendment if adopted | P1 TrustMark, P4 KD3, offload, tiling, precision, scheduling, replacement AE files | Freeze change and why before outcomes; this audit does not adopt them |
| Missing evidence | Actual checkpoint source tensor precision where metadata lacks it; server VRAM/elapsed time; effective SDPA kernel; TrustMark newly downloaded bytes | Collect during authorized setup, not invented from paper/model-size numbers |

Consequential checks only: Stage2 should verify2/4/8 scheduler tails, SDXL full-fp32 encode/decode guards after R1/D1 switching, native WAM raw-logit aggregation/empty-mask handling, and distinct PNG rounding. Optional P1 would need exact61payload/schema/245resize assertions; optional P4 would need the continuous-latent bypass. Existing CPU tests are not rerun or relabelled as CUDA/model validation here.

## Search coverage and audit boundaries

Sixteen distinct substantive queries cover general web discovery (8), OpenAlex scholarly search (4), and official Hub search (4). Direct file retrievals do not count toward breadth. Search results include noisy leads and newer alternatives; only inspected primary methods/evaluation and exact pinned code support claims. Raw API/tool responses, failed retrieval events and SHA manifests are retained. No packages/models were executed and no marks, real images or held-out pixels were inspected.

## what we might still have missed

- A compatible exact-release checkpoint may contain metadata unsupported by the frozen safe loader; text source inspection cannot establish actual deserialization success.
- Effective CUDA/SDPA kernel selection, full-fp32-VAE peak memory and runtime depend on the rented hardware. Documentary compatibility is not a measured smoke result.
- Public CDN weight URLs can change; historical WAM SHA and TrustMark expected MD5 must be checked after authorized downloads, with SHA256 recorded. TrustMark's native downloader does not itself validate new bytes after transfer.
- Official release/model-card metadata and paper training descriptions can be inconsistent (VINE is a concrete case); unreported training-data overlap remains possible despite independent AE training.
- Hub fuzzy searches missed the author VINE handle and returned unofficial TrustMark mirrors; direct author-source resolution corrected these leads. New papers found via OpenAlex were discovery leads, not silently cited as evaluated evidence.
- T5 is a fidelity audit, not an exhaustive alternative-method ranking. T1/T2/T3 own attack/encoder/baseline breadth, and this package adds no unapproved external baseline.

Stop boundary remains the Stage1b documentary review. No server start, paid compute, model download, image scoring or held-out run follows from this audit.

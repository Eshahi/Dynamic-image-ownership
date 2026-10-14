# Independent research: enhancing the registry direction (Claude, 2026-10-14)

The user asked for a separate, independent check of whether the registry-based verification direction (`thesis-runs/d916749c/NEXT-GOAL-20261014.md`) can be improved, and for new ideas. This memo is exploratory development evidence. There was no held-out data, no generation and no GPU use; it is not a milestone result.

## Summary

1. **The proposal's "dynamic ownership" is the strongest argument for the registry.** The title and problem statement promise ownership transfer (`inputs/proposal-text.md` lines 77, 171 and 177). It is recorded as unresolved scope conflict U-01 (`research/scope.md`), and nothing built so far implements it.
   - A registry of owner-signed, append-only records makes transfer a new signed event: the pixels never change and nothing is re-marked.
   - This is a scope decision for the user and supervisor. `research/scope-guard.md` line 17 still excludes registry and ledger infrastructure.
2. **The theoretical ground is already published.**
   - Fairoze et al. (Google DeepMind, 2025) prove that a robust, unforgeable, publicly detectable watermark needs capacity at least signature plus embedding length. They call this out of reach today: signatures need 384 bits or more, and TrustMark reaches at most about 200 bits.
   - Their own way out is "deferred storage": the watermark carries a database reference.
   - C2PA's soft-binding API does the same in practice: a watermark or fingerprint is used to look up a manifest.
   - Our measured walls match this theory: about 32 robust bits, and the r3-256 test failed.
3. **E3's own fine-detail features are an excellent registry descriptor** on the development panel when compared continuously instead of being hashed.
   - The lowest similarity of a regenerated copy is .54 at strength .2 and .32 at .4. The highest similarity of any impostor or synthetic look-alike is .057.
   - DINOv2, CLIP and pixel thumbnails separate real impostors but cannot separate the look-alike pairs (similarity .99).
4. **There is a risk to address head-on:** the same descriptor finds regenerated copies even without a watermark.
   - Unmarked regenerated copies score as high as marked ones.
   - A reviewer will ask what the watermark adds over a fingerprint database such as DinoHash. The thesis needs a fingerprint-only ablation and the scenario where the watermark matters (idea 3).
5. **New ideas, ranked:**
   1. signed append-only records for dynamic ownership;
   2. the fine-feature descriptor as the primary registry key;
   3. a fingerprint-only arm plus a registry-squatting scenario;
   4. a random record-ID pointer instead of a content-derived q;
   5. a zero-bit owner-presence fallback with catalog search;
   6. orbit enrollment;
   7. privacy through fuzzy commitment;
   8. a small trained metric head, only if the fine features fail off-distribution.

## What the literature says

| Source | Relevance |
|---|---|
| [Fairoze et al., "On the Difficulty of Constructing a Robust and Publicly-Detectable Watermark", arXiv 2502.04901](https://arxiv.org/html/2502.04901v1) | **Construction:** watermark = Encode(x, Sign(sk, e) ‖ e) with e = robust embedding; detection verifies the signature and compares e with the image's recomputed embedding. **Limits:** capacity c ≥ δ + n is unreachable with current watermarks (signatures of 384-3072 bits; TrustMark at most about 200 bits before BER grows). **Deferred storage:** the watermark stores a database reference; "if the database is offline, detection is impossible," at no security cost, since the adversary can still destroy but not forge. **Descriptors:** DINOv2 copy-detection AUC .990 clean; white-box ℓ∞ attacks break descriptors (SSCD .057 at 4/255), which is adaptive-adversary territory (T7, out of our scope). |
| [C2PA Soft Binding API](https://spec.c2pa.org/specifications/specifications/2.3/softbinding/Decoupled.html), [TrustMark C2PA docs](https://opensource.contentauthenticity.org/docs/trustmark/c2pa/) | **Industry practice:** the watermark ID is a lookup key into a manifest repository, and a fingerprint is a second lookup route. The watermark is not robust to diffusion regeneration (TrustMark: 0.00 detection under regeneration in SpreadMark's table). |
| [Singhi et al., DinoHash and MP-FHE provenance, arXiv 2503.11195](https://arxiv.org/abs/2503.11195) | **Fingerprint-only alternative:** a DINOv2-based perceptual hash with an encrypted registry, presented as an alternative to watermarking. The abstract does not report diffusion regeneration. This is exactly the baseline a reviewer will raise. |
| [Wang et al., Image Copy Detection for Diffusion Models (ICDiff), NeurIPS 2024, arXiv 2409.19952](https://arxiv.org/abs/2409.19952) | **Diffusion replicas:** existing copy-detection descriptors miss them; PDF-Embedding is trained on 40k human-graded SD1.5 replica pairs. A ready reference if a trained descriptor becomes necessary (idea 8). |
| [SpreadMark, arXiv 2608.03165](https://arxiv.org/html/2608.03165) | **Regeneration robustness:** a spread-spectrum learned watermark; under SD1.4 img2img at .25 it reaches BA .78 / DA .77 on COCO at 128 px, versus TrustMark and WAM at DA 0.00. Its PSNR is about 30 dB and regeneration robustness falls sharply at higher resolution. This supports keeping our optimization-based carriers rather than switching to a learned one. |
| [Iida and Kiya, fuzzy commitment for privacy-preserving image identification](https://www.jstage.jst.go.jp/article/mta/5/2/5_67/_article/-char/en) | **Privacy:** a fuzzy commitment over sign features protects stored descriptors (idea 7). |
| Recent removal papers: [2511.10933](https://arxiv.org/html/2511.10933), [2511.05598](https://arxiv.org/abs/2511.05598), [2603.04696](https://arxiv.org/pdf/2603.04696) | **Removal:** regeneration removes pixel watermarks in general, including VINE under stronger regeneration. A design that also identifies the image through a registry degrades gracefully when the mark is lost. |

## Screen results (CPU only, existing development images)

- **Run:** MAIN `.thesis-build/dev-runs/20261014-2258-claude-registry-descriptor-screen-r2/run.json`.
- **Code:** `scripts/claude_registry_descriptor_screen.py`, commit `422c73a`; 125 s on CPU. (The first run, `20261014-2256-claude-registry-descriptor-screen` at `be4fd2c`, gives the same numbers without the content control.)
- **Positives (6 sources):** E3 marks under SD1.5/SDXL VAE reconstruction and SD1.5 DDIM regeneration at .1, .2 and .4, seeds 9-11. The sources are 30, 72, 73, 89, 127 and 165, from runs H1 and WAM-common.
- **Negatives:**
  - 24 × 23 clean marked and canonical impostor pairs;
  - 1,932 regenerated-impostor pairs;
  - the six synthetic texture-sibling pairs from the descriptor round.

| Descriptor | Highest negative (impostors / siblings) | Lowest positive at .2 | Lowest positive at .4 | Accepted with zero observed false accepts |
|---|---|---|---|---|
| D1: E3 native fine features, uncompressed cosine | .057 / .052 | .543 | .323 | **all positives (VAE 12/12, .1 18/18, .2 36/36, .4 18/18)** |
| D2: DINOv2-small CLS | .444 / **.991** | .720 | .538 | 0 (siblings); without siblings, all |
| D2b: DINOv2 mean patch | .575 / **.992** | .866 | .709 | 1 (siblings); without siblings, all |
| D3: CLIP ViT-B/32 | .715 / **.998** | .897 | .819 | 0 (siblings); without siblings, all |
| D0: 32 × 32 gray pixels | .667 / **.996** | .936 | .820 | VAE and some .1 only (siblings) |

**Content control.** D1 similarity between an unmarked canonical image and its own unmarked regeneration is median .732 at .2 and .528 at .4. Marked copies score .685 and .468. The similarity is carried by content, not by the watermark, and marking lowers it slightly. This makes a fingerprint-only registry a real competitor (idea 3).

**Orbit enrollment** (record = clean + VAE + .2 regenerations with the other two seeds; leave one seed out):
- the margin between the lowest positive and the highest real negative grows for every descriptor: D1 .279 → .298, DINO CLS .094 → .121, CLIP .116 → .161, DINO patch .133 → .189;
- on this panel, D1 does not need it.

**1:N scale.** No real impostor reached the 95%-TPR threshold for any descriptor (0/3,036). The Gaussian tail extrapolation is not reliable this far out and is reported only as "negligible for unrelated photos". The open risk is near-duplicates, not random images.

**Limits:**
- six positive sources, all with E3 marks;
- one regenerator family (SD1.5), with the unseen regenerators still to come from the Codex brief, step 1b;
- synthetic siblings instead of real near-duplicate photos;
- consulted images, so selection on them is a hypothesis, not a result.

## Ideas, ranked by value and cost

### 1. Signed append-only records, which make "dynamic ownership" real (design work and a small implementation; needs a scope decision)

**Record:**
- r = (record ID, owner public key, D1 descriptor quantized to 8 bits (Fairoze et al. report little loss from 8-bit quantization), q, time, previous-record hash);
- signed by the owner;
- stored in an append-only log (a transparency-log pattern).

**Operations:**
- **Transfer:** the current owner signs a transfer event to the new owner's key.
- **Revocation and licensing:** further signed events.
- **Verification:** decode the pointer, fetch the chain, verify the signatures, then compare D1.

**Why it matters for the thesis:**
- It answers SCOPE-03/U-01 and the title with no new watermark capacity, because the image never changes after enrollment.
- Re-embedding at each transfer, the earlier idea in `research/scope-execution-decision.md`, would stack marks and is unnecessary.

**Security for T4/T5:** forging still requires a descriptor collision with the enrolled record, so it reduces to idea 2's measurements.

**Costs:** it relies on registry availability, and white-box descriptor attacks are excluded (T7).

### 2. Use D1 (uncompressed fine features) as the primary registry key (no new cost)

It already exists in the codebase (`journal_fine_gaussian_instance.descriptor()['vector']`). On this panel it is the only tested descriptor that rejects the texture siblings. Keep DINOv2 as a secondary key; it is stronger semantically and needed if real near-duplicates differ in structure rather than texture.

### 3. Add a fingerprint-only arm and a registry-squatting scenario (cheap; essential for credibility)

The control above shows D1 finds regenerated copies without any mark. The thesis must show where the watermark adds value. Candidate cases:
- **Squatting:** an attacker regenerates the owner's image and enrolls the copy as their own, possibly in another registry. A fingerprint-only system sees two matching records; only timestamps decide, and only if both sit in one registry. With a regeneration-robust pointer, the attacker's copy still points to the original owner's record (E3 reads the exact pointer on about 95% of images at .2 in M2).
- **Owner signal without registry search,** and public presence evidence.
- **Scoping among near-duplicates of different owners.**

Measure the fingerprint-only system (1:N search over all records) against pointer plus registry, on the same positives and negatives, including the squatting case.

### 4. A random record-ID pointer instead of a content-derived q (needs re-embedding; later)

With a registry, the payload no longer has to bind content; the record check does that. Today's q is a CLIP-derived code, and q drift was F5's main failure mode. A random ID protected by BCH has no drift and no collisions between an owner's similar images. E3 already reads blindly at about 95-99%. Test it as a variant once step 2 passes.

### 5. Zero-bit fallback: owner presence plus catalog search (cheap once stronger-strength images exist)

At heavier regeneration the code is often unreadable while presence still registers. In the F5 r2 stress grid at .5, 17 of 36 successes were recomputed-only. If owner O is detected but q is unreadable, search O's catalog with D1 (1:N_O). The false-accept rate becomes P(false presence) × P(D1 false match within N_O). This extends the usable strength range without a new carrier.

### 6. Orbit enrollment (cheap; secondary)

At enrollment the owner stores descriptors of a few self-made regenerations. It gives a small, consistent gain in margin. It is most useful for generic descriptors and unseen regenerators; test it cross-model, with an SD1.5 orbit tested against SD2.1 attacks.

### 7. Privacy through fuzzy commitment or a secure sketch of D1 (optional)

Store a commitment instead of the raw descriptor, comparing in a sign-quantized space with BCH, as Iida and Kiya do. This trades some margin for not exposing the content descriptor.

### 8. A trained metric head (only if D1 fails on unseen regenerators or real near-duplicates)

This is the natural place for "training" in a neural-watermarking thesis:
- a small projection on frozen DINOv2 and fine features;
- contrastive positives from multi-model regenerations of free COCO train images;
- hard negatives from same-category images;
- ICDiff's PDF-Embedding as the reference.

## Recommended changes to the Codex brief (if the user agrees)

1. Make D1 the sole primary descriptor and DINOv2 secondary. Today both are co-primary; this screen gives a reason to rank them.
2. Add a fingerprint-only arm and the squatting scenario to step 2a/2b (idea 3).
3. Add real near-duplicate negatives to 2b: burst photos or a public near-duplicate set with a recorded licence, chosen by a fixed rule.
4. Clarify that the user's step-2 decision overrides `research/scope-guard.md` line 17 for the verification registry only; ownership transfer stays U-01.
5. Add a step 3, conditional on the scope decision: signed append-only records and a transfer demo (idea 1).

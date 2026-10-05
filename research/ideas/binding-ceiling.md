# Binding ceiling: the 32-bit sketch, not CLIP drift, limits F5 binding at .4/.5

2026-10-05, Claude Code (Opus 5.5, supervisor session). Development data only: the F5 r2 stress baseline `20261005-1200-f5-stress-baseline-f5r2` (12 development sources, .4/.5/.6 x 5 seeds, 20 steps, CFG 1). CPU only. Script `scripts/f5_binding_ceiling.py`, raw output `research/ideas/binding-ceiling-baseline.json`.

## Question

Every lens of the ideas fan-out agreed that binding (CLIP code drift) is the bottleneck at .4/.5, and the top four ranked fixes (A-P2 UEP, A-P3 list+CRC, C-1 BCH sketch, C-2 soft LDPC) all act on the existing 32-bit code q. Before spending GPU time on them, how much could any binding fix gain at all, and where is the loss?

## Method

- Seven-view CLIP vectors (the production `semantic_feature`, ViT-B/32) for the 12 covers and the 173 completed C1 T3 images. The code q recomputed from each cover matches the code in the embed report for all 12 sources.
- **Intra pairs:** regenerated image vs its own cover. **Inter pairs:** cover i's code vs cover j's vector, 132 ordered pairs of distinct covers (the same pairs as H4 and T5).
- Each estimator is scored at **matched false-match rate on inter pairs**: the threshold admits exactly k of 132 inter pairs (k = 0, and k = 4, the current F5 r2 clean level from H4). Rows lost to the carrier (owner not found) stay failures.
- Estimators:
  - true angle between the 512-d vectors (infinite code, no carrier error);
  - the keyed 32-bit code with the true q (no carrier error), soft ML angle as in rev 2;
  - random Rademacher codes of L = 32/64/128/256 bits with the same soft ML estimator, 5 draws each.

## Results

Status of the 173 rows under the production detector: .4 ok 49 / bind 6 / carrier 3; .5 ok 37 / bind 14 / carrier 7; .6 ok 10 / bind 9 / carrier 38.

**Angles (degrees).**

| | median | max |
|---|---:|---:|
| intra .4 | 22 | 40 |
| intra .5 | 29 | 50 |
| intra .6 | 44 | 61 |
| inter (distinct covers) | 59 | |

The inter minimum is 32.7 (one pair; p5 45.6). The binding failures at .4 sit at 24-32 degrees, well inside the inter distribution's lower edge.

**Matched false-match rate k = 4/132.** C1 success out of 58/58/57:

| estimator | .4 | .5 | .6 |
|---|---:|---:|---:|
| true angle (ideal ceiling) | 55 | 44 | 14 |
| keyed 32-bit, true q | 51 | 30 | 6 |
| random 32-bit (5 draws) | 33-50 | 17-33 | 0-7 |
| random 64-bit | 47-54 | 29-45 | 5-11 |
| random 128-bit | 48-54 | 30-44 | 8-13 |
| random 256-bit | 54-55 | 44-48 | 12-15 |
| production F5 r2 (own threshold 6, decoded q) | 49 | 37 | 10 |

**AUC at .5** (intra non-carrier vs inter):

| code | AUC |
|---|---:|
| 32-bit random | 0.90-0.95 |
| keyed 32-bit | 0.91 |
| 64-bit | 0.93-0.98 |
| 128-bit | 0.95-0.97 |
| 256-bit | 0.98 |
| true angle | 0.985 |

## Reading

1. **The ideal binding ceiling is .4 55/58, .5 44/58, .6 14/57** at the current false-match level. No binding change of any kind can beat that with this feature (7-view CLIP ViT-B/32). Against production, the room is about +6 at .4, +7 at .5 and +4 at .6. On .4+.5 that means at most about 99/116 against 86/116 today.
2. **Most of the loss to that ceiling is the 32-bit sketch itself.**
   - A 32-sign random projection estimates the angle with about 2 bits of standard deviation, so intra and inter overlap. At 256 bits the estimator reaches the true-angle ceiling (AUC .98 vs .985).
   - It is not mainly CLIP drift: the ideal feature separates the pairs well at .4/.5.
   - It is not mainly carrier bit errors: production with decoded bits already scores like the true-q keyed code.
3. **The 32-bit result depends on the projection draw.** Five random 32-bit draws span 33-50 at .4 and 17-33 at .5, and the keyed draw F5 uses is on the lucky side. A short code makes the binding rate a property of the key draw as much as of the method. A long code removes that variance.
4. **ECC on the existing 32 bits cannot exceed the 32-bit ceiling.** This covers UEP, list+CRC, BCH syndrome and soft LDPC as proposed. A secure sketch or list decoder is a thresholding of the same distance between the same 32 bits and the suspect. It adds no information about the cover's CLIP direction, so it can only recover carrier-side bit errors, which item 2 shows are not the main loss. The Phase 0 shootout (`scripts/f5_phase0_shootout.py`) would at best show this, so running it is low priority.
5. **The right lever is a longer semantic sketch: 128-256 bits.**
   - This is the GPU lead's codec r3 direction (`research/f5-codec-r3-selection.md` on `claude/f5-gpu`).
   - The coding ideas become useful there, as the means to carry it:
     - A-P1 concatenated code, so the long sketch survives the carrier;
     - C-1/C-2 syndrome coding of a long sketch: Slepian-Wolf with the suspect's own projections as side information, so only part of the L bits must ride the carrier.
6. **The r3 kill prediction in `f5-codec-r3-selection.md` assumes a coupled design.** It predicts many more carrier failures at 64 bits because the decoded threshold grows with the 2^L code search (8.26 to 10.59). That holds only while owner detection is coupled to the code.
   - The recomputed path, which builds the pattern from the suspect's own q' and uses one hypothesis at threshold 4.98, should not scale with L at a fixed chip count. Checked in `v5._key_test`: the recomputed score sums the segments where the suspect bit agrees (the other pattern scores about 0), so its expectation is (1 - θ/π) times the full score for any L at a fixed chip count.
   - Alternatively, a code-independent owner pilot decouples detection from the code. A long code then costs per-bit carrier error rate, not detection threshold.
   - The r3 pilot should therefore test the decoupled form, not only the 64x5 / 128x5 drop-ins.

## Caveats

- 12 development sources. The inter set is 66 unordered pairs (132 ordered), so the false-match rate is coarse: one pair moves k by 1-2.
- The simulated codes assume the code reaches the detector without carrier error. Real long codes have fewer chips per bit and a higher bit error rate at .5. The capacity estimate from lens A (about 100 bits at .5) suggests 64-128 effective bits, which is where most of the gain already is (128-bit: .5 30-44).
- Production numbers use the production threshold and decoded q with error-rate mixing, so they are not on exactly the same false-match scale as the simulated rows. The ceiling comparison is the robust part.
- .6 is carrier-limited (38/57 carrier losses); no binding change addresses that.

## Implication for the ranking in `research/f5-ideas-ranked.md`

- Demote A-P2, A-P3, C-1 and C-2 as fixes on the 32-bit code.
- Promote "long semantic sketch (128-256 bits), decoupled from owner detection, carried with A-P1 coding or syndrome (C-1/C-2) with the suspect as side information" to rank 1 for .4/.5.
- Expected gain up to the ceiling: about +6 at .4 and +7 at .5.
- The decisive cheap test, with no GPU, is to read the carrier's soft per-bit values on the existing stress latents and measure the bit error rate L bits would see at 5 or 2.5 chips per bit. That gives the effective information that reaches the detector.

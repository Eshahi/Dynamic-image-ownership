# G2-B: bounded diagnosis of the two transfer accepts

JUDGMENT: **Keep B promotion at KILL.** The two retained accepts satisfy the fixed G2-B kill condition and come from one donor-recipient pair at two scales. The saved records support a decoded-word instance-binding failure for this pair. They do not establish a unique physical mechanism or justify a rescue. This is a diagnostic note, not a WP6 review or a new ruling. Locators below are relative to `research/f5-components-20261101/` unless prefixed `scripts/`, which is relative to the repository root.

SOURCE: Gate 2 R5, “G2-B,” kills promotion on any B accept rejected by C at PSNR > 35 dB and SSIM > .9. The frozen rule is B = Bs OR (Bi AND NOT veto); each B tier requires the **decoded** score at the computed ball threshold and corrected decoded-word distance <= 6. Veto is frozen semantic `read AND NOT content_match`. See `gates/GATE-2-RULING.md`, R5/G2-A and G2-B; `analysis/gate2_reader.py:13-16,22-40`. The saved exact threshold is 7.779133080172838 (`results/g2-a/summary.json:3`), displayed as 7.7791 in the ruling.

## What the records establish

MEASURED: `results/g2-b-transfer/summary.json`, `counts` and `kill_events`, records 480/480 successful, strict-quality cases: C 0, O 14, O_U 8, Bs 0, Bi 2 and B 2. Both B events are donor 544 (DESIGN) to recipient 1359 (EVALUATE). Their complete raw records are `results/g2-b-transfer/batch-0448-08.jsonl:7-8`, IDs `g2b-544-1359-0.5` and `g2b-544-1359-1.0`.

MEASURED: Every numerical entry in this table is retained in those two JSONL rows, under `raw`, `endpoints` or `quality`.

| Field | Scale .5, row 7 | Scale 1.0, row 8 |
|---|---:|---:|
| Semantic decoded score | 3.677971718 | 3.838595829 |
| Semantic decoded word | `bdd7544f` | `bdd7544f` |
| Suspect semantic code q | `fbc6b624` | `bbc6b624` |
| B semantic Hamming / corrected distance | 14 / 0.0 | 13 / 0.0 |
| Frozen semantic read / content match | false / false | false / false |
| Instance decoded score | 7.811984902 | 8.894064897 |
| Instance decoded word | `f4f3364f` | `f4d3340f` |
| Suspect perceptual hash h | `d4e8b48f` | `d4e8b48f` |
| B instance Hamming distance | 9 | 8 |
| B instance corrected distance | 5.593171325 | 5.653505340 |
| Legacy instance candidate / read | recomputed / false | decoded / true |
| Legacy instance recomputed score | 5.525792758 | 6.648262495 |
| C / Bs / Bi / veto / B | false / false / true / false / true | false / false / true / false / true |
| PSNR, dB | 47.831396692 | 42.346682644 |
| SSIM | 0.989417504 | 0.963925469 |
| LPIPS | 0.013517014 | 0.071865894 |

DERIVED: The semantic tiers fail their score requirement despite their clipped corrected distance of zero; zero there is not evidence of semantic agreement. The instance scores exceed B's threshold by 0.032851821 and 1.114931817. Both corrected distances are below 6, and neither semantic read activates the veto. Consequently both records satisfy `Bi AND NOT veto`, with C false. This follows directly from the recorded values and `analysis/gate2_reader.py:22-40`; no reader or model was rerun.

DERIVED: From the retained unrounded corrected distance c and integer Hamming distance d, the correction formula implies e = (d-c)/(32-2c): 0.163682366 and 0.113395635. The equivalent raw-distance limits 6+20e are 9.273647315 and 8.267912696. Thus d=9 and d=8 pass intentionally. SOURCE: e is inferred by the score model in `scripts/revised_watermark_v5.py:1207-1229`, then used by `analysis/gate2_reader.py:22-26`. JUDGMENT: This correction is a model-based expectation adjustment, not observed error locations, an error-correcting decoder certificate, or proof that the donor and recipient represent the same content.

MEASURED: Donor 544 contributes 2/60 B accepts and recipient 1359 contributes 2/16 (`results/g2-b-transfer/by-donor.csv:23-25`, `by-recipient.csv:53-55`). DERIVED: The descriptive rate is 2/480 images, or one accepted pair among 240 tested donor-recipient pairs. The two scales reuse the same three input hashes (JSONL rows 7-8); the panel also reuses donors and recipients across pairs. These are not two independent discoveries or 480 independent trials. No zero-event upper bound applies. JUDGMENT: The PSNR/SSIM gate is satisfied; those metrics and the measured LPIPS do not supply a human invisibility judgment.

## Why this differs from N3

SOURCE: Gate 2 R2/N3 describes `t4-residual-177015-25394-0.5`: instance decoded score 8.2202 narrowly misses 8.2593, while recomputed score 5.3190 exceeds 4.9820. The decoded word is 12 bits from the recipient h, but the legacy recomputed route treats the candidate as its recomputed code. At scale 1.0 that old pair is rejected after the decoded word becomes readable. This note relies on the judge's retained diagnosis, not an independent rerun of N3.

SOURCE: The legacy fallback explicitly sets distance and corrected distance to zero for recomputed-only detection (`scripts/revised_watermark_v5.py:1232-1257`). B independently compares `decoded_code` with the suspect center (`analysis/gate2_reader.py:19-33,37`). MEASURED: Row 7 consequently contains legacy `code_distance=0` beside B `i_distance=9`. JUDGMENT: That difference is expected endpoint semantics, not evidence that B accidentally reused the recomputed route. B fixes the particular N3 route ambiguity, but these new words actually lie within its permitted corrected-distance region.

DERIVED: At scale 1.0 the instance score also exceeds the frozen 8.259326826136963 threshold and its corrected distance is 5.653505340. It would pass the ruling's frozen-style instance rule at the same h center; no lower B score threshold is needed for that event. At scale .5, the lower B threshold permits a decoded-word decision that the frozen decoded-score rule would not make. Both statements use JSONL rows 7-8 and the frozen-style rule in Gate 2 R5/G2-A. JUDGMENT: Attributing both failures solely to lowering the threshold is unsupported. Making the second tier an acceptance route exposes an existing approximate-binding weakness in this pair as well.

## What the code distances do, and do not, explain

MEASURED: G2-C stores C0 donor 544 q=`b567b438`, h=`f2523603`, and C0 recipient 1359 q=`dbc2b624`, h=`d4e8b48f` (`results/g2-c/codes.json:58-61,142-145`). Their q and h distances are both 13 (`results/g2-c/pairs.csv:757`, CROSS row). SOURCE: These are successful **unmarked clean-image** detection codes, not an embedded-code trace (`analysis/gate2_saved_tests.py:152-169`).

DERIVED: XOR/popcount of those codes and the two saved output records gives:

| Distance | Scale .5 | Scale 1.0 |
|---|---:|---:|
| Suspect q to C0 donor q | 11 | 10 |
| Suspect q to C0 recipient q | 2 | 3 |
| Decoded instance word to C0 donor h | 8 | 7 |
| Decoded instance word to recipient/suspect h | 9 | 8 |

DERIVED: Recipient h remains unchanged in both records. The decoded instance word is neither C0 donor h nor recipient h, and both C0 donor-recipient distances exceed 9. Thus a simple claim that the donor's exact C0 h already collided inside the recipient acceptance ball is false for this pair. These calculations use only the saved code strings; they do not infer an unobserved embedded word.

SOURCE: Instance patterns depend jointly on each segment's q bit **and** h bit, as `table[j][bq][bh]` (`scripts/revised_watermark_v5.py:352-380`). The F5 reader selects q-bound branches before decoding h; when semantic `found` is false, q_bound is q_now (`scripts/f5_latent_codec.py:294-304`). Both events have semantic `found=false`, so their instance words were decoded using the suspect q branches. `_key_test` maximizes the two h options segment by segment, against the actual projection vector (`scripts/revised_watermark_v5.py:1178-1199`).

DERIVED: For a fixed q branch, two h words at distance d share 32-d instance-pattern segments. That shortcut cannot be applied to donor versus recipient using h distance alone when their q branches differ. With the C0 codes as an explicitly limited proxy, q/h joint equality holds in only 14/32 segments for the clean donor-recipient pair, and in 15/32 and 16/32 for C0 donor versus the two suspects. These counts are `32-popcount((q_d XOR q_s) OR (h_d XOR h_s))`, derived from the same saved strings. They describe table-index equality, not observed signal energy or predicted score ratios.

SOURCE: The writer computes embedded h from the robust-marked image, and can refine/repeat the stages (`scripts/f5_latent_codec.py:227-250`); C0 h is not guaranteed to be that embedded h. The transferred object is the full saved C1-C0 pixel residual, clipped and rounded on the recipient (`analysis/gate2_transfer_panel.py:291-305`; `scripts/three_threat_protocol.py:87-94`). JUDGMENT: C0 q/h distances alone cannot distinguish partial donor-pattern carryover, changed q branch selection, recipient projection contributions, clipping/rounding, or a miscalibrated score-to-error correction. The aggregate raw scores do not expose per-segment projections or the writer's intermediate h. Joint table dependence makes a shared-segment explanation plausible; it does not identify its contribution here. No stage-causation or scale-causation claim follows from two dependent outcomes.

## Implementation and scope conclusion

JUDGMENT: No meaningful implementation discrepancy explaining away these two accepts was found in the inspected route, distance calculation, veto, threshold or transfer formula. The exact computed threshold versus its four-decimal display and the legacy six-decimal corrected-distance rounding cannot change either event. The apparent row-7 “recomputed” label belongs to the legacy endpoint; B's independently stored decoded-word decision is consistent with its source and the ruling. This is a bounded source/record comparison, not a pixel replay or an all-panel implementation audit.

SOURCE: Gate 2 R2 limits the conditional-q null argument to honest-null randomness under the PRF model and excludes adaptive public-key security. JUDGMENT: A recipient supplied with a residual containing same-owner watermark signal is not that honest null; these transfer accepts therefore do not by themselves falsify the conditional-null bound. They do falsify B's promotion requirement on this fixed development panel. The attack assumes paired donor C1/C0 access. Keep KILL, the frozen reader, all failed outcomes and the stated mechanism uncertainty. No threshold, radius, veto, pair or scale revision is proposed.

SOURCE: Work for this note consisted of reading the cited source and saved outputs, plus isolated stdlib arithmetic on saved code strings and endpoint values. No experiment, writer, reader or model call, new image inspection, held-out access, install, download or commit was performed.

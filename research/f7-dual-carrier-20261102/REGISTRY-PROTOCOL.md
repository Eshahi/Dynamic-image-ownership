# F7 as the registry pointer: frozen protocol

Claude, 2026-11-02, after the F7 screen ended in SCIENTIFIC_KILL ([RESULTS.md](RESULTS.md)). Claude recommended testing F7 as the pointer for the registry verification already confirmed on held-out data (`research/claude-registry-heldout-results-20261018.md` on `claude/registry-research`). The user's reply, verbatim: "Yes, run it".

This is a development test on the F7 screen's saved outputs: 16 Stage S development sources, no held-out data, no new marking or regeneration. It was written before any registry score of an F7 image was computed.

## 1. Question

The confirmed registry result holds on SD1.5 and SD2.1 only. F5's pointer reads 0/16 on SDXL .1 and Kandinsky 3 .2, so the registry cannot work there with F5. F7's pointer reads 13/16 and 15/16 there, but F7's in-mark content check let copies through (T4).

In the registry, the in-mark content check plays no part: the pointer selects the enrolled record, and the image is compared with that record. So the test asks: **with F7 as the pointer, does the frozen registry rule accept regenerated copies on SDXL .1 and Kandinsky 3 .2 while rejecting every copy-paste, false claim, wrong-source pair and unmarked image?**

The main unknown is whether the registry's fine-detail descriptor D1 survives SDXL and Kandinsky 3 regeneration. It has never been measured on those regenerators.

## 2. Frozen definitions (nothing here is fitted on F7 data)

**Registry rule.** It is the round-3 rule, unchanged, from `research/claude-round3-frozen-20261017.json` (git blob 6c87e117):
- D1 is E3's native fine-detail vector, and B1 is the 32 × 32 grey layout vector. Both are computed by `claude_two_factor_instance.Features` (blob bf3fc0b3) without a cache.
- Accept when D1 ≥ .0594367 and B1 ≥ .90.
- If D1 abstains for either image, accept when B1 ≥ .99.
- The rule function is `claude_round3_two_factor.rule` (blob c9ceed46).

**Record.** Each source has one record, owned by `qim-pilot-owner-alpha`: the F7 clean marked image, with q equal to that image's embedded payload q (`clean.jsonl`, `payload.q`).

**Pointer.** The pointer is the held-out pointer (`registry_step2_screen.pointer`, `m1b_registry_analysis.qmatch`), applied to each F7 carrier with the F7 union threshold:
- A carrier c (F5 or v5) carries q_c when, in the saved detect row under the owner's key, the semantic tier has `found` and `read`, `decoded_score` is at least 8.341671 (the F7 union threshold, 1e-6 split over two carriers), and `decoded_code` is a valid 32-bit word.
- The pointer selects record r when some carried q_c is within Hamming distance 6 of r's q.
- The in-mark content check (`content_match`) is not used, exactly as in the held-out run.

The pointer is taken from the saved detect rows (`detect-f7-*.jsonl`, both owners' calls), so no detector is rerun.

**Registry acceptance F_R** of a query against record r: the pointer selects r, and the rule accepts the (query, r) pair.

## 3. Data

All images come from the F7 screen run in the folder `/workspace/runs/f6l/f7/screen` on vast instance 58795791 (stopped, not destroyed). The run's code is commit 06545ee. Each image is fetched by the path in its journal row, and its SHA-256 must match the row. Otherwise it is listed as missing.

**Positives.**
- F7 natives, 3 seeds × 16 sources, in the three core cells: SD1.5 .2 (`R0-0.2`), SDXL .1 (`R1-0.1`) and Kandinsky 3 .2 (`K3-0.2`).
- Reported only: SDXL .2 (`R1-0.2`), SD1.5 .4 (`R0-0.4`), and the F7 clean images.

**Negatives.**
- **N1, T4:** 96 F7-arm T4 images (patch 128 and 256, their shams, residual .5 and 1.0).
- **N2, T5:** 16 F7-arm T5 images (the recipient image, unmodified).
- **N3, wrong-source pairs:** every F7 positive query against every other source's record.
- **N4, C0:** the 16 unmarked clean images and the 240 unmarked natives, against every record including their own source's.
- **N5, wrong owner (the held-out E3 test, exact-copy case):**
  - In each core cell, an attacker with key `qim-pilot-owner-beta` enrols the seed-0 F7 native of each source as their own record. Its q is the beta call's `semantic_code`, as in the held-out run. The F5 carrier's value is used; both carriers compute it from the same features.
  - That native is then the query, against all 16 alpha and 16 beta records.
  - The candidates and the attribution are computed by `m1b_registry_analysis.attribution` logic, with the pointer as defined in section 2.

## 4. Gates (all must hold)

| Gate | Bar |
|---|---|
| F_R, source majority (2 of 3 seeds), SD1.5 .2 | ≥ 12/16 |
| F_R, source majority, SDXL .1 | ≥ 12/16 |
| F_R, source majority, Kandinsky 3 .2 | ≥ 12/16 |
| N1 T4: accepts of any record other than the recipient's | 0 |
| N2 T5: accepts of any record other than the recipient's | 0 |
| N3 wrong-source accepts | 0 |
| N4 C0 accepts (any record) | 0 |
| N5 queries with a beta record accepted | 0 |

A seed blocked by the safety checker, or a missing image, counts as a miss for a positive. For a negative it is listed as unknown. An unknown negative in N1-N5 makes the verdict INCOMPLETE, not PASS.

- **PASS:** every gate holds and no negative is unknown.
- **SCIENTIFIC_KILL:** any F_R bar or any negative gate fails.

## 5. Early futility stop (local, before the instance is restarted)

The laptop already holds the seed-0 natives and clean images of the unmarked arm. As a proxy for D1 survival, the frozen rule (without pointer) is applied to each unmarked seed-0 native against its own unmarked clean image.

If fewer than 10 of 16 sources pass in SDXL .1 or in Kandinsky 3 .2, the test stops with SCIENTIFIC_STOP and the instance is not restarted.

The proxy is optimistic: the unmarked image carries no mark residual that regeneration would remove. That is why a fail is decisive and a pass is not. The same proxy on the F5 arm's seed-0 natives is reported, but it does not gate.

## 6. Reported, not gated

- F_R in each cell by carrier (F5 only, v5 only, union).
- The pointer alone, and the rule alone (fingerprint only), per cell.
- D1 abstain counts, and the D1 and B1 distributions.
- The pointer-only F_R upper bound for the F5 r2 and v5 r3 arms, from their own detect rows.
- Fingerprint-only attribution in N5.

## 7. Claim limits

- This is a development test on 16 sources. A pass makes "F7 pointer plus registry" a candidate for a fresh development round or a held-out confirmation, which would need the user's approval. It is not itself a confirmed result.
- The look-alike limitation (E2) belongs to the rule, not the pointer, and is not retested here.
- The further-regeneration attribution case needs new regenerations and is out of scope.
- F7 is an image-domain mark, not the proposal's latent method. Human visual review is missing.

## 8. Where things go

- Scorer: `scripts/f7_registry_test.py` on `claude/f7-dual-20261102`.
- Data and outputs: MAIN `.thesis-build/dev-runs/20261102-f7-registry/`.
- Results: `research/f7-dual-carrier-20261102/RESULTS-REGISTRY.md`.

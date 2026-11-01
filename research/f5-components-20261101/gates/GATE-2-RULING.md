# Gate 2 ruling

Claude (Opus 5.5), judge, 2026-11-01. Applies to commit 610d8dc. `PHASE_B_JOURNALS=off`.

**WP2 to WP5 are accepted with the changes below. Run the three new tests, revise the affected verdicts, then do WP6 and WP7 and stop.** This ruling binds wherever it differs from your request. It authorizes no GPU, no writer run, no held-out access and no change to F6.

## What I checked independently

With my own code, from raw journals and raw reader outputs ([verify_gate2_a.py](../judge/verify_gate2_a.py) to [verify_gate2_e.py](../judge/verify_gate2_e.py)):

- **Thresholds:** 8.2593, 4.9820, 8.4232, 5.2438, 10.7164 all reproduce.
- **T1:** every O, O_U and O_Q source count I recounted matches. Zero C0 and wrong-owner events in 12,960 calls.
- **T2:** T4 and T5 panel counts match. r3 accepts every wrong-content direction on F5, not only the report half: 22/22 DESIGN, 30/30 EVALUATE, 62/62 CROSS.
- **T3:** all retention medians I recomputed match to six places, from `T3-pairs.csv`. I did not recompute the pairs from pixels.
- **T4:** rho .6316 and .5506, cut 1.0033, gaps +.7768 and +.9768 reproduce.
- **Conduct:** 835 tool calls in 17 sessions. No vast key, SSH, held-out path, Phase B journal, diffusion or writer run, install, force-push or ruling write; the three pattern hits are prose, an exclusion glob and a read. Every changed file is inside RD, `judge/` is untouched, the tip is pushed, and the guard killed nothing.
- **Literature:** Crossref confirms identity, venue, volume and pages for Latent Watermark, Padhi, Ozkaya, Tang and Arenas. The AJSE page shows SJR Q1 and JCR Q2 as you recorded. The cards I read in K04, K08, K09 and K11 are careful and appropriately skeptical of their own sources.

I did not recheck TQ, TK2, the per-cell T0 table, T3 from pixels, or the other cards. WP6 samples those.

## R1. Floors

**The nine exhaustion dispositions are accepted as access-limited, not as floors met.** Report it that way: 32 of 56 journal slots and 35 of 36 conference slots are filled. Your K03 table shows why the gap exists. Directly relevant journal papers were found and could not be read (IEEE Access, TCSVT, CVIU). So the empty slots mean "not read", never "does not exist".

Specific decisions:

- **Accepted as counted, with the caveat kept on the card:** HOLISTIC accepted extension; Latent Watermark and MarkPlugger author versions; FEAP's author manuscript; CMBH; K11's two full-text-web PDFs without hashes.
- **TrustMark counts as TOP** for claims in its final main paper. The supplement stays unread and no claim may depend on it. K03 becomes 0/5 and 3/3. No ZIP download.
- **Ranking is a limit on the claim.** AJSE, PLOS ONE and Machine Learning are Q1 by SJR and Q2 by JCR. Keep them counted, and mark every journal row SJR or JCR in `floor-accounting.md`, so the count can be restated if the user chooses JCR.
- **K09's five journals are statistical foundations.** They count for reader calibration only. State that no Q1 journal paper on a watermark reader was read.
- **K08's journals carry little weight.** They are tamper-recovery papers. State that no counted journal paper bears on T3.
- **Search surfaces:** site-scoped web search is accepted as you disclosed it, and must not be described as native database search.

**Required:** write `literature/UNREAD-LEADS.md`, at most 15 identified but unread Q1 journal papers, ranked by what they could change, with DOI, component and one line on why. The user may be able to supply PDFs. K03 first.

## R2. Reader conclusions

**Rejecting promotion of O, O_U and exact r3 is accepted.** But your reason for the union is incomplete, and it hid an option.

**N3. The T4 event went through one specific route.** In `t4-residual-177015-25394-0.5` the instance decoded score is 8.2202 against 8.2593, just failing, and the recomputed score is 5.3190 against 4.9820, so `_channel_result` counts it as carrying the recomputed code. Yet the decoded word is 12 bits from the recipient's h. This follows from `derive_keys`: codes at distance d share 32-d segments, so a same-owner transplant scores about (32-d)/32 of its decoded score on any recomputed code. The ratio here is .647 against .625, and on the 20 DESIGN T4 rows the ratio follows that share. At scale 1.0 the same attack is correctly rejected by content mismatch, because the decoded word passes and is compared. So the failure is the recomputed route, in a gap just below the decoded threshold. It is not the second tier as such.

Consequences:

- **The kill stands for O, O_U and the cross-tier veto (K10-O3).** Your claim that no contradiction is available when semantic evidence is absent is too broad: inside the tier, the decoded word contradicts the recomputed code. Correct K09, K10, INTERACTIONS and the ledger.
- **My Gate 1 counts are inflated.** "C or second tier with content ok" (SDXL .1 32, SDXL .2 12) included the recomputed route. Do not cite them as gains. Second-tier found counts (52, 30) still stand as physical evidence.
- **r3 fails for the same reason in reverse:** it gives up the requirement that the best word lies near the suspect's own code. Hence 114/114 wrong-content acceptances.

**K09-O4, a new option you did not test.** Keep the requirement that the decoded word is the one compared, and spend the budget only on words that could be accepted. The acceptance set is then a ball, so the threshold may fall with no change to the binding logic. Section G2-A fixes it exactly.

**Error accounting.** Conditional-q is the primary statement for the honest null: the instance table is domain-separated from the semantic table, so a q chosen from the image and the semantic table is independent of instance-pattern randomness under the PRF model. O_Q stays a labelled sensitivity analysis. Neither says anything about an adaptive attacker with the public key, and every report must keep saying so.

## R3. Attribution and verdicts

**Accepted:** predictive margin evidence is not stage causation; response ordering is not a scale effect. K04, K05 and K08 keep research priority as joint diagnosis, with no rewrite.

| Component | Ruling |
|---|---|
| K01, K02 | KEEP accepted. Add the G2-C finding on q's low entropy to their limits. |
| K03, K06 | UNKNOWN accepted. |
| K04, K05 | IMPROVE accepted, for diagnosis and channel modelling only. |
| K07 | KEEP means no change is justified yet. It does not mean the budget is right. Lower the confidence until Q-STAGE. |
| K08 | IMPROVE accepted. Add G2-C if it holds: h may be the better binding code. |
| **K09** | **KEEP changed to UNKNOWN**, pending G2-A and G2-B. The production reader stays in place meanwhile. |
| K10 | IMPROVE accepted, with the corrected reason from N3. |
| K11, K12 | Accepted. K12 adds: no recomputed-only route counts as owner evidence in a new endpoint without a transplant test. |

## R4. Queue

Q-RES then Q-STAGE is accepted as the proposed order. **Q-STAGE's reuse of S12 is accepted as a mechanism diagnostic only.** Add Bs, Bi and B to both as reported endpoints, computed from saved raw scores. Q-RES is my recommendation to run before the coarse-lattice test and F6, because it is cheap, writes nothing and changes how F6's foreign cells are read. The user decides and pays. F6's package and receipt stay untouched.

**Required:** write runners for both under `server/`, each with a `--plan` dry run that prints exact units and costs, plus pure-logic tests. Execute neither.

## R5. Required next work

Number these tests G2-A, G2-B and G2-C, so they cannot be confused with threats T3, T4 and T5. The rules below were fixed before any EVALUATE outcome of B was computed. I saw only the DESIGN half for B, plus the EVALUATE T4 scores printed before this rule existed, including the N3 event. That event is therefore not fresh evidence for B, which is why G2-B exists.

### G2-A. Decoded-word reader B on saved journals

For a tier with decoded score s, decoded word w and the suspect's own code c (`semantic_code`, or `perceptual_hash` for the instance tier):

- d = Hamming(w, c); e = `_decoding_error_rate(s)`; corrected = min(32, max(0, (d-32e)/(1-2e))), exactly as in `_channel_result`.
- **The tier passes if and only if s >= 7.7791 and corrected <= 6.** The value is `_threshold` at alpha/2 with the ball of radius 9, 7.7791 by my calculation. Compute it in code and assert 32e(s)+6(1-2e(s)) < 10 for all s at or above it, so the acceptance set lies inside that ball.
- **B = semantic passes OR (instance passes AND NOT veto),** where veto = frozen `semantic.read` is true and frozen `semantic.content_match` is false.
- No recomputed route. Conditional union at most alpha. C OR B has at most 2 alpha and is reported separately, never as a replacement. C and J stay frozen.
- Hard corrected distance is primary for the semantic tier because F5's soft features are not saved. A soft-distance sensitivity with CPU CLIP is allowed, labelled descriptive.

Report C, J, Bs, Bi, B and C OR B for all 22 study/cells, both methods, both halves, with missingness rules unchanged. On EVALUATE, **kill B's promotion** if any of these holds:

1. Fewer than 5 gains over C across F5 foreign native source-cells (SDXL .1, .2, .4 and K3 .2, denominator 120).
2. Any loss of a C-positive F5 source on SD1.5 .1 or .2.
3. Any C0 or wrong-owner accept in any saved call.
4. Any accept that C rejects on the saved F5 T4 EVALUATE panel.
5. Any accept that the frozen-style rule (decoded at least 8.2593, corrected at most 6) rejects, at the same reference center, on the different-content T5 EVALUATE directions.

No threshold, radius or veto may be changed after an outcome. For reference only, my DESIGN result on F5 /30, C then B: SD1.5 .2 27 to 28, .4 18 to 18 (C OR B 21, two C sources lost by B), SDXL .1 0 to 9, SDXL .2 0 to 2, K3 2 to 4, and zero events in 1,252 negative calls and 40 T4 calls. Do not treat these as a forecast.

### G2-B. A larger T4 panel from saved marks

Forty F5 T4 images cannot settle this. Build residual transfers with the same formula as the `20261005-0700-f5r2-t4` panel, from existing clean Stage-2 F5 marks and their C0: recipients are all 30 EVALUATE sources, donors the first 8 DESIGN sources in sorted order, scales .5 and 1.0, giving 480 images. This is CPU arithmetic plus the F5 reader; it is not a writer run and is allowed under this ruling. Batches stay under 10 minutes. Save a PNG only for accepted images; keep metrics for all.

Report C, O, O_U, Bs, Bi and B with PSNR and SSIM against the recipient, plus LPIPS only if existing weights load without any download, otherwise MISSING. Report accepts per donor and per recipient, because the images are dependent. **Kill B's promotion on any B accept that C rejects at PSNR above 35 and SSIM above .9.** Zero events give about .6% one-sided if treated as independent, and they are not independent, so say both.

### G2-C. Code collision floor

On S60 clean C0 codes, report all pairwise Hamming distances for q and h: mean, minimum, and counts at or below 6, 8 and 9, by split, against the uniform share. My DESIGN result: q mean 10.03, with 30/435 at or below 6 and 178/435 at or below 9; h mean 16.13, with 0/435 at or below 8 and 2/435 at or below 9. This bounds chance acceptance under any transplant and bears on K01, K02 and K08. No kill rule. It is a limit to state.

### Then

1. Revise K09, K10, K08, VERDICTS, INTERACTIONS, the ledger and SERVER-QUEUE. If B survives, K09 becomes IMPROVE and `CANDIDATE-DESIGNS.md` may replace Design A with "retained F5 writer with reader B"; it may not exceed two designs. If B dies, K09 returns to KEEP with no rescue.
2. WP6: the three fresh reviews as in the brief. The floor review samples at least 20 cards including TQ, TK2 and T0 inputs, and re-opens one K11 full-text-web PDF. The hostile review attacks N3, B's validity argument and my rule choices as hard as your work. The steelman review looks for what this ruling wrongly rejected.
3. WP7: `FINAL-REPORT.md`. No hidden wins: every candidate names what it did not test.

Commit and push after each step. Stop when WP7 is pushed. Your final message is at most five lines, in English.

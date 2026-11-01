# Final ruling

Claude (Opus 5.5), judge, 2026-11-01. Applies to commit d58ead5. `PHASE_B_JOURNALS=off`.

**The dossier is accepted. F5 stays the reference. No component change was shown to improve F5 safely.** This ruling authorizes no GPU, writer run, held-out access or change to F6. Frozen C and J are unchanged.

## What I checked independently

- **G2-A, G2-B, G2-C:** recomputed with my own implementation of the rule, written apart from `gate2_reader.py` ([verify_final.py](../judge/verify_final.py)). All match: F5 EVALUATE C to B 30 to 30, 30 to 27, 21 to 24, 0 to 12, 0 to 4, 0 to 0, 3 to 6; lost sources 629, 790, 1779; G2-B C 0, O 14, Bs 0, Bi 2, B 2 of 480; G2-C q mean 10.857, h mean 16.023. My B agrees with the recorded B on every row. O_U 8 is taken from the recorded rows and the hostile review's recount; I did not recompute it.
- **New from that recount:** of the 14 O accepts beyond C, 13 used the recomputed-only route and 1 a read decoded word. N3 explains most of the union's failure, not all of it.
- **Conduct:** 203 tool calls in 11 sessions. No vast key, SSH, held-out path, Phase B journal, diffusion, install, force-push or ruling write. The three `robust_pgd` and `embed_rgb` hits are source-hash pins in server code, not writer runs. Every changed file is inside RD, `judge/` is untouched by Codex, the tip is pushed, and the guard killed nothing.
- **Runners:** both self-tests and the 14 integration tests pass here. I read Q-RES's generation and reader paths and found no defect. Neither runner has met a GPU.
- **Literature:** Crossref confirms three of the top unread leads. The floor review reopened 20 works online. I did not reread the other 28.

## Errors of mine that the reviews found

1. **"No change to the binding logic" was false.** My rule replaced F5's soft binding with hard corrected distance, and the three SD1.5 .2 losses come from that, at scores 9.85 to 12.81, well above both thresholds. G2-A was a fair test of the package I specified. It was not a test of a lower threshold alone.
2. **G2-C does not "bound chance acceptance under any transplant".** It describes clean-code distances on 60 images. The G2-B pair shows why: clean h distance there is 13, yet the decoded word lands within 8 and 9 bits of the recipient.
3. **"Corrected" distance is a model statistic, not an error bound.** It tolerates more differing bits at lower scores, where the evidence is weakest. B inherited this. Frozen C has the same property.

## Rulings

**F1. Verdicts.**

| Component | Final verdict | Scope |
|---|---|---|
| K01 semantic descriptor | KEEP | q is concentrated on this cohort: mean pair distance 10.46 of 32. A limit to state. |
| K02 content code | KEEP | Approximation caveat stays. |
| K03 payload code | UNKNOWN | Distance 2 refutes a one-chip guarantee. No new code was written. No journal paper read. |
| K04 carrier space | IMPROVE | Diagnosis only, through Q-RES. No rewrite is justified. |
| K05 encoder model | IMPROVE | Channel diagnosis only. F6 unchanged. |
| K06 optimizer | UNKNOWN | Margin predicts survival. The cause is unidentified until Q-STAGE. |
| K07 quality budget | KEEP | Low confidence until Q-STAGE. Not a claim that the budget is right. |
| K08 second carrier | IMPROVE | Diagnosis only. Its physical signal on SDXL is real; no safe acceptance rule exists. |
| K09 reader statistic | KEEP | The production reader stays. Reader research remains open: only the tested packages are rejected. |
| K10 binding decision | IMPROVE | Reporting only: separate unchecked, decoded, recomputed and conflicting evidence. |
| K11 keys | KEEP | Narrow public-statistical scope. No unforgeability claim. |
| K12 evaluation | IMPROVE | Cross family and resolution; keep separate endpoints and dependence explicit. |

**F2. Reader packages.** O, O_U, exact r3 and B are all rejected, and B gets no rescue in this study. Frozen C accepted 0 of 480 copy-paste images. Report that with its limits: development data, shared donors and recipients, an attacker holding the unmarked donor, and no human viewing. A later reader needs a fresh disjoint protocol with its null argument written first.

**F3. Steelman options.** All three stay deferred, without a forecast. Joint q and h decoding is the first reader question to return to. One note for whoever does: a contradiction check can only shrink the acceptance set, so it needs no extra false-positive budget, but anything aimed at the G2-B pair is post hoc on these sources. The other two wait behind the transport diagnosis.

**F4. Literature.** Accepted at 32 of 56 journal slots and 36 of 36 conference slots, with nine access-limited exhaustions. No paper read demonstrates survival of an independently trained encoder at F5's quality, so the literature changes what to test, not any measured gain. Its 14 unread leads have zero credit. The quartile evidence is SJR or JCR as marked and mostly third-party, and it does not certify any paper.

**F5. Queue.** I recommend Q-RES then Q-STAGE before the coarse-lattice test and F6. They are cheap, Q-RES writes nothing, and both change how F6's foreign cells and its budget should be read. No evidence proves this order is best. The user decides and pays. A pilot on the first source must run first, and any report must show missingness bounds beside the fixed counts (hostile W09, W10). Q-STAGE's reuse of S12 is a mechanism diagnostic only. Neither run can promote a method.

**F6. What may not be claimed.** Neither design nor any result here claims latent insertion, lightweight extraction, cryptographic or legal ownership, universal independent-encoder survival, confirmed T4 or T5 safety, human invisibility, or Q1 submission readiness.

The Codex session is closed. Further work needs a new decision from the user.

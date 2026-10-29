# Round 2: close the known risks before Stage S runs (Codex session brief, 2026-10-29)

Written by Claude (Opus 5.5) after reviewing round 1 (head `665b4dd`). The user asked, verbatim: "خب بهتر نیست اول ریسک هارو توسط codex برطرف کنیم و بعدش ادامه بدیم؟" ("Isn't it better to have Codex fix the risks first, then continue?"). Claude proposed the scope below, and the user answered, verbatim: "خود مقاله رو دانلود کردم. الان پرامپت رو بده تا تو کدکس ادامه بدم." ("I downloaded the paper itself. Now give me the prompt so I can continue in Codex.")

The rules of `BRIEF.md` section 1 apply unchanged: nothing runs on this laptop; stdlib Python only; write in `research/tifs-20261028/` (TD) and `scripts/tifs_*`; never modify F5 r2, v5 r3 or any retained artifact. **No Stage S output exists yet**, so the design may still change now. Every change must be committed, reviewed and frozen before any server run, and recorded as a pre-output amendment in `TD/08-round2-amendment.md`. The session is **3 hours**. Log it in `TD/PROGRESS.md` under a new "Round 2" heading with its own deadline.

## What Claude found in round 1

Round 1 is sound as preparation:
- the paths touched comply with the brief;
- the guard killed nothing;
- the 67 tests pass when Claude reruns them;
- the F6 writer matches `f5_latent_codec.robust_pgd`/`embed_rgb` line by line, adding only the surrogate gradient.

Three risks remain. The second is the most important, because it decides whether a Stage S pass would matter for TIFS at all.

## R2-1: novelty check first (30 min)

- **ForenMark** (Knowledge-Based Systems, DOI 10.1016/j.knosys.2026.117084, listed 25 October 2026). The user downloaded the full text.
  - Look for it at MAIN `.thesis-build/cache-tifs/papers/forenmark.pdf`, then in `C:/Users/Soroush/Downloads/`.
  - If it is in neither place, record it as still not full-text inspected and continue.
  - **Where the PDF comes from (CLI run).** The user is away from the laptop and is sending the PDF to Claude, who puts it at the cache path above. If it is not there when you start, do R2-3 and R2-2 first. Check for the file at the start of every item, and do the ForenMark part of R2-1 as soon as it appears. If it is still missing when 40 minutes remain, record ForenMark as uninspected.
  - If found, write a card: claim, mechanism, threat model, what it reads, side information, robustness and regeneration results, limits.
  - Say exactly what it pre-empts for F6 and for R2-2's bound-carrier arm.
- **The other papers.** Re-check F6's exact claim and the bound-carrier arm against SemBind (2601.20310), MetaSeal (2509.10766), Dual-Guard (2604.19090), Guidance Watermarking (2509.22126), DrawMark, OptMark (2508.21727) and ONRW (2601.17388). Read the method sections relevant to these two claims only. Claude verified that Guidance Watermarking and SemBind exist as described. The venue labels in round 1 (ICLR 2026, ICML 2026) were not visible on their arXiv pages, so confirm or drop them.
- **Where to record it.** Update `02-prior-art-delta.md` and the novelty paragraph of `04-selection.md`. If F6's claim is pre-empted, say so plainly and carry it into the feasibility verdict.

## R2-2: a bound robust-carrier baseline inside Stage S (85 min design and code)

**Why.** VINE-R keeps its known message in every cell (158-200 of 200 held-out sources). A TIFS reviewer's first question will be: why not put the content-bound code into a robust published carrier? That means writing F5's semantic code q, and whatever owner information the F5 rule needs, into VINE-R's 100-bit message, and at detection comparing the decoded code with q recomputed from the suspect under the unchanged F5 content-consistency rule. If that baseline does as well as F6 across families, a Stage S pass for F6 would not support a TIFS claim. If it does better, it may be the stronger article contribution, subject to R2-1's prior art.

**What to do.**
- Specify and implement **VINE-B** as a Stage S arm, reusing the retained VINE-R adapter and F5's semantic functions without modifying them:
  - Message layout: keyed function of owner and q, and h if the rule needs it.
  - Decoding, and the binding decision with the F5 soft rule.
  - Wrong-owner and C0 queries.
  - Endpoints C, Q, J and F where they apply.
  - T4/T5 in the combined mode.
  - The secondary distortion grid.
- Decide, with reasons, whether a WAM-B arm is needed too. WAM has only 32 bits.
- Before any output, fix how F6 must compare with VINE-B for the **article** claim, separately from the thesis gate. For example: non-inferior or superior on a pre-declared dimension such as clean quality (LPIPS/PSNR), T4/T5 false acceptance, exact payload recovery, or reader cost and side information.
- Fix the verdict labels for each outcome. For example: "F6 GO and article GO"; "F6 GO but VINE-B dominates: article claim moves to the bound-carrier protocol, if R2-1 leaves it new"; "both fail".
- Update `05-stage-s-protocol.md`, `stage-s/frozen-config.json`, the runtime, readers, analysis and tests. The thesis gates of round 1 stay as they are.

## R2-3: GPU memory and capacity fix (30 min)

- **The bug.** `scripts/tifs_stage_s_forecast.py` line 38 hardcodes `gpu_ok = peak_device_bytes <= 24 * 1024**3`. The F6 writer backpropagates through the SDXL VAE encoder and decoder at 1024x1024 in fp32. Claude's estimate is that this probably needs more than 24 GiB of activations. The result would be an OOM on a 24 GB card, or a false RESOURCE_STOP on the 48 GB card that the Phase-B instance reports. Claude plans to reuse that instance (57877693, about 49,140 MiB reported).
- **Fix 1, checkpointing.** Enable gradient checkpointing on the VAEs that the F6 writer differentiates through. This does not change the mathematics. First confirm from the diffusers 0.35.1 source, read online, that `AutoencoderKL` encoder and decoder checkpoint in eval mode under `torch.is_grad_enabled()`. If they do not, implement an equivalent `torch.utils.checkpoint` wrapper around the blocks. Keep it off for native regeneration, readers and quality.
- **Fix 2, capacity bound.** Derive the bound from the measured device total minus a stated margin, for example 1.5 GiB, recorded in the forecast. Keep "24 GB class" only as the minimum hardware statement.
- **Tests and documentation.** Add tests. Update the RUNBOOK and `writer-implementation.md`.

## R2-4: cost (10 min)

Recompute the Stage S inventory and the conservative time budget with the new arm or arms. Keep the 15-instance-hour cap, or state the smallest new cap as a decision for the user.

## R2-5: independent review (25 min)

Spawn one fresh reviewer agent (gpt-6-astra, xhigh, no prior context) on the round-2 diff only. Its scope is correctness against the amended protocol, decision rules fixed before outputs, the bound-carrier implementation and its side information, and the memory fix. Apply its findings and record the dispositions in `TD/07-review.md` under "Round 2".

## R2-6: handoff (when less than 25 minutes remain)

- **Final report.** Refresh `FINAL-REPORT.md`. Keep line 1 `STATUS: COMPLETE` or `STATUS: PARTIAL`. Line 2 is the `FEASIBILITY` verdict, revised if R2-1 or R2-2 change it. Add a short "Round 2" section.
- **Other files.** Update `stage-s/READINESS.json` and the RUNBOOK. Replace the TIFS section in MAIN `thesis-runs/d916749c/STATE.md` (at most eight lines).
- **Close.** Commit, push, and end with a short Persian summary.

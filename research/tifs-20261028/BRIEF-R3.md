# Round 3: raise F6's chance of passing the thesis gate before Stage S (Codex session brief, 2026-10-29)

Written by Claude (Opus 5.5) after reviewing round 2 (head `2c41d5f`). The user asked, verbatim: "کار دیگه ای نمیشه کرد تا F۶ بتونه سقف پایان نامه رو رد کنه؟ و احتمالش بالاتر بره؟ من ۷۸ درصد از لیمیت هفتگی کدکس 5x رو دارم و میتونم ازش استفاده کنم. از سطح thinking در ultra میشه استفاده کرد اگر بخوای." ("Can nothing else be done so F6 can pass the thesis bar, and raise its probability? I have 78% of my weekly Codex 5x limit and can use it. Ultra thinking can be used if you want.") Claude proposed the round below. The user answered, verbatim: "شروع کن" ("start").

## Rules

- **Unchanged rules.** The rules of `BRIEF.md` section 1 apply:
  - nothing runs on this laptop;
  - stdlib Python only;
  - write only in `research/tifs-20261028/` (TD) and `scripts/tifs_*`;
  - never modify F5 r2, v5 r3 or any retained artifact.
- **Ultra effort.** This session runs at `ultra` effort, which is the user's explicit override of the AGENTS rule "never max or ultra". Agents you spawn stay at `xhigh` or below.
- **No outputs yet.** Neither Stage S nor Stage P outputs exist, so every change is a pre-output amendment. Record each one in `TD/09-round3-amendment.md`. Never write or simulate scientific outputs.
- **Gate changes are proposals, not decisions.** Implement them so they can be selected, but keep the current round-1 gate as the default and effective profile.
  - The user chooses after this round. Claude then records the choice in a commit before any server run.
  - Never write an approval yourself.
  - Never lower a bar only to raise the pass probability without stating, next to it, what the claim loses.
- **Article rule.** The F6-versus-VINE-B article rule stays as frozen in round 2. Adapt it only where a quality-budget change forces it, and say so.
- **ForenMark.** It is still not available. Skip it; Claude handles it if the user supplies it.
- **Progress log.** The session is **4 hours**. Log it in `TD/PROGRESS.md` under a new "Round 3" heading with its own deadline. Commit and push after every item.

## What Claude found: three weaknesses and two gate issues

1. **No GPU feedback.** Every F6 setting was chosen on paper: steps, the noise schedule, loss weights and the quality budget. Stage S would be its first execution. The 0.25 prior is a zero-shot estimate.
2. **The surrogate is not the attack.** `scripts/tifs_writer.py` (around line 233) computes `z = a*z + b*eps` and then decodes `z / scaling_factor` directly: "No division by a, latent normalization, denoiser, or RGB8 rounding". The real regenerators run the denoiser for the remaining steps. The denoiser pulls the latent toward natural images and removes perturbations that look like noise. That is the most plausible removal mechanism behind F5's 0/200 at SDXL .2, while codec round trips alone kept 55/60. The current objective trains readability from a decoded noisy latent, not survival of denoising.
3. **The quality budget is locked to F5.**
   - Writer budget: the robust-stage target is `psnr_db` 52 and the refine target is 58.
   - Gate: F6's paired median LPIPS may exceed F5's by at most .005, and its PSNR may be at most 1 dB lower.
   - Absolute bar: it only requires PSNR > 35, SSIM > .9 and LPIPS < .1.
   - So F6 must survive regeneration with essentially F5's energy. This may be the binding constraint.
4. **Gate issue: the conjunctive ablation bar.** F6-noise must also beat F6-codec and F6-generic by at least 3 sources in each SDXL cell and at least 1 in K3. If a control also works well, the whole gate fails, even though a positive cross-family result exists.
5. **Gate issue: K3 is unseen.** K3 is excluded from optimization yet must reach 12/16, against F5's 61/200 held-out. Stage C already plans SD3.5 as its prospectively unseen family.

## R3-1: denoiser-aware surrogate (60 min)

- **Add a writer variant** (working name `f6-x0`) whose surrogate includes the native denoiser, for each optimized family:
  1. encode with the posterior mode, as now;
  2. form `z_t = a*z + b*eps` at a timestep sampled from the native img2img window of that cell's strength (derive the window from the pinned scheduler and native step count);
  3. run one ε-prediction of the native UNet with the native conditioning;
  4. form the x0 estimate, decode and read.
- **Match the native pipelines** used by the Stage S runtime: prompt, negative prompt, guidance scale and SDXL added conditioning (time ids, pooled embeddings). If they use classifier-free guidance, decide between the exact two-branch and a cheaper approximation, and justify the choice.
- **Optional search option:** a k-step DDIM surrogate with checkpointing. Add it to R3-2's search space only if the budget allows.
- **Primary sources.** Confirm from diffusers 0.35.1 source, read online, how `UNet2DConditionModel` gradient checkpointing behaves in eval mode and how the SDXL conditioning is built.
- **Memory and precision.**
  - Choose the UNet weight dtype and autocast policy, and state their effect on gradients.
  - Enable checkpointing only inside writer gradient scopes, as in round 2.
  - Extend the capacity rule and the rehearsal checks: finite nonzero gradients, plus a parity check of the one-step surrogate against the native first step.
- **Arms.** Keep the current `f6-noise` as an ablation, with F6-codec and F6-generic still as controls.
- **Tests.** Write pure-mock tests for the schedule, the conditioning assembly, scope cleanup and the variant dispatch.

## R3-2: Stage P, a tuning stage on the 24 unused development sources (50 min)

- **The 24 sources.** The 60-source pool in `research/encoder-transfer-20261019/source-list.json` minus all four partitions of `stage-s/source-manifest.json` (16 + 16 + 2 + 2) leaves 24.
  - Verify the count and write a committed Stage P manifest with its SHA256.
  - Never use Stage S sources, the 200 Phase-B sources, the 40 reserves or Stage C identifiers.
- **Purpose.** Choose F6's frozen configuration before Stage S. Stage P results are development evidence, never enter Stage S or Stage C denominators, and are reported as tuning.
- **Pre-declared, bounded search space.** Fix it before any output, and keep it small, because each F6 write is expensive:
  - surrogate: `f6-noise`, `f6-x0`, and k-step only if affordable;
  - quality budget: several robust-stage PSNR targets between 52 and the strict floor, for example 52, 46, 42 and 38, each meeting the absolute strict bar on every source;
  - K3 in or out of optimization: design both, as a user decision; see R3-3;
  - steps and EOT samples only if needed.
- **Allocation and cells.** Use successive halving or a similar budgeted allocation over cells R1 .1, R1 .2 and K3 .2, plus R0 .2 retention. Fix seeds, rungs and per-rung source counts in advance. Split the 24 sources so the final selected configuration is checked on sources that did not drive the selection.
- **Selection rule, fixed before any output.** For example: maximize the minimum, over foreign cells, of the C and J source-majority counts, subject to strict quality on every source, clean F and zero C0 or wrong-owner false events; break ties by quality.
- **Stop-early rule.** If the best configuration falls clearly below the Stage S bars on Stage P, stop and report before paying for Stage S. Define "clearly" in advance.
- **Multiplicity.** Record every configuration tried, and disclose that number in the thesis and the article.
- **Code.**
  - Reuse the Stage S runtime (journals, native replay, readers, quality) with a Stage P mode rather than new infrastructure.
  - Add a selection script that writes `TD/stage-p/selected-config.json`.
  - Stage S consumes that file. Without it, Stage S runs the current frozen F6 configuration, if the user declines Stage P.
- **Matched-quality F5 control.** If R3-3 recommends it: the F5 objective at the selected F6 budget, implemented through the F6 writer with the surrogate disabled. Prove by test that it equals F5 `robust_pgd` at the original budget. F5 r2 itself is never changed.

## R3-3: gate analysis and proposals for the user (40 min)

- **Pass-probability model.**
  - Per cell and arm, assume a true per-source retention rate p, with 3 seeds, source majority and n = 16.
  - Compute the probability of passing the current gate, and each alternative, over a grid of plausible p.
  - Show which conjuncts dominate.
  - State every assumption, and label all estimates subjective. Give your own subjective pass estimate for the current design and for the recommended package.
- **Proposals to evaluate.** For each, state what it buys and what the claim loses:
  - **a.** Replace F5-relative quality parity with the absolute strict bar, plus a matched-quality F5 control. The attribution test becomes a gain over that control.
  - **b.** Make the ablation gains a secondary mechanism report instead of a primary conjunct, or lower them.
  - **c.** Put K3 into optimization (seen), so that unseen-family generalization rests on SD3.5 in Stage C, or keep it unseen.
  - **d.** Anything else you find, for example the 12/16 absolute bar at SDXL .2 measured against what VINE-B is likely to reach.
- **Implementation.**
  - Write gate profiles in the config: `round1` (default, effective) and `round3-proposed`.
  - The analyzer reports both.
  - The run records which profile the user approved; Claude commits that receipt, and Codex never writes it.
- **Decisions for the user.** Write a "Decisions for the user" section in `09-round3-amendment.md`, one line per choice with its consequence, and a recommended package.

## R3-4: cost (20 min)

- Inventory and a conservative GPU-hour forecast for Stage P and for the amended Stage S, including UNet backward for `f6-x0`.
- Plan one server session: setup once, then Stage P, then a freeze (selection plus the user's gate choice, recorded by Claude), then Stage S.
- Give the caps as decisions for the user.
- The old 15-hour Stage S cap may need to change; give the smallest defensible cap and its arithmetic.

## R3-5: independent review (25 min)

Spawn one fresh reviewer agent (gpt-6-astra, xhigh, no prior context) on the round-3 diff only. Its scope:
- correctness of the x0 surrogate against the native pipelines;
- the Stage P isolation, with no leakage into Stage S or Stage C;
- the selection and stop rules fixed before outputs;
- the gate profiles, with the default staying effective;
- the cost arithmetic.

Apply its findings and record the dispositions in `TD/07-review.md` under "Round 3".

## R3-6: handoff (when less than 25 minutes remain)

- **Final report.** Refresh `FINAL-REPORT.md`:
  - line 1 `STATUS: COMPLETE` or `STATUS: PARTIAL`;
  - line 2 the `FEASIBILITY` verdict;
  - a short "Round 3" section with the subjective pass estimates before and after, and the decisions for the user.
- **Other files.**
  - Update `stage-s/READINESS.json`.
  - Update the RUNBOOK, adding a Stage P section before Stage S.
  - Replace the TIFS section in MAIN `thesis-runs/d916749c/STATE.md` (at most eight lines).
- **Close.** Commit, push, and end with a short Persian summary.

---
name: feedback-three-threat-scope
description: Thesis watermark work must stay on the three threats T3 regeneration, T4 copy-paste, T5 semantic collision; no other attack types
metadata:
  type: feedback
---

Test and judge designs only on T3 (regeneration), T4 (copy-paste forgery) and T5 (semantic collision), as defined in `research/threat-model.md`. Do not run or weigh other attacks (T1/T2: JPEG, grayscale, crops, colour changes).

**Why:** on 2026-10-05 the user asked why I tested colour attacks on family 4 when the goal was the three threats. I had run grayscale/saturation/hue/JPEG, led my summary with "grayscale removes it" as a serious weakness, and let it steer the next hypothesis, while T5 (in scope) was only argued, not measured.

**How to apply:** for any candidate, measure all three of T3/T4/T5 before anything else; if a design obviously opens a new cheap removal route, mention it in one line as an unweighted limitation, not as a test campaign or verdict input. `AGENTS.md` now has a "Threat scope" rule saying the same for Codex.

Related: [[f4-chroma-carrier]], [[m1-regeneration-gate]], [[codex-autonomous-handoff]]

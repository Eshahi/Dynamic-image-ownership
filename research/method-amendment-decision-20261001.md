# Method amendment decision record: v4 candidate

Date: 2026-10-01

## Source of the instruction

The user's direct instruction in the Claude Code session of 2026-09-30/2026-10-01, working in the main checkout. Original wording (Persian):

> من الگوریتم رو بهبود دادم ولی هنوز به نظرم یک سری جای کار داره. اونو بررسی کن، نیاز داشت بهبودش بده طبق برنامه و plan، همینطور حتما لازم نیست روش دقیقا روش proposal باشه میتونیم بهش اضافه کنیم ولی میخوام معیار های آکادمیک و تطابق با پروپوزال رو حفظ کنه.

Translation: "I improved the algorithm but I think it still needs work. Review it and, if needed, improve it according to the programme and the plan. The method does not have to be exactly the proposal's method; we can add to it, but I want it to keep academic standards and conformity with the proposal."

Recorded by: Claude Code (model `claude-opus-5-5`), the author of the v4 files. This record is not a supervisor or university approval, it accepts no gate, and it authorizes no compute.

## What the instruction is taken to authorize

- A review of the v3 candidate (`scripts/revised_watermark_v3.py`) against the proposal, the scope guard and the proposal-aligned plan of 2026-09-30.
- A new, separately versioned candidate that adds to the proposal's method where the additions are declared and justified, and that restores proposal mechanisms the QIM candidates had dropped.
- Engineering work only: code, synthetic tests, a synthetic benchmark, configuration files and documentation.

## What it is not taken to authorize

- Replacing the latent/initial-noise route. v4 is an image-domain codec and is labelled the pixel comparator; RQ-02 and HYP-02 stay open.
- Any run on study images, model weights or a GPU. None was performed.
- Editing the proposal, the claim ledger, the A5 method specification, the v2/v3 code, the retained run outputs, `AGENTS.md`, `approval-policy.md`, `continuation.md` or the offline guide. None was edited.
- Commits, pushes, issue or PR changes. None was made.
- Introducing a secret-key model as the method's default. The default profile is the proposal's public-derived one; the keyed profile is a separately labelled variant.

## Consequences

The v4 candidate needs, before any scientific use: an independent review of the exact amendment and code, its own preregistered profile (A4), the wrapper and receipts listed in [method-amendment-v4.md](method-amendment-v4.md), and the existing runner's manifest-specific authorization. The declared additions and deviations are listed in that file under "Additions and deviations". Whether the thesis adopts v4 as its image-domain arm is a decision for the user and, where the method materially departs from the approved proposal, for the supervisor.

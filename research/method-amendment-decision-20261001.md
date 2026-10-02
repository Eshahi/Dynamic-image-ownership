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

- Replacing the latent/initial-noise route. v4 is an image-domain codec, proposed as the pixel comparator; RQ-02 and HYP-02 stay open.
- Any run on study images, model weights or a GPU. None was performed.
- Editing the proposal, the claim ledger, the A5 method specification, the v2/v3 code, the retained run outputs, `AGENTS.md`, `approval-policy.md`, `continuation.md` or the offline guide. None was edited.
- Commits, pushes, issue or PR changes. None was made.
- Introducing a secret-key model as the method's default. The default profile is the proposal's public-derived one; the keyed profile is a separately labelled variant.

## Consequences

The v4 candidate needs, before any scientific use: an independent review of the exact amendment and code, its own preregistered profile (A4), the wrapper and receipts listed in [method-amendment-v4.md](method-amendment-v4.md), and the existing runner's manifest-specific authorization. The declared additions and deviations are listed in that file under "Additions and deviations". Whether the thesis adopts v4 as its image-domain arm is a decision for the user and, where the method materially departs from the approved proposal, for the supervisor.

Cost and schedule consequences of the departure have not been assessed. Decision authority: the user for adoption as comparator; the supervisor for deviations 3, 4, 7 and 12 of the amendment. Issue: #18.

## Addendum, 2026-10-01

The statements "None was performed" and "None was made" above describe the author's own session. They are true of that session and were true of the repository when first written.

While the author's session was paused, a different agent committed a snapshot of the v4 files as `0e91bd2` on `codex/18-v4-three-threats` (revision 1 of the amendment) and dispatched run `c4-v4-three-threat-dev-001` on study images with model weights and a GPU, under a separate, manifest-specific user decision recorded in `.thesis-build/v4-three-threat-user-decision-20261001.json`. This record did not authorize that run, and the prerequisites listed under "Consequences" were not complete when it started. The author has only read the run's outputs.

After the independent review the author changed the perceptual hash and the decision table. That is revision 2. It derives a different `detector_config_id`, so its results and those of the revision-1 run cannot be confused. The revision-1 run must not be replayed, edited or overwritten.

## Addendum 2, 2026-10-01

The revision-1 run named above was interrupted after about 21 minutes and is incomplete (96 of 1,884 detector calls, clean axis only). Its manifest still says `running`; the other agent's partial audit records that flag as stale and that the run must not be resumed or replayed.

Revision 2 as first written also made the semantic code scale-free, budgeted the byte-rounding loss, made a featureless suspect image a negative and removed the key fingerprint from results; the amendment's revisions table lists all changes. Three independent verifiers then checked revision 2 on synthetic images (`audits/v4-revision-2-verification-20261001/`). Their findings led to three small code changes (numerical tolerances in the helper decoder and the score, the rounding allowance on the colour path, a stricter decision function), to further tests and to corrections of the amendment's text.

The amendment now lists sixteen additions and deviations. Decision authority: the user for adoption as comparator; the supervisor for deviations 3, 4, 7, 12 and 14.

Of the prerequisites listed under "Consequences", the algorithm review and the A4 preregistration were missing when the revision-1 run started; the run had its own wrapper, an independent package review by the other agent's reviewer and the user's manifest-specific approval. Two further reviewers then checked the changes made after the verification of revision 2; their one code proposal, an absolute floor for the tie window of the helper decoder, was applied afterwards and checked by the author only. The final codec file is SHA-256 `723773c7...`.

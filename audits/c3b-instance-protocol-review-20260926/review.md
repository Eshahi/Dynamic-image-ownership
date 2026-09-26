# C3b independent engineering review and delegated decision

Actual reviewer `/root/b3_intake_review`, author/decision recorder `/root`.
Source of delegated authority: AGENTS.md and research/approval-policy.md,
authenticated user's2026-09-22 instruction. Decision checkpoint2026-09-26T15:54:10Z.
This is an actual distinct reviewer, not an invented human verdict.

## Versions and findings

First exact candidate `e576b1c7efdeddd9b0f189d2a0a8ea44649a1858`: no core arithmetic
or score-inventory blocker. Reviewer ran nine tests, independently matched direct
full2D DCT coefficients and packed codes on three additional owned shapes, checked
fixed13/429 inventories, common-q rule, strict thresholds, zero-variance veto and
tie ordering. Regenerated report and five provenance hashes matched. Windows/WSL
protocol fields matched; small floating-margin differences were preserved.

One actual blocker against immutable guide-plan-38 C3b steps/outputs: report
omitted explicit key distances and fixed pair/shape inventory. Author repaired
generator, declared report and regression at exact
`693a4fbc444522515f1437fe3484bcc8f0e6eaf0`; core instance.py unchanged.

Actual re-review found **no remaining narrow C3b blocker**. Ten focused tests pass;
JSON-normalized regenerated report matches, all five provenance hashes match.
Four pairs' native HWC shapes, byte lengths2/4/32/32 and every q/pHash/Ws/Wi Hamming
distance independently verified:

- Repeat: all0bits.
- Same supplied syntheticq, changed native instance: h8bits, Wi129bits, Ws0bits.
- Wrong public owner: Ws138bits, Wi138bits, h/q unchanged.
- Differently colored constant collision: all0bits, explicitly retained.

The shared q is a **synthetic semantic-code control**, not measured equivalent
semantic content. Neither pHash nor public signatures are collision-free or
authentication evidence. Scores/config/threshold labels are caller-supplied, not
calibration or the full C5 detector. No study images, models, GPU, scientific
execution, installs/downloads or source writes occurred during review.

## Report custody and reproducibility

At the reviewed repair, the JSON objects agree but byte encodings differ:

- Committed LF blob SHA256 `c1021e8a50b9a7220c51bccd223b926b929e1794271938c2ee8ec91ab6c96485`.
- Checkout bytes SHA256 `fc7fa289aeb89801411c134402fadcf2caff2603c8498c2226a77cda8652cb74`.
- Original generated Windowsv2 receipt SHA256 `dc481fba404e19770423926e3f2c2eefc5163dd896335687efca0f73b91ebf41`.

Earlier v1 Windows/WSL originals remain in stableignored .thesis-build, recorded
by reports/dev/instance-protocol-parity.json. No failed check or unfavorable
collision was removed. The original full-float parity failure and diagnostic
syntax failure are documented. A later direct object comparison initially failed
because Pythonlibc tuple becomes a JSONlist; JSON-normalized replay passed without
altering results or relaxing a numerical test. There is no universal runtime
bit-parity claim; platform/libc identities remain explicit.

Tests:10focused passWindows andWSL,38combined Windows owner/instance/semantic/C2
tests34pass4expectedskips,185script tests174pass11expectedskips. The immutable guide
names pytest, but neither installed environment contains it: **pytest was not run
or claimed successful**. These unittest classes were executed directly by the
standard-library runner in both existing environments, an explicit ordinary
test-command substitution, not a scope/method change or an unauthorized install.

## State-bound task acceptance

After resolving the actual blocker, `/root` accepts only C3b's CPU implementation/
protocol deliverable under the recorded delegation. PR#66 may close issue#17
after exact remote-head/merge verification; future scientific pHash/marked-image
stability, full detection and attribution/rights claims remain unproved. The prior
approved C2 single scientific run is consumed and was not repeated. This task
review grants no additional compute authorization.

Official controller: d916749c paused atplan-acceptance, nullchoice, workflowSHA
`772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51` unchanged.
No lifecycle transition/human acceptance is invented. C4/#18 becomes dependency-
ready only after actual#17closure; its scientific outputs cannot be closed on
these synthetic protocol tests.

# C4 reconstruction localization launch-design review

Author: `/root`. Independent reviewer: `/root/b3_intake_review`.
Authority: research/approval-policy.md; bounded technical review only.

## Exact reviewed artifacts and findings

The reviewer inspected the complete worker, launcher, manifest builder, input
closure, component, strict experiment specification and design at
`813b4c00c928a18785365c6dc2bed6231c5597e3`. The in-memory builder reproduced
candidate canonical manifest SHA-256
`9b3d44b0940dd3c4b9d1549374e5bbf3fb804921dd5164dd553cf915d6fd1449`;
all 42 input pins matched working bytes and Git equivalents. This candidate is
historical, not the final execution binding.

No blocking launch-design finding remained. Two nonblocking warnings were real:
initial resource measurements followed the refusal guard, and an unused carrier
remained referenced before LPIPS. Repair
`5c75ef05f6ee20783937def9e29e3e4268c4fdae` durably records measurements before
refusal and explicitly releases both unused carriers. The reviewer inspected
this exact repair and independently passed all four Windows package tests,
reporting no remaining narrow launch-design blocker.

The review checked fixed shared encoding, ordered VAE-only/zero-noise/fixed-base
DDIM arms, native saved-byte references, prior-control exact pixel replay, safety
before LPIPS, terminal failure retention, bounded offline launch/resources and
the separate actual-user execution approval boundary. Neither reviewer nor
author executed the new scientific worker, loaded models or measured new study
pixels during this preparation. No scientific acceptance or C4 closure follows.

## Tests and preserved failures

- Author Windows script suite at repaired commit: 226 tests, 195 passed and 31
  expected skips.
- Author owned WSL component/package/quality suite: 33 tests, 32 passed and one
  expected Windows-path-only skip; no learned models or study inputs.
- Independent initial full-package Windows tests: three passed; WSL owned suite:
  31 passed and one expected skip. Independent repair Windows tests: four passed.
- The earlier component maximum-side type/bounds defect was independently
  blocked and repaired; see the component review, not erased history.
- The first combined WSL package test run had one Windows-path translation error.
  The Windows-only launcher test was correctly scoped to its host and passed
  there; no full WSL launcher pass is claimed.

Final clean-commit manifest rebinding, design validation, official dry preview
and a separate exact user compute decision are required before execution.
Prior run003 and saved-triplet run001 approvals remain consumed. This is a
one-source exploratory localization package, not an improved method, independent
N=3 sample, successful quality repair or permission for paid compute.

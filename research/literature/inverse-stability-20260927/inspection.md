# Primary-source inspection, inverse stability

Observer /root, 2026-09-27. This is selected-section inspection, not experimental
reproduction or whole-paper certification. Public literature only; no dataset,
model, package install or scientific execution. Notes checksum identifies this
record, not the publication. Raw snapshots are ignored, outside Git.

## AIDI, ICCV 2023

Pan, Gherardi, Xie and Huang; title and venue verified at
https://arxiv.org/abs/2309.04907. Selected full text inspected at
https://arxiv.org/html/2309.04907v1: sections3.1--3.2, equations2/7/8 and Algorithm1.
Anderson mixing solves a constrained residual-history problem; AIDI_E uses
averaging. Its guidance/editing protocol is not our empty-conditioned two-edge
path. This supports a candidate solver, not local convergence or source quality.
No upstream implementation was installed, pinned or reproduced.

Raw: stable project's `.thesis-build/c4-inverse-literature-20260927/aidi-v1.html`.
SHA256 `192f6cc3fd2ac76c475c9b0f4e3a23dfc577d00623cc5e19f40bb45d5be65efa`.
Proceedings PDF access failed; the successful HTML sections above were used.

## ReNoise, ECCV 2024

Garibi, Patashnik, Voynov, Averbuch-Elor and Cohen-Or. Venue verified at
https://research.google/pubs/renoise-real-image-inversion-through-iterative-noising/.
Selected full text: https://arxiv.org/html/2403.14602v1, method, AppendixA,
Table3 and AppendixC/Figure20. The averaging argument assumes convergence of the
underlying sequence; it does not guarantee a root for arbitrary divergence.
SDXL examples and different timestep/guidance profiles are not local evidence.

Raw: stable project's `.thesis-build/c4-inverse-literature-20260927/renoise-v1.html`.
SHA256 `f480bbb2f41cbca661df34f85c286952c65f66319f0de307c494a57c5c2437fc`.

## PreciseInv, NeurIPS 2025: abstract-only

Title/authors/venue/DOI and abstract inspected at
https://proceedings.neurips.cc/paper_files/paper/2025/hash/2e4bc9f6e31aa27861299940aa5242ad-Abstract-Conference.html.
Authors: Jing Zuo, Luoping Cui, Chuang Zhu, Yonggang Qi.
DOI10.52202/085713-1081. Authors propose recursive test-time optimization of
parameterized noise sequences for few-step inversion. This motivates a secondary
optimization route; unseen proofs, hyperparameters and local compatibility remain
unverified. PDF access failed. The linked official repository README was inspected
only for supported-model information; its code was not audited, pinned or executed.

## Limits

The independent Astra route review separately inspected EDICT/GNRI primary sections
and existing cards. Those are not newly verified cards in this synthesis. No
exhaustive newest-paper survey or universal best-method claim is supported.

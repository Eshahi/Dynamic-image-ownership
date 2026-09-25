# Independent bounded CLIP adapter review

Read-only reviewer actor: `/root/a6_clip_review`, separate from adapter author `/root`. Scope: exact A6 worktree at `e3afd24a97905f43989084f147b0cb8b1fe8cb52`, `scripts/a6_clip_visual.py`, metric probe, tests and receipts. This is a technical code review, **not** Spec Kit gate acceptance or a human verdict.

The reviewer independently confirmed that the A5 image-only path uses the pinned official CLIP visual builder, checkpoint and preprocessing; it avoids the eager tokenizer/`regex` import, does not alter Windows policy or download weights, and returns only compatibility evidence from the synthetic probe. Two findings:

1. **Blocking for an exact-byte fail-closed claim:** the adapter hashed source/checkpoint paths and then reopened them to execute/load. A concurrent file replacement could make the consumed bytes differ from the verified bytes. The follow-up implementation now compiles the verified source byte snapshot and loads the verified checkpoint byte snapshot through `io.BytesIO`; no second file open is used. The original changed-before-check test was insufficient, and the post-fix exact model-load check is retained as separate evidence.
2. **Numerical profile caveat:** the adapter converts the reconstructed model to float32 on CUDA. Upstream `clip.load` retains its default CUDA fp16 profile, whereas A5 declares float32 inference. The observed CUDA feature is a project-profile compatibility result, **not** proof of parity with upstream default fp16.

The reviewer has not yet re-reviewed the post-fix bytes. Keep the exact-byte closure and numerical-parity findings open until that review and a nontrivial acceptance criterion; do not close A6 on this document.

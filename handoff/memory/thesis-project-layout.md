---
name: thesis-project-layout
description: "Where the image-ownership thesis repo lives, which interpreters to use, and the project rules that bind any agent working in it"
metadata:
  node_type: memory
  type: project
  originSessionId: 74ce1155-fef8-48dc-bdf4-3552bd30995f
  modified: 2026-10-01T08:28:17.726Z
---

The working repo is `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5` (a git repo; the parent folder is not). It is a master's thesis: "Dynamic Image Ownership With Robust Neural Watermarking" (proposal in `inputs/proposal-text.md`, Persian). Other Codex worktrees of the same repo live under `C:\Users\Soroush\.codex\worktrees\` (e.g. `c4-qim-pilot` holds the three-threat study worker and RGB/CLIP adapters).

Rules come from the repo's `AGENTS.md`, `research/approval-policy.md`, `research/scope-guard.md`:
- Talk to the user in Persian; write repo docs, commits, issues in English.
- Never edit the proposal, claim ledger, `THESIS_GUIDE_OFFLINE.html`, or retained run outputs under `.thesis-build/*runs*`.
- Since 2026-10-03 development runs (synthetic or development-split images, local, USD 0) are delegated to the agent; only confirmatory held-out runs need the official runner and the user's approval at a milestone ([[codex-autonomous-handoff]]).
- Image-domain watermark = labelled pixel comparator only; never report it as the proposal's latent method (RQ-02/HYP-02 stay open).
- A Codex heartbeat agent also writes `thesis-runs/d916749c/continuation.md`; avoid competing edits to shared state files.

Interpreters: stdlib-only `.thesis-build/venv/Scripts/python.exe` (has jsonschema, no numpy); `.thesis-build/a6-science-venv/Scripts/python.exe` has numpy, PIL, scipy, torch, diffusers, lpips. Run tests with `python -m unittest discover -s scripts` from the repo root.

Related: [[watermark-v4-candidate]]

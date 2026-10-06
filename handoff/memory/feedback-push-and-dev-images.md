---
name: feedback-push-and-dev-images
description: "Agents may push and add development images without asking; since 2026-10-06 commits and pushes must appear as the user (their git identity, no Claude co-author line)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 29b48b68-14a0-40ca-9984-740f0217b7d4
  modified: 2026-10-06T23:23:36.241Z
---

**2026-10-05:** the user said agents may add new development images and push without asking. At that time, pushes had to show which agent made them.

**2026-10-06, this replaces the attribution part:** "I also want the pushes to be done by my account and shows there as me push, not claude."

**Why:** the user wants the repository history to appear under their own GitHub account.

**How to apply:**
- **Push:** remote `origin` = github.com/Eshahi/Dynamic-image-ownership.
  - Commit with the repository's own git identity (user.name `Soroush`, email as configured in the repo). Do not override the author.
  - Add no `Co-Authored-By: Claude` trailer. The user's instruction takes precedence over the default attribution lines.
  - Push only to new working branches, never `main`. No force-push.
  - If the default Windows TLS backend stalls, push with `git -c http.sslBackend=openssl push`.
- **Older commits:** those authored "Claude Code …" on the `claude/*` branches stay as they are. Rewriting them would need a force-push, which only happens if the user explicitly asks.
- **New development images:**
  - free, licensed sources;
  - recorded in `research/downloads.md` and `research/development-sources.md`;
  - selected by a pre-fixed rule;
  - never from validation, test or held-out pools.
- **Still needs the user:** held-out data decisions, paid compute, publication.

Related: [[codex-autonomous-handoff]], [[f5-encoder-amplified-latent]], [[thesis-project-layout]]

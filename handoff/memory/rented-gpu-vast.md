---
name: rented-gpu-vast
description: "2026-10-05 user decided to rent a vast.ai GPU (~10 h) instead of the local laptop GPU; SSH key, rules for what goes to the remote"
metadata:
  node_type: memory
  type: project
  originSessionId: 306009c7-f156-43a4-a6a7-e543c6058349
  modified: 2026-10-05T22:39:11.260Z
---

On 2026-10-05 (~22:45 UTC) the user decided to rent a GPU on vast.ai for about 10 hours and share it with Claude, because long runs at ~95% might damage the local machine (an RTX 5070 Ti Laptop GPU). This overrides the earlier "no paid compute" rule for this rental only.

**Why:** heavy GPU jobs (stress grids, 15-25 min each) were running back to back on a laptop.

**How to apply:**
- The user buys, creates and destroys the instance; Claude never handles their vast account, payment or API key.
- Claude connects only with the dedicated key `~/.ssh/vast_ed25519`. The user adds `vast_ed25519.pub` to vast.ai.
- Only code and development images go to the remote; held-out data never does.
- The F5 r2 baseline must be re-run on the remote GPU, so comparisons stay paired on the same hardware.
- Copy the results back before the user destroys the instance.

Related: [[f5-encoder-amplified-latent]], [[thesis-project-layout]]

**Instance (2026-10-05):**
- vast.ai ID 54395023: 1x RTX PRO 4500 Blackwell (32 GB), Belgium, 32 GB disk, about $0.35/h; the user put $5 of credit.
- SSH: `ssh -i ~/.ssh/vast_ed25519 -p <port> root@<server-ip>`. The port may change after a restart.
- Stopped by Claude at about 23:10 UTC with the container's own key (`vastai stop instance $CONTAINER_ID --api-key $CONTAINER_API_KEY` inside the box) when the user went to sleep. Nothing had been installed yet.
- To resume: the user clicks Start (Claude has no account API key) and sends the new Connect line. If the GPU was taken meanwhile, create a new instance the same way.

**Morning plan (the user's request):** run the 256-bit semantic sketch test on the rented GPU, then stop the server and report.
- Paired baseline on the remote first.
- Design to commit before running (r3-256), changing only the robust semantic channel:
  - keyed 256x512 Rademacher sketch of the 7-view CLIP vector;
  - 256 antipodal bit-chips over the 3272 band slots;
  - owner found by a soft-weighted recomputed correlation (a Rademacher sum, same single-pattern threshold 4.982);
  - binding by a soft ML angle from per-bit carrier LLRs plus the suspect's projections, same radii 6/10 in 32-bit units;
  - fragile tier unchanged (32-bit q).
- Both stress families; also T4/T5.

**2026-10-06 run:**
- Instance 54395023 stayed unavailable, so the user rented RTX PRO 4000 instance 54451380 (`ssh -p <port> root@<vast-ssh-host>`).
- Setup: uv venv at /workspace/thesis/venv; assets hash-verified; code snapshot.
- Ran the paired r2 / r3-256 family-1 test; r3-256 killed. Results are in MAIN `.thesis-build/dev-runs/20261006-0800-remote-pro4000/`.
- Claude stopped the instance at about 08:40 UTC. Both stopped instances still carry small storage fees until the user destroys them.

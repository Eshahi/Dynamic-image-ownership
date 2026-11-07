# Lean F6 runbook

For Claude, once the user has started the instance. Rules are in [PROTOCOL.md](PROTOCOL.md). Never handle the user's vast account, payment or API key. Connect only with `~/.ssh/vast_ed25519`. Never put GitHub credentials on the server. Stop instances; never destroy them.

## What the user provides

The SSH line, the hourly price and the instance start time in UTC. Vast 57877693 is the first choice, if it is available. Check before setup that it has the expected GPU, at least 40 GB of RAM and at least 80 GB of free disk, of which the models take 48.6 GB unless already there.

## Prepare on the laptop

The repository is private, so the code travels as an archive. Check that Hotspot Shield is off, because it blocks SSH.

```bash
git -C "C:/Users/Soroush/.codex/worktrees/claude-f6-lean" -c core.autocrlf=false -c core.eol=lf archive -o "C:/Users/Soroush/AppData/Local/Temp/f6l-code.tar" HEAD scripts research/tifs-20261028 research/encoder-transfer-20261019/stage2b-config.json research/encoder-transfer-20261019/source-list.json experiments/c4-v5-two-tier-regeneration-v1 AGENTS.md
```

```bash
"W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe" -I "C:/Users/Soroush/.codex/worktrees/claude-f6-lean/scripts/f6l_stage_sources.py" --dest "C:/Users/Soroush/AppData/Local/Temp/f6l-sources.tar" --from "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/fresh-development-20261013" "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/registry-fresh-20261016/canonical"
```

Upload both, check hashes, then unpack the code at `/workspace/f6l` and the sources into `/workspace/assets`. Upload is about 100 KB/s. Run `git hash-object --no-filters` on a few files against the laptop `ls-tree` to confirm byte identity.

## Setup and run

Run in tmux, so the work survives a lost SSH connection. Set the actual values first.

```bash
cd /workspace/f6l && export START=ACTUAL_UTC PRICE=ACTUAL_HOURLY TIFS_PYTHON=/workspace/venv/bin/python
```

```bash
PYTHONPATH=scripts python3 scripts/f6l_setup.py --assets /workspace/assets --venv /workspace/venv --instance-start-utc "$START" --hourly-usd "$PRICE" 2>&1 | tee /workspace/f6l-setup.log
```

```bash
bash scripts/f6l_driver.sh /workspace/assets /workspace/runs/f6l "$START" "$PRICE"
```

The driver runs the probe and stages 1 to 3 without waiting for anyone, and it exits as soon as a fixed rule says stop. Exit codes: 0 a GO label, 2 scientific stop, 3 resource stop, 4 incomplete.

## Watching it

Check `/workspace/runs/f6l/driver.log`, `probe/policy.json`, `probe/probe-measure.json`, and each stage's `decision.json` and `*-fit.json`. Check these soon after each step:

- **After setup:** elapsed time, and that `f6l-setup-ready.json` says complete.
- **After the probe:** actual writer graph times against the estimates (SDXL graph 2.5 to 6 s, UNet .7 to 1.5 s, reader .52 s), and that gradient agreement and peak memory look sane.
- **After Stage 1:** the table of decoded scores, and that spend so far is at most about USD 6.

A stop rule's exit is the end of the study. Do not resume with changed code in the same folder. A code repair needs a new folder and a note, and the paid clock keeps counting.

## F7 dual-carrier test (2026-11-02)

The F7 protocol is `research/f7-dual-carrier-20261102/PROTOCOL.md`. On a restarted instance the start time changes, so run setup again with the new START and price. It reuses the verified models and takes about 15 minutes. Then run the driver in f7 mode, from a code archive of branch `claude/f7-dual-20261102`:

```bash
bash scripts/f6l_driver.sh /workspace/assets /workspace/runs/f6l "$START" "$PRICE" f7
```

It runs the Stage S rehearsal, checks that the 16-source screen fits the cap, runs the screen, then writes `f7/screen/decision.json`.

## F7 registry replication, f7c (frozen 2026-11-07)

Protocol: `research/f7-dual-carrier-20261102/REPLICATION-PROTOCOL.md`. Branch `claude/f7-confirm-20261107`. Needs the user to rent an instance and give the SSH line and the hourly price. Turn Hotspot Shield off for SSH. Check the instance: GPU with at least 24 GB, at least 64 GB of RAM, at least 80 GB of free disk, and a fast desktop CPU (the readers are CPU bound).

1. Build the code archive on the laptop from the branch head, and use the fixed sources archive, which is built already:

```bash
git -C "C:/Users/Soroush/.codex/worktrees/claude-f6-lean" -c core.autocrlf=false -c core.eol=lf archive -o "C:/Users/Soroush/AppData/Local/Temp/f7c-code.tar" HEAD scripts research/tifs-20261028 research/f7-dual-carrier-20261102 research/encoder-transfer-20261019/stage2b-config.json research/encoder-transfer-20261019/source-list.json research/claude-round3-frozen-20261017.json experiments/c4-v5-two-tier-regeneration-v1 AGENTS.md
```

   - `C:/Users/Soroush/AppData/Local/Temp/f7c-sources.tar`: 128 canonical PNGs as `sources/<id>.png`, SHA-256 8d53af22fe4cd3febfebca03891ed85084ec8b8b0dd96b4128b0dd6f908cd58a, 56 MB. If it is lost, rebuild it from MAIN `.thesis-build/assets/f7c-fresh-20261107/canonical`; `prepare` checks every PNG and pixel hash against the manifest.
   - `C:/Users/Soroush/AppData/Local/Temp/f6l-sources.tar`: the 60 Stage S sources, which setup verifies and the rehearsal uses.
2. Upload all three, check their hashes, unpack the code at `/workspace/f6l`, and both source archives into `/workspace/assets`. The upload runs at about 100 KB/s, so start it before setup and let the two overlap.
3. Run setup as in the sections above, with the new START and PRICE.
4. Run the driver, detached, with its output in a log:

```bash
cd /workspace/f6l && nohup bash scripts/f6l_driver.sh /workspace/assets /workspace/runs/f6l "$START" "$PRICE" f7c > /workspace/f7c-driver.out 2>&1 &
```

   It runs the rehearsal, writes `f7c-fit.json`, then runs the 64-source screen and notes FINISHED. Stop it if the fit forecasts more than 6 h in total.
5. Fetch:

```bash
cd /workspace/runs/f6l/f7c && python3 /workspace/f6l/scripts/f7c_fetch_list.py && tar -cf /workspace/f7c-fetch.tar -T /workspace/f7c-fetch-list.txt
```

   Download it with a hash check into MAIN `.thesis-build/dev-runs/<date>-f7c-replication/`, unpack it, and write a `run.json`. Then stop the instance from inside (`vastai stop instance "$CONTAINER_ID" --api-key "$CONTAINER_API_KEY"`); never destroy it.
6. Score it on the laptop:

```bash
"W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe" "C:/Users/Soroush/.codex/worktrees/claude-f6-lean/scripts/f7c_registry_score.py" --screen "<run>/unpacked/screen" --out "<run>/score"
```

   Write `RESULTS-REPLICATION.md` next to the protocol.

## Finish

Pack and fetch, then stop the instance by hand. Do this before the reserve runs out.

```bash
/workspace/venv/bin/python -I scripts/f6l_pack.py --root /workspace/runs/f6l --dest /workspace/f6l-results.tgz
```

Download through byte ranges with hash checks if the connection is unreliable, into MAIN `.thesis-build/dev-runs/<date>-f6-lean/` with a `run.json`. Native images other than the seed-0 sample stay on the instance disk until the user destroys it.

Then report: the status label, C and J tables, quality, T4 and T5 events, spend, and everything missing.

## Validation boundary

Local checks are the rule tests, a flow test of every stage with stubbed models, a CPU run of the writer on real SD1.5 weights with very few steps, a real SDXL VAE gradient at 256 px, and syntax checks. These do not cover the SDXL graph at 1024 px (it crashes the laptop process on CPU, probably from memory), bf16 backward, UNet gradients, Kandinsky 3, native replay, VINE adapters, setup, GPU memory or any scientific outcome. The probe and the Stage 3 rehearsal are the first real tests of those paths.

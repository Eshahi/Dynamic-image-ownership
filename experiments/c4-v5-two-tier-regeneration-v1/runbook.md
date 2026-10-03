# Runbook: what is left to run for v5, in order

> Current status (2026-10-03): dev-001 has finished; see `results-dev-001.md`. The instructions below describe the historical preparation. The user subsequently authorized needed local experiments with a 45-minute ceiling and retained Codex launch responsibility. Current harness deadlines are 2500 s worker, 2600 s WSL plus 30 s kill grace, 2650 s launcher and 2700 s official runner. Historical manifests/approvals remain unchanged and cannot be reused with this changed code. No new scientific run is packaged here; a future run requires a new identity, same-commit full rehearsal and exact runner provenance.

Written 2026-10-02; updated the same day after the user's "ادامه بده" ("continue") and "continue until you reach an acceptable result", and on 2026-10-03 after "continue improving the algorithm". Paths are those of this machine. `PY` is the stdlib interpreter `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\venv\Scripts\python.exe`, `SCI` the science interpreter `...\.thesis-build\a6-science-venv\Scripts\python.exe`, `WT` this worktree `C:\Users\Soroush\.codex\worktrees\v5-study\THESIS_GUIDE_OFFLINE_v5`, `MAIN` the main checkout.

Before any GPU step: no other GPU job may be running (`nvidia-smi`), and the worker needs 8.7 GB of free VRAM.

## Done

- Development checks of codec revision 1 with the CLIP vector and with the refinement stage (`check-r1-clip`, `check-r1-refined`).
- Codec revision 2: designed in the numpy lab (`scripts/dev_v5_lab*.py`, reports under `MAIN\.thesis-build\rehearsal\v5-lab\dev\`), checked with the full codec on the sixteen development hosts and on twenty held-out hosts, with the proxy and with the CLIP vector, and for the C2 profile (`check-r2-default`, `check-r2-holdout`, `check-r2-holdout-clip`, `check-r2-holdout-clip-strong`). Results: `research/method-amendment-v5.md`, "Engineering evidence".
- This package moved to revision 2 (codec, profiles, worker check, transfer arm, tests, plan). Rehearsal 002 at `a1c2d71` passed; the manifest `v5-study-final-001.json` was then built at `a1c2d71` and never presented.
- Codec revision 3 (2026-10-03; embedder only, detector of revision 2): designed in the same lab over three seeds, checked with the full codec on the development hosts, the first held-out set and a second held-out set (`check-r3-default`, `check-r3-holdout`, `check-r3-holdout-clip`, `check-r3-holdout2-clip`, `check-r3-holdout-clip-strong`, with `check-r2-holdout2-clip` for comparison). This package moved to revision 3 (codec, profiles, worker check, tests, plan). The revision-2 manifests (`v5-study-rehearsal-manifest-002.json`, `v5-study-final-001.json`) are superseded.

## 1. Rehearsal of this package (synthetic images; no approval needed; about 30 to 60 minutes)

Policy basis: `research/approval-policy.md`, section "Rehearsal tier and infrastructure-only reruns, 2026-10-02". The rehearsal uses the identical launcher and worker on the twelve generated hosts in `MAIN\.thesis-build\rehearsal\v5-channel-dev\hosts`, reads no study image and writes only under `.thesis-build\rehearsal`. The worktree must be clean at the commit to be presented.

```powershell
cd $WT
& $PY scripts\prepare_v5_study.py --rehearsal --out "$MAIN\.thesis-build\v5-study-rehearsal-manifest-003.json"
& $PY scripts\run_v5_study.py --manifest "$MAIN\.thesis-build\v5-study-rehearsal-manifest-003.json" --output-dir "$MAIN\.thesis-build\rehearsal\v5-study-rehearsal-003"
& $PY scripts\analyze_v5_study.py "$MAIN\.thesis-build\rehearsal\v5-study-rehearsal-003\outputs\results.json" --out "$MAIN\.thesis-build\rehearsal\v5-study-rehearsal-003\analysis.json"
```

(The manifest `v5-study-rehearsal-manifest-001.json` was built at revision-1 commit `f9087a2` and never run; `-002` was run at revision-2 commit `a1c2d71` and passed. Both are superseded by the revision-3 commit.)

Pass condition: the launcher returns 0, which the worker gives only when all 617 rows are complete, all 2,204 detector calls were made and no stage failed. A safety-checker block on a synthetic image makes the return 1 without being a harness failure; read the worker log and `outputs/results.json` before deciding. A harness failure is fixed on this branch, committed, and the rehearsal repeated from the start at the new commit. Rehearsal outputs are synthetic and are never evidence.

## 2. The study itself (needs the user's approval; the user launches it)

Only after step 1 passes at the same clean commit.

1. Build the manifest; this hashes the twelve reserved source files to check that they are unchanged, and runs nothing:

   ```powershell
   cd $WT
   & $PY scripts\prepare_v5_study.py --out "$MAIN\.thesis-build\v5-study-final-002.json"
   ```

   It prints the manifest SHA-256 and the commit.
2. Independent review of the package by a reviewer other than the author (approval policy). None has taken place.
3. The user's approval of that exact manifest hash, recorded as an approval file in `MAIN\.thesis-build\` in the format of the earlier runs.
4. Launch by the user from their own terminal through the official dispatcher:

   ```powershell
   & $PY -B "C:\Users\Soroush\.codex\skills\thesis-compute-runner\scripts\dispatch_experiment.py" dispatch "$MAIN\.thesis-build\v5-study-final-002.json" --repo $WT --artifacts "$MAIN\.thesis-build\v5-study-runs" --approval <approval file> --execute
   ```

5. Analysis: `scripts\analyze_v5_study.py` on the run's `outputs\results.json`, then the results document against `acceptance-criteria.md`. Two independent human visual assessments are still required by the criteria.

Expected cost: local GPU only, USD 0, no download; 20 to 90 minutes (`compute-estimate.json`).

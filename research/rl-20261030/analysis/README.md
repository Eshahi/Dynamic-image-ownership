# Reproduce the saved-number analyses

These scripts use only Python's standard library. They do not import repository science code, load images/models, run experiments or contact a server. All outputs are exploratory descriptive analyses, not new validation. `PHASE_B_JOURNALS=off`.

The explicitly allowed MAIN development journals and their SHA-256 values are in `data-inventory.json`. Stage2b includes Stage2a; the extractor uses its last state for each ID and does not duplicate Stage2a. Phase A is kept separate. No archive extraction was needed because the permitted numeric journals were already extracted. Earlier status-event counts are retained; no failed outputs were removed.

The versioned `dev-records.jsonl.gz` is a deterministic compressed numeric snapshot, SHA-256 of its decompressed content `61cd39060c8ffc70c2f7d13fd1a3289b25c7ad1a3d4d473e8a0453f2bcfcab55`. It contains 11,760 rows for the 60 development sources, with no image pixels or Phase B records. The uncompressed JSONL is an ignored local cache. The extractor recreates both from the original journals. To analyze the snapshot on another machine, decompress it to `dev-records.jsonl` in this directory with a standard gzip reader before running the analysis scripts.

In PowerShell, use the authorized interpreter, with `-I` on each invocation:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/extract_saved.py'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/reward_spread.py'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/variance.py'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/oracle.py'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/predictability.py'
```

Each script was run as a short foreground process, well below the ten-minute bound. `inspect_saved.py` is the initial schema/count diagnostic and is not needed for reproduction. It includes allowed Stage2a/Phase-A mechanism journals in its explicit whitelist, never wildcard run discovery. Stored raw reader values are numerical measurements, not rerun detector calls. Extraction asserts C/read/content semantics and J implies C; analysis scripts include their own arithmetic/invariant checks. The published original counts are unchanged.

Output map: reward-results.json/reward-tables.md cover soft margins, binary rewards and attacker choice; variance-results.json/variance-note.md cover source/seed decomposition and conditional cost planning; oracle-results.json/oracle-note.md cover fixed versus hindsight choices; predictability-results.json/predictability-note.md cover whole-source LOSO diagnostics. The main interpretation is ../03-logged-analysis.md.

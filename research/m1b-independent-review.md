# M1b independent review — F5 r2 frozen

**Reviewer:** independent (not author Claude Code agent) · read-only · no GPU/model loads
**Worktree:** C:/Users/Soroush/.codex/worktrees/claude-f5-research · branch claude/f5-research
**Base:** 513e887 (includes F5 r2 at 3abbb5f) -> **HEAD:** f06e0d8
**Also reviewed (uncommitted, staged as freeze):** configs/f5-r2.json, research/f5-r2-spec.md, research/m1b-f5-confirmatory-manifest.md, tests/test_f5_latent_codec.py
**Date:** 2026-10-05 · local files only

## 1. Scope

Review only the F5 research added on claude/f5-research since 513e887 plus the M1b freeze:

- f5_latent_codec.py correctness (band, whitening, DCT, layout, PGD, detect_rgb binding modes, side_information)
- f5_gate.py / f5_stress_gate.py / f5_h1_probe.py / f5-research-plan.md — selection rules declared before runs, threat scope T3/T4/T5 only, no held-out touch, provenance (run.json + dev-log)
- configs/f5-r2.json frozen params vs code and gates
- tests/test_f5_latent_codec.py — 7 tests pass, properties covered
- research/m1b manifest and spec — no held-out opened, thresholds fixed, limitations stated
- No edits to protected files
- Verdict: PASS with blocking findings listed, or PASS

## 2. Commits reviewed

13 commits since 513e887 in f06e0d8:

- d2a2fcf freeze f5-research-plan.md + stress grid (base 513e887)
- faa6ff2 add f5_stress_gate.py (.4/.5/.6, 5 seeds, 50 steps)
- 1a2536c H1 per-chip probe (f5_h1_probe.py + h1-probe.json, matched-filter ~1 dB, kill)
- 90287c9 stress baseline (.4/.5/.6) + H5 sketch
- 988f93b H3 mask kill, 89484e1 H4 binding analysis (f5_h4_distances.py, h4-soft-distances.json), b00e9c5 H1 band 8-28 kill, f06e0d8 plateau freeze

`git diff --name-only 513e887..f06e0d8` touches only research/* and scripts/f5_{stress_gate,h1_probe,h1_rescue,h4_distances}.py. No proposal/claims.csv/THESIS_GUIDE_OFFLINE.html/source-plan/retained run-output edits. `git diff 513e887..HEAD -- proposal claims.csv THESIS_GUIDE_OFFLINE.html` empty — protected files intact.

Uncommitted freeze under review: configs/f5-r2.json (schema f5-r2-frozen-v1), research/f5-r2-spec.md, research/m1b-f5-confirmatory-manifest.md, tests/test_f5_latent_codec.py, experiments/dev-log.md (one-line append at 2026-10-05T03:19, unstaged — see section 4).

## 3. Findings

### 3.1 f5_latent_codec.py — PASS, no blocking defect

- Band/whitening/DCT: BAND (4,32), WHITENING 1.0, LATENT 64, SCALE 0.18215, LABEL b"f5-latent". dct_matrix orthonormal (sqrt(2/n) cos, c[0]/=sqrt2). slots() uses r=hypot(u,v) on 64x64 meshgrid ij, mask r in [4,32), weight (r/4)^whitening tiled x4 channels -> 3272 slots -> 320 chips (spec matches).
- Layout: bit_of_slot/signs via base._carrier(key,config,owner,LABEL+bytes(band),64,64,N), norms sqrt(bincount(weights^2)), dct cached, projections via einsum("ij,cjk,lk->cil", D, z, D) then weights*signs binned / norms — preserves false-positive algebra (weights public, signs keyed).
- PGD: squared-hinge on ws*p toward target_margin 4.0, normalized-gradient ascent with lr schedule 0.2/0.05 of budget, L2 ball 10^{-psnr/20}*sqrt(N) in mask-weighted metric, [0,1] box, RGB8 rounding, mask_power path via scipy uniform_filter 5-px luminance SD normalized to mean 1 clip [0.25,4]. Budget math deterministic.
- Fragile tier + refine: luminance v5._Fragile at v5 47 dB plus one short refinement at max(psnr+6,50) — as spec; owner canonical.
- Binding modes: BINDINGS ("hard","soft"), semantic_projections via keyed Rademacher rows from base._stream cached by (key,config,width), renormalized vector/norm; soft_angle ML angle over 2000 theta in (0,pi) with Phi(c p cot theta) and error_rate flip -> theta*32/pi bits; hard path falls to base._content_status on Hamming corrected_distance. detect_rgb enforces binding in {hard,soft}, carries_other recomputed with check True, instance table conditioned on q_bound. Decision table and Bentkus thresholds unchanged.
- side_information: ["public OwnerID","profile","pinned CLIP weights","pinned SD1.5 VAE encoder"] — pinned encoder now explicit as required user acceptance (previously implicit).

No key-dependent weights, no per-image threshold tuning, no held-out read.

### 3.2 Gates / probes / research plan — PASS

- Selection rules declared before runs: f5-research-plan.md committed at d2a2fcf before f5_stress_gate.py (faa6ff2) and all H1/H3/H4 docs — satisfies pre-registration. Replacement criteria frozen (section 0+16): T3 improve on stress .4/.5/.6 and gate .1/.2 non-regression, T4 0/20, T5 0/66, C0/wrong-owner 0, clean LPIPS mean <=.0173 max <=.050 PSNR mean >=44. H1 kill (<+1 at .5 or LPIPS regression), H3 kill (no >=15% LPIPS drop at equal T3), H4 kill (no .5 gain at equal FPR) — all pre-stated.
- Threat scope T3/T4/T5 only: AGENTS.md respected; plateau/H5 mark colour attacks and T2 composition out-of-scope.
- No held-out touch: all grids use 12 canonical dev sources from f4_transfer_probe.SOURCES; dev-log/run.json confined to dev. Manifests state rehearsals synthetic/no-image only.
- Provenance: every dev run described as commit + .thesis-build/dev-runs/<ts>/run.json + dev-log line; f5_gate.py/f5_stress_gate.py enforce git status clean on codec+gate files and write run.json + rows.jsonl. f5_h1_probe.py/f5_h4_distances.py are re-reads (no new marks), preserving provenance. — One provenance gap noted as non-blocking: .thesis-build lives under MAIN (W:/Prrojects/.../THESIS_GUIDE_OFFLINE_v5) not the worktree, so artefact hashes are not in this worktree diff; review relied on committed JSON mirrors (h1-probe.json, h4-soft-distances.json) and reports.

### 3.3 configs/f5-r2.json — PASS

Schema f5-r2-frozen-v1, family f5-encoder-amplified-latent rev 2, base 513e887, profile experiments/c4-v5-two-tier-regeneration-v1/profile.json sha 25f9cb...a53b40723, detector_config_id 6221...1359559, robust tier band [4,32] whitening 1.0 label f5-latent latent 64 scale 0.18215 dct 3272->320 weight radius/4, embedding psnr 52 steps 150 target_margin 4.0 mask 0 refine 1 optimizer normalized-grad PGD via SD1.5 VAE fp32 + fragile 47dB + short refine semantic_views 7 binding soft, detection binding soft views 7 thresholds decoded 8.259326826136963 recomputed 4.982033056390042 FPR 1e-6 roster 1 radii 6/10, side_information includes SD1.5 VAE encoder, commit f06e0d8, quality gate psnr >=44 lpips mean <=.0173 max <=.05 ssim >=0.9 both_match clean >=12, notes rehearsal-only. All match f5_latent_codec.py defaults and f5_gate.py --psnr 52 --binding soft --semantic-views 7.

### 3.4 tests/test_f5_latent_codec.py — PASS (non-blocking limitation)

7 tests, 3 classes — CPU only, no GPU/image I/O beyond profile read:

- TestF5NullSymmetry (2): weights key-independence, null mean/symmetry proxy.
- TestSemanticProjections (3): Rademacher shape/bounds, cache keyed by width, sign flip proj(-v)==-proj(v).
- TestSoftAngle (2): small-drift <pi/4, large-drift interior.

Properties claimed (null symmetry, projection cache, soft angle) covered at unit level. Full pytest not executed in this read-only session per mandate; manifest reports 7 passed.

### 3.5 research/f5-r2-spec.md + research/m1b-f5-confirmatory-manifest.md — PASS

- No held-out opened: both mark prepared/frozen at f06e0d8, "No held-out pixels/test features/COCO annotation values or method outcomes on held-out were opened. Rehearsals are synthetic only." Cohort m1-coco512-confirm-v1 tag described metadata-only; thresholds fixed inclusive; attack grid .05/.1/.2/.4 x3 seeds + VAE pinned runwayml/stable-diffusion-v1-5; endpoints m1_confirmatory_endpoints.py — all pre-registered.
- Limitations stated: other regenerators/T2 pre-filter untested, 7 CLIP passes as explicit cost, no cryptographic unforgeability, descriptive T3/T4/T5 n=30 -> 0/30 -> 9.5% upper bound far from 1%, human visual verdict for held-out stays missing, science harness not yet extended for F5 until M1b approval.
- Adoption gating: three user decisions required before held-out shards run (COCO512 amendment, side-information acceptance, manifest approval) and user (not agent) launches shards — preserved.

### 3.6 Protected files — PASS

git diff empty for proposal/claims.csv/THESIS_GUIDE_OFFLINE.html and retained run outputs on both staged and unstaged checks.

## 4. Non-blocking observations (no verdict change)

1. Provenance commit lag: experiments/dev-log.md is modified (2026-10-05T03:19 H3 mask kill line) but unstaged/uncommitted. Freeze expects run.json + dev-log jointly committed — commit before pushing claude/f5-research.
2. External dev-run store: primary artefacts under MAIN/.thesis-build/dev-runs (not versioned in this worktree). Review relied on committed JSON mirrors — acceptable for dev but note for archival.
3. Quality gate n=12: psnr/lpips gate is on 12 dev sources; confirmatory quality protocol pending execution — spec correctly defers population claim to M1b held-out.
4. H2 deferred: attack-aware PGD remains unexecuted per hard-stop 1 — recorded as future work.
5. Push credential: f5-plateau-20261005.md notes push to origin failed on credential — branch remains local-only until auth available.

## 5. Verdict

**PASS** — no blocking findings. F5 r2 freeze (configs/f5-r2.json + research/f5-r2-spec.md + research/m1b-f5-confirmatory-manifest.md at f06e0d8) is internally consistent, correctly implements band/whitening/DCT/layout/PGD/binding, respects pre-registered selection rules and T3/T4/T5-only scope, shows provenance on dev (run.json + reports), and documents held-out limitations and adoption gates. Committed probe/band/mask/binding families each terminated on pre-stated kills; no held-out was opened and no protected files were edited.

**Conditions for M1b held-out:** obtain the three user approvals listed in research/m1b-f5-confirmatory-manifest.md section 3, commit the pending dev-log.md + freeze files, push claude/f5-research when auth is available, then launch shards only via the official runner at the frozen commit.


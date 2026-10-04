# M1 development evidence index

Working inventory, 2026-10-03. **M1 incomplete.** This index does not alter the protected claim ledger, lifecycle gates or confirmatory authorization. Paths below are relative to the authoritative MAIN checkout unless prefixed WT. All measurements are exploratory development evidence; missing results remain missing.

## Method families and decision status

| Family | Distinct mechanism | Current evidence | Required next decision |
| --- | --- | --- | --- |
| A | Optimize a terminal VAE latent through the frozen decoder for two image-DCT signatures derived from source CLIP, pHash and public OwnerID | Implementation/config/spec committed; CPU tests pass; GPU pilot pending | Compare actual saved-image blind detection and quality; inspect source-template versus suspect-feature disagreement |
| A hybrid diagnostic | Add the decoder's latent-induced residual to the original source | Implementation ready; no measurements | Explicit image bypass; not an independent family or evidence for pure latent reconstruction |
| B | Gaussian Shading initial-noise sign coding, repeated payload with whitening; native DDIM inversion | SD1.5/SHAKE adaptation ready; synthetic run pending | Measure native recovery, T3 survival and inversion cost; no existing-photo quality claim |
| C | Progressive symbol guidance during generation; native VAE+DCT readout | GROW-inspired adaptation ready; synthetic run pending | Determine whether the final latent carries recoverable symbols after saved RGB/VAE and T3; not yet dual-key binding |
| D candidate | Phase modulation of the Fourier transform of a spatial latent crop, with VAE readout | Primary paper and pinned official implementation inspected; feasibility decision pending | Adopt only a bounded, explicitly attributed adaptation with independently correct quality/threshold arithmetic |

No family is exhausted merely because it is unimplemented, a run is missing, or another family's quality failed. A finite negative result supports only its measured settings and budget. A source bypass does not evade photographic quality accounting.

## Supporting completed and running evidence

- Reconstruction: `.thesis-build/dev-runs/20261003-1455-latent-reconstruction` contains four completed cases and an interrupted fifth. Its root status remained stale after the user pause. WT `research/m1-pause-artifacts-20261003.json` qualifies that interruption and preserves artifact hashes. The new `20261003-2255-latent-reconstruction-recovery` run restarts eight remaining cases from initialization; only whole completed cases replace incomplete history in the fixed twelve-case analysis. These are pure frozen-VAE reconstruction diagnostics, not watermark trials or proofs of a global decoder ceiling.
- Features: `.thesis-build/dev-runs/20261003-1507-feature-codes`, source commit `8eecaaf`, compares three fixed projection realizations on development data. Full-512 feature C0/C1 pair-ranking AUC is approximately .982/.972, versus original sign32 .649/.590. The seven same-content and 57 different-content pairs share source images; two uncertain pairs are retained separately. This does not measure watermark transport, independent population error, or human semantic validity.
- Image-domain comparator: retained `c4-v5-two-tier-dev-001` source `baeb218` has clean quality/detection 12/12 and joint semantic-presence/content-retention counts 10/10/7/3/0 of 12 for VAE/strength .05/.1/.2/.4. Safety-blocked rows and the failed overall runner remain retained. T4 and T5 coverage/quality limits must accompany their rates; v5 is not the proposed latent method.

## Package obligations before milestone review

1. Record actual commands, source commits, input hashes, timing, failed attempts, all fixed denominators and output locations for each scientific run in `experiments/dev-log.md` and its run manifest.
2. Freeze the method implementation/config/spec and precise amendments, including extraction side information, public-key forgery limitations, three qualified evidence states and abstention. Preserve code/feature and causal-history distinctions.
3. Supply clean, T3, T4 and T5 evidence with source counts, valid counts, quality/content-retention conditions, failure treatment and comparison with v5 and a published latent baseline. Synthetic generation comparisons do not substitute for existing-photo preservation.
4. Report either development targets met or at least three substantially different measured design families falling short. Missing human assessments stay missing. No claim of universal impossibility, population 1% FPR, legal ownership or native-resolution fidelity follows from the small development set.
5. Prepare the exact held-out evaluation package without inspecting held-out pixels/features/annotations; validate its official runner interface and synthetic rehearsals. Any proposed scope/threshold/attack amendment is explicit and reviewed before authorization.
6. Obtain one fresh independent milestone review scoped to the complete change since the last reviewed commit. The user then receives the M1 package in Persian and one decision: approve the confirmatory run or redirect.

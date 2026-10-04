# C-Q5/EQ5 development result and stage-local diagnosis

**Neither operator qualifies for the frozen conditional diffusion test.** EQ5 retains the carrier but passes clean quality on only1/8 outputs. Q5 passes clean quality on8/8 and clean detection on8/8, but passes the additional-VAE carrier gate on6/8: original-word seed1002 has13/16 matches and seed1003 has11/16. The all-eight gate remains unchanged. No conditional T3 manifest was frozen or adapter run; no T3 survival claim is available for these operators.

Source: MAIN `.thesis-build/dev-runs/20261004-0937-progressive-vote-margin`, committed runner `7be2a6c`, completed in142.703 seconds. Source `run.json` SHA-256 is `38241d538c242bd5181f3d2cbc3d750488a97d0f4103445be5d9c73741886530`. All24 generations and48 primary clean/VAE conditions completed across the same four reused synthetic prompt/seed clusters. C0 and old late original-word PNG replay passed on both channels for every seed. All four C0 images stayed below14/16 against both words on both channels. Neither failed seeds nor complementary targets are omitted.

The read-only post-run script [m1_progressive_vote_results.py](../scripts/m1_progressive_vote_results.py) independently reconstructs endpoint/trace words from recorded128-coefficient vectors, checks primary/endpoint agreement and50-row trace inventories, recomputes the runner's gate, and verifies all192 source artifact hashes and sizes (120,366,848 artifact bytes). Its retained [stage diagnosis JSON](m1-progressive-vote-margin-stage-diagnosis.json), SHA-256 `bedb59886b71a432a42d09b8d0e8dcf287c224d468e2b347db275fd49f0f5df0`, includes input receipts and its own script hash. This is post hoc CPU arithmetic on existing records, not new inference, an independent milestone review, or a formal full provenance analyzer. An initial invocation correctly refused the reused PNG-only path helper for non-PNG tensor/trace artifacts; the local diagnostic now checks single-component resolved paths. No source output was modified.

## Fixed-denominator results

All values below are eligible **native VAE-DCT** detector results; the image-DCT diagnostic is not substituted. Strict clean quality is PSNR>35, SSIM>.9, LPIPS<.1 versus the newly replayed same-seed generated C0 image. This is generated-counterfactual preservation, not existing-photo imperceptibility.

|Seed / target|EQ5 PSNR|EQ5 clean/VAE matches|Q5 PSNR|Q5 clean/VAE matches|
|---|---:|---:|---:|---:|
|1000 / original|31.458725|16 /16|39.588198|16 /15|
|1000 / complement|31.859731|16 /16|44.153750|16 /15|
|1001 / original|27.379893|16 /16|40.266894|16 /15|
|1001 / complement|27.078269|16 /16|37.846346|15 /16|
|1002 / original|31.148037|16 /16|41.281134|16 /13|
|1002 / complement|31.445616|16 /16|43.613116|15 /14|
|1003 / original|34.801853|16 /16|44.106337|16 /11|
|1003 / complement|35.558558|16 /16|47.531048|16 /15|

EQ5 mean PSNR31.341335, SSIM.948875 and LPIPS.022796. Its SSIM and LPIPS pass on8/8, but PSNR passes only seed1003 complement; all32 endpoint stages (8 images x4 diagnostic/eligible stages) recover the exact16-bit word.

Q5 mean PSNR42.298353, SSIM.993591 and LPIPS.002426; all eight satisfy all three strict clean metrics. The fixed between-operator comparison therefore supports the intended quality benefit of the minimum-change constraint on these development blocks. It does not make quality independent of content, establish generalization, or prove that the next stronger carrier will retain this quality.

|Q5 readout stage|Exact16/16|Presence>=14/16|Role|
|---|---:|---:|---|
|Terminal predecode|8/8|8/8|Oracle carrier diagnostic|
|Clipped-float decode/re-encode|6/8|8/8|Codec diagnostic, not PNG detector|
|Clean RGB8|6/8|8/8|Primary clean image detector|
|Additional VAE RGB8|1/8|6/8|Primary extra-cycle image detector|

The mean Q5 match counts are16,15.75,15.75 and14.25 respectively. These stages and eight word/seed arms are correlated, not32 independent images. The clean/VAE gate fails even though the final-stage mean exceeds14; the preregistered criterion requires every one of the eight outputs to qualify.

## The lost bits are localized to codec-induced vote-margin erosion

Every Q5 terminal predecode word is exact. The stage traces therefore rule out a failure to establish this public carrier in the final latent as the immediate explanation for the observed two gate failures. For the two failed outputs, the intended clean objective at the last step is already small:9.2813e-6 for seed1002 and1.6926e-5 for seed1003. On **each of their five guided steps**, the intended corrected-clean five-vote objective is0 after the update. Actual scheduler output and codec output are different states: a zero corrected-clean loss never guaranteed persistence after DDIM transport or VAE cycling.

The table uses zero-based bit indices. The signed decision margin is the fifth largest intended-signed coefficient for a target1, and the fourth largest for a target0, because the unchanged reader assigns a4-to4 tie to0. Q5 embedding itself uniformly requests five confident coefficients for either target sign. No coefficients in these listed groups are exactly zero.

|Seed / bit / target|Terminal margin|Clipped-float margin|Clean RGB8 margin|Extra-VAE margin|Clean→extra positive votes|
|---|---:|---:|---:|---:|---:|
|1002 /3 /1|.30399|.02009|.02245|-.03167|5→4|
|1002 /10 /1|.27669|.01980|.02399|-.05574|5→4|
|1002 /15 /1|.32364|.17472|.18013|-.18518|5→4|
|1003 /2 /1|.30618|.21875|.19437|-.00407|5→4|
|1003 /6 /0|.29860|.11955|.13149|-.13742|3→5|
|1003 /9 /1|.28904|.02122|.01224|-.07680|5→4|
|1003 /10 /1|.32829|-.00397|.00824|-.04321|5→3|
|1003 /12 /1|.30879|.07646|.08099|-.04026|5→4|

Most failing target1 groups have exactly the minimum five positive votes in the clean image, so a single positive-to-negative sign change removes the majority. Seed1003 bit6 instead targets0: two of five negative votes become positive, taking positive votes from3 to5. Seed1003 bit10 is already slightly wrong in the clipped-float cycle, recovers after RGB8 rounding/re-encoding, then loses two positive votes in the additional cycle. RGB8 should consequently not be modeled as uniformly degrading or improving all bits.

The clean errors in the complementary arms also illustrate distinct stages: seed1001 complement bit1 fails already in clipped float and clean RGB8 but recovers after the extra cycle; seed1002 complement bit7 is correct in clipped float and becomes wrong in clean RGB8, then remains wrong after the extra cycle while bit14 also fails. The JSON retains every group's signed coefficients/votes rather than only these highlighted failures.

These observations are consistent with the planned redundancy tradeoff: Q5 preserves natural coefficients and achieves much smaller clean distortion, while only a minimal subset carries reliable sign votes and the autoencoder perturbs them. They do not prove a universal VAE noise distribution, a content-independent erasure probability, or a global lower bound. Neither a higher margin nor a sixth vote was tested here; selecting either requires a separate prospective design. The next scientific question is how much decoder-channel redundancy or channel-aware margin is needed within the now-measured clean-quality headroom, rather than changing the detector's14/16 criterion or dropping the failing seed.

## Claim boundary

This is a successful clean-quality/carrier tradeoff measurement with a failed complete codec gate. It does not exhaust family C. There is still no CLIP+pHash+OwnerID binding, cryptographic authentication, fixed-photograph guarantee, diffusion T3 result, T4/T5 result, human visual verdict or M1 acceptance. Public16-bit payloads and the dependent wrong64 hypothesis panel cannot establish calibrated FPR or ownership. The result and every failed arm remain retained; no held-out data was accessed.

# Deterministic A-C component and public-owner compatibility

Exploratory development, 2026-10-04. This completes the original two-source component gate; it does not freeze the new original200 + A-C100 end-to-end method or complete M1.

## Component evidence

Run `MAIN/.thesis-build/dev-runs/20261004-1021-terminal-deterministic` executed source `10f9156` in 1340.110 seconds with peak allocated GPU memory 9,731,623,936 bytes. It used original retained unmarked200 initialization, fixed100 A-C updates, strict deterministic execution and inference-model offload. All8 C0/C1 clean/VAE conditions and32 four-owner queries completed. CPU analysis `20261004-1045-terminal-deterministic-analysis` at `eb14e3f` verified the complete receipt/stage inventory and independently reproduced pixel quality, cap and recorded-array score algebra. Analysis receipt SHA256: `8bfebd92644ae912d687466cca41d5d27f645592cadade43584a51232a654261`. CLIP and LPIPS inference were recorded observations, not re-inferred by that analyzer.

| Source | Clean PSNR / SSIM / LPIPS | Clean semantic / instance | VAE semantic / instance |
|---|---|---|---|
|1675|36.381863 / .980194 / .010315|5.889760 / 7.361003|5.742863 / 6.343574|
|4795|36.404445 / .977745 / .012986|5.896329 / 7.384739|5.910104 / 4.750063|

At the unchanged inclusive threshold4, clean quality, clean both-match and VAE semantic gates each passed2/2; all28 negative queries were below both thresholds. Both VAE cases also retained instance detection, although the gate required only semantic detection. VAE outputs themselves were not source-quality admissible: PSNR26.364736 and24.966098, respectively. These are two repeated-source observations under a particular operator, not independent samples per owner/channel or a general regeneration robustness claim.

The previous nondeterministic OOM and exact-replay failure remain retained and do not become successful runs. The present gate activates only the prospectively specified end-to-end initialization audit in `m1-end-to-end-initialization-design.md`; it does not authorize remaining-ten-source expansion using legacy initializers. Literal200 versus adapter100 plus fresh-process resumed100 must first agree exactly, then both original sources must pass the new end-to-end gate.

## Owner input-domain extension

Implementation `b3a69eb` follows `m1-owner-seed-extension-design.md`: the four original `OWNERS` remain unchanged; exactly sixteen A4 identities join the accepted input set. `MAP_VERSION` retains literal `m1-blind-noise-template-v1`, all numerical/map operations and threshold4 remain unchanged, and the immutable owner-map cache capacity becomes20. New owner-interface metadata is not hashed into maps. Invalid aliases, normalization and implicit conversions remain rejected.

CPU audit `MAIN/.thesis-build/dev-runs/20261004-1050-owner-extension` completed in16.375 seconds. Receipt SHA256: `0be38ec21d262bcd4009bdf3017a9e4b53ba0676443041ed871c500c40d62eeb`. It pinned legacy source `fe02a466b5ba33f7a9fd7d5a4df0080098defaf2`, SHA256 `df3e7140ee910519a1f57d8ea564d55636671c7404ca574fd40695e8514bccef`, and retained raw reference source, fixture digests, scalar matrices and output hashes.

- 128 legacy owner/descriptor cells passed exact template, ancillary, projection and score parity twice across different cache orderings; all32 retained development queries also exactly matched legacy and recorded values.
- All20 full owner maps were distinct and independent prefix framing matched.
- 512 new-owner projection cells passed independent geometry/variance checks. All512 alignment diagonals were both-match: semantic range50.981211–53.632973 and instance51.161772–53.508829.
- All8192 alignment cells and512 independent synthetic-null queries were retained, with row maxima and owner extrema. The7680 off-diagonal cells had no threshold exceedances in either channel; neither did the512 null queries. No invalid null was observed. No owner, threshold or seed was selected from these results.

The parent reran12 original core tests (only the declared cache-size assertion changed), five owner audit tests and sixteen end-to-end runner tests. The end-to-end runner also accepted the actual component plus compatibility receipts through its fail-closed CPU preflight.

This establishes input-domain compatibility and finite synthetic geometry, not sixteen-owner photograph efficacy, calibrated photographic FPR, an adaptive-forgery bound or cryptographic authentication. Four-owner development claims retain their original scope. The fixed A4 uint64 schedule remains exact audit metadata for deterministic A-C, not a consumed scientific noise seed; final candidate-facing documents must disclose that amendment before the single confirmatory decision.


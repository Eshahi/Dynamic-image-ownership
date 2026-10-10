# Massey 1969: algebraic BCH decoding

Primary source: James L. Massey, *Shift-Register Synthesis and BCH Decoding*, IEEE Transactions on Information Theory 15(1), 122–127. DOI: [10.1109/TIT.1969.1054260](https://doi.org/10.1109/TIT.1969.1054260). [Author archive PDF](https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI411.pdf). Inspected 2026-10-10: Sections III and V, including the syndrome/locator derivation and decoding condition. Citation key: `Massey1969ShiftRegister`.

Claim and mechanism: an iterative shortest shift-register construction supplies the error-locator polynomial from consecutive BCH syndromes; reciprocal roots locate binary errors. BCH designed distance d bounds minimum distance and supports correction of at most floor((d-1)/2) errors.

Threat and numbers: this is an algebraic communication-channel result, without image attacks, PSNR, neural models or watermark false-positive measurements. It does not establish ownership authentication.

Use and limit: E1's shortened (59,32) code, generator, five-error radius, antipodal carrier, thresholds and image writer are local design choices and derivations. The paper supports the decoder construction, not their photographic feasibility or regeneration survival. Errors beyond the radius may yield another valid message; code validity alone is not watermark presence. No code, installer, weights or paper file was downloaded into the project.

# Agarwal2026NRGMark

**Source:** Shruti Agarwal, Élie Michel, Vishal Asnani, Tania Mathern, John Collomosse. *NRGMark: Localized Watermarking for Energy Transparency in Images*. WACV 2026, pp. 7779–7788; DOI [10.1109/WACV61042.2026.00751](https://doi.org/10.1109/WACV61042.2026.00751). Inspected [author-hosted paper](https://collomosse.com/pubs/Agarwal-WACV-2026.pdf), accessed 2026-10-19. **V2:** §§3–4 and references read. CVF metadata identified the paper; no byte-equivalence claim between author PDF and proceedings PDF.

**Verified edges:** PDF p.9, reference [15] cites final TrustMark, ICCV2025; [13] separately cites the older TrustMark preprint.

**Direct evidence:** §3.2 localizes watermarked regions before decoding, with frozen watermark components and a trained localizer. A decoded UUID resolves a C2PA manifest in a cloud repository through a SoftBindingResolution API. §4 trains on 100K MIRFlickr images and evaluates other images/COCO. For 40 printed posters, reported bit accuracy is .91±.08 and BCH identification succeeds for 80% of watermarks. Substantial region overlap reduces localization recall.

**Interpretation:** authors target localized energy provenance. My inference: watermark-to-manifest lookup further preempts broad watermark-plus-registry novelty. Side information includes a manifest database and trained components. This is not evidence for continuous registered-image matching, diffusion attribution, or lawful ownership.

**Artifact:** MAIN `.thesis-build/q1-research-20261018/cache/nrgmark-wacv2026.pdf`; SHA256 `6B4197A5E448675F1C54E2AD9EA74D99AA08DE7BF6FF284A33574207DDA2817F`.

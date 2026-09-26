# C2 first development execution: descriptive evidence

Run `c2-semantic-dev-001`, one fixed seed0, original32 development images,
96 dependent planned comparisons. All96 completed; zero failed/pending cases.
No validation/test images, threshold selection, new seed or rerun.

| Condition | Completed cases | Equal12-bit q / equal Ws | q distance range | Mean recorded feature distance |
| --- | ---: | ---: | ---: | ---: |
| Same-image uncached repeat |32|32|0| -4.937992514886247e-10 |
| Fixed JPEG95, subsampling0 |32|29|0–1|0.0010730298065704837|
| Fixed same-domain different content |32|2|0–6|0.5108865466773699|

Every same-image feature vector was exactly equal, including independent fresh
cache verification. The tiny nonzero/negative repeat `1-dot` values arise from
approximately unit float32 features widened to double; they are retained, not
clamped or evidence of unequal features.

Three JPEG cases flipped one q bit, changing123,140 and126 of256 Ws bits,
respectively: DiffusionDB part420/d1ea0ff7…, part1929/5c91f290…, and COCO80932.
The complete IDs, distances and margins are in `statistics.json` and the verbatim
`reports/dev/semantic-examples.json`. Two different-content collisions are the
fixed DiffusionDB pairs part1467/e7af85ee…→part1854/5d6106b2… and
part1854/5d6106b2…→part1929/5c91f290…. Their recorded feature distances are
0.4372039277001588 and0.6283525454612512. Equal q gives equal Ws under the same
public OwnerID; hashing does not remove a collision in the input code.

This is evidence of repeat determinism for this exact runtime/32-image recipe,
not universal cross-runtime determinism. It contradicts any assertion that this
fixed q/Ws construction is unchanged under every JPEG95 edit or separates every
different image. Digest Hamming distance is not a semantic metric. These outcomes
remain available for downstream method evaluation; no projection seed, code
length, acceptance threshold or research scope was silently changed.

The report includes n, mean, median, descriptive sample SD and range per condition;
these are dependent-case summaries, not uncertainty estimates or independent N.
There is one execution and no CI, bootstrap, significance test, population FPR/TPR,
full watermark/latent method result, legal authority or publication clearance.
The descriptive summaries were chosen after outputs and are exploratory. The
shipped seed-comparison analysis backend cannot treat96 within-run records as96
independent runs; this read-only extension validates/replays the full journal and
computes descriptions only. It does not invent a confirmatory aggregation rule.

Reproduce without model execution:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/analyze_c2_development.py --artifacts 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/scientific-artifacts/C2-development/c2-semantic-dev-001' --output '<unused-analysis-path>.json'
```

An unused output is required; original artifacts are never modified. The helper
checks prospective tracked hashes, original32 development metadata, fixed96 pair
identities, terminal journal/report equality and declared output digests.
Independent results review is required before issue acceptance.

# A content-consistency diagnosis (exploratory)

This metadata-only diagnosis covers the four completed hybrid-source-bypass development sources in the pilot and old2 runs. It reads retained JSON records and code, not images, models, or mutable recovery4a outcomes. It does not amend the method, recalibrate a threshold, or assert a scientific gate.

The clean6012 result finds both carriers but abstains on instance content: corrected distance6.098384 exceeds the frozen match radius6. This is not a carrier-detection failure. The observed discontinuity combines decoded-code errors with source-to-suspect feature drift; the records alone cannot causally allocate their contributions.

## Frozen detector and observation boundary

Each channel passes if recomputed score >=4.982033056390042 or decoded score >=8.259326826136963. Content match uses corrected distance <=6, mismatch >=10, and abstention between. The decoded-distance correction is max(0,min(32,(d−32p)/(1−2p))), rounded to6 decimals, with p inferred from the decoded score by a segment-noise model (revised_watermark_v5.py:1207–1276). It is not measured bit error against the enrollment code. Instance status inherits the worse semantic/instance comparison (same file:1328–1356).

The embedder fixes enrollment CLIP semantic code q and source pre-watermark pHash h. The final blind detector recomputes q/h from each saved/redecoded suspect. Its instance hypothesis uses q_now unless semantic content is classified other. Surrogate scores optimize fixed source-slot weights and are explicitly not the final detector. The retained records contain32-bit feature codes and receipts, not the raw512-dimensional CLIP vectors or projection margins. “Raw” below means retained native detector fields; no feature recomputation was run for this diagnosis.

## Source and run receipts

|Run|Commit|Run JSON SHA256|Duration s|
|---|---|---|---:|
|20261003-2347-A-hybrid-pilot|421787d14cfaceaa41c94141f517e1730da0390a|0e56178cbdf483ac790bef3c2b575ca9e072b3a4ca0f65a93a4a20f93848a677|466.016|
|20261004-0012-A-hybrid-old2|dc012fbc6a466f017fb3d837506ed1a0a8b079c6|8c435eeaf94bae86ab476692f4a2894606fe588f538560e71b2765da1d56da4d|466.250|

|Case|Raw original SHA256 (recorded)|Source RGB8 SHA256 (recorded)|Result JSON SHA256|
|---:|---|---|---|
|1675|6ba641627c08ef424b7dc3e6cee069aa0dd49615a31c54ae0de1ecd1fabd9dea|9cce870c4d0c6318fe0897639a25c7fa537aec02e222b45bebe1c7a21a3e3c6e|f0b8b4b50ed8fb540bf39bd001b2dfff7b44c2b19e7f3c527879d8c678cf778d|
|4795|6f8994bac6aef0602d4aa4397ecd4b7d579f5b18f66058a2df021352dd22bdc6|d7349d172153462d1af71ebbdac0ad49bf7f34679f485dbb04990bb5d6f2ea8d|d532e9a7592b18606a8c4bd2c362de3c2d85dc150769b8aff6b3a45d06fc4bc0|
|6012|7cd0d627b15c09f373aa613d013fb2d8ae6bd20bcce0d98aa31b963e6bcca495|8974f1763627d2df54354cfaba520100635227646f42f405cbe3ac1689057252|20cd4a76ed5bb6cb5caf10f450686c9ea6bd564fdf8b74e305e228a52fb626f2|
|25394|f13f54a3cbe28140004425b1b010c51bd5be0e4c4da1d4b1e382e3e0b426e316|7cf34edc36cd2abc8f234dea67e6cfdce4faa6bb939b634ac8cf91ba0c2482d2|940e9f964adff8afc3c8e897eaeaf9661af21f192d8729af8c5d6635b6013113|

Source hashes are copied from retained provenance, not verified by opening original images. Result JSON equals its run.json route object byte-for-value after JSON parsing. These are512×512 resized existing development photographs; the hybrid operator explicitly adds source pixels: clip(source+decoded(z)−decoded(z_reference),0,1).

## All four source codes and suspect drift

|Case|Channel|Enrollment code|C1 recomputed|C1 source drift bits|VAE recomputed|VAE source drift bits|
|---:|---|---|---|---:|---|---:|
|1675|semantic|6aa41e3c|6aa41e3c|0|6aa41e3c|0|
|1675|instance|0ba0e08b|4bb0c08b|3|4bb2e088|5|
|4795|semantic|aa440fb8|aa440fb8|0|2a4c0fb8|2|
|4795|instance|ea8ed24f|ea8ef24f|1|ea8fe34f|4|
|6012|semantic|ba84b4b8|ba84b438|1|9a84b4f8|2|
|6012|instance|a003e39d|a007e19f|3|a10be1bd|4|
|25394|semantic|cbc5a778|cbc5a678|1|cbc5b678|2|
|25394|instance|86cb5f8a|86cb5f8a|0|82ea5f8a|3|

## Retained carrier and content measurements

d_src and d_obs are independently computed Hamming distances from the retained decoded code to enrollment and current suspect. d_recorded is the native detector field: when decoding fails but recomputation passes it deliberately reports0 for its recomputed candidate; when neither passes it stays null. It is not always the observed decoded-code distance. Score columns retain both testing routes; found/status are actual recorded detector outputs. A dash preserves null fields when no carrier is found.

|Case|Condition|Channel|Decoded code|d_src|d_obs|d_recorded|p|Corrected d|Recomputed score|Decoded score|Found|Content|
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
|1675|C1|semantic|6bc41e3c|3|3|3|0.106056|0.000000|8.581955|9.071938|True|match|
|1675|C1|instance|8ba0e089|2|5|5|0.123894|1.376465|7.491552|8.649936|True|match|
|1675|C1_VAE_cycle|semantic|4bc41a3c|5|5|5|0.121280|1.477396|8.256209|8.709664|True|match|
|1675|C1_VAE_cycle|instance|0981f281|7|10|0|—|0.000000|5.144721|6.833871|True|match|
|4795|C1|semantic|aa440fb8|0|0|0|0.121018|0.000000|8.715696|8.715696|True|match|
|4795|C1|instance|e196524f|6|7|7|0.072273|5.479279|9.012177|9.990950|True|match|
|4795|C1_VAE_cycle|semantic|aa440f18|2|4|4|0.122091|0.123174|8.233271|8.691068|True|match|
|4795|C1_VAE_cycle|instance|e09e724f|5|7|—|—|—|4.714028|6.119090|False|—|
|6012|C1|semantic|3a94b4a9|4|5|5|0.117480|1.621674|8.532601|8.797726|True|match|
|6012|C1|instance|e013e219|5|8|8|0.096026|6.098384|7.795062|9.325934|True|uncertain|
|6012|C1_VAE_cycle|semantic|ba9494a8|3|5|5|0.127871|1.220171|7.426166|8.560318|True|match|
|6012|C1_VAE_cycle|instance|e493e079|10|10|—|—|—|4.452634|6.653775|False|—|
|25394|C1|semantic|c9e5a678|3|2|2|0.112229|0.000000|8.891555|8.921923|True|match|
|25394|C1|instance|a6cb578a|2|2|2|0.108893|0.000000|8.793749|9.002434|True|match|
|25394|C1_VAE_cycle|semantic|49e5a678|4|4|4|0.112235|0.526717|8.320387|8.921780|True|match|
|25394|C1_VAE_cycle|instance|269f5682|8|11|0|—|0.000000|5.247307|7.712866|True|match|

## Quality, states and optimization (not interchangeable)

|Case|Clean PSNR/SSIM/LPIPS|Clean state|VAE state|Surrogate semantic/instance/cycle semantic|
|---:|---|---|---|---|
|1675|38.628993/0.985181/0.007618|both_match|both_match|8.859951/8.492918/8.473060|
|4795|38.255458/0.982948/0.009204|both_match|semantic_only|8.848691/9.204966/8.712351|
|6012|38.104299/0.985960/0.005320|content_uncertain|semantic_only|8.686949/9.124286/8.633843|
|25394|39.430214/0.982597/0.007273|both_match|both_match|8.815603/9.106532/8.545578|

## Interpretation of6012

Enrollment q=ba84b4b8/h=a003e39d; clean suspect q=ba84b438/h=a007e19f, moving1 semantic and3 pHash bits. The semantic decoded code3a94b4a9 is5 bits from the suspect and4 from enrollment; corrected distance1.621674 matches. Instance decoded e013e219 is8 bits from the suspect and5 from enrollment. Both carrier tests pass, but its inferred p=.09602552467674665 yields corrected distance6.098384, just outside6, hence content_uncertain/abstain and present=false despite watermark_found=true. The enrollment-code discrepancy and suspect drift partly oppose/compound each other by bit location; distances cannot be added. A strong surrogate9.124286 does not guarantee decoded content consistency.

After VAE,6012 semantic is still match, but instance recomputed4.452634 and decoded6.653775 both fall below their respective thresholds. Instance distance/status stays null, yielding semantic_only. This is a distinct loss of carrier evidence, not the clean content-radius failure. Operational regeneration-consistent labels do not establish causal history, and VAE-only processing is not the full T3 diffusion threat.

## Coverage and reusable analyzer readiness

Repeated --dual-dir is already supported: pass the pilot and old2 directories, then append completed4a/4b shards once finalized. Existing source/route overlap rejection prevents double counting or best-attempt selection. analyze_dual produces raw per-condition/channel fields, source_route_inventory, summaries and reserved coverage; its raw channel dictionaries retain the full codes, scores and distances tabulated here. No schema change is needed for these disjoint shards. Fixture tests cover disjoint merge, duplicate rejection and2-declared-vs12-reserved denominators. At this snapshot4/12 reserved sources are completed in the two read runs; the other8 are outside this diagnosis. This is not4/4 general success or12-source evidence. No partial moving recovery results were read. D-residual adaptation remains pending the parent-provided schema.

All C0_source/C0_matched/C0_VAE_cycle and wrong-owner checks in these four retained cases are negative for watermark_found; this descriptive inventory is not a population FPR estimate. Human visual verdicts remain missing. Feature thresholds and detector decisions remain unchanged.

Verification:8 CPU analyzer fixture tests passed (test_m1_analyze_pilots); no analyzer mutation was necessary for repeated disjoint shards.

You are helping design a watermarking method for a master's thesis. Read the brief and the literature notes below, then design.

[PASTE research/redesign-brief-20261002.md HERE]

[PASTE research/redesign-inputs/perplexity-results.md HERE]

Task:
1. Treat every citation in the literature notes as unverified. Mark each claim you rely on as "from notes, unverified", "established in the literature (you are confident)" or "my conjecture". Never invent a reference.
2. Explain why the DCT-domain mark was removed by the VAE round trip alone, and which properties a mark needs to survive it.
3. Propose ONE concrete design that keeps the proposal's dual keys (Ks, Ki), the three decision states and a lightweight extractor, or says exactly which of these it changes and why. Give: the embedding rule, the extraction/detection statistic, the threshold rule, the mapping of Ks and Ki to the latent pattern, and how real photos (not generated images) are handled.
4. Predict the failure modes against: VAE round trip, SD img2img (strength .05 to .4), copy-paste/transplant, semantic collision.
5. Give the smallest experiment that could falsify the design on one 12 GB GPU (SD 1.5 fp16, 512x512, 12 COCO images, a few GPU hours), with the pass/fail rule stated before running.
6. List two alternative designs you rejected and why.

Output as a structured document with these six headings. Be concise and precise; no marketing language.
